# Board measurement — Jobs in Guyana (`jobsinguyana.com`, Guyana): «Guyana's number 1 jobs website» by its search snippet — the TLS handshake fails to the declared client and to curl alike on 2026-09-18 (`SSL_ERROR_ZERO_RETURN`), plain HTTP answers 403: nothing of the site was read; indeterminate, a measure to redo; no adapter yet

<!-- verified: 2026-09-18 -->

<!-- hosts: jobsinguyana.com, www.jobsinguyana.com -->
<!-- script: none -->
<!-- countries: GY -->
<!-- content: indeterminate · **TLS failure on two reads by the declared client at 06:54:32 and 06:54:39 UTC (`URLError: [SSL] unknown error (0xa0003e8)`), the same by curl (`LibreSSL SSL_connect: SSL_ERROR_ZERO_RETURN`, exit 35), `www.` the same, and `http://jobsinguyana.com/` answers 403; no body read, no rules read (`_robots.allowed` → open, `certain: False`); the search engine's snippet (Guyana's number 1 jobs website) is the only text known — reported, not measured** · 2026-09-18 -->
<!-- witness: none — nothing was read · 2026-09-18 -->
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
