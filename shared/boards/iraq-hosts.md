# Assessed, no adapter — Iraq: nineteen hosts named, and no countable inventory

<!-- verified: 2026-09-07 -->

<!-- hosts: careeriraq.com, works-jobsiq.com, vacanciesiniraq.com, www.t9iq.com, jobs.krd, taeen.iq, ngosjobs-bids.com, www.employiq.net, masteriraq.com, iqjscout.com, eshjob.com, www.iraqhire.com, www.kurdistanjob.com, pharmajobs.skpi.krd, www.evtc-krg.org, lvtd.gov.iq, kar.molsa.gov.krd, www.hawa.jobs, atgroup.iq -->
<!-- script: none -->
<!-- countries: IQ -->
<!-- source-error-rate: 3 of 23 · unclassified 6 · [13.0 % ; 39.1 %] · 2026-09-07 -->
<!-- hosts-source: all 19 named by `jobsiniraq.github.io`, a directory of job platforms in Iraq that names 103 distinct hosts; **no hostname was composed**, and the hosts DISCARDED here are recorded with the rest so this source's error rate is computable — see #162 · 2026-09-07 -->
<!-- content: measured · 19 hosts guarded and 10 fetched; the only server-rendered board declares 1 advertisement through 7 of its own facet counts; 0 `JobPosting` across the 10 · 2026-09-07 -->
<!-- witness: `works-jobsiq.com` states its own total through every facet of its listing — title, country, governorate, city, experience, contract type, industry, all reading `1` · 2026-09-07 -->

**Iraq — forty-five million people — was absent from the country queue on
2026-09-05, invisible exactly as if it had a page.** Issue #161 measured five
hosts. This card measures nineteen.

## Where the hosts come from, and none is composed

**`jobsiniraq.github.io` — a directory of job platforms in Iraq — names 103
distinct hosts.** It was read on 2026-09-07 after its guard turned permissive:
its rules name `claudebot`, `claude-web` and `anthropic-ai` and close everything
to each, and **`claude-user` is not named, so it falls under `*`, which
permits**. On 2026-09-05 the same file read as a refusal.

> **That is our doctrine changing on 2026-09-07, not the host changing.** The
> earlier reading was correct under the rule then in force.

**The directory also settles a question #161 deliberately left open.** That
issue refused to compose `aweza.com` from a brand name, writing that composing
would be *"the naming motif counted as a host"*. **The directory names
`www.aweza.co`.** *Composing would have produced a host that is wrong, not
merely unattested — the caution paid, and it is rare to be able to show it.*

## The three ways in, and what each yields

### Refused in the rules — three hosts, nothing fetched

```
www.kurdistanjob.com     allowed=False, certain
pharmajobs.skpi.krd      allowed=False, certain
www.evtc-krg.org         allowed=False, certain
earthlink.iq             allowed=False, certain
```

### Refused at the transport with a body that is not theirs — three hosts

```
iqjscout.com       403   25 o   md5 9ccabba20b9f   x2, STABLE
eshjob.com         403   25 o   md5 9ccabba20b9f   x2, STABLE
www.iraqhire.com   403   25 o   md5 9ccabba20b9f   x2, STABLE
```

**All three guard `allowed=True, certain=True` and all three refuse.** *Each was
fetched twice: a refusal body carrying a rendering element changes md5 on every
request and cannot be compared across hosts. These do not move.*

**`9ccabba20b9f` is a body this repository holds on seven other hosts across
five regions**, `jobstore.com` and `www.hays.fr` among them, measured the same
day. **It is a provider default, not a page an Iraqi operator wrote** — so these
three refusals say nothing about Iraqi publishers.

### Indeterminate — two hosts, and they are NOT probed

```
lvtd.gov.iq      unreachable   allowed=None
www.hawa.jobs    unreachable   allowed=None
```

**`lvtd.gov.iq` is the only `.gov.iq` any source has named us.** *A timeout is
neither a refusal nor a permission, and an indeterminate is not sounded.*

## What the ten fetched hosts actually serve

| host | bytes | visible text | `JobPosting` | what it is |
| :-- | --: | --: | --: | :-- |
| `www.t9iq.com` | 430 219 | 3 863 | 0 | **a Blogger site** — 82 `blogspot`/`blogger` markers, 10 internal links |
| `vacanciesiniraq.com` | 167 775 | 1 490 | 0 | WordPress board, **regional**: its title names UAE, Dubai, Qatar, Saudi |
| `works-jobsiq.com` | 112 369 | 14 715 | 0 | **the only server-rendered board — and it holds ONE advertisement** |
| `masteriraq.com` | 64 627 | 5 128 | 0 | *"Master Group — Connecting Markets"*: **not a job board** |
| `www.employiq.net` | 35 576 | 1 598 | 0 | thin |
| `careeriraq.com` | 32 679 | ~1 039 | 0 | client-rendered, **identical byte count on 09-05 and 09-07** |
| `ngosjobs-bids.com` | 31 386 | 2 148 | 0 | **NGO jobs AND tenders**, mixed |
| `jobs.krd` | 13 935 | 9 | 0 | client-rendered shell |
| `taeen.iq` | 4 428 | 0 | 0 | empty shell |
| `eshjob.com` · `www.iraqhire.com` | 25 | — | — | the provider refusal above |

**Zero `JobPosting` on ten hosts.** *Not one carries structured job data.*

### The one board that counts, and it counts one

**`works-jobsiq.com/jobs` states its own inventory through every facet of its
listing, server-rendered:**

```
Jobs By Title       technician  1
Jobs By Country     Iraq        1
Jobs By Governorate Duhok       1
Jobs By City        Duhok       1
Jobs By Experience  <1 year     1
Jobs By Job Type    Contract    1
Jobs By Industry    RECRUITMENT AGENCY  1
```

**One advertisement, and the site is the witness.** *This is not a silent zero
and not client rendering: seven independent facets agree, and the single ad
link — `/job/technician-56` — is in the markup.*

**And its homepage says what it is**: *"INTERNATIONAL TRAINING CENTER &
RECRUITMENT AGENCY"*, *"a private company that specializes in education and
hiring staff"*. **A company's own jobs module, not a national board.**

## Why no adapter is proposed

**Nothing here has a countable inventory reachable by a script.** The one
server-rendered board holds a single advertisement; the two largest hosts are a
Blogger site and a regional WordPress board whose scope is the Gulf; the
national-looking candidate renders its cards client-side and declares no
sitemap — *and `--sitemaps` says so rather than guessing one.*

**This is a finding, not an omission.** *`no adapter` here means the hosts were
named, guarded and fetched, and none offers a surface worth writing against.*

## What this card does NOT establish

- **nothing about `careeriraq.com`'s volume** — its cards arrive client-side and
  were not counted; a browser route was not attempted;
- **nothing about the 84 hosts of the directory not listed here** — among them
  `job.studio`, `lezan.app`, `www.rwangaforas.com`, `www.jobzone.ai`, and
  `baly.jobs.personio.de`, **an Iraqi Personio tenant already covered by
  `personio.md`'s host form**;
- **nothing about the Iraqi state** — `lvtd.gov.iq` is unreachable and was not
  sounded, and `kar.molsa.gov.krd` (Kurdistan's labour ministry) answers
  `unrecognised`: permitted under the 2026-09-07 decision on #171, but
  `certain=False`;
- **nothing about what the three refusing hosts serve** — a refusal is not a
  description.

## The census — and the first bounded error rate for a source (#162)

**The 19 hosts above mix two sources and were chosen because they looked like
boards. That is the selection bias #162 names, reproduced.** So the source was
censused instead: `jobsiniraq.github.io` marks its listed portals mechanically
with `data-testid="link-portal-N"`, and there are **23 of them**.

> **The directory MENTIONS 103 hosts; it LISTS 23 as portals.** The other 80 are
> per-portal social links, analytics, employer sites and ATS vendor names.
> *Six of the 19 above — `careeriraq.com`, `masteriraq.com`, `works-jobsiq.com`,
> `www.employiq.net`, `www.iraqhire.com`, `atgroup.iq` — are **not** on the
> portal list, so `masteriraq.com` being no job board is **not** this source's
> error. It was nearly counted as one.*

**A census, not a sample: 23 is measurable whole, so there is no draw to
pre-register and no seed. The denominator is the population.** *The expected
distribution was written before the first new measurement: 15-18 true portals,
3-5 real but not Iraq-specific, 1-3 dead or not portals at all — an error rate
expected between 5 % and 15 %.*

```
5   TRUE PORTALS       ngosjobs-bids · vacanciesiniraq · job-helper
                       jobzone.ai · kar.molsa.gov.krd (Kurdish labour ministry,
                       server-rendered, 4 340 characters of Kurdish)
2   NOT IRAQ-SPECIFIC  linkedin.com · www.bayt.com — real, worldwide
7   REFUSED            iqjscout · eshjob · aweza.co · kurdistanjob
                       pharmajobs.skpi.krd · evtc-krg · unjobs.org
6   INDETERMINATE      lvtd.gov.iq · hawa.jobs · iraq.tanqeeb.com
                       lezan.app · taeen.iq · jobs.krd
3   THE SOURCE WAS WRONG
      www.rwangaforas.com   709 o, `window._trfd.push({ap:"parking"})`
                            and `LANDER_SYSTEM="PW"` — a PARKED DOMAIN
      www.t9iq.com          a Blogger site, 82 platform markers
      job.studio            « a virtual marketplace where talent is traded »,
                            no job listing in its navigation
```

**`www.rwangaforas.com` is the same FAMILY as `bestzambiajobs.com` — a credible
name, listed as a portal, serving something else entirely — but not the same
shape, and the earlier wording that said «&nbsp;exact shape&nbsp;» was too strong.**
*`bestzambiajobs.com` was **repurposed**: it serves working content, a Turkish
streaming site with a title and a sitemap. This one is **parked**: 709 bytes and
nobody running anything.* **The parked sub-species announces itself in one grep —
`ap:"parking"` — and the repurposed one does not**, which is why a check built on
that marker would pass `bestzambiajobs.com` cleanly. See `bestzambiajobs.md`. *That is the case
#162 says vanishes without trace every time a retraction works. It did not
vanish here, because this card names it beside the source that named it.*

### The rate, and why it is a bound and not a number

**3 of 23 is 13.0 %. But 6 hosts cannot be classified**, so the true rate lies
in **[13.0 %, 39.1 %]** — every indeterminate could turn out either way.

**The prediction is half confirmed and half not.** *«&nbsp;1 to 3 dead or not
portals&nbsp;» landed on exactly 3. «&nbsp;3 to 5 not Iraq-specific&nbsp;» landed on 2.
And the interval is too wide to confirm or refute the 5-15 % expectation.*

> **A census removed the selection problem and did not produce a demonstrable
> rate.** *What blocks it now is neither disappearance nor selection: it is that
> six hosts refuse to say what they are — four render client-side and two never
> answer.* **The obstacle has changed, and it is narrower each time.**

**An indeterminate is not missing data to discard.** *Dropping the six would put
the rate at 3 of 17 — 17.6 % — and would rebuild, on a smaller scale, the very
bias this census exists to remove.*

## Pace

Guards taken on the exact path, in a turn of its own, before every fetch.
Twenty-one fetches in all, each through `bin/fetch-body.py` with provenance
written beside the body. No host was composed.
