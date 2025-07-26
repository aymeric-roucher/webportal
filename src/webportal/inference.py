import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

assert os.getenv("OPENAI_API_KEY") is not None, "OPENAI_API_KEY is not set"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = "gpt-4.1"


def call_llm(prompt: str) -> str:
    """Call via OpenAI API"""

    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=8096,
    )

    output = response.choices[0].message.content
    if output is None:
        raise Exception("No output from LLM")
    return output
