+++
title = "Résumé"
description = "Efe-Oghene Erhie, a mechanical engineer moving into robotics software. MEng at Waterloo, four years in manufacturing test and automation, and a public portfolio of simulation and systems work."
template = "resume.html"
aliases = ["/cv/"]

# The résumé is STRUCTURED DATA, not markdown prose. Each role, degree, skill
# group and award is its own record, so templates/resume.html can lay them out
# the way a résumé needs: organisation over role, dates right-aligned on the
# role's line. Markdown cannot express that — it renders a heading and a
# separate date paragraph, and CSS cannot reliably put those on one line.
#
# This file is still the single source. The web page renders from it, the PDF
# is printed from that page (scripts/build-resume-pdf.sh), and build.sh's drift
# check hashes this file. Dates are abbreviated so the date column stays narrow.

[extra]
title = "Efe-Oghene Erhie"
subtitle = "Mechanical engineer moving into robotics software. MEng candidate at Waterloo."
pdf = "/resume/efe-oghene-erhie-resume.pdf"

[[extra.education]]
degree = "MEng, Mechanical & Mechatronics Engineering"
school = "University of Waterloo"
dates = "Sep 2026 – present"
details = ["Co-operative, course-based"]

[[extra.education]]
degree = "BSc, Mechanical Engineering"
school = "University of Manitoba"
dates = "Graduated Jun 2022"
details = ["GPA 4.36 / 4.50", "Best Graduating Student, Department of Mechanical Engineering"]

[[extra.experience]]
org = "Antec Controls"
role = "Manufacturing Specialist"
dates = "Nov 2022 – Aug 2026"
bullets = [
  "Operated and maintained automated test equipment for airflow testing of valves used in critical environments.",
  "Owned technical documentation and calibration procedures maintaining NVLAP accreditation for airflow measurement systems.",
  "Supported planning and execution of a production facility relocation into a space twice the size of the previous one.",
  "Provided strategic support implementing a new ERP system (IFS Cloud) integrating manufacturing and inventory processes.",
]

[[extra.experience]]
org = "PepsiCo Beverages Canada"
role = "Operations Leadership Trainee"
dates = "Aug 2022 – Oct 2022"
bullets = [
  "Led a project to improve reliability of critical equipment at the beverage production plant.",
  "Coordinated equipment contractors to maximise the value of on-site visits.",
  "Analysed and improved the changeover process on key machines of the bottling line.",
]

[[extra.experience]]
org = "Academic Learning Centre, University of Manitoba"
role = "Content / Study Skills Tutor"
dates = "Aug 2021 – May 2022"
bullets = [
  "Tutored engineering and science courses including thermodynamics, fluid mechanics, and CAD.",
  "Coached students on study technique and time management to build independent learning capability.",
]

[[extra.experience]]
org = "PepsiCo Beverages Canada"
role = "Production Shift Supervisor (Co-op)"
dates = "Jan 2021 – Sep 2021"
bullets = [
  "Directed a production team against cost, line efficiency, waste, safety and productivity standards.",
  "Oversaw facility equipment reliability to minimise downtime.",
  "Built front-line capability through training and communication.",
]

[[extra.skills]]
label = "Languages"
items = "Python, C++, Rust, JavaScript"

[[extra.skills]]
label = "Simulation & numerical"
items = "NumPy vectorisation, spatial partitioning, control-loop tuning, cross-implementation performance profiling"

[[extra.skills]]
label = "Systems"
items = "Rust/WebAssembly toolchain, Tauri, event-sourced data models, static-site architecture"

[[extra.skills]]
label = "Engineering"
items = "SolidWorks, AutoCAD, Fusion 360, GD&T, automated test equipment, calibration procedure authorship, NVLAP-compliant documentation, ERP systems (IFS Cloud)"

[[extra.projects]]
name = "Boids flocking simulation"
stack = "Python · NumPy · Rust · WebAssembly"
page = "projects/boids.md"
summary = "A flocking model built three times over to study the same system from different angles: a scalar Python reference, a vectorised NumPy rewrite, and a Rust core compiled to WebAssembly. Covers control-loop stability under changing gains, and the move from an O(n²) neighbour scan to a spatial grid."

[[extra.projects]]
name = "omni-me"
stack = "Rust · Tauri · Dioxus"
page = "projects/omni-me.md"
summary = "A cross-platform personal-data application. Event-sourced transaction model with multi-source reconciliation, recurring-transaction detection, and multi-currency account handling."

[[extra.projects]]
name = "mylearnbase"
stack = "Zola · Tera · JavaScript"
page = "projects/mylearnbase.md"
# Named, never "this site": the same text is printed, and a PDF has no "here".
summary = "A static portfolio and learning journal at mylearnbase.com. Build-time TF-IDF for content-based related posts, in-browser search over a pre-built index, and self-contained interactive demos embedded in articles."

[[extra.awards]]
name = "Best Graduating Student, Department of Mechanical Engineering"
dates = "2022"

[[extra.awards]]
name = "Dean's Honour List, Faculty of Engineering"
dates = "2018 – 2022"

[[extra.awards]]
name = "UMSU Scholarship"
dates = "2019 – 2021"

[[extra.awards]]
name = "International Undergraduate Student Scholarship"
dates = "2019 – 2021"

[[extra.awards]]
name = "Grettir Eggertson Memorial Scholarship"
dates = "2019 – 2021"
+++
