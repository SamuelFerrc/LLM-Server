from cortex.application.prompts import build_google_search_prompt, build_need_google_prompt
from cortex.bootstrap import (
    create_assistant_runtime,
    create_fastapi_app,
    create_voice_runtime,
)


_assistant_runtime = create_assistant_runtime()
_voice_runtime = create_voice_runtime()

MAX_TOKENS = 500
UNKNOWN_COMMAND_MESSAGE = "Desculpa, nao entendi o que quis dizer"

app = create_fastapi_app()


def speech_acts(text: str) -> str:
    return _assistant_runtime.speech_classifier.classify(text).value


def get_command(text: str) -> str:
    return _assistant_runtime.command_translator.translate(text) or ""


def execute_command(command: str, action_name: str = None):
    return _assistant_runtime.request_processor.execute_command(command, action_name)


def generate_response_cmd(command: str, intention: str, action_name: str = None) -> str:
    del intention
    command_output = execute_command(command, action_name=action_name)
    return _assistant_runtime.request_processor.build_command_output(command_output)


def sintet_aud(texto: str) -> bytes:
    return _voice_runtime.voice_service.synthesize(texto)


def need_google_prompt(text: str):
    return build_need_google_prompt(text)


def google_search_prompt(searched: str, result: str) -> str:
    return build_google_search_prompt(searched, result)


def process_requis(text: str) -> str:
    return _assistant_runtime.request_processor.process(text)
