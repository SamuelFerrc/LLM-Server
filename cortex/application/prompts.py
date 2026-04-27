from __future__ import annotations

from cortex.domain.models import ConversationSession


DEFAULT_SYSTEM_PROMPT = (
    "Voce se chama Cortex e e um assistente util, direto e tecnico.\n"
    "Responda de forma clara e objetiva."
)


def build_assistant_prompt(
    session: ConversationSession,
    intention: str,
    current_message: str,
) -> str:
    context = session.system_prompt + "\n\n"

    if session.summary:
        context += f"Resumo da conversa ate agora:\n{session.summary}\n\n"

    if session.history:
        context += "\n".join(session.history[-10:])

    context += f"\n\nIntencao da mensagem atual: {intention}"
    context += "\nResponda somente como assistente, sem mencionar a intencao."
    context += f"\nMensagem atual:\n{current_message}"
    context += "\nAssistente:"
    return context


def build_summary_prompt(full_text: str) -> str:
    return (
        "Resuma a conversa abaixo de forma curta e objetiva:\n\n"
        f"{full_text}\n\n"
        "Resumo:\n"
    )


def build_action_justification_prompt(
    session: ConversationSession,
    action: str,
) -> str:
    context = session.system_prompt + "\n\n"

    if session.summary:
        context += f"Resumo da conversa ate agora:\n{session.summary}\n\n"

    context += "Historico recente:\n"
    context += "\n".join(session.history[-10:])

    context += (
        "\n\nCom base no historico da conversa, justifique de forma curta e objetiva "
        "a acao abaixo.\n\n"
        f"Acao realizada:\n{action}\n\n"
        "Justificativa:\n"
    )
    return context


def build_need_google_prompt(text: str) -> str:
    return f"""
Voce e um classificador binario chamado Cortex.

Decida se a mensagem do usuario precisa de pesquisa no Google para responder corretamente.

Responda APENAS com:
1  -> precisa pesquisar
0  -> nao precisa pesquisar

Retorne 1 se envolver:
- tutoriais ou ensinamentos
- noticias ou eventos recentes
- informacoes que mudam com o tempo
- precos, clima, eleicoes, cotacoes
- "hoje", "agora", "ultimas", "recentes"
- fatos atuais sobre pessoas, empresas, produtos
- necessidade de consultar fontes externas

Retorne 0 se for:
- conhecimento geral estavel
- explicacoes conceituais ou historicas
- programacao
- matematica ou logica
- conversa casual
- tarefas criativas

Mensagem:
{text}

Resposta (somente 0 ou 1):
""".strip()


def build_google_search_prompt(searched: str, result: str) -> str:
    return f"""
Voce e um assistente chamado Cortex, que responde perguntas com base em resultados de busca do Google.

Pergunta pesquisada:
{searched}

Resultados encontrados:
{result}

Tarefa:
Use apenas as informacoes dos resultados acima para gerar uma explicacao clara, objetiva e informativa que responda a pergunta pesquisada.

Regras:
- Resuma e integre as informacoes encontradas.
- Explique em linguagem natural, como uma resposta para o usuario.
- Se houver multiplas fontes ou perspectivas, combine-as em uma resposta coerente.
- Se os resultados forem insuficientes ou ambiguos, diga isso explicitamente.
- Nao mencione "com base nos resultados" ou "as fontes dizem"; apenas responda diretamente.
- Nao invente fatos fora do conteudo fornecido.

Resposta:
""".strip()


def build_command_output_prompt(command_output: str) -> str:
    return f"Essas sao os resultados.\n\n{command_output}\n"

