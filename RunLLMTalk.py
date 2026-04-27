from cortex.bootstrap import create_assistant_runtime


_runtime = create_assistant_runtime()


def need_google(prompt: str) -> str:
    return _runtime.research_decider.decide_from_prompt(prompt)


def generate_response(
    prompt: str,
    intention: str,
    max_tokens: int = 100,
    historyAdd: bool = True,
) -> str:
    return _runtime.conversation_service.generate_response(
        prompt,
        intention,
        max_tokens=max_tokens,
        add_to_history=historyAdd,
    )


def generate_summary() -> str:
    return _runtime.conversation_service.generate_summary()


def add_log(action: str, justification: str | None = None) -> None:
    _runtime.action_log_service.add_log(action, justification)


def generate_log() -> str:
    return _runtime.action_log_service.generate_log()


def execute_action(action_name: str, func, *args, **kwargs):
    return _runtime.action_service.execute_action(action_name, func, *args, **kwargs)
