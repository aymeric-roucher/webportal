import asyncio
import json

from browser_use import Agent
from browser_use.llm import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

with open("benchmark/data/gaia_validation_interactive_questions.jsonl", "r") as f:
    questions = [json.loads(line) for line in f]

print(len(questions))


async def run_browser_use_agent(
    questions: list[dict], max_concurrency: int = 8
) -> list[str]:
    # Limit the number of concurrently running agent tasks using a semaphore
    sem = asyncio.Semaphore(max_concurrency)

    async def run_single(example):
        agent = Agent(
            task=example["Question"],
            llm=ChatOpenAI(model="o4-mini", temperature=1.0),
        )
        async with sem:
            output = await agent.run(max_steps=50)
            return example | {"answer": output.final_result()}

    output = await asyncio.gather(*(run_single(example) for example in questions))
    return output


if __name__ == "__main__":
    results = asyncio.run(run_browser_use_agent(questions[2:3]))
    with open("benchmark/output/browser_use.jsonl", "w") as f:
        for result in results:
            f.write(json.dumps(result) + "\n")
