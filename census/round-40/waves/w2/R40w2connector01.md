# R40w2connector01 — wave-2 falsify / connector: cross-claim overlap scan (C1/C2/C3)

Date: 2026-10-28. Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Revisions: instrument landing `128e412b0ced3c243dc27c3dd3332054a611bc2e`; receipt/closure rev
`549d9ec53a1f5932337ff14438fcd22b0621828d`; current tip `994de3b447e9a7bea2abfbd80c4736f6215d3e47`
(landed while this scan ran); base `0242085909fb6a4ee041c5443d76316ac6d59d4b`; C2 defect rev
`ed30b7f5b77939c9073348d810730bc4f355708d`.

**Question (seat task):** do C1, C2 and C3 read or mutate shared bytes? Which claim's verification
depends on another claim's landing?

**Headline verdict: SAFE** on the overlap question — the three claims share tool *bytes* (git
blobs), never shared mutable files, never shared scratch, and none of the 3 runs wrote a single
byte into the lane (strace-verified). **One sub-finding FALSIFIED**: the C1 receipt's recorded
command line is not revision-stable — re-running it verbatim at the recorded rev *today* flips
`R40-CLAIM-D3` to OPEN (rc 1), because the counter's own bytes are not pinned by the receipt.

---

## 1. Method

Ground truth from two sources, cross-checked:

1. **Source read** of the landed bytes (all at HEAD, verified `git hash-object` == `git rev-parse
   HEAD:` for every file listed in §2 — all SAME).
2. **strace of the real receipt commands** at the receipt rev, `strace -f -ff -e trace=%file`, with
   per-pid cwd replay to resolve relative paths:

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && \
strace -f -ff -e trace=%file -o $S/strace/c1 python3 -B census/round-40/c1-counter.py \
  --root $LANE --rev 549d9ec53a1f5932337ff14438fcd22b0621828d \
  --items census/round-40/c1-items.tsv --forged census/round-40/c1-forged.tsv \
  --register census/round-40/cells.tsv --min-cells 3 --min-commit-rows 3 --scratch $S/c1
# → C1-RC=0, SUMMARY byte-identical to census/round-40/records/c1-after-d.txt
strace ... -o $S/strace/c2 python3 -B census/round-40/c2-counter.py \
  --root $LANE --rev 549d9ec... --base-rev 0242085... --scratch $S/c2
# → C2-RC=0, `SUMMARY legs=7 pass=7 fail=0 harm=0 drift_sha=e48ed08e6728 fixture_sha=0dc6c789a741`
#   byte-identical to records/c2-after-d.txt
strace ... -o $S/strace/c3 python3 -B census/round-40/c3-counter.py \
  --root $LANE --rev 549d9ec... --base-rev 0242085... --scratch $S/c3
# → C3-RC=0, `SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=8
#   tool_sha=e48ed08e6728 fixture_sha=a6ec36f0ce9e` byte-identical to records/c3-after-d.txt
```

All three receipts **reproduce exactly** from committed bytes at their stated rev.

## 2. File inventory per claim (strace-verified, worktree + git-object reads)

Shared inputs are git **blobs** reached via `git show REV:path`; the worktree is read only where noted.

**C1 — `census/round-40/c1-counter.py`** (206 distinct lane paths, almost all `.git/objects/*`):
- worktree reads (unpinned): `census/round-40/c1-items.tsv`, `census/round-40/c1-forged.tsv`
  (opened by path, `c1-counter.py` run(): `open(args.items)`); the script file itself.
- git-pinned: `--register census/round-40/cells.tsv` via `git_show(root, register_rev, register)`;
  `tools/souji-citation-reconcile.py` @rev (extracted to scratch, executed; extract at
  `c1-counter.py:register_leg`, scratch write root `souji-r40-c1.*` — exactly 1 file).
- lane git access: `cat-file -e`, `show`, `merge-base --is-ancestor` only.

**C2 — `census/round-40/c2-counter.py`** (140 lane paths):
- `tools/souji-citation-reconcile.py` @rev/@base-rev/@defect-base-rev (`CITATION`, :59);
  `tools/souji-worktree-drift.py` @rev/@base-rev (`DRIFT`, :60);
  `census/round-40/docstring-classes.py` @rev loaded by importlib from a scratch copy
  (`load_analyzer`); `tests/fixtures/r40-docstring-joined.py` @rev (`FIXTURE`, :61); 7 consumer
  fixtures @rev (`CONSUMERS`, :62 — incl. `tests/fixtures/r39-drift-record-rules.py`);
  `census/round-38/cells.tsv` passed as `--register` to the reconciler in L1–L3 (:145-150) —
  reconciler pins it via `git_show` at `--register-rev` (`tools/souji-citation-reconcile.py:263-267`).
- own script file. Scratch root `souji-r40-c2.*` (5878 writes, all under `--scratch`).

**C3 — `census/round-40/c3-counter.py`** (40 lane paths):
- `tools/souji-worktree-drift.py` @rev (`--tool` default, :129-130 area; `git_show` :146 area);
  `tests/fixtures/r40-drift-record-branches.py` @rev (`--fixture` default);
  `tests/fixtures/r39-drift-record-rules.py` @rev (`--base-fixture` default, :130).
- own script file. Scratch root `souji-r40-c3.*` (857 writes: pristine + 4 mutants + fixture
  fleet-roots; `tests/fixtures/r40-drift-record-branches.py:74` writes `record-*.tsv` under the
  scratch fleet-root via `tempfile.mkstemp(dir=root)`, never in the lane).

**C2's L5 fixture** `tests/fixtures/r40-docstring-joined.py` reads only `--analyzer`/`--tool` paths
(copies in scratch). **C1's selftest fixture** `tests/fixtures/r40-c1-evidence.py` builds its own
repo in `--work` (:134 `mkdtemp(prefix="souji-r40-c1.", dir=work)`) but its default reconciler read
is `os.path.join(lane_root, RECONCILER)` (:75) — a **worktree** read (F5 below).

## 3. Overlap matrix (byte level)

| Shared bytes | C1 | C2 | C3 | Evidence |
|---|---|---|---|---|
| `tools/souji-citation-reconcile.py` @rev | executed (register leg, :203 child) | executed L1–L3 (:145-150) @rev/base/defect | — | sha equal at 549d9ec (same blob) |
| `tools/souji-worktree-drift.py` @rev | — | audited L4/L6 (`drift_sha=e48ed08e6728`) | mutated+scored (`tool_sha=e48ed08e6728`) | both receipts stamp the same 12-hex; recomputed from the blob: `e48ed08e6728` ✔ |
| `tests/fixtures/r39-drift-record-rules.py` @rev | — | consumer #4, harm control (`7/7(base 7/7)`) | `--base-fixture`, must-survive control (`base_killed=0`) | same bytes, two no-harm roles |
| `.git` object store of the lane | read | read | read | read-only refs/objects/packs |
| Worktree TSVs (`c1-items.tsv`, `c1-forged.tsv`) | **C1 only** | — | — | no claim reads another claim's inputs |
| Scratch | `souji-r40-c1.*` | `souji-r40-c2.*` | `souji-r40-c3.*` | disjoint prefixed `mkdtemp`; fallback `/var/tmp` (never `/tmp`), subdir-isolated |

Lane-read intersections contain only `.git` internals (`HEAD`, `packed-refs`, commit-graph, shared
blobs) and the `census/round-40` directory entry. **No worktree file is read by more than one
claim.**

## 4. Mutation check (the "do they mutate shared bytes" arm)

Every write-mode `open` across all three traces resolves to: my `--scratch` subtree, `/dev/null`
(GIT_ENV `GIT_CONFIG_GLOBAL=/dev/null`), or scratch fixture repos (e.g. the `git branch wt HEAD`
calls in C2's L6 r36 consumer chdir into `…/c2/souji-r40-c2.*/souji-r36-drift.*/prunable/fleet/alpha`
— the `.git/logs/refs/heads/wt` reflog writes are those scratch repos, **not** the lane; the lane
has no `wt` ref: `git for-each-ref refs/heads/wt` → empty, `test -e .git/logs/refs/heads/wt` →
absent, `git worktree list` → main worktree only).

```
grep -hE "open(at)?\(" $S/strace/c1.* $S/strace/c2.* $S/strace/c3.* \
  | grep "O_WRONLY\|O_RDWR\|O_CREAT\|O_TRUNC" | grep -F "$LANE" | sort -u
# → (no output)  — zero write-mode opens naming the lane
git -C $LANE status --porcelain   # unchanged by my runs (only the L1's own in-flight edits)
```

Tool-level confirmation: the reconciler's git children re-whitelist env internally
(`citation-reconcile.py` `git_proc`/`git_show`); drift runs git with `--no-optional-locks`,
`core.fsmonitor=false`, `hooksPath=/dev/null`, and writes only an explicit `--json` target
(`open_nofollow`, O_WRONLY|O_CREAT|O_TRUNC at `worktree-drift.py:250`) which **no counter or
fixture ever passes**. No `/tmp` or `/var/tmp` pollution: no `souji-r40-c*` entries exist after the
runs.

## 5. Cross-claim verification dependencies

1. **C1 depends on C2's and C3's landings.** Item `R40-CLAIM-D1` evidence =
   `census/round-40/records/census-after.txt@6ded1248…`; item `R40-CLAIM-D2` evidence =
   `census/round-40/records/c2-after.txt@6ded1248…` (`census/round-40/c1-items.tsv`, rows 2-3).
   `evaluate_item` fails an item with `EVIDENCE-PATH-ABSENT` (`c1-counter.py:257`) unless those
   receipt files **exist at the pinned revision** — i.e. C1's closure requires the C2 (and census)
   receipt bytes to have landed. `R40-CLAIM-D2`'s must-tokens additionally require the SCORECARD
   line at rev to carry `8a5fbdbddaab24c5ba43fc6a133499efb405f214` (the C2 counter-fix commit) and
   `legs=7`. No reverse dependency: C2's and C3's lane reads contain no C1 artifact (verified in
   the strace inventories).
2. **C1 ⇄ C2 coupled failure surface (no landing-order dependence).** Both execute the
   `citation-reconcile` blob at rev; a regression there fails C1 with exit 2
   (`COULD-NOT-EVALUATE`) and C2's L1–L3 simultaneously.
3. **C2 ⇄ C3 share their no-harm control.** The same `r39-drift-record-rules.py` blob is C2's
   consumer-harm control and C3's must-survive base arm, and both receipts stamp the same
   `drift_sha`/`tool_sha=e48ed08e6728` — the two claims provably audited the same drift bytes.

## 6. Findings

**F1 — FALSIFIED (reproducibility, C1 axis).** The C1 receipt does not pin its own instrument
bytes. The recorded command (`records/c1-after-d.txt` header) runs the counter from the **worktree
path** while pinning only the data rev. Between `549d9ec` and `994de3b` the counter's
`EVIDENCE-NOT-BOUND` condition was tightened to bind the evidence *path* as well
(`c1-counter.py:263` at tip). Re-running the recorded line verbatim today:

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -B census/round-40/c1-counter.py \
  --root . --rev 549d9ec53a1f5932337ff14438fcd22b0621828d \
  --items census/round-40/c1-items.tsv --forged census/round-40/c1-forged.tsv \
  --register census/round-40/cells.tsv --min-cells 3 --min-commit-rows 3 --scratch $S/c1-mixed
→ ITEM R40-CLAIM-D3 OPEN EVIDENCE-NOT-BOUND census/round-40/c1-counter.py@8a5fbdbddaab24c5ba43fc6a133499efb405f214
→ SUMMARY items=3 open=1 … items_sha=8f97b0097e09 forged_sha=915b1184e9c6   (rc 1)
```

— same rev, same input shas as the receipt (`items_sha=8f97b0097e09 forged_sha=915b1184e9c6` in
both), opposite verdict. Byte-consistent runs of the same command with the counter extracted from
the measured rev (`git show 549d9ec:census/round-40/c1-counter.py`) reproduce the receipt exactly
(rc 0), and the tip counter at the tip rev also passes (rc 0, all items CLOSED, forged all OPEN).
So the **predicate is sound at every self-consistent byte set** — but the recorded measurement
contract is under-determined: an L1 re-running the receipt line after any counter commit reads a
false OPEN. The counters stamp shas for every audited byte (`items_sha`, `drift_sha`,
`tool_sha`, `fixture_sha`) except **their own** — the one sha whose drift I demonstrated within a
single wave.

**F2 — observation (shared-tool envelope inconsistency).** C1 launches the shared reconciler with
`env={"PATH": …, "TMPDIR": scratch}` (`c1-counter.py:203`) — no `GIT_ENV`; C2 launches the same
bytes with the full whitelist including `LC_ALL=C` (`c2-counter.py:150` via `child_env(scratch)`).
Git-level sandboxing is intact either way (the reconciler re-whitelists inside
`git_proc`/`git_show`), but the reconciler's *Python* process runs under ambient locale in C1 vs
`LC_ALL=C` in C2. Not exploited; noted as an envelope asymmetry on shared bytes.

**F3 — observation (TMPDIR gap, harmless today).** `c2-counter.py:154-158` `run_drift` calls
`child_env()` without scratch → the drift child inherits **no TMPDIR**. Verified harmless: drift
itself mkdtemps nothing, writes only an explicit `--json` target (never passed), and post-run
`/tmp`/`/var/tmp` contain no `souji-r40-c*` entries.

**F4 — observation (unpinned C1 inputs).** C1's `--items`/`--forged` are read from the mutable
worktree while the register is git-pinned. Today worktree == HEAD for both (verified by blob hash),
but on a lane actively receiving commits (as during this wave) the items can diverge from the
committed ones with only the printed `items_sha` to notice.

**F5 — observation (fixture defaults are worktree-bound).** `tests/fixtures/r40-c1-evidence.py:75`
defaults to the lane worktree reconciler; `tests/fixtures/r40-drift-record-branches.py:131`
defaults `--tool` to the lane worktree drift. Counter-driven runs override both with git-pinned
scratch copies, so only bare fixture invocations are exposed.

## 7. Connector move (one bounded proposal)

**Pin the instrument bytes in the receipts, as the data bytes already are.** Re-run each receipt
via `git show REV:census/round-40/cX-counter.py > $SCRATCH/counter.py` and execute that copy (and/
or have each counter print its own blob sha next to `items_sha`/`drift_sha`/`fixture_sha`). This
directly removes the F1 falsifier, improves the calibration axis (a receipt becomes
revision-stable under its recorded command line), and costs C2/C3 nothing — their counters are
unchanged since the receipts, so their recorded lines already coincide with the pinned form; the
change only forecloses the same drift class for future counter edits. Compatible synthesis on the
shared control: stamp `r39-drift-record-rules.py`'s sha in both the C2 and C3 receipts, since that
one fixture is simultaneously C2's harm control and C3's must-survive control (§5.3) — one extra
field, no behavior change, no harm to any axis.

## 8. Verdicts

- **Overlap question (seat task): SAFE** — shared bytes are git blobs and `.git` read state only;
  no shared mutable file, no shared scratch bytes, zero lane writes (§3, §4).
- **C1 calibration instrument: SAFE at its receipt rev** with committed bytes (exact reproduction,
  rc 0, SUMMARY byte-identical, forged token-only item OPEN) — but the **receipt's recorded command
  line: FALSIFIED** as a stable measurement contract (F1, command + output above).
- **C2 operability instrument: SAFE** — `legs=7 pass=7 fail=0 harm=0` reproduced byte-identically.
- **C3 coverage instrument: SAFE** — `mutants=4 killed=4 survived=0 pristine=ok base_killed=0
  cases=8` reproduced byte-identically.

Scratch: `/fast/scratch/hyaku/souji-r40/w2/R40w2connector01` **removed** (verified absent with
`test ! -e`). Installs: none (strace 7.2 already present; pacman untouched per host pause). Lane
mutations by this seat: none (report file only).
