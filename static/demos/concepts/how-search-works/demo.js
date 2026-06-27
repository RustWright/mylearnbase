/* ───────────────────────────────────────────────────────────────────────
   "How search works — the index trick" · concepts demo logic
   Vanilla, self-contained. Loads corpus.json (public-domain Sherlock Holmes,
   one sentence per "document"), then lets the reader race two methods:
     · SCAN  — examine every document          → N comparisons / query
     · INDEX — prebuilt term → [docIds] lookup  → 1 comparison / query, but
               an up-front build cost of P postings (shown, and charted).
   ─────────────────────────────────────────────────────────────────────── */
(function () {
  "use strict";

  var root = document.getElementById("demo");
  if (!root) return; // not the demo page

  var SVGNS = "http://www.w3.org/2000/svg";
  var $ = function (id) { return document.getElementById(id); };
  var fmt = function (n) { return n.toLocaleString("en-US"); };
  var esc = function (s) {
    return s.replace(/[&<>]/g, function (c) {
      return c === "&" ? "&amp;" : c === "<" ? "&lt;" : "&gt;";
    });
  };
  var fmtTime = function (ms) {
    return ms < 1000 ? ms.toFixed(0) + " ms" : (ms / 1000).toFixed(1) + " s";
  };

  // ── search primitives ──────────────────────────────────────────────
  function tokenize(s) { return s.toLowerCase().match(/[a-z0-9]+/g) || []; }

  function buildIndex(docs) {
    var idx = new Map(), postings = 0;
    for (var i = 0; i < docs.length; i++) {
      var seen = {};
      var toks = tokenize(docs[i]);
      for (var j = 0; j < toks.length; j++) {
        var t = toks[j];
        if (seen[t]) continue;       // one posting per (term, doc)
        seen[t] = 1; postings++;
        if (!idx.has(t)) idx.set(t, []);
        idx.get(t).push(i);
      }
    }
    return { idx: idx, postings: postings, terms: Array.from(idx.keys()).sort(), N: docs.length };
  }

  function lookup(index, term) { return index.idx.get(term.toLowerCase()) || []; }

  function scanAll(docs, term) {        // examines all N docs; returns hit ids
    term = term.toLowerCase();
    var hits = [];
    for (var i = 0; i < docs.length; i++) {
      if (tokenize(docs[i]).indexOf(term) !== -1) hits.push(i);
    }
    return hits;
  }

  function lowerBound(arr, x) {
    var lo = 0, hi = arr.length;
    while (lo < hi) { var m = (lo + hi) >> 1; if (arr[m] < x) lo = m + 1; else hi = m; }
    return lo;
  }

  // ── state ───────────────────────────────────────────────────────────
  var FULL = null, SMALL = null;        // { docs, index }
  var QMAX = 40, qStar = 12;
  var step = 0, scan = { raf: 0, running: false, cancel: null };
  var NARROW = window.matchMedia("(max-width: 640px)");  // mobile = flow mode

  var MISSIONS = [
    { label: "Mission 1 / 4", q: "Holmes", corpus: "small", viz: "build",
      prompt: "Find every line that mentions “Holmes”.",
      sub: "A handful of documents. Both methods reach the same answer. Watch how much work each does to get there." },
    { label: "Mission 2 / 4", q: "revolver", corpus: "full", viz: "A",
      prompt: "Now the whole book: find where “revolver” appears.",
      sub: "5,463 documents. The scan has to walk every one; the index already knows." },
    { label: "Mission 3 / 4", q: "submarine", corpus: "full", viz: "A", ghost: true,
      prompt: "Find any line mentioning “submarine”.",
      sub: "You can’t tell in advance whether it’s in there. Let the scan run… or lose patience and let the index answer." },
    { label: "Mission 4 / 4", q: "", corpus: "full", viz: "B",
      prompt: "Was building the index even worth it?",
      sub: "The index isn’t free. It costs an up-front build. Drag the number of searches and find the point where it pays off." },
    { label: "Free play", q: "", corpus: "full", viz: "A", free: true,
      prompt: "Your turn. Type any word and run both.",
      sub: "Try a common word, a rare one, or one that isn’t in the book at all." }
  ];

  function active() { return MISSIONS[step]; }
  function corpus() { return active().corpus === "small" ? SMALL : FULL; }

  // ── scan lane (the paced animation) ─────────────────────────────────
  function renderWindow(docs, pos, hitSet) {
    var N = docs.length, span = NARROW.matches ? 7 : 13;    // fewer rows on mobile (it flows, no fixed budget)
    var startI = Math.max(0, Math.min(pos - 2, N - span));  // playhead near top → stays visible in short boxes
    if (startI < 0) startI = 0;
    var endI = Math.min(N, startI + span);
    var html = "";
    for (var i = startI; i < endI; i++) {
      var cls = "doc";
      if (i === pos) cls = "doc checking";
      else if (hitSet.has(i) && i <= pos) cls = "doc hit";
      html += '<div class="' + cls + '"><span class="id">d' + i + "</span>" + esc(docs[i]) + "</div>";
    }
    $("scan-corpus").innerHTML = html;
  }

  function stopScan() {
    if (scan.raf) cancelAnimationFrame(scan.raf);
    scan.raf = 0; scan.running = false; scan.cancel = null;
    $("skip").hidden = true;
  }

  function runScan(term) {
    var docs = corpus().docs, N = docs.length;
    var hitSet = new Set(scanAll(docs, term));
    var reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
    var duration = N <= 30 ? N * 160 : (reduce ? 1200 : 22000);
    $("scan-paced").textContent = N > 30 ? "(paced so you can watch; real time is a few ms)" : "";
    $("scan-result").hidden = true;

    var t0 = null;
    function finish() {
      stopScan();
      renderWindow(docs, N - 1, hitSet);
      $("scan-cmp").textContent = fmt(N);
      showResult($("scan-result"), Array.from(hitSet), term, N);
    }
    function frame(ts) {
      if (t0 === null) t0 = ts;
      var elapsed = ts - t0;
      var pos = Math.min(N, Math.floor(N * (elapsed / duration)));
      renderWindow(docs, Math.min(pos, N - 1), hitSet);
      $("scan-cmp").textContent = fmt(pos);
      $("scan-time").textContent = fmtTime(elapsed);
      if (pos >= N || elapsed >= duration) { finish(); return; }
      scan.raf = requestAnimationFrame(frame);
    }
    scan.running = true;
    scan.cancel = finish;                 // "let the index finish it" jumps to end
    $("skip").hidden = N <= 30;           // only worth offering on the long grind
    scan.raf = requestAnimationFrame(frame);
  }

  // ── index lane ──────────────────────────────────────────────────────
  function postingsLabel(ids) {
    if (!ids.length) return "(no such term)";
    var head = ids.slice(0, 4).map(function (i) { return "d" + i; }).join(", ");
    return head + (ids.length > 4 ? " …(+" + (ids.length - 4) + ")" : "");
  }

  function renderIndexSlice(index, term) {
    var terms = index.terms, t = (term || "").toLowerCase();
    var center = t ? lowerBound(terms, t) : 0;
    var span = 7, startI = Math.max(0, Math.min(center - 3, terms.length - span));
    var html = "";
    for (var i = startI; i < startI + span && i < terms.length; i++) {
      var tt = terms[i], ids = index.idx.get(tt);
      var lit = (tt === t) ? " lit" : "";
      html += '<div class="term-row' + lit + '"><span class="term">' + esc(tt) +
        '</span><span class="arrow">→</span><span class="postings">' + postingsLabel(ids) + "</span></div>";
    }
    if (t && terms.indexOf(t) === -1) {
      html += '<div class="index-note">“' + esc(t) + "” isn’t in the index, so the lookup returns nothing, instantly. No documents examined.</div>";
    } else {
      html += '<div class="index-note">' + fmt(index.idx.size) + " terms in this index, built once from " + fmt(index.N) + " documents.</div>";
    }
    $("index-view").innerHTML = html;
  }

  function runIndex(term) {
    var index = corpus().index, ids = lookup(index, term);
    renderIndexSlice(index, term);
    $("index-cmp").textContent = "1";
    $("index-time").textContent = "0.0 ms";
    showResult($("index-result"), ids, term, index.N);
  }

  // build animation for the small corpus (M1): postings file in one by one
  function buildAnimation() {
    var index = SMALL.index, terms = index.terms;
    var view = $("index-view");
    var reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
    view.innerHTML = "";
    var rows = terms.map(function (tt) {
      return '<div class="term-row"><span class="term">' + esc(tt) +
        '</span><span class="arrow">→</span><span class="postings">' +
        postingsLabel(index.idx.get(tt)) + "</span></div>";
    });
    if (reduce) {
      view.innerHTML = rows.join("") +
        '<div class="index-note">Index built: ' + fmt(index.postings) + " postings filed (one per word, per document).</div>";
      return;
    }
    var i = 0, built = 0;
    (function tick() {
      if (i >= rows.length) {
        view.insertAdjacentHTML("beforeend",
          '<div class="index-note">Index built: ' + fmt(index.postings) +
          " postings filed (one per word, per document). That up-front cost is the catch. See the chart below.</div>");
        return;
      }
      var d = document.createElement("div");
      d.innerHTML = rows[i];
      var node = d.firstChild;
      node.classList.add("flying");
      node.style.opacity = "0";
      node.style.transform = "translateY(6px)";
      view.appendChild(node);
      requestAnimationFrame(function () { node.style.opacity = ""; node.style.transform = ""; });
      built += index.idx.get(terms[i]).length;
      i++;
      setTimeout(tick, 90);
    })();
  }

  // ── shared result strip ─────────────────────────────────────────────
  function showResult(elm, ids, term, N) {
    elm.hidden = false;
    if (!ids.length) {
      elm.className = "result none";
      elm.textContent = "Nothing found. “" + term + "” is in none of the " + fmt(N) + " documents.";
    } else {
      elm.className = "result";
      elm.textContent = "Found in " + fmt(ids.length) + " document" + (ids.length === 1 ? "" : "s") + ".";
    }
  }

  // ── charts (hand-rolled SVG) ────────────────────────────────────────
  var PAD = { l: 34, r: 12, t: 12, b: 22 };
  function chartBox(svg) {
    var w = +svg.getAttribute("width"), h = +svg.getAttribute("height");
    return { w: w, h: h, pw: w - PAD.l - PAD.r, ph: h - PAD.t - PAD.b };
  }
  function svgEl(name, attrs) {
    var e = document.createElementNS(SVGNS, name);
    for (var k in attrs) e.setAttribute(k, attrs[k]);
    return e;
  }
  function clear(node) { while (node.firstChild) node.removeChild(node.firstChild); }

  function axes(svg, b, xlab, ylab) {
    svg.appendChild(svgEl("line", { x1: PAD.l, y1: PAD.t, x2: PAD.l, y2: PAD.t + b.ph, stroke: "var(--line)" }));
    svg.appendChild(svgEl("line", { x1: PAD.l, y1: PAD.t + b.ph, x2: PAD.l + b.pw, y2: PAD.t + b.ph, stroke: "var(--line)" }));
    var tx = svgEl("text", { x: PAD.l + b.pw, y: b.h - 5, "text-anchor": "end", fill: "var(--pale)", "font-size": "10" });
    tx.textContent = xlab; svg.appendChild(tx);
    var ty = svgEl("text", { x: 4, y: PAD.t + 7, fill: "var(--pale)", "font-size": "10" });
    ty.textContent = ylab; svg.appendChild(ty);
  }
  function dot(svg, x, y, color) { svg.appendChild(svgEl("circle", { cx: x, cy: y, r: 3.5, fill: color })); }

  // Viz A — comparisons vs corpus size
  function chartA() {
    var svg = $("chart"); clear(svg);
    var b = chartBox(svg), N = FULL.index.N, curN = corpus().index.N;
    var x = function (s) { return PAD.l + (s / N) * b.pw; };
    var yTop = PAD.t, yBot = PAD.t + b.ph;
    var yScan = function (c) { return yBot - (c / N) * b.ph; };
    axes(svg, b, "corpus size", "comparisons");
    // index line: ~1, flat along the bottom
    svg.appendChild(svgEl("line", { x1: x(0), y1: yBot, x2: x(N), y2: yBot - (1 / N) * b.ph, stroke: "var(--index)", "stroke-width": 2 }));
    // scan line: comparisons = size (diagonal)
    svg.appendChild(svgEl("line", { x1: x(0), y1: yScan(0), x2: x(N), y2: yScan(N), stroke: "var(--scan)", "stroke-width": 2 }));
    dot(svg, x(curN), yScan(curN), "var(--scan)");
    dot(svg, x(curN), yBot, "var(--index)");
    // value readouts parked in the empty lower-right interior (below the diagonal,
    // above the x-axis label) and right-anchored, so they never clip or sit on a line
    var lx = PAD.l + b.pw - 6, ly = yTop + b.ph * 0.62;
    var ts = svgEl("text", { x: lx, y: ly, "text-anchor": "end", fill: "var(--scan)", "font-size": "11", "font-weight": "600" });
    ts.textContent = "scan: " + fmt(curN); svg.appendChild(ts);
    var ti = svgEl("text", { x: lx, y: ly + 15, "text-anchor": "end", fill: "var(--index)", "font-size": "11", "font-weight": "600" });
    ti.textContent = "index: 1"; svg.appendChild(ti);
    setVizText("Work vs. how much data",
      "Scanning grows with the corpus (" + fmt(curN) + " comparisons here); the index stays at one lookup no matter how big the book gets.");
    $("viz-controls").innerHTML = legendHTML();
  }

  // Viz B — total cost vs number of queries (the break-even)
  function drawB(q) {                    // redraw chart + caption only (drag-safe)
    var svg = $("chart"); clear(svg);
    var b = chartBox(svg), N = FULL.index.N, P = FULL.index.postings;
    var maxCost = QMAX * N;
    var x = function (qq) { return PAD.l + (qq / QMAX) * b.pw; };
    var y = function (c) { return PAD.t + b.ph - (c / maxCost) * b.ph; };
    axes(svg, b, "searches", "total work");
    // scan: q*N   index: P + q
    svg.appendChild(svgEl("line", { x1: x(0), y1: y(0), x2: x(QMAX), y2: y(QMAX * N), stroke: "var(--scan)", "stroke-width": 2 }));
    svg.appendChild(svgEl("line", { x1: x(0), y1: y(P), x2: x(QMAX), y2: y(P + QMAX), stroke: "var(--index)", "stroke-width": 2 }));
    // break-even marker
    svg.appendChild(svgEl("line", { x1: x(qStar), y1: PAD.t, x2: x(qStar), y2: PAD.t + b.ph, stroke: "var(--pale)", "stroke-dasharray": "3 3" }));
    var be = svgEl("text", { x: x(qStar) + 3, y: PAD.t + 9, fill: "var(--pale)", "font-size": "9.5" });
    be.textContent = "break-even"; svg.appendChild(be);
    // current-q markers
    dot(svg, x(q), y(q * N), "var(--scan)");
    dot(svg, x(q), y(P + q), "var(--index)");
    var scanC = q * N, idxC = P + q, win = scanC < idxC ? "scanning wins" : "the index wins";
    setVizText("Work vs. how often you search",
      "After " + fmt(q) + " search" + (q === 1 ? "" : "es") + ": scanning costs " + fmt(scanC) +
      ", the index costs " + fmt(idxC) + " (a " + fmt(P) + "-posting build, then ~1 each). So far, " + win +
      ". They cross at ≈ " + qStar + " searches, about the average words per sentence.");
    var out = $("qout"); if (out) out.textContent = q;
  }
  function chartB(q) {                    // build controls once, then draw
    $("viz-controls").innerHTML = legendHTML() +
      ' <label class="legend">searches: <input id="qslider" type="range" min="1" max="' + QMAX +
      '" value="' + q + '"></label> <output id="qout">' + q + "</output>";
    var sl = $("qslider");
    if (sl) sl.addEventListener("input", function () { drawB(+sl.value); });
    drawB(q);
  }

  function legendHTML() {
    return '<span class="legend"><i class="s"></i>scan</span> &nbsp; <span class="legend"><i class="i"></i>index</span>';
  }
  function setVizText(title, caption) {
    $("viz-title").textContent = title;
    $("viz-caption").textContent = caption;
  }

  // ── mission rendering + stepper ─────────────────────────────────────
  function resetMetrics() {
    $("scan-cmp").textContent = "0"; $("scan-time").textContent = "0 ms"; $("scan-paced").textContent = "";
    $("index-cmp").textContent = "0"; $("index-time").textContent = "0 ms";
    $("scan-result").hidden = true; $("index-result").hidden = true;
  }

  function renderMission() {
    stopScan();
    var m = active();
    $("mission-label").textContent = m.label;
    $("mission-prompt").textContent = m.prompt;
    $("mission-sub").textContent = m.sub;
    $("query").value = "";
    var sug = $("suggest");
    if (m.q && !m.free) { sug.hidden = false; sug.textContent = "try: “" + m.q + "”"; }
    else sug.hidden = true;
    $("corpus-size").textContent = fmt(corpus().index.N) + " documents";
    resetMetrics();

    // scan lane initial view
    renderWindow(corpus().docs, 0, new Set());
    // index lane
    if (m.viz === "build") buildAnimation();
    else renderIndexSlice(corpus().index, m.q);
    // viz
    if (m.viz === "B") chartB(Math.min(QMAX, Math.max(1, qStar)));
    else chartA();

    // nav state
    $("prev").disabled = step === 0;
    $("next").disabled = step === MISSIONS.length - 1;
    var dots = $("dots"); dots.innerHTML = "";
    for (var i = 0; i < MISSIONS.length; i++) {
      var d = document.createElement("span");
      d.className = "dot" + (i === step ? " on" : "");
      dots.appendChild(d);
    }
    syncRun();
  }

  function syncRun() { $("run").disabled = !$("query").value.trim(); }

  function go() {
    var term = $("query").value.trim();
    if (!term) return;
    stopScan();
    resetMetrics();
    runIndex(term);   // instant — sits there while the scan grinds
    runScan(term);
    // keep the chart in step with the corpus being queried
    if (active().viz !== "B") chartA();
  }

  // ── wiring ──────────────────────────────────────────────────────────
  $("run").addEventListener("click", go);
  $("query").addEventListener("input", syncRun);
  $("query").addEventListener("keydown", function (e) { if (e.key === "Enter" && !$("run").disabled) go(); });
  $("suggest").addEventListener("click", function () { $("query").value = active().q; syncRun(); $("query").focus(); });
  $("skip").addEventListener("click", function () { if (scan.cancel) scan.cancel(); });
  $("prev").addEventListener("click", function () { if (step > 0) { step--; renderMission(); } });
  $("next").addEventListener("click", function () { if (step < MISSIONS.length - 1) { step++; renderMission(); } });

  // On mobile the demo flows to natural height and sizes its own iframe to fit
  // (same-origin → window.frameElement is reachable), so the host page scrolls
  // rather than trapping content in a clipped frame. Desktop keeps its fixed height.
  function resizeFrame() {
    var fe;
    try { fe = window.frameElement; } catch (e) { return; }   // cross-origin guard
    if (!fe) return;                                          // standalone, not embedded
    if (NARROW.matches) fe.style.height = root.scrollHeight + "px";
    else fe.style.removeProperty("height");
  }
  function syncNarrow() {
    document.body.classList.toggle("is-narrow", NARROW.matches);
    resizeFrame();
  }
  window.addEventListener("resize", syncNarrow);
  if (NARROW.addEventListener) NARROW.addEventListener("change", syncNarrow);
  if (window.ResizeObserver) new ResizeObserver(resizeFrame).observe(root);  // refit when content height changes

  // ── boot ────────────────────────────────────────────────────────────
  fetch("./corpus.json")
    .then(function (r) { return r.json(); })
    .then(function (docs) {
      FULL = { docs: docs, index: buildIndex(docs) };
      var smallDocs = docs.slice(0, 10);
      SMALL = { docs: smallDocs, index: buildIndex(smallDocs) };
      qStar = Math.max(2, Math.round(FULL.index.postings / (FULL.index.N - 1)));
      QMAX = Math.min(60, Math.max(24, qStar * 3));
      syncNarrow();
      renderMission();
    })
    .catch(function () {
      root.innerHTML = '<p style="padding:20px;color:var(--scan)">Couldn’t load the corpus. If you opened this file directly, serve the folder over http instead.</p>';
    });
})();
