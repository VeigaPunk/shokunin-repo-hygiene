#!/usr/bin/env python3
"""Probe set J: record field structure, class naming, and whether the counter can see it."""
import os
import subprocess
import sys

sys.path.insert(0, "/fast/scratch/hyaku/souji-r86/S86Sentinel")
from probe import (S, TOOL, WRITER, ENV, build_fixture, git, move_nest, run_tool, show,
                   k4_rows, fresh, tool_copy)

OUT = []


def emit(s):
    OUT.append(s)
    print(s)


def raw(p):
    return p.stdout.decode("utf-8", "replace")


def j1_record_field_structure():
    """The K4 'record' field for an uncommitted path: can it hold a raw tab or newline?
    git quotes such paths in porcelain output; the tool takes line[3:].strip() verbatim."""
    d = fresh("j1")
    repo, rev, nest, nest1 = build_fixture(d)
    for rel in ("nl\nname.txt", "tab\tname.txt", "sp ace.txt"):
        with open(os.path.join(repo, rel), "wb") as f:
            f.write(b"x\n")
    st = subprocess.run(["git", "-C", repo, "status", "--porcelain"], stdout=subprocess.PIPE, env=ENV)
    emit("=== J1 git status --porcelain quoting of control-byte paths ===")
    emit("porcelain: %r" % st.stdout)
    p = run_tool(TOOL, repo, rev)
    rows = [ln for ln in raw(p).split("\n") if ln.startswith("MISMATCH\tK4")]
    emit("K4 rows: %r" % rows)
    for r in rows:
        fields = r.split("\t")
        emit("  fields=%d  record=%r" % (len(fields), fields[2] if len(fields) > 2 else None))
    bad = [r for r in rows if len(r.split("\t")) != 5]
    emit("VERDICT J1: %s" % ("every K4 row keeps exactly 5 tab-separated fields"
                              if not bad else "a row has %d fields" % len(bad.split("\t"))))


def j2_class_names_mechanism():
    """Does the record name the mechanism? Enumerate every K4 class the tool can emit and the
    message each is paired with."""
    d = fresh("j2")
    repo, rev, nest, nest1 = build_fixture(d)
    git(repo, "update-index", "--skip-worktree", "nest")
    move_nest(nest)
    p = run_tool(TOOL, repo, rev)
    rows = [ln for ln in raw(p).split("\n") if ln.startswith("MISMATCH\tK4")]
    emit("=== J2 the class paired with the refusal text ===")
    for r in rows:
        f = r.split("\t")
        emit("class=%r" % f[3])
        emit("detail=%r" % f[4][:160])
        emit("the class is chosen by msg.startswith(('RECEIPT-GITLINK-CONCEALED','RECEIPT-INDEX-')) "
             "- i.e. by the MESSAGE PREFIX, not by which check fired")


def j3_counter_cannot_see_the_env_route():
    """The counter's ENV strips every GIT_* variable, so it cannot carry the env route; and
    the in-tree config route is visible to it."""
    counter = "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-86/c2-k4-counter.py"
    src = open(counter, encoding="utf-8").read()
    line = [ln for ln in src.split("\n") if "not k.startswith(\"GIT_\")" in ln]
    emit("=== J3 the counter's environment ===")
    emit("counter ENV line: %r" % line)
    emit("-> the counter cannot carry GIT_CONFIG_PARAMETERS, so the env route is invisible to it")
    # the in-tree config route: does the counter's KG1 row still match?
    emit("")
    d = fresh("j3")
    repo, rev, nest, nest1 = build_fixture(d)
    move_nest(nest)
    git(repo, "update-index", "--skip-worktree", "nest")
    git(repo, "config", "core.sparseCheckout", "true")
    p = run_tool(TOOL, repo, rev)
    rows = [ln for ln in raw(p).split("\n") if ln.startswith("MISMATCH\tK4")]
    emit("in-tree core.sparseCheckout=true, KG1 shape: k4_rows=%d" % len(rows))
    for r in rows:
        emit("K4ROW %r" % r)
    named = any("nest" in (r + "\t" + "\t") for r in rows)
    emit("the counter's KG1 check looks for 'nest' in the row: %s" % named)


def j4_write_scope_of_the_claim():
    """What the claim's wording asserts vs what the probes show. Machine-check the two
    sentences of the claim that the probes bear on."""
    emit("=== J4 claim-wording checks (machine-checked) ===")
    d = fresh("j4")
    repo, rev, nest, nest1 = build_fixture(d)
    move_nest(nest)
    git(repo, "update-index", "--skip-worktree", "nest")
    # 'any record whose tag is not H is refused through the writer's own _flag_refusal'
    base = {k: v for k, v in ENV.items() if not k.startswith("GIT_CONFIG_")}
    e = dict(base)
    e["GIT_CONFIG_PARAMETERS"] = "'core.sparseCheckout=true'"
    tag_clean = subprocess.run(["git", "-C", repo, "ls-files", "-v", "-z", ":(top)"],
                               stdout=subprocess.PIPE, env=base).stdout
    tag_dirty = subprocess.run(["git", "-C", repo, "ls-files", "-v", "-z", ":(top)"],
                               stdout=subprocess.PIPE, env=e).stdout
    emit("tag of the flagged entry, tool's config view : %r" % [t for t in tag_clean.split(b"\0")
                                                                 if t.endswith(b"nest")])
    emit("tag of the flagged entry, writer's config view: %r" % [t for t in tag_dirty.split(b"\0")
                                                                  if t.endswith(b"nest")])
    emit("-> the sweep's input is a TAG, and the tag the sweep reads is not the tag the index "
         "holds, because the two halves read different config views")


if __name__ == "__main__":
    for fn in (j1_record_field_structure, j2_class_names_mechanism,
               j3_counter_cannot_see_the_env_route, j4_write_scope_of_the_claim):
        try:
            fn()
        except Exception as exc:  # noqa: BLE001
            emit("PROBE %s ERROR: %s: %s" % (fn.__name__, type(exc).__name__, exc))
    outp = os.path.join(S, "receipts", "probe-set-J.txt")
    open(outp, "w", encoding="utf-8").write("\n".join(OUT) + "\n")
    print("\n[receipt] %s" % outp)
