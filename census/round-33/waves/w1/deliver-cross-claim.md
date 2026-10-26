# Souji r33 w1 — cross-claim separability check (C1-CURRENCY × C2-SCRATCH)

Seat: SwarmConnector44. Bytes read at base `6017a482e7068d5afb7617640198fbb0fe743357`
(scratch clone, detached). Counters/guards read at frozen list-rev
`2d9bca55a9f042a2c9ed60a797a8069e74c41f46`. Analysis only — no lane mutation.

## 0. What C2 can change (the reachable set)

Per `census/round-33/c2-legs.tsv` and the r32 routed defect 2:

- O1: `tools/souji-evidence-cache.py` — selftest scratch under literal `/var/tmp` (`:1295` `mkdtemp(..., dir="/var/tmp")`, `:1311` env `"TMPDIR": "/var/tmp"`).
- O2: `tests/fixtures/r15-census-config.py` — `:1545` `mkdtemp(..., dir="/var/tmp")`, `:828` env `"TMPDIR": "/var/tmp"`.
- O3: `tests/fixtures/r15-preservation-frozen/regenerate.py` — `:138` `mkdtemp(..., dir="/var/tmp")`.
- O4: `tools/souji-census.sh` trailing-slash TMPDIR — the `st_worker_tmpdir` `case` pattern at `:1990`
  (`"${TMPDIR:-/tmp}"/souji-census-now.*/*)` vs the `/proc/<pid>/fd/1` readlink target, which the kernel
  resolves with single slashes).
- O5: `tools/souji-round9-selftest.sh` trailing-slash TMPDIR — `:7` `R9_TMP=$(mktemp -d "${TMPDIR:-/var/tmp}/souji-round9-selftest.XXXXXX")`.
- Re-pin commit (Q73, L1-owned): regenerates `tests/fixtures/r15-preservation-frozen/{expected.json,record.json}`.
  `expected.json` at base pins exactly three files: `tests/fixtures/r14-census-boundary.py`,
  `tests/fixtures/r15-census-config.py`, `tools/souji-census.sh` — **not** `souji-round9-selftest.sh`.

Reachable-file set R = {souji-census.sh, souji-evidence-cache.py, r15-census-config.py, regenerate.py,
souji-round9-selftest.sh, r15-preservation-frozen/*}.

## 1. C1 items that reach R

Scanned all 24 items' `files` and `argv` in `census/round-33/c1-items.tsv` against R, plus transitive
execution reach of each item's fixture.

### K07 — LIVE reach of O4 (the only live executable coupling)
- Item: `SCORECARD.md:160`, argv `python3 tests/fixtures/r17-census-hygiene.py --census tools/souji-census.sh`;
  files include `tools/souji-census.sh` (frozen; a restatement cause commit may name it).
- The fixture drives the census with env `"TMPDIR": "/var/tmp"` (`r17-census-hygiene.py:349`) — never a
  trailing slash — and its own scratch is `mkdtemp(dir="/var/tmp")` (`:1279`).
- C1 counter env: `TMPDIR=<os.path.join(mkdtemp, "tmp")>` (`c1-counter.py:150-164` at list-rev) — never a
  trailing slash.
- Prediction: a Q71-only O4 repair (canonicalise the `:1990` pattern, e.g. `${TMPDIR%/}`) is a no-op under
  every no-slash TMPDIR above. K07's stated outcome `total=29 failed=0` cannot move. C1 prints
  `K07 ... AGREE` at the C1 landing commit and at the tip. If a non-Q71 repair *did* move no-slash census
  output, C2 fails first on its own rails: the O4 `slash` leg requires the no-slash run at `--rev` to equal
  the `--base` no-slash run, and G6 (the same command as K07) would count `harm=1`; only then would C1's tip
  reading show `K07 ... MISMATCH`.
- Note for the L1: the O4 repair commit touches `tools/souji-census.sh`, so it is a *cause-eligible* commit
  for a K07 restatement (names a frozen file). Under Q71 it is not needed (outcome holds there). Same logic
  for the O2 repair commit and K-items that name `tests/fixtures/r15-census-config.py` — none do.

### K08 — DEAD reach of O5 (selftest path the item never executes)
- Item: `SCORECARD.md:161`, argv `bash tests/fixtures/r17-jj-receipts.sh --tool-dir tools`; files include
  `tools/souji-verify.sh`, `tools/souji-vault-verify.sh`, `tools/souji-quarantine.sh`.
- Each tool execs `souji-round9-selftest.sh` exactly once, only inside its `--selftest` path
  (`souji-verify.sh:1485` under `:1505 --selftest` dispatch; `souji-vault-verify.sh:1720`;
  `souji-quarantine.sh:1868`; one `round9` ref per file, all in `st_*` selftest blocks).
- `r17-jj-receipts.sh` invokes the tools' normal verdict CLIs only (J1–J15 `v_expect`/`q_expect`, e.g.
  `:720-792`); it exports `TMPDIR="$T/tmp"` (`:183`) and never passes `--selftest`. So the changed bytes
  `souji-round9-selftest.sh` are never read or executed by K08.
- Prediction: unmoved by any Q71 O5 repair. C1: `K08 ... AGREE` at landing and tip. No C2 leg or guard runs
  `r17-jj-receipts.sh`, so C2 never even observes K08's output.

### K03 — DEAD reach of O5 (same pattern)
- Item: `SCORECARD.md:154`, argv `bash tests/fixtures/r13-quarantine-bounds.sh`; files include
  `tools/souji-quarantine.sh`. The fixture invokes the tool only as
  `bash "$TOOL" --hold 0 "$@"` (`r13-quarantine-bounds.sh:143`) with dry-run/staging cases — never
  `--selftest`. Its scratch is a literal `/var/tmp` mktemp (`:88`), unaffected by C2.
- Prediction: unmoved. C1: `K03 ... AGREE` at landing and tip.

### K06 — NOMINAL reach only (string literals + historical bytes)
- Item: `SCORECARD.md:158`, argv `python3 tests/fixtures/r16-landing-gate.py`; files are the fixture and
  `tools/souji-landing-gate.py` — neither in R. The fixture text *names* `tools/souji-census.sh` and
  `r15-preservation-frozen` in expectation tuples (`r16-landing-gate.py:31-33, :232-234, :508-510`) and its
  replay case runs the gate at fixed historical rev `b410186`; per its boundary note it "never runs
  tools/souji-census.sh" (`:52`). Immutable history: C2's r33 commits cannot move `b410186` bytes.
- The landing-gate selftest behind K05/K06/K11/K21/K23 builds fully synthetic repos under scratch
  (`souji-landing-gate.py:1900-2059`, `_mkrepo`/`_write_file`/`_commit_all` worlds) and never reads the live
  `tools/souji-census.sh` or the live r15 pin.
- Prediction: unmoved by any C2 repair or by the re-pin commit.

### All other 20 items — no reach
- Files/argv of K01-K06(except K06 above), K11-K26 intersect R nowhere; their fixtures reference no file in R
  (grep of every named fixture for `round9|evidence-cache|r15-|souji-verify|souji-vault|souji-quarantine|
  souji-census` returned only the four fixtures above). K22 reads fixed historical revisions only (Q70c).
  No item runs `souji-evidence-cache.py`, `r15-census-config.py`, or `regenerate.py` — O1/O2/O3 repairs
  touch nothing any C1 item executes.

## 2. Can a C1 restatement row move any C2 leg? — NO (byte-verified)

- A restatement lands only in the appended `### Round 33 capability currency` section of SCORECARD.md.
- G-guards: `grep SCORECARD` over `tests/fixtures/r22-result-oracle.py`, `census/round-22/mutation-adequacy.py`,
  `tests/fixtures/r14-evidence-cache.py`, `tools/souji-preservation-evidence.py`,
  `tests/fixtures/r15-preservation-evidence.py`, `tests/fixtures/r17-census-hygiene.py`,
  `census/round-21/run-acceptance.py` → **0 matches**.
- O tools: `grep SCORECARD` over `tools/souji-census.sh`, `tools/souji-evidence-cache.py`,
  `tests/fixtures/r15-census-config.py`, `tests/fixtures/r15-preservation-frozen/regenerate.py`,
  `tools/souji-round9-selftest.sh`, `tools/souji-verify.sh`, `tools/souji-vault-verify.sh`,
  `tools/souji-quarantine.sh` → **0 matches**.
- `c2-counter.py` at list-rev: **0 SCORECARD references** (rc=1); it reads only `c2-legs.tsv` and runs legs.
- Conclusion: C1's surface is invisible to every C2 leg and to the C2 counter. C1→C2 coupling is null.

## 3. Net assessment

- C2→C1: one live coupling (K07 via `tools/souji-census.sh` bytes), and it is doubly guarded — the C1
  environment never uses a trailing-slash TMPDIR, and any non-Q71 output move fails C2's own O4 slash-equality
  and G6 guard before C1's tip reading matters. K08/K03 reach O5 only through `--selftest` paths their
  fixtures never take. The preregistration's `== Separability` sentence ("a C2 repair that moves a C1 item's
  output fails C2 first") holds at byte level.
- C1→C2: null. Restatement rows, and the C1 landing commit generally, cannot move any O leg or G guard.
- No amendment and no ATTACK indicated: the frozen separability design is accurate, slightly conservative
  (it names K08 as coupled through `tools/souji-verify.sh`; the executable coupling is narrower).
