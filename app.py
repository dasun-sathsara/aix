from pathlib import Path

from pydantic import BaseModel, Field

from api.api_interface import API
from data.api_response import APIResponse
from data.message import Message


class Config(BaseModel):
    print_code_block: bool = Field(True, description='Include the code block in the output markdown file.')
    print_error_block: bool = Field(True, description='Include the error block in the output markdown file.')
    print_file_content: bool = Field(True, description='Include file content in the output markdown file.')
    save_conversation: bool = Field(False, description='Whether to save the conversation.')
    markdown_language: str = Field('plaintext', description='The markdown language for the output markdown file.')


class App:
    def __init__(self, api: API, config: Config):
        self._api = api
        self._config = config
        self._printing_history: list[Message] = []

    def set_config(self, config: Config) -> None:
        """Update the configuration."""
        self._config = config

    def send_message(
        self, prompt: str, code_block: str | None = None, error_block: str | None = None, files: list[str] | None = None
    ) -> None:
        llm_prompt = self._create_llm_prompt(prompt, code_block, error_block, files)
        user_prompt = self._create_user_prompt(prompt, code_block, error_block, files)
        self._printing_history.append(user_prompt)

        response = self._api.send_message(llm_prompt)
        self._printing_history.append(Message(role='Assistant', content=response.message))

        self.save_to_disk('output.md')

    def _create_user_prompt(
        self, prompt: str, code_block: str | None = None, error_block: str | None = None, files: list[str] | None = None
    ) -> Message:
        """Create the printing history for the given inputs."""

        message_parts = []

        if files and self._config.print_file_content:
            message_parts.extend(self._process_files(files))

        if code_block and self._config.print_code_block:
            message_parts.append(self._format_block('Code Block', code_block))

        if error_block and self._config.print_error_block:
            message_parts.append(self._format_block('Error Block', error_block))

        message_parts.append(self._format_block('Prompt', prompt.strip()))

        return Message(role='User', content='\n'.join(message_parts))

    def _create_llm_prompt(
        self, prompt: str, code_block: str | None = None, error_block: str | None = None, files: list[str] | None = None
    ) -> str:
        """Create the LLM prompt from the given inputs."""

        prompt_parts = []

        if files:
            prompt_parts.extend(self._process_files(files))
        if code_block:
            prompt_parts.append(self._format_block('Code Block', code_block))
        if error_block:
            prompt_parts.append(self._format_block('Error Block', error_block))

        prompt_parts.append(self._format_block('Prompt', prompt.strip()))

        return '\n\n'.join(filter(None, prompt_parts)).strip()

    def _process_files(self, files: list[str]) -> list[str]:
        """Process the list of files and return their contents."""

        file_contents = []
        for file in files:
            try:
                content = Path(file).read_text(encoding='utf-8').strip()
                if self._config.print_file_content:
                    file_contents.append(f'**File Name**: {file}\n**File Content:**\n```{self._config.markdown_language}\n{content}\n```\n')
            except OSError as e:
                print(f'Error reading file {file}: {e}')
        return file_contents

    def _format_block(self, block_type: str, content: str) -> str:
        """Format a block of content with markdown."""

        return f'**{block_type}:**\n```{self._config.markdown_language}\n{content.strip()}\n```'

    def clear_session(self) -> None:
        """Clear the session."""

        self._api.clear_session()
        self._printing_history.clear()

    def rewind(self, count: int = 1) -> None:
        """Rewind the conversation by a specified number of user-assistant pairs."""

        if count < 1:
            raise ValueError('Rewind count must be at least 1')

        self._api.rewind(count)

        for _ in range(min(count, len(self._printing_history) // 2)):
            self._printing_history.pop()  # Remove latest Assistant message
            self._printing_history.pop()  # Remove latest User message

    def save_to_disk(self, path: str) -> None:
        """Save the conversation to a file."""

        with Path(path).open('w') as f:
            for message in self._printing_history:
                if message.role == 'User':
                    f.write(f'## Me\n\n{message.content}\n\n')
                else:
                    f.write(f'## You\n\n{message.content}\n\n')
                    f.write('---')
