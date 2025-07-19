# GitHub NumPy Issues Page

$repo_name: numpy/numpy
$repo_id: 908607

URL: https://github.com/numpy/numpy/issues
Page Overview
This is the issues listing page for the repository on GitHub, where users can view, search, and filter through open issues.

```interactive_element_issue_hover
type: Hover trigger
visual_element: Issue links
trigger: Mouseover on issue link
request: GET https://github.com/numpy/numpy/issues/$issue_number/hovercard
arguments: {
  "subject": "repository:$repo_id",
  "current_path": "/$repo_name/issues"
}
effect: Displays a popup card to view issue details
returns: HTML with issue title, description preview, and labels
viewport_effect: none
```

```interactive_element_author_filter
type: Button/Dropdown
visual_element: "Author" button on top of the issues list, in the filter bar
trigger: Click
request: GET https://github.com/_graphql
arguments: {
  "body": '{"query":"76143934e91fc5d431ea7b83f63b08b9","variables":{"capabilities":["CAN_BE_AUTHOR"],"first":30,"loginNames":null,"name":"numpy","owner":"numpy","query":""}}'
}
effect: Loads author suggestions for filtering
returns: JSON with suggested authors including bots and users
viewport_effect: none
```
