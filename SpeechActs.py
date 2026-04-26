import re

def normalize(text):
    return text.lower().strip()


# -----------------------------
# DETECTORES BASE
# -----------------------------

QUESTION_MARKERS = [
    "o que", "como", "quando", "onde", "por que", "porque",
    "qual", "quais", "quem", "quanto", "quantos"
]

COMMAND_VERBS = [
    "abra", "feche", "execute", "rode", "crie", "delete",
    "remova", "instale", "inicie", "pare", "desligue", "ligue",
    "mostre", "liste", "copie", "mova", "renomeie", "quero que", "faça",
    "isto é uma ordem", "mostrar noticias"
]

POLITE_MARKERS = [
    "pode", "poderia", "consegue", "conseguiria",
    "tem como", "seria possível", "dá pra", "vc pode"
]

SUGGESTION_MARKERS = [
    "talvez", "acho que", "poderia tentar", "seria bom",
    "recomendo", "seria interessante", "você deveria"
]

TECH_INSTRUCTION_MARKERS = [
    "passo", "primeiro", "depois", "em seguida",
    "execute o comando", "use o comando", "faça o seguinte"
]


# -----------------------------
# FEATURES
# -----------------------------

def has_question(text):
    return "?" in text or any(q in text for q in QUESTION_MARKERS)

def has_command_verb(text):
    return any(v in text for v in COMMAND_VERBS)

def has_polite_request(text):
    return any(p in text for p in POLITE_MARKERS)

def has_suggestion(text):
    return any(s in text for s in SUGGESTION_MARKERS)

def has_instruction(text):
    return any(t in text for t in TECH_INSTRUCTION_MARKERS)


# -----------------------------
# CLASSIFICADOR PRINCIPAL
# -----------------------------

def classify_speech_act(text):
    text = normalize(text)
    if "quero que" in text.lower():
        return "ORDEM"
    question = has_question(text)
    command = has_command_verb(text)
    polite = has_polite_request(text)
    suggestion = has_suggestion(text)
    instruction = has_instruction(text)

    # 1. PERGUNTA
    if question and not command:
        return "PERGUNTA"

    # 2. ORDEM (imperativo direto forte)
    if command and not polite:
        return "ORDEM"

    # 3. PEDIDO (comando + educação)
    if command and polite:
        return "ORDEM"

    # 4. INSTRUÇÃO TÉCNICA (passo a passo, guia)
    if instruction:
        return "ORDEM"

    # 5. SUGESTÃO
    if suggestion:
        return "SUGESTÃO"

    return "NEUTRO"

