from fastapi import FastAPI
from fastapi.responses import FileResponse
import subprocess
import uuid
import os

app = FastAPI()

PIPER = "piper"
MODEL = "./voice-model/pt_BR-faber-medium.onnx"

def gerar_audio(texto):
    os.makedirs("aud", exist_ok=True)

    out_file = f"aud/{uuid.uuid4().hex}.wav"

    subprocess.run([
        PIPER,
        "--model", MODEL,
        "--output_file", out_file
    ], input=texto, text=True)

    return out_file


@app.get("/tts")
def tts(texto: str):
    audio = gerar_audio(texto)
    return FileResponse(audio, media_type="audio/wav")