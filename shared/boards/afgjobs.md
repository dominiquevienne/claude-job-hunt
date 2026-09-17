# Board measurement — Afgjobs (`www.afgjobs.org`, Afghanistan): «The Fastest Growing Jobs Portal in Afghanistan» per its snippet — on 2026-09-17 the root answers 403 to the declared client AND to a bare `curl` (787 B, the same body, a LiteSpeed «Access to this resource on the server is denied!»), rules open; a refusal rendered to every client, consigned, not a verdict

<!-- verified: 2026-09-17 -->

<!-- hosts: www.afgjobs.org -->
<!-- script: none -->
<!-- countries: AF -->
<!-- content: indeterminate · **the root answers HTTP 403, 787 B, md5 ff715af41f83 identical on two reads under the declared identity and the same code and size under a bare `curl` (13:39 UTC) — a LiteSpeed «403 Forbidden — Access to this resource on the server is denied!» page, static (no challenge, the fingerprint does not move); `_robots.allowed('www.afgjobs.org','/')` → open, certain (the rules file itself is served); nothing of the board was read** · 2026-09-17 -->
<!-- witness: none — nothing was served · 2026-09-17 -->

**Found by the Afghanistan search of #613 (the private boards beside
`jobs.af`, which the country page already carries), measured 2026-09-17
13:38–13:39 UTC by the declared client, the guard on the exact path first,
`bin/fetch-body.py`, two reads.** The method is written on #613: two
searches (the NGO coordination body's portal, which the first Afghan
portal grew from; and the portals the engine returns by name), no composed
host names. *A measurement, not an adapter.*

```
_robots.allowed('www.afgjobs.org', '/')   open, certain — the rules file is served, the pages are not
GET https://www.afgjobs.org/    403, 787 B, md5 ff715af41f83 ×2   (Claude-User)
GET https://www.afgjobs.org/    403, 787 B                        (curl, its own identity — the control)
```

**A 403 rendered to every client is not the identity's** (borne 0): the
server refuses from here whoever asks — a geo-fence or a hosting-level
block, not established which. Not a verdict of closure (§2 sexies); a tab
(not connected on the day) is the next reading, and the issue says what
blocks.
