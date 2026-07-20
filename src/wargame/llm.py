"""All model calls go through this one function. Nothing else in the
project should import litellm or the Claude Agent SDK directly — if we
ever need to add retries, logging, or swap providers, this is the only
place that changes.

Two backends behind the same call_agent() contract (same pattern as the
alignment-data-pipeline repo's shared/api.py):

- "openrouter" (default): litellm routed through OpenRouter
  (openrouter.ai). One API key format for any model, which matters a lot
  once each agent/judge can pick its own model independently.
- "claude_code": the Claude Agent SDK driving the locally installed
  Claude Code CLI. No API key at all — calls are billed to whichever
  Claude account the CLI on this machine is logged into (or a
  CLAUDE_CODE_OAUTH_TOKEN from `claude setup-token`). Only Anthropic
  models, named by Anthropic model id ("claude-sonnet-5",
  "claude-haiku-4-5") or CLI alias ("sonnet", "haiku", "opus").
"""

import re
import sys
import time

import litellm

BACKENDS = ("openrouter", "claude_code")

# Transient CLI failures (mid-stream stalls, init timeouts, dropped
# connections) get retried with exponential backoff — observed live
# 2026-07-20: a single stalled stream killed an entire 31-call game.
# Subscription-window exhaustion must NOT be retried (it takes hours to
# reset); the CLI reports it as "usage limit" / "session limit".
_RETRY_BACKOFF_S = [5, 15, 45]  # 4 attempts total
_LIMIT_PATTERN = re.compile(r"(usage|session)\s+limit", re.IGNORECASE)

# Claude Code treats an empty system prompt as unset and substitutes its
# own agentic CLI prompt, which would leak tool/codebase behavior into
# agent responses. Every wargame call sends a non-empty system prompt
# today (build_agent_system_prompt / build_judge_system_prompt), so this
# is a guard against future callers, not a path any current game hits.
_NEUTRAL_SYSTEM = "You are Claude, a helpful AI assistant. Respond directly to the user's message."


def call_agent(
    model: str,
    system_prompt: str,
    user_prompt: str,
    api_key: str,
    backend: str = "openrouter",
) -> str:
    """Ask one model one question and return its text reply.

    For backend "openrouter": `model` is an OpenRouter model slug, e.g.
    "anthropic/claude-3.5-sonnet" or "openai/gpt-4o" (browse slugs at
    https://openrouter.ai/models), and `api_key` is the caller's
    OpenRouter key — passed in explicitly (not read from environment/.env
    here) because a real caller is a website request carrying one
    visitor's key, not a fixed server-side secret.

    For backend "claude_code": `model` is an Anthropic model id or CLI
    alias, and `api_key` is ignored entirely — authentication is the
    Claude Code CLI's own login on this machine.
    """
    if backend == "claude_code":
        return _call_claude_code(model=model, system_prompt=system_prompt, user_prompt=user_prompt)
    if backend != "openrouter":
        raise ValueError(f"Unknown backend {backend!r}. Must be one of {BACKENDS}.")

    # litellm routes to OpenRouter when the model string is prefixed with
    # "openrouter/". This is the one line to change if we ever stop using
    # OpenRouter and start calling a provider's API directly instead.
    response = litellm.completion(
        model=f"openrouter/{model}",
        api_key=api_key,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content


class _NonRetryableError(RuntimeError):
    """A claude_code failure that retrying can't fix: SDK/CLI missing, or
    the subscription usage window is exhausted (resets on the order of
    hours — see _LIMIT_PATTERN)."""


def _call_claude_code(model: str, system_prompt: str, user_prompt: str) -> str:
    """One single-turn Claude Code CLI call, with retries on transient
    failures (see _RETRY_BACKOFF_S). Non-retryable failures — missing
    SDK/CLI, usage-limit exhaustion — raise immediately."""
    for attempt, backoff_s in enumerate([*_RETRY_BACKOFF_S, None], start=1):
        try:
            return _claude_code_query_once(model, system_prompt, user_prompt)
        except _NonRetryableError:
            raise
        except RuntimeError as e:
            if backoff_s is None:
                raise
            print(
                f"  claude_code call attempt {attempt} failed ({str(e)[:200]}) — "
                f"retrying in {backoff_s}s",
                file=sys.stderr,
            )
            time.sleep(backoff_s)
    raise AssertionError("unreachable")  # the last loop iteration always returns or raises


def _claude_code_query_once(model: str, system_prompt: str, user_prompt: str) -> str:
    """A single attempt at a single-turn, tool-less Claude Code CLI call.

    The CLI is a full agentic coding environment; everything here exists
    to strip that back down to plain text generation so a wargame turn on
    this backend behaves like a plain API call:
    - tools=[] and max_turns=1: no file/bash/web access, one reply.
    - setting_sources=[]: hermetic — don't load ~/.claude settings
      (custom agents, hooks, permission modes) into generated text.
    - env blanks ANTHROPIC_API_KEY/AUTH_TOKEN: Claude Code treats an
      empty value as unset and falls back to its own login (or
      CLAUDE_CODE_OAUTH_TOKEN), so a key sitting in this server's
      environment can't be silently billed.
    """
    # Imported lazily so the openrouter backend (and the test suite)
    # never needs the claude-agent-sdk package installed.
    try:
        import anyio
        from claude_agent_sdk import CLINotFoundError, ClaudeAgentOptions, query
        from claude_agent_sdk.types import AssistantMessage, ResultMessage, TextBlock
    except ImportError as e:
        raise _NonRetryableError(
            "The Claude Code backend requires the claude-agent-sdk package; "
            "run: pip install -r requirements.txt"
        ) from e

    options = ClaudeAgentOptions(
        model=model,
        system_prompt=system_prompt if system_prompt.strip() else _NEUTRAL_SYSTEM,
        tools=[],
        max_turns=1,
        setting_sources=[],
        permission_mode="default",
        env={"ANTHROPIC_API_KEY": "", "ANTHROPIC_AUTH_TOKEN": ""},
    )

    async def _run():
        text_parts: list[str] = []
        result_msg = None
        stream = query(prompt=user_prompt, options=options)
        try:
            async for msg in stream:
                if isinstance(msg, AssistantMessage):
                    for block in msg.content:
                        if isinstance(block, TextBlock):
                            text_parts.append(block.text)
                elif isinstance(msg, ResultMessage):
                    # The result is final for a single-turn call — stop here.
                    # After an is_error result the CLI exits non-zero; reading
                    # past the result would turn that exit into a raw process
                    # error and mask the CLI's actual error text below.
                    result_msg = msg
                    break
        finally:
            await stream.aclose()
        return text_parts, result_msg

    try:
        text_parts, result_msg = anyio.run(_run)
    except CLINotFoundError as e:
        raise _NonRetryableError(
            "The Claude Code backend requires the Claude Code CLI "
            "(https://claude.com/claude-code); install it, then log in "
            "or set CLAUDE_CODE_OAUTH_TOKEN from `claude setup-token`."
        ) from e
    except Exception as e:  # CLI failures surface as assorted exception types
        raise _classify_failure(str(e)) from e

    if result_msg is None:
        raise RuntimeError("Claude Code returned no result message.")
    if result_msg.is_error:
        raise _classify_failure(result_msg.result or result_msg.subtype or "unknown error")
    if result_msg.result is not None:
        return result_msg.result
    return "".join(text_parts)


def _classify_failure(message: str) -> RuntimeError:
    """Usage-limit exhaustion is non-retryable; everything else (stalled
    streams, init timeouts, dropped connections) is worth retrying."""
    if _LIMIT_PATTERN.search(message):
        return _NonRetryableError(f"Claude Code call failed: {message}")
    return RuntimeError(f"Claude Code call failed: {message}")
