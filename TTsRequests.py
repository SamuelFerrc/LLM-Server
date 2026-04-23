import requests
import winsound
import sounddevice as sd
import queue
import json
from vosk import Model, KaldiRecognizer

SERVER = "http://192.168.1.15:8000"

# Caminho da pasta do modelo Vosk (ajuste aqui)
model_path = "voice-model/vosk-model-small-pt-0.3"

model = Model(model_path)

samplerate = 16000
q = queue.Queue()


def falar(texto):
    r = requests.get(f"{SERVER}/tts", params={"texto": texto})
    r.raise_for_status()
    winsound.PlaySound(r.content, winsound.SND_MEMORY)


def callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(bytes(indata))


def ouvir_microfone():
    print("🎤 Fale algo...")

    rec = KaldiRecognizer(model, samplerate)

    with sd.RawInputStream(
        samplerate=samplerate,
        blocksize=8000,
        dtype="int16",
        channels=1,
        callback=callback
    ):
        texto_final = ""

        while True:
            data = q.get()

            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                texto_final += result.get("text", "")
                break

        return texto_final.strip()


while True:
    input("Pressione ENTER para falar...")

    texto = ouvir_microfone()

    print("📝 Você disse:", texto)

    if texto.lower() == "sair":
        break

    if texto:
        falar(texto)