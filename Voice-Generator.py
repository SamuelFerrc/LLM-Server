from fastapi import FastAPI
from fastapi.responses import Response
from io import BytesIO
from pathlib import Path
import wave
from piper import PiperVoice
from RunLLMTalk import generate_response
from RunLLMToOrder import generate_command
from SpeechActs import classify_speech_act

app = FastAPI()
MODEL = "./voice-model/pt_BR-faber-medium.onnx"
VOICE = PiperVoice.load(Path(MODEL))

def gerar_audio(text):
    global count
    intention = classify_speech_act(text)
    if intention != "ORDEM":
        response = generate_response(text, intention,50)
    else:
        cmd_response = generate_command(text)
        response = generate_response(f"Você vai usar este comando '{cmd_response}', fale sobre ele como se estivesse apresentando ele", intention,50)

    print("gerar_audio(): " + intention)
    if intention == "ORDEM":
        print("gerar_audio(): " + cmd_response)

    with BytesIO() as buffer:
        with wave.open(buffer, "wb") as wav_file:
            VOICE.synthesize_wav(response, wav_file)
        return buffer.getvalue()


@app.get("/tts")
def tts(text: str):
    audio = gerar_audio(text)
    return Response(content=audio, media_type="audio/wav")
