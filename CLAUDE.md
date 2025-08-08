# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Webportal is a Python project that converts websites into agent-friendly interfaces by:
1. Using a smolagents web agent to navigate websites
2. Looking at the network requests made by the agent to extract the API calls
3. Describing those API calls so that any agent that want to access that specific ressource can directly do it using the API calls instead of having to crawl the website again.

For the user, it would enter a website url, and, either the site has already been processed in which cas it can download a markdown file. Otherwise, it will process the website and in the meantime provide a progress bar with images of the website being crawled.

### Todo
- peu importe l'algorithme utilisé au début, on veut juste que tout puisse tourner sur une image docker avec la partie playwright et la partie selenium (celui d'aymeric, et un algo où on parse juste le site en demandant au llm de trouver les fonctionnalités principales, on peut faire un mélange, l'idée est que ça tourne facilement, d'avoir un docker avec les deux fonctionnalités et de pouvoir les utiliser en parallèle), je pense qu'il manque une information au llm au début pour avoir les bons liens. De plus, il lui faut des exemples d'utilisation de ces liens
- on veut une base de donnée sur un bucket avec: un dossier par site web, ensuite un sous dossier avec la date, et on sauvegarde tout dedans
- on veut remplacer tous les calls llm sauf Qwen obviously par gemini
- on veut faire le site avec ça, et notamment les fonctionnalités suivantes:
    - pouvoir voir les parsing en cours **optionnel**
    - pouvoir lancer un parsing, avec une API
    - pouvoir lancer le benchmark
    - avoir un aspect cybersécurité, le docker doit impérativement être séparé du site et ne pas permettre l'utilisation des clés API, avoir un accès restreint à la base de donnée
    - 
    - 
- lancer le benchmark et contacter aymeric
- lancer gcp 
- avoir sur le site une fonctionnalité pour lancer un benchmark de deux manières différentes. 
- on aura sans doute 3 manières:
    - browser seul
    - perplexity/google

    - llm + request + notre résultat
    - llm + browser + request + notre résultat

- add try except here
- try and launch it on google cloud
- try to do the benchmark
- add a specific step if an API is found- 
### Coding Style
- DO NOT USE TRY/EXCEPT blocks except if it is absolutely necessary (meaning that this is the only way to handle the error). And in that case, you should except a specific error.
- This is python3.13 code so DO NOT use "List" or "Dict" for typing, use "list" or "dict" instead. 
- Typing is important
- Always choose the simplest solutions that will do the job.
- do not rely on positional arguments, use keyword arguments instead.
- stop writing comments, they are useless.