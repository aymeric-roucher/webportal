# Interactive Elements Analysis

This file contains the analysis of interactive elements discovered during website exploration.
Each element shows the API calls triggered by user interactions.


## Step 1

```interactive_element_request
location_page: https://github.com/
trigger: open_url("https://github.com")
request: GET https://github.com/
returns: HTML page content
```


## Step 4

```interactive_element_batch_deferred_sponsor_buttons
location_page: https://github.com/search?q=numpy&type=repositories
trigger: press_key("enter", "to execute the search for 'numpy' on GitHub")
request: POST https://github.com/sponsors/batch_deferred_sponsor_buttons
arguments: "body" (form-data): [multipart form data]
returns: JSON object with keys: item-288276-908607, item-327203-20206590, item-23187665-72523920
```

```interactive_element_search
location_page: https://github.com/search?q=numpy&type=repositories
trigger: press_key("enter", "to execute the search for 'numpy' on GitHub")
request: GET https://github.com/search?q=numpy&type=repositories
arguments: URL params: q="numpy", type="repositories"
returns: HTML page content
```


## Step 5

```interactive_element_main
location_page: https://github.com/numpy/numpy
trigger: click(400, 160, "blue hyperlink text 'numpy/numpy', approximately 100x20 pixels, located at the top of the search results list")
request: GET https://github.com/numpy/numpy/latest-commit/main
returns: JSON object with keys: oid, url, date, shortMessageHtmlLink, bodyMessageHtml...
```

```interactive_element_refs
location_page: https://github.com/numpy/numpy
trigger: click(400, 160, "blue hyperlink text 'numpy/numpy', approximately 100x20 pixels, located at the top of the search results list")
request: GET https://github.com/numpy/numpy/refs?type=branch
arguments: URL params: type="branch"
returns: JSON object with keys: refs, cacheKey
```

```interactive_element_main
location_page: https://github.com/numpy/numpy
trigger: click(400, 160, "blue hyperlink text 'numpy/numpy', approximately 100x20 pixels, located at the top of the search results list")
request: GET https://github.com/numpy/numpy/tree-commit-info/main
returns: JSON object with keys: .circleci, .devcontainer, .github, .spin, benchmarks...
```

```interactive_element_main
location_page: https://github.com/numpy/numpy
trigger: click(400, 160, "blue hyperlink text 'numpy/numpy', approximately 100x20 pixels, located at the top of the search results list")
request: GET https://github.com/numpy/numpy/overview-files/main
returns: JSON object with keys: files, processingTime
```

```interactive_element_branch-and-tag-count
location_page: https://github.com/numpy/numpy
trigger: click(400, 160, "blue hyperlink text 'numpy/numpy', approximately 100x20 pixels, located at the top of the search results list")
request: GET https://github.com/numpy/numpy/branch-and-tag-count
returns: JSON object with keys: branches, tags
```

```interactive_element_numpy
location_page: https://github.com/numpy/numpy
trigger: click(400, 160, "blue hyperlink text 'numpy/numpy', approximately 100x20 pixels, located at the top of the search results list")
request: GET https://github.com/numpy/numpy
returns: HTML page content
```


## Step 6

```interactive_element__graphql
location_page: https://github.com/numpy/numpy/issues
trigger: click(150, 158, "gray tab labeled 'Issues', approximately 50x20 pixels, located next to the 'Code' tab")
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
returns: JSON with data object containing structured information
```

```interactive_element__graphql
location_page: https://github.com/numpy/numpy/issues
trigger: click(150, 158, "gray tab labeled 'Issues', approximately 50x20 pixels, located next to the 'Code' tab")
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
returns: JSON with data object containing structured information
```

```interactive_element_issues
location_page: https://github.com/numpy/numpy/issues
trigger: click(150, 158, "gray tab labeled 'Issues', approximately 50x20 pixels, located next to the 'Code' tab")
request: GET https://github.com/numpy/numpy/issues
returns: HTML page content
```


## Step 7

```interactive_element__graphql
location_page: https://github.com/numpy/numpy/labels
trigger: click(785, 228, "gray button labeled 'Labels', approximately 80x30 pixels, located near the top of the page")
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
returns: JSON with data object containing structured information
```

```interactive_element_labels
location_page: https://github.com/numpy/numpy/labels
trigger: click(785, 228, "gray button labeled 'Labels', approximately 80x30 pixels, located near the top of the page")
request: GET https://github.com/numpy/numpy/labels
returns: HTML page content
```


## Step 8

```interactive_element__graphql
location_page: https://github.com/numpy/numpy/issues
trigger: click(150, 158, "gray tab labeled 'Issues', approximately 50x20 pixels, located next to the 'Code' tab")
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
returns: JSON with data object containing structured information
```

```interactive_element__graphql
location_page: https://github.com/numpy/numpy/issues
trigger: click(150, 158, "gray tab labeled 'Issues', approximately 50x20 pixels, located next to the 'Code' tab")
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
returns: JSON with data object containing structured information
```

```interactive_element_issues
location_page: https://github.com/numpy/numpy/issues
trigger: click(150, 158, "gray tab labeled 'Issues', approximately 50x20 pixels, located next to the 'Code' tab")
request: GET https://github.com/numpy/numpy/issues
returns: HTML page content
```


## Step 10

```interactive_element__graphql
location_page: https://github.com/numpy/numpy/issues?q=is%3Aissue%20state%3Aopen%20sort%3Acreated-asc
trigger: click(920, 565, "option labeled 'Oldest', approximately 50x20 pixels, located within the 'Order' submenu of the 'Sort' dropdown")
request: GET https://github.com/_graphql?body=%7B%22query%22%3A%2222d008b451590c967cc8d672452db3f9%22%2C%22variables%22%3A%7B%22includeReactions%22%3Afalse%2C%22name%22%3A%22numpy%22%2C%22owner%22%3A%22numpy%22%2C%22query%22%3A%22is%3Aissue%20state%3Aopen%20sort%3Acreated-asc%20repo%3Anumpy%2Fnumpy%22%2C%22skip%22%3A0%7D%7D
arguments: "body" (url-encoded): 
{
  "query": "22d008b451590c967cc8d672452db3f9",
  "variables": {
    "includeReactions": false,
    "name": "numpy",
    "owner": "numpy",
    "query": "is:issue state:open sort:created-asc repo:numpy/numpy",
    "skip": 0
  }
}
returns: JSON with data object containing structured information
```

```interactive_element__graphql
location_page: https://github.com/numpy/numpy/issues?q=is%3Aissue%20state%3Aopen%20sort%3Acreated-asc
trigger: click(920, 565, "option labeled 'Oldest', approximately 50x20 pixels, located within the 'Order' submenu of the 'Sort' dropdown")
request: GET https://github.com/_graphql?body=%7B%22query%22%3A%2294d38dded736cdabaf92c2e06e57dc3e%22%2C%22variables%22%3A%7B%22includeReactions%22%3Afalse%2C%22nodes%22%3A%5B%22MDU6SXNzdWU1OTAyNTUx%22%2C%22MDU6SXNzdWU2MzA4MTIy%22%2C%22MDU6SXNzdWU3NzE4NjM1%22%2C%22MDU6SXNzdWU3NzE4NjUw%22%2C%22MDU6SXNzdWU3NzE4NjU4%22%2C%22MDU6SXNzdWU3NzE4Njgw%22%2C%22MDU6SXNzdWU3NzIzOTkz%22%2C%22MDU6SXNzdWU3NzI0MDIy%22%2C%22MDU6SXNzdWU3NzI0MDIz%22%2C%22MDU6SXNzdWU3NzI1MjAz%22%2C%22MDU6SXNzdWU3NzI4MTUz%22%2C%22MDU6SXNzdWU3NzI4Mzk0%22%2C%22MDU6SXNzdWU3NzI4NTkz%22%2C%22MDU6SXNzdWU3NzI4NjE2%22%2C%22MDU6SXNzdWU3NzI4NjIy%22%2C%22MDU6SXNzdWU3NzI4ODAx%22%2C%22MDU6SXNzdWU3NzI4OTE0%22%2C%22MDU6SXNzdWU3NzI4OTIz%22%2C%22MDU6SXNzdWU3NzI4OTI2%22%2C%22MDU6SXNzdWU3NzI4OTYw%22%2C%22MDU6SXNzdWU3NzI5MDEw%22%2C%22MDU6SXNzdWU3NzI5MDE0%22%2C%22MDU6SXNzdWU3NzI5MDMz%22%2C%22MDU6SXNzdWU3NzI5MjAx%22%2C%22MDU6SXNzdWU3NzMxMDkw%22%5D%7D%7D
arguments: "body" (url-encoded): 
{
  "query": "94d38dded736cdabaf92c2e06e57dc3e",
  "variables": {
    "includeReactions": false,
    "nodes": [
      "MDU6SXNzdWU1OTAyNTUx",
      "MDU6SXNzdWU2MzA4MTIy",
      "MDU6SXNzdWU3NzE4NjM1",
      "MDU6SXNzdWU3NzE4NjUw",
      "MDU6SXNzdWU3NzE4NjU4",
      "MDU6SXNzdWU3NzE4Njgw",
      "MDU6SXNzdWU3NzIzOTkz",
      "MDU6SXNzdWU3NzI0MDIy",
      "MDU6SXNzdWU3NzI0MDIz",
      "MDU6SXNzdWU3NzI1MjAz",
      "MDU6SXNzdWU3NzI4MTUz",
      "MDU6SXNzdWU3NzI4Mzk0",
      "MDU6SXNzdWU3NzI4NTkz",
      "MDU6SXNzdWU3NzI4NjE2",
      "MDU6SXNzdWU3NzI4NjIy",
      "MDU6SXNzdWU3NzI4ODAx",
      "MDU6SXNzdWU3NzI4OTE0",
      "MDU6SXNzdWU3NzI4OTIz",
      "MDU6SXNzdWU3NzI4OTI2",
      "MDU6SXNzdWU3NzI4OTYw",
      "MDU6SXNzdWU3NzI5MDEw",
      "MDU6SXNzdWU3NzI5MDE0",
      "MDU6SXNzdWU3NzI5MDMz",
      "MDU6SXNzdWU3NzI5MjAx",
      "MDU6SXNzdWU3NzMxMDkw"
    ]
  }
}
returns: JSON with data object containing structured information
```

```interactive_element__graphql
location_page: https://github.com/numpy/numpy/issues?q=is%3Aissue%20state%3Aopen%20sort%3Acreated-asc
trigger: click(920, 565, "option labeled 'Oldest', approximately 50x20 pixels, located within the 'Order' submenu of the 'Sort' dropdown")
request: GET https://github.com/_graphql?body=%7B%22query%22%3A%2229746fd23262d23f528e1f5b9b427437%22%2C%22variables%22%3A%7B%22name%22%3A%22numpy%22%2C%22owner%22%3A%22numpy%22%2C%22query%22%3A%22is%3Aissue%20state%3Aopen%20sort%3Acreated-asc%20repo%3Anumpy%2Fnumpy%22%7D%7D
arguments: "body" (url-encoded): 
{
  "query": "29746fd23262d23f528e1f5b9b427437",
  "variables": {
    "name": "numpy",
    "owner": "numpy",
    "query": "is:issue state:open sort:created-asc repo:numpy/numpy"
  }
}
returns: JSON with data object containing structured information
```

