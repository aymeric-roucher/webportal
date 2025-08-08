from dotenv import load_dotenv
from openai import OpenAI

from webportal.secret_manager import get_openai_api_key

load_dotenv()

client = OpenAI(api_key=get_openai_api_key())
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
