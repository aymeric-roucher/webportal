```interactive_element_search
location_page: data:,
type: 
visual_element: 
trigger: 
request: GET https://github.com/search?q=numpy&type=repositories
arguments: URL params: q="numpy", type="repositories"
effect: 
returns: JSON with payload containing response data
viewport_effect: 
```

```interactive_element_batch_deferred_sponsor_buttons
location_page: data:,
type: 
visual_element: 
trigger: 
request: POST https://github.com/sponsors/batch_deferred_sponsor_buttons
arguments: "body" (form-data): [multipart form data]
effect: 
returns: JSON object with keys: item-288276-908607, item-327203-20206590, item-23187665-72523920
viewport_effect: 
```

```interactive_element_main
location_page: data:,
type: 
visual_element: 
trigger: 
request: GET https://github.com/numpy/numpy/latest-commit/main
effect: 
returns: JSON object with keys: oid, url, date, shortMessageHtmlLink, bodyMessageHtml...
viewport_effect: 
```

```interactive_element_refs
location_page: data:,
type: 
visual_element: 
trigger: 
request: GET https://github.com/numpy/numpy/refs?type=branch
arguments: URL params: type="branch"
effect: 
returns: JSON object with keys: refs, cacheKey
viewport_effect: 
```

```interactive_element_main
location_page: data:,
type: 
visual_element: 
trigger: 
request: GET https://github.com/numpy/numpy/tree-commit-info/main
effect: 
returns: JSON object with keys: .circleci, .devcontainer, .github, .spin, benchmarks...
viewport_effect: 
```

```interactive_element_main
location_page: data:,
type: 
visual_element: 
trigger: 
request: GET https://github.com/numpy/numpy/overview-files/main
effect: 
returns: JSON object with keys: files, processingTime
viewport_effect: 
```

```interactive_element_branch-and-tag-count
location_page: data:,
type: 
visual_element: 
trigger: 
request: GET https://github.com/numpy/numpy/branch-and-tag-count
effect: 
returns: JSON object with keys: branches, tags
viewport_effect: 
```

```interactive_element__graphql
location_page: data:,
type: 
visual_element: 
trigger: 
request: GET https://github.com/_graphql?body=%7B%22query%22%3A%2229746fd23262d23f528e1f5b9b427437%22%2C%22variables%22%3A%7B%22name%22%3A%22numpy%22%2C%22owner%22%3A%22numpy%22%2C%22query%22%3A%22is%3Aissue%20archived%3Afalse%20repo%3Anumpy%2Fnumpy%20sort%3Acreated-desc%22%7D%7D
arguments: "body" (url-encoded): 
{
  "query": "29746fd23262d23f528e1f5b9b427437",
  "variables": {
    "name": "numpy",
    "owner": "numpy",
    "query": "is:issue archived:false repo:numpy/numpy sort:created-desc"
  }
}
effect: 
returns: JSON with data object containing structured information
viewport_effect: 
```

```interactive_element__graphql
location_page: data:,
type: 
visual_element: 
trigger: 
request: GET https://github.com/_graphql?body=%7B%22query%22%3A%2294d38dded736cdabaf92c2e06e57dc3e%22%2C%22variables%22%3A%7B%22includeReactions%22%3Afalse%2C%22nodes%22%3A%5B%22I_kwDOAA3dP87CYJWK%22%2C%22I_kwDOAA3dP87B-PUE%22%2C%22I_kwDOAA3dP87B9gZ8%22%2C%22I_kwDOAA3dP87B9Lh1%22%2C%22I_kwDOAA3dP87BzbQL%22%2C%22I_kwDOAA3dP87BGb_Z%22%2C%22I_kwDOAA3dP87A9ZPS%22%2C%22I_kwDOAA3dP87ARGqU%22%2C%22I_kwDOAA3dP86_5GXW%22%2C%22I_kwDOAA3dP86_nYmy%22%2C%22I_kwDOAA3dP86_lHb1%22%2C%22I_kwDOAA3dP86_buBy%22%2C%22I_kwDOAA3dP86_XVnG%22%2C%22I_kwDOAA3dP86-xDnl%22%2C%22I_kwDOAA3dP86-PtAa%22%2C%22I_kwDOAA3dP86-GK8I%22%2C%22I_kwDOAA3dP86-EKh5%22%2C%22I_kwDOAA3dP869eJ2O%22%2C%22I_kwDOAA3dP869JKuS%22%2C%22I_kwDOAA3dP8685HPq%22%2C%22I_kwDOAA3dP868tsnz%22%2C%22I_kwDOAA3dP868pw6t%22%2C%22I_kwDOAA3dP868mNGE%22%2C%22I_kwDOAA3dP868le8V%22%2C%22I_kwDOAA3dP868OJk1%22%5D%7D%7D
arguments: "body" (url-encoded): 
{
  "query": "94d38dded736cdabaf92c2e06e57dc3e",
  "variables": {
    "includeReactions": false,
    "nodes": [
      "I_kwDOAA3dP87CYJWK",
      "I_kwDOAA3dP87B-PUE",
      "I_kwDOAA3dP87B9gZ8",
      "I_kwDOAA3dP87B9Lh1",
      "I_kwDOAA3dP87BzbQL",
      "I_kwDOAA3dP87BGb_Z",
      "I_kwDOAA3dP87A9ZPS",
      "I_kwDOAA3dP87ARGqU",
      "I_kwDOAA3dP86_5GXW",
      "I_kwDOAA3dP86_nYmy",
      "I_kwDOAA3dP86_lHb1",
      "I_kwDOAA3dP86_buBy",
      "I_kwDOAA3dP86_XVnG",
      "I_kwDOAA3dP86-xDnl",
      "I_kwDOAA3dP86-PtAa",
      "I_kwDOAA3dP86-GK8I",
      "I_kwDOAA3dP86-EKh5",
      "I_kwDOAA3dP869eJ2O",
      "I_kwDOAA3dP869JKuS",
      "I_kwDOAA3dP8685HPq",
      "I_kwDOAA3dP868tsnz",
      "I_kwDOAA3dP868pw6t",
      "I_kwDOAA3dP868mNGE",
      "I_kwDOAA3dP868le8V",
      "I_kwDOAA3dP868OJk1"
    ]
  }
}
effect: 
returns: JSON with data object containing structured information
viewport_effect: 
```

```interactive_element__graphql
location_page: data:,
type: 
visual_element: 
trigger: 
request: GET https://github.com/_graphql?body=%7B%22query%22%3A%22b314e1ada402f5a1ad5a80f5d3395c1d%22%2C%22variables%22%3A%7B%22nodes%22%3A%5B%22MDU6TGFiZWw2MzU5MjE0%22%2C%22MDU6TGFiZWw2MzU5MjM5%22%2C%22MDU6TGFiZWwzNjgyNTgyNQ%3D%3D%22%2C%22MDU6TGFiZWw2MzU5OTkw%22%2C%22MDU6TGFiZWw2MzU5OTQ1%22%2C%22MDU6TGFiZWw2Mzk0ODU5%22%2C%22MDU6TGFiZWw4MTQ5ODUyMA%3D%3D%22%2C%22MDU6TGFiZWwyNDkxOTM0MDg%3D%22%2C%22MDU6TGFiZWw1NDYzNzg3NTQ%3D%22%2C%22MDU6TGFiZWw2MDI2MzkzNTQ%3D%22%2C%22MDU6TGFiZWw2MzU5ODE3%22%2C%22MDU6TGFiZWw2MzU5ODkz%22%2C%22MDU6TGFiZWw2MzU5OTI1%22%2C%22MDU6TGFiZWw2MzU5MzE1%22%2C%22MDU6TGFiZWw2MzU5MzUy%22%2C%22MDU6TGFiZWw1MzU0MDI0NjE%3D%22%2C%22MDU6TGFiZWwxMDI0Mzk1MTYw%22%2C%22MDU6TGFiZWwxMDM1MTUyODc5%22%2C%22MDU6TGFiZWwxMDg2NDkxNjAx%22%2C%22MDU6TGFiZWwxMTgxMzkwNjcx%22%2C%22MDU6TGFiZWwxMjMyMjA1NzM0%22%2C%22MDU6TGFiZWwxMjQ0NTEzNzg0%22%2C%22MDU6TGFiZWwxNTAxMDU3NTI2%22%2C%22MDU6TGFiZWwxNTAxMDU1NTI5%22%2C%22MDU6TGFiZWwxNzE1MDY0NjY1%22%2C%22MDU6TGFiZWwyMjUwNjA5MjQx%22%2C%22MDU6TGFiZWwyNTA2MDg1MzM1%22%2C%22LA_kwDOAA3dP87cvxtl%22%2C%22LA_kwDOAA3dP88AAAABlbVqug%22%2C%22LA_kwDOAA3dP88AAAABokdLGg%22%5D%7D%7D
arguments: "body" (url-encoded): 
{
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
effect: 
returns: JSON with data object containing structured information
viewport_effect: 
```

```interactive_element_search
location_page: data:,
type: 
visual_element: 
trigger: 
request: GET https://github.com/search?q=numy&type=repositories
arguments: URL params: q="numy", type="repositories"
effect: 
returns: HTML page content
viewport_effect: 
```

```interactive_element_numpy
location_page: data:,
type: 
visual_element: 
trigger: 
request: GET https://github.com/numpy/numpy
effect: 
returns: HTML page content
viewport_effect: 
```

```interactive_element_issues
location_page: data:,
type: 
visual_element: 
trigger: 
request: GET https://github.com/numpy/numpy/issues
effect: 
returns: HTML page content
viewport_effect: 
```

```interactive_element_labels
location_page: data:,
type: 
visual_element: 
trigger: 
request: GET https://github.com/numpy/numpy/labels
effect: 
returns: HTML page content
viewport_effect: 
```