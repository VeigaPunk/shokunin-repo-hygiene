#!/usr/bin/env python3
"""R42w2reviewer09 — disambiguation test for register rows whose token basename denotes
MORE THAN ONE committed path.

A basename that matches several tree paths is where a mis-resolution can hide: the counter's
derivation rule (R2/R4) picks one.  This script asks the content question directly:

  for the cell's OWN claim values (the tokens of the reference that holds the token),
  does the REGISTERED path carry them, and do its sibling candidates fail to?

  registered-carries-all && no-sibling-carries-all  -> the registered pick is CONFIRMED.
  no-path-carries-all                                -> the claim is in another artifact
                                                       (a sibling named in the same cell).

Read-only.
"""
import json
import os
import re
import subprocess

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
BASE = "bf618f6c5c09d302994871c94903abbea2deb60d"
TIP = "3105a63b23481fccf7df58e74d14a6681e0ea0c8"
SEAT = "/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-42/w2/R42w2reviewer09"
GIT_ENV = {"LC_ALL": "C", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
           "GIT_CONFIG_SYSTEM": os.devnull, "GIT_TERMINAL_PROMPT": "0"}
RE_EQ = re.compile(r"[A-Za-z_][A-Za-z0-9_.\-]*=(\d+)\b")
RE_FRAC = re.compile(r"(?<![\w.])(\d+)/(\d+)(?![\w.])")
RE_HEX = re.compile(r"(?<![0-9a-zA-Z])([0-9a-f]{7,64})(?![0-9a-zA-Z])")


def show(rev, path):
    p = subprocess.run(["git", "-C", LANE, "show", "%s:%s" % (rev, path)],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       env={**os.environ, **GIT_ENV}, check=False)
    return p.stdout.decode("utf-8", "replace") if p.returncode == 0 else None


def toks(text):
    out = []
    for m in RE_EQ.finditer(text):
        out.append(m.group(0))
    for m in RE_FRAC.finditer(text):
        out.append(m.group(0))
    for m in RE_HEX.finditer(text):
        out.append(m.group(1))
    seen = set()
    return [t for t in out if not (t in seen or seen.add(t))]


def main():
    D = json.load(open(os.path.join(SEAT, "final-decisions.json")))
    cache = {}

    def blob(rev, path):
        if (rev, path) not in cache:
            cache[(rev, path)] = show(rev, path)
        return cache[(rev, path)]

    amb = [r for r in D if len(r["same_basename_candidates"]) > 1]
    print("ambiguous-basename resolved rows: %d" % len(amb))
    out = []
    for r in amb:
        cands = r["same_basename_candidates"]
        claim = r["tokens_found_exact"] + [t for t, _v in r["tokens_found_by_shape"]]
        # the claim values of the cell that are NOT already confirmed in the registered file
        residual = [t for t in toks(r["cell_text"]) if t not in claim]
        print("=" * 100)
        print("L%-4s %-34s registered=%s  ctx_round=%s" % (r["line"], r["token"][:34], r["resolved_to"], r["round_context"]))
        print("   candidates (%d): %s" % (len(cands), cands))
        print("   cell claim values: %s" % (claim,))
        print("   cell residual (not in registered file): %s" % (residual,))
        scored = []
        for c in cands:
            b = (blob(BASE, c) or "") + "\n" + (blob(TIP, c) or "")
            hits = [t for t in toks(r["cell_text"]) if t in b]
            scored.append((len(hits), c, hits))
        for n, c, h in sorted(scored, reverse=True):
            mark = "  <= REGISTERED" if c == r["resolved_to"] else ""
            print("   %-92s carries %2d cell tokens %s%s" % (c, n, h[:6], mark))
        best = max(scored)[0]
        winners = [c for n, c, _h in scored if n == best]
        if r["resolved_to"] in winners and len(winners) == 1:
            verdict = "CONFIRMED-UNIQUE"
        elif r["resolved_to"] in winners:
            verdict = "CONFIRMED-TIED"
        else:
            verdict = "NOT-TOP"
        print("   VERDICT:", verdict, " best=%d" % best)
        out.append({"line": r["line"], "token": r["token"], "registered": r["resolved_to"],
                    "candidates": cands, "verdict": verdict, "best": best,
                    "winners": winners,
                    "scored": [{"path": c, "carries": h, "n": n} for n, c, h in scored]})
    with open(os.path.join(SEAT, "disambiguation.tsv"), "w") as h:
        h.write("line\ttoken\tregistered\tverdict\tcandidates\twinners\n")
        for o in out:
            h.write("%d\t%s\t%s\t%s\t%d\t%s\n" % (o["line"], o["token"], o["registered"],
                    o["verdict"], len(o["candidates"]), "|".join(o["winners"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
