import ast
import asyncio

from litellm import completion
from pydantic import BaseModel

from webportal.map_website.crawl import crawl

raw_tree = """
Site Structure for nature.com
==================================================
├── [partnerships.nature.com|nano.nature.com|masterclasses.nature.com|...]/
├── www.nature.com/
│   ├── [npjscifood|npjacoustics|natfood|...]/
│   ├── authors/
│   │   ├── [open-access-funding|blog|biochemistry|...]/
│   │   └── author_resources/
│   │       └── index.html/
│   ├── nature/
│   │   ├── [open-access-funding|blog|biochemistry|...]/
│   │   └── awards/
│   │       └── [author-reprints|indexing-abstracting|mentorship|...]/
│   ├── my-account/
│   │   └── alerts/
│   │       └── subscribe-journal/
│   └── auth/
│       └── personal/
│           └── nature/
├── support.nature.com/
│   ├── support/
│   │   └── home/
│   └── {id}/
│       └── support/
│           ├── home/
│           └── solutions/
│               └── articles/
│                   └── 6000214118-corresponding-author-defined/
├── [nature.com|www.nature.com]/
└── navigator.nature.com/
    └── info/
        └── dataProcessing/
"""


class SiteStructure(BaseModel):
    urls: list[str]


def get_clean_urls_list(raw_tree: str) -> list[str]:
    reponse = completion(
        model="gpt-4.1",
        messages=[
            {
                "role": "user",
                "content": "You're helping extract all the information from a website. To this end, you need to send agents visting a curated seleciton of pages to understand the website dynamic components.Extract a list of interesting urls to visit from the following site structure:\n"
                + raw_tree
                + "\n\nEach page that you select should be one that you think has a unique interactive kind of element to try out. Make sure to first include the most important pages of the website: if the website has a specific common template of webpage urls, make sure to include at least one example.",
            }
        ],
        response_format=SiteStructure,
    )

    content = ast.literal_eval(reponse.choices[0].message.content)["urls"]
    return content


if __name__ == "__main__":
    crawler = asyncio.run(crawl("semrush.com", 100, 5, 10))
    tree_output = crawler.export_structure("tree")
    content = get_clean_urls_list(tree_output)[:10]
    print(content)
