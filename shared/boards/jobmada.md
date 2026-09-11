# Board measurement — jobmada.com (Madagascar): `Disallow: /` to everyone, and a written refusal is honoured by every route

<!-- verified: 2026-09-11 -->

<!-- hosts: jobmada.com, www.jobmada.com -->
<!-- script: none -->
<!-- countries: MG -->
<!-- witness: none — nothing was read past the rules file, which is the only body this card holds: 26 bytes, the same on both hosts, four reads · 2026-09-11 -->

**This card is a measurement and not an adapter, and the measurement is one
request per host, twice.** *Madagascar had one card (`portaljob-madagascar.md`,
indeterminate — an Inertia.js shell) and no adapter; this host was named in
a survey's prose on 2026-09-04 and never asked.* **Asked, it answers with a
rule, and the rule is the whole answer.**

## Step 1 — the rules, twice, on both hosts (2026-09-11 13:47–13:48 UTC)

```
https://jobmada.com/robots.txt        200   26 o   md5 83daced97d66ba47ac4837f35a1be311   ×2
https://www.jobmada.com/robots.txt    200   26 o   md5 83daced97d66ba47ac4837f35a1be311   ×2   the same file

    User-agent: *
    Disallow: /
```

**Group `*`, rule `/`, `certain: True`** — `_robots.verdict()`: *«everything
closed, evenly. Not swept.»* No `Crawl-delay`, no `Sitemap:`, no other group.
**Nothing else was fetched: the guard on the root, the listing, an
advertisement and a sitemap all resolve to this one rule**, and a request past
it would be the act the rule forbids.

## Which kind of refusal this is — and it is the one no route crosses

> **A `Disallow` written in the rules is an intention; it is not crossed by any
> route, browser included** — bound 1 of the 2026-09-07 doctrine, the bound
> that separates «the transport refuses our client» from «the operator said no».

*This is neither family (1) — the 25-byte vendor default that a browser is
served past, the class of #222 — nor family (3), a challenge. It is the case
`shared/robots-policy.md` lands on **obey** by its own four questions: aimed at
nobody in particular, even-handed, no sanctioned door.* **The one exception the
repository carries to a `*` / `Disallow: /` is `api.smartrecruiters.com`, by the
owner's decision of 2026-09-08, and §2 sexies says it extends to no other
host.**

**A note on the instrument, not on the host.** `_robots.identity('jobmada.com')`
reports `state: 'browser'` because both tokens are refused — but they are
refused by the `*` group, not by name, and the «browser» state was written for a
host that names both tokens and refuses them. *On a `*` refusal the browser is
excluded too; `verdict()` says so, `identity()`'s label does not.* Reported to
the module's keeper, not changed here.

## What this card does not say

Nothing about the board — its size, its markup, its language — because nothing
was read. **«Madagascar's `jobmada.com` refuses every robot in writing» is what
this card can write; whether the site is alive behind that line, it cannot.**
What would change it: the operator changing the file, which the next reader
measures with the same two requests.
