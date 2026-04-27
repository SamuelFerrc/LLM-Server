from __future__ import annotations

from io import BytesIO
from pathlib import Path
import wave

from piper import PiperVoice


class PiperSpeechSynthesizer:
    def __init__(self, model_path: str | Path):
        self._voice = PiperVoice.load(Path(model_path))

    def synthesize(self, text: str) -> bytes:
        with BytesIO() as buffer:
            with wave.open(buffer, "wb") as wav_file:
                self._voice.synthesize_wav(text, wav_file)

            return buffer.getvalue()

