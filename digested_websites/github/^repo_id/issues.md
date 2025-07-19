# GitHub NumPy Issues Page
URL: https://github.com/numpy/numpy/issues
Page Overview
This is the issues listing page for the repository on GitHub, where users can view, search, and filter through open issues.

```interactive_element_issue_hover
Type: Hover trigger
Visual: When hovering over issue #29393
Action: Mouseover on issue link

Request: GET https://github.com/numpy/numpy/issues/29393/hovercard
Parameters: 
  - subject=repository:908607
  - current_path=/numpy/numpy/issues

Response effect: Displays a popup card with issue preview
Content returned: HTML with issue title, description preview, and labels

Agent instruction: This is a hover action that displays additional information. 
To view issue details without navigating away, use:
visit_webpage(
  url="https://github.com/numpy/numpy/issues/29393/hovercard",
  method="GET",
  arguments={
    "subject": "repository:908607",
    "current_path": "/numpy/numpy/issues"
  }
)
````

```interactive_element_author_filter
Type: Button/Dropdown
Visual: "Author" button in the filter bar
Location: Top of issues list, in the filter toolbar

Trigger: Click
Request: GET https://github.com/_graphql
Query parameters: Complex GraphQL query for author suggestions

Response effect: Loads author suggestions for filtering
Data returned: JSON with suggested authors including bots and users

Agent instruction: To get author suggestions for filtering, use:
visit_webpage(
  url="https://github.com/_graphql",
  method="GET",
  arguments={
    "body": '{"query":"76143934e91fc5d431ea7b83f63b08b9","variables":{"capabilities":["CAN_BE_AUTHOR"],"first":30,"loginNames":null,"name":"numpy","owner":"numpy","query":""}}'
  }
)
```
