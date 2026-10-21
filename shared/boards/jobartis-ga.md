# Board measurement — Jobartis Gabon (`www.jobartis.ga`): 228 advertisements, served by `jobartis.py --country GA` since 2026-10-21 (#1172) — the sitemap shape transposes, the VOCABULARY does not, and the corpus is frozen in 2019

<!-- verified: 2026-10-21 -->

<!-- hosts: www.jobartis.ga -->
<!-- script: jobartis.py -->
<!-- countries: GA -->
<!-- content: measured · **228 advertisements under `/emploi-<slug>`** in the declared `sitemap.xml.gz` — a flat `urlset` of **339 `<loc>`, all 339 distinct**, with no child sitemap and **no `<![CDATA[`** (checked, because that trap returns zero on a 343 977-byte file for `cabinets-es.md`). The classification is **exhaustive and its classes are disjoint: 228 advertisements + 106 faceted listing pages under `/emplois/…` + 5 chrome pages = 339, intersection zero.** **The apex redirects to `www`**: `bin/fetch-body.py https://jobartis.ga/` recorded `final_url: https://www.jobartis.ga/`, and the guard queried on the apex names `www.jobartis.ga` as the host that answered — so the body came from the host the guard answered for. `m.jobartis.ga` is linked from the root and is not used; `assets.jobartis.com` serves the stylesheet and the favicons and is the NETWORK's asset host, never a board host. Root 200, 41 690 B, French, `<title>` «Offres d'emploi | Jobartis Emplois | Emplois au Gabon». **EXTRACTION MEASURED 2026-10-21 (#1172), four advertisement pages: the STRUCTURE transposes and the VOCABULARY does not.** `data-job-id` 4/4, `<h1>` 4/4, the `data-label` pair motif yields 13 fields on 4/4, no `ld+json` — but all ten field labels are FRENCH and both Portuguese state markers are ABSENT on 4/4, so the Angolan parser run unchanged here emits **10 of 10 fields null and `state: null`** against **0 of 11 null and `state: closed`** with the per-instance table. **And the corpus is FROZEN: `lastmod` 2019-02-20 .. 2021-03-26, 227 of 228 dated 2019, 16 distinct dates** — 4 of 4 sampled pages carry «Offre d'emploi fermée», the most recent advertisement in the corpus included · 2026-10-21 -->
<!-- witness: none the site states — no total on the root and none on `/emplois`; 228 is a figure about the FILE, being its 339 `<loc>` after the other two classes are named and enumerated. Single locale, so no per-language inflation: 339 `<loc>` for 339 distinct, against the 416-for-100 shape · 2026-10-21 -->
<!-- route: http · 228 · 2026-10-21 -->
<!-- closure: detail · «Offre d'emploi fermée» on the ADVERTISEMENT page, 4 of 4 sampled on 2026-10-21 (#1172) — the first, the median and the last of the sitemap order plus the single most recent advertisement in the corpus. **The listing cannot carry closure here by construction**: the enumerator is `sitemap.xml.gz` and it holds `<loc>` and `<lastmod>` and nothing else. **And the OPEN marker is UNMEASURED** — no sampled page carries one, so a page without the closed marker reports `state: null` and is never called open · 2026-10-21 -->

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

## The reserve is lifted, and one clause of this card was wrong

**CORRECTION 2026-10-21 (#1172), measured by RUNNING the adapter and not by re-reading this card.** The title said the Angolan adapter was «ONE locale constant away», and the paragraph below reserved only the EXTRACTION. *The reserve was right and the figure in the title was not:* the prefix is one constant, and beside it stand **ten French field labels, a French closed marker, a deny-list entry the Angolan one does not have (`emplois`), an `Accept-Language`, a country code and a ledger namespace**. **What was right is the thing that decided: the URL SHAPE is shared, so the ROUTE transposes and the cost is a TABLE rather than a rewrite** — the `hays-fr` case, and the measurement did not move it towards `randstad`.

**`/emplois` is why the table is per-instance and not a shared default.** The Angolan deny-list knows `vagas-emprego` and not `emplois`, so the Angolan rules applied here would have promoted the French listing index to an advertisement — one false advertisement, found before it was written. *And anything single-segment that is neither the prefix nor a known chrome page is now counted and NAMED rather than dropped as chrome or promoted: a deny-list bets the problem was enumerated, and this one was enumerated on 2026-10-21.*

**AND THE TWO INSTANCES MUST NOT SHARE A LEDGER NAMESPACE.** Both number their advertisements with a bare `data-job-id` — 59272 on `.com`, 37514 here — and nothing says the sequences are disjoint; a collision would file a Gabonese vacancy over an Angolan one and the ledger would look consistent. *`source` and `ledger_id` carry `jobartis-ga`; `.com` keeps `jobartis`, so no existing ledger key moves.*

**THE OPEN MARKER IS UNMEASURED HERE, AND DECLARED RATHER THAN GUESSED.** No sampled page carries one, so the instance table holds `None` and a page without «Offre d'emploi fermée» reports `state: null` — never «open» by default. *Reading one host's rule onto another declares every closed post open, and the plugin then drafts for a vacancy that is gone.*

**A FROZEN CORPUS IS NOT A SHUT HOST.** *«À priori, il n'y a jamais aucune raison pour que nous n'utilisions pas un board», and only the owner declares a host shut (§2 sexies).* What it changes is that `list` prints the age of what it returns, **derived from the file in hand rather than written down** — a figure that prescribes goes stale with its input, which is why the `.com` docstring's 18.5 % is history and this one is computed.

**AND `/curriculum-vitae/*` IS REFUSED IN WRITING** by this host's rules file. Nothing the adapter fetches goes near it — the sitemap carries no such path — and it is recorded because the opposite case cost a measurement elsewhere: a Tajik board whose rules refused NOTHING exposed 34 894 candidate CVs, and there the path filter was a safety condition rather than an optimisation.

> **What follows was true when this card was written, and its first sentence no longer is — kept because a correction cites what it corrects.**
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

## The false half of a measured sentence, and it is mine

**CORRECTION 2026-10-21: Gabon ALREADY had a card.** *This card said «Gabon had
no card and no issue of any kind before this one». The ISSUE half was measured —
a search of all 634 issues, by host and by country, returns zero for `jobartis`
and for `Gabon` — and the CARD half was **never measured at all**: it was
extrapolated from the issue search, which answers a different question.
Measured on both sides of the commit, by generating this country's fragment
from `shared/boards/` each time: **`emploi-ga.md` has declared `GA` since
2026-09-12**, with `route: browser · 67`.*

> **And the consequence is a ratio that does NOT move while a whole adapter
> lands.** *`fait 1 / faisable 1 / total 1` before, `fait 2 / faisable 2 /
> total 2` after — **100 % on both sides**, both terms `+1`. Naming the quotient
> alone would read tomorrow as a country that learned nothing, which is why a
> republished ratio announces the MOVEMENT OF ITS TWO TERMS and never the
> quotient.*

**So `jobartis.py` is Gabon's first SCRIPT and not its first adapter.** *The
owner's decision of 2026-09-08 counts the two together — «un adaptateur non-web
et un adaptateur web lui permettent d'extraire la MÊME donnée. La distinction
est liée aux CGU des sites» — so a browser route already delivered here, and
«first adapter, all types» is the one phrasing that is wrong.*

*The claim travelled from this card into a peer's message and its journal bullet
before anyone checked it. That is what an unmeasured half of a measured sentence
does: the measured half carries the unmeasured one.*
