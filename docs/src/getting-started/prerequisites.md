# Prerequisites

## Required

### Zola

Zola is the static site generator that builds the site. Install version **0.22.1** or later.

**Linux (recommended):**
```bash
# Download and extract
curl -sL https://github.com/getzola/zola/releases/download/v0.22.1/zola-v0.22.1-x86_64-unknown-linux-gnu.tar.gz | tar xz

# Move to a directory in your PATH
sudo mv zola /usr/local/bin/

# Verify
zola --version
```

**Other platforms:** See the [Zola installation guide](https://www.getzola.org/documentation/getting-started/installation/).

### Git

Required for cloning the repo and managing the Serene theme (which is a git submodule).

```bash
git --version  # Should be 2.x or later
```

## Optional

### mdBook

Only needed if you want to build this documentation locally.

```bash
# Requires Rust/Cargo
cargo install mdbook

# Verify
mdbook --version
```

### Rust / Cargo

Only needed for installing mdBook or for future WASM demo development.

See [rustup.rs](https://rustup.rs/) for installation.
