from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import Response

from cortex.application.services import VoiceAssistantService


def create_app(voice_assistant_service: VoiceAssistantService) -> FastAPI:
    app = FastAPI()

    @app.get("/tts")
    def tts(text: str):
        audio = voice_assistant_service.synthesize(text)
        return Response(content=audio, media_type="audio/wav")

    return app

