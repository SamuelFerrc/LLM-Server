import os
from llama_cpp import Llama

model_dir = "model"

gguf_files = [f for f in os.listdir(model_dir) if f.endswith(".gguf")]

if not gguf_files:
    raise Exception("Nenhum modelo .gguf encontrado!")

model_path = os.path.join(model_dir, gguf_files[0])

print("Usando modelo:", model_path)

llm = Llama(
    model_path=model_path,
    n_threads=4
)

while True:
    prompt = input()
    if prompt == "quit":
        break

    print("Resposta:")

    for chunk in llm(
        prompt,
        max_tokens=100,
        stream=True  # 🔥 ISSO AQUI
    ):
        print(chunk["choices"][0]["text"], end="", flush=True)

    print("\n")