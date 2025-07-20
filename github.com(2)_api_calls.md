```interactive_element_get_main
type: GET request
visual_element: Page navigation or link click
trigger: User interaction (click, hover, form submission, etc.)
request: GET https://github.com/numpy/numpy/latest-commit/main
arguments: {}
effect: Fetches data from server
returns: JSON or HTML response data
viewport_effect: Updates page content
```

```interactive_element_get_main
type: GET request
visual_element: Page navigation or link click
trigger: User interaction (click, hover, form submission, etc.)
request: GET https://github.com/numpy/numpy/tree-commit-info/main
arguments: {}
effect: Fetches data from server
returns: JSON or HTML response data
viewport_effect: Updates page content
```

```interactive_element_get_main
type: GET request
visual_element: Page navigation or link click
trigger: User interaction (click, hover, form submission, etc.)
request: GET https://github.com/numpy/numpy/overview-files/main
arguments: {}
effect: Fetches data from server
returns: JSON or HTML response data
viewport_effect: Updates page content
```

```interactive_element_get_branch-and-tag-count
type: GET request
visual_element: Page navigation or link click
trigger: User interaction (click, hover, form submission, etc.)
request: GET https://github.com/numpy/numpy/branch-and-tag-count
arguments: {}
effect: Fetches data from server
returns: JSON or HTML response data
viewport_effect: Updates page content
```

```interactive_element_post_collect
type: POST request
visual_element: Form submission or button click
trigger: User interaction (click, hover, form submission, etc.)
request: POST https://collector.github.com/github/collect
arguments: {}
effect: Creates or submits new data
returns: JSON or HTML response data
viewport_effect: Updates page content or shows success/error message
```

```interactive_element_get__graphql
type: GET request
visual_element: GraphQL query interface
trigger: User interaction (click, hover, form submission, etc.)
request: GET https://github.com/_graphql?body=%7B%22query%22%3A%2229746fd23262d23f528e1f5b9b427437%22%2C%22variables%22%3A%7B%22name%22%3A%22numpy%22%2C%22owner%22%3A%22numpy%22%2C%22query%22%3A%22is%3Aissue%20archived%3Afalse%20repo%3Anumpy%2Fnumpy%20sort%3Acreated-desc%22%7D%7D
arguments: {
    "body": "{\"query\":\"29746fd23262d23f528e1f5b9b427437\",\"variables\":{\"name\":\"numpy\",\"owner\":\"numpy\",\"query\":\"is:issue archived:false repo:numpy/numpy sort:created-desc\"}}"
}
effect: Executes GraphQL query to fetch data
returns: JSON or HTML response data
viewport_effect: Updates page content
```

```interactive_element_post_pull_request_review_decisions
type: POST request
visual_element: Form submission or button click
trigger: User interaction (click, hover, form submission, etc.)
request: POST https://github.com/pull_request_review_decisions
arguments: {}
effect: Creates or submits new data
returns: JSON or HTML response data
viewport_effect: Updates page content or shows success/error message
```