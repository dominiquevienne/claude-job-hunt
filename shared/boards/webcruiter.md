# Board measurement — Webcruiter (a Nordic ATS, one tenant at a time): every employer's list lives on `candidate.webcruiter.com/<lang>/Home/companyadverts?companylock=<id>` — a host that writes `User-agent: * / Disallow: /` and opens its listing paths to Googlebot alone; no route crosses a written refusal, and nothing is readable to write the adapter from — the user's own key is the exit (#403), and it needs a first keyed read (#465)

<!-- verified: 2026-09-20 -->

<!-- hosts: candidate.webcruiter.com, www.webcruiter.no -->
<!-- script: none -->
<!-- countries: * -->
<!-- content: measured · **rules read twice on each host, 2026-09-20 13:2x UTC, the declared client. `candidate.webcruiter.com/robots.txt` (200, 1 085 B ×2, md5 e6df8957646f ×2): `User-agent: Googlebot` / `Allow: /home/alladverts/`, `/home/companyAdverts/`, `/brannjobb/`, `/kirkejobb/` in nine locales, then `User-agent: * / Disallow: /` — the listing paths are opened to one named crawler and refused to everyone else; `www.webcruiter.no/robots.txt` (200, 130 and 128 B, md5 cd184ea0a63c / a9e9cfdb1347 — a byte moves): `User-agent: Googlebot` / `Allow: /wcmain/advertviewpublic.aspx`, `/wcmain2/advertviewpublic.aspx`, then `User-agent: * / Disallow: /`; `www.webcruiter.com` publishes no rules file (404) and is the vendor's marketing site. `_robots.allowed()` on `/` of both hosts: allowed False, certain, rule `/`. Tenants named by the family's signature in a search engine (2026-09-20): Trondheim kommune (`companylock=7254`), NRK (`238765`), Bærum kommune (`67504050`), Kristiansand kommune (`650010`), Arendal kommune (`3293781034`), Grimstad (`3293780607`) — all under `/nb-no/Home/companyadverts`. No page was requested on either host — the refusal is written and it covers every path** · 2026-09-20 -->
<!-- witness: none reachable by a permitted path — the count would live on the refused `companyadverts` page · 2026-09-20 -->

**Issue #465 (opened under #406, the ATS families). The premise of 13.09
(`User-agent: * / Disallow: /` on `candidate.webcruiter.com`) verified on
2026-09-20: it holds, and `www.webcruiter.no` writes the same. The
tenants exist and are named; the route to them is refused in writing to
every agent but Googlebot.** Rank: the pilot's order of 2026-09-20 12:5x,
after #464.

## What Webcruiter is, and where its tenants live

Webcruiter is a Norwegian ATS (Oslo; Norwegian municipalities, hospitals,
NRK, Equinor's suppliers) whose candidate side moved from
`www.webcruiter.no/wcmain/…` to **`candidate.webcruiter.com`**: an
employer's list is `/<lang>/Home/companyadverts?companylock=<id>`, an advert
`/<lang>/Home/Ad/<id>` or the old `advertviewpublic.aspx?oppdragsnr=…`. The
employer's own site links or frames these pages; it does not carry the
list itself (Trondheim, NRK and Bærum link to `candidate.webcruiter.com`).

## The route — refused in writing, to everyone but one named crawler

```
User-agent: Googlebot
Allow: /home/companyAdverts/     (+ alladverts, brannjobb, kirkejobb, nine locales)
User-agent: *
Disallow: /
```

**This is the AMS / SmartRecruiters shape** (`shared/robots-policy.md`): a
platform opened to one privately held actor and closed to every other,
free or paid, browser or script. The plugin honours a written `Disallow`
by every route (borne 1), so there is no browser route either. **The exit
is the user's own `boards.webcruiter.override_robots: true`** — the general
mechanism of #403, set by the user in their own name, never by default.

**And nothing is readable to write the adapter from.** UKG Pro (#463) and
Työmarkkinatori (#371) were built under the key because a permitted page
or a served bundle showed the request the adapter had to make; here every
path of both hosts is refused, and an adapter written blind would be a
guess presented as a route. **What lifts it:** one `companyadverts` page
and one advert, read by a user who has set the key in their own workspace
(or a permitted path that carries the list — none found: no sitemap line,
no feed, the employers' sites link out), given to the repository as a
fixture; the adapter follows in the same shape as `ukgpro.py` (the gate on
the list first, exit 7 without the key, the banner with it).

## What an adapter would give under the key, and what it never gives

Each named tenant's adverts by its `companyadverts` page (title, place,
deadline, the advert's page), the advert by its own page. Never: the refusal
crossed without the user's own key; the contacts an advert names (Webcruiter
adverts carry the hiring manager's name and telephone — withheld); the
application (`/cv?…`, an account).
