#!/usr/bin/env python3
"""The parsing core, tested without touching the network.

**Sixty-one adapters depend on third-party sites; testing those in CI would
mean sweeping the web on every commit**, which is the thing this project
teaches people not to do. So the perimeter is the pure-parsing core, and every
case here is synthetic. Issue #108.

**Most of these cases already existed — written by hand, run once, and read
afterwards.** `_robots.py`'s group grammar was corrected twice in one day
(#101) against exactly these inputs, typed into a shell. **A case that is not
executed is a comment**, and a comment does not fail when someone changes the
function under it.

Run: `python3 -m unittest discover -s tests -v`
"""

import os
import re
import sys
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
        std = set(sys.stdlib_module_names)
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
