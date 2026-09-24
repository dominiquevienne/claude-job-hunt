# Board measurement — Afgjobs (`www.afgjobs.org`, Afghanistan): the engine still describes it as «The Fastest Growing Jobs Portal in Afghanistan», and on 2026-09-24 **nothing on the host serves a board** — the root refuses 403 to every client including a real browser, and every other path answers a hosting error page carrying an advert. The 403 is not what shuts the door: there is no longer anything behind it

<!-- verified: 2026-09-24 -->

<!-- hosts: www.afgjobs.org -->
<!-- script: none -->
<!-- countries: AF -->
<!-- content: out-of-domain · **the root answers HTTP 403, 787 B, md5 ff715af41f83 (×2, unmoved since 2026-09-17) — a LiteSpeed «Access to this resource on the server is denied!» page, static, no challenge — and a real Chrome on the same machine and address is served the SAME 403; every other path answers HTTP 404, 4 511 B, md5 b16e9097fc7d — a hosting error page («This Page Does Not Exist», `/htdocs_error/page_not_found.svg`) carrying a Google advert iframe, with no navigation and no board markup; `_robots.allowed('www.afgjobs.org','/')` → open, certain, `state: absent` — because the rules PATH is one of those 404s** · 2026-09-24 -->
<!-- witness: none — no listing exists to count · 2026-09-24 -->

**Measured 2026-09-24 19:06–19:12 UTC by the declared client, the guard on the
exact path first, `bin/fetch-body.py`, two reads of the root; and by a real
Chrome driven from the same machine — the tab the 2026-09-17 card named as its
next reading, which was not connected that day.**

```
GET https://www.afgjobs.org/            403,   787 B, md5 ff715af41f83 ×2   (Claude-User)
GET https://www.afgjobs.org/            403,   787 B, the same page          (Chrome, real browser, same address)
GET https://www.afgjobs.org/robots.txt  404, 4 511 B, md5 b16e9097fc7d
GET https://www.afgjobs.org/sitemap.xml 404, 4 511 B, md5 b16e9097fc7d       (byte-identical to the line above)
GET https://www.afgjobs.org/jobs        404, «This Page Does Not Exist»      (Chrome, real browser)
```

**The browser answers borne 0, and it answers it the other way round from what
the issue expected.** A 403 rendered to the declared client *and* to a bare
`curl` left open whether a real browser would be served; it is not. **A host
that refuses a real browser too has refused** — so no browser route opens here,
and none is owed.

**But the refusal is no longer the interesting fact.** The 403 covers `/` only:
every other path is served, and what it serves is a *hoster's* error page —
«This Page Does Not Exist», an image under `/htdocs_error/`, and an advert
iframe. **There is no application behind this name.** The engine's «Fastest
Growing Jobs Portal» line is a cached description, not a measurement; it can
outlive the site it describes by years, and here it has.

> **A 403 says «not to you». A parking page says «not to anyone, about
> anything».** *They are opposite facts, and the first one hides the second —
> the root is the one path that never reveals it.*

**A CORRECTION TO THE 2026-09-17 CARD, and it is the kind that leaves no
symptom.** That card wrote «`_robots.allowed(...)` → open, certain (**the rules
file itself is served**)». The tool's own `reason` says the opposite, and says
it in words:

```
"no rules were read — the host answered HTTP 404 and the state is `absent`.
 **A 404 is knowledge**: there is no file, so there are no rules."
state: absent
```

**`certain: True` means «no rules apply», not «we read the file».** The two
readings agree on the verdict — open, either way — so nothing ever contradicted
the card, and the sentence survived a week. *It also supplied the only evidence
that something was still alive on the host: a served rules file implies a
server that serves.* **Read the field the tool sets (`state`), not the mood of
the field it happens to print beside it.**

**This is not a verdict of closure, and not a verdict of absence either
(§2 sexies).** What is measured is that on 2026-09-24 this host served no
listing, no navigation and no job markup by any of the three clients tried. Whether
Afgjobs is to be written off is the owner's call, and it is carried to him with
the reason named: *not «refused us», but «is no longer a board»* — the class of
`africajobboard` and `myjoboo`, not the class of `tala-com`.
