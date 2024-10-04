from api.gemini_api import GeminiAPI
from app import App, Config
from utils.configs import gemini_settings
from utils.functions import read_system_prompt


def main():
    gemini = GeminiAPI(
        api_key=gemini_settings.api_key,
        model=gemini_settings.models.GEMINI_FLASH.value,
        system_prompt=read_system_prompt('general_assistant'),
    )
    
    app = App(api=gemini, config=Config(markdown_language='python', print_file_content=True, print_code_block=False))

    code_block = r"""
    def add(a, b):
        return a + b
    """

    error_block = r"""
    Traceback (most recent call last):
      File "main.py", line 1, in <module>
        def add(a, b):
      File "main.py", line 2, in add
        return a + b
    TypeError: unsupported operand type(s) for +: 'int' and 'str'
    """

    app.send_message('Describe what is in my prompt', code_block, error_block)


if __name__ == '__main__':
    main()
