# Board adapter — Forasna (Egypt): rules open to `Claude-User`, a challenge on every path, sitemap included

<!-- verified: 2026-09-11 -->

<!-- hosts: forasna.com -->
<!-- script: none -->
<!-- countries: EG -->
<!-- content: indeterminate · 1 host, 4 paths tried under the permitted token (`/`, `/sitemap.xml`, `/sitemap_index.xml`, plus the rules) and every one of the 3 content paths answers HTTP 403 with a 5 645–5 717-byte Cloudflare interstitial titled `Just a moment...`, md5 different on two fetches of the root at constant size — a challenge; unlike its Egyptian sibling `wuzzuf.net`, the XML is behind it too, so nothing of the site was read · 2026-09-11 13:54 UTC -->
<!-- witness: none — nothing was served, and the rules declare no Sitemap line -->

**Egypt's second board on a card with `wuzzuf.net`, and the same family of
«no» — with one difference that decides the route.** Measured 2026-09-11,
13:54 UTC, every fetch through `bin/fetch-body.py` under the declared
identity, the guard on the exact path first.

## The rules — the Cloudflare managed file, `ClaudeBot` refused, `*` open

```
GET /robots.txt        200, fetched twice, same body
User-agent: *          Content-Signal: search=yes,ai-train=no,use=reference   Allow: /
User-agent: Amazonbot · Applebot-Extended · Bytespider · CCBot · ClaudeBot ·
            CloudflareBrowserRenderingCrawler · Google-Extended · GPTBot · meta-externalagent   Disallow: /
```

No `Crawl-delay`, **no `Sitemap:` line** — `shared/robots-policy.md` already
lists this host with `wuzzuf.net` among the Egyptian carriers of the managed
file. `identity("forasna.com", "/")` → `http`, `claude-user`; `allowed()`
`True`, `certain: True` on `/`, `/jobs`, `/jobs/egypt`, `/sitemap.xml`.
**The permitted token exists on paper and is the one that was tried.**

## The transport — a challenge on every path, the XML included

```
GET /                     403, 5 645 B, «Just a moment...», md5 a2d8d492…  then 43fcbfed…   ← same URL twice
GET /sitemap.xml          403, 5 678 B, «Just a moment...»
GET /sitemap_index.xml    403, 5 717 B, «Just a moment...»
```

**Same size, different md5 on two fetches of the same URL — a challenge, the
`revolico` / `mabumbe` / `wuzzuf` family.** *The comparison across hosts is
void by the rule of 2026-09-07 (the `cf-ray` is inside the body), and the
comparison of one URL with itself is what says «challenge».* **Where
`wuzzuf.net` serves its sitemap XML from behind the same interstitial, this
host does not** — the two guessed sitemap paths answer the challenge like the
root, and the rules declare none. *So there is no address inventory here, and
no script.*

**A challenge is where the browser branch stops** (borne 2): the plugin
neither defeats one nor asks the user to. Whether a real browser passes this
managed challenge without a person is not measured, and this card claims
nothing either way.

## What this card is, and is not

- **Not a verdict that the board is closed** — the owner's decision, on his
  express validation (rule of 2026-09-08). Recorded: three content paths, one
  day, one client, a challenge each time.
- **Not the #222 case as measured here**: a challenge, not a static 403.
- **No script, no configuration.** A user with a forasna.com URL can hand it
  to `cover-letter`; whether that page is served to a browser is not
  established here.
- **What would change it:** a `Sitemap:` line, or XML served from behind the
  interstitial as `wuzzuf.net` does — one request to check, dated.
