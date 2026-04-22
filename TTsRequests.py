import requests
import os

SERVER = "http://192.168.1.15:8000"

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