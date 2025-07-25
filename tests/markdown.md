```interactive_element_search
location_page: data:,
trigger: {'url': 'https://github.com'}
request: GET https://github.com/search
arguments: URL params: q="numpy", type="repositories"
returns: JSON object with keys: payload, title
```

```interactive_element_batch_deferred_sponsor_buttons
location_page: data:,
trigger: {'url': 'https://github.com'}
request: POST https://github.com/sponsors/batch_deferred_sponsor_buttons
arguments: "body" (form-data): [multipart form data]
returns: JSON object with keys: item-288276-908607, item-327203-20206590, item-23187665-72523920
```

```interactive_element_main
location_page: data:,
trigger: {'url': 'https://github.com'}
request: GET https://github.com/numpy/numpy/latest-commit/main
returns: JSON object with keys: oid, url, date, shortMessageHtmlLink, bodyMessageHtml, author, authors, committerAttribution, committer, pusher, pushedDate, status, isSpoofed
```

```interactive_element_refs
location_page: data:,
trigger: {'url': 'https://github.com'}
request: GET https://github.com/numpy/numpy/refs
arguments: URL params: type="branch"
returns: JSON object with keys: refs, cacheKey
```

```interactive_element_main
location_page: data:,
trigger: {'url': 'https://github.com'}
request: GET https://github.com/numpy/numpy/tree-commit-info/main
returns: JSON object with keys: .circleci, .devcontainer, .github, .spin, benchmarks, branding/logo, doc, meson_cpu, numpy, requirements, tools, vendored-meson, .cirrus.star, .clang-format, .codecov.yml, .coveragerc, .ctags.d, .editorconfig, .gitattributes, .gitignore, .gitmodules, .mailmap, CITATION.bib, CONTRIBUTING.rst, INSTALL.rst, LICENSE.txt, LICENSES_bundled.txt, README.md, THANKS.txt, azure-pipelines.yml...
```

```interactive_element_main
location_page: data:,
trigger: {'url': 'https://github.com'}
request: GET https://github.com/numpy/numpy/overview-files/main
returns: JSON object with keys: files, processingTime
```

```interactive_element_branch-and-tag-count
location_page: data:,
trigger: {'url': 'https://github.com'}
request: GET https://github.com/numpy/numpy/branch-and-tag-count
returns: JSON object with keys: branches, tags
```

```interactive_element__graphql
location_page: data:,
trigger: {'url': 'https://github.com'}
request: GET https://github.com/_graphql
arguments: "body" (url-encoded): 
{
  "query": "29746fd23262d23f528e1f5b9b427437",
  "variables": {
    "name": "numpy",
    "owner": "numpy",
    "query": "is:issue archived:false repo:numpy/numpy sort:created-desc"
  }
}
returns: JSON object with keys: data
```

```interactive_element__graphql
location_page: data:,
trigger: {'url': 'https://github.com'}
request: GET https://github.com/_graphql
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
returns: JSON object with keys: data
```

```interactive_element__graphql
location_page: data:,
trigger: {'url': 'https://github.com'}
request: GET https://github.com/_graphql
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
returns: JSON object with keys: data, extensions
```

```interactive_element_search
location_page: data:,
trigger: {'url': 'https://github.com'}
request: GET https://github.com/search
arguments: URL params: q="numy", type="repositories"
returns: HTML page content
```

```interactive_element_numpy
location_page: data:,
trigger: {'url': 'https://github.com'}
request: GET https://github.com/numpy/numpy
returns: HTML page content
```

```interactive_element_issues
location_page: data:,
trigger: {'url': 'https://github.com'}
request: GET https://github.com/numpy/numpy/issues
returns: HTML page content
```

```interactive_element_labels
location_page: data:,
trigger: {'url': 'https://github.com'}
request: GET https://github.com/numpy/numpy/labels
returns: HTML page content
```