/* ───────────────────────────────────────────────────────────────────────
   TF-IDF · demo 3 "compare your own text" — vanilla, self-contained.

   The reader supplies two texts; we vectorize each with the same TF-IDF machine
   as demos 1-2 and show their cosine, decomposed word by word. The catch with
   IDF is that it needs a corpus to judge rarity against — two pasted texts alone
   can't say what's "common". So rarity is measured against the same background
   library from the earlier demos (its 12 documents), with the reader's two texts
   added in. That keeps everyday words discounted even in text never seen before.

   Tokenizer, stopwords, plural-stemmer, sublinear tf, smoothed idf and L2
   normalization are ported from scripts/compute-related.py (matching on stems,
   displaying a representative surface form; ordinal fragments like "19th"→"th"
   dropped as noise).
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

  // ── tokenizer + light stemmer, ported from compute-related.py ──
  var STOPWORDS = {};
  ("a about above after again all also am an and any are as at be because been " +
   "before being below between both but by can could did do does doing done down " +
   "during each few for from further had has have having he her here hers him his " +
   "how i if in into is it its just let like made make many me more most much my no " +
   "nor not now of off on once one only or other our out over own per same she " +
   "should so some still such than that the their them then there these they thing " +
   "things this those through to too under until up use used using very was we were " +
   "what when where which while who why will with would you your yet get got via want " +
   "wanted need needed well way ways ll ve re im isn didn doesn don won wasn aren " +
   "wouldn couldn shouldn hasn haven wont cant"
  ).split(" ").forEach(function (w) { STOPWORDS[w] = true; });
  ["th", "st", "nd", "rd"].forEach(function (w) { STOPWORDS[w] = true; });   // ordinal noise

  function stem(tok) {
    if (tok.length <= 4) return tok;
    if (/(ss|us|is)$/.test(tok)) return tok;
    if (/ies$/.test(tok)) return tok.slice(0, -3) + "y";
    if (/s$/.test(tok)) return tok.slice(0, -1);
    return tok;
  }

  var TOKEN_RE = /[a-z][a-z0-9-]*[a-z0-9]|[a-z]/g;
  function tokenize(text, surf) {
    var raw = (text.toLowerCase().match(TOKEN_RE) || []), out = [];
    for (var i = 0; i < raw.length; i++) {
      var t = raw[i].replace(/^-+|-+$/g, "");
      if (t.length < 2 || STOPWORDS[t]) continue;
      var s = stem(t);
      if (STOPWORDS[s]) continue;
      if (surf) { var m = surf[s] || (surf[s] = {}); m[t] = (m[t] || 0) + 1; }
      out.push(s);
    }
    return out;
  }
  function counts(toks) {
    var c = {};
    for (var i = 0; i < toks.length; i++) c[toks[i]] = (c[toks[i]] || 0) + 1;
    return c;
  }

  // ── background library: document frequencies over the 12 corpus docs ──
  var BG_DF = {}, BG_N = 0;
  function buildBackground(corpus) {
    BG_N = corpus.docs.length;
    corpus.docs.forEach(function (d) {
      var seen = {}, toks = tokenize(d.text);
      for (var i = 0; i < toks.length; i++) {
        if (!seen[toks[i]]) { seen[toks[i]] = 1; BG_DF[toks[i]] = (BG_DF[toks[i]] || 0) + 1; }
      }
    });
  }

  function ramp(i, n) {
    var h = 222 - (222 - 22) * (n <= 1 ? 0 : i / (n - 1));
    return "hsl(" + h.toFixed(0) + ", 62%, 56%)";
  }
  function verdict(c) {
    if (c >= 0.45) return "very similar";
    if (c >= 0.22) return "clearly related";
    if (c >= 0.09) return "loosely related";
    if (c > 0) return "barely related";
    return "no shared words";
  }

  // ── compare the two texts ─────────────────────────────────────────────────
  function compare() {
    var surf = {};
    var tא = tokenize($("txtA").value, surf), tb = tokenize($("txtB").value, surf);
    if (!tא.length || !tb.length) { showEmpty(); return; }

    var ca = counts(tא), cb = counts(tb);
    var setA = ca, setB = cb;
    var N = BG_N + 2;                                   // background docs + these two

    // idf for any term either text uses (background df + presence in A / B)
    function idf(t) {
      var df = (BG_DF[t] || 0) + (t in setA ? 1 : 0) + (t in setB ? 1 : 0);
      return Math.log((1 + N) / (1 + df)) + 1;
    }
    function vec(c) {
      var raw = {}, sq = 0;
      Object.keys(c).forEach(function (t) {
        var w = (1 + Math.log(c[t])) * idf(t); raw[t] = w; sq += w * w;
      });
      var norm = Math.sqrt(sq) || 1, v = {};
      Object.keys(raw).forEach(function (t) { v[t] = raw[t] / norm; });
      return v;
    }
    var va = vec(ca), vb = vec(cb);

    var sh = [];
    Object.keys(va).forEach(function (t) { if (t in vb) sh.push({ t: t, c: va[t] * vb[t] }); });
    sh.sort(function (x, y) { return y.c - x.c; });
    var full = sh.reduce(function (s, x) { return s + x.c; }, 0);

    var label = {};
    Object.keys(surf).forEach(function (s) {
      var f = surf[s], best = s, n = -1;
      Object.keys(f).forEach(function (k) { if (f[k] > n) { n = f[k]; best = k; } });
      label[s] = best;
    });

    showResult(sh, full, label, {
      shared: sh.length,
      onlyA: Object.keys(setA).filter(function (t) { return !(t in setB); }).length,
      onlyB: Object.keys(setB).filter(function (t) { return !(t in setA); }).length
    });
  }

  function showEmpty() { $("empty").hidden = false; $("result").hidden = true; fit(); }

  function showResult(sh, full, label, stats) {
    $("empty").hidden = true; $("result").hidden = false;

    var TOPK = 8, top = sh.slice(0, TOPK), rest = sh.slice(TOPK);
    var restSum = rest.reduce(function (s, x) { return s + x.c; }, 0);

    var segs = top.map(function (x, i) {
      return "<span class='seg' style='width:" + (x.c * 100).toFixed(2) +
        "%;background:" + ramp(i, top.length) + "' title='" + esc(label[x.t]) + " · " +
        x.c.toFixed(3) + "'></span>";
    }).join("");
    if (restSum > 0)
      segs += "<span class='seg rest' style='width:" + (restSum * 100).toFixed(2) + "%'></span>";
    $("stack").innerHTML = segs;

    $("scorenum").innerHTML = "cosine similarity <b>" + full.toFixed(2) + "</b> out of 1.0 " +
      "&nbsp;&middot;&nbsp; <span class='verdict'>" + verdict(full) + "</span>";

    if (!sh.length) {
      $("contribs").innerHTML = "";
      $("bkhead").style.display = "none";
    } else {
      $("bkhead").style.display = "";
      var maxc = top[0].c;
      var barW = function (v) { return Math.min(100, Math.max(2, v / maxc * 100)).toFixed(1); };
      var rows = top.map(function (x, i) {
        return "<li><span class='cw'>" + esc(label[x.t]) + "</span>" +
          "<span class='cbar' style='width:" + barW(x.c) + "%;background:" + ramp(i, top.length) +
          "'></span><span class='cv'>" + x.c.toFixed(3) + "</span></li>";
      }).join("");
      if (rest.length)
        rows += "<li class='rest'><span class='cw'>+ " + rest.length + " more</span>" +
          "<span class='cbar' style='width:" + barW(restSum) + "%'></span>" +
          "<span class='cv'>" + restSum.toFixed(3) + "</span></li>";
      $("contribs").innerHTML = rows;
    }

    $("sharednote").innerHTML = "They share <b>" + stats.shared + "</b> words. " +
      "<b>" + stats.onlyA + "</b> words appear only in A and <b>" + stats.onlyB +
      "</b> only in B &mdash; those multiply against a zero and add nothing. " +
      "(Rarity is scored against the earlier demos&rsquo; 12-document library plus your two texts.)";
    fit();
  }

  function fit() {
    if (window.frameElement) window.frameElement.style.height = document.body.scrollHeight + "px";
  }

  // ── examples (original text; blank by default) ──────────────────────────────
  var EXAMPLES = [
    { label: "Two takes on espresso",
      a: "A good espresso starts with fresh beans ground fine and packed evenly into the basket. Hot water is forced through the grounds under pressure, pulling a thick dark shot in well under a minute.",
      b: "To pull a clean shot, grind the beans just before brewing and tamp the grounds flat. The machine pushes pressurized hot water through the coffee, and a good espresso comes out dark and syrupy." },
    { label: "Coffee vs. photography",
      a: "A good espresso depends on fresh roasted beans, a fine even grind, and water heated to just the right point, forced through under steady pressure to pull a rich dark shot without ever scorching the coffee.",
      b: "A good landscape photo depends on soft early light, a low steady tripod, and no small amount of patience, so that every shot stays crisp and sharp from the near mossy rocks to the far mountain peaks." },
    { label: "Same idea, other words",
      a: "The film was a slog. I kept checking my phone and could not wait for the credits to roll.",
      b: "What a tedious movie. My attention wandered within minutes and the ending came as a mercy." }
  ];
  function buildExamples() {
    $("exbtns").innerHTML = EXAMPLES.map(function (e, i) {
      return "<button class='exbtn' data-i='" + i + "'>" + esc(e.label) + "</button>";
    }).join("");
    [].forEach.call($("exbtns").querySelectorAll(".exbtn"), function (b) {
      b.addEventListener("click", function () {
        var e = EXAMPLES[+b.getAttribute("data-i")];
        $("txtA").value = e.a; $("txtB").value = e.b; compare();
      });
    });
  }

  // ── wiring ────────────────────────────────────────────────────────────────
  var timer = null;
  function onInput() { clearTimeout(timer); timer = setTimeout(compare, 180); }

  fetch("../corpus.json")
    .then(function (r) { return r.json(); })
    .then(function (corpus) {
      buildBackground(corpus);
      $("credit").innerHTML = "Background library: " + esc(corpus.attribution) +
        ' <a href="' + esc(corpus.license_url) + '">CC BY-SA 4.0</a>. Your text stays in the browser.';
      buildExamples();
      $("txtA").addEventListener("input", onInput);
      $("txtB").addEventListener("input", onInput);
      showEmpty();
    })
    .catch(function (err) { $("empty").textContent = "Could not load the background library: " + err; });
})();
