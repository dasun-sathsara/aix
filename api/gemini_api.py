import google.generativeai as genai

from data.api_response import APIResponse
from data.message import Message

from .api_interface import API


class GeminiAPI(API):
    """
    A specialized API wrapper for interacting with Google's Generative AI models.
    """

    def __init__(self, api_key: str, model: str, system_prompt: str, temperature: float = 0.85, max_tokens: int = 8192) -> None:
        """
        Initializes the GeminiAPI with the provided configuration.
        Configures the API key and sets up the model with specified parameters.
        """

        genai.configure(api_key=api_key)

        self._model_name: str = model
        self._system_prompt: str = system_prompt
        self._conversation: list[Message] = []

        self._config: dict[str, any] = {
            'temperature': temperature,
            'max_output_tokens': max_tokens,
            'top_p': 0.95,
            'top_k': 40,
            'response_mime_type': 'text/plain',
        }

        self._model = self._create_model()
        self._chat_session = self._model.start_chat(history=[])

    def _create_model(self) -> genai.GenerativeModel:
        """
        Creates and returns a GenerativeModel instance with the configured parameters.
        """

        return genai.GenerativeModel(
            model_name=self._model_name,
            generation_config=self._config,
            system_instruction=self._system_prompt,
        )

    def send_message(self, message: str) -> APIResponse:
        """
        Sends a message to the AI model and returns the response along with token usage.
        """

        try:
            self._conversation.append(Message(role='User', content=message))
            response = self._chat_session.send_message(message)
            self._conversation.append(Message(role='Assistant', content=response.text))

            usage_metadata = response.to_dict().get('usage_metadata', {})
            return APIResponse(
                message=response.text,
                prompt_tokens=int(usage_metadata.get('prompt_token_count', 0)),
                output_tokens=int(usage_metadata.get('candidates_token_count', 0)),
            )
        except Exception as e:
            raise RuntimeError(f'Error sending message: {e!s}') from e

    def clear_session(self) -> None:
        """
        Resets the chat session and clears the conversation history.
        """

        self._chat_session = self._model.start_chat(history=[])
        self._conversation.clear()

    def get_chat_history(self) -> list[Message]:
        """
        Returns a copy of the current conversation history.
        """

        return self._conversation.copy()

    def rewind(self, count: int = 1) -> None:
        """
        Rewinds the conversation by a specified number of user-assistant pairs.
        """

        if count < 1:
            raise ValueError('Rewind count must be at least 1')

        for _ in range(min(count, len(self._conversation) // 2)):
            self._chat_session.rewind()
            self._conversation.pop()  # Remove latest Assistant message
            self._conversation.pop()  # Remove latest User message
