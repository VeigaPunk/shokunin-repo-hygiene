import re, html, hashlib, sys, os
S = os.path.dirname(os.path.abspath(__file__))
def norm(raw):
    t = re.sub(r'<[^>]+>', '', raw)
    t = html.unescape(t)
    for ch in ('\u00a0', '\u2009', '\u200b', '\u2007'):
        t = t.replace(ch, ' ')
    return re.sub(r'\s+', ' ', t)

G = open(os.path.join(S, 's290-git-log.html'), encoding='utf-8', errors='replace').read()
U = open(os.path.join(S, 's291-git-update-index.html'), encoding='utf-8', errors='replace').read()
GN, UN = norm(G), norm(U)

QUOTES = [
  # (label, capture, doc_text, quote, heading, anchor)
  ("S290-primary", "s290-git-log.html", GN,
   "Select only files that are Added (A), Copied (C), Deleted (D), Modified (M), Renamed (R)",
   "OPTIONS -> DIFF FORMATTING (h2 id=_diff_formatting)",
   "Documentation/git-log.txt---diff-filterACDMRTUXB"),
  ("S290-corroborating-1", "s290-git-log.html", GN,
   "Also, these upper-case letters can be downcased to exclude. E.g. --diff-filter=ad excludes added and deleted paths.",
   "OPTIONS -> DIFF FORMATTING (h2 id=_diff_formatting)",
   "Documentation/git-log.txt---diff-filterACDMRTUXB"),
  ("S290-corroborating-2", "s290-git-log.html", GN,
   "Various other options and paths parameters can be used to further limit the result.",
   "DESCRIPTION (h2 id=_description)",
   "Documentation/git-log.txt---description"),
  ("S291-primary", "s291-git-update-index.html", UN,
   'the object names recorded for the paths are not updated. Instead, these options set and unset the "skip-worktree" bit for the paths.',
   "OPTIONS (h2 id=_options), entry --skip-worktree / --no-skip-worktree",
   "Documentation/git-update-index.txt---skip-worktree"),
  ("S291-primary-alt", "s291-git-update-index.html", UN,
   "treat the file as unchanged when it is not present in the working directory",
   "SKIP-WORKTREE BIT (h2 id=_skip_worktree_bit)",
   "Documentation/git-update-index.txt---skip-worktree"),
  ("S291-limit-caveat", "s291-git-update-index.html", UN,
   "This does not work as expected, since Git may still check working tree files against the index when performing certain operations.",
   "NOTES (h2 id=_notes)",
   "Documentation/git-update-index.txt---notes"),
  ("S291-corroborating", "s291-git-update-index.html", UN,
   "Git commands will also avoid treating the lack of such files as an intentional deletion",
   "SKIP-WORKTREE BIT (h2 id=_skip_worktree_bit)",
   "Documentation/git-update-index.txt---skip-worktree"),
  ("S291-corroborating-2", "s291-git-update-index.html", UN,
   "Note that not all git commands will pay attention to this bit, and some only partially support it.",
   "SKIP-WORKTREE BIT (h2 id=_skip_worktree_bit)",
   "Documentation/git-update-index.txt---skip-worktree"),
  ("S291-corroborating-3", "s291-git-update-index.html", UN,
   "Although this bit looks similar to assume-unchanged bit, its goal is different.",
   "SKIP-WORKTREE BIT (h2 id=_skip_worktree_bit)",
   "Documentation/git-update-index.txt---skip-worktree"),
]

out = []
out.append("quote-check.txt — S61ScoutSources, souji round 61")
out.append("method: strip HTML tags (regex <[^>]+>), decode HTML entities (html.unescape),")
out.append("        map U+00A0/U+2009/U+200B/U+2007 to space, collapse whitespace runs to one space.")
out.append("        Each quote below was then tested with str.find() against the normalized capture text.")
out.append("        VERBATIM = the quote is a contiguous substring of the normalized capture (find() >= 0).")
out.append("")
allok = True
for label, cap, doc, q, heading, anchor in QUOTES:
    i = doc.find(q)
    ok = i >= 0
    allok = allok and ok
    words = len(q.split())
    out.append("=== %s" % label)
    out.append("capture: %s" % cap)
    out.append("heading: %s" % heading)
    out.append("anchor:  %s" % anchor)
    out.append("quote:   %s" % q)
    out.append("words:   %d (limit 25)" % words)
    out.append("words_ok: %s" % ("yes" if words <= 25 else "NO"))
    out.append("VERBATIM: %s (normalized offset %d)" % ("YES" if ok else "NO", i))
    if ok:
        out.append("context: ...%s..." % doc[max(0, i - 90):i + len(q) + 60].strip())
    out.append("")
out.append("SUMMARY: all quotes verbatim = %s" % ("YES" if allok else "NO"))
out.append("SUMMARY: all quotes <= 25 words = %s" % ("YES" if all(len(q.split()) <= 25 for _, _, _, q, _, _ in QUOTES) else "NO"))
txt = "\n".join(out) + "\n"
open(os.path.join(S, 'quote-check.txt'), 'w', encoding='utf-8').write(txt)
print(txt)
sys.exit(0 if allok else 1)
