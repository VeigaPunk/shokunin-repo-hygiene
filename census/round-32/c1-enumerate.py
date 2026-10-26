#!/usr/bin/env python3
"""r32 C1 enumeration (frozen at the r32 preregistration): the count integers that the r31 notation skipped.

Rows: every capability-table row of SCORECARD.md at --rev (default: the r32 base) — lines 147-175, 313-314,
354-355 (the rows r31 enumerated) and 422-424 (the r31 capability rows). Cell: the evidence cell (third cell).
Every maximal digit run in that cell is one item, unless a mask below covers it. Masks, applied to a copy of the
cell with every masked byte replaced by a space (positions kept):
  M1  backticked command spans: a backtick span whose first word is python3, bash, git, sha256sum or starts
      with TMPDIR= (the argv is not a count; output spans such as `cases=7 pass=7` stay)
  M2  r31 items: on lines <= 355 every `N/M` at digit boundaries and every `cases=N pass=N` (L01-L41; L29 is
      carried by id, below)
  M3  hex runs of 7+ [0-9a-f] at word boundaries (commit ids, digests)
  M4  path tokens: a token containing `/` whose first component is census, tests, tools, corpus, knowledge,
      .ufo or records, or any token ending in .py .sh .json .tsv .md .txt .out .adoc (with optional :N)
  M5  ids: an upper-case letter or two followed by digits (S035, Q63, G1, L29, R3, K5, M4, C1), incl. ranges
  M6  round tags: r<N> (also r<N>-era, r<N>w<M>), round-<N>, v<N>
  M7  versions N.N[.N], dates YYYY-MM-DD, `<...>` placeholders, a key name ending in digits before `=` (k1=),
      `exit N`, `python3`, `sha256`
Remaining digit runs are the items N01..Nk in line order, then position. Each item records its integer and its
unit words: the letters-only words (2+ letters, lower-cased) glued to the integer or separated from it by one of
` `, `=`, `:`, `(`, `-` on either side, within the same whitespace-free token or the adjacent token.
L29 (SCORECARD.md:170, the second `18/18`, r31 enumeration) is carried as item L29, integers 18 18, units
remote, source, after, json — r31's one unbound item (routed r31 closure defect 1).

Output TSV: id, line, integer, units (comma-joined), rounds (r31 rule: every integer after a standalone `r`
or after `round-` on the base line), context (40 bytes around the integer, tabs/pipes replaced).
"""
import argparse
import re
import subprocess
import sys

STOP = {"at", "over", "all", "old", "of", "in", "the", "and", "to", "on", "by", "is", "a", "an"}
LINES = list(range(147, 176)) + [313, 314, 354, 355, 422, 423, 424]
ROOTS = r"(?:census|tests|tools|corpus|knowledge|\.ufo|records)"


def mask(s, pat, flags=0):
    return re.sub(pat, lambda m: " " * len(m.group(0)), s, flags=flags)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--rev", default="85b61a151923986e7e6b48f7084b9122561b5f3d")
    a = ap.parse_args()
    text = subprocess.run(["git", "-C", a.root, "cat-file", "blob", f"{a.rev}:SCORECARD.md"],
                          capture_output=True, text=True, check=True).stdout.split("\n")
    out = ["id\tline\tinteger\tunits\trounds\tcontext"]
    n = 0
    for ln in LINES:
        line = text[ln - 1]
        cells = re.split(r"(?<!\\)\|", line)
        if not line.startswith("|") or len(cells) < 5:
            print(f"COULD-NOT-EVALUATE line {ln} is not a table row", file=sys.stderr)
            return 2
        cell = cells[3]
        m = cell
        m = mask(m, r"`(?:python3|bash|git|sha256sum|TMPDIR=)[^`]*`")
        if ln <= 355:
            m = mask(m, r"(?<!\d)\d+/\d+(?!\d)")
            m = mask(m, r"cases=\d+ pass=\d+")
        m = mask(m, r"(?<![0-9A-Za-z])[0-9a-f]{7,}(?![0-9A-Za-z])")
        m = mask(m, r"(?<![\w.])" + ROOTS + r"/[^\s`'\"(),;|]*")
        m = mask(m, r"[\w./*…-]+\.(?:py|sh|json|tsv|md|txt|out|adoc)(?::\d+(?:[-–]\d+)?)?")
        m = mask(m, r"(?<![A-Za-z0-9])[A-Z]{1,2}\d+(?:[–-][A-Z]{1,2}\d+)?(?![0-9])")
        m = mask(m, r"(?<![A-Za-z0-9])r\d+(?:-era|w\d+)?(?![0-9])")
        m = mask(m, r"round-\d+")
        m = mask(m, r"(?<![A-Za-z0-9])v\d+(?![0-9])")
        m = mask(m, r"\d+(?:\.\d+)+")
        m = mask(m, r"\d{4}-\d{2}-\d{2}")
        m = mask(m, r"<[^<>]*>")
        m = mask(m, r"[A-Za-z_]+\d+(?==)")
        m = mask(m, r"exit \d+")
        m = mask(m, r"python3|sha256")
        rounds = sorted({int(g1 or g2) for g1, g2 in re.findall(r"(?<![A-Za-z0-9])r(\d+)|round-(\d+)", line)})
        prev_units = set()
        for mm in re.finditer(r"\d+", m):
            n += 1
            s, e = mm.span()
            units = set()
            left = cell[:s]
            right = cell[e:]
            key = re.search(r"([A-Za-z][A-Za-z0-9_]*)=$", left)
            glued = re.search(r"([A-Za-z]{2,})$", left)
            if key:
                units.add(key.group(1).lower())
            else:
                if glued:
                    units.add(glued.group(1).lower())
                for w in re.findall(r"[A-Za-z]{2,}", re.match(r"^[ \-)`]{0,2}((?:[A-Za-z]+[ ]?){0,3})", right).group(1))[:3]:
                    if w.lower() not in STOP:
                        units.add(w.lower())
                        break
                if not units and re.search(r"(?:→|->)[ `]*$", left) and prev_units:
                    units |= prev_units
            prev_units = units
            ctx = cell[max(0, s - 20):e + 20].replace("\t", " ").replace("|", "/").replace("\n", " ")
            out.append(f"N{n:02d}\t{ln}\t{mm.group(0)}\t{','.join(sorted(units))}\t{','.join(map(str, rounds))}\t{ctx}")
    l170 = text[169]
    r170 = sorted({int(g1 or g2) for g1, g2 in re.findall(r"(?<![A-Za-z0-9])r(\d+)|round-(\d+)", l170)})
    out.append(f"L29\t170\t18 18\tafter,json,remote,source\t{','.join(map(str, r170))}\tremote-source-after.json18/18 (r31 L29)")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
