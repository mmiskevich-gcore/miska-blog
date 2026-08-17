# miska.blog

Source for the static site served at [miska.blog](http://miska.blog), the origin behind the `cdn.miska.blog` CDN resource.

## Structure

```
index.html, page2.html, page3.html   generated homepage (paginated, 8 posts/page)
about.html                            hand-written, not generated
posts/                                 generated post pages
css/style.css
scripts/generate.py                   source of truth for post content + generator (not deployed)
static/                               served page (linked from nowhere in nav, kept as a plain static asset)
api/                                  serves data.json, linked from the site nav as "API"/"status"
images/                               post hero images
```

## Adding or editing a post

Edit the `POSTS` list in `scripts/generate.py` (title, date, excerpt, image, body HTML), then regenerate:

```sh
python3 scripts/generate.py
```

This rewrites `index.html`/`page2.html`/`page3.html` and everything in `posts/` from that one data source — don't hand-edit those generated files directly, edits will be overwritten on the next run. `about.html` is the one page that's still hand-written.

New post images are fetched with a deterministic seed so they're reproducible, e.g.:

```sh
curl -sL -o images/my-new-post.jpg "https://picsum.photos/seed/my-new-post/800/600"
```

## Local preview

```sh
python3 -m http.server 8000
```

then visit `http://localhost:8000`.

## Deploy

Pushing to `main` on GitHub (`github.com/mmiskevich-gcore/miska-blog`) auto-deploys via `.github/workflows/deploy.yml` — it rsyncs the repo to the origin VM, fixes ownership/permissions, and tests the nginx config. Requires a `MISKA_BLOG_DEPLOY_KEY` repo secret (Settings → Secrets and variables → Actions) holding a private key whose public half is in the VM's `~/.ssh/authorized_keys` for the `ubuntu` user — a dedicated deploy-only key, separate from any personal key.

Manual deploy (bypasses GitHub, useful for testing before pushing):

```sh
./deploy.sh
```

Same rsync steps as the Actions workflow, run locally. Requires the VM's private key at `~/.ssh/miska-blog-vm` (or set `MISKA_BLOG_KEY` to another path).

Note: the CDN edge (`cdn.miska.blog`) caches responses — a deploy updates the origin immediately, but the CDN may keep serving a cached copy until its TTL expires or the cache is purged in the Gcore portal (CDN resource → Cache → Purge).
