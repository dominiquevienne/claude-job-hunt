# Board adapter — Keejob (Tunisia)

<!-- verified: 2026-09-05 -->

<!-- hosts: www.keejob.com -->
<!-- script: keejob.py -->
<!-- countries: TN -->
<!-- content: measured · 808 advertisements in the sitemap, 25 of 25 sampled pages read · 2026-09-05 -->
<!-- witness: SECOND READING **and** SECOND SOURCE — the two classes at once, which is why this card is the model. The sitemap read twice gave 827 then 808, and the site's own counter states 808 in two places: the second reading converged on the second source. **A net-to-flow objection does not apply**, because the agreement is on the value and not on the change · 2026-09-05 10:58 UTC -->

**The only readable board of the eight Tunisian ranks measured on 2026-09-04** —
rank 1 is a public service whose rules could not be read, rank 3 answers 403 to
its own `robots.txt`. **So this does not add a board to a covered country: it is
the Tunisian market as far as this tool can see it.**

```
keejob.py list                                   # the sitemap alone, one request
keejob.py list --since 2026-08-20 --fetch        # with fields, one request each
keejob.py ad --id 246110
```

## 808, with no duplicates — and 827 eleven hours earlier

```
2026-09-05 00:1x UTC   827 <loc>, 827 distinct, 0 duplicates
                       28 dates, 2026-08-05 → 2026-09-04, all within thirty days
2026-09-05 10:58 UTC   808 <loc>, 808 distinct, 0 duplicates
                       28 dates, 2026-08-06 → 2026-09-05
```

**That there are no duplicates is worth stating**, because it is not the usual
case: `onape.td` lists one advertisement three times, `caglobalint.com` lists
its own index page among its advertisements, and `myjobsfiji.com` puts 2 789
company pages in with 224 jobs. **Here the file length is the board's size**,
and that had to be checked rather than assumed.

`/sitemap.xml` names its children honestly — `sitemap-jobs.xml` beside
`-companies`, `-professions`, `-static` and three blog files.

*Three of the seven children are declared over `http`, not `https`. The adapter
follows only `sitemap-jobs.xml`, which is on `https`; the mixed scheme is
recorded because it bites a caller who follows the index blindly.*

## The witness, and it converged while this card was being written

The site states its own count in two places on `/offres-emploi/` — the results
line and the page title:

```
2026-09-05 00:1x UTC   sitemap 827      site "808 offres d'emploi trouvées"
2026-09-05 10:58 UTC   sitemap 808      site "808 offres d'emploi trouvées"
```

**Two provenances, and they now agree exactly.** The earlier gap of nineteen ran
the way the mechanism predicts — a sitemap keeps recently closed advertisements
a while, so it sits above a live counter — and it closed within eleven hours.

*This is the only figure on any of these cards to have been read twice at
different times. The first reading alone would have shown a gap and left its
direction as an argument; the second turns it into an observation.*

**The window rolls.** `2026-08-06 → 2026-09-05` at the second reading against
`2026-08-05 → 2026-09-04` at the first: thirty days that move, as on `job.am`.
So 808 is what the board keeps, not a total.

*A note on how the second reading nearly went wrong: `grep -c '<loc>'` returned
**1** on a 146 KB file, because `-c` counts matching lines and this sitemap is
five lines long. It looked exactly like a board that had emptied overnight.
`grep -o … | wc -l` gives 808.*

## `strict=False` is not optional, and losing a third would be silent

Each page carries one `JobPosting`. **Three of eight blocks sampled hold a raw
control character inside a string**, which `json.loads` refuses outright.
`strict=False` read all eight, and 25 of 25 on the larger sample.

**A reader without it loses about a third of the board and loses it silently**,
because a decode error on one advertisement reads as a broken advertisement
rather than a broken reader. That is the `jobivoire.py` lesson on a different
site.

## What the fields are worth, measured on 25 advertisements

| field | rate | note |
| :-- | :-- | :-- |
| title · employer · city · region | 25/25 | |
| posted · valid_through | 25/25 | real dates, a month apart |
| `salary_tnd_*` | 9/25 | `TND`, min/max, monthly |
| employer anonymous | 7/25 | the site's own placeholder |
| `employmentType` | 14/14 — **not emitted** | |

**`employmentType` is `"OTHER"` on every advertisement measured.** Present,
well-formed, and carrying no information. **The adapter does not emit it**: a
field whose only value is a placeholder does not become useful by being passed
on, and a caller filtering on contract type would be filtering on a constant.
This is the `salary_shown_flag` species from `shared/plausible-and-false.md`,
and the answer there is the answer here — leave it out and say why.

**The salary carries its currency in the field name** — `salary_tnd_min`,
`salary_tnd_max`, `salary_period` — never a bare number beside a currency that
could travel separately. `kalibrr.md` is the model.

**Seven employers of twenty-five read `Entreprise Anonyme`.** That is the
site's placeholder for an employer who chose not to be named, **not a missing
value**, so it is emitted as written with `employer_anonymous: true`.
*"Anonymous by the employer's choice" and "we could not find it" are different
facts, and a `None` would merge them.*

## Access

`robots.txt` reads and the host sweeps. Its nine `Disallow` rules cover
`/api/`, `/utils/`, `/comments/`, the OAuth login paths and `/banners/click/` —
**none of them a path this adapter uses**, checked per path rather than per
host.

## Cost

`list` without `--fetch` costs **one request** and returns ids and dates.
With `--fetch` it is one request per advertisement, so `--since` and `--limit`
bound it: the board is 808 pages and reading all of them should not happen by
accident.
