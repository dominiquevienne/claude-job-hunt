#!/usr/bin/env python3
"""Supply an intermediate certificate a server forgot to send. Issue #104.

**`empleate.gob.es` sends its leaf and nothing else.** Measured 2026-09-03:

    openssl s_client   ->  0 s:CN=*.empleate.gob.es      (and no 1 s:)
                           Verify return code: 21 (unable to verify the
                           first certificate)
    urllib             ->  CERTIFICATE_VERIFY_FAILED, unable to get local
                           issuer certificate

**Browsers do not notice**, because they cache intermediates from other sites
and fetch the missing one from the AIA extension. So the operator has no
symptom to fix, and the plugin is the only thing that breaks.

THE RULE THIS SITS UNDER. A third party's infrastructure problem is not the
plugin's to fix. **The exception, and it is narrow: when the fault is masked
for web users — so the operator has no reason to correct it — and an
alternative exists that keeps verification intact, take the alternative.**
Supplying the missing intermediate keeps it intact entirely: the same chain is
verified, to the same root, with the same store.

**`verify=False` is never the alternative** and no wording of the request makes
it one. It does not fix this connection, it removes the check from every
connection the plugin makes.

WHAT WAS VERIFIED BEFORE THIS WAS EMBEDDED, and the name was not enough:

    the leaf's AIA names   http://crt.sectigo.com/EntrustOVTLSIssuingRSACA2.crt
    fetched                200 application/pkix-cert, 1 594 bytes
    subject                CN=Entrust OV TLS Issuing RSA CA 2
                           — identical to the leaf's issuer
    issuer                 CN=Sectigo Public Server Authentication Root R46
    `openssl verify -untrusted inter.pem leaf.pem`   ->  OK
    that root in Python's default store               ->  present, of 188

**It chains, and it was checked rather than assumed from its name.**

NARROW ON PURPOSE. `context_for()` returns `None` for every host but the two
named, and the caller then uses the ordinary default context. **Nothing here
widens trust globally**; the augmented store exists for these hosts only.

AND IT WILL EXPIRE. This certificate stops being valid on the date printed by
`expires()`, read **from the certificate itself** rather than from a constant
that could drift away from it. **On that day the failure must name itself** —
`shared/never-fail-silently.md` — instead of returning as an opaque
`CERTIFICATE_VERIFY_FAILED` and making somebody repeat this whole
investigation. `context_for()` raises `Expired` with the date and the AIA URL
to fetch a fresh one from.
"""

import datetime
import ssl

__all__ = ["HOSTS", "AIA_URL", "Expired", "context_for", "expires", "check"]

# The two names the certificate covers and the adapter reads. **A set, not a
# suffix match**: `notempleate.gob.es` must not pick this up.
HOSTS = frozenset({"empleate.gob.es", "www.empleate.gob.es"})

AIA_URL = "http://crt.sectigo.com/EntrustOVTLSIssuingRSACA2.crt"

INTERMEDIATE = """\
-----BEGIN CERTIFICATE-----
MIIGNjCCBB6gAwIBAgIRAIIHau9WPYiNkOddhKBQHE0wDQYJKoZIhvcNAQEMBQAw
XzELMAkGA1UEBhMCR0IxGDAWBgNVBAoTD1NlY3RpZ28gTGltaXRlZDE2MDQGA1UE
AxMtU2VjdGlnbyBQdWJsaWMgU2VydmVyIEF1dGhlbnRpY2F0aW9uIFJvb3QgUjQ2
MB4XDTI0MTIxMTAwMDAwMFoXDTI3MTIxMDIzNTk1OVowUTELMAkGA1UEBhMCQ0Ex
GDAWBgNVBAoTD0VudHJ1c3QgTGltaXRlZDEoMCYGA1UEAxMfRW50cnVzdCBPViBU
TFMgSXNzdWluZyBSU0EgQ0EgMjCCAaIwDQYJKoZIhvcNAQEBBQADggGPADCCAYoC
ggGBAKo4ANoGIiqBGhTl3Wb2KYyxA/2xdrUR6VP+yFWqlm6BKHKib/XHiiE8UmZO
iUQzSWNXKWNRwuVrzq1gzFKLfU8FiV9rCRd+uW5JpzxLVO7Ojzpxj6/9P3oYpiO6
3T51mxqiEv9c2wKrO8aY3d4v/FnzTcbytQI2W4a2vKq+ZV/61Ph3+a26Y16KJMWg
LKKeRNEsOxoa/qr7ro8T0/6CzQhxKnVeuJMsOiVV45WqhFmUUx0FOFbH9wbPG7Fj
ddpkHGUxtdy433BVKvnwbemXDCHy+L1PhidcX3k+vYYD4xbuC3xApQcNBahpn6pG
9AGbbs5vjvs7LAFkewYG+NYH3JcF4f5sPhOFwlEoivxro57coEWzvIheq3dp8U3r
/8GyeK6cWK0fp+0w0JhckdKzMUo0Fxi2dlXsmcRch/Borkh9PXv3NGzs5/gmOYcO
Pa+46gyrlSHr4t7miFahk0Fpii8kBIZ1fBS/J0O4s85e9zgfMhZv0W5A2reGQQjB
9JFO/QIDAQABo4IBeTCCAXUwHwYDVR0jBBgwFoAUVnNYZJX5khqwEioEYnmhQBWI
IUkwHQYDVR0OBBYEFBfRrwB0+VX7UjfYhHYLWxKKUFrFMA4GA1UdDwEB/wQEAwIB
hjASBgNVHRMBAf8ECDAGAQH/AgEAMB0GA1UdJQQWMBQGCCsGAQUFBwMBBggrBgEF
BQcDAjATBgNVHSAEDDAKMAgGBmeBDAECAjBUBgNVHR8ETTBLMEmgR6BFhkNodHRw
Oi8vY3JsLnNlY3RpZ28uY29tL1NlY3RpZ29QdWJsaWNTZXJ2ZXJBdXRoZW50aWNh
dGlvblJvb3RSNDYuY3JsMIGEBggrBgEFBQcBAQR4MHYwTwYIKwYBBQUHMAKGQ2h0
dHA6Ly9jcnQuc2VjdGlnby5jb20vU2VjdGlnb1B1YmxpY1NlcnZlckF1dGhlbnRp
Y2F0aW9uUm9vdFI0Ni5wN2MwIwYIKwYBBQUHMAGGF2h0dHA6Ly9vY3NwLnNlY3Rp
Z28uY29tMA0GCSqGSIb3DQEBDAUAA4ICAQBP/UQxKHBFQTfLCE6B7MkHDnFHqMlk
3boabJl0VxzIyLvMcgY6MVUwG0tOw/0aOPxKMwGTUQ+Mbj06XFQ9zwHP1rWpiGW3
SiJRhsGRY8BXTrU4l34Ysb30q77mTdjLXJfClBXRnVB0Gj/3eQmIIUSG16yjRKm4
g4MMXBK66Egq1VFHDvlSRRwZtiYzgXyv6umJMmtDtWqeyYXK5N1XGQ7UdlPUEpf5
/TI7zsFIR2PpgFmfedXReAtkwfiuwu2lVP5FcUMl9ZJyqSacV0Jd4PXkWKkcIWCb
a5KhD7TCCSyiLQWAbZLBG7TX+HBAaIAuCWPG5CaSK2H5qtIUlkrsw7keWBxW1Q6L
/j8N7vqb5KRAEDeBWIx9u5OqGORvRSo6FqZ7rq4opmXCMgLhJx4Cojccoj0i+p8o
Rfz32Yag1NPGBII2YNvgSbGKcDlpdxtvoKDPXnYn/2KBrJfCssWVadI83XbNc+n+
fdSupnjRzPY0KHx+V0glh3Qx14hYaGFJ0v4Of+kbrUyoHA1Ex5Lb0pZUU6vawIST
2X2bIDtDwJwObKgRRYPwUg+bo1Tp3/JL8uoYfb4ibbQHkMjYgGaartCpFeEZZbHa
ZIT+D2OnrLUsZuM4N5slfyi42i3NVnhmmduazaexMoWDATwL/8v2FH2t5Zrz7l++
qBfllYs4GyW26A==
-----END CERTIFICATE-----
"""


class Expired(Exception):
    """The embedded certificate is past its validity. Named, never silent."""


def expires():
    """`notAfter` of the embedded certificate, read from the certificate.

    Public API only — `load_verify_locations(cadata=...)` then
    `get_ca_certs()`. **A constant written beside the PEM would be a second
    source of truth**, and this repository spent a day on fields that drifted
    from what they described.
    """
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.load_verify_locations(cadata=INTERMEDIATE)
    got = ctx.get_ca_certs()[0]["notAfter"]
    return datetime.datetime.strptime(got, "%b %d %H:%M:%S %Y %Z").replace(
        tzinfo=datetime.timezone.utc)


def context_for(host, now=None):
    """An SSL context for `host`, or **`None` — meaning use the default.**

    `None` is not a failure: it is *this host needs nothing special*, which is
    every host but two.
    """
    if host not in HOSTS:
        return None
    when = now or datetime.datetime.now(datetime.timezone.utc)
    end = expires()
    if when > end:
        raise Expired(
            f"the intermediate certificate embedded for {host} expired on "
            f"{end:%Y-%m-%d}. **This is not a new TLS fault and not a "
            f"change at the operator**: {host} has always sent its leaf alone "
            f"and relied on clients fetching the issuer themselves. Fetch the "
            f"current one from the AIA URL the leaf publishes — {AIA_URL} — "
            f"check that it verifies the leaf (`openssl verify -untrusted`), "
            f"and replace the block in `_tls.py`. **Do not disable "
            f"verification**: that removes the check from every connection "
            f"this plugin makes, and it would not fix this one.")
    ctx = ssl.create_default_context()
    # **Added to the store for these hosts only.** The cost, stated: the
    # intermediate is then trusted directly rather than through its root, so a
    # future distrust of it by that root would not reach us. That is why
    # `check()` exists and why the set of hosts is two names long.
    ctx.load_verify_locations(cadata=INTERMEDIATE)
    return ctx


def check():
    """What to run when this looks wrong: the facts, not a verdict."""
    end = expires()
    left = (end - datetime.datetime.now(datetime.timezone.utc)).days
    return {"hosts": sorted(HOSTS), "expires": f"{end:%Y-%m-%d}",
            "days_left": left, "aia_url": AIA_URL,
            "note": ("re-fetch from `aia_url` and verify with "
                     "`openssl verify -untrusted <new> <leaf>` before "
                     "replacing the embedded block")}
