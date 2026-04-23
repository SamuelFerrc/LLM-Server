import os
import json
from llama_cpp import Llama

model_dir = "text-model"

gguf_files = [f for f in os.listdir(model_dir) if f.endswith(".gguf")]

if not gguf_files:
    raise Exception("Nenhum modelo .gguf encontrado!")

model_path = os.path.join(model_dir, gguf_files[0])

llm = Llama(
    model_path=model_path,
    n_threads=2
)

# 🔹 carregar comandos
with open("commands.json", "r", encoding="utf-8") as f:
    COMMANDS = json.load(f)


def build_prompt(user_input: str) -> str:
    intents = []

    for intent, data in COMMANDS.items():
        examples = ", ".join(data["examples"])
        intents.append(f"{intent}: {examples}")

    intents_text = "\n".join(intents)

    return f"""
Escolha a intenção mais próxima da frase do usuário.

Intenções disponíveis:
{intents_text}

Frase: {user_input}

Responda APENAS com o nome da intenção.
"""


def generate_command(user_input: str) -> str:
    prompt = build_prompt(user_input)

    response = llm(
        prompt,
        max_tokens=10,
        temperature=0.0,
        stop=["\n"]
    )

    intent = response["choices"][0]["text"].strip()

    # segurança: se não existir, retorna vazio
    if intent not in COMMANDS:
        return ""

    # 🔥 RETORNO FINAL: APENAS O COMANDO
    return COMMANDS[intent]["command"]


# 🔹 loop
while True:
    user_input = input(">> ")

    command = generate_command(user_input)
    print(command)