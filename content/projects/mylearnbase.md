+++
title = "mylearnbase"
description = "The site you are reading, a static learning journal and portfolio with build-time related posts, in-browser search, and interactive demos that work inside articles and on their own."
weight = 30

[extra]
# active | complete. Anything else fails the build (templates/project.html).
status = "active"
period = "February 2026 – present"
stack = ["Zola", "Tera", "JavaScript", "Python"]
repo = "https://github.com/RustWright/mylearnbase"
logbook = "posts/logbook/mylearnbase/_index.md"
# Concepts posts whose question came from building this site: search, the
# Related links, and the site's own logo.
posts = [
  "posts/concepts/how-search-works.md",
  "posts/concepts/tf-idf.md",
  "posts/concepts/how-svgs-work.md",
]
+++

The site you are reading. It is built with Zola, so every page is plain HTML generated ahead of time and nothing runs per visitor.

Most of the work is in making a static site do more than serve pages. Related posts are chosen at build time by comparing the text of every post. Search runs entirely in the browser, over an index built during deployment. Interactive demos are self-contained pages that embed into articles and also stand on their own, and the build works out which post each demo belongs to instead of keeping that list by hand.

Several of those features led to a concepts post explaining the idea underneath, alongside the logbook entries that record how each one was built.
