```interactive_element_search
location_page: https://github.com/search?q=numpy&type=repositories
type: Search
visual_element: Search bar at the top of the GitHub homepage
trigger: press_key("enter", "to execute the search for 'numpy' in the GitHub search bar")
example:
result = get_request("https://github.com/search", {
    "q": "numpy",
    "type": "repositories"
})
effect: Executes a search for repositories related to 'numpy'
returns: HTML page content with search results
viewport_effect: Displays a list of repositories matching the search query
```

```interactive_element_repository_navigation
location_page: https://github.com/numpy/numpy
type: Link
visual_element: Blue hyperlink text 'numpy/numpy' in search results
trigger: click(408, 160, "blue hyperlink text 'numpy/numpy', approximately 100x20 pixels, located near the top of the search results")
example:
result = get_request("https://github.com/numpy/numpy")
effect: Navigates to the numpy repository page
returns: HTML page content of the numpy repository
viewport_effect: Displays the main page of the numpy repository
```

```interactive_element_issues_tab
location_page: https://github.com/numpy/numpy/issues
type: Tab
visual_element: Gray tab labeled 'Issues' next to the 'Code' tab
trigger: click(150, 158, "gray tab labeled 'Issues', approximately 50x20 pixels, located next to the 'Code' tab")
example:
result = get_request("https://github.com/numpy/numpy/issues")
effect: Opens the issues page of the numpy repository
returns: HTML page content of the issues section
viewport_effect: Displays a list of issues related to the numpy repository
```

```interactive_element_labels_filter
location_page: https://github.com/numpy/numpy/labels
type: Button
visual_element: Gray button labeled 'Labels' in the toolbar above the list of issues
trigger: click(785, 228, "gray button labeled 'Labels', approximately 80x30 pixels, located in the toolbar above the list of issues")
example:
result = get_request("https://github.com/numpy/numpy/labels")
effect: Opens the labels page showing all available labels for filtering issues
returns: HTML page content with a list of labels
viewport_effect: Displays available labels with their colors and descriptions
```

```interactive_element_label_selection
location_page: https://github.com/numpy/numpy/issues?q=state%3Aopen%20label%3A%2200%20-%20Bug%22
type: Label
visual_element: Label '00 - Bug' in the labels list
trigger: click(75, 385, "label '00 - Bug', approximately 60x20 pixels, located near the top of the labels list")
example:
result = get_request("https://github.com/_graphql", {
    "body": {
        "query": "29746fd23262d23f528e1f5b9b427437",
        "variables": {
            "name": "numpy",
            "owner": "numpy",
            "query": "state:open label:\"00 - Bug\" repo:numpy/numpy sort:created-desc"
        }
    }
})
effect: Filters issues by the '00 - Bug' label
returns: JSON with issues data filtered by the selected label
viewport_effect: Displays issues associated with the '00 - Bug' label
```

```interactive_element_sort_oldest
location_page: https://github.com/numpy/numpy/issues
type: Dropdown
visual_element: Sort dropdown button with "Oldest" option in the issues list header
trigger: Click on sort dropdown and select "Oldest"
example:
result = get_request("https://github.com/_graphql", {
    "body": {
        "query": "22d008b451590c967cc8d672452db3f9",
        "variables": {
            "includeReactions": false,
            "name": "numpy",
            "owner": "numpy",
            "query": "state:closed label:\"00 - Bug\" author:andyfaff repo:numpy/numpy sort:created-desc",
            "skip": 0
        }
    }
})
effect: Sorts the issues list by creation date in ascending order (oldest first)
returns: JSON with paginated issues data sorted by oldest creation date first
viewport_effect: Updates the issues list display to show issues sorted chronologically from oldest to newest
```

```interactive_element_issue_details
location_page: https://github.com/numpy/numpy/issues/24966
type: Link
visual_element: Issue titled 'BUG: scipy and numpy, --use-scipy-openblas vs --with-scipy-openblas' in the issues list
trigger: click(150, 330, "issue titled 'BUG: scipy and numpy, --use-scipy-openblas vs --with-scipy-openblas', approximately 600x20 pixels, located at the top of the issues list")
example:
result = get_request("https://github.com/_graphql", {
    "body": {
        "query": "2d7d4b00e17984f22f2bb06bd6eeb12d",
        "variables": {
            "allowedOwner": null,
            "count": 15,
            "number": 24966,
            "owner": "numpy",
            "repo": "numpy",
            "skip": null
        }
    }
})
effect: Opens the details page of the selected issue
returns: JSON with detailed issue data including comments and metadata
viewport_effect: Displays the full details of the selected issue including description and comments
```