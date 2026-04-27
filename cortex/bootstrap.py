from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from cortex.application.prompts import DEFAULT_SYSTEM_PROMPT
from cortex.application.services import (
    ActionLogService,
    ActionService,
    ConversationService,
    RequestProcessor,
    ResearchDeciderService,
    VoiceAssistantService,
)
from cortex.domain.models import ConversationSession
from cortex.infrastructure.classifiers import RuleBasedSpeechActClassifier
from cortex.infrastructure.commands import FuzzyCommandTranslator, JsonCommandCatalog
from cortex.infrastructure.execution import SubprocessCommandExecutor


ROOT_DIR = Path(__file__).resolve().parent.parent
COMMANDS_PATH = ROOT_DIR / "commands.json"
TEXT_MODEL_DIR = ROOT_DIR / "text-model"
VOICE_MODEL_PATH = ROOT_DIR / "voice-model" / "pt_BR-faber-medium.onnx"


@dataclass(frozen=True)
class AssistantRuntime:
    conversation_service: ConversationService
    research_decider: ResearchDeciderService
    action_log_service: ActionLogService
    action_service: ActionService
    request_processor: RequestProcessor
    command_translator: FuzzyCommandTranslator
    speech_classifier: RuleBasedSpeechActClassifier
    command_executor: SubprocessCommandExecutor
    search_service: object


@dataclass(frozen=True)
class VoiceRuntime:
    assistant_runtime: AssistantRuntime
    speech_synthesizer: object
    voice_service: VoiceAssistantService


@lru_cache(maxsize=1)
def create_speech_classifier() -> RuleBasedSpeechActClassifier:
    return RuleBasedSpeechActClassifier()


@lru_cache(maxsize=1)
def create_command_translator() -> FuzzyCommandTranslator:
    catalog = JsonCommandCatalog(COMMANDS_PATH)
    return FuzzyCommandTranslator(catalog)


@lru_cache(maxsize=1)
def create_search_service():
    from cortex.infrastructure.search import DDGSWebSearchService

    return DDGSWebSearchService()


@lru_cache(maxsize=1)
def create_assistant_runtime() -> AssistantRuntime:
    from cortex.infrastructure.llm import LlamaTextModel

    model = LlamaTextModel(TEXT_MODEL_DIR)
    session = ConversationSession(system_prompt=DEFAULT_SYSTEM_PROMPT)
    conversation_service = ConversationService(model, session)
    action_log_service = ActionLogService(model, session)
    research_decider = ResearchDeciderService(model, action_log_service)
    action_service = ActionService(action_log_service)
    command_translator = create_command_translator()
    speech_classifier = create_speech_classifier()
    command_executor = SubprocessCommandExecutor()
    search_service = create_search_service()
    request_processor = RequestProcessor(
        speech_classifier=speech_classifier,
        command_translator=command_translator,
        conversation_service=conversation_service,
        research_decider=research_decider,
        command_executor=command_executor,
        search_service=search_service,
        action_service=action_service,
    )

    return AssistantRuntime(
        conversation_service=conversation_service,
        research_decider=research_decider,
        action_log_service=action_log_service,
        action_service=action_service,
        request_processor=request_processor,
        command_translator=command_translator,
        speech_classifier=speech_classifier,
        command_executor=command_executor,
        search_service=search_service,
    )


@lru_cache(maxsize=1)
def create_voice_runtime() -> VoiceRuntime:
    from cortex.infrastructure.tts import PiperSpeechSynthesizer

    assistant_runtime = create_assistant_runtime()
    speech_synthesizer = PiperSpeechSynthesizer(VOICE_MODEL_PATH)
    voice_service = VoiceAssistantService(
        assistant_runtime.request_processor,
        speech_synthesizer,
    )
    return VoiceRuntime(
        assistant_runtime=assistant_runtime,
        speech_synthesizer=speech_synthesizer,
        voice_service=voice_service,
    )


def create_fastapi_app():
    from cortex.api import create_app

    return create_app(create_voice_runtime().voice_service)
