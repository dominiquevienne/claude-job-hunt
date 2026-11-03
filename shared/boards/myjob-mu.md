# Board measurement — MyJob.mu (`myjob.mu`, Mauritius): **NO adapter, and the measure of 2026-11-03 (#697) is why** — the list STATES «1,345 jobs found» and serves **8 of them, 0.6 %**, with no pagination control of any form; the only data host its payload names, `app.myjob.mu`, publishes `User-agent: * / Disallow: /` (borne 1, every route), and its own `/robots.txt` is 1 248 bytes of Cloudflare «content signals» preamble carrying ZERO directives — open, `certain: False`, and that is correct

<!-- verified: 2026-11-03 -->

## 2026-11-03 — #697: the measure is the deliverable, and no script ships

The head this card carried read «1,515 Jobs» and «no adapter yet». The total moved to **1,345** and the second half is now a decision with a reason rather than a backlog.

**Why no adapter.** `/jobs` serves **8 distinct adverts of the 1,345 it states** — 0.6 % — and carries **no pagination control of any form**: seven candidate forms return zero, there is no `<select>`, and no button or link bearing a navigation word. The Nuxt payload is the shell's data (filters, banners, 63 keyword counts) and holds no advert. **The only data host the payload names is `app.myjob.mu`, and it publishes `User-agent: * / Disallow: /` and that reading is CERTAIN** — borne 1, which blocks every route including the browser. An adapter written today would under-report by a factor of 168 and would have to declare «partial» on every run, which is an avertissement qui tire toujours.

**NOT ESTABLISHED, and declared:** that the job LIST comes from `app.myjob.mu`. The payload names it for a FILE route only, and the main bundle `/_nuxt/wJEzAB2-.js` (169 710 B) names neither it nor `/api/job-board`. *Either way only the 8 are reachable today, so the conclusion does not rest on that gap — but the gap is said rather than closed by inference.*

**A `robots.txt` that is 200 and carries ZERO directives.** Its 1 248 bytes are the Cloudflare «content signals» preamble — a legal notice defining `search`, `ai-input` and `ai-train`, with **no `User-agent`, no `Disallow`, and not even a `Content-Signal:` line**. `_robots` renders `state: unrecognised`, `certain: False`, open, and that is CORRECT: there is nothing to recognise, and the file's own clause (c) says a signal that is absent «neither grants nor restricts permission». **This is NOT the #180 defect** — that one is `Disallow` lines with no `User-agent` being ignored, and here there are zero `Disallow` lines. *This format is a Cloudflare default and will be met again; the reading above is what it means.*

**WHAT IS NOT MINE TO WRITE.** Nothing here says this board is closed. §2 sexies reserves that verdict to the owner, and the `override_robots` key his 2026-09-13 decision makes available on **any** board whose rules refuse by writing is HIS to set, never ours and never by default. What is recorded is the dated measure.


<!-- hosts: myjob.mu -->
<!-- script: none -->
<!-- countries: MU -->
<!-- content: measured · **NO adapter, and the measure is why. `myjob.mu/jobs` (200, 103 119 B, md5 7b2b368cc5ea, 21:13 UTC) STATES «1,345 jobs found» — the «1,515» of 2026-09-18 moved — and serves **8 distinct `/job/<id>/<slug>` adverts**, i.e. 0.6 % of its own total, with **no pagination control of any form**: `?page=`, `&page=`, `pagination`, `rel="next"`, `page-link`, «Next», «Load more» all return ZERO, there is no `<select>`, no `<button>` or link carrying a navigation word, and one form. The site is a Nuxt app; `/jobs/_payload.json` (200, 28 110 B) is the shell's data — filters, banners, 63 keyword counts — and carries NO advert. **The only data host the payload names is `app.myjob.mu`, and it publishes `User-agent: * / Disallow: /` — everything closed, evenly, and that reading is CERTAIN (the file is read, not merely absent)**, which is borne 1: a `Disallow` written in the rules blocks every route, the browser included. *NOT ESTABLISHED: that the job LIST comes from that host — the payload names it for a FILE route (`/api/job-board/file?filePath=client-logo/…`) and the main bundle `/_nuxt/wJEzAB2-.js` (169 710 B) names neither it nor `/api/job-board` at all.* Either way only the 8 are reachable today. And `myjob.mu/robots.txt` is 200 with **1 248 bytes of Cloudflare «content signals» preamble and ZERO directives** — no `User-agent`, no `Disallow`, no `Content-Signal` — so `_robots` renders `state: unrecognised`, `certain: False`, open, which is correct: its own clause (c) says a signal that is absent «neither grants nor restricts permission». **This is NOT the #180 defect**: there are zero `Disallow` lines to ignore** · 2026-11-03 -->
<!-- witness: the list's own «1,345 jobs found», against the 8 it serves — the total is real and 99.4 % of it is not reachable by a route we may use. The «1,515 Jobs» of 2026-09-18 is history · 2026-11-03 -->
<!-- content: measured · **the root (200, 102 133 B, md5 156659d9b3bf / 4e90166d5503 — a rendered element moves) states «1,515 Jobs» and per-category counts («256 jobs», «212 jobs», «149 jobs»), links `/jobs/<category>?category=…` and `/job/<id>/<slug>`; no JobPosting on the root; `_robots.allowed('myjob.mu','/')` → open, `certain: False`; the list and the ad not read** · 2026-09-18 -->
<!-- witness: the root's own «1,515 Jobs» and its category counts · 2026-09-18 -->

**Found by the Mauritius search of #618 (a country never searched),
measured 2026-09-18 06:45–06:47 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads.** The method is written
on #618: one search naming the National Employment Department's portal
and the private boards, no composed host names. *A measurement, not an
adapter.*

```
_robots.allowed('myjob.mu', '/')   open
GET https://myjob.mu/   200 ×2 — see the content line
```

The list, its pager and the ad are the adapter's first line (its `adapter` issue).
