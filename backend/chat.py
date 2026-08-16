# chat.py — a mini chat with Gemini. Type "exit" to stop.
import llm

while True:
    question = input("You: ")
    if question.lower() == "exit":
        break
    print("AI:", llm.ask(question))
    print()