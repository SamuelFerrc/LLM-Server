import spacy
from collections import Counter

nlp = spacy.load("pt_core_news_sm")

def extract_keys(texto):
    doc = nlp(texto.lower())

    entidades = [ent.text for ent in doc.ents]

    substantivos = [
        token.lemma_
        for token in doc
        if token.pos_ in ["NOUN", "PROPN"]
        and not token.is_stop
        and token.is_alpha
    ]

    candidatos = entidades + substantivos

    if not candidatos:
        return None, []

    freq = Counter(candidatos)

    assunto = freq.most_common(1)[0][0]

    if " " in assunto:
        assunto = assunto.split()[-1]

    keywords = [k for k, _ in freq.most_common(5)]

    keywords = [
        kw.split()[-1] if " " in kw else kw
        for kw in keywords
    ]
    return assunto, keywords


#texto = "Quero ver noticias sobre a guerra do irã"

#assunto, keywords = extrair_assunto_e_keywords(texto)

#print("Assunto:", assunto)
#print("Keywords:", keywords)