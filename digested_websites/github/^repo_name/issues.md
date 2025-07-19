# GitHub NumPy Issues Page

$repo_name: numpy/numpy
$repo_id: 908607

URL: https://github.com/numpy/numpy/issues
Page Overview
This is the issues listing page for the repository on GitHub, where users can view, search, and filter through open issues.

```interactive_element_issue_hover
type: Hover trigger
action: Mouseover on issue link

request: GET https://github.com/numpy/numpy/issues/$issue_number/hovercard
parameters:
  - subject=repository:$repo_id
  - current_path=/$repo_name/issues

response_effect: Displays a popup card with issue preview
content_returned: HTML with issue title, description preview, and labels
viewport_effect: none

Agent instruction: This is a hover action that displays additional information. 
To view issue details without navigating away, use:
visit_webpage(
  url="https://github.com/numpy/numpy/issues/$issue_number/hovercard",
  method="GET",
  arguments={
    "subject": "repository:$repo_id",
    "current_path": "/$repo_name/issues"
  }
)
```

```interactive_element_author_filter
Type: Button/Dropdown
Visual: "Author" button in the filter bar
Location: Top of issues list, in the filter toolbar

Trigger: Click
Request: GET https://github.com/_graphql
Query parameters: Complex GraphQL query for author suggestions

Response effect: Loads author suggestions for filtering
Data returned: JSON with suggested authors including bots and users
viewport_effect: none

Agent instruction: To get author suggestions for filtering, use:
visit_webpage(
  url="https://github.com/_graphql",
  method="GET",
  arguments={
    "body": '{"query":"76143934e91fc5d431ea7b83f63b08b9","variables":{"capabilities":["CAN_BE_AUTHOR"],"first":30,"loginNames":null,"name":"numpy","owner":"numpy","query":""}}'
  }
)
```
