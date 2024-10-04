from abc import ABC, abstractmethod

from data.api_response import APIResponse
from data.message import Message


class API(ABC):
    @abstractmethod
    def send_message(self, message: str) -> 'APIResponse':
        pass

    @abstractmethod
    def clear_session(self) -> None:
        pass

    @abstractmethod
    def get_chat_history(self) -> list['Message']:
        pass

    @abstractmethod
    def rewind(self, count: int = 1) -> None:
        pass
