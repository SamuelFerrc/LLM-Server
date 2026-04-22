import requests
import winsound

SERVER = "http://"

def falar(texto):
    r = requests.get(f"{SERVER}/tts", params={"texto": texto})
    r.raise_for_status()

    # Reproduz o WAV recebido sem salvar um arquivo local.
    winsound.PlaySound(r.content, winsound.SND_MEMORY)


while True:
    txt = input("Digite: ")
    if txt == "sair":
        break

    falar(txt)
