# R13 w1 — RegistryDraft (gate-registry rows for four installed tools + r13 entries)

Seat: `SoujiR13.RegistryDraft` (executor, leaf). Axes: calibration, operability,
coverage. This seat is lane-dispatched and is **not** an independent non-author
verifier; it claims no such status. Certification remains **OFF**.

## Files changed

- `census/round-13/registry-draft.md` (new) — the deliverable: the
  exact 8-field replacement table for the SKILL gate registry, per-row evidence,
  the three r13 entries, the conformance-debt table, the advisory/OFF explanation,
  and the L1 check list.
- `.ufo/waves/round-13/w1/RegistryDraft.md` (this report).

No existing SKILL.md, shared bookkeeping, sibling-repo, operator-sweep or census
file was modified. No commit, build, lint or test was run (round contract). No
tool was installed or upgraded.

## What the draft decides, and why

### 1. The four installed tools are registered as **probes**, not gates

PROTOCOL §Gate standard (lines 390–392) defines a gate as reading surfaces and
comparing them to expected values persisted in its own repo; "A tool that cannot
fail is a probe." All four fail the gate test on two independent grounds read
from source:

- **They cannot fail on their surface verdicts** (census `--compare` is the one
  differential exception). `souji-verify` and `souji-vault-verify` end `exit 0`
  after emitting per-target verdicts (`tools/souji-verify.sh:1316`;
  `tools/souji-vault-verify.sh:1632`); NOT-SAFE is data by design
  (`tools/souji-verify.sh:12`, H6 assert at `:1255`). `souji-census` emits a
  census and exits 0 (`:827`); only the caller-supplied `--compare` mode exits 3
  on a delta (`:466`). `souji-quarantine` is a mutating operation whose receipt
  authority is the child engine (`:5–8` at 31984f4).
- **Code 1 is overloaded.** It means *failed* for a selftest assertion
  (`souji-verify.sh:1282`, `souji-vault-verify.sh:1588`, `souji-census.sh:791`,
  `souji-quarantine.sh:1553`) but *could-not-evaluate* for a missing dependency or
  internal setup (`souji-verify.sh:1226,1308-1309`;
  `souji-vault-verify.sh:1444,1623-1624`; `souji-census.sh:346,514,818-819`;
  `souji-quarantine.sh:611,1307-1309,1519`). The fleet convention reserves 1 for
  failed, so promotion to a gate requires moving setup paths to 2 first.

This is a schema classification, not a claim that their verdicts are correct or
incorrect.

### 2. Exact rows, exit maps, selftest flags, pinned paths, write scopes

The draft's §3 is a copy-paste replacement table with 9 rows × 8 fields
(name, kind, entry, verdict map, self-test command + spelling, pinned-value path,
write scope, owner). Load-bearing cells:

- `souji-verify`: `--selftest`; in-script case ids F1–F10/E1–E8/H1–H6; **no
  pinned id-set or tally**; scratch `${TMPDIR:-/tmp}` at `:1105`.
- `souji-vault-verify`: `--selftest`; F/V/H ids; no pinned tally; scratch
  `${TMPDIR:-/tmp}` at `:1308`; advisory `obsidian-cli` under timeout (header 5–11).
- `souji-census`: `--selftest`; compare asserts 0/3/2 at `:707–756`; no committed
  census baseline + digest; temp `${TMPDIR:-/tmp}/souji-census-now.*` at `:418`;
  selftest scratch `:516`.
- `souji-quarantine`: exit map 0/3/4/1/2 from header 92–96 and code
  (`RC=3` at 399/525–579; `exit 4` at 624; final `:1569`); scratch `:1247`,
  err temp `:1519`; mutation only under `<repo>/.ufo-quarantine/<utc-date>/`.
- `r12-maintenance-guard`: gate; `--selftest`; `selftest=PASS ids=6/6`;
  `SELFTEST_EXPECTED_IDS` at fixture `:130–137`; `/var/tmp` scratch `:68`;
  observed run `tests/results/r12-maintenance-guard.txt`.
- r13 rows below.

### 3. The three r13 entries (plus their gate fixtures)

- **r13-1 `souji-cert-evidence` — gate.** CLI `--root/--manifest`, `--frozen`,
  `--selftest`. Exit 0 clean; 1 only `fragment-reported-fail`; 2 everything
  untrustworthy. 9 required fragment keys as implemented (`FRAGMENT_FIELDS`):
  author, class, artifact, sha256, command, exit_code, verdict, evidence,
  evidence_sha256. The committed frozen snapshot
  `tests/fixtures/r13-cert-frozen/` landed during the read window; `expected.json`
  pins all seven inputs and this seat recomputed the seven sha256 values **equal**
  (read-time consistency, not a gate run). The file produced five observed
  digests during the read window (`f2729f19…` → `5c86764d…` → `f64c0762…` → `90542347…`
  (32 cases) → `1b942b78…` (35 cases, last read)); L1 must reconcile the landed
  bytes. The external black-box replay `tests/fixtures/r13-cert-evidence.py`
  also landed (`3a3535da…`, 196 lines): five checks (`selftest`,
  `external-clean`, `external-digest-mismatch`, `frozen-clean`,
  `frozen-tampered`), exit 0/1/2, `/var/tmp` scratch only.
- **r13-2 `souji-repo-structure` — probe** (`--repo PATH`; exit 0/2/3/4, all
  non-zero classes could-not-evaluate; refuses promisor repos; no scratch file)
  and **`r13-repo-structure` — gate** (`--selftest [--probe PATH]`; pinned ids
  `SOUJI-R13-STRUCT-{manifest-control,write-free,object-metrics,bogus-repo}` at
  fixture `:626–631`, plus `promisor-refusal` appended only in `--probe` mode at
  `:632–634`; `ids=4/4` baseline, `5/5` probe; hard-coded `/var/tmp` at `:159`;
  measured command bounded by `timeout 120`).
- **r13-3 `souji-quarantine` bounds + `r13-quarantine-bounds` gate.** The tool row
  is updated in place; the in-flight diff (read at 02:19, uncommitted) adds fixed
  `timeout --kill-after=10` bounds (digest 120s/300s, mv 60s, engine 120s, rm
  120s, special scan 60s), special-file/symlink/device refusal, one-device
  staging, fail-closed with residue preserved, and removes the candidate-engine
  fallback (Q6). The gate fixture **landed during the window** (`dd4a29ee…`, 271
  lines): CLI `--tool PATH` / `--verify PATH` / `--case ID`, no `--selftest`
  flag (the default isolated `/var/tmp` run is the self-test), five stable case
  ids `R13Q8-01…05`, exit 0/1/2. Red-before rule: `--tool <baseline copy>` must
  exit 1 (04/05 fail on rc 124 vs wanted 3; 02/03 fail on missing refusal
  tokens); the installed arm must exit 0; a both-green fixture is not a gate and
  must be rejected. Two recorded caveats: the header promises `HANG` but the
  code emits only `PASS`/`FAIL` (D9), and there is no pinned id-set equality
  (D8).

### 4. Advisory receipts and OFF certification are stated, not implied

The draft quotes `SCORECARD.md:70,72–77` ("Receipts are advisory"; "Deletion
authorization stays OFF"), `census/round-13/claims.json` (`certification: OFF`),
and QUALITY Q18 (`corpus/QUALITY.md:42`). It states per row what a clean result
does **not** establish. For `souji-cert-evidence` specifically: consistency, not
truth; `expected.json` is a caller-supplied anchor; author labels are
unauthenticated; commands are never run; no fixed installed-tool allowlist
(header: "does not maintain a fixed installed-tool allowlist"); only `cand-`
basenames are rejected. A clean gate is Q18's integrity verdict, never deletion
authority.

## Proposed L1 checks (none run here)

The full list is §7 of the draft; the minimum discriminating set:

1. `test -f tests/fixtures/r13-cert-frozen/expected.json` → 0, then
   `python3 tools/souji-cert-evidence.py --selftest; echo rc=$?` → 0 and
   `selftest: N/N passed` (N = landed case count; do not pin N in the row), then
   `python3 tests/fixtures/r13-cert-evidence.py` → 0 `fixture: 5/5 checks passed`.
2. Red-before/green-after bounds:
   `git -C <lane> show 31984f4:tools/souji-quarantine.sh > /var/tmp/souji-quarantine.r13-baseline.sh`;
   `bash tests/fixtures/r13-quarantine-bounds.sh --tool /var/tmp/...` → 1 with
   `R13Q8-04`/`R13Q8-05` FAIL (not all PASS); then
   `bash tests/fixtures/r13-quarantine-bounds.sh` → 0 `SUMMARY total=5 failed=0`.
   Commit both transcripts under `tests/results/`.
3. `bash tests/fixtures/r13-repo-structure.sh --selftest` → 0 `ids=4/4`;
   add `--probe tools/souji-repo-structure.sh` → 0 `ids=5/5`.
4. `bash tests/fixtures/r12-maintenance-guard.sh --selftest` → 0 `ids=6/6`.
5. Four embedded selftests → each exit 0, last line `selftest: N checks, 0 failed`;
   record N; do not compare to the stale r10 counts
   (`census/round-10/S06-selftest-counts.txt`).
6. `sha256sum tools/souji-{verify,vault-verify,quarantine,census}.sh` at check
   time, compared to admitted fragments — never to digests copied from this
   report.
7. Q4/Q9: new shell fixtures `grep -c 'TMPDIR:-/tmp'` → 0, `grep -c '/var/tmp'` ≥ 1,
   trap cleanup; `shellcheck -S warning` → 0 for changed/new shell.

## Retained evidence (opened, not executed)

- Four installed tools at HEAD: `souji-verify.sh` sha256 `9adb1764…` (1316 lines),
  `souji-vault-verify.sh` `f9e778ca…` (1632), `souji-census.sh` `6a000c59…` (827),
  `souji-quarantine.sh` baseline `141c0fdc…` (1569; r13 diff uncommitted at read).
- `tests/fixtures/r12-maintenance-guard.sh` `a359070a…`.
- r13 read-time digests: `souji-repo-structure.sh` `958d45d7…` (changed again
  after the draft's first citation), `r13-repo-structure.sh` `922c3ff8…` (changed
  after first citation), `souji-cert-evidence.py` `1b942b78…` at 35 cases
  (`90542347…` at 32 was an intermediate read),
  `tests/fixtures/r13-cert-evidence.py` `3a3535da…` (196 lines),
  `tests/fixtures/r13-quarantine-bounds.sh` `dd4a29ee…` (271 lines),
  `r13-cert-frozen` pins recomputed equal.
- Exit-code and scratch-path lines are enumerated per row in the draft; the
  historical selftest counts are labelled stale observations, not pins.
- Worktree state at read: `M PROVINCE.md SHONEN.md SKILL.md corpus/QUALITY.md
  corpus/README.md corpus/SOURCES.md tools/souji-quarantine.sh`; SKILL's registry
  table moved from HEAD `:102–106` to working-tree `:118–122`.

## Risks and blockers

- **Moving worktree (risk, not blocker).** Other seats edited SKILL and shared
  docs and were writing the r13 tools during this seat's read window;
  `souji-cert-evidence.py` produced five observed digests. The draft names digests and says
  "reconcile at integration" rather than asserting final bytes.
- **Late-landing fixtures (risk, not blocker).** `r13-quarantine-bounds.sh`
  (271 lines, `dd4a29ee…`) and `r13-cert-evidence.py` (196 lines, `3a3535da…`)
  appeared after the first read; their rows are filled from the landed files but
  were not executed. Two recorded conformance caveats: the bounds fixture's
  header promises `HANG` while the code emits only `PASS`/`FAIL`, and it has no
  pinned id-set equality.
- **SKILL concurrency.** SKILL.md was modified by another seat while I was
  forbidden to edit it. The replacement table is provided as a fenced block with a
  content anchor; L1 must re-locate the paragraph and ensure no duplicate row
  names.
- **No execution by this seat (limitation).** Selftest tallies and expected
  verdicts in the draft are design targets or historical observations; the gate
  fixtures and the cert-evidence frozen run are L1's to execute and commit.

## Calibration notes (facts vs inference)

Facts: all line citations, hashes, exit statements, scratch paths, the frozen
pin equality, and the absent/present file states above were observed by reading
the stated files at the stated times. Inference: the gate/probe classification
and the class mapping of each exit code follow the protocol definition plus the
code; they are not an empirical claim about tool safety. No operator-sweep
content, credentials or session material was read.
