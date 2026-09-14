# Board adapter — Práca za rohom (`www.pracazarohom.sk`, SK): Alma Career's «work around the corner» board, one Next.js stack with Práce za rohem (`pracezarohem.md`, the Czech host) by `pracezarohem.py --host sk` — «18 586» stated by the page's own state on 2026-09-14 and printed beside every walk; the ad's `recruiter` object never emitted

<!-- verified: 2026-09-14 -->

<!-- hosts: www.pracazarohom.sk -->
<!-- script: pracezarohem.py -->
<!-- host-forms: www.pracazarohom.sk -->
<!-- host-forms-basis: read — every card links `/dl/jd/<id>` relative to the host; `pracezarohem.py` names the host in `BOARDS["sk"]` and builds every address on it · 2026-09-14 -->
<!-- countries: SK -->
<!-- content: measured · **`/ponuky` (200) is a Next.js page whose `__NEXT_DATA__` carries 50 adverts and `adverts.numFound` — 18 586 on the day — and a count per region (Bratislavský 6 666, Trnavský 2 058, Nitriansky 2 024, Žilinský 1 949 … 8 regions); `?page=2` carries 50 other adverts; 100 read in two pages** — read by the declared client, the guard on the exact path (the rules, 270 B and the same on both hosts: `/b2c`, `/apply`, `/cv`, `/deeplink*` refused; the sitemaps named are 90 files of ~49 000 FACET rows each — region × profession listings, and the Slovak host serves the Czech ones — not ads, not read); a card: id `PROF-<uuid>` (from Profesia), title, company, place and address, the salary the card prints («od 1 000 €» on the cards, no period), the age in the site's words, `personalAgency`, the employer's Atmoskop rating; the ad `/dl/jd/<id>` (the same template) carries `advert` in its state — title, company, `salaryDetailed`, labelled `jobProperties`, `jobText`, locations, `validEnd`, `replyMethod` — **and `recruiter` {name, email, phone}: never emitted; the texts scrubbed of e-mail addresses and Czech/Slovak telephone numbers; the app deep link (`b2c.pzr.sk`) and the `?mode=b2b` address never followed** · 2026-09-14 -->
<!-- witness: the page's own `adverts.numFound` — printed beside every walk with the regions the site counts («… the site states 18 586 on www.pracazarohom.sk/ponuky — walked by request, not a shortfall»); a page serving page 1's adverts again exits 6, as does a page without an advert in its state · 2026-09-14 -->

**Práca za rohom is Alma Career's board of everyday jobs near home — shop staff,
warehouses, drivers, care, hospitality — 18 586 advertisements stated on the
day, beside Profesia (`profesia.md`) and Služby zamestnanosti (`sluzbyzamestnanosti.md`).** Issue #347. Measured 2026-09-14 03:0x UTC by the declared
client, the guard on the exact path before each request. One script for
the two hosts: `--host cz` (the default) and `--host sk`.

## One stack, two hosts

```
www.pracazarohom.sk/robots.txt                200, 270 B — User-agent: *: Disallow /b2c, /apply, /cv, /deeplink, /deeplink2, /deeplinks; Sitemap ×3 (.cz, .pl, .sk)
GET https://www.pracazarohom.sk/ponuky           200 — __NEXT_DATA__: page /advrts/[[...slugs]], adverts.adverts[50], adverts.numFound 18 586, navigators.location (a count per region)
GET https://www.pracazarohom.sk/ponuky?page=2    200 — 50 other adverts, the same numFound
GET https://www.pracazarohom.sk/sitemap.xml    200, 10 039 B — 91 files: sitemap-base.xml (the site's pages) and sitemap1…90.xml of ~49 000 /nabidky/<region>/<profession> facet rows each — not ads
GET https://www.pracazarohom.sk/dl/jd/PROF-d9f823a4-c15b-4140-849b-6c6a3dd45657   200 — __NEXT_DATA__: advert {title, company, recruiter, location(s), salary, salaryDetailed, descFields, validEnd, replyMethod, atmoskop}, appLink, cognitoToken
```

| named per board | Czechia (`cz`, default) | Slovakia (`sk`) |
| :-- | :-- | :-- |
| host · country · language | `www.pracezarohem.cz` · CZ · cs | `www.pracazarohom.sk` · SK · sk |
| the listing | `/nabidky` | `/ponuky` |
| `source` / ledger key | `pracezarohem` | `pracazarohom` |
| stated on the day | 20 758 | 18 586 |

Everything else is one code path: the page's state, 50 a page, `?page=N`
from one with the guard against a pager that does not page, **only
`page` ever sent** (the `?mode=b2b` address and the app's parameters are
refused before the gate), `--region <slug>` on the site's own region
slugs (`hlavni-mesto-praha`, `bratislavsky` …), `--pages` 3 unless told.

```
pracezarohem.py list --host sk --pages 2
[pracezarohem] 100 emitted over 2 page(s) of 50, the site states 18 586 on www.pracazarohom.sk/ponuky — walked by request (--pages/--limit), not a shortfall.
[pracezarohem] regions the site counts: Bratislavský 6 666, Trnavský 2 058, Nitriansky 2 024, Žilinský 1 949 … 8 regions.
[pracezarohem] the ad's `recruiter` object (name, e-mail, telephone) is never emitted; texts scrubbed; the app deep link and the b2b address never followed.
```

## The ad — and the recruiter it carries

The ad's state is the record: title, company (and its web when given),
locations, `salaryDetailed` (a text, read to a range without a period —
«od 1 000 €» is a floor, not a range), the labelled `jobProperties`
(Úvazek, Smlouva, Benefity, Vzdělání, Jazyky …) as `properties`, the
`jobText` as `description` and the `companyText` as `employer_text`,
`validEnd`, `replyMethod`, `cvRequired`, the employer's Atmoskop
rating. **The state also carries `recruiter` — {name, email, phone,
initials} — which is never emitted; description and employer text are
scrubbed of e-mail addresses and Czech and Slovak telephone shapes;
`contacts_withheld` on every record.** The `appLink` into the mobile app
and the `webUrl?mode=b2b` address are never followed.

## Configuration

```yaml
boards:
  pracazarohom:
    enabled: true
    host: sk
    region: bratislavsky     # optional
    pages: 3
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `host` | yes | `sk` (or `www.pracazarohom.sk`) |
| `region` / `pages` / `limit` | no | the site's region slug; 50 a page |

No credentials, no browser, no login. `list` is one request a page; `ad`
one.

## What is not established

- **The whole list** — 18 586 stated, 100 read; the pager goes on and was not
  walked to its end.
- **The facet sitemaps** — 90 files, ~4.4 million rows of region ×
  profession listings; whether any file lists ads was not checked
  beyond the first (49 197 facet rows, no ad).
- **The card ids' origins** — `PZRG`, `G2`, `PROF` prefixes look like
  the source boards of the Alma group (Práce za rohem, Jobs.cz/Teamio,
  Profesia); read as opaque keys.
- **The Polish sibling** (`www.pracazarogiem.pl`, named in the rules) —
  not measured; likely the same stack.

## 2026-09-14 — shipped

`list`: 100 in 2 pages against 18 586 stated, every card with an employer
and a place, the regions printed; `ad`: one, its recruiter withheld and
its texts scrubbed, no name, number or address in the output. Two tests;
six mutations on a detached worktree (`python3 -B`), six red — the
host's listing path not used, the key not on the record, `numFound` not
read, «od» read as a range, the recruiter emitted, the text not scrubbed.
