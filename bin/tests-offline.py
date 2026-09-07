#!/usr/bin/env python3
"""Run the suite with **outbound** connections blocked. — #170

    bin/tests-offline.py

A test that reaches a host is a test whose result depends on that host: it
fails on an isolated runner, and it passes or fails elsewhere for reasons the
report does not carry. This says whether any of ours does.

WHY THE FIRST VERSION OF THIS ANSWERED WRONG

Blocking *every* socket reported two tests as reaching the network. They stand
up an `http.server` on `127.0.0.1` and talk to themselves — **loopback is not
the network**: no external host, no DNS, and it works on an isolated runner,
which is the whole question.

So the block is on **outbound** connections and on resolving anything but
`localhost`. *A detector too broad reports a defect that is not there, and it
reads exactly like a detector that works.* This one is exercised in both
directions before it is believed: an external name must be refused, a loopback
address must be allowed.

WHERE IT CAME FROM

Two `core` runs failed on 2026-09-06, on a contributor's branch since deleted,
with the logs expired. Our suite passes on that branch's head, its shell
scripts carry no CR and parse, and every file compiles under 3.9 — so the cause
was environmental and is no longer recoverable. **The useful residue was
asking whether our own suite could fail that way.** It cannot: 436 tests, no
outbound connection.
"""

import io
import socket
import sys
import unittest

LOCAL = {"127.0.0.1", "::1", "localhost"}
# **No guard on `create_connection`.** It is built on `socket.connect`, so the
# block below already covers it — and a redundant guard is one that cannot be
# tested in isolation: removing it changed nothing, because the probe was
# stopped one layer down. *A guard that cannot fail on its own is not defence
# in depth, it is a line nobody can check.*
_conn, _gai = socket.socket.connect, socket.getaddrinfo


class Outbound(RuntimeError):
    """A test tried to leave the machine."""


def _host(addr):
    return addr[0] if isinstance(addr, tuple) and addr else None


def _block():
    def connect(self, addr, *a, **k):
        if _host(addr) not in LOCAL:
            raise Outbound(f"connect to {_host(addr)}")
        return _conn(self, addr, *a, **k)

    def getaddrinfo(host, *a, **k):
        if host not in LOCAL:
            raise Outbound(f"resolve {host}")
        return _gai(host, *a, **k)

    socket.socket.connect = connect
    socket.getaddrinfo = getaddrinfo


def _self_check():
    """**Each block exercised on its own, in both directions.**

    Checking only `getaddrinfo` left two of the three blocks untested: removing
    the `connect` guard changed nothing observable, because the suite never
    reaches out anyway and the remaining resolver block still answered the one
    question asked. *A detector whose parts are not individually exercised
    reports the health of the part that is.*
    """
    # **An address, not a name, for the two connect paths.** Probing them with
    # a hostname sends the call through `getaddrinfo` first, which is already
    # blocked — so both passed *for the wrong reason* and removing either
    # guard changed nothing. `192.0.2.1` is TEST-NET-1 and resolves nowhere.
    for name, call, host in (
            ("getaddrinfo", lambda h: socket.getaddrinfo(h, 80),
             "example.invalid"),
            ("create_connection (via connect)",
             lambda h: socket.create_connection((h, 9), timeout=1),
             "192.0.2.1"),
            ("socket.connect",
             lambda h: socket.socket().connect((h, 9)), "192.0.2.1")):
        try:
            call(host)
            return f"{name} let an external host through"
        except Outbound:
            pass
        except Exception:                                   # noqa: BLE001
            return f"{name} failed for a reason other than the block"
    try:
        socket.getaddrinfo("127.0.0.1", 80)
    except Outbound:
        return ("the block refuses loopback, so every local server would be "
                "reported as a network call")
    return None


def main():
    # **One thing this cannot check about itself.** Removing the call below
    # makes the self-check silent, and no self-check catches its own absence.
    # A guard asserts it from outside, in `tests/test_core.py`; here the
    # limit is written where someone editing this line will read it.
    _block()
    wrong = _self_check()
    if wrong:
        print(f"ERROR: the detector is not sound — {wrong}", file=sys.stderr)
        return 2
    sys.path.insert(0, "tests")
    buf = io.StringIO()
    result = unittest.TextTestRunner(stream=buf, verbosity=0).run(
        unittest.TestLoader().discover("tests"))
    bad = [(t, tb) for t, tb in result.failures + result.errors
           if "Outbound" in tb]
    print(f"[offline] {result.testsRun} tests, {len(result.failures)} "
          f"failure(s), {len(result.errors)} error(s), "
          f"{len(bad)} reaching outward", file=sys.stderr)
    for t, _tb in bad:
        print(f"    {t.id()}", file=sys.stderr)
    if bad:
        print("A test that reaches a host depends on that host: it fails on an "
              "isolated runner and passes elsewhere for reasons no report "
              "carries.", file=sys.stderr)
        return 1
    return 0 if not (result.failures or result.errors) else 3


if __name__ == "__main__":
    sys.exit(main())
