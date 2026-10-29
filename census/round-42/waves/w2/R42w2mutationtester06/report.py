#!/usr/bin/env python3
"""R42w2mutationtester06 — merge scores.json + the oracle shards into the table and survivor list.

Classification is the seat's reading of the oracle output (a class per survivor, with the reason);
the oracle output itself is the evidence and is read from --scratch, never edited here.
"""
import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mutants import MUTANTS  # noqa: E402

TOOL = "/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-worktree-drift.py"

# survivor -> (class, one-line behaviour, reason)
# NE  = non-equivalent: observable behaviour (stdout/rc/refusal class/traceback/--json document or mode) differs
# EQ  = equivalent under the lane's C3 rule (no observable behaviour change: code-proved, format-only or label-only)
# EQP = equivalent only under a stated precondition the battery does not construct (race, cross-device, host state)
CLASS = {
 "MM01": ("EQ", "worktree-record prefix without trailing space", "git porcelain has no other line starting 'worktree'"),
 "MM03": ("NE", "prune nonzero rc not reported: a failed prune is read as zero prunable", "stdout DRIFT rows differ (s_prune_rc_nonzero)"),
 "MM04": ("NE", "blank/whitespace stderr lines counted as prunable candidates", "rc and stdout differ (s_prune_whitespace_line)"),
 "MM05": ("NE", "prune timeout reported under the list-timeout class string", "stdout class differs (s_prune_hangs)"),
 "MM06": ("NE", "prune TimeoutExpired not caught: the run crashes instead of reporting UNREACHABLE", "traceback vs DRIFT row (s_prune_hangs)"),
 "MM09": ("EQ", "success path returns \"\" instead of None for the error slot", "`if error:` treats \"\" and None alike"),
 "MM10": ("NE", "worktree-list output decoded strictly: non-UTF-8 path crashes the run", "rc 0 vs traceback rc 1 (s_list_output_invalid_utf8)"),
 "MD01": ("NE", "root listing unsorted: --json drift array follows filesystem order", "--json document differs (s_json_many_unrecorded); fs-order dependent"),
 "MD02": ("EQ", "child 'is a directory' guard dropped", "a regular-file child has no .git dir/file, so the .git test already rejects it"),
 "MD04": ("NE", "root basename appended instead of inserted: --json drift array order changes", "--json document differs (s_json_root_repo_unrecorded_child)"),
 "MD05": ("NE", "listing OSError swallowed: NameError crash instead of an empty discovery", "stdout and traceback differ (s_unreadable_root)"),
 "MD06": ("EQ", "root basename without rstrip('/')", "root is os.path.abspath()'d, which already strips a trailing slash"),
 "MD07": ("EQP", "nameless-root fallback 'root' dropped", "reachable only for --root / with a /.git directory; host has no /.git"),
 "MD10": ("NE", "root with a .git FILE also contributes its basename to discovery (duplicate measurement)", "stdout differs (s_root_gitfile_child_same_name)"),
 "MR02": ("NE", "root self-name branch no longer requires --root to hold a .git: a non-repo root is measured", "stdout differs (s_root_basename_row_other)"),
 "MR04": ("EQ", "root self-name comparison without rstrip('/')", "root is abspath()'d before repo_path() is called"),
 "MR05": ("NE", "root self-name branch accepts a .git FILE (linked worktree root) as its repository", "stdout differs (s_root_git_is_a_file_self_named)"),
 "MO01": ("NE", "relative-path guard removed; reachable only by --json / (empty component list): JSON-UNWRITABLE becomes an IndexError traceback", "rc 2 vs rc 1 + traceback (s_json_root_slash)"),
 "MO02": ("EQ", "'.' components kept in the walked path", "--json target is realpath()'d, so '.' never reaches the walk"),
 "MO03": ("EQP", "ancestor directory opened without O_NOFOLLOW", "--json target is realpath()'d; only a symlink swapped in between realpath and open reaches it (race, not constructed)"),
 "MO04": ("EQP", "leaf opened without O_NOFOLLOW", "--json target is realpath()'d, so the leaf is never a symlink; only a race reaches it (not constructed)"),
 "MO09": ("EQ", "root directory fd opened without O_DIRECTORY", "'/' is a directory; the flag is redundant"),
 "MO11": ("NE", "created --json file mode 0600 instead of 0644", "file mode differs (s_json_plain and five more)"),
 "MO12": ("EQ", "comment appended to the JSON-NOT-REGULAR refusal line", "comment only: no code change"),
 "MJ02": ("EQ", "JSON written without sort_keys", "format only: bytes differ, the parsed document is identical"),
 "MJ03": ("EQ", "JSON written with indent=None", "format only: bytes differ, the parsed document is identical"),
 "MJ04": ("EQ", "trailing newline after the JSON document dropped", "format only: bytes differ, the parsed document is identical"),
 "MJ07": ("EQ", "JSON-HARDLINKED message drops the link count", "label only: the REFUSAL class token is unchanged"),
 "MJ08": ("EQ", "--json containment loop compares commonpath to root instead of each base", "the root iteration (measured[0]) refuses every path the per-base test would refuse, with the same message"),
 "MJ10": ("EQP", "alias check compares inode only", "the two paths must sit on different devices with equal inode numbers; not constructed"),
 "MJ11": ("EQ", "path-equality alias check dropped (inode check remains)", "a same-path target has the same inode, so the inode check catches it"),
 "MJ12": ("EQ", "JSON-IS-RECORD message reworded", "label only: the REFUSAL class token is unchanged"),
 "MJ13": ("EQ", "JSON-INSIDE-MEASURED-TREE message reworded", "label only: the REFUSAL class token is unchanged"),
 "MA02": ("NE", "PRUNABLE-CHANGED emitted only when live exceeds the record", "a record that over-counts prunables gets no drift row (s_prunable_changed)"),
 "MA10": ("NE", "drift rows printed in record order, not sorted", "stdout order differs (s_two_drift_rows_reversed)"),
 "MA11": ("NE", "ABSENT row loses its recorded-figure detail", "stdout differs (s_absent)"),
 "MX04": ("EQ", "USAGE refusal message reworded", "label only: the REFUSAL USAGE class token is unchanged"),
 "MX07": ("EQ", "--json realpath without abspath", "realpath() of a relative path already resolves against the cwd"),
 "MX08": ("EQ", "record path compared without realpath in the alias check", "os.stat follows the symlink, so the inode check catches the alias"),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    scores = json.load(open(os.path.join(a.scratch, "scores.json")))
    shards = {}
    for path in sorted(glob.glob(os.path.join(a.scratch, "diff-shard-*.json"))):
        shards.update(json.load(open(path))["mutants"])
    rows = scores["rows"]
    lines = {}
    src = open(TOOL, encoding="utf-8").read().split("\n")
    for mid, fn, desc, old, new in MUTANTS:
        first = old.split("\n")[0]
        for i, line in enumerate(src, 1):
            if first in line and old in "\n".join(src[i - 1:i - 1 + len(old.split("\n"))]):
                lines[mid] = i
                break
    fns = ["measure", "discover", "repo_path", "open_nofollow", "json-writer", "drift-accounting", "exit-code-mapping"]
    tab = []
    tab.append("| function | mutants | killed | survived (non-equivalent / equivalent) |")
    tab.append("|---|---|---|---|")
    tot = [0, 0, 0, 0, 0]
    surv_lines = []
    kill_only_r42 = []
    for fn in fns:
        rs = [r for r in rows if r["function"] == fn]
        k = sum(1 for r in rs if r["killed_by"])
        sv = [r for r in rs if not r["killed_by"]]
        ne = sum(1 for r in sv if CLASS[r["id"]][0] == "NE")
        eq = len(sv) - ne
        tab.append("| %s | %d | %d | %d (%d / %d) |" % (fn, len(rs), k, len(sv), ne, eq))
        tot = [tot[0] + len(rs), tot[1] + k, tot[2] + len(sv), tot[3] + ne, tot[4] + eq]
        for r in sv:
            c = CLASS[r["id"]]
            surv_lines.append((fn, r["id"], lines[r["id"]], c[0], c[1], c[2]))
    tab.append("| **total** | %d | %d | %d (%d / %d) |" % tuple(tot))
    for r in rows:
        if r["killed_by"] == ["r42-drift-conditions.py"]:
            kill_only_r42.append((r["id"], lines[r["id"]]))
    out = []
    out.append("\n".join(tab))
    out.append("")
    out.append("SURVIVORS (function | id | line | class | behaviour | reason)")
    for fn, mid, ln, cl, beh, why in surv_lines:
        out.append("%s | %s | %d | %s | %s | %s" % (fn, mid, ln, cl, beh, why))
    out.append("")
    out.append("KILLED ONLY BY THE LANDED r42 FIXTURE: " + (", ".join("%s (line %d)" % x for x in kill_only_r42) or "none"))
    out.append("SURVIVE ALL EIGHT PRIOR FIXTURES (the r42 fixture may or may not kill them; ids listed): " + ", ".join(
        "%s" % r["id"] for r in rows if not any(k != "r42-drift-conditions.py" for k in r["killed_by"])))
    # oracle mutant counts
    ne_n = sum(1 for s in surv_lines if s[3] == "NE")
    out.append("")
    out.append("ORACLE: shards=%d survivors_evaluated=%d scenarios=%d" % (
        len(shards), len([k for k in shards if k in CLASS]),
        next(iter(shards.values()))["n_scenarios"] if shards else 0))
    out.append("NE=%d EQ=%d EQP=%d" % (ne_n, sum(1 for s in surv_lines if s[3] == "EQ"), sum(1 for s in surv_lines if s[3] == "EQP")))
    # cross-check: the oracle's semantic verdict agrees with the class
    mismatch = []
    for fn, mid, ln, cl, beh, why in surv_lines:
        sem = shards.get(mid, {}).get("sem", [])
        if (cl == "NE") != bool(sem):
            mismatch.append(mid)
    out.append("CLASS-vs-ORACLE mismatches: " + (",".join(mismatch) or "none"))
    text = "\n".join(out) + "\n"
    open(a.out, "w", encoding="utf-8").write(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
