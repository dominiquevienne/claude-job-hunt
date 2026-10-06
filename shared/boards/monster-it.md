# Board measurement — Monster Italia (`monster.it`, Italy): 403 at the root, and `monster.it` → `monster.com/it` is TWO hosts and not an arrow

<!-- verified: 2026-10-06 -->

<!-- hosts: www.monster.it, monster.it, www.monster.com -->
<!-- script: none -->
<!-- countries: IT -->
<!-- content: measured · **read 2026-10-06: `www.monster.it/` answers HTTP 403 with 774 B** under the declared identity. **AND THE REDIRECTION IS TWO HOSTS, NOT AN ARROW: `monster.it` publishes NO readable rules (`state: no-rules`, `certain: False`, so an absence of rules and therefore open under the 2026-09-13 decision) while `www.monster.com` serves one (`state: read`, `certain: True`).** *Two different states, each guarded separately, because `robots.txt` binds a HOST and not a brand — the same shape as `inpa.gov.it` / `www.inpa.gov.it` in tranche 1.* Neither writes a **`Crawl-delay`**, so the 2 s of our own pace apply. What remains: whether `monster.com/it` serves the Italian adverts to a plain client, and borne 0 on the 403 before any browser route is considered · 2026-10-06 -->
<!-- witness: none — a 774-byte refusal states nothing · 2026-10-06 -->

## Measured 2026-10-06 under the declared identity, one guard per host form

Opened under **#949**, tranche 2 — the six Italian generalists and classifieds.
*The owner opened the campaign by tranches on 2026-10-06, verbatim « oui, ouvre
#949 par tranches, commence par l'Italie ».*

**The guard was taken on EVERY host form separately, in a turn distinct from the
retrieval, because `robots.txt` binds a HOST and not a brand.** *Thirteen forms
were guarded across this tranche and they returned THREE different states —
`read`, `no-rules` and `unrecognised` — all open, which is why `state` and not
the verdict is what each card records.*

**No adapter is declared here, and that is the finding rather than an
omission.**
