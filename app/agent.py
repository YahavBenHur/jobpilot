from app.analyzer import get_client
from app.config import LLM_MODEL
from app.tools import TOOLS, run_tool

MAX_STEPS = 8

AGENT_PROMPT = """You are JobPilot, an assistant that helps a job seeker manage their job search.
You can analyze job postings against the user's CV, save applications and list saved applications.

Guidelines:
- Use the tools when they are needed. Never guess information you can get from a tool.
- Before saving an application, you need the company and the job title. If they appear in the job posting, use them without asking. Ask the user only if they are really missing.
- When you report an analysis, give the score, the main gaps and 2-3 key suggestions. Keep it short.
- If a tool returns an error, explain the problem to the user in simple words.
- Only offer actions you can perform with your rools.
- In Hebrew, address the user in a gender-neutral way: use the infinitive form and avoid gendered words.
- Reply in the same language the user writes in."""


def run_agent(message: str, language: str = "he") -> tuple[str, list[str]]:
    client = get_client()
    messages = [{"role": "user", "content": message}]
    steps: list[str] = []

    for _ in range(MAX_STEPS):
        response = client.messages.create(
            model=LLM_MODEL,
            max_tokens=2048,
            system=AGENT_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        # The model is done: return its final text answer
        if response.stop_reason != "tool_use":
            answer = "".join(block.text for block in response.content if block.type == "text")
            return answer, steps

        # The model asked for tools: keep its request in the history
        messages.append({"role": "assistant", "content": response.content})

        # Run every tool it asked for and collect the results
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

        # Send the results back to the model, and loop again
        messages.append({"role": "user", "content": tool_results})

    return "The agent stopped after too many steps.", steps