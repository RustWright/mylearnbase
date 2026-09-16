/* hero-flock.js — the homepage's living background.
 *
 * A port of the flocking rules from this project's Rust core. Background and
 * rationale live in architecture.md § Interactive Demos; the comments below are
 * only the ones that guard a decision someone would otherwise undo.
 *
 * PROVENANCE, AND WHY IT MATTERS: every constant in P comes from config.py in
 * ~/life/masters_planning/projects/01_boids — a SEPARATE repo, not a submodule
 * here. Nothing can detect divergence: that repo does not exist on the build
 * machine, so there is no moment when both values are in scope. Retune a rule
 * there and this file is silently wrong. This comment is the only control.
 */
(function () {
  "use strict";

  var REF_W = 1600, REF_H = 1200;   // boids-core: WIDTH / HEIGHT
  var RADIUS = 8;                   // boids-core: RADIUS
  var POPULATION = 100;             // config.py: tuned for the reference world

  /* UNITS PER CSS PIXEL IS THE CONSTANT — not the world width. Fixing the world
   * at REF_W and deriving everything else looks equivalent and is not: it makes
   * units-per-pixel a function of viewport width (1.25 on a 1280px hero, 4.27 on
   * a 375px one), so a phone renders 3px boids with a 28px cohesion radius while
   * a laptop renders 12px boids with a 96px one. Same rules, different zoom.
   * Holding K fixed keeps boid size, every rule radius, and boids-per-pixel
   * identical at every width. */
  var K = 1.25;

  /* DENSITY, NOT COUNT. POPULATION is tuned for REF_W x REF_H; carrying the raw
   * number onto a differently-shaped world changes the density, and an over-dense
   * flock collapses into a packed lattice sitting at separation equilibrium —
   * static-looking, not flocking. */
  var DENSITY = POPULATION / (REF_W * REF_H);

  var P = {
    cohesionRadius: 120, cohesionGain: 0.06,
    separationRadius: 64, separationGain: 0.08,
    alignmentRadius: 72, alignmentGain: 0.5,
    speedClamp: 7.0,
    accelerationCap: 3.0,
    wallRepulsion: 0.4,
    wallMarginFrac: 0.05,
    predatorAvoidanceRadius: 80,
    predatorFearFactor: 0.2
  };

  function clampLength(x, y, max) {
    var len = Math.hypot(x, y);
    if (len <= max || len === 0) return [x, y];
    var k = max / len;
    return [x * k, y * k];
  }

  // Zero for a zero vector, matching Vec2::normalized() in the Rust core.
  // Separation depends on this: a coincident neighbour contributes nothing
  // instead of needing a random-direction guard.
  function norm(x, y) {
    var len = Math.hypot(x, y);
    return len === 0 ? [0, 0] : [x / len, y / len];
  }

  function mount(canvas, opts) {
    opts = opts || {};
    var ctx = canvas.getContext("2d", { alpha: true });
    var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    var densityScale = opts.density != null ? opts.density : 1;
    var count = opts.count || 0;              // 0 = derive from world area
    var opacity = opts.opacity != null ? opts.opacity : 0.2;

    var worldW = REF_W, worldH = 400;
    var dpr = 1;
    var boids = [];
    var predator = null;
    var running = false;
    var rafId = 0;

    // Deterministic spawn: the flock looks the same on every load, so a visual
    // change is a real change rather than reseeded noise.
    var seed = 0x9e3779b9;
    function rnd() {
      seed ^= seed << 13; seed ^= seed >>> 17; seed ^= seed << 5;
      return ((seed >>> 0) % 100000) / 100000;
    }

    function autoCount() {
      return Math.max(12, Math.round(DENSITY * densityScale * worldW * worldH));
    }

    function spawn() {
      boids = [];
      var n = count || autoCount();
      for (var i = 0; i < n; i++) {
        var a = rnd() * Math.PI * 2;
        var s = 2 + rnd() * 4;
        boids.push({
          x: RADIUS + rnd() * (worldW - 2 * RADIUS),
          y: RADIUS + rnd() * (worldH - 2 * RADIUS),
          vx: Math.cos(a) * s,
          vy: Math.sin(a) * s
        });
      }
    }

    function resize() {
      var r = canvas.getBoundingClientRect();
      if (r.width === 0 || r.height === 0) return;
      dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = Math.round(r.width * dpr);
      canvas.height = Math.round(r.height * dpr);

      var prevW = worldW, prevH = worldH;
      // The world IS the canvas, at the fixed zoom. Everything the simulation
      // owns is on screen.
      //
      // A floored world width (simulate 1600 wide, show a centred window) was
      // tried and is wrong: at 375px only ~28% of the world is visible, so what
      // you see depends on where the single flock has drifted — measured 35 of 47
      // boids in frame where uniform spread predicts 13. The hero would swing
      // between crowded and empty. Matching the world to the canvas cannot do
      // that, because there is no off-screen for the flock to hide in.
      //
      // The trade this accepts: rule radii are absolute lengths, so a narrow
      // world is small relative to cohesionRadius and the flock behaves more
      // globally there. That is the honest physics of a smaller tank, and it is
      // the half worth giving up — identical dynamics AND identical appearance
      // across a 3.5x width change is not available.
      worldH = r.height * K;
      worldW = r.width * K;

      if (!boids.length ||
          (!count && (Math.abs(worldH - prevH) / prevH > 0.2 ||
                      Math.abs(worldW - prevW) / prevW > 0.2))) spawn();
    }

    function wallForce(b) {
      var mx = P.wallMarginFrac * worldW;
      var my = P.wallMarginFrac * worldH;
      var left = Math.min(Math.max(b.x, RADIUS), mx);
      var right = Math.min(Math.max(worldW - b.x, RADIUS), mx);
      var top = Math.min(Math.max(b.y, RADIUS), my);
      var bottom = Math.min(Math.max(worldH - b.y, RADIUS), my);
      return [(mx - left) - (mx - right), (my - top) - (my - bottom)];
    }

    function step() {
      var n = boids.length;
      var snap = boids.slice();          // phase 1 reads only a frozen snapshot
      var nextVel = new Array(n);

      for (var i = 0; i < n; i++) {
        var me = snap[i];
        var cx = 0, cy = 0, cN = 0;
        var sx = 0, sy = 0, sN = 0;
        var ax = 0, ay = 0, aN = 0;

        for (var j = 0; j < n; j++) {
          if (j === i) continue;
          var o = snap[j];
          var dx = me.x - o.x, dy = me.y - o.y;
          var d = Math.hypot(dx, dy);
          if (d <= P.cohesionRadius) { cx += o.x; cy += o.y; cN++; }
          if (d <= P.separationRadius) {
            var u = norm(dx, dy);
            sx += u[0] * (P.separationRadius - d);
            sy += u[1] * (P.separationRadius - d);
            sN++;
          }
          if (d <= P.alignmentRadius) { ax += o.vx; ay += o.vy; aN++; }
        }

        var w = wallForce(me);
        var fx = w[0] * P.wallRepulsion, fy = w[1] * P.wallRepulsion;

        if (cN) { fx += (cx / cN - me.x) * P.cohesionGain; fy += (cy / cN - me.y) * P.cohesionGain; }
        if (sN) { fx += sx * P.separationGain; fy += sy * P.separationGain; }
        if (aN) {
          // The asymmetry is deliberate: the group velocity stays RAW while only
          // self-velocity is normalised. That is what makes alignment self-damp
          // where neighbours disagree — their velocities cancel, shrinking the
          // steering target. Normalising the group turns this into pure heading-
          // matching, which overshoots and jitters at this gain.
          var mv = norm(me.vx, me.vy);
          fx += (ax / aN - mv[0]) * P.alignmentGain;
          fy += (ay / aN - mv[1]) * P.alignmentGain;
        }

        if (predator) {
          var px = me.x - predator.x, py = me.y - predator.y;
          var pd = Math.hypot(px, py);
          if (pd <= P.predatorAvoidanceRadius) {
            var pu = norm(px, py);
            var mag = (P.predatorAvoidanceRadius - pd) * P.predatorFearFactor;
            fx += pu[0] * mag; fy += pu[1] * mag;
          }
        }

        // Cap acceleration, add to velocity, then cap speed. The order matters
        // and matches boids.py.
        var f = clampLength(fx, fy, P.accelerationCap);
        nextVel[i] = clampLength(me.vx + f[0], me.vy + f[1], P.speedClamp);
      }

      for (var k = 0; k < n; k++) {
        var b = boids[k];
        b.vx = nextVel[k][0]; b.vy = nextVel[k][1];
        b.x += b.vx; b.y += b.vy;
        b.x = Math.min(Math.max(b.x, RADIUS), worldW - RADIUS);
        b.y = Math.min(Math.max(b.y, RADIUS), worldH - RADIUS);
        if ((b.x + RADIUS >= worldW && b.vx > 0) || (b.x - RADIUS <= 0 && b.vx < 0)) b.vx = -b.vx;
        if ((b.y + RADIUS >= worldH && b.vy > 0) || (b.y - RADIUS <= 0 && b.vy < 0)) b.vy = -b.vy;
      }
    }

    function draw() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      // Read the live theme variable so light/dark flips for free. Serene defines
      // its custom properties on `body`, not `:root` — the dark toggle keys off a
      // class there — so reading from documentElement returns empty.
      var cs = getComputedStyle(document.body);
      ctx.fillStyle = cs.getPropertyValue("--primary-color").trim() || "#5871a2";
      ctx.globalAlpha = opacity;

      var s = dpr / K;                  // world units -> device pixels
      var L = RADIUS * 1.5 * s, W = RADIUS * 0.75 * s;
      for (var i = 0; i < boids.length; i++) {
        var b = boids[i];
        var x = b.x * s, y = b.y * s;
        var h = norm(b.vx, b.vy);
        if (h[0] === 0 && h[1] === 0) h = [1, 0];
        ctx.beginPath();
        ctx.moveTo(x + h[0] * L, y + h[1] * L);
        ctx.lineTo(x - h[0] * L - h[1] * W, y - h[1] * L + h[0] * W);
        ctx.lineTo(x - h[0] * L + h[1] * W, y - h[1] * L - h[0] * W);
        ctx.closePath();
        ctx.fill();
      }
      ctx.globalAlpha = 1;
    }

    function frame() {
      if (!running) return;
      step();
      draw();
      rafId = requestAnimationFrame(frame);
    }

    function start() { if (!running && !reduced) { running = true; rafId = requestAnimationFrame(frame); } }
    function stop() { running = false; cancelAnimationFrame(rafId); }

    resize();
    window.addEventListener("resize", function () { resize(); draw(); });

    if (reduced) {
      for (var w = 0; w < 240; w++) step();   // one settled frame, no loop
      draw();
    } else {
      document.addEventListener("visibilitychange", function () {
        document.hidden ? stop() : start();
      });
      if ("IntersectionObserver" in window) {
        new IntersectionObserver(function (es) {
          es[0].isIntersecting ? start() : stop();
        }, { threshold: 0 }).observe(canvas);
      } else {
        start();
      }

      canvas.addEventListener("pointermove", function (e) {
        var r = canvas.getBoundingClientRect();
        predator = { x: (e.clientX - r.left) * K, y: (e.clientY - r.top) * K };
      });
      canvas.addEventListener("pointerleave", function () { predator = null; });
    }

    return {
      setCount: function (c) { count = c; spawn(); draw(); },
      setDensity: function (d) { densityScale = d; count = 0; spawn(); draw(); },
      setOpacity: function (o) { opacity = o; draw(); },
      stats: function () {
        var r = canvas.getBoundingClientRect();
        var cx = 0, cy = 0;
        for (var i = 0; i < boids.length; i++) {
          cx += boids[i].x; cy += boids[i].y;
        }
        var n = boids.length || 1;
        return {
          boids: boids.length,
          world: [Math.round(worldW), Math.round(worldH)],
          unitsPerPixel: K,
          // The world matches the canvas, so every boid is on screen — this is
          // the number that must hold steady across viewport widths.
          perMegapixel: Math.round(boids.length / (r.width * r.height) * 1e6),
          centroid: [Math.round(cx / n), Math.round(cy / n)],
          spread: Math.round(boids.reduce(function (s, b) {
            return s + Math.hypot(b.x - cx / n, b.y - cy / n);
          }, 0) / n)
        };
      },
      start: start,
      stop: stop
    };
  }

  window.HeroFlock = { mount: mount };
})();
