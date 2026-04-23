import requests
import winsound
import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel

SERVER = "http://"

model = WhisperModel(
    "small",
    device="cpu",
    compute_type="int8"
)

samplerate = 16000
block_duration = 3


def falar(texto):
    r = requests.get(f"{SERVER}/tts", params={"texto": texto})
    r.raise_for_status()
    winsound.PlaySound(r.content, winsound.SND_MEMORY)


def ouvir_microfone():
    print("🎤 Fale algo...")

    audio = sd.rec(
        int(block_duration * samplerate),
        samplerate=samplerate,
        channels=1,
        dtype=np.float32
    )

    sd.wait()
    audio = np.squeeze(audio)

    segments, _ = model.transcribe(audio, language="pt")

    texto_final = ""

    for segment in segments:
        texto_final += segment.text + " "

    return texto_final.strip()


while True:
    input("Pressione ENTER para falar...")

    texto = ouvir_microfone()

    print("📝 Você disse:", texto)

    if texto.lower() == "sair":
        break

    if texto:
        falar(texto)