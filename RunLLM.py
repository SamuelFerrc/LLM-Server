import os
from llama_cpp import Llama

model_dir = "text-model"

gguf_files = [f for f in os.listdir(model_dir) if f.endswith(".gguf")]

if not gguf_files:
    raise Exception("Nenhum modelo .gguf encontrado!")

model_path = os.path.join(model_dir, gguf_files[0])

print("Usando modelo:", model_path)

llm = Llama(
    model_path=model_path,
    n_threads=4
)

def gerar_resposta(prompt: str, max_tokens: int = 100) -> str:
    resposta = ""

    for chunk in llm(
        prompt,
        max_tokens=max_tokens,
        stream=True
    ):
        resposta += chunk["choices"][0]["text"]

    return resposta
