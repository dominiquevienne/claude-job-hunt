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
import sys
import unittest

sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "skills", "job-scan", "scripts"))

import _language          # noqa: E402
import _ldjson            # noqa: E402
import _locations         # noqa: E402
import _match             # noqa: E402
import _robots            # noqa: E402
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
        token, dis, allow = _robots.group_for(self.CLOUDFLARE)
        self.assertEqual(token, "claudebot")
        self.assertEqual(dis, ["/"])

    def test_the_star_group_still_reads_as_open(self):
        # Both are true of the same file, which is why the group has to be
        # selected before anything is evaluated.
        dis, allow = _robots._star_group(self.CLOUDFLARE)
        self.assertEqual(dis, [])
        self.assertEqual(allow, ["/"])

    def test_a_named_permission_is_found_too(self):
        # The other direction, and it is real: taleez.com allows our tokens
        # by name. Selection is not a refusal detector.
        token, dis, allow = _robots.group_for(
            "User-agent: *\nDisallow: /x\n\n"
            "User-agent: ClaudeBot\nAllow: /\n")
        self.assertEqual(token, "claudebot")
        self.assertEqual(allow, ["/"])
        self.assertEqual(dis, [])

    def test_falls_back_to_star_when_we_are_not_named(self):
        token, dis, _ = _robots.group_for(
            "User-agent: *\nDisallow: /a\n\n"
            "User-agent: GPTBot\nDisallow: /\n")
        self.assertEqual(token, "*")
        self.assertEqual(dis, ["/a"])

    def test_the_longest_matching_token_wins(self):
        # RFC 9309: the most specific match. `claude-web` is longer than
        # `claudebot`, so a file naming both binds by the longer one.
        token, dis, _ = _robots.group_for(
            "User-agent: ClaudeBot\nDisallow: /a\n\n"
            "User-agent: Claude-Web\nDisallow: /b\n")
        self.assertEqual(token, "claude-web")
        self.assertEqual(dis, ["/b"])

    def test_our_tokens_are_declared_not_derived(self):
        # A module that decides consent must not depend on a UA string built
        # elsewhere: an adapter changing its `UA` would change which rules
        # bind, silently.
        self.assertIn("claudebot", _robots.OUR_AGENTS)
        self.assertIn("claude-user", _robots.OUR_AGENTS)
        self.assertTrue(all(a == a.lower() for a in _robots.OUR_AGENTS))

    def test_repeated_named_records_merge(self):
        token, dis, _ = _robots.group_for(
            "User-agent: ClaudeBot\nDisallow: /a\n\n"
            "User-agent: ClaudeBot\nDisallow: /b\n")
        self.assertEqual((token, dis), ("claudebot", ["/a", "/b"]))


class RobotsPaths(unittest.TestCase):
    """`_match_len`: prefix, `*`, `$`, and the empty `Disallow`."""

    def test_prefix_match_returns_its_length(self):
        self.assertEqual(_robots._match_len("/p", "/pq"), 2)

    def test_no_match_is_minus_one(self):
        self.assertEqual(_robots._match_len("/z", "/pq"), -1)

    def test_star_is_a_wildcard(self):
        self.assertEqual(_robots._match_len("/a*b", "/axxb"), 5)

    def test_dollar_anchors_the_end(self):
        self.assertEqual(_robots._match_len("/x$", "/x"), 2)
        self.assertEqual(_robots._match_len("/x$", "/xy"), -1)

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
        rows = [{"match": True}, {"match": False}, {"match": True}]
        said = _match.share(rows)
        self.assertIn("3", said)
        self.assertIn("2", said)


if __name__ == "__main__":
    unittest.main(verbosity=2)
