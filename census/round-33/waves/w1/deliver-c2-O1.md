# r33 C2 leg O1 — repair receipt (evidence-cache selftest scratch root)

Scratch: `/fast/scratch/hyaku/souji-r33/FixO1/` (clone `c` at 2d9bca55a9f042a2c9ed60a797a8069e74c41f46, origin removed).
Scratch commit: `1595c203cc34083bc67c0edb28c131bcb01cb3f6` (throwaway identity `scratch <scratch@invalid>`), tag
`r33-c2-o1` in the clone only. All Python run with `python3 -B`. Scratch removed after this receipt was written.

Patch: `.ufo/waves/round-33/w1/deliver-c2-O1.patch` = `git -C <clone> diff 2d9bca55a9f042a2c9ed60a797a8069e74c41f46`
(2 files, +13/-6). Apply with `git apply -p1`; the lane config sets `diff.mnemonicPrefix=true`, so regenerate the
diff with `git -c diff.mnemonicPrefix=false diff <rev>` if it must be regenerated.

## 1. Why the consumers depended on the cache tool's bytes

1. `census/round-21/run-acceptance.py:503` (base bytes) computed the cache-demo expectation from the **live** tree:
   `gate_sha = sha256_bytes(read_regular(root / "tools/souji-evidence-cache.py"))`, then required
   `gate.get("sha256") == gate_sha`.
2. `tests/fixtures/r22-result-oracle.py:17,96-103` re-grades the pinned r21 receipt
   (`census/round-21/final-out-S1.json`) through that runner with `root = ROOT`, ROOT being the lane checkout
   (`ROOT = Path(__file__).resolve().parents[2]`), not a clone at the payload's revision
   (`revision = ff425ab835614f38205426330b9cdb93fd267045`). The pinned payload records the r21 tool
   `sha256 dd279ba95eebd13a6674f79983cec286fd856aa6d7e0719bf551ae0fc08939d6`, so **any** edit to the live tool
   failed two literal positives.
3. `census/round-22/mutation-adequacy.py` requires the pristine runner to pass all 258 oracle cases, so it followed.
   This is the r32 a2 R2 statement: "census/round-21/run-acceptance.py:503 compares the live tool's sha256 with the
   frozen cache-demo payload" (`census/round-32/records/a2-repairs.txt`, R2) — the repair is not a tool revert but a
   correction of that comparison.

Mechanism reproduced in scratch (tool repair applied **without** the runner change, runner untouched):

```
$ git -C <clone> checkout -qf --detach 2d9bca5 && git apply --include=tools/souji-evidence-cache.py <patch>
$ python3 -B tests/fixtures/r22-result-oracle.py --runner census/round-21/run-acceptance.py
rc=1  total 258 pass 256 fail 2
failing ids: positive/clean-cache-demonstration, positive/cache-transient-path-and-time
$ python3 -B census/round-22/mutation-adequacy.py
rc=1  "mutants": 59, "survived": 0     (base: rc=0, survived 7)
```

## 2. The repair

`tools/souji-evidence-cache.py` (Q71 — scratch root from `TMPDIR`, nothing else changes):
`_selftest` takes its fixture root from `tempfile.mkdtemp(prefix="souji-r14-cache-selftest.")` (no `dir=`) and the
child environment receives the caller's `TMPDIR` when set instead of the literal `/var/tmp`; the module docstring
line for `--selftest` follows. Digest `dd279ba9…3939d6` (75817 B) -> `6b826da2…e7297` (75864 B).

`census/round-21/run-acceptance.py` (Q73 — the consumer pin, not historical evidence): the cache-demo summariser now
digests `tools/souji-evidence-cache.py` **at the graded revision**
(`git cat-file blob <revision>:tools/souji-evidence-cache.py`) instead of the live file. Justification: the pinned
payload is a historical record of what revision `ff425ab` shipped, so the revision blob is the correct subject; real
r21 runs already bind the working tree to the revision (`combined_snapshot` before and after every step, via
`pin.input_snapshot`, and `pin.resolve_durable(..., tree_check=True)`), so no live-vs-revision binding is lost, and no
no-op-traversal-in-a-symlinked-tree refusal is lost either (that lives in `pin.input_snapshot`). No historical
evidence (`census/round-21/final-out-S1.json`, `tests/fixtures/r22-result-oracle.json`, `step-inventory.json`) was
edited; `tests/fixtures/r15-preservation-frozen` pins neither file (grep count 0 in `expected.json` and `record.json`),
so no re-pin is required.

## 2b. Rule citations (verbatim, `corpus/QUALITY.md`)

- Q71 (`corpus/QUALITY.md:176`): "takes its scratch root from the caller's `TMPDIR`" and, for the measurement form,
  "Honouring it is measured, not grepped".
- Q73 (`corpus/QUALITY.md:178`): "is either regenerated with its own committed script at the candidate, or the tool
  edit is reverted".
- Q74 (`corpus/QUALITY.md:179`): "every base refusal code still fires for its base input".

## 3. Red-before — `--rev 2d9bca55a9f042a2c9ed60a797a8069e74c41f46`

```
$ python3 -B census/round-33/c2-counter.py --root <lane> --rev 2d9bca5… --base 6017a48… --list-rev 2d9bca5… --scratch <scratch> --only O1,G1,G2,G3
LEG	O1	sandbox	FAIL	base=rc0:W302:selftest: 48/48 passed	sbox=rc2:W0:selftest-unavailable: [Errno 30] Read-only file system: '<TMP>'
LEG	G1	guard	PASS	base=rc0:"total": 258	rev=rc0:"total": 258
LEG	G2	guard	PASS	base=rc0:"survived": 7	rev=rc0:"survived": 7
LEG	G3	guard	PASS	base=rc0:fixture: 22/22 checks passed	rev=rc0:fixture: 22/22 checks passed
SUMMARY legs=4 pass=0 fail=1 harm=0 partial=1 rev=2d9bca55a9f042a2c9ed60a797a8069e74c41f46
```

## 4. Candidate — `--rev 1595c203cc34083bc67c0edb28c131bcb01cb3f6`

```
$ python3 -B census/round-33/c2-counter.py --root <clone> --rev 1595c20… --base 6017a48… --list-rev 2d9bca5… --scratch <scratch> --only O1,G1,G2,G3
LEG	O1	sandbox	PASS	base=rc0:W302:selftest: 48/48 passed	sbox=rc0:W303:selftest: 48/48 passed
LEG	G1	guard	PASS	base=rc0:"total": 258	rev=rc0:"total": 258
LEG	G2	guard	PASS	base=rc0:"survived": 7	rev=rc0:"survived": 7
LEG	G3	guard	PASS	base=rc0:fixture: 22/22 checks passed	rev=rc0:fixture: 22/22 checks passed
SUMMARY legs=4 pass=1 fail=0 harm=0 partial=1 rev=1595c203cc34083bc67c0edb28c131bcb01cb3f6
```

## 5. Scratch root actually moved (strace, 6 repetitions of prefix extraction)

```
$ TMPDIR=<scratch>/str strace -f -qq -o st.log -e trace=mkdir,mkdirat python3 -B <tool> --selftest   # rc=0 both
base      : 209 scratch path mentions, all rooted "/var/tmp
candidate : 209 scratch path mentions, all rooted "<scratch>/str
$ ls -d /var/tmp/souji-r14-cache-selftest.* 2>/dev/null | wc -l   -> 0 ; <scratch>/str left empty (0 entries)
candidate --selftest: "selftest: 48/48 passed", rc 0 (same case count and line as base)
```

## 6. Q73 consumer readings (rc + last digit-bearing line, base vs candidate)

| consumer | base | candidate |
|---|---|---|
| `python3 -B tests/fixtures/r22-result-oracle.py --runner census/round-21/run-acceptance.py` (G1) | rc0 `"total": 258` (258/258, finding null) | rc0 `"total": 258` (258/258) |
| `python3 -B census/round-22/mutation-adequacy.py` (G2) | rc0 `    "survived": 7` (59 mutants, 52 killed) | rc0 `    "survived": 7` (59 mutants, 52 killed, disagree []) |
| `python3 -B tests/fixtures/r14-evidence-cache.py` (G3) | rc0 `fixture: 22/22 checks passed` | rc0 `fixture: 22/22 checks passed` |
| `python3 -B tests/fixtures/r20-input-binding.py --baseline 12516f7d…` (SKILL row 234) | rc0 `SUMMARY total=52 pass=52 fail=0 blocked=0 inventory=exact baseline_mismatches=31` | rc0 `SUMMARY total=52 pass=52 fail=0 blocked=0 inventory=exact baseline_mismatches=32` |
| `python3 -B census/round-14/cache-demonstration.py` (default gate) | rc0 `"retained_measured_commit": "2d9bca5…"` / status ok, 33/33 checks, residue [] | rc0 `"retained_measured_commit": "1595c20…"` / status ok, 33/33 checks, residue [] |
| `python3 -B census/round-14/count-claims.py <rev>` | rc0 (output byte-identical to candidate after rev normalization) | rc0 (same) |
| `python3 -B census/round-13/run-verification.py` (no args) | rc2 `run-verification: refusing: --round N and --output census/round-N/<new>.json are required; no default output exists` | rc2, same line |
| `python3 -B census/round-14/run-verification.py` | rc2 `run-verification: refused: refuse overwriting exercised evidence (no record written)` | rc2, same line |
| `python3 -B census/round-14/run-targeted.py` | rc2 `run-targeted: refused: refuse overwriting exercised evidence (no record written)` | rc2, same line |
| `python3 -B census/round-20/run-acceptance.py --root <clone> --rev <rev> --output <new>` | rc2 `run-acceptance: refused before checks/output: root must be the lane path used by the bounded r16/r18 fixtures` | rc2, same line (refuses in any clone by design) |

Consumer set: `git -C <clone> grep -l tools/souji-evidence-cache.py -- tests/fixtures census` = 79 files, identical list
at 2d9bca5 and at the candidate (diff of the two listings is empty after the revision prefix). 9 of them are live
executables (`census/round-13/run-verification.py`, `census/round-14/{cache-demonstration,count-claims,
run-targeted,run-verification}.py`, `census/round-20/run-acceptance.py`, `census/round-21/run-acceptance.py`,
`tests/fixtures/r14-evidence-cache.py`, `tests/fixtures/r20-input-binding.py`); the rest are historical records
(r20/r21 replay JSON, r22/r31/r32 wave artifacts) and the r26 assimilation snapshot, none of which executes. G1 and G2
are not literal grep hits: `tests/fixtures/r22-result-oracle.py` names the r21 runner, which names the tool, and
`tests/fixtures/r22-result-oracle.json` carries the pinned payload that the runner re-grades. SKILL `## Gate registry` rows naming the tool: 208 (`souji-evidence-cache`,
its own selftest = O1), 209 (`r14-evidence-cache` = G3), 242 (`r22-result-oracle` = G1); row 234
(`r20-input-binding`) copies the tool as a measured closure input and is the row above.

Teeth check (the gate comparison was not removed): `census/round-22/mutation-adequacy.py` at the candidate keeps the
gate mutants killed — `gate-sha` killed by `adequacy/cache/gate-sha-mismatch`,
`adequacy/residual/cache/gate-both-slots-wrong`, `adequacy/residual2/r3/cache/gate-empty`; `gate-isinstance` and
`gate-self-consistency` and `cache-gate-sha-default` killed as well.

## 7. Q74 — every refusal retained (base vs candidate, same argv, same rc and same finding line)

The tool has exactly one `/var/tmp` mention that is a refusal example, the name-pattern one at docstring line 144
("`/var/tmp/token-audit` is conservatively refused while a checkout beneath an innocuous ancestor is allowed"); all
other `/var/tmp` mentions were the scratch root and are gone (grep: base 4 mentions at lines 33/144/1295/1311,
candidate 1 at line 144).

| Q74 input | base | candidate |
|---|---|---|
| `--root /var/tmp/token-audit --record <valid>` | rc2 `finding root-protected: --root is secret-shaped name 'token-audit'` | identical |
| `--root /etc --record <valid>` | rc2 `finding root-protected: --root is inside or at /etc` | identical |
| `--root <root> --record <record declaring .ssh/id_ed25519>` | rc2 `finding path-protected: '.ssh/id_ed25519': credential or repository metadata component '.ssh'` | identical |
| `--root <symlink> --record <valid>` | rc2 `finding root-symlink: --root is a symlink` | identical |
| `--root /var/tmp --record <valid>` (boundary stays allowed) | rc1 `souji-evidence-cache: stale finding dependency-missing: 'src/a.txt': declared dependency is absent` | identical |
| `--selftest` with `/tmp`,`/var/tmp`,`/dev/shm` read-only and no usable temp dir (bwrap, TMPDIR unset, cwd read-only) | rc2 `selftest-unavailable: [Errno 30] Read-only file system: '/var/tmp/souji-r14-cache-selftest.…'` | rc2 `selftest-unavailable: [Errno 2] No usable temporary directory found in ['/tmp', '/var/tmp', '/usr/tmp', …]` |

The 48 embedded selftest cases (refusals, protected reads, frozen-snapshot tampering) all still fire: `48/48 passed`
at both revisions, identical case count.

## 8. Residuals (for the L1, not repaired here)

1. `SKILL.md:208` write-scope cell still reads "inputs read-only; isolated selftest `/var/tmp`; never executes a
   recorded command" — false after this patch. The C1 claim measures SCORECARD.md rows only, so this is a doc
   restatement for the L1 (`isolated selftest under the caller's TMPDIR`).
2. `tests/fixtures/r20-input-binding.py` last line moves `baseline_mismatches=31 -> 32`: the tool is in its measured
   closure and its digest vs the 2026-10-20 baseline revision is a data count, not a verdict (`fail=0`,
   `inventory=exact`, rc 0 both). Same class as the r32 T18 flaky anchor.
3. `tempfile.gettempdir()` keeps Python's documented search: with `TMPDIR` unset or unusable the scratch root is
   `/tmp` (or the next usable candidate), never `/var/tmp` again. Q71 names `tempfile` without `dir=` as the compliant
   form, so this is the rule's own semantics, not a widened skip.
4. `census/round-14/cache-demonstration.py`, `tests/fixtures/r14-evidence-cache.py` and the r14/r20 runners still pin
   their own `/var/tmp` scratch roots; they are other C2 legs (O2/O3 shape) or historical runners, not this leg.
5. `census/round-20/run-acceptance.py:458` has the same live read as r21:503, but it refuses outside the literal lane
   path, so it cannot be measured from a clone, and when it does run it executes inside a clone at `--rev` (live bytes
   equal revision bytes). Left unchanged.
