/* Standalone-demo chrome: a way back into the site.
 *
 * Every demo under /demos/ is served two ways from the SAME file: iframed into
 * the post that embeds it, and on its own URL. Standalone it is a dead end —
 * the demos do not load site CSS at all, so there is no existing chrome to
 * extend and no link to anything. That matters more once a Playground exists,
 * because the gallery's whole job is to send people INTO demos, and the moment
 * someone wants to know how the thing works there is nowhere to go.
 *
 * The bar therefore appears in the standalone case only. Inside the iframe it
 * would point at the page the reader is already on.
 *
 * Mapping comes from /demos/_shared/demos.json, derived from the posts'
 * demo() shortcode calls by scripts/build-demo-index.py. If it is missing
 * (a plain `zola serve` without build.sh) the bar still renders with the site
 * brand, so the page is never a total dead end.
 *
 * Self-contained by necessity: the demos own their stylesheets and must not be
 * restyled, so everything here is namespaced under #dc-bar and every property
 * the bar depends on is set explicitly rather than inherited.
 */
(function () {
  'use strict';

  if (window.self !== window.top) return;   // embedded: the post is the context

  // Poster capture (scripts/capture-demo-posters.py) loads the demo standalone,
  // where the bar would otherwise be baked into the gallery thumbnail. Opting
  // out by URL beats cropping the bar off afterwards, which would have to know
  // which of the two layout modes it landed in.
  if (/[?&]poster\b/.test(window.location.search)) return;

  var INDEX = '/demos/_shared/demos.json';

  // The site mark, inlined rather than fetched: 278 bytes, and fill="currentColor"
  // means it takes the bar's colour in both schemes with no second asset.
  var LOGO =
    '<svg viewBox="0 0 100 100" fill="currentColor" aria-hidden="true" focusable="false">' +
    '<path d="M50 6 C53 32 62 43 80 46 C62 49 53 60 50 70 C47 60 38 49 20 46 C38 43 47 32 50 6 Z"/>' +
    '<rect x="28" y="81" width="44" height="8" rx="4"/></svg>';

  var CSS = [
    '#dc-bar{position:fixed;z-index:2147483000;box-sizing:border-box;',
    'display:flex;align-items:center;gap:.75rem;',
    'font:500 13px/1.4 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;',
    '-webkit-font-smoothing:antialiased;',
    'background:#fffffff2;color:#1a1a1a;border:1px solid #0000001f;',
    'backdrop-filter:saturate(1.6) blur(8px);-webkit-backdrop-filter:saturate(1.6) blur(8px)}',
    '#dc-bar.dc-push{top:0;left:0;right:0;padding:.5rem .9rem;',
    'border-width:0 0 1px 0;justify-content:space-between}',
    // Float mode overlays instead of offsetting, so it is kept small and tucked
    // into a corner rather than spanning the width.
    '#dc-bar.dc-float{top:.5rem;right:.5rem;max-width:calc(100% - 1rem);',
    'padding:.4rem .7rem;border-radius:999px;box-shadow:0 2px 10px #00000026}',
    '#dc-bar a{color:inherit;text-decoration:none;display:inline-flex;',
    'align-items:center;gap:.4rem;border:0;background:none;padding:0;min-width:0}',
    '#dc-bar a:hover{text-decoration:underline}',
    '#dc-bar svg{width:15px;height:15px;flex:0 0 auto}',
    '#dc-bar .dc-brand{font-weight:600;white-space:nowrap}',
    '#dc-bar .dc-read{min-width:0}',
    '#dc-bar .dc-read b{font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}',
    '#dc-bar .dc-lead{opacity:.72}',
    // Under 560px the wordmark and the post title are both 600-weight 13px text
    // 12px apart, which reads as one run rather than two links. The mark alone
    // carries the brand and gives the title back ~85px — the same call the site
    // header makes at phone widths, for the same reason.
    '@media (max-width:560px){#dc-bar .dc-lead{display:none}',
    '#dc-bar .dc-brand span{display:none}}',
    '@media (prefers-color-scheme:dark){#dc-bar{background:#161616f2;color:#ededed;',
    'border-color:#ffffff24}}'
  ].join('');

  function normalise(p) {
    return ('/' + String(p || '').replace(/index\.html$/, '').replace(/^\/+|\/+$/g, '') + '/')
      .replace('//', '/');
  }

  function build(entry) {
    var style = document.createElement('style');
    style.textContent = CSS;
    document.head.appendChild(style);

    var bar = document.createElement('div');
    bar.id = 'dc-bar';

    var home = document.createElement('a');
    home.className = 'dc-brand';
    home.href = '/';
    // Labelled explicitly because the wordmark is display:none on phones, which
    // takes it out of the accessibility tree along with the visual layout.
    home.setAttribute('aria-label', 'My Learn Base — home');
    home.innerHTML = LOGO + '<span>My Learn Base</span>';
    bar.appendChild(home);

    // Copy converts, it does not navigate: name the destination rather than
    // offering a bare "back". Play -> read is the whole point of the bar.
    // The title goes in as text and the href is required to be site-relative:
    // demos.json is generated from this repo's own content, but it is also a
    // fetched document, and "/" -prefixed is the only shape this bar ever needs.
    if (entry && entry.post && /^\/[^/]/.test(entry.post.url || '')) {
      var read = document.createElement('a');
      read.className = 'dc-read';
      read.href = entry.post.url;
      read.innerHTML = '<span class="dc-lead">Read how this works:</span>' +
        '<b></b><span aria-hidden="true">→</span>';
      read.querySelector('b').textContent = entry.post.title;
      bar.appendChild(read);
    }

    document.body.appendChild(bar);
    return bar;
  }

  /* Push or float.
   *
   * Pushing the page down (fixed bar + padding on <html>) is the better result:
   * nothing is covered. But a demo that sets overflow:hidden on body is
   * declaring that it manages its own viewport — how-search-works pins a
   * 100vh flex column and hides body overflow deliberately — and offsetting
   * that pushes its bottom row past the fold with NO WAY TO SCROLL to it. So
   * where the page cannot scroll, the bar overlays instead.
   *
   * Decided by measurement rather than by a list of demo names, and re-decided
   * on resize: that same demo drops the fixed-viewport model under 640px, and
   * gets the nicer push treatment there for free.
   */
  function managesOwnViewport() {
    return getComputedStyle(document.body).overflowY === 'hidden' ||
           getComputedStyle(document.documentElement).overflowY === 'hidden';
  }

  function applyMode(bar) {
    var root = document.documentElement;
    root.style.paddingTop = '';
    bar.className = 'dc-push';
    if (managesOwnViewport()) {
      bar.className = 'dc-float';
      return;
    }
    root.style.paddingTop = bar.offsetHeight + 'px';
  }

  function mount(entry) {
    var bar = build(entry);
    requestAnimationFrame(function () { applyMode(bar); });
    var timer;
    window.addEventListener('resize', function () {
      clearTimeout(timer);
      timer = setTimeout(function () { applyMode(bar); }, 150);
    });
  }

  function start() {
    var here = normalise(window.location.pathname);
    fetch(INDEX, { credentials: 'omit' })
      .then(function (r) { return r.ok ? r.json() : null; })
      .then(function (data) {
        var list = (data && data.demos) || [];
        var entry = null;
        for (var i = 0; i < list.length; i++) {
          if (normalise(list[i].url) === here) { entry = list[i]; break; }
        }
        mount(entry);
      })
      .catch(function () { mount(null); });   // brand-only beats no way out
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
