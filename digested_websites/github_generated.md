```interactive_element_search_repository
location_page: ^root/search
type: Search Bar
visual_element: Top navigation search bar with magnifying glass icon
trigger: Type repository name (e.g., "^owner/^repo_name") and submit search
request: GET https://github.com/search
arguments:
  URL params:
    q: "^owner/^repo_name"
    type: "repositories"
returns: HTML page content with repository search results
effect: Searches for repositories matching the query
viewport_effect: Displays a list of repositories matching the search term
```

```interactive_element_repository_link
location_page: ^root/search?q=^owner%2F^repo_name&type=repositories
type: Link
visual_element: Blue hyperlink text with repository name (e.g., "^owner/^repo_name") in search results
trigger: Click on the repository name link in the search results
request: GET https://github.com/^owner/^repo_name
returns: HTML page content for the repository main page
effect: Navigates to the selected repository's main page
viewport_effect: Loads the repository overview, showing code, issues, and other tabs
```

```interactive_element_issues_tab
location_page: ^owner/^repo_name
type: Tab Button
visual_element: Gray tab labeled "Issues" in the repository navigation bar
trigger: Click on the "Issues" tab
request: GET https://github.com/^owner/^repo_name/issues
returns: HTML page content for the issues list
effect: Navigates to the issues list for the repository
viewport_effect: Displays the issues list with filtering and sorting options
```

```interactive_element_issues_list_graphql
location_page: ^owner/^repo_name/issues
type: Data Fetch (GraphQL)
visual_element: (Not directly visible; triggered when issues page loads or filters change)
trigger: Load issues page or change filters (e.g., state, label, sort)
request: GET https://github.com/_graphql
arguments:
  "body" (url-encoded): {
    "query": "29746fd23262d23f528e1f5b9b427437",
    "variables": {
      "name": "^repo_name",
      "owner": "^owner",
      "query": "^query"
    }
  }
returns: JSON with issues data matching the query/filter
effect: Fetches issues matching the current filter/sort/search criteria
viewport_effect: Updates the issues list display according to the applied filters
```

```interactive_element_labels_dropdown
location_page: ^owner/^repo_name/issues
type: Dropdown
visual_element: "Labels" filter button in the issues toolbar
trigger: Click on the "Labels" button to open the labels dropdown
request: GET https://github.com/_graphql
arguments:
  "body" (url-encoded): {
    "query": "b480cbd1d6d3f7ba4a98229e88acf3fd",
    "variables": {
      "count": 100,
      "labelNames": "",
      "owner": "^owner",
      "repo": "^repo_name",
      "shouldQueryByNames": false
    }
  }
returns: JSON with available labels, their colors, and descriptions
effect: Fetches all available labels for the repository
viewport_effect: Displays a dropdown menu listing all labels with checkboxes
```

```interactive_element_label_filter
location_page: ^owner/^repo_name/issues
type: Checkbox
visual_element: Checkbox next to a label name in the labels dropdown
trigger: Click on a label's checkbox to filter issues by that label
request: GET https://github.com/_graphql
arguments:
  "body" (url-encoded): {
    "query": "29746fd23262d23f528e1f5b9b427437",
    "variables": {
      "name": "^repo_name",
      "owner": "^owner",
      "query": "is:issue label:\"^label_name\" repo:^owner/^repo_name sort:created-desc"
    }
  }
returns: JSON with issues filtered by the selected label
effect: Filters the issues list to show only issues with the selected label
viewport_effect: Updates the issues list to display only issues tagged with the chosen label
```

```interactive_element_state_toggle
location_page: ^owner/^repo_name/issues
type: Tab Button
visual_element: "Open" and "Closed" tabs above the issues list
trigger: Click on the "Closed" tab to view closed issues (or "Open" to view open issues)
request: GET https://github.com/_graphql
arguments:
  "body" (url-encoded): {
    "query": "22d008b451590c967cc8d672452db3f9",
    "variables": {
      "includeReactions": false,
      "name": "^repo_name",
      "owner": "^owner",
      "query": "is:issue state:closed label:\"^label_name\" repo:^owner/^repo_name sort:created-desc",
      "skip": 0
    }
  }
returns: JSON with issues filtered by state (open/closed) and label
effect: Changes the issues list to show only open or closed issues as selected
viewport_effect: Updates the issues list to reflect the selected state filter
```

```interactive_element_label_validate
location_page: ^owner/^repo_name/issues
type: Data Fetch (Validation)
visual_element: (Not directly visible; triggered when filtering by label)
trigger: Filter issues by label (e.g., after selecting a label checkbox)
request: GET https://github.com/_filter/labels/validate
arguments:
  URL params:
    repo: "^owner/^repo_name"
    q: "^label_name"
    filter_value: "^label_name"
returns: JSON with label metadata (name, description, color)
effect: Validates and fetches metadata for the selected label
viewport_effect: No direct UI change; supports label filtering logic
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
    "variables":{
      "includeReactions":false,
      "name":"^repo_name",
      "owner":"^owner",
      "query":"is:issue state:^state label:\"^label_name\" repo:^owner/^repo_name sort:created-asc",
      "skip":0
    }
  }
effect: Sorts the issues list by creation date in ascending order (oldest first)
returns: JSON with paginated issues data sorted by oldest creation date first
viewport_effect: Updates the issues list display to show issues sorted chronologically from oldest to newest
```
