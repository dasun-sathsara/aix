import os
from enum import Enum
from typing import ClassVar

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load environment variables
load_dotenv()


# Enum definitions for models
class DeepSeekModels(Enum):
    DEEPSEEK_CHAT = 'deepseek-chat'


class QwenModels(Enum):
    QWEN_INSTRUCT = 'Qwen/Qwen2.5-72B-Instruct'


class OpenAIModels(Enum):
    CHATGPT_4O = 'chatgpt-4o-latest'
    GPT4O_MINI = 'gpt-4o-mini-2024-07-18'


class GeminiModels(Enum):
    GEMINI_FLASH = 'gemini-1.5-flash-002'
    GEMINI_PRO = 'gemini-1.5-pro-002'


# Settings classes with updated protected namespaces
class DeepSeekSettings(BaseSettings):
    model_config = SettingsConfigDict(protected_namespaces=('settings_',))
    model_name: DeepSeekModels = DeepSeekModels.DEEPSEEK_CHAT
    base_url: str = 'https://api.deepseek.com/beta'
    api_key: str = Field(default=os.getenv('DEEPSEEK_CHAT_API_KEY'))


class QwenSettings(BaseSettings):
    model_config = SettingsConfigDict(protected_namespaces=('settings_',))
    model_name: QwenModels = QwenModels.QWEN_INSTRUCT
    base_url: str = 'https://api.hyperbolic.xyz/v1'
    api_key: str = Field(default=os.getenv('QWEN_API_KEY'))


class OpenAISettings(BaseSettings):
    model_config = SettingsConfigDict(protected_namespaces=('settings_',))
    models: ClassVar = OpenAIModels
    api_key: str = Field(default=os.getenv('OPENAI_API_KEY'))


class GeminiSettings(BaseSettings):
    model_config = SettingsConfigDict(protected_namespaces=('settings_',))
    models: ClassVar = GeminiModels
    api_key: str = Field(default=os.getenv('GEMINI_API_KEY'))


# Create settings instances
deepseek_settings = DeepSeekSettings()
qwen_settings = QwenSettings()
openai_settings = OpenAISettings()
gemini_settings = GeminiSettings()
