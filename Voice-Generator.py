from fastapi import FastAPI
from fastapi.responses import Response
from io import BytesIO
from pathlib import Path
import wave
from piper import PiperVoice
from RunLLM import gerar_resposta

app = FastAPI()

MODEL = "./voice-model/pt_BR-faber-medium.onnx"
VOICE = PiperVoice.load(Path(MODEL))

def gerar_audio(texto):
    resposta = gerar_resposta(texto)

    with BytesIO() as buffer:
        with wave.open(buffer, "wb") as wav_file:
            VOICE.synthesize_wav(resposta, wav_file)
        return buffer.getvalue()


@app.get("/tts")
def tts(texto: str):
    audio = gerar_audio(texto)
    return Response(content=audio, media_type="audio/wav")
