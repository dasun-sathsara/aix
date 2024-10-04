from .generic_api import GenericAPI


class OpenAI_API(GenericAPI):
    """
    A specialized API wrapper for interacting with OpenAI's models.
    """

    def __init__(self, api_key: str, model: str, system_prompt: str, temperature: float = 0.85, max_tokens: int = 16383) -> None:
        """
        Initializes the OpenAI_API class with the provided configuration,
        using the default OpenAI base URL.
        """

        super().__init__(
            api_key=api_key,
            model=model,
            system_prompt=system_prompt,
            base_url='https://api.openai.com/v1',
            temperature=temperature,
            max_tokens=max_tokens,
        )
