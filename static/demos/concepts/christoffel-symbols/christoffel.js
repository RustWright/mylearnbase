/* Shared logic for the three Christoffel demos (build/, predict/, check/).
 *
 * The question all three answer: given a mass matrix M(q), which entries of
 * dM/dq does the Christoffel recipe combine into each entry of C(q, qdot)?
 *
 *   c_ijk = 1/2 ( dM_kj/dq_i + dM_ki/dq_j - dM_ij/dq_k ),   C_kj = sum_i c_ijk qdot_i
 *
 * Convention: k is the EQUATION (row of C), as in Spong, Hutchinson and
 * Vidyasagar. Books order the three slots differently, which is half of why the
 * indices are confusing; every demo states this one.
 *
 * Plain globals, loaded before each demo's own script. KaTeX must already be on
 * the page; \htmlClass needs `trust`, which is safe because every string
 * rendered here is authored in this file, never taken from input.
 */

/* ---------- colored-index LaTeX helpers ---------- */
const I = s => `\\htmlClass{xi}{${s}}`, J = s => `\\htmlClass{xj}{${s}}`, K = s => `\\htmlClass{xk}{${s}}`;
const KX = { throwOnError: false, trust: true, strict: false };
const tex = (el, s, display = true) => katex.render(s, el, { ...KX, displayMode: display });
const ktex = s => katex.renderToString(s, KX);
const renderMathIn = el => { el.innerHTML = el.innerHTML.replace(/\$([^$]+)\$/g, (_, s) => katex.renderToString(s, KX)); };
const $ = id => document.getElementById(id);
const wait = ms => new Promise(r => setTimeout(r, ms));
const REDUCED = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

/* ---------- systems ----------
   dM[c][a][b] = coefficient of `atom` in dM_ab/dq_c (0-indexed). Every nonzero
   partial in these two systems is a multiple of ONE atom, so every sum below
   stays exact and prints as a clean multiple of it. A third system would need
   that property too, or symbolic arithmetic. */
const SYS = {
  polar: {
    name: "Puck on a table (polar coordinates)",
    q: ["r", "\\varphi"], qd: ["\\dot r", "\\dot\\varphi"],
    T: "T = \\tfrac12 m(\\dot r^2 + r^2\\dot\\varphi^2)",
    M: "\\begin{bmatrix} m & 0 \\\\ 0 & m r^2 \\end{bmatrix}",
    atom: "m r",
    Mcell: [["m", "0"], ["0", "m r^2"]],
    eom: ["m\\ddot r \\CT{- m r\\,\\dot\\varphi^2} = Q_1",
          "m r^2\\ddot\\varphi \\CT{+ 2 m r\\,\\dot r\\dot\\varphi} = Q_2"],
    dM: [ [[0,0],[0,2]],  [[0,0],[0,0]] ],
    p: { m: 1 },
    Mnum: (q, p) => [[p.m, 0], [0, p.m * q[0] * q[0]]],
    atomNum: (q, p) => p.m * q[0],
    sliders: [["r", 0.2, 2, 1], ["φ", -3.14, 3.14, 0.5]], dots: ["ṙ", "φ̇"],
  },
  cart: {
    name: "Cart–pendulum",
    q: ["x", "\\theta"], qd: ["\\dot x", "\\dot\\theta"],
    T: "T = \\tfrac12(m_c+m_p)\\dot x^2 + m_p l\\cos\\theta\\,\\dot x\\dot\\theta + \\tfrac12 m_p l^2\\dot\\theta^2",
    M: "\\begin{bmatrix} m_c+m_p & m_p l\\cos\\theta \\\\ m_p l\\cos\\theta & m_p l^2 \\end{bmatrix}",
    atom: "m_p l\\sin\\theta",
    Mcell: [["m_c+m_p", "m_p l\\cos\\theta"], ["m_p l\\cos\\theta", "m_p l^2"]],
    eom: ["(m_c+m_p)\\ddot x + m_p l\\cos\\theta\\,\\ddot\\theta \\CT{- m_p l\\sin\\theta\\,\\dot\\theta^2} = Q_1",
          "m_p l\\cos\\theta\\,\\ddot x + m_p l^2\\ddot\\theta + m_p g l\\sin\\theta = Q_2"],
    dM: [ [[0,0],[0,0]],  [[0,-1],[-1,0]] ],
    p: { mc: 1, mp: 0.5, l: 1 },
    Mnum: (q, p) => [[p.mc + p.mp, p.mp * p.l * Math.cos(q[1])], [p.mp * p.l * Math.cos(q[1]), p.mp * p.l * p.l]],
    atomNum: (q, p) => p.mp * p.l * Math.sin(q[1]),
    sliders: [["x", -2, 2, 0], ["θ", -3.14, 3.14, 0.8]], dots: ["ẋ", "θ̇"],
  },
};

/* ---------- the recipe ---------- */
function cijk(s, i, j, k) { const d = SYS[s].dM; i--; j--; k--; return 0.5 * (d[i][k][j] + d[j][k][i] - d[k][i][j]); }
/* the three partials the recipe combines, as atom coefficients */
function terms(s, i, j, k) { const d = SYS[s].dM; return [d[i-1][k-1][j-1], d[j-1][k-1][i-1], d[k-1][i-1][j-1]]; }
/* [row of M, column of M, differentiate-by] that each term reads from */
const slotsFor = (i, j, k) => [[k, j, i], [k, i, j], [i, j, k]];

/* ---------- formatting ---------- */
function coefTex(c) {
  if (c === 1) return ""; if (c === -1) return "-";
  const r = Math.round(c * 2);
  if (r % 2 !== 0) return (r < 0 ? "-" : "") + `\\tfrac{${Math.abs(r)}}{2}`;
  return String(c);
}
const term = (c, atom) => c === 0 ? "0" : coefTex(c) + atom;
const paren = (c, atom) => c < 0 ? `(${term(c, atom)})` : term(c, atom);
function combo(pairs, atom) {
  const nz = pairs.filter(p => p[0] !== 0);
  if (!nz.length) return "0";
  if (nz.length === 1) return coefTex(nz[0][0]) + atom + "\\," + nz[0][1];
  if (nz.every(p => p[0] === nz[0][0])) return coefTex(nz[0][0]) + atom + "\\left(" + nz.map(p => p[1]).join("+") + "\\right)";
  return atom + "\\left(" + nz.map((p, n) => (n && p[0] > 0 ? "+" : "") + coefTex(p[0]) + p[1]).join("") + "\\right)";
}
const termLabel = n => n === 2 ? "−3" : "+" + (n + 1);
const termGeneric = n => [
  `\\partial M_{${K("k")}${J("j")}}/\\partial q_{${I("i")}}`,
  `\\partial M_{${K("k")}${I("i")}}/\\partial q_{${J("j")}}`,
  `\\partial M_{${I("i")}${J("j")}}/\\partial q_{${K("k")}}`][n];
const c3 = (i, j, k) => `c_{${I(i)}${J(j)}${K(k)}}`;
const RECIPE = `c_{${I("i")}${J("j")}${K("k")}} = \\tfrac12\\Big(
  \\underbrace{\\frac{\\partial M_{${K("k")}${J("j")}}}{\\partial q_{${I("i")}}}}_{+1} +
  \\underbrace{\\frac{\\partial M_{${K("k")}${I("i")}}}{\\partial q_{${J("j")}}}}_{+2} -
  \\underbrace{\\frac{\\partial M_{${I("i")}${J("j")}}}{\\partial q_{${K("k")}}}}_{-3}\\Big)`;

/* entry C_kj and row k of C qdot, as LaTeX */
function Ckj(s, k, j) { const S = SYS[s]; return combo([1, 2].map(i => [cijk(s, i, j, k), S.qd[i-1]]), S.atom); }
function Cqk(s, k) {
  const S = SYS[s], c = (i, j) => cijk(s, i, j, k);
  return combo([[c(1,1), S.qd[0] + "^2"], [c(1,2) + c(2,1), S.qd[0] + S.qd[1]], [c(2,2), S.qd[1] + "^2"]], S.atom);
}

/* ---------- system card ----------
   Every demo opens on the system it is using, because each one must make sense
   arriving cold from its standalone URL: name, M(q), and the two equations of
   motion with their velocity-times-velocity terms highlighted. */
function renderSystem(el, s) {
  const S = SYS[s];
  el.innerHTML = `<b style="color:var(--ink)">${S.name}</b><span class="mtex"></span>
    <div class="eomwrap"><span class="eom"></span>
      <div class="note">Highlighted: the velocity-times-velocity terms. These are exactly what $C\\dot q$ has to produce.</div></div>`;
  tex(el.querySelector(".mtex"), `M(q) = ${S.M},\\ \\ q = \\begin{bmatrix} ${S.q[0]} \\\\ ${S.q[1]} \\end{bmatrix}`, false);
  tex(el.querySelector(".eom"), `\\begin{aligned}
      &\\text{equation } ${K(1)}\\ (\\text{for } q_1 = ${S.q[0]}): && ${S.eom[0].replace(/\\CT\{/g, "\\htmlClass{cterm}{")}\\\\
      &\\text{equation } ${K(2)}\\ (\\text{for } q_2 = ${S.q[1]}): && ${S.eom[1].replace(/\\CT\{/g, "\\htmlClass{cterm}{")}
    \\end{aligned}`, false);
  renderMathIn(el.querySelector(".note"));
}

/* ---------- objective stepper ----------
   A demo's steps, one at a time, in one card: title, progress dots, prev/next.
   Each step's `enter(step)` decides what is on screen, so panels appear only
   when the step that uses them arrives. */
function stepper(steps, enter) {
  const st = { n: 0 };
  const go = n => {
    st.n = Math.max(0, Math.min(steps.length - 1, n));
    const s = steps[st.n];
    $("otitle").textContent = s.title;
    $("dots").innerHTML = steps.length > 1
      ? steps.map((_, m) => `<span class="${m === st.n ? "cur" : m < st.n ? "done" : ""}"></span>`).join("") : "";
    $("otext").innerHTML = s.text; renderMathIn($("otext"));
    $("prev").disabled = st.n === 0; $("next").disabled = st.n === steps.length - 1;
    $("next").classList.remove("ready");
    $("prompt").textContent = ""; $("prompt").className = "";
    enter(s);
  };
  $("prev").onclick = () => go(st.n - 1);
  $("next").onclick = () => go(st.n + 1);
  if (steps.length < 2) { $("prev").classList.add("hidden"); $("next").classList.add("hidden"); }
  return { go, nudge: () => { if (st.n < steps.length - 1) $("next").classList.add("ready"); } };
}
/* ---------- fit the host iframe ----------
   Embedded in a post, size the iframe to the content so the PAGE scrolls past
   the demo instead of trapping it behind a nested scrollbar. Always on, not
   just on mobile (cf. how-search-works): these demos change height between
   steps at every width, as panels appear and the workbench fills. Same-origin,
   so frameElement is reachable; standalone it is null and this does nothing.
   The shortcode's height= is only the pre-script fallback. */
(function fitFrame() {
  let fe = null;
  try { fe = window.frameElement; } catch (e) { return; }   // cross-origin guard
  if (!fe || !window.ResizeObserver) return;
  const fit = () => {
    const main = document.querySelector("main");
    // + the frame's own borders (the shortcode draws a 1px one), which the
    // height property includes and the content area does not.
    const chrome = fe.offsetHeight - fe.clientHeight;
    if (main) fe.style.height = Math.ceil(main.getBoundingClientRect().height) + chrome + "px";
  };
  document.addEventListener("DOMContentLoaded", () => {
    const main = document.querySelector("main");
    if (main) new ResizeObserver(fit).observe(main);
  });
})();

function setPrompt(html, cls) { const p = $("prompt"); p.className = cls || ""; p.innerHTML = html; renderMathIn(p); }
function enterAnim(el) { el.classList.remove("enter"); void el.offsetWidth; el.classList.add("enter"); }
