# Board adapter — Werkstraat (`werkstraat.com`, Suriname): «De vacaturesite van Suriname», a WordPress job board that serves ten cards a page with its count («Showing 1–10 of 341 jobs» on 2026-09-16) and an ad with the same meta block — a free-posting board polluted by spam, so the employer's name is scrubbed like a text; `werkstraat.py`, the count printed beside every walk

<!-- verified: 2026-09-16 -->

<!-- hosts: werkstraat.com -->
<!-- script: werkstraat.py -->
<!-- host-forms: werkstraat.com -->
<!-- host-forms-basis: read — every card, company and pager link is on the apex; `werkstraat.py` names it as a literal and accepts a `www.` ad address by rewriting it · 2026-09-16 -->
<!-- countries: SR -->
<!-- content: measured · **rules read (67 B): `User-agent: *` — `Disallow: /wp-admin/`, `Allow: /wp-admin/admin-ajax.php`; no Crawl-delay. `/jobs/` (200, 210 774 B) prints «Showing 1–10 of 341 jobs» and ten `<article class="… noo_job … post-<id>">` cards — title, employer (`company-name`, a `/companies/<slug>/` link, a hidden `hiringOrganization` microdata), `job-type`, `job-location` links (several per card), a `<time datetime>` — and a pager `/jobs/page/2/ … /jobs/page/35/`; `/jobs/page/2/` (200, 211 210 B) «Showing 11–20 of 341»; the ad `/jobs/<slug>/` (200, 128 520 B) `<h1 class="job-title">`, the meta block with `job-category` links and the expiry beside the date («september 15, 2026 - oktober 5, 2026»), `<div class="job-desc">` «Functieomschrijving»; no JobPosting JSON-LD (a Yoast WebPage graph only); **nine of the ten newest cards on the day were spam — supplement «reviews», essay mills — posted under an e-mail address as the employer's name**; `werkstraat.py list --pages 2` on the day: «20 emitted from 2 page(s) of the 35 the pager names; the site states 341»** · 2026-09-16 -->
<!-- witness: the list's own «Showing 1–10 of 341 jobs», printed on the server and read by `werkstraat.py list` beside the walk — a count of what the board lists, spam included · 2026-09-16 -->
<!-- route: http · 341 · 2026-09-16 -->

**Issue #445 (opened under #416, Suriname searched on 2026-09-13). Measured
2026-09-16 12:10–12:12 UTC by the declared client, the guard on the exact
path first, `bin/fetch-body.py`; the script exercised on the same minutes
and again at 23:4x under the owner's weekly derogation.** Rank: the pilot's
risk order of 2026-09-14 10:4x, after EmpleosEnUruguay (#437).

## What the board is — open to anyone, and it shows

A WordPress board (Noo JobMonster / Jobica theme) where an employer posts
for free after registering. **On the day, nine of the ten newest cards were
not Surinamese jobs at all**: «AlkaVitality Reviews: Ingredients…», «NURS
FPX 4055 Assessment 3…», «Vivanta Kidney Hospital» — spam posted under an
e-mail address as the employer's name, with a US street as the location.
The tenth («Chat Moderator (Remote)», Paramaribo, «Freelance») is a job.
**The adapter emits what the site lists and does not judge it** — the
categories, the type and the locations are the site's own labels, and a
reader filters on them (a Surinamese location, a Dutch title); the stated
«341» counts the spam too, and the card says so.

## The rules, the transport

```
robots.txt              200, 67 B — `*`: Disallow: /wp-admin/, Allow: /wp-admin/admin-ajax.php
allowed('/jobs/')       open, certain      allowed('/jobs/page/2/')   open, certain
GET /                   200, 140 088 B, md5 69d8fd089f4c   (12:10:48Z)   the front, six cards
GET /jobs/              200, 210 774 B, md5 c8fd499953cf   (12:11:03Z)   «Showing 1–10 of 341 jobs», 10 cards, pager to 35
GET /jobs/page/2/       200, 211 210 B, md5 2cd45efdc594   (12:11:06Z)   «Showing 11–20 of 341», 10 cards
GET /jobs/chat-moderator/   200, 128 520 B, md5 1aa2e06a0015   (12:11:49Z)   the ad: meta block, categories, expiry, «Functieomschrijving»
```

`/wp-admin/`, `/wp-json/`, `/member/`, `/xmlrpc.php`, `/wp-login.php` are
never sent (exit 7 before the gate) — the REST API is open by WordPress'
default and refused by ours.

## What the adapter emits, and withholds

`list [--pages N]`: id (the post id), url, slug, title, company,
company_profile, locations, job_type, posted (categories are on the ad
only). `ad --url`: the same block plus categories, valid_through (the
expiry beside the date, Dutch month names), the description flattened and
scrubbed. Guards: no stated count exits 6; a page without a card exits 6;
page 1 served again exits 6; the walk ends at the pager's last page.

**Withheld:** the employer's name is passed through the same scrub as a
text — an e-mail address as a name becomes «[e-mail withheld]» (the spam's
signature, and a private address either way); the description is scrubbed
of e-mail addresses and Surinamese telephone numbers (`+597`, 7-digit
mobiles, 6-digit landlines); `contacts_withheld` on every record; the
application («Solliciteer», a member account) never touched; the company
logo not emitted.

## Tests and mutations

`ASurinameseFreePostingBoardWhoseListStatesItsCountAndWhoseEmployerFieldIsScrubbedLikeAText`,
both ways on fixtures (the walk to the pager's last page with a repeated
card read once, three employers of which one is an e-mail address,
`--pages`, the three exit-6 cases, four refused addresses, the ad with its
categories, expiry and scrubbed body). Mutation bench on a detached copy,
`python3 -B`, 6 / 6 red: the stated count not read · the last page not read
· the dedup dropped · the employer not scrubbed · the expiry not read · the
description not scrubbed.
