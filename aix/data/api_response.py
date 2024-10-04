from dataclasses import dataclass


@dataclass
class APIResponse:
    message: str
    prompt_tokens: int
    output_tokens: int
