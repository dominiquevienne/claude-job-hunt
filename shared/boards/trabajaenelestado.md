# Board adapter — Trabaja en el Estado (`www.trabajaenelestado.cl` · `elastic.serviciocivil.cl`, Chile): the Servicio Civil's public-service calls, read from the index the page queries itself — 349 open calls stated, 349 emitted, the appointed person's name never emitted, the refusing host never fetched

<!-- verified: 2026-09-14 -->

<!-- hosts: elastic.serviciocivil.cl, www.trabajaenelestado.cl -->
<!-- script: trabajaenelestado.py -->
<!-- host-forms: elastic.serviciocivil.cl -->
<!-- host-forms-basis: read — `trabajaenelestado.py:HOST`, a single literal; the page's own `$.ajax` names exactly `https://elastic.serviciocivil.cl/listado_teee/_doc/_search` and nothing else · 2026-09-14 -->
<!-- countries: CL -->
<!-- content: measured · **`hits.total` 349 stated by the index for `Estado: postulacion`, 349 emitted over 10 pages of 36 — equal** — read by the declared client through the page's own POST, 00:02 UTC; 28 of the 349 carry no `ID Conv` (the JUNJI feed) and take the index's `_id`, said on the record; 255 of the 349 addresses are on `www.empleospublicos.cl` (`Disallow: /`) and are emitted as data, never fetched — there is no `ad` command; the rules — `elastic.serviciocivil.cl/robots.txt` 404 (an absence, certain, open), `www.trabajaenelestado.cl/robots.txt` an S3 `AccessDenied` (an absence since #283); **`Ganador`, the appointed person's name on finished calls, is never emitted** · 2026-09-14 -->
<!-- witness: the index's own `hits.total` (`track_total_hits: true`), read on the first page of every walk and printed beside the emitted count; a bounded walk says so and is never «short»; the 10 000 window the page itself caps at is named when reached · 2026-09-14 -->

**Chile's public service — the calls of the ministries, the health
services, the municipalities and JUNJI, as `www.trabajaenelestado.cl`
lists them.** Issue #302; `chile-public-sector.md` (2026-09-03) records why
none of five portals had an adapter, and this card is the first to have
one: the page names its data route, and that route has no rule against
us. Measured 2026-09-13 23:59 – 2026-09-14 00:02 UTC by the declared
client, the guard on the exact path first.

## Rules and the route

```
elastic.serviciocivil.cl/robots.txt              404 — an absence of rules, certain, open; no Crawl-delay
www.trabajaenelestado.cl/robots.txt              403, S3 AccessDenied — an absence since #283 (certain: False)
GET  https://www.trabajaenelestado.cl/           200, 40 102 B — a jQuery page; doSearch() builds the query below
POST https://elastic.serviciocivil.cl/listado_teee/_doc/_search   {"from":0,"size":36,"track_total_hits":true,"sort":[{"Datesum":"asc"},{"ID Conv.keyword":"asc"}],"query":{"bool":{"must":[{"term":{"Estado":"postulacion"}}]}}}
                                                 200 — hits.total 349, 36 hits, took 2 ms
```

**The page is the client, and the adapter sends what the page sends** —
the same index, the same `term` filters its buttons post (`Estado`,
`Codigo Region`), its own page size of 36 — **with two differences said
out loud**: the page's sort is a Painless `_script` (a score multiplier
per state), and this adapter sorts by the plain field `Datesum` then the
id, because a client does not send scripts to someone else's cluster;
and `track_total_hits: true`, so the total is exact rather than capped.
Elasticsearch's `from + size` window is 10 000, which the page itself caps
at — the adapter stops there and names it. No Crawl-delay; 2 s is the
adapter's own.

## The record

```
{"ID Conv": "139384", "Cargo": "Técnico en Enfermería para Unidad de Cardiología Intervencional", "Institucion/Entidad": "Servicio de Salud Metropolitano Oriente / Instituto Nacional del Tórax",
 "Ministerio": "Ministerio de Salud", "Region": "Región Metropolitana de Santiago", "Codigo Region": "region13", "Ciudad": "Providencia", "Area de Trabajo": "Salud", "Cargo Profesional": "Técnicos",
 "Tipo Convocatoria": "EEPP", "Tipo Postulacion": "Postulacion en linea", "Fecha inicio Convocatoria": "27/05/2026 0:00:00", "Fecha cierre Convocatoria": "03/06/2026 23:59:00", "Estado": "postulacion",
 "URL": "https://www.empleospublicos.cl/pub/convocatorias/convpostularavisoTrabajo.aspx?i=139384&c=0&j=0&tipo=convpostularavisoTrabajo", "Ganador": ""}
```

The record is the listing: title, employer (the State's own service),
ministry, region and code, city, area, professional category, call type,
application type, opening and closing (as stored, `DD/MM/YYYY H:MM:SS`),
state. **28 of the 349 open calls carry an empty `ID Conv`** — the JUNJI
feed (`Origen: JUNJI`, addresses on `junji.myfront.cl`) — and take the
index's own `_id`, with `id_is_index_id` true; without that the walk was
28 short. **`Ganador` is the appointed person's name on finished calls —
personal data — and is never emitted.** Ministerio de Salud carried 178
of the 349 on the day. `--estado` takes the site's three states or
`todos`; `--region` the site's own code (`region13` is the Metropolitana).

**There is no `ad` command.** 255 of the 349 addresses are on
`www.empleospublicos.cl`, whose operator publishes `User-agent: * /
Disallow: /` — the address is emitted as the record's own field (a user
may open it), `url_not_fetched` says why on each such record, and the
adapter never reads it: reading the operator's pages through an index
host that merely has no rules file would be choosing the host that says
yes (`chile-public-sector.md`). The 94 others (JUNJI, and the special
calls) are not fetched either — the listing is the record.

```
trabajaenelestado.py list
[trabajaenelestado] 349 emitted over 10 page(s), index states 349 (Estado postulacion) — equal.
[trabajaenelestado] 255 of the 349 addresses are on www.empleospublicos.cl, which says no in writing — every address is emitted as data and none is fetched; there is no `ad` command.
```

## Configuration

```yaml
boards:
  trabajaenelestado:
    enabled: true
    estado: postulacion     # the page's default — open calls; evaluacion · finalizadas · todos
    region: region13        # optional — the site's own code
```

| Key | Required | Notes |
| :-- | :-- | :-- |
| `enabled` | yes | False or absent → not scanned |
| `estado` | no | `postulacion` by default |
| `region` | no | `region01` … `region16`, as the page's select codes them |

No credentials, no browser, no login. `list` is one request a page at 2 s
(10 on the day for the whole open list).

## What is not established

- **Whether `postulacion` means open today** — the first record in
  `Datesum` order closed on 03/06/2026 and still carries the state; the
  state is the site's, emitted as stated, not judged.
- **The `X-API-KEY: cambia-este-token` header** the sister page
  (`empleospublicos.cl`) hardcodes — not sent, not needed: this index
  answered the page's own shape without any header.
- **The Painless sort's effect on order** — the adapter's plain sort gives
  every record once, in date order; the page's ranking (open first) is a
  presentation the user can redo on `status`.
- **The `evaluacion` and `finalizadas` totals** — only a two-record sample
  of `finalizadas` was read on the day.

## 2026-09-14 — shipped

`list`: 349 of 349 (after the `_id` fallback — the first run was 28
short, and the shortfall was the 28 empty ids); `list --estado
finalizadas --pages 1 --limit 2`. Three tests; six mutations on a
detached worktree (`python3 -B`), six red — the script sort restored, the
`_id` fallback dropped, `Ganador` emitted, the total read as the hit
count, the window stop dropped, the refusing-host note dropped.
