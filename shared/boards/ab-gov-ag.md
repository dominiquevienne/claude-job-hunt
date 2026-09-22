# Board measurement — Government of Antigua and Barbuda (`ab.gov.ag`, Antigua and Barbuda): its «Current Vacancies» page — **3 posts on 2026-09-22, ONE OPEN** (Meteorological Officer III, deadline 2026-10-03) beside two whose deadline has passed, each a PDF the department publishes; `abgovag.py` — the markup is the department's own (`<date>`, an unclosed `<span>`), the closed posts are kept and counted, and the PDF is named, never downloaded

<!-- verified: 2026-09-22 -->

<!-- hosts: ab.gov.ag -->
<!-- script: abgovag.py -->
<!-- countries: AG -->
<!-- content: measured · **the page read by the declared client, 2026-09-22 08:5x UTC, the guard on the exact path: `/detail_template.php?page=media/vacancies` 200, 13 689 B, md5 bc57c674409f — **3 posts under «Current Vacancies», ONE OPEN**: Meteorological Officer III (ABMS, deadline 2026-10-03), Deputy Accountant General (Treasury, 2026-07-06, past) and HRM Consultant (Treasury, 2026-03-31, past), each an `<a>` to `media/pdf/vacancies/*.pdf`. The markup is the department's: each post is its own `ul.events_list`, the employer is the `&lt;strong&gt;` INSIDE the link, the title follows the dash in the same link, the deadline sits in a `&lt;date&gt;` element nobody else uses («October 03rd 2026», an ordinal suffix no date library parses), and the `&lt;span&gt;` is never closed. The scan is bounded by the page's own «Events content end»: the footer carries a `ul.events_list` of the same class (a policy PDF). `ab.gov.ag` answers 404 to `/robots.txt` — no file, so no rule (open, certain). **This host is not `mpsl.gov.ag`** (#750). Exercised: `jobs --country-code AG` → **3 emitted, «the page states no count» and «2 already past» said** · 2026-09-22 -->
<!-- witness: none — the page states no count; `abgovag.py jobs` prints the posts read, those without a deadline and those already closed · 2026-09-22 -->
<!-- route: http · 3 · 2026-09-22 -->

**Found by the Antigua and Barbuda search of #620 (a country never
searched), measured 2026-09-18 07:29–07:34 UTC by the declared client, the guard
on the exact path first, `bin/fetch-body.py`, two reads.** The method is
written on #620: four searches naming the Government, the Labour
Department's One Stop Employment Centre and the private boards, no composed
host names. *A measurement, not an adapter.*

The Government's own site, the public source of public-sector vacancies; the Labour Department's One Stop Employment Centre (OSEC) has no site of its own found by this search — its notices go through Facebook and through `dadlijobs.com`.

```
_robots.allowed('ab.gov.ag', '/detail_template.php?page=media/vacancies')   open
GET https://ab.gov.ag/detail_template.php?page=media%2Fvacancies   200 ×2 — two PDF vacancies, both past their deadline
```

The adapter's first line: the page's list of PDF links with their deadlines (a list of two today, with nothing open), the PDF as the ad; a page that has not changed since the spring is a thin flow to be dated, not a verdict.

## The adapter — `abgovag.py` (#728, 2026-09-22)

```
GET /detail_template.php?page=media/vacancies   200, 13 689 B — 3 posts, 1 open, 3 PDFs

<h2>Current Vacancies</h2>
<ul class="events_list"><li><date>Deadline - October 03rd 2026</date> - <span>
  <a href="media/pdf/vacancies/AD_2026_Meteorological_Officer_III.pdf">
    <strong>Antigua and Barbuda Meteorological Service (ABMS)</strong> - Meteorological Officer III
  </a><span></li></ul>
```

**The markup is the department's, and it is read as written.** The `<span>` is
never closed and `<date>` is an element nobody else uses, so the employer is
the `<strong>` **inside the link** and the title is what follows the dash **in
the same link** — splitting the line on its dash would put the department's
name in the title, and reading the span would take everything after it.
«October 03rd 2026» carries an ordinal suffix no date library parses by
default.

**The scan is bounded by the page's own «Events content end».** The footer
carries a `ul.events_list` of the same class — a policy PDF with a 2020 date —
and a scan that ran to the end of the document would publish it as a vacancy.

**The page keeps closed posts, and the issue was opened on that.** #728 records
«rien d'ouvert le 18.09» — two posts, both past. Today there are three, **one
open**: *a month with nothing open is not a page that publishes nothing*, and
the closed ones are emitted with their date and **counted**, never dropped in
silence. `--open-on` drops them only when asked, and says the filter is ours.

**The advertisement is the PDF**: named, never downloaded. **Withheld:**
e-mail addresses and telephone numbers in a title or a department name.

*`ab.gov.ag` is the Government's portal; `mpsl.gov.ag`, the Ministry of Public
Safety and Labour, is a different host whose TLS chain is incomplete (#750,
`blocked`). Two hosts, two tickets. The One Stop Employment Centre has no site
of its own: its notices go through Facebook and Dadli Jobs (#730).*

**Tests and mutations.**
`AGovernmentPageWhoseMarkupIsItsOwnAndWhoseClosedPostsStay`, both ways on
fixtures (the employer split from a title that itself contains a dash, an
ordinal date, a deadline that is not a date at all, the footer's list of the
same class, `--open-on` and its drop count, a page without the heading, a 404,
a bad `--open-on`, the `www.` host refused). Mutation bench on a detached copy,
`python3 -B`, **10 / 10 red**: the employer not split from the title · the
ordinal suffix not tolerated · the heading not required · the scan not bounded
· the closed count silenced · the `--open-on` drop count silenced · the undated
count silenced · the document marked downloaded · the scrub dropped · the host
check dropped.
