from pathlib import Path

from pydantic import BaseModel, Field

from api.api_interface import API
from data.message import Message


class Config(BaseModel):
    print_code_block: bool = Field(True, description='Include the code block in the output markdown file.')
    print_error_block: bool = Field(True, description='Include the error block in the output markdown file.')
    print_file_content: bool = Field(True, description='Include file content in the output markdown file.')
    save_conversation: bool = Field(False, description='Whether to save the conversation.')
    markdown_language: str = Field('plaintext', description='The markdown language for the output markdown file.')


class App:
    def __init__(self, api: API, config: Config):
        self.api = api
        self.config = config
        self.printing_history: list[Message] = []

    def set_config(self, config: Config) -> None:
        """Update the configuration."""
        self.config = config

    def send_message(
        self, prompt: str, code_block: str | None = None, error_block: str | None = None, files: list[str] | None = None
    ) -> None:
        llm_prompt = self._create_llm_prompt(prompt, code_block, error_block, files)
        with Path('temp.md').open('w', encoding='utf-8') as f:
            f.write(llm_prompt)

    def _create_printing_history(
        self, prompt: str, code_block: str | None = None, error_block: str | None = None, files: list[str] | None = None
    ) -> None:
        """Create the printing history for the given inputs."""

        message = []

        if files and self.config.print_file_content:
            message.extend(self._process_files(files))

        if code_block and self.config.print_code_block:
            message.append(self._format_block('Code Block', code_block))

        if error_block and self.config.print_error_block:
            message.append(self._format_block('Error Block', error_block))

        message.append(f'Prompt:\n{prompt.strip()}')

        self.printing_history.append(Message(role='User', content='\n'.join(message)))

    def _create_llm_prompt(
        self, prompt: str, code_block: str | None = None, error_block: str | None = None, files: list[str] | None = None
    ) -> str:
        """Create the LLM prompt from the given inputs."""

        self._create_printing_history(prompt, code_block, error_block, files)

        with Path('print.md').open('w', encoding='utf-8') as f:
            f.write(self.printing_history[-1].content)

        llm_prompt = []
        if code_block and self.config.print_code_block:
            llm_prompt.append(self._format_block('Code Block', code_block))
        if error_block and self.config.print_error_block:
            llm_prompt.append(self._format_block('Error Block', error_block))
        llm_prompt.append(f'Prompt:\n{prompt.strip()}')

        return '\n\n'.join(llm_prompt)

    def _process_files(self, files: list[str]) -> list[str]:
        """Process the list of files and return their contents."""

        file_contents = []
        for file in files:
            try:
                content = Path(file).read_text(encoding='utf-8').strip()
                if self.config.print_file_content:
                    file_contents.append(f'File Name: {file}\nFile Content:\n```{self.config.markdown_language}\n{content}\n```\n')
            except OSError as e:
                print(f'Error reading file {file}: {e}')
        return file_contents

    def _format_block(self, block_type: str, content: str) -> str:
        """Format a block of content with markdown."""

        return f'{block_type}:\n```{self.config.markdown_language}\n{content.strip()}\n```'

    def clear_session(self) -> None:
        """Clear the session."""
        self.api.clear_session()
        self.printing_history = []
