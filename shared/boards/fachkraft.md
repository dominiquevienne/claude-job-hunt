# Board adapter — fachkraft.ch / sta.jobs

<!-- script: fachkraft.py -->
<!-- verified: 2026-09-02 -->
<!-- countries: CH -->

**Re-verified 2026-09-02**: **3 580 of 3 580 ads**, and the run still warns that keys are domain-scoped without `--with-ref` because the numeric id differs between domains.

**One board, several brand domains — and `fachkraft.ch` is the umbrella.**
Corrected 2026-08-29: this file first said "one board, two domains", which was
incomplete. `www.fachkraft.ch` carries the listings of at least three brands,
each with its own reference suffix and its own front door:

| Domain | Reference suffix | Relationship to fachkraft.ch |
| :-- | :-- | :-- |
| `www.fachkraft.ch` | serves **all** of them | the umbrella — **sweep this one** |
| `www.sta.jobs` | `-STAZH`, `-STALU`, `-STAOF` | a subset |
| `www.stellenpartner.ch` | `-SPFFR`, `-SPZZG` | a subset, **501 of 501 slugs also on fachkraft.ch** |

The containment is one-way: `21790-SPFFR` resolves on stellenpartner.ch **and**
on fachkraft.ch, while `19868-STAZH` answers `410` on stellenpartner.ch and
`21790-SPFFR` answers `410` on sta.jobs.

**So sweep `fachkraft.ch` and nothing else.** Enabling a brand domain as well
records every one of its ads a second time — the numeric ids are per-domain (see
below), so without `--with-ref` the ledger cannot tell they are the same ad.

A staffing **agency** board, like `michaelpage.md`: `hiringOrganization` is
*STA Personal AG* on every ad and **the client employer is never named**.

Read by `skills/job-scan/scripts/fachkraft.py`. Server-rendered HTML with a
`JobPosting` block on every ad. **No key, no cookie, no browser.**

**Verified 2026-08-29** on both domains — 3 534 ads read from fachkraft.ch,
1 835 from sta.jobs.

## The whole board arrives in one request

`/stellen/` ships **every** card in its markup and reveals 20 at a time
client-side (`data-load-more="20"`, the rest `style="display:none"`). So there is
nothing to paginate, and a single fetch is the complete board.

Each card carries title, canonical URL, canton, region, contract type, start
date and a description teaser — enough to score on without opening the ad.

> The links are **absolute** (`href="https://www.fachkraft.ch/stellen/…"`). A
> relative-href regex finds zero and reads as an empty listing; that is what the
> first look at this board concluded. And `data-job-id` is **not** the ad id — it
> has 118 distinct values across 3 534 cards, because it identifies the sector.

## The id that crosses domains, and the one that does not

**The per-domain numeric id is not shared.** Of 3 534 fachkraft ids and 1 835
sta.jobs ids, **zero** are common — for jobs whose slugs are otherwise
identical (`anlagen-und-apparatebauer-in-aarau-dauerstelle-<id>`). Each domain
numbers the same job its own way.

**The portable key is the `<n>-STAxx` reference**, and it resolves on both:

```
$ fachkraft.py resolve --ref 19868-STAZH
{"slug": "polymechaniker-…-295702", "url": "https://www.fachkraft.ch/…"}
$ fachkraft.py resolve --ref 19868-STAZH --domain www.sta.jobs
{"slug": "polymechaniker-…-108097", "url": "https://www.sta.jobs/…"}
```

Same ad, same reference, **different slugs**. It is also the form job-room
publishes as its `externalUrl`, so it is the key that survives every crossing.

```
fachkraft:<n>-STAxx            e.g. fachkraft:19868-STAZH
```

**The listing does not carry the reference** — only the ad page does. So
`list --with-ref` fetches it, at **one request per kept ad**. Without the flag
the row falls back to `fachkraft:<domain>:<numeric id>`, carries
`portable_key: false`, and the run says plainly that such rows **will not match
a job-room row or the other domain**. Filter first, then take the references you
need.

**The numeric id alone rebuilds nothing**: `/stellen/281907/`,
`/stellen/x-281907/` and every variant answer `410`. The full slug or the
reference is required.

## Traps

**1. Gone is `410`, not `404`.** An unknown slug or reference answers **HTTP 410
Gone** — semantically right, and unusual enough that a `404`-only check misses
it entirely and treats a dead ad as unreachable rather than closed.

**2. The employer is never named.** `hiringOrganization` is the agency on every
ad, so the card carries `company: null` and `employer_named: false` rather than
writing *STA Personal AG* where the ledger expects the company the user would
work for. The fuzzy employer-name dedup cannot match these ads against the same
role on the employer's own ATS — expect that duplicate to survive, and say so.

**3. `<title>` carries the site suffix**, `… - fachkraft.ch - Jobs für
Handwerker`. The `JobPosting` block carries the job title alone; the adapter
reads that and falls back to `<title>` only if it is missing.

**4. fachkraft.ch is the umbrella, not just the larger face.** 3 534 ads against
1 835 on sta.jobs and 707 on stellenpartner.ch on the same day — and every
stellenpartner slug (501 of 501 distinct) also appears on fachkraft. Sweep
fachkraft and **never sweep a brand domain as well**: that is the same board
twice, and without `--with-ref` the ledger cannot tell.

## What this board gives that most do not

`validThrough` on every ad, in the `JobPosting` block — the expiry date
`cover-letter` step 1b now checks before anything else
(`shared/ats-open-check.md`). `check` returns it alongside its verdict.

## Applying

Through the agency, and through a consultant. The plugin does not create
accounts and does not fill credential fields — hand the user the ad URL and
their documents, and tell them the employer's identity usually arrives only
after contact.

## Pace

`list` is one request for the whole board. `--with-ref` is where the cost is:
one per kept ad, so filter with `--canton` and `--search` first.
