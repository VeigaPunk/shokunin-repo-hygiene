#!/usr/bin/env python3
"""SwarmReviewer13 r30-w2: counter-examples against the C2 landing-gate diff.

Runs tools/souji-landing-gate.py at C2 (68447af) and at base (9420341) over
synthetic worlds that probe the named attack surfaces:
  shadow      partial wave-dir force-add shadows capture reports (precedence)
  renamed     pointer to a wave .gitignore whose capture name is .captured
  excluded    pointer to a wave path the capture recorded in excluded.tsv
  cutmistake  hand-written mistaken pointer `census/round-` (round- cut rule)
  pcts        Python-style template token `census/round-%d/waves/`
  exemptstale exemption row for a pointer the capture now resolves
  clean       control (capture-only, no findings)
"""
import importlib.util
import os
import subprocess
import sys

D = os.path.dirname(os.path.abspath(__file__))
C2_GATE = os.path.join(D, "c", "tools", "souji-landing-gate.py")
BASE_GATE = os.path.join(D, "base-gate.py")

spec = importlib.util.spec_from_file_location(
    "r30fix", os.path.join(D, "c", "tests", "fixtures", "r30-landing-gate-discovery.py")
)
fx = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fx)

LESSON_HEAD = "# Round 30 lesson\n\nadmitted: false\n"
CLEAN = "# Seat\n\nSTATUS: ok - clean.\n"
FAILTXT = "# Hidden\n\nSTATUS: FAIL - hidden uncarried failure.\n"


def build(base, env, name):
    repo = fx.Repo(base, name, env)
    repo.write("SKILL.md", fx.SKILL)
    extra = []
    if name == "shadow":
        repo.write(".ufo/waves/round-30/w1/Only.md", CLEAN)
        repo.write("census/round-30/waves/w1/Only.md", CLEAN)
        repo.write("census/round-30/waves/w2/Hidden.md", FAILTXT)
    elif name == "renamed":
        extra.append("Ignored-rules receipt: `.ufo/waves/round-30/.gitignore`.")
        repo.write("census/round-30/waves/.gitignore.captured", "junk.log\n")
        repo.write(
            "census/round-30/waves/renames.tsv",
            "# original\tstored\n.gitignore\t.gitignore.captured\n",
        )
        repo.write("census/round-30/waves/w1/Seat.md", CLEAN)
    elif name == "excluded":
        extra.append("Ignored receipt: `.ufo/waves/round-30/junk.log`.")
        repo.write(
            "census/round-30/waves/excluded.tsv",
            "# path\tsha256\treason\njunk.log\t%s\tignored\n" % ("a" * 64),
        )
        repo.write("census/round-30/waves/w1/Seat.md", CLEAN)
    elif name == "cutmistake":
        extra.append("Mistaken citation: see census/round- for the wave receipt.")
        repo.write("census/round-30/waves/w1/Seat.md", CLEAN)
    elif name == "pcts":
        extra.append("Template in prose: `census/round-%d/waves/`.")
        repo.write("census/round-30/waves/w1/Seat.md", CLEAN)
    elif name == "exemptstale":
        extra.append("Capture-mapped pointer: `.ufo/waves/round-30/w1/X.md`.")
        repo.write("census/round-30/waves/w1/X.md", CLEAN)
        repo.write("census/round-30/waves/w1/Seat.md", CLEAN)
        repo.write(
            "corpus/pointer-exemptions.tsv",
            ".ufo/waves/round-30/w1/X.md\tsynthetic pre-capture exemption\n",
        )
    elif name == "clean":
        repo.write("census/round-30/waves/w1/Seat.md", CLEAN)
    else:
        raise RuntimeError(name)
    if extra:
        repo.write(
            "corpus/lessons/round-30.md",
            LESSON_HEAD + "\n" + "\n".join(extra) + "\n",
        )
    return repo.path, repo.commit("world " + name)


def main():
    scratch = os.path.join(D, "probe-scratch")
    os.makedirs(os.path.join(scratch, "home"), exist_ok=True)
    env = fx.git_env(scratch)
    worlds = {}
    for name in ("shadow", "renamed", "excluded", "cutmistake", "pcts",
                 "exemptstale", "clean"):
        worlds[name] = build(os.path.join(scratch, "repos"), env, name)

    for label, tool in (("C2", C2_GATE), ("BASE", BASE_GATE)):
        print("=== gate %s (%s)" % (label, tool))
        for name, (root, rev) in sorted(worlds.items()):
            r = fx.run_gate(tool, root, rev, 30)
            print("--- world %s: rc=%d reports=%s status=%s" % (
                name, r.rc, r.summary("checked_reports"),
                r.summary("status_lines")))
            for row in r.rows:
                if row.startswith("LG-"):
                    print("    " + row.replace("\t", " | "))
            if r.cne:
                print("    COULD-NOT-EVALUATE (stderr seen)")
            if not any(row.startswith("LG-") for row in r.rows) and not r.cne:
                print("    (no findings)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
