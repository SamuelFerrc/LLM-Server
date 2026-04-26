import json
import re
import unicodedata
from rapidfuzz import fuzz


with open(
    "commands.json",
    "r",
    encoding="utf-8"
) as f:
    COMMANDS = json.load(f)



# -------------------------
# Normalização
# -------------------------

def normalize(text):

    text = text.lower()

    # remove acentos
    text = ''.join(
        c for c in unicodedata.normalize(
            'NFD',
            text
        )
        if unicodedata.category(c) != 'Mn'
    )

    # singular/plural simples
    text = text.replace(
        "noticias",
        "noticia"
    )

    # remove pontuação
    text = re.sub(
        r"[^\w\s]",
        "",
        text
    )

    # espaços duplicados
    text = " ".join(
        text.split()
    )

    return text



# -------------------------
# Similaridade robusta
# -------------------------

def similarity(a,b):

    return fuzz.token_set_ratio(
        normalize(a),
        normalize(b)
    )



# -------------------------
# Detectar intenção
# -------------------------

def detect_intent(user_input):

    text = normalize(
        user_input
    )

    best_intent = None
    best_example = None
    best_score = 0


    for intent,data in COMMANDS.items():

        for ex in data["examples"]:

            ex_clean = ex.replace(
                "X",
                ""
            ).strip()

            score = similarity(
                text,
                ex_clean
            )

            if score > best_score:
                best_score = score
                best_intent = intent
                best_example = ex_clean


    print(
      f"Intent={best_intent} score={best_score}"
    )

    if best_score < 60:
        return None,None

    return best_intent,best_example



# -------------------------
# Extrair argumento
# -------------------------

def extract_argument(
    user_input,
    matched_example
):

    text = normalize(
        user_input
    )

    prefix = normalize(
        matched_example
    )


    if text.startswith(prefix):

        arg = text[
            len(prefix):
        ].strip()

        return arg


    words = prefix.split()

    if len(words)>=2:

        pivot = " ".join(
            words[-2:]
        )

        idx = text.find(
            pivot
        )

        if idx != -1:

            return text[
                idx+len(pivot):
            ].strip()

    return ""



# -------------------------
# Gerar comando
# -------------------------

def generate_command(
    user_input
):

    intent,example = detect_intent(
        user_input
    )

    if not intent:
        return ""


    entry = COMMANDS[intent]


    # comando fixo
    if "command" in entry:
        return entry["command"]


    # template dinâmico
    if "template" in entry:

        arg = extract_argument(
            user_input,
            example
        )

        if not arg:
            return ""

        return entry["template"].format(
            query=arg,
            arg=arg,
            value=arg
        )


    return ""

