import ast

from litellm import completion
from pydantic import BaseModel

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
│   ├── articles/
│   │   └── [blog|biochemistry|researcher-training|...]/
│   ├── collections/
│   │   └── jcjhabjhgi/
│   ├── naturecareers/
│   │   └── job/
│   │       └── {hash}/
│   │           └── [director-of-latam-country-and-site-operations|associate-or-senior-editor-nature|associate-or-senior-editor-nature-computational-science|...]/
│   ├── info/
│   │   ├── [blog|biochemistry|researcher-training|...]/
│   │   └── [evolution|legal_notice.html|biochemistry|...]/
│   ├── briefing/
│   │   └── signup/
│   ├── npg_/
│   │   ├── company_info/
│   │   │   └── index.html/
│   │   ├── press_room/
│   │   │   ├── press_releases.html/
│   │   │   └── index.html/
│   │   └── index_npg.html/
│   ├── [blog|courses-coming-soon|additional-services|...]/
│   │   └── open-access/
│   ├── immersive/
│   │   └── [index.html|natureawards|innovatorsinscience|...]/
│   │       └── index.html/
│   ├── nams/
│   │   └── svc/
│   │       └── myaccount/
│   ├── [blog|libraries|courses-coming-soon|...]/
│   │   └── index.html/
│   ├── [nprot|debug|catalogue|...]/
│   ├── subjects/
│   │   ├── [evolution|blog|nature-journal-digital-advertising|...]/
│   │   └── [evolution|biochemistry|cell-biology|...]/
│   ├── openresearch/
│   │   └── publishing-with-npg/
│   ├── nature-portfolio/
│   │   ├── [evolution|biochemistry|cell-biology|...]/
│   │   ├── about/
│   │   │   └── [journal-metrics|why-publish-with-nature-research|engineering|...]/
│   │   ├── open-access/
│   │   │   └── [engineering|author-reprints|indexing-abstracting|...]/
│   │   └── for-authors/
│   │       └── [author-reprints|indexing-abstracting|permissions-requests|...]/
│   ├── nature-research/
│   │   ├── open-access/
│   │   │   └── nature-partner-journals/
│   │   ├── for-authors/
│   │   │   └── [author-reprints|indexing-abstracting|permissions-requests|...]/
│   │   └── reprints-and-permissions/
│   │       └── [permissions-requests|author-reprints]/
│   ├── [nature-research|nature-portfolio|nature-research-journals]/
│   │   └── for-authors/
│   │       └── nature-research-journals/
│   └── auth/
│       └── personal/
│           └── nature/
├── [idp.nature.com|partnerships.nature.com|masterclasses.nature.com|...]/
│   └── search/
│       └── advanced/
├── idp.nature.com/
│   ├── auth/
│   │   └── personal/
│   │       └── springernature/
│   ├── [blog|libraries|courses-coming-soon|...]/
│   │   └── natureuser/
│   ├── [debug|catalogue|login|...]/
│   └── authors/
│       └── [evolution|blog|nature-journal-digital-advertising|...]/
├── support.nature.com/
│   ├── support/
│   │   └── home/
│   └── {id}/
│       └── support/
│           ├── home/
│           └── solutions/
│               └── articles/
│                   └── 6000214118-corresponding-author-defined/
├── [http:|https:|information-for-institutions]/
│   └── www.nature.com/
│       └── openresearch/
│           └── about-open-access/
│               └── information-for-institutions/
├── partnerships.nature.com/
│   ├── product/
│   │   └── [evolution|blog|nature-journal-digital-advertising|...]/
│   ├── [catalogue|register|case-studies|...]/
│   ├── products/
│   │   └── [evolution|blog|nature-journal-digital-advertising|...]/
│   ├── audiences/
│   │   └── [evolution|blog|legal_notice.html|...]/
│   └── blog/
│       └── our-newsletters/
├── [http:|alert]/
│   └── www.nature.com/
│       └── nams/
│           └── svc/
│               └── myaccount/
│                   └── save/
│                       └── alert/
├── masterclasses.nature.com/
│   ├── live-expert-trainer-led/
│   │   └── [evolution|biochemistry|cell-biology|...]/
│   ├── [login|register|catalogue]/
│   └── [blog|courses-coming-soon|additional-services|...]/
│       └── {hash}/
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
    from .crawl import FastJSCrawler

    crawler = FastJSCrawler(
        start_url="semrush.com",
        max_pages=100,
        max_depth=5,
    )
    await crawler.crawl()

    output = crawler.export_structure("tree")
    content = get_clean_urls_list(output)
    print(content)
