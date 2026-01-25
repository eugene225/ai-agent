import json
import os
from typing import Any

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

Tooling
- If the user asks you to remember a fact or preference, you MUST call remember.
- If the user asks to recall a stored fact, you MUST call recall.
- Do not answer memory questions directly without using tools.
- Examples:
  - "내 이름은 유진이야, 기억해줘" -> remember(key="name", value="Eugene")
  - "내 이름 뭐였지?" -> recall(key="name")
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "remember",
            "description": "Store a short user fact or preference for this session.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string"},
                    "value": {"type": "string"},
                },
                "required": ["key", "value"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "recall",
            "description": "Retrieve a stored fact by key.",
            "parameters": {
                "type": "object",
                "properties": {
                    "key": {"type": "string"},
                },
                "required": ["key"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_baseball_rules",
            "description": "Return a brief explanation of baseball rules by topic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "topic": {
                        "type": "string",
                        "description": "Rule topic like scoring, innings, strikes, balls, outs.",
                    }
                },
                "required": ["topic"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_baseball_schedule",
            "description": "Return a simple schedule overview for a league and date range.",
            "parameters": {
                "type": "object",
                "properties": {
                    "league": {
                        "type": "string",
                        "description": "League name like KBO, MLB, NPB.",
                    },
                    "date": {
                        "type": "string",
                        "description": "Date or range like 2025-08-01 or 2025-08-01~2025-08-07.",
                    },
                },
                "required": ["league", "date"],
            },
        },
    },
]


def build_client() -> OpenAI:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Set it in .env or your shell environment."
        )
    return OpenAI()


class BaseballAgent:
    def __init__(self) -> None:
        self._client = build_client()
        self._messages: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        self._memory: dict[str, str] = {}

    def _tool_remember(self, arguments: dict[str, str]) -> str:
        key = arguments.get("key", "").strip()
        value = arguments.get("value", "").strip()
        if not key or not value:
            return "Missing key or value."
        self._memory[key] = value
        return f"Stored: {key}."

    def _tool_recall(self, arguments: dict[str, str]) -> str:
        key = arguments.get("key", "").strip()
        if not key:
            return "Missing key."
        return self._memory.get(key, "")

    def _tool_get_baseball_rules(self, arguments: dict[str, str]) -> str:
        topic = arguments.get("topic", "").strip().lower()
        if not topic:
            return "Missing topic."
        return "Rules lookup is a placeholder. " f"Requested topic: {topic}."

    def _tool_get_baseball_schedule(self, arguments: dict[str, str]) -> str:
        league = arguments.get("league", "").strip().upper()
        date = arguments.get("date", "").strip()
        if not league or not date:
            return "Missing league or date."
        return (
            "Schedule lookup is a placeholder. "
            f"Requested league: {league}, date: {date}."
        )

    def _run_tool(self, name: str, arguments: dict[str, str]) -> str:
        function_map = {
            "remember": self._tool_remember,
            "recall": self._tool_recall,
            "get_baseball_rules": self._tool_get_baseball_rules,
            "get_baseball_schedule": self._tool_get_baseball_schedule,
        }
        handler = function_map.get(name)
        if not handler:
            return "Unknown tool."
        print(f"[tool] {name} called with {arguments}")
        return handler(arguments)

    def chat(self, user_input: str) -> str:
        self._messages.append({"role": "user", "content": user_input})
        response = self._client.chat.completions.create(
            model="gpt-4o-mini",
            messages=self._messages,
            tools=TOOLS,
            tool_choice="auto",
        )
        message = response.choices[0].message

        if message.tool_calls:
            self._messages.append(
                {
                    "role": "assistant",
                    "content": message.content or "",
                    "tool_calls": message.tool_calls,
                }
            )
            for tool_call in message.tool_calls:
                try:
                    arguments = json.loads(tool_call.function.arguments or "{}")
                except json.JSONDecodeError:
                    arguments = {}
                result = self._run_tool(tool_call.function.name, arguments)
                self._messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result,
                    }
                )

            response = self._client.chat.completions.create(
                model="gpt-4o-mini",
                messages=self._messages,
                tools=TOOLS,
                tool_choice="auto",
            )
            message = response.choices[0].message

        content = message.content or ""
        self._messages.append({"role": "assistant", "content": content})
        return content


def main() -> None:
    agent = BaseballAgent()
    print("Ask a baseball question. Type 'q' or 'quit' to exit.")
    while True:
        question = input("> ").strip()
        if question.lower() in {"q", "quit"}:
            break
        if not question:
            print("Please enter a question about baseball.")
            continue
        print(agent.chat(question))


if __name__ == "__main__":
    main()
