import openai
import tiktoken

from data.api_response import APIResponse
from data.message import Message

from .api_interface import API


class GenericAPI(API):
    """
    A generic API wrapper for interacting with OpenAI-compatible models.
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        system_prompt: str,
        base_url: str,
        temperature: float = 0.85,
        max_tokens: int = 8192,
    ) -> None:
        """
        Initializes the GenericAPI class with the provided configuration,
        including setting the API key, base URL, and conversational parameters.
        """
        self._client = openai.OpenAI(api_key=api_key, base_url=base_url)
        self._model_name: str = model
        self._system_prompt: str = system_prompt
        self._temperature: float = temperature
        self._max_tokens: int = max_tokens
        self._conversation: list[dict] = []

        # Add the system prompt to the conversational history
        self._conversation.insert(0, {'role': 'system', 'content': self._system_prompt})

    def rewind(self, count: int = 1) -> None:
        """
        Rewinds the conversation by a specified number of user-assistant pairs.
        """
        if count < 1:
            raise ValueError('Rewind count must be at least 1')

        for _ in range(min(count, len(self._conversation) // 2)):
            self._conversation.pop()  # Remove latest Assistant message
            self._conversation.pop()  # Remove latest User message

    def get_chat_history(self) -> list[Message]:
        """
        Returns a copy of the current conversation history.
        """
        history = []
        for message in self._conversation:
            if message['role'] == 'system':
                continue

            role = 'User' if message['role'] == 'user' else 'Assistant'
            history.append(Message(role=role, content=message['content']))

        return history

    def clear_session(self) -> None:
        """
        Resets the chat session and clears the conversation history.
        """
        self._conversation.clear()

    def _count_tokens(self, text: str) -> int:
        """
        Counts the number of tokens in a given text.
        """
        encoding = tiktoken.get_encoding('o200k_base')
        return len(encoding.encode(text))

    def send_message(self, message: str) -> APIResponse:
        """
        Sends a message to the AI model and returns the response along with token usage.
        """
        try:
            self._conversation.append({'role': 'user', 'content': message})
            response = self._client.chat.completions.create(
                model=self._model_name,
                messages=self._conversation,
                temperature=self._temperature,
                max_tokens=self._max_tokens,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0.67,
                response_format={'type': 'text'},
            )

            response_text = response.choices[0].message.content
            self._conversation.append({'role': 'assistant', 'content': response_text})

            return APIResponse(
                message=response_text,
                output_tokens=self._count_tokens(response_text),
                prompt_tokens=self._count_tokens(message),
            )

        except Exception as e:
            raise RuntimeError(f'Error sending message: {e!s}') from e
