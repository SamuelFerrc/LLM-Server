from __future__ import annotations

from collections.abc import Callable

from cortex.application.prompts import (
    build_action_justification_prompt,
    build_assistant_prompt,
    build_command_output_prompt,
    build_google_search_prompt,
    build_need_google_prompt,
    build_summary_prompt,
)
from cortex.domain.models import ActionLogEntry, ConversationSession, SpeechAct
from cortex.domain.protocols import (
    CommandExecutor,
    CommandTranslator,
    SearchService,
    SpeechActClassifier,
    SpeechSynthesizer,
    TextModel,
)


DEFAULT_STOP_SEQUENCES = ["Usuario:", "\nUsuario:"]
ACTION_LOG_STOP_SEQUENCES = ["\n\n", "Acao:", "Usuario:"]


class ConversationService:
    def __init__(self, model: TextModel, session: ConversationSession):
        self._model = model
        self._session = session

    @property
    def session(self) -> ConversationSession:
        return self._session

    def generate_response(
        self,
        user_text: str,
        intention: str,
        *,
        max_tokens: int = 100,
        add_to_history: bool = True,
        prompt_override: str | None = None,
    ) -> str:
        task_prompt = prompt_override or user_text

        if add_to_history:
            self._session.message_counter += 1
            self._session.history.append(f"Usuario: {user_text}")

        prompt = build_assistant_prompt(self._session, intention, task_prompt)
        response = self._model.generate(
            prompt,
            max_tokens=max_tokens,
            stream=True,
            stop=DEFAULT_STOP_SEQUENCES,
        ).strip()

        if add_to_history:
            self._session.history.append(f"Assistente: {response}")

            if self._session.message_counter % self._session.summary_interval == 0:
                self.generate_summary()

        return response

    def generate_summary(self) -> str:
        full_text = "\n".join(self._session.history)
        summary_text = self._model.generate(
            build_summary_prompt(full_text),
            max_tokens=150,
        ).strip()

        print("\nNovo resumo gerado:\n", summary_text, "\n")

        self._session.history.clear()
        self._session.summary = summary_text
        return summary_text


class ResearchDeciderService:
    def __init__(self, model: TextModel):
        self._model = model

    def decide_from_prompt(self, prompt: str) -> str:
        return self._model.generate(prompt, max_tokens=5, stream=True).strip()

    def should_use_google(self, text: str) -> bool:
        raw_response = self.decide_from_prompt(build_need_google_prompt(text))
        return "1" in raw_response


class ActionLogService:
    def __init__(self, model: TextModel, session: ConversationSession):
        self._model = model
        self._session = session
        self._entries: list[ActionLogEntry] = []

    @property
    def entries(self) -> list[ActionLogEntry]:
        return list(self._entries)

    def add_log(self, action: str, justification: str | None = None) -> None:
        if justification is None:
            justification = self._model.generate(
                build_action_justification_prompt(self._session, action),
                max_tokens=80,
                stop=ACTION_LOG_STOP_SEQUENCES,
            ).strip()

        self._entries.append(
            ActionLogEntry(action=action, justification=justification)
        )

    def generate_log(self) -> str:
        if not self._entries:
            return "Nenhum registro de log."

        lines = ["LOG DE ACOES", ""]
        for index, item in enumerate(self._entries, start=1):
            lines.append(f"{index}. Acao: {item.action}")
            lines.append(f"   Justificativa: {item.justification}")
            lines.append("")

        return "\n".join(lines).strip()


class ActionService:
    def __init__(self, action_log_service: ActionLogService):
        self._action_log_service = action_log_service

    def execute_action(
        self,
        action_name: str,
        func: Callable[..., str],
        *args,
        **kwargs,
    ) -> str:
        result = func(*args, **kwargs)
        self._action_log_service.add_log(action_name)
        return result


class RequestProcessor:
    def __init__(
        self,
        *,
        speech_classifier: SpeechActClassifier,
        command_translator: CommandTranslator,
        conversation_service: ConversationService,
        research_decider: ResearchDeciderService,
        command_executor: CommandExecutor,
        search_service: SearchService,
        action_service: ActionService,
        max_tokens: int = 500,
        unknown_command_message: str = "Desculpa, nao entendi o que quis dizer",
    ):
        self._speech_classifier = speech_classifier
        self._command_translator = command_translator
        self._conversation_service = conversation_service
        self._research_decider = research_decider
        self._command_executor = command_executor
        self._search_service = search_service
        self._action_service = action_service
        self._max_tokens = max_tokens
        self._unknown_command_message = unknown_command_message

    def build_command_output(self, command_output: str) -> str:
        return build_command_output_prompt(command_output)

    def execute_command(self, command: str, action_name: str | None = None) -> str:
        label = action_name or f"Executar comando: {command}"
        return self._action_service.execute_action(
            label,
            self._command_executor.execute,
            command,
        )

    def execute_search(self, query: str) -> str:
        return self._action_service.execute_action(
            f"Pesquisar no Google: {query}",
            self._search_service.search_as_text,
            query,
        )

    def process(self, text: str) -> str:
        intention = self._speech_classifier.classify(text)
        print(f"Intencao detectada: {intention.value}")

        if intention is SpeechAct.ORDER:
            command = self._command_translator.translate(text)
            print(text, command)
            print(f"Comando detectado: {command}")

            if not command:
                return self._unknown_command_message

            command_output = self.execute_command(
                command,
                action_name=f"Executar comando do usuario: {command}",
            )
            return self.build_command_output(command_output)

        need_google = self._research_decider.should_use_google(text)
        print("Isso precisa de google?", int(need_google))

        if not need_google:
            return self._conversation_service.generate_response(
                text,
                intention.value,
                max_tokens=self._max_tokens,
            )

        search_output = self.execute_search(text)
        print(search_output)
        print("-" * 30)

        return self._conversation_service.generate_response(
            user_text=text,
            intention=intention.value,
            max_tokens=self._max_tokens,
            prompt_override=build_google_search_prompt(text, search_output),
        )


class VoiceAssistantService:
    def __init__(
        self,
        request_processor: RequestProcessor,
        speech_synthesizer: SpeechSynthesizer,
    ):
        self._request_processor = request_processor
        self._speech_synthesizer = speech_synthesizer

    def respond(self, text: str) -> str:
        return self._request_processor.process(text)

    def synthesize(self, text: str) -> bytes:
        response_text = self.respond(text)
        return self._speech_synthesizer.synthesize(response_text)
