# Board measurement — UKG Pro, ex-UltiPro (an ATS, one tenant at a time): the tenant's job board on `recruiting.ultipro.com/<code>/JobBoard/<guid>` is permitted in writing and served, but the list it loads lives under `JobBoardView/LoadSearchResults` — refused in writing to `*` (`Disallow: */JobBoardView`); no route crosses a written refusal, the decision is the owner's (#792)

<!-- verified: 2026-09-20 -->

<!-- hosts: recruiting.ultipro.com, recruiting2.ultipro.com -->
<!-- script: none -->
<!-- countries: * -->
<!-- content: measured · **rules read (200): `User-agent: *` / `Disallow: /` / `Allow: */JobBoard/` / `Disallow: */JobBoardView` / `Disallow: */JobBoard/*/Styles` / `Disallow: */JobBoard/*/AnonymousSessionCheck` — the tenant's board page is permitted by the Allow, the list route it calls is refused; the board page `/HOL1002HPHM/JobBoard/be27b89b-…` (Macmillan; 200, 741 036 B, one read — the second read broke off at 523 351 B, an IncompleteRead) and `/UNI1076UNFI/JobBoard/86df2700-…` (UNFI; 200, 403 954 B ×2, md5 5bd3a01eacea / 6c0ae8917e89 — a token moves) are a Knockout application with no opportunity in the markup, a `__RequestVerificationToken`, and its own settings in an inline script: `pageSize: 50`, `loadUrl: "/<code>/JobBoard/<guid>/JobBoardView/LoadSearchResults"`, `opportunityLinkUrl: "…/OpportunityDetail"`; no JobPosting; `_robots.allowed('recruiting.ultipro.com', '/HOL1002HPHM/JobBoard/<guid>')` → allowed, certain, rule `*/JobBoard/`; the list route `…/JobBoardView/LoadSearchResults` falls under `Disallow: */JobBoardView` — a written refusal, honoured by every route (borne 1); `recruiting2.ultipro.com` serves the same application for other tenants (ARUP, Helix), not read** · 2026-09-20 -->
<!-- witness: none — no list was read; the page states no count · 2026-09-20 -->

**Issue #463 (opened under #406, the ATS families). Tenants found by the
signature `recruiting.ultipro.com/<code>/JobBoard/<guid>` on 2026-09-20 (UNFI,
BMD, Macmillan, ARUP on `recruiting2`, Helix Electric, TridentCare),
measured by the declared client, the guard on the exact path first, two
reads.** *A measurement and a written refusal — the decision belongs to the
owner (§2 sexies), and it is asked for on #792, `adapter` + `blocked`.*

## What UKG Pro is, and where its tenants live

UKG Pro (Ultimate Software's UltiPro, merged into UKG) is a US HR suite
whose recruiting module hosts the employer's job board at
**`https://recruiting.ultipro.com/<code>/JobBoard/<guid>`** (or
`recruiting2.ultipro.com` for other tenants); an opportunity at
`…/JobBoard/<guid>/OpportunityDetail?opportunityId=<guid>`.

## The route — permitted page, refused list

The rules file, verbatim (200, 2026-09-20):

```
User-agent: *
Disallow: /
Allow: */JobBoard/
Disallow: */JobBoardView
Disallow: */JobBoard/*/Styles
Disallow: */JobBoard/*/AnonymousSessionCheck
```

```
GET  https://recruiting.ultipro.com/robots.txt                          200 — * Disallow / · Allow */JobBoard/ · Disallow */JobBoardView …
GET  https://recruiting.ultipro.com/HOL1002HPHM/JobBoard/be27b89b-…      200 — the board's application, no opportunity in the markup
POST …/JobBoard/be27b89b-…/JobBoardView/LoadSearchResults                 NOT SENT — refused in writing (Disallow: */JobBoardView)
```

**The page the site permits carries no ad, and the call that carries them
is the one it refuses** — to every robot, in writing, on the exact path.
The plugin honours a written `Disallow` on every route, browser included
(borne 1), so there is no browser route either: the decision is the
owner's — the user's own `boards.ukgpro.override_robots` key (the
mechanism generalised on 2026-09-13, #403: set by the user, never by
default, always with the warning), or a validated exclusion. A permitted
path that enumerates opportunities (a sitemap, a feed) would be a third
way; none was found on the page.

## What an adapter would give under the derogation, and what it never gives

Each named tenant's opportunities by the page's own call
(`LoadSearchResults`, 50 a page, the page's anti-forgery token) and the
opportunity by `OpportunityDetail`. Never: the refusal crossed without the
user's own key; the contacts; the application (`QuickApply`, an account).
