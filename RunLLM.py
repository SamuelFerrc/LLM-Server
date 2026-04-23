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

# 🔹 contexto inicial fixo (em português)
SYSTEM_PROMPT = """Você é um assistente útil, direto e técnico.
Responda de forma clara e objetiva."""

# 🔹 memória
history = []
summary = ""
message_counter = 0


def generate_response(prompt: str, max_tokens: int = 100) -> str:
    global message_counter, summary, history

    message_counter += 1

    history.append(f"Usuário: {prompt}")

    context = SYSTEM_PROMPT + "\n\n"

    if summary:
        context += f"Resumo da conversa até agora:\n{summary}\n\n"

    context += "\n".join(history[-10:])
    context += "\nAssistente:"

    response = ""

    for chunk in llm(
        context,
        max_tokens=max_tokens,
        stream=True
    ):
        token = chunk["choices"][0]["text"]
        response += token
        print(token, end="", flush=True)

    print()

    history.append(f"Assistente: {response}")

    if message_counter % 5 == 0:
        summary = generate_summary()

    return response


def generate_summary() -> str:
    global history

    full_text = "\n".join(history)

    prompt = f"""
Resuma a conversa abaixo de forma curta e objetiva:

{full_text}

Resumo:
"""

    summary_text = llm(prompt, max_tokens=150)["choices"][0]["text"]

    print("\n📌 Novo resumo gerado:\n", summary_text, "\n")

    # limpa histórico
    history = []

    return summary_text