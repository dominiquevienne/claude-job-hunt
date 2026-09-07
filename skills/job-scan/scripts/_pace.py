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

import os
import re
import tempfile
import time

import _robots


# **The slot file, and why it is not in the workspace.** Spacing is a fact
# about this machine's traffic, not about the user's job search: it belongs in
# the temp directory, which is writable everywhere and disposable. *Writing to
# a configuration directory because a tool ran is a side effect, and #142
# settled that.*
_SLOTS = os.path.join(tempfile.gettempdir(), "claude-job-hunt-pace")

# A claim further ahead than this is not a claim, it is a clock that moved or a
# process that died holding one. **Ignoring it is safer than honouring it**:
# the worst case is one request too early, against a wait of unbounded length.
_MAX_CLAIM = 300.0


def _slot_path(host):
    """One file per host. **Never one file for everything.**

    Two different hosts must not slow each other down — a global pace would
    turn one slow site into a tax on every other, and that is not what any of
    them asked for.
    """
    safe = re.sub(r"[^a-z0-9._-]", "_", (host or "").lower())[:80] or "_"
    return os.path.join(_SLOTS, safe)


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

    def _claim(self):
        """Reserve this host's next slot **across processes**, and return it.

        `self._last` lives in one process's memory, and `None` on the first
        call means *fire now*. **So every new process fired immediately**,
        whatever another had just done: on 2026-09-07 nine requests from
        `bin/fetch-body.py` and twenty-three from a sweep reached
        `emploisburkina.bf` in ninety seconds, each impeccably paced in its
        own process, and the host stopped answering. **Twenty-two of
        twenty-three failed, and a zero drawn from that would have been
        indistinguishable from an empty board.** #179.

        Each caller writes the slot it has taken *before* sleeping, so a
        second process reads a claim rather than an empty file. The
        read-modify-write is not locked — the window is microseconds against a
        wait of seconds, and `os.replace` is atomic on both platforms this
        repository runs on. *A lock would need `fcntl` on one and `msvcrt` on
        the other, and this does not need one.*
        """
        path = _slot_path(self.host)
        now = time.time()
        try:
            with open(path, encoding="utf-8") as fh:
                claimed = float(fh.read().strip() or 0.0)
        except (OSError, ValueError):
            claimed = 0.0
        if claimed > now + _MAX_CLAIM:
            claimed = 0.0
        target = max(now, claimed)
        try:
            os.makedirs(_SLOTS, exist_ok=True)
            tmp = f"{path}.{os.getpid()}"
            with open(tmp, "w", encoding="utf-8") as fh:
                fh.write(repr(target + self.delay))
            os.replace(tmp, path)
        except OSError:
            # **A temp directory we cannot write is not a licence to hurry.**
            # The in-process spacing below still applies; only the
            # cross-process half is lost, and it is lost quietly rather than
            # turning into no spacing at all.
            pass
        return target

    def wait(self):
        """Sleep for whatever of this host's interval has not already passed —
        **counting requests made by other processes.**"""
        if not self.delay:
            self._last = time.monotonic()
            return 0.0
        target = self._claim()
        slept = max(0.0, target - time.time())
        # The in-process view still applies: it is cheaper than a file read and
        # it is what the existing cases exercise.
        if self._last is not None:
            slept = max(slept, self.delay - (time.monotonic() - self._last))
        slept = max(0.0, slept)
        if slept:
            time.sleep(slept)
        self._last = time.monotonic()
        return slept
