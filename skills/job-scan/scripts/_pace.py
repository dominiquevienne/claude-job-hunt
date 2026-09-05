#!/usr/bin/env python3
"""The rate a host asks for, applied between requests. — #161

    from _pace import Pace
    pace = Pace("careers.icims.com", own=0.0)
    ...
    pace.wait()          # before each request after the first
    code, body = fetch(url)

WHY THIS EXISTS

`Crawl-delay` was dropped by the rules parser until 2026-09-05, so **no adapter
in this repository had ever applied one**. Measured that day:

    76 adapters touch the network
    65 of 71 whose fetch wrapper could be identified make several requests
       to the same host — 92 %, not the exception
    33 have no spacing of any kind
     0 read the host's delay

And the concrete case is a host on our own cards:

    careers.icims.com/robots.txt   84 bytes, md5 2a0e78d4b005, 12:14:48Z
        User-agent: *
        Allow: /
        crawl-delay: 5

    icims.py   3 requests per run, no spacing at all

**The host asks for five seconds and we give none.**

THE DELAY COMES FROM THE HOST, NEVER FROM A NUMBER WE PICKED

`Pace(host)` reads `_robots.verdict(host)["crawl_delay"]`. **When the host sets
none, this waits `own` — the adapter's own existing spacing — and nothing
else.** It does not invent a second, or a half: *a default of one second is a
choice, not a measurement*, and dressing a choice as a host's request is the
species this repository keeps catching.

Where both exist, the **longer** wins. An adapter that already sleeps 2s on a
host asking 5s waits 5; one that sleeps 2s on a host asking nothing keeps its 2.
Neither is weakened by the other.

PACING AND BACK-OFF STAY TWO THINGS

They had to be separated even to count — 47 adapters carrying `time.sleep`
turned out to be 43 spacing plus 4 backing off from 429/503. **This module does
pacing only.** A retry after a refusal answers a different question, is driven
by the response rather than the rules, and belongs where it already is.
"""

import time

import _robots


class Pace:
    """Spacing between requests to one host.

    `own` is whatever fixed spacing the adapter already applied, in seconds —
    passing it keeps that behaviour intact where the host asks for less, or for
    nothing at all.
    """

    def __init__(self, host, own=0.0):
        self.host = host
        self.own = max(0.0, float(own or 0.0))
        try:
            declared = (_robots.verdict(host) or {}).get("crawl_delay")
        except Exception:                                  # noqa: BLE001
            # **An unreadable rules file is not a permission to hurry.** The
            # guard reports that separately; here it means we fall back to
            # whatever the adapter already did, never to zero.
            declared = None
        self.declared = float(declared) if declared else None
        self.delay = max(self.own, self.declared or 0.0)
        self._last = None

    def source(self):
        if self.declared and self.declared >= self.own:
            return f"{self.delay:g}s, asked for by {self.host}"
        if self.delay:
            return (f"{self.delay:g}s, this adapter's own spacing — "
                    f"{self.host} asks for nothing")
        return f"no spacing: {self.host} asks for none and this adapter set none"

    def wait(self):
        """Sleep only for the part of the interval that has not already passed."""
        if not self.delay:
            self._last = time.monotonic()
            return 0.0
        now = time.monotonic()
        if self._last is None:
            self._last = now
            return 0.0
        slept = max(0.0, self.delay - (now - self._last))
        if slept:
            time.sleep(slept)
        self._last = time.monotonic()
        return slept
