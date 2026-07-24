# miska.blog

Source for the static site served at [miska.blog](http://miska.blog), the origin behind the `cdn.miska.blog` CDN resource used for Gcore CDN/FastEdge testing.

## Structure

```
index.html          homepage (post list)
about.html
posts/               individual post pages
css/style.css
static/               test path used for CDN/FastEdge experiments
api/                  test path (data.json) used for CDN/FastEdge experiments
images/               test images used for CDN/FastEdge experiments
```

`static/`, `api/`, and `images/` are precondition test paths from the CDN/FastEdge setup guide (`Onboarding/CDN-FastEdge-Setup-Guide.md` in the gcore-pm-framework project) — leave them in place, Part 3 FastEdge apps route through them.

## Local preview

No build step — plain HTML/CSS. Open `index.html` directly, or serve it locally:

```sh
python3 -m http.server 8000
```

then visit `http://localhost:8000`.

## Deploy

```sh
./deploy.sh
```

Rsyncs this directory to the origin VM (`/var/www/miska.blog`), fixes ownership/permissions, and reloads-tests nginx config. Requires the VM's private key at `~/.ssh/miska-blog-vm` (or set `MISKA_BLOG_KEY` to another path).

Note: the CDN edge (`cdn.miska.blog`) caches responses — a deploy updates the origin immediately, but the CDN may keep serving a cached copy until its TTL expires or the cache is purged in the Gcore portal (CDN resource → Cache → Purge).
