from cortex.bootstrap import create_speech_classifier


_classifier = create_speech_classifier()


def normalize(text):
    return _classifier.normalize(text)


def has_question(text):
    return _classifier.has_question(text)


def has_command_verb(text):
    return _classifier.has_command_verb(text)


def has_polite_request(text):
    return _classifier.has_polite_request(text)


def has_suggestion(text):
    return _classifier.has_suggestion(text)


def has_instruction(text):
    return _classifier.has_instruction(text)


def classify_speech_act(text):
    return _classifier.classify(text).value
