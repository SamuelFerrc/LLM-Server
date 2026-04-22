import requests
import os

SERVER = "http://IP_DO_SEU_SERVIDOR:8000"

def falar(texto):
    r = requests.get(f"{SERVER}/tts", params={"texto": texto})

    with open("audio.wav", "wb") as f:
        f.write(r.content)

    os.system("start audio.wav")  # Windows


while True:
    txt = input("Digite: ")
    if txt == "sair":
        break

    falar(txt)