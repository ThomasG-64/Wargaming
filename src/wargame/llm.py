"""All model calls go through this one function. Nothing else in the
project should import litellm directly — if we ever need to add retries,
logging, or swap providers, this is the only place that changes.
"""

import litellm


def call_agent(model: str, system_prompt: str, user_prompt: str) -> str:
    """Ask one model one question and return its text reply.

    `model` is a litellm model string, e.g. "claude-sonnet-4-5-20250929"
    or "gpt-5". litellm reads the matching API key (ANTHROPIC_API_KEY,
    OPENAI_API_KEY, ...) from the environment automatically based on
    this string.
    """
    response = litellm.completion(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    return response.choices[0].message.content
