#!/usr/bin/env python3
"""souji r86 S86MutCounter reachability probe: for every mutant that SURVIVED both pinned populations, is the
edited clause DEAD (no input tells the mutant from the counter) or only UNEXERCISED by the populations?

Differentials against the pristine counter, in-process; no lane write (r85 S85MutCounter reach.py method, extended
with a judge-level fixture so the c7 branch is probed end to end rather than inferred):

  (a) judge level - a synthetic fixture repo (scratch `git init` under --work, toplevel asserted twice) holds the
      TARGET shapes only, every one with the same body whose sha256 is the item's `frozen` digest. A probe item is
      fabricated (the caller supplies `blob`), so the token is absent at the revision, the digest test passes and
      the basename/round tests pass: execution reaches the branch under test. Pairs whose pristine status is
      CAPTURED/MISMATCH short-circuit before the branch and are reported as NOT PROBES, never as differences.
      A difference is split into STATUS (what the harness compares; a kill channel) and WHY-only (message text,
      which the harness cannot see).
  (b) _owntree_ok - component-tail sweep to depth 3 (the r85 sweep extended past depth 2), which covers both
      halves of the short-shape guard independently of the judge chain's earlier exits.
  (c) c7 predicate equivalence - on the set of path pairs the own-tree branch ACCEPTS (exactly the set on which the
      c7 branch can fire, since both branches share the same `target[:round] == token[:round]` prefix test), does
      the filed c7 predicate `not _capture_ok(...)` agree with the mutant's predicate? Pure path logic, no git.
"""
import argparse
import hashlib
import importlib.util
import os
import subprocess
import sys

sys.dont_write_bytecode = True
LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
FLEET = "/home/vgpnk/Projects/shokunin"
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "LC_ALL": "C",
            "GIT_AUTHOR_NAME": "r86 probe", "GIT_AUTHOR_EMAIL": "probe@r86.invalid",
            "GIT_COMMITTER_NAME": "r86 probe", "GIT_COMMITTER_EMAIL": "probe@r86.invalid",
            "GIT_AUTHOR_DATE": "2026-11-07T00:00:00Z", "GIT_COMMITTER_DATE": "2026-11-07T00:00:00Z"})
BODY = b"r86 reach probe: one byte source for every target shape\n"
CENSUS = "census/round-84"
OWN = ".ufo/waves/round-32"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def git(repo, *args):
    if not repo or not os.path.isabs(repo):
        raise SystemExit(f"refusing git -C {repo!r}")
    p = subprocess.run(["git", "-C", repo, "-c", "core.hooksPath=/dev/null", *args],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV)
    if p.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} rc={p.returncode}: {p.stderr.decode()[:300]}")
    return p.stdout.decode().strip()


def all_tails(depth, comps):
    tails = [()]
    for k in range(1, depth + 1):
        tails += [t + (c,) for t in tails if len(t) == k - 1 for c in comps]
    return tails


def pairs():
    """(label, token, target). Every token basename is unique to its probe so no probe's token is present at the
    fixture revision as some other probe's target."""
    return [
        # --- the twelve shapes the r85 reach.py model used, renamed uniquely
        ("A1 short token -> capture under own round", f"{OWN}/XA1", f"{OWN}/waves/XA1"),
        ("A2 short token -> assimilation under own round", f"{OWN}/XA2", f"{OWN}/assimilation/XA2"),
        ("A3 short token -> decoy under own round", f"{OWN}/XA3", f"{OWN}/decoy/XA3"),
        ("A4 true own-tree move (deep token, w2)", f"{OWN}/a2w1/XA4", f"{OWN}/w2/XA4"),
        ("A5 own-tree move with an extra dir", f"{OWN}/a2w1/XA5", f"{OWN}/w2/sub/XA5"),
        ("A6 flat copy at the round root", f"{OWN}/a2w1/XA6", f"{OWN}/XA6"),
        ("B1 census capture (true, TF11 shape)", f"{CENSUS}/records/YB1", f"{CENSUS}/waves/YB1"),
        ("B2 census w1 under own round (NF-W shape)", f"{CENSUS}/records/YB2", f"{CENSUS}/w1/YB2"),
        ("B3 census capture, remainder not a suffix", f"{CENSUS}/records/YB3", f"{CENSUS}/waves/sub/YB3"),
        ("B4 census records/copy (NF-R shape)", f"{CENSUS}/records/YB4", f"{CENSUS}/records/copy/YB4"),
        ("B5 one-component census token -> capture (NF-Y shape)", f"{CENSUS}/YB5", f"{CENSUS}/waves/YB5"),
        ("B6 one-component census token -> records", f"{CENSUS}/YB6", f"{CENSUS}/records/YB6"),
        # --- census shapes that separate the c7 branch's own prefixes from the own-tree branch
        ("C1 capture of a one-component token (B5 twin)", f"{CENSUS}/YC1", f"{CENSUS}/waves/YC1"),
        ("C2 capture remainder not a suffix (B3 twin)", f"{CENSUS}/records/YC2", f"{CENSUS}/waves/sub/YC2"),
        ("C3 partial capture: remainder is a suffix (middle dir dropped)", f"{CENSUS}/records/sub/YC3",
         f"{CENSUS}/waves/YC3"),
        ("C4 partial capture: remainder keeps its middle dir", f"{CENSUS}/records/sub/YC4",
         f"{CENSUS}/waves/sub/YC4"),
        ("C5 capture whose remainder repeats the token's own dir", f"{CENSUS}/records/YC5",
         f"{CENSUS}/waves/records/YC5"),
        ("C6 capture remainder is neither suffix nor prefix", f"{CENSUS}/records/YC6",
         f"{CENSUS}/waves/other/YC6"),
        ("C7 w1 with an extra dir", f"{CENSUS}/records/YC7", f"{CENSUS}/w1/sub/YC7"),
        ("C8 assimilation under own round", f"{CENSUS}/records/YC8", f"{CENSUS}/assimilation/YC8"),
        ("C9 one-component token -> w1", f"{CENSUS}/YC9", f"{CENSUS}/w1/YC9"),
        ("C10 one-component token -> records", f"{CENSUS}/YC10", f"{CENSUS}/records/YC10"),
        # --- own-tree shapes r85's sweep found interesting
        ("U1 own-tree move replacing the token's dir with w1", f"{OWN}/decoy/ZU1", f"{OWN}/w1/decoy/ZU1"),
        ("U2 own-tree move from records/ into w2", f"{OWN}/records/ZU2", f"{OWN}/w2/ZU2"),
        ("U3 wave dir replaced (w2 -> w1)", f"{OWN}/w2/ZU3", f"{OWN}/w1/ZU3"),
        ("U4 wave dir replaced, deeper token", f"{OWN}/w2/sub/ZU4", f"{OWN}/w1/sub/ZU4"),
        ("U5 short token -> w2 (no capture)", f"{OWN}/XU5", f"{OWN}/w2/XU5"),
        ("U6 short token -> waves (capture)", f"{OWN}/XU6", f"{OWN}/waves/XU6"),
        ("U7 waves/ token -> decoy", f"{OWN}/waves/XU7", f"{OWN}/decoy/XU7"),
        ("U8 deep token -> record-keeping dir with matching tail", f"{OWN}/a2w1/deep/XU8",
         f"{OWN}/w2/deep/XU8"),
    ]


def build(work):
    repo = os.path.join(work, "reach-fixture")
    os.makedirs(repo, exist_ok=True)
    git(repo, "init", "-q", "-b", "main")
    top = git(repo, "rev-parse", "--show-toplevel")
    if os.path.realpath(top) != os.path.realpath(repo):
        raise SystemExit(f"reach fixture toplevel {top} is not {repo}")
    targets = sorted({t for _l, _k, t in pairs()})
    tokens = {k for _l, k, _t in pairs()}
    overlap = sorted(tokens & set(targets))
    if overlap:
        raise SystemExit(f"probe token is also a target: {overlap}")
    for t in targets:
        p = os.path.join(repo, t)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "wb") as f:
            f.write(BODY)
    git(repo, "add", "-f", "--", ".")
    git(repo, "commit", "-q", "--no-verify", "-m", "r86 reach probe shapes")
    rev = git(repo, "rev-parse", "HEAD")
    for t in targets:
        row = git(repo, "ls-tree", rev, "--", t)
        mode = row.split(" ")[0] if row else ""
        if mode not in ("100644", "100755"):
            raise SystemExit(f"probe target {t} is not a regular blob (mode {mode!r})")
    if os.path.realpath(git(repo, "rev-parse", "--show-toplevel")) != os.path.realpath(repo):
        raise SystemExit("reach fixture toplevel drifted")
    return repo, rev


def judge_diff(pristine, mut, repo, rev):
    frozen = "f:" + hashlib.sha256(BODY).hexdigest()
    rows = []
    for label, token, target in pairs():
        item = ("ZZ", "LOG.md", "1", token, frozen)
        blob = ["# pointer " + token + " moved\n"]
        pa = pristine.judge(repo, rev, FLEET, item, ("MOVED", target), blob)
        ma = mut.judge(repo, rev, FLEET, item, ("MOVED", target), blob)
        if pa[0] in ("CAPTURED", "MISMATCH"):
            continue  # short-circuits before the branch: not a probe of any MOVED clause
        kind = "" if pa == ma else ("STATUS" if pa[0] != ma[0] else "WHY-only")
        rows.append((label, token, target, pa, ma, kind))
    return rows


def owntree_sweep(pristine, mut, depth=3, comps=("X", "w1", "w2", "waves", "records", "a2w1")):
    tails = all_tails(depth, comps)
    n, diff = 0, []
    for tok_tail in tails:
        token = f"{OWN}/" + "/".join(tok_tail)
        kr = pristine.ROUND.search(token)
        for tgt_tail in tails:
            target = f"{OWN}/" + "/".join(tgt_tail)
            tr = pristine.ROUND.search(target)
            n += 1
            if pristine._owntree_ok(token, kr, target, tr) != mut._owntree_ok(token, kr, target, tr):
                diff.append((token, target))
    return n, diff


def c7_equiv(pristine, mut, depth=3, comps=("X", "w1", "w2", "waves", "records", "sub")):
    """On the pairs the own-tree branch accepts (the only pairs on which the c7 branch can fire), does the mutant's
    c7 predicate agree with the filed `not _capture_ok(...)`? Path logic only."""
    tails = all_tails(depth, comps)
    n_reach = 0
    bad = []
    for tok_tail in tails:
        token = f"{CENSUS}/" + "/".join(tok_tail)
        kr = pristine.ROUND.search(token)
        for tgt_tail in tails:
            target = f"{CENSUS}/" + "/".join(tgt_tail)
            tr = pristine.ROUND.search(target)
            if target[:tr.start(0)] != token[:kr.start(0)]:
                continue
            if not pristine._owntree_ok(token, kr, target, tr):
                continue  # the own-tree branch refuses first: c7 cannot fire
            if not pristine._capture_ok(token, kr, target, tr):
                n_reach += 1
            p_fire = not pristine._capture_ok(token, kr, target, tr)
            m_fire = not mut.CAPTURE.match(target[tr.end(0):].rstrip("/"))
            if p_fire != m_fire:
                bad.append((token, target))
    return n_reach, bad


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--mutants-dir", required=True)
    ap.add_argument("--pristine", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--out", required=True)
    ns = ap.parse_args(argv)
    if os.path.realpath(ns.work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
        print("REACH-FATAL: --work under /tmp", file=sys.stderr)
        return 2
    os.makedirs(ns.work, exist_ok=True)
    pristine = load("counter_pristine", os.path.abspath(ns.pristine))
    repo, rev = build(os.path.abspath(ns.work))
    lines = [f"# pristine {os.path.abspath(ns.pristine)}",
             f"# probe fixture {repo} rev={rev} (scratch; toplevel asserted twice; target blobs only)"]
    for name in sorted(n for n in os.listdir(ns.mutants_dir) if n.endswith(".py")):
        mut = load("mut_" + name.replace("-", "_")[:-3], os.path.join(ns.mutants_dir, name))
        jd = judge_diff(pristine, mut, repo, rev)
        nd, od = owntree_sweep(pristine, mut)
        pd = [x for x in jd if x[5]]
        status_diff = [x for x in jd if x[5] == "STATUS"]
        lines.append(f"## {name}")
        lines.append(f"  judge matrix: probes={len(jd)} status_differing={len(status_diff)} "
                     f"why_only_differing={len(pd) - len(status_diff)}")
        for label, _tok, _tgt, ps, ms, kind in jd:
            mark = {"": "same", "STATUS": "DIFF ", "WHY-only": "why  "}[kind]
            lines.append(f"    {mark} {label}: pristine={ps} mutant={ms}")
        lines.append(f"  _owntree_ok sweep: pairs={nd} differing={len(od)}")
        for token, target in od[:10]:
            lines.append(f"    DIFF {target} ({token})")
        if name.startswith("x3-"):
            n_reach, bad = c7_equiv(pristine, mut)
            lines.append(f"  c7 predicate equivalence (own-tree-accepted census pairs): reachable_not_capture="
                         f"{n_reach} predicate_differing={len(bad)}")
            for token, target in bad[:10]:
                lines.append(f"    DIFF {target} ({token})")
        verdict = ("REACHABLE (judge status)" if status_diff else
                   "REACHABLE (function level only)" if od else
                   "REACHABLE (message text only)" if pd else "DEAD (no input differs)")
        lines.append(f"  verdict={verdict}")
    text = "\n".join(lines) + "\n"
    with open(ns.out, "w", encoding="utf-8") as f:
        f.write(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
