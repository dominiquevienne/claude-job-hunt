# Board adapter — HelloJob (Azerbaijan)

<!-- verified: 2026-09-04 -->

<!-- hosts: www.hellojob.az -->
<!-- script: hellojob.py -->
<!-- countries: AZ -->
<!-- content: measured · live sitemap read in full, 8 of 8 sampled pages parsed on every field · 2026-09-04 -->

**The only board of the series that does the freshness work itself.**
`/sitemap.xml` declares seven children, two of which are `vacancies.xml` and
`expired-vacancies.xml` — **live and dead in separate files, by the site's own
reckoning.**

Everywhere else it had to be inferred: `jobsbotswana.info` keeps expired
advertisements among the live ones and only a `validThrough` separates them,
`ihararejobs.com` gives 64 % of its entries the date of the measurement, and
`myjobsfiji.com` gives all 3 187 the same one. **An adapter that is told which
advertisements are live cannot be wrong about it**, and that is worth more than
volume.

```
hellojob.py counts                              # both files, with URL and time
hellojob.py list --since 2026-08-06 --fetch     # live only, newest first
hellojob.py ad --slug layihe-rehberi-15784394
```

## What was measured — URL, time, raw count, distinct count

```
https://www.hellojob.az/vacancies.xml
  2026-09-04 22:31 UTC · 190 929 o · 588 <loc> · 588 distinct · 0 duplicates
  44 dates, 2026-02-10 → 2026-09-04 · 533 within thirty days

https://www.hellojob.az/expired-vacancies.xml
  2026-09-04 22:31 UTC · 8 546 148 o · 27 402 <loc> · 27 402 distinct
  2 098 dates, 2019-05-02 → 2026-09-04 — not read by the adapter
```

**Counting both gives 27 990, and that is a different quantity rather than a
bigger one.** `counts` prints both with the time, because a count without its
provenance cannot be checked by the next person.

## Two measurements three hours apart, and the total is conserved

Another session measured the same two files at **21:08 UTC**: 591 live, 27 399
expired. This one at **22:31**: 588 and 27 402.

```
591 + 27 399 = 27 990
588 + 27 402 = 27 990
```

**Three advertisements moved from one file to the other and nothing else
changed.** Not a disagreement between two counts — a board running, and the
conserved total is what shows it.

**The precondition, and it must travel with the argument.** The sum is
invariant *only because the partition is closed*: an advertisement leaves
`vacancies` by entering `expired-vacancies`, and that is the only operation the
site performs on the pair. Any other cause — a client served different content,
a truncated file, a faulty read — **would break the sum**, which is exactly what
makes it a witness.

**`vacancies` / `expired` is closed. `jobs` / `companies` / `blog` is not.** A
`/company/` page never becomes a `/jobs/` page, so a total across those files
constrains nothing and invoking conservation there would be superstition.
**Check the closure before invoking the conservation** — otherwise it is a
coincidence being reused.

**And the competing explanation was tested rather than dismissed.** The earlier
figures were taken under a browser `User-Agent`; these under ours. *"The content
depends on who asks"* predicts the same gap. A 2×2 square at 22:34 UTC — two
agents, two files — returned **588 and 27 402 under both**. Identity has no
effect here, so elapsed time is the whole of it.

## Where the fields come from

**There is no `JobPosting`.** The page's only `ld+json` is a `FAQPage` of
site-help boilerplate — six questions about using the search — carrying nothing
about the advertisement.

The fields sit in a labelled list, `<li><span>LABEL</span>…<p>VALUE</p></li>`:
`Şəhər` (city then street), `Kateqoriya`, `Maaş`, `Bitmə tarixi`. The role comes
from `<title>` before ` vakansiyası`, the employer from the `description` meta
before ` şirkəti`. **Measured on eight advertisements: 8/8 on every field.**

**`Razılaşma ilə` — *by agreement* — is emitted as written in `salary_text`,
and no number is parsed from it.** It is a real answer, not a missing one, and
a numeric `None` would merge it with an advertisement that omits the field.

Month names are listed rather than parsed by locale: `%B` would depend on the
runner's locale, which is not the site's.

## Access and cost

`robots.txt` reads with **no `Disallow` at all**, and every path was asked about
per path. `list` without `--fetch` costs one request; with it, one per
advertisement, so `--since` and `--limit` bound it.
