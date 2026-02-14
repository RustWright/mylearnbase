# Deployment

The site deploys automatically to Cloudflare Pages on every push to the `main` branch.

## How It Works

```
Push to GitHub → Cloudflare detects change → Runs build command → Deploys to CDN
```

No manual deployment steps needed.

## Cloudflare Pages Configuration

| Setting | Value |
|---------|-------|
| **Production branch** | `main` |
| **Build command** | `curl -sL https://github.com/getzola/zola/releases/download/v0.22.1/zola-v0.22.1-x86_64-unknown-linux-gnu.tar.gz \| tar xz && ./zola build` |
| **Build output directory** | `public` |
| **Custom domain** | `mylearnbase.com` |

> **Why the custom build command?** Cloudflare Pages no longer pre-installs Zola. The build command downloads Zola on each build, then runs `zola build`. This adds a few seconds but is reliable.

## Domain Setup

The domain `mylearnbase.com` was migrated to Cloudflare's nameservers (from Porkbun) and configured as a custom domain in the Cloudflare Pages dashboard. HTTPS is handled automatically by Cloudflare.

## Known Issue: Preview URLs

Cloudflare Pages generates preview URLs for non-production branches (e.g., `abc123.mylearnbase.pages.dev`). These previews may have broken CSS because Zola generates URLs based on `base_url` in `zola.toml`, which is set to `https://mylearnbase.com`. The preview URL doesn't match, so absolute paths to CSS files break.

**Workaround:** Test locally with `zola serve` instead of relying on preview URLs for visual verification.
