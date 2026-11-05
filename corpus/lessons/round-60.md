# Round 60 — freeze-record substance binding and atomic receipt writing

Two claims. C1 calibration (lowest legacy axis 7; claim type: capability acquisition): the freeze
checker gains an opt-in `--substance` arm that binds a claim's `Control:` receipt to the declared
`Counter:` path, that counter's committed blob digest at the freeze commit, a full-40 revision that is
a strict ancestor of the freeze commit, and a `command=` naming the counter. C2 operability:
`tools/souji-receipt-write.py` writes a receipt through a same-directory temp file, `fsync` and
`link(2)`, refusing an existing output, a racing creator, a dirty worktree, an over-bound capture, a
short or non-commit revision, an absent instrument and an out-of-root target.
Base `1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4`; controls `3b5525099356e15ff9d17b7fbd2835c2d3512eee`;
freeze `2670e96af1b81c7aa793acc34d40361b4beecff8`; predicate `census/round-60/preregistration.txt`.
This round does not re-declare the rejected r56/r57 visibility-parser claims, the r58 receipt-gate
claim or the r59 classification repair.

## Gate

Sources opened 2026-11-04 by the L1 (`curl -sSL`, HTTP 200; captures and digests under
`census/round-60/sources/`; quote word counts by `wc -w` on the captured text).

- **S288 admit** — Python 3.15.2 documentation, `os.replace`:
  https://docs.python.org/3/library/os.html#os.replace — 791358 bytes, sha256
  `ece1ab71f281f72bbaaa318f6e376adeceed40466f086861eb1edfbb79f68079`. Located quote (14 words):
  `If successful, the renaming will be an atomic operation (this is a POSIX requirement).`
- **S289 reject** — same page, different scope: the inference that a temp file under `$TMPDIR` can be
  renamed onto a receipt path on another device. The page says `The operation may fail on some Unix
  flavors if src and dst are on different filesystems.` Flip: place the temp beside the output. The
  page is not rejected; the inference is.
- **Re-opened, cells unchanged**: S110 `rename(2)` (man-pages 6.19, sha256 `8772946a809a0db5…`), S213
  POSIX `rename()`, S214 POSIX `fsync()` (sha256 `f0a986d21500222e…`) — the three primitives F4's
  `origin-record-exclusivity-r28.md` already holds — and S251 `git merge-base --is-ancestor`
  (sha256 `46d106b777754f7e…`), the strict-descendant contract of
  `git-strict-descendant-relation-r40.md`. This round applies held knowledge in a tool; it claims no
  new file-system ground.
- No package adoption: `/home/vgpnk/Projects/shokuknow/merge/souji/` was checked but not adopted (the
  r46 mass-id-drift hold is retained). `considerthese/` is absent from the lane root.
- Rows added: A1 (S288) / B0 / C0; one rejection (S289). Registry 211 → 213 rows.

## Mistakes

| class | evidence | captured-by | fix |
|---|---|---|---|
| vacuous: a freeze grammar that binds labels, not bytes | `corpus/lessons/round-59.md` `## Additional mistakes`; the five forgery states the arm now refuses; `census/round-60/controls/c1-do-nothing.txt` (base accepts all five) | Q99 (label grammar) and the r59 critic F1/F2 | `CONTROL-INSTRUMENT-*` / `CONTROL-REV-*` / `CONTROL-COMMAND-*` classes, with the five forgeries as frozen matrix rows and the round's own record scoring `findings=0` |
| reference-drift: the round's own prompt carried a base value the instrument had already refuted (C2 "base 3/8" while the fixture measures 4/8) | `census/round-60/controls/c2-do-nothing.txt` `pass=4`; critic S60CriticRound finding 1; `S60ExecControls/do-nothing-c2.txt` `pass=4` | the frozen `Target:`/`Kill:` rule (a claim is judged on the counter, not on the prose that described it) | the prereg names `pass=4`; the 3/8 figure stays in the wave spec as filed and is reported, not rewritten |
| concurrency: an existence check followed by `os.replace` is a TOCTOU that destroys a racing creator's bytes | reviewer S60ReviewerRecorder a1/a2 on the delivered candidate (`raced_bytes_lost=True`) | the writer's own publish step | publish with `os.link` (EEXIST on a lost race) before the freeze; the attack now returns rc 2 with the racer's file intact |
| scope: a receipt target that follows a symlink out of the lane | reviewer S60ReviewerRecorder b1 (`wrote_outside_lane=True`) | the writer's out-path handling | resolve the out directory and refuse when it leaves `--root` unless `--allow-outside`; b1 now returns rc 2 |

## Named limits

- **C1 binds bytes, a graph relation and an argv token — never execution.** A truthful forgery with the
  real counter digest and a real ancestor revision passes. `--is-ancestor` is history, not wall-clock
  chronology. A tag OID that peels to an ancestor is still accepted as the control's `rev=`.
- **C1's matrix pins each case's expected verdict, not its finding class.** The class names in the entry
  and in this lesson come from the arm's own output on those cases, not from a matrix assertion.
- **`forgery-rev-at-freeze` is a tag, not the freeze commit.** A receipt committed inside the freeze
  commit cannot name that commit's hash; the case names a lightweight tag placed on it, so the arm
  refuses through `CONTROL-REV-INVALID` or `CONTROL-REV-NOT-BEFORE-FREEZE` depending on resolution. The
  truly-not-an-ancestor full-40 arm (an orphan commit) is not in the frozen matrix.
- **C2's fixture observes atomicity indirectly** (in-flight absence, kill residue), not the publish
  syscall itself. A mutant that hashes the worktree file instead of the committed blob survives it; the
  writer's own selftest covers that path.
- **C2's dirty-tree guard is `git status --porcelain`**: an ignored file does not make the tree dirty,
  and a file modified *during* the run is not caught. A SIGKILL still leaves a `<out>.*.tmp` sibling;
  the next write of the same OUT sweeps it.
- Mutation results (S60MutMutation, 15 mutants): 10 killed, 5 survived — `c1-m3` (rev-at-freeze), `c1-m5`
  (instrument name ignored), `c1-m6` (missing command), `c2-m2` (overwrite pre-check skipped; the
  `link(2)` publish makes that mutant equivalent), `c2-m6` (worktree digest). Survivors are findings for
  r61, not passes.
- Certification OFF, K5 HELD. Nothing was removed, quarantined, signalled or certified safe to delete.
  No credential material was opened. No tool installed or updated; no pacman transaction.

## Integrated verification

- Freeze record under the arm it lands: `python3 -B tools/souji-freeze-check.py --root . --prereg
  census/round-60/preregistration.txt --rev 2670e96af1b81c7aa793acc34d40361b4beecff8 --substance` →
  `SUMMARY claims=2 findings=0`, EXIT 0.
- C1 after: `census/round-60/records/c1-after.txt` → `new_forgeries=0 new_honest=3 stubs=REJECTED`,
  EXIT 0. Before: `census/round-60/controls/c1-do-nothing.txt` → `new_forgeries=5`, EXIT 1.
- C2 after: `census/round-60/records/c2-after.txt` → `pass=8 fail=0
  control=ALWAYS-WRITE-REJECTED,ALWAYS-REFUSE-REJECTED`, EXIT 0. Before:
  `census/round-60/controls/c2-do-nothing.txt` → `pass=4 fail=4`, EXIT 1.
- Instrument selftests: freeze checker `cases=41 pass=41` default and `cases=12 pass=12` with
  `--substance`; writer `cases=12 pass=12`.
- Both control receipts are written by the new writer, so each carries `instrument=`,
  `instrument_sha256=`, `rev=3b55250…` (a strict ancestor of the freeze) and `command=` — the shape the
  C1 arm requires, verified by the arm itself on the frozen record.

## Wave

One validated v1 wave, 14 seats (band 8–16): executor 5, scout 2, scribe 1, connector 1, reviewer 2,
critic 1, mutation-tester 1, sentinel 1. Attack share 4/14. The L1 held the canonical planner seat.
Seat findings drove six pre-freeze repairs (SCORECARD round-60 amendments 1–3); no seat wrote a
production file, committed, or pushed.

## Round-end census

`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`
→ EXIT 0 at round end (`census/round-60/records/sources-after.txt`); registry rows 211 → 213 by
`grep -cE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' corpus/SOURCES.md`. The round-start run was EXIT 0 with 211
rows and the same W04 duplicate-URL warning family. One E11 was found and fixed before the end: the
`used-by` cell is split on commas, not semicolons (my S288 cell used `; `, which the census read as one
path). That is a second mined mistake of this round: *a registry cell's separator is part of its
grammar, and a warning-free row can still be dangling* — captured by the census's own E11 rule, fixed by
using the separator the census documents.
