#!/usr/bin/env python3
"""R41w2mutationtester06 helper: writes single-defect mutants of the landed C1 files.

Base bytes are read from the lane tip with `git show` (read-only). Each mutation replaces an exact
substring whose occurrence count is asserted, so every mutant differs from its base by one edit.
Output: mutants/<id>.<basename> plus mutants/manifest.tsv (id, dest, base, description).
"""
import os, subprocess, sys

SEAT = os.path.dirname(os.path.abspath(__file__))
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
TIP = "1d41c13574db80fdd9a4bde490b712da7ce2a85f"
MEAS = "bffcc0f660ff36eb8add3f61582748a7af019a5b"
BASES = {
    "r41": ("corpus/lessons/round-41.md", "corpus/lessons/round-41.md"),
    "r40": ("corpus/lessons/round-40.md", "corpus/lessons/round-40.md"),
    "reg": ("corpus/SOURCES.md", "corpus/SOURCES.md"),
}

def base_text(path):
    p = subprocess.run(["git", "-C", LANE, "show", "%s:%s" % (TIP, path)], stdout=subprocess.PIPE, check=True)
    return p.stdout.decode("utf-8")

def line_with(text, needle):
    hits = [l for l in text.split("\n") if needle in l]
    assert len(hits) == 1, (needle, len(hits))
    return hits[0]

# (id, base, old, new, count, description, expected)
# old/new are exact substrings; new=None deletes the whole line containing `old` (old must be the full line).
M = [
 # --- lesson round-41.md: CORRECTION lines and prose
 ("L01", "r41", "derived=rows=2,v2.56.0=0 rev=", "derived=rows=1,v2.56.0=0 rev=", 1, "derived value of I1 changed 2->1", "junk=1, I1 uncorrected"),
 ("L02", "r41", "derived=before=6,after=3 rev=", "derived=before=6,after=6 rev=", 1, "derived value of I3 changed after=3->6", "junk=1, I3 uncorrected"),
 ("L03", "r41", "derived=occurrences=0 rev=", "derived=occurrences=1 rev=", 1, "derived value of I4 changed 0->1", "junk=1, I4 uncorrected"),
 ("L04", "r41", "derived=before=6,after=3 rev=" + MEAS, "derived=before=6,after=3 rev=" + MEAS[:-1] + "c", 1, "one hex char of the MEASURED rev on the I3 line", "junk=1, I3 uncorrected"),
 ("L05", "r41", "derived=occurrences=0 rev=" + MEAS, "derived=occurrences=0 rev=" + MEAS[:-1], 1, "I4 rev truncated to 39 hex digits", "junk=1 or malformed, I4 uncorrected"),
 ("L06", "r41", "derived=rows=2,v2.56.0=0 rev=" + MEAS, "derived=rows=2,v2.56.0=0 rev=31e4d3e758bb903808a9270018d7e5be99ce38a4", 1, "I1 rev replaced by a real non-MEASURED commit", "junk=1, I1 uncorrected"),
 ("L07", "r41", "CORRECTION I3 file=SCORECARD.md", "CORRECTION I5 file=SCORECARD.md", 1, "id I3 renamed I5 (unknown id)", "junk=1, I3 uncorrected"),
 ("L08", "r41", "file=SCORECARD.md filed=like-for-like", "file=SCORECARD filed=like-for-like", 1, "file token of I3 truncated", "junk=1, I3 uncorrected"),
 ("L09", "r41", "filed=like-for-like derived", "filed=like-for-kind derived", 1, "filed token of I3 changed", "junk=1, I3 uncorrected"),
 ("L10", "r41", "file=corpus/lessons/round-40.md filed=9-rows", "file=corpus/lessons/round-39.md filed=9-rows", 1, "file token of I1 changed to another round", "junk=1, I1 uncorrected"),
 ("L11", "r41", "source=S258", "source=S033", 1, "I1 source row changed S258->S033 (tier A but status queued, opened 2026-10-19)", "sourced=0, I1 uncorrected"),
 ("L12", "r41", "source=S258", "source=S259", 1, "I1 source row changed to an id that is absent from the registry", "sourced=0, I1 uncorrected"),
 ("L13", "r41", "CORRECTION I4 file=LOG.md filed=error-text-recorded derived=occurrences=0 rev=" + MEAS + " source=-\n", None, 1, "delete the I4 CORRECTION line", "uncorrected=1"),
 ("L14", "r41", "CORRECTION I1 file=corpus/lessons/round-40.md filed=9-rows derived=rows=2,v2.56.0=0 rev=" + MEAS + " source=S258\n", None, 1, "delete the I1 CORRECTION line", "uncorrected=1, sourced=0"),
 ("L15", "r41", "CORRECTION I3 file=SCORECARD.md filed=like-for-like derived=before=6,after=3 rev=" + MEAS + " source=-", "CORRECTION I3 file=SCORECARD.md filed=like-for-like derived=before=6,after=3 rev=" + MEAS + " source=-\nCORRECTION I3 file=SCORECARD.md filed=like-for-like derived=before=6,after=3 rev=" + MEAS + " source=-", 1, "duplicate the I3 CORRECTION line (adjacent)", "survives (duplicate lines not counted as junk)"),
 ("L16", "r41", "CORRECTION I4 file=LOG.md", " CORRECTION I4 file=LOG.md", 1, "indent the I4 CORRECTION line by one space", "uncorrected=1 (malformed line skipped, not junk)"),
 ("L17", "r41", "source=- \n" if False else "derived=before=6,after=3 rev=" + MEAS + " source=-", "derived=before=6,after=3 rev=" + MEAS + " source=- (checked)", 1, "trailing text after the I3 CORRECTION line", "uncorrected=1"),
 ("L18", "r41", "CORRECTION I4 file=LOG.md filed=error-text-recorded derived=occurrences=0 rev=" + MEAS + " source=-", "```\nCORRECTION I4 file=LOG.md filed=error-text-recorded derived=occurrences=0 rev=" + MEAS + " source=-\n```", 1, "wrap the I4 CORRECTION line in a code fence", "survives (counter is fence-blind; N1)"),
 ("L19", "r41", "## Named limits", "Retraction: the CORRECTION lines above are withdrawn; the filed statements stand.\n\n## Named limits", 1, "prose retraction of all three corrections inserted above the limits section", "survives (counter reads only CORRECTION lines; N1)"),
 ("L20", "r41", "CORRECTION I4 file=LOG.md filed=error-text-recorded derived=occurrences=0 rev=" + MEAS + " source=-", "CORRECTION I4 file=LOG.md filed=error-text-recorded derived=occurrences=0 rev=" + MEAS + " source=- \n", 1, "trailing space after the I4 CORRECTION line (benign control)", "survives (benign)"),
 ("L21", "r41", "Round: souji round 41, hyaku run 11, attempt 1.", "Round: souji round 41, hyaku run 11, attempt 2.", 1, "lesson header attempt number edited (not a CORRECTION line)", "survives (no check reads the header)"),
 ("L22", "r41", "CORRECTION I4 file=LOG.md filed=error-text-recorded derived=occurrences=0 rev=" + MEAS + " source=-", "CORRECTION I4 file=LOG.md filed=error-text-recorded derived=occurrences=0 rev=" + MEAS + " source=-\nCORRECTION I9 file=LOG.md filed=x derived=occurrences=0 rev=" + MEAS + " source=-", 1, "add an unknown-id CORRECTION line (junk control)", "junk=1 detected"),
 ("L23", "r41", "CORRECTION I1 file=corpus/lessons/round-40.md", "CORRECTION I1 file=corpus/lessons/round-40.md\nCORRECTION I1 file=corpus/lessons/round-40.md", 1, "duplicate the I1 line with the same bytes (adjacent)", "survives (duplicate)"),
 # --- round-40 filed line (own clone; dest not on score-candidate allowlist)
 ("M01", "r40", "appears in 9 rows", "appears in 8 rows", 1, "filed I1 anchor rewritten 9->8 in round-40.md", "rewritten=1, mismatched=2"),
 ("M02", "r40", "appears in 9 rows", "appears in 9 rows (see round 41)", 1, "filed I1 anchor kept, sentence extended in place", "rewritten=1 (append-only prefix broken)"),
 ("M03", "r40", "## ", "Note: edited.\n\n## ", 1, "a line inserted mid-file, anchor untouched", "rewritten=1"),
 ("M04", "r40", None, "\nAppended after the filed text (legitimate append).\n", 0, "pure append at end (benign control)", "survives (intact)"),
 ("M05", "r40", "# Round 40", "# Round 40 (edited)", 1, "heading edited in first line, anchor untouched", "rewritten=1"),
]

def main():
    man = []
    for mid, base, old, new, cnt, desc, exp in M:
        path = BASES[base][0]
        text = base_text(path)
        if old is None:
            # pure append
            out = text + new
        elif new is None:
            assert text.count(old) == 1, (mid, text.count(old)); out = text.replace(old, "")
        else:
            n = text.count(old)
            assert n == cnt or (cnt == 1 and n == 1), (mid, old[:40], n)
            out = text.replace(old, new, 1)
        if mid == "L17":
            pass
        dest = BASES[base][1]
        name = "%s.%s" % (mid, os.path.basename(dest))
        with open(os.path.join(SEAT, "mutants", name), "w", encoding="utf-8", newline="") as f:
            f.write(out)
        assert out != text, mid
        man.append((mid, dest, name, desc, exp))
    with open(os.path.join(SEAT, "mutants", "manifest.tsv"), "w", encoding="utf-8") as f:
        f.write("id\tdest\tfile\tdescription\texpected\n")
        for row in man:
            f.write("\t".join(row) + "\n")
    print("wrote", len(man), "mutants")

if __name__ == "__main__":
    main()
