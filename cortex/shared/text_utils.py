from __future__ import annotations

import re
import unicodedata


def normalize_text(text: str) -> str:
    return " ".join(text.lower().strip().split())


def strip_accents(text: str) -> str:
    return "".join(
        char
        for char in unicodedata.normalize("NFD", text)
        if unicodedata.category(char) != "Mn"
    )


def normalize_command_text(text: str) -> str:
    normalized = strip_accents(normalize_text(text))
    normalized = normalized.replace("noticias", "noticia")
    normalized = re.sub(r"[^\w\s]", "", normalized)
    return " ".join(normalized.split())

