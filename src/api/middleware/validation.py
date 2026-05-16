from fastapi import HTTPException
import re

MAX_PROMPT_LENGTH = 3000

INJECTION_PATTERNS = [
    r"ignore previous instructions",
    r"you are now",
    r"act as",
    r"disregard all",
    r"system prompt",
    r"forget everything",
]


def validate_prompt(prompt: str) -> None:
    """
    Validates the user prompt. Raises HTTP 400 on failure.
    Checks: non-empty, max 3000 characters, prompt injection patterns.
    """
    if not prompt or prompt.strip() == "":
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")
    if len(prompt) > MAX_PROMPT_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Prompt exceeds maximum length of {MAX_PROMPT_LENGTH} characters."
        )
    lowered = prompt.lower()
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, lowered):
            raise HTTPException(status_code=400, detail="Prompt contains disallowed content.")
