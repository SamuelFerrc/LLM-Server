from llama_cpp import Llama

llm = Llama(
    model_path="Mistral-Nemo-2407-12B-Thinking-Claude-Gemini-GPT5.2-Uncensored-HERETIC.Q2_K.gguf",
    n_threads=4,
    n_ctx=512
)

while True:
    prompt = input()
    if prompt == "quit":
        break

    print("Resposta:")

    for chunk in llm(
        prompt,
        max_tokens=100,
        stream=True  # 🔥 ISSO AQUI
    ):
        print(chunk["choices"][0]["text"], end="", flush=True)

    print("\n")