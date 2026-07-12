/* ───────────────────────────────────────────────────────────────────────
   "How SVGs work" · demo 2 "read the path" — vanilla, self-contained.

   The logo's own path is modelled as a list of commands. render() rebuilds the
   SVG stage from that model each frame; renderD() rebuilds the tokenised `d`
   string. A stepper walks the commands; on a cubic (C) the two control points
   become draggable. Pointer capture lives on the persistent <svg> root (not the
   dot, which is recreated every render), so a drag survives the re-render.
   ─────────────────────────────────────────────────────────────────────── */
(function () {
  "use strict";

  var $ = function (id) { return document.getElementById(id); };
  var stage = $("stage"), dstr = $("dstr");

  // the logo path, from static/img/logo.svg, as an editable model
  function makeModel() {
    return [
      { type: "M", pt: [50, 6] },
      { type: "C", c1: [53, 32], c2: [62, 43], pt: [80, 46] },
      { type: "C", c1: [62, 49], c2: [53, 60], pt: [50, 70] },
      { type: "C", c1: [47, 60], c2: [38, 49], pt: [20, 46] },
      { type: "C", c1: [38, 43], c2: [47, 32], pt: [50, 6] },
      { type: "Z" }
    ];
  }
  var cmds = makeModel();

  // a friendly name for where each command lands on this particular logo
  var WHERE = ["the top point", "out to the right point", "down to the bottom point",
               "over to the left point", "back up to the top point", ""];

  var step = 0, drag = null;

  // ── helpers ──────────────────────────────────────────────────────────────
  function fmt(p) { return Math.round(p[0]) + " " + Math.round(p[1]); }
  function anchorAt(i) {
    if (i < 0) return cmds[0].pt;
    var c = cmds[i];
    return c.type === "Z" ? cmds[0].pt : c.pt;
  }
  function buildD() {
    return cmds.map(function (c) {
      if (c.type === "M") return "M" + fmt(c.pt);
      if (c.type === "C") return "C" + fmt(c.c1) + " " + fmt(c.c2) + " " + fmt(c.pt);
      return "Z";
    }).join(" ");
  }
  function segmentD(i) {
    var c = cmds[i];
    if (c.type === "M") return "";
    var p0 = anchorAt(i - 1);
    if (c.type === "C") return "M" + fmt(p0) + " C" + fmt(c.c1) + " " + fmt(c.c2) + " " + fmt(c.pt);
    return "M" + fmt(p0) + " L" + fmt(cmds[0].pt);   // Z
  }

  // ── draw the stage from the model ──────────────────────────────────────────
  function render() {
    var d = buildD(), p = [];
    for (var i = 10; i < 100; i += 10) {
      p.push('<line class="grid" x1="' + i + '" y1="0" x2="' + i + '" y2="100"/>');
      p.push('<line class="grid" x1="0" y1="' + i + '" x2="100" y2="' + i + '"/>');
    }
    p.push('<path class="fillprev" d="' + d + '"/>');
    p.push('<path class="outline" d="' + d + '"/>');
    var seg = segmentD(step);
    if (seg) p.push('<path class="seg" d="' + seg + '"/>');

    cmds.forEach(function (c, i) {
      if (c.type === "Z") return;
      p.push('<circle class="anchor' + (i === step ? " cur" : "") +
             '" cx="' + c.pt[0] + '" cy="' + c.pt[1] + '" r="1.7"/>');
    });

    var cur = cmds[step];
    if (cur.type === "C") {
      var p0 = anchorAt(step - 1);
      p.push(hline(p0, cur.c1));
      p.push(hline(cur.pt, cur.c2));
      p.push(handle(step, "c1", cur.c1));
      p.push(handle(step, "c2", cur.c2));
    }
    stage.innerHTML = p.join("");
  }
  function hline(a, b) {
    return '<line class="hline" x1="' + a[0] + '" y1="' + a[1] +
           '" x2="' + b[0] + '" y2="' + b[1] + '"/>';
  }
  function handle(i, w, pt) {
    return '<circle class="grab" data-cmd="' + i + '" data-which="' + w +
           '" cx="' + pt[0] + '" cy="' + pt[1] + '" r="6"/>' +
           '<circle class="ctrl" cx="' + pt[0] + '" cy="' + pt[1] + '" r="2.4"/>';
  }

  // ── the d string + the per-command explanation ─────────────────────────────
  function renderD() {
    dstr.innerHTML = cmds.map(function (c, i) {
      var t = c.type === "M" ? "M" + fmt(c.pt)
            : c.type === "C" ? "C" + fmt(c.c1) + " " + fmt(c.c2) + " " + fmt(c.pt)
            : "Z";
      return '<span class="tok' + (i === step ? " on" : "") +
             '" data-step="' + i + '">' + t + "</span>";
    }).join(" ");
  }
  function explain() {
    var c = cmds[step], t;
    if (c.type === "M") {
      t = '<span class="cmd">M</span> &mdash; <b>M</b>ove the pen to (' + fmt(c.pt) +
          '). The pen is up, so nothing is drawn; this is just where the outline ' +
          'starts, at ' + WHERE[step] + '.';
    } else if (c.type === "Z") {
      t = '<span class="cmd">Z</span> &mdash; <b>Z</b> closes the path: a straight ' +
          'line from the last point back to the start, sealing the sparkle.';
    } else {
      t = '<span class="cmd">C</span> &mdash; a <b>C</b>ubic curve ' + WHERE[step] +
          ' at (' + fmt(c.pt) + '). The two hollow dots are <b>control points</b> ' +
          '&mdash; magnets that bend the line without ever sitting on it. Drag them.';
    }
    $("expl").innerHTML = t;
  }

  function draw() {
    render(); renderD(); explain();
    $("stepcount").textContent = "command " + (step + 1) + " / " + cmds.length;
    $("prev").disabled = step === 0;
    $("next").disabled = step === cmds.length - 1;
  }

  // ── dragging control points ────────────────────────────────────────────────
  function toSvg(e) {
    var r = stage.getBoundingClientRect();
    var x = (e.clientX - r.left) / r.width * 100;
    var y = (e.clientY - r.top) / r.height * 100;
    return [Math.max(0, Math.min(100, x)), Math.max(0, Math.min(100, y))];
  }
  stage.addEventListener("pointerdown", function (e) {
    var g = e.target.closest && e.target.closest(".grab");
    if (!g) return;
    drag = { cmd: +g.getAttribute("data-cmd"), which: g.getAttribute("data-which") };
    stage.classList.add("dragging");
    stage.setPointerCapture(e.pointerId);
  });
  stage.addEventListener("pointermove", function (e) {
    if (!drag) return;
    cmds[drag.cmd][drag.which] = toSvg(e);
    render(); renderD();
  });
  function endDrag(e) {
    if (!drag) return;
    drag = null;
    stage.classList.remove("dragging");
    try { stage.releasePointerCapture(e.pointerId); } catch (_) {}
  }
  stage.addEventListener("pointerup", endDrag);
  stage.addEventListener("pointercancel", endDrag);

  // ── stepping ───────────────────────────────────────────────────────────────
  function go(to) { step = Math.max(0, Math.min(cmds.length - 1, to)); draw(); }
  $("prev").addEventListener("click", function () { go(step - 1); });
  $("next").addEventListener("click", function () { go(step + 1); });
  $("reset").addEventListener("click", function () { cmds = makeModel(); draw(); });
  dstr.addEventListener("click", function (e) {
    var tok = e.target.closest(".tok");
    if (tok) go(+tok.getAttribute("data-step"));
  });

  // narrow-screen note
  var narrow = window.matchMedia("(max-width: 640px)");
  function syncNarrow() { document.body.classList.toggle("is-narrow", narrow.matches); }
  narrow.addEventListener("change", syncNarrow);
  syncNarrow();

  draw();
})();
