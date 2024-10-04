from dataclasses import dataclass
from typing import Literal

User = Literal['User']
Assistant = Literal['Assistant']


@dataclass
class Message:
    role: User | Assistant
    content: str
