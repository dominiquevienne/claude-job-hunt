# Board adapter — welcometothejungle.com

<!-- verified: 2026-09-02 -->

<!-- hosts: www.welcometothejungle.com -->
<!-- script: wttj.py -->
<!-- countries: FR -->
<!-- witness: SECOND READING, not conclusive. 88 913 on 2026-09-05 against 88 222 on 2026-09-02, +691. **42 637 entries carry a recent `lastmod`, so the net is 1.6 % of the movement** — weaker than turijobs at 12.3 % or platsbanken at 9 %. **And the argument closes on both branches**: if those dates are real the net is a sixtieth of the gross; if they are regeneration stamps the flow is not legible at all. What it does establish: 8 × 10 000 + 8 913 across nine `job-listings-*` children, union equal to the raw sum, and the index's fifteen other children are not advertisements · 2026-09-05 -->
**Re-tested 2026-09-02: the discovery half still works without a browser.** `robots.txt` answers 200 (216 bytes, `text/plain`) and the index it advertises, `/sitemaps/index.xml.gz`, answers 200 with **24 sub-sitemaps**. The split this file documents — plain HTTP to discover, browser to read — is unchanged.

**88 222 ads** in the site's own sitemaps, about **two thirds of them
French-language** — the largest French inventory this repository had left
uncovered. Startups, scale-ups, and also Carrefour, Thales, Vinci and the
Ministère des Armées: it stopped being a tech board some time ago.

**Everything here was verified on 2026-09-01**, from a script for the sitemaps
and from the user's own browser for the ads.

## This adapter is cut in two, and the cut is not a style choice

```
discovery  →  skills/job-scan/scripts/wttj.py    plain HTTP, no browser
reading    →  the user's browser session, one navigation per ad
```

`robots.txt` publishes a sitemap index, and the sitemaps are served to a plain
client without complaint. **Every HTML page is another matter**: it answers
`HTTP 202` with the header `x-amzn-waf-action: challenge` — an AWS WAF
challenge, delivered as a **2xx status with a body that contains no ad**. Not a
403, not a block page. A naive client reads 2xx as success and records nothing.

Slowing down does not clear it: measured at one request every 6 s and again at
one every 12 s, **10 of 10 were challenged**. The browser passes it, because
passing it is what a browser does — the same position as `indeed.md`, where the
challenge is solved by the user's own session and never by the plugin.

### And in-page `fetch()` is not the shortcut it was on Figaro Emploi

`figaro-emploi.md` runs its whole sweep as `fetch()` calls from one open tab,
because there the page's clearance carries. **Here it does not.** Measured from
a page already loaded on the origin: the first **two** fetches return the ad,
and every one after that comes back `202 challenge` — at 2.5 s spacing, from
inside the browser, on the same origin. Two sampling runs died that way before
the pattern was clear.

**Navigation, by contrast, is reliable**: four consecutive page loads, four ads
rendered, no challenge. So the reading step is one navigation per ad. That is
slower than a fetch loop and it is the only thing that works.

*(Two boards, two opposite answers to the same question. Test the fetch route
before assuming it, and stop after the second success rather than the first.)*

## Discovery

```bash
python3 "${JOB_HUNT_ROOT}/skills/job-scan/scripts/wttj.py" \
  discover --locale fr --since 2026-09-01 --limit 200

python3 "${JOB_HUNT_ROOT}/skills/job-scan/scripts/wttj.py" \
  companies --locale fr --top 30
```

Nine sitemap files of 10 000 URLs each. What is known **before any fetch**:

| Field | From |
| :-- | :-- |
| `company_slug` | the URL path — this board names the employer in the URL |
| `locale` | `fr` or `en` — **a language, not a country**, see trap 1 |
| `lastmod` | the sitemap, and it is real: **7 691 distinct values** in one 10 000-URL file |

That `lastmod` is worth the whole discovery step. `figaro-emploi.md` publishes
one identical timestamp across 30 000 entries; here it is per ad, so
`--since` genuinely narrows a re-scan to what changed.

File 0 alone holds **1 048 French-locale companies**: Groupement Les
Mousquetaires 839 ads, Carrefour 240, Ministère des Armées 223, Vinci
Construction 183, Thales 170.

## Reading, in the browser

Navigate to the ad URL, wait for load, then read the `JobPosting` from
`script[type="application/ld+json"]`. The ad page also redirects
`/companies/` to `/companies-v1/`; follow it, the content is the same.

Measured across **17 ads** — the total that came back before the WAF ended four
sampling runs, which is itself the measurement that shaped this adapter:

| Field | Rate | Example |
| :-- | :-- | :-- |
| `hiringOrganization.name` | every ad | Thales, Groupement Mousquetaires |
| **`hiringOrganization.sameAs`** | every ad | `https://www.mousquetaires.com/` |
| `addressCountry` / `postalCode` | every location | FR / 78990 |
| **`streetAddress`** | every location | and it is the job's, not a head office |
| `industry` | every ad | *Grande distribution, Agroalimentaire* — real sectors |
| `qualifications` | every ad | |
| `experienceRequirements` | most | |
| `description` | every ad | **563 to 5 618 characters** |
| `baseSalary` | about a third | 1 900, 2 095 |

**`sameAs` is the employer's own website**, and no other board here publishes
it. For `cover-letter` that is the difference between writing about a company
and reading about it first.

`jobLocation` is an **array**, so a multi-site ad is native rather than hidden
in a tooltip the way `softy.md` hides its seven communes.

In the ledger: `wttj:<company_slug>/<slug>`.

## Traps

**1. A locale is not a country.** The `/fr/` prefix is the page's language.
Measured on six `/fr/` ads taken at random: **Cologne (DE), Rio de Janeiro
(BR), Fort-de-France (MQ)** and three in metropolitan France. Filtering on
`/fr/` and calling the result French is wrong twice over — it admits Germany
and Brazil, and it would exclude an English-language ad in Paris.
**`addressCountry` on the ad page is the only answer**, which means the country
is not known until the ad is read.

**2. The city is in the URL and cannot be taken from it.** The tail is
`<job>_<city>_<id>` on some ads and `<job>_<city>` on others, and `_` occurs
inside job slugs too. Measured on 10 000 URLs: **6 576 end in something
id-shaped and 3 424 do not**, with no rule separating them. `wttj.py` emits
`city_from_url: null` rather than guess; the location comes from the ad page.

**3. `validThrough` is `datePosted` + 90 days.** On **14 of 14** ads where both
were present. A formula, like `hellowork.md` (+30) and `figaro-emploi.md` (+90).
Not an expiry, and not to be recorded as one.

**4. The WAF answers 2xx.** Repeating the point because it is the one that will
bite a future maintainer: `202` with `x-amzn-waf-action: challenge`, a body of
0 or 2 450 bytes, no error to catch. `wttj.py` checks that header on every
sitemap request and dies loudly if it ever appears there.

**5. And a zero from a sitemap is a failure to read until proved otherwise.**
The discovery side reads `.gz` files, and **a gzip layer read as text yields no
`<loc>` from a perfectly healthy index** — a 200, a plausible body, the wrong
content, nothing raised. `wttj.py` treats zero URLs from the index or from any
sitemap as an error naming decompression, never as an empty board: an empty
board would still be a `<urlset>` with tags in it. The distinction is the
message.

*(Added after a sibling session hit exactly this on another board's sitemap —
`/sitemap.gz`, 286 bytes, zero `<loc>` read as text and five sub-sitemaps once
decompressed. Same species as trap 4 by its signature: the status code is not
the answer, only the payload is.)*

*(A sibling session hit the identical signature on `tanqeeb`, an unrelated
board, the same day — 202, empty body, same header. It is worth recognising on
sight.)*

## Applying

The apply flow is the employer's, reached from the ad page. **The plugin does
not create accounts and does not fill credential fields.** Hand the user the ad
URL — and the `sameAs` link, which is the company's own site.

## Pace, and the note on access

Discovery is nine requests for the whole board, on the route `robots.txt`
advertises. Reading is one navigation per ad in the user's own session, so it is
paced by the person, not by a loop: narrow with `--company` and `--since`
before reading anything. The search page — `Disallow: /*?` and
`*/jobs?query=*` — is never requested.
