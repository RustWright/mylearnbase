+++
title = "Posts"
description = "Every post on My Learn Base, grouped by form (logbook, concepts, workflows, opinions and resources), plus an archive of earlier writing."
sort_by = "date"
template = "posts_aggregator.html"
page_template = "post.html"
insert_anchor_links = "right"
generate_feeds = true

[extra]
lang = "en"
title = "Posts"
subtitle = "Logbooks of real projects, the workflows I actually use, and interactive demos of the ideas behind them, all built in the open as I learn."
date_format = "%b %-d, %Y"
categorized = false
back_to_top = true
toc = true
comment = false
copy = true
outdate_alert = false
outdate_alert_days = 120

# The form guide: what each kind of post is, in the order the page lists them.
# templates/posts_aggregator.html iterates THIS array, so it is the one place
# that decides which forms appear and in what order. `name` is the subsection
# directory under content/posts/.
guide = [
  { name = "logbook", desc = "Build journals from real projects, feature by feature." },
  { name = "concepts", desc = "Interactive demos of the ideas behind the work." },
  { name = "workflows", desc = "Repeatable processes I actually use." },
  { name = "opinions", desc = "Takes on tools, practices, and trade-offs." },
  { name = "resources", desc = "Curated references worth keeping." },
  { name = "archive", desc = "Earlier writing, from before the site had forms." },
]
+++
