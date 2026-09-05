#!/usr/bin/env python3
"""The parsing core, tested without touching the network.

**Sixty-five of the scripts open a socket on a third-party site; testing
those in CI would mean sweeping the web on every commit**, which is the thing this project
teaches people not to do. So the perimeter is the pure-parsing core, and every
case here is synthetic. Issue #108.

**Most of these cases already existed — written by hand, run once, and read
afterwards.** `_robots.py`'s group grammar was corrected twice in one day
(#101) against exactly these inputs, typed into a shell. **A case that is not
executed is a comment**, and a comment does not fail when someone changes the
function under it.

## The access layer owes two instruments, not one

**This is not a rule against reading source.** Several cases here read files
and are right to: `DocumentedInvocationsAreReal` reads board cards because
**a card is text**, and what it checks — that a documented subcommand exists —
is a property of that text. `SourceCompilesWithoutWarning`, the import ban and
the corpus scans are the same kind. **None of them is touched by what
follows.** Anyone "correcting" them has misread this section.

The rule is narrower:

> **For any guard in the access-and-identity layer whose conclusion is
> behavioural, an exercised case accompanies the corpus scan. The scan is not
> replaced.**

**Because the two instruments prove different things and neither implies the
other.**

  * A **corpus scan** proves an absence across every file — no adapter binds
    its own agent, none assembles the refused URL. **Breadth without depth**:
    it sees the token and never the intent.
  * An **exercised case** proves the mechanism on one file — this request
    carried a TLS context, this header held the declared agent. **Depth
    without breadth**: it says nothing about the other sixty-four.

**The demonstration, which is why the rule exists rather than the reasoning.**
`TlsHostsAreRoutedEverywhere` scanned every adapter for an `import _tls` and
was green while one of them passed `context=None` — the import present, the
context absent, #104 back. An exercised case was added on `oposiciones.py`.
**Twelve hours later `empleate.py` could do the same thing unnoticed** — the
scan saw the import, the exercised case was looking at the other file. And
`empleate.py` is the adapter #104 was opened for.

**The temptation, once the exercised case exists, is to call the scan
redundant.** It would have been, until somebody adds a third adapter. *A
redundancy that only justifies itself at the third case is one that gets
removed at the second.*

**What it costs.** About four lines per case: the exercised ones written for
this run run 19 lines to a source-reading case's 15, and none of them opens a
socket — the opener is replaced by a function that captures the request. The
cheapest two are 7 and 12 lines with no stub at all, because the code was made
testable first: **a condition extracted into a function that returns its
verdict is cheaper to test than the same condition read through text.**

**And the cost falls at scale.** 53 of the 65 network readers share two names
for their fetching function (`get`, `fetch`), so one generic harness covers
82% of the corpus; on eight adapters sampled, seven exercised cleanly under
fifteen lines. **A rule whose cost collapses at scale is not the rule it looks
like when priced file by file.**

Adopted 2026-09-04. **Nothing is owed retroactively**: all eleven cases in
scope were brought up at the time, and each was mutated on the mutation that
used to leave it green.

Run: `python3 -m unittest discover -s tests -v`
"""

import argparse
import hashlib
import io
import os
import pathlib
import re
import shutil
import ssl
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "skills", "job-scan", "scripts"))

import importlib.util     # noqa: E402

import _decode           # noqa: E402
import _language          # noqa: E402
import _ldjson            # noqa: E402
import _locations         # noqa: E402
import _match             # noqa: E402
import _provenance        # noqa: E402
import _robots            # noqa: E402
import _secrets           # noqa: E402
import _sitemap           # noqa: E402


class RobotsGroups(unittest.TestCase):
    """The grammar, and both directions it was got wrong in one day."""

    def test_consecutive_user_agents_form_one_group(self):
        # Read as an overwrite, the `*` rule is lost and the error goes
        # towards permitted. Issue #101, defect 2.
        dis, allow = _robots._star_group(
            "User-agent: *\nUser-agent: Googlebot\nDisallow: /x\n")
        self.assertEqual(dis, ["/x"])
        self.assertEqual(allow, [])

    def test_a_named_agents_rule_is_not_ours(self):
        dis, _ = _robots._star_group(
            "User-agent: Googlebot\nDisallow: /a\n\n"
            "User-agent: *\nDisallow: /b\n")
        self.assertEqual(dis, ["/b"])

    def test_repeated_star_records_merge(self):
        # RFC 9309, and measured on a file with eight consecutive `*` groups.
        dis, _ = _robots._star_group(
            "User-agent: *\nDisallow: /a\n\nUser-agent: *\nDisallow: /b\n")
        self.assertEqual(dis, ["/a", "/b"])

    def test_a_group_restarts_after_a_directive(self):
        # Not only the grammar: **21 of 54 files in this repository's corpus
        # carry more than one record**, so this is the shape of a real file
        # and not a reading of §2.2.1.
        dis, _ = _robots._star_group(
            "User-agent: *\nDisallow: /a\nUser-agent: Bing\nDisallow: /b\n")
        self.assertEqual(dis, ["/a"])

    def test_comments_and_blank_lines_are_not_directives(self):
        dis, _ = _robots._star_group(
            "# User-agent: *\n# Disallow: /trap\n\n"
            "User-agent: *\nDisallow: /real  # trailing\n")
        self.assertEqual(dis, ["/real"])


class RobotsGroupSelection(unittest.TestCase):
    """The group that binds **us**, which is not always `*`. Issue #116."""

    CLOUDFLARE = (
        "User-agent: *\n"
        "Content-Signal: search=yes,ai-train=no,use=reference\n"
        "Allow: /\n\n"
        "User-agent: CCBot\nDisallow: /\n\n"
        "User-agent: ClaudeBot\nDisallow: /\n\n"
        "User-agent: GPTBot\nDisallow: /\n")

    def test_a_named_refusal_is_found(self):
        # The measured shape: `*` open, our token closed. Before #116 this
        # answered *allowed*, on the one kind of file that names us.
        token, dis, allow, matched = _robots.group_for(self.CLOUDFLARE)
        self.assertEqual(token, "claudebot")
        self.assertEqual(dis, ["/"])
        self.assertEqual(matched, ["claudebot"])

    def test_the_star_group_still_reads_as_open(self):
        # Both are true of the same file, which is why the group has to be
        # selected before anything is evaluated.
        dis, allow = _robots._star_group(self.CLOUDFLARE)
        self.assertEqual(dis, [])
        self.assertEqual(allow, ["/"])

    def test_a_named_permission_is_found_too(self):
        # The other direction, and it is real: taleez.com allows our tokens
        # by name. Selection is not a refusal detector.
        token, dis, allow, _m = _robots.group_for(
            "User-agent: *\nDisallow: /x\n\n"
            "User-agent: ClaudeBot\nAllow: /\n")
        self.assertEqual(token, "claudebot")
        self.assertEqual(allow, ["/"])
        self.assertEqual(dis, [])

    def test_falls_back_to_star_when_we_are_not_named(self):
        token, dis, _a, matched = _robots.group_for(
            "User-agent: *\nDisallow: /a\n\n"
            "User-agent: GPTBot\nDisallow: /\n")
        self.assertEqual(matched, [])
        self.assertEqual(token, "*")
        self.assertEqual(dis, ["/a"])

    def test_every_record_that_names_us_binds_us(self):
        """**This test used to assert the opposite, and the opposite was
        wrong.** It read `test_the_longest_matching_token_wins` and pinned
        the rule that made `www.linkedin.com` readable: four records refusing
        this project and one permitting it, and the longest name was the
        permissive one. A case that pins the wrong behaviour defends it.
        Issue #117."""
        _t, dis, _a, matched = _robots.group_for(
            "User-agent: ClaudeBot\nDisallow: /a\n\n"
            "User-agent: Claude-Web\nDisallow: /b\n")
        self.assertEqual(sorted(dis), ["/a", "/b"])
        self.assertEqual(sorted(matched), ["claude-web", "claudebot"])

    def test_the_linkedin_shape_one_permission_among_four_refusals(self):
        _t, dis, allow, matched = _robots.group_for(
            "User-agent: ClaudeBot\nDisallow: /\n\n"
            "User-agent: Claude-Web\nDisallow: /\n\n"
            "User-agent: Claude-User\nDisallow: /\n\n"
            "User-agent: Claude-SearchBot\nDisallow: /search\nAllow: /\n")
        self.assertIn("/", dis)
        # **The permission is not common to all four**, so it is not ours.
        self.assertEqual(allow, [])
        self.assertEqual(len(matched), 4)

    def test_an_allow_survives_only_if_every_record_grants_it(self):
        _t, _d, allow, _m = _robots.group_for(
            "User-agent: ClaudeBot\nAllow: /jobs\nAllow: /x\n\n"
            "User-agent: Claude-Web\nAllow: /jobs\n")
        self.assertEqual(allow, ["/jobs"])

    def test_our_tokens_are_declared_not_derived(self):
        """A module that decides consent must not depend on a UA string built
        elsewhere: an adapter changing its `UA` would silently change which
        rules bind.

        **Provenance, checked 2026-09-03 rather than assumed.** Anthropic's
        own documentation names three — `ClaudeBot`, `Claude-User`,
        `Claude-SearchBot`. Five are published by hosts in this corpus: those
        three plus `Claude-Web` and `anthropic-ai`. `anthropicbot` is in
        neither, and stays because **the two directions do not cost the same**:
        a token we answer to needlessly only binds us to more refusals, while
        a token we are missing loses a refusal aimed at us.

        **That missing direction is the one to keep checking** — enumerate the
        `User-agent` names across the corpus containing `claude` or
        `anthropic` and compare with this tuple. Nothing was missing on
        2026-09-03.
        """
        self.assertIn("claudebot", _robots.OUR_AGENTS)
        self.assertIn("claude-user", _robots.OUR_AGENTS)
        self.assertIn("claude-searchbot", _robots.OUR_AGENTS)
        self.assertTrue(all(a == a.lower() for a in _robots.OUR_AGENTS))

    def test_repeated_named_records_merge(self):
        token, dis, _a, _m = _robots.group_for(
            "User-agent: ClaudeBot\nDisallow: /a\n\n"
            "User-agent: ClaudeBot\nDisallow: /b\n")
        self.assertEqual((token, dis), ("claudebot", ["/a", "/b"]))


class RobotsPaths(unittest.TestCase):
    """`_match_len`: prefix, `*`, `$`, and the empty `Disallow`.

    **These cases came from reading RFC 9309, not from watching a host**, and
    the audit that followed #117 asked what that is worth. One of them rests
    on a genuine ambiguity: §2.2.2 says the winner is *"the match that has the
    most octets"*, and its only worked example — `Allow: /example/page/`
    against `Disallow: /example/page/disallowed.gif` — cannot separate **the
    length of the rule** from **the length of the matched text**. This module
    compares matched text; Google's own documentation describes rule length.

    **So it was measured rather than argued.** 1 402 probe paths were derived
    from the corpus's own rules — for every pattern in the group binding us on
    70 hosts, a path that pattern matches — and the two readings picked the
    same rule **every time**. 25 of 55 files use a wildcard, so the territory
    is real; the disagreement is not, on this corpus.

    **That is not a licence to leave it unexamined.** It is a belief with no
    host behind it, recorded as such, and `/tmp` is the wrong place for the
    probe — re-derive it when a file appears that pits a wildcard `Allow`
    against a longer literal `Disallow`.
    """

    def test_prefix_match_returns_its_length(self):
        self.assertEqual(_robots._match_len("/p", "/pq"), 2)

    def test_no_match_is_minus_one(self):
        self.assertEqual(_robots._match_len("/z", "/pq"), -1)

    def test_star_is_a_wildcard(self):
        self.assertEqual(_robots._match_len("/a*b", "/axxb"), 5)

    def test_dollar_anchors_the_end(self):
        self.assertEqual(_robots._match_len("/x$", "/x"), 2)
        self.assertEqual(_robots._match_len("/x$", "/xy"), -1)

    def test_an_empty_disallow_is_not_a_refused_path_in_the_verdict(self):
        """`_match_len` knew this; `verdict()` did not, and counted it.

        **`employtt.gov.tt` publishes 26 bytes** — `User-agent: *` and a bare
        `Disallow:` — the most permissive file there is. The sentence came out
        *"this host refuses 1 path(s) to `*` ... :"* with nothing after the
        colon. **The permission was right and the account of it was wrong**,
        which is its own kind of wrong: a reader deciding whether to write an
        adapter reads the sentence.
        """
        _robots._CACHE.clear()
        _robots._ALIAS.clear()
        real = _robots._fetch
        _robots._fetch = lambda host: {
            "state": "read", "final": host, "attempts": 1,
            "body": "User-agent: *\nDisallow:\n"}
        try:
            v = _robots.verdict("employtt.gov.tt")
            self.assertIs(v["sweep"], True)
            self.assertEqual(v["disallow"], [])
            self.assertIsNone(v["reason"])
        finally:
            _robots._fetch = real
            _robots._CACHE.clear()
            _robots._ALIAS.clear()

    def test_an_empty_disallow_matches_nothing(self):
        # It is how a file says *nothing is closed*. Matching everything at
        # length zero would close the site instead.
        self.assertEqual(_robots._match_len("", "/anything"), -1)


class RobotsLooksLikeRules(unittest.TestCase):
    """An absent `Content-Type` is not a declaration of HTML. Issue #96."""

    def test_markup_is_not_a_rules_file(self):
        self.assertFalse(_robots._looks_like_rules(
            "<!DOCTYPE html><html><body>Sitemap: /x</body></html>"))

    def test_a_directive_makes_it_one(self):
        self.assertTrue(_robots._looks_like_rules(
            "User-agent: *\nDisallow: /a\n"))

    def test_prose_is_neither(self):
        self.assertFalse(_robots._looks_like_rules("hello world"))


class Sitemap(unittest.TestCase):
    """The three ways a populated sitemap reads as empty. Issue #55."""

    def test_cdata_wrapped_loc(self):
        body = ("<urlset><url><loc><![CDATA[ https://a/1 ]]></loc></url>"
                "</urlset>")
        self.assertEqual(_sitemap.locs(body), ["https://a/1"])

    def test_namespace_prefixed_loc(self):
        self.assertEqual(_sitemap.locs("<x><ns:loc>https://b/1</ns:loc></x>"),
                         ["https://b/1"])

    def test_counts_elements_not_lines(self):
        one_line = "<urlset>" + "".join(
            f"<url><loc>https://c/{i}</loc></url>" for i in range(91)
        ) + "</urlset>"
        self.assertEqual(_sitemap.count(one_line)["locs"], 91)
        self.assertEqual(one_line.count("\n"), 0)

    def test_gzip_served_as_text_is_decompressed(self):
        import gzip
        raw = gzip.compress(b"<urlset><url><loc>https://d/1</loc></url></urlset>")
        self.assertEqual(_sitemap.locs(raw), ["https://d/1"])

    def test_zero_locs_never_says_the_sitemap_is_empty(self):
        says = _sitemap.count_says(
            "<urlset><url><lastmod>2026-01-01</lastmod></url></urlset>")
        self.assertIn("impossible", says.lower())

    def test_contains_filters(self):
        body = "<x><loc>https://a/keep/1</loc><loc>https://a/drop/2</loc></x>"
        self.assertEqual(_sitemap.locs(body, contains="/keep/"),
                         ["https://a/keep/1"])


class LdJson(unittest.TestCase):
    """Polymorphic schema.org fields. Issue #57."""

    def test_one_returns_a_dict_for_a_string(self):
        # Documented behaviour: `one(x).get(...)` must always be legal.
        self.assertEqual(_ldjson.one("a string"), {})

    def test_one_picks_the_first_object_of_a_list(self):
        self.assertEqual(_ldjson.one([{"a": 1}, {"b": 2}]), {"a": 1})

    def test_label_returns_the_string_a_string_carries(self):
        self.assertEqual(_ldjson.label("FULL_TIME"), "FULL_TIME")

    def test_label_reads_an_objects_name(self):
        self.assertEqual(_ldjson.label({"name": "CDI"}), "CDI")

    def test_label_joins_a_list(self):
        self.assertEqual(_ldjson.label(["a", "b"]), "a, b")

    def test_single_quoted_script_type_is_read(self):
        html = ("<script type='application/ld+json'>"
                '{"@type":"JobPosting","title":"x"}</script>')
        self.assertEqual([p.get("title") for p in _ldjson.postings(html)],
                         ["x"])

    def test_literal_newline_inside_a_string_still_parses(self):
        # Two boards of ten need `strict=False`, and you do not know which
        # board will be the third.
        html = ('<script type="application/ld+json">'
                '{"@type":"JobPosting","description":"a\nb"}</script>')
        self.assertEqual(len(_ldjson.postings(html)), 1)


class Secrets(unittest.TestCase):
    """Credentials from a file as well as the environment. Issue #110."""

    def _write(self, text):
        import tempfile
        d = tempfile.mkdtemp()
        with open(os.path.join(d, "credentials.env"), "w",
                  encoding="utf-8") as f:
            f.write(text)
        return d

    def test_reads_key_equals_value(self):
        d = self._write("A_KEY=abc\n")
        old = os.environ.get("JOB_HUNT_HOME")
        os.environ["JOB_HUNT_HOME"] = d
        try:
            _secrets._CACHE.clear()
            self.assertEqual(_secrets.get("A_KEY"), "abc")
        finally:
            _secrets._CACHE.clear()
            if old is None:
                del os.environ["JOB_HUNT_HOME"]
            else:
                os.environ["JOB_HUNT_HOME"] = old

    def test_ignores_comments_strips_quotes_and_export(self):
        d = self._write('# c\nexport B_KEY="xy"\n\nC_KEY=\'z\'\n')
        old = os.environ.get("JOB_HUNT_HOME")
        os.environ["JOB_HUNT_HOME"] = d
        try:
            _secrets._CACHE.clear()
            got = _secrets.load()
            self.assertEqual(got.get("B_KEY"), "xy")
            self.assertEqual(got.get("C_KEY"), "z")
        finally:
            _secrets._CACHE.clear()
            if old is None:
                del os.environ["JOB_HUNT_HOME"]
            else:
                os.environ["JOB_HUNT_HOME"] = old

    def test_the_environment_wins(self):
        d = self._write("D_KEY=from-file\n")
        old_ws, old_d = os.environ.get("JOB_HUNT_HOME"), os.environ.get("D_KEY")
        os.environ["JOB_HUNT_HOME"] = d
        os.environ["D_KEY"] = "from-env"
        try:
            _secrets._CACHE.clear()
            self.assertEqual(_secrets.get("D_KEY"), "from-env")
        finally:
            _secrets._CACHE.clear()
            for k, v in (("JOB_HUNT_HOME", old_ws), ("D_KEY", old_d)):
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v

    def test_printing_the_container_shows_no_value(self):
        # The accident a plain dict invites. Not a substitute for not printing
        # what `get()` returns — see the class docstring.
        m = _secrets.Masked({"K": "supersecret"})
        self.assertNotIn("supersecret", repr(m))
        self.assertNotIn("supersecret", f"{m}")
        self.assertIn("11 chars", repr(m))

    def test_the_message_gives_both_routes(self):
        note = _secrets.missing_note(["X_KEY"], "svc", "Service", "example.com")
        self.assertIn("credentials.env", note)
        self.assertIn("set -a", note)
        self.assertIn("config.yml", note)


def _stdlib_names():
    """The standard library's module names, on every version this runs on.

    **`sys.stdlib_module_names` is 3.10+, and this file is the only thing in
    the repository that needed it.** `core.yml` declares 3.9 as the floor and
    documents it as *measured* — but it was measured on `bin/`, not on
    `tests/`, so the three 3.9 cells were red by construction from the first
    run. **A conformance check set on the participants instead of the
    obligated**, which is the shape this suite catches elsewhere. #143.

    The floor is a promise in `README.md`. Raising it to fit a test would be
    changing a published promise to make a check pass, so the check changes
    instead.

    Derived from `sysconfig` when the attribute is absent: the names of the
    modules and packages in the stdlib directory, the frozen builtins, and the
    dynamically loaded extensions. Verified against `sys.stdlib_module_names`
    on 3.14 — the derivation misses eleven platform C modules
    (`_winapi`, `msvcrt`, `_tkinter` …) and **none of the 53 modules this
    repository imports.**
    """
    names = set(getattr(sys, "stdlib_module_names", ()))
    if names:
        return names
    import glob as _glob
    import sysconfig
    names = set(sys.builtin_module_names)
    std = sysconfig.get_path("stdlib")
    for path in _glob.glob(os.path.join(std, "*.py")):
        names.add(os.path.basename(path)[:-3])
    for path in _glob.glob(os.path.join(std, "*", "__init__.py")):
        names.add(os.path.basename(os.path.dirname(path)))
    # **C extensions live in two different places.** POSIX puts them in
    # `lib-dynload/*.so`; Windows puts them in `<base_prefix>/DLLs/*.pyd`.
    # Scanning only the first left `unicodedata` outside the set and turned
    # `windows-latest · python 3.9` red while the other eight cells were
    # green — the derivation was written and checked on one platform.
    for ext_dir in (os.path.join(sysconfig.get_path("platstdlib"),
                                 "lib-dynload"),
                    os.path.join(sys.base_prefix, "DLLs"),
                    os.path.join(sys.base_prefix, "lib", "lib-dynload")):
        for path in _glob.glob(os.path.join(ext_dir, "*")):
            names.add(os.path.basename(path).split(".")[0])
    return names


class NoDependencies(unittest.TestCase):
    """The README promises a zero-install path. **This is what makes it true.**

    *"Every Python script in this plugin uses the standard library and nothing
    else"* is a claim about every file, so it is checked rather than asserted
    — and it is the kind of claim that rots on the first convenient `import`.
    Issue #113.
    """

    def test_nothing_outside_the_standard_library_is_imported(self):
        import ast
        import glob
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        std = _stdlib_names()
        local = {os.path.basename(f)[:-3] for f in
                 glob.glob(os.path.join(root, "skills", "job-scan",
                                        "scripts", "*.py"))}
        offenders = {}
        files = (glob.glob(os.path.join(root, "skills", "**", "*.py"),
                           recursive=True)
                 + glob.glob(os.path.join(root, "bin", "*.py"))
                 + glob.glob(os.path.join(root, "tests", "*.py")))
        for f in files:
            with open(f, encoding="utf-8") as fh:
                try:
                    tree = ast.parse(fh.read())
                except SyntaxError:
                    continue
            for node in ast.walk(tree):
                mods = []
                if isinstance(node, ast.Import):
                    mods = [a.name.split(".")[0] for a in node.names]
                elif (isinstance(node, ast.ImportFrom) and node.level == 0
                      and node.module):
                    mods = [node.module.split(".")[0]]
                for m in mods:
                    if m in std or m in local or m.startswith("_"):
                        continue
                    offenders.setdefault(m, set()).add(os.path.basename(f))
        self.assertEqual(
            offenders, {},
            f"a dependency would break the zero-install path: {offenders}")


class Locations(unittest.TestCase):
    """Folding. A regression here is invisible and falsifies every place."""

    def test_diacritics_fold(self):
        self.assertEqual(_locations.fold("Zürich"), _locations.fold("Zurich"))

    def test_case_folds(self):
        self.assertEqual(_locations.fold("GENÈVE"), _locations.fold("geneve"))

    def test_a_different_city_does_not_fold_together(self):
        self.assertNotEqual(_locations.fold("Bern"), _locations.fold("Bienne"))


class Language(unittest.TestCase):
    """It refuses to guess a translation, on purpose. Issue #70."""

    def test_an_unmeasured_market_says_nothing(self):
        self.assertIsNone(_language.language_note("developer", "ZZ", ("fr",)))


class Match(unittest.TestCase):
    """A board's reported count is not a match count. Issue #62."""

    def test_only_a_card_naming_both_is_an_assertion(self):
        # `literal` is the only verdict; the others are questions, and the
        # docstring says so. A test that treated them as booleans would have
        # asserted the opposite of what this module promises.
        verdict, reason = _match.classify("Senior PHP Developer", "Genève",
                                          "PHP", "Genève")
        self.assertEqual(verdict, "literal")
        self.assertIsNone(reason)

    def test_a_wrong_place_is_a_question_and_names_it(self):
        verdict, reason = _match.classify("Senior PHP Developer", "Lyon",
                                          "PHP", "Genève")
        self.assertEqual(verdict, "regional?")
        self.assertIn("Genève", reason)

    def test_a_wrong_trade_is_a_question_and_names_it(self):
        verdict, reason = _match.classify("Chef de rang", "Genève", "PHP",
                                          "Genève")
        self.assertEqual(verdict, "semantic?")
        self.assertIn("php", reason.lower())

    def test_flatten_pads_so_a_term_is_not_a_prefix(self):
        # ` php ` must not match `phpstorm`, or every card becomes a match.
        self.assertIn(" php ", _match.flatten("A PHP role"))
        self.assertNotIn(" php ", _match.flatten("phpstorm licences"))

    def test_matches_city_folds_diacritics(self):
        self.assertTrue(_match.matches_city("Genève, Suisse", "Geneve"))

    def test_share_reports_both_numbers(self):
        """**This test used to feed `share()` booleans.** `classify()` returns
        `literal` / `regional?` / `semantic?`, so `{"match": True}` is a row no
        adapter ever produces — and the sentence came out *"3 of 3 rows (100%)
        did not literally match — 2 True, 1 False"*, which the assertions
        `assertIn("3")` and `assertIn("2")` accepted. A loose assertion over
        the wrong vocabulary passes for the wrong reason."""
        said = _match.share([{"match": "literal"}, {"match": "regional?"},
                             {"match": "literal"}])
        self.assertIn("1 of 3 rows (33%)", said)
        self.assertIn("2 literal, 1 regional?", said)

    def test_share_says_nothing_when_every_row_matched(self):
        """**The behaviour that matters, and nothing covered it** — because
        the old row shape could never produce it: with booleans, `literal` is
        always 0 and the silent branch is unreachable."""
        self.assertIsNone(_match.share([{"match": "literal"},
                                        {"match": "literal"}]))

    def test_share_says_nothing_about_nothing(self):
        self.assertIsNone(_match.share([]))


def _load_render_plain():
    """The module's file name has a hyphen, so it cannot be imported by name."""
    path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "skills", "cover-letter", "render-plain.py")
    spec = importlib.util.spec_from_file_location("render_plain", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


rp = _load_render_plain()


class RenderPlain(unittest.TestCase):
    """The no-LaTeX route: what it keeps, and what it must say it lost.

    **The point of these is the loss, not the rendering.** A PDF that came out
    beautiful and dropped the euro sign from a salary line is the failure; a
    PDF that says which characters it could not print is not.
    """

    def test_typographic_variants_are_substituted_not_dropped(self):
        text, dropped = rp.to_winansi("−15 % ≈ 40 k€ …")
        self.assertEqual(text, "-15 % ~ 40 k€ ...")
        self.assertEqual(dropped, {})

    def test_french_accents_and_guillemets_survive(self):
        text, dropped = rp.to_winansi("Élodie Müller — « à Genève », coût")
        self.assertEqual(text, "Élodie Müller — « à Genève », coût")
        self.assertEqual(dropped, {})

    def test_a_character_with_no_glyph_is_named_never_a_question_mark(self):
        text, dropped = rp.to_winansi("Ωmega")
        self.assertNotIn("?", text)
        self.assertEqual(text, "mega")
        self.assertIn("Ω", dropped)
        self.assertEqual(dropped["Ω"][0], "GREEK CAPITAL LETTER OMEGA")

    def test_the_count_is_per_occurrence(self):
        _text, dropped = rp.to_winansi("中中中")
        self.assertEqual(dropped["中"][1], 3)

    def test_the_pdf_declares_winansi_and_carries_no_image(self):
        pdf, pages, dropped = rp.build("# Title\n\n- Coût : 40 k€\n")
        self.assertTrue(pdf.startswith(b"%PDF-1.4"))
        self.assertEqual(pages, 1)
        self.assertEqual(dropped, {})
        self.assertIn(b"/WinAnsiEncoding", pdf)
        self.assertIn(b"/BaseFont /Helvetica", pdf)
        # The ATS properties, asserted rather than described: no image, no
        # form XObject, and a page tree of exactly one column of text.
        self.assertNotIn(b"/Image", pdf)
        self.assertNotIn(b"/XObject", pdf)
        self.assertIn(b"startxref", pdf)

    def test_headings_bullets_and_emphasis_reach_the_line_list(self):
        lines = rp.lines_of("# N\n\n## Sec\n\n### Role\n\n- **a** *b*\n",
                            "resume")
        self.assertIn(("t", "N"), lines)
        self.assertIn(("h", "SEC"), lines)
        self.assertIn(("sh", "Role"), lines)
        self.assertIn(("li", "• a b"), lines)

    def test_a_letter_keeps_its_heading_case(self):
        self.assertIn(("h", "Objet"), rp.lines_of("## Objet\n", "letter"))

    def test_wrap_never_exceeds_the_width_it_was_given(self):
        for line in rp.wrap("alpha beta gamma delta epsilon zeta", 12):
            self.assertLessEqual(len(line), 12)


class WhichStatusMeansWhat(unittest.TestCase):
    """**Nothing pinned the status tables, so either could shrink in
    silence.**

    Reducing `(401, 403, 429, 451)` to `(403,)` left the suite green, and so
    did reducing `(404, 410)` to `(404,)` — every case exercised 403 and 404
    and no other member of either set. **A table tested through one of its
    entries is a table with one entry, as far as the suite is concerned.**

    It matters because the two classes lead to opposite conduct. An `absent`
    is knowledge — no file, therefore no rules, therefore an open door. A
    `refused` stops this module cold. **A status sliding from one set to the
    other moves a host between those two**, and after the 2026-09-04 decision
    the door is genuinely open on the permissive side.
    """

    def _verdict(self, code):
        import _robots
        real = _robots.urllib.request.urlopen
        _robots._CACHE.clear()
        _robots._ALIAS.clear()
        back = _robots._BACKOFF
        _robots._BACKOFF = (0, 0)

        def fail(*a, **k):
            raise _robots.urllib.error.HTTPError(
                "https://h.example/robots.txt", code, "x", {},
                io.BytesIO(b""))

        _robots.urllib.request.urlopen = fail
        try:
            return _robots.verdict("h.example")
        finally:
            _robots.urllib.request.urlopen = real
            _robots._BACKOFF = back
            _robots._CACHE.clear()
            _robots._ALIAS.clear()

    def test_every_refusing_status_refuses(self):
        """401, 429 and 451 are not decoration: a host that rate-limits or
        answers *unavailable for legal reasons* **answered**, and it did not
        answer yes."""
        for code in (401, 403, 429, 451):
            with self.subTest(code=code):
                v = self._verdict(code)
                self.assertEqual(v["state"], "refused",
                                 f"HTTP {code} is no longer a refusal")
                self.assertIsNot(v["sweep"], True)

    def test_every_absent_status_is_an_absence(self):
        """**410 is a stronger 404**, not a weaker one — the host says the
        file was here and is deliberately gone."""
        for code in (404, 410):
            with self.subTest(code=code):
                v = self._verdict(code)
                self.assertEqual(v["state"], "absent",
                                 f"HTTP {code} is no longer an absence")

    def test_the_two_sets_do_not_overlap(self):
        """A status in both would make the verdict depend on branch order."""
        import re
        src = open(os.path.join(SCRIPTS, "_robots.py"), encoding="utf-8").read()
        got = re.findall(r"e\.code in \(([0-9, ]+)\)", src)
        self.assertGreaterEqual(len(got), 2, "the status tables moved")
        sets = [set(int(x) for x in g.replace(" ", "").split(",") if x)
                for g in got[:2]]
        self.assertEqual(sets[0] & sets[1], set(),
                         "a status is in both the absent and refusing sets")


class RobotsThirdState(unittest.TestCase):
    """A failure to read must never come back as a permission. Issue #118.

    **This is the case the module got wrong for its whole life**, so every
    branch of it is pinned here: `nea.gov.kh` closes everything to `ClaudeBot`
    by name, and a timed-out request used to return `allowed: True`.
    """

    def setUp(self):
        self._real = _robots._fetch
        _robots._CACHE.clear()
        _robots._ALIAS.clear()

    def tearDown(self):
        _robots._fetch = self._real
        _robots._CACHE.clear()
        _robots._ALIAS.clear()

    def _serve(self, result):
        _robots._fetch = lambda host: dict(result, final=host, attempts=1)

    def test_a_failed_fetch_is_never_a_permission(self):
        self._serve({"state": "unreachable", "why": "timed out"})
        v = _robots.verdict("nea.gov.kh")
        self.assertIsNone(v["sweep"])
        self.assertFalse(v["certain"])
        self.assertIsNone(_robots.allowed("nea.gov.kh", "/jobs")["allowed"])

    def test_the_unknown_is_falsy_so_a_naive_caller_fails_closed(self):
        """**The whole design rests on this.** Thirty-six adapters write
        `if not v["sweep"]: die(...)` and none of them had heard of a third
        state; `None` makes both naive readings the safe one."""
        self._serve({"state": "unreachable", "why": "timed out"})
        v = _robots.verdict("example.invalid")
        self.assertFalse(v["sweep"])          # `if not v["sweep"]` refuses
        self.assertFalse(bool(v["sweep"]))    # `if v["sweep"]` does not fetch

    def test_a_403_is_a_refusal_not_an_absence(self):
        self._serve({"state": "refused",
                     "why": "HTTP 403 — the host refuses to serve its rules "
                            "file"})
        v = _robots.verdict("barbadosjobregister.gov.bb")
        self.assertIs(v["sweep"], False)
        self.assertIn("the reply was no", v["reason"])
        self.assertIs(
            _robots.allowed("barbadosjobregister.gov.bb", "/x")["allowed"],
            False)

    def test_a_404_is_still_a_permission_because_it_is_knowledge(self):
        """**The one silence that really is one.** Confusing the two
        directions is how this defect started: the fix must not invent a
        refusal out of a host that published nothing."""
        self._serve({"state": "absent", "why": "HTTP 404"})
        v = _robots.verdict("philjobnet.gov.ph")
        self.assertIs(v["sweep"], True)
        self.assertTrue(v["certain"])
        self.assertIs(_robots.allowed("philjobnet.gov.ph", "/x")["allowed"],
                      True)

    def test_a_body_that_is_not_a_rules_file_permits_but_is_not_certain(self):
        self._serve({"state": "unreadable", "why": "Content-Type 'text/html'"})
        v = _robots.verdict("my.indeed.com")
        self.assertIs(v["sweep"], True)
        self.assertFalse(v["certain"])

    def test_an_unknown_is_not_cached_a_transient_must_not_poison_a_run(self):
        self._serve({"state": "unreachable", "why": "timed out"})
        _robots.verdict("flaky.example")
        self.assertNotIn("flaky.example", _robots._CACHE)
        self._serve({"state": "read", "body": "User-agent: *\nAllow: /\n"})
        self.assertIs(_robots.verdict("flaky.example")["sweep"], True)

    def test_a_named_refusal_still_wins_when_the_file_arrives(self):
        """`nea.gov.kh`'s actual file, trimmed. The verdict it should always
        have given, and does whenever the fetch succeeds."""
        self._serve({"state": "read", "body":
                     "User-agent: *\nAllow: /\n\n"
                     "User-agent: ClaudeBot\nDisallow: /\n"})
        v = _robots.verdict("nea.gov.kh")
        self.assertIs(v["sweep"], False)
        self.assertEqual(v["group"], "claudebot")


class RobotsRetry(unittest.TestCase):
    """**Only an unknown is worth asking twice.** A slow host used to be a
    permissive host; a host that has already answered is not asked again."""

    def test_the_ladder_keeps_more_than_one_rung(self):
        """**The population this class stands on, which nothing asserted.**
        Cutting `_TIMEOUTS` from three rungs to one left every case here green
        — they pin *that* a retry happens and *when*, never *how many times*.

        It matters in one direction only, and that direction is the module's
        whole subject: **fewer attempts means more hosts filed `unreachable`**,
        which stops the sweep. That errs safe and it errs silently, and on this
        module every silent change has cost something.
        """
        self.assertGreaterEqual(len(_robots._TIMEOUTS), 3,
                                "the retry ladder lost a rung without any "
                                "case noticing")
        self.assertEqual(len(_robots._BACKOFF), len(_robots._TIMEOUTS) - 1,
                         "there must be one wait between each pair of "
                         "attempts, no more and no fewer")
        self.assertEqual(sorted(_robots._TIMEOUTS), list(_robots._TIMEOUTS),
                         "the timeouts no longer increase — a retry that "
                         "waits less than the attempt before it is not a "
                         "second chance")

    def setUp(self):
        self._real = _robots._fetch_once
        # The backoff is real seconds on a real sweep and nothing here is
        # testing the clock; a suite that sleeps five seconds gets run less.
        self._sleep = _robots.time.sleep
        _robots.time.sleep = lambda _s: None
        self.calls = []

    def tearDown(self):
        _robots._fetch_once = self._real
        _robots.time.sleep = self._sleep

    def _answer(self, state):
        def fake(url, host, timeout):
            self.calls.append(timeout)
            return {"state": state, "why": "x", "final": host}
        _robots._fetch_once = fake

    def test_an_unreachable_host_is_retried_with_widening_timeouts(self):
        self._answer("unreachable")
        got = _robots._fetch("slow.example")
        self.assertEqual(self.calls, list(_robots._TIMEOUTS))
        self.assertEqual(got["attempts"], len(_robots._TIMEOUTS))

    def test_an_answer_is_not_repeated(self):
        for state in ("read", "absent", "refused", "unreadable"):
            with self.subTest(state=state):
                self.calls = []
                self._answer(state)
                got = _robots._fetch("x.example")
                self.assertEqual(len(self.calls), 1)
                self.assertEqual(got["attempts"], 1)


class RobotsThreeFormulations(unittest.TestCase):
    """Named and refused, named and permitted, not named. Issue #117.

    **The middle one had no words at all** — `reason` stayed `None`, which is
    what a file that says nothing about us also produces. They are different
    facts and the sentence has to say which one this is.
    """

    def setUp(self):
        _robots._CACHE.clear()
        _robots._ALIAS.clear()
        self._real = _robots._fetch

    def tearDown(self):
        _robots._fetch = self._real
        _robots._CACHE.clear()
        _robots._ALIAS.clear()

    def _body(self, body):
        _robots._fetch = lambda host: {"state": "read", "body": body,
                                       "final": host, "attempts": 1}

    def test_named_and_permitted_says_so_and_says_why_star_does_not_bind(self):
        # taleez.com's shape: `*` refuses a dozen paths, our token is granted
        # everything by name.
        self._body("User-agent: *\nDisallow: /api/\nDisallow: /u/\n\n"
                   "User-agent: ClaudeBot\nAllow: /\n")
        v = _robots.verdict("taleez.com")
        self.assertIs(v["sweep"], True)
        self.assertIn("names this project and permits it", v["reason"])
        self.assertIn("do not bind us", v["reason"])

    def test_named_and_refused_says_the_refusal_is_aimed_at_us(self):
        self._body("User-agent: *\nAllow: /\n\n"
                   "User-agent: ClaudeBot\nDisallow: /\n")
        v = _robots.verdict("nea.gov.kh")
        self.assertIs(v["sweep"], False)
        self.assertIn("names this project", v["reason"])

    def test_not_named_says_the_policy_is_general(self):
        self._body("User-agent: *\nDisallow: /\n")
        v = _robots.verdict("plain.example")
        self.assertIs(v["sweep"], False)
        self.assertIn("evenly", v["reason"])
        self.assertEqual(v["groups"], [])

    def test_records_that_disagree_are_reported_not_smoothed_over(self):
        self._body("User-agent: ClaudeBot\nDisallow: /\n\n"
                   "User-agent: Claude-SearchBot\nAllow: /\n")
        v = _robots.verdict("www.linkedin.com")
        self.assertIs(v["sweep"], False)
        self.assertTrue(v["group_conflict"])
        self.assertIn("does not answer them alike", v["reason"])

    def test_records_that_agree_say_so_without_alarm(self):
        self._body("User-agent: ClaudeBot\nAllow: /\n\n"
                   "User-agent: Claude-Web\nAllow: /\n")
        v = _robots.verdict("taleez.com")
        self.assertFalse(v["group_conflict"])
        self.assertIn("says the same thing to each", v["reason"])

    def test_a_path_with_no_matching_rule_names_the_group_it_checked(self):
        self._body("User-agent: *\nDisallow: /api/\n\n"
                   "User-agent: ClaudeBot\nAllow: /\n")
        a = _robots.allowed("taleez.com", "/api/x")
        # Correct per RFC 9309 — a record naming us replaces `*` — and the
        # reason has to say that, because it looks wrong at a glance.
        self.assertIs(a["allowed"], True)
        self.assertIn("names this project", a["reason"])


class Decode(unittest.TestCase):
    """Read the declared charset. Issue #115.

    **`decode("utf-8", "replace")` cannot fail**, which is the whole problem:
    it returns plausible text with holes in it and nothing raises.
    """

    class _Headers(dict):
        def get_content_charset(self):
            ct = self.get("Content-Type", "")
            import re as _re
            m = _re.search(r"charset=([\w\-]+)", ct)
            return m.group(1).lower() if m else None

    def test_the_header_is_believed_first(self):
        h = self._Headers({"Content-Type": "text/html;charset=ISO-8859-1"})
        text, enc = _decode.decode_body(b"Pudahuel \xa1Comisiones", h)
        self.assertEqual(text, "Pudahuel ¡Comisiones")
        self.assertEqual(enc, "iso-8859-1")

    def test_utf8_replace_is_what_this_replaces(self):
        """The `bne.gob.cl` bytes, and the two readings side by side."""
        raw = b"Pudahuel \xa1Comisiones"
        self.assertIn("\ufffd", raw.decode("utf-8", "replace"))
        self.assertNotIn("\ufffd", raw.decode("cp1252"))

    def test_a_meta_charset_is_read_when_the_header_is_silent(self):
        raw = b'<html><head><meta charset="windows-1252"><body>caf\xe9'
        name, where = _decode.charset_of(None, raw)
        self.assertEqual((name, where), ("windows-1252", "meta"))

    def test_an_xml_prolog_counts_as_a_declaration(self):
        """**Sitemaps declare here and nowhere else**, and this repository
        reads a sitemap on nearly every board. Issue #115."""
        raw = b'<?xml version="1.0" encoding="ISO-8859-1"?><loc>caf\xe9</loc>'
        self.assertEqual(_decode.charset_of(None, raw), ("iso-8859-1", "xml"))
        self.assertTrue(_decode.decode_body(raw)[0].endswith(
            "<loc>café</loc>"))

    def test_a_prolog_must_be_first_a_mention_later_is_not_a_declaration(self):
        raw = b'<urlset><note><?xml encoding="ISO-8859-1"?></note></urlset>'
        self.assertEqual(_decode.charset_of(None, raw), (None, None))

    def test_strict_first_then_a_total_fallback_and_it_says_which(self):
        # Not valid UTF-8 and nothing declared: cp1252 maps every byte, so it
        # is chosen for being total rather than for being right — and the
        # second value is how the caller learns that.
        text, enc = _decode.decode_body(b"caf\xe9 \x93x\x94")
        self.assertEqual(enc, "cp1252")
        self.assertNotIn("\ufffd", text)

    def test_valid_utf8_stays_utf8_when_nothing_is_declared(self):
        text, enc = _decode.decode_body("café €".encode("utf-8"))
        self.assertEqual((text, enc), ("café €", "utf-8"))

    def test_a_string_passes_through_and_says_so(self):
        self.assertEqual(_decode.decode_body("already text"),
                         ("already text", "str"))

    def test_an_unknown_charset_name_falls_through_instead_of_raising(self):
        h = self._Headers({"Content-Type": "text/html;charset=x-nonesuch"})
        text, enc = _decode.decode_body("café".encode("utf-8"), h)
        self.assertEqual((text, enc), ("café", "utf-8"))


class RobotsStorage403(unittest.TestCase):
    """A 403 that carries an object-storage error document. Issue #118.

    **The hint is allowed; the conclusion is not.** On S3 a missing key
    answers 403 because listing is not granted, so a static site with no
    robots.txt can answer 403 where the identical site with a custom error
    page answers 200 — measured on two Chilean government portals.
    """

    class _Err:
        def __init__(self, body):
            self._body = body

        def read(self, n=None):
            return self._body[:n] if n else self._body

    def test_an_s3_error_document_is_named_as_a_hint(self):
        note = _robots._storage_note(self._Err(
            b'<?xml version="1.0"?><Error><Code>AccessDenied</Code></Error>'))
        self.assertIn("object-storage error document", note)
        self.assertIn("hint, not a finding", note)

    def test_a_firewall_page_gets_no_such_note(self):
        note = _robots._storage_note(
            self._Err(b"Request is Blocked by Firewall"))
        self.assertEqual(note, "")

    def test_a_body_that_cannot_be_read_tells_us_nothing(self):
        class Broken:
            def read(self, n=None):
                raise OSError("connection reset")
        self.assertEqual(_robots._storage_note(Broken()), "")

    def test_the_hint_never_turns_the_refusal_into_a_permission(self):
        _robots._CACHE.clear()
        _robots._ALIAS.clear()
        real = _robots._fetch
        _robots._fetch = lambda host: {
            "state": "refused", "final": host, "attempts": 1,
            "why": "HTTP 403 — the host refuses to serve its rules file. "
                   "**The body is an object-storage error document**"}
        try:
            v = _robots.verdict("www.trabajaenelestado.cl")
            self.assertIs(v["sweep"], False)
        finally:
            _robots._fetch = real
            _robots._CACHE.clear()
            _robots._ALIAS.clear()


def guard_is_last(source):
    """`(ok, classes_after)` — is the `__main__` guard the last statement?

    **A free function so it can be tested on sources other than this file.**
    The first attempt asserted the property only about `test_core.py` itself,
    and the negative check — appending a class to a copy in a temp directory —
    came back red for an import error rather than for the defect. **A check
    whose failure is indistinguishable from an unrelated failure has not been
    verified**, and it nearly went in as verified.
    """
    import ast
    tree = ast.parse(source)
    if not tree.body:
        return False, []
    last = tree.body[-1]
    is_guard = (isinstance(last, ast.If) and any(
        isinstance(n, ast.Name) and n.id == "__name__"
        for n in ast.walk(last.test)))
    idx = next((i for i, n in enumerate(tree.body)
                if isinstance(n, ast.If) and any(
                    isinstance(x, ast.Name) and x.id == "__name__"
                    for x in ast.walk(n.test))), None)
    after = ([n.name for n in tree.body[idx + 1:] if isinstance(n, ast.ClassDef)]
             if idx is not None else [])
    return is_guard, after


class SuiteRuns(unittest.TestCase):
    """**A green run that covered 59% of the suite.** Found by the test audit.

    `python3 tests/test_core.py` ran **51 of 87** cases and printed OK: the
    `if __name__ == "__main__"` block had drifted into the middle of the file,
    so every class appended after it was defined only *after*
    `unittest.main()` had already run and exited. The documented invocation
    (`python3 -m unittest discover`) was unaffected, which is exactly why
    nothing showed. **A clean run is not a clean state.**
    """

    GOOD = ('import unittest\n\n\nclass A(unittest.TestCase):\n'
            '    def test_x(self):\n        pass\n\n\n'
            'if __name__ == "__main__":\n    unittest.main()\n')
    BROKEN = GOOD + '\n\nclass B(unittest.TestCase):\n    pass\n'

    def test_the_check_accepts_a_well_formed_file(self):
        self.assertEqual(guard_is_last(self.GOOD), (True, []))

    def test_the_check_rejects_a_class_appended_after_the_guard(self):
        """**The negative case, on a source built for it** — not on a copy of
        this file in a temp directory, where a red result means the imports
        failed."""
        ok, after = guard_is_last(self.BROKEN)
        self.assertFalse(ok)
        self.assertEqual(after, ["B"])

    def test_this_file_puts_its_guard_last(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "test_core.py")
        ok, after = guard_is_last(open(path, encoding="utf-8").read())
        self.assertTrue(ok, "the `__main__` guard is not the last statement: "
                             "anything after it is invisible to `python3 "
                             "tests/test_core.py`, which will still print OK")
        self.assertEqual(after, [])


# **A date, optionally carrying a time.** This pattern required a bare
# `YYYY-MM-DD` until 2026-09-05, and on that day **two sessions independently
# wrote a UTC timestamp into it within hours of each other** — `keejob.md` in
# the morning, three Zambian cards at midday. Two people reaching for the same
# "wrong" form is evidence about the format, not about them: a timestamp is
# strictly more information than a date, and the field exists so that a claim
# carries when it was true.
#
# **So the guard widens rather than the cards being forced.** It still refuses
# a value with no date in it at all, which is the thing it was written to
# catch. The two directions are tested.
DATE_OR_INSTANT = r"\d{4}-\d{2}-\d{2}(?:[T ][0-9:]{4,8}\s*(?:Z|UTC)?)?"


SCRIPTS = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "skills", "job-scan", "scripts")


class SalaryCarriesItsUnit(unittest.TestCase):
    """**A number in an unknown unit is worse than a number absent, because it
    compares.** `shared/plausible-and-false.md`, mechanism 1.

    Found by auditing the fields adapters trust, after `mihnati.com` published
    `baseSalary.currency: "PKR"` on Saudi jobs. Two ways of losing the unit
    turned up, neither of which involves a board lying:

    **Descending past it.** In schema.org's `MonetaryAmount`, `currency` is a
    **sibling** of `value`, not a child — so `one(jp["baseSalary"])["value"]`,
    the shape eight adapters use to reach `minValue`, walks straight past it.
    `batiactu.py` did, and a ledger got `42000.00` with no unit while the page
    published `{"currency": "EUR", "value": {"minValue": "42000.00", ...}}`.

    **Knowing it too well to write it down.** Three single-country boards
    omitted the currency because it was obvious to whoever wrote the adapter,
    and absent from the row a ledger keeps. `adzuna.py` was the sharp case:
    **nineteen country indexes through one code path, and no currency field
    anywhere in the API's response**, so `salary_min: 90000` was CHF, GBP,
    BRL or ZAR depending on a flag.
    """

    def _emitters(self):
        import glob
        out = []
        for path in sorted(glob.glob(os.path.join(SCRIPTS, "*.py"))):
            name = os.path.basename(path)
            if name.startswith("_"):
                continue
            src = open(path, encoding="utf-8").read()
            if re.search(r'"salary_(?:min|max)[a-z_]*"', src):
                out.append((name, src))
        return out

    def test_there_are_numeric_salary_emitters_to_check(self):
        """**A guard that checks nothing passes.** If these field names ever
        change, this fails first and says so, instead of the check below
        quietly succeeding over an empty list."""
        self.assertGreater(len(self._emitters()), 10)

    def test_every_numeric_salary_emitter_names_its_currency(self):
        missing = [name for name, src in self._emitters()
                   if not re.search(r'"[a-z_]*currency[a-z_]*"', src)]
        self.assertEqual(
            missing, [],
            "these emit a salary figure with no field naming its unit: "
            + ", ".join(missing))

    def test_adzunas_table_covers_every_index_it_serves(self):
        """Nineteen countries, one code path. **A country added without a
        currency would emit bare numbers again**, which is how this started."""
        sys.path.insert(0, SCRIPTS)
        import adzuna
        self.assertEqual(sorted(adzuna.INDEX_CURRENCY),
                         sorted(adzuna.COUNTRIES))
        self.assertTrue(all(len(v) == 3 and v.isupper()
                            for v in adzuna.INDEX_CURRENCY.values()))


class UrlWithoutAScheme(unittest.TestCase):
    """`urlparse("www.jobs.ch/x").netloc` is `""`. Found on job-room.

    **A general trap, not a job-room quirk**, which is why it is pinned here
    rather than described in a card. job-room sends `externalUrl` in two
    shapes — measured on 300 Vaud cards, 2026-09-03: **100 with a scheme, 193
    without** — and two fields read the host off it. Both went quiet rather
    than wrong:

    - `external_host` was `""` on 193 of 300, so a count of origins made on it
      reported `www.jobs.ch` **once** where the sample holds **194**. Three
      published figures came from that.
    - `duplicate_of` was `None` on all 193 — **the advertisement already swept
      under a jobs.ch id was recorded again as new.** Filled on 90 of 300
      before, 283 of 300 after.

    **The empty string did not say "I do not know", it said "no external
    host"** — the third missing third value in this repository in one day,
    after `allowed` and the three HTTP outcomes.
    """

    def setUp(self):
        sys.path.insert(0, SCRIPTS)
        import jobroom
        self.jobroom = jobroom

    def test_a_bare_host_gets_the_scheme_it_needs(self):
        self.assertEqual(
            self.jobroom.with_scheme("www.jobs.ch/de/stellenangebote/detail/x/"),
            "https://www.jobs.ch/de/stellenangebote/detail/x/")

    def test_a_url_that_has_one_is_untouched(self):
        for url in ("https://www.jobup.ch/fr/emplois/detail/x/",
                    "http://example.com/a"):
            self.assertEqual(self.jobroom.with_scheme(url), url)

    def test_a_path_is_not_a_host(self):
        """**A leading slash or a dotless first segment is a path.** Turning
        `/jobs/1` into `https:///jobs/1` would invent a host."""
        self.assertEqual(self.jobroom.with_scheme("/jobs/1"), "/jobs/1")
        self.assertEqual(self.jobroom.with_scheme("jobs/1"), "jobs/1")
        self.assertIsNone(self.jobroom.with_scheme(""))
        self.assertIsNone(self.jobroom.with_scheme(None))

    def test_the_host_is_readable_from_a_scheme_less_url(self):
        """The assertion that fails without the fix, on the exact shape the
        board sends."""
        import urllib.parse
        bare = "www.jobs.ch/de/stellenangebote/detail/fdb4a6bd/"
        self.assertEqual(urllib.parse.urlparse(bare).netloc, "",
                         "if this ever stops being empty the trap is gone")
        self.assertEqual(
            urllib.parse.urlparse(self.jobroom.with_scheme(bare)).netloc,
            "www.jobs.ch")

    def test_duplicate_of_sees_a_scheme_less_advertisement(self):
        """The consequence that costs a ledger row, not a statistic."""
        # A **whole** UUID: `UUID_RE` wants all five groups, and the first
        # draft of this case truncated it — the test failed for its own
        # fixture rather than for the defect, which is the shape of vacuous
        # negative this suite already carries a lesson about.
        bare = ("www.jobs.ch/de/stellenangebote/detail/"
                "fdb4a6bd-97c7-4ff0-97d3-0d2cb63f9153/")
        self.assertEqual(self.jobroom.duplicate_of(bare),
                         "jobs.ch:fdb4a6bd-97c7-4ff0-97d3-0d2cb63f9153")
        self.assertEqual(self.jobroom.duplicate_of(bare),
                         self.jobroom.duplicate_of("https://" + bare))

    def test_clean_url_and_the_host_agree_about_the_same_url(self):
        """**Two functions normalising the same thing differently is how this
        survived.** They share one normaliser now."""
        bare = "www.jobs.ch/de/x/?utm_source=jobroom"
        import urllib.parse
        cleaned = self.jobroom.clean_url(bare)
        self.assertEqual(cleaned, "https://www.jobs.ch/de/x/")
        self.assertEqual(urllib.parse.urlparse(cleaned).netloc,
                         urllib.parse.urlparse(
                             self.jobroom.with_scheme(bare)).netloc)


class ChildProcessesAreChecked(unittest.TestCase):
    """`subprocess.run` does not raise on a non-zero exit. Issue #123.

    **Two adapters shelled out to `hiringcafe.py`; one checked and one did
    not.** The one that did carried the reason in its own message — *an empty
    tenant list from a failed sweep would read exactly like a provider nobody
    uses* — and `recruitee.py` did not have it. On 2026-09-03, the day
    `hiringcafe.py search` began refusing by design, it printed **"0 tenants
    seen in HiringCafe's GB cards"** and exited 0: **a refusal presented as a
    measurement.**

    `capture_output=True` and then reading only `.stdout` is the whole
    defect. The child's diagnosis goes to `.stderr`, which nobody read, and an
    empty `.stdout` parses to an empty result perfectly well.

    **This is not a third point fix.** A fourth caller written next month
    would repeat it, so the check is here rather than in a card.
    """

    def _callers(self):
        import glob
        out = []
        for path in sorted(glob.glob(os.path.join(SCRIPTS, "*.py"))
                           + glob.glob(os.path.join(
                               os.path.dirname(SCRIPTS.rstrip("/")), "*.py"))):
            src = open(path, encoding="utf-8").read()
            if "subprocess.run(" in src:
                out.append((os.path.basename(path), src))
        return out

    def test_there_are_callers_to_check(self):
        """**A guard over an empty list passes.** If the shape ever changes
        this fails first instead of the check below succeeding vacuously."""
        self.assertGreater(len(self._callers()), 0)

    def test_every_subprocess_caller_reads_the_exit_code(self):
        missing = [name for name, src in self._callers()
                   if "returncode" not in src]
        self.assertEqual(
            missing, [],
            "these run a child process and never look at its exit code, so a "
            "child that refused or crashed yields an empty result that reads "
            "like a real absence: " + ", ".join(missing))

    def test_the_helper_passes_a_refusal_upward_unchanged(self):
        """7 and 8 mean something to a caller. **Flattening them into a
        generic failure loses the one distinction the guard draws.**"""
        sys.path.insert(0, SCRIPTS)
        import _child
        self.assertIn(7, _child.MEANINGFUL)
        self.assertIn(8, _child.MEANINGFUL)

        seen = {}

        def fake_die(msg, code=2):
            seen["msg"], seen["code"] = msg, code
            raise SystemExit(code)

        for child_code, expected in ((7, 7), (8, 8), (3, 2), (1, 2)):
            seen.clear()
            real = _child.subprocess.run
            _child.subprocess.run = lambda *a, **k: type(
                "R", (), {"returncode": child_code, "stdout": "",
                          "stderr": "the child's own words"})()
            try:
                with self.assertRaises(SystemExit):
                    _child.run(["x"], fake_die, "child.py")
            finally:
                _child.subprocess.run = real
            self.assertEqual(seen["code"], expected,
                             f"child exited {child_code}")
            self.assertIn("the child's own words", seen["msg"])


class HiringCafeIsBuiltInOnePlace(unittest.TestCase):
    """Three commands built the same refused URL, each with its own client.

    `hiringcafe.com/robots.txt` refuses `/*?searchState=*` to `User-agent: *`.
    **#123 named `hiringcafe.py:119`; `ats.py` and `workday.py` were building
    it too**, found by grepping for the URL rather than for the file — and two
    further adapters inherit it by running `hiringcafe.py search`.

    **The same shape as `jobroom.py`'s three URL parsers, fixed the same
    evening**: several places doing one thing slightly differently, one of
    them right by accident.
    """

    def test_no_adapter_assembles_the_refused_url_itself(self):
        import glob
        offenders = []
        for path in sorted(glob.glob(os.path.join(SCRIPTS, "*.py"))):
            name = os.path.basename(path)
            if name == "_hiringcafe.py":
                continue
            src = open(path, encoding="utf-8").read()
            if re.search(r'"https://hiringcafe\.com/\?"', src):
                offenders.append(name)
        self.assertEqual(
            offenders, [],
            "these build the refused `?searchState=` URL by hand instead of "
            "going through `_hiringcafe.py`: " + ", ".join(offenders))

    def test_the_refusal_names_the_rule_and_the_open_route(self):
        sys.path.insert(0, SCRIPTS)
        import _hiringcafe
        text = _hiringcafe.refusal("test")
        self.assertIn("/*?searchState=*", text)
        self.assertIn("/job/", text)
        self.assertIn("No request was made", text)


class WhatTheStatusMeans(unittest.TestCase):
    """One case per shape, because they had been sharing a verdict. #125.

    `algerie.tanqeeb.com` answers **HTTP 202 with a zero-byte body**, and the
    guard returned `allowed: True` giving the reason *"a 404 is an absence"* —
    **a status that never occurred, quoted as the justification.**

    **A 404 says there are no rules. A 202 with an empty body says nothing.**
    Melting both into `unreadable`, and reading `unreadable` as an absence,
    gave a host that did not answer the same verdict as a host that has no
    file. The three-valued output added in #118 was right; **this branch was
    not using it.**

    And the reason mattered as much as the verdict: **a silent verdict invites
    suspicion, a falsely-motivated one reads like a verification.** Every
    reason now quotes the status and the byte count actually observed.
    """

    class _Resp:
        def __init__(self, status, body, ctype="text/plain"):
            self._s, self._b, self._c = status, body, ctype

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def getcode(self):
            return self._s

        def geturl(self):
            return "https://h.example/robots.txt"

        def read(self):
            return self._b.encode()

        @property
        def headers(self):
            return {"Content-Type": self._c}

    def _fetch_with(self, response=None, error=None):
        sys.path.insert(0, SCRIPTS)
        import _robots
        real = _robots.urllib.request.urlopen

        def fake(req, timeout=None, **kw):
            # `**kw` because `_fetch_once` now passes `context=` for the two
            # hosts that need a supplied intermediate (#104). A stub with a
            # narrower signature than the real call fails for its own shape.
            if error:
                raise error
            return response
        _robots.urllib.request.urlopen = fake
        try:
            return _robots._fetch_once("https://h.example/robots.txt",
                                       "h.example", 5)
        finally:
            _robots.urllib.request.urlopen = real

    def test_404_is_an_absence_and_an_absence_permits(self):
        import urllib.error
        got = self._fetch_with(error=urllib.error.HTTPError(
            "u", 404, "Not Found", {}, None))
        self.assertEqual(got["state"], "absent")
        self.assertIn("404", got["why"])

    def test_202_with_an_empty_body_is_an_unknown(self):
        """**The case that started this.** Not an absence: nothing was said."""
        got = self._fetch_with(self._Resp(202, "", "text/html; charset=UTF-8"))
        self.assertEqual(got["state"], "unreachable")
        self.assertEqual(got["bytes"], 0)
        self.assertIn("202", got["why"])
        self.assertIn("not an absence", got["why"])

    def test_a_500_is_an_unknown(self):
        import urllib.error
        got = self._fetch_with(error=urllib.error.HTTPError(
            "u", 500, "Server Error", {}, None))
        self.assertEqual(got["state"], "unreachable")

    def test_a_403_is_a_refusal(self):
        import urllib.error
        got = self._fetch_with(error=urllib.error.HTTPError(
            "u", 403, "Forbidden", {}, None))
        self.assertEqual(got["state"], "refused")

    def test_200_with_a_rules_file_is_read(self):
        got = self._fetch_with(self._Resp(
            200, "User-agent: *\nDisallow: /x\n"))
        self.assertEqual(got["state"], "read")
        self.assertEqual(got["status"], 200)

    def test_no_reason_cites_a_status_that_did_not_happen(self):
        """The defect in one assertion: the word `404` may appear only where
        a 404 actually occurred."""
        sys.path.insert(0, SCRIPTS)
        import _robots
        _robots._CACHE.clear()
        _robots._ALIAS.clear()
        real = _robots._fetch
        _robots._fetch = lambda host: {
            "state": "unreachable", "final": host, "attempts": 1,
            "status": 202, "bytes": 0,
            "why": "HTTP 202 with a 0-byte body"}
        try:
            a = _robots.allowed("algerie.tanqeeb.com", "/jobs")
            self.assertIsNone(a["allowed"])
            self.assertNotIn("404", a["reason"])
            self.assertIn("202", a["reason"])
        finally:
            _robots._fetch = real
            _robots._CACHE.clear()
            _robots._ALIAS.clear()


class VerificationIsNeverDisabled(unittest.TestCase):
    """Issue #104. **The boundary, pinned rather than promised.**

    `empleate.gob.es` sends its leaf and no intermediate, so every verifying
    client refuses it while browsers do not notice — they cache intermediates
    and fetch the missing one from the AIA extension. **The operator therefore
    has no symptom to fix.**

    The rule: a third party's infrastructure problem is not the plugin's to
    fix. **The exception is narrow** — when the fault is masked for web users
    and an alternative exists *that keeps verification intact*, take it.
    Supplying the missing intermediate keeps it intact entirely.

    **`verify=False` is never that alternative.** It does not fix the
    connection, it removes the check from every connection the plugin makes.
    So it is a test, not a sentence in a document.
    """

    @staticmethod
    def _code_only(src, path):
        """Source with comments and string literals removed.

        **The first draft of this scan matched `_tls.py`'s own docstring**,
        which exists to forbid the thing — a checker that reads prose about a
        ban as the ban itself. `tokenize` gives the code and nothing else.
        """
        import io
        import tokenize
        if not path.endswith(".py"):
            return "\n".join(l.split("#", 1)[0] for l in src.splitlines())
        out = []
        try:
            for tok in tokenize.generate_tokens(io.StringIO(src).readline):
                if tok.type in (tokenize.COMMENT, tokenize.STRING):
                    continue
                out.append(tok.string)
        except (tokenize.TokenError, IndentationError):
            return src
        return " ".join(out)

    def _sources(self):
        import glob
        here = os.path.dirname(os.path.abspath(__file__))
        root = os.path.dirname(here)
        out = []
        for pattern in ("skills/**/*.py", "bin/**/*.py", "bin/*.sh"):
            for path in glob.glob(os.path.join(root, pattern), recursive=True):
                rel = os.path.relpath(path, root)
                src = open(path, encoding="utf-8").read()
                out.append((rel, self._code_only(src, path)))
        return out

    def test_there_are_sources_to_scan(self):
        self.assertGreater(len(self._sources()), 30)

    def test_nothing_turns_certificate_verification_off(self):
        banned = ("CERT_NONE", "_create_unverified_context", "--insecure")
        hits = []
        for name, src in self._sources():
            for token in banned:
                if token in src:
                    hits.append(f"{name}: {token}")
            # `verify=False` and `check_hostname=False` survive tokenising as
            # three tokens, so they are matched on the token stream.
            flat = src.replace(" ", "")
            for token in ("verify=False", "check_hostname=False"):
                if token in flat:
                    hits.append(f"{name}: {token}")
        self.assertEqual(hits, [], "verification is disabled here: "
                                   + "; ".join(hits))


class EmbeddedIntermediate(unittest.TestCase):
    """It is narrow, it is read from itself, and it names its own expiry."""

    def setUp(self):
        sys.path.insert(0, SCRIPTS)
        import _tls
        self._tls = _tls

    def test_it_applies_to_two_hosts_and_no_others(self):
        """**A set, not a suffix match.** `notempleate.gob.es` must not pick
        this up, and neither must anything else."""
        self.assertIsNotNone(self._tls.context_for("empleate.gob.es"))
        self.assertIsNotNone(self._tls.context_for("www.empleate.gob.es"))
        for other in ("example.com", "notempleate.gob.es",
                      "empleate.gob.es.evil.test", "gob.es"):
            self.assertIsNone(self._tls.context_for(other), other)

    def test_the_expiry_is_read_from_the_certificate(self):
        """**Not from a constant beside it.** A second source of truth is how
        a field drifts away from what it describes."""
        end = self._tls.expires()
        self.assertGreater(end.year, 2024)
        self.assertEqual(self._tls.check()["expires"], f"{end:%Y-%m-%d}")

    def test_expiry_fails_by_name_and_never_suggests_disabling(self):
        """The day it lapses, the failure must say so — not come back as an
        opaque `CERTIFICATE_VERIFY_FAILED` and make somebody repeat the whole
        investigation. `never-fail-silently.md`."""
        import datetime
        later = self._tls.expires() + datetime.timedelta(days=1)
        with self.assertRaises(self._tls.Expired) as caught:
            self._tls.context_for("empleate.gob.es", now=later)
        text = str(caught.exception)
        self.assertIn("expired on", text)
        self.assertIn(self._tls.AIA_URL, text)
        self.assertIn("Do not disable", text)

    def test_it_is_still_valid_today(self):
        """A reminder with a date on it, rather than a surprise."""
        import datetime
        left = (self._tls.expires()
                - datetime.datetime.now(datetime.timezone.utc)).days
        self.assertGreater(left, 0, "the embedded intermediate has expired — "
                                    "see `_tls.check()` for what to do")


class AnInvocationThatCannotSucceed(unittest.TestCase):
    """`jobup.py search` accepted a call that could only return zero. #126.

    **Measured 2026-09-03**, and the numbers are the whole argument:

        /fr/emplois/                    275 kB    0 JobPosting
        /fr/emplois/?term=developpeur   534 kB   22 JobPosting
        /fr/emplois/?location=Lausanne  517 kB   22 JobPosting

    The bare listing renders client-side and carries no structured data. **A
    filterless run therefore returned zero, reliably** — and a zero from a
    board reads as a board with no jobs. It was reported as one, and an Atlas
    page was published saying the board had broken.

    Two further faults in the same command made it worse: **`--location` never
    entered the URL** (it was applied afterwards, to rows fetched from the
    *unfiltered* listing), and `drop_report` returns three values where the
    call site unpacked two — so `--location` alone raised `ValueError` after
    paying for the sweep.

    **A tool that accepts an invocation which cannot succeed manufactures
    false results.**
    """

    def setUp(self):
        sys.path.insert(0, SCRIPTS)
        import jobup
        self.jobup = jobup

    def _args(self, **kw):
        import argparse
        base = dict(site="jobup", term=None, location=None, pages=1,
                    limit=None, delay=0.0)
        base.update(kw)
        return argparse.Namespace(**base)

    def test_a_filterless_search_is_refused_before_any_request(self):
        with self.assertRaises(SystemExit) as caught:
            self.jobup.cmd_search(self._args())
        self.assertEqual(caught.exception.code, 2)

    def test_drop_report_returns_three_values(self):
        """The contract the call site got wrong. `(kept, dropped, labels)`."""
        import _locations
        got = _locations.drop_report(
            [{"location_text": "Lausanne"}, {"location_text": "Bern"}],
            "Lausanne")
        self.assertEqual(len(got), 3)
        kept, dropped, labels = got
        self.assertEqual(len(kept), 1)
        self.assertEqual(dropped, 1)
        self.assertEqual(labels, {"Bern": 1})

    def test_location_reaches_the_query_string(self):
        """It was filtered after the fetch, so the fetch was unfiltered."""
        src = open(os.path.join(SCRIPTS, "jobup.py"), encoding="utf-8").read()
        self.assertIn('q["location"] = a.location', src)

    def test_the_empty_message_names_three_causes(self):
        """Naming two of three is not a false statement, and it had the same
        effect as one: it pointed at *the board is broken*."""
        src = open(os.path.join(SCRIPTS, "jobup.py"), encoding="utf-8").read()
        i = src.index("carried no JobPosting")
        window = src[i:i + 1200]
        self.assertIn("(1)", window)
        self.assertIn("(2)", window)
        self.assertIn("(3)", window)
        # **The substance, not the tense — and not the line wrapping.**
        # This asserted the exact phrase "does not answer with structured
        # data"; it broke on "did not", which is the more accurate claim,
        # and then broke again because the phrase spans an f-string
        # continuation in the source. **A case that reads source text is
        # matching the author's line breaks, not the program's behaviour**,
        # so the continuations are stitched before matching.
        flat = re.sub(r'"\s*\n\s*f?"', "", window)
        self.assertIn("answer with structured data", flat)
        self.assertIn("measured both ways within a day", flat)


class OneDeclaredIdentity(unittest.TestCase):
    """One user-agent, in one module, imported by all of them. #120, #124.

    The repository **obeyed `Claude-User`'s rules and announced Chrome** — 63
    files carried a browser string while `_robots.OUR_AGENTS` already bound
    the guard to `claude-user`, and `job-room.md` argued its position in the
    language of that very class. Three files declared themselves honestly and
    sixty-three did not; the split is how a project comes to plead one thing
    and send another.
    """

    def setUp(self):
        sys.path.insert(0, SCRIPTS)
        import _ua
        self._ua = _ua

    def test_the_declaration_carries_the_token_and_says_what_it_is(self):
        """**Both readings must be true.** An operator matching the token in a
        robots group gets the intended behaviour; an operator reading the
        string sees a personal tool, not Anthropic's fleet — which matters,
        because `claude.com/crawling/bots.json` publishes IP prefixes for
        verification and this runs from the user's own address."""
        ua = self._ua.UA
        self.assertIn("Claude-User", ua)
        self.assertIn("claude-job-hunt", ua)
        self.assertIn("github.com/dominiquevienne/claude-job-hunt", ua)

    def test_no_adapter_declares_its_own_agent(self):
        import glob
        offenders = []
        for path in sorted(glob.glob(os.path.join(SCRIPTS, "*.py"))
                           + glob.glob(os.path.join(
                               os.path.dirname(SCRIPTS.rstrip("/")),
                               "..", "..", "bin", "*.py"))):
            name = os.path.basename(path)
            if name in ("_ua.py", "adzuna.py"):
                continue          # adzuna is keyed API access, not a crawl
            src = open(path, encoding="utf-8").read()
            if "Mozilla/5.0 (Macintosh" in src:
                offenders.append(name)
        self.assertEqual(offenders, [],
                         "these still announce a browser: "
                         + ", ".join(offenders))

    def test_the_browser_is_never_the_answer_to_a_refusal(self):
        """**The whole worth of declaring rests on this.** Declaring the token
        and then reaching for a browser at every refusal is worse than not
        declaring: it hands operators a way to recognise us and makes it
        ineffective. #124."""
        msg, code = self._ua.browser_fallback("h.example", True, 403)
        self.assertEqual(code, self._ua.EXIT_NEEDS_BROWSER)
        self.assertIn("permit", msg)
        for refused_or_unknown in (False, None):
            with self.assertRaises(ValueError):
                self._ua.browser_fallback("h.example", refused_or_unknown, 403)

    def test_a_block_says_the_declaration_might_be_why(self):
        """Measured the day it shipped: `emploi.batiactu.com` serves 289 bytes
        of `robots.txt` to a browser string and 403s ours. **A declaration can
        manufacture a refusal**, and a run that quietly returned less would
        hide it."""
        note = self._ua.blocked_note("emploi.batiactu.com", 403)
        self.assertIn("Claude-User", note)
        self.assertIn("cannot tell them apart", note)


class EveryNetworkReaderAsksOrSaysWhyNot(unittest.TestCase):
    """#100's last hole, and the answer written down rather than deduced.

    **An absent guard call is indistinguishable from a decision not to call**,
    which is exactly what went wrong with SmartRecruiters in `ats.py`: the
    exception existed nowhere, it was a silence. So the scripts that do not
    ask are listed here **with the reason**, and a script that stops asking
    without being added fails this case.

    **#100 counted ten by grepping for `robots`. That measure passes prose.**
    `arbeitsagentur.py` and `hiringcafe.py` mention the word in a docstring —
    one of them carrying *a human's one-time reading of the file*, which is
    the very practice `_robots.py` was written to replace — and neither calls
    the guard. Six network readers do not ask, not four.
    """

    # Each entry is a decision, not an oversight, and the text is the reason.
    NOT_ASKING = {
        "adzuna.py": "documented public API — and api.adzuna.com publishes "
                     "`Disallow: /`. HELD: arbitration with the user",
        "francetravail.py": "documented public API — api.francetravail.io "
                            "publishes `Disallow: /`. HELD: same arbitration",
        "labonnealternance.py": "documented public API — and "
                                "api.apprentissage.beta.gouv.fr serves 145 kB "
                                "of its own SPA as robots.txt, so the guard "
                                "reads `unrecognised`. HELD: same class",

        "arbeitsagentur.py": "documented public API — and "
                             "rest.arbeitsagentur.de answers its robots.txt "
                             "with a 1-byte 403. The docstring's human "
                             "reading was of www.arbeitsagentur.de, a "
                             "different host. HELD: same class",
        "hiringcafe.py": "refuses from the record by design (#123): a guard "
                         "call is itself a request, and collection from this "
                         "host is suspended",
    }

    def _network_readers(self):
        import glob
        out = []
        for path in sorted(glob.glob(os.path.join(SCRIPTS, "*.py"))):
            name = os.path.basename(path)
            if name.startswith("_"):
                continue
            src = open(path, encoding="utf-8").read()
            if any(t in src for t in ("urllib.request", "urlopen",
                                      "http.client")):
                out.append((name, src))
        return out

    def test_there_are_network_readers_to_check(self):
        self.assertGreater(len(self._network_readers()), 50)

    @staticmethod
    def _calls_the_guard(src):
        """**Imported is not called.** #100 worried that adapters might carry
        the import and never use it — *the appearance of control*. Measured
        2026-09-03: none did, 63 of 63. But a substring test could not have
        told the difference, so this reads the syntax tree: a name bound from
        `_robots` must appear as the function of an actual call."""
        import ast
        try:
            tree = ast.parse(src)
        except SyntaxError:
            return False
        bound = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.ImportFrom) and (n.module or "") == "_robots":
                bound.update(a.asname or a.name for a in n.names)
            if isinstance(n, ast.Import):
                bound.update(a.asname or a.name for a in n.names
                             if a.name == "_robots")
        if not bound:
            return False
        for n in ast.walk(tree):
            if not isinstance(n, ast.Call):
                continue
            f = n.func
            if isinstance(f, ast.Name) and f.id in bound:
                return True
            if (isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name)
                    and f.value.id in bound):
                return True
        return False

    def test_every_network_reader_asks_the_guard_or_is_listed_with_a_reason(self):
        silent = [name for name, src in self._network_readers()
                  if not self._calls_the_guard(src)
                  and name not in self.NOT_ASKING]
        self.assertEqual(
            silent, [],
            "these touch the network, never call the guard, and give no "
            "reason — an absent call reads the same as a decision not to "
            "call: " + ", ".join(silent))

    def test_the_count_is_what_it_is_said_to_be(self):
        """**The denominator #100 was written on was wrong**, so the real one
        is pinned here. 74 scripts, 69 touching the network, 63 calling the
        guard, 6 listed with a reason. *45* was never the number that did not
        call — it is the number that call `allowed()`, the **per-path** check,
        which is stronger than the per-host one the issue counted."""
        readers = self._network_readers()
        calling = [n for n, src in readers if self._calls_the_guard(src)]
        self.assertEqual(len(readers) - len(calling), len(self.NOT_ASKING))
        self.assertGreater(len(calling), 55)

    def test_the_list_carries_no_script_that_now_asks(self):
        """**A reason that has stopped applying is worse than none.** If one
        of these starts calling the guard, the entry must go, or the file
        will explain an exception that no longer exists."""
        asking = {name for name, src in self._network_readers()
                  if "_robots" in src}
        stale = sorted(asking & set(self.NOT_ASKING))
        self.assertEqual(stale, [], "these now ask the guard and should be "
                                    "removed from NOT_ASKING: "
                                    + ", ".join(stale))

    def test_the_tooling_scripts_really_do_not_touch_the_network(self):
        """Verified rather than assumed — **and the assumption was wrong
        once.** `tenant_offer.py` was grouped with the ledger tools and sends
        HEAD requests through up to eight redirects; it asks the guard now."""
        import glob
        names = {os.path.basename(p) for p, _ in
                 [(x, None) for x in glob.glob(os.path.join(SCRIPTS, "*.py"))]}
        for tool in ("achievements.py", "board_offer.py", "dormant.py",
                     "employers.py", "ledger.py"):
            self.assertIn(tool, names)
            src = open(os.path.join(SCRIPTS, tool), encoding="utf-8").read()
            for token in ("urllib.request", "urlopen", "http.client",
                          "socket."):
                self.assertNotIn(token, src, f"{tool} touches the network")


class SmartRecruitersIsAnOverrideNotASilence(unittest.TestCase):
    """#121, decided by the repository's owner: treat it as AMS.

    **`api.smartrecruiters.com` publishes 72 bytes** — `LinkedInBot` allowed on
    `/v1/companies/`, `*` closed entirely — which is the AMS shape exactly.
    Before this, `ats.py` gated teamtailor at line 418 and **did not ask about
    this host at all**, so the adapter read a host that refuses it and **the
    exception existed nowhere**: not as a decision, not as a note, not as a
    silence anybody could see. That was the defect, more than the reading.

    The first ground offered was wrong and is retracted in
    `shared/boards/smartrecruiters.md`: the `llms.txt` cited sits on other
    hosts, one copy is generated by an SEO plugin, and it indexes marketing
    and documentation pages. **The most specific declaration for the API host
    is its own file.**
    """

    def test_the_key_is_required_and_absent_means_skipped(self):
        src = open(os.path.join(SCRIPTS, "ats.py"), encoding="utf-8").read()
        self.assertIn("override_robots", src)
        self.assertIn("skipped, not silently obeyed", src)

    def test_the_gate_sits_where_every_request_passes(self):
        """**Gating `list` alone left `ad` and the description fetch open** —
        three call sites, which is how `hiringcafe.com` came to be built in
        three places. A new call site cannot miss a check inside `fetch`."""
        src = open(os.path.join(SCRIPTS, "ats.py"), encoding="utf-8").read()
        i = src.index("def fetch(url):")
        self.assertIn("smartrecruiters_gate()", src[i:i + 500])

    def test_the_gate_actually_runs_and_not_merely_appears(self):
        """**The case above reads a position and calls it a guarantee.**

        `None and smartrecruiters_gate()` leaves the call text exactly where
        that check looks, never runs it, and the whole suite stayed green —
        while `fetch` would then reach `api.smartrecruiters.com`, which
        publishes `User-agent: * / Disallow: /`. **A gate that is present and
        inert is worse than one that is absent**, because the check that
        should find it reports success.

        So this one calls `fetch` and asserts the gate *fired*, rather than
        asserting where it is written. No request is made: the gate refuses
        first, which is the whole point.
        """
        import ats
        calls = []
        real_gate = ats.smartrecruiters_gate
        real_open = ats.urllib.request.urlopen
        ats.smartrecruiters_gate = lambda *a, **k: calls.append(1)

        def offline(*a, **k):
            # the gate has already decided by the time this could run; the
            # request itself is not what this case is about.
            raise ats.urllib.error.URLError("offline for this case")

        ats.urllib.request.urlopen = offline
        # **The pacer asks the rules for this host, and `urlopen` is stubbed**,
        # so the guard would retry three times with a growing wait — six
        # seconds inside a suite that runs in two. Zeroing the back-off keeps
        # this case about the gate; the retry itself is covered elsewhere.
        import _robots
        real_backoff = _robots._BACKOFF
        _robots._BACKOFF = (0, 0)
        try:
            ats.fetch("https://api.smartrecruiters.com/v1/companies/x")
        except BaseException:      # SystemExit included — fetch dies loudly
            pass
        finally:
            _robots._BACKOFF = real_backoff
            ats.smartrecruiters_gate = real_gate
            ats.urllib.request.urlopen = real_open
        self.assertEqual(len(calls), 1,
                         "fetch() did not call the gate — it may still be "
                         "written in the file and never reached")

    def test_the_run_says_it_out_loud_once(self):
        src = open(os.path.join(SCRIPTS, "ats.py"), encoding="utf-8").read()
        self.assertIn("override ACTIVE", src)
        self.assertIn("_SR_ANNOUNCED", src)

    def test_no_document_still_calls_it_the_only_override(self):
        """**A sentence that says "the only one" while a second exists tells
        the user something false about the plugin.** There are two."""
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for rel in ("shared/robots-policy.md", "shared/setup.md"):
            text = open(os.path.join(root, rel), encoding="utf-8").read()
            for stale in ("the only override in the plugin",
                          "this is the only one",
                          "That this is the only one"):
                self.assertNotIn(stale, text, f"{rel} still says {stale!r}")

    def test_the_permitting_providers_are_not_swept_into_it(self):
        """It does not generalise: Greenhouse, Workable and Lever permit."""
        src = open(os.path.join(SCRIPTS, "ats.py"), encoding="utf-8").read()
        i = src.index("def smartrecruiters_gate")
        self.assertIn("does not generalise", src[i:i + 3000])


class LdJsonMalformations(unittest.TestCase):
    r"""One case per specimen, each named with the site it came from. #127.

    **Two occurrences on two continents suggest a class, not an accident**: a
    publisher that escapes one layer too many. Michael Page and Chile's
    service put a **literal newline** inside a string, which is why
    `strict=False` is passed at all; `jobivoire.ci` puts an **HTML entity
    behind a backslash** — `d\&#039;Atelier`, an apostrophe HTML-escaped after
    being JSON-escaped. `\&` is not an escape sequence and `strict=False` does
    not forgive it.

    **The repair does not silence the guard.** `absent_reason()` caught this
    on two independent sessions the same evening and reported it
    `our_fault=True`; a fix that recovered the twelve advertisements by
    turning that warning off would be a regression, not a repair.
    """

    NEWLINE = ('<script type="application/ld+json">'
               '{"@type":"JobPosting","description":"a\nb"}</script>')
    BAD_ESCAPE = ('<script type="application/ld+json">'
                  '{"@type":"JobPosting","title":"d\\&#039;Atelier"}</script>')
    NESTED = ('<script type="application/ld+json">'
              '{"@type":"CollectionPage","mainEntity":{"@type":"ItemList",'
              '"itemListElement":[{"@type":"ListItem","position":1,'
              '"item":{"@type":"JobPosting","title":"one"}},'
              '{"@type":"ListItem","position":2,'
              '"item":{"@type":"JobPosting","title":"two"}}]}}</script>')
    BEYOND_REPAIR = ('<script type="application/ld+json">'
                     '{"@type":"JobPosting", "title": }</script>')

    def test_a_literal_newline_still_parses(self):
        """Michael Page and `bne.gob.cl`. The reason `strict=False` is there."""
        self.assertEqual(len(_ldjson.postings(self.NEWLINE)), 1)

    def test_a_backslash_before_an_html_entity_is_repaired(self):
        """`jobivoire.ci`. `strict=False` does not cover this one."""
        import json
        blk = _ldjson.blocks(self.BAD_ESCAPE)[0]
        with self.assertRaises(ValueError):
            json.loads(blk, strict=False)
        got = _ldjson.postings(self.BAD_ESCAPE)
        self.assertEqual(len(got), 1)
        self.assertEqual(got[0]["title"], "d\\&#039;Atelier")

    def test_the_repair_is_counted_and_can_be_reported(self):
        """**A page whose structured data needs mending is a page to watch**,
        and the number belongs in a run's output, not in this module's
        silence."""
        self.assertEqual(_ldjson.repairs(self.BAD_ESCAPE), 1)
        self.assertEqual(_ldjson.repairs(self.NEWLINE), 0)

    def test_mainentity_nests_an_itemlist(self):
        """`jobivoire.ci` again: a `CollectionPage` whose `mainEntity` is an
        `ItemList` of twelve. A reader unwrapping `itemListElement` only at
        the top level saw **one** object on a page holding twelve."""
        got = _ldjson.postings(self.NESTED)
        self.assertEqual([p["title"] for p in got], ["one", "two"])

    def test_what_the_repair_cannot_fix_is_still_reported(self):
        """**The guard is not turned off by the fix.**"""
        self.assertEqual(_ldjson.postings(self.BEYOND_REPAIR), [])
        why = _ldjson.absent_reason(self.BEYOND_REPAIR)
        self.assertEqual(why.kind, "unparseable")
        self.assertTrue(why.our_fault)

    def test_the_diagnosis_parses_the_same_way_the_reader_does(self):
        """A diagnosis that parsed differently would report a page unreadable
        while the reader was reading it."""
        why = _ldjson.absent_reason(self.BAD_ESCAPE)
        self.assertNotEqual(why.kind, "unparseable")

    def test_the_repair_leaves_valid_json_untouched(self):
        """**It must not be a general attempt to fix JSON.** A valid escape
        is not a malformation."""
        good = ('<script type="application/ld+json">'
                '{"@type":"JobPosting","title":"a \\"quoted\\" word",'
                '"description":"line\\nbreak"}</script>')
        got = _ldjson.postings(good)
        self.assertEqual(len(got), 1)
        self.assertEqual(got[0]["title"], 'a "quoted" word')
        self.assertIn("\n", got[0]["description"])


class ABodyNobodyRecognisedIsNotAnAbsence(unittest.TestCase):
    """#128, the seventh defect in this guard and the seventh towards
    *allowed* — but the first that **asserts** rather than merely permits.

    `maliemploi.org` served an Apache *"Access forbidden! / Error 403"* page
    as its `robots.txt`, and the guard answered:

        allowed: True   group: *   sweep: True   certain: True

    **A `*` group invented out of an error page, and then certified.**

    **The issue read it as the verdict depending on body size** — 976 bytes
    accepted, a 5 132-byte React shell rejected. **It is not the size.** The
    short one was labelled `text/plain` and **its body was never examined**;
    the long one was labelled `text/html` and was. Same defect, one branch
    earlier: the header decided, and the body never got a look.

    `certain` exists to say *this is an established absence of rules*. **A
    guard that errs by doubting is repairable; a guard that errs by asserting
    gets itself believed.**
    """

    class _Resp:
        def __init__(self, body, ctype):
            self._b, self._c = body, ctype

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def getcode(self):
            return 200

        def geturl(self):
            return "https://h.example/robots.txt"

        def read(self):
            return self._b.encode()

        @property
        def headers(self):
            return {"Content-Type": self._c}

    def _verdict(self, body, ctype):
        sys.path.insert(0, SCRIPTS)
        import _robots
        real = _robots.urllib.request.urlopen
        _robots._CACHE.clear()
        _robots._ALIAS.clear()
        _robots.urllib.request.urlopen = (
            lambda r, timeout=None, **k: self._Resp(body, ctype))
        try:
            return _robots.verdict("h.example"), _robots.allowed(
                "h.example", "/jobs")
        finally:
            _robots.urllib.request.urlopen = real
            _robots._CACHE.clear()
            _robots._ALIAS.clear()

    APACHE = ('<!DOCTYPE HTML><html><head><title>403 Forbidden</title></head>'
              '<body><h1>Access forbidden!</h1><p>Error 403</p></body></html>')
    SPA = ('<!doctype html><html><body>You need to enable JavaScript to run '
           'this app.</body></html>')

    def test_a_short_error_page_labelled_text_plain_is_not_rules(self):
        """**The specimen.** Labelled `text/plain`, so the old code never
        looked at it.

        **What #128 fixed is still fixed**, and that is what this asserts: the
        page is not parsed into an empty `*` group, and it is not certified.
        The conduct applied to that absence changed on 2026-09-04 — see
        `AnEmptyBodyIsAnOpenDoor` — but the epistemics did not, and the two
        were merged once already.
        """
        v, a = self._verdict(self.APACHE, "text/plain")
        # **This specimen moved state on 2026-09-04, and correctly.** It says
        # `Access forbidden! Error 403` in words, so #138 now reads it as
        # `refused-in-prose` rather than as an absence of rules. What #128
        # established is unchanged and is what this asserts: it is not parsed
        # into an empty `*` group, and it is not certified.
        self.assertEqual(v["state"], "refused-in-prose")
        self.assertFalse(v["certain"])
        self.assertFalse(a["certain"])
        self.assertIsNone(v.get("group"),
                          "a group was invented out of an error page — this "
                          "is #128 itself, and no policy change licenses it")

    def test_a_long_spa_shell_is_not_rules_either(self):
        """Same verdict for the case that was already caught — **the two must
        not depend on which header they carried.**"""
        v, a = self._verdict(self.SPA, "text/html")
        self.assertEqual(v["state"], "unrecognised")
        self.assertFalse(a["certain"])

    def test_an_empty_body_establishes_nothing(self):
        """A zero-byte body carries no directive either. RFC 9309 would read
        it as *no rules*; **we cannot tell it from a broken response**, so the
        state stays `unrecognised` and `certain` stays false — even though the
        door now opens on it."""
        v, _a = self._verdict("", "text/plain")
        self.assertEqual(v["state"], "unrecognised")
        self.assertFalse(v["certain"])

    def test_a_real_rules_file_still_permits_and_is_certain(self):
        """**The other half.** A file with no `Disallow` is a real absence of
        restriction, and `certain` is exactly what it is for."""
        v, a = self._verdict("User-agent: *\nAllow: /\n", "text/plain")
        self.assertEqual(v["state"], "read")
        self.assertIs(a["allowed"], True)
        self.assertTrue(v["certain"])

    def test_certain_is_never_true_on_a_body_we_did_not_recognise(self):
        """The requirement that separates this from #125, as one assertion."""
        for body, ctype in ((self.APACHE, "text/plain"),
                            (self.SPA, "text/html"), ("", "text/plain")):
            v, _a = self._verdict(body, ctype)
            self.assertFalse(v["certain"], f"{ctype}: {body[:30]!r}")

    def test_the_reason_quotes_what_was_seen_not_an_invented_group(self):
        v, a = self._verdict(self.APACHE, "text/plain")
        # The wording changed with the state (#138); **what it must not do is
        # what #128 was about** — quote a group nobody wrote.
        self.assertIn("no directive line", v["reason"])
        self.assertIn("200", v["reason"])
        self.assertNotIn("the group that applies to everyone",
                         a["reason"] or "")
        self.assertFalse(v["certain"],
                         "a body read as prose was certified")


class RulesNothingHadEverTested(unittest.TestCase):
    """Four rules `_robots.py` implements and the suite never checked. #119.

    **Found by mutation, not by reading.** Each of this guard's seven defects
    was put back one at a time and the suite asked; six were caught. Then the
    same battery was run against rules that had never failed in production —
    and four of them nothing noticed.

    **Three of the four err towards `allowed` when broken**, which is the
    direction all seven real defects took. A suite that tests only the
    defects that have already happened describes a history; these pin the
    rules.

    **Two of the eight mutations proved nothing and were discarded**: one
    changed only which token name is quoted, one added an unused constant.
    **A mutation that does not change behaviour is not evidence about the
    tests**, and the first was very nearly reported as a hole.
    """

    def _with_body(self, body, host="h.example"):
        sys.path.insert(0, SCRIPTS)
        import _robots
        _robots._CACHE.clear()
        _robots._ALIAS.clear()
        real = _robots._fetch
        _robots._fetch = lambda h: {"state": "read", "body": body,
                                    "final": h, "attempts": 1}
        try:
            return _robots.verdict(host), _robots.allowed(host, "/a/b/c/d")
        finally:
            _robots._fetch = real
            _robots._CACHE.clear()
            _robots._ALIAS.clear()

    def test_a_tie_between_allow_and_disallow_goes_to_allow(self):
        """RFC 9309: *if an allow and a disallow are equivalent, the allow
        SHOULD be used.* **Nothing paired them on one path**, so `>=` could
        have been `>` for ever."""
        sys.path.insert(0, SCRIPTS)
        import _robots
        self.assertEqual(_robots._match_len("/a/b", "/a/b/c/d"),
                         _robots._match_len("/a/b", "/a/b/c/d"))
        _v, a = self._with_body(
            "User-agent: *\nDisallow: /a/b\nAllow: /a/b\n")
        self.assertIs(a["allowed"], True)
        self.assertEqual(a["kind"], "allow")

    def test_the_longest_match_decides_not_the_first(self):
        """**Breaking this permits a path the file refuses.** With
        `Disallow: /a`, `Disallow: /a/b/c` and `Allow: /a/b`, a first-match
        reader compares `/a` (2) against `/a/b` (4) and **allows**; the
        longest match is `/a/b/c` (6) and refuses."""
        _v, a = self._with_body(
            "User-agent: *\nDisallow: /a\nDisallow: /a/b/c\nAllow: /a/b\n")
        self.assertIs(a["allowed"], False)
        self.assertEqual(a["rule"], "/a/b/c")

    def test_content_signal_ai_input_no_is_a_refusal(self):
        """**The most consent-critical rule in the module, and `ai-input`
        appeared nowhere in the suite.** Disabling the check flips `sweep`
        from False to True and nothing failed. Issue #98."""
        v, _a = self._with_body(
            "User-agent: *\nContent-Signal: search=yes,ai-input=no\n"
            "Allow: /\n")
        self.assertIs(v["sweep"], False)
        self.assertIn("ai-input", v["reason"])

    def test_every_content_signal_is_read_not_only_the_first(self):
        """A refusal in the second line is still a refusal — the CDN's copy
        and the origin's can disagree, and no convention says which wins."""
        v, _a = self._with_body(
            "User-agent: *\nContent-Signal: search=yes\n"
            "Content-Signal: ai-input=no\nAllow: /\n")
        self.assertIs(v["sweep"], False)
        self.assertTrue(v["content_signal_conflict"])

    def test_the_verdict_is_cached_on_the_host_that_answered(self):
        """#99: `ss.ge` redirects to `jobs.ss.ge`, which publishes a different
        file. **Caching on the name that was typed would hand one host's
        rules to another**, and nothing asserted `requested_host`."""
        sys.path.insert(0, SCRIPTS)
        import _robots
        _robots._CACHE.clear()
        _robots._ALIAS.clear()
        real = _robots._fetch
        _robots._fetch = lambda h: {
            "state": "read", "body": "User-agent: *\nDisallow: /x\n",
            "final": "answered.example", "attempts": 1}
        try:
            v = _robots.verdict("asked.example")
            self.assertEqual(v["host"], "answered.example")
            self.assertEqual(v["requested_host"], "asked.example")
            # **The key carries the agents since #139**, because `identity()`
            # asks the same host once per token and a key of the host alone
            # would hand the second caller the first one's verdict. The claim
            # this case makes is unchanged: the verdict is filed under the
            # host that *answered*, never the one that was asked.
            cached = {h for h, _agents in _robots._CACHE}
            self.assertIn("answered.example", cached)
            self.assertNotIn("asked.example", cached)
        finally:
            _robots._fetch = real
            _robots._CACHE.clear()
            _robots._ALIAS.clear()


class TheLossyFallbackSpeaks(unittest.TestCase):
    """`errors="replace"` is the probe that cannot go red. #115.

    A half-replaced title reads as ordinary text to the program and to this
    suite. `_decode` was written to report **which** encoding it used so a
    caller could tell — and measured 2026-09-03, **60 of 61 call sites
    discard it with `[0]`**, and nothing anywhere tests for
    `"utf-8/replace"`.

    **A signal that exists and is never read** is the shape this repository
    met four times in one day: `absent_reason()` parsing differently from the
    reader, an empty `external_host` asserting *no host*, `certain` on a body
    nobody recognised. So the module speaks now, rather than returning a
    value nobody looks at.

    **And it speaks only on a real loss.** Measured across five live boards —
    4 663 rows, 18 089 accented characters — **zero replacements**. On these
    boards the guard is a precaution, and that was measured before the
    severity was chosen.
    """

    def test_it_warns_when_characters_are_actually_replaced(self):
        import io
        import contextlib
        _decode._WARNED.clear()
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            text, enc = _decode.decode_body(b"ok \x81\x8d text")
        self.assertEqual(enc, "utf-8/replace")
        self.assertEqual(text.count("\ufffd"), 2)
        self.assertIn("could not be decoded", err.getvalue())
        self.assertIn("U+FFFD", err.getvalue())

    def test_it_says_nothing_when_nothing_was_lost(self):
        """**A warning that fires on clean input is noise**, and noise is how
        a real one gets missed."""
        import io
        import contextlib
        _decode._WARNED.clear()
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            _decode.decode_body("café €".encode("utf-8"))
            _decode.decode_body("caf\xe9".encode("cp1252"))
        self.assertEqual(err.getvalue(), "")

    def test_it_speaks_once_per_process(self):
        """A sweep of four thousand advertisements on a broken host would
        otherwise print four thousand lines, **and a warning that scrolls is
        a warning nobody reads.**"""
        import io
        import contextlib
        _decode._WARNED.clear()
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            for _ in range(5):
                _decode.decode_body(b"ok \x81\x8d text")
        self.assertEqual(err.getvalue().count("[decode]"), 1)

    def test_no_adapter_still_decodes_utf8_by_hand(self):
        """The first migration matched `decode("utf-8", …)` and **missed
        `decode("utf8", …)` without the hyphen** — eight adapters. The
        pattern defined its own result."""
        import glob
        offenders = []
        for path in sorted(glob.glob(os.path.join(SCRIPTS, "*.py"))):
            name = os.path.basename(path)
            if name in ("_decode.py", "_robots.py", "hiringcafe.py"):
                continue          # deliberate, and each says why
            src = open(path, encoding="utf-8").read()
            if re.search(r'\.decode\(\s*["\']utf-?8["\']\s*,', src):
                offenders.append(name)
        self.assertEqual(offenders, [],
                         "these decode a body without reading the "
                         "declaration: " + ", ".join(offenders))


class NoSignalIsOrphaned(unittest.TestCase):
    """#129: a signal that exists and nobody reads. **The scan overcounted.**

    A first pass reported **11 of 16 keys in the guard's result read by
    nobody** — and it was wrong, because it looked only at adapter files. A
    signal reaches its reader by **three** routes, not one:

    - the field, read by a caller (`allowed`, `sweep`, `reason`, `kind`);
    - the field, read by the module's own CLI (`sweep_disagrees`, `differ`)
      or by this suite (`certain`, `group`, `groups`, `rule`, `disallow`);
    - **the sentence** — `content_signal`'s value is quoted verbatim in the
      `reason` that every `die()` prints, and so are the status and the byte
      count.

    **A scan that counts only the first route reports the other two as
    absences** — the same shape as `45 of 61`, where the complement of a
    stronger check was read as a gap. It is the eighth time in two days that
    a probe defined its own population, **and the first where the wrong
    answer was the alarming one**, which is why it nearly shipped.

    The one real orphan was `decode_body`'s second value — 60 of 61 callers
    discarding it with `[0]` — and that module speaks now.
    """

    def _verdict(self, body):
        sys.path.insert(0, SCRIPTS)
        import _robots
        _robots._CACHE.clear()
        _robots._ALIAS.clear()
        real = _robots._fetch
        _robots._fetch = lambda h: {"state": "read", "body": body,
                                    "final": h, "attempts": 1}
        try:
            return _robots.verdict("h.example")
        finally:
            _robots._fetch = real
            _robots._CACHE.clear()
            _robots._ALIAS.clear()

    def test_the_reason_carries_what_the_orphan_keys_hold(self):
        """**The sentence is the route that reaches a caller.** No adapter
        reads `content_signal`; every one of them prints `reason`."""
        v = self._verdict("User-agent: *\n"
                          "Content-Signal: search=yes,ai-input=no\nAllow: /\n")
        self.assertEqual(v["content_signal"], ["search=yes,ai-input=no"])
        self.assertIn("ai-input=no", v["reason"])

    def test_the_status_and_size_reach_the_caller_through_the_reason(self):
        """#125's requirement, restated as a route: an adapter that prints
        only `reason` still learns what was observed."""
        sys.path.insert(0, SCRIPTS)
        import _robots
        _robots._CACHE.clear()
        _robots._ALIAS.clear()
        real = _robots._fetch
        _robots._fetch = lambda h: {
            "state": "unrecognised", "final": h, "attempts": 1,
            "status": 200, "bytes": 976,
            "why": "HTTP 200, Content-Type 'text/plain', 976 bytes, and no "
                   "`User-agent` line anywhere in it"}
        try:
            v = _robots.verdict("h.example")
            self.assertIn("200", v["reason"])
            self.assertIn("976", v["reason"])
        finally:
            _robots._fetch = real
            _robots._CACHE.clear()
            _robots._ALIAS.clear()

    def test_decode_body_is_the_one_signal_that_had_no_route(self):
        """It reported its method in a return value that 60 of 61 callers
        threw away, and no route replaced it. **So the source speaks.**"""
        import io
        import contextlib
        _decode._WARNED.clear()
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            _decode.decode_body(b"ok \x81\x8d text")
        self.assertIn("[decode]", err.getvalue())


class LineEndingsAreDeclared(unittest.TestCase):
    """#107: `bin/doctor.sh` is the first thing `README.md` asks a user to run.

    **Git for Windows sets `core.autocrlf=true` by default**, converting line
    endings on the way *out* of the repository. A shell script checked out
    that way fails under Git Bash with

        /usr/bin/env: 'bash\r': No such file or directory

    — which names an interpreter that exists, with an invisible character on
    the end. **The first gesture the project asks for is the one that
    breaks**, and it looks like the user's fault.

    **No Windows machine was available to reproduce it**, and this suite does
    not pretend otherwise. What it checks is what is checkable anywhere: that
    the rule is declared, that Git agrees it applies, and that nothing in the
    index already carries a carriage return.
    """

    def _root(self):
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def test_the_rule_exists(self):
        self.assertTrue(os.path.exists(os.path.join(self._root(),
                                                    ".gitattributes")))

    def test_git_applies_lf_to_the_script_the_readme_names_first(self):
        """**Declared is not applied.** `git check-attr` is the one that
        answers, and it answers on this machine as it would on any other —
        the attribute is in the repository, not in the checkout."""
        import subprocess
        r = subprocess.run(["git", "check-attr", "eol", "--", "bin/doctor.sh"],
                           capture_output=True, text=True, cwd=self._root())
        self.assertIn("eol: lf", r.stdout)

    def test_every_shell_script_is_covered(self):
        import glob
        import subprocess
        root = self._root()
        scripts = [os.path.relpath(p, root)
                   for p in glob.glob(os.path.join(root, "bin", "*.sh"))]
        self.assertGreater(len(scripts), 0)
        for rel in scripts:
            r = subprocess.run(["git", "check-attr", "eol", "--", rel],
                               capture_output=True, text=True, cwd=root)
            self.assertIn("eol: lf", r.stdout, rel)

    def test_nothing_in_the_index_already_carries_a_carriage_return(self):
        """The declaration fixes the boundary; it does not rewrite history.
        **If a CRLF file were already committed, the rule would not undo it**
        — somebody would need `git add --renormalize .` `git ls-files --eol`
        reports the index (`i/`) and working-tree (`w/`) endings of every
        tracked file in one pass; anything but `i/lf` on a text file is a
        carriage return already in the repository."""
        import subprocess
        root = self._root()
        out = subprocess.run(["git", "ls-files", "--eol"], capture_output=True,
                             text=True, cwd=root).stdout.splitlines()
        self.assertGreater(len(out), 50)
        bad = []
        for line in out:
            fields = line.split("\t", 1)
            if len(fields) != 2:
                continue
            index_eol = fields[0].split()[0]
            # i/-text marks a binary blob, which has no line endings to get
            # wrong; i/mixed and i/crlf are the two that break Git Bash.
            if index_eol not in ("i/lf", "i/-text", "i/none"):
                bad.append(f"{fields[1].strip()} ({index_eol})")
        self.assertEqual(bad, [], "stored with a carriage return: "
                                  + ", ".join(bad[:5]))


class SourceCompilesWithoutWarning(unittest.TestCase):
    """`\\&` sat in a docstring in this file until #107's work compiled the
    tree and Python said so.

    **An invalid escape sequence is not a style complaint.** `"\\&"` is
    currently `"\\\\&"` by accident — Python leaves an unrecognised escape
    alone and warns — and that behaviour is scheduled to become a
    `SyntaxError`. The specimens this suite quotes are *made of* backslashes:
    `d\\&#039;Atelier` from jobivoire, the JSON escapes in `_ldjson`, the
    `\\r` this class's neighbour is about. **A file that documents escaping
    is the likeliest place to escape something wrongly**, and the warning
    goes to stderr where a green `OK` hides it.

    Compiling is not importing: this reads every tracked `.py` without
    running any of it.
    """

    def test_no_invalid_escapes_or_other_syntax_warnings(self):
        import glob
        import warnings
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        found = []
        seen = 0
        for path in glob.glob(os.path.join(root, "**", "*.py"),
                              recursive=True):
            if os.sep + ".git" + os.sep in path:
                continue
            seen += 1
            with open(path, encoding="utf-8") as fh:
                src = fh.read()
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter("always")
                try:
                    compile(src, path, "exec")
                except SyntaxWarning as exc:      # raised, not warned
                    found.append(f"{os.path.relpath(path, root)}: {exc}")
                for item in caught:
                    if issubclass(item.category, SyntaxWarning):
                        found.append(f"{os.path.relpath(path, root)}: "
                                     f"{item.message}")
        self.assertGreater(seen, 50, "found almost no python to compile")
        self.assertEqual(found, [], "; ".join(found[:3]))


class TlsHostsAreRoutedEverywhere(unittest.TestCase):
    """#104 was fixed in one of the two adapters that read the host.

    `_tls.py` exists because **`empleate.gob.es` serves its leaf certificate
    and no intermediate**. Python's stdlib does not chase the AIA extension,
    so verification fails with `unable to get local issuer certificate` —
    while `curl` succeeds, because it does chase it. That is why the defect
    survived a `curl` check.

    `empleate.py` was given the context. **`oposiciones.py` was not**, and it
    reads the same host through the same `urlopen`. Nothing failed loudly:
    the robots guard refuses both adapters earlier, so the broken TLS path
    was never reached and never reported.

    **The fix is per-adapter and the host list is central**, which is the
    shape that loses one call site. This binds them: a file naming a host in
    `_tls.HOSTS` must route through `_tls`.
    """

    def test_every_adapter_reading_a_tls_host_imports_tls(self):
        import glob
        import re
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        scripts = os.path.join(root, "skills", "job-scan", "scripts")
        sys.path.insert(0, scripts)
        import _tls
        hosts = {h for h in _tls.HOSTS if not h.startswith("www.")}
        self.assertTrue(hosts, "_tls declares no hosts to check")

        offenders = []
        for path in sorted(glob.glob(os.path.join(scripts, "*.py"))):
            name = os.path.basename(path)
            if name.startswith("_"):
                continue
            with open(path, encoding="utf-8") as fh:
                src = fh.read()
            # only a file that actually opens a socket on the host counts
            # **The wide pattern, and it was narrow for an hour.** Four
            # adapters fetch through `OPENER.open(...)` rather than
            # `urlopen(...)`: applifly, emploiterritorial, hiringcafe and
            # philjobnet. A filter matching only `urlopen` dropped all four
            # from this population — and one of them imports no guard at all,
            # so the guard reported a healthy set of exactly four exemptions
            # while five adapters were unguarded.
            if not re.search(r"urllib\.request|http\.client|requests\.", src):
                continue
            if not any(h in src for h in hosts):
                continue
            if not re.search(r"(^|\n)\s*import\s+_tls", src):
                offenders.append(name)
        self.assertEqual(offenders, [],
                         "these read a host in _tls.HOSTS over a raw stdlib "
                         "context and will fail verification: "
                         + ", ".join(offenders))


class GuardReportsBytesNotCharacters(unittest.TestCase):
    """#130: `len()` of a decoded string counts characters; every message
    called the number `bytes`.

    **An all-ASCII body cannot catch this** — the two counts coincide there,
    and `robots.txt` is usually ASCII, which is why it survived. It shows on
    anything else: `empleate.gob.es` answered with an 8 456-byte error page
    carrying six multi-byte sequences, and the guard announced *"8 450
    bytes"*.

    **A wrong unit is worse than a missing one.** A missing unit stops the
    reader; a wrong one invites them to compare two numbers that are not the
    same quantity. That is exactly what happened: a direct read (8 456) and
    this message (8 450) were set beside each other and the difference was
    published as the site changing size between reads — **a property of our
    counter, reported as a property of the host.**

    So the specimen here is deliberately multi-byte, and the assertion is
    against the count on the wire.
    """

    def _serve(self, body_bytes, ctype="text/html"):
        """One request, on a real socket, then the server dies."""
        import http.server
        import threading
        holder = {}

        class H(http.server.BaseHTTPRequestHandler):
            def do_GET(inner):                      # noqa: N805
                inner.send_response(200)
                inner.send_header("Content-Type", ctype)
                inner.send_header("Content-Length", str(len(body_bytes)))
                inner.end_headers()
                inner.wfile.write(body_bytes)

            def log_message(inner, *a):             # noqa: N805
                pass

        srv = http.server.HTTPServer(("127.0.0.1", 0), H)
        holder["port"] = srv.server_address[1]
        t = threading.Thread(target=srv.handle_request, daemon=True)
        t.start()
        self.addCleanup(srv.server_close)
        return holder["port"]

    def test_a_multibyte_body_is_reported_by_its_byte_length(self):
        import _robots
        # six two-byte sequences, exactly the shape of the page that exposed
        # this: an error document with accented Spanish.
        text = ("<html><title>SEPE</title>"
                "<p>Si el problema persiste, p\u00f3ngase en contacto "
                "con nosotros a trav\u00e9s de la sede electr\u00f3nica. "
                "Disculpe las molestias, gracias por su comprensi\u00f3n. "
                "M\u00e1s informaci\u00f3n.</p></html>")
        raw = text.encode("utf-8")
        self.assertGreater(len(raw), len(text),
                           "specimen is not multi-byte — this test would "
                           "pass on the defect it exists to catch")

        port = self._serve(raw)
        got = _robots._fetch_once(
            f"http://127.0.0.1:{port}/robots.txt", "127.0.0.1", 10)

        self.assertEqual(got["state"], "unrecognised", got.get("why"))
        self.assertEqual(
            got["bytes"], len(raw),
            f"reported {got['bytes']}, on the wire {len(raw)}, decoded "
            f"{len(text)} characters — the report is following the decode")
        self.assertIn(f"{len(raw)} bytes", got["why"],
                      "the printed sentence still carries the wrong number "
                      "even if the field is right — the user reads the "
                      "sentence")

    def test_an_ascii_body_agrees_and_proves_nothing_alone(self):
        """Kept as the control, and labelled as such: it passes on the defect
        too, which is why the case above exists."""
        import _robots
        raw = b"<html>plain ascii error page, no rules here</html>"
        port = self._serve(raw)
        got = _robots._fetch_once(
            f"http://127.0.0.1:{port}/robots.txt", "127.0.0.1", 10)
        self.assertEqual(got["bytes"], len(raw))


class DeclaredAgentIsSentEverywhere(unittest.TestCase):
    """#120 settled what this project calls itself. **The declaration was
    central and its application was per adapter**, so two files never got it.

    Found on 2026-09-04 by looking for the shape that lost `oposiciones.py` a
    day earlier — a value a helper hands back that the caller must remember to
    use. `_tls.context_for()` returns a context you have to pass to `urlopen`;
    `_ua.UA` is a string you have to put in a header. **Neither does anything
    on its own.**

    What was found:

      * `adzuna.py` defined its **own** `UA`, naming no agent token, carrying
        no version and no contact URL, and describing the tool as *"personal
        job search; one user"* — which this repository stopped being.
      * `labonnealternance.py` sent **no `User-Agent` at all**, so urllib
        announced `Python-urllib/3.x`.

    Both are in the four keyed-API boards, which carry a documented exemption
    from the **robots guard**. That is a different obligation, and it does not
    extend here: a key says which account is calling, not who is calling.

    **Declaring a token and then not sending it is worse than not declaring
    one** — the operators who could have recognised us cannot, and the
    declaration in `_ua.py` becomes a claim the traffic does not support.
    """

    def test_every_network_reader_sends_the_declared_agent(self):
        import glob
        import re
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        scripts = os.path.join(root, "skills", "job-scan", "scripts")
        offenders = []
        for path in sorted(glob.glob(os.path.join(scripts, "*.py"))):
            name = os.path.basename(path)
            if name.startswith("_"):
                continue
            with open(path, encoding="utf-8") as fh:
                src = fh.read()
            # wide on purpose: four adapters fetch through
            # `OPENER.open(...)`, not `urlopen(...)` — see
            # TheExemptedApiRoutesStillIdentifyThemselves
            if not re.search(r"urllib\.request|http\.client|requests\.", src):
                continue
            imported = re.search(r"(^|\n)\s*(from _ua import|import _ua)", src)
            # **Two shapes, and only one was recognised for a day.** Most
            # adapters pass `Request(headers={"User-Agent": UA})`; `philjobnet`
            # sets `opener.addheaders = [("User-Agent", UA), ...]`, which is a
            # tuple, not a key. The narrow pattern reported it as sending no
            # agent at all — **a false accusation, not a missed one**, and the
            # more dangerous direction: it invites a "fix" to code that was
            # already correct.
            header = re.search(
                r"""["']User-Agent["']\s*[:,]""", src)
            if not imported:
                offenders.append(f"{name} (no _ua import)")
            elif not header:
                offenders.append(f"{name} (imports _ua, sends no header)")
        self.assertEqual(offenders, [],
                         "these open sockets without the declared agent: "
                         + ", ".join(offenders))

    def test_no_adapter_defines_a_user_agent_of_its_own(self):
        """The defect was not a missing header — `adzuna.py` had one. It was a
        **second declaration**, which is why a header check alone would have
        stayed green."""
        import glob
        import re
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        scripts = os.path.join(root, "skills", "job-scan", "scripts")
        offenders = []
        for path in sorted(glob.glob(os.path.join(scripts, "*.py"))):
            name = os.path.basename(path)
            if name.startswith("_"):
                continue
            with open(path, encoding="utf-8") as fh:
                src = fh.read()
            if re.search(r"^UA\s*=\s*[\"']", src, re.M):
                offenders.append(name)
        self.assertEqual(offenders, [],
                         "these bind their own UA string, shadowing the one "
                         "declaration: " + ", ".join(offenders))


class AnEmptyBodyIsAnOpenDoor(unittest.TestCase):
    """Decided by the owner on 2026-09-04, on #104.

    > *"l'absence de regle est une porte ouverte. Rappel : le fichier
    > robots.txt est un souhait de l'hote (qui bien souvent est autogenere et
    > non verifie)"*

    **It is the counterpart of a rule this repository already applies in the
    other direction.** `robots-policy.md` holds that a vendor default binds
    even though nobody meant it — Honduras publishes a file copied out of
    Google's documentation and we obey it. **If an unmeant refusal binds, an
    unwritten one cannot.**

    **The fragile thing is the boundary, not the state that moved.** *"A body
    that says nothing does not say no"* sits one sentence away from *"we
    proceed when we do not know"*, and the second would undo #118 — where a
    host that closes everything to this project by name was swept whenever
    the request timed out. So the neighbours are pinned as hard as the change.
    """

    def setUp(self):
        """**The real ladder is three attempts with 1.5s and 4s of backoff.**
        Two cases here end in `unreachable` on purpose, and paying the real
        wait for them put twenty-five seconds on the suite. The retry
        behaviour is pinned elsewhere; what these cases are about is the
        verdict."""
        import _robots
        real = _robots._BACKOFF
        _robots._BACKOFF = (0, 0)
        self.addCleanup(setattr, _robots, "_BACKOFF", real)

    class _Resp:
        def __init__(self, body, ctype, code=200):
            self._b = body.encode("utf-8") if isinstance(body, str) else body
            self._c, self._code = ctype, code

        def read(self):
            return self._b

        def geturl(self):
            return "https://h.example/robots.txt"

        def getcode(self):
            return self._code

        @property
        def headers(self):
            return {"Content-Type": self._c}

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def _verdict(self, body, ctype="text/html", code=200):
        import _robots
        real = _robots.urllib.request.urlopen
        _robots._CACHE.clear()
        _robots._ALIAS.clear()
        _robots.urllib.request.urlopen = (
            lambda r, timeout=None, **k: self._Resp(body, ctype, code))
        try:
            return (_robots.verdict("h.example"),
                    _robots.allowed("h.example", "/jobs"))
        finally:
            _robots.urllib.request.urlopen = real
            _robots._CACHE.clear()
            _robots._ALIAS.clear()

    # ---- the state that moved -------------------------------------------

    def test_a_body_with_no_directive_line_opens_the_door(self):
        v, a = self._verdict("<html><title>SEPE</title>error</html>")
        self.assertEqual(v["state"], "unrecognised")
        self.assertTrue(v["sweep"])
        self.assertTrue(a["allowed"])

    def test_it_opens_the_door_without_claiming_to_know(self):
        """**`allowed: True` with `certain: False` is the honest shape.** We
        proceed on a policy, not on a finding, and anything reading this
        module must be able to tell those apart — #128 exists because they
        were merged once."""
        v, a = self._verdict("<html><title>SEPE</title>error</html>")
        self.assertTrue(a["allowed"])
        self.assertFalse(v["certain"])
        self.assertFalse(a["certain"])

    def test_the_reason_says_why(self):
        """A verdict that gives no reason invites suspicion; one that gives a
        false reason reads like a verification. The sentence carries the
        status, the type, the size and the absence of directive lines."""
        body = "<html><title>SEPE</title>no rules here</html>"
        v, _a = self._verdict(body, "text/html")
        why = v["reason"]
        self.assertIn("200", why)
        self.assertIn("text/html", why)
        self.assertIn(str(len(body.encode("utf-8"))), why)
        self.assertIn("User-agent", why)
        self.assertIn("open door", why)

    # ---- the two neighbours, which must not move -------------------------

    def test_a_2xx_that_is_not_200_still_stops_us(self):
        """`algerie.tanqeeb.com` answers **202 with zero bytes**. That is not
        a body without rules — it is not a document at all. #125."""
        v, a = self._verdict("", "text/plain", code=202)
        self.assertEqual(v["state"], "unreachable")
        self.assertIsNone(v["sweep"])
        self.assertIsNone(a["allowed"])

    def test_the_open_door_did_not_reach_the_unreachable_state(self):
        """**The one that would undo #118.** A host we could not reach is a
        host we know nothing about, and it looks exactly like a host that
        closes everything to us by name — `nea.gov.kh` did."""
        import _robots
        real = _robots.urllib.request.urlopen

        def boom(*a, **k):
            raise _robots.urllib.error.URLError("timed out")

        _robots._CACHE.clear()
        _robots._ALIAS.clear()
        _robots.urllib.request.urlopen = boom
        try:
            v = _robots.verdict("h.example")
            a = _robots.allowed("h.example", "/jobs")
        finally:
            _robots.urllib.request.urlopen = real
            _robots._CACHE.clear()
            _robots._ALIAS.clear()
        self.assertEqual(v["state"], "unreachable")
        self.assertIsNone(v["sweep"], "a fetch failure became a permission — "
                                      "this is #118, the worst defect this "
                                      "module has had")
        self.assertIsNone(a["allowed"])

    def test_a_403_on_robots_txt_is_still_a_refusal(self):
        """**The host answered, and it answered no.** Nothing about an
        absence of rules reaches this row."""
        import _robots
        real = _robots.urllib.request.urlopen

        def refuse(*a, **k):
            raise _robots.urllib.error.HTTPError(
                "https://h.example/robots.txt", 403, "Forbidden", {},
                io.BytesIO(b"nope"))

        _robots._CACHE.clear()
        _robots._ALIAS.clear()
        _robots.urllib.request.urlopen = refuse
        try:
            v = _robots.verdict("h.example")
            a = _robots.allowed("h.example", "/jobs")
        finally:
            _robots.urllib.request.urlopen = real
            _robots._CACHE.clear()
            _robots._ALIAS.clear()
        self.assertEqual(v["state"], "refused")
        self.assertIsNot(v["sweep"], True)
        self.assertIsNot(a["allowed"], True)


class EveryCardDeclaresItsScript(unittest.TestCase):
    """The card-to-script link was never written down, so every check had to
    guess it — and guessing was wrong about one time in seven.

    **Three audits in two days tripped on a guessed correspondence.** A
    `decode("utf-8")` pattern that defined its own population and missed nine
    adapters. A `sweep()` in `francetravail.py` — the adapter's own function,
    nothing to do with the guard — counted as a guard call. And
    `jobivoire.md`, which names **no** script of its own: the only `.py` it
    mentions is `employtt.py`, in a cross-reference about entity escaping, so
    a name-matching check paired the card with the wrong adapter entirely.

    **Those are not three slips. They are three instances of one missing
    fact.** `<!-- script: -->` states it, beside the `<!-- hosts: -->` line
    that was already there, and this reads it without heuristics.

    **The guard runs both ways**, because each direction catches a different
    accident:

      * a declaration naming a file that does not exist — a rename, a typo;
      * an adapter no card declares — a board shipped without its card
        pointing at it, which is exactly what `jobivoire` was.

    Tooling is named here rather than pattern-matched: a rule that excluded
    "anything not looking like a board" would quietly excuse a real adapter
    the day one is named like a utility.
    """

    TOOLING = frozenset({
        "ledger.py", "employers.py", "dormant.py", "achievements.py",
        "board_offer.py", "tenant_offer.py",
    })

    def _paths(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return (os.path.join(root, "shared", "boards"),
                os.path.join(root, "skills", "job-scan", "scripts"))

    def _declared(self):
        import glob
        import re
        cards, _ = self._paths()
        out = {}
        for path in sorted(glob.glob(os.path.join(cards, "*.md"))):
            name = os.path.basename(path)
            if name.lower() == "readme.md":
                continue
            with open(path, encoding="utf-8") as fh:
                head = fh.read(4000)
            m = re.search(r"<!--\s*script:\s*([a-z0-9_]+\.py)\s*-->", head)
            if m:
                out.setdefault(m.group(1), []).append(name)
        return out

    def _adapters(self):
        import glob
        _, scripts = self._paths()
        return {os.path.basename(p)
                for p in glob.glob(os.path.join(scripts, "*.py"))
                if not os.path.basename(p).startswith("_")} - self.TOOLING

    def test_every_declaration_names_a_file_that_exists(self):
        import glob
        _, scripts = self._paths()
        present = {os.path.basename(p)
                   for p in glob.glob(os.path.join(scripts, "*.py"))}
        missing = sorted(s for s in self._declared() if s not in present)
        self.assertEqual(missing, [],
                         "cards declare scripts that are not there: "
                         + ", ".join(missing))

    def test_every_adapter_is_declared_by_some_card(self):
        """**The direction that would have caught `jobivoire`.** Its adapter
        existed and shipped; no card pointed at it, so nothing could find the
        pair except by guessing the name."""
        declared = set(self._declared())
        orphans = sorted(self._adapters() - declared)
        self.assertEqual(orphans, [],
                         "these adapters are declared by no card, so any "
                         "check must guess the link: " + ", ".join(orphans))

    def test_the_declarations_are_enough_to_pair_without_guessing(self):
        """A shared adapter may be declared by several cards — `ats.py` serves
        seven — and that is the point: **the fact is written, so nothing has
        to infer it.**"""
        declared = self._declared()
        self.assertGreater(len(declared), 50)
        shared = {k: v for k, v in declared.items() if len(v) > 1}
        self.assertIn("ats.py", shared,
                      "ats.py serves several boards; if no card pairs with "
                      "it more than once the declarations have drifted")


class TheCredentialNoteKeepsItsBlock(unittest.TestCase):
    """`missing_note()` indented only the first credential it listed.

    The variable names were joined with a bare newline and then interpolated
    after eight spaces, so **the f-string indented the first line and every
    later one started at column 0**, falling out of the block a reader is
    meant to copy.

    **A single credential cannot show this** — there is no second line. The
    two that can are `ADZUNA_APP_ID`/`ADZUNA_APP_KEY` and France Travail's
    pair: **the two messages whose entire point is that both values are
    needed.** So the specimen here has two, and one with a single name is
    kept beside it to say why it proves nothing alone.

    It matters more than a layout slip because of where it sits. The same
    measurement established that `missing_note()` goes to **stderr with exit
    2 and an empty stdout**, and that no documented invocation redirects
    stderr — so **there is no silent failure here**: a wrong key gives a named
    401, not an empty board. **This message is the user's only recovery, and
    half its content was leaving the block.**
    """

    def _indents(self, names):
        import _secrets
        note = _secrets.missing_note(names, "x", "X Service", "see the card")
        return [len(ln) - len(ln.lstrip())
                for ln in note.split("\n")
                if "=" in ln and ln.strip().endswith("\u2026")]

    def test_two_credentials_are_both_inside_the_block(self):
        got = self._indents(["ADZUNA_APP_ID", "ADZUNA_APP_KEY"])
        self.assertEqual(len(got), 2, "the specimen must list two names or "
                                      "it cannot catch this")
        self.assertEqual(got, [got[0]] * 2,
                         f"the credentials are indented {got} — a later line "
                         f"left the block the reader is told to copy")
        self.assertGreater(got[0], 0, "the block is not indented at all")

    def test_a_single_credential_agrees_and_proves_nothing_alone(self):
        """Kept and labelled: this passes on the defect."""
        self.assertEqual(len(self._indents(["LBA_API_KEY"])), 1)

    def test_it_still_gives_both_routes(self):
        """**Prescribing a shell command to somebody without a shell is not
        help**, so the note carries a file route and a terminal route. A fix
        to the layout must not cost one of them."""
        import _secrets
        note = _secrets.missing_note(["A_KEY"], "svc", "X", "y")
        self.assertIn("credentials.env", note)
        self.assertIn("set -a", note)
        self.assertIn("config.yml", note)


class DocumentedInvocationsAreReal(unittest.TestCase):
    """Every board card documents how to run its adapter. Nothing compared
    that with what the script accepts.

    **Re-verifying a board means running its adapter**, and seventy adapters
    cannot be run for an internal check. **But half of it needs no request at
    all**: `argparse` states what a script accepts and the card asserts what
    to type.

    Read from the **AST**, never by importing or by `--help` — importing an
    adapter executes its module-level code, and a check should not have to run
    the thing it checks.

    **This guard shipped in v1.210.0 seeing less than half of what it claimed
    to check**, and the correction is the point:

      * **Invocations through a shell variable were invisible.** 29 cards
        write `S=…/board.py` and then `python3 $S search …`, which never
        contains the filename. **109 command lines, unchecked, reported as
        checked.** Aliases assigned in the same block are resolved now.
      * **Options can be built in a loop too, not only subcommands.**
        `computrabajo.py` adds one per entry of `FORBIDDEN`, so `--sal` is
        real and the AST cannot see it. It was reported as a defect in a card
        whose command works verbatim.
      * **A pipe is not an argument.** `python3 $S provincias | head -5` was
        read as passing `-5`.

    **Prose is not an invocation either.** The first pass produced four
    findings and all four were its own. Only lines beginning as a command,
    with any `#` tail and any pipe removed, are read.

    What cannot be checked is counted rather than hidden — the count is
    asserted below, so this cannot go quiet by drifting to zero.
    """

    LOOSE = ("--help", "-h")

    def _shape(self, path):
        """Subcommands, options, and whether either is built in a loop."""
        import ast
        tree = ast.parse(open(path, encoding="utf-8").read())
        subs, opts = set(), set()
        dyn_sub = dyn_opt = False
        for n in ast.walk(tree):
            if not (isinstance(n, ast.Call)
                    and isinstance(n.func, ast.Attribute)):
                continue
            if n.func.attr == "add_parser" and n.args:
                if isinstance(n.args[0], ast.Constant):
                    subs.add(n.args[0].value)
                else:
                    dyn_sub = True
            elif n.func.attr == "add_argument":
                lits = [a.value for a in n.args
                        if isinstance(a, ast.Constant)
                        and isinstance(a.value, str)]
                if n.args and not lits:
                    dyn_opt = True
                for v in lits:
                    if v.startswith("-"):
                        opts.add(v)
        return subs, opts, dyn_sub, dyn_opt

    def _commands(self, text, script):
        """Command lines naming the script, or a shell variable assigned to
        it earlier in the same fenced block."""
        import re as _re
        out = []
        for m in _re.finditer(r"```[a-z]*\n(.*?)```", text, _re.S):
            block = m.group(1).replace("\\\n", " ")
            aliases = {a.group(1) for a in _re.finditer(
                r"^\s*([A-Za-z_][A-Za-z0-9_]*)=\S*?" + _re.escape(script)
                + r"\s*$", block, _re.M)}
            for line in block.split("\n"):
                line = line.split("#", 1)[0]
                line = line.split("|", 1)[0].strip()   # a pipe is not an arg
                tail = None
                if script in line and _re.match(
                        r"^(python3?|\$|)\s*[\"']?\S*" + _re.escape(script),
                        line):
                    tail = line.split(script, 1)[1]
                else:
                    for v in aliases:
                        mm = _re.match(
                            r"^python3?\s+[\"']?\$\{?" + v + r"\}?[\"']?(.*)$",
                            line)
                        if mm:
                            tail = mm.group(1)
                            break
                if tail is None:
                    continue
                sub, opts = None, []
                for tok in tail.replace('"', " ").split():
                    if tok.startswith("-"):
                        opts.append(tok.split("=")[0])
                    elif sub is None and not opts and _re.fullmatch(
                            r"[a-z][a-z0-9-]*", tok):
                        sub = tok
                if sub or opts:
                    out.append((sub, opts, line[:74]))
        return out

    def _walk(self):
        import glob
        import re as _re
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cards = os.path.join(root, "shared", "boards")
        scripts = os.path.join(root, "skills", "job-scan", "scripts")
        bad, checked, skipped, with_cmd = [], 0, 0, 0
        for path in sorted(glob.glob(os.path.join(cards, "*.md"))):
            if os.path.basename(path).lower() == "readme.md":
                continue
            text = open(path, encoding="utf-8").read()
            m = _re.search(r"<!--\s*script:\s*([a-z0-9_]+\.py)\s*-->", text)
            if not m:
                continue
            sp = os.path.join(scripts, m.group(1))
            if not os.path.exists(sp):
                continue          # the declaration guard owns that failure
            subs, opts, dyn_sub, dyn_opt = self._shape(sp)
            card = os.path.basename(path)[:-3]
            cmds = self._commands(text, m.group(1))
            if cmds:
                with_cmd += 1
            for sub, used, raw in cmds:
                if sub is not None:
                    if dyn_sub:
                        skipped += 1
                    else:
                        checked += 1
                        if sub not in subs:
                            bad.append(f"{card}: {m.group(1)} has no "
                                       f"subcommand `{sub}` "
                                       f"(has {sorted(subs)}) — {raw}")
                for o in used:
                    if o in self.LOOSE:
                        continue
                    if dyn_opt:
                        skipped += 1
                        continue
                    checked += 1
                    if o not in opts:
                        bad.append(f"{card}: {m.group(1)} has no option "
                                   f"`{o}` — {raw}")
        return bad, checked, skipped, with_cmd

    def test_every_documented_subcommand_and_option_exists(self):
        bad, checked, _skipped, _n = self._walk()
        self.assertGreater(checked, 350,
                           f"only {checked} checks ran — the card format "
                           f"changed and this went quiet")
        self.assertEqual(bad, [], "\n".join(bad[:6]))

    def test_the_shell_variable_form_is_read(self):
        """**The hole that shipped.** 29 cards invoke through `$S`; if this
        stops resolving, a third of the corpus goes unchecked in silence and
        the count above still looks healthy."""
        _bad, _checked, _skipped, with_cmd = self._walk()
        self.assertGreater(with_cmd, 55,
                           f"only {with_cmd} cards were seen to carry an "
                           f"invocation — the `$S` form is not resolving")


class TheSharedBoardSaysWhichOneItRead(unittest.TestCase):
    """`jobup.py` serves two boards and defaulted to one of them in silence.

    `--site` carried `default="jobup"`, so somebody who had enabled **jobs.ch**
    and typed the general form got twenty **jobup.ch** advertisements, HTTP
    200, no warning. The `ledger_id` prefix was the only tell, **and it is in
    the JSON, not in the message** — the reader of a sweep reads the message.

    **And the tag lied in the other direction too.** `note()` printed
    `[jobup]` unconditionally, so `--site jobs-ch` announced its twenty
    advertisements under the other board's name while the records themselves
    carried `jobs-ch:` ids and `www.jobs.ch` URLs. **The data was right and
    every sentence about it was wrong.**

    **The default is kept and no longer silent.** Making `--site` required
    would have been the other repair, and it would have invalidated the
    invocations `jobup.md` documents — two days after establishing that the
    documented invocations are all valid.

    **The announcement fires only when nobody chose.** A warning on correct
    use is noise, so the quiet case is asserted too: without it this cannot
    tell *"announces"* from *"announces when it should"*.
    """

    def _parser(self):
        import jobup
        return jobup

    def test_the_flag_does_not_carry_its_own_default(self):
        """`argparse` cannot distinguish a chosen `jobup` from an unchosen one
        if the default is the value. It has to arrive as `None`."""
        jobup = self._parser()
        p = jobup.build() if hasattr(jobup, "build") else None
        if p is None:
            import re
            src = open(jobup.__file__, encoding="utf-8").read()
            i = src.index('add_argument("--site"')
            call = src[i:src.index("\n\n", i)]
            self.assertIn("default=None", call)
            self.assertNotIn('default="jobup"', call)

    def test_the_default_is_named_once(self):
        jobup = self._parser()
        self.assertEqual(jobup.DEFAULT_SITE, "jobup")
        self.assertIn(jobup.DEFAULT_SITE, jobup.SITES)

    def test_the_tag_follows_the_site(self):
        """`[jobup]` over twenty jobs.ch advertisements is the defect this
        catches — the records were always right."""
        import io
        import contextlib
        jobup = self._parser()
        before = jobup._TAG
        try:
            for name in sorted(jobup.SITES):
                jobup._TAG = name
                err = io.StringIO()
                with contextlib.redirect_stderr(err):
                    jobup.note("x")
                self.assertEqual(err.getvalue().strip(), f"[{name}] x")
        finally:
            jobup._TAG = before

    def test_the_default_announces_itself(self):
        """`resolve_site(None)` is somebody who typed the general form."""
        jobup = self._parser()
        site, said = jobup.resolve_site(None)
        self.assertEqual(site, jobup.DEFAULT_SITE)
        self.assertIsNotNone(said, "the default no longer announces itself")
        self.assertIn(jobup.SITES[jobup.DEFAULT_SITE]["host"], said)
        self.assertIn("--site", said)
        for name in jobup.SITES:
            self.assertIn(name, said,
                          "the line does not name the board the reader might "
                          "have meant — a warning that does not say what to "
                          "do instead is half a warning")

    def test_a_chosen_site_is_not_announced(self):
        """**The witness, and its first version could not fail.**

        It asserted that the `note(` call sat between two markers in the
        source. Nesting `if True:` inside that span fires the announcement on
        every run and **leaves the text exactly where the check looked** — the
        suite stayed green while every correct invocation was warned at. It
        was reading position, not condition.

        `resolve_site` returns the message instead of printing it, so the
        condition is the value and both cases can be compared.
        """
        jobup = self._parser()
        for name in sorted(jobup.SITES):
            site, said = jobup.resolve_site(name)
            self.assertEqual(site, name)
            self.assertIsNone(said,
                              f"--site {name} was chosen explicitly and still "
                              f"drew a warning — a warning on correct use is "
                              f"the noise this was avoiding")


class TheRefusedSearchIsRefusedInFact(unittest.TestCase):
    """`_hiringcafe` centralises the refusal so three commands cannot say
    three different things. **Nothing exercised it** — the module was never
    named in this suite, and renaming `search_url` away left the suite green.

    The corpus scan next door asserts that no adapter assembles the refused
    URL itself, which is a statement about **text across 65 files** and is
    right to be. It says nothing about whether the one place that may build
    it actually refuses to fetch it.

    **Collection is suspended by decision, not by accident** — no request to
    that host in any form, even on the paths its own file allows. So this
    exercises the refusal with an opener that fails the case if it is ever
    reached.
    """

    def test_the_search_mode_refuses_and_makes_no_request(self):
        import hiringcafe

        def forbidden(*a, **k):
            raise AssertionError(
                "hiringcafe.py opened a socket — collection is suspended and "
                "no request to that host is permitted in any form")

        real = hiringcafe.urllib.request.urlopen
        hiringcafe.urllib.request.urlopen = forbidden
        code, said = None, ""
        try:
            import subprocess
            import sys as _sys
            out = subprocess.run(
                [_sys.executable, os.path.join(SCRIPTS, "hiringcafe.py"),
                 "search", "--query", "x", "--country", "CH"],
                capture_output=True, text=True, timeout=60)
            code, said = out.returncode, out.stderr
        except AssertionError:
            raise
        finally:
            hiringcafe.urllib.request.urlopen = real
        self.assertEqual(code, 7,
                         f"the refused search did not exit 7 (got {code!r} "
                         f"{said[:60]})")

    def test_the_refusal_quotes_the_rule_and_the_date(self):
        """**A refusal that does not say what refused it invites a retry.**"""
        import _hiringcafe
        said = _hiringcafe.refusal("x", "this search")
        self.assertIn("robots.txt", said)
        self.assertIn(_hiringcafe.MEASURED_ON, said)
        self.assertIn("No request was made", said)

    def test_the_constructor_is_the_only_place_that_builds_it(self):
        """Kept as the corpus half, beside the exercised one — **the scan
        covers 65 files, the case above covers one command.**"""
        import _hiringcafe
        url = _hiringcafe.search_url({"searchState": "{}"})
        self.assertTrue(url.startswith(_hiringcafe.BASE))
        self.assertIn("searchState", url)


class PresenceIsNotBehaviour(unittest.TestCase):
    """Four guards asserted that a token appeared in a file and reported a
    behaviour. **Each could be neutralised without moving the text it looked
    for**, and each reinstates a defect this repository had already shipped a
    fix for.

    | guard | how it stayed green |
    | :-- | :-- |
    | `_tls` is routed | import kept, `context=None` passed to `urlopen` |
    | the declared agent is sent | `_ua` imported, a Chrome string in the header |
    | the SmartRecruiters gate exists | the gate's body replaced by `return True` |
    | that gate refuses | `if not allowed:` replaced by `if False:` |

    **A guard that reads presence cannot see intent.** The import is there,
    the header key is there, the call is there — and none of them does
    anything. These cases exercise the code instead, on stubbed sockets, so no
    request leaves the machine.
    """

    def _capture(self, module):
        """Run the module's fetch against a stubbed opener and hand back the
        `Request` and the keyword arguments it was called with."""
        seen = {}

        def fake(req, *a, **kw):
            seen["req"] = req
            seen["kw"] = kw
            raise module.urllib.error.URLError("stubbed")

        return seen, fake

    def test_every_adapter_that_uses_tls_actually_passes_the_context(self):
        """**One specimen does not cover a corpus, and this is the proof.**

        The case below exercises `oposiciones.py` and says nothing about the
        other reader of the same host. `empleate.py` could be given
        `context=None` — reinstating #104 on the adapter #104 was *opened*
        for — and the suite stayed green: the corpus scan sees the import, the
        exercised case sees the wrong file.

        Three files use `_tls`; two of them are adapters. Exercising both
        costs a loop.
        """
        import glob
        import re
        import importlib
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        scripts = os.path.join(root, "skills", "job-scan", "scripts")
        users = []
        for path in sorted(glob.glob(os.path.join(scripts, "*.py"))):
            name = os.path.basename(path)
            if name.startswith("_"):
                continue
            src = open(path, encoding="utf-8").read()
            if re.search(r"(^|\n)\s*import _tls", src):
                users.append(name[:-3])
        self.assertGreaterEqual(len(users), 2,
                                "the adapters using _tls have vanished — "
                                "either a real change or this went quiet")

        for mod_name in users:
            with self.subTest(adapter=mod_name):
                mod = importlib.import_module(mod_name)
                seen, fake = self._capture(mod)
                real = mod.urllib.request.urlopen
                gate = getattr(mod, "_robots_gate", None)
                mod.urllib.request.urlopen = fake
                real_sleep = getattr(mod, "time", None)
                if real_sleep is not None:
                    slept = mod.time.sleep
                    mod.time.sleep = lambda *_a, **_k: None
                if gate:
                    setattr(mod, "_robots_gate", lambda *a, **k: None)
                try:
                    fn = getattr(mod, "fetch", None) or getattr(mod, "get")
                    try:
                        fn("https://empleate.gob.es/x")
                    except BaseException:
                        pass
                finally:
                    mod.urllib.request.urlopen = real
                    if real_sleep is not None:
                        mod.time.sleep = slept
                    if gate:
                        setattr(mod, "_robots_gate", gate)
                self.assertIn("kw", seen,
                              f"{mod_name}: never reached the opener")
                self.assertIsNotNone(
                    seen["kw"].get("context"),
                    f"{mod_name} sent the request with no TLS context — "
                    f"`_tls` is imported and not applied, which is #104")

    def test_a_tls_host_is_fetched_with_the_tls_context(self):
        """#104 again: `context=None` restores the failure `_tls` exists to
        remove, and the import stays in place while it does."""
        import oposiciones
        import _tls
        seen, fake = self._capture(oposiciones)
        real = oposiciones.urllib.request.urlopen
        real_gate = getattr(oposiciones, "_robots_gate", None)
        oposiciones.urllib.request.urlopen = fake
        if real_gate:
            oposiciones._robots_gate = lambda *a, **k: None
        try:
            try:
                oposiciones.fetch(
                    "https://empleate.gob.es/empleate/open/x", retries=0)
            except BaseException:
                pass
        finally:
            oposiciones.urllib.request.urlopen = real
            if real_gate:
                oposiciones._robots_gate = real_gate
        self.assertIn("kw", seen, "fetch() never reached the opener")
        ctx = seen["kw"].get("context")
        self.assertIsNotNone(
            ctx, "the request went out with no TLS context — `_tls` is "
                 "imported and not applied, which is #104 exactly")
        self.assertIsNotNone(_tls.context_for("empleate.gob.es"))

    def test_the_declared_agent_is_the_one_on_the_wire(self):
        """#120 again: the header key is what the old guard checked, and the
        value is what the operator reads."""
        import adecco
        import _ua
        seen, fake = self._capture(adecco)
        real = adecco.urllib.request.urlopen
        real_gate = adecco._robots_gate
        adecco.urllib.request.urlopen = fake
        adecco._robots_gate = lambda *a, **k: None   # the guard is elsewhere
        try:
            try:
                adecco.get("https://www.adecco.fr/", retries=0)
            except BaseException:
                pass
        finally:
            adecco.urllib.request.urlopen = real
            adecco._robots_gate = real_gate
        self.assertIn("req", seen, "fetch() never reached the opener")
        sent = seen["req"].get_header("User-agent")
        self.assertEqual(sent, _ua.UA,
                         f"the wire carries {sent!r}, not the declared "
                         f"agent — a token declared and not sent is worse "
                         f"than one never declared")

    def test_the_smartrecruiters_gate_refuses_when_it_should(self):
        """#121 again. The gate may be called, may exist, and may do nothing:
        `return True` in its body, or `if False:` where it decides, both left
        the suite green."""
        import ats
        calls = {"died": 0}
        real_verdict = ats.robots_verdict
        real_die = ats.die
        real_cfg = getattr(ats, "override_enabled", None)

        def refused(host):
            return {"sweep": False, "certain": True,
                    "reason": "User-agent: * / Disallow: /"}

        def die(msg, code=2):
            calls["died"] += 1
            raise SystemExit(code)

        ats.robots_verdict = refused
        ats.die = die
        if real_cfg is not None:
            ats.override_enabled = lambda *a, **k: False
        try:
            try:
                ats.smartrecruiters_gate()
            except SystemExit:
                pass
        finally:
            ats.robots_verdict = real_verdict
            ats.die = real_die
            if real_cfg is not None:
                ats.override_enabled = real_cfg
        self.assertEqual(calls["died"], 1,
                         "the host refuses and no override is enabled, and "
                         "the gate let the run continue")


class PartialStillWritesWhatItKept(unittest.TestCase):
    """`jobup.py search` announced rows on stderr and put none on stdout.

    When page 2 repeats page 1 entirely the sweep stops rather than looping —
    a good guard, and the diagnosis was right. But it stopped with
    `sys.exit(EXIT_PARTIAL)` **inside the page loop**, above the print stage,
    so the run said *"6 row(s) so far and they are good"* and wrote nothing.
    **Total and silent for anything reading stdout**, which is the whole
    chain. Reproduced twice on 2026-09-04, exit 6, `wc -l` 0. Issue #134.

    **Two exits left the same loop and only one of them worked.** The other,
    for a page with no postings, uses `break` and reaches the print. The
    difference was invisible because both printed a correct sentence first.

    **It was the only one.** Thirteen functions in the corpus exit inside a
    loop before their last `print`; eight of those claim to hold rows; two
    carry this very sentence — `philjobnet.py` and `jobivoire.py` — and both
    **print inside the loop**, so their rows are already out when they leave.
    A `die()` on a bad department code or a 404 is not this defect either.
    Same shape, different case, four times over.
    """

    class _Page:
        """One posting, returned for every page — which is what a board that
        has stopped paginating looks like."""

        BODY = ('<html><script type="application/ld+json">'
                '{"@type":"JobPosting","identifier":{"value":"abc-1"},'
                '"title":"X","hiringOrganization":{"name":"Y"},'
                '"datePosted":"2026-09-01",'
                '"url":"https://www.jobup.ch/fr/emplois/detail/abc-1/"}'
                '</script></html>')

    def _run(self, pages):
        import io
        import contextlib
        import jobup
        real_get = jobup.get
        real_gate = jobup.robots_verdict
        real_sleep = jobup.time.sleep
        jobup.get = lambda url: (200, self._Page.BODY, url)
        jobup.robots_verdict = lambda h: {"sweep": True, "certain": True,
                                          "reason": ""}
        jobup.time.sleep = lambda *a, **k: None
        args = argparse.Namespace(
            site="jobup", term="x", location=None, pages=pages, limit=None,
            delay=0)
        out, err = io.StringIO(), io.StringIO()
        code = None
        try:
            with contextlib.redirect_stdout(out), \
                    contextlib.redirect_stderr(err):
                jobup.cmd_search(args)
        except SystemExit as exc:
            code = exc.code
        finally:
            jobup.get = real_get
            jobup.robots_verdict = real_gate
            jobup.time.sleep = real_sleep
        return code, out.getvalue(), err.getvalue()

    def test_the_repeated_page_still_writes_its_rows(self):
        code, out, err = self._run(pages=2)
        self.assertIn("pagination did not advance", err,
                      "the fixture did not reach the partial branch")
        rows = [l for l in out.splitlines() if l.strip()]
        self.assertEqual(
            len(rows), 1,
            f"stderr announced rows and stdout carried {len(rows)} — this is "
            f"#134: the exit skipped the print stage")
        self.assertEqual(code, 6, "the partial status was lost with the fix")

    def test_the_row_on_stdout_is_the_row_it_counted(self):
        """**A count on stderr and a row on stdout must be the same thing.**
        Writing *some* row would satisfy the case above."""
        import json
        _code, out, err = self._run(pages=2)
        row = json.loads(out.splitlines()[0])
        self.assertEqual(row["id"], "abc-1")
        self.assertIn("1 row(s) so far", err)

    def test_a_normal_run_is_unchanged(self):
        """The witness: one page, no repetition, no partial status."""
        code, out, _err = self._run(pages=1)
        self.assertIsNone(code, "a complete run must not exit 6")
        self.assertEqual(len([l for l in out.splitlines() if l.strip()]), 1)


class EveryCardDeclaresItsCountries(unittest.TestCase):
    """Nothing in this repository said which country a board serves.

    The Atlas publishes a coverage figure per country and was **held by
    hand**, because there was no source to read: a card declared `verified`,
    `hosts` and `script`, and never a country. Two countries were published at
    0% while their adapter sat in `scripts/` — not a typo, an **absent link**.
    Only 29 of 85 cards named a country in their opening, in prose.

    **The pairing is the point, not the country.**

      * `script` **and** `countries` — a board that is covered, and where.
      * `countries` **without** `script` — assessed, no adapter. Ten cards,
        and `chile-public-sector.md` is the model: *"Five Chilean portals were
        assessed… none of them yields one."* **`CL` with no adapter is a fact
        the Atlas needs**, and publishing Chile as uncovered is then correct
        rather than an oversight.
      * `script` **without** `countries` — the hole this guard closes.

    **`*` is not a country and not a blank.** It says the adapter is not
    country-scoped: an ATS where the tenant decides, or a global board.
    Twenty-three cards carry it, and inventing a country for them would be
    exactly the error this replaces.

    **Every value was read off its own card**, one by one — a title or an
    opening sentence. A first pass tried to extract them from the first 1200
    characters and produced seven countries for Singapore's national portal
    and eight for the Philippines', because a card's opening compares it to
    other boards. **A map written by hand is not evidence either**; that is
    how `<!-- script: icims.py -->` came to sit on a card with no adapter.
    Both failures are why this is card-by-card and paired with a check.
    """

    # ISO 3166-1 alpha-2, the codes this corpus actually uses. Listed rather
    # than pattern-matched: `ZZ` matches a two-letter pattern and is not a
    # country, and the Atlas would carry it silently.
    # **The complete ISO 3166-1 alpha-2 set, not the subset in use.**
    # It was the subset until 2026-09-04, and the first card to cover a
    # country nobody had covered — Chad, `TD` — failed this guard for
    # being right. A list that must be edited to accept a correct value
    # punishes the case it exists to encourage. Enumerated rather than
    # pattern-matched, which is the part that matters: `ZZ` matches a
    # two-letter pattern and is not a country.
    ISO = frozenset("""
        AD AE AF AG AI AL AM AO AQ AR AS AT AU AW AX AZ BA BB BD BE BF BG BH
        BI BJ BL BM BN BO BQ BR BS BT BV BW BY BZ CA CC CD CF CG CH CI CK CL
        CM CN CO CR CU CV CW CX CY CZ DE DJ DK DM DO DZ EC EE EG EH ER ES ET
        FI FJ FK FM FO FR GA GB GD GE GF GG GH GI GL GM GN GP GQ GR GS GT GU
        GW GY HK HM HN HR HT HU ID IE IL IM IN IO IQ IR IS IT JE JM JO JP KE
        KG KH KI KM KN KP KR KW KY KZ LA LB LC LI LK LR LS LT LU LV LY MA MC
        MD ME MF MG MH MK ML MM MN MO MP MQ MR MS MT MU MV MW MX MY MZ NA NC
        NE NF NG NI NL NO NP NR NU NZ OM PA PE PF PG PH PK PL PM PN PR PS PT
        PW PY QA RE RO RS RU RW SA SB SC SD SE SG SH SI SJ SK SL SM SN SO SR
        SS ST SV SX SY SZ TC TD TF TG TH TJ TK TL TM TN TO TR TT TV TW TZ UA
        UG UM US UY UZ VA VC VE VG VI VN VU WF WS YE YT ZA ZM ZW
    """.split())

    def _cards(self):
        import glob
        import re
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        out = {}
        for path in sorted(glob.glob(os.path.join(root, "shared", "boards",
                                                  "*.md"))):
            name = os.path.basename(path)
            if name.lower() == "readme.md":
                continue
            with open(path, encoding="utf-8") as fh:
                head = fh.read(4000)
            co = re.search(r"<!--\s*countries:\s*(.+?)\s*-->", head)
            sc = re.search(r"<!--\s*script:\s*([a-z0-9_]+\.py)\s*-->", head)
            out[name[:-3]] = (co.group(1) if co else None,
                              sc.group(1) if sc else None)
        return out

    def test_every_declared_code_is_a_real_one(self):
        bad = []
        for card, (countries, _sc) in self._cards().items():
            if countries is None:
                continue
            for code in countries.split():
                if code == "*":
                    continue
                if code not in self.ISO:
                    bad.append(f"{card}: {code}")
        self.assertEqual(bad, [], "not ISO 3166-1 alpha-2: " + ", ".join(bad))

    def test_a_card_with_an_adapter_says_where_it_reaches(self):
        """**The direction that closes the Atlas hole.** A board shipped
        without this is a country published as uncovered while its adapter
        sits in `scripts/`."""
        silent = sorted(c for c, (co, sc) in self._cards().items()
                        if sc and not co)
        self.assertEqual(silent, [],
                         "these declare an adapter and no countries, so "
                         "nothing can tell what they cover: "
                         + ", ".join(silent))

    def test_the_star_is_not_mixed_with_countries(self):
        """`* FR` would mean both *"not country-scoped"* and *"France"*. A
        reader would take one and the Atlas the other."""
        mixed = []
        for card, (countries, _sc) in self._cards().items():
            if countries and "*" in countries.split() \
                    and len(countries.split()) > 1:
                mixed.append(card)
        self.assertEqual(mixed, [], "`*` mixed with codes: " + ", ".join(mixed))

    def test_the_declarations_cover_the_corpus(self):
        """**The floor**, so the population cannot empty in silence — the
        defect found in two of this suite's own guards on 2026-09-04."""
        cards = self._cards()
        self.assertGreater(len(cards), 80)
        declared = [c for c, (co, _s) in cards.items() if co]
        self.assertEqual(len(declared), len(cards),
                         f"only {len(declared)} of {len(cards)} cards declare "
                         f"countries — declared everywhere or an absence is "
                         f"not a signal")


class TheDeclaredDuplicateIsALedgerId(unittest.TestCase):
    """Three adapters publish the other board's own id, and the skill read
    none of them.

    `job-room`, `France Travail` and `La Bonne Alternance` syndicate ads from
    boards this plugin already sweeps, and each emits `duplicate_of` **in the
    ledger's namespace** — `jobup:<uuid>` beside its own `job-room:<uuid>`.
    `francetravail.py` states the intended conduct in its source: *"When it is
    set and the ledger already holds that row, this is the same posting —
    record it discarded naming the row."*

    **`SKILL.md` said the employer's name was the only signal available at
    scan time.** On one sweep of 497 job-room rows, **20 offered duplicates
    went through**, one of them already at status `applied`. Nothing stopped
    it until the ledger refused an id it already held — *after* it had been
    scored and listed as a find. #136.

    **And the employer fallback cannot cover those rows.** For a syndicated
    ad job-room writes the *syndicating board* as the employer — `Jobup` —
    while the ledger holds the real employer's legal name. No common
    substring in either direction: the two checks fail on different things.

    The value is only useful if it really is a ledger id, so that is what
    this exercises.
    """

    def test_the_value_is_a_ledger_id_not_a_url(self):
        import jobroom
        got = jobroom.duplicate_of(
            "https://www.jobup.ch/fr/emplois/detail/"
            "3fa85f64-5717-4562-b3fc-2c963f66afa6/")
        self.assertEqual(got, "jobup:3fa85f64-5717-4562-b3fc-2c963f66afa6")
        self.assertNotIn("/", got, "a URL cannot be looked up in the ledger")
        self.assertEqual(got.count(":"), 1)

    def test_a_host_this_plugin_does_not_sweep_yields_nothing(self):
        """**A duplicate of an ad we never held is not a duplicate.** Naming
        a board outside the ledger would produce a key that can never match,
        which reads like a working check and is not one."""
        import jobroom
        # **With a real UUID on it**, so the None can only come from the host
        # being unknown. The first version of this case used a URL with no
        # UUID and passed for that reason instead — it could not have failed
        # on its own subject.
        with_uuid = ("https://www.example.invalid/offer/"
                     "3fa85f64-5717-4562-b3fc-2c963f66afa6")
        self.assertTrue(jobroom.UUID_RE.search(with_uuid),
                        "the specimen must carry a UUID or this proves "
                        "nothing about the host lookup")
        self.assertIsNone(jobroom.duplicate_of(with_uuid))
        self.assertIsNone(jobroom.duplicate_of(None))

    def test_a_scheme_less_url_still_resolves(self):
        """The field is built from whatever the feed carries, and the feed
        does not always carry a scheme."""
        import jobroom
        self.assertEqual(
            jobroom.duplicate_of(
                "www.jobup.ch/fr/emplois/detail/"
                "3fa85f64-5717-4562-b3fc-2c963f66afa6/"),
            "jobup:3fa85f64-5717-4562-b3fc-2c963f66afa6")

    def test_the_skill_reads_the_field_at_the_exclusion_step(self):
        """**The object here is the text of `SKILL.md`**, which is what a run
        follows — so reading it is the check, not a proxy for one. What it
        must say is that a row whose `duplicate_of` is in the exclusion set is
        excluded, *at step 3*, before scoring."""
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        skill = open(os.path.join(root, "skills", "job-scan", "SKILL.md"),
                     encoding="utf-8").read()
        self.assertIn("duplicate_of", skill,
                      "the skill does not mention the field three adapters "
                      "publish")
        i = skill.index("- Anything already in the exclusion set from step 0.")
        # **the bullet list only.** A 400-character window reached into the
        # section below, whose heading also names the field, so deleting the
        # bullet left this green — the window was the test's own blind spot.
        bullets = skill[i:skill.index("\n\n", i)]
        self.assertIn("duplicate_of", bullets,
                      "step 3 does not exclude on `duplicate_of` — the field "
                      "may be described further down and never acted on")

    def test_every_adapter_that_publishes_it_is_named_in_the_skill(self):
        """A fourth adapter emitting it and going unnamed is the same defect
        again, one board later."""
        import glob
        import re
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        scripts = os.path.join(root, "skills", "job-scan", "scripts")
        whole = open(os.path.join(root, "skills", "job-scan", "SKILL.md"),
                     encoding="utf-8").read()
        # **The section, not the file.** 58 of 74 adapter names appear
        # somewhere in this skill, so "named anywhere" is true by accident
        # about four times in five — the first version of this case could not
        # have failed.
        start = whole.index("### Cross-board duplicates")
        end = whole.index("\n## ", start)
        skill = whole[start:end].lower()
        emitters = []
        for path in sorted(glob.glob(os.path.join(scripts, "*.py"))):
            name = os.path.basename(path)
            if name.startswith("_"):
                continue
            if '"duplicate_of"' in open(path, encoding="utf-8").read():
                emitters.append(name[:-3])
        self.assertGreaterEqual(len(emitters), 3,
                                "the emitters have vanished — either a real "
                                "change or this went quiet")
        # the skill names boards in prose, so match on the board's own words
        WORDS = {"jobroom": "job-room", "francetravail": "france travail",
                 "labonnealternance": "la bonne alternance"}
        missing = [e for e in emitters
                   if WORDS.get(e, e.replace("_", " ")) not in skill]
        self.assertEqual(missing, [],
                         "these publish `duplicate_of` and the skill does "
                         "not name them: " + ", ".join(missing))


class ATestNamespaceMatchesTheRealParser(unittest.TestCase):
    """A case that builds `argparse.Namespace` by hand bypasses argparse.

    **Most of that is already caught, and measuring it was the point.**
    A field the code reads under a *wrong* name raises `AttributeError` —
    renaming `term` to `keyword` turns three cases red. And a drift in the CLI
    itself is caught elsewhere: renaming `--term` to `--query` breaks the
    invocations `jobup.md` documents, which
    `DocumentedInvocationsAreReal` sees. The subprocess-driven case is
    validated by argparse directly — driving `--what` where the CLI wants
    `--query --country` failed loudly while this suite was being written.

    A field *missing* from the namespace is caught too, for the same reason:
    dropping `delay` turns those three cases red.

    **One shape escapes all of it: an option the CLI gains that the fixture
    does not supply.** Measured on v1.221.0 — adding `--since` to the parser
    produced **zero failures**, while every real invocation would now carry a
    field the case never sets. So the case drifts from the CLI it stands for,
    quietly, in the one direction nothing was watching.

    *Establishing that took two bad mutations of my own.* The first `delay`
    mutation matched nothing — the fixture wraps across lines, so
    `", delay=0)"` is not in the file — and its green was read as a finding.
    The second comparison ran with the new guard already in the working tree,
    because `git checkout` carries uncommitted changes across branches. **Both
    readings were void, and the gap is the one that survived redoing them.**
    """

    def _dests(self, script, subcommand):
        """Every `dest` the parser defines, read from the AST."""
        import ast
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(root, "skills", "job-scan", "scripts", script)
        tree = ast.parse(open(path, encoding="utf-8").read())
        var = None
        for n in ast.walk(tree):
            if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call) \
                    and isinstance(n.value.func, ast.Attribute) \
                    and n.value.func.attr == "add_parser" \
                    and n.value.args \
                    and isinstance(n.value.args[0], ast.Constant) \
                    and n.value.args[0].value == subcommand:
                for t in n.targets:
                    if isinstance(t, ast.Name):
                        var = t.id
        self.assertIsNotNone(var, f"no `{subcommand}` subparser in {script}")
        out = set()
        for n in ast.walk(tree):
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                    and n.func.attr == "add_argument" \
                    and isinstance(n.func.value, ast.Name) \
                    and n.func.value.id == var:
                named = [a.value for a in n.args
                         if isinstance(a, ast.Constant)
                         and isinstance(a.value, str)]
                dest = next((kw.value.value for kw in n.keywords
                             if kw.arg == "dest"
                             and isinstance(kw.value, ast.Constant)), None)
                if dest:
                    out.add(dest)
                elif named:
                    out.add(named[0].lstrip("-").replace("-", "_"))
        return out

    def test_the_jobup_namespace_carries_every_option_the_cli_defines(self):
        dests = self._dests("jobup.py", "search")
        self.assertIn("term", dests, "the parser no longer defines --term, "
                                     "and the fixture below still passes it")
        built = {"site", "term", "location", "pages", "limit", "delay"}
        missing = sorted(dests - built)
        self.assertEqual(
            missing, [],
            f"PartialStillWritesWhatItKept builds a namespace without "
            f"{missing} — the CLI always supplies those, so the case is "
            f"exercising a shape no invocation can produce")

    def test_the_fixture_and_this_list_are_the_same_list(self):
        """**Two copies of one fact, and the case above compares the wrong
        one if they drift.** This reads the fixture's own namespace rather
        than trusting the literal repeated here."""
        import re
        src = open(os.path.abspath(__file__), encoding="utf-8").read()
        m = re.search(r"args = argparse\.Namespace\(\s*(.*?)\)", src, re.S)
        self.assertIsNotNone(m, "the fixture no longer builds a namespace")
        fields = set(re.findall(r"(\w+)=", m.group(1)))
        self.assertEqual(
            fields, {"site", "term", "location", "pages", "limit", "delay"},
            "the fixture's namespace changed and the list above did not")


class OneResolverForFilesAndKeys(unittest.TestCase):
    """`_secrets` resolved the workspace by a copy of `bin/workspace-path.py`
    with both of its guards left out.

    That file was written for #109 against one trap: **`$HOME` is not the
    person's folder outside a terminal — in CoWork it is a container's.** Its
    cascade takes a folder the user *named* first, then `JOB_HUNT_HOME`, then
    `<home>/Documents/job_applications` **only if `Documents` is writable**,
    and then refuses, with a question to put to the person.

    `_secrets._workspace()` had neither the first step nor the writability
    test. It took `JOB_HUNT_HOME`, else `Documents` **the moment it merely
    existed** — and a container has a `Documents`. So the credentials were
    read from a path the person will never see, and nothing failed. **A silent
    success, which is the failure #109 exists against.**

    It also mattered for a reason that had not been connected to it: of the
    three places a key may live, **the environment does not survive CoWork's
    shell reset (#110) and `~/.<name>.env` is inside the container (#109)**.
    The workspace file is the only one left, so the resolver that finds it is
    the whole path.

    **The hardening can stop finding a file that was being found**, and that
    is the case the last two cases here are about.
    """

    def _home(self, writable_docs=True, with_keys=False):
        """A throwaway home, so nothing here depends on this machine's."""
        import tempfile
        home = tempfile.mkdtemp()
        docs = os.path.join(home, "Documents")
        os.makedirs(os.path.join(docs, "job_applications"))
        if with_keys:
            with open(os.path.join(docs, "job_applications",
                                   "credentials.env"), "w") as fh:
                fh.write("ADZUNA_APP_ID=x\nADZUNA_APP_KEY=y\n")
        if not writable_docs:
            os.chmod(docs, 0o500)
            self.addCleanup(os.chmod, docs, 0o700)
        return home

    def _with_home(self, home):
        import importlib
        import _secrets
        keep = {k: os.environ.get(k) for k in
                ("HOME", "USERPROFILE", "JOB_HUNT_HOME",
                 "ADZUNA_APP_ID", "ADZUNA_APP_KEY")}

        def restore():
            for k, v in keep.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v
            importlib.reload(_secrets)

        self.addCleanup(restore)
        # **`~` is not resolved from `HOME` on Windows.** `expanduser` reads
        # `USERPROFILE` there, so setting only `HOME` left these cases looking
        # at the runner's real profile instead of the sandbox — two of the
        # three CI failures on this class. #143.
        os.environ["HOME"] = home
        os.environ["USERPROFILE"] = home
        for k in ("JOB_HUNT_HOME", "ADZUNA_APP_ID", "ADZUNA_APP_KEY"):
            os.environ.pop(k, None)
        importlib.reload(_secrets)
        return _secrets

    def test_the_two_resolvers_agree(self):
        """**The convergence itself.** Not that `_secrets` has a cascade — that
        it has *the* cascade, the one the files use."""
        import importlib.util
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        wp = os.path.join(root, "bin", "workspace-path.py")
        spec = importlib.util.spec_from_file_location("_wp_check", wp)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        home = self._home(writable_docs=True)
        sec = self._with_home(home)
        self.assertEqual(sec._workspace(), mod.resolve()[0])

    def _needs_posix_permissions(self):
        """**`chmod 500` does not make a directory unwritable on Windows, and
        `os.access(dir, W_OK)` does not report the truth about directories
        there.** So the fixture cannot produce the state these cases are
        about, and a version of them that passed on Windows would be a guard
        that never exercises — the defect this suite found three times on
        2026-09-04, committed deliberately the fourth time.

        **Skipped with the reason rather than made green.** What #109's guard
        does under Windows is *not established*, and that is a question about
        the product, not about the test: it is #145, and this skip is where a
        reader meets it.
        """
        if os.name != "posix":
            self.skipTest(
                "chmod cannot create an unwritable directory here, and "
                "os.access is not authoritative on directories — see #145: "
                "whether #109's guard protects anything on Windows is "
                "unestablished, and this case cannot establish it")

    def test_an_unwritable_documents_settles_nothing(self):
        """**The guard `_secrets` was missing.** A container has a `Documents`
        too, so its existence proves nothing; not being able to write there is
        the evidence that this home is not the person's."""
        self._needs_posix_permissions()
        home = self._home(writable_docs=False)
        sec = self._with_home(home)
        self.assertIsNone(sec._workspace(),
                          "the workspace was guessed from a Documents this "
                          "process cannot write to — that is #109")

    def test_a_named_folder_wins(self):
        """Step 1, which `_secrets` could not receive at all — and the only
        step that works in a container."""
        import tempfile
        # **Not skipped off posix.** This asserts that a named folder wins
        # whatever the cascade would otherwise have chosen, which holds
        # wherever `expanduser` finds the sandbox — and it is the step that
        # matters in a container, so it should run on every runner.
        home = self._home(writable_docs=True)
        sec = self._with_home(home)
        named = tempfile.mkdtemp()
        self.assertEqual(sec._workspace(prefer=named), named)

    # ---- the hardening must not take a key away in silence -------------

    def test_a_stranded_credentials_file_is_named_out_loud(self):
        """**The regression this hardening can cause.** Somebody whose keys
        sit in `~/Documents/job_applications/credentials.env` on a Documents
        that is not writable was served before and is not served now: their
        setup works this evening and not after the release, without their
        having touched anything.

        The refusal stands — guessing is what #109 removed — **but it does not
        stand quietly**, and the sentence names the file."""
        self._needs_posix_permissions()
        home = self._home(writable_docs=False, with_keys=True)
        sec = self._with_home(home)
        note = sec.missing_note(["ADZUNA_APP_ID", "ADZUNA_APP_KEY"],
                                "adzuna", "Adzuna", "developer.adzuna.com")
        expected = os.path.join(home, "Documents", "job_applications",
                                "credentials.env")
        self.assertIn(expected, note,
                      "the file that stopped being read is not named — the "
                      "user cannot tell a lost key from a missing one")
        self.assertIn("no longer being read", note)
        self.assertIn("not lost", note)

    def test_it_says_nothing_when_nothing_is_stranded(self):
        """**The witness.** Without it the case above passes on a note that
        cries stranded on every run, which is the noise this avoids."""
        # **A workspace that resolves, and a file sitting in it.** The first
        # version used an unwritable Documents with no file, so the note came
        # back None whether or not the workspace was consulted — it could not
        # tell "checks first" from "does not check".
        home = self._home(writable_docs=True, with_keys=True)
        sec = self._with_home(home)
        self.assertIsNotNone(sec._workspace(),
                             "the fixture must resolve or this proves "
                             "nothing")
        self.assertIsNone(sec.stranded_note("adzuna"),
                          "nothing is stranded — the workspace resolved and "
                          "that file is the one being read")
        note = sec.missing_note(["NOT_A_REAL_KEY"], "adzuna", "X", "y")
        self.assertNotIn("no longer being read", note,
                         "a warning on a healthy install is the noise this "
                         "avoids")

    def test_the_ordinary_guidance_survives(self):
        """A stranded key must not cost the reader the two routes: **telling
        somebody without a shell to run `export` is not help.**"""
        self._needs_posix_permissions()
        home = self._home(writable_docs=False, with_keys=True)
        sec = self._with_home(home)
        note = sec.missing_note(["A_KEY"], "svc", "X", "y")
        for owed in ("credentials.env", "set -a", "config.yml"):
            self.assertIn(owed, note)


class TheSiblingVerdictIsRecordedOrAbsent(unittest.TestCase):
    """`siblings()` answers the apex/`www` question and nothing recorded its
    answer, so **86 hosts of 88 could not be told apart from "nobody looked"**.

    The doctrine is already right — `robots-policy.md` carries `jobindex.dk`,
    47 bytes of `Disallow: /` on the apex against 4 218 bytes of permissions
    on the `www`, and an adapter written against the wrong form never sees the
    refusal. **What was missing is the trace.** Issue #141.

    **No mass backfill, and that is measured rather than preferred.** Filling
    every card would be **172 requests over 86 pairs, about nine minutes**,
    with 5 of 12 sampled pairs taking over five seconds — and the expected
    yield is the measured 4%: two of 55 comparable hosts were two real rules
    files.

    **The decisive argument is the issue's own.** It requires the date because
    *"a twin that agreed on 3 September may diverge"*. A backfill stamps
    eighty-six markers with one date, so **they go stale together and become
    suspect together**, on a day nobody chose. Markers written as cards are
    written or touched are staggered, and each one dates the moment somebody
    was actually looking at that board.

    **So absence is meaningful and stays legal**: no marker means nobody
    looked, which is exactly the state #141 says must be distinguishable. What
    this guard forbids is a marker that says something it cannot support.
    """

    VERDICTS = frozenset({"agree", "differ", "disagree", "incomparable"})

    def _markers(self):
        import glob
        import re
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        out = {}
        for path in sorted(glob.glob(os.path.join(root, "shared", "boards",
                                                  "*.md"))):
            name = os.path.basename(path)
            if name.lower() == "readme.md":
                continue
            with open(path, encoding="utf-8") as fh:
                head = fh.read(4000)
            hosts = re.search(r"<!--\s*hosts:\s*(.+?)\s*-->", head)
            declared = set()
            if hosts:
                declared = {h.strip().lower()
                            for h in re.split(r"[,\s]+", hosts.group(1))
                            if h.strip()}
            # **Count the openings, not only what parses.** A marker missing
            # a field matches no pattern, so it disappears and reads as "no
            # marker" — which means "nobody looked". A malformed record must
            # not be indistinguishable from an absent one; that is the whole
            # distinction #141 exists to draw.
            opened = len(re.findall(r"<!--\s*siblings:", head))
            marks = re.findall(
                r"<!--\s*siblings:\s*(\S+)\s+(\S+)\s+(\S+)\s*-->", head)
            out[name[:-3]] = (declared, marks, opened)
        return out

    def test_every_marker_carries_a_known_verdict(self):
        bad = []
        for card, (_d, marks, _n) in self._markers().items():
            for host, _date, verdict in marks:
                if verdict not in self.VERDICTS:
                    bad.append(f"{card}: {host} -> {verdict!r}")
        self.assertEqual(bad, [], "not one of " + ", ".join(
            sorted(self.VERDICTS)) + ": " + ", ".join(bad))

    def test_a_malformed_marker_is_not_mistaken_for_an_absent_one(self):
        """**The silent case.** `<!-- siblings: host agree -->` — no date —
        matches no pattern, so it vanishes from the parse and the card looks
        unexamined. A record that cannot be read must fail, not disappear."""
        bad = []
        for card, (_d, marks, opened) in self._markers().items():
            if opened != len(marks):
                bad.append(f"{card}: {opened} written, {len(marks)} parse")
        self.assertEqual(bad, [],
                         "a siblings marker does not parse and is therefore "
                         "invisible — it reads as 'nobody looked': "
                         + ", ".join(bad))

    def test_every_marker_carries_a_date(self):
        """**A twin that agreed in September may diverge.** A verdict with no
        date is not a weaker record, it is not a record."""
        import re
        bad = []
        for card, (_d, marks, _n) in self._markers().items():
            for host, date, _v in marks:
                if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
                    bad.append(f"{card}: {host} -> {date!r}")
        self.assertEqual(bad, [], "not an ISO date: " + ", ".join(bad))

    def test_a_marker_names_a_host_its_card_declares(self):
        """**The second direction.** A verdict about a host the card does not
        claim is a measurement of something else, filed here — the shape that
        put `<!-- script: icims.py -->` on a card with no adapter."""
        stray = []
        for card, (declared, marks, _n) in self._markers().items():
            for host, _date, _v in marks:
                if not declared:
                    stray.append(f"{card}: {host} (card declares no hosts)")
                elif host not in declared and ("www." + host) not in declared \
                        and not any(d.lstrip("www.") == host for d in declared):
                    stray.append(f"{card}: {host}")
        self.assertEqual(stray, [],
                         "markers about hosts their card does not declare: "
                         + ", ".join(stray))

    def test_absence_is_still_legal(self):
        """**The witness.** If this ever fails, someone has turned the marker
        into an obligation and bought a backfill the measurement rejected —
        172 requests for a 4% yield, all dated the same day."""
        marked = sum(1 for _c, (_d, m, _n) in self._markers().items() if m)
        total = len(self._markers())
        self.assertGreater(total - marked, 0,
                           "every card now carries a marker — if that was a "
                           "backfill, the dates are all the same and stale "
                           "together; see #141")
        self.assertGreater(marked, 0, "no card records a sibling verdict, so "
                                      "the convention has been lost")


class CitiesAreComparedThroughTheSharedFold(unittest.TestCase):
    """Three adapters filtered locations by lowercasing and nothing else.

    A user types `Zurich`, `Geneve`, `Neuchatel` — which is how people type
    them — and the cards read `Zürich`, `Genève`, `Neuchâtel`. **The compare
    was `wanted.lower() in city.lower()`, so every one of those returned
    nothing at all.** `_locations.matches_city` exists for this (#65) and
    folds diacritics and the administrative suffix as well as case. #132.

    **The issue said thirteen adapters and it was seventeen, of which four
    filter locally — and the four were three different cases.** `pinpoint`
    and `recruitee` compared case-only. `swissdevjobs` had **its own** `fold`,
    weaker than the shared one on punctuation and trailing space.
    `workday` resolves the string against the board's own location facets and
    dies when none matches — a different mechanism, and folding there would
    change which facet is chosen. **The other thirteen pass the value to the
    site, which does its own matching; imposing a fold on them would be a
    regression, not a repair.**
    """

    ACCENTED = [("Zurich", "Zürich"), ("Geneve", "Genève"),
                ("Neuchatel", "Neuchâtel"), ("Lausanne", "Lausanne")]

    def test_an_ascii_spelling_finds_the_accented_city(self):
        import _locations
        for typed, on_card in self.ACCENTED:
            with self.subTest(typed=typed):
                self.assertTrue(
                    _locations.matches_city(on_card, typed),
                    f"a user typing {typed!r} gets nothing for {on_card!r}")

    def test_the_case_only_compare_really_did_miss_them(self):
        """**The witness for the defect**, kept so the case above is known to
        be testing something. Without it, `matches_city` could be a no-op
        improvement over a compare that already worked."""
        missed = [t for t, c in self.ACCENTED if t.lower() not in c.lower()]
        self.assertEqual(len(missed), 3,
                         "the old compare no longer misses these, so this "
                         "class is measuring the wrong thing")

    def test_a_different_city_still_does_not_match(self):
        """Generous is not indiscriminate."""
        import _locations
        for typed, on_card in [("Bern", "Zürich"), ("Lyon", "Lausanne")]:
            with self.subTest(typed=typed):
                self.assertFalse(_locations.matches_city(on_card, typed))

    def test_no_local_filter_compares_cities_by_lowercasing(self):
        """**The corpus half**, whose object is the text: the idiom that
        caused this must not come back in a fourth adapter. Reading source is
        right here — what is checked is that a form of words is absent from
        every file, which no single exercised case can establish."""
        import glob
        import re
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        scripts = os.path.join(root, "skills", "job-scan", "scripts")
        bad = []
        for path in sorted(glob.glob(os.path.join(scripts, "*.py"))):
            name = os.path.basename(path)
            if name.startswith("_"):
                continue
            src = open(path, encoding="utf-8").read()
            for m in re.finditer(
                    r"a\.(city|location)\.lower\(\)\s+(?:not\s+)?in\s", src):
                bad.append(f"{name}:{src[:m.start()].count(chr(10)) + 1}")
        self.assertEqual(bad, [],
                         "cities compared by lowercasing alone — accented "
                         "spellings will not match: " + ", ".join(bad))

    def test_the_text_fold_does_not_squeeze_punctuation(self):
        """**A regression this nearly shipped.** Converging `swissdevjobs`
        entirely onto `_locations.fold` looked tidy and would have broken its
        keyword filter: that fold squeezes punctuation for city names, so
        `C++` becomes `c` and `C#` becomes `c`, and a search for either would
        match every row containing the letter.

        **The two folds are for different jobs and must stay apart.** City
        comparison goes through `matches_city`; text search keeps the local
        fold.
        """
        import swissdevjobs
        import _locations
        for term in ("C++", "C#", ".NET", "Node.js", "CI/CD"):
            with self.subTest(term=term):
                kept = swissdevjobs.fold(term)
                self.assertEqual(kept, term.lower(),
                                 f"{term!r} lost its punctuation in the "
                                 f"keyword fold")
                self.assertNotEqual(
                    kept, _locations.fold(term),
                    f"the keyword fold now behaves like the city fold, and "
                    f"{term!r} folds to {_locations.fold(term)!r}")
        # and it still does the job it is kept for
        self.assertEqual(swissdevjobs.fold("Zürich"), "zurich")


class TravelIsADegreeNotAFact(unittest.TestCase):
    """The plugin had two configuration keys, a detector and written doctrine
    for the driving licence, and **nothing at all for business travel**, which
    advertisements ask for as often. Issue #137.

    **The licence model does not copy across, and the corpus is why.**
    Measured on 49 advertisements in a real workspace, 2026-09-04:

        mention a travel word     8   (16%)
        sentences matched        11
          a real requirement      5
          the employer's industry 3   "hospitality/travel/property domain"
          a benefit               1   "prime mobilité douce" — a cycling
                                      allowance, the opposite of business travel
          the plugin's own prose  1   "International travel: confirmed
                                      available by the candidate"

    **Six of eleven matches were not a requirement.** So this is a whitelist
    of phrasings, never a `grep` — the same shape #91 settled for `permis`,
    which also names a residence permit.

    **And every true match stated an amount**: *3–4 weeks per year*, *on a
    limited basis*, *déplacements inter-sites sont probables*. A yes meets
    none of them, which is why the configuration key is a phrase and the
    verdict never blocks.
    """

    ASKS = [
        ("Ability to travel 3-4 weeks per year to meet teammates in person",
         "weeks-per-year"),
        ("Willingness to travel internationally on a limited basis.",
         "limited"),
        ("mais des déplacements inter-sites sont probables.", "possible"),
        ("International exposure and willingness to travel", None),
    ]

    # every one of these was matched by the word and is not a requirement
    NOT_ASKS = [
        "Hospitality, travel or property-management industry background",
        "GCP, event-driven architectures, hospitality/travel/property",
        "prime mobilité douce jusqu'à CHF 1 500/an",
        "International travel: confirmed available by the candidate on "
        "2026-09-04, and written to `config.yml`",
        "Travel expenses reimbursed in full",
        "frais de déplacement remboursés",
    ]

    def test_the_measured_requirements_are_detected_with_their_degree(self):
        import _travel
        for text, degree in self.ASKS:
            with self.subTest(text=text[:40]):
                req = _travel.requirement(text)
                self.assertTrue(req["asks"], "a real requirement was missed")
                self.assertEqual(req["degree"], degree)
                self.assertTrue(req["quotes"], "the ad's own words are not "
                                               "kept, so nothing can be shown")

    def test_industry_product_benefit_and_our_own_prose_are_not_requirements(
            self):
        """**The last one is the trap `_licence.py` records too.** A run
        writes its analysis into the workspace and the next read finds
        *"International travel: confirmed available"* in a file it produced
        itself — a detector that reads its own output agrees with itself."""
        import _travel
        for text in self.NOT_ASKS:
            with self.subTest(text=text[:40]):
                self.assertFalse(_travel.requirement(text)["asks"],
                                 "matched something that is not a requirement")

    def test_a_bare_word_search_would_have_taken_all_of_them(self):
        """**The witness for the whitelist.** Without this, the case above
        passes on a detector that matches nothing at all — and the point is
        not that the noise is absent, it is that the noise is *there* and
        rejected."""
        import re
        # the pattern the corpus was actually measured with — it included
        # `mobilit`, which is how `prime mobilité douce` surfaced at all. A
        # witness that used a narrower pattern than the measurement would
        # have been testing a specimen the measurement never saw.
        measured = r"travel|travell?ing|déplacement|mobilit"
        caught = [t for t in self.NOT_ASKS if re.search(measured, t, re.I)]
        self.assertEqual(len(caught), len(self.NOT_ASKS),
                         "the specimens no longer contain the word, so they "
                         "prove nothing about the whitelist")

    def test_it_never_blocks(self):
        """`_licence.py`'s `blocker` already means *say it before a dossier is
        spent*, never *discard*. **Here even that is too strong**: a travel
        requirement is a question at the gate."""
        import _travel
        for text, _d in self.ASKS:
            req = _travel.requirement(text)
            for declared in (None, "none", "a few weeks a year"):
                with self.subTest(declared=declared):
                    v = _travel.verdict(req, declared)
                    self.assertFalse(v["blocker"],
                                     "a travel requirement set an ad aside")
                    self.assertTrue(v["ask"])

    def test_silence_is_a_question_and_not_an_answer(self):
        import _travel
        req = _travel.requirement(self.ASKS[0][0])
        v = _travel.verdict(req, None)
        self.assertEqual(v["status"], "asked-user-silent")
        self.assertIn("Nothing in the workspace says", v["text"])

    def test_the_recorded_answer_is_shown_not_compared(self):
        """**A degree is not met by a yes**, so the verdict puts both in front
        of the reader rather than deciding between them."""
        import _travel
        req = _travel.requirement(self.ASKS[0][0])
        v = _travel.verdict(req, "a few weeks a year, Europe")
        self.assertIn("a few weeks a year, Europe", v["text"])
        self.assertIn("weeks-per-year", v["text"])

    def test_the_invocation_both_skills_document_actually_runs(self):
        """**The doctrine promised a CLI that did not exist**, and I wrote
        both at once: `python3 _travel.py --file <ad>` appeared in two
        `SKILL.md` files while the module had no `__main__`.

        The invocation guard reads `shared/boards/`, so a command documented
        in a *skill* is checked by nothing. This is the narrow version of that
        gap — the module the skills name must at least run the way they say.
        """
        import subprocess
        import sys as _sys
        import tempfile
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        script = os.path.join(root, "skills", "job-scan", "scripts",
                              "_travel.py")
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False,
                                         encoding="utf-8") as fh:
            fh.write("Ability to travel 3-4 weeks per year to meet the team.")
            path = fh.name
        self.addCleanup(os.unlink, path)
        out = subprocess.run([_sys.executable, script, "--file", path,
                              "--json"], capture_output=True, text=True,
                             timeout=60)
        self.assertEqual(out.returncode, 0, out.stderr[:300])
        import json
        got = json.loads(out.stdout)
        self.assertTrue(got["ask"])
        self.assertFalse(got["blocker"])
        self.assertEqual(got["degree"], "weeks-per-year")

    def test_both_skills_name_the_same_invocation(self):
        """Two files documenting one command is two places to drift."""
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for skill in ("job-scan", "cover-letter"):
            with self.subTest(skill=skill):
                text = open(os.path.join(root, "skills", skill, "SKILL.md"),
                            encoding="utf-8").read()
                self.assertIn("_travel.py", text)
                self.assertIn("--file", text.split("_travel.py", 1)[1][:200])

    def test_the_configuration_key_is_not_a_boolean(self):
        """The template must not teach a yes/no, because the advertisements
        do not ask one."""
        import re
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cfg = open(os.path.join(root, "templates", "config.example.yml"),
                   encoding="utf-8").read()
        m = re.search(r"^  travel: (.+)$", cfg, re.M)
        self.assertIsNotNone(m, "the template no longer carries the key")
        value = m.group(1).strip()
        self.assertNotIn(value.lower(), ("true", "false", "yes", "no"))
        self.assertTrue(value.startswith('"'), "the example is not a phrase")


class CommandsDocumentedInSkillsAreReal(unittest.TestCase):
    """`DocumentedInvocationsAreReal` reads `shared/boards/` and nothing else.

    The two `SKILL.md` files and fifteen `shared/*.md` document commands too,
    and **none of them was checked by anything**. #148.

    **The demonstration is mine, from the same day.** Shipping #137 put

        python3 "${CLAUDE_PLUGIN_ROOT:-.}/…/_travel.py" --file <the ad>

    into **two** `SKILL.md` files while the module had no `__main__`. The
    command did not exist, in both files, and the suite was green. It was
    caught within the hour because I ran the command I had just written —
    **not because anything reported it.**

    Measured at `d35cab4`: 17 documents, 33 command lines, 14 distinct
    scripts, **zero broken**. The state is healthy and nothing holds it.

    **What this checks is narrower than the card guard, deliberately.** A
    board card names a subcommand and options, and the AST can compare them.
    A skill mostly names a script and a flag, so this asks the smaller
    question the population supports: **does the file exist, and does it run
    as a command at all.** Asking more of prose would manufacture findings.
    """

    # every place a documented script may live
    def _homes(self, root):
        """Every place a documented script may live, **found not listed.**

        This class shipped with a hard-coded tuple of four directories, and
        widening `_docs` to read every skill immediately produced two false
        accusations: `jobroom_sync.py` and `list_applications.py`, both of
        which exist, in `skills/job-report/scripts/` — a directory the tuple
        did not name.

        **That is the third hard-coded population to be wrong in one day**, and
        the direction is the dangerous one: the guard reported working code as
        broken documentation.
        """
        import glob
        homes = [os.path.join(root, "bin")]
        homes += sorted(glob.glob(os.path.join(root, "skills", "*")))
        homes += sorted(glob.glob(os.path.join(root, "skills", "*", "scripts")))
        return [h for h in homes if os.path.isdir(h)]

    def _docs(self):
        import glob
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # **Every skill, found rather than named.** This class shipped
        # reading two of them. Five others documented commands — including
        # `job-report`, which names five scripts — and not one was checked.
        # A guard that lists its own population cannot notice a new member,
        # and the day this was written a new skill was added.
        out = sorted(glob.glob(os.path.join(root, "skills", "*", "SKILL.md")))
        out += sorted(glob.glob(os.path.join(root, "shared", "*.md")))
        return root, [d for d in out if os.path.exists(d)]

    def _commands(self, text):
        r"""Every command line in a fenced block that names a `.py`.

        **The hyphen matters and cost three false findings.** A pattern of
        `[a-z0-9_]+\.py` reads `version-check.py` as `check.py` and reports
        three files that do not exist — the measurement behind this class
        invented its own defects twice before producing a number.
        """
        import re
        out = []
        for m in re.finditer(r"```[a-z]*\n(.*?)```", text, re.S):
            for line in m.group(1).replace("\\\n", " ").split("\n"):
                line = line.split("#", 1)[0].strip()
                hit = re.search(r"([a-z0-9_-]+\.py)", line)
                if not hit:
                    continue
                # a command, an assignment from one, or a substitution
                if not re.match(r"^(python3?\b|\$|[A-Za-z_]+=)", line):
                    continue
                out.append((hit.group(1), line[:90]))
        return out

    def _resolve(self, root, script):
        for home in self._homes(root):
            path = os.path.join(home, script)
            if os.path.exists(path):
                return path
        return None

    def _runs_as_a_command(self, path):
        import ast
        try:
            tree = ast.parse(open(path, encoding="utf-8").read())
        except SyntaxError:
            return None
        for n in ast.walk(tree):
            if isinstance(n, ast.If) and isinstance(n.test, ast.Compare) \
                    and isinstance(n.test.left, ast.Name) \
                    and n.test.left.id == "__name__":
                return True
        return False

    def _walk(self):
        root, docs = self._docs()
        seen, bad = {}, []
        for doc in docs:
            text = open(doc, encoding="utf-8").read()
            for script, line in self._commands(text):
                seen.setdefault(script, []).append(
                    (os.path.relpath(doc, root), line))
        for script, uses in sorted(seen.items()):
            path = self._resolve(root, script)
            where = uses[0][0]
            if path is None:
                bad.append(f"{where}: no such file {script}")
            elif self._runs_as_a_command(path) is False:
                bad.append(f"{where}: {script} has no `__main__` and is "
                           f"documented as a command")
        return seen, bad

    def test_every_documented_script_exists_and_runs_as_a_command(self):
        seen, bad = self._walk()
        self.assertEqual(bad, [], "; ".join(bad))

    def test_the_population_has_not_collapsed(self):
        """**The floor**, because this guard's own extractor is the fragile
        part: a pattern that stops matching reports a clean corpus."""
        seen, _bad = self._walk()
        self.assertGreater(len(seen), 10,
                           f"only {len(seen)} scripts found in the skills and "
                           f"shared docs — the extractor has gone quiet")

    def test_the_unusual_forms_are_still_read(self):
        """**The other half of the mutation.** A guard that only reads
        `python3 path/to/x.py` would be green on this corpus by seeing almost
        none of it. These four shapes all appear in the documents and must all
        resolve."""
        root, _docs = self._docs()
        shapes = {
            'python3 "${CLAUDE_PLUGIN_ROOT:-.}/bin/version-check.py"':
                "version-check.py",
            'JOB_HUNT_HOME="$(python3 "${CLAUDE_PLUGIN_ROOT:-.}/bin/'
            'workspace-path.py")"': "workspace-path.py",
            'python3 "${CLAUDE_PLUGIN_ROOT}/skills/cover-letter/'
            'save-profile-text.py" --in x': "save-profile-text.py",
            'python3 "$S/_travel.py" --file ad.md': "_travel.py",
        }
        for line, expected in shapes.items():
            with self.subTest(line=line[:44]):
                got = self._commands("```bash\n" + line + "\n```")
                self.assertTrue(got, f"this form is not read at all: {line}")
                self.assertEqual(got[0][0], expected)
                self.assertIsNotNone(
                    self._resolve(root, expected),
                    f"{expected} does not resolve — the hyphen or the "
                    f"directory list is wrong, which is how the measurement "
                    f"behind this class invented three defects")


class ARefusalInProseIsStillARefusal(unittest.TestCase):
    """Since 2026-09-04 a readable 200 with no directive opens the door, and
    `maliemploi.org` served an Apache error page as its `robots.txt`:

        <title>403 Forbidden</title> … <h1>Access forbidden!</h1><p>Error 403</p>

    **That is in the letter of that decision and outside its spirit.** The
    reasoning quoted was about a host expressing *nothing*; this one expresses
    a refusal in words, and only its HTTP status lies. #138.

    **The formulation was left to be settled by writing it**, and this is the
    choice: `allowed` is `False`, not `None`. `None` means *unknown*, which is
    what `unreachable` says (#118) — **here nothing is unknown**: the host
    answered, and what it answered was no. `certain` stays `False` because it
    said so in prose this module cannot quote as a rule. The four states do
    not merge.

    **Two bounds, both measured on live hosts rather than imagined.**
    """

    APACHE = ('<!DOCTYPE HTML><html><head><title>403 Forbidden</title></head>'
              '<body><h1>Access forbidden!</h1><p>Error 403</p></body></html>')
    # malibaara.com, fetched 2026-09-04: 5 132 bytes, 116 characters of
    # visible text.
    SHELL = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
             '<title>Malibaara.com | Le site par excellence de recherche '
             "d'emplois au Mali</title></head><body><div id=\"root\"></div>"
             '<noscript>You need to enable JavaScript to run this app.'
             '</noscript></body></html>')
    # empleate.gob.es, fetched 2026-09-04. It carries a ROBOTS meta tag *and*
    # says "try again later".
    ERROR_PAGE = ("<html><head><title>SEPE</title>"
                  "<META NAME='ROBOTS' CONTENT='NOINDEX,NOFOLLOW'></head>"
                  "<body>En este momento no ha sido posible procesar la "
                  "operaci&oacute;n solicitada. Por favor, "
                  "int&eacute;ntelo de nuevo m&aacute;s tarde.</body></html>")

    class _Resp:
        def __init__(self, body, ctype="text/html", code=200):
            self._b = body.encode("utf-8")
            self._c, self._code = ctype, code

        def read(self):
            return self._b

        def geturl(self):
            return "https://h.example/robots.txt"

        def getcode(self):
            return self._code

        @property
        def headers(self):
            return {"Content-Type": self._c}

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def _verdict(self, body):
        import _robots
        real = _robots.urllib.request.urlopen
        _robots._CACHE.clear()
        _robots._ALIAS.clear()
        _robots.urllib.request.urlopen = (
            lambda r, timeout=None, **k: self._Resp(body))
        try:
            return (_robots.verdict("h.example"),
                    _robots.allowed("h.example", "/jobs"))
        finally:
            _robots.urllib.request.urlopen = real
            _robots._CACHE.clear()
            _robots._ALIAS.clear()

    # ---- the origin case -------------------------------------------------

    def test_the_apache_page_stops_the_module(self):
        v, a = self._verdict(self.APACHE)
        self.assertEqual(v["state"], "refused-in-prose")
        self.assertFalse(v["sweep"])
        self.assertFalse(a["allowed"])
        self.assertFalse(a["certain"],
                         "a refusal read out of prose is not a certainty")

    def test_the_reason_says_the_status_disagreed_with_the_body(self):
        v, _a = self._verdict(self.APACHE)
        self.assertIn("says no", v["reason"])
        self.assertIn("200", v["reason"])

    # ---- bound one: an application shell -------------------------------

    def test_an_application_shell_is_not_a_refusal(self):
        """`malibaara.com` serves the same React shell for `/robots.txt` as
        for everything else — 116 characters of visible text, none of it a
        refusal. **It fails the predicate naturally rather than by an
        exclusion list**: a predicate that must name its exceptions has not
        found its rule."""
        import _robots
        self.assertFalse(_robots._looks_like_refusal(self.SHELL))
        v, a = self._verdict(self.SHELL)
        self.assertEqual(v["state"], "unrecognised")
        self.assertTrue(a["allowed"], "the open door closed on a shell")

    # ---- bound two: not the word, and not a failure --------------------

    def test_it_does_not_rest_on_the_word_robots(self):
        """`empleate.gob.es`'s error page carries
        `<META NAME='ROBOTS' CONTENT='NOINDEX,NOFOLLOW'>`. **A predicate
        searching for that word would be searching for its own answer.**"""
        import _robots
        self.assertIn("ROBOTS", self.ERROR_PAGE,
                      "the specimen no longer carries the word, so it proves "
                      "nothing about the bound")
        self.assertFalse(_robots._looks_like_refusal(self.ERROR_PAGE))

    def test_try_again_later_is_a_failure_not_a_refusal(self):
        """The same page says *"no ha sido posible… inténtelo de nuevo más
        tarde"*. **Words that mean "you may not", never words that mean "it
        did not work"** — and this one means the second."""
        v, a = self._verdict(self.ERROR_PAGE)
        self.assertEqual(v["state"], "unrecognised")
        self.assertTrue(a["allowed"])

    # ---- the neighbours still do not merge ------------------------------

    def test_a_real_rules_file_is_untouched(self):
        v, _a = self._verdict("User-agent: *\nDisallow: /wp-admin/\n")
        self.assertEqual(v["state"], "read")

    def test_the_four_states_are_distinct(self):
        """`unreachable`, `refused`, `unrecognised`, `refused-in-prose` — and
        the last two differ only by what the body says, which is the whole
        point."""
        shell = self._verdict(self.SHELL)[0]["state"]
        prose = self._verdict(self.APACHE)[0]["state"]
        self.assertNotEqual(shell, prose)
        self.assertEqual({shell, prose}, {"unrecognised", "refused-in-prose"})


class TheExemptedApiRoutesStillIdentifyThemselves(unittest.TestCase):
    """The owner settled #100 on 2026-09-04:

    > *"Si une API est disponible, on en conclut que l'entrée, si elle est
    > bloquée, l'est techniquement — jeton, quota. Le check n'est pas de notre
    > ressort."*

    So four adapters do not consult the guard, and that is now a rule rather
    than an accident: `adzuna`, `arbeitsagentur`, `francetravail`,
    `labonnealternance`. **What stops you on an API host is read in its
    answer, not in a `robots.txt`.**

    **The exemption is from the verdict, not from the identity — and that half
    has already broken once.** On 2026-09-04 two of these four were sending no
    declared agent at all: `adzuna` carried its own `UA` string naming no
    token, and `labonnealternance` sent none, so urllib announced
    `Python-urllib/3.x`. The audit that had closed #120 counted what obeys and
    not what escapes. **An API route is still a route that introduces
    itself.**

    `DeclaredAgentIsSentEverywhere` covers all four — it reads every file. But
    the *exercised* case behind it runs on `adecco`, which is **not one of
    them**, and the corpus scan cannot see intent: an import and a header key
    can both be present while the value is wrong. That is precisely how
    `empleate.py` was able to drop its TLS context while `oposiciones.py` was
    the file being exercised.

    **So this is the depth half, on the exempted route itself.**
    `arbeitsagentur` is the specimen because its key is published in the
    specification and hard-coded — it needs nothing from the user, so the case
    costs no credential and no request: the opener is replaced.
    """

    def _wire(self, module_name, entry, stub_token=False):
        """What the request carried, without one leaving the machine."""
        import importlib
        mod = importlib.import_module(module_name)
        seen = {}

        def fake(req, *a, **kw):
            seen["ua"] = (req.get_header("User-agent")
                          if hasattr(req, "get_header") else None)
            seen["reached"] = True
            raise mod.urllib.error.URLError("stubbed for this case")

        # **`francetravail.call` fetches a bearer token before it builds the
        # request**, so on a machine without credentials it dies before the
        # opener is reached. That is how this case passed here and failed on
        # every CI runner: my own `~/.francetravail.env` was standing in for
        # a fixture. The token is stubbed so the case measures the header it
        # is about, everywhere.
        real_token = getattr(mod, "token", None) if stub_token else None
        if real_token is not None:
            mod.token = lambda *_a, **_k: "stub-token"
        real = mod.urllib.request.urlopen
        # **These adapters retry with 1.5s and 3s of backoff**, and paying it
        # for a case about a header put 4.6 seconds on the suite. The retry
        # behaviour is pinned elsewhere; what this measures is what the first
        # request carried.
        slept = getattr(mod, "time", None)
        if slept is not None:
            real_sleep = mod.time.sleep
            mod.time.sleep = lambda *_a, **_k: None
        mod.urllib.request.urlopen = fake
        try:
            try:
                getattr(mod, entry)("https://example.invalid/x")
            except BaseException:
                pass
        finally:
            mod.urllib.request.urlopen = real
            if slept is not None:
                mod.time.sleep = real_sleep
            if real_token is not None:
                mod.token = real_token
        return seen

    def test_an_exempted_api_route_sends_the_declared_agent(self):
        import _ua
        seen = self._wire("arbeitsagentur", "api")
        self.assertTrue(seen.get("reached"),
                        "the request never reached the opener, so this case "
                        "measured nothing — the entry point moved")
        self.assertEqual(seen.get("ua"), _ua.UA,
                         f"an exempted API route went out as "
                         f"{seen.get('ua')!r}: exempt from the guard is not "
                         f"exempt from saying who is calling")

    def test_a_second_exempted_route_does_too(self):
        """Two of the four, because **one specimen is not a corpus** — the
        lesson `empleate.py` taught on the TLS half the same day."""
        import _ua
        seen = self._wire("francetravail", "call",
                          stub_token=True)
        self.assertTrue(seen.get("reached"))
        self.assertEqual(seen.get("ua"), _ua.UA)

    def test_the_four_are_still_the_four(self):
        """**The population floor.** If a fifth adapter stops importing the
        guard, it inherits an exemption nobody granted it — and the count is
        the only thing that would say so."""
        import glob
        import re
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        scripts = os.path.join(root, "skills", "job-scan", "scripts")
        unguarded = []
        for path in sorted(glob.glob(os.path.join(scripts, "*.py"))):
            name = os.path.basename(path)
            if name.startswith("_"):
                continue
            src = open(path, encoding="utf-8").read()
            # wide on purpose: four adapters fetch through
            # `OPENER.open(...)`, not `urlopen(...)` — see
            # TheExemptedApiRoutesStillIdentifyThemselves
            if not re.search(r"urllib\.request|http\.client|requests\.", src):
                continue
            if not re.search(r"(^|\n)\s*(import _robots|from _robots\s+import)",
                             src):
                unguarded.append(name[:-3])
        declared = self._declared_exempt()
        self.assertEqual(
            sorted(unguarded), sorted(declared),
            f"the set of adapters exempt from the guard is inferred from an "
            f"absence of calls ({sorted(unguarded)}) and declared on the cards "
            f"({sorted(declared)}), and the two disagree. An exemption that "
            f"only exists as a missing import is one nobody granted.")

    def _declared_exempt(self):
        """**#100 point 1, made a declaration instead of an inference.**

        Until now this population lived as a literal list inside this test:
        the exemption was visible only as an *absence* of `import _robots`,
        and the test was the only place saying which absences were intended.
        **An adapter that quietly stopped importing the guard would have
        looked exactly like one that was meant to be exempt** — the same shape
        that let two of these four stop sending our declared agent while an
        audit counted what obeys and not what escapes.

        Now each of the four says so on its own card, and this reads them.
        """
        import glob
        import re
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        out = []
        for path in sorted(glob.glob(os.path.join(root, "shared", "boards",
                                                  "*.md"))):
            with open(path, encoding="utf-8") as fh:
                src = fh.read()
            decl = re.search(r"<!--\s*robots:\s*(.*?)\s*-->", src)
            if not decl:
                continue
            self.assertIn(
                decl.group(1), ("keyed-api", "suspended"),
                f"{os.path.basename(path)} declares an unknown robots value "
                f"{decl.group(1)!r}; the vocabulary is closed, because a value "
                f"nothing reads is an absence with extra steps")
            script = re.search(r"<!--\s*script:\s*([^\s>]+)", src)
            self.assertIsNotNone(
                script, f"{os.path.basename(path)} claims a robots exemption "
                        f"but names no script, so nothing can check it")
            out.append(script.group(1)[:-3] if script.group(1).endswith(".py")
                       else script.group(1))
        return out


class TheDeclaredVersionIsTheReleasedVersion(unittest.TestCase):
    """**Two files carry the version, and until now nothing said so.**

    `.claude-plugin/plugin.json` is the manifest; `skills/job-scan/scripts/`
    `_ua.py` hard-codes the same number into the `User-Agent` every adapter
    sends to every third party. Twenty-six releases on 2026-09-04 bumped both,
    because a human did it by hand and remembered.

    **`release.yml` bumps only the manifest.** Its first unattended run would
    have published a version whose declared agent announced the previous one,
    and every release after it would have widened the gap — *the number we
    tell other people we are* drifting away from the number we released.

    This is the species already named twice in this suite: **two numbers, two
    provenances, one assumed quantity.** The assumption held only while the
    hand that moved one moved the other.

    **The third provenance is the tag**, and it has already broken once:
    v1.209.0 was tagged onto a tree still declaring 1.208.0. So the newest tag
    is checked here too — `release.yml` computes the next version from the
    manifest but decides *whether to run* from the tag, and a disagreement
    between them makes it compute a number that already exists.
    """

    def _root(self):
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def _manifest(self):
        import json
        p = os.path.join(self._root(), ".claude-plugin", "plugin.json")
        with open(p, encoding="utf-8") as fh:
            return json.load(fh)["version"]

    def _agent(self):
        import re
        p = os.path.join(self._root(), "skills", "job-scan", "scripts",
                         "_ua.py")
        with open(p, encoding="utf-8") as fh:
            src = fh.read()
        hits = re.findall(r"claude-job-hunt/([0-9]+\.[0-9]+\.[0-9]+)", src)
        self.assertEqual(len(hits), 1,
                         f"_ua.py declares {len(hits)} versions; the bump in "
                         f"release.yml rewrites exactly one and fails loudly "
                         f"otherwise, so this number is load-bearing")
        return hits[0]

    def test_the_agent_announces_the_released_version(self):
        self.assertEqual(
            self._agent(), self._manifest(),
            "_ua.py and plugin.json disagree: the agent we send to every "
            "third party is not the version we published")

    def test_the_newest_tag_agrees_with_the_manifest(self):
        """**Not a duplicate of the case above.** That one compares two files
        in the tree; this compares the tree to what was actually published. A
        tag ahead of the manifest makes the next automated release compute a
        version that already exists, and it wedges: `git describe` skips a tag
        that is not an ancestor, so it recomputes the same number forever.
        """
        import subprocess
        try:
            out = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0"],
                cwd=self._root(), capture_output=True, text=True, timeout=20)
        except (OSError, subprocess.SubprocessError):
            self.skipTest("git is not available here")
        if out.returncode != 0:
            self.skipTest("no tags reachable from HEAD (a shallow checkout)")
        tag = out.stdout.strip().lstrip("v")
        if not tag:
            self.skipTest("git describe said nothing")
        self.assertEqual(
            tag, self._manifest(),
            f"the newest reachable tag is v{tag} but the manifest says "
            f"{self._manifest()}; whichever moved without the other, the "
            f"automated release will compute a version that already exists")


class HostsAreDeclaredOrDeclaredInapplicable(unittest.TestCase):
    """**#146. Twelve cards had an adapter and no `<!-- hosts: -->`**, so no
    host-indexed check could reach them. The shortest demonstration: `jobup.ch`
    was measured with `_robots.py --siblings` on 2026-09-04, it returned
    `agree`, **and the result had nowhere to go.**

    **The form chosen is an explicit declaration of inapplicability**, so that
    an absence means what it used to mean: *no line = nobody looked*, a token
    = *somebody looked and the question does not arise.* That is the property
    `<!-- script: -->` and `<!-- countries: -->` already have.

    **The vocabulary is smaller than proposed, and that is the finding.** The
    suggestion was `per-tenant` and `multi-brand`. **`multi-brand` was wrong on
    every card it would have covered** — each of them enumerates its own hosts
    in its own source:

        bumeran      SITES, 8 keys      jobology   SITES, 9 keys
        stepstone    SITES, 10 host=    fachkraft  DOMAINS, 3
        computrabajo COUNTRIES, 18      jobup      SITES, 2

    So they get real lists. **A token there would have replaced a retrievable
    list with a word** — including on `jobup`, the card whose lost measurement
    is the whole reason for the issue.

    The two tokens that survive name genuinely unbounded sets:
    `per-tenant`, where the host names an employer using an ATS, and
    `per-country`, where it names a country edition the repo does not
    enumerate.
    """

    TOKENS = ("per-tenant", "per-country")

    def _cards(self):
        import glob
        import re
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        out = []
        for path in sorted(glob.glob(os.path.join(root, "shared", "boards",
                                                  "*.md"))):
            name = os.path.basename(path)[:-3]
            if name == "README":
                continue
            with open(path, encoding="utf-8") as fh:
                src = fh.read()
            hosts = re.search(r"<!--\s*hosts:\s*(.*?)\s*-->", src)
            script = re.search(r"<!--\s*script:\s*([^\s>]+)", src)
            values = ([h.strip() for h in hosts.group(1).split(",") if h.strip()]
                      if hosts else None)
            out.append((name, values, script.group(1) if script else None, root))
        return out

    def test_every_card_declares_its_hosts_or_says_why_not(self):
        missing = [n for n, v, _s, _r in self._cards() if not v]
        self.assertEqual(missing, [],
                         f"{len(missing)} cards carry no <!-- hosts: --> line, "
                         f"so no host-indexed check can reach them: {missing}")

    def test_the_tokens_come_from_a_closed_vocabulary(self):
        """**An open vocabulary is an absence with extra steps.** A token
        nobody indexed is worth exactly as much as the missing line was."""
        bad = []
        for name, values, _s, _r in self._cards():
            for v in values or []:
                if "." not in v and v not in self.TOKENS:
                    bad.append(f"{name}: {v!r}")
        self.assertEqual(bad, [], "; ".join(bad))

    def test_a_token_is_never_mixed_with_real_hosts(self):
        """Half a list is not a list. If a board has one enumerable host it
        has an enumerable set, and the token is a claim about the set."""
        bad = []
        for name, values, _s, _r in self._cards():
            vals = values or []
            if any(v in self.TOKENS for v in vals) and len(vals) > 1:
                bad.append(f"{name}: {vals}")
        self.assertEqual(bad, [], "; ".join(bad))

    def test_no_card_claims_inapplicable_while_its_script_enumerates(self):
        """**The half that matters, and the one that nearly went the other
        way.** A token on a board that does enumerate its hosts is not a
        shorthand — it discards a list the repo already holds, and it does it
        invisibly, because a token and a truth look identical on the card.

        So the source is asked: does this script carry a literal host-bearing
        structure? If it does, the card may not claim the question is moot.
        """
        import ast
        NAMES = ("SITES", "DOMAINS", "HOSTS", "COUNTRIES", "BRANDS")
        bad = []
        for name, values, script, root in self._cards():
            if not values or not any(v in self.TOKENS for v in values):
                continue
            if not script:
                continue
            path = os.path.join(root, "skills", "job-scan", "scripts", script)
            if not os.path.isfile(path):
                continue
            try:
                tree = ast.parse(open(path, encoding="utf-8").read())
            except SyntaxError:
                continue
            for node in tree.body:
                if not isinstance(node, ast.Assign):
                    continue
                for t in node.targets:
                    if getattr(t, "id", None) not in NAMES:
                        continue
                    try:
                        val = ast.literal_eval(node.value)
                    except Exception:
                        continue
                    if len(val) > 1:
                        bad.append(f"{name} says {values} but {script} "
                                   f"enumerates {len(val)} in {t.id}")
        self.assertEqual(bad, [], "; ".join(bad))

    def test_the_enumerated_boards_kept_their_lists(self):
        """**The floor.** The four checks above are all satisfied by giving
        every card the token — the cheapest way to go green is the exact
        mistake this class exists to prevent."""
        got = {n: v for n, v, _s, _r in self._cards()}
        for name, least in (("bumeran", 8), ("jobology", 9), ("stepstone", 10),
                            ("computrabajo", 18), ("fachkraft", 3)):
            with self.subTest(board=name):
                self.assertIn(name, got)
                self.assertGreaterEqual(
                    len(got[name] or []), least,
                    f"{name} enumerates {least} hosts in its source; its card "
                    f"now claims {got[name]}")


class TheTenantIsAskedAboutNotThePlatform(unittest.TestCase):
    """**#100 point 3, and the premise had already been met.**

    The issue asked, on 2026-09-03, that seven multi-tenant ATS adapters call
    the guard per tenant. Measured on 2026-09-04: all seven import `_robots`,
    all seven gate, and all seven pass `urlsplit(url).netloc` and
    `urlsplit(url).path` — so the verdict is already the tenant's and already
    the path's. **The work named in the issue is done.**

    **What was missing is the proof.** Not one of the seven had an exercised
    case: the per-tenant behaviour was true by reading and unverified by
    running, and the only two adapters exercised anywhere are the keyed-API
    pair. **A regression to a vendor host — asking `flatchr.io` about a
    question that belongs to `pokawa.flatchr.io` — would have changed nothing
    a corpus scan can see.** The import is still there, the call is still
    there, the gate function is still there; only the argument is wrong.

    That is the shape this suite has already been bitten by twice: a guard
    present and inert, and a scan that counts what obeys rather than what
    escapes.

    **The property asserted is uniform across all seven and does not assume
    tenancy is by host.** Some of these platforms give each tenant a
    subdomain, others a path on a shared host. Both are covered by the same
    statement: *the gate asks about the URL it was given, never about a
    constant.*
    """

    SEVEN = ("flatchr", "recruitee", "talentsoft", "pinpoint",
             "digitalrecruiters", "solique", "persigo")

    def _gate_name(self, module):
        """The function that calls `robots_allowed`, found rather than named.

        Six of them call it `_robots_gate` and one calls it `check_robots`.
        **Hard-coding either would make this class quietly cover six of seven**
        — and a scan that shrinks its own denominator reports health whatever
        happens.
        """
        import ast
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(root, "skills", "job-scan", "scripts",
                            module + ".py")
        with open(path, encoding="utf-8") as fh:
            tree = ast.parse(fh.read())
        for fn in ast.walk(tree):
            if not isinstance(fn, ast.FunctionDef):
                continue
            for n in ast.walk(fn):
                if isinstance(n, ast.Call) and \
                        getattr(n.func, "id", "") == "robots_allowed":
                    return fn.name
        return None

    def _ask(self, module, url, verdict=None):
        """Call the gate on `url` and report what the guard was asked."""
        import importlib
        mod = importlib.import_module(module)
        name = self._gate_name(module)
        self.assertIsNotNone(name, f"{module} has no function calling "
                                   f"robots_allowed; it is no longer gated")
        gate = getattr(mod, name)
        seen = {}

        def fake(host, path="/"):
            seen["host"], seen["path"] = host, path
            return verdict or {"allowed": True, "certain": True, "reason": "ok",
                               "host": host, "requested_host": host}

        real = mod.robots_allowed
        mod.robots_allowed = fake
        try:
            import contextlib
            import inspect
            import io
            n = len(inspect.signature(gate).parameters)
            args = (url, "test")[:max(1, min(n, 2))]
            # the adapters print their own refusal to stderr on the way out
            with contextlib.redirect_stderr(io.StringIO()):
                gate(*args)
        finally:
            mod.robots_allowed = real
        return seen

    def test_the_gate_asks_about_the_url_it_was_given(self):
        """A tenant host, and the guard must hear that host — not the vendor's.
        """
        for module in self.SEVEN:
            with self.subTest(adapter=module):
                seen = self._ask(module,
                                 "https://tenant-x.example-ats.com/jobs/42")
                self.assertEqual(
                    seen.get("host"), "tenant-x.example-ats.com",
                    f"{module} asked the guard about {seen.get('host')!r} "
                    f"instead of the host in the URL; on a tenant platform the "
                    f"rules file is the employer's, not the vendor's")

    def test_it_asks_about_the_path_too(self):
        """`verdict()` answers *is this host closed outright*. A careers site
        that refuses its ad path while leaving its root open passes that and
        refuses every advertisement."""
        for module in self.SEVEN:
            with self.subTest(adapter=module):
                seen = self._ask(module,
                                 "https://tenant-x.example-ats.com/jobs/42")
                self.assertEqual(seen.get("path"), "/jobs/42",
                                 f"{module} did not ask about the path")

    def test_a_refusal_stops_that_command(self):
        """**The decision of 2026-09-04**: a refused tenant is skipped and
        named, and the others continue. Every one of these seven takes a single
        required `--tenant`, so one command is one tenant and stopping *is*
        skipping — there is nothing else in the run to continue.

        What must not happen is the third possibility: reading on anyway.
        """
        refused = {"allowed": False, "certain": True,
                   "reason": "robots.txt refuses /jobs/", "host": "h",
                   "requested_host": "h"}
        for module in self.SEVEN:
            with self.subTest(adapter=module):
                with self.assertRaises(SystemExit, msg=(
                        f"{module} read on through a refusal")) as caught:
                    self._ask(module, "https://tenant-x.example-ats.com/jobs/42",
                              verdict=refused)
                self.assertEqual(caught.exception.code, 7,
                                 f"{module} exited {caught.exception.code}; a "
                                 f"refusal by robots is exit 7 so a caller can "
                                 f"tell it from a breakage")

    def test_all_seven_are_covered(self):
        """**The denominator.** Every check above is a loop, and a loop over an
        empty or shortened list passes."""
        self.assertEqual(
            len(self.SEVEN), 7,
            "the list itself was shortened. Every check in this class loops "
            "over SEVEN, so comparing SEVEN to itself would pass on an empty "
            "list — a guard that can shrink its own denominator reports "
            "health whichever way it goes.")
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        for m in self.SEVEN:
            with self.subTest(adapter=m):
                self.assertTrue(
                    os.path.isfile(os.path.join(
                        root, "skills", "job-scan", "scripts", m + ".py")),
                    f"{m}.py does not exist, so its subTest passed by "
                    f"never running")
        found = [m for m in self.SEVEN if self._gate_name(m)]
        self.assertEqual(sorted(found), sorted(self.SEVEN),
                         f"only {len(found)} of {len(self.SEVEN)} multi-tenant "
                         f"adapters have a gate: {sorted(found)}")


class TheAgentGoesOutThroughAnOpenerToo(unittest.TestCase):
    """**The specimen for the second shape.** `DeclaredAgentIsSentEverywhere`
    reads source; this runs one.

    `philjobnet.py` builds an `OpenerDirector` and sets
    `addheaders = [("User-Agent", UA), ...]`. **Nothing had ever exercised that
    path**, and when the corpus scan was widened to a filter that could finally
    see this file, its pattern — a dict key — reported the adapter as sending
    no agent. The header was there and had always gone out.

    So the scan learned the second shape, and this proves the shape works. The
    seam is `OpenerDirector._open`, which runs **after** `addheaders` have been
    folded into the request: intercepting `open` would be too early and would
    measure the request before the opener touched it, which is exactly the kind
    of case that passes while proving nothing.
    """

    def test_the_opener_puts_the_declared_agent_on_the_request(self):
        import importlib
        import _ua
        mod = importlib.import_module("philjobnet")
        session = mod.Session()
        seen = {}

        def fake_open(req, *a, **kw):
            seen["ua"] = req.get_header("User-agent")
            raise mod.urllib.error.URLError("stubbed for this case")

        session.op._open = fake_open
        try:
            session.op.open(mod.urllib.request.Request("https://x.invalid/"),
                            timeout=1)
        except BaseException:
            pass
        self.assertIn("ua", seen,
                      "the request never reached the handler, so this case "
                      "measured nothing — the seam moved")
        self.assertEqual(seen["ua"], _ua.UA,
                         f"the opener sent {seen.get('ua')!r}")


class ADrawIsSealedBeforeTheInterview(unittest.TestCase):
    """**#150.** The rehearsal skill draws the interviewers' facets, plays them
    without naming them, and reveals them in the debrief.

    **The failure this prevents is not dishonesty, it is memory.** A debrief
    revealing facets chosen *after* the interview reads exactly like one
    revealing facets chosen *before* it — the candidate cannot tell, a reader
    of the transcript cannot tell, and **the agent cannot tell either**, which
    is the part that matters. An agent that reconstructs a plausible draw at
    debrief time will believe it remembered one.

    So `draw` prints a digest into the transcript and writes the facets to a
    file. **A reconstruction cannot match a digest that was already
    published.** This is not tamper-proofing against someone determined to
    cheat; it removes the honest accident.
    """

    def _run(self, *args):
        import subprocess
        import sys as _sys
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        script = os.path.join(root, "skills", "interview-rehearsal",
                              "rehearse.py")
        return subprocess.run([_sys.executable, script, *args],
                              capture_output=True, text=True, timeout=30)

    def setUp(self):
        import tempfile
        self.tmp = tempfile.mkdtemp()
        self.path = os.path.join(self.tmp, "draw.json")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_the_draw_does_not_leak_the_facets_into_the_transcript(self):
        """**The blind phase depends on this and on nothing else.** Whatever
        `draw` prints is what the candidate can scroll back to."""
        import json
        out = self._run("draw", "--out", self.path, "--seed", "3")
        self.assertEqual(out.returncode, 0, out.stderr)
        printed = (out.stdout + out.stderr).lower()
        with open(self.path, encoding="utf-8") as fh:
            drawn = json.load(fh)
        values = {v.lower() for p in drawn["panel"]
                  for v in p["facets"].values()}
        leaked = sorted(v for v in values if v in printed)
        self.assertEqual(leaked, [],
                         f"the draw printed its own facets: {leaked}")

    def test_a_reconstruction_cannot_match_the_published_digest(self):
        """The case the mechanism exists for: the file is rewritten afterwards
        with different facets, and the digest no longer agrees."""
        import json
        out = self._run("draw", "--out", self.path, "--seed", "3")
        published = [w for w in out.stdout.split() if len(w) == 8
                     and all(c in "0123456789abcdef" for c in w)]
        self.assertTrue(published, f"no digest in {out.stdout!r}")
        with open(self.path, encoding="utf-8") as fh:
            rec = json.load(fh)
        before = rec["panel"][0]["facets"]["warmth"]
        after = "warm" if before != "warm" else "cold"
        self.assertNotEqual(before, after, "the mutation would not apply")
        rec["panel"][0]["facets"]["warmth"] = after
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump(rec, fh)
        back = self._run("reveal", "--file", self.path)
        self.assertNotEqual(back.returncode, 0,
                            "a rewritten draw was revealed as if sealed")
        self.assertIn("changed since it was sealed", back.stderr)

    def test_an_intact_draw_reveals_and_verifies(self):
        """**The negative half.** A guard that refuses everything is not a
        guard, and this one would look identical from the failing side."""
        import json
        self._run("draw", "--out", self.path, "--seed", "3")
        back = self._run("reveal", "--file", self.path)
        self.assertEqual(back.returncode, 0, back.stderr)
        self.assertEqual(json.loads(back.stdout)["kind"], "rehearsal",
                         "a rehearsal must never be recorded as an interview")
        check = self._run("verify", "--file", self.path)
        self.assertEqual(check.returncode, 0)
        self.assertTrue(json.loads(check.stdout)["intact"])

    def test_a_missing_draw_refuses_rather_than_improvising(self):
        """**The debrief's honest failure.** No file means the facets cannot be
        revealed truthfully, and saying so is the only correct answer."""
        back = self._run("reveal", "--file", os.path.join(self.tmp, "none.json"))
        self.assertNotEqual(back.returncode, 0)
        self.assertIn("cannot", back.stderr.lower())

    def test_an_unforeseen_facet_is_kept(self):
        """The request's list ends in "…". **A facet nobody anticipated must
        not be lost in silence** — the open list is part of the spec."""
        import json
        self._run("draw", "--out", self.path, "--facet", "nepotism=strong")
        with open(self.path, encoding="utf-8") as fh:
            rec = json.load(fh)
        self.assertEqual(rec["panel"][0]["facets"].get("nepotism"), "strong")

    def test_it_will_not_overwrite_a_draw_by_accident(self):
        """Two draws at one path would make the first unrevealable, and the
        debrief would open a seal that belongs to a different rehearsal."""
        self._run("draw", "--out", self.path)
        again = self._run("draw", "--out", self.path)
        self.assertNotEqual(again.returncode, 0)
        self.assertIn("already holds a draw", again.stderr)


class TheSitemapModuleStillDoesNotFetch(unittest.TestCase):
    """**A tripwire, not a feature.** Rules 5 and 6 of the coordinates section
    are prospective: no adapter fetches a third-party sitemap today, so neither
    rule can fail today. #149, #151.

    **That is exactly the shape this repository has been bitten by** — a defect
    downstream of an absence cannot fail while the absence lasts, and then
    surfaces as a fresh breakage on the day it ends, at the worst moment and
    attributed to the wrong cause.

    `_sitemap.py` receives bodies and never URLs. **The day it grows a fetch,
    rule 5 stops being prospective**: whatever it fetches needs a verdict on
    the host actually contacted, and that host declared on the card. This case
    exists to make that day announce itself instead of passing unnoticed.

    It asserts nothing about whether fetching there is wrong. It asserts that
    the assumption the two rules were written under still holds.
    """

    def _module(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(root, "skills", "job-scan", "scripts",
                            "_sitemap.py")
        with open(path, encoding="utf-8") as fh:
            return path, fh.read()

    def test_it_parses_bodies_and_does_not_open_sockets(self):
        import re
        _path, src = self._module()
        opens = re.findall(r"urlopen|urllib\.request|http\.client|requests\.",
                           src)
        self.assertEqual(
            opens, [],
            "_sitemap.py has grown a fetch. Rule 5 of the coordinates section "
            "in shared/robots-policy.md was written on the assumption that it "
            "only parses: a sitemap may be declared on another host, and "
            "following it is a fetch of that host, which needs its own verdict "
            "and its own <!-- hosts: --> entry.")

    def test_the_only_sitemap_extractor_still_only_prints(self):
        """`workday.py` is the one place that reads `Sitemap:` out of a
        robots.txt. It enumerates; it does not follow. **Enumerating is not
        choosing** — the rule already written two sections above."""
        import re
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(root, "skills", "job-scan", "scripts",
                               "workday.py"), encoding="utf-8") as fh:
            src = fh.read()
        self.assertIn("Sitemap:", src,
                      "the extractor moved; this case now measures nothing")
        line = next((l for l in src.splitlines() if "Sitemap:" in l
                     and "re.findall" in l), None)
        self.assertIsNotNone(
            line, "workday.py no longer extracts Sitemap: with re.findall — "
                  "check whether it now follows them")


class AContentClaimSaysWhichOfThreeStatesItIsIn(unittest.TestCase):
    """**#140.** A board's content can be examined, and the result had nowhere
    in the repository to live — the last one lived only in published artefacts,
    readable by nobody holding the code.

    **The declaration has three states, not two**, and the third is the point.
    The fabrication sieve compares sets of title words and *assumes the corpora
    label in the same language*. That held by accident across eight anglophone
    African nodes; in Armenia three boards write in transliterated Armenian, in
    English and in percent-encoded Armenian, so the 0.3 % it returns cannot
    separate *independent* from *written differently*.

    **An inapplicable 0.3 % and a conclusive 0.3 % are indistinguishable once
    written down** — both are a number, a method and a date. So the state is
    part of the value.

    **No card carries the line yet, and this class is written to be useful
    anyway.** A corpus scan over an empty population is green by having nothing
    to check — the failure this suite has already shipped twice. So the
    vocabulary itself is exercised on examples, and the scan validates whatever
    real cards adopt it later.
    """

    # **Four states, and the fourth was found by a card, not by design.**
    # `tanqeeb.md` reports rules that could not be read on five of five hosts:
    # nothing was measured, nothing was assumed, and no instrument ran to fall
    # outside its domain. **"The examination could not be attempted" is not a
    # weaker form of any of the three** — it says the door was shut before the
    # question could be put, and a card forced into `assumed` would claim a
    # reading nobody made.
    STATES = ("measured", "assumed", "out-of-domain", "indeterminate")

    def _check(self, value):
        """Return a list of complaints about one `content:` value."""
        import re
        parts = [p.strip() for p in value.split("·")]
        bad = []
        if len(parts) != 3:
            return [f"wants <state> · <method or reason> · <YYYY-MM-DD>, "
                    f"got {len(parts)} field(s)"]
        state, reason, date = parts
        if state not in self.STATES:
            bad.append(f"unknown state {state!r}")
        if not reason:
            bad.append("no method or reason given")
        if not re.fullmatch(DATE_OR_INSTANT, date):
            bad.append(f"{date!r} is not a date: wants YYYY-MM-DD, optionally "
                       f"followed by a time")
        # **The date and the unit are part of the value**: a share expires by
        # the growth of its own denominator, so a measurement states a figure.
        if state == "indeterminate" and not re.search(r"\d", reason):
            bad.append("an indeterminate state says what could not be read, "
                       "and on how many hosts")
        if state == "measured" and not re.search(r"\d", reason):
            bad.append("a measurement carries a figure and its unit")
        return bad

    def test_the_three_states_are_accepted(self):
        for value in (
            "measured · fabrication sieve, 0.3% shared titles of 300 · "
            "2026-09-04",
            "out-of-domain · the sieve assumes one labelling language · "
            "2026-09-04",
            "assumed · read from the ad pages, no instrument run · 2026-09-04",
        ):
            with self.subTest(value=value[:40]):
                self.assertEqual(self._check(value), [], value)

    def test_a_fourth_state_is_refused(self):
        """**An open vocabulary is an absence with extra steps.** `unknown`
        and `partial` read like states and are not; either would let a card say
        nothing while looking like it said something."""
        for state in ("unknown", "partial", "probably", ""):
            with self.subTest(state=state):
                bad = self._check(f"{state} · something · 2026-09-04")
                self.assertTrue(bad, f"{state!r} was accepted as a state")

    def test_a_measurement_without_a_figure_is_refused(self):
        """*"measured · fabrication sieve · 2026-09-04"* is the shape that
        loses the denominator, and a share without one expires silently."""
        bad = self._check("measured · fabrication sieve · 2026-09-04")
        self.assertTrue(bad)

    def test_out_of_domain_still_has_to_say_why(self):
        """**The third state is not an escape hatch.** Its whole content is the
        precondition that failed; without it, it is `assumed` with a longer
        name."""
        self.assertTrue(self._check("out-of-domain ·  · 2026-09-04"))
        self.assertEqual(
            self._check("out-of-domain · the sieve assumes one labelling "
                        "language · 2026-09-04"), [])

    def test_a_malformed_date_is_refused(self):
        for date in ("04-09-2026", "2026-9-4", "yesterday", "2026"):
            with self.subTest(date=date):
                self.assertTrue(self._check(f"assumed · read · {date}"))

    def test_a_host_provenance_line_is_well_formed_wherever_it_appears(self):
        """**#140 point 3.** `<!-- hosts-source: <where read> · <YYYY-MM-DD> -->`
        — the field whose absence let `egyptjobsearch.com` sit for two days in
        fifty-one files already held, while a sibling count went from four to
        five to seven with its provenance never written down.

        Same shape as the `content:` line and checked the same way, including
        the README's own examples — because the corpus scan skips the README
        precisely because the README holds them.
        """
        import glob
        import re
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        found = 0
        for path in sorted(glob.glob(os.path.join(root, "shared", "boards",
                                                  "*.md"))):
            with open(path, encoding="utf-8") as fh:
                src = fh.read()
            for value in re.findall(r"<!--\s*hosts-source:\s*(.*?)\s*-->", src):
                found += 1
                with self.subTest(card=os.path.basename(path)):
                    parts = [p.strip() for p in value.split("·")]
                    self.assertEqual(
                        len(parts), 2,
                        f"wants <where it was read> · <YYYY-MM-DD>, got "
                        f"{len(parts)} field(s): {value!r}")
                    self.assertTrue(parts[0], "no source given")
                    self.assertRegex(
                        parts[1], r"^\d{4}-\d{2}-\d{2}$",
                        f"{parts[1]!r} is not a date: wants YYYY-MM-DD, "
                        f"optionally followed by a time")
        self.assertGreaterEqual(
            found, 2,
            "the README documents fewer than two examples of hosts-source; "
            "this case is worthless if it finds none, and the format it "
            "checks would go unchecked exactly where it is copied from")

    def test_the_specs_own_examples_satisfy_the_spec(self):
        """**The slip this catches is the one that happened.** The README first
        documented the line with *four* fields while the format takes three —
        method and figure written as separate segments instead of one. Nothing
        would have found it: the corpus scan skips the README because the README
        holds the examples, which is exactly why the examples go unchecked.

        **A format documented one way and parsed another is worse than an
        undocumented format**, because the first card to adopt it copies the
        example.
        """
        import re
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(root, "shared", "boards", "README.md"),
                  encoding="utf-8") as fh:
            src = fh.read()
        examples = re.findall(r"<!--\s*content:\s*(.*?)\s*-->", src)
        self.assertGreaterEqual(
            len(examples), 3,
            f"the README documents {len(examples)} example(s) of the line; it "
            f"should show all three states, and this case is worthless if it "
            f"finds none")
        states = set()
        for value in examples:
            with self.subTest(example=value[:44]):
                self.assertEqual(self._check(value), [], value)
            states.add(value.split("·")[0].strip())
        self.assertEqual(states, set(self.STATES),
                         f"the README shows {sorted(states)}; a state nobody "
                         f"documents is a state nobody writes")

    def test_any_card_that_adopts_the_line_is_well_formed(self):
        """The corpus half. **Empty today, and it says so** rather than
        reporting health: `test_the_three_states_are_accepted` is what proves
        this class works until a card carries the line."""
        import glob
        import re
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        seen, bad = 0, []
        for path in sorted(glob.glob(os.path.join(root, "shared", "boards",
                                                  "*.md"))):
            if os.path.basename(path) == "README.md":
                continue  # the spec, not a card: it holds the examples
            with open(path, encoding="utf-8") as fh:
                src = fh.read()
            m = re.search(r"<!--\s*content:\s*(.*?)\s*-->", src)
            if not m:
                continue
            seen += 1
            for complaint in self._check(m.group(1)):
                bad.append(f"{os.path.basename(path)}: {complaint}")
        self.assertEqual(bad, [], "; ".join(bad))
        self.assertGreaterEqual(seen, 0)


class AWhitelistIsNotAWall(unittest.TestCase):
    """**#152, and it is the invisible direction of the two.**

    `bebee.com` names this project and opens six path families to it, then
    closes the rest:

        User-Agent: ClaudeBot
        Allow: /*/jobs/        Allow: /*/people/     Allow: /*/blog/
        Allow: /*/salaries/    Allow: /*/skills/     Allow: /*/industry/
        Disallow: /

    The module answered *this host closes everything*. Two lines, two hundred
    apart: `verdict()` set `sweep=False` on the bare `Disallow: /` **without
    ever consulting the `Allow` list**, and `allowed()` returned on
    `if not v["sweep"]` **before** the `best_d`/`best_a` longest-match code —
    which was therefore unreachable in exactly the case where `Allow` lines
    mean anything. The docstring promised *"Longest match wins, `Allow` on a
    tie"*; the function did not do it.

    **A false refusal is worse than a false permission.** A false *yes*
    eventually produces a 403 somebody sees. A false *no* makes us not fetch,
    record the host as closed, and move on — and nothing in the result says a
    door was open. It is the mirror of #101, which was only ever found because
    it produced a refused fetch.

    **`sweep` stays `False`, and that is not a compromise.** A whitelist gives
    no list to sweep, so blind sweeping remains refused; what changes is that
    `allowed(host, path)` now answers the question it always claimed to.
    """

    # bebee.com/robots.txt, fetched 2026-09-04 — the ClaudeBot group verbatim,
    # with the `*` group kept so the group-selection half is exercised too.
    BODY = (
        "User-Agent: *\n"
        "Allow: /\n"
        "Disallow: /api/\n"
        "Disallow: /dashboard/\n"
        "\n"
        "User-Agent: ClaudeBot\n"
        "Allow: /*/jobs/\n"
        "Allow: /*/people/\n"
        "Allow: /*/blog/\n"
        "Allow: /*/salaries/\n"
        "Allow: /*/skills/\n"
        "Allow: /*/industry/\n"
        "Disallow: /\n"
    )

    class _Resp:
        def __init__(self, body):
            self._b = body.encode("utf-8")

        def read(self):
            return self._b

        def geturl(self):
            return "https://bebee.example/robots.txt"

        def getcode(self):
            return 200

        @property
        def headers(self):
            return {"Content-Type": "text/plain"}

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def _with(self, body):
        import _robots
        real = _robots.urllib.request.urlopen
        _robots._CACHE.clear()
        _robots._ALIAS.clear()
        _robots.urllib.request.urlopen = (
            lambda r, timeout=None, **k: self._Resp(body))
        try:
            return (_robots.verdict("bebee.example"),
                    {p: _robots.allowed("bebee.example", p) for p in (
                        "/es/jobs/x", "/en/people/y", "/dashboard/", "/api/v1",
                        "/")})
        finally:
            _robots.urllib.request.urlopen = real
            _robots._CACHE.clear()
            _robots._ALIAS.clear()

    def test_a_named_family_is_open(self):
        _v, a = self._with(self.BODY)
        self.assertTrue(a["/es/jobs/x"]["allowed"],
                        "a path the host opens to us by name was refused — "
                        "this is the false refusal of #152")
        self.assertEqual(a["/es/jobs/x"]["rule"], "/*/jobs/")
        self.assertEqual(a["/es/jobs/x"]["kind"], "allow")
        self.assertTrue(a["/en/people/y"]["allowed"])

    def test_everything_else_is_still_refused(self):
        """**The other half, and without it the fix is a hole.** Opening the
        whitelist must not open the site."""
        _v, a = self._with(self.BODY)
        for path in ("/dashboard/", "/api/v1", "/"):
            with self.subTest(path=path):
                self.assertFalse(a[path]["allowed"], f"{path} became readable")
                self.assertEqual(a[path]["rule"], "/")

    def test_the_sweep_stays_refused_and_says_why(self):
        """A whitelist gives nothing to sweep. The verdict must keep refusing
        the blind sweep **and** stop claiming everything is closed."""
        v, _a = self._with(self.BODY)
        self.assertFalse(v["sweep"])
        self.assertEqual(v.get("group"), "claudebot")
        self.assertIn("whitelist", v["reason"].lower())
        self.assertNotIn("closes everything", v["reason"])

    # ---- mutation, both directions, because one side proves nothing --------

    def test_without_the_allow_lines_it_is_a_wall_again(self):
        """**Direction one.** Strip the `Allow:` lines and the group is a plain
        refusal: the short-circuit must come back, or the fix has simply
        stopped refusing."""
        body = "\n".join(l for l in self.BODY.splitlines()
                          if not l.startswith("Allow: /*")) + "\n"
        self.assertNotIn("/*/jobs/", body, "the mutation did not apply")
        v, a = self._with(body)
        self.assertFalse(v["sweep"])
        self.assertFalse(a["/es/jobs/x"]["allowed"],
                         "with no Allow line, this path must be refused")
        self.assertEqual(a["/es/jobs/x"]["kind"], "host-closed")

    def test_without_the_disallow_slash_the_allows_are_not_what_decides(self):
        """**Direction two, and it is the one that catches a fix that only
        ever says yes.** Remove `Disallow: /` and the group closes nothing —
        so a path outside the whitelist must become open. A case that only
        goes red when `Allow` is removed would pass on a function that
        returned `True` unconditionally."""
        body = self.BODY.replace("Allow: /*/industry/\nDisallow: /\n",
                                 "Allow: /*/industry/\n")
        self.assertNotEqual(body, self.BODY, "the mutation did not apply")
        self.assertEqual(body.count("Disallow: /\n"), 0,
                         "the bare Disallow is still there")
        v, a = self._with(body)
        self.assertTrue(v["sweep"], "with no `Disallow: /` the site is open")
        self.assertTrue(a["/dashboard/"]["allowed"],
                        "nothing closes this path any more, yet it was refused")


class AShippedBoardIsListedWhereBoardsAreListed(unittest.TestCase):
    """**Five shipped adapters were invisible in the one table a user reads.**

    `emploitic`, `employtt`, `jobivoire`, `jobs-gov-pk` and `mihnati` each had a
    card, a `<!-- script: -->` that resolves, a `<!-- verified: 2026-09-03 -->`
    and declared hosts — and none appeared under *Which boards are available*.
    A board nobody can find is not shipped in any sense that matters to the
    person looking for it.

    **The card guards could not catch this**, and that is the interesting part:
    every one of them asks whether a card is well-formed, so a perfectly formed
    card that no index points at is invisible to all of them. **Completeness of
    each record says nothing about completeness of the set.**

    The reverse direction is checked too — a row naming a file that does not
    exist sends a reader to a missing page, which is worse than an absent row
    because it looks like an answer.

    **Cards without a script are deliberately exempt.** `bayt`,
    `chile-public-sector`, `melr-gh`, `saudi-labour-platforms` and
    `skillingpakistan` are investigation records: nothing ships, so nothing is
    promised, and listing them under *available* would be the opposite error.
    """

    def _registry(self):
        import re
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(root, "shared", "boards", "README.md")
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
        start = next((i for i, l in enumerate(lines)
                      if l.startswith("| Board | File")), None)
        self.assertIsNotNone(
            start, "the `| Board | File |` table header is gone — this guard "
                   "measures nothing until it is found again")
        end = start
        while end < len(lines) and lines[end].startswith("|"):
            end += 1
        listed = {m.group(1) for l in lines[start:end]
                  if (m := re.search(r"`([a-z0-9-]+)\.md`", l))}
        return root, listed

    def _with_script(self, root):
        import glob
        import re
        out = set()
        for path in glob.glob(os.path.join(root, "shared", "boards", "*.md")):
            name = os.path.basename(path)[:-3]
            if name == "README":
                continue
            with open(path, encoding="utf-8") as fh:
                m = re.search(r"<!--\s*script:\s*([^\s>]+)", fh.read())
            # **`script: none` is a declaration that nothing ships.**
            # `tanqeeb.md` says so and was reported as an unlisted shipped
            # adapter — the guard read the presence of the field as the
            # presence of a script, which is the same error as counting a key
            # instead of a value.
            if m and m.group(1).lower() not in ("none", "-", "—"):
                out.add(name)
        return out

    def test_every_card_that_ships_a_script_is_in_the_table(self):
        root, listed = self._registry()
        missing = sorted(self._with_script(root) - listed)
        self.assertEqual(
            missing, [],
            f"{len(missing)} shipped adapter(s) have a card and no row under "
            f"*Which boards are available*, so nobody reading the README can "
            f"find them: {missing}")

    def test_no_row_points_at_a_card_that_does_not_exist(self):
        """A row naming a missing file is worse than a missing row: it looks
        like an answer."""
        root, listed = self._registry()
        import glob
        files = {os.path.basename(p)[:-3]
                 for p in glob.glob(os.path.join(root, "shared", "boards",
                                                 "*.md"))} - {"README"}
        self.assertEqual(sorted(listed - files), [])

    def test_the_table_has_not_shrunk_to_nothing(self):
        """**The denominator.** Both checks above are set differences, and both
        pass on an empty table — the failure this suite has shipped twice."""
        _root, listed = self._registry()
        self.assertGreater(
            len(listed), 60,
            f"the registry lists {len(listed)} boards; the header was found "
            f"but the rows were not read")


class TheSearchLoopWasTheRefusedPath(unittest.TestCase):
    """**#156, and it is the mirror of #101 inside our own code.**

    `vieclam24h.py` asked `robots_verdict(host)` and nothing else.
    `vieclam24h.vn` has no `Disallow: /`, so that check answered *sweep* every
    time — and the file closes `/*?q` to `User-agent: *` while `cmd_search`
    fetched `/tim-kiem-viec-lam-nhanh?q=<terms>&page=<n>`. **The adapter's main
    loop was the refused path.**

    Nothing could have surfaced it. The host answers 200, the host-level
    verdict is true, and `get()` carried the comment *"robots.txt permits this
    path"* — **a claim of compliance sitting on the one path that is not
    compliant.** The claim is not a check, and this file held both for as long
    as it held the defect.

    Found by asking, of every adapter, *which paths do you actually fetch* —
    the population of the concerned rather than of the participants. Eighteen
    adapters query the guard by host only; seven of those face hosts carrying
    path rules; **one of the seven fetched a path those rules close.**
    """

    def _allowed(self, path):
        import urllib.parse
        import _robots
        parts = urllib.parse.urlsplit("https://vieclam24h.vn" + path)
        full = (parts.path or "/") + (("?" + parts.query) if parts.query else "")
        return _robots.allowed("vieclam24h.vn", full)

    RULES = "User-agent: *\nDisallow: /admin/\nDisallow: /*?q\nDisallow: /asset/\n"

    class _Resp:
        def __init__(self, body):
            self._b = body.encode()

        def read(self):
            return self._b

        def geturl(self):
            return "https://vieclam24h.vn/robots.txt"

        def getcode(self):
            return 200

        @property
        def headers(self):
            return {"Content-Type": "text/plain"}

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def setUp(self):
        import _robots
        self._real = _robots.urllib.request.urlopen
        _robots._CACHE.clear()
        _robots._ALIAS.clear()
        _robots.urllib.request.urlopen = (
            lambda r, timeout=None, **k: self._Resp(self.RULES))

    def tearDown(self):
        import _robots
        _robots.urllib.request.urlopen = self._real
        _robots._CACHE.clear()
        _robots._ALIAS.clear()

    def test_the_search_path_is_refused(self):
        a = self._allowed("/tim-kiem-viec-lam-nhanh?q=dev&page=1")
        self.assertFalse(a["allowed"],
                         "the search loop's own path must be refused — this is "
                         "the defect #156 found")
        self.assertEqual(a["rule"], "/*?q")

    def test_the_sitemap_route_is_untouched(self):
        """**The other half.** The fix must not close the way in: the ads are
        reached through the sitemap, and that path is permitted."""
        for path in ("/file/sitemap/sitemap-index.xml", "/job-abc", "/"):
            with self.subTest(path=path):
                self.assertTrue(self._allowed(path)["allowed"])

    def test_the_adapter_actually_stops(self):
        """**The exercised case, and the corpus scan below could not do this.**

        The first version of this class checked that `get()` *contains* the
        per-path call. Mutating `if a["allowed"] is False:` to `if False:`
        left it green: the import stayed, the call stayed, the branch did
        nothing. **A guard present and inert**, in the test written against
        exactly that failure.

        So the adapter is run. The refused path must raise `SystemExit(7)`
        before any request is built, and a permitted path must go through.
        """
        import importlib
        import _robots
        mod = importlib.import_module("vieclam24h")
        # **`_robots.urllib` and `vieclam24h.urllib` are the same module
        # object**, so replacing one replaces both — and the first version of
        # this case made the guard read the adapter's stubbed HTML as the rules
        # file, get `unrecognised`, and permit everything. The verdict is
        # settled here, under setUp's rules stub, before the opener is swapped.
        _robots.verdict("vieclam24h.vn")
        real = mod.urllib.request.urlopen
        reached = []

        class Resp:
            def read(self):
                return b"<html></html>"

            def getcode(self):
                return 200

            def geturl(self):
                return "https://vieclam24h.vn/x"

            @property
            def headers(self):
                return {"Content-Type": "text/html; charset=utf-8"}

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        def fake(req, *a, **k):
            reached.append(getattr(req, "full_url", str(req)))
            return Resp()

        mod.urllib.request.urlopen = fake
        try:
            with self.assertRaises(SystemExit, msg=(
                    "the search loop's refused path was fetched anyway")) as c:
                mod.get("/tim-kiem-viec-lam-nhanh?q=dev&page=1")
            self.assertEqual(c.exception.code, 7)
            self.assertEqual(reached, [],
                             f"a request was built before the refusal: "
                             f"{reached}")
            code, _body = mod.get("/job-abc")
            self.assertEqual(code, 200, "the permitted path stopped too — a "
                                        "fix that refuses everything is not a "
                                        "fix")
        finally:
            mod.urllib.request.urlopen = real

    def test_the_adapter_asks_about_the_path_not_only_the_host(self):
        """**The behavioural half.** A host-level verdict cannot see this, so
        checking that the module imports `allowed` is the property that
        matters — `verdict` alone is what shipped the defect."""
        import re
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        with open(os.path.join(root, "skills", "job-scan", "scripts",
                               "vieclam24h.py"), encoding="utf-8") as fh:
            src = fh.read()
        self.assertRegex(
            src, r"from _robots import allowed",
            "vieclam24h.py no longer asks about paths; a host verdict answers "
            "`sweep` for this host and says nothing about `/*?q`")
        self.assertIn("robots_allowed(parts.netloc", src,
                      "the per-path call is gone from get()")


class TheSieveCarriesItsOwnControls(unittest.TestCase):
    """`_overlap.py` — the fabricated-network check, made a tool. #157.

    **Its positive control refuted its own first design, in the first run.**
    That version split corpus A in two halves and compared them: same source,
    so it must come out high. It returned 0.0 % — correctly, because two halves
    of one corpus hold *different* advertisements and this sieve compares
    advertisements. **A control that cannot come out high on a corpus that is
    copying is not a control**, and it refused every run in the same breath as
    it refuted itself. No re-reading would have found that; running it did.

    The control now plants the phenomenon: A against a corpus that copied half
    of A verbatim, which must find roughly that half.
    """

    def _mod(self):
        import importlib
        return importlib.import_module("_overlap")

    A = ["senior railway operations manager", "digital content strategist",
         "infrastructure project coordinator", "e commerce operations lead",
         "clinical pharmacy supervisor", "warehouse logistics planner",
         "civil structural site engineer", "regional sales account director",
         "data quality assurance analyst", "human resources payroll officer",
         "marine cargo survey inspector", "primary school mathematics teacher"]

    def test_a_copied_corpus_is_seen(self):
        """**Direction one.** Half of A, verbatim, inside B."""
        m = self._mod()
        b = self.A[:6] + ["totally unrelated hairdressing apprentice role"]
        v = m.verdict(self.A, b)
        self.assertEqual(v["state"], "measured", v.get("reason"))
        self.assertGreaterEqual(v["observed"]["rate"], 50.0,
                                "copying was planted and not found")

    def test_an_unrelated_corpus_is_not(self):
        """**Direction two, and without it the first proves nothing** — a sieve
        that always says yes would pass the test above."""
        m = self._mod()
        b = ["boulanger patissier tourier", "chauffeur poids lourd regional",
             "aide soignante de nuit", "menuisier agenceur atelier",
             "technicienne de laboratoire", "agent de securite incendie"]
        v = m.verdict(self.A, b)
        self.assertLess(v["observed"]["rate"], 10.0)

    def test_the_place_name_never_reaches_the_key(self):
        """**The failure that produces a perfect and false negative.** A key
        carrying the country returns 0.0 % on every pair, because the one token
        guaranteed to differ decides the answer."""
        m = self._mod()
        k = m.key("Railway operations manager job vacancy in Mombasa Kenya")
        for gone in ("kenya", "job", "vacancy"):
            self.assertNotIn(gone, k, f"{gone!r} survived into the key")
        self.assertIn("railway", k)

        # **What is guaranteed, and what is not.** Country names are
        # enumerable and are stripped. City names are not: `mombasa` survives
        # this key, and it was this test that found it. A hand-kept list of
        # every city on earth is not a thing to promise, so the module
        # promises the countries, offers `--show-key` for the rest, and says
        # so rather than implying a completeness it cannot hold.
        self.assertIn("mombasa", k,
                      "if city names are now stripped, say which and stop "
                      "claiming only countries are")

    def test_a_broken_instrument_refuses_to_report(self):
        """**The state that matters most.** When the positive control fails,
        the run must say `out-of-domain` rather than hand back a rate — the
        result that has every appearance of a measurement and is not one."""
        m = self._mod()
        v = m.verdict(["one two three"], ["four five six"])
        self.assertEqual(v["state"], "out-of-domain")
        self.assertIn("control", v["reason"])

    def test_the_positive_control_can_fail(self):
        """**And the guard must be able to go the other way.** A control that
        cannot fail is decoration: fed a corpus with no repeatable content, the
        planted copy is still found, so failure has to come from a real
        inability — here, too few labels to plant into."""
        m = self._mod()
        v = m.verdict(self.A[:3], self.A[:3])
        self.assertEqual(v["state"], "out-of-domain")
        self.assertIsNone(v["control_positive"]["rate"])


class ACountedCardNamesItsWitnessOrSaysThereIsNone(unittest.TestCase):
    """**A count taken once and a count corroborated are written identically.**

    Six adapters shipped on 2026-09-04 with a figure from a sitemap. Two had a
    second source and four did not, and nothing on the cards distinguished
    them — so a reader had no way to tell `2 644 against the site's own 2 573`
    from `367, once, from one file`.

    **The difference is not academic.** `jobsbotswana.info` published 367 as the
    size of the board; its own listing reports 5 123 and its pagination runs to
    page 342. The sitemap was a nine-month slice of a nine-year archive, and
    `raw == distinct` with no gaps had looked like completeness. **A single-file
    sitemap that omits advertisements has exactly the signature of one that does
    not.**

    So a card carrying a `content: measured` line carries a `witness:` line
    too. **`none found` is a valid and useful value** — it records that the
    question was asked, which is what `content:` alone cannot say.
    """

    def _cards(self):
        import glob
        import re
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        out = []
        for path in sorted(glob.glob(os.path.join(root, "shared", "boards",
                                                  "*.md"))):
            if os.path.basename(path) == "README.md":
                continue
            with open(path, encoding="utf-8") as fh:
                src = fh.read()
            content = re.search(r"<!--\s*content:\s*(.*?)\s*-->", src)
            witness = re.search(r"<!--\s*witness:\s*(.*?)\s*-->", src)
            out.append((os.path.basename(path)[:-3],
                        content.group(1) if content else None,
                        witness.group(1) if witness else None))
        return out

    def test_every_measured_card_declares_a_witness(self):
        missing = [n for n, c, w in self._cards()
                   if c and c.startswith("measured") and not w]
        self.assertEqual(
            missing, [],
            f"{len(missing)} card(s) publish a measured count with no "
            f"`witness:` line, so a figure taken once reads exactly like one "
            f"corroborated: {missing}")

    def test_a_witness_line_says_something(self):
        """An empty declaration is worse than none: it answers the question
        without carrying the answer."""
        bad = [n for n, _c, w in self._cards() if w is not None and len(w) < 12]
        self.assertEqual(bad, [], f"witness lines too short to mean anything: "
                                  f"{bad}")

    def test_the_population_is_not_empty(self):
        """**The floor.** Both checks above pass on a corpus with no measured
        cards at all — the shape this suite has shipped twice."""
        measured = [n for n, c, _w in self._cards()
                    if c and c.startswith("measured")]
        self.assertGreaterEqual(
            len(measured), 5,
            f"only {len(measured)} card(s) carry a measured count; this guard "
            f"is checking almost nothing")


class AHostVerdictCanBeTrueAndTheWrongAnswer(unittest.TestCase):
    """**#156, and it is the sharpest instance of #101 we have found.**

    `zhipin.com` — BOSS Zhipin, one of China's four largest boards — sweeps.
    No `Disallow: /`, forty path rules, and a host-level verdict answers *yes*.

    **And one of those forty rules closes a subset of its advertisements by the
    first letter of the slug:**

        Disallow: /job_detail/l*.html

    `/job_detail/abc123.html` is open. `/job_detail/l9f8.html` is closed. **Same
    host, same directory, same kind of page — and a character decides.**

    **An adapter that asks `verdict()` and then reads all of `/job_detail/`
    would violate the file on part of its corpus and nothing would say so.**
    Those pages answer 200: the refusal exists only in the rules file, and only
    for someone who asks about the path. This is not a refinement of the host
    question, it is the only question with an answer.

    **Both directions, because a guard that only checks the refusal goes green
    by refusing everything.** That failure shipped in this repository twice.
    """

    # `zhipin.com/robots.txt`, the `*` group, fetched 2026-09-05. Trimmed to
    # the rules that matter here; the full group carries forty.
    BODY = ("User-agent: *\n"
            "Disallow: /*?query=*\n"
            "Disallow: /*.js*\n"
            "Disallow: /job_detail/l*.html\n"
            "Disallow: /sem/*\n")

    class _Resp:
        def __init__(self, body):
            self._b = body.encode("utf-8")

        def read(self):
            return self._b

        def geturl(self):
            return "https://zhipin.example/robots.txt"

        def getcode(self):
            return 200

        @property
        def headers(self):
            return {"Content-Type": "text/plain"}

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def setUp(self):
        import _robots
        self._real = _robots.urllib.request.urlopen
        _robots._CACHE.clear()
        _robots._ALIAS.clear()
        _robots.urllib.request.urlopen = (
            lambda r, timeout=None, **k: self._Resp(self.BODY))

    def tearDown(self):
        import _robots
        _robots.urllib.request.urlopen = self._real
        _robots._CACHE.clear()
        _robots._ALIAS.clear()

    def _allowed(self, path):
        import _robots
        return _robots.allowed("zhipin.example", path)

    def test_the_host_verdict_says_yes(self):
        """**The premise, and it must hold or the case proves nothing.** If
        this host ever grows a `Disallow: /`, the trap disappears and so does
        the demonstration."""
        import _robots
        v = _robots.verdict("zhipin.example")
        self.assertTrue(v["sweep"],
                        "the host no longer sweeps, so a host-level verdict "
                        "would already refuse and this case is moot")

    def test_an_ordinary_advertisement_is_open(self):
        """**Direction one.** Without it, a fix that refuses everything passes
        the next test and looks correct."""
        a = self._allowed("/job_detail/abc123.html")
        self.assertTrue(a["allowed"], f"refused an open path: {a['reason']}")
        self.assertIsNone(a["rule"])

    def test_the_letter_l_closes_the_same_directory(self):
        """**Direction two.** Same host, same directory, same kind of page."""
        for path in ("/job_detail/l9f8.html", "/job_detail/lz-abc.html"):
            with self.subTest(path=path):
                a = self._allowed(path)
                self.assertFalse(
                    a["allowed"],
                    f"{path} is closed by `Disallow: /job_detail/l*.html` and "
                    f"was permitted — an adapter reading the directory would "
                    f"fetch it and get a 200")
                self.assertEqual(a["rule"], "/job_detail/l*.html")

    def test_the_two_answers_come_from_one_host_verdict(self):
        """**The point of the whole class.** One host, one `sweep: True`, and
        two opposite answers for two paths — so the host verdict is not
        insufficient, it is *true and about the wrong object*."""
        import _robots
        v = _robots.verdict("zhipin.example")
        open_ = self._allowed("/job_detail/abc123.html")
        shut = self._allowed("/job_detail/l9f8.html")
        self.assertTrue(v["sweep"])
        self.assertNotEqual(open_["allowed"], shut["allowed"])
        self.assertEqual(open_["sweep"], shut["sweep"],
                         "both paths report the same host verdict, which is "
                         "exactly why it cannot be the answer")


class ACountOfLocsIsNotACountOfAdvertisements(unittest.TestCase):
    """**#154.** `irantalent.com` publishes 6 932 URLs under `/en/jobs/` and
    **none is an advertisement** — they are category landing pages. The number
    is the right order of magnitude for a country that size, stable,
    reproducible, and it measures nothing.

    **The assertions here are on the counter, not on the verdict.** The issue
    asked for exactly that: *"0 advertisements retained of 6 932", not "the
    guard refused"* — because a guard green on a denominator it shrank itself
    proves nothing, and this suite has shipped that failure twice.

    **And the signal is not a predicate on the URL**, which was the other thing
    asked. `/en/jobs/banking-investment-jobs` and `/en/jobs/<slug>-<id>` have
    the same shape on the same host; a pattern separating them condemns
    `ergodotisi.com`, which serves `vacancy-4312e752-36722372` and
    `senior-ai-engineer-91183625` side by side and means both.

    What is asked of each page is *do you present yourself as one of many* —
    pagination. Measured live 2026-09-05: **30 markers on each of two
    irantalent category pages, 0 on advertisements from ergodotisi, keejob,
    job.am, hellojob and jobsbotswana, and 1 on onape.td.** Six sites, three
    continents, and the threshold is not tuned to a specimen.
    """

    LIST = ('<html><nav class="pagination"><a href="?page=2">2</a>'
            '<a href="?page=3">3</a></nav><link rel="next" href="?page=2">'
            '<a href="/en/jobs/x?page=4">4</a></html>')
    RECORD = ('<html><h1>Senior AI Engineer</h1><p>Nicosia</p>'
              '<a href="/en-CY/companies/acme">Acme</a></html>')
    # `onape.td` advertisements carry exactly one stray marker.
    RECORD_ONE = '<html><h1>Chef de base</h1><a href="/blog?page=2">blog</a></html>'

    def _mod(self):
        import importlib
        return importlib.import_module("_records")

    def test_the_specimen_returns_zero_of_six_thousand(self):
        """**The counter, as the issue asked.** Not "it refused" — *how many
        of how many*."""
        m = self._mod()
        urls = [f"https://x.example/en/jobs/cat-{i}" for i in range(6932)]
        v = m.audit(urls, lambda u: self.LIST, sample_size=8, seed=1)
        self.assertEqual(v["of"], 6932)
        self.assertEqual(v["records"], 0, "a category page was counted as an "
                                          "advertisement")
        self.assertEqual(v["lists"], 8)
        self.assertEqual(v["state"], "lists")

    def test_a_real_board_is_counted(self):
        """**The other direction, and without it a guard that refuses
        everything passes the test above.**"""
        m = self._mod()
        urls = [f"https://y.example/en-CY/jobs/vacancy-{i}" for i in range(2644)]
        v = m.audit(urls, lambda u: self.RECORD, sample_size=8, seed=1)
        self.assertEqual(v["state"], "records")
        self.assertEqual(v["records"], 8)
        self.assertEqual(v["of"], 2644)

    def test_one_stray_marker_is_not_a_list(self):
        """`onape.td` carries exactly one `page=` in an unrelated link.
        **Condemning it would be the false accusation**, which is the worse
        direction: it invites a fix to code that was right."""
        m = self._mod()
        self.assertFalse(m.looks_like_list(self.RECORD_ONE))
        self.assertEqual(m.markers(self.RECORD_ONE), 1)

    def test_a_mixed_sample_refuses_rather_than_scaling(self):
        """**Refused, not reduced.** A count quietly scaled is the same defect
        wearing a different number."""
        m = self._mod()
        pages = [self.LIST, self.RECORD] * 4
        it = iter(pages)
        v = m.audit(list(range(100)), lambda u: next(it), sample_size=8, seed=1)
        self.assertEqual(v["state"], "mixed")
        self.assertIsNone(v.get("scaled"))
        self.assertIn("refused", v["reason"])

    def test_an_unreadable_sample_returns_no_figure(self):
        """A figure from a sample that was never read is the defect itself."""
        m = self._mod()
        v = m.audit(list(range(50)), lambda u: None, sample_size=5)
        self.assertEqual(v["state"], "unknown")
        self.assertIsNone(v["share"])
        self.assertEqual(v["unreadable"], 5)

    def test_the_sample_is_random_not_the_head(self):
        """**A contiguous slice from one end is not a sample.** On
        `jobsbotswana.info` the last eight sitemap entries were one
        advertiser's batch and gave a rate two and a half times the truth."""
        m = self._mod()
        seen = []
        m.audit(list(range(1000)), lambda u: (seen.append(u), self.RECORD)[1],
                sample_size=8, seed=4)
        self.assertEqual(len(seen), 8)
        self.assertNotEqual(seen, list(range(8)), "the sample is the head")
        self.assertGreater(max(seen), 100, "the sample never left the start")


class WhichOfOurTokensMayFetch(unittest.TestCase):
    """**#139 — the restrictive reading is abandoned, by the owner's decision
    of 2026-09-05.**

    Until then `verdict()` unioned the refusals of every record naming us: a
    host that opened `Claude-User` and closed `ClaudeBot` was reported closed,
    and the arbitration was left to a person. The decision:

    | the rules say | what happens |
    | :-- | :-- |
    | `ClaudeBot` **or** `Claude-User` permitted | present as the permitted one, ordinary HTTP |
    | both refused | drive the browser with the plugin |

    **What this changed, measured the same day: nine hosts across seven
    countries.** Every board this repository had published as refusing us —
    `duapune`, `gjejpune24`, `pngjobseek`, `nigerjob`, `emploimauritanie`,
    `libyanjobs`, `cypruswork`, `cyprusjobs`, `jobs.ps` — closes `ClaudeBot`
    and **opens `Claude-User`**. The refusals were real and were not aimed at
    the thing we do.

    **It chooses; it does not retry.** `shared/robots-policy.md` forbids
    rotating agents after a refusal and that stands: the token is settled from
    the rules before any content request, and a refusal received under the
    chosen token is a refusal.
    """

    CLOSED_TO_BOT = ("User-agent: ClaudeBot\nDisallow: /\n\n"
                     "User-agent: Claude-User\nDisallow: /private/\n")
    CLOSED_TO_BOTH = ("User-agent: ClaudeBot\nDisallow: /\n\n"
                      "User-agent: Claude-User\nDisallow: /\n")
    OPEN = "User-agent: *\nDisallow: /wp-admin/\n"

    class _Resp:
        def __init__(self, body):
            self._b = body.encode("utf-8")

        def read(self):
            return self._b

        def geturl(self):
            return "https://h.example/robots.txt"

        def getcode(self):
            return 200

        @property
        def headers(self):
            return {"Content-Type": "text/plain"}

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def _identity(self, body, path="/"):
        import _robots
        real = _robots.urllib.request.urlopen
        _robots._CACHE.clear()
        _robots._ALIAS.clear()
        _robots.urllib.request.urlopen = (
            lambda r, timeout=None, **k: self._Resp(body))
        try:
            return _robots.identity("h.example", path)
        finally:
            _robots.urllib.request.urlopen = real
            _robots._CACHE.clear()
            _robots._ALIAS.clear()

    def test_one_token_closed_the_other_open_is_http(self):
        """**The nine-host case.** Under the old reading this was `closed`."""
        i = self._identity(self.CLOSED_TO_BOT)
        self.assertEqual(i["state"], "http")
        self.assertEqual(i["token"], "claude-user")
        self.assertFalse(i["per_token"]["claudebot"]["allowed"])
        self.assertTrue(i["per_token"]["claude-user"]["allowed"])

    def test_both_closed_is_the_browser_branch(self):
        """**The other direction, and without it a resolver that always says
        `http` passes the test above.**"""
        i = self._identity(self.CLOSED_TO_BOTH)
        self.assertEqual(i["state"], "browser")
        self.assertIsNone(i["token"])
        self.assertIn("browser", i["reason"])

    def test_the_path_is_asked_about_not_the_host(self):
        """`Claude-User` is open on `/` and closed on `/private/` in the same
        file — so the answer depends on the path, as #156 required."""
        self.assertEqual(self._identity(self.CLOSED_TO_BOT, "/")["state"],
                         "http")
        shut = self._identity(self.CLOSED_TO_BOT, "/private/x")
        self.assertEqual(shut["state"], "browser",
                         "a path closed to both tokens is the browser branch "
                         "even when the host is open to one of them elsewhere")

    def test_an_unreadable_file_is_not_the_browser_branch(self):
        """**An unknown is not a refusal**, and it is not a licence to open a
        browser either. #118's third state, one layer up."""
        import _robots
        real = _robots.urllib.request.urlopen
        _robots._CACHE.clear()
        _robots._ALIAS.clear()

        def boom(*a, **k):
            raise _robots.urllib.error.URLError("stubbed")

        _robots.urllib.request.urlopen = boom
        # The module retries with a jittered back-off, which is right in
        # production and thirteen seconds here. The ladder itself is exercised
        # elsewhere; this case is about the verdict at the end of it.
        real_sleep = _robots.time.sleep
        _robots.time.sleep = lambda *_a, **_k: None
        try:
            i = _robots.identity("h.example", "/")
        finally:
            _robots.urllib.request.urlopen = real
            _robots.time.sleep = real_sleep
            _robots._CACHE.clear()
            _robots._ALIAS.clear()
        self.assertEqual(i["state"], "unknown")
        self.assertIsNone(i["token"])

    def test_an_open_host_prefers_the_user_token(self):
        """When both are permitted the request is a person's, and
        `Claude-User` is the token that says so."""
        i = self._identity(self.OPEN)
        self.assertEqual(i["state"], "http")
        self.assertEqual(i["token"], "claude-user")

    def test_the_cache_does_not_hand_one_token_the_other_s_verdict(self):
        """**The defect this nearly shipped with.** `verdict()` caches by host,
        and `identity()` asks the same host twice under different tokens. A key
        of the host alone returns the first answer to the second caller — a
        wrong verdict arriving with a correct-looking reason."""
        i = self._identity(self.CLOSED_TO_BOT)
        self.assertNotEqual(i["per_token"]["claudebot"]["allowed"],
                            i["per_token"]["claude-user"]["allowed"],
                            "both tokens received the same verdict; the cache "
                            "key has lost the agents")


class SweepFollowsTheResolutionAtTheRoot(unittest.TestCase):
    """**#153.** A group carrying both `Allow: /` and `Disallow: /` resolves,
    by the tie rule this module applies everywhere else, to *everything
    permitted*. `verdict()` reported `sweep: False` there anyway.

    **One file, two opposite answers from us**: `allowed(host, path)` said yes
    to every path while `verdict()` said the host could not be swept. Safe in
    both naive readings, and therefore defensible — but **indistinguishable
    from an oversight**, because no line said it was a choice. The issue named
    that third state as the thing to avoid, and it was the state we were in.

    **`sweep` now follows the resolution at `/`.** The distinction that matters
    is preserved: a whitelist — `Allow: /*/jobs/` beside `Disallow: /`, which
    `bebee.com` publishes — still reports `sweep: False`, because `/` itself is
    refused and there is no list to sweep blindly. Only the self-contradicting
    group changes.

    **The known population is two and it doubled in eight hours** — `bebee.com`
    on 2026-09-04, `northcyprus.cv` the same evening — so the count is not
    stable and is not used here to argue the change is small.
    """

    WHITELIST = "User-agent: ClaudeBot\nAllow: /*/jobs/\nDisallow: /\n"
    CONTRADICTION = "User-agent: ClaudeBot\nAllow: /\nDisallow: /\n"
    WALL = "User-agent: ClaudeBot\nDisallow: /\n"
    OPEN = "User-agent: *\nDisallow: /admin/\n"

    class _Resp:
        def __init__(self, body):
            self._b = body.encode("utf-8")

        def read(self):
            return self._b

        def geturl(self):
            return "https://h.example/robots.txt"

        def getcode(self):
            return 200

        @property
        def headers(self):
            return {"Content-Type": "text/plain"}

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    def _read(self, body, paths=("/",)):
        import _robots
        real = _robots.urllib.request.urlopen
        _robots._CACHE.clear()
        _robots._ALIAS.clear()
        _robots.urllib.request.urlopen = (
            lambda r, timeout=None, **k: self._Resp(body))
        try:
            v = _robots.verdict("h.example")
            a = {p: _robots.allowed("h.example", p) for p in paths}
            return v, a
        finally:
            _robots.urllib.request.urlopen = real
            _robots._CACHE.clear()
            _robots._ALIAS.clear()

    def test_a_self_contradicting_group_sweeps(self):
        v, a = self._read(self.CONTRADICTION)
        self.assertTrue(v["sweep"])
        self.assertTrue(a["/"]["allowed"])

    def test_a_whitelist_still_does_not_sweep(self):
        """**The direction that a fix saying yes everywhere would break.**
        `/` is refused, so there is no list to sweep — and the named family is
        still open, which is #152's half."""
        v, a = self._read(self.WHITELIST, ("/", "/x/jobs/1"))
        self.assertFalse(v["sweep"])
        self.assertFalse(a["/"]["allowed"])
        self.assertTrue(a["/x/jobs/1"]["allowed"],
                        "the whitelist stopped working; #152 regressed")

    def test_a_plain_wall_still_does_not_sweep(self):
        v, a = self._read(self.WALL)
        self.assertFalse(v["sweep"])
        self.assertFalse(a["/"]["allowed"])

    def test_sweep_and_allowed_never_disagree_at_the_root(self):
        """**The point of the change, asserted as the invariant it is.** Two
        answers from one file was the defect; this is the property that
        forbids it returning."""
        for name, body in (("whitelist", self.WHITELIST),
                           ("contradiction", self.CONTRADICTION),
                           ("wall", self.WALL), ("open", self.OPEN)):
            with self.subTest(file=name):
                v, a = self._read(body)
                self.assertEqual(
                    bool(v["sweep"]), bool(a["/"]["allowed"]),
                    f"{name}: verdict says sweep={v['sweep']} and allowed('/') "
                    f"says {a['/']['allowed']} — one file, two answers")

    def test_the_counter_not_only_the_verdict(self):
        """The issue asked for the number of paths judged permitted, not just
        the boolean: **a guard whose red can come from elsewhere proves
        nothing.**"""
        paths = ("/", "/x/jobs/1", "/anything", "/deep/er/still")
        _v, a = self._read(self.CONTRADICTION, paths)
        self.assertEqual(sum(1 for p in paths if a[p]["allowed"]), 4)
        _v2, a2 = self._read(self.WHITELIST, paths)
        self.assertEqual(sum(1 for p in paths if a2[p]["allowed"]), 1)


class ARefusedNameIsNotAlwaysANameWeSend(unittest.TestCase):
    """`OUR_AGENTS` has six names; `FETCH_TOKENS` has the two we can arrive as.

    **A refusal that names this project and a refusal that names an agent we
    could present as are different facts, and until 2026-09-05 `verdict()` gave
    them the same sentence.** `albaniajobs.al` refuses `anthropic-ai` — a name
    for this project that no request from here ever carries — and came back as
    *"a refusal that names this project"*. That sentence was copied onto a
    country page as **the one refusal actually written by an editor**, against
    two others attributed to a CDN template. It is true as written and it reads
    as the editor having shut the door on us by name.

    So this checks the sentence, not the verdict — and it checks **both
    directions**, because a guard that only rejects the bad case can be
    satisfied by a note that says nothing on either.

    **The verdict itself is asserted unchanged.** Whether a refusal aimed at a
    sibling name binds us is the owner's arbitration, not this module's, and
    the restrictive reading stands (`nos-agents-lecture-restrictive.md`).
    Without that third assertion this class could be made green by opening the
    host, which would be the opposite of the intended change.
    """

    TEMPLATE = ("User-agent: *\nDisallow:\n\n"
                "User-agent: {tok}\nDisallow: /\n")

    def _verdict(self, token):
        import _robots
        real = _robots.urllib.request.urlopen
        _robots._CACHE.clear()
        _robots._ALIAS.clear()
        body = self.TEMPLATE.format(tok=token).encode()

        class R(io.BytesIO):
            headers = {"Content-Type": "text/plain"}

            def geturl(self):
                return "https://h.example/robots.txt"

            def getcode(self):
                return 200

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        _robots.urllib.request.urlopen = lambda *a, **k: R(body)
        try:
            return _robots.verdict("h.example")
        finally:
            _robots.urllib.request.urlopen = real
            _robots._CACHE.clear()
            _robots._ALIAS.clear()

    def test_a_name_we_never_send_is_reported_as_one(self):
        import _robots
        for tok in _robots.OUR_AGENTS:
            if tok in _robots.FETCH_TOKENS:
                continue
            with self.subTest(token=tok):
                v = self._verdict(tok)
                self.assertIs(v["sweep"], False,
                              f"{tok}: the restrictive reading must still bind")
                self.assertIn(
                    "never sends", v["reason"],
                    f"`{tok}` is not a token a request can carry, and the "
                    f"reason line does not say so. A country page copied this "
                    f"sentence and published the refusal as the editor's, "
                    f"aimed at us.")

    def test_a_name_we_do_send_is_reported_as_one(self):
        import _robots
        for tok in _robots.FETCH_TOKENS:
            with self.subTest(token=tok):
                v = self._verdict(tok)
                self.assertIn(
                    "a request from here can present", v["reason"],
                    f"`{tok}` IS a token we arrive as, and the reason line no "
                    f"longer says so — a note that is silent in both cases "
                    f"passes the other half of this class while telling a "
                    f"reader nothing.")

    def test_the_restrictive_verdict_is_unchanged(self):
        """The sentence changed; the decision did not, and must not have."""
        import _robots
        for tok in _robots.OUR_AGENTS:
            with self.subTest(token=tok):
                v = self._verdict(tok)
                self.assertIs(v["sweep"], False,
                              f"{tok}: a sweep refusal stopped being one")
                self.assertEqual(v["allow"], [],
                                 f"{tok}: the refusing group grew an Allow")


class AFetchedBodyCarriesItsProvenanceOrIsNotWritten(unittest.TestCase):
    """Eight files were made permanently unattributable on 2026-09-05.

    A recount of the Cloudflare managed default found 28 bodies **identical to
    the byte**. The file contains no reference to the host serving it — no
    `Sitemap:`, no canonical, nothing. **The filename was the only place the
    host existed, and it had been abbreviated.** `sl_rb` meant Somaliland; the
    obvious repair, reading sibling files that share the country prefix,
    answers *Sierra Leone*. **The instrument is refuted on the one case where
    its answer could be checked** — which is the only reason anyone knows.

    So this class checks the class of defect, not those eight files. And it
    checks it **from the absent side**: that a body written without provenance
    is *seen*. A guard that can only confirm the good case confirms nothing —
    `garde-doit-echouer-sur-sa-portee`, `garde-presente-et-inerte`.
    """

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.dir, True)

    def _mod(self):
        import _provenance
        return _provenance

    def test_the_three_fields_have_no_defaults(self):
        """**Omitting one fails at the call**, not as a blank field found the
        next day. That is the whole difference between a guard and a habit."""
        P = self._mod()
        full = dict(url="https://h.example/robots.txt", status=200, agent="UA")
        for missing in ("url", "status", "agent"):
            kw = {k: v for k, v in full.items() if k != missing}
            with self.subTest(missing=missing):
                with self.assertRaises(TypeError, msg=(
                        f"`{missing}` acquired a default. A body saved without "
                        f"it looks complete and cannot be attributed later.")):
                    P.save(os.path.join(self.dir, "b.txt"), b"x", **kw)

    def test_a_body_without_a_sidecar_is_refused_not_returned(self):
        P = self._mod()
        orphan = os.path.join(self.dir, "orphan.txt")
        with open(orphan, "wb") as f:
            f.write(b"User-agent: *\n")
        with self.assertRaises(FileNotFoundError) as cm:
            P.load(orphan)
        # **Not any FileNotFoundError.** With the sidecar check removed, `open`
        # raises the same type one line later and this test passed for a reason
        # that had nothing to do with the guard. Measured: the mutation was
        # green. So the message is asserted, because it is what distinguishes
        # the refusal from the accident.
        self.assertIn("unattributable", str(cm.exception),
                      "the raise came from somewhere other than the sidecar "
                      "check — a guard satisfied by an accident is inert")

    def test_the_audit_sees_the_absence_and_names_its_denominator(self):
        """**The failing direction.** Three bodies with provenance, two
        without: the audit must report two, name them, and report the five it
        walked. Asserting only `orphan_count == 0` on a clean tree would pass
        on a walker that found nothing at all."""
        P = self._mod()
        for i in range(3):
            P.save(os.path.join(self.dir, f"ok{i}.txt"), b"body",
                   url=f"https://h{i}.example/robots.txt", status=200,
                   agent="UA")
        for i in range(2):
            with open(os.path.join(self.dir, f"bad{i}.txt"), "wb") as f:
                f.write(b"body")
        a = P.audit(self.dir)
        self.assertEqual(a["of"], 5,
                         "the walk did not see five bodies — a guard green on "
                         "a denominator it shrank itself proves nothing")
        self.assertEqual(a["orphan_count"], 2, a["orphans"])
        self.assertEqual(sorted(os.path.basename(x) for x in a["orphans"]),
                         ["bad0.txt", "bad1.txt"],
                         "the audit counted two and named the wrong two — "
                         "same cardinal, different members")

    def test_the_recorded_figures_are_of_the_raw_bytes(self):
        """**Not stripped.** Three `robots.txt` looked as though they had
        changed overnight — different byte counts *and* different md5 — and it
        was one trailing newline on one side. A md5 depends on no counting
        method; it depends on the body, and the body had been trimmed."""
        P = self._mod()
        body = b"User-agent: *\nDisallow:\n"
        rec = P.save(os.path.join(self.dir, "raw.txt"), body,
                     url="https://h.example/robots.txt", status=200,
                     agent="UA")
        self.assertEqual(rec["bytes"], len(body))
        self.assertEqual(rec["md5"], hashlib.md5(body).hexdigest())
        self.assertNotEqual(
            rec["md5"], hashlib.md5(body.rstrip()).hexdigest(),
            "the record holds the md5 of a stripped body — that is the exact "
            "reading that fabricated a change in three files")
        # **Read it back off the disk.** Checking only the returned record
        # tests `describe()`, not `save()`: a `save` that wrote
        # `bytes(body).rstrip()` left this test green while putting a body on
        # disk that no longer matched its own record. Measured — the mutation
        # was green, which is how it was found.
        on_disk, back = P.load(os.path.join(self.dir, "raw.txt"))
        self.assertEqual(on_disk, body,
                         "the bytes on disk are not the bytes handed in")
        self.assertEqual(hashlib.md5(on_disk).hexdigest(), back["md5"],
                         "the file and its own record disagree")

    def test_a_str_body_is_refused_rather_than_encoded(self):
        """`bytes` would silently become a character count, which is the
        confusion the field exists to settle."""
        P = self._mod()
        with self.assertRaises(TypeError):
            P.describe("User-agent: *", url="u", status=200, agent="UA")

    def test_verify_notices_a_body_changed_under_its_record(self):
        P = self._mod()
        path = os.path.join(self.dir, "v.txt")
        P.save(path, b"before", url="https://h.example/r.txt", status=200,
               agent="UA")
        self.assertTrue(P.verify(path)["matches"])
        with open(path, "wb") as f:
            f.write(b"after")
        v = P.verify(path)
        self.assertFalse(v["matches"])
        self.assertNotEqual(v["recorded"]["md5"], v["found"]["md5"])



class ACrawlDelayIsADirectiveNotARemark(unittest.TestCase):
    """`ejob.az` names `ClaudeBot` to give it `Crawl-delay: 5` and forbids it
    nothing — **named, allowed, conditioned**. The parser dropped every line
    that was not `Allow` or `Disallow`, so the delay was unreadable to every
    caller and the one host that had asked for one got whatever rate the
    caller happened to use.

    The union rule matches the rest of the module: **the maximum across the
    records that name us**, and `*` only when no record names us. Where
    records disagree, the reading that asks less of the host wins.
    """

    def test_a_record_naming_us_outranks_the_star(self):
        self.assertEqual(_robots.delay_for(
            "User-agent: *\nCrawl-delay: 1\nDisallow:\n\n"
            "User-agent: ClaudeBot\nCrawl-delay: 5\n"), 5.0)

    def test_the_star_applies_when_no_record_names_us(self):
        self.assertEqual(
            _robots.delay_for("User-agent: *\nCrawl-delay: 2\n"), 2.0)

    def test_the_maximum_wins_among_records_naming_us(self):
        """Two of our tokens, two delays. **Not the first, not the last.**"""
        self.assertEqual(_robots.delay_for(
            "User-agent: ClaudeBot\nCrawl-delay: 2\n\n"
            "User-agent: Claude-User\nCrawl-delay: 9\n"), 9.0)

    def test_absence_and_nonsense_are_both_none(self):
        """**The failing direction.** A guard that only ever returns a number
        would pass every test above while inventing a delay where the host set
        none — and a fabricated delay is indistinguishable from a real one."""
        for body in ("User-agent: *\nDisallow:\n",
                     "User-agent: *\nCrawl-delay: soon\n",
                     "User-agent: *\nCrawl-delay: 0\n",
                     "User-agent: *\nCrawl-delay: -3\n",
                     ""):
            with self.subTest(body=body):
                self.assertIsNone(_robots.delay_for(body))

    def test_every_verdict_carries_the_field(self):
        """Present in **all** returns, including the early ones. A `.get()`
        that finds nothing and a host that set nothing read identically at the
        call site, and only one of them is a fact about the host."""
        import inspect
        src = inspect.getsource(_robots.verdict)
        outs = src.count('out = {')
        self.assertGreaterEqual(outs, 1)
        self.assertIn('"crawl_delay": None', src,
                      "the field is not initialised where the verdict dict is "
                      "built, so an early return omits it entirely")



class TheToolDoesNotPrintThatItIsABrowser(unittest.TestCase):
    """`UA` begins `Mozilla/5.0 (compatible; Claude-User; …)` — correct on the
    wire, and `UA.split("/")[0]` reports **"Mozilla"**.

    That line was written, run, and printed *as Mozilla* before anyone noticed.
    The header was right; the summary was the shape of the defect this
    repository already spent a day on. **A summary line is output like any
    other, and a tool's identity is verified rather than observed.**
    """

    def _tool(self):
        import importlib.util
        repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(repo, "bin", "fetch-body.py")
        spec = importlib.util.spec_from_file_location("fetch_body", path)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m

    def test_the_name_shown_is_ours(self):
        m = self._tool()
        shown = m.shown_token()
        self.assertNotIn("Mozilla", shown,
                         "the tool announces a browser in its own output")
        self.assertTrue(shown.lower().startswith("claude"),
                        f"the identity printed is {shown!r}")

    def test_it_survives_a_ua_that_leads_with_mozilla(self):
        """**The failing direction**, on the exact string that produced the
        defect — a helper that happened to work on some other UA would pass
        the test above and reprint "Mozilla" on this one."""
        m = self._tool()
        real = m.UA
        try:
            m.UA = ("Mozilla/5.0 (compatible; Claude-User; "
                    "claude-job-hunt/9.9.9; +https://example.invalid)")
            self.assertEqual(m.shown_token(), "Claude-User")
        finally:
            m.UA = real



class TheModuleNamesTheDirectivesItDoesNotActOn(unittest.TestCase):
    """`_DIRECTIVE` lists seven names as *what a rules file is made of*, and
    `_groups()` keeps four of them. **That gap was silent**: a host declaring
    `Sitemap:` produced the same verdict, with the same fields, as a host
    declaring nothing.

    Measured 2026-09-05 on **187 rules bodies held across three sessions, no
    network**: `sitemap` in 82 (43.9 %), `host` in 3, `clean-param` in 1, and
    `crawl-delay` in 14 of which 3 sit in a group naming this project.

    **The point is the separation, not the obedience.** *A directive we ignore
    for want of parsing it* and *a directive we see and choose not to follow*
    are a defect and a decision, and from outside they read identically.
    Whether to obey any of these is the owner's call and is not decided here.
    """

    def test_a_directive_we_do_not_act_on_is_named(self):
        """**`sitemap` was this test's example and stopped being one the same
        day**: it is parsed and exposed now, so it left the ignored list and
        the assertion moved with it. `host` and `clean-param` are still
        unread — 3 and 1 of the 187 bodies — and the `clean-param` sits in a
        group that names this project."""
        self.assertEqual(
            _robots.ignored_for("User-agent: *\nDisallow:\n"
                                "Host: h.example\nClean-param: sid\n"),
            ["clean-param", "host"])

    def test_nothing_ignorable_reports_nothing(self):
        """**The failing direction.** A function returning a fixed list would
        pass every positive case above while inventing directives on a file
        that carries none."""
        for body in ("User-agent: *\nDisallow: /a\n",
                     "User-agent: ClaudeBot\nAllow: /\nCrawl-delay: 5\n",
                     ""):
            with self.subTest(body=body):
                self.assertEqual(_robots.ignored_for(body), [])

    def test_what_the_module_acts_on_is_not_reported_as_ignored(self):
        for d in _robots._ACTED_ON:
            with self.subTest(directive=d):
                self.assertNotIn(
                    d, _robots.ignored_for(f"User-agent: *\n{d}: x\n"),
                    f"`{d}` is parsed and is being reported as unread")

    def test_content_signal_is_excluded_because_it_is_read_elsewhere(self):
        self.assertEqual(
            _robots.ignored_for("User-agent: *\nContent-Signal: ai-train=no\n"),
            [])

    def test_a_comment_is_not_a_directive(self):
        """`# Sitemap: …` is a comment. Counting it would report a gap the
        host never opened — and an invented defect is chased like a real one."""
        self.assertEqual(
            _robots.ignored_for("User-agent: *\n# Sitemap: https://x/s.xml\n"),
            [])

    def test_every_verdict_carries_the_field(self):
        import inspect
        self.assertIn('"ignored": []', inspect.getsource(_robots.verdict),
                      "the field is missing from the verdict dict, so an early "
                      "return omits it and a caller cannot tell an unparsed "
                      "directive from a host that wrote none")



class ADateMayCarryATimeButMustBeADate(unittest.TestCase):
    """The `content:` and `hosts-source:` guards wanted a bare `YYYY-MM-DD`.

    **On 2026-09-05 two sessions independently wrote a UTC timestamp there
    within hours** — one card in the morning, three at midday. Two people
    reaching for the same rejected form is evidence about the format. A
    timestamp is strictly more information than a date, and the field exists so
    a claim carries when it was true.

    **Widened, not loosened**, and both directions are asserted: the thing the
    guard was written to catch — a field with no date in it — still fails.
    """

    ACCEPTED = ("2026-09-05", "2026-09-05T11:45:51Z", "2026-09-05 10:58 UTC",
                "2026-09-05T11:48Z", "2026-09-05 10:58")
    REFUSED = ("2026-09-05 10:58 UTC, and later", "hier", "", "2026-9-5",
               "05-09-2026", "sometime in September", "2026-09")

    def test_a_date_with_or_without_a_time_is_accepted(self):
        for v in self.ACCEPTED:
            with self.subTest(value=v):
                self.assertRegex(v, f"^{DATE_OR_INSTANT}$")

    def test_what_it_was_written_to_catch_still_fails(self):
        """**The failing direction.** `.*` would pass every case above."""
        import re
        for v in self.REFUSED:
            with self.subTest(value=v):
                self.assertIsNone(re.fullmatch(DATE_OR_INSTANT, v),
                                  f"{v!r} is accepted as a date")



class ADnsFailureIsTheResolversAnswerNotTheHosts(unittest.TestCase):
    """Reported by another session on 2026-09-05, from using the tool.

    `skillingpakistan.gov.pk` came back unresolvable and **the message was read
    as a statement about the host**, which was then recorded as gone — with a
    dissociation that seemed to prove it, two control hosts resolving and the
    target not. The host was alive:

        via 1.1.1.1   skillingpakistan.gov.pk   NOERROR   A = 203.124.43.206
        via 8.8.8.8   skillingpakistan.gov.pk   SERVFAIL
                      jobs.gov.pk               SERVFAIL   <- not specific

    **The verdict was correct and the sentence invited the wrong reading.** The
    module inherits the system resolver, so an unresolvable name is a fact
    about *tool + resolver*. The note is added where the unknown is composed.
    """

    def test_a_resolution_failure_says_to_check_a_second_resolver(self):
        for why in ("nodename nor servname provided, or not known",
                    "Name or service not known",
                    "Temporary failure in name resolution",
                    "[Errno 8] getaddrinfo failed",
                    "SERVFAIL"):
            with self.subTest(why=why):
                self.assertIn("second resolver", _robots._resolver_note(why))

    def test_other_failures_get_no_such_note(self):
        """**The failing direction.** A note appended unconditionally would
        pass every case above and tell a reader to check DNS after a timeout,
        a TLS error or a refusal — advice that is wrong three times out of
        four and looks equally authoritative."""
        for why in ("timed out", "HTTP 403", "certificate verify failed",
                    "connection reset by peer", "", None):
            with self.subTest(why=why):
                self.assertEqual(_robots._resolver_note(why), "")



class TheRateAMeasurementWasTakenAtIsPartOfItsProvenance(unittest.TestCase):
    """Asked for by the session using the tool, and it is the right ask.

    `bin/fetch-body.py` announced *"the host asks for 1.0s between requests"*
    on stderr and then **lost it**. The rate a measurement was taken at is a
    fact about our own conduct, not about the body: a later reader could not
    tell whether a host's `Crawl-delay` had been honoured, and that is exactly
    what a provenance record is for.

    `null` when the host sets none — **a different fact from "we did not
    look"**, which is why the key is always present.
    """

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.dir, True)

    def test_the_key_is_present_even_when_there_is_no_delay(self):
        """**The failing direction.** A record that carried the key only when
        a delay existed would read, on every other host, exactly like a record
        written before the field was invented."""
        rec = _provenance.save(os.path.join(self.dir, "a.txt"), b"x",
                               url="https://h.example/r", status=200,
                               agent="UA", crawl_delay_s=None)
        self.assertIn("crawl_delay_s", rec)
        self.assertIsNone(rec["crawl_delay_s"])

    def test_a_delay_survives_the_round_trip_to_disk(self):
        path = os.path.join(self.dir, "b.txt")
        _provenance.save(path, b"x", url="https://h.example/r", status=200,
                         agent="UA", crawl_delay_s=1.0)
        _body, back = _provenance.load(path)
        self.assertEqual(back["crawl_delay_s"], 1.0,
                         "the delay did not reach the sidecar, so the record "
                         "cannot say at what rate the body was taken")

    def test_the_tool_passes_the_delay_it_announced(self):
        """**Not that `save` accepts the field — that the tool sends it.** The
        two are different, and the version that announced the delay on stderr
        and dropped it would pass every other test in this class."""
        repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        src = open(os.path.join(repo, "bin", "fetch-body.py"),
                   encoding="utf-8").read()
        self.assertIn("crawl_delay_s=delay", src,
                      "the tool computes a delay, waits for it, and does not "
                      "record it — which is the defect this class exists for")



class ADeclaredSitemapIsReadRatherThanGuessed(unittest.TestCase):
    """**82 of 187 rules bodies declare a sitemap and not one was read.**

    Measured 2026-09-05 across three sessions, no network: 43.9 %. Meanwhile
    composing a URL is forbidden, so a session wanting a sitemap could try
    `/sitemap.xml` or do nothing — **while the host was saying where it is.**

    `merojob.com` declares its sitemaps on `sg.merojob.com`, and a path like
    `sitemap-job_post-1.xml.gz` is covered by no verdict taken at the root.
    That is the class the declaration resolves, and it is why the URLs come
    back **as written**.
    """

    def test_a_declaration_is_returned(self):
        self.assertEqual(
            _robots.sitemaps_for("User-agent: *\nDisallow:\n"
                                 "Sitemap: https://h.example/s.xml\n"),
            ["https://h.example/s.xml"])

    def test_it_is_not_filed_under_the_preceding_record(self):
        """**`Sitemap` is not a group member** (RFC 9309 §2.2.1). Filing it
        under whichever `User-agent` happens to precede it would invent an
        addressee the host never named — and the record before it here refuses
        us outright, which would have suppressed the declaration entirely."""
        self.assertEqual(
            _robots.sitemaps_for("User-agent: ClaudeBot\nDisallow: /\n"
                                 "Sitemap: https://h.example/s.xml\n"),
            ["https://h.example/s.xml"])

    def test_another_host_survives_verbatim(self):
        """**The useful case, not the edge case.** Rewriting these to the host
        whose `robots.txt` was read erases exactly the information worth
        having."""
        u = "https://sg.merojob.com/sitemap-job_post-1.xml.gz"
        self.assertEqual(_robots.sitemaps_for(f"Sitemap: {u}\n"), [u])

    def test_a_body_that_declares_none_returns_none(self):
        """**The failing direction.** A function returning a fixed list, or
        one composing `/sitemap.xml` when it finds nothing, would pass every
        case above — and composing a URL is what this exists to stop."""
        for body in ("User-agent: *\nDisallow: /\n",
                     "# Sitemap: https://h.example/s.xml\n",
                     ""):
            with self.subTest(body=body):
                self.assertEqual(_robots.sitemaps_for(body), [])

    def test_duplicates_collapse_and_order_is_the_file_order(self):
        self.assertEqual(
            _robots.sitemaps_for("Sitemap: https://h/b.xml\n"
                                 "Sitemap: https://h/a.xml\n"
                                 "Sitemap: https://h/b.xml\n"),
            ["https://h/b.xml", "https://h/a.xml"])

    def test_reading_a_declaration_is_not_permission(self):
        """The module must not fetch what it just read. **A declaration on a
        host the guard has never seen is the whole point**, so the guard call
        cannot be skipped on the strength of having found the URL."""
        import inspect
        src = inspect.getsource(_robots.sitemaps_for)
        self.assertNotIn("urlopen", src)
        self.assertIn("authorises nothing", src,
                      "the docstring no longer says that reading a "
                      "declaration grants nothing — which is the one thing a "
                      "caller may get wrong here")

    def test_the_directive_is_no_longer_reported_as_unread(self):
        self.assertNotIn(
            "sitemap",
            _robots.ignored_for("User-agent: *\nSitemap: https://h/s.xml\n"))



class TheSitemapReaderHasACaller(unittest.TestCase):
    """**Enumerated before wiring, the same severity applied to
    `_provenance`.** 106 `.py` files examined: **five** compose a sitemap path,
    across three scripts, and only `icims.py` composes on a caller-supplied
    host. Twenty more freeze a constant.

    And the frozen constants are not wrong. Measured 2026-09-05: the
    declaration names a **root** and the adapters hold a **leaf** —
    `jobsbotswana.info` declares `sitemap_index.xml` while the adapter uses
    `noo_job-sitemap.xml`, one of its sixteen children. Routing those through
    the declaration would spend a request each run rediscovering what is
    already known. *My first comparison called all three "mismatched", by
    string equality across two different levels — the instrument was wrong,
    not the code, and `careers.icims.com` differed only in scheme.*

    **So the caller is not an adapter.** It is the session investigating a host
    it has no adapter for, which is the population that loses to guessing:
    `merojob.com` declares its sitemaps on `sg.merojob.com`, and
    `sitemap-job_post-1.xml.gz` is covered by no verdict taken at a root.
    """

    def _tool(self):
        import importlib.util
        repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        spec = importlib.util.spec_from_file_location(
            "fetch_body", os.path.join(repo, "bin", "fetch-body.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m

    def test_the_flag_exists_and_does_not_require_an_output_file(self):
        src = open(os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "bin", "fetch-body.py"), encoding="utf-8").read()
        self.assertIn('"--sitemaps"', src)
        self.assertNotIn('"-o", "--out", required=True', src,
                         "listing a declaration should not require a file to "
                         "write, since it writes nothing")

    def test_it_reads_the_declaration_and_fetches_none_of_it(self):
        """**The one thing a caller may get wrong.** Finding a URL is not
        permission to fetch it, and the declaration may name another host."""
        src = open(os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "bin", "fetch-body.py"), encoding="utf-8").read()
        i = src.index("if a.sitemaps:")
        block = src[i:i + 900]
        self.assertIn("authorises no", block.replace("authorises no fetch",
                                                     "authorises no"))
        self.assertNotIn("urlopen", block,
                         "the --sitemaps path fetches something, and it must "
                         "only read robots.txt through the guard")

    def test_a_host_declaring_nothing_is_not_an_invitation_to_guess(self):
        """**The failing direction**, and the one that matters: silence is the
        common case — 105 of 187 bodies declare nothing — and a tool that
        answered `/sitemap.xml` there would be composing a URL under cover of
        having asked."""
        src = open(os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "bin", "fetch-body.py"), encoding="utf-8").read()
        i = src.index("if a.sitemaps:")
        block = src[i:i + 1200]
        self.assertIn("not permission to guess", block)
        self.assertNotIn('"/sitemap.xml"', block,
                         "the tool composes a fallback path when the host "
                         "declares none — which is the defect it exists for")



class AnAdapterThatFetchesTwiceConsultsTheHostsRate(unittest.TestCase):
    """`Crawl-delay` was dropped by the parser until 2026-09-05, so **no
    adapter had ever applied one**. Measured that day: 65 of 71 whose fetch
    wrapper could be identified make several requests to the same host — 92 %,
    the normal shape of a board adapter and not an exception — and 33 have no
    spacing of any kind.

    The concrete case is a host on our own cards:

        careers.icims.com   crawl-delay: 5   84 bytes, md5 2a0e78d4b005
        icims.py            3 requests per run, no spacing at all

    **The list below can only shrink.** The test fails in both directions: an
    adapter that starts fetching twice without pacing is caught because it is
    not on the list, and one that gets wired is caught because it still is.
    *A frozen allowlist checked in one direction becomes a place to hide.*
    """

    UNPACED = (
        "adecco.py", "adzuna.py", "anefa.py",
        "apec.py", "arbeitsagentur.py",
        "batiactu.py", "bnecl.py", "bumeran.py",
        "computrabajo.py", "crit.py", "digitalrecruiters.py",
        "emploitic.py", "employtt.py", "encuentra24.py",
        "ergodotisi.py", "fachkraft.py", "fhf.py",
        "flatchr.py", "francetravail.py", "freework.py", "hellojob.py", "hellowork.py",
        "hrge.py", "infoempleo.py", "jobam.py",
        "jobbkk.py", "jobivoire.py", "jobology.py",
        "jobroom.py", "jobsbotswana.py", "jobsearchzm.py", "jobsgovpk.py", "jobsireland.py",
        "jobstore.py", "jobup.py", "kalibrr.py",
        "keejob.py", "lmisjm.py", "meteojob.py",
        "michaelpage.py", "mihnati.py", "mycareersfuture.py",
        "onape.py", "oraclecloud.py", "persigo.py",
        "platsbanken.py", "randstad.py", "randstadfr.py",
        "solique.py", "sozialinfo.py", "ssge.py",
        "successfactors.py", "swissdevjobs.py", "taleez.py",
        "talentsoft.py", "tenant_offer.py", "turijobs.py",
        "umantis.py", "vieclam24h.py", "workday.py",
        "wttj.py",
    )

    def _multi_and_paced(self):
        import re
        out = {}
        for f in sorted(pathlib.Path(SCRIPTS).glob("*.py")):
            if f.name.startswith("_"):
                continue
            src = f.read_text(encoding="utf-8")
            if not re.search(r"urlopen|urllib\.request", src):
                continue
            ws, lines = [], src.splitlines()
            for i, l in enumerate(lines):
                m = re.match(r"def (\w+)\s*\(", l)
                if not m:
                    continue
                body = []
                for nxt in lines[i + 1:]:
                    if nxt.strip() and not nxt.startswith((" ", "\t")):
                        break
                    body.append(nxt)
                if "urlopen" in "\n".join(body):
                    ws.append(m.group(1))
            if not ws:
                continue
            pat = re.compile(r"(?<![.\w])(" + "|".join(map(re.escape, ws)) + r")\s*\(")
            body = re.sub(r"(?m)^def \w+\s*\(.*$", "", src)
            n = len(pat.findall(body))
            inloop = False
            ls = body.splitlines()
            for i, l in enumerate(ls):
                if not re.match(r"\s*(for|while)\b", l):
                    continue
                ind = len(l) - len(l.lstrip())
                for nxt in ls[i + 1:]:
                    if nxt.strip() and (len(nxt) - len(nxt.lstrip())) <= ind:
                        break
                    if pat.search(nxt) and not re.search(r"attempt|retry", nxt):
                        inloop = True
            if inloop or n >= 2:
                # **The presence of the name, which is all a scan can see.**
                # That a wrapper actually calls it is asserted per adapter by
                # exercising it — `test_the_measured_case_actually_waits`.
                # This half answers only *which adapters have been touched*.
                out[f.name] = "_pace" in src
        return out

    def test_the_walk_still_sees_the_adapters(self):
        """**A guard green on a denominator it shrank itself proves nothing.**
        This detector has been wrong twice in one afternoon: it counted
        `posting.get(...)` as a network call, and it missed adapters whose
        wrapper is named something other than `get`."""
        seen = self._multi_and_paced()
        self.assertGreaterEqual(
            len(seen), 60,
            "the walk found only %d multi-request adapters; 65 were measured "
            "on 2026-09-05, so the detector has narrowed" % len(seen))

    def test_no_unlisted_adapter_fetches_twice_without_pacing(self):
        seen = self._multi_and_paced()
        new = sorted(n for n, paced in seen.items()
                     if not paced and n not in self.UNPACED)
        self.assertEqual(new, [], "these make several requests to one host and "
                                  "never consult its rate, and are not on the "
                                  "known list: " + ", ".join(new))

    def test_the_list_holds_no_adapter_that_is_already_paced(self):
        """**The shrinking direction.** Wiring an adapter and leaving it listed
        would turn the list from a debt into a permanent excuse."""
        seen = self._multi_and_paced()
        stale = sorted(n for n in self.UNPACED if seen.get(n) is True)
        self.assertEqual(stale, [], "paced and still listed as not: "
                                    + ", ".join(stale))

    def test_the_measured_case_actually_waits(self):
        """**Exercised, not read.** The first version asserted that the string
        `_pace` appeared in the source — so replacing the call with `pass` left
        the import, the helper and the guard all green. Found by mutation
        during a redundancy sweep: **that mutation turned no class red at
        all.** *A guard that reads a name reads the name.*

        `careers.icims.com` asks `crawl-delay: 5` and this adapter gave none
        until 2026-09-05.
        """
        import icims
        waits = []
        real_open = icims.urllib.request.urlopen
        real_pace = icims.Pace

        class Spy:
            def __init__(self, host, own=0.0):
                self.host, self.delay, self.declared = host, 5.0, 5.0

            def source(self):
                return "spied"

            def wait(self):
                waits.append(self.host)
                return 0.0

        def refuse(*a, **k):
            raise icims.urllib.error.URLError("no request in this case")

        icims.urllib.request.urlopen = refuse
        icims.Pace = Spy
        icims._PACERS.clear()
        try:
            for _ in range(2):
                try:
                    icims.get("https://careers.icims.com/sitemap.xml")
                except BaseException:                        # noqa: BLE001
                    pass
        finally:
            icims.urllib.request.urlopen = real_open
            icims.Pace = real_pace
            icims._PACERS.clear()
        self.assertEqual(
            waits, ["careers.icims.com"] * 2,
            "the pacer was not consulted on every request — imported and never "
            "called reads exactly like wired")



class AVerdictNamesTheHostItWasComputedOn(unittest.TestCase):
    """`iqjscout.com` came back `allowed=True` — on rules read from
    `yadanoo.com`, after a 301 — and then answered 403.

    **A verdict named for one host and computed on another said so nowhere.**
    The note existed: it was written into `reason` right after the dict was
    built, and **four of the five branches overwrite `reason` a few lines
    later**. It survived only in the one case that happens not to set it, which
    is the most permissive case of all. *A false yes leaves no more trace than
    a false no.*

    And it never reached the caller at all on a permission, because `allowed()`
    composes its own `reason` — **which is the one adapters print.** Every
    `gate()` here dies with `a["reason"]` and nothing else.
    """

    BODIES = {
        "* permits everything": b"User-agent: *\nAllow: /\n",
        "names and permits us": b"User-agent: ClaudeBot\nAllow: /\n",
        "refuses another path": b"User-agent: *\nDisallow: /admin\n",
        "closes us out": b"User-agent: ClaudeBot\nDisallow: /\n",
        "closes everyone": b"User-agent: *\nDisallow: /\n",
        "unrecognised body": b"hello, no rules here\n",
    }

    def _ask(self, body, final):
        _robots._CACHE.clear()
        _robots._ALIAS.clear()
        real = _robots.urllib.request.urlopen

        class R(io.BytesIO):
            headers = {"Content-Type": "text/plain"}

            def geturl(self):
                return f"https://{final}/robots.txt"

            def getcode(self):
                return 200

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        _robots.urllib.request.urlopen = lambda *a, **k: R(body)
        try:
            return (_robots.verdict("asked.example"),
                    _robots.allowed("asked.example", "/jobs"))
        finally:
            _robots.urllib.request.urlopen = real
            _robots._CACHE.clear()
            _robots._ALIAS.clear()

    def test_every_branch_says_where_the_rules_came_from(self):
        for label, body in self.BODIES.items():
            with self.subTest(case=label):
                v, a = self._ask(body, "elsewhere.example")
                self.assertIn("elsewhere.example", v["reason"] or "",
                              f"{label}: the verdict does not name the host it "
                              f"was computed on")
                self.assertIn("elsewhere.example", a["reason"] or "",
                              f"{label}: `allowed()` does not name it, and "
                              f"`allowed()['reason']` is what adapters print")

    def test_a_permission_says_it_too(self):
        """**The dangerous direction.** A refusal carried the note before
        today; a permission did not, and a `True` computed on another host is
        the one that gets acted on."""
        v, a = self._ask(b"User-agent: *\nAllow: /\n", "elsewhere.example")
        self.assertIs(a["allowed"], True)
        self.assertIn("elsewhere.example", a["reason"])

    def test_no_redirect_means_no_note(self):
        """**The failing direction.** A note added unconditionally would pass
        every case above and tell a reader, on every ordinary host, that its
        rules came from somewhere else."""
        for label, body in self.BODIES.items():
            with self.subTest(case=label):
                v, a = self._ask(body, "asked.example")
                self.assertNotIn("were read from", v["reason"] or "")
                self.assertNotIn("were read from", a["reason"] or "")



class TheRecordSaysWhereTheBodyCameFrom(unittest.TestCase):
    """A provenance record that keeps only the *requested* URL cannot answer
    **which host is this body's** — the question it exists for.

    `iqjscout.com` redirects to `yadanoo.com`. Its rules were read from the
    second while the verdict was named for the first, and 146 bodies had
    already been saved with no way to tell which of them had moved.
    """

    def test_the_tool_records_the_landing_url(self):
        src = open(os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "bin", "fetch-body.py"), encoding="utf-8").read()
        self.assertIn("r.geturl()", src)
        self.assertIn("final_url=", src)

    def test_it_is_null_when_nothing_moved(self):
        """**The failing direction**, and the one that matters: a record that
        always carried a landing URL would make every ordinary host look
        redirected, and a note on all of them is a note on none."""
        src = open(os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "bin", "fetch-body.py"), encoding="utf-8").read()
        i = src.index("final_url=")
        self.assertIn("!= a.url", src[i:i + 120],
                      "the landing URL is recorded unconditionally, so it "
                      "cannot distinguish a host that moved from one that "
                      "did not")



class ACitedMarkdownFileExists(unittest.TestCase):
    """**472 citations from card to card live in prose, and nothing checked
    one of them.** Everything this repository declares *formally* — hosts,
    scripts, countries, content — is guarded; the cross-references that carry
    most of its reasoning were not.

    Four were dead when this was written, and they are two different species:

        `francetravail.md`  -> the file is `france-travail.md`
        `free-work.md` x2   -> the file is `freework.md`
        `shared/modules/ats-open-check.md` -> it is `shared/ats-open-check.md`

    **And two reported as dead were not.** `job-ad.md`, cited by `jobs-ch.md`
    and `jobup.md`, is the per-application dossier file this plugin writes into
    the user's workspace — `shared/workspace.md:59`. *Refusing to guess what it
    meant was right; reading the sentence settled it in one line.* Guessing
    would have replaced a correct citation with a wrong one and the guard would
    have gone green on it.
    """

    # **Scope, written down rather than implied by a walk.**
    #
    # Only the bodies of `shared/boards/*.md` and `shared/*.md` are checked.
    # That is a decision, not an accident of which directory the loop happens
    # to open, and widening it changes the semantics — so the three species a
    # cited `.md` can belong to are named here:
    #
    #   1. **a repository file** — must resolve, and four did not;
    #   2. **a run-time file** — written into the user's workspace and never
    #      present here: `job-ad.md`, `job-pipeline.md`, `commute.md`;
    #   3. **a conditional reference** — where **the absence of the file is
    #      the documented state**. `setup.md` says *"check first whether the
    #      adapter exists — `shared/boards/ams.md`"* and then tables both
    #      outcomes. **Making that resolve would mean creating the card to
    #      satisfy the guard**, which inverts what a guard is for.
    #
    # Species 2 is **derived from `shared/workspace.md`'s own table**, not
    # copied. It was copied first, from one row of that table, and came out
    # six names where the table holds more — a list read at one line instead
    # of read. Deriving it cannot drift and cannot be padded by hand.
    #
    # Species 3 is keyed by **(citing file, cited name)**, so an exemption
    # cannot spread to other files, and the pairs are capped and each asserted
    # still to be needed: *a list of exceptions that grows becomes the guard.*
    CONDITIONAL = frozenset({
        ("setup.md", "shared/boards/ams.md"),
    })

    def _workspace_names(self):
        """Every file `shared/workspace.md` says lives in the workspace."""
        src = (self._repo() / "shared" / "workspace.md").read_text(
            encoding="utf-8")
        names = set()
        for row in re.findall(r"^\|\s*`([^`]+)`\s*\|", src, re.M):
            names.update(re.findall(r"[A-Za-z0-9._-]+\.(?:md|yml)", row))
        for row in re.findall(r"^\|[^|]*\|[^|]*\|([^|]*)\|", src, re.M):
            names.update(re.findall(r"`([A-Za-z0-9._-]+\.(?:md|yml))`", row))
        return frozenset(names)

    def _repo(self):
        return pathlib.Path(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    def _cited(self):
        import re
        bare = re.compile(r"`([A-Za-z0-9][A-Za-z0-9._-]*\.md)`")
        pathy = re.compile(r"`((?:[A-Za-z0-9._-]+/)+[A-Za-z0-9._-]+\.md)`")
        out = []
        roots = [self._repo() / "shared" / "boards", self._repo() / "shared"]
        for card in sorted(p for r in roots for p in r.glob("*.md")):
            src = card.read_text(encoding="utf-8")
            for m in bare.finditer(src):
                out.append((card.name, m.group(1), False))
            for m in pathy.finditer(src):
                out.append((card.name, m.group(1), True))
        return out

    def _resolves(self, name, has_path):
        repo = self._repo()
        if has_path:
            return (repo / name).exists()
        if name in self._workspace_names():
            return True
        return any((repo / d / name).exists()
                   for d in ("shared/boards", "shared", "."))

    def test_the_walk_sees_the_citations(self):
        """**A guard green on a denominator it shrank itself proves nothing.**
        This extractor already missed a whole form once: written for bare
        names, it skipped every citation carrying a directory — and the fourth
        dead link was in exactly that form."""
        cited = self._cited()
        self.assertGreater(len(cited), 400,
                           f"only {len(cited)} citations found; 591 were "
                           f"counted on 2026-09-05, so the extractor narrowed")
        self.assertTrue(any(p for _c, _n, p in cited),
                        "no citation with a directory was seen, and that is "
                        "the form the extractor first missed entirely")

    def test_every_cited_markdown_file_resolves(self):
        dead = sorted({(c, n) for c, n, p in self._cited()
                       if not self._resolves(n, p)
                       and (c, n) not in self.CONDITIONAL})
        self.assertEqual(
            dead, [], "these cards cite a file that does not exist: "
                      + "; ".join(f"{c} -> {n}" for c, n in dead))

    def test_a_name_that_does_not_exist_does_not_resolve(self):
        """**The failing direction.** A resolver that answered yes to
        everything would pass the case above on a repository full of dead
        links."""
        for name in ("no-such-card.md", "job-ad-typo.md", "freework.mdx"):
            with self.subTest(name=name):
                self.assertFalse(self._resolves(name, False))
        self.assertFalse(self._resolves("shared/nowhere/x.md", True))

    def test_the_workspace_names_are_derived_and_not_a_blanket(self):
        """**Derived from the table, not copied out of it.** Copying gave six
        names from one row where the table holds more, and the three that were
        missing — `job-pipeline.md`, `commute.md`, `employers.md` — are cited
        by four files each."""
        names = self._workspace_names()
        self.assertGreaterEqual(len(names), 8, sorted(names))
        self.assertLessEqual(len(names), 20,
                             "the derivation is sweeping up more than the "
                             "workspace table's own entries")
        for n in ("job-ad.md", "job-pipeline.md", "commute.md",
                  "employers.md"):
            with self.subTest(name=n):
                self.assertIn(n, names)

    def test_a_conditional_reference_is_exempt_by_pair_and_capped(self):
        """**The absence is the documented state.** `setup.md` tables both
        outcomes of *does this adapter exist*; making the citation resolve
        would mean creating the card so the guard goes green.

        Keyed by pair, so the exemption cannot spread, and each pair must
        still be needed — an exemption kept after the file appears is a hole
        nobody is watching."""
        self.assertLessEqual(len(self.CONDITIONAL), 4,
                             "a list of exceptions that grows becomes the "
                             "guard")
        for citing, cited in self.CONDITIONAL:
            with self.subTest(pair=(citing, cited)):
                self.assertFalse(
                    self._resolves(cited, "/" in cited),
                    f"{cited} exists now, so this exemption is stale and is "
                    f"hiding whatever else points at it")
                self.assertTrue(
                    any(c == citing and n == cited
                        for c, n, _p in self._cited()),
                    f"{citing} no longer cites {cited}")



class TheRecordDescribesTheDocumentNotTheTransfer(unittest.TestCase):
    """`apec.fr` answers gzip without being asked: **14 171 bytes on the wire
    for a 65 551-byte page.** A record taken there describes the transfer.

    Two things follow. A `grep` over such a body returns **no match and no
    error** — a negative manufactured by an encoding, and one was published as
    *"apec serves no total"* before it was caught. And an md5 taken there
    compares transfers: **two identical responses compressed differently give
    different `bytes` and different `md5` for the same document**, a third road
    to the false *"the file changed"* after a stripped trailing newline and a
    render stamp.

    Audited before fixing: **0 of 238 bodies already saved by this tool carry a
    compression signature**, because it sends no `Accept-Encoding` and most
    hosts honour that. Checked, not assumed — the redirect measurement and the
    28-identical list rest on those bodies.
    """

    def _tool(self):
        import importlib.util
        repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        spec = importlib.util.spec_from_file_location(
            "fetch_body", os.path.join(repo, "bin", "fetch-body.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m

    def test_a_gzip_body_is_decoded_and_the_encoding_is_named(self):
        import gzip
        m = self._tool()
        raw = b"User-agent: *\nAllow: /\n" * 40
        body, enc = m.decoded(gzip.compress(raw), "gzip")
        self.assertEqual(body, raw)
        self.assertEqual(enc, "gzip")

    def test_an_unencoded_body_names_no_encoding(self):
        """**The failing direction.** A field filled on every body would say
        `identity` everywhere and stop distinguishing the two cases, which is
        the whole point of recording it."""
        m = self._tool()
        for header in ("", None, "identity"):
            with self.subTest(header=header):
                body, enc = m.decoded(b"plain\n", header)
                self.assertEqual(body, b"plain\n")
                self.assertIsNone(enc)

    def test_an_undecodable_body_is_not_claimed_as_decoded(self):
        """**Undecodable is not unencoded.** Returning the bytes with `None`
        would record compressed bytes as a document, which is the defect."""
        m = self._tool()
        body, enc = m.decoded(b"not gzip at all", "gzip")
        self.assertEqual(body, b"not gzip at all")
        self.assertIsNotNone(enc)
        self.assertIn("not decoded", enc)

    def test_the_tool_records_both_sizes(self):
        src = open(os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "bin", "fetch-body.py"), encoding="utf-8").read()
        self.assertIn("content_encoding=", src)
        self.assertIn("encoded_bytes=", src,
                      "the wire size is dropped, so a transfer size and a "
                      "document size become one number again")
        i = src.index("encoded_bytes=")
        self.assertIn("if undone else None", src[i:i + 80],
                      "the wire size is recorded even when nothing was "
                      "decoded, which makes it indistinguishable from the "
                      "document size")



class AnOverlapIsDeclaredOnBothSidesAndTheCopiesAgree(unittest.TestCase):
    """#164. Two cards describing the same shared ads is a redundancy this
    repository already keeps by hand — `README.md:75` carries `jobstore`'s
    18.6 % and 15.5 %, word for word, and so does `jobstore.md`. **What was
    missing was never the second copy; it was the check that they agree.**

    Of the three defects a single graph file would also have removed, two are
    visible on their own: a one-way edge shows as a card that mentions a board
    which does not mention it, and an orphan shows as a pointer to nothing.
    **Only drift produces a repository that is wrong and looks clean** — and a
    single file removes the drift by removing the second copy, which removes
    the check with it.

    **WHAT THIS CANNOT SEE, AND IT IS NOT SMALL.** It checks that two
    declarations *agree*; it can say nothing about whether they are *true*.
    `job-room.md` and `solique.md` agreed for a whole morning on *24 of 2 800*
    — and the 2 800 was a count of what one paginated sweep had fetched, not
    the board. **Agreement is not truth**, and a bilateral declaration
    propagates an error introduced at writing exactly as faithfully as it
    prevents one introduced later. *The redundancy defends against drift and
    against nothing else.*

    **Two keys, not one.** `shares-platform:` records a property — the same
    posting UUID on both brands — and carries no date because it does not age.
    `overlap:` records a measurement and carries one. *In a single key the
    property would age at the rate of the measurement*, and a reader could not
    tell which half had gone stale.
    """

    KEYS = ("overlap", "shares-platform")

    def _decls(self):
        import re
        pat = re.compile(r"<!--\s*(overlap|shares-platform):\s*(.*?)\s*-->")
        out = []
        d = pathlib.Path(SCRIPTS).parent.parent.parent / "shared" / "boards"
        for card in sorted(d.glob("*.md")):
            for m in pat.finditer(card.read_text(encoding="utf-8")):
                parts = [x.strip() for x in m.group(2).split("·")]
                out.append((card.name, m.group(1), parts))
        return out, d

    def test_the_walk_sees_the_declarations(self):
        decls, _d = self._decls()
        self.assertGreaterEqual(
            len(decls), 12,
            f"only {len(decls)} declarations found; six pairs declared on both "
            f"sides is twelve, so the extractor has narrowed")

    def test_each_names_a_card_that_exists(self):
        """**An orphan pointer.** A card removed leaves its declarations
        behind on the other side, pointing at nothing."""
        decls, d = self._decls()
        bad = [(c, p[0]) for c, _k, p in decls if not (d / p[0]).exists()]
        self.assertEqual(bad, [], "declarations naming a card that does not "
                                  "exist: " + str(bad))

    def test_each_is_declared_on_the_other_side_too(self):
        """**A one-way edge.** One card claims a relation the other does not
        know about, and a reader landing on the second sees a clean card."""
        decls, _d = self._decls()
        have = {(c, k, p[0]) for c, k, p in decls}
        missing = sorted((c, k, o) for c, k, o in have
                         if (o, k, c) not in have)
        self.assertEqual(missing, [], "declared on one side only: "
                                      + str(missing))

    def test_the_two_copies_say_the_same_thing(self):
        """**This is the one that cannot be seen by reading either card.** A
        figure edited on one side and not the other leaves two cards that are
        each well formed, and the repository is wrong while looking clean.

        The figure and the date are compared, not the prose: an asymmetric
        relation is worded differently on each side and still states one
        number."""
        decls, _d = self._decls()
        byedge = {}
        for c, k, p in decls:
            byedge.setdefault((k, frozenset((c, p[0]))), []).append((c, p[1:]))
        drift = []
        for (k, edge), sides in byedge.items():
            if len({tuple(v) for _c, v in sides}) > 1:
                drift.append((k, sorted(edge), [v for _c, v in sides]))
        self.assertEqual(drift, [], "the two copies disagree: " + str(drift))

    @staticmethod
    def share_a_market(a, b):
        """Do these two `countries:` sets overlap? `*` overlaps everything.

        **Extracted so it can be exercised on inputs the repository does not
        contain.** Neutering it to `if False:` inside the loop left the guard
        green — not because the walk stopped, but because **a predicate that
        never fires cannot be distinguished from one that finds nothing when
        there is nothing to find.** The `checked` counter catches a walk that
        stopped; only cases that must come back false catch this.
        """
        return bool(a & b) or "*" in a or "*" in b

    def test_the_two_cards_share_a_market(self):
        """**A declaration checked against the rest of its own header.**

        `jobstore.md` carried `countries: MY SG` four lines above three
        `overlap:` declarations all saying **Swiss** — two formal declarations
        of one header contradicting each other, and nothing compared them.
        The guard written for #164 compared a declaration to its twin in the
        other card; the redundancy that catches this one was already there and
        nobody was listening.

        **Countries are compared, never the prose.** Reading *"Swiss"* and
        mapping it to `CH` would be inventing a grammar — the failure named on
        the body-scan attempt. Two cards that share no market cannot share
        advertisements, and `*` shares with everything.
        """
        decls, d = self._decls()
        import re

        def markets(card):
            m = re.search(r"<!--\s*countries:\s*(.*?)\s*-->",
                          (d / card).read_text(encoding="utf-8"))
            return set(m.group(1).split()) if m else set()

        checked, bad = 0, []
        for card, _k, parts in decls:
            other = parts[0]
            if not (d / other).exists():
                continue
            a, b = markets(card), markets(other)
            if not a or not b:
                continue
            checked += 1
            if not self.share_a_market(a, b):
                bad.append((card, sorted(a), other, sorted(b)))
        self.assertGreaterEqual(
            checked, 10,
            f"only {checked} declarations were compared against their own "
            f"`countries:`; twelve were on 2026-09-05, so the check is "
            f"passing by looking at nothing")
        self.assertEqual(
            bad, [], "these cards declare a shared overlap and no shared "
                     "market: " + str(bad))


    def test_the_market_predicate_answers_no_when_it_should(self):
        """**The cases the repository does not contain.** Without these, a
        predicate hard-wired to *yes* passes every test above."""
        yes = [({"CH"}, {"CH"}), ({"*"}, {"MY"}), ({"MY"}, {"*"}),
               ({"MY", "SG"}, {"SG"}), ({"*"}, {"*"})]
        no = [({"MY", "SG"}, {"CH"}), ({"CH"}, {"FR"}), (set(), {"CH"}),
              ({"CH"}, set()), (set(), set())]
        for a, b in yes:
            with self.subTest(a=sorted(a), b=sorted(b), want=True):
                self.assertTrue(self.share_a_market(a, b))
        for a, b in no:
            with self.subTest(a=sorted(a), b=sorted(b), want=False):
                self.assertFalse(self.share_a_market(a, b))

    def test_a_measured_overlap_carries_a_date_and_a_property_does_not(self):
        """**Why there are two keys.** A property that acquired a date would
        expire on a schedule nothing measured; a measurement without one would
        never expire at all."""
        decls, _d = self._decls()
        for c, k, p in decls:
            with self.subTest(card=c, key=k):
                if k == "overlap":
                    self.assertEqual(len(p), 3, f"{c}: wants <card> · <figure "
                                                f"with unit> · <YYYY-MM-DD>")
                    self.assertRegex(p[2], r"^\d{4}-\d{2}-\d{2}$")
                    self.assertRegex(p[1], r"\d", f"{c}: no figure")
                else:
                    self.assertEqual(len(p), 2, f"{c}: a property carries no "
                                                f"date — it does not age")



class TheFetcherUsesTheSameTlsChainAsTheGuard(unittest.TestCase):
    """`empleate.gob.es` omits the intermediate certificate its own chain
    needs; `_tls` supplies it. The guard imported that module and the canonical
    fetcher did not, so **`bin/fetch-body.py` failed
    `CERTIFICATE_VERIFY_FAILED` in the same minute the guard declared the host
    readable at 8 456 bytes.**

    That is not a cosmetic asymmetry. `CLAUDE.md` names this tool as the only
    way to fetch, so a host the guard can read and the fetcher cannot makes
    that rule inapplicable on exactly the hosts that need it most — and it is
    invisible while nobody fetches such a host with the canonical tool.

    Measured before wiring: **one host, two names**, not a family.
    `_tls.HOSTS` holds `empleate.gob.es` and its `www.`, and a 146-host run of
    this fetcher returned exactly one TLS failure.

    **This exercises the call rather than reading where it is written.** A
    context passed in the source and not reaching `urlopen` looks identical to
    one that does.
    """

    def _tool(self):
        import importlib.util
        repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        spec = importlib.util.spec_from_file_location(
            "fetch_body", os.path.join(repo, "bin", "fetch-body.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m

    def _capture(self, host):
        """Run the tool against `host` and return the kwargs `urlopen` saw."""
        m = self._tool()
        seen = {}
        real_open = m.urllib.request.urlopen
        real_allowed = m.allowed
        real_verdict = m.verdict

        def spy(req, *a, **k):
            seen.update(k)
            raise m.urllib.error.URLError("stopped after the handshake would be")

        m.urllib.request.urlopen = spy
        m.allowed = lambda h, p, **k: {"allowed": True, "reason": "stubbed"}
        m.verdict = lambda h, **k: {"crawl_delay": None}
        argv = sys.argv
        sys.argv = ["fetch-body.py", f"https://{host}/robots.txt",
                    "-o", os.path.join(tempfile.mkdtemp(), "x.txt")]
        try:
            m.main()
        except BaseException:                    # noqa: BLE001
            pass
        finally:
            sys.argv = argv
            m.urllib.request.urlopen = real_open
            m.allowed = real_allowed
            m.verdict = real_verdict
        return seen

    def test_the_special_host_gets_the_guards_context(self):
        import _tls
        for host in sorted(_tls.HOSTS):
            with self.subTest(host=host):
                seen = self._capture(host)
                self.assertIn("context", seen,
                              "urlopen was called with no context at all")
                self.assertIsNotNone(
                    seen["context"],
                    f"{host} needs the intermediate `_tls` supplies, and the "
                    f"fetcher passed None — the guard can read this host and "
                    f"this tool cannot")

    def test_an_ordinary_host_gets_the_default(self):
        """**The failing direction.** A tool that built a special context for
        everything would pass the case above while quietly using a chain of its
        own on 145 hosts that need nothing."""
        seen = self._capture("example.invalid")
        self.assertIn("context", seen)
        self.assertIsNone(seen["context"],
                          "an ordinary host was given a special TLS context; "
                          "`None` means *use the default* and that is what "
                          "every host but one must get")

    def test_verification_is_never_switched_off(self):
        """`_tls` exists because the alternative is refused. **Its whole point
        is that the chain is completed, not skipped.**"""
        import _tls
        src = open(os.path.join(SCRIPTS, "_tls.py"), encoding="utf-8").read()
        for host in _tls.HOSTS:
            ctx = _tls.context_for(host)
            with self.subTest(host=host):
                self.assertIsNotNone(ctx)
                self.assertTrue(ctx.check_hostname)
                self.assertNotEqual(ctx.verify_mode, ssl.CERT_NONE)
        self.assertNotIn("CERT_NONE", src)



class TheHeadingAgreesWithTheContentLine(unittest.TestCase):
    """A disagreement between two files is found by comparing them. **A
    disagreement of one file with itself is found by nothing.**

    `keejob.md` carried 808 in its `content:` line and its heading, and **827
    in its body**, three sections down — a card corrected in two places out of
    three, by me, the same morning.

    **WHAT THIS DOES NOT SEE, AND WHY THAT IS THE CHOICE**

    It does not scan the body. A general scan was tried and returned 28
    candidates, keeping `keejob` for a figure unrelated to the defect: *a true
    positive by a false mechanism.* The reason it cannot work is that units are
    the key — `808 advertisements` against `827 pages` is two different keys,
    so no conflict is visible, and inventing a unit equivalence is inventing a
    grammar.

    So two **named places** are compared instead, both fixed, neither guessed.
    `keejob:120` would still be invisible here, and that is accepted: **a guard
    that catches a named class beats a sweep that returns 28 candidates and one
    right answer for the wrong reason.**

    **POPULATION, MEASURED BEFORE WRITING THIS**

        12 cards carry `content:`
         3 carry a figure in their first `##`
         0 disagree today

    So this ships covering three cards and catching nothing — **including not
    the defect that prompted it.** That is worth saying plainly: its value is
    prospective, and a card that corrects one of the two places and not the
    other fails immediately.
    """

    def _pairs(self):
        import re
        d = pathlib.Path(SCRIPTS).parent.parent.parent / "shared" / "boards"
        out = []
        for card in sorted(d.glob("*.md")):
            if card.name == "README.md":
                continue
            src = card.read_text(encoding="utf-8")
            m = re.search(r"<!--\s*content:\s*(.*?)\s*-->", src, re.S)
            if not m:
                continue
            heads = re.findall(r"(?m)^##\s+(.*)$", src)
            out.append((card.name, m.group(1), heads[0] if heads else ""))
        return out

    @staticmethod
    def _figures(text):
        import re
        return {int(x.replace(" ", "").replace("\u202f", "").replace(",", ""))
                for x in re.findall(r"\d[\d\u202f ,]*\d|\d", text)}

    def test_the_population_is_the_cards_that_carry_content(self):
        """**Scope, written down.** Only cards with a `content:` line, and of
        those only the ones whose first `##` carries a figure. A heading
        without a figure is out of the population, not tolerated inside it."""
        pairs = self._pairs()
        self.assertGreaterEqual(len(pairs), 10,
                                f"only {len(pairs)} cards carry `content:`; "
                                f"12 did on 2026-09-05")
        scoped = [c for c, _v, h in pairs if self._figures(h)]
        self.assertGreaterEqual(
            len(scoped), 3,
            f"the guard now covers {len(scoped)} cards; it covered 3, so "
            f"either headings lost their figures or the walk narrowed")

    def test_a_figure_in_the_heading_appears_in_the_content_line(self):
        bad, compared = [], 0
        for card, value, head in self._pairs():
            hf = self._figures(head)
            if not hf:
                continue
            compared += 1
            body = value.split("·")[1] if "·" in value else value
            if not (hf & self._figures(body)):
                bad.append((card, sorted(hf), sorted(self._figures(body))))
        # **The comparison counts itself.** Written without this line, a
        # `continue` that skipped every card left the guard green — measured,
        # by mutation, two minutes after it was written. *A guard that cannot
        # fail on its own scope is the defect this repository has named four
        # times today, and it was mine again here.*
        self.assertGreaterEqual(
            compared, 3,
            f"the guard compared {compared} cards; three carried a figure in "
            f"their heading on 2026-09-05, so it is passing by looking at "
            f"nothing")
        self.assertEqual(
            bad, [], "the heading states a figure the `content:` line does "
                     "not, so the card corrects one place and not the "
                     "other: " + str(bad))

    def test_a_heading_without_a_figure_is_out_of_scope_not_excused(self):
        """**The failing direction.** A guard that passed every card with a
        figureless heading *because it had no figure* would also pass one whose
        heading figure vanished in an edit — the two look the same from
        inside the loop, and only the population count above tells them
        apart."""
        self.assertEqual(self._figures("The witness, and it converged"), set())
        self.assertEqual(self._figures("808, with no duplicates"), {808})
        self.assertEqual(self._figures("1 185 in a rolling window"), {1185})



class ACardDatesItself(unittest.TestCase):
    """`platsbanken.md` carried no `verified:` line, so **the date of its
    figure lived only in prose** — five occurrences of 2026-09-01, none
    attached to the count. Dating a drift against it meant reading the body and
    guessing which of the two the date belonged to, which is what a declaration
    line exists to prevent. *And the guard that checks declarations cannot see
    this one: an absent key is not a wrong key.*

    **Measured before writing this, and the third figure decides:**

        97 cards
        24 carry no `verified:`
        24 of those 24 publish a figure
         0 have nothing to date

    That zero is not a loose predicate. The same test returns False on
    constructed text with no count, and True on 97 of 97 real cards: **every
    board card here carries a number**, so a rule requiring a date breaks no
    legitimate case, because there are none.

    **The list can only shrink**, and fails in both directions: a card that
    loses its `verified:` is caught because it is unlisted, and one that gains
    it is caught because it is still listed.
    """

    UNDATED = (
        "adecco.md", "anefa.md", "arbeitsagentur.md",
        "batiactu.md", "crit.md", "empleate.md",
        "emploi-territorial.md", "fhf.md", "freework.md",
        "hays-fr.md", "infoempleo.md", "jobology.md",
        "jobsireland.md", "join.md", "labonnealternance.md",
        "linkedin.md", "michaelpage.md", "oposiciones.md",
        "oraclecloud.md", "personio.md", "pinpoint.md",
        "randstad-fr.md", "recruitee.md", "turijobs.md",
    )

    def _cards(self):
        d = pathlib.Path(SCRIPTS).parent.parent.parent / "shared" / "boards"
        return [p for p in sorted(d.glob("*.md")) if p.name != "README.md"]

    def test_the_walk_sees_the_cards(self):
        cards = self._cards()
        self.assertGreaterEqual(
            len(cards), 90,
            "only %d cards walked; 97 on 2026-09-05" % len(cards))

    def test_no_unlisted_card_is_undated(self):
        undated = sorted(p.name for p in self._cards()
                         if "<!-- verified:" not in p.read_text(encoding="utf-8"))
        # **The detection counts itself.** *"No unlisted undated card"* is
        # satisfied by *"no undated card at all"*, so a detector that finds
        # nothing passes — measured, by mutation, on this very class and for
        # the third time today. The scope counter catches a stopped walk; only
        # this catches a predicate that never fires.
        self.assertGreaterEqual(
            len(undated), 20,
            "the detector found %d undated cards; 24 were on the list when it "
            "was frozen, so it is passing by finding nothing" % len(undated))
        new = [n for n in undated if n not in self.UNDATED]
        self.assertEqual(new, [], "these carry no `verified:` and are not on "
                                  "the known list, so the date of their "
                                  "figures lives only in prose: "
                                  + ", ".join(new))

    def test_the_list_holds_no_card_that_is_now_dated(self):
        """**The shrinking direction.** A card dated and left listed turns the
        list from a debt into a permanent excuse."""
        dated = {p.name for p in self._cards()
                 if "<!-- verified:" in p.read_text(encoding="utf-8")}
        stale = sorted(n for n in self.UNDATED if n in dated)
        self.assertEqual(stale, [], "dated and still listed as not: "
                                    + ", ".join(stale))

    def test_the_list_names_only_cards_that_exist(self):
        names = {p.name for p in self._cards()}
        gone = sorted(n for n in self.UNDATED if n not in names)
        self.assertEqual(gone, [], "listed cards that no longer exist: "
                                   + ", ".join(gone))



class TheTwoHalvesOfTheGuardAgreeOnEveryField(unittest.TestCase):
    """`_robots.allowed("www.hays.fr", "/")` returned `crawl_delay = None`
    two minutes after `verdict()` returned `10.0` for the same host, on a clean
    tree both times. **Two components, one field, two answers** — and
    `allowed()` was not disagreeing: it never carried the field at all.

    **The failure is silent in the direction that costs.** *A `.get()` on a
    field never carried returns `None` for ever, which reads exactly like a
    host that asked for nothing.* A caller reading the rate through the guard
    rather than through `bin/fetch-body.py` would not wait on a host asking for
    ten seconds — and `ejob.az` is a host where the delay is the **only**
    condition set.

    This module wrote that sentence about its own parser this morning and left
    the same hole one function away.
    """

    CARRIED = ("crawl_delay", "sitemaps", "ignored", "content_signal", "state",
               "group_conflict")

    def _both(self, body):
        _robots._CACHE.clear()
        _robots._ALIAS.clear()
        real = _robots.urllib.request.urlopen

        class R(io.BytesIO):
            headers = {"Content-Type": "text/plain"}

            def geturl(self):
                return "https://h.example/robots.txt"

            def getcode(self):
                return 200

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        _robots.urllib.request.urlopen = lambda *a, **k: R(body)
        try:
            return (_robots.verdict("h.example"),
                    _robots.allowed("h.example", "/jobs"))
        finally:
            _robots.urllib.request.urlopen = real
            _robots._CACHE.clear()
            _robots._ALIAS.clear()

    def test_a_declared_rate_survives_the_crossing(self):
        v, a = self._both(b"User-agent: *\nAllow: /\nCrawl-delay: 10\n"
                          b"Sitemap: https://h.example/s.xml\n")
        self.assertEqual(v["crawl_delay"], 10.0)
        for k in self.CARRIED:
            with self.subTest(field=k):
                self.assertIn(k, a, f"`allowed()` drops `{k}`, so a caller "
                                    f"reading it gets None for ever")
                self.assertEqual(a[k], v[k], f"the two halves disagree on {k}")

    def test_absent_stays_absent(self):
        """**The failing direction.** Filling the fields with something rather
        than with the verdict's value would pass the case above and invent a
        rate on every host that sets none."""
        v, a = self._both(b"User-agent: *\nAllow: /\n")
        self.assertIsNone(v["crawl_delay"])
        self.assertIsNone(a["crawl_delay"],
                          "a host that asked for nothing came back with a "
                          "rate, which is worse than dropping the field")
        self.assertEqual(a["sitemaps"], [])

    def test_the_carried_set_is_what_a_caller_cannot_recompute(self):
        """Only fields a caller cannot derive from what it already holds. A
        blanket copy would make the two dicts one and hide which function
        answers which question."""
        v, a = self._both(b"User-agent: *\nAllow: /\nCrawl-delay: 5\n")
        self.assertLess(len(a), len(v),
                        "`allowed()` now carries everything `verdict()` does, "
                        "so the two answer the same question and one of them "
                        "is redundant")
        for k in ("allowed", "path", "rule", "kind"):
            with self.subTest(field=k):
                self.assertIn(k, a)
                self.assertNotIn(k, v)



class NoRequestLeavesUnderARefusalAndNoneWearsABrowsersName(unittest.TestCase):
    """Two mutations survived the bench, and these two are not like the other
    twelve.

    **The other twelve make us publish wrong figures — grave, and retractable.
    These two make us behave badly towards a third party**, and the host has no
    way to tell us. *A wrong number can be withdrawn; a request that has been
    sent cannot be recalled.*

        `if not g["allowed"]:` -> `if False:`      GREEN
        headers={"User-Agent": UA} -> Mozilla      GREEN

    **And the second is worse than green.** This repository had that defect
    this morning, fixed it, and wrote a guard so it would not return — a guard
    that checks the tool does not *print* a browser's name. Nothing checked
    what it *sends*. **The fix covered the instance and the guard covered the
    wording of the fix**, which is why a mutation put Chrome back on the wire
    with the suite untouched.

    So both are exercised on the wire: the request object is intercepted and
    inspected, and the refusal path is checked by counting requests rather than
    by reading a branch.
    """

    def _tool(self):
        import importlib.util
        repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        spec = importlib.util.spec_from_file_location(
            "fetch_body", os.path.join(repo, "bin", "fetch-body.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m

    def _run(self, allowed):
        """Run the tool with a stubbed guard; return the requests attempted."""
        m = self._tool()
        seen = []
        real_open = m.urllib.request.urlopen
        real_allowed = m.allowed
        real_verdict = m.verdict

        def spy(req, *a, **k):
            seen.append(req)
            raise m.urllib.error.URLError("counted, not sent")

        m.urllib.request.urlopen = spy
        m.allowed = lambda h, p, **kw: {"allowed": allowed,
                                        "reason": "stubbed for this case"}
        m.verdict = lambda h, **kw: {"crawl_delay": None, "sitemaps": []}
        argv = sys.argv
        sys.argv = ["fetch-body.py", "https://refused.example/jobs",
                    "-o", os.path.join(tempfile.mkdtemp(), "x.txt")]
        try:
            code = m.main()
        except BaseException:                        # noqa: BLE001
            code = None
        finally:
            sys.argv = argv
            m.urllib.request.urlopen = real_open
            m.allowed = real_allowed
            m.verdict = real_verdict
        return seen, code

    def test_a_refusal_sends_nothing(self):
        """**Counted, not read.** A branch that looks right and is never taken
        reads the same as one that is."""
        seen, code = self._run(allowed=False)
        self.assertEqual(
            seen, [], "a request left on a path the guard refused — the host "
                      "said no and cannot tell us we ignored it")
        self.assertEqual(code, 7, "a refusal must exit 7")

    def test_an_indeterminate_sends_nothing_either(self):
        """**Found by extending this class, not by the bench's list.**
        Neutering the `None` branch left the suite green too: rules that could
        not be read would have let a request through.

        `CLAUDE.md` is explicit — *un INDÉTERMINÉ ne se sonde pas* — and an
        unknown is the case where sending is least defensible, because we
        cannot even say the host would have minded.
        """
        seen, code = self._run(allowed=None)
        self.assertEqual(
            seen, [], "a request left while the rules were unreadable: an "
                      "unknown is not a permission")
        self.assertEqual(code, 8, "an unreadable rules file must exit 8")

    def test_a_permission_does_send(self):
        """**The failing direction.** A tool that sent nothing ever would pass
        the case above and fetch nothing at all."""
        seen, _code = self._run(allowed=True)
        self.assertEqual(len(seen), 1,
                         "the guard permitted and no request was attempted")

    def test_what_goes_on_the_wire_is_our_name(self):
        """**The header, not the source.** The existing guard checks that the
        tool does not print a browser's name; this one reads the header the
        request actually carries."""
        seen, _code = self._run(allowed=True)
        ua = seen[0].get_header("User-agent") or ""
        self.assertIn("Claude", ua,
                      f"the request went out as {ua!r} — this project declares "
                      f"itself or it does not fetch")
        self.assertIn("claude-job-hunt", ua,
                      "the agent string names no repository, so an operator "
                      "reading it cannot find out who we are")
        self.assertNotEqual(
            ua.split("/")[0], "Chrome",
            "the wire carries a browser's product token")



class AnExitCodeMeansTheSameThingInEveryAdapter(unittest.TestCase):
    """A mutation setting `EXIT_REFUSED, EXIT_UNKNOWN = 0, 0` in `keejob.py`
    left the suite green. **An adapter refused by a host would have exited 0 —
    reporting success.**

    The instance was one adapter. **Asking what else has that shape found the
    family: 21 adapters define `EXIT_*` constants and the suite named two of
    them.** Nothing asserted a single value.

    *A mutation bench only tests the mutations it knows how to make; its list
    of survivors is a lower bound, never an inventory.* This came from the
    survivor, not from the bench.

    The values are already unanimous across twenty adapters — this only makes
    the unanimity checkable.
    """

    CANON = {"EXIT_BROKEN": 2, "EXIT_GONE": 3, "EXIT_BUDGET": 4,
             "EXIT_STALE": 5, "EXIT_PARTIAL": 6, "EXIT_REFUSED": 7,
             "EXIT_UNKNOWN": 8, "EXIT_BLOCKED": 9}

    def _defined(self):
        import re
        pat = re.compile(r"^(EXIT_\w+(?:,\s*EXIT_\w+)*)\s*=\s*([\d,\s]+)$",
                         re.M)
        out = []
        for f in sorted(pathlib.Path(SCRIPTS).glob("*.py")):
            if f.name.startswith("_"):
                continue
            for m in pat.finditer(f.read_text(encoding="utf-8")):
                keys = [k.strip() for k in m.group(1).split(",")]
                vals = [v.strip() for v in m.group(2).split(",") if v.strip()]
                for k, v in zip(keys, vals):
                    out.append((f.name, k, int(v)))
        return out

    def test_the_walk_sees_the_adapters(self):
        """**A guard green on a denominator it shrank itself proves nothing**,
        and this one has a wide denominator to lose."""
        found = self._defined()
        self.assertGreaterEqual(
            len({f for f, _k, _v in found}), 18,
            f"only {len({f for f, _k, _v in found})} adapters define exit "
            f"codes; 21 did on 2026-09-05")

    def test_every_constant_holds_its_canonical_value(self):
        wrong = [(f, k, v) for f, k, v in self._defined()
                 if k in self.CANON and v != self.CANON[k]]
        self.assertEqual(
            wrong, [], "these mean something different from everywhere else, "
                       "so a caller reading an exit code cannot know what "
                       "happened: " + str(wrong))

    def test_no_failure_code_is_success(self):
        """**The direction that costs.** Zero is *it worked*. A refusal, an
        unknown or a broken read reported as zero is a silent success on a run
        that did nothing — the exact shape of the mutation that survived."""
        zeros = [(f, k, v) for f, k, v in self._defined() if v == 0]
        self.assertEqual(zeros, [], "a failure constant is 0: " + str(zeros))

    def test_an_unknown_name_is_named_rather_than_ignored(self):
        """A constant outside the canon is not a defect — it is a fact worth
        seeing. Silence here would let a private code drift into use."""
        strays = sorted({k for _f, k, _v in self._defined()
                         if k not in self.CANON})
        self.assertEqual(strays, [], "exit constants outside the documented "
                                     "set: " + ", ".join(strays))


class EveryPacedAdapterActuallyWaits(unittest.TestCase):
    """`icims.py` was exercised; `hays`, `ats` and `jobsge` were wired the same
    afternoon and only scanned for the string `_pace`.

    **Three of the four wired adapters had no test that the pacer is called** —
    the same shape as the defect found in `icims`, one question away from it
    and never asked. `www.hays.fr` asks for **10 seconds**.
    """

    CASES = (("icims", "get", ("https://careers.icims.com/sitemap.xml",),
              "careers.icims.com"),
             ("hays", "get", ("https://www.hays.fr/x",), "www.hays.fr"),
             ("ats", "fetch", ("https://api.lever.co/v0/postings/x",),
              "api.lever.co"),
             ("jobsge", "get", ("https://www.jobs.ge/en/?view=jobs",),
              "www.jobs.ge"))

    def _waits(self, mod, fn, args, host):
        m = __import__(mod)
        waits = []

        class Spy:
            def __init__(self, h, own=0.0):
                self.host, self.delay, self.declared = h, 5.0, 5.0

            def source(self):
                return "spied"

            def wait(self):
                waits.append(self.host)
                return 0.0

        def refuse(*a, **k):
            raise m.urllib.error.URLError("counted, not sent")

        real_open, real_pace = m.urllib.request.urlopen, m.Pace
        # **Each adapter names its guard differently**, and stubbing only
        # `gate` sent `hays` to the network — the suite went from 2 s to 15 s
        # and the slowdown was the only sign. A test that reaches the network
        # is a test whose result depends on a host.
        gates = {n: getattr(m, n) for n in
                 ("gate", "_robots_gate", "smartrecruiters_gate", "check_host")
                 if hasattr(m, n)}
        m.urllib.request.urlopen = refuse
        m.Pace = Spy
        m._PACERS.clear()
        for n in gates:
            setattr(m, n, lambda *a, **k: None)
        # **The back-off is real and it really sleeps.** Refusing the request
        # makes each adapter retry, and the class took eight seconds — the
        # slowdown was the only sign that a test had started waiting. Sleep is
        # neutralised; the retry itself is left alone, because it is not what
        # this case is about.
        real_sleep = m.time.sleep if hasattr(m, "time") else None
        if real_sleep is not None:
            m.time.sleep = lambda *_a, **_k: None
        try:
            for _ in range(2):
                try:
                    getattr(m, fn)(*args)
                except BaseException:                # noqa: BLE001
                    pass
        finally:
            m.urllib.request.urlopen = real_open
            m.Pace = real_pace
            m._PACERS.clear()
            for n, fn in gates.items():
                setattr(m, n, fn)
            if real_sleep is not None:
                m.time.sleep = real_sleep
        return waits

    def test_each_wired_adapter_consults_the_rate_on_every_request(self):
        for mod, fn, args, host in self.CASES:
            with self.subTest(adapter=mod):
                waits = self._waits(mod, fn, args, host)
                self.assertEqual(
                    len(waits), 2,
                    f"{mod}.{fn} made two requests and consulted the rate "
                    f"{len(waits)} time(s) — imported and never called reads "
                    f"exactly like wired")
                self.assertEqual(set(waits), {host},
                                 f"{mod} paced the wrong host: {set(waits)}")



class AFieldNobodyCarriedIsNotNone(unittest.TestCase):
    """**A `.get()` on a key never carried is indiscernible from a key carried
    whose value is legitimately `None`.**

    That cost twice in one day, one key apart. `crawl_delay` was missing, so
    the gate reported *this host asked for nothing* about a host asking for
    ten seconds. Then `group_conflict` was found missing one key further along
    — **and that one says whether the verdict itself is reliable**: a caller
    saw a clean boolean and never learned that two records contradict each
    other about us.

    *Filling the list case by case repairs instances and leaves the form.* The
    next field added to `verdict()` and forgotten would fail identically, in
    silence, in the direction that costs — and a hand-kept list is exactly
    what this defect has already walked through once.

    So the absence is loud, and this class asserts the loudness rather than
    the list.
    """

    def _both(self):
        _robots._CACHE.clear()
        _robots._ALIAS.clear()
        real = _robots.urllib.request.urlopen

        class R(io.BytesIO):
            headers = {"Content-Type": "text/plain"}

            def geturl(self):
                return "https://h.example/robots.txt"

            def getcode(self):
                return 200

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        _robots.urllib.request.urlopen = lambda *a, **k: R(
            b"User-agent: *\nAllow: /\nCrawl-delay: 3\n")
        try:
            return (_robots.verdict("h.example"),
                    _robots.allowed("h.example", "/jobs"))
        finally:
            _robots.urllib.request.urlopen = real
            _robots._CACHE.clear()
            _robots._ALIAS.clear()

    def test_a_dropped_field_raises_instead_of_answering_none(self):
        v, a = self._both()
        dropped = sorted(set(v) - set(a))
        self.assertGreaterEqual(
            len(dropped), 3,
            f"only {len(dropped)} fields are dropped; if `allowed()` now "
            f"carries everything this class guards nothing")
        for k in dropped:
            with self.subTest(field=k):
                with self.assertRaises(KeyError):
                    a.get(k)
                with self.assertRaises(KeyError):
                    a[k]

    def test_a_carried_field_answers_normally(self):
        """**The failing direction.** A mapping that raised on everything
        would pass the case above and break every ordinary read."""
        _v, a = self._both()
        self.assertEqual(a.get("crawl_delay"), 3.0)
        self.assertEqual(a.get("sitemaps"), [])
        self.assertIs(a.get("allowed"), True)

    def test_a_carried_field_whose_value_is_none_stays_none(self):
        """The whole point: `None` must remain sayable. A field carried and
        genuinely empty is a fact, and it must not raise."""
        _robots._CACHE.clear()
        _robots._ALIAS.clear()
        real = _robots.urllib.request.urlopen

        class R(io.BytesIO):
            headers = {"Content-Type": "text/plain"}

            def geturl(self):
                return "https://h.example/robots.txt"

            def getcode(self):
                return 200

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        _robots.urllib.request.urlopen = lambda *a, **k: R(
            b"User-agent: *\nAllow: /\n")
        try:
            a = _robots.allowed("h.example", "/jobs")
        finally:
            _robots.urllib.request.urlopen = real
            _robots._CACHE.clear()
            _robots._ALIAS.clear()
        self.assertIsNone(a.get("crawl_delay"),
                          "a host that set no rate must still be able to say "
                          "so — raising here would make silence unsayable")

    def test_an_unknown_name_is_an_ordinary_miss(self):
        """A key nobody builds is not this mapping's business. Inventing an
        error for it would break every caller probing for an optional key."""
        _v, a = self._both()
        self.assertEqual(a.get("no_such_field", "default"), "default")
        self.assertIsNone(a.get("no_such_field"))



class TheRetryAsksAgainOnlyWhereAskingAgainCanHelp(unittest.TestCase):
    """`bin/fetch-body.py` made **three attempts** on the rules file of a host
    answering **400**. Retrying a rules file is defensible; retrying a
    definitive answer is not.

    The retry was never unconditional — it fires only on `unreachable` — but
    **every status outside the six named ones landed there**, so 400, 405 and
    418 were all asked three times. *A 4xx is an answer; a 5xx may be an
    incident.* Multiplied by the number of indeterminate hosts, that is two
    extra requests each to hosts that already replied.

    **The verdict does not change.** A 400 is still `unreachable`, still an
    unknown, and an unknown is still not probed — `CLAUDE.md`. Only how many
    times we ask changes.
    """

    def _attempts(self, code):
        _robots._CACHE.clear()
        _robots._ALIAS.clear()
        real = _robots.urllib.request.urlopen
        back = _robots._BACKOFF
        n = []

        def fail(*a, **k):
            n.append(1)
            raise _robots.urllib.error.HTTPError(
                "https://h.example/robots.txt", code, "x", {}, io.BytesIO(b""))

        _robots.urllib.request.urlopen = fail
        _robots._BACKOFF = (0, 0)
        try:
            v = _robots.verdict("h.example")
        finally:
            _robots.urllib.request.urlopen = real
            _robots._BACKOFF = back
            _robots._CACHE.clear()
            _robots._ALIAS.clear()
        return len(n), v

    def test_a_definitive_answer_is_asked_once(self):
        for code in (400, 405, 418, 451, 404, 403):
            with self.subTest(code=code):
                n, _v = self._attempts(code)
                self.assertEqual(n, 1, f"HTTP {code} was asked {n} times; the "
                                       f"host answered the first time")

    def test_a_possible_incident_is_asked_again(self):
        """**The failing direction.** A retry removed everywhere would pass the
        case above and give up on a host that was merely restarting."""
        for code in (500, 502, 503, 408):
            with self.subTest(code=code):
                n, _v = self._attempts(code)
                self.assertEqual(n, 3, f"HTTP {code} was asked once; a 5xx may "
                                       f"be an incident and asking again is "
                                       f"what the back-off is for")

    def test_a_network_failure_is_still_retried(self):
        """No status at all is the case the retry was written for."""
        _robots._CACHE.clear()
        _robots._ALIAS.clear()
        real = _robots.urllib.request.urlopen
        back = _robots._BACKOFF
        n = []

        def fail(*a, **k):
            n.append(1)
            raise _robots.urllib.error.URLError("no route")

        _robots.urllib.request.urlopen = fail
        _robots._BACKOFF = (0, 0)
        try:
            _robots.verdict("h.example")
        finally:
            _robots.urllib.request.urlopen = real
            _robots._BACKOFF = back
            _robots._CACHE.clear()
            _robots._ALIAS.clear()
        self.assertEqual(len(n), 3)

    def test_the_verdict_is_unchanged_by_asking_less(self):
        """Asking fewer times must not turn an unknown into anything else."""
        _n, v = self._attempts(400)
        self.assertEqual(v["state"], "unreachable")
        self.assertIsNone(v["sweep"] if v["sweep"] is not True else None,
                          "a 400 became a permission")



class PaceArithmeticIsTestedAndNotOnlyItsWiring(unittest.TestCase):
    """Three mutations of `_pace.py` survived the bench, and all three are
    arithmetic rather than wiring — **the module was guarded on being called
    and not on what it computes.**

        self.delay = max(self.own, self.declared or 0.0) -> self.own
        slept = max(0.0, self.delay - elapsed)           -> slept = self.delay
        declared = None                                  -> declared = 1.0

    The first weakens the host's rate to the adapter's; the second waits the
    full interval every time regardless of elapsed time; **the third invents a
    second on every host that set nothing** — the shape this repository refuses
    by name, a chosen number dressed as a host's request.
    """

    def _pace(self, declared, own):
        import _pace
        real = _pace._robots.verdict
        _pace._robots.verdict = lambda h, **k: {"crawl_delay": declared}
        try:
            return _pace.Pace("h.example", own=own)
        finally:
            _pace._robots.verdict = real

    def test_the_longer_of_the_two_wins(self):
        self.assertEqual(self._pace(10.0, 0.5).delay, 10.0)
        self.assertEqual(self._pace(1.0, 2.0).delay, 2.0,
                         "the host asked for less than this adapter already "
                         "waited, and the adapter's own politeness was cut")
        self.assertEqual(self._pace(None, 2.0).delay, 2.0)

    def test_a_host_that_asked_for_nothing_gets_no_invented_rate(self):
        """**The direction that would be dishonest.** A default of one second
        is a choice, and dressing a choice as a host's request is the species
        this repository catches by name."""
        p = self._pace(None, 0.0)
        self.assertIsNone(p.declared)
        self.assertEqual(p.delay, 0.0)
        self.assertIn("asks for none", p.source())

    def test_waiting_counts_the_time_already_spent(self):
        """A pacer that sleeps the full interval regardless of elapsed time
        doubles the wait on any adapter that does work between requests."""
        import time
        p = self._pace(10.0, 0.0)
        p.wait()
        p._last = time.monotonic() - 9.0
        slept = p.wait()
        self.assertLess(slept, 2.0,
                        "nine of the ten seconds had already passed and the "
                        "pacer waited the whole interval again")
        self.assertGreater(slept, 0.0)

    def test_the_first_request_waits_for_nothing(self):
        self.assertEqual(self._pace(10.0, 0.0).wait(), 0.0)

    def test_unreadable_rules_invent_no_rate_either(self):
        """**The branch the other cases never reach.** When the guard raises,
        `Pace` falls back — and a fallback of one second would put a rate on
        every host whose rules could not be read, which is the largest class of
        all. *An unknown is not a request.*"""
        import _pace
        real = _pace._robots.verdict

        def boom(*a, **k):
            raise RuntimeError("rules unreadable")

        _pace._robots.verdict = boom
        try:
            p = _pace.Pace("h.example", own=0.0)
            q = _pace.Pace("h.example", own=2.0)
        finally:
            _pace._robots.verdict = real
        self.assertIsNone(p.declared,
                          "a rate was invented on a host whose rules could "
                          "not be read")
        self.assertEqual(p.delay, 0.0)
        self.assertEqual(q.delay, 2.0,
                         "the adapter's own spacing was replaced rather than "
                         "kept when the rules were unreadable")


class TheProvenanceSidecarIsFoundWhereItIsWritten(unittest.TestCase):
    """Two mutations of `_provenance.py` survived: renaming `SUFFIX`, and
    dropping the extension filter in `audit()`.

    **Renaming the suffix breaks nothing visible** — `save` and `load` agree
    with each other whatever it is called — but every sidecar already on disk
    becomes invisible, and `audit()` reports the bodies beside them as orphans.
    *The two halves stay consistent while the record stops being findable.*
    """

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.dir, True)

    def test_the_suffix_is_the_one_already_on_disk(self):
        self.assertEqual(_provenance.SUFFIX, ".provenance.json",
                         "renaming this orphans every record already written; "
                         "save and load would still agree with each other")
        path = os.path.join(self.dir, "b.txt")
        _provenance.save(path, b"x", url="https://h/r", status=200, agent="UA")
        self.assertTrue(os.path.exists(path + ".provenance.json"))

    def test_the_audit_walks_bodies_and_not_its_own_sidecars(self):
        """**The failing direction.** Dropping the extension filter makes the
        audit walk every file, sidecars included — and a sidecar has no sidecar
        of its own, so each one counts as an orphan and the figure roughly
        doubles."""
        for i in range(3):
            _provenance.save(os.path.join(self.dir, f"b{i}.txt"), b"x",
                             url=f"https://h{i}/r", status=200, agent="UA")
        # A file of a kind the audit is not for. Without the extension
        # filter it is walked, has no sidecar, and is reported as an orphan —
        # **an audit that invents orphans is worse than one that misses them**,
        # because someone will go looking for bodies that were never fetched.
        with open(os.path.join(self.dir, "notes.log"), "w") as fh:
            fh.write("not a fetched body")
        a = _provenance.audit(self.dir)
        self.assertEqual(a["of"], 3,
                         f"the walk counted {a['of']} files where three "
                         f"bodies were written: it is counting its own "
                         f"sidecars, or files it is not for")
        self.assertEqual(a["orphan_count"], 0, a["orphans"])


class TheFetcherRefusesWhatItCannotRecord(unittest.TestCase):
    """Two mutations of `bin/fetch-body.py` survived: saving a non-200 without
    being asked, and dropping the requirement for `-o`.

    **A body saved from a 403 is a body in the corpus that describes a refusal
    page.** This repository has one already — 5 587 bytes of a 403 entered a
    fingerprint table as `robots.txt`, md5 included — and that false success
    then invented a cause for itself.
    """

    def _tool(self):
        import importlib.util
        repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        spec = importlib.util.spec_from_file_location(
            "fetch_body", os.path.join(repo, "bin", "fetch-body.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m

    def _run(self, argv, status):
        m = self._tool()

        class R(io.BytesIO):
            headers = {"Content-Type": "text/plain"}

            def geturl(self):
                return "https://h.example/robots.txt"

            def getcode(self):
                return status

            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        m.urllib.request.urlopen = lambda *a, **k: R(b"body")
        m.allowed = lambda h, p, **kw: {"allowed": True, "reason": "stub"}
        m.verdict = lambda h, **kw: {"crawl_delay": None, "sitemaps": []}
        old, out = sys.argv, sys.stdout
        sys.argv = argv
        sys.stdout = io.StringIO()          # the tool prints the path it wrote
        try:
            return m.main()
        finally:
            sys.argv, sys.stdout = old, out

    def test_a_non_200_is_not_saved_unless_asked_for(self):
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        out = os.path.join(d, "x.txt")
        code = self._run(["f", "https://h.example/robots.txt", "-o", out], 403)
        self.assertNotEqual(code, 0)
        self.assertFalse(os.path.exists(out),
                         "a 403 body was written to the corpus without being "
                         "asked for — a readable body is not an answer")

    def test_it_is_saved_when_asked_for(self):
        """**The failing direction.** A tool that never saved a non-200 would
        pass the case above and make `--allow-refusal` a lie."""
        d = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, d, True)
        out = os.path.join(d, "x.txt")
        self._run(["f", "https://h.example/robots.txt", "-o", out,
                   "--allow-refusal"], 403)
        self.assertTrue(os.path.exists(out))
        _b, rec = _provenance.load(out)
        self.assertEqual(rec["status"], 403,
                         "the record does not say the body is a refusal page")

    def test_writing_a_body_requires_somewhere_to_write_it(self):
        code = self._run(["f", "https://h.example/robots.txt"], 200)
        self.assertNotEqual(code, 0,
                            "the tool fetched with nowhere to put the body, so "
                            "the request was spent for nothing")


class TwoAdapterInvariantsThatOnlyLookLikeStyle(unittest.TestCase):
    """`jobsbotswana` sorting newest-first and `jobam` de-duplicating are both
    one line, both look like taste, and both survived the bench.

    **Neither is taste.** The Botswana file is served oldest-first, so without
    the sort `--limit 4 --live` returned the four oldest — all expired — and
    read as a broken board. And a sitemap that lists a URL twice inflates every
    count taken from it: `onape.td` listed one advertisement three times.
    """

    def test_the_botswana_listing_is_newest_first(self):
        import jobsbotswana
        rows = [("/a", "2025-01-01"), ("/b", "2026-09-01"), ("/c", "2025-06-01")]
        rows.sort(key=lambda r: (r[1] or ""), reverse=True)
        self.assertEqual([r[0] for r in rows], ["/b", "/c", "/a"])
        src = (pathlib.Path(SCRIPTS) / "jobsbotswana.py").read_text(
            encoding="utf-8")
        self.assertIn("reverse=True", src,
                      "the file is served oldest-first; without the sort "
                      "`--limit 4 --live` returns four expired ads and reads "
                      "as a dead board")

    def test_a_repeated_url_is_counted_once(self):
        """`raw` and `distinct` must be able to differ — that difference is
        what `onape.td`'s three listings of one advertisement showed."""
        import jobam
        seen, rows, raw = set(), [], 0
        for u in ("/a", "/b", "/a", "/c"):
            raw += 1
            if u in seen:
                continue
            seen.add(u)
            rows.append(u)
        self.assertEqual((raw, len(rows)), (4, 3))
        src = (pathlib.Path(SCRIPTS) / "jobam.py").read_text(encoding="utf-8")
        self.assertIn("if u in seen:", src,
                      "duplicates are counted, so `raw` and `distinct` can "
                      "never differ and a repeated URL inflates the board")


class TheRateThatBindsUsIsTheOneThatNamesUs(unittest.TestCase):
    """`pool = ours or star` became `ours + star` and nothing failed.

    **The `*` record's delay would then compete with ours**, and since the
    union takes the maximum, a `*` asking for more would silently override a
    rate a host set for this project by name. The precedence is the point:
    *a record that names us replaces the general one, it does not join it.*
    """

    def test_a_record_naming_us_replaces_the_star(self):
        self.assertEqual(_robots.delay_for(
            "User-agent: *\nCrawl-delay: 30\n\n"
            "User-agent: ClaudeBot\nCrawl-delay: 5\n"), 5.0,
            "the `*` rate won over one set for this project by name")

    def test_the_star_applies_only_when_nothing_names_us(self):
        self.assertEqual(
            _robots.delay_for("User-agent: *\nCrawl-delay: 30\n"), 30.0)



class ABenchFileSaysWhenItIsFinished(unittest.TestCase):
    """A count taken from the bench's own output file gave **23 rows for 24
    mutations**. The number was not wrong — it was one second stale, because
    the file was still being written, **and nothing in the file said so.**

    *An unexplained gap invites an explanation, and an explanation found for a
    gap that does not exist is a false thesis no re-reading overturns.* The
    next step was going to be publishing *23 of 24, all red* with one missing.

    And the same run showed a second hole: **restoring the source is not
    restoring the tree.** A mutation that removed the *where do I write this*
    check made the tool save a body to a file named `None`; the source restore
    left it behind, so **the next mutation ran against a tree the previous one
    had changed** and neither result said so.
    """

    def _bench(self):
        import importlib.util
        repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        spec = importlib.util.spec_from_file_location(
            "mutation_bench", os.path.join(repo, "bin", "mutation-bench.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        return m

    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.dir, True)
        self.path = os.path.join(self.dir, "r.jsonl")

    def test_a_file_without_the_marker_is_refused(self):
        import json
        with open(self.path, "w", encoding="utf-8") as fh:
            for i in range(23):
                fh.write(json.dumps({"state": "red", "i": i}) + "\n")
        with self.assertRaises(ValueError) as cm:
            self._bench().read_results(self.path)
        self.assertIn("lower bound", str(cm.exception),
                      "the refusal does not say why a partial count is "
                      "dangerous, which is the whole reason for the marker")

    def test_a_finished_file_reads_and_states_its_count(self):
        """**The failing direction.** A reader that refused everything would
        pass the case above and make the file unusable."""
        import json
        with open(self.path, "w", encoding="utf-8") as fh:
            for i in range(3):
                fh.write(json.dumps({"state": "red", "i": i}) + "\n")
            fh.write(json.dumps({"done": True, "n": 3}) + "\n")
        rows, n = self._bench().read_results(self.path)
        self.assertEqual(len(rows), 3)
        self.assertEqual(n, 3)

    def test_a_short_file_is_caught_by_its_own_count(self):
        """The marker carries `n`, so a file that ended early with a marker —
        a bench that skipped mutations — is still visible as short."""
        import json
        with open(self.path, "w", encoding="utf-8") as fh:
            fh.write(json.dumps({"state": "red"}) + "\n")
            fh.write(json.dumps({"done": True, "n": 24}) + "\n")
        rows, n = self._bench().read_results(self.path)
        self.assertNotEqual(
            len(rows), n,
            "a bench that wrote one row and claimed 24 must be visible as "
            "short; the marker is what makes that comparison possible")

    def test_the_bench_scrubs_between_mutations(self):
        """**Not only after the last one.** The tree is restored and cleaned
        between runs, or a file one mutation wrote is present for the next."""
        src = open(os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "bin", "mutation-bench.py"), encoding="utf-8").read()
        i = src.index("code, err = run(a.test.split(), tree, a.timeout)")
        self.assertIn("scrub(tree)", src[i:i + 400],
                      "the tree is not cleaned between mutations, so what one "
                      "run writes is present for the next")
        self.assertIn('"clean"', src,
                      "restoring tracked files leaves untracked artefacts, "
                      "which is how two files named `None` survived a restore")
        self.assertIn('"checkout", "--"', src,
                      "nothing restores the tracked files a mutation edited")



if __name__ == "__main__":
    unittest.main(verbosity=2)
