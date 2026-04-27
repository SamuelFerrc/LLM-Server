from __future__ import annotations

import subprocess


class SubprocessCommandExecutor:
    def execute(self, command: str) -> str:
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
            )

            if result.stdout.strip():
                return result.stdout.strip()

            if result.stderr.strip():
                return result.stderr.strip()

            return "Comando executado."

        except Exception as error:
            return f"Erro ao executar comando: {error}"

