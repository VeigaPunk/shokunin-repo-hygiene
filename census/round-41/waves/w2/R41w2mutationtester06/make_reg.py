#!/usr/bin/env python3
"""R41w2mutationtester06 helper: registry (corpus/SOURCES.md) mutants; extends make.M and writes all mutants."""
import make

S258_LINE_PREFIX = "| S258 |"
REG = [
 ("S01", "reg", "| queued | 2026-10-19 | on-release |", "| mined | 2026-10-19 | on-release |", 1, "S033 status cell queued->mined (row rewritten, not an S258 cell)", "survives counter (S033 not read by C1); human-only"),
 ("S02", "reg", "| docs | A | git 2.55.0 worktrees/<id> admin files", "| docs | B | git 2.55.0 worktrees/<id> admin files", 1, "S033 tier cell A->B", "survives counter; human-only"),
 ("S03", "reg", "although worktree.c ages by it", "although worktree.c never ages by it", 1, "S033 locator/quote cell rewritten", "survives counter; human-only"),
 ("S04", "reg", "| code | A | what `git worktree prune`", "| code | B | what `git worktree prune`", 1, "S258 tier A->B", "sourced=0, I1 uncorrected"),
 ("S05", "reg", "| mined | 2026-10-28 | on-release |", "| queued | 2026-10-28 | on-release |", 1, "S258 status mined->queued", "sourced=0, I1 uncorrected"),
 ("S06", "reg", "| mined | 2026-10-28 | on-release |", "| mined | 2026-10-27 | on-release |", 1, "S258 date cell 2026-10-28->2026-10-27", "sourced=0, I1 uncorrected"),
 ("S07", "reg", "opened 2026-10-28)", "opened 2026-10-27)", 1, "S258 location-cell date (not one of the sourced cells)", "survives counter; human-only"),
 ("S08", "reg", "v2.56.0", "v2.55.0", -1, "S258 row: every v2.56.0 changed to v2.55.0 (single-line edit)", "sourced=0, I1 uncorrected"),
 ("S09", "reg", "| on-release | corpus/lessons/round-41.md |", "| on-release |", 1, "S258 row loses its last cell (10 cells)", "sourced=0 (cell count), I1 uncorrected"),
 ("S10", "reg", None, None, 0, "S258 row deleted", "sourced=0, I1 uncorrected"),
 ("S11", "reg", None, None, 0, "second S258 row (tier B, queued) appended after the original", "survives (first match wins; duplicate id unseen)"),
 ("S12", "reg", None, None, 0, "second S258 row (tier B, queued) inserted before the original", "sourced=0 (first match fails)"),
 ("S13", "reg", "| S258 |", "| S259 |", 1, "S258 id renamed S259 (lesson source=S258 now dangling)", "sourced=0"),
 ("S14", "reg", "| S258 |", " | S258 |", 1, "S258 row indented one space (ROW regex anchored at column 0)", "sourced=0"),
 ("S15", "reg", None, None, 0, "S258 row wrapped in a code fence", "survives (fence-blind; N2)"),
 ("S16", "reg", "| mined | 2026-10-28 | on-release |", "| mined  | 2026-10-28 | on-release |", 1, "S258 status cell extra space (benign control)", "survives (benign)"),
 ("S17", "reg", "worktree.c", "worktree.h", -1, "S258 row: every worktree.c changed to worktree.h", "sourced=0"),
 ("S18", "reg", "| on-release | corpus/lessons/round-41.md |", "| on-release | corpus/lessons/round-40.md |", 1, "S258 used-by cell names round-40 instead of round-41", "survives counter; Q62 used-by check only"),
]

def apply_reg(entry):
    mid, base, old, new, cnt, desc, exp = entry
    text = make.base_text("corpus/SOURCES.md")
    if mid in ("S10",):
        lines = text.split("\n"); idx = [i for i, l in enumerate(lines) if l.startswith("| S258 |")]
        assert len(idx) == 1; del lines[idx[0]]; return "\n".join(lines)
    if mid == "S11":
        lines = text.split("\n"); idx = [i for i, l in enumerate(lines) if l.startswith("| S258 |")]
        assert len(idx) == 1
        dup = lines[idx[0]].replace("| code | A |", "| code | B |").replace("| mined | 2026-10-28 |", "| queued | 2026-10-28 |")
        assert dup != lines[idx[0]]
        lines.insert(idx[0] + 1, dup); return "\n".join(lines)
    if mid == "S12":
        lines = text.split("\n"); idx = [i for i, l in enumerate(lines) if l.startswith("| S258 |")]
        assert len(idx) == 1
        dup = lines[idx[0]].replace("| code | A |", "| code | B |").replace("| mined | 2026-10-28 |", "| queued | 2026-10-28 |")
        lines.insert(idx[0], dup); return "\n".join(lines)
    if mid == "S15":
        lines = text.split("\n"); idx = [i for i, l in enumerate(lines) if l.startswith("| S258 |")]
        assert len(idx) == 1
        lines.insert(idx[0] + 1, "```"); lines.insert(idx[0], "```"); return "\n".join(lines)
    if cnt == -1:  # replace every occurrence inside the single S258 row
        lines = text.split("\n"); idx = [i for i, l in enumerate(lines) if l.startswith("| S258 |")]
        assert len(idx) == 1 and old in lines[idx[0]]
        lines[idx[0]] = lines[idx[0]].replace(old, new); return "\n".join(lines)
    row = "| S033 |" if mid in ("S01", "S02", "S03") else "| S258 |"
    lines = text.split("\n"); idx = [i for i, l in enumerate(lines) if l.startswith(row)]
    assert len(idx) == 1, (mid, len(idx))
    assert lines[idx[0]].count(old) == 1, (mid, lines[idx[0]].count(old))
    lines[idx[0]] = lines[idx[0]].replace(old, new, 1)
    return "\n".join(lines)

make.M = [e for e in make.M if e[0] != "M03"] + [("M03", "r40", "", "Note: edited.\n", 0, "a line prepended at the top of round-40.md, anchor untouched", "rewritten=1 (prefix broken)")]
for e in REG:
    make.M.append(e)

# patch make.main to use apply_reg for reg entries
orig = make.base_text
def main():
    import os
    man = []
    for mid, base, old, new, cnt, desc, exp in make.M:
        path = make.BASES[base][0]
        text = make.base_text(path)
        if base == "reg":
            out = apply_reg((mid, base, old, new, cnt, desc, exp))
        elif old == "":
            out = new + text
        elif old is None:
            out = text + new
        elif new is None:
            assert text.count(old) == 1, (mid, text.count(old)); out = text.replace(old, "")
        else:
            assert text.count(old) == 1, (mid, old[:40], text.count(old)); out = text.replace(old, new, 1)
        assert out != text, mid
        dest = make.BASES[base][1]
        name = "%s.%s" % (mid, os.path.basename(dest))
        with open(os.path.join(make.SEAT, "mutants", name), "w", encoding="utf-8", newline="") as f:
            f.write(out)
        man.append((mid, dest, name, desc, exp))
    with open(os.path.join(make.SEAT, "mutants", "manifest.tsv"), "w", encoding="utf-8") as f:
        f.write("id\tdest\tfile\tdescription\texpected\n")
        for row in man:
            f.write("\t".join(row) + "\n")
    print("wrote", len(man), "mutants")

if __name__ == "__main__":
    main()
