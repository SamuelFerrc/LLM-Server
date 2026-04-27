from __future__ import annotations

import json
import sys
from pathlib import Path
from difflib import SequenceMatcher

try:
    from rapidfuzz import fuzz
except ImportError:  # pragma: no cover - fallback for minimal Python setups
    fuzz = None

from cortex.domain.models import CommandDefinition, CommandMatch
from cortex.shared.text_utils import normalize_command_text


class JsonCommandCatalog:
    def __init__(self, commands_path: str | Path):
        self._commands_path = Path(commands_path)
        self._commands = self._load_commands()

    def _load_commands(self) -> dict[str, CommandDefinition]:
        raw_commands = json.loads(self._commands_path.read_text(encoding="utf-8"))
        return {
            name: CommandDefinition(
                name=name,
                examples=data["examples"],
                command=data.get("command"),
                template=data.get("template"),
            )
            for name, data in raw_commands.items()
        }

    def items(self) -> list[tuple[str, CommandDefinition]]:
        return list(self._commands.items())

    def get(self, name: str) -> CommandDefinition:
        return self._commands[name]


class FuzzyCommandTranslator:
    def __init__(
        self,
        catalog: JsonCommandCatalog,
        *,
        python_executable: str | None = None,
        threshold: int = 60,
    ):
        self._catalog = catalog
        self._python_executable = python_executable or sys.executable
        self._threshold = threshold

    def normalize(self, text: str) -> str:
        return normalize_command_text(text)

    def similarity(self, left: str, right: str) -> float:
        normalized_left = self.normalize(left)
        normalized_right = self.normalize(right)

        if fuzz is not None:
            return fuzz.token_set_ratio(normalized_left, normalized_right)

        return SequenceMatcher(None, normalized_left, normalized_right).ratio() * 100

    def detect_intent(self, user_input: str) -> CommandMatch | None:
        text = self.normalize(user_input)
        best_match: CommandMatch | None = None

        for _, definition in self._catalog.items():
            for example in definition.examples:
                clean_example = example.replace("X", "").strip()
                score = self.similarity(text, clean_example)

                if best_match is None or score > best_match.score:
                    best_match = CommandMatch(
                        definition=definition,
                        matched_example=clean_example,
                        score=score,
                    )

        if best_match is None:
            print("Intent=None score=0")
            return None

        print(f"Intent={best_match.definition.name} score={best_match.score}")

        if best_match.score < self._threshold:
            return None

        return best_match

    def extract_argument(self, user_input: str, matched_example: str) -> str:
        text = self.normalize(user_input)
        prefix = self.normalize(matched_example)

        if text.startswith(prefix):
            return text[len(prefix) :].strip()

        words = prefix.split()
        if len(words) >= 2:
            pivot = " ".join(words[-2:])
            pivot_index = text.find(pivot)

            if pivot_index != -1:
                return text[pivot_index + len(pivot) :].strip()

        return ""

    def translate(self, user_input: str) -> str | None:
        match = self.detect_intent(user_input)

        if match is None:
            return None

        definition = match.definition

        if definition.command:
            return definition.command

        if definition.template:
            argument = self.extract_argument(user_input, match.matched_example)

            if not argument:
                return None

            return definition.template.format(
                query=argument,
                arg=argument,
                value=argument,
                python=self._python_executable,
            )

        return None
