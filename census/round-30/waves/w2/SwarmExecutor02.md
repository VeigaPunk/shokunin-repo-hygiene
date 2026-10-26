# SwarmExecutor02 — r30 w2 C2 rerun (falsification seat)

STATUS: PASS — every attack in the ticket ran against committed bytes and returned a verdict; PASS here means the attacks executed, not that C2 held.

## Status

STATUS: PASS — v1 and v2 counters were re-run at both named revisions from the frozen prereg blob and the A1 amendment, the landing gate was run directly at the C2 landing commit, and the base/tip selftests were diffed byte-for-byte; the three L1 readings in the ticket are confirmed, and two further measured facts break C2's text as frozen (landing-commit SUMMARY, and A1's `regress_full=same` literal).

## Evidence

All numbers below are from this run. Lane HEAD at run time `9dcd367655fc28ba73d679a0e2cadaff96d2bcb8`; frozen v1 counter extracted with `git show d4928ec...:census/round-30/c2-counter.py`; blob `fbaab0cd407ed69de8a0d8419ea4c1a091333c78` identical at `d4928ec` and at tip (`rev-parse` both sides), so the v1 bytes run are the frozen ones and were never amended in place.

1. v1 (frozen) `--root <lane> --base 9420341 --fleet-root /home/vgpnk/Projects/shokunin`:
   - `@68447af` rc=1: `SUMMARY reports=86 cne=0 dangling=1 other=7 fixture=ok redarm=ok regress=same rev=68447afef62e4761249af55a2467657f04046537`
   - `@9dcd367` rc=0: `SUMMARY reports=86 cne=0 dangling=0 other=0 fixture=ok redarm=ok regress=same rev=9dcd367655fc28ba73d679a0e2cadaff96d2bcb8`
   - independent tip clone as `--root` (live tree has `M SKILL.md`, `M corpus/QUALITY.md`, `?? corpus/lessons/round-30.md`): same rc=0 SUMMARY, `reports=86 cne=0 dangling=0 other=0`.
2. Direct gate `--root <lane> --rev 68447af... --round 29 --fleet-root /home/vgpnk/Projects/shokunin`, rc=1, stderr empty: one pointer finding and seven uncarried ones —
   `LG-DANGLING-PTR .ufo/waves/round-30/w1/deliver-c1-literal-history.tsv SCORECARD.md:322 cites path absent at 68447afef62e`, plus seven `LG-SEAT-UNCARRIED` on `census/round-29/waves/w1/*.md`; `SUMMARY findings=8 checked_reports=86 carry_heading=0`.
3. Pointer causality probe: in a scratch clone, `checkout 68447af`, add only `census/round-30/waves/w1/deliver-c1-literal-history.tsv` from tip, commit → `SUMMARY findings=7 checked_reports=86`, zero `LG-DANGLING-PTR`, seven uncarried. The gate bytes are byte-identical at `68447af` and tip (`git diff --stat 68447af..tip -- tools/souji-landing-gate.py` empty), so the landing-commit miss is data, not tool.
4. v2 (A1) at both revisions: `bind` ok only at tip (`reports=86 expected=86 ufo_md=0 cne=0 dangling=0`; at `68447af` `dangling=1 bind=fail`), `nocap=ok`, `ptrarm=ok` (flagged exactly the two absent paths, not the template and not `.ufo/waves/round-29/w1/SwarmConnector63.md`), `fixture=ok`, `redarm=ok`, and `regress_full=differs` at both revisions → rc=1 at tip.
5. Base/tip selftest diff (`--selftest`, 66 lines each, `diff -u` of raw bytes): exactly 2 differing lines, `pointer-without-wave-reports` and `no-wave-dir-exit2`; each differs only after `fleet=[] err=`, base `no .md reports under .ufo/waves/round-18/ at f822f82d...`, tip `no .md reports under .ufo/waves/round-18/ or census/round-18/waves/ at f822f82d...` (same for round-16). `tests/fixtures/r16-landing-gate.py` diff empty, `SUMMARY total=15 failed=0` both. Strip experiment on the two normalized outputs: as-is `False`, v2 regex `False`, whitespace-tolerant regex `True`.

## Findings

1. **C2 misses its frozen target at its own landing commit — real and singular.** `tools/souji-landing-gate.py:492` prints `"no .md reports under %s or %s at %s"` and maps wave pointers at `:916` `return "census/%s/waves%s" % (match.group(1), match.group(2) or "")`; the pointer is cited at `SCORECARD.md:322` (`git show 68447af...:SCORECARD.md`, line length 1300, offset 1206: `Literal provenance per row: `.ufo/waves/round-30/w1/deliver-c1-literal-history.tsv``). The capture blob does not exist at `68447af` (`git cat-file -e` rc=128) and does at tip; it was added by `aea0525`, four commits after the landing. Kill rule "any other SUMMARY at the C2 landing commit ... is a miss" is therefore met literally. This refutes "C2 met at its landing commit"; it does not impugn the capability, which the probe in Evidence 3 shows working once the bytes exist.
2. **A1's target is unmet at the tip as printed, by a defect inside A1's own instrument.** `census/round-30/c2-counter-v2.py:69` strips `re.sub(r"\terr=.*$", "", l)`; the selftest writes the tail as `fleet=[] err=...` with a space, so nothing is ever stripped and `regress_full=differs` is printed while the byte difference is exactly the two `err=` tails (Evidence 5) and `rc` plus the r16 fixture are identical. Semantic intent of REGRESS-FULL (no line changed except the reworded tail) is satisfied; the literal `SUMMARY-V2 ... regress_full=same` cannot be printed while the reworded message stands. Reported as an ATTACK on A1's instrument, not as a relaxation request.
3. **C2's landing-commit SUMMARY also fails on `other=7`.** Those are the seven r29 `LG-SEAT-UNCARRIED` STATUS lines that only the lesson carry `936efc8` removed; they are not attributable to C2, but the frozen SUMMARY at the landing commit differs in that field too, so the miss is not dangling-only.
4. **v1 does not enforce the literal 86.** `census/round-30/c2-counter.py:118`: `return 0 if reports > 0 and cnef == 0 and dangling == 0 and fok and rok and same else 1`. The target literal is met only because the observed count is 86 (read off the line at both revisions); the frozen instrument would exit 0 on a different positive count. A1's BIND binds 86 to the tree, so the value stands on measurement, not on v1's exit code.
5. **The tip pass is not a live-tree artifact.** An independent clone at tip reproduces the tip SUMMARY exactly, and the discovery/pointer code reads the tree at `--rev`, so the three uncommitted lane paths visible at run time do not contribute.

## Attack log

- v1 `dangling=1` at `68447af` — HOLDS (reproduced, rc=1).
- Which pointer — HOLDS, named: `SCORECARD.md:322` cites `.ufo/waves/round-30/w1/deliver-c1-literal-history.tsv`; capture added at `aea0525`; single-pointer probe clears it.
- v1 target met at tip — HOLDS (`reports=86 cne=0 dangling=0 other=0 fixture=ok redarm=ok regress=same`, rc=0; also from an independent clone).
- v2 `regress_full=differs` caused only by the ` err=` tail — HOLDS; exact mechanism located (tab-anchored regex vs space; two CASE lines; r16 identical).
- "C2 met at its landing commit" — BROKEN (v1 rc=1, `dangling=1 other=7`).
- "C2 meets A1's target at the tip" — BROKEN as printed (`regress_full=differs`, rc=1); DEFECT-NOT-FATAL with respect to tool behaviour, since no selftest verdict, id, path, exit or r16 line moved.
- v1 exit code as proof of the 86 literal — DEFECT-NOT-FATAL (`reports > 0`, cite Finding 4).
- tip SUMMARY dependence on the live working tree — HOLDS against (independent-clone reproduction identical).

## Deliveries

- `.ufo/waves/round-30/w2/deliver-c2-rerun.txt` — verbatim rerun receipts, pointer resolution table, selftest diff, strip experiment, verdicts.
- Tooling installed/updated: none (no pacman, no uv, no downloads; existing `python3`/`git` only).

Report: .ufo/waves/round-30/w2/SwarmExecutor02.md
