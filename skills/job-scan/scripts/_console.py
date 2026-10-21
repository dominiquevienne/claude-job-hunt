"""argparse writes its help to a console that may not be able to encode it.

**#1166, measured 2026-10-21: of 298 argparse CLIs in this directory, 75 exit
with a traceback on `--help` under `PYTHONIOENCODING=cp1252`**, the default
code page of a Windows console -- a platform the owner targets. The character
is almost always the arrow this repository writes 471 times in its docstrings;
after that come Arabic, Persian and Turkish in the cards they cite.

    UnicodeEncodeError: 'charmap' codec can't encode character '\\u2192'

Importing this module patches `argparse.ArgumentParser._print_message`, the
one place argparse writes help, usage and its own error text.

WHAT THIS DELIBERATELY DOES NOT DO, and it is the whole choice (#1166 left the
form to the session that codes it). It does NOT reconfigure `sys.stdout`. A
process-wide `encoding="utf-8"` would also stop the crash, and it would reach
the DATA path -- which sounds like more value and is worth less: an adapter's
`list` prints JSON that a parent process reads, and a parent decoding with the
locale encoding would then read UTF-8 bytes as mojibake. **That trades a loud
failure for a silent one**, and the arrow in a job title would be corrupted in
a file nobody re-reads. A process-wide `errors="replace"` is worse again: it
writes `?` into that JSON. So the fix is bounded to the text a HUMAN reads,
and every data write in this directory is left exactly as it was.

AND THE DEGRADATION IS CONDITIONAL ON THE FAILURE, not unconditional. The
original write is attempted first and kept whenever it succeeds, so the 223
CLIs that were already fine are unaffected to the byte; `?` appears only where
the alternative was a traceback. An unconditional `errors="replace"` would
have replaced characters on consoles that could have printed them.

*Imported for its side effect. That is impolite, and the alternative was
editing 298 `main()` bodies, each written differently -- a far larger surface
for a mistake. The guard in `tests/` holds the real directory, so a CLI added
without this import is named by a failing test and not by a user.*
"""

import argparse
import sys


def _print_message(self, message, file=None):
    """argparse's own writer, with a fallback that only runs on failure."""
    if not message:
        return
    if file is None:
        file = sys.stderr
    try:
        file.write(message)
    except UnicodeEncodeError:
        # The console named its own encoding; honour it and lose only the
        # characters it cannot represent. `errors="replace"` on the encode
        # AND the decode, because a lone surrogate would raise on the way
        # back otherwise.
        codage = getattr(file, "encoding", None) or "ascii"
        file.write(message.encode(codage, "replace").decode(codage, "replace"))


argparse.ArgumentParser._print_message = _print_message
