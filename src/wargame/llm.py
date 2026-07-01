"""All model calls go through this one function. Nothing else in the
project should import litellm directly — if we ever need to add retries,
logging, or swap providers, this is the only place that changes.

We route every call through OpenRouter (openrouter.ai) rather than
calling providers directly. That means one API key format for any
model, which matters a lot once each agent/judge can pick its own
model independently.
"""

import litellm


def call_agent(model: str, system_prompt: str, user_prompt: str, api_key: str) -> str:
    """Ask one model one question and return its text reply.

    `model` is an OpenRouter model slug, e.g. "anthropic/claude-3.5-sonnet"
    or "openai/gpt-4o" (browse available slugs at https://openrouter.ai/models).
    `api_key` is the caller's OpenRouter key — passed in explicitly (not
    read from environment/.env here) because a real caller is a website
    request carrying one visitor's key, not a fixed server-side secret.
    """
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
