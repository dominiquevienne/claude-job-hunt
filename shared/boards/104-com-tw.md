# Board measurement — 104.com.tw (Taiwan): a challenge page to our client, and a connected tab served the search without a click — «共 1000+ 筆», 150 pages of 20; `route: browser`, no script

<!-- verified: 2026-09-16 -->

<!-- hosts: 104.com.tw, www.104.com.tw -->
<!-- script: none -->
<!-- countries: TW -->
<!-- witness: none — the search's own «共 1000+ 筆» is a floor, its pager «第 1 / 150 頁» the reachable bound; nothing past the challenge was read by a client · 2026-09-16 -->
<!-- content: measured · **the declared client gets a moving-md5 challenge on `/robots.txt`, `/` and `/jobs/search/` (2026-09-11, 2026-09-13); a connected tab on 2026-09-16 05:3x UTC was served, without any click, the unfiltered search `/jobs/search/?keyword=` — «共 1000+ 筆», a page selector «第 1 / 150 頁», `&page=150` served with 17+ titles, so 150 × 20 ≈ 3 000 ads reachable through the pager and the site's display capped at «1000+» (the Taipei filter `area=6001001000` alone shows «1000+» too); `/jobs/main/` states «96,000+ foreigner-friendly job openings»; the ad `/job/<code>` prints the title, the employer (a link), «2026/09/10更新», «上班地點» with a street address, «月薪45,500~62,500元», and a contact person (a name) — never emitted** · 2026-09-16 -->
<!-- route: browser · 3000 · 2026-09-16 -->

**This card is a measurement and not an adapter.** *No card declared `TW`
before it; the host was known to the repository as a line in
`shared/robots-policy.md` — «a 403 the browser denies … two md5s for apex and
www, and its search page loads fine in Chrome» (2026-09-08) — and nothing
had measured which KIND of refusal it is.* **That is the question this card
answers, and the answer closes the browser route for now.**

## Step 1 — the rules, twice, on both hosts (2026-09-11 13:39–13:41 UTC)

```
https://104.com.tw/robots.txt        403   twice   Cloudflare (server, cf-ray)   guard: host-closed, rule "/", certain True
https://www.104.com.tw/robots.txt    403   twice   Cloudflare                    guard: host-closed, rule "/", certain True
```

**The host refuses its own rules file** — on the apex and on the `www`, four
reads, four 403s. *`_robots.allowed()` calls this `host-closed`: not an absent
file, not an unreadable one — the host replied, and the reply was no.* No
`Disallow` was ever read, so nothing here is a rule written by the operator.

## The question that sorts — STABLE or MOVING fingerprint — and the answer

**The refusal body, read four times, is the SAME request the guard sends
(`/robots.txt`, our declared identity), repeated to read what it carries:**

```
104.com.tw      #1  403   5 648 o   md5 e62ed710fce62e82b751b7696a677a6e   <title>Just a moment...</title>
104.com.tw      #2  403   5 648 o   md5 9862ba5ee99133871e29321dd4aa8dc3   bodies differ at byte 408
www.104.com.tw  #1  403   5 648 o   md5 678323f188f937df0d22ddcb76eae616
www.104.com.tw  #2  403   5 648 o   md5 93c637511161a16a6911d9bac4490f09
                                     `challenge` ×8 in the body
```

**Same size every time, a different fingerprint every time, titled «Just a
moment…»** — *this is family (3) of `shared/robots-policy.md`, the challenge
page whose md5 moves per request, the `revolico.com` class — and not
family (1), the 25-byte vendor default of `eshjob`, `kariera.mk`, `jobs.af`.*

> **A challenge is bound 2 of the 07.09 doctrine: we do not defeat it, and we
> do not ask the user of the plugin to defeat it.** *So this host does NOT go
> to #222 — that list is the eleven whose refusal is a static 403 to a client
> that a browser is served past without a challenge.*

**What stays open, and cannot be sorted from here.** The policy's own
distinction — *a passive interstitial is re-read; a challenge that asks for a
click is a stop* — decides whether a browser route exists, and **it is a
browser-time question**: from a scripted client both shapes are the same
5 648 bytes. The 08.09 note that «its search page loads fine in Chrome» is
consistent with a passive interstitial and with a human having clicked; it does
not say which. **If a session with the extension connected loads a search page
here without any click, that observation reopens this card as a browser
candidate; until then it is closed by a challenge, dated.**

## What this card does not say

Nothing about the board's size, its markup, its ids or its language — nothing
was read. Nothing about the operator's intention — no rule was read either.
**«Taiwan has no board» is not a sentence this repository can write from this
card; «Taiwan's largest board serves our client a challenge page» is.**

## 2026-09-13 — #283: an unread rules file is an absence of rules, and the transport measured

**Owner's decision of 2026-09-13, verbatim: «toutes incapacité d'ouvrir robots.txt
doit aboutir à l'absence de règles et donc à l'ouverture».** This card read
«host-closed, rule "/", certain True» — a verdict taken on the rules file alone. Since #283 the 403 on
`/robots.txt` is `no-rules-403`, `allowed: True, certain: False`: nothing
was read, nothing forbids, and **the transport decides**. Measured with
`bin/fetch-body.py --allow-refusal` under the new guard, the root (and a
listing path where one was known) twice:

```
GET https://www.104.com.tw/                              403, 5 597 B, md5 dc352ca5f4b6   (15:29:59Z)
GET https://www.104.com.tw/                              403, 5 597 B, md5 3f926bc2aa17   (15:30:00Z)
GET https://www.104.com.tw/jobs/search/                  403, 5 654 B, md5 1657645d8e22   (15:30:01Z)
GET https://www.104.com.tw/jobs/search/                  403, 5 654 B, md5 921f89163317   (15:30:02Z)
```

**The transport answers a **challenge** — «Attention Required!» / «Just a moment...», the md5 moving at constant size: borne 2 of the 2026-09-07 decision, the plugin neither defeats it nor asks anyone to; a real browser is not measured here.** *A verdict of closure was never
this card's to give (§2 sexies); what it gives now is a dated transport
reading, and the class it falls in.*

## 2026-09-16 — the observation this card asked for: the search loads, no click

**The card wrote on 2026-09-11: «If a session with the extension connected
loads a search page here without any click, that observation reopens this
card as a browser candidate».** Measured 2026-09-16 05:3x UTC, two readings
from a connected tab, no click, no interstitial shown:

```
tab, /jobs/search/?keyword=&area=6001001000     served — Taipei: «共 1000+ 筆», titles
tab, /jobs/search/?keyword=                      served — all Taiwan: «共 1000+ 筆», page selector «第 1 / 150 頁»
tab, /jobs/search/?keyword=&page=150             served — «第 150 / 150 頁», 17+ titles on the page
tab, /jobs/main/                                 served — «96,000+ foreigner-friendly job openings»
tab, /job/95gel                                  served — title, employer link, «2026/09/10更新», address, «月薪45,500~62,500元», a contact person's name
```

**`route: browser · 3000 · 2026-09-16`** — the count is the pager's reach
on the unfiltered search (150 pages of 20), not the board's size: the site
caps its display at «1000+» and states «96,000+» for the foreigner-friendly
subset alone. **What a session does from a tab:** `/jobs/search/?keyword=&page=N`
to 150, the id from `/job/<code>`, and a filter (area, category) to unfold
what the cap hides; the ad's contact person is a name and is never emitted.
No script: the declared client is still answered by the challenge (#404).

**The 2026-09-14 refusal named «domain permission» was the tool, not the
site**: «Navigation to this domain is not allowed» is what `navigate` prints
as a non-first item of a `browser_batch` toward a domain not yet visited in
the session — measured 4/4 on `tecoloco.md` today; this host was served at
the first try.
