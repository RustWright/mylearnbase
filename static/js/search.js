// Site search overlay (Pagefind). Progressive enhancement: the header trigger
// ships [hidden] and is revealed here; the Pagefind UI bundle + index are
// lazy-loaded on the FIRST open, so a reader who never searches pays nothing.
// Opens on click, "/" , or Cmd/Ctrl-K; closes on Esc or backdrop click.
(function () {
  "use strict";

  var toggle = document.getElementById("search-toggle");
  var overlay = document.getElementById("search-overlay");
  var mount = document.getElementById("search-ui");
  if (!toggle || !overlay || !mount) return;

  // JS is running — surface the trigger (it ships hidden so no-JS users get no
  // dead button).
  toggle.hidden = false;

  var uiLoaded = false;
  var lastFocus = null;

  function loadPagefindUI() {
    return new Promise(function (resolve, reject) {
      if (uiLoaded) {
        resolve();
        return;
      }
      var css = document.createElement("link");
      css.rel = "stylesheet";
      css.href = "/pagefind/pagefind-ui.css";
      document.head.appendChild(css);

      var script = document.createElement("script");
      script.src = "/pagefind/pagefind-ui.js";
      script.onload = function () {
        /* global PagefindUI */
        new PagefindUI({
          element: "#search-ui",
          showSubResults: true,
          showImages: false,
        });
        uiLoaded = true;
        resolve();
      };
      script.onerror = reject;
      document.body.appendChild(script);
    });
  }

  function open() {
    if (!overlay.hidden) return;
    lastFocus = document.activeElement;
    overlay.hidden = false;
    document.body.classList.add("search-open");
    loadPagefindUI()
      .then(function () {
        var input = overlay.querySelector("input");
        if (input) input.focus();
      })
      .catch(function () {
        // e.g. deployed before the Pagefind index exists — fail soft, not blank.
        var msg = document.createElement("p");
        msg.textContent = "Search is unavailable right now.";
        msg.style.cssText = "padding:1rem;margin:0;color:var(--text-pale-color)";
        mount.replaceChildren(msg);
      });
  }

  function close() {
    if (overlay.hidden) return;
    overlay.hidden = true;
    document.body.classList.remove("search-open");
    if (lastFocus && typeof lastFocus.focus === "function") lastFocus.focus();
  }

  toggle.addEventListener("click", open);

  // Backdrop click (outside the dialog) closes.
  overlay.addEventListener("click", function (e) {
    if (e.target === overlay) close();
  });

  // Keep Tab focus inside the dialog while open (focusables recomputed each Tab,
  // since Pagefind adds results dynamically).
  overlay.addEventListener("keydown", function (e) {
    if (e.key !== "Tab") return;
    var f = overlay.querySelectorAll(
      'a[href], button:not([disabled]), input, [tabindex]:not([tabindex="-1"])'
    );
    if (!f.length) return;
    var first = f[0];
    var last = f[f.length - 1];
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  });

  document.addEventListener("keydown", function (e) {
    var t = e.target;
    var typing =
      /^(input|textarea|select)$/i.test(t.tagName) || t.isContentEditable;

    // Open: "/" (when not already typing) or Cmd/Ctrl-K.
    if (
      (e.key === "/" && !typing) ||
      ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k")
    ) {
      e.preventDefault();
      open();
      return;
    }
    if (e.key === "Escape") close();
  });
})();
