```interactive_element_search
location_page: https://github.com/search?q=numpy&type=repositories
type: Search
visual_element: Search bar in the top right corner of the GitHub homepage
trigger: Press the enter key to submit the search query in the GitHub search bar
request: GET https://github.com/search
arguments: 
  URL params: 
    q: "numpy"
    type: "repositories"
effect: Executes a search for repositories matching the term "numpy"
returns: HTML page content with search results for repositories
viewport_effect: Displays a list of repositories matching the search term "numpy"
```

```interactive_element_navigation
location_page: https://github.com/numpy/numpy
type: Link
visual_element: Blue hyperlink text 'numpy/numpy' in the search results
trigger: Click on the 'numpy/numpy' link in the search results
request: GET https://github.com/numpy/numpy
returns: HTML page content of the numpy repository
viewport_effect: Navigates to the numpy repository page
```

```interactive_element_issues_tab
location_page: https://github.com/numpy/numpy/issues
type: Tab
visual_element: Gray text 'Issues' tab with a badge showing the number of issues
trigger: Click on the 'Issues' tab
request: GET https://github.com/numpy/numpy/issues
returns: HTML page content of the issues section
viewport_effect: Displays the issues list for the numpy repository
```

```interactive_element_labels_dropdown
location_page: https://github.com/numpy/numpy/issues
type: Dropdown
visual_element: Gray text 'Labels' button with a small downward arrow
trigger: Click on the 'Labels' button to view all available labels
request: GET https://github.com/_graphql
arguments: 
  "body" (url-encoded): 
    {
      "query": "b480cbd1d6d3f7ba4a98229e88acf3fd",
      "variables": {
        "count": 100,
        "labelNames": "",
        "owner": "numpy",
        "repo": "numpy",
        "shouldQueryByNames": false
      }
    }
effect: Retrieves a list of labels available for filtering issues
returns: JSON object with label data
viewport_effect: Opens a dropdown menu displaying available labels
```

```interactive_element_closed_issues
location_page: https://github.com/numpy/numpy/issues?q=is%3Aissue%20state%3Aclosed
type: Button
visual_element: Gray text 'Closed' button with a badge showing the number of closed issues
trigger: Click on the 'Closed' button to view closed issues
request: GET https://github.com/_graphql
arguments: 
  "body" (url-encoded): 
    {
      "query": "22d008b451590c967cc8d672452db3f9",
      "variables": {
        "includeReactions": false,
        "name": "numpy",
        "owner": "numpy",
        "query": "is:issue state:closed label:\"00 - Bug\" repo:numpy/numpy sort:created-desc",
        "skip": 0
      }
    }
effect: Filters the issues list to show only closed issues
returns: JSON object with closed issues data
viewport_effect: Updates the issues list to display only closed issues
```

```interactive_element_sort_oldest
location_page: numpy/numpy/issues
type: Dropdown
visual_element: Sort dropdown button with "Oldest" option in the issues list header
trigger: Click on sort dropdown and select "Oldest"
request: GET https://github.com/_graphql
arguments: 
  "body" (url-encoded): 
    {
      "query": "22d008b451590c967cc8d672452db3f9",
      "variables": {
        "includeReactions": false,
        "name": "numpy",
        "owner": "numpy",
        "query": "is:issue state:closed sort:created-asc repo:numpy/numpy",
        "skip": 0
      }
    }
effect: Sorts the issues list by creation date in ascending order (oldest first)
returns: JSON with paginated issues data sorted by oldest creation date first
viewport_effect: Updates the issues list display to show issues sorted chronologically from oldest to newest
```

```interactive_element_issue_details
location_page: https://github.com/numpy/numpy/issues/291
type: Link
visual_element: Issue title 'Changes in PyArray_FromAny between 1.5.x and 1.6.x' in the issues list
trigger: Click on the issue title to view its details
request: GET https://github.com/_graphql
arguments: 
  "body" (url-encoded): 
    {
      "query": "2d7d4b00e17984f22f2bb06bd6eeb12d",
      "variables": {
        "allowedOwner": null,
        "count": 15,
        "number": 291,
        "owner": "numpy",
        "repo": "numpy",
        "skip": null
      }
    }
effect: Retrieves detailed information about the selected issue
returns: JSON object with issue details
viewport_effect: Displays the detailed view of the selected issue
```