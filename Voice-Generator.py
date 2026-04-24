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
    print("gerar_audio(): " + intention)
    if intention != "ORDEM":
        response = generate_response(text, intention,50)
    else:
        cmd_response = generate_command(text)
        if cmd_response != "":
            response = generate_response(f"Você vai usar este comando '{cmd_response}', siga a seguinte ordem na sua fala, inicialmente confirme que irá realizar a tarefa, depois diga qual comando irá usar, não precisa explicar o comando", intention,50)
        else:
            response = "Desculpa, não entendi o que quis dizer"
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
