/* ───────────────────────────────────────────────────────────────────────
   "How SVGs work" · demo 1 "pixels versus instructions" — vanilla, self-contained.

   The site logo, twice, at the same 240px display size:
     • vector panel — an inline <svg> whose path is re-rasterized by the browser
       at whatever size it's shown, so it stays sharp at any zoom.
     • raster  panel — a <canvas> drawn at a shrunken backing resolution
       (DISPLAY / zoom) then CSS-stretched to 240px with image-rendering:
       pixelated. Zooming in lowers the stored resolution, so the fixed pixel
       grid blows up into visible blocks — exactly what a PNG does.
   ─────────────────────────────────────────────────────────────────────── */
(function () {
  "use strict";

  var DISPLAY = 240;                 // on-screen px, both panels
  var SPARKLE = "M50 6 C53 32 62 43 80 46 C62 49 53 60 50 70 " +
                "C47 60 38 49 20 46 C38 43 47 32 50 6 Z";
  var BAR = '<rect x="28" y="81" width="44" height="8" rx="4"/>';

  var $ = function (id) { return document.getElementById(id); };

  // the logo as an SVG string, with an explicit fill baked in (data-URL images
  // have no CSS `color`, so currentColor wouldn't resolve on the raster side).
  function logoSVG(size, fill) {
    return '<svg xmlns="http://www.w3.org/2000/svg" width="' + size +
           '" height="' + size + '" viewBox="0 0 100 100" fill="' + fill + '">' +
           '<path d="' + SPARKLE + '"/>' + BAR + '</svg>';
  }

  function accent() {
    var c = getComputedStyle(document.documentElement)
              .getPropertyValue("--accent").trim();
    return c || "#3b5bdb";
  }

  // ── vector panel: inline SVG, fill comes from CSS (tracks dark mode) ──
  $("vecframe").innerHTML =
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">' +
    '<path d="' + SPARKLE + '"/>' + BAR + '</svg>';

  // ── raster panel: draw the logo into a small canvas, let CSS blow it up ──
  var canvas = $("ras");
  var ctx = canvas.getContext("2d");
  var logoImg = null, ready = false;

  function buildImage() {
    ready = false;
    logoImg = new Image();
    logoImg.onload = function () { ready = true; rasterize(); };
    // high-res source (240px) so the downscale to `saved` looks like a real save
    logoImg.src = "data:image/svg+xml;charset=utf-8," +
                  encodeURIComponent(logoSVG(DISPLAY, accent()));
  }

  function rasterize() {
    if (!ready) return;
    var zoom = +$("zoom").value;
    var saved = Math.max(2, Math.round(DISPLAY / zoom));   // stored pixel grid
    canvas.width = saved;
    canvas.height = saved;
    ctx.imageSmoothingEnabled = true;         // smooth DOWN-scale (a real save)
    ctx.clearRect(0, 0, saved, saved);
    ctx.drawImage(logoImg, 0, 0, saved, saved);
    // CSS keeps the element at 240px and up-scales with nearest-neighbour blocks
    $("zval").innerHTML = zoom + "&times;";
    $("rres").innerHTML = "saved as " + saved + "&times;" + saved + " px";
  }

  $("zoom").addEventListener("input", rasterize);

  // rebuild the baked-in colour when the OS theme flips
  window.matchMedia("(prefers-color-scheme: dark)")
    .addEventListener("change", buildImage);

  // narrow-screen note
  var narrow = window.matchMedia("(max-width: 640px)");
  function syncNarrow() { document.body.classList.toggle("is-narrow", narrow.matches); }
  narrow.addEventListener("change", syncNarrow);
  syncNarrow();

  buildImage();
})();
