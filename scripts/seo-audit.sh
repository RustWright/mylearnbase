#!/usr/bin/env bash
#
# seo-audit.sh — one-command objective SEO/AEO audit for mylearnbase.
#
# Bundles every check that can be run WITHOUT a public deploy:
#   1. zola build (must be clean)
#   2. zola check (internal links)
#   3. Root resources present + correct: sitemap.xml, robots.txt (custom + prod
#      Sitemap line), llms.txt
#   4. JSON-LD on every page: parses as JSON + carries an expected @type
#      (BlogPosting + BreadcrumbList on leaf posts, WebSite on home/sections)
#   5. <head> surface: canonical + OpenGraph + Twitter present on a sample post
#   6. Lighthouse SEO category score (needs google-chrome + npx; auto-skipped if
#      either is missing) — run against `zola serve` so canonical matches host
#
# With --online it ALSO POSTs rendered pages to validator.schema.org and asserts
# 0 errors. Offline by default so it works in CI / on a plane.
#
# Usage:  scripts/seo-audit.sh [--online]
# Exit:   0 = all checks passed, 1 = at least one failed.
#
# What this CANNOT check (needs a public URL → Phase 4, by design):
#   - Google Rich Results Test (rich-result eligibility / author recognition)
#   - Search Console / Bing indexing & coverage
#   - ahrefs / Screaming Frog site-wide crawl
#
set -uo pipefail
cd "$(dirname "$0")/.."   # repo root (script lives in scripts/)

ONLINE=0
[[ "${1:-}" == "--online" ]] && ONLINE=1

FAIL=0
section(){ printf '\n\033[1m== %s ==\033[0m\n' "$1"; }
ok(){   printf '  \033[32m[PASS]\033[0m %s\n' "$1"; }
bad(){  printf '  \033[31m[FAIL]\033[0m %s\n' "$1"; FAIL=1; }
skip(){ printf '  \033[33m[SKIP]\033[0m %s\n' "$1"; }
info(){ printf '  \033[36m[ .. ]\033[0m %s\n' "$1"; }

# ── 1. Build ─────────────────────────────────────────────────────────────────
section "Build"
if zola build >/tmp/seo_build.log 2>&1; then
  ok "zola build clean — $(grep -oE 'Creating [0-9]+ pages.*' /tmp/seo_build.log)"
else
  bad "zola build failed:"; tail -8 /tmp/seo_build.log; exit 1
fi

# ── 2. Internal link check ───────────────────────────────────────────────────
section "Link check"
if zola check --skip-external-links >/tmp/seo_check.log 2>&1; then
  ok "zola check clean (internal links)"
else
  bad "zola check reported problems:"; tail -8 /tmp/seo_check.log
fi

# ── 3. Root resources ────────────────────────────────────────────────────────
section "Root resources (sitemap / robots / llms)"
[[ -s public/sitemap.xml ]] && ok "sitemap.xml present" || bad "sitemap.xml missing"
if [[ -s public/robots.txt ]]; then
  grep -q "Sitemap: https://mylearnbase.com/sitemap.xml" public/robots.txt \
    && ok "robots.txt present + production Sitemap line" \
    || bad "robots.txt present but Sitemap line wrong/missing"
  grep -q "GPTBot"  public/robots.txt && ok "robots.txt has AI-crawler stance" \
    || info "robots.txt has no explicit AI-crawler stance"
else
  bad "robots.txt missing"
fi
[[ -s public/llms.txt ]] && ok "llms.txt present" || bad "llms.txt missing"

# ── 4. JSON-LD validity across the whole build ───────────────────────────────
section "JSON-LD (parse + @type) — all pages"
read_json=$(python3 - <<'PY'
import re, json, glob
blocks=bad=0; bp=ws=bc=0
VALID={"BlogPosting","WebSite","BreadcrumbList"}  # BreadcrumbList added Cycle 4
for path in glob.glob("public/**/index.html", recursive=True):
    html=open(path,encoding='utf-8').read()
    for raw in re.findall(r'<script type=[^>]*ld\+json[^>]*>(.*?)</script>',html,re.DOTALL):
        blocks+=1
        try:
            t=json.loads(raw).get("@type")
            bp+=t=="BlogPosting"; ws+=t=="WebSite"; bc+=t=="BreadcrumbList"
            if t not in VALID: bad+=1
        except Exception: bad+=1
print(blocks,bad,bp,ws,bc)
PY
)
set -- $read_json; BLOCKS=$1; LDBAD=$2; BP=$3; WS=$4; BC=$5
if [[ "$LDBAD" -eq 0 && "$BLOCKS" -gt 0 && "$BP" -gt 0 && "$WS" -gt 0 ]]; then
  ok "$BLOCKS JSON-LD blocks valid (BlogPosting=$BP, WebSite=$WS, BreadcrumbList=$BC)"
else
  bad "JSON-LD problem (blocks=$BLOCKS invalid=$LDBAD BlogPosting=$BP WebSite=$WS BreadcrumbList=$BC)"
fi

# ── 5. <head> social surface on a sample post ────────────────────────────────
section "Head surface (canonical / OpenGraph / Twitter) on a sample post"
SAMPLE=$(python3 - <<'PY'
import re, glob
for path in sorted(glob.glob("public/posts/**/index.html", recursive=True)):
    html=open(path,encoding='utf-8').read()
    if 'BlogPosting' in html:
        print(path); break
PY
)
if [[ -n "$SAMPLE" ]]; then
  info "sample: $SAMPLE"
  grep -q 'rel=canonical'     "$SAMPLE" && ok "canonical present"      || bad "canonical missing"
  grep -q 'property=og:title' "$SAMPLE" && ok "OpenGraph present"      || bad "OpenGraph missing"
  grep -q 'name=twitter:card' "$SAMPLE" && ok "Twitter card present"   || bad "Twitter card missing"
else
  bad "no BlogPosting post found to sample"
fi

# ── 6. Lighthouse SEO ────────────────────────────────────────────────────────
section "Lighthouse SEO"
if ! command -v google-chrome >/dev/null || ! command -v npx >/dev/null; then
  skip "lighthouse needs google-chrome + npx (one is missing)"
else
  PORT=8979
  # NB: do NOT pass --base-url here. `zola serve --port N` already rewrites
  # base_url to http://127.0.0.1:N; passing --base-url too doubles the port
  # (…:N:N), which breaks canonical/crawlable-anchors/robots-txt audits.
  zola serve --interface 127.0.0.1 --port "$PORT" >/tmp/seo_serve.log 2>&1 &
  SERVE_PID=$!
  trap '[[ -n "${SERVE_PID:-}" ]] && kill "$SERVE_PID" 2>/dev/null' EXIT
  # wait for readiness (<=20s)
  for _ in $(seq 1 40); do
    curl -sf -o /dev/null "http://127.0.0.1:$PORT/" && break || sleep 0.5
  done
  POSTURL="http://127.0.0.1:$PORT/${SAMPLE#public/}"; POSTURL="${POSTURL%index.html}"
  for url in "http://127.0.0.1:$PORT/" "$POSTURL"; do
    export CHROME_PATH=/usr/bin/google-chrome
    if timeout 280 npx --yes lighthouse "$url" --only-categories=seo --quiet \
         --chrome-flags="--headless --no-sandbox --disable-gpu --hide-scrollbars" \
         --output=json --output-path=/tmp/seo_lh.json >/dev/null 2>&1; then
      SCORE=$(python3 -c "import json;print(round(json.load(open('/tmp/seo_lh.json'))['categories']['seo']['score']*100))")
      [[ "$SCORE" -ge 90 ]] && ok "SEO $SCORE/100 — $url" || bad "SEO only $SCORE/100 — $url"
    else
      bad "lighthouse run failed for $url"
    fi
  done
  kill "$SERVE_PID" 2>/dev/null; SERVE_PID=""
fi

# ── 7. Optional: live schema.org validator ───────────────────────────────────
if [[ "$ONLINE" -eq 1 ]]; then
  section "Schema.org validator (--online)"
  validate_file(){
    local f="$1" label="$2"
    curl -sS --max-time 40 'https://validator.schema.org/validate' \
      --data-urlencode "html@${f}" -H 'Accept: application/json' -o /tmp/seo_so.json 2>/dev/null
    python3 - "$label" <<'PY'
import json, sys
raw=open("/tmp/seo_so.json",encoding='utf-8').read()
if raw.startswith(")]}'"): raw=raw.split("\n",1)[1]
d=json.loads(raw)
e,w=d.get("totalNumErrors",-1),d.get("totalNumWarnings",-1)
print(f"{sys.argv[1]}\t{e}\t{w}")
PY
  }
  while IFS=$'\t' read -r label e w; do
    [[ "$e" == "0" ]] && ok "$label — $e errors, $w warnings" \
                      || bad "$label — $e errors, $w warnings"
  done < <(
    validate_file "public/index.html" "home (WebSite)"
    [[ -n "$SAMPLE" ]] && validate_file "$SAMPLE" "post (BlogPosting)"
  )
fi

# ── Summary ──────────────────────────────────────────────────────────────────
section "Result"
if [[ "$FAIL" -eq 0 ]]; then
  printf '  \033[1;32mALL CHECKS PASSED\033[0m\n'; exit 0
else
  printf '  \033[1;31mSOME CHECKS FAILED\033[0m (see [FAIL] lines above)\n'; exit 1
fi
