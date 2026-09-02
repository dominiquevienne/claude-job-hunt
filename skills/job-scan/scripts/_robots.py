#!/usr/bin/env python3
"""Read one host's robots.txt before sweeping it — because on a per-tenant ATS
the policy belongs to the tenant, not to the platform.

**Measured 2026-09-02, and this is why the module exists.** Three Teamtailor
tenants, same platform, same product:

    investengine.teamtailor.com  Content-Signal: search=yes, ai-train=no, ai-input=yes
    oatly.teamtailor.com         Content-Signal: search=yes, ai-train=no, ai-input=yes
    polestar.teamtailor.com      Content-Signal: search=no,  ai-train=no, ai-input=no
    normative.teamtailor.com     Content-Signal: search=no,  ai-train=no, ai-input=no

`teamtailor.md` records the first line **as the platform's policy**. Two of the
four tenants say the opposite, and `ai-input=no` is a tenant asking not to be
read into an AI system — which is what this plugin does, on a user's behalf.

No script in this repository read a tenant's `robots.txt` at runtime before
this one. The policy was read once by a person, written into a board file, and
applied to every tenant of the family afterwards.

**Where this matters and where it does not.** Greenhouse, Lever, Ashby and
Workable serve every tenant from one API host — `boards-api.greenhouse.io`,
`api.lever.co`, `api.ashbyhq.com`, `apply.workable.com` — so one file governs
the family and reading it once is right. Teamtailor, Workday, Taleez,
Personio, umantis, SuccessFactors, Oracle Cloud and iCIMS give each tenant its
own hostname, so each tenant can answer differently, and two of six iCIMS
hosts sampled served `Disallow: /` outright.

Use `verdict(host)` and act on it. It fetches once per host per process.
"""

import re
import urllib.error
import urllib.request

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")

_CACHE = {}


def _fetch(host):
    url = f"https://{host}/robots.txt"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=20) as r:
            ctype = r.headers.get("Content-Type", "")
            body = r.read().decode("utf-8", "replace")
            # A robots.txt that is not text/plain is not a robots.txt — see
            # shared/robots-policy.md. 126 KB of sign-in HTML answered 200 on
            # my.indeed.com, and an Angular shell did the same on kemnaker.
            if "text/plain" not in ctype:
                return {"state": "unreadable",
                        "why": f"Content-Type {ctype!r}, {len(body)} bytes — "
                               f"not a rules file"}
            return {"state": "read", "body": body}
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"state": "absent", "why": "404 — no robots.txt published"}
        return {"state": "unreadable", "why": f"HTTP {e.code}"}
    except (urllib.error.URLError, OSError) as e:
        return {"state": "unreadable", "why": str(e)}


def verdict(host):
    """What this host says about being read.

    Returns a dict with `sweep` (bool), `reason`, and the raw signals. It is
    deliberately conservative in one direction only: a blanket `Disallow: /`
    for `*`, or a `Content-Signal` saying `ai-input=no`, returns
    `sweep: False`. Everything else — including an unreadable or absent file —
    returns True with the reason named, because an absent file is not a
    refusal and this module must not invent one.
    """
    if host in _CACHE:
        return _CACHE[host]
    got = _fetch(host)
    out = {"host": host, "sweep": True, "reason": None,
           "content_signal": None, "state": got["state"]}
    if got["state"] != "read":
        out["reason"] = f"robots.txt {got['state']}: {got.get('why')}"
        _CACHE[host] = out
        return out

    body = got["body"]
    signal = None
    m = re.search(r"(?im)^\s*Content-Signal\s*:\s*(.+)$", body)
    if m:
        signal = m.group(1).strip()
        out["content_signal"] = signal
        if re.search(r"ai-input\s*=\s*no", signal, re.I):
            out["sweep"] = False
            out["reason"] = (f"this host publishes `Content-Signal: {signal}`. "
                             f"`ai-input=no` is the operator asking that its "
                             f"content not be read into an AI system, which is "
                             f"what a sweep does. Not swept.")
            _CACHE[host] = out
            return out

    # The `*` group only: a rule aimed at one named crawler is not aimed here.
    star, current = [], None
    for line in body.splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        k, _, v = line.partition(":")
        k, v = k.strip().lower(), v.strip()
        if k == "user-agent":
            current = v
        elif k == "disallow" and current == "*":
            star.append(v)
    if "/" in star:
        out["sweep"] = False
        out["reason"] = ("this host's robots.txt is `User-agent: * / "
                         "Disallow: /` — everything closed, evenly. Not swept.")
    _CACHE[host] = out
    return out
