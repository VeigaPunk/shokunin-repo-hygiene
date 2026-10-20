# round-13 — gate-registry draft (four installed tools + r13 entries)

Status: **DRAFT, not applied.** The registry home is `SKILL.md`; this seat was
forbidden to edit it. This file is the exact replacement table plus the evidence
for every cell. Author seat: `SoujiR13.RegistryDraft` (leaf). This seat is **not**
an independent non-author verifier and claims no such status.

Basis: lane HEAD `31984f473ce4bdab61a99b16cca194b28108cb81` (31984f4). Measurements
below were read at 2026-10-20 ~02:12–02:30 -03:00. **The worktree was moving while
this draft was written** (`git -C /home/vgpnk/Projects/shokunin/souji-shokunin status
--porcelain` showed `M PROVINCE.md SHONEN.md SKILL.md corpus/QUALITY.md corpus/README.md
corpus/SOURCES.md tools/souji-quarantine.sh` and untracked r13 tool/fixture files).
Every r13-file claim names the digest it was read at and must be reconciled by L1
after the wave lands. The four installed tools other than `souji-quarantine.sh` were
at their committed HEAD bytes when hashed.

No tool, fixture, build, lint or test was executed by this seat (round contract).
All exit maps and scratch paths below are **read from source**, not observed runs.

---

## 1. The protocol test applied

`PROTOCOL.md` §Gate standard (lines 388–430) fixes the row schema and the
gate/probe distinction:

> A **gate** is a committed, re-runnable verdict script a lane owns: it reads
> surfaces, compares them against expected values persisted in its own repo, and
> returns a verdict. A tool that cannot fail is a **probe**, and is registered as
> one. (lines 390–392)
>
> Row fields: name, `gate|probe`, entry command, verdict map (code → class),
> self-test command and spelling, pinned-value path, write scope, owner. (414–416)

Decision rule used for every row, in order:

1. Does the process compare measured surfaces against expected values **persisted
   in this repo**? If no, it is not a gate.
2. Can it return `1` for a **surface** verdict (not just for an internal error)?
   If no, it cannot fail → probe.
3. Does code `1` mean *could-not-evaluate* (setup, missing dependency) rather than
   *failed*? Then it cannot be registered as a gate without an exit-map repair,
   because the fleet-wide convention fixes `1 = failed` (protocol 393–394).

Rule 3 is the finding that decides four rows: the installed tools use `1` for
missing `git`/`rg`/`du`, nested-selftest refusal, or internal setup failure. That is
`could-not-evaluate` semantics under a code the fleet reserves for `failed`. They
are therefore registered as probes now; promotion is a code change, not a prose
change. This is a fact about the source below, not a preference.

The schema is binary, so one nuance is recorded rather than hidden:
`souji-quarantine` is an **operation**, not a measurement, and it exits nonzero on
blocked targets. It is registered as a probe because it has no persisted expected
values to compare against and its nonzero codes are target outcomes, not a
conformance verdict; "cannot fail" in the row means it cannot fail such a verdict,
not that it never exits nonzero.

If L1 overrules this classification and labels a tool `gate`, the minimum repair is
already visible in the row: move setup/dependency exits to `2`, add a committed
expected id-set or frozen input snapshot, and name the revision measured. Until
those exist, a `gate` label would be a prose claim the code does not support.

## 2. Per-tool interface and selftest facts (read at HEAD bytes unless noted)

| tool | sha256 read | header CLI contract | selftest spelling | selftest scratch root |
|---|---|---|---|---|
| `tools/souji-verify.sh` | `9adb17645a5f452ae2cc28673642ad256f9aee92109939531f3c34a0972812cd` | lines 7–8 | `--selftest` (line 1290) | `mktemp -d "${TMPDIR:-/tmp}/souji-verify-selftest.XXXXXX"` (line 1105) |
| `tools/souji-vault-verify.sh` | `f9e778ca478c7aa8b33234ee793030df631c1b9fcebc942b1ff41d0008ed9c5b` | lines 13–16 | `--selftest` (line 1595) | `mktemp -d "${TMPDIR:-/tmp}/souji-vault-verify-selftest.XXXXXX"` (line 1308) |
| `tools/souji-census.sh` | `6a000c59fe7486fbde7e5f68663c61cf60404cadb4185e84205b56fe4648c026` | lines 8–10 | `--selftest` (line 799) | `mktemp -d "${TMPDIR:-/tmp}/souji-census-selftest.XXXXXX"` (line 516) |
| `tools/souji-quarantine.sh` | `141c0fdc4eaf9d0a3d628b381cc5386f6d4be71565ddfb98aa10f6eb3c9573c9` (baseline; r13 edits uncommitted) | lines 11–14 | `--selftest` (line 1524; main at 1553–1554) | `mktemp -d "${TMPDIR:-/tmp}/souji-quarantine-selftest.XXXXXX"` (line 1247) |
| `tests/fixtures/r12-maintenance-guard.sh` | `a359070a66706ad2570eb92f0ce87f5ba840136f02f3cf987adb57272e95a0f9` | lines 30–47 | `--selftest` (line 64) | `mktemp -d /var/tmp/souji-r12-maintenance.XXXXXX` (line 68) |

### 2.1 `souji-verify.sh` — probe

- Verdicts are stdout data and the process **cannot fail on them**: `NOT-SAFE
  means "no removal receipt" — the safe default, not an error` (line 12);
  main ends `exit 0` (line 1316); the selftest case H6 asserts exit 0 on a
  NOT-SAFE verdict (line 1255).
- Only non-zero exits: `1` nested-selftest refusal (1226), selftest assertion
  failure (1282), missing `git`/`rg` (1308–1309); `2` usage via `usage 2`
  (87–90, `usage_err`).
- Selftest asserts in-script case ids: F1–F10 (1232–1241), E1–E8 (1242–1249),
  H2–H4 via `st_status` (1251–1253), plus H1/H5/H6 audit asserts; tally line at
  1281. **No pinned expected id-set or tally is compared**; deleting a case
  lowers the count silently. Last committed count measurement is
  `census/round-10/S06-selftest-counts.txt` (`40 checks, 0 failed`) — pre-r13 and
  not a pin.
- Write scope: read-only on live surfaces; the selftest alone writes under
  `${TMPDIR:-/tmp}`.

### 2.2 `souji-vault-verify.sh` — probe

- Same outer shape: verdict lines plus `VERIFIED/NOT-VERIFIED` vocabulary; main
  `exit 0` (line 1632); `1` at 1444 (nested selftest), 1588 (selftest failure),
  1623–1624 (missing `git`/`rg`); `2` via `usage 2` (75–79).
- The optional `obsidian-cli` shim is *advisory only*, never the receipt, and is
  run under `timeout ${SOUJI_CLI_TIMEOUT:-6}` (header lines 5–11). That is an
  external process invocation, not a write.
- Selftest ids: F1–F5/F7–F10, V1–V6/V9/V12/V15/V17/V18/V20, H4–H5
  (1451–1534, 1570–1571); tally at 1587; **no pinned id-set**. Historical r10
  count `51 checks, 0 failed` (`census/round-10/S06-selftest-counts.txt`), stale.
- Write scope: read-only over source and vault; selftest under `${TMPDIR:-/tmp}`.

### 2.3 `souji-census.sh` — probe (with a differential mode that is not a gate)

- Default census emits TSV and ends `exit 0` (line 827). `--compare PREV.tsv`
  returns `3` when any row differs (line 466) and `0` for a header-only diff.
- Non-zero setup paths: `1` for a non-directory `--root` (346), nested selftest
  (514), selftest failure (791), missing `git`/`du` (818–819); `2` for usage and
  for an empty/malformed baseline (`usage_err`, 93; rationale at 357–361).
- This is the closest installed tool to a gate: compare mode can fail
  differentially. It is **not** registered as one because (a) the expected value
  is a caller-supplied TSV with no committed digest or pinned count, and (b) code
  `1` is `could-not-evaluate` in this tool, which a gate may not use for that
  class. Gate promotion requires a committed census TSV + `expected.json` digest
  map and a `1 → 2` remap for setup failures.
- Compare mode writes `mktemp "${TMPDIR:-/tmp}/souji-census-now.XXXXXX"` and
  removes it (line 418); selftest under `${TMPDIR:-/tmp}` (516). Last committed
  count: `32 checks, 0 failed` (r10 record, stale).

### 2.4 `souji-quarantine.sh` — probe (mutating operation; receipt authority delegated)

All line numbers in this subsection are HEAD `31984f4` bytes; the uncommitted r13
diff shifts them. Behavior claims come from the baseline plus the diff read at
02:19.

- Receipt authority is not re-implemented: the header states the engine is
  `tools/souji-verify.sh`, invoked as a child (lines 5–8 at baseline). The r13
  diff additionally removes the `cand-merge-verify.sh` fallback so the engine is
  always the installed tree's `souji-verify.sh` unless `SOUJI_VERIFY_BIN` pins a
  fixture (Q6).
- Exit map as documented (lines 92–96) and implemented: `0` every target
  DELETED/SKIPPED/DRY-RUN-PASS; `3` at least one NOT-AUTHORIZED, ABORTED or
  STAGE2-FAILED (`RC=3` at 399, 525–579), or DRY-RUN-BLOCKED; `4` live-fleet
  mutation guard refusal (624); `1` internal/setup/engine-missing (611, 1307–1309,
  1519); `2` usage (159). Final `exit "$RC"` (1569).
- r13 in-flight Q8 bounds (uncommitted diff, read 02:19): file digest 120s,
  directory digest 300s, staging `mv`/`git mv` 60s, engine 120s, final `rm` 120s,
  special-file scan 60s, all under `timeout --kill-after=10`; a bound hit is
  fail-closed and nothing is deleted after a timeout; symlink/FIFO/socket/device
  targets and descendants are refused; staging requires one device; a timed-out
  `git mv` may leave `.git/index.lock`, which is reported and never removed by
  the tool. These are the bytes that the r13 bounds gate must exercise.
- Selftest ids: G1, D1–D3, N1–N4, P1–P3, SKIP1, L1, A1, U1–U5, H1/H3
  (1327–1499); tally at 1513; **no pinned id-set**. Historical r10 count
  `91 checks, 0 failed`, stale; the r13 diff changes the count.
- Write scope: live mutation only under `<repo>/.ufo-quarantine/<utc-date>/`
  (header 97–99); selftest under `${TMPDIR:-/tmp}` (1247); a stderr temp
  `${TMPDIR:-/tmp}/souji-quarantine.err.XXXXXX` (1519).

## 3. Exact replacement table for `SKILL.md`

Apply by **content anchor**, not line number: the table currently follows the
`Gate registry (PROTOCOL §Gate standard; ...)` paragraph. At HEAD the anchor is
`SKILL.md:102–106`; at this read the working tree placed it at `SKILL.md:118–122`
(other seats added content before it), so L1 must locate the paragraph text and
replace it in place.

Replace the paragraph and table with:

```markdown
Gate registry (PROTOCOL §Gate standard; `0` clean · `1` failed fleet-wide; every
other code is declared per row and mapped to `clean|failed|could-not-evaluate`;
a code outside the row's map reads as could-not-evaluate). `probe` = a
measurement or operation with no conformance verdict to fail; its nonzero codes
are diagnostics/target outcomes and its `--selftest` is capability evidence, not
a verdict.

| name | kind | entry command | verdict map (code → class) | self-test command (spelling) | pinned-value path | write scope | owner |
|---|---|---|---|---|---|---|---|
| souji-verify | probe | `bash tools/souji-verify.sh [--json] [--stale-days N] <path>...` | 0 clean (verdicts emitted; NOT-SAFE is data) · 1 failed (selftest assertion failure); the same code also carries missing git/rg, i.e. could-not-evaluate (debt) · 2 could-not-evaluate (usage) | `bash tools/souji-verify.sh --selftest` (`--selftest`; in-script ids F1–F10, E1–E8, H1–H6; no id-set assertion) | none — no pinned id-set/tally; `census/round-10/S06-selftest-counts.txt` is a stale observation, not a pin | read-only live; selftest `mktemp -d "${TMPDIR:-/tmp}/souji-verify-selftest.XXXXXX"` only | souji |
| souji-vault-verify | probe | `bash tools/souji-vault-verify.sh [--json] [--stale-days N] [--ledger PATH] [--vault PATH] [--fallback/--cli/--auto] <path>...` | 0 clean (VERIFIED/NOT-VERIFIED emitted; not an error) · 1 failed (selftest assertion failure); the same code also carries missing git/rg (debt) · 2 could-not-evaluate (usage) | `bash tools/souji-vault-verify.sh --selftest` (`--selftest`; F/V/H case ids; no id-set assertion) | none — no pinned id-set/tally; r10 `51 checks` record is stale | read-only over source+vault; optional `obsidian-cli` shim under `timeout ${SOUJI_CLI_TIMEOUT:-6}`; selftest `mktemp -d "${TMPDIR:-/tmp}/souji-vault-verify-selftest.XXXXXX"` only | souji |
| souji-census | probe | `bash tools/souji-census.sh [--root DIR] [--include-root] [--compare PREV.tsv]` | 0 clean (census emitted or diff header-only) · 3 failed (differential rows; `--compare` only) · 1 failed (selftest assertion failure); the same code also carries root-invalid/missing git/du, i.e. could-not-evaluate (debt) · 2 could-not-evaluate (usage; malformed baseline) | `bash tools/souji-census.sh --selftest` (`--selftest`; compare asserts 0/3/2 at 707–756; no id-set assertion) | none — caller-supplied `--compare` only, no committed census TSV + digest; r10 `32 checks` record is stale | live scan read-only; compare temp `mktemp "${TMPDIR:-/tmp}/souji-census-now.XXXXXX"` (removed); selftest `mktemp -d "${TMPDIR:-/tmp}/souji-census-selftest.XXXXXX"` only | souji |
| souji-quarantine | probe | `bash tools/souji-quarantine.sh [--dry-run] [--hold N] [--list FILE] <repo> <target>...` | 0 clean (DELETED/SKIPPED/DRY-RUN-PASS) · 3 failed (NOT-AUTHORIZED/ABORTED/STAGE2-FAILED; DRY-RUN-BLOCKED) · 4 could-not-evaluate (live-fleet mutation guard) · 1 failed (selftest assertion failure); the same code also carries internal/setup/engine-missing, i.e. could-not-evaluate (debt) · 2 could-not-evaluate (usage) | `bash tools/souji-quarantine.sh --selftest` (`--selftest`; G1/D/N/P/SKIP/L/A/U/H ids; must stay green through the r13 bounds change) | none — no pinned id-set; `tests/fixtures/r13-quarantine-bounds.sh` is the conformance gate | mutation only under `<repo>/.ufo-quarantine/<utc-date>/`; selftest `mktemp -d "${TMPDIR:-/tmp}/souji-quarantine-selftest.XXXXXX"`; stderr temp `${TMPDIR:-/tmp}/souji-quarantine.err.XXXXXX`; a timed-out `git mv` may leave `.git/index.lock` (reported, never removed) | souji |
| r12-maintenance-guard | gate | `bash tests/fixtures/r12-maintenance-guard.sh` | 0 clean · 1 failed · 2 could-not-evaluate | `bash tests/fixtures/r12-maintenance-guard.sh --selftest` (`--selftest`, `selftest=PASS ids=6/6`) | `tests/fixtures/r12-maintenance-guard.sh:130-137` pinned id set + per-case expected counts in the header; observed run `tests/results/r12-maintenance-guard.txt` | `mktemp -d /var/tmp/souji-r12-maintenance.XXXXXX` only | souji |
| souji-cert-evidence | gate | `python3 tools/souji-cert-evidence.py --root PATH --manifest PATH` (or `--frozen DIR`) | 0 clean · 1 failed (`fragment-reported-fail` only) · 2 could-not-evaluate (all other finding ids; argparse usage = 2) | `python3 tools/souji-cert-evidence.py --selftest` (embedded; invokes the CLI per case, asserts rc + finding ids; 32→35 cases across the read window, count moves) and `python3 tests/fixtures/r13-cert-evidence.py` (black-box replay: selftest + external-clean + external-digest-mismatch + frozen-clean + frozen-tampered; exit 0/1/2) | embedded: `tests/fixtures/r13-cert-frozen/expected.json` (7 inputs pinned; recomputed equal at last read) + finding-id list in the script header. Replay: same frozen snapshot, 5 named checks | read-only live; embedded selftest `tempfile.mkdtemp(dir="/var/tmp")` only; replay `tempfile.mkdtemp(dir="/var/tmp")` only | souji |
| souji-repo-structure | probe | `bash tools/souji-repo-structure.sh --repo PATH` | 0 clean (probe.status=ok + 28 structure keys) · 2 could-not-evaluate (usage, git missing, unusable/promisor repo) · 3 could-not-evaluate (installed git lacks repo structure --format=lines) · 4 could-not-evaluate (structure nonzero or metrics absent) | none in the tool (a probe has no verdict); conformance gate is `r13-repo-structure` | none — output is repository-dependent; the gate fixture asserts invariants, not metric constants | read-only; no scratch file | souji |
| r13-repo-structure | gate | `bash tests/fixtures/r13-repo-structure.sh --selftest` (baseline arm) or `--selftest --probe <tool>` (lane probe arm) | 0 clean · 1 failed · 2 could-not-evaluate | `bash tests/fixtures/r13-repo-structure.sh --selftest [--probe PATH]` (`--selftest`; `selftest=PASS ids=4/4` baseline, `ids=5/5` with `--probe`, the 5th being `SOUJI-R13-STRUCT-promisor-refusal`) | `tests/fixtures/r13-repo-structure.sh:626-634` `SELFTEST_EXPECTED_IDS` + case expectations in the header (`SOUJI-R13-STRUCT-*`); observed run to be committed at `tests/results/r13-repo-structure.txt` | `mktemp -d /var/tmp/souji-r13-repo-structure.XXXXXX` only; measured command bounded by `timeout 120` | souji |
| r13-quarantine-bounds | gate | `bash tests/fixtures/r13-quarantine-bounds.sh [--tool PATH] [--verify PATH] [--case ID ...]` (default runs all five; `--tool` selects the baseline red arm) | 0 clean (every selected case PASS) · 1 failed (any case FAIL; the header names `HANG` too, but the code only emits PASS/FAIL) · 2 could-not-evaluate (usage/environment: missing timeout/mv/sha256sum/tool/engine) | `bash tests/fixtures/r13-quarantine-bounds.sh` itself (no `--selftest` flag; isolated `/var/tmp` repo; stable CASE ids R13Q8-01…05; rc asserted per case; no pinned id-set equality) | case expectations in the fixture header (lines 5–11) and case bodies (`CASE<R13Q8-0N> PASS or FAIL` tokens, rc, RESULT tokens, filesystem state); observed run to be committed at `tests/results/r13-quarantine-bounds.txt` | `mktemp -d /var/tmp/r13-qbounds.XXXXXX` only (trap removes), inner git repo inside it; fixture sets `SOUJI_QUARANTINE_ALLOW_LIVE=1` for that isolated repo only | souji |
```

Owner is the lane (`souji`) for every row; no row is operator-owned. At the
last read every row's entry file existed; the r13 files were still being edited
during the window, so the digest-qualified notes in §4 and §8 are the evidence
of record, not an assumption that the bytes stopped moving.

## 4. The three r13 entries, precisely

### r13-1 — `souji-cert-evidence` (gate, C1)

Landed while this draft was written. The file **produced five observed digests in
the read window** — `f2729f19…` (02:14) → `5c86764d…` (02:16) → `f64c0762…`
(02:19) → `90542347…` (32 selftest cases) →
`1b942b78f7fb2788e4b733662315423d4571e4277e793e31d0a04a3b331fc008` (35 cases,
last read). L1 must re-read the landed bytes; the row's stable facts are the exit
map and the finding-id vocabulary, not the case count.

- CLI: `--root PATH --manifest PATH`, `--frozen DIR`, `--selftest`; argparse
  usage errors exit 2 before any finding (header "Exit codes", "Argparse usage
  errors also exit 2").
- Exit map: 0 clean; 1 failed only for `fragment-reported-fail` (an honest,
  schema-valid failure); 2 for every untrustworthy input (malformed, duplicate
  author/fragment, shared artifact/evidence/inode, parent symlink, path
  escape/symlink, artifact/evidence digest mismatch, missing/empty evidence,
  missing artifact, false pass, false fail, missing class, candidate artifact,
  frozen tamper, etc.).
- Fragment schema is 9 required keys as implemented (`FRAGMENT_FIELDS`):
  `author, class, artifact, sha256, command, exit_code, verdict, evidence,
  evidence_sha256`. Behavior wins over prose (QUALITY Q2); the header at the last
  read lists the same nine.
- Selftest: 32→35 cases across the read window (35 at the last read), each
  invoked as a real subprocess and asserted on return code and finding id; includes clean, digest mismatch,
  duplicate fragment/author, shared artifact/evidence/claim/inode, missing
  evidence/artifact/class, false pass, honest fail, false fail, path
  escape/absolute/symlink/parent-symlink, FIFO evidence, malformed
  manifest/fragment, schema, empty manifest, non-regular fragment, missing
  manifest, non-directory root, candidate artifact, and four frozen cases (clean,
  tampered, incomplete pins, verdict mismatch). Temp root is hard-coded
  `dir="/var/tmp"`.
- Pinned values: `tests/fixtures/r13-cert-frozen/` is the committed snapshot.
  At the **last** read it held `expected.json` (743 B) plus `manifest.json`, two
  fragments, two installed fixtures and two evidence files; `expected.json` names
  all seven inputs with sha256 and `verdict: "clean"`. This seat recomputed the
  seven digests with `sha256sum` and all equal the pins — a read-time consistency
  check, **not** a gate run. Earlier in the window the same directory had no
  `expected.json`; the file landed while the draft was being written.
- Scope limits that the row must not overstate: the gate checks consistency, not
  truth; `expected.json` is caller-supplied and not self-authenticated; there is
  **no fixed installed-tool allowlist** (the manifest + `--root` define the
  measured set; only `cand-` basenames are rejected by `artifact-candidate`); a
  clean result is not deletion authorization or tool safety.
- Two evidence layers, both landed by the last read: the tool's embedded
  `--selftest` (32→35 cases across the window) and the external black-box replay
  `tests/fixtures/r13-cert-evidence.py` (sha256 `3a3535da…`, 196 lines; 5 named
  checks: `selftest`, `external-clean`, `external-digest-mismatch`,
  `frozen-clean`, `frozen-tampered`; scratch
  `tempfile.mkdtemp(dir="/var/tmp")`; exit 0/1/2).
  The replay is the registry self-test: it invokes only the documented CLI and
  asserts rc + finding ids. The embedded selftest is capability evidence in the
  tool itself. Neither grants certification.

### r13-2 — `souji-repo-structure` (probe) + `r13-repo-structure` (gate, C3)

Read at sha256 `6be5e3217e1e3290fe879f549866aa6cecb9d91ea70791eb1c84a98eacaa445c`
(tool, 02:18) and `6c94f7fcce1c8f4c962bedce018303446530727f89f33ecd1f61fb32e28aa729`
(fixture, 02:16). Both were still being edited in the read window.

- Probe: `--repo PATH`; exactly one guarded `git -C PATH -c
  maintenance.auto=false -c maintenance.autoDetach=false ... repo structure
  --format=lines`, with `GIT_OPTIONAL_LOCKS=0`, `GIT_NO_LAZY_FETCH=1`,
  `GIT_TERMINAL_PROMPT=0`; refuses promisor/partial-clone repos before the walk;
  emits `probe.status=ok`, `probe.git_version`, `probe.command` and the command's
  28 keys; writes no scratch file.
- Exit map: 0 ok; 2 usage/git-missing/unusable-or-promisor repo; 3 capability
  absent (`git repo structure -h` lacks `repo structure`/`lines`); 4 config
  unreadable, structure nonzero, or `objects.commits.count=` absent.
- Gate: `r13-repo-structure.sh --selftest [--probe PATH]`; pinned ids
  `SOUJI-R13-STRUCT-{manifest-control,write-free,object-metrics,bogus-repo}`
  (`SELFTEST_EXPECTED_IDS` at fixture lines 626–631) plus
  `SOUJI-R13-STRUCT-promisor-refusal`, appended only in `--probe` mode
  (632–634). Final line is `selftest=PASS ids=4/4` for the baseline arm and
  `ids=5/5` for the probe arm. The fixture uses hard-coded `/var/tmp` scratch
  (line 159), a positive detector control (content/stat/mtime deltas), a full
  `.git` path/content/stat manifest before/after, and a measured command bounded
  by `timeout 120`. Without `--probe` it runs the raw baseline command (the
  r12-deferred capability); with `--probe` it runs the lane tool and parses its
  output without copying it.
- Pinned values are fixture constants and case expectations, not metric values
  from a live repo. **The observed run file does not exist yet**; L1 must commit
  it and name it in the row (proposed `tests/results/r13-repo-structure.txt`).

### r13-3 — `souji-quarantine` bounds + `r13-quarantine-bounds` (gate, C2)

- The tool row above is updated in place (exit vocabulary unchanged); the Q8 fix
  is the in-flight diff described in §2.4 (fixed `timeout --kill-after=10` bounds,
  special-file/symlink/device refusal before reading, one-device staging,
  fail-closed with residue preserved, no deletion after timeout, engine forced to
  the installed `souji-verify.sh` unless a fixture pins `SOUJI_VERIFY_BIN`).
- The gate landed at the last read:
  `tests/fixtures/r13-quarantine-bounds.sh` (sha256 `dd4a29ee…`, 271 lines).
  CLI `--tool PATH` (default the installed tool; `SOUJI_QUARANTINE_BIN` honored),
  `--verify PATH` (pins `SOUJI_VERIFY_BIN`), `--case ID …` (default all five),
  `-h`. No `--selftest` flag: the default run **is** the self-test over an
  isolated `mktemp -d /var/tmp/r13-qbounds.XXXXXX` repo.
- Cases and stable ids: `R13Q8-01` regular stale file → DELETED; `R13Q8-02`
  FIFO target → `DRY-RUN-BLOCKED special-file-refused`; `R13Q8-03` FIFO
  descendant → `special-descendant`; `R13Q8-04` delayed `mv` →
  `STAGE2-FAILED mv-timeout`; `R13Q8-05` delayed `sha256sum` →
  `NOT-AUTHORIZED digest-timeout`. The clock is compressed by a PATH `timeout`
  shim that rewrites the tool's fixed bound to 2s with kill-after 1; the shim
  only accepts the documented `timeout --kill-after=N DURATION` shape, so a tool
  that never calls `timeout` (the baseline) is caught, not passed.
- Exit map: 0 every selected case PASS; 1 any case FAIL; 2 usage/environment
  (missing `timeout`/`mv`/`sha256sum`/tool/engine). The header promises a `HANG`
  token, but the code emits only `PASS`/`FAIL` and the outer `timeout 20` turns a
  baseline hang into `FAIL` on the rc expectation. Record the code behavior
  (QUALITY Q2), not the header's `HANG` wording.
- Red-before: the same fixture with `--tool <baseline copy>` must exit 1
  (`R13Q8-04`/`R13Q8-05` fail on rc 124 vs wanted 3; `R13Q8-02`/`03` fail on the
  missing refusal tokens); the installed arm must exit 0. A fixture that passes
  on both is not a gate for this change and must be rejected at integration.
- Two conformance caveats: there is no pinned id-set equality, so deleting a
  case silently reduces `SUMMARY total=`; and the fixture sets
  `SOUJI_QUARANTINE_ALLOW_LIVE=1` for its isolated repo because a baseline copy
  under `/var/tmp` derives its live root as `/var`, which would otherwise trip
  exit 4. The allow-live value is bounded to the scratch repo it passes as
  `$REPO`; it must never be set for a live-fleet path.
- Write scope: `/var/tmp/r13-qbounds.XXXXXX` only, removed by trap; inner repo
  and fleet fixture inside it; the receipt engine is pinned to the installed
  `tools/souji-verify.sh` unless `--verify` overrides.

## 5. Missing-baseline and conformance debts (must stay visible in the rows)

| id | debt | evidence | consequence for the row / L1 |
|---|---|---|---|
| D1 | Code `1` is overloaded: it means *failed* for a selftest assertion but *could-not-evaluate* for missing dependency/internal setup, in verify/vault/census/quarantine | selftest-fail: `tools/souji-verify.sh:1282`; `tools/souji-vault-verify.sh:1588`; `tools/souji-census.sh:791`; `tools/souji-quarantine.sh:1553`. setup/dep: `tools/souji-verify.sh:1226,1308-1309`; `tools/souji-vault-verify.sh:1444,1623-1624`; `tools/souji-census.sh:346,514,818-819`; `tools/souji-quarantine.sh:611,1307-1309,1519` | rows are `probe`; promotion to gate requires moving setup/dep paths to `2` so `1` means only failed |
| D2 | Four embedded selftests do not compare an expected id-set or tally; a deleted case only lowers a printed count | `tools/souji-verify.sh:1281`; `tools/souji-vault-verify.sh:1587`; `tools/souji-census.sh:790`; `tools/souji-quarantine.sh:1513` | pins are absent; do not present these as Gate-standard self-tests |
| D3 | Four embedded selftests write under `${TMPDIR:-/tmp}`, which defaults to `/tmp` | Q4 (`corpus/QUALITY.md:28`) test: `grep -c 'TMPDIR:-/tmp'` → 0 required; the tools have it at lines 1105/1308/516/1247 | Q4 deviation recorded in write-scope cells; r13 fixtures must hard-code `/var/tmp` (r12 gate and r13 fixtures do) |
| D4 | No frozen snapshot/revision pin for the four installed probes | they grade live surfaces; protocol 403–410 | if promoted, they need a committed input snapshot + expected verdict; today their runs name no revision |
| D5 | `r13-cert-frozen/expected.json` landed **during** this read window, after first being absent | `find tests/fixtures/r13-cert-frozen -type f` (02:18 vs last read); pins recomputed equal by this seat | row may name the pinned path; L1 still must run `--selftest` and commit the transcript — no green tally is claimed here |
| D6 | `r13-quarantine-bounds.sh` landed during the read window | last read: sha256 `dd4a29ee…`, 271 lines, sha printed by `sha256sum` | row may name the path; L1 still must run it and commit `tests/results/r13-quarantine-bounds.txt` |
| D7 | Census compare baseline is caller-supplied, not committed | `tools/souji-census.sh:359-361,414-418` | census stays a probe even though compare can exit 3 |
| D8 | The bounds fixture has no pinned id-set equality; deleting a case silently lowers `SUMMARY total=` | fixture runs a hard-coded `for id in R13Q8-01 … R13Q8-05` loop and prints `SUMMARY total=<ran>`; no expected-list comparison | conformance debt like D2; do not present it as a Gate-standard self-test until the list is pinned |
| D9 | The bounds fixture header promises `HANG`, the code emits only `PASS`/`FAIL` | header lines 14, 25, 36–37 vs `finish_case` (only PASS/FAIL) and `SUMMARY`; a baseline hang becomes rc 124 → FAIL | registry row records the code behavior; the header should be corrected by its author, not silently trusted |

D1–D4 and D7–D9 are facts read from source. D5–D6 record files that landed
during the read window, observed by `find`/`ls`/`sha256sum` at the stated times —
timestamps, not predictions.

## 6. Advisory receipts and certification OFF (why these rows grant nothing)

Deletion certification is **OFF**. The registry is an interface inventory, not an
authorization. The evidence chain:

- `SCORECARD.md` §Tool certification: "Receipts are advisory until the r10
  hardening closes the classes" (line 70); the r12 correction says the r11
  re-certification "was NOT granted — the certifier evidence was compromised
  (shared relay, verdicts on non-installed bytes)" and "Deletion authorization
  stays OFF; receipts stay advisory until a no-relay re-certification passes"
  (lines 72–77).
- `census/round-13/claims.json` records the round's own bound:
  `"certification":"OFF; integrity validity does not certify receipt tools for
  deletion"`.
- `corpus/QUALITY.md` Q18 (`:42`) makes the split explicit: "Certification
  integrity and tool safety are separate verdicts. A passing integrity gate never
  grants deletion authority."
- Concretely, for each row:
  - `souji-verify` / `souji-vault-verify` emit `SAFE`/`NOT-SAFE` as **data** and
    exit 0; a `SAFE` is a receipt candidate the operator still gates through
    quarantine + hold + second check. A `NOT-SAFE` is the default, not a tool
    failure.
  - `souji-census` and `souji-repo-structure` are measurements. Size counts are
    not reclaimable bytes and neither tool has a delete verb.
  - `souji-quarantine` deletes only inside a quarantine date directory after a
    second check; its exit 0 is not an operator approval.
  - `souji-cert-evidence` clean means "the declared fragments are internally
    consistent and digest-pinned". It cannot authenticate `author`, prove the
    recorded `command` ran, establish full class coverage, or tell an installed
    artifact from a candidate except by the `cand-` basename rule. Its header
    states that it "does not maintain a fixed installed-tool allowlist" and that
    a clean result grants no certification. A clean gate is therefore Q18's
    integrity verdict, not deletion certification.
  - The gate fixtures (`r12-maintenance-guard`, `r13-repo-structure`,
    `r13-quarantine-bounds`) prove a bounded mechanism; they do not authorize a
    removal.
- What would move certification is out of this draft's scope: a no-relay
  re-certification over installed digests with class suites, adjudicated by the
  operator. This draft does not claim it.

## 7. Exact bounded final checks for L1 (after the wave lands; none run here)

Run from `/home/vgpnk/Projects/shokunin/souji-shokunin`. Expected values are
design targets unless marked observed.

1. **Registry shape**: after applying the table,
   `grep -cE '^\| (souji-|r12-|r13-)' SKILL.md` → `9`; every row has 8 columns
   (`awk -F'|' '/^\| (souji-|r12-|r13-)/{print NF-2}' SKILL.md | sort -u` → `8`).
2. **cert-evidence fixture**: `test -f tests/fixtures/r13-cert-frozen/expected.json; echo $?`
   → `0` before any selftest is trusted.
3. **cert-evidence gate**: `python3 -m py_compile tools/souji-cert-evidence.py`
   → exit 0; then `python3 tools/souji-cert-evidence.py --selftest; echo rc=$?`
   → `rc=0` and last line `selftest: N/N passed` where N is the landed case count
   (35 at the last read; recount with
   `grep -cE '^\s+(case|frozen_case)\("' tools/souji-cert-evidence.py`). Do not
   pin N in the registry row; the rc and the asserted finding ids are the
   authority. Then the black-box replay:
   `python3 tests/fixtures/r13-cert-evidence.py; echo rc=$?` → `rc=0` and
   `fixture: 5/5 checks passed` (`selftest`, `external-clean`,
   `external-digest-mismatch`, `frozen-clean`, `frozen-tampered`).
4. **cert-evidence frozen run**: run `--frozen tests/fixtures/r13-cert-frozen`
   → exit 0 `clean`; mutate a copied snapshot input and confirm
   `snapshot_tampered`, exit 2 (the selftest's frozen-tampered case already does
   this, so this is a L1 spot-check of the committed fixture, not a substitute).
5. **quarantine bounds gate (red before, green after)**:
   `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show
   31984f4:tools/souji-quarantine.sh > /var/tmp/souji-quarantine.r13-baseline.sh`
   then `bash tests/fixtures/r13-quarantine-bounds.sh --tool
   /var/tmp/souji-quarantine.r13-baseline.sh; echo rc=$?` → `rc=1` with
   `R13Q8-04`/`R13Q8-05` (and normally `02`/`03`) reported FAIL, never all PASS;
   then `bash tests/fixtures/r13-quarantine-bounds.sh; echo rc=$?` → `rc=0`,
   `SUMMARY total=5 failed=0`. Record both transcripts under
   `tests/results/r13-quarantine-bounds.txt` and delete the baseline copy (it is
   a `/var/tmp` artifact, not repo content). The fixture's own trap removes its
   scratch tree; the baseline copy is L1's to remove.
6. **repo-structure gate**: `bash tests/fixtures/r13-repo-structure.sh --selftest; echo $?`
   → `0` `selftest=PASS ids=4/4`; then with the probe:
   `bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh; echo $?`
   → `0` `selftest=PASS ids=5/5` (the extra id is
   `SOUJI-R13-STRUCT-promisor-refusal`). Commit both transcripts as
   `tests/results/r13-repo-structure.txt`.
7. **probe contract**: `bash tools/souji-repo-structure.sh --help; echo $?` → 0;
   `bash tools/souji-repo-structure.sh --repo /nonexistent; echo $?` → 2 and no
   stdout key. Do not run it on a live lane repo; the fixture is the evidence.
8. **r12 gate unchanged**: `bash tests/fixtures/r12-maintenance-guard.sh --selftest; echo $?`
   → 0 `selftest=PASS ids=6/6`.
9. **embedded selftests (capability only)**:
   `bash tools/souji-verify.sh --selftest; bash tools/souji-vault-verify.sh --selftest;
   bash tools/souji-census.sh --selftest; bash tools/souji-quarantine.sh --selftest`
   each → exit 0 with last line `selftest: N checks, 0 failed`; **record N** in the
   round evidence (there is no pinned N; do not compare to the stale r10 counts).
10. **digest honesty for C1**: `sha256sum tools/souji-verify.sh
    tools/souji-vault-verify.sh tools/souji-quarantine.sh tools/souji-census.sh`
    and compare to the fragments actually admitted; never copy the digests from
    this draft. A mismatch is the gate's `artifact-digest-mismatch`, not a prose
    correction.
11. **new-fixture isolation (Q4)**: for each new shell fixture,
    `grep -c 'TMPDIR:-/tmp' <f>` → `0`; `grep -c '/var/tmp' <f>` ≥ `1`; confirm
    the `trap ... rm -rf` line. The four installed tools' embedded selftests fail
    the first grep; that is D3, already recorded, not a new defect to "fix" inside
    this round's registry work.
12. **shell lint (Q9)**: `shellcheck -S warning tools/souji-quarantine.sh
    tests/fixtures/r13-quarantine-bounds.sh tests/fixtures/r13-repo-structure.sh`
    → exit 0 for the new/changed shell. No shellcheck for the Python gate.
13. **no SKILL drift**: `git -C ... diff -- SKILL.md` shows only the registry
    paragraph/table replacement plus the r13 sections L1 already owns; no duplicate
    row names:
    `grep -c '^| souji-verify |' SKILL.md` → 1 (same for each name).

## 8. Limitations of this draft (facts vs inference)

- **Read, not run**: every exit map, selftest case id and scratch path is read from
  the script text. No selftest was executed (round contract). The r10 counts cited
  are committed historical observations, not this round's measurements.
- **Moving target**: six shared files and `tools/souji-quarantine.sh` were modified
  by other seats during this read window; `souji-cert-evidence.py` produced five
  observed digests and `souji-repo-structure.sh` shrank from 18585 to 8703 bytes
  in the same window. `tests/fixtures/r13-cert-frozen/expected.json` was absent at
  02:18 and landed by the last read. Digests name what I read, not what L1 will
  commit.
- **Late-landing files**: `tests/fixtures/r13-quarantine-bounds.sh` and
  `tests/fixtures/r13-cert-evidence.py` appeared between the first and last
  reads; the bounds fixture was read at 271 lines / `dd4a29ee…`, the replay at
  196 lines / `3a3535da…`. They may change again before L1 runs them; no run was
  performed here.
- **Classification is inference from the protocol definition plus code**, not an
  empirical claim that the tools are safe or unsafe. Marking a tool `probe` is a
  registry-schema statement; it does not assert its verdicts are correct.
- **No independence claim**: this seat is lane-dispatched; it cannot supply the
  non-author admission sample that closure reserves for the orchestrator.
- **No operator-sweep content was read**; no credentials or secrets were inspected;
  no commits, builds, lints or tests were made by this seat.
