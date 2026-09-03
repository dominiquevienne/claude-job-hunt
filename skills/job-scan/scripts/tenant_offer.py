#!/usr/bin/env python3
"""An ad points at an ATS the user already sweeps — under a tenant they never
configured. Read it off the URL and offer it.

**Issue #83.** A HiringCafe card carried

    apply_url = https://jobs.smartrecruiters.com/Evooq/744000146883069-…

`smartrecruiters` was **already enabled** in that config, with three tenants.
`Evooq` was not one of them. The provider is in the host, the tenant is the
first path segment, **and nothing read either** — the deduction was made by
hand and the line typed into the config.

A second case the same day, on a different board and a different provider:
SICPA on jobup, `jobs.sicpa.com`, a SuccessFactors tenant, while
`successfactors` was enabled for another host entirely.

WHY READING IT BEATS GUESSING IT. `shared/boards/smartrecruiters.md` records
that **a wrong tenant answers 200 with zero ads**. So a tenant cannot be
guessed and confirmed by probing — the only safe way to add one is **to have
seen it on a real advert**, which is exactly what this produces. The
repository's own warning, turned into the feature.

FOLLOW THE REDIRECTS BEFORE READING THE HOST. jobup publishes SICPA's
`externalUrl` as `sicpa.contactrh.com`, which is **a 302 with a zero-byte body**
to `career012.successfactors.eu` and then to `jobs.sicpa.com`. An
implementation that reads the provider off the URL as published concludes
*"contactrh, unknown provider"* and misses a perfectly identifiable tenant.
`jobs-ch.md` already listed `contactrh.com` among the hosts it sees — without
saying it was a redirector.

WHAT THIS NEVER DOES:

- **It never writes the config.** It prints what it saw and what would be
  added. The file is the user's, and the offer rides in a question already
  being asked — the same constraint as issue #80.
- **It never offers a tenant it has not confirmed.** A provider whose wrong
  tenants answer 200-and-empty makes an unverified offer worse than silence.
- **It never guesses a provider.** A host it does not recognise is reported as
  `unknown` with the host named, not silently dropped: a URL nobody could read
  is a fact worth seeing.

    tenant_offer.py read --url <apply_url> [--no-follow]
    tenant_offer.py scan --urls urls.txt --config ~/…/config.yml
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dormant import read_boards            # noqa: E402  the config parser

from _robots import allowed as robots_allowed
from _ua import UA
DEFAULT_CONFIG = os.path.join(
    os.environ.get("JOB_HUNT_HOME",
                   os.path.expanduser("~/Documents/job_applications")),
    "config.yml")

# host suffix -> (board name in config.yml, where the tenant lives)
#
# `path` means the first path segment; `host` means the hostname itself is the
# tenant, which is how the config names them for those boards. Only shapes this
# repository has an adapter for are listed: a provider nobody can sweep is not
# worth offering.
SHAPES = (
    ("jobs.smartrecruiters.com", "smartrecruiters", "path"),
    ("careers.smartrecruiters.com", "smartrecruiters", "path"),
    ("boards.greenhouse.io", "greenhouse", "path"),
    ("job-boards.greenhouse.io", "greenhouse", "path"),
    ("jobs.lever.co", "lever", "path"),
    ("jobs.eu.lever.co", "lever", "path"),
    ("jobs.ashbyhq.com", "ashby", "path"),
    ("apply.workable.com", "workable", "path"),
    ("join.com", "join", "path"),
    (".teamtailor.com", "teamtailor", "subdomain"),
    (".recruitee.com", "recruitee", "subdomain"),
    (".taleez.com", "taleez", "subdomain"),
    (".jobs.personio.com", "personio", "subdomain"),
    (".jobs.personio.de", "personio", "subdomain"),
    (".myworkdayjobs.com", "workday", "host"),
    (".umantis.com", "umantis", "host"),
    ("icims.com", "icims", "host"),
    ("successfactors.eu", "successfactors", "host"),
    ("successfactors.com", "successfactors", "host"),
)
# Hosts that are known to be a hop and never the destination. Named so a
# reader knows the redirect was expected rather than incidental.
REDIRECTORS = ("contactrh.com", "career012.successfactors.eu")


def die(msg, code=2):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def note(msg):
    print(f"[tenant] {msg}", file=sys.stderr)


def final_url(url, follow=True):
    """The URL after redirects, and every hop on the way.

    A zero-byte 302 is a real answer here, so the body is never read — only
    where it went.
    """
    hops = [url]
    if not follow:
        return url, hops
    seen = set()
    current = url
    for _ in range(8):
        if current in seen:
            break
        seen.add(current)
        # **A HEAD is a request.** This script was one of ten that never
        # mentioned `robots` (#100), and the assumption that grouped it with
        # the ledger tools was wrong: it follows up to eight redirects with
        # HEAD, reading no body but touching every hop.
        #
        # The tempting exemption is that it retrieves no content and follows a
        # link the user supplied — the `Claude-User` class. **`www.linkedin.com`
        # refutes it**: that file names `Claude-User` and closes everything to
        # it, which is an operator using these rules to govern exactly this
        # kind of access. Being user-directed is not an exemption; it is a
        # class operators address. So this asks, per host and per path.
        parts = urllib.parse.urlsplit(current)
        gate = robots_allowed(parts.netloc, parts.path or "/")
        if gate["allowed"] is not True:
            note(f"stopping at {current} — {gate['reason']} **No HEAD was "
                 f"sent to this hop.** The chain so far is reported; the "
                 f"provider behind this URL is not identified, which is not "
                 f"the same as there being none.")
            break
        req = urllib.request.Request(current, headers={"User-Agent": UA},
                                     method="HEAD")
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                landed = r.geturl()
        except urllib.error.HTTPError as e:
            landed = e.geturl() if hasattr(e, "geturl") else current
        except (urllib.error.URLError, OSError, ValueError):
            # Unreachable is not "unknown provider": say which URL stopped us.
            note(f"could not follow {current} — reading the host as published")
            break
        if landed == current:
            break
        hops.append(landed)
        current = landed
    return current, hops


def identify(url):
    """`{provider, tenant}` from a URL, or a named `unknown`."""
    p = urllib.parse.urlparse(url)
    host = (p.hostname or "").lower()
    segs = [s for s in p.path.split("/") if s]
    for suffix, board, where in SHAPES:
        if not (host == suffix.lstrip(".") or host.endswith(suffix)):
            continue
        if where == "path":
            tenant = segs[0] if segs else None
        elif where == "subdomain":
            tenant = host[: -len(suffix)] if host.endswith(suffix) else None
        else:
            tenant = host
        return {"provider": board, "tenant": tenant, "host": host,
                "redirector": host.endswith(REDIRECTORS)}
    return {"provider": None, "tenant": None, "host": host,
            "redirector": any(host.endswith(r) for r in REDIRECTORS)}


BOARD_RE = re.compile(r"^  ([A-Za-z0-9_.-]+):\s*$")


def employers_of(cfg_path):
    """The `employers:` list under each board, in both shapes it is written.

    `dormant.py`'s parser deliberately skips nested lists — it reads flat
    dormancy keys — so this reads the one nested key that matters here:

        employers: ["nexthink", "swissquote"]        inline
        employers:                                    block, of maps
          - host: "logitech.wd5.myworkdayjobs.com"

    **A tenant already configured must never be offered again**, and that is
    the only thing this is for.
    """
    out, board = {}, None
    for raw in open(cfg_path, encoding="utf-8").read().splitlines():
        m = BOARD_RE.match(raw)
        if m:
            board = m.group(1)
            continue
        if board is None or (raw.strip() and not raw.startswith("  ")):
            if raw.strip() and not raw.startswith(" "):
                board = None
            continue
        m = re.match(r"\s+employers:\s*\[(.*)\]\s*$", raw)
        if m:
            out.setdefault(board, set()).update(
                v.strip().strip('"\'') for v in m.group(1).split(",") if v.strip())
            continue
        m = re.match(r"\s+-\s+host:\s*\"?([^\"\s]+)\"?\s*$", raw)
        if m and board:
            out.setdefault(board, set()).add(m.group(1))
        m = re.match(r"\s+-\s+\"?([A-Za-z0-9_.-]+)\"?\s*$", raw)
        if m and board:
            out.setdefault(board, set()).add(m.group(1))
    return out


def configured(cfg_path):
    """What the user's config already sweeps: enabled state and tenants."""
    if not os.path.exists(cfg_path):
        return None
    boards = read_boards(cfg_path)
    tenants = employers_of(cfg_path)
    out = {}
    for name, row in boards.items():
        enabled = str(row.get("enabled", "")).strip().lower() in ("true", "yes")
        out[name] = {"enabled": enabled,
                     "tenants": {t.lower() for t in tenants.get(name, ())}}
    return out


def identify_chain(hops):
    """The first hop that names a provider — not the first URL, not the last.

    **Both ends of a redirect chain lie, and in opposite directions.** Measured
    2026-09-02:

        sicpa.contactrh.com  ->  …successfactors.eu  ->  jobs.sicpa.com
            the published host is a redirector: reading it says "unknown"

        boards.greenhouse.io/elastic  ->  job-boards.greenhouse.io/elastic
                                      ->  jobs.elastic.co/
            the final host is the employer's own vanity domain: reading it
            also says "unknown", and the provider was visible at hop two

    So neither "read what was published" nor "read where it ended" is right.
    Walk the chain and take the first hop that identifies.
    """
    for url in hops:
        row = identify(url)
        if row["provider"]:
            row["identified_at"] = url
            return row
    row = identify(hops[-1])
    row["identified_at"] = None
    return row


def probe(host):
    """Ask a host what it is, for providers a hostname cannot reveal.

    **A SuccessFactors tenant usually lives on the employer's own domain** —
    `jobs.sicpa.com` contains nothing to match on, and it is exactly the case
    issue #83 was opened about. The adapter already has the test:
    `successfactors.py locale --host` answers `{"locale": "en_GB"}` on a real
    tenant. One request, and only when no hop identified anything.
    """
    import subprocess
    script = os.path.join(HERE, "successfactors.py")
    try:
        out = subprocess.run([sys.executable, script, "locale", "--host", host],
                             capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError) as exc:
        print(f"[tenant-offer] the successfactors probe could not be run "
              f"({exc}) — **that is not the same as this host not being a "
              f"SuccessFactors tenant**, and nothing here can tell them "
              f"apart.", file=sys.stderr)
        return None
    # **A probe that failed and a probe that found nothing both return None
    # here**, because this is one hop among several and it must not stop the
    # others. So the difference is said aloud rather than folded away:
    # `subprocess.run` does not raise on a non-zero exit, and an empty stdout
    # parses to "no locale" perfectly well. Issue #123.
    if out.returncode != 0:
        print(f"[tenant-offer] the successfactors probe exited "
              f"{out.returncode} on {host}: "
              f"{(out.stderr or '').strip()[:200]} — **treated as 'not "
              f"identified', which is weaker than 'not a tenant'.**",
              file=sys.stderr)
        return None
    try:
        d = json.loads(out.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        return None
    if d.get("locale"):
        return {"provider": "successfactors", "tenant": host, "host": host,
                "redirector": False, "probed": "successfactors.py locale",
                "locale": d["locale"]}
    return None


def cmd_read(a):
    landed, hops = final_url(a.url, follow=not a.no_follow)
    row = identify_chain(hops)
    if row["provider"] is None and a.probe:
        hit = probe(urllib.parse.urlparse(landed).hostname or "")
        if hit:
            hit["identified_at"] = landed
            row = hit
    row["url"] = a.url
    row["resolved_url"] = landed
    row["hops"] = hops if len(hops) > 1 else []
    if row["provider"] is None:
        row["note"] = (
            f"{row['host']!r} matches no ATS shape this repository has an "
            f"adapter for. **Named rather than dropped**: a URL nobody could "
            f"read is a fact worth seeing, and it may be a provider worth an "
            f"adapter.")
    if len(hops) > 1:
        row["note_redirect"] = (
            f"followed {len(hops) - 1} redirect(s) before reading the host — "
            f"the published URL was {urllib.parse.urlparse(a.url).hostname!r}. "
            f"Reading the host as published would have answered "
            f"'unknown provider' for a tenant that is identifiable.")
    print(json.dumps(row, ensure_ascii=False))
    return 0


def cmd_scan(a):
    cfg = configured(a.config)
    if cfg is None:
        die(f"no config at {a.config} — nothing to compare against.")
    urls = [l.strip() for l in open(a.urls, encoding="utf-8") if l.strip()]
    seen = {}
    for u in urls:
        landed, hops = final_url(u, follow=not a.no_follow)
        row = identify_chain(hops)
        if row["provider"] is None and a.probe:
            row = probe(urllib.parse.urlparse(landed).hostname or "") or row
        if not row["provider"] or not row["tenant"]:
            key = ("unknown", row["host"])
        else:
            key = (row["provider"], row["tenant"])
        seen.setdefault(key, {"count": 0, "example": u, "resolved": landed,
                              "hops": len(hops) - 1})
        seen[key]["count"] += 1
    for (provider, tenant), info in sorted(seen.items(),
                                           key=lambda kv: -kv[1]["count"]):
        board = cfg.get(provider)
        known = bool(board and tenant
                     and str(tenant).lower() in board["tenants"])
        state = ("no-adapter" if provider == "unknown" else
                 "board-not-configured" if board is None else
                 "board-disabled" if not board["enabled"] else
                 "tenant-already-configured" if known else
                 "tenant-missing")
        print(json.dumps({
            "provider": provider, "tenant": tenant, "ads": info["count"],
            "board_state": state, "example": info["example"],
            "resolved": info["resolved"], "redirects": info["hops"],
            # **Never `offer: true` on an unverified tenant.** A wrong
            # SmartRecruiters tenant answers 200 with zero ads, so an offer
            # made without confirming it is worse than saying nothing.
            "offer": state == "tenant-missing",
            "verify_first": (
                "confirm the tenant answers before offering it — on "
                "SmartRecruiters a wrong one returns 200 with an empty list, "
                "which is why a tenant is only ever added from an ad that was "
                "actually seen"
                if state == "tenant-missing" else None),
        }, ensure_ascii=False))
    note(f"{len(urls)} URL(s) read, {len(seen)} distinct provider/tenant pair(s). "
         f"**Nothing was written**: adding a tenant is the user's line in their "
         f"own config, offered in a question they are already answering.")
    return 0


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("read", help="one apply URL -> provider and tenant")
    r.add_argument("--url", required=True)
    r.add_argument("--no-follow", action="store_true", dest="no_follow",
                   help="read the host as published. **Shows the trap**: "
                        "a redirector reads as an unknown provider")
    r.add_argument("--probe", action="store_true",
                   help="when no hop names a provider, ask the host itself. "
                        "One extra request, and the only way to see a "
                        "SuccessFactors tenant on the employer's own domain")
    r.set_defaults(func=cmd_read)

    s = sub.add_parser("scan", help="a run's apply URLs against the config")
    s.add_argument("--urls", required=True, help="one URL per line")
    s.add_argument("--config", default=DEFAULT_CONFIG)
    s.add_argument("--no-follow", action="store_true", dest="no_follow")
    s.add_argument("--probe", action="store_true",
                   help="ask a host that no hop identified — one extra request "
                        "each, and it is what finds a SuccessFactors tenant on "
                        "an employer's own domain")
    s.set_defaults(func=cmd_scan)
    a = p.parse_args()
    return a.func(a)


if __name__ == "__main__":
    raise SystemExit(main())
