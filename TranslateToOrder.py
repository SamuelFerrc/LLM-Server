from cortex.bootstrap import create_command_translator


_translator = create_command_translator()


def normalize(text):
    return _translator.normalize(text)


def similarity(a, b):
    return _translator.similarity(a, b)


def detect_intent(user_input):
    match = _translator.detect_intent(user_input)

    if match is None:
        return None, None

    return match.definition.name, match.matched_example


def extract_argument(user_input, matched_example):
    return _translator.extract_argument(user_input, matched_example)


def generate_command(user_input):
    return _translator.translate(user_input) or ""
