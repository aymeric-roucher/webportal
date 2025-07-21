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

```interactive_element_post_pull_request_review_decisions
type: POST request
visual_element: Form submission or button click
trigger: User interaction (click, hover, form submission, etc.)
request: POST https://github.com/pull_request_review_decisions
arguments: {}
effect: Creates or submits new data
returns: JSON or HTML response data
example return: {}
viewport_effect: Updates page content or shows success/error message
```