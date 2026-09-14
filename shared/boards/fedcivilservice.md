# Board measurement — Federal Civil Service Commission (`fedcivilservice.gov.ng`, Nigeria): the commission's site is served and publishes no vacancy — a «Vacancies» page of prose, an application process «under construction», an empty circulars list, promotion notices in the news

<!-- verified: 2026-09-14 -->

<!-- hosts: fedcivilservice.gov.ng, www.fedcivilservice.gov.ng -->
<!-- script: none -->
<!-- countries: NG -->
<!-- content: measured · **no vacancy on any page the site links**: `/page-vacancies` (200, 28 501 B) is a description of the Recruitment Board's mission with no listing; `/page-job_application_process` (200) says «Page currently under construction»; `/advert_tenders` answers 404; `/circulars` (200) says «This list is currently empty»; `/news` (200) carries promotion and examination notices (the latest 9 Sep 2026) as PDFs, none a recruitment; the rules request answers the site's own 404 page — an absence, certain, open; read by the declared client, 01:0x UTC · 2026-09-14 -->
<!-- witness: none — the site states no count and lists no vacancy; the measurement is the set of pages read, each with its code and size · 2026-09-14 -->
<!-- route: none · the site publishes no vacancy listing — a recruitment exercise, when the commission runs one, is announced as a news item with a PDF; there is nothing for a script to render (#404: a script that yields nothing does not count) · 2026-09-14 -->

**The commission that appoints into Nigeria's federal civil service — and
its site, on the day, lists nothing to apply to.** Issue #389, opened
under #291 on a root read in 200. Measured 2026-09-14 01:0x UTC by the
declared client, the guard on the exact path first (the rules request
answers the site's own 404 page: no rule read, an absence).

## The pages, each read

```
GET /robots.txt                                  404 — the site's own «Not Found» page; no rule
GET /                                            200, 44 009 B — «Federation Civil Service Commission»; the menu: Career → Vacancies, Adverts and Tenders, Circulars; What we do → Recruitment & Appointment
GET /page-vacancies                              200, 28 501 B — «Vacant positions details / Recruitment Board»: the Office of the Head of Service's mission and processes; NO position
GET /page-job_application_process                200, 21 482 B — «Page currently under construction»
GET /advert_tenders                              404
GET /circulars                                   200, 15 762 B — «This list is currently empty.»
GET /department-recruitment_and_appointment      200, 22 901 B — the department's functions: «placing advertisement for vacancies in National Dailies, Television, Radio and the Internet»
GET /news                                        200, 29 987 B — promotion and examination notices (9 Sep 2026, 13 Aug 2026, 14 Mar 2026 …), each «CLICK TO DOWNLOAD» a PDF; no recruitment notice on the day
```

## What this card is, and is not

- **A measurement, not a verdict on the commission**: when a federal
  recruitment exercise runs, the department says it advertises «in
  National Dailies, Television, Radio and the Internet» — the site's
  news list is where a notice would appear, as a PDF. On the day there
  is none, and there is no listing at all.
- **No script, by the owner's rule of 2026-09-13 (#404)**: a script that
  renders nothing does not count. What a script could do here — watch
  `/news` for a title containing «recruitment» and hand the PDF's link
  to the user — is a watch, not a board; it is not built, and this card
  says so rather than shipping a route to nothing.
- **Nigeria is covered elsewhere**: `jobberman.md` and
  `hotnigerianjobs.md` are the shipped scripts; MyJobMag (#391) is a
  candidate. The federal public sector's postings, when they exist,
  are re-listed by those boards.
- **To rouvrir**: a recruitment notice in `/news`, or a listing under
  «Vacancies» — the two observations that would renverser this card,
  named here.
