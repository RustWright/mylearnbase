// Sticky site header: reveal on scroll-up, tuck away on scroll-down.
// Pairs with .site-header / .site-header.is-hidden in css/custom.css. Vanilla,
// progressive enhancement — with JS disabled the header is simply always shown.
// Reduced-motion is handled in CSS (.is-hidden becomes a no-op there), so the
// class may toggle freely without causing movement for those readers.
(function () {
  "use strict";

  var header = document.getElementById("site-header");
  if (!header) return;

  var lastY = window.scrollY || window.pageYOffset;
  var ticking = false;
  var TOP_ZONE = 80; // always reveal within this many px of the top
  var DELTA = 6;     // ignore sub-pixel / jitter scrolling

  function update() {
    ticking = false;
    var y = window.scrollY || window.pageYOffset;

    if (y <= TOP_ZONE) {
      header.classList.remove("is-hidden");
      lastY = y;
      return;
    }

    if (Math.abs(y - lastY) < DELTA) return;

    if (y > lastY) {
      header.classList.add("is-hidden");    // scrolling down → tuck away
    } else {
      header.classList.remove("is-hidden"); // scrolling up → reveal
    }
    lastY = y;
  }

  window.addEventListener("scroll", function () {
    if (!ticking) {
      window.requestAnimationFrame(update);
      ticking = true;
    }
  }, { passive: true });
})();
