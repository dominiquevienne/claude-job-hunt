# Board measurement — Openjobmetis (`openjobmetis.it`, Italy): an antirobot challenge served as HTTP 200, in 836 bytes

<!-- verified: 2026-10-06 -->

<!-- hosts: openjobmetis.it, www.openjobmetis.it -->
<!-- script: none -->
<!-- countries: IT -->
<!-- content: indeterminate · read 2026-10-06 — the root answers HTTP 200 with 836 B whose body is an Incapsula interstitial: `META ROBOTS NOINDEX, NOFOLLOW`, an iframe to `/_Incapsula_Resource` and the words «Request unsuccessful», so a refusal arrives under a success code that neither the status nor the size reveals; borne 2 forbids defeating an antirobot control by ANY route, the browser included, so this stays indeterminate and no route is attempted · 2026-10-06 -->
<!-- witness: none possible — the body carries a per-request incident identifier, so its fingerprint MOVES by construction and no md5 comparison is meaningful here · 2026-10-06 -->

## Measured 2026-10-06 — 836 bytes, HTTP 200, and nothing behind it that we may reach


Opened under **#949**, tranche 3 — the Italian staffing agencies, the ATS and the
sector board. *The owner opened the campaign by tranches on 2026-10-06, verbatim
« oui, ouvre #949 par tranches, commence par l'Italie ».*

**The guard was taken on EVERY host form separately, in a turn DISTINCT from the
retrieval, because `robots.txt` binds a HOST and not a brand.** Eleven forms were
guarded across this tranche; nine answered `state: read` and two `unrecognised`,
all open, **and not one carries a `Crawl-delay`** — so the pace is ours, and an
absent delay is not an absence of rate limiting. *Retrieval through
`bin/fetch-body.py` under the declared identity, provenance written beside each
body.* No contact value is reproduced anywhere below; counts only.

```
openjobmetis.it/     HTTP 200      836 B      <- le code et la taille ne disent rien
corps : <META NAME="ROBOTS" CONTENT="NOINDEX, NOFOLLOW">
        <iframe src="/_Incapsula_Resource?…&incident_id=…&cip=…">
        « Request unsuccessful. Incapsula incident ID: … »
title  (aucun)   h1 (aucun)   href 0   texte visible 82 caracteres
rules : `state: unrecognised`, `certain: False` on both host forms -> OPEN (#283)
```

**A REFUSAL SERVED AS 200 ESCAPES EVERY CHECK BUILT ON THE STATUS CODE.** *The
repository already carries «a readable body is not an answer — the code decides»;
this is its mirror, and the harder half: **the code says 200 and the body is the
refusal.*** *A tool that counted links here would print `0 href` and a session
would read «this board publishes nothing» — a plausible, specific, entirely false
sentence.* **What separated them is the `h1` and the title being ABSENT beside a
200**, which is the same discriminant as printing a page-identity marker next to
any count.

**WHY NO SECOND FETCH, AND WHY NO BROWSER.** *Borne 0 requires fetching twice
before COMPARING two `md5` between hosts — no such comparison is made here, and
the body states its own per-request incident id, so the fingerprint is moving by
construction.* **Borne 2 is the one that decides: an antirobot control is never
defeated, and it is never handed to the plugin's user to defeat either.** So no
route is attempted, by HTTP or by browser.

**AND THE BODY CARRIES OUR OWN IP ADDRESS in its iframe URL. It is not reproduced
here, nor in the issue** — a measurement does not need it, and a card is a public
file of this repository.

## What this card is, and is not

- **Not a verdict that the host is closed.** The rules are OPEN on both forms; what
  refuses is infrastructure, and the challenge is a limit of ROUTE and not a
  statement about the board (§2 sexies). *An indeterminate is a measurement to
  redo, never a renouncement.*
- The issue it carries will be OPEN with that reserve, never `blocked` — the
  reserve is precisely what remains to be lifted.
