# Board adapter — Emplois Burkina (Burkina Faso)

<!-- verified: 2026-09-14 -->

<!-- hosts: emploisburkina.bf -->
<!-- hosts-source: named by the Burkina Faso country page, rank consigned, 2026-09-04; its sitemap is declared on the third-party host `afriqueemplois.com` and the guard was taken there separately · 2026-09-07 -->
<!-- script: none -->
<!-- countries: BF -->
<!-- content: indeterminate · remeasured 2026-09-08 09:01-09:07 UTC at 10 s spacing: of the 24 URLs the network attributes to this host, **4 serve a real `JobPosting`**, **7 redirect to the site root** (271 550 bytes each, identical), and **13 could not be read at all** — the host stopped accepting connections after the 11th request and never resumed. So the live count is **between 4 and 17**, and no single number describes it · 2026-09-08 -->
<!-- witness: the site's own «2305 offres» on the root and `numberOfItems: 2305` in its CollectionPage JSON-LD (a category page: «165 offres d'emploi dans la catégorie», `numberOfItems: 165`), read by the declared client on 2026-09-14 10:47–10:53 UTC at 3 s spacing, 200 on every page asked (7 requests, no connection refused today); the pages carry 3–4 cards each, the rest of the list behind `/api/load-more?page=N&category=…` — `/api/` is refused in writing — and the «EXCLUSIF» cards behind a subscription modal; the network's job sitemaps on `afriqueemplois.com` (`sitemap-jobs.xml`, `sitemap-jobs-BF.xml`) answer 500, twice · 2026-09-14 -->
<!-- route: none · served, and the list is locked: 3–4 cards a page in the HTML, the rest by `/api/load-more` (refused in writing, honoured by every route), the «EXCLUSIF» ads behind a paid subscription, the network's sitemaps 500 today, no JobPosting on the post page any more (there was one on 2026-09-08); a script would render a score of advertisements against a stated 2 305 — the pilot to say whether that counts; next control of the sitemaps 2026-09-21 · 2026-09-14 -->

**Burkina Faso had no card in this repository.** This one records a
measurement that **stopped**, and why.

## The network, re-verified today

`emploisburkina.bf` declares its sitemap on **another host** —
`https://afriqueemplois.com/sitemap.xml` — and the guard was taken there in
its own turn.

```
2026-09-04 (country page)   149 advertisements · 25 for Burkina
2026-09-07 (this reading)   141 advertisements · 23 for Burkina

partition        141 ids, 141 distinct, ZERO present on two domains
                 afriqueemplois.com 75 · emploiivoire.ci 37
                 emploisburkina.bf  23 · emploisenegal.sn  6
lastmod          141 of 141, 2026-01-12 … 2026-09-07
```

**The third archetype holds three days later**, on a smaller inventory.
*And the dates are on the sitemap, which the country page does not record:
freshness is measurable here without opening an advertisement.*

**`sitemap-jobs-BF.xml` still answers with 6 615 bytes that are not a
sitemap** — the country page called it a Laravel error page and the byte count
is identical. **The general file is what carries the Burkinabè URLs.**

## What six probes showed, and why they are not twenty-three

```
5 of 6   redirect to https://emploisburkina.bf/ — the HOMEPAGE title
1 of 6   serves a real advertisement, `JobPosting` present
         « World Vision recrute un Directeur en Recherche stratégique »
```

**Without `final_url` the five would have been counted as advertisements**, at
272 KB of homepage each. *That field is why this card does not open with a
count of 23.*

**And the behaviour belongs to the domain, not to the network**:
`afriqueemplois.com` served both its probes, `emploiivoire.ci` one of two,
`emploisenegal.sn` redirected both to `/sn`.

## The measurement stopped, and the cause is mine

**Reading all 23 was the right instinct — 23 is small, and a rate on six is
worse than a count on twenty-three.** It failed:

```
23 attempted · 1 answered · 22 failed at the transport
~32 requests to this host in about 90 seconds
     9 through bin/fetch-body.py, 16:29:54Z … 16:31:06Z
    23 in a sweep that paced itself at 1 s and knew nothing of the 9
```

**The host answered every probe minutes earlier and then stopped.** *The most
likely reading is that the rate was mine.* **No count is published, and
`content:` says `indeterminate` rather than a zero** — *a zero manufactured by
one's own request rate is the defect this repository has already paid for.*

### Two faults in my own instrument, and the second is worse

**`Pace` is per-process.** The sweep started fresh and had no knowledge of the
nine requests already made from another script. **Two tools pacing correctly
can still hammer a host together**, and nothing in either one can see it.

**And the sweep recorded `code: null` with no reason.** The exception text was
discarded, so the record cannot distinguish a refusal from a timeout from a
reset — *the failure is attested and its nature is not.* **A record that
cannot say why is why this card cannot say what.**

## What remains to be done, and it is not more requests today

**Re-read the 23 after a pause, from one process, at a slower rate.** The
sitemap is on a third host and costs one request; the 23 are the whole
Burkinabè inventory of this network.

*And the question that decides whether an adapter is worth writing is already
sharp: if five in six of the listed URLs redirect to the root, this facade
lists far more than it serves, and the board carrying the matter is
`afriqueemplois.com`.*


## 2026-09-08 — remeasured, and the pacing theory does not survive it

**The 2026-09-07 card blamed our own rate:** *~32 requests in 90 s, 22 of 23
failing.* **Today's run used 10 s spacing — 6 requests a minute, roughly a
third of that — and the host still cut us off.**

```
ordre des 24, 09:01 -> 09:07:16 UTC
.....A..AAAxxxxxxxxxxxxx
. redirect to root (271 550 bytes, identical)   A real JobPosting   x unreadable

11 requests answered, then 13 consecutive failures and no recovery
```

**What the 13 are, exactly — and they are not refusals.**

```
INDETERMINATE: robots.txt could not be read after 3 attempt(s):
               <urlopen error [Errno 61] Connection refused>
```

**The guard could not be taken, so nothing was fetched.** *`fetch-body.py`
declined rather than reaching for the page without a verdict, which is the
behaviour it was written for.* **13 unknown is not 13 closed**, and this card
does not count them either way.

### What this measures, and what it retracts

| of the 24 URLs the network attributes to this host | |
| :-- | --: |
| serve a real `JobPosting`, no redirect | **4** |
| redirect to the site root — 271 550 bytes, identical to the byte | **7** |
| unreadable, connection refused at the guard | **13** |

**So the live inventory is between 4 and 17.** *Four is measured; seventeen is
four plus the thirteen unknowns; and no figure of 23, 24 or 25 was ever a count
of live advertisements — those are counts of URLs in a third party's sitemap.*

**And the redirects are why `final_url` was in the protocol.** *All seven answer
HTTP 200 with a 271 550-byte body.* **Without recording where they landed, all
seven would have been counted as advertisements** — a plausible 11 instead of a
measured 4.

### The pacing theory is now doubtful, and that changes the prescription

**Yesterday's reading was "a rate that was ours". At a third of that rate the
host still stopped, after 11 requests rather than after 90 seconds.** *That
points at a cumulative count rather than a rate* — **and if it is cumulative,
waiting longer between runs does not help, which is exactly what yesterday's
prescription assumed.**

**This is a hypothesis and not a measurement.** *One request 35 seconds after
the run was also refused, and 35 seconds is not a test of recovery.* **What
would test it: a single request after a long idle period.** *Two observations
now share a shape; neither isolates the variable, and the honest reading is that
we do not know what trips it.*

## 2026-09-13 — #283: a timeout on the rules file is an absence of rules — and today the file reads

The INDETERMINATE of 2026-09-08 («could not be read after 3 attempt(s)») was
a verdict on a rules file that did not answer; since #283 (owner's decision
of 2026-09-13) that is `no-rules-timeout`, open on `certain: False`, with the
first transport request waiting 10 s. On 2026-09-13 it does not even come to that:
`/robots.txt` **reads** (348 B, `sweep: True, certain: True`) and the root
answers **200, 309 107 B, twice** (15:28:52Z, 15:28:55Z, the host's
`Crawl-delay: 1` honoured). *The measurement above stands as dated; the
host is served today.*

## 2026-09-14 10:47–10:53 UTC — the host answers, the site has changed, and the list is locked

The host that refused connections after the eleventh request on
2026-09-08 answered every request today (7, at 3 s; `Crawl-delay: 1` in
the rules). The site is a new build — a WordPress-less app of the
Afrique Emplois network (`afriqueemplois.com`, with `/ci`, `/sn` … fronts
and per-country job sitemaps declared there):

```
GET /robots.txt               200 — * Allow /, Disallow /api/, /login, /register, /forgot-password, /profile, /subscription, /talents/create; Sitemap https://afriqueemplois.com/sitemap.xml; Crawl-delay 1
GET /                         200, 298 610 B — «Offres d'emploi 2305 offres», CollectionPage numberOfItems 2305, #posts-container with 3 /post/<id> cards and «EXCLUSIF» cards that open a subscription modal; the rest by fetch(`/api/load-more?page=…`)
GET /category/12              200, 254 779 B — «165 offres d'emploi dans la catégorie», numberOfItems 165, 4 cards, the rest by /api/load-more?page=N&category=12
GET /post/38265               200, 92 649 B — «Caritas Suisse recrute 03 experts», «Date limite: 14 sept. 2026», the body (an e-mail in it), «Postuler»; WebSite / Organization / BreadcrumbList JSON-LD, no JobPosting
GET afriqueemplois.com/sitemap.xml            200 — 22 files: sitemap-jobs.xml and 17 sitemap-jobs-<CC>.xml
GET afriqueemplois.com/sitemap-jobs-BF.xml    500, 6 615 B — twice (10:52, 10:53); sitemap-jobs.xml 500 as well
```

**What this leaves.** The count is stated and read; the list is locked
three ways — the pager is an `/api/` route the rules refuse in writing
(honoured by every route, a tab included: the plugin does not scroll a
page into a refused call), the «EXCLUSIF» advertisements are behind a paid
subscription, and the network's sitemap that would name every post
answers 500 today. A script would emit the three or four cards of the
root and of each category page — a score of advertisements against a
stated 2 305, «short» by design — which is something rendered and next to
nothing covered; the pilot decides whether that counts (#404). **Next
control 2026-09-21**: the BF sitemap of `afriqueemplois.com`; if it
answers, it is the inventory and a script follows.

