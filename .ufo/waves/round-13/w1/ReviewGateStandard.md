# ReviewGateStandard — round 13 (souji-r13-w1)

Seat: `SoujiR13.ReviewGateStandard` (reviewer, leaf, read-only). Lane root: `/home/vgpnk/Projects/shokunin/souji-shokunin` (HEAD `31984f4`, per `census/round-13/before.json:measured_commit`).
Axes: calibration, operability, coverage.
Execution: none. No build, lint, test, or fixture run. No installs or upgrades. Reads only.
Standard read at fleet root `/home/vgpnk/Projects/shokunin/PROTOCOL.md` (working tree; `git status` clean for PROTOCOL.md, PROTOCOL-APPENDIX.md, SCORECARD.md; PROTOCOL.md last changed at `7c5b34f`; fleet HEAD `4c8f2f6`).

## 1. Verdict on the question asked

- The canonical standard is PROTOCOL.md `## Gate standard` (lines 375-423). It defines a **gate** (committed, re-runnable, compares surfaces against persisted expected values, returns a verdict) and a **probe** (a tool that cannot fail, registered as one). Exit `0`=clean, `1`=failed, any other code = could-not-evaluate unless declared (lines 377-384).
- Two obligations are triggered by a mutable input: a self-test over isolated fixtures with committed expected values (385-389), and a **frozen run** over a committed input snapshot whose `expected.json` MUST pin the sha256 of every snapshot input; a mismatch is `snapshot_tampered` (could-not-evaluate) (390-397).
- A child lane's registry row lives in its own `SKILL.md` with eight fields (398-403). Closure grades no gate conformant until that row exists (418-421).
- **Recommendation:** the round-13 cert-evidence validator (`tools/souji-cert-evidence.py`, spec item `EvidenceGate`) is a gate whose verdict depends on a mutable manifest, fragments and installed tool bytes. It therefore REQUIRES a digest-pinned frozen snapshot, and that snapshot is not currently in its write scope (Finding F1).

## 2. Classification of planned round-13 artifacts

Classification uses the PROTOCOL definitions only. "Action" means a mutating tool; PROTOCOL does not define that class, so this is an inference (I-1).

| artifact (seat) | class | registry row (SKILL.md, child-lane home) | self-test | frozen snapshot | pinned values path |
|---|---|---|---|---|---|
| `tools/souji-cert-evidence.py` (EvidenceGate) | gate: verdict depends on mutable manifest, fragments, installed bytes | REQUIRED, `gate` | REQUIRED, literal finding ids and exit codes (385-389) | REQUIRED: committed snapshot + `expected.json` digests (390-397) | NOT YET DEFINED; must be a path under `tests/fixtures/r13-cert-evidence/` (see F1, §3) |
| `tools/souji-repo-structure.sh` (SizeProbe) | probe: read-only report, no compare to pinned value (inference, I-2) | REQUIRED, `probe` (379, 398) | recommended; 385 is worded for gates (I-3) | not required unless it grades a size against a pinned number; if it does, it becomes a gate | none unless it becomes a gate |
| `tools/souji-quarantine.sh` (BoundQuarantine) | action (mutates); not gate/probe by definition (I-1) | not required by PROTOCOL; SKILL should state the exemption so no reader credits it with verdict authority | fixture `tests/fixtures/r13-quarantine-bounds.sh` is a test, not a gate | n/a | n/a |
| `census/round-13/registry-draft.md` (RegistryDraft) | documentation only | rows must land in `SKILL.md`, which RegistryDraft does not own; L1 integrates | n/a | n/a | n/a |
| `scripts/sources-census.sh validate ... souji` (before.json `source_census`) | fleet-owned script reading mutable `corpus/SOURCES.md` | not a souji gate; cite output only as committed evidence (416-417, 407-408) | n/a | if cited as a verdict, the committed output needs its input digest | n/a |
| `tests/fixtures/r12-maintenance-guard.sh` (existing, registered) | gate; inputs are git binary behaviour in a hermetic `mktemp -d /var/tmp/...` root, not a fleet artifact (I-4) | registered: `SKILL.md:106` | `SELFTEST_EXPECTED_IDS` at line 130 | not mandated by 390-397 (I-4) | script body (acceptable; see F5) |

## 3. Findings (ranked)

**F1 (HIGH, calibration/operability) — the mandated frozen snapshot has no owner.**
- `EvidenceGate` owns only `tools/souji-cert-evidence.py` and `tests/fixtures/r13-cert-evidence.py` (spec item `EvidenceGate`, `.ufo/waves/round-13/w1-spec.json`, Target text).
- PROTOCOL.md:391-392 requires "a run over a committed input snapshot with its committed expected verdict"; 395-396 requires `expected.json` to pin every snapshot input digest.
- A single `.py` fixture that builds its inputs in a mktemp dir produces no committed snapshot, so the obligation cannot be met by construction.
- Fix: either add `tests/fixtures/r13-cert-evidence/**` (snapshot inputs plus `expected.json`) to the seat's write scope, or name L1 as the committer of that path. Either way the snapshot must be committed in a commit separate from the validator code (see §4, anchor).

**F2 (HIGH, calibration) — the live path reads mutable inputs with no pin.**
- The spec's live interface is `gate --root PATH --manifest PATH`. It reads an explicit manifest of fragment paths, each carrying `sha256`, `command`, `exit_code`, `verdict` and `evidence` (spec, EvidenceGate).
- Nothing in the spec pins the manifest, the fragments, or the evidence files. A hand-edit of any of them changes the verdict silently. This is the r11 class (`corpus/lessons/round-11.md:14`, M40 in `corpus/lessons/round-12.md:102`).
- PROTOCOL.md:393-394: a verdict must name the revision it grades. The spec's verdict output does not require `git rev-parse HEAD` or a worktree-dirty flag.
- Fix: the frozen path verifies every digest in `expected.json` before any verdict (mismatch → `snapshot_tampered`, exit 2, per PROTOCOL.md:396 and Appendix row "Frozen inputs", `PROTOCOL-APPENDIX.md:45`). The live path prints `revision=<HEAD>` and `worktree_dirty=<0|1>`.

**F3 (HIGH, operability) — registry rows for the round tools are not specified, and the SKILL table has the wrong shape.**
- PROTOCOL.md:401-403 lists eight row fields: name, `gate|probe`, entry command, verdict map (code → class), self-test command and spelling, pinned-value path, write scope, owner.
- `SKILL.md:104-106` has six columns: `name | kind | entry / self-test | pinned values | write scope | owner`. The verdict map appears only in prose at line 102, and self-test spelling is folded into the entry column.
- Only one row exists (`r12-maintenance-guard`, line 106). No row exists for the three round-13 tools.
- Closure consequence (PROTOCOL.md:418-421): no gate is conformant until its row exists at the registry home. The SKILL edit belongs to L1, since `RegistryDraft` does not own `SKILL.md`.
- Fix: add the verdict-map and self-test-spelling columns, or put all eight fields in each row, and write one row per gate or probe.

**F4 (MEDIUM, calibration) — the exit map is not declared.**
- The spec says `clean=0 failed=1 could-not-evaluate=2` with stable finding ids. It does not say which contradiction maps to which code.
- PROTOCOL.md:380-384 requires a declared map, and an undeclared nonzero code reads as could-not-evaluate.
- Precedent: SCORECARD.md:194 maps missing input, parse error, bad usage and `snapshot_tampered` to `2`.
- Proposed map (I-5), see §4.

**F5 (MEDIUM, calibration) — self-test independence is not required by the spec.**
- PROTOCOL.md:385-389 requires committed expected values "independent of the recomputation", and says "a helper-only or model-only self-check does not satisfy this clause".
- The r12 pattern (`tests/fixtures/r12-maintenance-guard.sh`, `SELFTEST_EXPECTED_IDS` at line 130, asserted at line 37-41) is the template to copy.
- Fix: literal expected finding ids and exit codes in the committed fixture, never derived by running the gate.

**F6 (LOW, calibration) — prior evidence for the r12 fixture does not match current bytes.**
- `census/round-12/critic.md:26-28` cites `tests/fixtures/r12-maintenance-guard.sh:35` as `${TMPDIR:-/var/tmp}` and says the scratch path is unfenced.
- At `31984f4` and in the worktree, line 35 is a comment, `TMPDIR` appears only in the comment at line 48 ("TMPDIR deliberately ignored"), and the scratch root is `mktemp -d /var/tmp/souji-r12-maintenance.XXXXXX` at line 68, with a trap at line 71.
- `critic.md:28` (the "checks only `after == expect`" claim) is also superseded: lines 44-45 now require `before==2` AND `after==expect`.
- Inference (I-6): the critic read an earlier draft. Do not carry its HIGH findings into round 13 without re-checking the current bytes.

**F7 (LOW, operability) — `tools/souji-repo-structure.sh` needs a read-only proof.**
- S006 (`corpus/lessons/round-12.md:191`): `GIT_OPTIONAL_LOCKS` prevents index refresh. The S005 entry says `git repo structure` is EXPERIMENTAL (`round-12.md:187`).
- The round-12 C3 rejection rested on "whether `git repo structure` writes or takes locks was not tested" (`round-12.md:133`). The round-13 probe is the test that was missing.
- If the probe is registered as a probe, its self-test must demonstrate no write: fixture `.git` snapshot via `find .git -newer`, run with `GIT_OPTIONAL_LOCKS=0`, diff empty. This is a proposal for L1, not run here.

## 4. Recommended digest-pinned expected inputs for the validator

Layout (proposed):
```
tests/fixtures/r13-cert-evidence/<case>/
  manifest.json                 # explicit fragments array
  fragments/<author>.json       # one author per fragment
  evidence/<relpath>            # evidence files
  installed/<tool>              # fixture copy of the installed bytes; NOT live tools/
  expected.json                 # pins + expected verdict
```

`expected.json` (proposed fields, shaped after `.ufo/waves/round-15/frozen/r15-pre-003400/expected.json`, which pins inputs in an `inputs` map):
```json
{
  "schema": "souji-cert-evidence-expected-v1",
  "gate": "tools/souji-cert-evidence.py",
  "pinned_at_commit": "<sha of the commit that adds expected.json>",
  "inputs": { "manifest.json": "<sha256>", "fragments/<author>.json": "<sha256>", "evidence/<relpath>": "<sha256>", "installed/<tool>": "<sha256>" },
  "expected": { "exit": 1, "finding_ids": ["<literal ids>"] }
}
```
- The frozen path checks every listed input, and rejects any file under the case directory that is absent from `inputs` (unlisted file → `snapshot_tampered`). A case with no `inputs` map reads `unpinned (legacy)` and is not clean.
- The live path (`--root`, `--manifest`) never reads `expected.json`. It hashes the live `tools/<tool>` and prints the revision.
- **Anti-self-blessing:** a regenerated pin that blesses an edit must fail. PROTOCOL-APPENDIX.md:44 records that `sha256(rounds[0:k])` plus a commit anchor kills this mutant (`history_pin_unanchored`). Analogously, `pinned_at_commit` should name a commit that changes only `expected.json`, and the reviewer re-derives the digests with `sha256sum` independently of the gate.

Proposed exit map for `souji-cert-evidence.py` (I-5):
- `0` clean: all fragments valid; installed digests match; evidence paths resolve as regular files; no contradiction.
- `1` failed: `installed_digest_mismatch`; `shared_fragment_or_duplicate_author`; `pass_with_nonzero_exit`; `fail_with_zero_exit` (false success); `reported_fail` (honest evidence; certification refused).
- `2` could-not-evaluate: manifest absent or unparseable; fragment absent; evidence path absent, symlink, or non-regular; `snapshot_tampered`; `unpinned (legacy)`; bad usage (argparse already exits 2).
- Undeclared codes are could-not-evaluate per PROTOCOL.md:380-382.

## 5. Proposed final checks for L1 (not run here)

1. `python3 tools/souji-cert-evidence.py --selftest; echo $?` → `0`, last line `selftest=PASS ids=<n>/<n>`.
2. `python3 tools/souji-cert-evidence.py --frozen tests/fixtures/r13-cert-evidence/<case>; echo $?` → equals `expected.exit`.
3. Tamper check in a `mktemp -d /var/tmp/...` copy with `trap` cleanup: flip one byte in an input, expect exit `2` with `snapshot_tampered`.
4. Independent digest re-derivation: `sha256sum -c` over every `inputs` entry, run by L1 outside the gate.
5. Live absent-manifest run: `python3 tools/souji-cert-evidence.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --manifest <absent>; echo $?` → `2`. Certification stays OFF.
6. SKILL shape: each new row has the eight PROTOCOL fields, one row per tool, no copied expected values.
7. Repo hygiene for the commit: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse --show-toplevel`; stage named paths only; `git -C ... -c maintenance.auto=false commit -- <paths>`.
8. Q9 (`corpus/QUALITY.md:33`): `shellcheck -S warning` on each new shell script; `-S error` is not the gate.

## 6. Limitations and inferences

- I-1: PROTOCOL does not define an "action tool" class. Classifying `souji-quarantine.sh` as outside gate/probe is an inference.
- I-2: `souji-repo-structure.sh` is a probe only if it cannot fail beyond setup. Its final code must confirm that.
- I-3: The self-test clause (385-389) is worded for gates. Requiring one for probes is a recommendation.
- I-4: The r12 gate's inputs are git-behaviour inputs, not a fleet artifact, so 390-397 is not triggered. Inference from the header (`tests/fixtures/r12-maintenance-guard.sh:1-10`).
- I-5: The exit map in §4 is my proposal; PROTOCOL fixes only the default codes.
- I-6: Critic staleness (F6) is inferred from the byte mismatch; I did not check git history for the critic's source revision.
- Limitation: `w1-spec.json` tool output truncated the EvidenceGate line at 768 bytes ("…stable finding ids and …"). The text I used is the 768-byte prefix plus the Acceptance section. The truncated tail was not read.
- Limitation: I did not read `SHONEN.md`, `SCORECARD.md` round-13 rows, or the `census/round-13/` drafts other than `before.json`; those are other seats' slices.
- Limitation: the fleet `scripts/sources-census.sh` was not read (fleet-owned, out of scope).
- Tool installs or upgrades: none.

Report: .ufo/waves/round-13/w1/ReviewGateStandard.md
