+++
title = "Dev Setup From Scratch: Claude Code, Dotfiles & Git Submodules"
slug = "dev-setup-from-scratch"
date = 2026-02-24
draft = false

[taxonomies]
tags = ["dev-setup", "dotfiles", "git", "claude-code", "productivity"]
series = ["Figuring Out My Dev Setup"]

[extra]
series_order = 1
+++

## Reflections

I have two primary machines for programming. The first is a Microsoft Surface Laptop 4 — light, portable, and the one I've been doing most of my development on recently. When I first started exploring CLI-based LLMs, this is where I set everything up, and I've stuck with it partly out of habit and partly because I genuinely like programming from bed. Comfort matters.

The second is a workstation I picked up refurbished from Best Buy. It's nothing impressive, but it gets the job done. I reach for it when I need to multitask — it has two 30" gaming monitors and noticeably more RAM than the Surface. The SL4 starts throwing a tantrum if I have VS Code open alongside more than ten browser tabs, which gets old fast.

For a while I just dealt with the friction of working across two machines. Eventually I got tired of it and decided to actually fix it — not just keep notes somewhere, but build a setup that lets me start work on one device and pick it up on the other without any manual git wrangling. That's what this tutorial covers.

Call it laziness if you want. I'd rather call it prioritising the things I actually enjoy. I don't enjoy managing sync state by hand. I enjoy building things. So I automated the part I don't like so I can spend more time on the part I do.

**A note before you jump in:** the tutorial references a `productive_learning` git repo quite a bit. That's a private workspace repo I use to organise everything I'm working on — you won't find it in my public repos. You can substitute it with whatever your own equivalent is; the structure and principles are the same regardless of what you call it.

I've set this up as a series too. As the setup evolves — new tools, new workflows, things I change my mind about — I'll add entries to track what changed and why.


---

## Tutorial: Dev Setup From Scratch

This tutorial documents the exact steps to reproduce my personal development environment on a new machine. The core is intentionally lean: Claude Code as the primary AI coding assistant, Gemini Research as a secondary research tool accessible from within Claude, a dotfiles repo to keep Claude config in sync, and one workspace repo that holds everything else. Session state syncs automatically across machines.

### Assumptions

Before starting, make sure you have Git and Node.js (v18 or later) installed.

**macOS:** The easiest path is [Homebrew](https://brew.sh/). Install it first if you do not have it, then run `brew install node git`.

**Linux:** Use your distro's package manager. On Debian/Ubuntu: `sudo apt install git nodejs npm`. On Arch: `sudo pacman -S git nodejs npm`.

**Windows:** Use [winget](https://learn.microsoft.com/en-us/windows/package-manager/winget/) (`winget install OpenJS.NodeJS Git.Git`) or [Scoop](https://scoop.sh/) (`scoop install nodejs git`). Note that some of the shell scripts used in this setup are written for bash. On Windows you will need [Git Bash](https://gitforwindows.org/) or WSL2 to run them. Path conventions also differ — adjust `~` to your user home directory accordingly.

---

### Step 1 — Install Claude Code

Claude Code is an AI coding assistant that runs in the terminal. It is distributed as an npm package.

```bash
npm install -g @anthropic-ai/claude-code
```

On macOS you can also install via Homebrew:

```bash
brew install claude-code
```

Or download the Mac app directly from [claude.ai](https://claude.com/product/claude-code). The npm install is the most portable option and works identically across platforms.

After installation, run `claude --version` to confirm it is on your PATH.

#### Authenticate

Before Claude Code can do anything useful, you need to authenticate. Run:

```bash
claude
```

On first launch it will open a browser window and walk you through an OAuth flow tied to your Anthropic account. Once that completes, your credentials are stored locally and you will not be prompted again on this machine.

You need an Anthropic account with an active Claude Code subscription (or API access) to proceed. If you do not have one yet, sign up at [claude.ai](https://claude.com/product/claude-code) before continuing.

---

### Step 2 — Bootstrap Claude Config via Dotfiles

Claude Code reads configuration from `~/.claude/`. Rather than managing those files directly, I keep everything in a dotfiles repo and symlink it in. This means any edit made inside a Claude Code session writes directly back to the versioned source.

#### Clone the dotfiles repo

```bash
git clone https://github.com/RustWright/dotfiles ~/.dotfiles
```

#### Run the setup script

```bash
~/.dotfiles/setup.sh
```

The script creates symlinks from `~/.claude/` into `~/.dotfiles/claude/`:

```bash
# What setup.sh does (simplified):
ln -sf ~/.dotfiles/claude/settings.json ~/.claude/settings.json
ln -sf ~/.dotfiles/claude/CLAUDE.md     ~/.claude/CLAUDE.md

# Each .md file in commands/ gets its own symlink
for f in ~/.dotfiles/claude/commands/*.md; do
    ln -sf "$f" ~/.claude/commands/
done

# Each directory in skills/ gets its own symlink
for d in ~/.dotfiles/claude/skills/*/; do
    ln -sfn "$d" ~/.claude/skills/
done
```

The script is idempotent — safe to re-run at any time without breaking anything.

#### Why symlinks instead of copies?

If you copied the files, any change Claude Code makes during a session (updating a command, tweaking settings) would modify the copy in `~/.claude/` but not the source in `~/.dotfiles/`. Symlinks eliminate this split — there is only one file, living in the dotfiles repo, and `~/.claude/` just points to it.

#### What becomes available immediately

After running `setup.sh`, the following slash commands are active inside Claude Code:

- `/create-post` — Draft a blog post for mylearnbase
- `/new-project` — Scaffold a new project directory
- `/sync-dotfiles` — Pull the latest config from the remote dotfiles repo

Any skills in `~/.dotfiles/claude/skills/` are also available.

---

### Step 3 — Clone the Workspace with Submodules

The main workspace lives at `~/productive_learning`. It contains sub-projects as Git submodules, so a plain `git clone` would leave those directories empty.

```bash
git clone --recurse-submodules https://github.com/RustWright/productive-learning.git ~/productive_learning
```

The `--recurse-submodules` flag clones the parent repo and then immediately initialises and clones every registered submodule in one pass. Without it, you would need to follow up with `git submodule update --init --recursive` manually.

The submodules pulled by this command are:

| Local path | Repository |
|---|---|
| `projects/mylearnbase` | `github.com/RustWright/mylearnbase` |
| `projects/img_gen` | `github.com/RustWright/img_gen` |

Each submodule is a full independent Git repository. You can `cd` into one and commit, push, or switch branches without affecting the parent.

---

### Step 4 — Set Up Gemini Research MCP

The workspace repo includes a local MCP server that lets Claude delegate research tasks to Gemini — web searches, documentation lookups, anything that benefits from Gemini's real-time access. Since the MCP server code lives inside `~/productive_learning/mcp-servers/gemini-research/`, it was already cloned in Step 3. What still needs doing: installing the Gemini CLI, authenticating, installing the server's dependencies, and pointing `.mcp.json` at it.

#### Install and authenticate the Gemini CLI

```bash
npm install -g @google/gemini-cli
gemini auth login
```

`gemini auth login` opens a browser window for OAuth. Once that completes, the CLI is ready. You can verify it works with:

```bash
gemini "Hello" --output-format json -y
```

#### Install MCP server dependencies

```bash
cd ~/productive_learning/mcp-servers/gemini-research
npm install
```

#### Create `.mcp.json`

At the root of `~/productive_learning`, create a `.mcp.json` file. This file is excluded from git because it contains your full local path and API keys, both of which differ between machines. A reference template is included in the repo at `.mcp.example.json` — copy it and fill in your values:

```bash
cp ~/productive_learning/.mcp.example.json ~/productive_learning/.mcp.json
```

Then edit `.mcp.json` and replace the placeholder path with your actual home directory:

```json
{
  "mcpServers": {
    "gemini-research": {
      "command": "node",
      "args": ["/home/your-username/productive_learning/mcp-servers/gemini-research/index.js"]
    }
  }
}
```

On macOS the path would start with `/Users/your-username`. The example file also includes entries for Brave Search and Codex — fill those in if you use them, or remove the ones you don't need.

After saving the file, restart Claude Code. Run `/mcp` inside Claude to confirm the `gemini-research` server is listed and active.

---

### Step 5 — Open Claude Code

```bash
claude ~/productive_learning
```

That is the entire setup. Claude Code will read `~/.claude/CLAUDE.md` at session start, your commands and skills will be available, and session sync (described below) will run automatically.

---

### How Session Sync Works

One of the recurring annoyances with any local dev tool is keeping work consistent across machines. This setup handles it with two layers.

#### Layer 1 — CLAUDE.md protocol (primary)

`~/.claude/CLAUDE.md` contains a global protocol that Claude reads at the start of every session. The protocol instructs Claude to:

1. Pull the latest state of `~/productive_learning` and initialise any new submodules before doing any work.
2. Commit and push all changes to `~/productive_learning` when the session ends.

This means picking up on a different machine is a matter of opening Claude Code and letting the session-start pull run.

#### Layer 2 — Stop hook (safety net)

`~/.claude/settings.json` registers a `Stop` hook pointing to `~/.dotfiles/scripts/session-end.sh`. This script runs every time a Claude Code session ends, regardless of how it ends (normal exit, crash, timeout).

The script checks whether there are uncommitted changes in `~/productive_learning`. If there are, it auto-commits them with a timestamped message and pushes. If Layer 1 already did the commit, the script finds a clean working tree and exits without doing anything.

The two layers cover each other:

- Layer 1 handles the normal case gracefully, with a meaningful commit message.
- Layer 2 catches anything Layer 1 missed — an abrupt disconnection, a session that ended before the protocol ran, etc.

---

### Dotfiles Structure Reference

```
~/.dotfiles/
├── claude/
│   ├── commands/
│   │   ├── create-post.md      # Draft blog posts for mylearnbase
│   │   ├── new-project.md      # Scaffold new projects
│   │   └── sync-dotfiles.md    # Pull latest config from remote
│   ├── skills/
│   │   └── dx-new/             # Dioxus project scaffolding
│   ├── settings.json           # Feature flags + Stop hook config
│   └── CLAUDE.md               # Global session sync protocol
├── scripts/
│   └── session-end.sh          # Auto-commit safety net
├── setup.sh                    # Run once after cloning
└── README.md
```

Every file under `~/.claude/` that matters is a symlink. Editing anything through Claude Code writes directly into `~/.dotfiles/` and is immediately ready to commit and push.

---

### Keeping the Dotfiles in Sync

#### On an existing machine

To pull the latest commands and settings from the remote:

```
/sync-dotfiles
```

This runs from inside Claude Code and handles the pull for you.

#### Adding a new command

1. Create the command file in the dotfiles repo:

```bash
touch ~/.dotfiles/claude/commands/new-thing.md
# edit it with your preferred editor or open Claude Code
```

2. Re-run the setup script to create the symlink:

```bash
~/.dotfiles/setup.sh
```

3. Commit and push:

```bash
git -C ~/.dotfiles add -A
git -C ~/.dotfiles commit -m "add new-thing command"
git -C ~/.dotfiles push
```

The command is now available on any machine that pulls the dotfiles repo and runs `setup.sh`.

---

### Adding New Projects

New projects are scaffolded with the `/new-project` command. During the setup flow, it asks whether you want to push to GitHub. If you say yes, it:

1. Creates a GitHub repo at `github.com/RustWright/<project-name>`
2. Adds the remote to the new project's local git repo and pushes
3. Registers the project as a submodule in `~/productive_learning` by updating `.gitmodules` and staging the submodule pointer
4. Commits and pushes the parent repo so the new submodule is tracked remotely

If you say no, the project is initialised as a local git repo only. You can register it as a submodule later by running `/new-project` again or manually with `git submodule add`.

#### Working from a project directory (not the root)

Opening Claude Code from inside a submodule (`projects/mylearnbase/` for example) is fully supported. The Stop hook script detects when it's running inside a submodule and handles the parent repo automatically:

1. Commits and pushes the submodule
2. Copies any new `.log/` files into `~/productive_learning/logs/<project>/`
3. Updates the parent's submodule pointer
4. Commits and pushes the parent

So you get cross-machine log sync and a current submodule pointer without ever needing to open Claude from `~/productive_learning/` directly.

#### Picking up a new submodule on another machine

Also automatic. The session-start protocol runs:

```bash
git pull --rebase --autostash
git submodule update --init --recursive
```

The pull brings in any new submodule registrations; the second command clones them. Open Claude Code and everything is there.

---

### Full Reproduction Checklist

For reference, here are all the steps in order with nothing omitted:

```bash
# 1. Install Claude Code
npm install -g @anthropic-ai/claude-code

# 2. Clone dotfiles and symlink Claude config
git clone https://github.com/RustWright/dotfiles ~/.dotfiles
~/.dotfiles/setup.sh

# 3. Clone the workspace (with submodules)
git clone --recurse-submodules https://github.com/RustWright/productive-learning.git ~/productive_learning

# 4. Open Claude Code
claude ~/productive_learning
```

Four commands. Everything else is automatic.
