# Board measurement — Public Service Commission (Kenya): the civil service's own recruitment system (`pscims.publicservice.go.ke`) — **2 active adverts on 2026-09-22, one post and one internship programme of 1 000 places**, each in a table whose header names its columns; `pscke.py` — the two tables do not share their columns, the detail is a `__doPostBack` that is not replayed, and the Commission's PDFs are not read because some of them name successful candidates

<!-- verified: 2026-09-22 -->

<!-- hosts: www.publicservice.go.ke, publicservice.go.ke, pscims.publicservice.go.ke -->
<!-- script: pscke.py -->
<!-- countries: KE -->
<!-- content: measured · **the host answers, 2026-09-20 14:03–14:10 UTC, the declared client, every list read twice.** Rules (`www.publicservice.go.ke/robots.txt`, 200, 1 882 B, md5 16a1cb350a50): Cloudflare's managed content signals — `User-agent: *` `Allow: /` with `Content-Signal: search=yes,ai-train=no,use=reference`, and `ClaudeBot`, `GPTBot`, `CCBot`, `Amazonbot`… refused `/`; `Claude-User` is not named, the `*` group applies (decision of 2026-09-07), no Crawl-delay. Root 200 (953 335 B, WordPress; the apex redirects to www). `/jobs/` 200 ×2 (629 852 B, md5 moves — a rendered element), 16 advert PDFs under `/download/…` (delegated advertisements, re-advertisements, appointed candidates). The recruitment system is `pscims.publicservice.go.ke` (ASP.NET WebForms, `__VIEWSTATE`): `/jobs/ActiveJobsAdverts.aspx` 200 ×2, 14 232 B, same md5, **1 active advert** (D111/2026 Principal Labour Migration Officer, CSG 8, 2 posts, «For Serving Officers Only», 14-09-2026 → 05-10-2026), details behind `__doPostBack`; `/jobs/ActiveAdvertsInternsInternshipExt.aspx` 200 ×2, header and no row; `/puio/` (public universities and independent offices) a welcome page. Applying needs an account (ID/passport) — the site's own instruction — measured 2026-09-20; **READ AGAIN 2026-09-22 09:5x UTC by the declared client, the guard on the exact path, two reads of the adverts table: `ActiveJobsAdverts.aspx` 200 ×2, 14 232 B, md5 24732dc66ffc BOTH times (a WebForms page whose `__VIEWSTATE` does not move), **1 active advert** — D111/2026, Principal Labour Migration Officer, CSG 8, 2 vacancies, «For Serving Officers Only», 14-09-2026 → 05-10-2026; `ActiveAdvertsInternsInternshipExt.aspx` 200, 14 538 B, **1 advert of 1 000 places** (Public Service Internship — Digital Literacy Programme, 15-09-2026 → 05-10-2026) where on 2026-09-20 that table carried its header and NO row. The two headers differ — eleven columns against eight, and the fourth cell is a job scale on one page and a ministry on the other — so the cells are read by their header. Exercised: `jobs --country-code KE` → **2 emitted, «neither table states a count» said** —** · 2026-09-22 -->
<!-- witness: none — neither table states a count; `pscke.py jobs` prints what each table listed and how many records lack a closing date · 2026-09-22 -->
<!-- route: http · 2 · 2026-09-22 -->

**Measured 2026-09-12 at 12:16:50Z UTC for #233, lot 6 — and the
measurement stops at the rules.** `_robots.verdict()` tried the rules file
three times and got a timeout each time, on two separate reads; the
`fetch-body.py` call for the root exited on `INDETERMINATE` without sending
anything. **A host that closes everything to us and a host that is slow to
answer look the same from here — and the doctrine says the difference is
not ours to guess.**

## The rules — unread

```
robots.txt      TIMEOUT ×3 (read 1, 12:16Z) · TIMEOUT ×3 (read 2, 12:22Z)
verdict()       sweep None — «This is an unknown, not a permission and not a refusal»
identity("/")   state unknown, token None
allowed("/")    None
fetch-body.py   INDETERMINATE, exit 8 — no request for content left this machine
```

*#233 listed this host under «another managed block naming ClaudeBot» from
a read on 2026-09-11; today the file did not answer at all. Both are
readings, each dated.*

## What this card is, and is not

- **Not a verdict** — neither open nor closed nor refused: *a measurement to
  redo* (`§2 sexies`: an INDETERMINATE is never a renunciation). A second
  resolver was not tried: the failure is a timeout on the HTTP read, not a
  DNS answer.
- **The object**: Kenya's Public Service Commission publishes its vacancies
  on this host (the page named it as the country's board); whether the site
  is slow, geo-fenced, or down this hour is exactly what the next read will
  say.
- **No script, no configuration.**

## 2026-09-13 — #283: a timeout on the rules file is an absence of rules; the transport timed out too

Since #283 (owner's decision of 2026-09-13: «toutes incapacité d'ouvrir
robots.txt doit aboutir à l'absence de règles») the three timeouts on
`/robots.txt` are `no-rules-timeout` — `allowed: True, certain: False` — and
the first transport request waits 10 s. Measured on 2026-09-13 (15:48 UTC): the
guard opened, `bin/fetch-body.py` waited its 10 s and asked for the root,
**and the root timed out as well** (`URLError: timed out`, 25 s). *The
INDETERMINATE moves from the rules file to the transport: nothing forbids,
and nothing answers. A measurement to redo, from another network or at
another hour; not a verdict.* `route:` is not declared — nothing was
served.

## 2026-09-20 — #283, the measurement redone: the host answers

**Read on 2026-09-20 between 14:03 and 14:10 UTC, `bin/fetch-body.py`, the
declared client, from the same machine that got nothing on 2026-09-12 and
2026-09-13.** Everything answered on the first attempt:

```
www.publicservice.go.ke/robots.txt                       200  1 882 B   Cloudflare managed content — * Allow: /, ClaudeBot refused, Claude-User not named
www.publicservice.go.ke/                                 200  953 335 B WordPress; publicservice.go.ke → www (final_url)
www.publicservice.go.ke/jobs/                            200  629 852 B ×2, md5 moves (rendered element); 16 advert PDFs under /download/
pscims.publicservice.go.ke/jobs/ActiveJobsAdverts.aspx   200  14 232 B  ×2, same md5 — 1 active advert (D111/2026), details by __doPostBack
pscims.publicservice.go.ke/jobs/ActiveAdvertsInternsInternshipExt.aspx  200  14 538 B ×2 — header, no row
pscims.publicservice.go.ke/puio/                         200  17 633 B  ×2 — the universities/independent-offices gateway, a welcome page
```

**What it is.** The Commission publishes its vacancies twice: as PDFs on
the WordPress site (`/jobs/`, ordered by publish date, «Advertised Jobs» /
«Archived Jobs» / «Shortlisted Candidates» / «Appointments»), and as rows in
its recruitment system PSCIMS — an ASP.NET WebForms application whose
active-adverts table is server-rendered (advert number, position, job scale,
ministry, number of vacancies, years of experience, category, dates) and
whose «Advert Details» is a postback. **One advert today, for serving
officers only; the internship table is empty.** A small board, and the
country's public-service one.

**What changed, and what did not.** The two mute days (12.09: rules timed
out ×3 on two reads; 13.09: rules `no-rules-timeout`, root timed out after
the 10 s wait) were the host, not us — same client, same network, and today
every request is answered within a second. *A timeout is dated; it is not a
property of the host* (the card said so on the 12th). The rules are now
READ: the `*` group allows everything and names `ClaudeBot` among the
refused — `Claude-User` is not named, so the decision of 2026-09-07 applies
and the HTTP route is open. **Not a verdict on the content beyond what was
read; the adapter, when it exists, reads `ActiveJobsAdverts.aspx` and the
PDF list, and replays the postback for the details** (the same WebForms
shape as `eploy.py`). Issue #802 (`adapter`) opened under #291 before any script.

## The adapter — `pscke.py` (#802, 2026-09-22)

```
GET /jobs/ActiveJobsAdverts.aspx                200 ×2, 14 232 B, same md5 — 1 advert
    ## · Advert Number · Position · Job Scale · Ministry · Number of Vacancies ·
    Years of Experience Required · Advert Category · Advert Date · Advert Close Date · (details)
GET /jobs/ActiveAdvertsInternsInternshipExt.aspx 200, 14 538 B — 1 advert, 1 000 places
    ## · Advert Number · Position · Ministry/State Department · Number of Vacancies ·
    Advert Date · Advert Close Date · Action
```

**The two tables do not share their columns** — eleven against eight — and
**the fourth cell is a job scale on one page and a ministry on the other**. The
cells are read by their header; a record whose `ministry` held «CSG 8» would be
wrong in a way nothing downstream could notice.

*And a column read by position is how a reading goes wrong while looking
complete: the first inspection of the adverts table printed its first nine cells
and concluded it had no closing date. **It has one, in the tenth.*** What a
table does not state stays `null`, and the run says how many records lack a
closing date.

**An empty table is a state, not a failure.** The internship table carried its
header and no row on 2026-09-20 and carries one today; a header with no rows is
reported, and a table with no HEADER is the page changing (exit 6) — the columns
would be unknown, and guessing them files each value under whatever name the
guess happens to hold.

**An advert number has the shape of a telephone number** («143/2026») and is
spared by name — as Cabo Verde's «176/2024» was.

**What is not read, and why it is not a technical limit:** the Commission's
WordPress site carries 16 PDFs under `/jobs/` — delegated adverts, re-adverts
**and lists of successful candidates**. *A list of named candidates is personal
data about people who did not publish it for us*, so that page is not opened at
all. The advert's detail is an ASP.NET `__doPostBack` and is not replayed
(`detail_read: false`). Applying needs an account (an ID or passport number);
the plugin creates none.

**Tests and mutations.**
`TwoTablesOfOneSystemWhoseColumnsAreNotTheSame`, both ways on fixtures (each
table read by its own header, the fourth cell meaning two different things, an
advert number kept whole, an empty cell left null, the pager's «< >» line not
taken for a row, an address scrubbed, an empty table reported, a table of rows
without a header refused, a 404, a 500, the WordPress host refused). Mutation
bench on a detached copy, `python3 -B`, **9 / 9 red**: the cells read by
position · the header not required · the advert number not spared · the
missing-close-date count silenced · the empty-table note dropped · `detail_read`
claimed true · the pager line taken for a row · the scrub dropped · the host
check dropped.
