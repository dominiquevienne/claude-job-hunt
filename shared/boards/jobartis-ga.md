# Board measurement — Jobartis Gabon (`www.jobartis.ga`): 228 advertisements, and the network's Angolan adapter is ONE locale constant away — the sitemap shape transposes, the extraction is unverified, no script yet

<!-- verified: 2026-10-21 -->

<!-- hosts: www.jobartis.ga -->
<!-- script: none -->
<!-- countries: GA -->
<!-- content: measured · **228 advertisements under `/emploi-<slug>`** in the declared `sitemap.xml.gz` — a flat `urlset` of **339 `<loc>`, all 339 distinct**, with no child sitemap and **no `<![CDATA[`** (checked, because that trap returns zero on a 343 977-byte file for `cabinets-es.md`). The classification is **exhaustive and its classes are disjoint: 228 advertisements + 106 faceted listing pages under `/emplois/…` + 5 chrome pages = 339, intersection zero.** **The apex redirects to `www`**: `bin/fetch-body.py https://jobartis.ga/` recorded `final_url: https://www.jobartis.ga/`, and the guard queried on the apex names `www.jobartis.ga` as the host that answered — so the body came from the host the guard answered for. `m.jobartis.ga` is linked from the root and is not used; `assets.jobartis.com` serves the stylesheet and the favicons and is the NETWORK's asset host, never a board host. Root 200, 41 690 B, French, `<title>` «Offres d'emploi | Jobartis Emplois | Emplois au Gabon» · 2026-10-21 -->
<!-- witness: none the site states — no total on the root and none on `/emplois`; 228 is a figure about the FILE, being its 339 `<loc>` after the other two classes are named and enumerated. Single locale, so no per-language inflation: 339 `<loc>` for 339 distinct, against the 416-for-100 shape · 2026-10-21 -->
<!-- route: http · 228 · 2026-10-21 -->

**Two requests, `bin/fetch-body.py` with the declared identity, 2026-10-21
18:25:15Z and 18:27:14Z.** Guard taken on each exact host form *separately* and
in a turn distinct from the retrieval: `jobartis.ga`, `www.jobartis.ga` and the
sitemap path all answer `allowed: True`, `state: read`, **`rule: None`** — the
rules file is read and nothing touches our paths — and **no `Crawl-delay` is
written anywhere**. Vendor: `server: cloudflare`, `via: 2.0 heroku-router`.

## The question that decides the next adapter, answered in the direction of Hays

`jobartis.py` ships today and is wired to Angola by three literals:
`BASE = "https://www.jobartis.com"`, `SITEMAP = BASE + "/sitemap.xml.gz"`, and
`countries: ["AO"]`.

```
.com (Angola, pt)   sitemap.xml.gz   flat urlset   advertisements  /emprego-<slug>
.ga  (Gabon,  fr)   sitemap.xml.gz   flat urlset   advertisements  /emploi-<slug>
```

**The URL SHAPE is shared, so the route transposes: this is the `hays-fr` case
and not the `randstad` case** — *the discriminant is whether the shape is
shared, never whether the brand is, and the brand is shared in both.* What
changes is one per-locale constant, the Portuguese `emprego-` becoming the
French `emploi-`.

**And the platform itself says the two instances are one codebase: three of the
five chrome `<loc>` are still in PORTUGUESE on this French host** —
`/candidatos/registe-se/sign_up`, `/empregador/registe-se`, `/ajuda` — beside
an English `/search-job-offers` and the bare root. *Only the advertisement
prefix is localised, which is the measured version of the claim above rather
than an inference from the brand.*

**The second advertisement form of the `.com` card has no counterpart here.**
*That card records 2 294 advertisements under a bare `/<slug>` beside its
38 588 prefixed ones, and the obvious worry is that `.ga` hides the same second
class. It does not: the non-`/emploi-`, non-`/emplois` remainder is **five**
`<loc>` and they are listed in full above — none is an advertisement.*

> **All of this is about the ROUTE and none of it about the EXTRACTION.** *No
> adapter was run against this host — re-verifying means **running** the
> adapter — and no advertisement page was opened, so what a `.ga` advertisement
> carries is not measured. `script: none` is the honest field; what this card
> buys is that the Gabonese adapter costs a parameter and not a rewrite.*

## The cadence is the network's, and it is already measured

`jobartis.py` carries `_PACE = Pace("www.jobartis.com", own=5.0)` under the
heading *one second between requests is too fast for this host*. **No
`Crawl-delay` is written on `.ga`, and a silent file does not say there is
none** — same operator, same stack, so the five seconds measured on `.com` are
the figure to honour here, not a cadence of ours.

*Gabon had no card and no issue of any kind before this one: a search of all
634 issues, by host and by country, returns zero for `jobartis` and for
`Gabon`.*
