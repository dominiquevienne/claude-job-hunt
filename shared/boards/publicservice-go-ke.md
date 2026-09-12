# Board measurement — Public Service Commission (Kenya): the rules could not be read — three timeouts — so nothing was asked, and nothing is concluded

<!-- verified: 2026-09-12 -->

<!-- hosts: www.publicservice.go.ke, publicservice.go.ke -->
<!-- script: none -->
<!-- countries: KE -->
<!-- content: indeterminate · 1 host, `robots.txt` unread — «could not be read after 3 attempt(s): urlopen error timed out», on two reads five minutes apart (12:16 and 12:22 UTC); `verdict()` answers `sweep: None`, `identity()` `state: unknown`, `allowed("/")` `None` — and an INDETERMINATE is not probed: 0 requests for content · 2026-09-12 12:22 UTC -->
<!-- witness: none — nothing was asked of the host beyond its rules file, which did not answer -->

**Measured 2026-09-12 at 12:16:50Z UTC for #233, lot 6 — and the
measurement stops at the rules.** `_robots.verdict()` tried the rules file
three times and got a timeout each time, on two separate reads; the
`fetch-body.py` call for the root exited on `INDETERMINATE` without sending
anything. **A host that closes everything to us and a host that is slow to
answer look the same from here — and the doctrine says the difference is
not ours to guess.**

## The rules — unread

```
robots.txt      TIMEOUT ×3 (read 1, 12:16Z) · TIMEOUT ×3 (read 2, 12:22Z)
verdict()       sweep None — «This is an unknown, not a permission and not a refusal»
identity("/")   state unknown, token None
allowed("/")    None
fetch-body.py   INDETERMINATE, exit 8 — no request for content left this machine
```

*#233 listed this host under «another managed block naming ClaudeBot» from
a read on 2026-09-11; today the file did not answer at all. Both are
readings, each dated.*

## What this card is, and is not

- **Not a verdict** — neither open nor closed nor refused: *a measurement to
  redo* (`§2 sexies`: an INDETERMINATE is never a renunciation). A second
  resolver was not tried: the failure is a timeout on the HTTP read, not a
  DNS answer.
- **The object**: Kenya's Public Service Commission publishes its vacancies
  on this host (the page named it as the country's board); whether the site
  is slow, geo-fenced, or down this hour is exactly what the next read will
  say.
- **No script, no configuration.**
