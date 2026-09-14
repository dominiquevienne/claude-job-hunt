# Board adapter — Práce za rohem (`www.pracezarohem.cz`, CZ): Alma Career's «work around the corner» board, one Next.js stack with Práca za rohom (`pracazarohom.md`, the Slovak host) by `pracezarohem.py --host cz` — «20 758» stated by the page's own state on 2026-09-14 and printed beside every walk; the ad's `recruiter` object never emitted

<!-- verified: 2026-09-14 -->

<!-- hosts: www.pracezarohem.cz -->
<!-- script: pracezarohem.py -->
<!-- host-forms: www.pracezarohem.cz -->
<!-- host-forms-basis: read — every card links `/dl/jd/<id>` relative to the host; `pracezarohem.py` names the host in `BOARDS["cz"]` and builds every address on it · 2026-09-14 -->
<!-- countries: CZ -->
<!-- content: measured · **`/nabidky` (200) is a Next.js page whose `__NEXT_DATA__` carries 50 adverts and `adverts.numFound` — 20 758 on the day — and a count per region (Hlavní město Praha 3 607, Jihomoravský 2 756, Jihočeský 1 109 … 14 regions); `?page=2` carries 50 other adverts; 100 read in two pages** — read by the declared client, the guard on the exact path (the rules, 270 B and the same on both hosts: `/b2c`, `/apply`, `/cv`, `/deeplink*` refused; the sitemaps named are 90 files of ~49 000 FACET rows each — region × profession listings, and the Slovak host serves the Czech ones — not ads, not read); a card: id `PZRG-<uuid>` (the board's own), `G2-<n>-…` (from Teamio/Jobs.cz), title, company, place and address, the salary the card prints («25 190 - 36 210 Kč hrubého», no period), the age in the site's words, `personalAgency`, the employer's Atmoskop rating; the ad `/dl/jd/<id>` (33 837 B) carries `advert` in its state — title, company, `salaryDetailed`, labelled `jobProperties`, `jobText`, locations, `validEnd`, `replyMethod` — **and `recruiter` {name, email, phone}: never emitted; the texts scrubbed of e-mail addresses and Czech/Slovak telephone numbers; the app deep link (`b2c.pzr.sk`) and the `?mode=b2b` address never followed** · 2026-09-14 -->
<!-- witness: the page's own `adverts.numFound` — printed beside every walk with the regions the site counts («… the site states 20 758 on www.pracezarohem.cz/nabidky — walked by request, not a shortfall»); a page serving page 1's adverts again exits 6, as does a page without an advert in its state · 2026-09-14 -->

**Práce za rohem is Alma Career's board of everyday jobs near home — shop staff,
warehouses, drivers, care, hospitality — 20 758 advertisements stated on the
day, beside Jobs.cz (`jobscz.md`), Prace.cz (`pracecz.md`) and the Úřad práce (`uradprace.md`).** Issue #355. Measured 2026-09-14 03:0x UTC by the declared
client, the guard on the exact path before each request. One script for
the two hosts: `--host cz` (the default) and `--host sk`.

## One stack, two hosts

```
www.pracezarohem.cz/robots.txt                200, 270 B — User-agent: *: Disallow /b2c, /apply, /cv, /deeplink, /deeplink2, /deeplinks; Sitemap ×3 (.cz, .pl, .sk)
GET https://www.pracezarohem.cz/nabidky           200 — __NEXT_DATA__: page /advrts/[[...slugs]], adverts.adverts[50], adverts.numFound 20 758, navigators.location (a count per region)
GET https://www.pracezarohem.cz/nabidky?page=2    200 — 50 other adverts, the same numFound
GET https://www.pracezarohem.cz/sitemap.xml    200, 10 039 B — 91 files: sitemap-base.xml (the site's pages) and sitemap1…90.xml of ~49 000 /nabidky/<region>/<profession> facet rows each — not ads
GET https://www.pracezarohem.cz/dl/jd/G2-2001321946-aden_brand0   200 — __NEXT_DATA__: advert {title, company, recruiter, location(s), salary, salaryDetailed, descFields, validEnd, replyMethod, atmoskop}, appLink, cognitoToken
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
pracezarohem.py list --host cz --pages 2
[pracezarohem] 100 emitted over 2 page(s) of 50, the site states 20 758 on www.pracezarohem.cz/nabidky — walked by request (--pages/--limit), not a shortfall.
[pracezarohem] regions the site counts: Hlavní město Praha 3 607, Jihomoravský 2 756, Jihočeský 1 109 … 14 regions.
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
  pracezarohem:
    enabled: true
    host: cz
    region: hlavni-mesto-praha     # optional
    pages: 3
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `host` | yes | `cz` (or `www.pracezarohem.cz`) |
| `region` / `pages` / `limit` | no | the site's region slug; 50 a page |

No credentials, no browser, no login. `list` is one request a page; `ad`
one.

## What is not established

- **The whole list** — 20 758 stated, 100 read; the pager goes on and was not
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

`list`: 100 in 2 pages against 20 758 stated, every card with an employer
and a place, the regions printed; `ad`: one, its recruiter withheld and
its texts scrubbed, no name, number or address in the output. Two tests;
six mutations on a detached worktree (`python3 -B`), six red — the
host's listing path not used, the key not on the record, `numFound` not
read, «od» read as a range, the recruiter emitted, the text not scrubbed.
