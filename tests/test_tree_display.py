#!/usr/bin/env python3
"""
Test script for the tree display functionality
"""

from src.webportal.get_skeleton.crawl import (
    FastJSCrawler,
    FixedTemplateSegment,
    Template,
    VariableTemplateSegment,
)


def test_tree_display():
    """Test the tree display with sample GitHub-like URLs"""
    # Create a test crawler
    crawler = FastJSCrawler("https://github.com")

    # Add some test templates to simulate GitHub URLs structure
    crawler.pattern_templates = [
        Template(
            segments=[
                FixedTemplateSegment(example="docs.github.com"),
                VariableTemplateSegment(examples={"id"}),
                FixedTemplateSegment(example="enterprise-cloud@latest"),
                FixedTemplateSegment(example="copilot"),
                FixedTemplateSegment(example="tutorials"),
                FixedTemplateSegment(example="copilot-chat-cookbook"),
                VariableTemplateSegment(
                    examples={"debug-errors", "document-code", "refactor-code"}
                ),
                VariableTemplateSegment(
                    examples={
                        "connect-with-wireguard",
                        "integrate-ai-agents",
                        "refactor-design-patterns",
                    }
                ),
            ]
        ),
        Template(
            segments=[
                FixedTemplateSegment(example="github.com"),
                FixedTemplateSegment(example="github"),
                FixedTemplateSegment(example="docs"),
                FixedTemplateSegment(example="tree"),
                FixedTemplateSegment(example="main"),
                FixedTemplateSegment(example="content"),
                FixedTemplateSegment(example="search-github"),
                FixedTemplateSegment(example="github-code-search"),
            ]
        ),
        Template(
            segments=[
                FixedTemplateSegment(example="github.com"),
                FixedTemplateSegment(example="github-linguist"),
                FixedTemplateSegment(example="linguist"),
                VariableTemplateSegment(examples={"tree", "blob"}),
                FixedTemplateSegment(example="main"),
                FixedTemplateSegment(example="lib"),
                FixedTemplateSegment(example="linguist"),
                FixedTemplateSegment(example="languages.yml"),
            ]
        ),
    ]

    # Test the tree export
    tree_output = crawler._export_tree()
    print("Tree Display Output:")
    print("=" * 50)
    print(tree_output)
    print("=" * 50)

    # Validate tree structure components (order of set items may vary)
    lines = tree_output.strip().split("\n")

    # Check header
    assert lines[0] == "Site Structure for github.com"
    assert lines[1] == "=" * 50
    assert lines[2] == ""

    # Check that all expected paths are present (except variable segments which may vary in order)
    expected_patterns = [
        "├── docs.github.com/",
        "│   └── [id]/",
        "│       └── enterprise-cloud@latest/",
        "│           └── copilot/",
        "│               └── tutorials/",
        "│                   └── copilot-chat-cookbook/",
        "└── github.com/",
        "    ├── github/",
        "    │   └── docs/",
        "    │       └── tree/",
        "    │           └── main/",
        "    │               └── content/",
        "    │                   └── search-github/",
        "    │                       └── github-code-search/",
        "    └── github-linguist/",
        "        └── linguist/",
        "                └── main/",
        "                    └── lib/",
        "                        └── linguist/",
        "                            └── languages.yml/",
    ]

    for pattern in expected_patterns:
        assert pattern in tree_output, f"Pattern '{pattern}' not found in tree output"

    # Check variable segment with flexible ordering
    assert any(("[tree|blob]" in line or "[blob|tree]" in line) for line in lines), (
        "Variable segment [tree|blob] or [blob|tree] not found"
    )

    # Check that variable segments contain expected values (order may vary)
    assert any(
        "debug-errors" in line and "document-code" in line and "refactor-code" in line
        for line in lines
    )
    assert any(
        "connect-with-wireguard" in line
        and "integrate-ai-agents" in line
        and "refactor-design-patterns" in line
        for line in lines
    )
    assert any("tree|blob" in line or "blob|tree" in line for line in lines)

    print("✅ Tree display test passed!")


if __name__ == "__main__":
    test_tree_display()
