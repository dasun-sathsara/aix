from aix.api.openai_api import OpenAI_API
from aix.conversation_manager import Config, ConversationHandler
from aix.utils.configs import openai_settings
from aix.utils.functions import read_system_prompt

openai_api = OpenAI_API(
    api_key=openai_settings.api_key,
    model=openai_settings.models.GPT4O_MINI.value,
    system_prompt=read_system_prompt('general_assistant'),
)

app = ConversationHandler(api=openai_api)

app.set_config(
    Config(print_code_block=True, print_error_block=True, print_file_content=True, save_conversation=True, markdown_language='python')
)

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

prompt = 'Explain this code block'

print('sending ')
app.send_message(prompt, code_block, error_block)
