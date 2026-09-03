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
import urllib.parse
import urllib.request

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")

# Keyed on the host **that answered**, never on the string a caller typed —
# see `verdict()`. `_ALIAS` maps what was asked to what answered, so a repeat
# of the same request costs nothing and a different spelling that lands on the
# same host reuses the verdict rather than re-reading the file.
_CACHE = {}
_ALIAS = {}


# The directives a rules file is made of. One of these, at the start of a
# line, is what a `robots.txt` looks like from the inside.
_DIRECTIVE = re.compile(
    r"(?im)^\s*(user-agent|disallow|allow|sitemap|crawl-delay|host|"
    r"content-signal)\s*:")


def _looks_like_rules(body):
    """Decide from the body when the server declined to declare a type.

    **The first line settles it and the size corroborates.** Real files
    measured here run 58 to a few hundred bytes and open on a directive; the
    impostors open on `<` and run to 126 015. Markup is checked first because
    a login page can perfectly well contain the word `sitemap`.
    """
    head = (body or "")[:400].lstrip().lower()
    if head.startswith(("<!doctype", "<html", "<?xml", "<")):
        return False
    return bool(_DIRECTIVE.search(body or ""))


def _fetch(host):
    """Read one host's file, and report **which host actually answered**.

    `urllib` follows redirects, and a redirect can cross hosts: `ss.ge` sends
    a jobs path to `jobs.ss.ge`, which publishes a **different** rules file —
    62 bytes of `Allow: /` against the apex's 478 bytes of named refusals.
    Returning only the body would hand the caller the right rules under the
    wrong name. Issue #99.
    """
    url = f"https://{host}/robots.txt"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=20) as r:
            final = urllib.parse.urlsplit(r.geturl()).netloc or host
            ctype = r.headers.get("Content-Type")
            body = r.read().decode("utf-8", "replace")
            # A robots.txt that is not text/plain is not a robots.txt — see
            # shared/robots-policy.md. 126 KB of sign-in HTML answered 200 on
            # my.indeed.com, and an Angular shell did the same on kemnaker.
            #
            # **But an absent header is not a declaration of HTML.** The
            # original test was `"text/plain" not in ctype` with `ctype`
            # defaulting to `""`, so a server that declares nothing was
            # rejected without its file being looked at:
            # `hukoomi.gov.qa` serves a valid 468-byte robots.txt with **no
            # `Content-Type` at all** and the plugin called it unreadable.
            # Same asymmetry this module already applies one level up — an
            # absent robots.txt is not a refusal — pushed one level down:
            # **an absence of metadata is not negative metadata.** Issue #96.
            if ctype is None:
                if _looks_like_rules(body):
                    return {"state": "read", "body": body, "final": final,
                            "why": "no Content-Type; the body is a rules file"}
                return {"state": "unreadable", "final": final,
                        "why": f"no Content-Type, and the {len(body)} bytes "
                               f"are not a rules file either"}
            if "text/plain" not in ctype:
                return {"state": "unreadable", "final": final,
                        "why": f"Content-Type {ctype!r}, {len(body)} bytes — "
                               f"not a rules file"}
            return {"state": "read", "body": body, "final": final}
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"state": "absent", "why": "404 — no robots.txt published"}
        return {"state": "unreadable", "why": f"HTTP {e.code}"}
    except (urllib.error.URLError, OSError) as e:
        return {"state": "unreadable", "why": str(e)}


def siblings(host):
    """Does the apex/`www` twin publish a **different rules file**?

    **A diagnostic, run once when a board is written — not on every sweep**,
    and the measurement is why. Across 55 comparable hosts already known to
    this repository, 2026-09-03:

        raw md5 difference          5 of 55
        two real rules files        2 of 55   — flatchr.io, jobindex.dk

    **Three of the five were not two rules files at all**: `job-room.ch`'s
    apex redirects to its home page, `job.id`'s `www` answers 59 KB of HTML,
    and `digitalrecruiters.com` sends both forms to `www.cegid.com`. Comparing
    bytes without asking whether a rules file came back inflated the finding
    by more than double — **the very guard this module applies is the one that
    ad-hoc comparison skips**.

    **So two requests on every host to catch four per cent is disproportionate,
    and the four per cent is not harmless:** `jobindex.dk` serves **47 bytes of
    `User-agent: * / Disallow: /`** on the apex and 4 218 bytes of detailed
    permissions on the `www`. An adapter written against the `www` never sees
    the refusal. Issue #98.
    """
    h = host[4:] if host.startswith("www.") else host
    pair = {}
    for name in (h, "www." + h):
        got = _fetch(name)
        pair[name] = {
            "state": got["state"],
            "final": got.get("final"),
            "bytes": len(got.get("body") or ""),
            "is_rules_file": got["state"] == "read",
            "why": got.get("why"),
        }
    a, b = pair[h], pair["www." + h]
    out = {"pair": pair, "comparable": a["is_rules_file"] and b["is_rules_file"],
           "differ": None, "sweep": {}}
    for name in pair:
        v = verdict(name)
        out["sweep"][name] = v["sweep"]
    if out["comparable"]:
        fa = _fetch(h).get("body") or ""
        fb = _fetch("www." + h).get("body") or ""
        out["differ"] = fa.strip() != fb.strip()
    # **The one that matters is a disagreement about permission**, not about
    # bytes: two files can differ in a comment and agree on everything.
    out["sweep_disagrees"] = len(set(out["sweep"].values())) > 1
    return out


def verdict(host):
    """What this host says about being read.

    Returns a dict with `sweep` (bool), `reason`, and the raw signals. It is
    deliberately conservative in one direction only: a blanket `Disallow: /`
    for `*`, or a `Content-Signal` saying `ai-input=no`, returns
    `sweep: False`. Everything else — including an unreadable or absent file —
    returns True with the reason named, because an absent file is not a
    refusal and this module must not invent one.

    **That claim used to be false in the one place it mattered.** The
    `Content-Signal` was read with `re.search`, which stops at the first
    occurrence — so on a file carrying two, a refusal in the second was never
    seen and the module returned `sweep: True`. **The error went towards
    permitted, on the only signal here that expresses a refusal of consent.**
    Every occurrence is read now, restrictions are unioned, and a file that
    contradicts itself says so in `content_signal_conflict` instead of being
    summarised by whichever line the CDN happened to inject first. Issue #98.

    `host` is the host that **answered**; `requested_host` is what the caller
    asked for. They differ whenever a redirect crossed hosts, and the file
    read is the answering host's — see the cache note below. Issue #99.
    """
    # **Keyed on the host that answered, not on the string that was typed.**
    # `urllib` follows redirects across hosts, so `verdict("ss.ge")` from one
    # caller and from another aiming at a path that lands on `jobs.ss.ge`
    # would share one entry — and those two hosts publish different files.
    # `_ALIAS` remembers what a spelling resolved to, so a repeat costs
    # nothing. **A spelling never seen before still costs one request**: there
    # is no way to learn a redirect without following it, and this fixes the
    # verdict being reused, not the fetch. Issue #99.
    if host in _ALIAS:
        return _CACHE[_ALIAS[host]]
    got = _fetch(host)
    final = got.get("final") or host
    if final in _CACHE:
        _ALIAS[host] = final
        return _CACHE[final]

    def _keep(result):
        _CACHE[final] = result
        _ALIAS[host] = final
        return result

    out = {"host": final, "requested_host": host, "sweep": True,
           "reason": None, "content_signal": None, "state": got["state"]}
    if final != host:
        out["reason"] = (f"read from {final!r}, not {host!r} — the request "
                         f"was redirected, and the two hosts do not "
                         f"necessarily publish the same file.")
    if got["state"] != "read":
        out["reason"] = f"robots.txt {got['state']}: {got.get('why')}"
        return _keep(out)

    body = got["body"]
    # **Every occurrence, not the first.** `re.search` stops at one, and which
    # one comes first is an accident of injection order — a file can carry the
    # origin's signal and a CDN's. Measured on `www.mtss.go.cr`: two
    # `Content-Signal` lines that disagree, one permitting `use=reference` and
    # one silent about it. **There is no resolution rule for this convention**,
    # so nothing is arbitrated: the restrictions are unioned and the
    # disagreement is reported. Issue #98.
    signals = [m.group(1).strip() for m in
               re.finditer(r"(?im)^\s*Content-Signal\s*:\s*(.+)$", body)]
    if signals:
        out["content_signal"] = signals
        out["content_signal_conflict"] = len(set(signals)) > 1
        refusing = [x for x in signals
                    if re.search(r"ai-input\s*=\s*no", x, re.I)]
        if refusing:
            out["sweep"] = False
            more = (f" The file declares {len(signals)} `Content-Signal` "
                    f"lines and they do not agree; **a refusal in any of them "
                    f"is a refusal**, because no convention says which wins."
                    if out["content_signal_conflict"] else "")
            out["reason"] = (f"this host publishes `Content-Signal: "
                             f"{refusing[0]}`. `ai-input=no` is the operator "
                             f"asking that its content not be read into an AI "
                             f"system, which is what a sweep does. Not "
                             f"swept.{more}")
            return _keep(out)

    # The `*` group only: a rule aimed at one named crawler is not aimed here.
    dis, allow = _star_group(body)
    out["disallow"] = dis
    out["allow"] = allow
    if "/" in dis:
        out["sweep"] = False
        out["reason"] = ("this host's robots.txt is `User-agent: * / "
                         "Disallow: /` — everything closed, evenly. Not swept.")
    elif dis:
        # **`sweep` answers "is this host closed in one block". It cannot
        # answer for a path, and it must not look as though it does.**
        # `empleate.gob.hn` refuses `/Vacantes/` and `/Candidatos/` to `*` —
        # the vacancies themselves — while `"/"` is absent, so `sweep` is
        # True and used to be the whole answer. Issue #101.
        out["reason"] = (
            f"this host refuses {len(dis)} path(s) to `*` and not the site as "
            f"a whole: {', '.join(dis[:4])}. **`sweep: True` means it is not "
            f"closed in one block; it does not mean the path you want is "
            f"open.** Call `allowed(host, path)` before fetching one.")
    return _keep(out)


def _star_group(body):
    """The `Disallow` and `Allow` rules that bind `*`, as written.

    **Consecutive `User-agent` lines form one group**, and the previous
    version overwrote the agent on each of them — so

        User-agent: *
        User-agent: Googlebot
        Disallow: /x

    lost the `*` rule entirely, and **the error went towards permitted.** It
    is the mirror of the defect that produced 41 false positives out of 143
    files elsewhere on the same day by reading those runs as separate groups:
    **the same ignorance of the grammar, erring in opposite directions
    depending on which way it is misread.** Issue #101.

    **Repeated `*` records merge** rather than the first winning — RFC 9309 —
    which this repository measured on eight consecutive `User-agent: *`
    groups.
    """
    dis, allow, agents, in_group = [], [], set(), False
    for line in (body or "").splitlines():
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        k, _, v = line.partition(":")
        k, v = k.strip().lower(), v.strip()
        if k == "user-agent":
            if in_group:            # a new group begins after a directive
                agents = set()
                in_group = False
            agents.add(v)
        elif k in ("disallow", "allow"):
            in_group = True
            if "*" in agents:
                (dis if k == "disallow" else allow).append(v)
    return dis, allow


def _match_len(pattern, path):
    """How many characters of `path` a robots pattern matches, or -1.

    Prefix matching with `*` and `$`, which is what the specification asks of
    a rule and all this needs. An **empty `Disallow:`** matches nothing — it
    is the way a file says *nothing is closed* — so it returns -1 rather than
    matching everything at length zero.
    """
    if pattern == "":
        return -1
    rx = re.escape(pattern).replace(r"\*", ".*")
    if rx.endswith(r"\$"):
        rx = rx[:-2] + "$"
    m = re.match(rx, path)
    return len(m.group(0)) if m else -1


def allowed(host, path):
    """May `path` be fetched on `host`? **Longest match wins, `Allow` on a tie.**

    `verdict()` answers *is this host closed in one block*. **A path needs its
    own question**, and until #101 there was no way to ask it: the `*` group's
    rules were computed and thrown away.

    Returns a dict, never a bare bool, because *why* matters as much as *no*:
    `allowed`, `rule` (the directive that decided), `kind`, and the host that
    actually answered.
    """
    v = verdict(host)
    out = {"host": v["host"], "requested_host": v.get("requested_host"),
           "path": path, "allowed": True, "rule": None, "kind": None,
           "sweep": v["sweep"]}
    if not v["sweep"]:
        out.update(allowed=False, kind="host-closed", rule="/")
        out["reason"] = v["reason"]
        return out
    if v["state"] != "read":
        out["reason"] = (f"no rules were read ({v['state']}) — **absence of a "
                         f"file is not a refusal**, and it is not a permission "
                         f"either. Proceed at a human pace and say so.")
        return out
    best_d = max(((_match_len(p, path), p) for p in v.get("disallow") or []),
                 default=(-1, None))
    best_a = max(((_match_len(p, path), p) for p in v.get("allow") or []),
                 default=(-1, None))
    if best_d[0] < 0:
        out["reason"] = "no `Disallow` in the `*` group matches this path."
        return out
    # A tie goes to `Allow`: the specification's rule, and the direction that
    # respects an operator who wrote both.
    if best_a[0] >= best_d[0]:
        out.update(rule=best_a[1], kind="allow")
        out["reason"] = (f"`Allow: {best_a[1]}` matches at least as much of "
                         f"this path as `Disallow: {best_d[1]}`.")
        return out
    out.update(allowed=False, rule=best_d[1], kind="disallow")
    out["reason"] = (f"`{v['host']}` refuses this path to `User-agent: *` — "
                     f"`Disallow: {best_d[1]}`. **This is a refusal aimed at "
                     f"everyone, not at a named crawler**, and the intention "
                     f"behind it does not change its effect.")
    return out


def _main():
    import argparse
    import json
    import sys
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("host")
    p.add_argument("--siblings", action="store_true",
                   help="also read the apex/www twin and compare — a "
                        "diagnostic for writing a board card, not for a sweep")
    a = p.parse_args()
    print(json.dumps(verdict(a.host), ensure_ascii=False, indent=1))
    if a.siblings:
        sib = siblings(a.host)
        print(json.dumps(sib, ensure_ascii=False, indent=1))
        if sib["sweep_disagrees"]:
            print("[robots] **the two forms disagree about whether this host "
                  "may be swept.** The more restrictive one was written by "
                  "the same operator; do not pick the convenient one.",
                  file=sys.stderr)
        elif sib["differ"]:
            print("[robots] the two forms publish different files that agree "
                  "on the sweep. Record which host the adapter reads.",
                  file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())
