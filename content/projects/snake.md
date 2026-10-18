+++
title = "Snake reinforcement learning"
description = "Snake bots built from a hand-written rule bot up to a deep Q-network, in Python and in Rust compiled to WebAssembly, used to study what a learning agent needs to be told."
weight = 15

[extra]
# active | complete. Anything else fails the build (templates/project.html).
status = "complete"
period = "August – October 2026"
stack = ["Python", "PyTorch", "Rust", "WebAssembly", "Dioxus"]
# The PUBLIC export. The working repository is private and must never be linked.
repo = "https://github.com/RustWright/snake-dqn"
posts = [
  "posts/concepts/choosing-what-a-snake-bot-sees.md",
  "posts/concepts/what-the-snake-bot-was-missing.md",
]
+++

A sequence of bots for the classic Snake game, each measured against the one before it. A hand-written rule bot sets the bar. A Q-table learns to beat it from the same five features. A deep Q-network then replaces the table, so the bot can be given more than a table could hold.

Every agent is written twice. The Python versions use PyTorch, and the Rust versions use only the standard library, with backpropagation and the Adam optimizer written by hand and checked against PyTorch to nine decimal places. The Rust core is what runs in the demos on this page, and replay checks confirm that it plays exactly the same moves as the Python.

Two write-ups came out of it. The first is about choosing what the rule bot sees, and what five numbers can and cannot tell apart. The second follows the deep Q-network as it dies, and uses each death to find the next feature it needed, more than doubling the Q-table's score.
