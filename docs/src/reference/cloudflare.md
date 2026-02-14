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
curl -sL https://github.com/getzola/zola/releases/download/v0.22.1/zola-v0.22.1-x86_64-unknown-linux-gnu.tar.gz | tar xz && ./zola build
```

Cloudflare Pages no longer pre-installs Zola, so the build command downloads it first. This adds a few seconds but is reliable.

**To update Zola version:** Change the version number in the URL (both the directory name and the tarball name).

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
1. Pin to the known-working version in the build command (currently v0.22.1)
2. Test the new version locally with `zola build` before updating the build command
3. Update the version in the build command only after local verification

## Monitoring

Cloudflare Pages dashboard shows:
- Build logs (stdout/stderr from the build command)
- Deploy history with rollback capability
- Bandwidth and request metrics

No additional monitoring is configured.
