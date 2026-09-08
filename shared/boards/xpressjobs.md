# Board adapter — XpressJobs (Sri Lanka): open, moved, and rendered client-side

<!-- verified: 2026-09-08 -->

<!-- hosts: xpress.jobs -->
<!-- script: none -->
<!-- countries: LK -->
<!-- hosts-source: `xpressjobs.lk` named on Sri Lanka's country page 2026-09-02; it redirects, and the guard reports the rules as read from `xpress.jobs` · 2026-09-08 -->
<!-- content: indeterminate · the sitemap holds 8 815 URLs and **zero advertisements** — 8 725 are `/Organization/` employer profiles and 53 are listing, sector and per-employer pages; every route returns the same 1 766-byte client-side shell · 2026-09-08 -->
<!-- witness: none — the site states «over 12,000 organizations», which is a claim about employers and not a count of advertisements -->

**Sri Lanka's country page listed this host as *«à instruire»* on 2026-09-02.
It is instructed: open, reachable, and not readable over HTTP.**

## The host named on the country page is not the host that answers

```
guard on xpressjobs.lk  ->  "These rules were read from 'xpress.jobs', not from …"
```

**The board has moved domain**, and the guard said whose rules it had actually
read rather than reporting them as the requested host's. *That is the
behaviour `shared/robots-policy.md` requires — «the rules that apply are the
receiving host's» — working before anything was fetched.*

Everything below is `xpress.jobs`.

## The rules are as open as a rules file gets

```
# https://www.robotstxt.org/robotstxt.html
User-agent: *
Disallow:
```

**Seventy bytes, one empty `Disallow`.** *An empty `Disallow:` is how a file
says nothing is closed* — not a refused path, which is a distinction this
repository has had to make before, on a 26-byte file that was reported as
refusing one path.

## The sitemap has 8 815 URLs and not one advertisement

```
/Organization/<id>/<slug>   8 725     employer profiles
/jobs/sector/<sector>          ~40     category pages
/Organization/<id>/jobs          4     per-employer job lists
/Jobs · /jobs/cvless · static     …     the rest
                            -----
                            8 815     lastmod on 0 of them
```

**Counting `<loc>` here would report a very large board where the file
contains no advertisement at all** — not 16.6 times too large, as on
`myjobsfiji`, but a number with no relation to the quantity.

*And nothing carries a `lastmod`*, so the file says nothing about freshness
either.

## Every route returns the same 1 766-byte shell

```
/Jobs                          1 766 o · no payload carrier · JobPosting 0
/jobs/sector/banking           1 766 o · idem
/Organization/10389/jobs       1 766 o · idem
<body><noscript>You need to enable JavaScript to run this app.</noscript>
       <div id="root"></div></body>
```

**Checked for payload carriers, not assumed from the size** — `data-page`,
`__NEXT_DATA__`, `application/json`, `__INITIAL_STATE__`: none present.

*That control exists because it was got wrong:* `portaljob-madagascar` was
filed as serving nothing when it serves its whole page in a `data-page`
attribute. **Here the check was run and the shell really is empty.**

### And the endpoint is not statically extractable

The bundle is 4.3 MB minified. It names `api/` paths for images and CVs —
`api/vacancy/getJobDescriptionImage?`, `api/candidate/cv?` — but the base is
**computed at runtime**:

```js
zs = Na() + "api/"
```

*The search endpoint is assembled from minified identifiers.* **Finding it
would mean executing the bundle, not reading it**, and this card does not
guess a path the site never writes down.

## What this is, and what it is not

**Not refused** — the rules are the most permissive form there is, and every
request returned 200. **Not absent** — the site is live and says it serves
over 12 000 organisations. **Not an anti-robot challenge** — nothing was
posed.

> **The object is simply not on the wire.** *A client-side application that
> computes its own API base is unreadable by this repository's HTTP route, and
> that is a property of the site's architecture rather than of its policy.*

**Sri Lanka stays uncovered by a national adapter.** *The country page records
that `hiring.cafe` carries 25 cards with a Sri Lankan city and that an existing
adapter reaches them; this card says nothing about those and does not count
them.*

**The other named hosts, from the country page and not re-measured here:**
`topjobs.lk` answers `/robots.txt` with 1.13 MB of home page and returns the
same body for an invented URL; `jobsnet.lk` serves a self-signed certificate
issued for `ln2.ceynet.asia`; `labourdept.gov.lk` is broken while
`labourmin.gov.lk` renders. `ikman.lk` — classifieds with a jobs section —
remains genuinely uninstructed, and its rules file **explicitly allows nine AI
agents including `ClaudeBot` and `anthropic-ai`**, with a comment saying so.
