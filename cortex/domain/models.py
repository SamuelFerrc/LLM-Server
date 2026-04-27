from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class SpeechAct(str, Enum):
    QUESTION = "PERGUNTA"
    ORDER = "ORDEM"
    SUGGESTION = "SUGESTAO"
    NEUTRAL = "NEUTRO"


@dataclass(frozen=True)
class CommandDefinition:
    name: str
    examples: list[str]
    command: str | None = None
    template: str | None = None


@dataclass(frozen=True)
class CommandMatch:
    definition: CommandDefinition
    matched_example: str
    score: float


@dataclass(frozen=True)
class SearchResult:
    title: str
    url: str
    content: str


@dataclass(frozen=True)
class ActionLogEntry:
    action: str
    justification: str


@dataclass
class ConversationSession:
    system_prompt: str
    summary_interval: int = 5
    history: list[str] = field(default_factory=list)
    summary: str = ""
    message_counter: int = 0

