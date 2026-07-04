/* ───────────────────────────────────────────────────────────────────────
   TF-IDF · demo 1 "the ablation" — vanilla, self-contained.

   Loads ../corpus.json (12 Wikipedia intros, CC BY-SA) and scores each
   document's words three ways so the reader can feel why you need both halves:
     · TF     count only        → common filler ("the", "of") wins
     · IDF    rarity only        → rarest one-offs win, however marginal
     · TF·IDF frequent AND rare  → the words that actually characterise the doc

   The TF-IDF maths is ported from scripts/compute-related.py (sublinear tf,
   smoothed idf) so it matches the site's live "related posts" engine. ONE
   deliberate difference: no stopword list here. Leaving "the/of/and" in is what
   lets IDF visibly earn its keep — that is the whole lesson. (The one thing we
   do drop is ordinal fragments like "19th" → "th": those are tokenizer noise,
   not words, so keeping them would just be misleading.)
   ─────────────────────────────────────────────────────────────────────── */
(function () {
  "use strict";

  var root = document.getElementById("demo");
  if (!root) return;

  var $ = function (id) { return document.getElementById(id); };
  var esc = function (s) {
    return String(s).replace(/[&<>]/g, function (c) {
      return c === "&" ? "&amp;" : c === "<" ? "&lt;" : "&gt;";
    });
  };

  // ── TF-IDF primitives (ported from compute-related.py; no stopwords) ──
  var ORDINAL = { th: 1, st: 1, nd: 1, rd: 1 };   // "19th"→"th" etc: tokenizer noise
  var TOKEN_RE = /[a-z][a-z0-9-]*[a-z0-9]|[a-z]/g;
  function tokenize(text) {
    var raw = (text.toLowerCase().match(TOKEN_RE) || []), out = [];
    for (var i = 0; i < raw.length; i++) {
      var t = raw[i].replace(/^-+|-+$/g, "");
      if (t.length >= 2 && !ORDINAL[t]) out.push(t);
    }
    return out;
  }

  var DOCS = [], N = 0, COUNTS = {}, IDF = {}, IDF_MIN = 0, IDF_MAX = 1;

  function buildModel(corpus) {
    DOCS = corpus.docs;
    N = DOCS.length;
    var DF = {};
    DOCS.forEach(function (d) {
      var c = {}, toks = tokenize(d.text);
      for (var i = 0; i < toks.length; i++) c[toks[i]] = (c[toks[i]] || 0) + 1;
      COUNTS[d.id] = c;
      Object.keys(c).forEach(function (t) { DF[t] = (DF[t] || 0) + 1; });
    });
    Object.keys(DF).forEach(function (t) {
      IDF[t] = Math.log((1 + N) / (1 + DF[t])) + 1;   // smoothed idf
    });
    var vals = Object.keys(IDF).map(function (t) { return IDF[t]; });
    IDF_MIN = Math.min.apply(null, vals);
    IDF_MAX = Math.max.apply(null, vals);
    return DF;
  }
  var DF = null;

  function tf(id, t) { return 1 + Math.log(COUNTS[id][t]); }   // sublinear tf
  function weight(id, t, mode) {
    if (mode === "tf") return tf(id, t);
    if (mode === "idf") return IDF[t];
    return tf(id, t) * IDF[t];
  }
  function topWords(id, mode, n) {
    var c = COUNTS[id];
    var arr = Object.keys(c).map(function (t) { return { t: t, w: weight(id, t, mode) }; });
    arr.sort(function (a, b) { return b.w - a.w; });
    return arr.slice(0, n);
  }

  // bar colour encodes rarity: common word → grey, rare word → accent blue
  function rarityColor(t) {
    var x = (IDF[t] - IDF_MIN) / ((IDF_MAX - IDF_MIN) || 1);   // 0..1
    var s = Math.round(8 + x * 64);       // saturation 8%..72%
    var l = Math.round(60 - x * 6);       // lightness  60%..54%
    return "hsl(224," + s + "%," + l + "%)";
  }

  // ── rendering ─────────────────────────────────────────────────────────
  var CAPTIONS = {
    tf: "<b>Count only.</b> The winners are the same filler on every card &mdash; " +
      "&ldquo;the&rdquo;, &ldquo;of&rdquo;, &ldquo;and&rdquo;. Raw frequency can&rsquo;t tell the documents apart.",
    idf: "<b>Rarity only.</b> Now the rarest words win. Distinctive &mdash; but is " +
      "&ldquo;one-thousandth&rdquo; really what Jupiter is <i>about</i>? Rarity ignores how central a word is to the document.",
    tfidf: "<b>TF &times; IDF.</b> Frequent in this document <i>and</i> rare across the others. " +
      "Each card now reads like a fingerprint of its topic."
  };
  var mode = "tf";

  function render() {
    var grid = $("grid");
    grid.innerHTML = "";
    DOCS.forEach(function (d) {
      var tops = topWords(d.id, mode, 6), max = tops[0].w || 1;
      var lis = tops.map(function (x) {
        var pct = Math.max(6, Math.round(100 * x.w / max));
        return '<li data-id="' + d.id + '" data-t="' + esc(x.t) + '">' +
          '<span class="w">' + esc(x.t) + '</span>' +
          '<span class="barwrap"><span class="bar" style="width:' + pct +
          '%;background:' + rarityColor(x.t) + '"></span></span></li>';
      }).join("");
      var card = document.createElement("div");
      card.className = "card";
      card.innerHTML = '<div class="card-title">' + esc(d.title) + '</div>' +
        '<ul class="words">' + lis + '</ul>';
      grid.appendChild(card);
    });
    $("caption").innerHTML = CAPTIONS[mode];
    refreshDetail();
    fit();
  }

  // ── inspector: click a word to see its actual numbers ─────────────────
  var sel = null;   // { id, t }
  function refreshDetail() {
    var el = $("detail");
    if (!sel || !COUNTS[sel.id] || !(sel.t in COUNTS[sel.id])) { el.hidden = true; return; }
    var id = sel.id, t = sel.t, title = "";
    for (var i = 0; i < DOCS.length; i++) if (DOCS[i].id === id) title = DOCS[i].title;
    var count = COUNTS[id][t], _tf = tf(id, t), _idf = IDF[t], _tfidf = _tf * _idf;
    function w(name, val, hot) {
      return '<span class="k">' + name + '</span> <span class="v' + (hot ? " win" : "") + '">' +
        val + '</span>';
    }
    el.innerHTML =
      '&ldquo;<b>' + esc(t) + '</b>&rdquo; in ' + esc(title) + ': ' +
      count + '&times; here, in ' + DF[t] + ' of ' + N + ' documents. &nbsp; ' +
      w("TF", _tf.toFixed(2), mode === "tf") + " &nbsp;·&nbsp; " +
      w("IDF", _idf.toFixed(2), mode === "idf") + " &nbsp;·&nbsp; " +
      w("TF·IDF", _tfidf.toFixed(2), mode === "tfidf");
    el.hidden = false;
    // mark the selected row
    var rows = document.querySelectorAll(".words li");
    for (var r = 0; r < rows.length; r++) {
      var on = rows[r].getAttribute("data-id") === id && rows[r].getAttribute("data-t") === t;
      rows[r].classList.toggle("sel", on);
    }
  }

  // ── iframe self-sizing (host page scrolls, no nested scrollbar) ───────
  function fit() {
    if (window.frameElement) window.frameElement.style.height = document.body.scrollHeight + "px";
  }

  // ── wiring ────────────────────────────────────────────────────────────
  function wire() {
    var btns = $("modes").querySelectorAll("button");
    for (var i = 0; i < btns.length; i++) {
      btns[i].addEventListener("click", function () {
        mode = this.getAttribute("data-mode");
        for (var j = 0; j < btns.length; j++) btns[j].classList.toggle("on", btns[j] === this);
        render();
      });
    }
    $("grid").addEventListener("click", function (e) {
      var li = e.target.closest ? e.target.closest("li[data-id]") : null;
      if (!li) return;
      sel = { id: li.getAttribute("data-id"), t: li.getAttribute("data-t") };
      refreshDetail();
    });
    window.addEventListener("resize", fit);
  }

  // ── boot ──────────────────────────────────────────────────────────────
  fetch("../corpus.json")
    .then(function (r) { return r.json(); })
    .then(function (corpus) {
      DF = buildModel(corpus);
      $("credit").innerHTML = esc(corpus.attribution) +
        ' <a href="' + esc(corpus.license_url) + '">CC BY-SA 4.0</a>';
      wire();
      render();
    })
    .catch(function (err) {
      $("caption").textContent = "Could not load the corpus: " + err;
    });
})();
