from __future__ import annotations

from cortex.domain.models import SpeechAct
from cortex.shared.text_utils import normalize_text, strip_accents


QUESTION_MARKERS = [
    "o que",
    "como",
    "quando",
    "onde",
    "por que",
    "porque",
    "qual",
    "quais",
    "quem",
    "quanto",
    "quantos",
]

COMMAND_VERBS = [
    "abra",
    "feche",
    "execute",
    "rode",
    "crie",
    "delete",
    "remova",
    "instale",
    "inicie",
    "pare",
    "desligue",
    "ligue",
    "mostre",
    "liste",
    "copie",
    "mova",
    "renomeie",
    "quero que",
    "faca",
    "isto e uma ordem",
    "mostrar noticias",
]

POLITE_MARKERS = [
    "pode",
    "poderia",
    "consegue",
    "conseguiria",
    "tem como",
    "seria possivel",
    "da pra",
    "vc pode",
]

SUGGESTION_MARKERS = [
    "talvez",
    "acho que",
    "poderia tentar",
    "seria bom",
    "recomendo",
    "seria interessante",
    "voce deveria",
]

TECH_INSTRUCTION_MARKERS = [
    "passo",
    "primeiro",
    "depois",
    "em seguida",
    "execute o comando",
    "use o comando",
    "faca o seguinte",
]


class RuleBasedSpeechActClassifier:
    def normalize(self, text: str) -> str:
        return strip_accents(normalize_text(text))

    def has_question(self, text: str) -> bool:
        normalized = self.normalize(text)
        return "?" in text or any(marker in normalized for marker in QUESTION_MARKERS)

    def has_command_verb(self, text: str) -> bool:
        normalized = self.normalize(text)
        return any(marker in normalized for marker in COMMAND_VERBS)

    def has_polite_request(self, text: str) -> bool:
        normalized = self.normalize(text)
        return any(marker in normalized for marker in POLITE_MARKERS)

    def has_suggestion(self, text: str) -> bool:
        normalized = self.normalize(text)
        return any(marker in normalized for marker in SUGGESTION_MARKERS)

    def has_instruction(self, text: str) -> bool:
        normalized = self.normalize(text)
        return any(marker in normalized for marker in TECH_INSTRUCTION_MARKERS)

    def classify(self, text: str) -> SpeechAct:
        normalized = self.normalize(text)

        if "quero que" in normalized:
            return SpeechAct.ORDER

        question = self.has_question(text)
        command = self.has_command_verb(normalized)
        polite = self.has_polite_request(normalized)
        suggestion = self.has_suggestion(normalized)
        instruction = self.has_instruction(normalized)

        if question and not command:
            return SpeechAct.QUESTION

        if command and not polite:
            return SpeechAct.ORDER

        if command and polite:
            return SpeechAct.ORDER

        if instruction:
            return SpeechAct.ORDER

        if suggestion:
            return SpeechAct.SUGGESTION

        return SpeechAct.NEUTRAL
