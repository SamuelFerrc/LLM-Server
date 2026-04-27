from __future__ import annotations

from typing import Protocol, Sequence

from .models import SearchResult, SpeechAct


class TextModel(Protocol):
    def generate(
        self,
        prompt: str,
        *,
        max_tokens: int,
        stream: bool = False,
        stop: Sequence[str] | None = None,
    ) -> str:
        ...


class SpeechActClassifier(Protocol):
    def classify(self, text: str) -> SpeechAct:
        ...


class CommandTranslator(Protocol):
    def translate(self, text: str) -> str | None:
        ...


class CommandExecutor(Protocol):
    def execute(self, command: str) -> str:
        ...


class SearchService(Protocol):
    def search(self, query: str, limit: int = 3) -> list[SearchResult]:
        ...

    def search_as_text(self, query: str, limit: int = 3) -> str:
        ...


class SpeechSynthesizer(Protocol):
    def synthesize(self, text: str) -> bytes:
        ...

