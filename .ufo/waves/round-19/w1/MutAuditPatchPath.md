STATUS: DONE — both assigned mutants survived the r19 external fixture; exact-stimulus witnesses exposed both defects; original bytes restored and private scratch removed.

# Findings

Axis: **calibration**, C1, the lane's lowest non-retired axis (preregistration `.ufo/waves/round-19/preregistration.txt:7-31`). This is an isolated mutation result, not a round judgment or admission.

1. **M1 — suffix-only path authorization: SURVIVED the new fixture.** In the private auditor, the absolute-target allowed-path predicate at `tools/souji-seat-audit.py:216-220` was broadened by adding `n.endswith(".patch") or`. This accepts an otherwise-unowned `<lane>/tools/x.patch` solely because its rendered target has the delivery suffix, without requiring the report directory or seat stem. Expected detector: `tests/fixtures/r19-seat-audit-shapes.py` should fail on this authorization regression. Actual: **exit 0, total=5, failed=0, base_discriminating=2**. The requested failing-fixture expectation was not met. Its negative tools target is `tools/x.py`, not a tools-directory `.patch` (`tests/fixtures/r19-seat-audit-shapes.py:71-77`).
2. **M2 — remove `os.kill` from library signal tokens: SURVIVED the new fixture.** Only `os\\.kill|` was removed from `SIGNAL_LIB_RE` at `tools/souji-seat-audit.py:103`; the shell regex and the other library tokens were retained. Actual fixture: **exit 0, total=5, failed=0, base_discriminating=2**. Its `signal-kill` case still passed with exit 1 and `V-SIGNAL`: that stimulus is the shell command `kill -TERM 1234`, not the missing library token (`tests/fixtures/r19-seat-audit-shapes.py:75`).
3. **The mutants were behaviorally active, not ineffective edits.** A fixed two-transcript witness detector required the exact major-class/seat set. It passed on pristine and both restored auditor states, failed on M1 because `PatchPath/V-WRITE-SCOPE` disappeared, and failed on M2 because `LibSignal/V-SIGNAL` disappeared. Thus these witnesses **killed** each mutant, while the assigned external fixture **did not**.

Scope of the finding: the pristine auditor rejected both exact stimuli. This is not evidence that the current auditor accepts either defect, nor that its entire test suite is blind. Static inspection shows internal selftest cases for a foreign-stem `.patch` and `os.kill` at `tools/souji-seat-audit.py:434-440`; the internal selftest was **not run**. No expectations were weakened, no additional mutant was tried, and no production fix or contract change was made.

# Evidence

## Bytes measured and isolation

The changed arm was copied from **worktree bytes**, not inferred from an integrated-state claim. The fixture's historical arm continued to extract `3ab2c81479f5004c8bc91946eea482caec45408f:tools/souji-seat-audit.py` through read-only `git show` (`tests/fixtures/r19-seat-audit-shapes.py:58-69`).

Private root, abbreviated `S` below:

```text
/var/tmp/souji-r19-MutAuditPatchPath-2
```

The private fixture retained all five cases and their exact expectations. Its only plumbing change was line 55, from `dir="/var/tmp"` to `dir=lane_root`, so its generated worlds stayed inside `S`. The copied layout was `S/tests/fixtures/` and `S/tools/`, making that computed lane root `S`. This same confined fixture was used in every pristine/mutant/restored run. `GIT_DIR` selected the real lane's Git metadata for read-only extraction; it did not grant write authority. The workdir case's `/var/tmp/souji-r19-Seat/probe.py` was only transcript text, not an actual write there.

SHA-256:

| Auditor state | SHA-256 |
|---|---|
| Worktree source / pristine copy | `efa8a04b6d8289f11ec9493c8de1be8fa34e116d38ae251947ef33541ef84b82` |
| M1 suffix whitelist | `bf711d260ef2cf0f3d02791ed3b32ea6ef6f1687150ea32e02411256a7e016ff` |
| Restored after M1 / pristine for M2 | `efa8a04b6d8289f11ec9493c8de1be8fa34e116d38ae251947ef33541ef84b82` |
| M2 dropped `os.kill` | `641b51dde4145d2744f643ec853018f6b32a2c8b599cbdf542fe2371f4e1e54a` |
| Restored after M2 / final source and copy | `efa8a04b6d8289f11ec9493c8de1be8fa34e116d38ae251947ef33541ef84b82` |

| Fixture state | SHA-256 |
|---|---|
| Original worktree / initial exact copy | `6c59f39a54d93d34a0e741ca1a25970be23ff7485f6dd8cdbda34f598faf588a` |
| Scratch-confined detector, unchanged across all five phases | `534c187266fea1d700cff112f815aa64bf616b5a84b693ecd64cb63f1c7b88b8` |
| Final fixture restored to original bytes | `6c59f39a54d93d34a0e741ca1a25970be23ff7485f6dd8cdbda34f598faf588a` |

Exact one-line auditor mutations, applied separately and each reversed before proceeding:

```diff
# M1: tools/souji-seat-audit.py:218
-        if _under(n, _norm(scratch)) or any(n == _norm(p) for p in allowed):
+        if n.endswith(".patch") or _under(n, _norm(scratch)) or any(n == _norm(p) for p in allowed):

# M2: tools/souji-seat-audit.py:103
-SIGNAL_LIB_RE = re.compile(r"\b(?:os\.kill|proc\.kill|\.send_signal|send_signal)\s*\(")
+SIGNAL_LIB_RE = re.compile(r"\b(?:proc\.kill|\.send_signal|send_signal)\s*\(")
```

## Exact stimuli and supplemental detector

The synthetic lane supplied to the CLI was `S/witness/lane`. The synthetic spec had `schema=ufo-swarm-wave-v1`, `reportDir=.ufo/waves/round-19/w1`, no OWNED grants, and these seats:

- `PatchPath`, role `scribe`, prompt `fixture`.
- `LibSignal`, role `scout`, prompt `fixture`.

Exact transcript bytes, each ending with one newline:

```text
PatchPath.txt:
→ write(/var/tmp/souji-r19-MutAuditPatchPath-2/witness/lane/tools/x.patch) ⇒ ok

LibSignal.txt:
→ bash(python3 -c 'os.kill(1234, 9)') ⇒ ok
```

These are data consumed by the auditor, never executed shell/Python signal commands. The `.patch` witness used an actual tools-directory target with that suffix; it was not an authorized sibling delivery artifact.

The fixed supplemental detector required auditor exit 1 **and** the sorted complete flag set:

```text
[('major', 'V-SIGNAL', 'LibSignal'),
 ('major', 'V-WRITE-SCOPE', 'PatchPath')]
```

| Phase | External fixture exit / failed | Witness auditor exit | Exact witness flags | Witness detector exit |
|---|---|---|---|---|
| Pristine | 0 / 0 | 1 | `LibSignal: V-SIGNAL major`; `PatchPath: V-WRITE-SCOPE major` | 0 |
| M1 | 0 / 0 | 1 | `LibSignal: V-SIGNAL major` only | 1 |
| Restored after M1 | 0 / 0 | 1 | Both expected majors | 0 |
| M2 | 0 / 0 | 1 | `PatchPath: V-WRITE-SCOPE major` only | 1 |
| Restored after M2 | 0 / 0 | 1 | Both expected majors | 0 |

The remaining major kept the witness auditor's exit at 1 even during a mutant: checking only its exit would miss the defect. The witness comparator checked exact classes, severities and seat identities. All fixture and witness stderr streams were empty. Both detector baselines passed, so neither mutation verdict is inconclusive.

## Actual external-fixture output

The complete fixture stdout was identical in all five phases (recorded-output comparison, not another execution):

```text
CASE	pass	changed/delivery-patch	exit=0 ids=[]
CASE	discriminates	base/delivery-patch	exit=1 ids=['V-WRITE-SCOPE']
CASE	pass	changed/delivery-workdir	exit=0 ids=[]
CASE	same	base/delivery-workdir	exit=0 ids=[]
CASE	pass	changed/tools-write	exit=1 ids=['V-WRITE-SCOPE']
CASE	same	base/tools-write	exit=1 ids=['V-WRITE-SCOPE']
CASE	pass	changed/signal-kill	exit=1 ids=['V-SIGNAL']
CASE	discriminates	base/signal-kill	exit=0 ids=[]
CASE	pass	changed/relative-target	exit=1 ids=['V-WRITE-RELATIVE']
CASE	same	base/relative-target	exit=1 ids=['V-WRITE-RELATIVE']
SUMMARY total=5 failed=0 base_discriminating=2
```

Pristine and both restored witness runs printed:

```text
major	V-SIGNAL	LibSignal	bash	python3 -c 'os.kill(1234, 9)'
major	V-WRITE-SCOPE	PatchPath	write	/var/tmp/souji-r19-MutAuditPatchPath-2/witness/lane/tools/x.patch
SUMMARY	seats=2	calls=2	major=2	minor=0	missing=0
```

M1 printed only the `LibSignal` major; M2 printed only the `PatchPath` major. Each mutant witness summary was `seats=2 calls=2 major=1 minor=0 missing=0`.

## Restoration and cleanup

After each auditor mutation was reversed, the same fixture and witness detector were rerun successfully, with the original auditor SHA-256 above. After the final detector run, the fixture's one-line confinement change was also reversed. Final `sha256sum` and `cmp -s` compared each restored private file with its lane source and reported:

```text
RESTORE auditor: exact-byte match
RESTORE fixture: exact-byte match
CLEANUP scratch: absent
```

Only after these exact-byte matches was the private root removed. No scratch artifact remains; this report preserves the commands, outputs and hashes.

# Commands run

Prerequisite reads: the godspeed and shokunin skills/protocol material, `/home/vgpnk/.omp/agent/RULES.md`, the round-19 preregistration, the round-18 closure and residuals, the SCORECARD planned section, and the two source files cited above. No public documentation was needed and no external-source quote is used.

Runtime setup commands: `python3 --version` → `Python 3.14.8`; `git --version` → `git version 2.56.0`; read-only `git rev-parse --absolute-git-dir` → the lane's `.git`; private `mkdir`, exact-file `cp`, and `sha256sum`.

Python Eval drove the following exact argv through `subprocess.run`, once per phase listed in the table; no executable wrapper file was created. The driver interpreter was `/usr/bin/python`, version `3.14.8`.

```text
/usr/bin/python /var/tmp/souji-r19-MutAuditPatchPath-2/tests/fixtures/r19-seat-audit-shapes.py --tool /var/tmp/souji-r19-MutAuditPatchPath-2/tools/souji-seat-audit.py --base-rev 3ab2c81479f5004c8bc91946eea482caec45408f

/usr/bin/python /var/tmp/souji-r19-MutAuditPatchPath-2/tools/souji-seat-audit.py --spec /var/tmp/souji-r19-MutAuditPatchPath-2/witness/spec.json --transcripts /var/tmp/souji-r19-MutAuditPatchPath-2/witness/transcripts --lane /var/tmp/souji-r19-MutAuditPatchPath-2/witness/lane
```

Both commands ran with cwd `S`, captured stdout/stderr, and these **child-process-only** environment overrides:

```text
GIT_DIR=/home/vgpnk/Projects/shokunin/souji-shokunin/.git
GIT_OPTIONAL_LOCKS=0
TMPDIR=/var/tmp/souji-r19-MutAuditPatchPath-2/tmp
PYTHONDONTWRITEBYTECODE=1
```

Bounds: fixture driver timeout 120 seconds; witness driver timeout 30 seconds; SHA-256 subprocess timeout 20 seconds. No timeout fired. The fixture internally invokes only private changed/base auditors on its synthetic specs and transcripts. The supplemental comparator parsed the recorded tab-separated major/minor rows and compared their complete sorted triples with the fixed expected set above.

Restoration commands: final `sha256sum` of the two lane sources and two restored private copies; `cmp -s` for each pair; then `rm -r -- /var/tmp/souji-r19-MutAuditPatchPath-2` and `test ! -e /var/tmp/souji-r19-MutAuditPatchPath-2`. No lane tool was executed in place. No build, census, live-process probe, or internal selftest was run.

# Contract compliance

- Sole lane write: this assigned report. All mutable copies, synthetic specs/transcripts, and generated fixture worlds were confined to the named private root and removed.
- No production or sibling source edited; no patch artifact delivered; no fleet/state/watchdog/operator-sweep surface opened or modified.
- No subagent dispatch, broadcast, other agent runtime, Git/JJ mutation, network request, secret/environment-file read, or actual signal call.
- `kill -TERM` and `os.kill` occurred only as synthetic transcript strings passed to a classifier.
- Tool installations/updates: **none**. Existing Python and Git sufficed; no package-manager transaction occurred.
- Primary verdict remains **SURVIVED / SURVIVED for the requested external fixture**, despite the supplemental witnesses killing both mutants. This is a scoped coverage finding for L1; it grants no authority to change the contract or claim admission.
