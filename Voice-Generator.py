import os
import subprocess
import uuid

PIPER = r"C:\piper\piper.exe"
MODEL = r"voice-model\pt_BR-faber-medium.onnx"

def gerar_e_tocar(texto):
    out_file = f"aud\out_{uuid.uuid4().hex}.wav"

    subprocess.run([
        PIPER,
        "--model", MODEL,
        "--output_file", out_file
    ], input=texto, text=True)

    # toca o áudio
    subprocess.Popen(["start", out_file], shell=True)

    return out_file

gerar_e_tocar("Oi Samuel ama Raquel muito")