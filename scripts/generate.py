#!/usr/bin/env python3
"""Generates index.html, page2.html, page3.html, and posts/*.html for miska.blog.

Source of truth is the POSTS list below. Run after editing it:
    python3 scripts/generate.py
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE_SIZE = 8

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>{description}
<link rel="stylesheet" href="/css/style.css">
</head>
<body>
<header class="site-head">
  <div class="wrap">
    <div class="brand">
      <h1><a href="/">miska.blog</a></h1>
    </div>
    <p class="tagline">notes on self-hosting, edge networks, and running things on boxes I can actually reason about</p>
    <nav class="site-nav">
      <a href="/">Home</a>
      <a href="/about.html">About</a>
      <a href="/api/data.json">API</a>
    </nav>
  </div>
</header>
"""

FOOT = """
<footer class="site-foot">
  <div class="wrap" style="display:flex; justify-content:space-between; width:100%; flex-wrap:wrap; gap:10px;">
    <span>&copy; 2026 miska.blog</span>
    <span><a href="/about.html">About</a> · <a href="/api/data.json">status</a></span>
  </div>
</footer>
</body>
</html>
"""

POST_TEMPLATE = """<main class="wrap">
  <a class="back-link" href="/">&larr; Back to all posts</a>
  <article class="post">
    <div class="post-meta">{date_display} · {read_min} min read</div>
    <h1>{title}</h1>
    <img class="hero" src="/images/{image}" alt="">
{body}
  </article>
</main>
"""

CARD_TEMPLATE = """    <li class="post-card">
      <img class="post-thumb" src="/images/{image}" alt="">
      <div>
        <div class="post-meta">{date_display} · {read_min} min read</div>
        <h2><a href="/posts/{slug}.html">{title}</a></h2>
        <p>{excerpt}</p>
      </div>
    </li>"""

PAGINATION_TEMPLATE = """  <nav class="pagination">
    {prev}
    <span class="page-numbers">{numbers}</span>
    {next}
  </nav>
"""

# ---------------------------------------------------------------------------
# Posts, newest first is NOT required here — the build sorts by date_iso.
# ---------------------------------------------------------------------------
POSTS = [
    dict(
        slug="nginx-on-a-cheap-box",
        title="Running nginx on a €7 box",
        date_iso="2026-07-20",
        date_display="July 20, 2026",
        read_min=4,
        image="nginx-on-a-cheap-box.jpg",
        excerpt="Everyone reaches for a bigger instance out of habit. Nginx serving static files barely notices — the disk matters more than the RAM.",
        body="""    <p>The instinct when you spin up a new server is to over-provision. More vCPUs, more RAM, "just in case." For a static nginx origin, that instinct is almost entirely wrong.</p>
    <p>The nginx worker process serving this page sits comfortably in tens of megabytes of resident memory. It doesn't fork per request, it doesn't hold a connection pool to a database, and it isn't compiling anything at request time. The bottleneck was never going to be compute.</p>
    <p>What actually needed headroom was disk — the default 5&nbsp;GiB volume gets tight once you add the OS, the apt cache, nginx itself, logs, and a handful of test images. Bumping to 10&nbsp;GiB cost a fraction of a cent more per month and removed the only real constraint.</p>
    <p>The lesson generalizes past this one box: before sizing a VM, ask what the workload is actually bound by. Static file serving is I/O and disk-bound, not CPU-bound. Sizing for the wrong resource means paying for capacity you'll never touch while quietly running low on the one you needed.</p>
    <pre><code>server {
    listen 80;
    server_name miska.blog;
    root /var/www/miska.blog;
    index index.html;
}</code></pre>
    <p>That's the entire server block doing the actual work. Everything else — DNS, CDN, edge logic — sits in front of it, but this is still what answers the request at the end of the chain.</p>""",
    ),
    dict(
        slug="what-a-cdn-actually-does",
        title="What actually happens when a CDN caches your page",
        date_iso="2026-07-15",
        date_display="July 15, 2026",
        read_min=6,
        image="what-a-cdn-actually-does.jpg",
        excerpt="Watching a HIT turn into a MISS and back again taught me more about caching than any diagram ever did.",
        body="""    <p>I'd read the diagrams a dozen times: browser hits edge, edge checks cache, cache miss goes to origin, response gets stored, next request is a hit. It made sense on paper. It didn't feel real until I watched it happen against a page I control.</p>
    <p>The first request after creating the resource came back with a cache status of <code>MISS</code> — the edge node had nothing stored yet, so it pulled from the origin VM, served it, and kept a copy. Every request after that, from anywhere near that edge node, came back <code>HIT</code> without touching origin at all.</p>
    <p>The part that isn't obvious from a diagram: a HIT and a MISS at the CDN layer are invisible to the end user in every way except one — origin load. The response looks identical. The only reason to care is that your origin now handles a fraction of the traffic it used to, which is the entire point.</p>
    <p>The other thing worth internalizing: cache state is edge-node-specific, not global. Whether the visitor next to me sees a HIT or a MISS depends on whether their nearest edge node already has a copy, not on whether the object exists anywhere at all in the CDN's network.</p>
    <pre><code>curl -I https://cdn.miska.blog/
&gt; HTTP/2 200
&gt; cache: HIT</code></pre>
    <p>That single header line is doing more explanatory work than any architecture diagram I'd looked at before actually standing one of these up myself.</p>""",
    ),
    dict(
        slug="delegating-dns-without-breaking-it",
        title="Delegating DNS without breaking everything",
        date_iso="2026-07-05",
        date_display="July 5, 2026",
        read_min=5,
        image="delegating-dns-without-breaking-it.jpg",
        excerpt="Nameservers versus DNS records are two different screens at every registrar, and only one of them is the one you want.",
        body="""    <p>Every registrar has two screens that look like they should be the same thing and are not. One manages individual DNS records — A, CNAME, TXT — for the nameservers you're currently using. The other lets you change which nameservers you're using at all. Only the second one is nameserver delegation.</p>
    <p>I found this out by opening the wrong one first. My registrar's records panel, on noticing I clicked into it, offered to "fix" my setup by resetting me back to its own default nameservers — the exact opposite of what I was there to do. Declining that dialog was the correct move; the actual delegation screen was a separate link entirely, one level up in the domain management view.</p>
    <p>Once I found it, the change itself was two lines: swap the registrar's nameservers for the new provider's, save, and wait. Propagation is quoted anywhere from a few minutes to 48 hours depending on who you ask, and there's no way to force it — the only honest way to check is asking DNS directly rather than trusting a timer:</p>
    <pre><code>dig NS miska.blog

;; ANSWER SECTION:
miska.blog. 3600 IN NS ns1.example-dns.net.
miska.blog. 3600 IN NS ns2.example-dns.net.</code></pre>
    <p>Once that query returns the new nameservers instead of the old ones, delegation is live, and every record from then on — CDN CNAMEs, ACME challenge records, the lot — gets managed in the new place. Until then, anything you configure on the new side is invisible to actual traffic, which is the failure mode worth designing your rollout around.</p>""",
    ),
    dict(
        slug="choosing-a-registrar-nobody-warns-you-about",
        title="Choosing a registrar nobody warns you about",
        date_iso="2026-06-28",
        date_display="June 28, 2026",
        read_min=4,
        image="choosing-a-registrar-nobody-warns-you-about.jpg",
        excerpt="The sticker price on a domain is not the number that ends up mattering — the renewal price and the DNS panel both matter more.",
        body="""    <p>Picking a domain registrar felt like a five-minute decision. Find a cheap TLD, put in a card, done. It's the two numbers after the checkout page that actually matter: the renewal price, and how much friction the DNS panel adds every time you need to touch a record.</p>
    <p>The first-year promo price on some of the cheaper TLDs is real, but it's a promo — the renewal quote a year later can be several times higher, and it's easy to not notice until the invoice shows up. Worth checking the renewal price before checkout, not after.</p>
    <p>The DNS panel matters more than I expected going in. Some registrars hand you a plain records table. Others route you through a third-party-branded panel that looks like it belongs to someone else entirely, with its own quirks and its own confirmation dialogs that assume you want their defaults back.</p>
    <p>None of this is a reason to avoid cheap TLDs — this domain is still on one. It's a reason to read the renewal price and click around the DNS panel once before committing, rather than after you're three records deep and need to change something in a hurry.</p>""",
    ),
    dict(
        slug="what-a-security-group-actually-blocks",
        title="What a security group actually blocks (and what it doesn't)",
        date_iso="2026-06-21",
        date_display="June 21, 2026",
        read_min=5,
        image="what-a-security-group-actually-blocks.jpg",
        excerpt="Security groups feel like a firewall until you actually reason through what \"default\" means and what happens when two groups disagree.",
        body="""    <p>A security group reads like a firewall rule set, and mostly it is one, but two things about how it actually behaves aren't obvious until you've been bitten by them once.</p>
    <p>First: groups are additive, not exclusive. Attaching a second group doesn't replace the first — a port is open if <em>any</em> attached group allows it. That's good news if you're worried about locking yourself out (keep the default group attached alongside a custom one), and bad news if you assumed removing a rule from one group closes a port that's still open via another.</p>
    <p>Second: they're stateful. A rule allowing inbound traffic on port 443 doesn't need a matching outbound rule for the response to get back out — the return path for an already-permitted connection is implicit. This trips people coming from stricter on-prem firewall mental models, where inbound and outbound are two separate universes you configure independently.</p>
    <p>The practical upshot: if a fresh VM times out on <code>curl</code> from the outside, check the security group before anything else. It's the single most common reason a server that's clearly running is still unreachable.</p>""",
    ),
    dict(
        slug="locked-out-root-is-a-feature",
        title="Locked-out root is a feature, not a bug",
        date_iso="2026-06-14",
        date_display="June 14, 2026",
        read_min=4,
        image="locked-out-root-is-a-feature.jpg",
        excerpt="Root SSH being blocked looked broken until I read the actual forced command sitting in root's authorized_keys.",
        body="""    <p>My first reaction to <code>ssh root@&lt;ip&gt;</code> printing a message and disconnecting, regardless of which key I offered, was that something was misconfigured. It wasn't — it's the default, and it's deliberate.</p>
    <p>Cloud images ship a forced command in root's <code>authorized_keys</code> that does exactly one thing: tell you to log in as the non-root user instead, then close the connection. No amount of key-juggling gets around it, because it isn't checking the key at all past that point — the forced command runs unconditionally for that account.</p>
    <p>The reasoning makes sense once you say it out loud: root is the single most-targeted account on any internet-facing box. Removing it as a valid SSH login target removes the single highest-value brute-force target by design, and the non-root user with <code>sudo</code> gives you everything you actually need.</p>
    <p>The corollary worth remembering: if <em>that</em> non-root user's <code>sudo</code> itself misbehaves — asks for a password that was never set, for instance — that's a different, genuinely broken state, not the same intentional restriction. Don't spend time trying to route around root's lockout in that case either; recreating the instance is faster than debugging either failure mode.</p>""",
    ),
    dict(
        slug="reading-nginx-logs-like-they-mean-something",
        title="Reading nginx logs like they're trying to tell you something",
        date_iso="2026-06-07",
        date_display="June 7, 2026",
        read_min=5,
        image="reading-nginx-logs-like-they-mean-something.jpg",
        excerpt="An access log line looks like noise until you know which field is answering which question.",
        body="""    <p>The default nginx access log format looked like a wall of text the first time I <code>tail -f</code>'d it. It stopped looking that way once I mapped each field to the question it's actually answering.</p>
    <pre><code>203.0.113.9 - - [24/Jul/2026:14:02:11 +0000] "GET /posts/nginx-on-a-cheap-box.html HTTP/1.1" 200 3021 "-" "Mozilla/5.0"</code></pre>
    <p>Client IP answers "who." The timestamp answers "when." The request line answers "what were they asking for." The status code answers "did it work." The byte count answers "how much did we actually send." The user agent answers "with what" — and that last one is the field that quietly does the most diagnostic work.</p>
    <p>A real browser user agent requesting <code>/posts/...html</code> with a 200 is exactly what you'd hope to see. A bare, malformed, or clearly automated user agent hitting <code>/wp-admin</code> or <code>/.env</code> with a 404 is noise — the internet scanning every IP address it can reach for low-hanging fruit, not a real visitor, and not something to react to on a static site with nothing at those paths to find.</p>
    <p>Once you can tell those two patterns apart at a glance, the log stops being noise and starts being the fastest way to answer "is anything actually wrong right now."</p>""",
    ),
    dict(
        slug="the-gap-between-up-and-live",
        title="The gap between \"server is up\" and \"site is live\"",
        date_iso="2026-05-31",
        date_display="May 31, 2026",
        read_min=4,
        image="the-gap-between-up-and-live.jpg",
        excerpt="systemctl status showing active tells you almost nothing about whether a visitor can actually reach the page.",
        body="""    <p><code>systemctl status nginx</code> showing <code>active (running)</code> feels like confirmation that the site is live. It confirms exactly one link in a chain of five or six, and it's rarely the one that's actually broken.</p>
    <p>Between "the process is running" and "a stranger's browser renders the page," you've got: the port actually bound and listening, the security group allowing the traffic in, DNS resolving the domain to the right IP, and — once TLS is in the picture — a valid certificate for the name being requested. Any single one of those failing looks identical from the outside: the site just doesn't load.</p>
    <p>The debugging order that's saved the most time: check locally on the box first (<code>curl localhost</code>), then by public IP from your own machine, then by domain name, then over HTTPS specifically if that's in play. Each step rules out one layer, and the point where it stops working tells you exactly where to look — instead of guessing across all five layers at once.</p>""",
    ),
    dict(
        slug="ttl-is-a-promise-not-a-guarantee",
        title="TTL is a promise, not a guarantee",
        date_iso="2026-05-24",
        date_display="May 24, 2026",
        read_min=4,
        image="ttl-is-a-promise-not-a-guarantee.jpg",
        excerpt="A TTL reads like a countdown timer. In practice it's more like a suggestion that most resolvers mostly honor.",
        body="""    <p>I'd assumed a DNS record's TTL was close to a hard contract: set it to 300 seconds, and any change is fully live everywhere five minutes later. Reality is looser than that.</p>
    <p>Recursive resolvers are supposed to discard a cached answer once its TTL expires, and most do. But there's no way to force every resolver on the internet to actually re-check on your schedule — some cache longer than instructed, some serve a stale answer if your authoritative server is briefly unreachable, and plenty of client-side layers (OS resolver cache, browser DNS cache) add their own caching on top with their own rules.</p>
    <p>None of this means TTLs don't matter — a low TTL genuinely narrows the window compared to a high one. It means treating a TTL as a target to plan around rather than a promise to test against. If a change needs to be verified as live, checking with a fresh <code>dig</code> query is closer to the truth than trusting the clock.</p>""",
    ),
    dict(
        slug="http-01-vs-dns-01",
        title="HTTP-01 vs DNS-01, and why the choice isn't cosmetic",
        date_iso="2026-05-17",
        date_display="May 17, 2026",
        read_min=5,
        image="http-01-vs-dns-01.jpg",
        excerpt="Let's Encrypt's two validation methods prove the same thing — that you control the domain — in ways that fail differently.",
        body="""    <p>Let's Encrypt needs proof you actually control a domain before it'll issue a certificate for it, and it offers two common ways to provide that proof — HTTP-01 and DNS-01 — that look like implementation details until one of them fails and the other doesn't.</p>
    <p>HTTP-01 asks your origin to serve a specific file at a specific path over plain HTTP at the moment of validation. It's simple and needs no DNS access at all, but it has a hard requirement baked in: your origin has to be reachable on port 80, right now, serving exactly that file. Anything sitting in front of the origin — a CDN not yet fully configured, a firewall rule, DNS that hasn't propagated — can silently break this path.</p>
    <p>DNS-01 instead asks you to publish a specific TXT record under <code>_acme-challenge</code>. It needs DNS write access, which is a higher bar to automate, but once you have it, validation doesn't care whether your origin is reachable at all — it's checking the DNS zone, not the server.</p>
    <p>The practical rule that's fallen out of using both: reach for DNS-01 first for anything sitting behind a CDN or proxy, since HTTP-01's requirement — a directly reachable origin on port 80 at exactly the right moment — is precisely the thing a CDN in front of your domain tends to complicate.</p>""",
    ),
    dict(
        slug="static-files-dont-need-a-database",
        title="Static files don't need a database",
        date_iso="2026-05-10",
        date_display="May 10, 2026",
        read_min=3,
        image="static-files-dont-need-a-database.jpg",
        excerpt="The temptation to reach for a CMS and a database for a blog with a dozen posts is strong, and almost always wrong.",
        body="""    <p>Every time I start a small site, there's a moment where the instinct says: this needs a real backend. A database for the posts, an admin panel to edit them, maybe a caching layer in front of the database to make up for adding one in the first place.</p>
    <p>For a blog with a couple dozen posts and no reader-generated content, that entire stack solves problems this site doesn't have. There's no data model here more complex than "a page has a title, a date, and some text." A flat HTML file, or a small script that generates one from a plain data structure, covers that completely.</p>
    <p>The tradeoff runs the other way too, of course — a database earns its keep the moment you have real relational queries, concurrent writers, or content that changes without a redeploy. None of that applies here. Recognizing which side of that line a project sits on, before reaching for the familiar tool, is the actual skill.</p>""",
    ),
    dict(
        slug="what-actually-fills-a-5gb-disk",
        title="What actually fills a \"5 GiB\" disk",
        date_iso="2026-05-03",
        date_display="May 3, 2026",
        read_min=4,
        image="what-actually-fills-a-5gb-disk.jpg",
        excerpt="5 GiB sounds like plenty until du -sh walks you through where it actually goes on a freshly provisioned box.",
        body="""    <p>5 GiB sounds like an absurd amount of space for a box that's only ever going to serve a handful of static files. It stops sounding that way once you actually total up what's on the disk before your content ever touches it.</p>
    <pre><code>$ du -sh /usr /var/log /var/cache/apt /var/www 2&gt;/dev/null
1.6G    /usr
420M    /var/log
310M    /var/cache/apt
    8K    /var/www</code></pre>
    <p>The base OS install alone accounts for over a gigabyte before nginx is even installed. The apt cache from every <code>apt update</code> and <code>apt install</code> run adds up and doesn't clear itself. Logs grow continuously and, on a box nobody's rotating aggressively, can quietly become one of the largest consumers of space on the whole system.</p>
    <p>None of that is your content's fault — it's the fixed and semi-fixed overhead of running any Linux box at all, and it's roughly the same whether you're serving one file or a thousand. Bumping to 10&nbsp;GiB for a few cents more a month buys enough headroom that this stops being something to think about.</p>""",
    ),
    dict(
        slug="cname-vs-alias-finally-understood",
        title="CNAME vs ALIAS, finally understood",
        date_iso="2026-04-26",
        date_display="April 26, 2026",
        read_min=4,
        image="cname-vs-alias-finally-understood.jpg",
        excerpt="A CNAME and an ALIAS point at the same kind of target and behave completely differently at the root of a domain.",
        body="""    <p>Both a CNAME and an ALIAS (sometimes called ANAME) point one name at another name rather than at a fixed IP. From that description alone, they sound interchangeable. They aren't, and the difference shows up specifically at the root of a domain.</p>
    <p>A CNAME record can't coexist with any other record at the same name — that's a DNS protocol rule, not a vendor limitation. Since the root of a domain almost always needs other records (MX for mail, at minimum), you can't point the bare root at a CNAME target. That's exactly why parking-page setups default to an ALIAS at the root instead: it's a provider-level construct, resolved to actual A records behind the scenes at query time, that's allowed to sit alongside other records at the root because it isn't really a CNAME under the hood.</p>
    <p>Practically, this is why swapping a root domain from a parking ALIAS to a real A record pointing at your own server means deleting the ALIAS first — the two can't sit at the same name any more than a CNAME and an MX record could, since the ALIAS is standing in for exactly the slot the A record needs.</p>""",
    ),
    dict(
        slug="watching-a-cold-cache-warm-up",
        title="Watching a cold cache warm up in real time",
        date_iso="2026-04-19",
        date_display="April 19, 2026",
        read_min=4,
        image="watching-a-cold-cache-warm-up.jpg",
        excerpt="Timing the same request five times in a row turns \"caching\" from a concept into something you can watch happen.",
        body="""    <p>It's one thing to know a CDN caches responses. It's another to sit at a terminal and time the exact same request five times in a row and watch the number change in a way that only makes sense if something got faster on the second attempt.</p>
    <pre><code>$ for i in 1 2 3 4 5; do curl -o /dev/null -s -w "%{time_total}s\\n" https://cdn.miska.blog/images/nginx-on-a-cheap-box.jpg; done
0.412s
0.041s
0.038s
0.039s
0.037s</code></pre>
    <p>The first request pays the full round trip to origin. Every request after it is roughly ten times faster, served entirely from the edge node's local cache. No code changed, no configuration changed between requests one and two — the only thing that changed was that the edge now had a copy.</p>
    <p>Seeing that timing gap directly is a better explanation of what a CDN is for than any amount of reading about "reduced origin load" in the abstract. The origin load reduction is real, but the thing a user actually experiences is exactly this: request two through five just arrive faster.</p>""",
    ),
    dict(
        slug="why-edge-location-beats-server-specs",
        title="Why edge location beats server specs",
        date_iso="2026-04-12",
        date_display="April 12, 2026",
        read_min=3,
        image="why-edge-location-beats-server-specs.jpg",
        excerpt="For anything cacheable, the distance to the nearest edge node matters more than any spec on the origin server.",
        body="""    <p>It's tempting to think a faster origin server makes a site faster. For anything that ends up cached at the edge, that's mostly not true — the origin's specs only matter on a cache miss, and a well-configured cache means most real visitors never trigger one.</p>
    <p>What actually governs the speed a visitor experiences is the round-trip time to their nearest edge node. That's a function of geography and network topology, not CPU generation or RAM. A visitor three hops from an edge node will always beat a visitor twelve hops away, regardless of how much you upgrade the single origin box sitting behind both of them.</p>
    <p>This reframes what's worth optimizing. Past a baseline where the origin isn't the bottleneck, the lever that actually moves the needle for most visitors is cache coverage and edge network breadth — not squeezing more performance out of the one server that, for a well-cached site, most requests never even reach.</p>""",
    ),
    dict(
        slug="things-that-break-propagation-checks",
        title="A short list of things that break DNS propagation checks",
        date_iso="2026-04-05",
        date_display="April 5, 2026",
        read_min=4,
        image="things-that-break-propagation-checks.jpg",
        excerpt="If a DNS change looks like it hasn't propagated, the cache that's lying to you is usually closer than you think.",
        body="""    <p>Every time a DNS change appears to not have taken effect, the actual cause has, so far, always been one of the same handful of things — and rarely the thing it looks like at first.</p>
    <p>The browser itself caches DNS lookups, separately from the OS. The OS resolver caches separately again, sometimes for longer than the record's TTL suggests it should. Your ISP's recursive resolver caches on its own schedule, which you have zero visibility into or control over. And checking from the same network, on the same machine, where you were looking at the old record five minutes ago is the single most common way to keep seeing a result that's already stale everywhere else.</p>
    <pre><code>dig +short miska.blog @8.8.8.8</code></pre>
    <p>Querying a public resolver directly, from a query tool rather than a browser, strips out at least two of those caching layers at once and gives the most honest read on whether the record has actually changed at the authoritative source — which is usually the answer to "has this propagated yet" that actually matters.</p>""",
    ),
    dict(
        slug="rebuilding-is-faster-than-debugging",
        title="Rebuilding is faster than debugging",
        date_iso="2026-03-29",
        date_display="March 29, 2026",
        read_min=3,
        image="rebuilding-is-faster-than-debugging.jpg",
        excerpt="For a cheap, disposable test box, recreating it from scratch is often the correct fix, not the lazy one.",
        body="""    <p>There's a reflex to treat rebuilding a broken server as giving up — real debugging means finding the root cause, not starting over. That reflex is worth overriding for a specific category of box: cheap, disposable, and fully reproducible from a runbook.</p>
    <p>When this VM's <code>sudo</code> unexpectedly demanded a password that had never been set, the honest options were: spend an unknown amount of time investigating a cloud-init failure on a $0.66-a-month test instance, or spend five minutes deleting it and creating an identical one. The second option won on pure economics — the time cost of debugging almost certainly exceeded the cost of the box itself many times over.</p>
    <p>The recreated instance worked cleanly on the first try, which also answered the underlying question for free: the failure was instance-specific, not a defect in the base image. Sometimes the fastest way to root-cause a problem is to remove the broken instance from the equation entirely and see whether the problem comes back.</p>""",
    ),
    dict(
        slug="what-origin-shielding-protects",
        title="What origin shielding actually protects you from",
        date_iso="2026-03-22",
        date_display="March 22, 2026",
        read_min=4,
        image="what-origin-shielding-protects.jpg",
        excerpt="An extra caching layer between edge and origin sounds redundant until you picture every edge node missing at once.",
        body="""    <p>Origin shielding showed up as an option while configuring the CDN resource, described briefly enough that it wasn't obvious why you'd want an extra caching layer between the edge and an origin that already has its own cache-friendly setup.</p>
    <p>The scenario it's actually solving for: a piece of content just expired everywhere at once — a TTL boundary, a purge, a deploy. Without shielding, every edge node globally that gets a request for that content in the next moment independently treats it as a miss and independently goes to origin at the same time. For a popular object, that's dozens or hundreds of simultaneous origin requests for content that's about to be identical across all of them.</p>
    <p>A shield node sits between the edge tier and the origin specifically to collapse that pattern: edge nodes miss against the shield, only the shield misses against origin, and the origin sees one request instead of many. For a test box handling essentially no concurrent traffic, that problem doesn't exist yet — which is exactly why it's a feature worth understanding and skipping for now rather than switching on by default.</p>""",
    ),
    dict(
        slug="the-compression-header-nobody-checks",
        title="The compression header nobody checks until the page is slow",
        date_iso="2026-03-15",
        date_display="March 15, 2026",
        read_min=3,
        image="the-compression-header-nobody-checks.jpg",
        excerpt="Content-Encoding is invisible right up until a page that should be fast, isn't.",
        body="""    <p><code>Content-Encoding: gzip</code> is one of those response headers that's easy to never think about, because when it's working correctly it's completely invisible — the page just loads, and looks identical whether or not the bytes were compressed in transit.</p>
    <p>It stops being invisible the moment it isn't there and should be. A small HTML or JSON test file barely benefits either way, which is exactly why it's easy to leave compression off during initial setup and not notice. The gap becomes real once the response bodies involved are actual page weight rather than a one-line JSON status check — CSS, larger HTML documents, anything text-based that compresses well.</p>
    <p>The check costs one line: <code>curl -H "Accept-Encoding: gzip" -I</code> against a resource and look for the header in the response. Worth running once against real page weight, not just the test fixtures, before assuming it's handled.</p>""",
    ),
    dict(
        slug="what-a-502-taught-me",
        title="What a 502 taught me",
        date_iso="2026-03-08",
        date_display="March 8, 2026",
        read_min=4,
        image="what-a-502-taught-me.jpg",
        excerpt="A 502 is the CDN telling you, specifically, that the problem is behind it — which narrows the search immediately.",
        body="""    <p>Restarting nginx mid-test to pick up a config change produced a brief window of <code>502 Bad Gateway</code> responses through the CDN — the first 502 this whole setup had actually produced, and a useful one to have seen on purpose rather than in a panic.</p>
    <pre><code>$ curl -I https://cdn.miska.blog/
HTTP/2 502</code></pre>
    <p>A 502 specifically means the layer answering the request — here, the CDN edge — successfully reached the next layer back but got an invalid or no response from it. That's a meaningfully different signal from a timeout, a DNS failure, or a TLS error, each of which point at a different part of the chain. A 502 says: the problem is at or behind the origin, not in DNS, not in TLS, not in the CDN's own routing.</p>
    <p>Watching it resolve itself within a couple of seconds, exactly as long as the reload took, confirmed the read: nginx was momentarily not accepting connections during its restart, the CDN correctly reported that as a bad gateway rather than silently retrying forever, and once nginx came back the 502s stopped without any other action needed.</p>""",
    ),
    dict(
        slug="why-quotas-required-isnt-a-config-error",
        title="Why \"Quotas required\" isn't a config error",
        date_iso="2026-03-01",
        date_display="March 1, 2026",
        read_min=3,
        image="why-quotas-required-isnt-a-config-error.jpg",
        excerpt="Some VM flavors are blocked behind an account-level approval, not a form field you filled in wrong.",
        body="""    <p>Picking a VM flavor and having the portal respond with something like "Quotas required" reads, at first glance, like a mistake somewhere in the form — a wrong field, a missing setting, something to fix and resubmit.</p>
    <p>It isn't that. It's an account-level limit on that specific resource type or tier that hasn't been raised yet, entirely separate from whether the instance configuration itself is valid. The form is correct; the account just isn't provisioned to create that particular shape of resource without an approval step first.</p>
    <p>The fix isn't to keep adjusting fields hoping one of them is the culprit — it's to either request the quota increase through the portal, or fall back to a smaller flavor that's already within the account's default limits, which is what actually unblocked this specific test box. Worth recognizing the message for what it is early, rather than spending time debugging a form that was never the problem.</p>""",
    ),
    dict(
        slug="everything-i-got-wrong-about-propagation",
        title="Everything I got wrong about propagation delay",
        date_iso="2026-02-22",
        date_display="February 22, 2026",
        read_min=4,
        image="everything-i-got-wrong-about-propagation.jpg",
        excerpt="A running list of the assumptions about DNS propagation that turned out not to survive contact with an actual domain.",
        body="""    <p>A few months into actually running a domain instead of just reading about how DNS works, it's worth listing out what I assumed going in that turned out to be wrong.</p>
    <p>I assumed propagation was one event with a single, knowable completion time. It isn't — it's thousands of independent resolvers each deciding on their own schedule when to stop trusting their cached answer, which means "propagated" is really a probability that climbs toward certain over hours, not a switch that flips.</p>
    <p>I assumed a lower TTL meant faster propagation on a change I hadn't made yet. It only helps retroactively — a TTL only bounds how long a resolver holds onto an answer <em>it already cached</em>, so lowering it moments before a change is too late to help that specific change; it only pays off if it was already low beforehand.</p>
    <p>I assumed checking from my own laptop was a reasonable proxy for "is this live yet." It's one of the least reliable checks available, precisely because my laptop and my ISP are exactly the resolvers most likely to already have a cached answer from before the change. Querying a public resolver directly turned out to be the far more honest test, every time.</p>""",
    ),
    dict(
        slug="why-i-stopped-fearing-a-silent-terminal",
        title="Why I stopped fearing a silent terminal",
        date_iso="2026-02-15",
        date_display="February 15, 2026",
        read_min=3,
        image="why-i-stopped-fearing-a-silent-terminal.jpg",
        excerpt="The first post in this notebook — on why a command producing no output isn't the same thing as a command failing.",
        body="""    <p>This is the first entry in what became this blog, written right after finishing the first pass of this whole setup — domain, VM, nginx — and before any of the CDN or edge-compute pieces existed yet.</p>
    <p>The habit I had to unlearn first had nothing to do with DNS or servers specifically: it was flinching every time a command finished without printing anything. <code>apt install</code>, <code>systemctl reload</code>, a successful <code>scp</code> — plenty of the commands that make up this kind of work say nothing at all when they succeed, and for a while every silent return felt like it might mean something had silently gone wrong.</p>
    <p>What actually tells you whether something worked is the exit code, not the presence of reassuring output — <code>echo $?</code> after anything that stayed quiet, or better, structuring commands so the next step only runs on success (<code>&amp;&amp;</code>) instead of blindly proceeding regardless. Once that became the reflex instead of waiting for comforting text on screen, a silent terminal stopped feeling like an open question.</p>
    <p>Writing each step down as I went — what worked, what didn't, what the actual fix turned out to be instead of the first thing I tried — is the reason this notebook exists at all. Everything since this post is what came out of that habit.</p>""",
    ),
]


def render_post(post):
    return HEAD.format(
        title=f"{post['title']} — miska.blog", description=""
    ) + POST_TEMPLATE.format(**post) + FOOT


def render_card(post):
    return CARD_TEMPLATE.format(**post)


def render_pagination(page_num, total_pages):
    def href(n):
        return "/" if n == 1 else f"/page{n}.html"

    prev = (
        f'<a class="page-link prev" href="{href(page_num - 1)}">&larr; Newer</a>'
        if page_num > 1
        else '<span class="page-link prev disabled">&larr; Newer</span>'
    )
    nxt = (
        f'<a class="page-link next" href="{href(page_num + 1)}">Older &rarr;</a>'
        if page_num < total_pages
        else '<span class="page-link next disabled">Older &rarr;</span>'
    )
    numbers = []
    for n in range(1, total_pages + 1):
        if n == page_num:
            numbers.append(f'<span class="page-num current">{n}</span>')
        else:
            numbers.append(f'<a class="page-num" href="{href(n)}">{n}</a>')
    return PAGINATION_TEMPLATE.format(prev=prev, next=nxt, numbers=" ".join(numbers))


def render_index_page(posts_page, page_num, total_pages):
    cards = "\n".join(render_card(p) for p in posts_page)
    body = f'  <ul class="post-list">\n{cards}\n  </ul>\n' + render_pagination(page_num, total_pages)
    title = "miska.blog — notes on small infrastructure" if page_num == 1 else f"miska.blog — page {page_num}"
    description = '\n<meta name="description" content="A small blog about self-hosting, edge networks, and building things on hardware you can actually reason about.">' if page_num == 1 else ""
    return HEAD.format(title=title, description=description) + f'\n<main class="wrap">\n{body}</main>\n' + FOOT


def main():
    posts_sorted = sorted(POSTS, key=lambda p: p["date_iso"], reverse=True)

    posts_dir = os.path.join(ROOT, "posts")
    os.makedirs(posts_dir, exist_ok=True)
    for post in posts_sorted:
        with open(os.path.join(posts_dir, f"{post['slug']}.html"), "w") as f:
            f.write(render_post(post))

    total_pages = (len(posts_sorted) + PAGE_SIZE - 1) // PAGE_SIZE
    for page_num in range(1, total_pages + 1):
        start = (page_num - 1) * PAGE_SIZE
        chunk = posts_sorted[start:start + PAGE_SIZE]
        content = render_index_page(chunk, page_num, total_pages)
        filename = "index.html" if page_num == 1 else f"page{page_num}.html"
        with open(os.path.join(ROOT, filename), "w") as f:
            f.write(content)

    print(f"Generated {len(posts_sorted)} posts across {total_pages} index pages.")


if __name__ == "__main__":
    main()
