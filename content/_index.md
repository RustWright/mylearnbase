+++
template = "home.html"

[extra]
lang = "en"
name = "My Learn Base"
# Logo mark as the homepage avatar. favicon.svg (explicit brand blue + dark-mode
# media query), NOT logo.svg — currentColor renders black when loaded via <img>.
avatar = "img/favicon.svg"
bio = "I build things to learn — and write down how."
links = [
  { name = "GitHub", icon = "github", url = "https://github.com/RustWright" },
  { name = "LinkedIn", icon = "linkedin", url = "https://www.linkedin.com/in/efe-erhie" },
]
footer = false
recent = true
recent_max = 5
recent_more_text = "more posts »"
date_format = "%b %-d, %Y"
guide = [
  { name = "logbook", path = "/posts/logbook", desc = "Build journals from real projects, feature by feature." },
  { name = "concepts", path = "/posts/concepts", desc = "Interactive demos of the ideas behind the work." },
  { name = "workflows", path = "/posts/workflows", desc = "Repeatable processes I actually use." },
  { name = "opinions", path = "/posts/opinions", desc = "Takes on tools, practices, and trade-offs." },
  { name = "resources", path = "/posts/resources", desc = "Curated references worth keeping." },
]
+++

Logbooks of real projects, the workflows I actually use, and interactive demos of the ideas behind them — built in the open as I learn.
