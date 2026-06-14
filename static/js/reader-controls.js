/* Reader controls — text-size + typeface picker for the article body.
 *
 * Persists to localStorage (survives browser restarts — accessibility prefs
 * should be sticky). The no-FOUC application happens in the inline head script
 * (templates/_head_extend.html); this file reveals the control, reflects the
 * stored state in the UI, and wires the buttons. Font stacks are defined in
 * static/css/custom.css and selected via the data-reader-font attribute on
 * <html>, so this script never carries a font map.
 */
(function () {
  "use strict";

  var MIN = 14, MAX = 28, STEP = 2, DEFAULT = 16;
  var root = document.documentElement;

  var container = document.getElementById("reader-controls");
  if (!container) return; // not a page with the control (non-post pages)

  var toggle = document.getElementById("reader-toggle");
  var panel = document.getElementById("reader-panel");
  var dec = document.getElementById("reader-size-dec");
  var inc = document.getElementById("reader-size-inc");
  var val = document.getElementById("reader-size-val");
  var reset = document.getElementById("reader-reset");
  var fontBtns = container.querySelectorAll(".reader-fonts button");

  function clamp(n) { return Math.min(MAX, Math.max(MIN, n)); }

  function currentSize() {
    var n = parseInt(localStorage.getItem("reader-size"), 10);
    return isNaN(n) ? DEFAULT : clamp(n);
  }
  function currentFont() {
    return localStorage.getItem("reader-font") || "sans";
  }

  function applySize(n) {
    root.style.setProperty("--reader-font-size", n + "px");
    val.textContent = n + "px";
    dec.disabled = n <= MIN;
    inc.disabled = n >= MAX;
  }
  function applyFont(key) {
    if (key === "sans") root.removeAttribute("data-reader-font");
    else root.setAttribute("data-reader-font", key);
    fontBtns.forEach(function (b) {
      b.setAttribute("aria-pressed", b.dataset.font === key ? "true" : "false");
    });
  }

  function setSize(n) {
    n = clamp(n);
    localStorage.setItem("reader-size", n);
    applySize(n);
  }
  function setFont(key) {
    localStorage.setItem("reader-font", key);
    applyFont(key);
  }
  function openPanel(open) {
    panel.hidden = !open;
    toggle.setAttribute("aria-expanded", open ? "true" : "false");
  }

  // Reflect stored state, then reveal the control now that JS is active.
  applySize(currentSize());
  applyFont(currentFont());
  container.hidden = false;

  toggle.addEventListener("click", function () { openPanel(panel.hidden); });
  dec.addEventListener("click", function () { setSize(currentSize() - STEP); });
  inc.addEventListener("click", function () { setSize(currentSize() + STEP); });
  fontBtns.forEach(function (b) {
    b.addEventListener("click", function () { setFont(b.dataset.font); });
  });
  reset.addEventListener("click", function () {
    localStorage.removeItem("reader-size");
    localStorage.removeItem("reader-font");
    root.style.removeProperty("--reader-font-size");
    applySize(DEFAULT);
    applyFont("sans");
  });

  // Dismiss on outside click / Escape.
  document.addEventListener("click", function (e) {
    if (!panel.hidden && !container.contains(e.target)) openPanel(false);
  });
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && !panel.hidden) { openPanel(false); toggle.focus(); }
  });
})();
