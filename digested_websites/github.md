Here is a manual for interacting with github.com.

To access a specific github issue, head to https://github.com/numpy/numpy/issues/$issue_number with GET request.

```issue_hover
location_page: ^repo_name/issues
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

```issue_filter_author
location_page: ^repo_name/issues
type: Button/Dropdown
visual_element: "Author" button on top of the issues list, in the filter bar
trigger: Click
request: GET https://github.com/_graphql
arguments: 
  "body" (url-encoded): {
    "query":"76143934e91fc5d431ea7b83f63b08b9",
    "variables":{"capabilities":["CAN_BE_AUTHOR"],"first":30,"loginNames":null,"name":"numpy","owner":"numpy","query":""}
  }
effect: Loads author suggestions for filtering
returns: JSON with suggested authors including bots and users
viewport_effect: none
```

```issue_filter_label
location_page: ^repo_name/issues
type: Button/Dropdown
visual_element: "Labels" button on top of the issues list, in the filter bar
trigger: Click
request: GET https://github.com/_graphql
arguments: "body" (url-encoded): 
  {
    "query":"b480cbd1d6d3f7ba4a98229e88acf3fd",
    "variables":{"count":100,"labelNames":"","owner":"numpy","repo":"numpy","shouldQueryByNames":false}
  }
effect: Loads all available labels for filtering issues
returns: JSON with label data including id, color, name, nameHTML, description, and URL for each label
viewport_effect: Opens dropdown showing all repository labels with color coding and descriptions
```

```issue_filter_closed_button
location_page: ^repo_name/issues
type: Button/Toggle
visual_element: "Closed" button in the issues filter bar
trigger: Click
request: GET https://github.com/numpy/numpy/issues
arguments: {
  "q": "is%3Aissue%20state%3Aclosed%20label%3A%2212%20-%20Bug%22"
}
effect: Filters issues to show only closed issues
returns: HTML page with filtered list of closed issues
viewport_effect: Reloads the issues list showing only closed issues, updates URL parameters
```

```issue_sort_oldest
location_page: ^repo_name/issues
type: Button/Dropdown
visual_element: Sort dropdown button with "Oldest" option in the issues list header
trigger: Click on sort dropdown and select "Oldest"
request: GET https://github.com/_graphql
arguments: 
  "body" (url-encoded): {
    "query":"22d008b451590c967cc8d672452db3f9",
    "variables":{"includeReactions":false,"name":"numpy","owner":"numpy","query":"is:issue state:closed sort:created-asc repo:numpy/numpy","skip":0}
  }
effect: Sorts the issues list by creation date in ascending order (oldest first)
returns: JSON with paginated issues data sorted by oldest creation date first
viewport_effect: Updates the issues list display to show issues sorted chronologically from oldest to newest
```