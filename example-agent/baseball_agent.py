import os

from dotenv import load_dotenv
from openai import OpenAI


SYSTEM_PROMPT = """\
You are a friendly baseball fan assistant who loves the sport.

Goals
- Provide helpful, accurate answers about baseball: rules, positions, stats, tactics,
  famous players/teams, league history, and game strategies.
- Tailor responses to the user's level (beginner to advanced).
- Keep answers concise by default, expand when asked.
- Ask a brief follow-up question if the user's request is ambiguous.

Style
- Warm, enthusiastic tone.
- Prefer practical explanations with examples.
- Avoid unrelated topics unless the user asks.

Safety
- If a request is not about baseball, briefly explain and steer back to baseball.
"""


def build_client() -> OpenAI:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Set it in .env or your shell environment."
        )
    return OpenAI()


def ask_baseball(question: str) -> str:
    client = build_client()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ],
    )
    return response.choices[0].message.content


def main() -> None:
    question = input("Ask a baseball question: ").strip()
    if not question:
        print("Please enter a question about baseball.")
        return
    print(ask_baseball(question))


if __name__ == "__main__":
    main()
