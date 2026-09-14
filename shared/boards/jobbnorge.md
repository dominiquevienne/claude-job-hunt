# Board adapter — Jobbnorge (`www.jobbnorge.no`, Norway): the public-sector and academic board, its whole list in one API answer — 1 078 postings, 2 321 positions counted by the site and summed by the adapter, equal; the contact persons the ad's data carries never emitted

<!-- verified: 2026-09-14 -->

<!-- hosts: www.jobbnorge.no, publicapi.jobbnorge.no, id.jobbnorge.no -->
<!-- script: jobbnorge.py -->
<!-- host-forms: publicapi.jobbnorge.no, id.jobbnorge.no, www.jobbnorge.no -->
<!-- host-forms-basis: read — the search page writes `apiUrl = 'https://publicapi.jobbnorge.no/'` and the posting page `api: { url: 'https://id.jobbnorge.no/api/' }`; `jobbnorge.py` names all three as literals and the API's own `link` field carries `www.jobbnorge.no` · 2026-09-14 -->
<!-- countries: NO -->
<!-- content: measured · **`/v1/jobs/count` states 2 321 and `/v3/jobs?language=1` carries 1 078 postings whose `positionCount` sums to 2 321 — equal** — read by the declared client through the two requests the search page itself makes, 00:52 UTC; NTNU 73, Universitetet i Oslo 51, Indre Østfold kommune 50, Bodø kommune 43 among the employers; 6 postings abroad, 35 with a department shown as the employer; the rules — `www.jobbnorge.no` (60 B) refuses the posting PDF and nothing else, `publicapi.` and `id.` write no rule; **the ad's data route (`id.jobbnorge.no/api/joblisting?jobId=`) carries `contacts` — name, telephone, title — never emitted; the text scrubbed** · 2026-09-14 -->
<!-- witness: the site's own `/v1/jobs/count` — a count of POSITIONS, which the page itself replaces by the sum of `positionCount` — printed beside the postings emitted and the positions summed on every walk; «equal» when the sum is the count · 2026-09-14 -->

**Norway's public sector — universities, colleges, municipalities,
counties and the State recruit through Jobbnorge; 1 078 open postings
for 2 321 positions on the day, beside NAV's Arbeidsplassen
(`arbeidsplassen.md`), which aggregates them.** Issue #366. Measured
2026-09-14 00:49–00:52 UTC by the declared client, the guard on the exact
path on each of the three hosts.

## Rules and the routes

```
www.jobbnorge.no/robots.txt              200, 60 B — User-agent: * / Disallow: /ledige-stillinger/joblisting/pdf/*
publicapi.jobbnorge.no, id.jobbnorge.no   no rule written — an absence, certain, open
GET https://www.jobbnorge.no/             200 → /search, 24 657 B — «Jobbnorge.no trenger JavaScript»; apiUrl = 'https://publicapi.jobbnorge.no/'
GET https://publicapi.jobbnorge.no/v1/jobs/count          200 — 2321 (a bare integer)
GET https://publicapi.jobbnorge.no/v3/jobs?language=1     200 — {"jobs": [1 078]}: every open posting, no paging
GET https://www.jobbnorge.no/ledige-stillinger/stilling/306650   200, 14 202 B — an Angular shell («Laster...»); api: { url: 'https://id.jobbnorge.no/api/' }
GET https://id.jobbnorge.no/api/joblisting?jobId=306650&languageId=1   200, 8 031 B — components, jobGapComponents, contacts, positionCount, isPublished
```

**The adapter sends what the page sends** — the count, then the whole
list, in the page's own two requests; `--language 1` is bokmål, `2`
English, the API's own codes. The page prints `#hits` from the count and
then overwrites it with the sum of `positionCount`: **the count is a
count of positions**, and the adapter prints the three figures —
postings emitted, positions summed, positions counted — «equal» when the
sum is the count (it was). No Crawl-delay; 2 s is the adapter's own, and
a full list is two requests.

## The record, and the ad

```
{"id": 306650, "title": "Tannlege 100 % fast Kirkenes tannklinikk", "employer": "Finnmark fylkeskommune (FFK)", "regardDepartmentAsEmployer": false, "department": "Kirkenes Tannklinikk",
 "jobScope": "Heltid", "jobDuration": "Fast", "positionCount": 1, "promoted": true, "publicationDate": "19.08.2026", "deadline": "16.09.2026",
 "locations": [{"address": "Hessengveien 6", "area": "Hesseng", "municipality": "Sør-Varanger", "county": "Finnmark", "isDomestic": true, "isPrimary": true, "zipCode": "9912"}], "link": "https://www.jobbnorge.no/ledige-stillinger/stilling/306650"}
```

One record per posting: title, employer — **the department when the site
says `regardDepartmentAsEmployer`** (35 of 1 078 on the day; the
institution then in `employer_parent`), department, summary (scrubbed),
the primary location first (area, municipality, county; postal code), the
other locations, `abroad` (6 on the day), scope, duration, job type,
`positions`, `promoted`, publication and deadline as the API prints them
(«Løpende» is a deadline the site writes). The ad is the posting page's
own data route: the `components` heading and text, the titled
`jobGapComponents` («Om stillingen», «Arbeidsoppgaver»,
«Kvalifikasjonskrav» …) as `sections`, `positions`, `published`. **The
route also carries `contacts` — the persons to call, with their
telephone and title — which the adapter never emits; the text and the
summary are scrubbed of e-mail addresses and Norwegian telephone numbers;
`contacts_withheld` on every ad record.** The «Søk» application is on
`jobseeker.jobbnorge.no`, never touched; the posting PDF is the one path
the rules refuse, never requested.

```
jobbnorge.py search
[jobbnorge] 1 078 posting(s) emitted, 2 321 position(s) summed, site counts 2 321 positions — equal.
```

## Configuration

```yaml
boards:
  jobbnorge:
    enabled: true
    language: 1            # 1 = bokmål (default), 2 = English — the API's own codes
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `language` | no | `1` by default |

No credentials, no browser, no login. `search` is two requests; `ad` is
one.

## What is not established

- **Filters** — the page posts `municipality`, `county`, `category`,
  `employer` on `/v3/jobs`; the adapter takes the whole list and lets the
  user filter what it emitted.
- **The English list** — `language=2` is the API's; not read on the day.
- **What NAV re-lists** — Arbeidsplassen aggregates public postings; the
  overlap between the two boards is not measured here (each emits its
  own ids).
- **`components[].text` on most postings** — the ad's text lives in the
  titled sections on the one read; `description` falls back to them.

## 2026-09-14 — shipped

`search`: 1 078 of 1 078 postings, 2 321 positions summed against 2 321
counted; `ad` on one, no name and no number in the output. Two tests;
six mutations on a detached worktree (`python3 -B`), six red — the count
compared to the number of postings, the duplicate id kept, the department
not taken as the employer when the site says so, the contacts emitted,
the phone scrub dropped, the primary location not put first.
