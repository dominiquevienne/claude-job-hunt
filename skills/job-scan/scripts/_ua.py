#!/usr/bin/env python3
"""What this plugin says it is, in one place. Issue #120, point 1 of #124.

**The repository obeyed `Claude-User`'s rules and announced Chrome.** 63 files
carried `Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) …` while
`_robots.OUR_AGENTS` already bound the guard to `claude-user`, and
`shared/boards/job-room.md` argued its position in as many words:

    This adapter does not crawl that path: it reads the portal's own public
    API, unauthenticated, a handful of times, for one user's own job search.

**That is the `Claude-User` class exactly** — and an operator reading the
request saw a Chrome browser. The decision on #120 (2026-09-03, by the
repository's owner) is to declare it, because the mechanism in #124 cannot
branch on *"`Claude-User` is allowed"* without it.

**DECLARING CHANGES WHAT WE SEND, NOT WHAT WE OBEY.** The guard has bound this
project to `claude-user` rules since #116; nothing in coverage moves because
of this file. What moves is that an operator can now recognise us, apply a
rule to us, and have it take effect.

**AND ONE CONSEQUENCE NOBODY HAS RAISED, WHICH LANDS ON THE USER.** Anthropic
publishes `https://claude.com/crawling/bots.json` so that operators can verify
its agents — and it contains **IP prefixes and nothing else**: no user-agent
strings, only `216.73.216.0/22` and some /32s. **This plugin runs on the
user's own machine, from the user's own address, which is not in that list.**
An operator who matches the token and then checks the address will find a
mismatch, and the reading available to them is *spoofed*.

**So the token is carried inside a string that says plainly what this is.** It
names the plugin, its version and its repository. An operator matching
`Claude-User` in a `robots.txt` group gets the behaviour the decision intends;
an operator reading the string sees that this is a personal tool on a personal
machine, not Anthropic's fleet. **Both readings are true, which is the only
arrangement worth sending.**

If a host that used to permit us starts refusing after this, that must be
visible on the day — `shared/never-fail-silently.md` — not discovered in a
count that quietly shrank. `blocked_note()` is what says it.
"""

__all__ = ["UA", "TOKEN", "blocked_note"]

TOKEN = "Claude-User"

# **One string, and every adapter imports it.** Three files already declared
# themselves honestly — `ats.py`, `jobroom.py`, `francetravail.py` — and 63
# announced Chrome; the split is exactly how a repository comes to plead one
# thing and send another.


UA = (f"Mozilla/5.0 (compatible; {TOKEN}; claude-job-hunt/1.195.0; "
      f"+https://github.com/dominiquevienne/claude-job-hunt)")


def blocked_note(host, status=None):
    """The sentence to add when a host refuses us at the network layer.

    **A block that arrives after this declaration is information, not noise.**
    It may be the operator acting on the token we now send — which is the
    system working — and it may be an ordinary bot wall that would have
    refused Chrome too. The two are not distinguishable from one response,
    **and saying so is the point**: a run that silently returns less is how a
    declaration turns into a quiet loss of coverage.
    """
    seen = f"HTTP {status}" if status else "a refusal"
    return (
        f"{host} answered {seen}. **This plugin declares `{TOKEN}` since "
        f"#120**, so this may be the operator acting on that token — or an "
        f"ordinary bot wall that would have refused any client. **One "
        f"response cannot tell them apart.** If this host used to answer and "
        f"has just stopped, the declaration is the thing that changed, and "
        f"that belongs in today's output rather than in a count that shrank "
        f"quietly. Note also that Anthropic's published verification list "
        f"(claude.com/crawling/bots.json) carries IP prefixes only, and this "
        f"runs from your own address — an operator who checks will see a "
        f"mismatch."
    )


# The exit code for *the rules permit this and the server refused the client*.
# Distinct from 7 (refused by the rules) and 8 (the rules could not be read),
# because it is the one case where the browser is a legitimate answer and the
# other two are cases where it is not.
EXIT_NEEDS_BROWSER = 9


def browser_fallback(host, guard_allowed, status=None, path="/"):
    """`(message, exit_code)` when a **permitted** host refuses the client.

    **The trigger is a fetch failure, never a refusal** — issue #124, and the
    whole worth of declaring `Claude-User` rests on it. Declaring the token and
    then reaching for a browser at every refusal would be **worse than not
    declaring**: it hands operators a way to recognise us and makes it
    ineffective, which is #100's *appearance of control* wearing the
    repository's own policy.

    So this raises rather than returns when the guard did not say yes:

        guard True   -> a fetch failure here is a client problem. #66: the
                        browser changes the layer, not the permission.
        guard False  -> refused. The browser changes what we wear, not what
                        the operator said.
        guard None   -> unknown. #118: *could not read* is not a permission,
                        and it does not become one because another client
                        exists.
    """
    if guard_allowed is not True:
        raise ValueError(
            f"browser_fallback called for {host} with guard_allowed="
            f"{guard_allowed!r}. **The browser is not an answer to a refusal "
            f"or to an unknown** — only to a host that permitted us and whose "
            f"server then refused the client. Issue #124.")
    # Callers pass either a path or a whole URL; `www.hays.frhttps://…` is
    # what happens when a formatter assumes one shape.
    where = path if path.startswith("http") else f"{host}{path}"
    return (
        f"{where} — **the rules permit this and the server refused the "
        f"client.** " + blocked_note(host, status) + "\n"
        f"  **This is the case where a browser is legitimate** (#66: it "
        f"changes the layer, not the permission). Open the page in the "
        f"user's own browser and read it there; do not retry with another "
        f"agent string, and do not treat this as an empty result.",
        EXIT_NEEDS_BROWSER)
