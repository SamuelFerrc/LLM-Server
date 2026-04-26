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
    n_ctx=4096,
    n_threads=8

)

# 🔹 contexto inicial fixo (em português)
SYSTEM_PROMPT = """Você se chama Cortex é um assistente útil, direto e técnico.
Responda de forma clara e objetiva."""

# 🔹 memória
history = []
summary = ""
message_counter = 0

def need_google(prompt: str) -> str:
    response = ""

    for chunk in llm(
        prompt,
        max_tokens=5,
        stream=True
    ):
        token = chunk["choices"][0]["text"]
        response += token
        print(token, end="", flush=True)

    print()
    return response.strip()

def generate_response(prompt: str, intention: str, max_tokens: int = 100, historyAdd: bool = True) -> str:
    global message_counter, summary, history

    if historyAdd:
        message_counter += 1
        history.append(f"O usuario te enviou uma mensagem com a inteção de {intention}")
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
    if historyAdd:
        history.append(f"Assistente: {response}")

        if message_counter % 5 == 0:
          summary = generate_summary()
    print(history)
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
