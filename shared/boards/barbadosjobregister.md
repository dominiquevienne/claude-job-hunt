# Board measurement — Barbados Job Register (`www.barbadosjobregister.gov.bb`, Barbados): «Request is Blocked by Firewall» to the declared client and to a real browser alike

<!-- verified: 2026-09-14 -->

<!-- hosts: www.barbadosjobregister.gov.bb, barbadosjobregister.gov.bb -->
<!-- script: none -->
<!-- countries: BB -->
<!-- content: measured · **403 «Request is Blocked by Firewall», 30 bytes, to a real browser as well** — the tab on `/` and `fetch('/')` from it, 16:26 UTC, the same body the declared client got (15:29 UTC, twice); a refusal rendered to everyone from here is not a client filter (borne 0) — whether it is a geography filter is not established; nothing of the register was read · 2026-09-13 -->
<!-- witness: none — nothing served to any client from this machine; the 30-byte firewall page is the only body, from the declared client and from a browser tab · 2026-09-13 -->
<!-- route: none · non faisable — validé par le propriétaire le 14.09.2026 (verbatim : « 1, 2, 3, 4, 5 => exclue ») — measured: the firewall refuses everyone from here — «Request is Blocked by Firewall» to the declared client and to a real browser on 2026-09-13 and 2026-09-14, the apex a certificate error · 2026-09-14 -->
**The register the Ministry of Labour's site points to as its «Online Job
Centre» (`labour-gov-bb.md`), and the only board of its country in this
repository.** *A measurement and not an adapter, and a short one, because
the guard closed the question at the rules file.* Measured 2026-09-13
10:38 UTC with the declared client.

## Two host forms, two verdicts, neither an open path

```
GET https://www.barbadosjobregister.gov.bb/robots.txt   403 · x-cache: CONFIG_NOCACHE · 10:38:24 UTC   (bin/fetch-body.py, twice, 3 s apart — the same)
_robots.allowed('www.barbadosjobregister.gov.bb', '/')  allowed False · certain True · rule "/" · rule_kind host-closed
_robots.allowed('barbadosjobregister.gov.bb', '/')      allowed None — «[SSL: CERTIFICATE_VERIFY_FAILED]»: INDETERMINATE, and an INDETERMINATE is not probed
```

**A `403` on the rules file is a refusal, and the doctrine keeps it one**
(the 2026-09-09 table reopened `401` alone); **a certificate that does not
verify is a non-answer**, not a door (`robots-policy.md`, «a non-answer is
not a refusal»). Between the two forms there is no path the rules open,
so the browser branch — which starts from «the rules open, the transport
refuses» — has nothing to start from. *Nothing beyond the rules file was
requested; no tab was opened.* Same shape as `kazibongo.md` the day
before, on a government host.

## What reopens it

- `www.…/robots.txt` answering anything but 403 — then the rules are
  read and the ordinary order applies;
- the apex presenting a certificate that verifies (or the TLS failure
  being isolated to this resolver/machine — a second machine's read would
  say);
- a doctrine decision on a 403 *at the rules file* — a question the card
  poses and does not decide.

## What this card does not say

Nothing about what the register serves — size, fields, whether a browser
is served — **because a browser was not opened**. *The country's page on
the Atlas keeps its ministry as «not a board» and its register as «rules
refused, dated».*

## 2026-09-13 — #283: an unread rules file is an absence of rules, and the transport measured

**Owner's decision of 2026-09-13, verbatim: «toutes incapacité d'ouvrir robots.txt
doit aboutir à l'absence de règles et donc à l'ouverture».** This card read
«route: none — 403 ×2 on the rules file + TLS on the apex (13.09)» — a verdict taken on the rules file alone. Since #283 the 403 on
`/robots.txt` is `no-rules-403`, `allowed: True, certain: False`: nothing
was read, nothing forbids, and **the transport decides**. Measured with
`bin/fetch-body.py --allow-refusal` under the new guard, the root (and a
listing path where one was known) twice:

```
GET https://www.barbadosjobregister.gov.bb/              403, 30 B, md5 c463f0baa3f3   (15:29:24Z)
GET https://www.barbadosjobregister.gov.bb/              403, 30 B, md5 c463f0baa3f3   (15:29:26Z)
```

**The transport answers a **static 403** — the same bytes on every fetch: a refusal at the transport aimed at the client, family (1) of #222, where a browser is legitimate and is not measured here.** *A verdict of closure was never
this card's to give (§2 sexies); what it gives now is a dated transport
reading, and the class it falls in.*

## 2026-09-13 16:26 UTC — the browser route, MEASURED (#222): the firewall page to the tab as well

```
tab: https://www.barbadosjobregister.gov.bb/     403, «Request is Blocked by Firewall», 30 B — the page itself
tab: fetch('/')                                  403, 30 B, the same sentence
```

**The same thirty bytes to a browser and to the declared client.** A
refusal rendered to everyone from this machine is not a client filter
(borne 0). *What it may be is a geography filter — a government register
served to its island — and that is not measured from Switzerland; a reader
inside Barbados is the only route this card leaves untested.* Nothing of
the register was read.

## 2026-09-14 09:50 UTC — the same answer a day later, from a connected tab

`www.barbadosjobregister.gov.bb/` and `/jobs`: «Request is Blocked by
Firewall», the only text on the page, twice; the apex
`barbadosjobregister.gov.bb/`: the browser's own certificate error page
(«Erreur liée à la confidentialité»), never clicked through. Two readings
a day apart, the client and a real browser alike — the firewall refuses
everyone from here (borne 0 of the 2026-09-07 doctrine: a 403 rendered to
all is the operator's refusal, not an infrastructure that does not know
us). `route: none` stands; the word «closed» is the owner's (§2 sexies),
and #305 waits for it — or for a reader inside Barbados.

## 2026-09-14 11:0x UTC — non faisable, validé par le propriétaire

**non faisable — validé par le propriétaire le 14.09.2026 (verbatim : « 1, 2, 3, 4, 5 => exclue »)** — relayed verbatim by the pilot (#305). What was measured above is the measurement; the word «closed» is the owner's, and he has given it: the firewall refuses everyone from here — «Request is Blocked by Firewall» to the declared client and to a real browser on 2026-09-13 and 2026-09-14, the apex a certificate error. The card stays as the record of the measurements; `route: none` is dated and motivated by this line, and the Atlas excludes the entry from the feasible denominator (#404). What would reopen it is written in the sections above; nothing is scheduled.

