```interactive_element_get_main
type: GET request
visual_element: Page navigation or link click
trigger: User interaction (click, hover, form submission, etc.)
request: GET https://github.com/numpy/numpy/latest-commit/main
arguments: {}
effect: Fetches data from server
returns: JSON or HTML response data
example return: {
  "oid": d02611ad99488637b48f4be203f297ea7b29c95d,
  "url": /numpy/numpy/commit/d02611ad99488637b48f4be203f297ea7b29c95d,
  "date": 2025-07-17T02:43:20.000-07:00,
  "shortMessageHtmlLink": <a data-pjax="true" class="Link--secondary" href="/numpy/numpy/commit/d02611ad99...,
  "bodyMessageHtml": Improve docstring examples for dstack and column_stack,
  "author": dict with keys: displayName, login, path, avatarUrl,
  "authors": list with 1 items,
  "committerAttribution": False,
  "committer": dict with keys: login, displayName, avatarUrl, path, isGitHub,
  "pusher": None,
  ... (3 more keys)
}
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
example return: {
  ".circleci": dict with keys: oid, url, date, shortMessageHtmlLink,
  ".devcontainer": dict with keys: oid, url, date, shortMessageHtmlLink,
  ".github": dict with keys: oid, url, date, shortMessageHtmlLink,
  ".spin": dict with keys: oid, url, date, shortMessageHtmlLink,
  "benchmarks": dict with keys: oid, url, date, shortMessageHtmlLink,
  "branding/logo": dict with keys: oid, url, date, shortMessageHtmlLink,
  "doc": dict with keys: oid, url, date, shortMessageHtmlLink,
  "meson_cpu": dict with keys: oid, url, date, shortMessageHtmlLink,
  "numpy": dict with keys: oid, url, date, shortMessageHtmlLink,
  "requirements": dict with keys: oid, url, date, shortMessageHtmlLink,
  ... (29 more keys)
}
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
example return: {
  "files": list with 4 items,
  "processingTime": 0
}
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
example return: {
  "branches": 32,
  "tags": 261
}
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
example return: response data
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
example return: {
  "data": dict with keys: repository
}
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
example return: {
  "item-0": ,
  "item-1": ,
  "item-2": ,
  "item-3": ,
  "item-4": ,
  "item-5":   <span class="d-inline-block ml-1">
      &bull;
        <a class="Link--muted ...,
  "item-6": ,
  "item-7": ,
  "item-8": ,
  "item-9": ,
  ... (15 more keys)
}
viewport_effect: Updates page content or shows success/error message
```