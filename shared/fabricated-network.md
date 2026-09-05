# The fabricated network — thirty-one hosts no adapter may be written for

<!-- verified: 2026-09-05 -->

**Thirty-one African national job boards, plus one continental portal that
carries no advertisement, are a single fabricated network.** Their content is
generated from a shared vocabulary; the advertisements do not exist. An adapter
written for any of them would serve a user jobs to apply for that were never
posted, and would make the market look more open than it is.

**Issue #157 establishes this. No sheet may be written for a host on this list
without citing that issue.**

`shared/plausible-and-false.md` is the doctrine; this page is the list.

## Why the list rather than a test

**Nothing in the form of these sites distinguishes them.** They publish clean
sitemaps, plausible dates, real city names, credible job titles, hundreds of
entries each. Only the comparison *between countries* betrays them — a shared
label vocabulary at ~17 % where unrelated boards sit near 4 %, and seven of the
eight dated nodes opening between 22 and 31 May 2026 across four time zones.

**A per-host check cannot see it. That is why the answer is a list.**

## The list, at 2026-09-05

The portal, which carries no `job_listing` sitemap and is not a content node:

    africajobsearch.com

The thirty-one country nodes:

    algeriajobsearch.com        malawijobsearch.com
    angolajobsearch.com         mauritiusjobsearch.com
    botswanajobsearch.com       moroccojobsearch.com
    cameroonjobsearch.com       mozambiquejobsearch.com
    egyptjobsearch.com          namibiajobsearch.com
    eritreajobsearch.com        nigeriajobsearch.com
    eswatinijobsearch.com       rwandajobsearch.com
    ethiopiajobssearch.com      senegaljobsearch.com
    gambiajobsearch.com         sierraleonejobsearch.com
    ghanajobsearch.com          somaliajobsearch.com
    kenyajobsearch.com          southafricajobsearch.com
    lesothojobsearch.com        southsudanjobsearch.com
    liberiajobsearch.com        sudanjobsearch.com
                                tanzaniajobsearch.com
                                tunisiajobsearch.com
                                ugandajobssearch.com
                                zambiajobssearch.com
                                zimbabwejobsearch.com

**Three are spelled `jobssearch`, with two `s`** — Ethiopia, Uganda, Zambia.
They are not typos on our side; that is how the hosts resolve.

## If a pattern is written, it is tested in both directions

**A pattern built on the twenty-eight single-`s` hosts misses exactly three, and
its silence is indistinguishable from an absence.** This has now happened three
times on this same network: first a missing `www.`, then this `s`, then this `s`
again after the pattern had been widened *for the `www.` and nothing else*.

    (?:^|//)(?:www\.)?[a-z0-9-]+jobs?search\.com$

**Two controls, and both must be run:**

| input | must | why |
| :-- | :-- | :-- |
| `ethiopiajobssearch.com` | **match** | the double `s`, missed three times |
| `jobsearch.api.jobtechdev.se` | **not match** | **Platsbanken** — a legitimate Swedish public API already carried by `shared/boards/platsbanken.md` |

The second is the one that matters. A pattern loose enough to be safe on the
first is loose enough to swallow a board this repository already serves.

**This was not hypothetical while writing this page.** The first run of the
control above extracted the host list from this very file with a pattern that
handled one column of the two-column block and not the other. It reported
**19 hosts of 32**, missed `ethiopiajobssearch.com` among them, and then
announced *"both directions pass"* — on a set that was missing thirteen entries.
**The failing test and the passing test look the same when the population is the
thing that is wrong.** Re-extracted with `\b([a-z0-9-]+jobs?search\.com)\b`
over the whole page: 32 of 32 match, 0 of 8 false positives, and the narrow
pattern misses exactly the three double-`s` hosts.

**A control over a population you also extracted tests two things at once, and
reports only one of them.**

**And the pattern is a convenience, not the authority. The list is the
authority** — a thirty-second host could be registered tomorrow under a name no
pattern anticipates, and a host could match the pattern without belonging to the
network.

## What is established, and by what

| instrument | what it establishes |
| :-- | :-- |
| same generator, same eighteen sitemaps in the same order, same slug template | a common technical origin |
| shared labels between countries, ~17 % against ~4 % for unrelated boards | a common inventory |
| seven of eight dated nodes open 22–31 May 2026, on four time zones | **a single act** |
| the same `sales@` and `support@` on the portal's domain, on eight nodes of eight | **one operator, declared by the sites themselves** |

Closure was checked by **two paths that do not depend on each other** — the list
the portal declares, and the hosts named in what the nodes serve. No discrepancy
on either side.

## What is not established, and must not be written

- **Domain antecedence.** No registry was queried. A first advertisement date is
  not a creation date. One node, `eritreajobsearch.com`, opens on 29 April —
  a month before the other seven — and that makes it a precursor, not a phase.
- **The operator's name**, beyond what the sites declare themselves.
- **The content of twenty-three of the thirty-one.** They carry a verified name
  and no figure, deliberately.
- **That the list is closed for ever.** It is closed at 2026-09-05, on two
  concordant paths.

## The measured eight, for whoever needs an order of magnitude

    somalia     475    south sudan  466    ethiopia  453    egypt   439
    eritrea     429    lesotho      424    rwanda    382    senegal 339

Median 449 across sixteen nodes measured, range 339–681. **An extrapolation to
thirty-one gives ~13 900 fabricated advertisements — quoted with its bounds
(10 500–21 100) and its denominator, never as a bare number.**
