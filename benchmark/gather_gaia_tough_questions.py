import json
import os

from datasets import Dataset
from openai import OpenAI
from pydantic import BaseModel

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

with open("benchmark/data/gaia_validation_full.jsonl", "r") as f:
    questions = [json.loads(line) for line in f]

questions = [q for q in questions if q["file_name"] == ""]
print(len(questions))


class Answer(BaseModel):
    keep: bool
    websites_to_use: list[str]


def filter_question(example) -> dict | None:
    prompt = f"""You are given an example from a benchmark. The question is: does answering this example's question require nontrivial interactions with a website?
Check the annotator's resolution process to see the solving process required.
Nontrivial interactions are for instance needing to click some interactive elements to access information. If a question only requires scrolling through pages and clicking links (not buttons), it is trivial, thus should not be kept.
To help you decide, think: could a crawler have collected the information required? If a crawler could find the information required (crawlers can read pdf) without clicking stuff except links, the interaction is trivial and the question should not be kept.
But if the information is hidden behind some interactions with filters/search bars, it is nontrivial and the question should be kept.
If some nontrivial interactions are required, return {{"keep": True, "websites_to_use": [list of domain names of websites to use, as in 'arxiv.org']}}. If no, return {{"keep": False, "websites_to_use": []}}.

Here is the example:
{str(example)}
"""
    try:
        response = client.responses.parse(
            model="gpt-4.1-mini",
            input=prompt,
            text_format=Answer,
        )
        outcome = response.output_parsed
        example["websites_to_use"] = outcome.websites_to_use
        example["keep"] = outcome.keep
        return example
    except Exception:
        example["websites_to_use"] = ["ERROR"]
        example["keep"] = True
        return example


dataset = Dataset.from_list(questions)
dataset = dataset.map(filter_question, num_proc=8)
dataset = dataset.filter(lambda x: x["keep"])

with open("benchmark/data/gaia_validation_interactive_questions.jsonl", "w") as f:
    for example in dataset:
        f.write(json.dumps(example) + "\n")
