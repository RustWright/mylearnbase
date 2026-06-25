# Cloudflare Deployment

## Setup Summary

The site is deployed on Cloudflare Pages, connected to the GitHub repository. Every push to `main` triggers a rebuild and deploy.

## Build Configuration

| Setting | Value |
|---------|-------|
| **Framework preset** | None (custom) |
| **Production branch** | `main` |
| **Build command** | See below |
| **Build output directory** | `public` |

### Build Command

```bash
bash build.sh
```

`build.sh` (repo root) owns the full pipeline: it downloads Zola if it isn't already
present, runs `zola build`, then indexes the rendered HTML with Pagefind
(`npx pagefind`), which writes the search index into `public/pagefind/`. Cloudflare's
build image already includes Node, so `npx` works with no extra setup. A plain
`zola build` would skip the Pagefind step, so the build command must call the script.

**To update the Zola or Pagefind version:** edit `ZOLA_VERSION` / `PAGEFIND_VERSION` at
the top of `build.sh` (no dashboard change needed). Test locally with `bash build.sh`
before pushing.

## Custom Domain

| Setting | Value |
|---------|-------|
| **Domain** | `mylearnbase.com` |
| **DNS provider** | Cloudflare (migrated from Porkbun) |
| **HTTPS** | Automatic via Cloudflare |

The domain's nameservers were migrated to Cloudflare to enable tight integration with Pages. HTTPS certificates are provisioned and renewed automatically.

## Known Issues

### CSS Missing on Preview URLs

Cloudflare generates preview URLs for branches (e.g., `abc123.mylearnbase.pages.dev`). These may show broken styling because:

1. `zola.toml` sets `base_url = "https://mylearnbase.com"`
2. Zola generates absolute URLs for CSS based on `base_url`
3. The preview URL (`*.pages.dev`) doesn't match, so CSS paths break

**Workaround:** Use `zola serve` locally for visual verification instead of preview URLs.

### Build Failures After Zola Updates

If a new Zola version introduces breaking changes:
1. Pin to the known-working version in `build.sh` (currently Zola v0.22.1, Pagefind v1.5.2)
2. Test the new version locally with `bash build.sh` before pushing
3. Update the version in `build.sh` only after local verification

## Monitoring

Cloudflare Pages dashboard shows:
- Build logs (stdout/stderr from the build command)
- Deploy history with rollback capability
- Bandwidth and request metrics

No additional monitoring is configured.
