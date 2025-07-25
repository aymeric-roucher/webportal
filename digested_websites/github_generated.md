```interactive_element_search
location_page: ^owner/^repo_name
type: Search Bar
visual_element: Search bar at the top-right corner of the GitHub homepage
trigger: Type '^query' in the search bar and press enter
request: GET https://github.com/search
arguments: 
  URL params: q="^query", type="repositories"
returns: HTML page content
viewport_effect: Displays search results for repositories matching the query
```

```interactive_element_repo_navigation
location_page: ^owner/^repo_name
type: Link
visual_element: Blue hyperlink text for a repository in search results
trigger: Click on the repository link
request: GET https://github.com/^owner/^repo_name
returns: HTML page content
viewport_effect: Navigates to the repository's main page
```

```interactive_element_issues_tab
location_page: ^owner/^repo_name
type: Tab
visual_element: Gray tab labeled 'Issues' near the top of the repository page
trigger: Click on the 'Issues' tab
request: GET https://github.com/^owner/^repo_name/issues
returns: HTML page content
viewport_effect: Displays the issues list for the repository
```

```interactive_element_author_filter
location_page: ^owner/^repo_name/issues
type: Button
visual_element: Gray button labeled 'Author' near the top of the issues list
trigger: Click on the 'Author' button
request: GET https://github.com/_graphql
arguments: 
  "body" (url-encoded): {
    "query": "76143934e91fc5d431ea7b83f63b08b9",
    "variables": {
      "capabilities": [],
      "first": 30,
      "loginNames": null,
      "name": "^repo_name",
      "owner": "^owner",
      "query": ""
    }
  }
returns: JSON object with keys: data
viewport_effect: Displays a list of authors who have contributed to the issues
```

```interactive_element_labels_filter
location_page: ^owner/^repo_name/issues
type: Button
visual_element: Gray button labeled 'Labels' next to the 'Author' button
trigger: Click on the 'Labels' button
request: GET https://github.com/_graphql
arguments: 
  "body" (url-encoded): {
    "query": "b314e1ada402f5a1ad5a80f5d3395c1d",
    "variables": {
      "nodes": [
        "MDU6TGFiZWw2MzU5MjE0",
        "MDU6TGFiZWw2MzU5MjM5",
        "MDU6TGFiZWwzNjgyNTgyNQ==",
        "MDU6TGFiZWw2MzU5OTkw",
        "MDU6TGFiZWw2MzU5OTQ1",
        "MDU6TGFiZWw2Mzk0ODU5",
        "MDU6TGFiZWw4MTQ5ODUyMA==",
        "MDU6TGFiZWwyNDkxOTM0MDg=",
        "MDU6TGFiZWw1NDYzNzg3NTQ=",
        "MDU6TGFiZWw2MDI2MzkzNTQ=",
        "MDU6TGFiZWw2MzU5ODE3",
        "MDU6TGFiZWw2MzU5ODkz",
        "MDU6TGFiZWw2MzU5OTI1",
        "MDU6TGFiZWw2MzU5MzE1",
        "MDU6TGFiZWw2MzU5MzUy",
        "MDU6TGFiZWw1MzU0MDI0NjE=",
        "MDU6TGFiZWwxMDI0Mzk1MTYw",
        "MDU6TGFiZWwxMDM1MTUyODc5",
        "MDU6TGFiZWwxMDg2NDkxNjAx",
        "MDU6TGFiZWwxMTgxMzkwNjcx",
        "MDU6TGFiZWwxMjMyMjA1NzM0",
        "MDU6TGFiZWwxMjQ0NTEzNzg0",
        "MDU6TGFiZWwxNTAxMDU3NTI2",
        "MDU6TGFiZWwxNTAxMDU1NTI5",
        "MDU6TGFiZWwxNzE1MDY0NjY1",
        "MDU6TGFiZWwyMjUwNjA5MjQx",
        "MDU6TGFiZWwyNTA2MDg1MzM1",
        "LA_kwDOAA3dP87cvxtl",
        "LA_kwDOAA3dP88AAAABlbVqug",
        "LA_kwDOAA3dP88AAAABokdLGg"
      ]
    }
  }
returns: JSON object with keys: data, extensions
viewport_effect: Displays all available labels with their colors and descriptions
```

```interactive_element_sort_oldest
location_page: ^owner/^repo_name/issues
type: Dropdown
visual_element: Sort dropdown button with "Oldest" option in the issues list header
trigger: Click on sort dropdown and select "Oldest"
request: GET https://github.com/_graphql
arguments: 
  "body" (url-encoded): {
    "query": "22d008b451590c967cc8d672452db3f9",
    "variables": {
      "includeReactions": false,
      "name": "^repo_name",
      "owner": "^owner",
      "query": "is:issue state:open sort:created-asc repo:^owner/^repo_name",
      "skip": 0
    }
  }
effect: Sorts the issues list by creation date in ascending order (oldest first)
returns: JSON with paginated issues data sorted by oldest creation date first
viewport_effect: Updates the issues list display to show issues sorted chronologically from oldest to newest
```
