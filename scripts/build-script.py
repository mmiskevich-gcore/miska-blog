#!/usr/bin/env python3
"""Bundle the static site into a single Bunny Edge Scripting file (script.ts).

Every deployable file in the repo is embedded into the script: text files as
strings, binaries (images) as base64. The generated script serves them from
memory at the edge, so no origin server is needed.

Usage:
    python3 scripts/build-script.py            # writes ./script.ts
    python3 scripts/build-script.py out.ts     # writes to a custom path
"""
import base64
import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "script.ts")

SDK_VERSION = "0.13.0"

# Same exclusions as deploy.sh / deploy.yml, plus the generated script itself.
EXCLUDE_DIRS = {".git", ".github", "scripts"}
EXCLUDE_FILES = {".gitignore", "deploy.sh", "README.md", "script.ts", ".DS_Store"}

CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".txt": "text/plain; charset=utf-8",
    ".xml": "application/xml; charset=utf-8",
    ".svg": "image/svg+xml",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".ico": "image/x-icon",
    ".woff": "font/woff",
    ".woff2": "font/woff2",
}
TEXT_EXTS = {".html", ".css", ".js", ".json", ".txt", ".xml", ".svg"}


def collect():
    assets = {}
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = sorted(d for d in dirnames if d not in EXCLUDE_DIRS)
        for name in sorted(filenames):
            if name in EXCLUDE_FILES:
                continue
            full = os.path.join(dirpath, name)
            rel = os.path.relpath(full, ROOT).replace(os.sep, "/")
            ext = os.path.splitext(name)[1].lower()
            ctype = CONTENT_TYPES.get(ext)
            if ctype is None:
                print(f"skip (unknown type): {rel}", file=sys.stderr)
                continue
            with open(full, "rb") as f:
                data = f.read()
            etag = hashlib.sha256(data).hexdigest()[:16]
            entry = {"type": ctype, "etag": etag}
            if ext in TEXT_EXTS:
                entry["text"] = data.decode("utf-8")
            else:
                entry["b64"] = base64.b64encode(data).decode("ascii")
            assets["/" + rel] = entry
    return assets


def render(assets):
    # json.dumps with ensure_ascii=True yields valid JS literals (escapes U+2028/2029 too).
    assets_js = json.dumps(assets, ensure_ascii=True, indent=0, separators=(",", ":"))
    return f'''// GENERATED FILE. Do not edit by hand.
// Built by scripts/build-script.py from the static site in this repo.
import * as BunnySDK from "https://esm.sh/@bunny.net/edgescript-sdk@{SDK_VERSION}";

type Asset = {{ type: string; etag: string; text?: string; b64?: string }};

const ASSETS: Record<string, Asset> = {assets_js};

const TEXT_CACHE = "public, max-age=300";
const STATIC_CACHE = "public, max-age=86400, immutable";

const decoded = new Map<string, Uint8Array>();

function bytesOf(path: string, asset: Asset): Uint8Array {{
  let cached = decoded.get(path);
  if (cached) return cached;
  const bin = atob(asset.b64 as string);
  const out = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out[i] = bin.charCodeAt(i);
  decoded.set(path, out);
  return out;
}}

function resolve(pathname: string): string | null {{
  let p = pathname;
  try {{
    p = decodeURIComponent(p);
  }} catch {{
    return null;
  }}
  if (p.includes("..")) return null;
  if (p.endsWith("/")) p += "index.html";
  if (p in ASSETS) return p;
  if (p + ".html" in ASSETS) return p + ".html";
  if (p + "/index.html" in ASSETS) return p + "/index.html";
  return null;
}}

function headersFor(asset: Asset): Headers {{
  const h = new Headers();
  h.set("Content-Type", asset.type);
  h.set("ETag", `"${{asset.etag}}"`);
  h.set("Cache-Control", asset.text !== undefined ? TEXT_CACHE : STATIC_CACHE);
  h.set("X-Served-By", "bunny-edge-script");
  return h;
}}

function notFound(): Response {{
  const page = ASSETS["/404.html"];
  if (page && page.text !== undefined) {{
    return new Response(page.text, {{ status: 404, headers: headersFor(page) }});
  }}
  return new Response("Not found\\n", {{
    status: 404,
    headers: {{ "Content-Type": "text/plain; charset=utf-8" }},
  }});
}}

BunnySDK.net.http.serve(async (request: Request): Promise<Response> => {{
  if (request.method !== "GET" && request.method !== "HEAD") {{
    return new Response("Method not allowed\\n", {{
      status: 405,
      headers: {{ Allow: "GET, HEAD", "Content-Type": "text/plain; charset=utf-8" }},
    }});
  }}

  const url = new URL(request.url);
  const path = resolve(url.pathname);
  if (path === null) return notFound();

  const asset = ASSETS[path];
  const headers = headersFor(asset);

  const inm = request.headers.get("If-None-Match");
  if (inm && inm.replace(/^W\\//, "") === `"${{asset.etag}}"`) {{
    return new Response(null, {{ status: 304, headers }});
  }}

  if (request.method === "HEAD") {{
    return new Response(null, {{ status: 200, headers }});
  }}

  const body: BodyInit = asset.text !== undefined ? asset.text : bytesOf(path, asset);
  return new Response(body, {{ status: 200, headers }});
}});
'''


def main():
    assets = collect()
    out = render(assets)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(out)
    size_kb = os.path.getsize(OUT) / 1024
    print(f"wrote {os.path.relpath(OUT, ROOT)}: {len(assets)} assets, {size_kb:.0f} KB")


if __name__ == "__main__":
    main()
