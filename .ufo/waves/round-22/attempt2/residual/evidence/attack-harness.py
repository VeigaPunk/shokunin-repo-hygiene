#!/usr/bin/env python3
"""Residual attack harness for souji round-22 C2 (souji-gate-check.py).

Builds an isolated /var/tmp root and runs one attack per invocation so the
counts line attributes to exactly one mutation. Read-only w.r.t. the lane.
"""
import hashlib
import os
import shutil
import subprocess

TOOL = "/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-gate-check.py"
BASE = "/var/tmp/regc-gatecheck/base"
GOOD_SNAP = "Option --no-copy: do not copy, just move. RENAME_NOREPLACE do not overwrite newpath.\n"
Y_SNAP = "The section below states the rule. Do not overwrite newpath.\n"
IDS = ["S114", "S123", "S124", "S126", "S131", "S133", "S138", "S118"]
REG = IDS + ["S109"]


def w(rel, text):
    path = os.path.join(BASE, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    return path


def entry(front="", gate_body=None, quote='RENAME_NOREPLACE do not overwrite newpath',
          snap="census/sources/x.txt", locator="\u00a7 DESCRIPTION flags", reason="fixture grounds the claim"):
    if gate_body is None:
        gate_body = (
            "## Gate\n\n"
            "url: https://example.invalid/doc\n"
            "snapshot: %s\n"
            "opened: 2026-10-25\n\n"
            '- ADMIT: "%s" \u2014 %s \u2014 reason: %s \u2014 snapshot: %s\n'
            "- REJECT: staged entry alpha \u2014 reason: quote cited against the wrong artifact\n"
            % (snap, quote, locator, reason, snap)
        )
    return (front + "verified-at: 2026-10-25\n\n# fixture entry\n\n" + gate_body + "\n")


def setup():
    if os.path.isdir(BASE):
        shutil.rmtree(BASE)
    os.makedirs(BASE)
    reg = "| id | source |\n|---|---|\n" + "".join("| %s | row |\n" % i for i in REG)
    w("corpus/SOURCES.md", reg)
    w("census/sources/x.txt", GOOD_SNAP)
    w("census/sources/section-3.txt", GOOD_SNAP)
    w("census/sources/y.txt", Y_SNAP)
    w("census/slice", "".join(" %s   `payload-absent` \n" % i for i in IDS))
    w("census/verdicts.tsv", "".join("%s\tpresent\tevidence for %s\n" % (i, i) for i in IDS))
    FRONT = "source: S109 \u2014 example\n"
    w("entries/good.md", entry(FRONT))
    w("census/outside.txt", GOOD_SNAP)
    os.symlink("../outside.txt", os.path.join(BASE, "census/sources/link-rel.txt"))
    os.symlink(os.path.join(BASE, "census/outside.txt"),
               os.path.join(BASE, "census/sources/link-abs.txt"))

    w("entries/a1-indented-source.md",
      entry(FRONT + "   - source: S999 \u2014 not in the registry\n"))
    w("entries/a2-reject-no-reason.md", entry(
        FRONT,
        gate_body=(
            "## Gate\n\nurl: https://example.invalid/doc\nsnapshot: census/sources/x.txt\n"
            "opened: 2026-10-25\n\n"
            '- ADMIT: "RENAME_NOREPLACE do not overwrite newpath" \u2014 \u00a7 DESCRIPTION flags '
            "\u2014 reason: fixture grounds the claim \u2014 snapshot: census/sources/x.txt\n"
            "- REJECT: staged entry alpha \u2014 quote cited against the wrong artifact, no reason field\n"
        )))
    w("entries/a2b-empty-reason.md", entry(
        FRONT,
        gate_body=(
            "## Gate\n\nurl: https://example.invalid/doc\nsnapshot: census/sources/x.txt\n"
            "opened: 2026-10-25\n\n"
            '- ADMIT: "RENAME_NOREPLACE do not overwrite newpath" \u2014 \u00a7 DESCRIPTION flags '
            "\u2014 reason: \u2014 snapshot: census/sources/x.txt\n"
            "- REJECT: staged entry alpha \u2014 reason: quote cited against the wrong artifact\n"
        )))
    w("entries/a3-symlink-rel.md", entry(FRONT, snap="census/sources/link-rel.txt"))
    w("entries/a3-symlink-abs.md", entry(FRONT, snap="census/sources/link-abs.txt"))
    w("entries/a4-locator-filename.md",
      entry(FRONT, snap="census/sources/section-3.txt", locator=""))
    w("entries/a4b-locator-backtick.md", entry(
        FRONT,
        gate_body=(
            "## Gate\n\nurl: https://example.invalid/doc\nsnapshot: census/sources/section-3.txt\n"
            "opened: 2026-10-25\n\n"
            '- ADMIT: "RENAME_NOREPLACE do not overwrite newpath" \u2014 see '
            "`census/sources/section-3.txt` \u2014 reason: fixture grounds the claim "
            "\u2014 snapshot: census/sources/section-3.txt\n"
            "- REJECT: staged entry alpha \u2014 reason: quote cited against the wrong artifact\n"
        )))
    w("entries/a4c-locator-inside-quote.md", entry(
        FRONT, snap="census/sources/y.txt", locator="",
        quote="The section below states the rule."))
    staged = w("pkg/staged-entry.md",
               "source: S109 \u2014 example\n\n# synthetic staged entry (no Gate)\n\nbody\n")
    shutil.copyfile(staged, os.path.join(BASE, "entries/a5-staged-copy.md"))
    sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()
    print("A5 sha staged=%s copy=%s equal=%s" % (
        sha(staged)[:16], sha(os.path.join(BASE, "entries/a5-staged-copy.md"))[:16],
        sha(staged) == sha(os.path.join(BASE, "entries/a5-staged-copy.md"))))
    w("census/verdicts-missing-row.tsv",
      "".join("%s\tpresent\tevidence for %s\n" % (i, i) for i in IDS if i != "S118"))
    w("census/slice-two-ids", " S114 S123   `payload-absent` \n S124   `payload-absent` \n")
    w("census/verdicts-two-ids.tsv", "S114\tpresent\tevidence\nS124\tpresent\tevidence\n")
    w("census/verdicts-badclass.tsv",
      "".join("%s\t%s\tevidence\n" % (i, "bogus" if i == "S114" else "present") for i in IDS))
    w("census/verdicts-dup.tsv",
      "".join("%s\tpresent\tevidence\n" % i for i in IDS) + "S114\tpresent\tsecond row\n")
    print("A7 base has .git: %s (snapshot 'committed' is unenforceable here)"
          % os.path.exists(os.path.join(BASE, ".git")))


def run(name, entry_rel, verdicts="census/verdicts.tsv", slice_rel="census/slice"):
    cmd = ["python3", "-B", TOOL, "--root", BASE, "--round-date", "2026-10-25",
           "--entries", entry_rel, "--snapshot-dir", "census/sources",
           "--slice", slice_rel, "--slice-verdicts", verdicts]
    p = subprocess.run(cmd, capture_output=True, text=True)
    print("\n=== %s" % name)
    print("CMD %s" % " ".join(cmd))
    print("RC %d" % p.returncode)
    for line in (p.stdout + p.stderr).strip().splitlines():
        print("OUT %s" % line)
    return p.returncode, p.stdout


def main():
    setup()
    run("BASELINE good entry (fixture root has no git repo)", "entries/good.md")
    run("A1 indented - source: S999", "entries/a1-indented-source.md")
    run("A2 REJECT without reason:", "entries/a2-reject-no-reason.md")
    run("A2b reason: empty payload", "entries/a2b-empty-reason.md")
    run("A3 symlink inside snapshot dir -> outside (relative)", "entries/a3-symlink-rel.md")
    run("A3 symlink inside snapshot dir -> outside (absolute)", "entries/a3-symlink-abs.md")
    run("A4 locator only from snapshot filename", "entries/a4-locator-filename.md")
    run("A4b locator only from backticked snapshot filename", "entries/a4b-locator-backtick.md")
    run("A4c locator only inside the quoted span", "entries/a4c-locator-inside-quote.md")
    run("A5 byte-exact staged copy without Gate", "entries/a5-staged-copy.md")
    run("A6 missing verdict row", "entries/good.md", verdicts="census/verdicts-missing-row.tsv")
    run("A6b two ids on one slice line, verdict for first only", "entries/good.md",
        verdicts="census/verdicts-two-ids.tsv", slice_rel="census/slice-two-ids")
    run("A6c bad class", "entries/good.md", verdicts="census/verdicts-badclass.tsv")
    run("A6d duplicate verdict row", "entries/good.md", verdicts="census/verdicts-dup.tsv")


if __name__ == "__main__":
    main()
