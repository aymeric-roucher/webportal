```interactive_element_search
location_page: ^repo_name/search
type: Search Bar
visual_element: Search input field in the GitHub header
trigger: Type 'numpy' and press 'Enter' in the search bar
request: GET https://github.com/search
arguments: 
  URL params: q="^query", type="repositories"
effect: Initiates a search for repositories matching the query
returns: HTML page content with search results
viewport_effect: Displays a list of repositories matching the search query
```

```interactive_element_repository_navigation
location_page: ^owner/^repo_name
type: Link
visual_element: Repository link in search results
trigger: Click on the repository link 'numpy/numpy'
request: GET https://github.com/^owner/^repo_name
returns: HTML page content of the repository
viewport_effect: Navigates to the repository's main page
```

```interactive_element_issues_tab
location_page: ^owner/^repo_name/issues
type: Tab
visual_element: 'Issues' tab in the repository navigation bar
trigger: Click on the 'Issues' tab
request: GET https://github.com/^owner/^repo_name/issues
returns: HTML page content of the issues section
viewport_effect: Displays the issues list for the repository
```

```interactive_element_labels_button
location_page: ^owner/^repo_name/labels
type: Button
visual_element: 'Labels' button in the issues section
trigger: Click on the 'Labels' button
request: GET https://github.com/^owner/^repo_name/labels
returns: HTML page content with a list of labels
viewport_effect: Displays all labels associated with the repository
```

```interactive_element_sort_oldest
location_page: ^owner/^repo_name/issues
type: Dropdown
visual_element: Sort dropdown button with "Oldest" option in the issues list header
trigger: Click on sort dropdown and select "Oldest"
request: GET https://github.com/_graphql
arguments: 
  "body" (url-encoded): {
    "query":"22d008b451590c967cc8d672452db3f9",
    "variables":{"includeReactions":false,"name":"^repo_name","owner":"^owner","query":"is:issue state:open sort:created-asc repo:^owner/^repo_name","skip":0}
  }
effect: Sorts the issues list by creation date in ascending order (oldest first)
returns: JSON with paginated issues data sorted by oldest creation date first
viewport_effect: Updates the issues list display to show issues sorted chronologically from oldest to newest
```

```interactive_element_graphql_issues
location_page: ^owner/^repo_name/issues
type: GraphQL Query
visual_element: Issues list in the repository
trigger: Load issues list
request: GET https://github.com/_graphql
arguments: 
  "body" (url-encoded): {
    "query": "29746fd23262d23f528e1f5b9b427437",
    "variables": {
      "name": "^repo_name",
      "owner": "^owner",
      "query": "is:issue archived:false repo:^owner/^repo_name sort:created-desc"
    }
  }
returns: JSON object with issues data
viewport_effect: Displays the issues list sorted by the specified criteria
```

```interactive_element_graphql_labels
location_page: ^owner/^repo_name/labels
type: GraphQL Query
visual_element: Labels list in the repository
trigger: Load labels list
request: GET https://github.com/_graphql
arguments: 
  "body" (url-encoded): {
    "query": "b314e1ada402f5a1ad5a80f5d3395c1d",
    "variables": {
      "nodes": ["^label_id_1", "^label_id_2", "^label_id_3", ...]
    }
  }
returns: JSON object with labels data
viewport_effect: Displays the list of labels associated with the repository
```
