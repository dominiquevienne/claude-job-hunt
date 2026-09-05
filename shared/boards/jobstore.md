# Board adapter — Jobstore

<!-- verified: 2026-09-02 -->

<!-- hosts: www.jobstore.com -->
<!-- script: jobstore.py -->
<!-- countries: * -->
<!-- content: measured · 52 128 advertisements on the Swiss site, from the six `job-*.xml` children; the aggregator runs 26 country sites and only Switzerland was counted · 2026-09-02 -->
<!-- witness: none found — the card records no site-served total for the Swiss site, and the one number the index offers is the sum of all twelve children, **250 000+, five times the truth**: a decoy rather than a witness · 2026-09-02 -->
<!-- overlap: hiringcafe.md · about 25 % of Swiss ads shared · 2026-09-03 -->
<!-- overlap: jobup.md · 15.5 % of Swiss ads shared · 2026-09-03 -->
<!-- overlap: jobs-ch.md · 18.6 % of Swiss ads shared · 2026-09-03 -->
An aggregator running **26 country sites** off one host, `www.jobstore.com/<cc>/`.
Switzerland carries **52 128 ads**.

**It is a hybrid adapter, and not by preference.** Discovery is plain HTTP —
sitemaps and the search page both answer 200. **Reading an ad needs the user's
own Chrome**: the ad page answers a plain client with **HTTP 403 and a
5 832-byte "Just a moment…" interstitial**, and renders normally in a real
browser.

That split is the layer rule from `shared/robots-policy.md` doing its work: a
403 with an interstitial sits **above** the browser, so a browser changes it.
Nothing else here does.

**Everything below was verified on 2026-09-02** — the sitemaps and search over
plain HTTP, the ad page and its apply button in Chrome.

## Count `job-*.xml` and nothing else

The Swiss sitemap index declares twelve sub-sitemaps. **Six of them are ads.**

| File | `<loc>` | What they are |
| :-- | --: | :-- |
| `job-1.xml` … `job-5.xml` | 10 000 each | **ads** |
| `job-6.xml` | 2 128 | **ads** |
| `jobs-search-1.xml` … `-4.xml` | 50 000 in the first alone | **query landing pages** |
| `employer-1.xml` | 3 876 | employer pages |
| `salary-1.xml` | 1 984 | salary pages |

**`job-*.xml` totals 52 128.** Summing every `<loc>` in the index reports more
than **250 000 Swiss ads** — five times the truth, with no error and no
warning anywhere.

This is the mistake to guard first, because it is the only one here that
produces a **confident wrong number**. `jobstore.py count` reads `job-*.xml`
only, prints the per-file totals, and names the files it skipped.

## What plain HTTP can see, and what it cannot

```
GET /ch/jobs/search?q=engineer&l=Switzerland&page=2   → 200, 226 KB
GET /ch/sitemap/job-1.xml                             → 200 application/xml
GET /ch/job/l27804407/technical-coordinator-job       → 403 + interstitial
```

The search page carries an `application/ld+json` **`ItemList` of URLs and
nothing else** — no title, no employer, no location, no salary. So the HTTP
half yields **an id and a slug**, and the card says exactly that: it carries
`title_from_slug`, **named for what it is**, a guess derived from a URL rather
than a title the board published. `needs_browser_to_read: true` rides on every
row.

Pagination works — `page=2` returns a different set of 15.

## What the browser sees

The same ad, opened in Chrome, renders in full after the interstitial clears:
title, employer with a link to its company page and a review score, job type
and level, location, **a salary range** — *CHF 6 000 – CHF 8 500 (Monthly)* —
and the whole description.

So the ad is worth reading; it just cannot be read without the browser. The
handles are ordinary headings and labelled blocks (*Job Type / Job Level*,
*Job Location*, *Salary Range*), plus the employer link
`/<cc>/company/<id>/<slug>`.

## The URL that goes in the ledger is a Jobstore URL

`https://www.jobstore.com/<cc>/job/l<id>/<slug>-job`, and the card marks it
`url_is_jobstore: true`.

**It must never be presented as the employer's posting.** This board is an
aggregator; the ad it shows is a copy, and handing the user a Jobstore link
labelled as the employer's would misdescribe where they are about to apply.

## "Apply on company site" does not go to the company site

The ad page shows a button reading **"Apply on company site"**, twice. Its
`href`, read from the DOM without clicking:

```
https://www.jobstore.com/jobseeker/apply/l27804407
```

**A Jobstore path** — and `robots.txt` disallows `/*/jobseeker/apply/` and
`/*/guest/apply/`. Applying requires a **Jobstore account**.

**The plugin corrects that label rather than repeating it.** When it hands a
Jobstore ad to the user it says: this is an aggregator's copy, applying goes
through a Jobstore account, and the employer's own posting is elsewhere — very
often on a board this repository already reads. **The plugin does not create
accounts and does not fill credential fields.**

## Scope: the overlap is small, so the reach is real

Measured against the boards already covered: about **a quarter overlap with
HiringCafe, 18.6% with jobs.ch, 15.5% with jobup**. Of 1 056 Swiss employers
those three surface, **82.5% do not appear on Jobstore** — and the reverse
holds, which is why it is worth having.

## Configuration

```yaml
boards:
  jobstore:
    enabled: true
    countries: ["ch"]           # any of the 26
    searches:
      - keyword: "engineer"
        location: "Switzerland"
    pages: 2
    delay: 1.5
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `countries` | yes | `my sg id ph hk au nz th vn us uk nl es ae in ca za ie ch no dk at se pt pl il` and one more, all declared in `robots.txt` |
| `searches` | no | `keyword` → `q=`, `location` → `l=`. Without one, use `corpus` |
| `pages` | no | 15 ad URLs a page |
| `delay` | no | Seconds between requests, default 1.5 |

**Prerequisites are split.** `count`, `search` and `corpus` need nothing —
no key, no cookie, no browser. **Reading an ad needs the Claude extension for
Chrome**; without it, the sweep still discovers ads and the user opens them
themselves.

## Zero-shaped answers

**1. A sitemap index whose files are mostly not ads.** Four of twelve carry
200 000 landing pages. Counting them inflates the board fivefold, silently.

**2. HTTP 403 with an interstitial on the ad page**, while the search page and
the sitemaps answer 200 on the same host. Not a refusal of the sweep — a
client filter, above the browser layer.

**3. An `ItemList` that looks like structured data and carries only URLs.**

**4. A button labelled "Apply on company site" that links to Jobstore.**

**5. A title that came from a URL slug.** Named `title_from_slug` so nothing
downstream treats it as the board's own.

## Pace

No published limit. About 20 requests at 1.5 s apart raised nothing, and the
`job-*.xml` files are 1.5 MB each — `corpus` is heavy in bytes and light in
requests, six calls for 52 128 ads.

## Verification

```bash
S=skills/job-scan/scripts/jobstore.py
python3 $S count  --country ch                      # 52 128, and it names the files it skipped
python3 $S search --country ch --keyword engineer --location Switzerland --limit 3
python3 $S corpus --country ch --limit 3
```
