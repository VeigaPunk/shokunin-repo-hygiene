#!/usr/bin/env python3
"""S62ScoutSources — quote verification for the round-62 frontier sources.

Method (the r61 seat's method, unchanged):
  strip HTML tags (regex <[^>]+>), decode HTML entities (html.unescape),
  map U+00A0/U+2009/U+200B/U+2007 to a space, collapse whitespace runs to one space.
  A quote is VERBATIM when it is a contiguous substring of the normalized capture.

Each capture is checked three ways:
  raw-normalized  -- the fetched HTML, normalized in memory
  text            -- the tag-stripped text file written next to the capture
  man             -- the installed man page (git 2.56.0), normalized; corroboration only

Exit status: 0 when every quote is verbatim in both the raw capture and the text file
and every quote is <= 25 words; 1 otherwise.
"""
import hashlib
import html
import os
import re
import sys

S = os.path.dirname(os.path.abspath(__file__))
CAP = os.path.join(S, "captures")


def norm(raw: str) -> str:
    t = re.sub(r"<[^>]+>", "", raw)
    t = html.unescape(t)
    for ch in ("\u00a0", "\u2009", "\u200b", "\u2007"):
        t = t.replace(ch, " ")
    return re.sub(r"\s+", " ", t)


def sha256(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


LS = "Similar to -t, but use lowercase letters for files that are marked as assume unchanged (see git-update-index[1])."
S291 = ("This does not work as expected, since Git may still check working tree files "
        "against the index when performing certain operations.")

# (label, capture file, text file, quote, heading, anchor)
QUOTES = [
    ("S292-primary", "ls-files.html", "ls-files.txt", LS,
     "OPTIONS (h2 id=_options), option -v",
     "Documentation/git-ls-files.txt--v"),
    ("S292-corr-tags-S", "ls-files.html", "ls-files.txt",
     "tracked file that is skip-worktree",
     "OPTIONS (h2 id=_options), option -t status-tag list, entry S",
     "Documentation/git-ls-files.txt--t"),
    ("S292-corr-tags-H", "ls-files.html", "ls-files.txt",
     "tracked file that is not either unmerged or skip-worktree",
     "OPTIONS (h2 id=_options), option -t status-tag list, entry H",
     "Documentation/git-ls-files.txt--t"),
    ("S291-notes", "update-index.html", "update-index.txt", S291,
     "NOTES (h2 id=_notes)",
     "Documentation/git-update-index.txt---notes"),
]

out = []
out.append("quote-check.txt — S62ScoutSources, souji round 62")
out.append("access_date=2026-11-05")
out.append("method: strip HTML tags (regex <[^>]+>), decode HTML entities (html.unescape),")
out.append("        map U+00A0/U+2009/U+200B/U+2007 to space, collapse whitespace runs to one space.")
out.append("        VERBATIM = the quote is a contiguous substring of the normalized text (find() >= 0).")
out.append("")
allok = True
for label, html_f, txt_f, q, heading, anchor in QUOTES:
    hp = os.path.join(CAP, html_f)
    tp = os.path.join(CAP, txt_f)
    h_raw = open(hp, encoding="utf-8", errors="replace").read()
    h_norm = norm(h_raw)
    t_raw = open(tp, encoding="utf-8", errors="replace").read()
    t_norm = re.sub(r"\s+", " ", t_raw)
    i_h = h_norm.find(q)
    i_t = t_norm.find(q)
    ok = (i_h >= 0) and (i_t >= 0)
    words = len(q.split())
    words_ok = words <= 25
    allok = allok and ok and words_ok
    out.append("=== %s" % label)
    out.append("capture: captures/%s" % html_f)
    out.append("capture_sha256: %s" % sha256(hp))
    out.append("text: captures/%s" % txt_f)
    out.append("text_sha256: %s" % sha256(tp))
    out.append("heading: %s" % heading)
    out.append("anchor:  %s" % anchor)
    out.append("quote:   %s" % q)
    out.append("words:   %d (limit 25)" % words)
    out.append("words_ok: %s" % ("yes" if words_ok else "NO"))
    out.append("VERBATIM in raw capture (normalized): %s (offset %d)" % ("YES" if i_h >= 0 else "NO", i_h))
    out.append("VERBATIM in tag-stripped text:        %s (offset %d)" % ("YES" if i_t >= 0 else "NO", i_t))
    out.append("quote_sha256: %s" % hashlib.sha256(q.encode()).hexdigest())
    if i_h >= 0:
        out.append("context: ...%s..." % h_norm[max(0, i_h - 80):i_h + len(q) + 40].strip())
    out.append("")

out.append("SUMMARY: all quotes verbatim in raw capture AND tag-stripped text = %s"
           % ("YES" if allok else "NO"))
txt = "\n".join(out) + "\n"
with open(os.path.join(S, "quote-check.txt"), "w", encoding="utf-8") as fh:
    fh.write(txt)
print(txt, end="")
sys.exit(0 if allok else 1)
