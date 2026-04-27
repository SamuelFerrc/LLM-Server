from __future__ import annotations

from pathlib import Path
from typing import Sequence

from llama_cpp import Llama


class LlamaTextModel:
    def __init__(
        self,
        model_dir: str | Path,
        *,
        n_ctx: int = 4096,
        n_threads: int = 8,
    ):
        self._model_path = self._resolve_model_path(model_dir)
        print("Usando modelo:", self._model_path)
        self._llm = Llama(
            model_path=str(self._model_path),
            n_ctx=n_ctx,
            n_threads=n_threads,
        )

    @staticmethod
    def _resolve_model_path(model_dir: str | Path) -> Path:
        directory = Path(model_dir)
        gguf_files = sorted(directory.glob("*.gguf"))

        if not gguf_files:
            raise FileNotFoundError("Nenhum modelo .gguf encontrado!")

        return gguf_files[0]

    def generate(
        self,
        prompt: str,
        *,
        max_tokens: int,
        stream: bool = False,
        stop: Sequence[str] | None = None,
    ) -> str:
        kwargs: dict[str, object] = {
            "max_tokens": max_tokens,
        }

        if stop:
            kwargs["stop"] = list(stop)

        if stream:
            response = ""
            for chunk in self._llm(prompt, stream=True, **kwargs):
                token = chunk["choices"][0]["text"]
                response += token
                print(token, end="", flush=True)

            print()
            return response.strip()

        response = self._llm(prompt, **kwargs)["choices"][0]["text"]
        return response.strip()

