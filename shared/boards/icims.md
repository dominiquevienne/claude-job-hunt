# Board adapter — iCIMS

<!-- verified: 2026-09-02 -->

<!-- hosts: careers.icims.com -->
An ATS: **one employer per site, no search across employers.** It earns an
adapter for a reason that is a repetition rather than a volume — **four country
surveys named it as the commonest family with no adapter here**: Ireland 10
cards of 240, Singapore 15 of 240, Philippines 12 of 240, Indonesia 5 of 120.
It kept coming ahead of families that are already shipped, and **one ATS family
serves every country at once**.

**No key, no cookie, no account, no browser.** Read by
`skills/job-scan/scripts/icims.py`.

**Everything below was verified against the live platform on 2026-09-02.**

## The default URL is not the ad — and the sitemap lists the default one

```
GET /jobs/8179/nurse/job              → 200, 90 117 bytes, no JobPosting, no title
GET /jobs/8179/nurse/job?in_iframe=1  → 200, 37 509 bytes, JobPosting "Nurse",
                                        a 4 637-character description
```

The bare URL — the one a person copies from the address bar, **the one the
sitemap publishes** — returns the employer's careers portal: a real page, HTTP
200, and nothing an adapter can use. The ad is rendered in a frame, and one
query parameter fetches it directly.

**So this is an instruction, not a warning: append `?in_iframe=1` to every URL
the sitemap gives you.** Written the obvious way, an adapter enumerates a
board, collects a plausible page per ad, finds no postings, and reports an
empty employer. `icims.py list` emits both: `url` for a human, **`read_url`**
for the fetch.

## The same id is a different vacancy on every host

```
careers-sunrise.icims.com/jobs/8179   → 200, a nurse at Sunrise
field-mvtransit.icims.com/jobs/8179   → 200, 192 KB, MV Transportation
careers.icims.com/jobs/8179           → 404
```

**The wrong host answers 200 with somebody else's page**, not a 404. So the
ledger key is `icims:<host>:<id>` and the host is not decoration.

This is the exact mirror of the Workday defect found the same day. There, one
vacancy arrived under **two keys** — the `site` coordinate's capitalisation —
and the symptom is a duplicate, which somebody notices. Here, two vacancies
share **one key**, and the symptom is that an ad silently replaces another.
**Of the two ways a ledger key can fail, this is the worse one.**

## Three host shapes, and the platform host is never constructed

| Shape | Example |
| :-- | :-- |
| `careers-<tenant>.icims.com` | `careers-sunrise.icims.com` |
| `<tenant>.icims.com` | `field-mvtransit.icims.com` |
| **the employer's own domain** | `careers.montenidoaffiliates.com`, `jobs.lutheranseniorlife.org` |

Three of ten iCIMS ads in a HiringCafe sample sat on an employer's own domain,
so an adapter that knows only `*.icims.com` misses roughly a third of them.

**And the platform host is read, never built.** A branded page names it in its
own markup, and `icims.py resolve --url <branded URL>` reads it out:

```
careers.montenidoaffiliates.com  →  careers-montenidoaffiliates.icims.com
jobs.lutheranseniorlife.org      →  apply-lutheranseniorlife.icims.com
```

with fallback markers — `iCIMS System ID`, `ICIMS-LINK`, `iCIMS ATS Hiring
Flow` — that are present **even on a 404 page**, so detection survives a dead
ad id.

**The prefix has been seen as `careers-`, `apply-`, `field-` and nothing at
all.** Constructing it produces a 404, and a 404 here reads as *this employer
has no vacancies*.

## robots.txt is read per host, at run time

Two of six iCIMS hosts sampled served **`User-agent: * / Disallow: /`** — 26
bytes — while four served a 372-byte file that closes `referral`, `login`,
`candidate` and `connect` and **leaves the job paths open**. There is no
platform answer to quote; there is only this host's answer.

`icims.py` reads it before every sweep, through
`skills/job-scan/scripts/_robots.py`, which also refuses on
`Content-Signal: … ai-input=no`. **It is the first adapter here to read a
tenant's robots.txt at run time** — no script did before 2026-09-02, and the
issue that came out of it is #73.

### When two hosts of one employer disagree

Both platform hosts recovered by `resolve` above serve the 26-byte refusal and
a **403 on their sitemap**, while the employers' own domains serve `Allow: /`
and the same ads. Same content, same employer, opposite policies.

**Three rules, in order:**

1. **The host given governs.** `robots.txt` is per origin — that is the
   specification, not a loophole — so reading the branded domain under its own
   `Allow: /` obeys the origin being asked.
2. **No host is ever substituted to escape a refusal.** If the host the user
   gave refuses, that is the answer. `resolve` does not become a route around
   it, and the script says so when it stops.
3. **If a sibling host refuses while the given host permits, say so.** Not
   silence in either direction: `--sibling` prints the conflict and leaves the
   decision with the person.

**What separates rules 1 and 2 is not the file read, it is the gesture.**
Being handed a branded domain and obeying it is legitimate; being refused and
then going looking for the host that says yes is not.

*(An observation the file records without acting on it: four of the six
platform hosts carry the **same** 26-byte file while two carry a configured
372-byte one, which looks like an iCIMS default rather than six decisions. By
the discipline of `shared/robots-policy.md`, a vendor default changes what may
be **written** about intent — "this host carries iCIMS's default file, which
refuses" is supported, "this employer refuses" is not — and changes **nothing**
about what may be done. And an employer that wants to be read already has the
means: two tenants configured the open file themselves. It is not a closed
door without recourse; it is a door the employer opens.)*

## Configuration

```yaml
boards:
  icims:
    enabled: true
    employers:
      - host: "careers-sunrise.icims.com"
        sibling: "careers.sunrise.example"   # optional, reported not used
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `employers` | yes | Each needs `host` — the one you were given, never one you built |
| `sibling` | no | Another host of the same employer; its refusal is **reported**, never used to override |

No credentials, no login, no browser. **No tenant directory was found**:
searched 2026-09-02, `careers.icims.com` is iCIMS's own careers site — a
sitemap index pointing at one file of **19 of their own vacancies** — and not
a customer list. Ask the user for the careers URL, or resolve it from a
branded one.

## What an ad yields

The `JobPosting` on the framed page: title, `hiringOrganization.name`,
`datePosted`, `validThrough`, `employmentType`, a structured `jobLocation`,
and the description. On `careers-sunrise/8179`: *Nurse*, Sunrise, posted
2026-08-21, expiring 2027-08-21, `FULL_TIME`, Washington UT US, 4 637
characters.

**`jobLocation` is sometimes a list.** A multi-site vacancy carries several
addresses; the card takes the first and reports `locations_listed` so the
count is visible rather than lost.

## Zero-shaped answers

**1. The ad URL without `?in_iframe=1`** — 200, 90 KB, a real page, no
posting. The commonest way to read this platform as empty.

**2. An id on the wrong host** — 200, another employer's vacancy. Never a 404.

**3. A constructed platform host** — 404, which reads as "no vacancies" rather
than "wrong host".

**4. `sitemap.xml` answering 403** on hosts whose robots.txt also refuses —
the two agree, and neither is a breakage to report.

**5. A branded domain that says `Allow: /` while the platform host says
`Disallow: /`** — both are true, of different origins.

## Applying

The employer's own flow, behind the iCIMS account the site offers. **The
plugin does not create accounts and does not fill credential fields** — hand
the user the ad URL and their documents.

## Verification

```bash
S=skills/job-scan/scripts/icims.py
python3 $S list    --host careers-sunrise.icims.com --limit 2
python3 $S ad      --host careers-sunrise.icims.com --id 8179 --slug nurse
python3 $S resolve --url "https://careers.montenidoaffiliates.com/jobs/9184?lang=en-us"
python3 $S list    --host careers-chsli.icims.com    # refuses, quoting its robots.txt
```
