# Board measurement — NGCareers (`ngcareers.com`): named in the prose of the 2026-09-04 inventory beside Sierra Leone and on the Nigeria page — on 2026-09-20 the host answers 301 to `www.jobberman.com`, Jobberman Nigeria, which `jobberman.py` already covers: an alias, not a board of its own, and nothing Sierra Leonean

<!-- verified: 2026-09-20 -->

<!-- hosts: ngcareers.com -->
<!-- script: none -->
<!-- countries: SL -->
<!-- content: out-of-domain · **`https://ngcareers.com/` answers 301 to `https://www.jobberman.com/` (curl; the declared client followed it on two reads: 200, 609 899 B, md5 a1b12c088146 / d265cde438b8 — a rendered element moves), and the body is Jobberman's Nigerian front («Find the Right Job Vacancies in Nigeria | Jobberman», 17 mentions of Nigeria, none of Sierra Leone); the name resolves on 1.1.1.1 and 8.8.8.8 (104.18.33.102, NOERROR); `_robots.allowed('ngcareers.com','/')` → open, `certain: False` (its rules path answers a page, not a rules file)** · 2026-09-20 -->
<!-- witness: none — the host is an alias of a board carded elsewhere · 2026-09-20 -->

**Measured for #764 on 2026-09-20 12:21 UTC by the declared client, the guard on
the exact path first, `bin/fetch-body.py`, two reads.** NGCareers was a
Nigerian board; the domain now redirects to Jobberman (the Ringier One
Africa Media group), whose card `jobberman.md` carries the adapter
`jobberman.py` for Nigeria, Kenya and Uganda. **Out of Sierra Leone's
denominators** (it never was Sierra Leonean — the 2026-09-04 prose named it
beside `jobshq.com.sl` in a ranking, not as a board of the country) and out
of Nigeria's too: an alias adds no board.

```
_robots.allowed('ngcareers.com', '/')   open, certain False
GET https://ngcareers.com/   301 → https://www.jobberman.com/   (curl)
GET https://ngcareers.com/   200 ×2 after the redirect — Jobberman Nigeria's front
```
