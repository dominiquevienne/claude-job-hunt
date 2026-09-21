# Board measurement — Jobs in Guyana (`jobsinguyana.com`, Guyana): «Guyana's number 1 jobs website» by its search snippet — the TLS handshake fails to the declared client and to curl alike on 2026-09-18 (`SSL_ERROR_ZERO_RETURN`), plain HTTP answers 403: nothing of the site was read; indeterminate, a measure to redo; no adapter yet

<!-- verified: 2026-09-21 -->

<!-- hosts: jobsinguyana.com, www.jobsinguyana.com -->
<!-- script: none -->
<!-- countries: GY -->
<!-- content: indeterminate · **TLS failure on two reads by the declared client at 06:54:32 and 06:54:39 UTC (`URLError: [SSL] unknown error (0xa0003e8)`), the same by curl (`LibreSSL SSL_connect: SSL_ERROR_ZERO_RETURN`, exit 35), `www.` the same, and `http://jobsinguyana.com/` answers 403; no body read, no rules read (`_robots.allowed` → open, `certain: False`); the search engine's snippet (Guyana's number 1 jobs website) is the only text known — reported, not measured** — **second control 2026-09-21, 06:14–06:15 UTC: the same TLS failure on two reads (`URLError: [SSL] unknown error (0xa0003e8)`); the name resolves on 1.1.1.1 and 8.8.8.8 (two Cloudflare addresses, NOERROR, 06:37 UTC) — the endpoint answers and closes; nothing read** · 2026-09-21 -->
<!-- witness: none — nothing was read · 2026-09-18 -->
<!-- route: none · non faisable — décision du propriétaire du 18.09.2026 (un hôte muet reçoit un ticket adapter+blocked qui dit pourquoi et ce qui lèverait), #745 · 2026-09-19 -->
**Found by the Guyana search of #621 (a country never searched), measured
2026-09-18 06:54–06:56 UTC by the declared client, the guard on the exact path
first, `bin/fetch-body.py`, two reads.** The method is written on #621:
three searches naming the public sources and the private boards, no
composed host names. *A measurement, not an adapter.*

```
_robots.allowed('jobsinguyana.com', '/')   open, certain False (the rules file did not answer)
GET https://jobsinguyana.com/      TLS: SSL_ERROR_ZERO_RETURN ×2 (client), ×1 (curl 8, LibreSSL)
GET https://www.jobsinguyana.com/  TLS: the same
GET http://jobsinguyana.com/       403
```

**A transport failure is neither a refusal nor a permission.** The host's TLS endpoint closes the connection during the handshake, to every client tried; whether a board lives behind it is unknown today. Not «closed»: a control read is due — the next control is 2026-09-21 (a deferred task of the session that measured), and a browser read counts as a control (a browser negotiates other cipher suites than LibreSSL).

## The control three days on — the same handshake failure

```
dig @1.1.1.1 / @8.8.8.8 jobsinguyana.com   NOERROR — 104.21.75.146, 172.67.177.224 (Cloudflare), 06:37 UTC
GET https://jobsinguyana.com/              URLError: [SSL] unknown error (0xa0003e8) ×2 by the declared client (06:14–06:15 UTC)
```

**The name lives, the TLS endpoint still closes the handshake to our
client.** The browser control (other cipher suites) remains the one that
could distinguish «TLS broken for everyone» from «TLS broken for this
client» — not done in this control. Not «closed»: #745 stays `blocked` with
this date; next control 2026-09-28.
