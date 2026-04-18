+++
title = "Autonomous UI Development with Playwright MCP"
slug = "autonomous-ui-development-with-playwright-mcp"
date = 2026-04-18
draft = false

[taxonomies]
tags = ["rust", "tauri", "dioxus", "wasm", "playwright", "ui-development"]
+++

## Reflections

Although I didn't include this as part of the [Building omni-me](/series/building-omni-me/) series, the work behind this post came out of my first cycle of development on a personal life app I've been building. I don't usually think of myself as someone with strong aesthetic preferences. I'm more of a "good enough" designer which is why UI development has never been one of my strong suits; and since I don't care about it that much, I've never put in the effort to get better at it.

That said, I'm building an app that I plan to use as a daily driver, so I had to reconcile two things: knowing how much impact good vs. bad UI/UX has on an app you use every day, and my general lackadaisical attitude toward writing UI code. Since I was already relying heavily on the LLM for the more technical aspects of development, I decided to leverage its help for the UI too. It can obviously do a better job than I can if we're both given the same short time frame to work with.

All of that led to needing to figure out this workflow before I got too deep into development. I've only completed the first cycle, which I consider a very early stage MVP. I've validated all the basic functionality, but there are a lot more features to add before the app reaches a level where I can start using it while continuing to build. Each new feature will require updating the UI and thinking through the design carefully. That's why I paused all other work on the app until I figured this out first.

Something the article doesn't point out is cost. I'm not made of money, and not thinking carefully about how an automated LLM pipeline (constantly taking screenshots and analysing them) will drain whatever budget you have for LLM spend is a recipe for disaster. I have the basic Claude Code Pro subscription at about $20 USD a month, and I paid for the annual version. While I can still make steady progress most of the time, I'm already running up against the token limits in the 5-hour usage windows. That concern was actually why I tried to get this working with Gemini first.

I can't say I tried very hard to make it work. My first attempt led to a lot of issues, so I came back to Claude with my tail between my legs and accepted that I have to move slower for now, or fork up more cash for a MAX account. I don't think I'm ready for that yet. So I'll try using this workflow, see if it blows up my budget, and if it does, I might look for a middle ground: maybe a cheaper model acting as the vision layer through a second MCP, so I'm not paying for Claude's vision capability on every screenshot. But I'm getting ahead of myself. I'll see if any of that is necessary after using this for a while.

That's all from me. Hope you find the article useful, future me or whoever else is reading this.

---

## Tutorial: Giving Your AI Coding Assistant Eyes for UI Development

I was building a personal app with Tauri v2 and Dioxus --- a Rust frontend compiled to WASM, rendered in Tauri's native WebView, talking to a Rust backend through IPC commands. The app worked. But every time I wanted the LLM to help with the UI, the same bottleneck appeared: the assistant would edit component code, and then I had to tell it what happened. "The button moved but the text is clipped." "The nav bar looks right now, try the settings page." Every change required me to be the visual feedback loop.

This is manageable for a few tweaks. It becomes painful when you have an entire UI to build --- multiple pages, forms, navigation flows, responsive layouts. I wanted to point the LLM at a design target and let it iterate autonomously.

### The failed attempt: Puppeteer scripts

The first approach, tried with a different LLM agent (Gemini CLI), was to write custom Puppeteer scripts. The idea was straightforward: a Node.js script launches a headless browser, navigates to the app, takes a screenshot, and hands it back to the LLM.

The problem was that Tauri renders the frontend inside a system WebView, not a browser. To get around this, we tried running the Dioxus frontend separately as a standalone web app. But the frontend calls Tauri IPC commands for all its data --- note lists, routine groups, settings. Without Tauri's backend, every IPC call fails and the UI renders nothing useful. This led to adding mock data stubs, which led to asset path mismatches between the standalone build and the Tauri build, which led to the editor component breaking, which led to the build pipeline itself breaking. The Puppeteer scripts added Node.js dependencies, custom tooling, and debugging surface area. After a full session, the app no longer compiled.

The approach was not wrong in principle --- it was over-engineered. The pieces needed to solve this problem already existed; they just needed to be wired together.

### What actually worked: three existing tools

The solution turned out to be a combination of three things, none of which required writing new tooling:

1. **Rust's conditional compilation** (`#[cfg(feature = "mock")]`) to stub all backend IPC calls with static data, so the Dioxus frontend can run standalone in a browser.
2. **Dioxus CLI's `dx serve`** to serve the WASM frontend on localhost with hot-reload, giving the LLM a browser-accessible URL to target.
3. **Playwright MCP** --- browser automation plugin accesible through Claude Code --- to navigate, screenshot, click, and inspect the running UI.

### Decoupling the frontend: feature-flagged mock data

In a Tauri app, the frontend communicates with the Rust backend through IPC commands --- `invoke("list_notes", ...)`, `invoke("save_note", ...)`, and so on. When the frontend runs standalone in a browser, `window.__TAURI__` does not exist and every one of these calls fails. The app renders a blank screen or panics.

The fix is Rust's conditional compilation. At compile time, a feature flag swaps every IPC call for a static data stub.

Define a `mock` feature in the frontend's `Cargo.toml`:

```toml
[features]
default = []
mock = []
```

Then, in every function that calls the backend, add a mock branch:

```rust
pub async fn invoke_list_notes() -> Result<Vec<NoteListItem>, String> {
    #[cfg(feature = "mock")]
    {
        return Ok(vec![
            NoteListItem {
                id: "note1".to_string(),
                preview: "Morning journal entry...".to_string(),
                created_at: "2026-04-15T08:30:00Z".to_string(),
                updated_at: "2026-04-15T08:30:00Z".to_string(),
            },
            NoteListItem {
                id: "note2".to_string(),
                preview: "Project planning notes".to_string(),
                created_at: "2026-04-14T14:00:00Z".to_string(),
                updated_at: "2026-04-14T16:45:00Z".to_string(),
            },
        ]);
    }

    #[cfg(not(feature = "mock"))]
    {
        let result = invoke("list_notes", JsValue::NULL).await;
        serde_wasm_bindgen::from_value(result)
            .map_err(|e| format!("Failed to deserialize: {}", e))
    }
}
```

Every IPC boundary gets this treatment. The `#[cfg(feature = "mock")]` block returns static data that is realistic enough to render all UI states: lists with multiple items, various data shapes, edge cases like long strings. The `#[cfg(not(feature = "mock"))]` block contains the real Tauri IPC call.

Key design principles for mock data:

- **Cover all IPC boundaries.** Every function that touches the backend needs a mock branch. Missing one causes a runtime panic when the frontend tries to call a Tauri command that does not exist.
- **Use realistic data.** A list with one item does not test the same rendering paths as a list with ten items of varying lengths. Include enough variety to exercise the UI.
- **Mutations return success but do not update state.** When the user clicks "save" in mock mode, the function returns `Ok(())` but the displayed data does not change. This is acceptable for visual development --- the goal is to see how components render, not to test data flow.
- **Keep mock data close to the real call.** Putting both branches in the same function makes it obvious when the real API signature changes and the mock needs updating.

A limitation worth noting: mock mode is exclusively for visual iteration. Integration testing with real data, state persistence, and cross-component data flow requires the full app running through `cargo tauri dev`.

### Serving the frontend to a browser: `dx serve`

With mock data in place, the frontend can run without Tauri's backend. The next step is making it accessible to browser automation. Dioxus CLI has a built-in dev server that compiles the frontend to WASM and serves it on localhost with hot-reload:

```bash
dx serve --platform web --features mock --open false --port 8080
```

Breaking down the flags:

- `--platform web` compiles to WASM and serves via HTTP, rather than launching a desktop window.
- `--features mock` activates the mock feature flag, so all IPC calls return static data.
- `--open false` prevents the dev server from automatically opening a browser tab (the LLM will navigate Playwright to the URL instead).
- `--port 8080` sets a predictable port.

With this running, the frontend is available at `http://localhost:8080` in any browser. Dioxus watches the source files and hot-reloads changes automatically --- when the LLM edits a `.rs` file, the browser updates within a few seconds without a manual refresh.

This is the key insight that makes the whole workflow possible. The same WASM binary that Tauri embeds in its WebView can be served to a regular browser. The mock feature flag handles the missing backend. No custom tooling, no additional dependencies.

### Giving the LLM eyes: Playwright MCP

The frontend is now running on `localhost:8080` with realistic mock data. The final piece is letting the LLM actually see and interact with it. Claude Code has built-in browser automation through Playwright via MCP (Model Context Protocol) --- no external scripts or dependencies needed. These tools let the LLM control a browser directly.

The key tools:

| Tool | Purpose |
|------|---------|
| `browser_navigate` | Navigate to a URL |
| `browser_take_screenshot` | Capture the current visual state as a PNG |
| `browser_snapshot` | Get the accessibility tree with element references |
| `browser_click` | Click an element by its accessibility ref |
| `browser_type` | Type text into a focused input |
| `browser_press_key` | Press a keyboard key (Enter, Tab, Escape, etc.) |
| `browser_console_messages` | Read browser console output for debugging |

The accessibility tree from `browser_snapshot` deserves special attention. It returns a structured representation of the page with reference identifiers for each interactive element. These references are what `browser_click` and `browser_type` use to target specific elements. This is more reliable than coordinate-based clicking and works even when the visual layout changes.

Important operational details:

- **Element refs invalidate after page updates.** Every hot-reload, navigation, or dynamic content change generates new refs. Always take a fresh `browser_snapshot` before interacting with elements.
- **Screenshots and snapshots serve different purposes.** Screenshots show visual layout, spacing, colors, and rendering issues. Snapshots show structure, text content, and interactive element targets. Use both.
- **Console messages catch invisible errors.** WASM panics, failed resource loads, and JavaScript errors appear in the console but not in screenshots. Check `browser_console_messages` when something looks wrong.

### The complete workflow loop

With all three pieces in place, the autonomous development loop looks like this:

```
Edit code --> Hot-reload --> Screenshot --> Analyze --> Repeat
```

In concrete steps:

1. **Start the dev server** in a background terminal:
   ```bash
   dx serve --platform web --features mock --open false --port 8080
   ```

2. **Navigate Playwright** to the dev server:
   The LLM calls `browser_navigate` with `http://localhost:8080`.

3. **Take an initial screenshot** to see the current state:
   The LLM calls `browser_take_screenshot` and receives a PNG image.

4. **Analyze and plan changes:**
   The LLM examines the screenshot, compares it to the target design, and determines what to edit.

5. **Edit source files:**
   The LLM modifies `.rs` component files, CSS, or layout code.

6. **Wait for hot-reload:**
   Dioxus detects the file change and recompiles the WASM binary. This typically takes 2--5 seconds.

7. **Screenshot again to verify:**
   The LLM takes a fresh screenshot to confirm the change had the intended effect.

8. **Iterate or move on:**
   If the result matches the target, move to the next component or page. If not, refine and repeat.

For interactive testing (verifying that buttons work, forms accept input, navigation functions correctly):

1. Call `browser_snapshot` to get the accessibility tree with element refs.
2. Call `browser_click` with the ref for the target element.
3. Call `browser_take_screenshot` to see the result.
4. For text inputs, call `browser_type` to enter text, then screenshot to verify.

### Build pipeline: separating dev and release

A practical issue that emerged during development: the WASM release build pipeline uses `wasm-opt` for binary optimization, which may not be installed or may crash on some systems. Development builds do not need this optimization. The solution is maintaining separate build scripts for dev and release.

In `package.json` (or equivalent task runner):

```json
{
  "scripts": {
    "build:editor": "npx esbuild assets/js/editor.js --bundle --outfile=assets/js/editor.bundle.js",
    "build:frontend": "cd frontend && dx build --platform web --release",
    "build:frontend:dev": "cd frontend && dx build --platform web",
    "copy:editor:release": "mkdir -p frontend/target/dx/frontend/release/web/public/assets/js && cp assets/js/editor.bundle.js frontend/target/dx/frontend/release/web/public/assets/js/",
    "copy:editor:dev": "mkdir -p frontend/target/dx/frontend/debug/web/public/assets/js && cp assets/js/editor.bundle.js frontend/target/dx/frontend/debug/web/public/assets/js/",
    "build": "npm run build:editor && npm run build:frontend && npm run copy:editor:release",
    "dev": "npm run build:editor && npm run build:frontend:dev && npm run copy:editor:dev"
  }
}
```

The `build` script runs the full release pipeline with `--release` and `wasm-opt`. The `dev` script produces a debug build without optimization. Both handle bundling external JavaScript assets (in this case, a CodeMirror 6 editor) and copying them to the correct output directory.

In `tauri.conf.json`, wire the Tauri dev command to use the debug build path:

```json
{
  "build": {
    "beforeDevCommand": "npm run dev",
    "beforeBuildCommand": "npm run build",
    "frontendDist": "../frontend/target/dx/frontend/debug/web/public"
  }
}
```

This way `cargo tauri dev` uses fast debug builds (no `wasm-opt`, faster compilation), while `cargo tauri build` produces optimized release binaries. The two pipelines share the same source code and build steps, differing only in the optimization flags and output paths.

### A UI checklist for systematic testing

Autonomous UI development benefits from structure. Rather than letting the LLM wander through the interface, define a checklist of items to verify. Each item specifies a page, a component or interaction, and the expected behavior.

An example checklist format:

```
Page: /notes
- [ ] Note list renders with multiple items
- [ ] Each note shows preview text and timestamp
- [ ] Clicking a note navigates to the detail view
- [ ] Search input accepts text
- [ ] Search filters the note list
- [ ] Empty search shows blank results (not all notes)

Page: /notes/new
- [ ] Editor component loads and is interactive
- [ ] Title field accepts input
- [ ] Save button is visible and clickable
- [ ] Clicking save returns to the note list
```

The LLM works through this checklist systematically, marking items as pass or fail. Failed items get detailed notes about what went wrong (with screenshots as evidence), which feeds into the next round of fixes.

### Validation results

When this workflow was first used on a real project (a Tauri + Dioxus app with SurrealDB backend and CodeMirror 6 editor), the results were:

- **35 out of 39 UI checklist items were tested autonomously** via Playwright, without any human screenshots or descriptions.
- The LLM navigated between pages, filled forms, tested search functionality, and verified component rendering across the application.
- A complex JavaScript editor component (CodeMirror 6, loaded via a bundled JS file and integrated with the Dioxus WASM frontend) rendered and functioned correctly in browser-only mode. A previous attempt using Gemini CLI with custom Puppeteer scripts had failed to achieve this due to asset path issues.
- **The entire testing session took approximately 6 minutes** of autonomous LLM work. A comparable manual testing session --- describing each screen state, pasting screenshots, waiting for analysis --- would have taken significantly longer.

The 4 items that were not tested were blocked by limitations of mock mode (they required real backend state changes), not by limitations of the Playwright workflow itself.

### Adapting to other stacks

Nothing here is Tauri- or Dioxus-specific in principle. The pattern is: mock layer + dev server + Playwright MCP. The implementations change per ecosystem:

| Piece | Tauri + Dioxus | JS frameworks (React, Vue, etc.) |
|-------|----------------|----------------------------------|
| Mock layer | `#[cfg(feature = "mock")]` compile-time stubs | MSW (Mock Service Worker) or env-switched fixture imports |
| Dev server | `dx serve --platform web --port 8080` | `npx vite --port 8080`, `npx next dev`, etc. |
| Browser automation | Playwright MCP (same) | Playwright MCP (same) |

The only requirements are that the dev server serves on a predictable localhost port with hot-reload, and that the mock layer is realistic enough to render all UI states. The Playwright side is identical regardless of framework.

### Cross-platform notes

This workflow was developed and tested on **Linux** (Ubuntu). Notes for other platforms:

- **macOS:** All commands work identically. If you need `wasm-opt` for release builds, install it via `brew install binaryen`.
- **Windows:** Use WSL2 for the smoothest experience. The `dx serve` command, Playwright MCP tools, and all browser automation work the same inside WSL2. Native PowerShell requires adjusting path separators (`/` to `\`) and may have issues with some Unix-specific shell syntax.
- **Dioxus CLI** is installed via `cargo install dioxus-cli`.
- **Tauri CLI** is installed via `cargo install tauri-cli`.
- Playwright MCP tools are built into Claude Code and require no separate installation. They work the same regardless of operating system. You'll need to install the playwright-mcp from the Claude plugin market place which can be accessed by entering the slash command `/plugin` in any Claude Code session.
