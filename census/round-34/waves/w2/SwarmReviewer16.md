# SwarmReviewer16 — seat findings (AttackE18, round-34 w2)

Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`; base `9c76c7222a8a…`, list-rev `2b0171e2071f…`. Read-only; full detail in `AttackE18.md` alongside.

## Status

**W1's E18 finding CONFIRMED (reproduced); correction valid and unique; landed bytes pass at new tip adac8bb.**

## Evidence (executed by this seat)

- Base do-nothing arm: `ITEM E18 MISMATCH original rc=0 expect_exit=0 predicate fails last=selftest=PASS ids=7/7` — exit **1** (`c1-counter.py:397`).
- Cause bracket: parent `679e2d02f46e` → `ids=5/5` rc=0 (fixture sha `b6bf5205…` == r24 receipt pin `census/round-24/records/r13-recheck-receipt.tsv`); cause `728b2ce71acb` → `ids=7/7` rc=0 with the two new probe cases; 0 digit-bearing lines after the selftest line; tool sha unchanged; `778747e` ancestor of parent; `728b2ce` touches `tests/fixtures/r13-repo-structure.sh` (1 of 181 paths) and is an ancestor of list-rev.
- Q76: no correction binds `SCORECARD.md:71` anywhere in the base tree; SECTION absent at base; counter has no runtime carry (restatements keyed by item id under SECTION only, `c1-counter.py:93-107,245-247`), and `:155` is a Capabilities-section row outside the frozen surface — K04 cannot carry E18.
- Tip `adac8bb` (landed during probe) appends the E18 restatement exactly as W1 proposed → `ITEM E18 AGREE restated … last=selftest=PASS ids=7/7`, exit 0.

## Findings

1. CONFIRMED (reproduced): stale cell at base; cause `728b2ce` valid; restated statement forced by A1(c) equality (`c1-counter.py:312`).
2. W1 report defect (reproduced): "Exit 0" claim false — counter exits 1 on any mismatch.
3. W1 report defect (cosmetic): quoted `TMPDIR=<fresh>` env inconsistent with quoted `/var/tmp` fixture_repo paths (fixture honors TMPDIR when set, `tests/fixtures/r13-repo-structure.sh:189`).
4. No missed honest route: Q76 carry machine-refuted; `6ed10a7`/`98e5203` causes BAD-CAUSE; RESULTS:-form vacuous (no `RESULT ` lines; `:0` is the frozen junk control); argv correction pointless/A1(b)-risky.
5. Timing note: W1's L1 "heading absent at tip" was true at read time (tip `51acb5f`); superseded by `adac8bb`.

Scratch: `/fast/scratch/hyaku/souji-r34/E18/` (12K retained after trimming a transient 148M clone). No lane file modified; no frozen artifact altered.
