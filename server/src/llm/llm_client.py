import os
from together import Together
from dotenv import load_dotenv

load_dotenv()

client = Together(api_key=os.getenv("TOGETHER_API_KEY"))

MODEL = "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct"


def _clean_output(text: str) -> str:
    """
    Remove markdown code fences returned by LLM.
    """
    text = text.strip()

    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("python"):
            text = text[len("python"):]
    return text.strip()


def ask_llm(prompt: str) -> str:
    """
    Sends repair request to LLM and returns fixed code.
    """

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a senior software engineer fixing CI failures. "
                    "Return ONLY valid code. Do not explain anything."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
        max_tokens=1500,
    )

    content = response.choices[0].message.content
    return _clean_output(content)
