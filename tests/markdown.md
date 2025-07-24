```interactive_element_step_1
location_page: ,
type: Interactive Element
visual_element: 
trigger: open_url with args {'url': 'https://github.com'}
request: GET https://github.com/search?q=numpy&type=repositories
effect: Performs search based on 
returns: JSON API response
response_structure:
  keys: ['payload', 'title']
additional_request_1: POST https://github.com/sponsors/batch_deferred_sponsor_buttons
  keys: ['item-288276-908607', 'item-327203-20206590', 'item-23187665-72523920']
additional_request_2: GET https://github.com/numpy/numpy/latest-commit/main
  keys: ['oid', 'url', 'date', 'shortMessageHtmlLink', 'bodyMessageHtml']
additional_request_3: GET https://github.com/numpy/numpy/refs?type=branch
  keys: ['refs', 'cacheKey']
additional_request_4: GET https://github.com/numpy/numpy/tree-commit-info/main
  keys: ['.circleci', '.devcontainer', '.github', '.spin', 'benchmarks']
additional_request_5: GET https://github.com/numpy/numpy/overview-files/main
  keys: ['files', 'processingTime']
additional_request_6: GET https://github.com/numpy/numpy/branch-and-tag-count
  keys: ['branches', 'tags']
additional_request_7: GET https://github.com/_graphql?body=%7B%22query%22%3A%2229746fd23262d23f528e1f5b9b427437%22%2C%22variables%22%3A%7B%22name%22%3A%22numpy%22%2C%22owner%22%3A%22numpy%22%2C%22query%22%3A%22is%3Aissue%20archived%3Afalse%20repo%3Anumpy%2Fnumpy%20sort%3Acreated-desc%22%7D%7D
  keys: ['data']
additional_request_8: GET https://github.com/_graphql?body=%7B%22query%22%3A%2294d38dded736cdabaf92c2e06e57dc3e%22%2C%22variables%22%3A%7B%22includeReactions%22%3Afalse%2C%22nodes%22%3A%5B%22I_kwDOAA3dP87CYJWK%22%2C%22I_kwDOAA3dP87B-PUE%22%2C%22I_kwDOAA3dP87B9gZ8%22%2C%22I_kwDOAA3dP87B9Lh1%22%2C%22I_kwDOAA3dP87BzbQL%22%2C%22I_kwDOAA3dP87BGb_Z%22%2C%22I_kwDOAA3dP87A9ZPS%22%2C%22I_kwDOAA3dP87ARGqU%22%2C%22I_kwDOAA3dP86_5GXW%22%2C%22I_kwDOAA3dP86_nYmy%22%2C%22I_kwDOAA3dP86_lHb1%22%2C%22I_kwDOAA3dP86_buBy%22%2C%22I_kwDOAA3dP86_XVnG%22%2C%22I_kwDOAA3dP86-xDnl%22%2C%22I_kwDOAA3dP86-PtAa%22%2C%22I_kwDOAA3dP86-GK8I%22%2C%22I_kwDOAA3dP86-EKh5%22%2C%22I_kwDOAA3dP869eJ2O%22%2C%22I_kwDOAA3dP869JKuS%22%2C%22I_kwDOAA3dP8685HPq%22%2C%22I_kwDOAA3dP868tsnz%22%2C%22I_kwDOAA3dP868pw6t%22%2C%22I_kwDOAA3dP868mNGE%22%2C%22I_kwDOAA3dP868le8V%22%2C%22I_kwDOAA3dP868OJk1%22%5D%7D%7D
  keys: ['data']
additional_request_9: GET https://github.com/_graphql?body=%7B%22query%22%3A%22b314e1ada402f5a1ad5a80f5d3395c1d%22%2C%22variables%22%3A%7B%22nodes%22%3A%5B%22MDU6TGFiZWw2MzU5MjE0%22%2C%22MDU6TGFiZWw2MzU5MjM5%22%2C%22MDU6TGFiZWwzNjgyNTgyNQ%3D%3D%22%2C%22MDU6TGFiZWw2MzU5OTkw%22%2C%22MDU6TGFiZWw2MzU5OTQ1%22%2C%22MDU6TGFiZWw2Mzk0ODU5%22%2C%22MDU6TGFiZWw4MTQ5ODUyMA%3D%3D%22%2C%22MDU6TGFiZWwyNDkxOTM0MDg%3D%22%2C%22MDU6TGFiZWw1NDYzNzg3NTQ%3D%22%2C%22MDU6TGFiZWw2MDI2MzkzNTQ%3D%22%2C%22MDU6TGFiZWw2MzU5ODE3%22%2C%22MDU6TGFiZWw2MzU5ODkz%22%2C%22MDU6TGFiZWw2MzU5OTI1%22%2C%22MDU6TGFiZWw2MzU5MzE1%22%2C%22MDU6TGFiZWw2MzU5MzUy%22%2C%22MDU6TGFiZWw1MzU0MDI0NjE%3D%22%2C%22MDU6TGFiZWwxMDI0Mzk1MTYw%22%2C%22MDU6TGFiZWwxMDM1MTUyODc5%22%2C%22MDU6TGFiZWwxMDg2NDkxNjAx%22%2C%22MDU6TGFiZWwxMTgxMzkwNjcx%22%2C%22MDU6TGFiZWwxMjMyMjA1NzM0%22%2C%22MDU6TGFiZWwxMjQ0NTEzNzg0%22%2C%22MDU6TGFiZWwxNTAxMDU3NTI2%22%2C%22MDU6TGFiZWwxNTAxMDU1NTI5%22%2C%22MDU6TGFiZWwxNzE1MDY0NjY1%22%2C%22MDU6TGFiZWwyMjUwNjA5MjQx%22%2C%22MDU6TGFiZWwyNTA2MDg1MzM1%22%2C%22LA_kwDOAA3dP87cvxtl%22%2C%22LA_kwDOAA3dP88AAAABlbVqug%22%2C%22LA_kwDOAA3dP88AAAABokdLGg%22%5D%7D%7D
  keys: ['data', 'extensions']
request: GET https://github.com/search?q=numy&type=repositories
effect: Performs search based on 
returns: HTML page content
page_analysis:
  title: Repository search results · GitHub
  page_indicators: ['search_page', 'has_forms', 'has_data_attributes']
  content_preview:  <!DOCTYPE html> <html lang="en" data-color-mode="auto" data-light-theme="light" data-dark-theme="dark" data-a11y-animated-images="system" data-a11y-link-underlines="true" > <head> <meta charset="utf-8"> <link rel="dns-prefetch" href="https://github.githubassets.com"> <link rel="dns-prefetch" href="https://avatars.githubusercontent.com"> <link rel="dns-prefetch" href="https://github-cloud.s3.amazonaws.com"> <link rel="dns-prefetch" href="https://user-images.githubusercontent.com/"> <link rel="preconnect" href="https://github.githubassets.com" crossorigin> <link rel="preconnect" href="https://avatars.githubusercontent.com"> <link crossorigin="anonymous" media="all" rel="stylesheet" href="https://github.githubassets.com/assets/light-d1334f2b22bf.css" /><link crossorigin="anonymous" media="all" rel="stylesheet" href="https://github.githubassets.com/assets/light_high_contrast-f695a361c6b2.css" /><link crossorigin="anonymous" media="all" rel="styl...
additional_html_request_1: GET https://github.com/numpy/numpy
  title: GitHub - numpy/numpy: The fundamental package for 
additional_html_request_2: GET https://github.com/numpy/numpy/issues
  title: GitHub · Where software is built
additional_html_request_3: GET https://github.com/numpy/numpy/labels
  title: GitHub · Where software is built
viewport_effect: Modifies page display or interaction state
```
