/* ───────────────────────────────────────────────────────────────────────
   TF-IDF · demo 2 "comparing two documents" — vanilla, self-contained.

   A document is a vector of word-weights (its TF-IDF scores, from demo 1).
   Cosine similarity between two documents is the dot product of their
   L2-normalized vectors: for every word they BOTH use, add weightA × weightB.
   A word only one document uses multiplies against a zero on the other side, so
   it contributes nothing. Those per-word contributions sum exactly to the
   cosine, which is what this demo shows: the number, decomposed into words, plus
   the full ranking of one document against every other.

   Tokenizer, stopwords, plural-stemmer, sublinear tf, smoothed idf and L2
   normalization are ported from scripts/compute-related.py, so the weights and
   the cosine match the site's live "related posts" engine. (Matching is done on
   stems; we display a representative surface form so plurals read naturally.
   We also drop ordinal fragments like "19th"→"th", which are tokenizer noise.)
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

  // ── tokenizer + light stemmer, ported verbatim from compute-related.py ──
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
  // ordinal fragments ("19th"→"th", "21st"→"st"): tokenizer noise, not words
  ["th", "st", "nd", "rd"].forEach(function (w) { STOPWORDS[w] = true; });

  function stem(tok) {
    if (tok.length <= 4) return tok;
    if (/(ss|us|is)$/.test(tok)) return tok;
    if (/ies$/.test(tok)) return tok.slice(0, -3) + "y";
    if (/s$/.test(tok)) return tok.slice(0, -1);
    return tok;
  }

  var TOKEN_RE = /[a-z][a-z0-9-]*[a-z0-9]|[a-z]/g;
  // returns stems; records the raw surface form each stem came from (for display)
  function tokenize(text, surf) {
    var raw = (text.toLowerCase().match(TOKEN_RE) || []), out = [];
    for (var i = 0; i < raw.length; i++) {
      var t = raw[i].replace(/^-+|-+$/g, "");
      if (t.length < 2 || STOPWORDS[t]) continue;
      var s = stem(t);
      if (STOPWORDS[s]) continue;
      if (surf) {
        var m = surf[s] || (surf[s] = {});
        m[t] = (m[t] || 0) + 1;
      }
      out.push(s);
    }
    return out;
  }

  // ── model: counts → tf·idf → L2-normalized vectors (compute-related.py) ──
  var DOCS = [], N = 0, VEC = {}, BYID = {}, LABEL = {};

  function buildModel(corpus) {
    DOCS = corpus.docs;
    N = DOCS.length;
    var COUNTS = {}, DF = {}, SURF = {};
    DOCS.forEach(function (d) {
      BYID[d.id] = d;
      var c = {}, toks = tokenize(d.text, SURF);
      for (var i = 0; i < toks.length; i++) c[toks[i]] = (c[toks[i]] || 0) + 1;
      COUNTS[d.id] = c;
      Object.keys(c).forEach(function (t) { DF[t] = (DF[t] || 0) + 1; });
    });
    var IDF = {};
    Object.keys(DF).forEach(function (t) {
      IDF[t] = Math.log((1 + N) / (1 + DF[t])) + 1;          // smoothed idf
    });
    DOCS.forEach(function (d) {
      var c = COUNTS[d.id], raw = {}, sq = 0;
      Object.keys(c).forEach(function (t) {
        var w = (1 + Math.log(c[t])) * IDF[t];               // sublinear tf · idf
        raw[t] = w; sq += w * w;
      });
      var norm = Math.sqrt(sq) || 1;
      var v = {};
      Object.keys(raw).forEach(function (t) { v[t] = raw[t] / norm; });   // L2
      VEC[d.id] = v;
    });
    // pick the most frequent surface form as each stem's display label
    Object.keys(SURF).forEach(function (s) {
      var forms = SURF[s], best = s, n = -1;
      Object.keys(forms).forEach(function (f) { if (forms[f] > n) { n = forms[f]; best = f; } });
      LABEL[s] = best;
    });
  }

  function label(t) { return LABEL[t] || t; }

  // shared words, sorted by contribution vA·vB (these sum to the full cosine)
  function shared(aId, bId) {
    var a = VEC[aId], b = VEC[bId], out = [];
    Object.keys(a).forEach(function (t) { if (t in b) out.push({ t: t, c: a[t] * b[t] }); });
    out.sort(function (x, y) { return y.c - x.c; });
    return out;
  }
  function cosine(aId, bId) {
    return shared(aId, bId).reduce(function (s, x) { return s + x.c; }, 0);
  }
  // words one doc uses and the other doesn't, highest-weight first
  function only(aId, bId) {
    var a = VEC[aId], b = VEC[bId], out = [];
    Object.keys(a).forEach(function (t) { if (!(t in b)) out.push({ t: t, w: a[t] }); });
    out.sort(function (x, y) { return y.w - x.w; });
    return out;
  }

  // ── state ───────────────────────────────────────────────────────────────
  var aId = "lion", bId = "tiger", TOPK = 8;

  // sequential blue→orange ramp for the top contribution segments
  function ramp(i, n) {
    var h = 222 - (222 - 22) * (n <= 1 ? 0 : i / (n - 1));
    return "hsl(" + h.toFixed(0) + ", 62%, 56%)";
  }

  function fillDocSelects() {
    var groups = {};
    DOCS.forEach(function (d) { (groups[d.cluster] = groups[d.cluster] || []).push(d); });
    ["selA", "selB"].forEach(function (id) {
      var sel = $(id);
      sel.innerHTML = "";
      Object.keys(groups).forEach(function (cl) {
        var og = document.createElement("optgroup"); og.label = cl;
        groups[cl].forEach(function (d) {
          var o = document.createElement("option"); o.value = d.id; o.textContent = d.title;
          og.appendChild(o);
        });
        sel.appendChild(og);
      });
    });
    $("selA").value = aId; $("selB").value = bId;
  }

  // ── render: the pair, decomposed ────────────────────────────────────────
  function renderPair() {
    var sh = shared(aId, bId), full = sh.reduce(function (s, x) { return s + x.c; }, 0);
    var top = sh.slice(0, TOPK), restArr = sh.slice(TOPK);
    var restSum = restArr.reduce(function (s, x) { return s + x.c; }, 0);

    $("pairhead").innerHTML =
      "<span class='a'>" + esc(BYID[aId].title) + "</span> vs " +
      "<span class='b'>" + esc(BYID[bId].title) + "</span>";

    // meter: fill = cosine, split into one segment per top word + a "rest" block
    var segs = top.map(function (x, i) {
      return "<span class='seg' style='width:" + (x.c * 100).toFixed(2) +
        "%;background:" + ramp(i, top.length) + "' title='" + esc(label(x.t)) +
        " · " + x.c.toFixed(3) + "'></span>";
    }).join("");
    if (restSum > 0)
      segs += "<span class='seg rest' style='width:" + (restSum * 100).toFixed(2) +
        "%' title='" + restArr.length + " more shared words · " + restSum.toFixed(3) + "'></span>";
    $("stack").innerHTML = segs;

    $("scorenum").innerHTML =
      "cosine similarity <b>" + full.toFixed(2) + "</b> out of 1.0 &nbsp;&middot;&nbsp; " +
      "built from <b>" + sh.length + "</b> shared words";

    // contribution list: top words (colour-matched to the meter) + a rest row
    var maxc = top.length ? top[0].c : 1;
    var barW = function (v) { return Math.min(100, Math.max(2, v / maxc * 100)).toFixed(1); };
    var rows = top.map(function (x, i) {
      return "<li><span class='cw'>" + esc(label(x.t)) + "</span>" +
        "<span class='cbar' style='width:" + barW(x.c) +
        "%;background:" + ramp(i, top.length) + "'></span>" +
        "<span class='cv'>" + x.c.toFixed(3) + "</span></li>";
    }).join("");
    if (restArr.length)
      rows += "<li class='rest'><span class='cw'>+ " + restArr.length + " more</span>" +
        "<span class='cbar' style='width:" + barW(restSum) + "%'></span>" +
        "<span class='cv'>" + restSum.toFixed(3) + "</span></li>";
    $("contribs").innerHTML = rows;

    renderUnique();
  }

  function chips(arr, n) {
    var s = arr.slice(0, n).map(function (x) {
      return "<span class='chip'>" + esc(label(x.t)) + " <span class='z'>&times;0</span></span>";
    }).join("");
    if (arr.length > n) s += "<span class='chip'>+ " + (arr.length - n) + " more</span>";
    return s;
  }
  function renderUnique() {
    var oa = only(aId, bId), ob = only(bId, aId);
    $("uqA").innerHTML = "<span class='who a'>Only " + esc(BYID[aId].title) + "</span> " +
      "(" + oa.length + " words): " + chips(oa, 6);
    $("uqB").innerHTML = "<span class='who b'>Only " + esc(BYID[bId].title) + "</span> " +
      "(" + ob.length + " words): " + chips(ob, 6);
  }

  // ── render: the whole ranking of A against every other document ──────────
  function renderRanks() {
    var rows = DOCS.filter(function (d) { return d.id !== aId; })
      .map(function (d) { return { id: d.id, title: d.title, cluster: d.cluster, c: cosine(aId, d.id) }; })
      .sort(function (x, y) { return y.c - x.c; });
    var aCluster = BYID[aId].cluster;

    $("rankhead").innerHTML = "<span class='a'>" + esc(BYID[aId].title) +
      "</span> compared with every other document:";
    $("ranklist").innerHTML = rows.map(function (r) {
      var cls = [];
      if (r.cluster === aCluster) cls.push("same");
      if (r.id === bId) cls.push("cur");
      return "<li data-id='" + esc(r.id) + "' class='" + cls.join(" ") + "'>" +
        "<span class='rk'>" + esc(r.title) +
        "<span class='rbar' style='width:" + Math.max(1, r.c * 100).toFixed(1) + "%'></span></span>" +
        "<span class='rv'>" + r.c.toFixed(2) + "</span></li>";
    }).join("");
    [].forEach.call($("ranklist").querySelectorAll("li"), function (li) {
      li.addEventListener("click", function () {
        bId = li.getAttribute("data-id");
        $("selB").value = bId;
        renderAll();
      });
    });

    $("ranknote").innerHTML = "Every score sits well below 1, yet <b>" +
      esc(BYID[aId].title) + "</b>&rsquo;s own kind lands on top. The useful " +
      "signal is the <b>ranking</b>, not the size of the number.";
  }

  function renderAll() { renderPair(); renderRanks(); fit(); }

  function fit() {
    if (window.frameElement) window.frameElement.style.height = document.body.scrollHeight + "px";
  }

  // ── wiring ────────────────────────────────────────────────────────────────
  function wire() {
    $("selA").addEventListener("change", function () {
      aId = this.value;
      if (bId === aId) { bId = DOCS[(DOCS.map(function (d) { return d.id; }).indexOf(aId) + 1) % N].id; $("selB").value = bId; }
      renderAll();
    });
    $("selB").addEventListener("change", function () {
      bId = this.value;
      if (aId === bId) { aId = DOCS[(DOCS.map(function (d) { return d.id; }).indexOf(bId) + 1) % N].id; $("selA").value = aId; }
      renderAll();
    });
    window.addEventListener("resize", fit);
  }

  // ── boot ────────────────────────────────────────────────────────────────
  fetch("../corpus.json")
    .then(function (r) { return r.json(); })
    .then(function (corpus) {
      buildModel(corpus);
      $("credit").innerHTML = esc(corpus.attribution) +
        ' <a href="' + esc(corpus.license_url) + '">CC BY-SA 4.0</a>';
      fillDocSelects();
      wire();
      renderAll();
    })
    .catch(function (err) {
      $("scorenum").textContent = "Could not load the corpus: " + err;
    });
})();
