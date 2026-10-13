import uuid

from app import storage
from app.analyzer import get_client
from app.config import LLM_MODEL
from app.tools import TOOLS, run_tool

MAX_STEPS = 8

AGENT_PROMPT = """You are JobPilot, an assistant that helps a job seeker manage their job search.
You can analyze job postings against the user's CV, save applications and list saved applications.

Guidelines:
- Use the tools when they are needed. Never guess information you can get from a tool.
- Before saving an application, you need the company and the job title. If they appear in the job posting, use them without asking. Ask the user only if they are really missing.
- When you report an analysis, give the score, the main gaps and 2-3 key suggestions.
- Keep answers under 6 lines unless the user explicitly asks for more detail.
- Only offer actions you can perform with your tools.
- If a tool returns an error, explain the problem to the user in simple words.
- Reply in the same language the user writes in.
- In Hebrew, address the user in a gender-neutral way: use the infinitive form and avoid gendered words."""


def block_to_dict(block) -> dict:
    if block.type == "text":
        return {"type": "text", "text": block.text}
    if block.type == "tool_use":
        return {"type": "tool_use", "id": block.id, "name": block.name, "input": block.input}
    if block.type == "thinking":
        return {"type": "thinking", "thinking": block.thinking, "signature": block.signature}
    if block.type == "redacted_thinking":
        return {"type": "redacted_thinking", "data": block.data}
    raise ValueError(f"Unsupported block type: {block.type}")


def run_agent(
    message: str, language: str = "he", conversation_id: str | None = None
) -> tuple[str, list[str], str]:
    if conversation_id is None:
        conversation_id = str(uuid.uuid4())
        messages = []
    else:
        messages = storage.load_conversation(conversation_id)

    messages.append({"role": "user", "content": message})
    steps: list[str] = []
    client = get_client()

    for _ in range(MAX_STEPS):
        response = client.messages.create(
            model=LLM_MODEL,
            max_tokens=2048,
            system=AGENT_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        # Keep every model turn in the history, including the final answer
        assistant_content = [block_to_dict(block) for block in response.content]
        messages.append({"role": "assistant", "content": assistant_content})

        # The model is done: save the conversation and return the answer
        if response.stop_reason != "tool_use":
            answer = "".join(b["text"] for b in assistant_content if b["type"] == "text")
            storage.save_conversation(conversation_id, messages)
            return answer, steps, conversation_id

        # Run every tool the model asked for
        tool_results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            steps.append(block.name)
            try:
                output = run_tool(block.name, block.input, language)
                tool_results.append(
                    {"type": "tool_result", "tool_use_id": block.id, "content": output}
                )
            except Exception as error:
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": f"Error: {error}",
                        "is_error": True,
                    }
                )

        messages.append({"role": "user", "content": tool_results})

    return "The agent stopped after too many steps.", steps, conversation_id