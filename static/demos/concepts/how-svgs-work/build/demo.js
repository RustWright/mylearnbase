/* ───────────────────────────────────────────────────────────────────────
   "How SVGs work" · demo 3 "build your own" — vanilla, self-contained.

   A textarea of SVG source drives a live preview. On every edit we parse the
   text with DOMParser("image/svg+xml"): a <parsererror> node means "not valid
   yet" (we keep the last good render rather than flashing blank); otherwise we
   strip <script> and on* handlers and inject the serialised result. Three
   challenges each ship a scaffolded starter and one revealable example; nothing
   ever leaves the browser.
   ─────────────────────────────────────────────────────────────────────── */
(function () {
  "use strict";

  var $ = function (id) { return document.getElementById(id); };
  var editor = $("src"), preview = $("preview"), status = $("status");

  var CHALLENGES = [
    {
      id: "smiley",
      name: "1 · Smiley",
      prompt: "<b>Draw a smiley face.</b> The head is here already. Add two small " +
              "<code>&lt;circle&gt;</code> eyes and a curved mouth (a <code>&lt;path&gt;</code> " +
              "with a <code>Q</code> curve, or an arc).",
      starter:
`<svg viewBox="0 0 100 100">
  <!-- Add two eyes and a smiling mouth. -->
  <circle cx="50" cy="50" r="40" fill="#ffd43b" stroke="#333" stroke-width="3"/>
</svg>`,
      example:
`<svg viewBox="0 0 100 100">
  <circle cx="50" cy="50" r="40" fill="#ffd43b" stroke="#333" stroke-width="3"/>
  <circle cx="37" cy="43" r="5" fill="#333"/>
  <circle cx="63" cy="43" r="5" fill="#333"/>
  <path d="M33 60 Q50 78 67 60" fill="none" stroke="#333"
        stroke-width="4" stroke-linecap="round"/>
</svg>`
    },
    {
      id: "boat",
      name: "2 · Boat",
      prompt: "<b>Draw a little boat on the water.</b> Try a <code>&lt;polygon&gt;</code> " +
              "hull (a trapezoid), a <code>&lt;line&gt;</code> mast, and a triangular " +
              "<code>&lt;polygon&gt;</code> sail.",
      starter:
`<svg viewBox="0 0 100 100">
  <!-- The sea is here. Build a boat on top:
       a polygon hull, a line mast, a triangular sail. -->
  <rect x="0" y="80" width="100" height="20" fill="#4dabf7"/>
</svg>`,
      example:
`<svg viewBox="0 0 100 100">
  <rect x="0" y="80" width="100" height="20" fill="#4dabf7"/>
  <line x1="50" y1="26" x2="50" y2="80" stroke="#5c3d2e" stroke-width="2"/>
  <polygon points="50,28 50,74 24,74" fill="#f1f3f5" stroke="#adb5bd" stroke-width="1"/>
  <polygon points="18,80 82,80 72,92 28,92" fill="#a0522d"/>
</svg>`
    },
    {
      id: "heart",
      name: "3 · Heart",
      prompt: "<b>Draw a heart</b> &mdash; this one needs real curves. Half of it is " +
              "drawn: add a second <code>C</code> command that mirrors it on the right, " +
              "ending back at <code>50 76</code>, then <code>Z</code> to close and switch to a " +
              "<code>fill</code>.",
      starter:
`<svg viewBox="0 0 100 100">
  <!-- Half a heart, as a stroke. Add a second C command
       mirroring it on the right (end at 50 76), then Z,
       then swap fill="none" stroke=... for a solid fill. -->
  <path d="M50 76 C10 40 30 12 50 40"
        fill="none" stroke="#e64980" stroke-width="3"/>
</svg>`,
      example:
`<svg viewBox="0 0 100 100">
  <path d="M50 76 C10 40 30 12 50 40 C70 12 90 40 50 76 Z"
        fill="#e64980"/>
</svg>`
    }
  ];

  var current = CHALLENGES[0];

  // ── live render: parse, scrub, inject (keep last good on error) ────────────
  function renderPreview() {
    var src = editor.value;
    var doc = new DOMParser().parseFromString(src, "image/svg+xml");
    var err = doc.getElementsByTagName("parsererror")[0];
    if (err || !doc.documentElement || doc.documentElement.nodeName === "parsererror") {
      status.className = "bad";
      status.textContent = "not valid SVG yet — check your tags are closed";
      return;                                   // keep the last good preview
    }
    // scrub anything executable before it touches the DOM
    Array.prototype.forEach.call(doc.querySelectorAll("script"), function (n) { n.remove(); });
    Array.prototype.forEach.call(doc.querySelectorAll("*"), function (el) {
      Array.prototype.slice.call(el.attributes).forEach(function (a) {
        var v = (a.value || "").replace(/\s/g, "").toLowerCase();
        if (/^on/i.test(a.name) || v.indexOf("javascript:") === 0) el.removeAttribute(a.name);
      });
    });
    preview.innerHTML = new XMLSerializer().serializeToString(doc.documentElement);
    status.className = "ok";
    status.textContent = "✓ valid SVG";
  }

  var timer;
  editor.addEventListener("input", function () {
    clearTimeout(timer);
    timer = setTimeout(renderPreview, 120);
  });

  // ── challenges ─────────────────────────────────────────────────────────────
  function isDirty() { return editor.value.trim() !== current.starter.trim(); }

  function loadChallenge(ch, force) {
    if (!force && ch !== current && isDirty() &&
        !window.confirm("Replace what's in the editor with the “" + ch.name.replace(/^\d+\s*·\s*/, "") + "” starter?")) {
      syncChips();
      return;
    }
    current = ch;
    editor.value = ch.starter;
    $("prompt").innerHTML = ch.prompt;
    $("excode").textContent = ch.example;
    $("reveal").open = false;
    syncChips();
    renderPreview();
  }

  function syncChips() {
    Array.prototype.forEach.call($("chips").children, function (btn) {
      btn.classList.toggle("on", btn.dataset.id === current.id);
    });
  }

  // build the chips
  CHALLENGES.forEach(function (ch) {
    var b = document.createElement("button");
    b.className = "chip";
    b.dataset.id = ch.id;
    b.type = "button";
    b.setAttribute("role", "tab");
    b.textContent = ch.name;
    b.addEventListener("click", function () { loadChallenge(ch); });
    $("chips").appendChild(b);
  });

  $("loadex").addEventListener("click", function () {
    if (isDirty() && !window.confirm("Replace what's in the editor with this example?")) return;
    editor.value = current.example;
    renderPreview();
  });

  // narrow-screen note
  var narrow = window.matchMedia("(max-width: 640px)");
  function syncNarrow() { document.body.classList.toggle("is-narrow", narrow.matches); }
  narrow.addEventListener("change", syncNarrow);
  syncNarrow();

  loadChallenge(CHALLENGES[0], true);
})();
