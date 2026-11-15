"""The transport to a Google Sheet, and nothing else: a token, a read, a write.

**Why there is not a single third-party import here.** `tests/test_core.py`
carries `NoDependencies.test_nothing_outside_the_standard_library_is_imported`,
which asserts that NO module of this repository imports outside the standard
library, so that the plugin keeps a zero-install path. The first version of
this file signed its token with `cryptography` — present on the machine it was
written on — and that suite turned it RED. **The question was never "is the
library here" but "does the plugin allow a dependency", and the repository
answers it with a test.**

**So the RS256 signature goes through `openssl`**, which is a BINARY and not an
import. The private key is fed to it through a FIFO: the key material never
lands in a file, and the node that carries it is created inside a 0700
directory that is removed in a `finally`. Measured on 2026-11-15: a key passed
as `/dev/fd/N` is REFUSED by openssl ("Bad"), a FIFO works, and a temporary
600 file works — so the FIFO is the only shape that both works and keeps the
key off the disk.

**AND WINDOWS HAS NO FIFOS**, which this machine cannot discover: `os.mkfifo`
simply does not exist there, and the CI is the only instrument that sees it —
it turned the first version RED on both Windows jobs with
`AttributeError: module 'os' has no attribute 'mkfifo'` while Linux and macOS
passed. So there are TWO paths and the weaker one is DECLARED rather than
hidden: where FIFOs exist the key never touches a file, and where they do not
it goes through a 0600 file inside a 0700 directory removed in a `finally`.
The fallback is exercised on POSIX too, by a test that makes `os.mkfifo`
raise — simulating an absent trait is possible for a BANC even when the trait
is unavailable at runtime.

**Why the write is an UPDATE and never a CLEAR.** `events_sheet.merge` builds
the UNION of the tab and our rows, so the row count never decreases and no row
the sheet holds can be dropped. Writing the union over the top is therefore
safe without clearing anything below it — and clearing is the one operation
that could destroy a row another agent put there.

**What this module refuses to do.** It does not look for the key anywhere but
the path it is given, it does not create a sheet, it does not share one, and it
never prints the key, the token, or the service-account address: a refusal says
WHICH step failed and what the provider answered, never with what identity.
"""

from __future__ import annotations

import base64
import json
import os
import shutil
import subprocess
import tempfile
import threading
import time
import urllib.error
import urllib.parse
import urllib.request

SCOPE = "https://www.googleapis.com/auth/spreadsheets"
API = "https://sheets.googleapis.com/v4/spreadsheets/"
DEFAULT_KEY = "~/.job-sync-sa.json"
ENV_KEY = "JOB_SYNC_SA_KEY"

EXIT_NO_KEY = 6          # no credential: the integration is simply not set up
EXIT_BAD_KEY = 7         # a file is there and it is not a service-account key
EXIT_REFUSED = 8         # the provider refused — token, sharing, or API off
EXIT_NO_OPENSSL = 9      # the signer is missing, which is not the key's fault

#  The fields a service-account key must carry for this to work. Checked by
#  NAME and never by shape: a key that is missing one of them fails later, at
#  the signature or the token exchange, with a message about cryptography
#  rather than about setup — and that message sends the reader elsewhere.
REQUIRED = ("type", "private_key", "client_email", "token_uri")


class SheetsRefused(Exception):
    """A refusal that names its step. Carries an exit code and no identity."""

    def __init__(self, message, code=EXIT_REFUSED):
        super().__init__(message)
        self.code = code


def key_path(given=None):
    """Where the credential is expected. Resolved, never searched for.

    The order is explicit so that a user who moved the file can say so without
    editing code: the argument wins, then the environment, then the documented
    default. **A missing file is not an error here** — it is what "the
    integration is not set up" looks like, and the caller decides.
    """
    return os.path.expanduser(given or os.environ.get(ENV_KEY) or DEFAULT_KEY)


def credential(given=None):
    """Load and VALIDATE the key. Raises with a code; never echoes a value."""
    path = key_path(given)
    if not os.path.exists(path):
        raise SheetsRefused(
            f"no service-account key at {path}. The sheet integration is "
            f"OPT-IN and this is what 'not set up' looks like: put the key "
            f"there with mode 600, or name another path with ${ENV_KEY}",
            EXIT_NO_KEY)
    try:
        with open(path, "rb") as fh:
            data = json.loads(fh.read().decode("utf-8"))
    except PermissionError:
        raise SheetsRefused(
            f"{path} is not readable by this user. A key owned by another "
            f"account cannot be read by the plugin either — `chown` it rather "
            f"than widening its mode, which would expose it to every account "
            f"on the machine", EXIT_NO_KEY)
    except (ValueError, UnicodeDecodeError) as exc:
        raise SheetsRefused(f"{path} is not readable JSON: {exc}", EXIT_BAD_KEY)
    if not isinstance(data, dict):
        raise SheetsRefused(f"{path} is JSON and is not an object", EXIT_BAD_KEY)
    missing = [k for k in REQUIRED if not data.get(k)]
    if missing:
        raise SheetsRefused(
            f"{path} is missing {', '.join(missing)} — it is not a "
            f"service-account key", EXIT_BAD_KEY)
    if data.get("type") != "service_account":
        raise SheetsRefused(
            f"{path} declares type {data['type']!r} and this transport only "
            f"knows service accounts", EXIT_BAD_KEY)
    return data


def _b64(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=")


def sign(pem, payload, timeout=30):
    """RS256 over `payload`, signed by `openssl`, key fed through a FIFO.

    The FIFO is the point: `-sign /dev/fd/N` is refused by openssl, a temporary
    file would put the private key on the disk, and a pipe node carries no
    data of its own. The writer is a daemon thread because `open()` on a FIFO
    blocks until a reader arrives — if openssl never starts, nothing must hang
    the caller.
    """
    exe = shutil.which("openssl")
    if not exe:
        raise SheetsRefused(
            "openssl is not on PATH. This transport signs with it rather than "
            "with a Python library, because the suite forbids a dependency; "
            "without it the integration cannot authenticate", EXIT_NO_OPENSSL)
    box = tempfile.mkdtemp(prefix="job-sync-sign-")
    os.chmod(box, 0o700)
    node = os.path.join(box, "key")
    try:
        try:
            os.mkfifo(node, 0o600)
            piped = True
        except (AttributeError, NotImplementedError, OSError):
            #  No FIFOs here — Windows. The key goes through a 0600 file in a
            #  0700 directory instead, and this is the WEAKER path: it is
            #  declared in the module head rather than silently taken.
            piped = False
            handle = os.open(node, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            try:
                os.write(handle, pem)
            finally:
                os.close(handle)
        if piped:
            def feed():
                try:
                    with open(node, "wb") as fh:
                        fh.write(pem)
                except OSError:
                    pass

            threading.Thread(target=feed, daemon=True).start()
        done = subprocess.run([exe, "dgst", "-sha256", "-sign", node],
                              input=payload, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, timeout=timeout)
    except OSError as exc:
        raise SheetsRefused(f"could not sign: {exc}", EXIT_NO_OPENSSL)
    finally:
        shutil.rmtree(box, ignore_errors=True)
    if done.returncode != 0 or not done.stdout:
        raise SheetsRefused(
            "openssl refused to sign with this key: "
            + done.stderr.decode("utf-8", "replace")[:200], EXIT_BAD_KEY)
    return done.stdout


def assertion(cred, scope=SCOPE, now=None, lifetime=3600):
    """The signed JWT. Split out from `token` so it can be tested OFFLINE:
    the parts that can be wrong here — the segments, the claims, the signature
    — are the parts a provider answers about in the least useful way."""
    issued = int(time.time() if now is None else now)
    head = _b64(json.dumps({"alg": "RS256", "typ": "JWT"},
                           separators=(",", ":")).encode())
    body = _b64(json.dumps({"iss": cred["client_email"], "scope": scope,
                            "aud": cred["token_uri"], "iat": issued,
                            "exp": issued + lifetime},
                           separators=(",", ":")).encode())
    signing_input = head + b"." + body
    return signing_input + b"." + _b64(
        sign(cred["private_key"].encode("utf-8"), signing_input))


def token(cred=None, scope=SCOPE, opener=None, timeout=30):
    """Exchange the assertion for an access token. Returns the token only."""
    cred = cred or credential()
    post = urllib.parse.urlencode({
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": assertion(cred, scope)}).encode()
    request = urllib.request.Request(cred["token_uri"], data=post)
    try:
        with (opener or urllib.request.urlopen)(request, timeout=timeout) as fh:
            got = json.loads(fh.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise SheetsRefused(
            f"the token exchange was refused with HTTP {exc.code}: "
            f"{exc.read().decode('utf-8', 'replace')[:300]}")
    if not got.get("access_token"):
        raise SheetsRefused("the token exchange returned no access_token")
    return got["access_token"]


def _call(access, method, path, payload=None, query="", timeout=30,
          opener=None):
    url = API + path + (("?" + query) if query else "")
    request = urllib.request.Request(
        url, method=method,
        headers={"Authorization": "Bearer " + access,
                 "Content-Type": "application/json"},
        data=None if payload is None else json.dumps(payload).encode())
    try:
        with (opener or urllib.request.urlopen)(request, timeout=timeout) as fh:
            return json.loads(fh.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:400]
        hint = ""
        if exc.code in (403, 404):
            hint = (" — either the sheet is not shared with the service "
                    "account, or the Sheets API is off for its project; the "
                    "two answer the same way and both are one click")
        raise SheetsRefused(f"{method} {path} was refused with HTTP "
                            f"{exc.code}{hint}: {detail}")


def fetch_values(sheet, a1, access=None, opener=None):
    """Read a range. Named `fetch_` and not `read_`: `events_sheet.read_tab`
    reads a FILE, and two functions one letter apart on the same object are
    how a caller reaches for the wrong one."""
    access = access or token(opener=opener)
    got = _call(access, "GET", "%s/values/%s" % (sheet, urllib.parse.quote(a1)),
                opener=opener)
    return got.get("values", [])


def write_values(sheet, a1, values, access=None, opener=None):
    """Write a range IN PLACE, RAW. Nothing is cleared — see the module head."""
    access = access or token(opener=opener)
    got = _call(access, "PUT",
                "%s/values/%s" % (sheet, urllib.parse.quote(a1)),
                {"values": values}, "valueInputOption=RAW", opener=opener)
    return got.get("updatedCells", 0), got.get("updatedRange", a1)
