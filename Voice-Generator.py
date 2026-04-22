import subprocess
import uuid
import os

PIPER = "piper"
MODEL = "./voice-model/pt_BR-faber-medium.onnx"

def gerar_e_tocar(texto):
    os.makedirs("aud", exist_ok=True)

    out_file = f"aud/out_{uuid.uuid4().hex}.wav"

    subprocess.run([
        PIPER,
        "--model", MODEL,
        "--output_file", out_file
    ], input=texto, text=True)

    subprocess.Popen(["aplay", out_file])

    return out_file


gerar_e_tocar("Oi, rodando no servidor")