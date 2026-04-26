import subprocess

from fastapi import FastAPI
from fastapi.responses import Response
from io import BytesIO
from pathlib import Path
import wave

from piper import PiperVoice
from RunLLMTalk import generate_response, need_google
from TranslateToOrder import generate_command
from SpeechActs import classify_speech_act


# =========================
# Configuração
# =========================

MODEL_PATH = "./voice-model/pt_BR-faber-medium.onnx"
MAX_TOKENS = 50
UNKNOWN_COMMAND_MESSAGE = "Desculpa, não entendi o que quis dizer"

app = FastAPI()
VOICE = PiperVoice.load(Path(MODEL_PATH))


# =========================
# Intent Service
# =========================

def speech_acts(text: str) -> str:
    return classify_speech_act(text)


# =========================
# Command Service
# =========================

def get_command(text: str) -> str:
    return generate_command(text)



def execute_command(command: str):

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )

        if result.stdout.strip():
            return result.stdout.strip()

        if result.stderr.strip():
            return result.stderr.strip()

        return "Comando executado."

    except Exception as e:
        return f"Erro ao executar comando: {e}"

def generate_response_cmd(text: str, intention: str) -> str:

    command_output = execute_command(
        text
    )
    prompt = (
        f"Essas são os resultados.\n"
        f"\n{command_output}\n"
    )
   # print(command_output)
    return prompt


# =========================
# TTS Service
# =========================

def sintet_aud(texto: str) -> bytes:

    response = process_requis(texto)

    with BytesIO() as buffer:
        with wave.open(buffer, "wb") as wav_file:
            VOICE.synthesize_wav(
                response,
                wav_file
            )

        return buffer.getvalue()


# =========================
# Pipeline Principal
# =========================
def need_google_prompt(text: str):
    prompt = f"""
Você é um classificador binário.

Decida se a mensagem do usuário precisa de pesquisa no Google para responder corretamente.

Responda APENAS com:
1  -> precisa pesquisar
0  -> não precisa pesquisar

Retorne 1 se envolver:
- tutoriais ou ensinamentos
- notícias ou eventos recentes
- informações que mudam com o tempo
- preços, clima, eleições, cotações
- "hoje", "agora", "últimas", "recentes"
- fatos atuais sobre pessoas, empresas, produtos
- necessidade de consultar fontes externas

Retorne 0 se for:
- conhecimento geral estável
- explicações conceituais ou históricas
- programação
- matemática ou lógica
- conversa casual
- tarefas criativas

Mensagem:
{text}

Resposta (somente 0 ou 1):
"""
    return prompt

def google_search_prompt(searched: str, result: str) -> str:
    return f"""
Você é um assistente que responde perguntas com base em resultados de busca do Google.

Pergunta pesquisada:
{searched}

Resultados encontrados:
{result}

Tarefa:
Use apenas as informações dos resultados acima para gerar uma explicação clara, objetiva e informativa que responda à pergunta pesquisada.

Regras:
- Resuma e integre as informações encontradas.
- Explique em linguagem natural, como uma resposta para o usuário.
- Se houver múltiplas fontes ou perspectivas, combine-as em uma resposta coerente.
- Se os resultados forem insuficientes ou ambíguos, diga isso explicitamente.
- Não mencione "com base nos resultados" ou "as fontes dizem"; apenas responda diretamente.
- Não invente fatos fora do conteúdo fornecido.

Resposta:
"""
def process_requis(text: str) -> str:

    intention = speech_acts(text)

    print(f"Intenção detectada: {intention}")

    if intention == "ORDEM":
        command = get_command(text)
        print(text, command)
        print(f"Comando detectado: {command}")

        if not command:
            return UNKNOWN_COMMAND_MESSAGE

        return generate_response_cmd(
            command,
            intention,
        )

    needGoogle = need_google(
        need_google_prompt(text),
    )
    print("Isso precisa de google?", needGoogle)
    if needGoogle == '0':
        response = "NÃO PRECISA DE GOOGLE"
        #response = generate_response(        text, intention,            MAX_TOKENS)
    else:
        google_search = generate_response_cmd(f"python .\\GoogleSearch\\GoogleSearch.py '{text}'", "question")
        print(google_search)
        print("-"*30)
        prompt = google_search_prompt(text, google_search)

        response = generate_response(
            prompt,
            intention,
            MAX_TOKENS
        )
    return response


# =========================
# API
# =========================

@app.get("/tts")
def tts(text: str):

    audio = sintet_aud(text)

    return Response(
        content=audio,
        media_type="audio/wav"
    )