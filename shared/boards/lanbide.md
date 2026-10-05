# Board measurement — Lanbide (`www.lanbide.euskadi.eus`, Spain/Basque Country): the Basque public employment service — **the information site answers instantly and the OFFERS live on another host, `apps.lanbide.euskadi.net`, whose TCP 443 does not answer at all**: it resolves identically on two resolvers, sits in the SAME /24 as the site that connects in 0,0 s, and times out at 8 s. The 928 `Disallow` rules read are the information site's, not the offers'. **No route to the offers from here on 2026-10-05; nothing about the board itself is concluded.**

<!-- verified: 2026-10-05 -->

<!-- hosts: www.lanbide.euskadi.eus, apps.lanbide.euskadi.net -->
<!-- script: none -->
<!-- countries: ES -->
<!-- host-forms-basis: read — `lanbide.euskadi.eus` and `www.lanbide.euskadi.eus` serve the SAME 31 692 B rules file (`state: read`, `certain: True`); the offers host `apps.lanbide.euskadi.net` serves NONE (`state: no-rules`, `certain: False`, rules file timed out after 3 attempts); `lanbide.euskadi.net` is NXDOMAIN on this resolver and `euskadi.net` fails TLS hostname verification — four forms, four different answers · 2026-10-05 -->
<!-- content: measured · **the offers are on a DIFFERENT HOST AND A DIFFERENT TLD, and that host does not answer: `apps.lanbide.euskadi.net` resolves to `185.161.116.6` IDENTICALLY on 1.1.1.1 and 8.8.8.8, and TCP 443 times out after 8 s — while `www.lanbide.euskadi.eus` resolves to `185.161.116.22`, the SAME /24, and connects in 0,0 s. So it is not this connection: a neighbouring address in the same range answers instantly. The route was found by reading the declared sitemap: `/sitemap.xml` (328 B) is an index of two language sitemaps, and `sitemap_es_superior.xml` (6 717 B, 30 `<loc>`) names FIVE URLs on `apps.lanbide.euskadi.net`, of which the offer search `OF_BUSQUEDA_OFERTAS?LG=C&ML=OFEMEN1` — an Oracle mod_plsql application (`PACKAGE.PROCEDURE` naming, e.g. `ALTA_LANBIDE.GE_ALTA_LANBIDE_INI`). WHAT THE RULES DO AND DO NOT COVER: the information site's `robots.txt` is 31 692 B with **928 `Disallow` rules and zero `Allow`**, and NOT ONE of the 928 matches an offer or employment keyword in Spanish, Basque or English — but they are the rules of the `.eus` host and they do not govern the `.net` one. AND THE RATE, on the only host that answers: the information site's 31 692 B of rules declare NO `Crawl-delay`, so the 2 s of our own pace are the ones that apply; the offers host declares nothing at all, its rules file having timed out. METHOD: guard taken on each host form separately; `fetch-body.py` waited 10 s before its first request because the rules file had timed out (a delay, not a refusal, #283), and the application timed out too** · 2026-10-05 -->

<!-- witness: none — no listing was reached, so there is nothing to count and no count is claimed · 2026-10-05 -->

## Measured 2026-10-05 — 928 rules read, and they govern the wrong host

```
www.lanbide.euskadi.eus   robots.txt 31 692 o   read, certain, 928 Disallow, 0 Allow
                                                aucune des 928 ne vise une offre
                          /sitemap.xml   328 o  index -> es_superior + eu_superior
                          es_superior  6 717 o  30 <loc>, dont 5 sur euskadi.NET
apps.lanbide.euskadi.net  robots.txt            TIMEOUT x3  -> no-rules, certain FALSE
                          DNS 1.1.1.1           185.161.116.6
                          DNS 8.8.8.8           185.161.116.6     (identique)
                          TCP 443               TIMEOUT a 8 s
www.lanbide.euskadi.eus   DNS                   185.161.116.22    (MEME /24)
                          TCP 443               OK en 0,0 s
```

**Found by the Spain pass of #949.** The country page carried this host as «&nbsp;à construire&nbsp;»
with «&nbsp;Service public de l'emploi du Pays basque… Site public, joignable. **Structure non
examinée.**&nbsp;» *Joignable is true of the information site and false of the offers.*

### `robots.txt` binds a HOST, not a brand — and here it cost 928 rules of reading

**The information site publishes 31 692 bytes of rules: 928 `Disallow`, no `Allow`.** *Not one of
the 928 matches `ofert`, `empl`, `enplegu`, `eskaint`, `lan_` or `job`*, so nothing in them refuses
the offers. **But they are not the rules that apply to the offers**, because the offers are not on
that host: the declared sitemap names them on **`apps.lanbide.euskadi.net`** — a different
subdomain *and a different top-level domain*.

> *This is Bast.af (#643) again, and the same way round: there `www.bast.af` refused `/api/` in
> writing while the data lived on `db.bast.af`, which published no rules at all.* **Here the 928
> rules say nothing about offers, and reading them as the verdict would have been just as wrong —
> the question they answer is about the other host.**

### And the offers host does not answer, which is a fact about transport and not about rules

**It resolves — identically on two public resolvers — and TCP 443 times out at 8 s.** *The
discriminant that makes this the host's and not ours:* **`www.lanbide.euskadi.eus` is
`185.161.116.22`, the SAME /24, and it connects in 0,0 s.** A neighbouring address in the Basque
government's own range answers instantly, so this connection is not the cause.

*`fetch-body.py` waited 10 s of its own accord before the first request, because the rules file had
timed out — the delay that #283 prescribes for a 429 or a timeout on the rules file, which is a
delay and never a refusal.* **The application timed out all the same.**

**A timeout is INDETERMINATE and is not read as a refusal.** *Nothing here says the host refuses
us; it says that from this connection, on this date, nothing was served.* **What is dated is the
reading, not the host.**

### Four host forms, four different answers — and that is the record worth keeping

| form | what it answers |
| :-- | :-- |
| `lanbide.euskadi.eus` · `www.lanbide.euskadi.eus` | the SAME 31 692 B rules file, `read`, `certain: True` |
| **`apps.lanbide.euskadi.net`** | **rules file TIMES OUT** → `no-rules`, `certain: False` |
| `lanbide.euskadi.net` | **NXDOMAIN** on this resolver |
| `euskadi.net` | **TLS hostname mismatch** — the certificate is not valid for that name |

**And the rate: the information site writes no `Crawl-delay` in its 31 692 bytes, so the 2 s of our own courtesy are what apply** — the offers host writes nothing at all, its rules file never having arrived.

*Three of the four fail, and each fails for a different reason.* **Under #283 all three absences
read as an open door with `certain: False`** — the owner's decision — *and none of them is a
refusal.*

### What this card does NOT say

**It does not say the board is closed, nor that the offers do not exist.** *The information site is
healthy, the sitemap is well-formed, and the offer application is named in it.* **What is
established is narrow and dated: from here, on 2026-10-05, `apps.lanbide.euskadi.net:443` did not
complete a connection.**

*The owner's decision of 2026-09-18 covers this shape — «&nbsp;si ces hôtes ne répondent pas… les
conserver comme "blocked" en tant que ticket et mentionné pourquoi&nbsp;» — and its express
validation is acquired for a host whose transport does not complete.* **So the issue carries
`blocked` with the measurement and a dated control, and the reason is named rather than implied.**
*What would lift it is one command: a TCP connect to 443 that completes.*

### And it refutes a prediction I had written myself

*Writing `feinaactiva.md` I noted that the regional services might share a shape and that this was
**to verify, not assume**.* **Verified, and they do not.** *Feina Activa is an Angular SPA whose
offers are behind an account wall with 138 endpoints and no public search; Lanbide's offers are an
Oracle mod_plsql application on a separate host that does not answer at all.* **Two regional
services, two unrelated obstacles — so the third (Emprego Xunta) is not predicted either.**

**Measured 2026-10-05 by the declared client, the guard taken on EACH host form separately,
`bin/fetch-body.py`, DNS on two public resolvers, TCP connect timed.** *A measurement, not an
adapter.*

```
_robots.verdict('www.lanbide.euskadi.eus')    state: read,     certain: True,  31 692 B, 928 Disallow
_robots.verdict('apps.lanbide.euskadi.net')   state: no-rules, certain: False, timeout x3
GET /sitemap.xml · /sitemaps/sitemap_es_superior.xml            200
GET apps…/apps/OF_BUSQUEDA_OFERTAS?LG=C&ML=OFEMEN1              URLError: timed out
dig @1.1.1.1 / @8.8.8.8  apps.lanbide.euskadi.net  ->  185.161.116.6  (identique)
TCP 185.161.116.6:443  timeout 8 s   ·   TCP 185.161.116.22:443  ok 0,0 s
```
