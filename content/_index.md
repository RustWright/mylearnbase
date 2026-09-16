+++
template = "home.html"

[extra]
lang = "en"
name = "My Learn Base"
# Logo mark as the homepage avatar. favicon.svg (explicit brand blue + dark-mode
# media query), NOT logo.svg: currentColor renders black when loaded via <img>.
avatar = "img/favicon.svg"
bio = "I build things to learn, then write down how."
links = [
  { name = "GitHub", icon = "github", url = "https://github.com/RustWright" },
  { name = "LinkedIn", icon = "linkedin", url = "https://www.linkedin.com/in/efe-erhie" },
]
footer = false
recent = true
recent_max = 5
recent_more_text = "more posts »"
date_format = "%b %-d, %Y"

# The homepage routes by what a visitor came for, not by how the writing is
# filed. The post-form guide lives on /posts/ (content/posts/_index.md), where
# the reader has already chosen to read. `@/` paths make a renamed destination
# fail the build instead of shipping a dead door.
doors = [
  { name = "Projects", path = "@/projects/_index.md", desc = "What I've built, and how each one works." },
  { name = "Playground", path = "@/playground/_index.md", desc = "Interactive demos. No reading required." },
  { name = "Résumé", path = "@/resume/_index.md", desc = "Background, skills, and a PDF to download." },
]

# The "Now" line is the body of this file, below. It is a claim about the
# present, so it is dated: the reader can judge its freshness, and build.sh
# warns once this date is 90 days old. Update both together.
now_updated = "2026-09-16"
+++

Studying for an MEng in Mechanical & Mechatronics Engineering at Waterloo, and building [omni-me](@/projects/omni-me.md), an offline-first personal app in Rust.
