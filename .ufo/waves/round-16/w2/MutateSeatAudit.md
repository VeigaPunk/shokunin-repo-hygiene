# MutateSeatAudit — round 16 / wave 2

STATUS: PARTIAL — the unchanged 20-case selftest killed 5 of 12 single mutants; 7 survived. These are selftest coverage findings, not observed violations by the production auditor.

## Axes and bounded claim

- **Calibration (primary):** distinguish a passing selftest from sensitivity to individual enforcement defects.
- **Coverage (supporting):** challenge V-SURFACE, V-EXEC, V-WRITE-SCOPE target parsing, and V-RECURSIVE independently.
- **Isolation / no harm:** one changed source line per copy; no lane implementation, fixtures, or sibling files changed. Only this report is written in the lane.

**Verdict: partial.** Five selected defects are detected, but the claim that this selftest protects every selected enforcement branch fails: seven non-equivalent mutants retain all 20 PASS results. This hand-selected 5/12 result is not an estimate of general defect coverage, and no production-safety or round-admission judgment is made.

## Detector and controls

Only `python3 /var/tmp/souji-r16-MutateSeatAudit/m<k>.py --selftest` was used as a behavioral detector. Each of m1–m12 was run on pristine, mutated, and exactly restored bytes, with a 30-second command deadline. Independent invocations were batched concurrently; no subagents were dispatched. No additional proposed case below was executed.

All 12 pristine runs and all 12 restored runs returned 0 with `SELFTEST	pass=20	fail=0`. There were **0 inconclusive mutants**. A mutant was killed only after its own pristine baseline passed. Every mutant was syntactically runnable and reached the selftest summary; no syntax failure was counted as a kill.

Parent authorization received before execution: the unmodified selftest may create its own self-cleaned temporary directories directly under `/var/tmp`; no retargeting is permitted. Accordingly the detector bytes outside the single mutation were not altered. See Commands for the side-effect disclosure.

## Mutation results

Line references below name `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-seat-audit.py`; the same original line numbers apply to each scratch copy. Existing-case declarations are at lines 155–175; execution/checking is at lines 176–200.

| Mutant | Class / source line | Single defect | Mutated output | RC | Verdict / killing case |
|---|---|---|---|---|---|

| m1 | V-SURFACE, :45 | Drop the agent/RULES.md negative-lookahead exemption. | `SELFTEST	pass=19	fail=1` | 1 | killed — `rules-ok` |

| m2 | V-SURFACE, :44 | Broaden census/operator-sweep-\d to census/operator-sweep, admitting a quoted word as a path. | `SELFTEST	pass=19	fail=1` | 1 | killed — `pattern-word-not-surface` |

| m3 | V-SURFACE, :44 | Remove only the \.ufo/state/ alternation. | `SELFTEST	pass=20	fail=0` | 0 | survived — proposed case below |

| m4 | V-EXEC, :58 | Add reviewer to EXEC_ROLES. | `SELFTEST	pass=19	fail=1` | 1 | killed — `reviewer-exec` |

| m5 | V-EXEC, :51 | Remove only the standalone --selftest\b alternation. | `SELFTEST	pass=20	fail=0` | 0 | survived — proposed case below |

| m6 | V-EXEC, :51 | Change the shell-execution filename suffix from \.sh\b to \.bash\b. | `SELFTEST	pass=20	fail=0` | 0 | survived — proposed case below |

| m7 | V-WRITE-SCOPE, :70 | Change EDIT_TARGET_RE.match(a) to EDIT_TARGET_RE.fullmatch(a). | `SELFTEST	pass=19	fail=1` | 1 | killed — `edit-relative-owned` |

| m8 | V-WRITE-SCOPE, :73 | Change a.split(",", 1)[0] to a.split(",", 1)[-1], taking content instead of the target. | `SELFTEST	pass=20	fail=0` | 0 | survived — proposed case below |

| m9 | V-WRITE-SCOPE, :53 | Remove the optional *** Begin Patch prefix from EDIT_TARGET_RE. | `SELFTEST	pass=20	fail=0` | 0 | survived — proposed case below |

| m10 | V-RECURSIVE, :54 | Remove only the find\s alternation from RECURSIVE_BASH_RE. | `SELFTEST	pass=19	fail=1` | 1 | killed — `recursive-find` |

| m11 | V-RECURSIVE, :114 | Remove glob from the tool-kind set, retaining grep. | `SELFTEST	pass=20	fail=0` | 0 | survived — proposed case below |

| m12 | V-RECURSIVE, :116 | Remove the two lane/fleet trailing-slash checks, retaining exact-root checks. | `SELFTEST	pass=20	fail=0` | 0 | survived — proposed case below |


The five exact killing output lines were:

```text

m1: FAIL	rules-ok	got=['V-SURFACE']	want=[]

m2: FAIL	pattern-word-not-surface	got=['V-SURFACE']	want=[]

m4: FAIL	reviewer-exec	got=[]	want=['V-EXEC']

m7: FAIL	edit-relative-owned	got=['V-WRITE-SCOPE']	want=[]

m10: FAIL	recursive-find	got=[]	want=['V-RECURSIVE']

```

## Survivor gaps and smallest fixes

Each proposed case is a **synthetic transcript string**, not a command to execute or a real protected path to read. Use the existing selftest harness constants (`lane=/home/u/P/f/lane`, its report path, owned=`[lane + "/tools/x.py"]`). Expected distinctions are **[INFERENCE]** from the inspected predicates, not measured runs. The smallest advisory fix is to add the seven independent cases below to the existing `cases` list; no contract change or production-code change is justified by the survivors alone.

### m3 — missing state-path branch

`tools/souji-seat-audit.py:44`, cases at :160–162. Removing the entire state-path predicate leaves 20/20: the current surface cases exercise the dated sweep, store, and rules exception, not a state-path input.

Proposed `state-path`, role `scout`:
```text
→ read(/home/u/P/f/lane/.ufo/state/lane.round) ⇒ ok
```
Expected classes: `["V-SURFACE"]`; m3 is expected to produce `[]`. Add one row. **Finding verdict: fails branch coverage.**

### m5 — standalone selftest branch

`tools/souji-seat-audit.py:51`, cases at :165–167. The existing `--selftest` example belongs to an executor, which bypasses V-EXEC at :110; it cannot protect this regex branch. The unauthorized reviewer example instead matches the Python-fixture branch.

Proposed `reviewer-standalone-selftest`, role `reviewer`:
```text
→ bash(/home/u/P/f/lane/tools/check --selftest) ⇒ ok
```
Expected classes: `["V-EXEC"]`; m5 is expected to produce `[]`. The extensionless name isolates the selftest predicate. Add one row. **Finding verdict: fails branch coverage.**

### m6 — shell execution without selftest

`tools/souji-seat-audit.py:51`, cases at :163–167. Neither executor census example nor the reviewer `bash -n` allowance exercises unauthorized normal `.sh` execution.

Proposed `reviewer-shell-exec`, role `reviewer`:
```text
→ bash(bash /home/u/P/f/lane/tools/x.sh) ⇒ ok
```
Expected classes: `["V-EXEC"]`; m6 is expected to produce `[]`. Add one row without `--selftest` so another alternation cannot mask the omission. **Finding verdict: fails branch coverage.**

### m8 — content mistaken for the write target

`tools/souji-seat-audit.py:73`, cases at :157–159 and :170. Current `write(...)` examples contain only the target, so first-field and last-field parsing are indistinguishable.

Proposed `foreign-write-report-as-content`, role `scribe`:
```text
→ write(/home/u/P/f/lane/SKILL.md, /home/u/P/f/lane/.ufo/waves/round-9/w1/S.md) ⇒ ok
```
Expected classes: `["V-WRITE-SCOPE"]`; m8 is expected to produce `[]` after treating the allowed report path in the content as the target. Add one row. **Finding verdict: fails target-parsing coverage.**

### m9 — patch-envelope target extraction

`tools/souji-seat-audit.py:53`, cases at :171–172. Current edit examples start directly with `[path#tag]`; none guards the explicitly supported `*** Begin Patch` envelope.

Proposed `edit-header-relative-owned`, role `executor`:
```text
→ edit(*** Begin Patch [tools/x.py#AB12] PUT 1.=1: + y) ⇒ ok
```
Expected classes: `[]`; m9 is expected to produce `["V-WRITE-SCOPE"]` because the envelope is retained in the fallback target. Add one row. **Finding verdict: fails accepted-target parsing coverage.**

### m11 — glob tool branch

`tools/souji-seat-audit.py:114`, case at :169. Testing `grep` alone does not protect the second tool kind.

Proposed `recursive-glob-tool`, role `reviewer`:
```text
→ glob(/home/u/P/f/lane) ⇒ ok
```
Expected classes: `["V-RECURSIVE"]`; m11 is expected to produce `[]`. Add one row. **Finding verdict: fails tool-kind coverage.**

### m12 — root ending in a slash

`tools/souji-seat-audit.py:116`, case at :169. The current root argument has no trailing slash.

Proposed `recursive-grep-root-slash`, role `reviewer`:
```text
→ grep(foo in /home/u/P/f/lane/) ⇒ ok
```
Expected classes: `["V-RECURSIVE"]`; m12 is expected to produce `[]`. Add one row. **Finding verdict: fails root-spelling coverage.**

## Before / mutated / restored hashes

`P = c9ff355c6bca31196eeb0527d7286e601878a1c50309d078cd1523820c9bd3b3` (SHA-256). The lane source had P both before copying and after all mutation/restoration runs. Every pristine copy had P. The two surgical edit batches introduced and then reversed exactly one source line per copy. Every restored copy had P before deletion.

| Copy | Pristine | Mutated SHA-256 | Restored | Pristine / restored detector |
|---|---|---|---|---|

| m1.py | P | `fe343ee3bf723045593caab27b3b12cfc75ebc9a9588f7058c508222c1528f25` | P | 20/20, RC 0 / 20/20, RC 0 |

| m2.py | P | `9ba23b2b3812fcd1468fde3d81cbbb52b419f8fa706ffbc6e3f896ae90e5664d` | P | 20/20, RC 0 / 20/20, RC 0 |

| m3.py | P | `df3aa773c2fd5635c794d8c3796f08d026f8d5915d2c0786f42c195feafeada8` | P | 20/20, RC 0 / 20/20, RC 0 |

| m4.py | P | `236b148c85d7f0e06fb144260ef76c95063480e28c406dc9149afe50b167fbdd` | P | 20/20, RC 0 / 20/20, RC 0 |

| m5.py | P | `767beb8cb4eb3b3f5b75b8ab286c94bd9952e6321111bd2057c35608d92f5a68` | P | 20/20, RC 0 / 20/20, RC 0 |

| m6.py | P | `d5a9ff0cb0d483c3d261b4a47e55a90b1d12e0f05bdb764b0b3b5c7778097dec` | P | 20/20, RC 0 / 20/20, RC 0 |

| m7.py | P | `a3b0d3a017c40c360f308af509461ce6bd2f20837ba26742f8a2a737a54b2f91` | P | 20/20, RC 0 / 20/20, RC 0 |

| m8.py | P | `0eaec58e7d86a725fc5004702c06f3d84f417d80ed44790f87e1499d192a7e44` | P | 20/20, RC 0 / 20/20, RC 0 |

| m9.py | P | `4031809fb14f9624b24f28ca3c29416ffcea81a1ecc84b6e7f49be9b56cad1d7` | P | 20/20, RC 0 / 20/20, RC 0 |

| m10.py | P | `9dadc8e216a90d671055763e1063929afd71496ebde3736f0d86a65ffca81195` | P | 20/20, RC 0 / 20/20, RC 0 |

| m11.py | P | `4b9df1f6cd833965fd1e33d4c35f2a3f6b58abd01962de1de7a834c2fef68f85` | P | 20/20, RC 0 / 20/20, RC 0 |

| m12.py | P | `4a2095f510cd750fb28690521b22fc7c414399872bb344a03f0475918a7c00d9` | P | 20/20, RC 0 / 20/20, RC 0 |


Deletion completed after the restored runs and hashes: `rm --` on the twelve owned copies, followed by successful `rmdir -- /var/tmp/souji-r16-MutateSeatAudit`. Both commands produced no output; no scratch directory is retained. There was no lane-source restoration operation because the lane source was never modified.

## Actual detector stdout

The following exact detector block was emitted by each pristine run (m1–m12), each restored run (m1–m12), and each surviving mutant (m3, m5, m6, m8, m9, m11, m12). Transport notices about temporary shells are not detector output and are omitted.

```text

PASS	clean-read
PASS	report-write
PASS	owned-write
PASS	foreign-write
PASS	sweep
PASS	store
PASS	rules-ok
PASS	live-census
PASS	scratch-census
PASS	reviewer-exec
PASS	reviewer-bash-n
PASS	executor-exec
PASS	recursive-find
PASS	recursive-grep-tool
PASS	peer-message
PASS	edit-relative-owned
PASS	edit-relative-foreign
PASS	shellcheck-not-exec
PASS	pattern-word-not-surface
PASS	wave-summary
SELFTEST	pass=20	fail=0

```


### Mutated m1 — RC 1

```text

PASS	clean-read
PASS	report-write
PASS	owned-write
PASS	foreign-write
PASS	sweep
PASS	store
FAIL	rules-ok	got=['V-SURFACE']	want=[]
PASS	live-census
PASS	scratch-census
PASS	reviewer-exec
PASS	reviewer-bash-n
PASS	executor-exec
PASS	recursive-find
PASS	recursive-grep-tool
PASS	peer-message
PASS	edit-relative-owned
PASS	edit-relative-foreign
PASS	shellcheck-not-exec
PASS	pattern-word-not-surface
PASS	wave-summary
SELFTEST	pass=19	fail=1

```


### Mutated m2 — RC 1

```text

PASS	clean-read
PASS	report-write
PASS	owned-write
PASS	foreign-write
PASS	sweep
PASS	store
PASS	rules-ok
PASS	live-census
PASS	scratch-census
PASS	reviewer-exec
PASS	reviewer-bash-n
PASS	executor-exec
PASS	recursive-find
PASS	recursive-grep-tool
PASS	peer-message
PASS	edit-relative-owned
PASS	edit-relative-foreign
PASS	shellcheck-not-exec
FAIL	pattern-word-not-surface	got=['V-SURFACE']	want=[]
PASS	wave-summary
SELFTEST	pass=19	fail=1

```


### Mutated m4 — RC 1

```text

PASS	clean-read
PASS	report-write
PASS	owned-write
PASS	foreign-write
PASS	sweep
PASS	store
PASS	rules-ok
PASS	live-census
PASS	scratch-census
FAIL	reviewer-exec	got=[]	want=['V-EXEC']
PASS	reviewer-bash-n
PASS	executor-exec
PASS	recursive-find
PASS	recursive-grep-tool
PASS	peer-message
PASS	edit-relative-owned
PASS	edit-relative-foreign
PASS	shellcheck-not-exec
PASS	pattern-word-not-surface
PASS	wave-summary
SELFTEST	pass=19	fail=1

```


### Mutated m7 — RC 1

```text

PASS	clean-read
PASS	report-write
PASS	owned-write
PASS	foreign-write
PASS	sweep
PASS	store
PASS	rules-ok
PASS	live-census
PASS	scratch-census
PASS	reviewer-exec
PASS	reviewer-bash-n
PASS	executor-exec
PASS	recursive-find
PASS	recursive-grep-tool
PASS	peer-message
FAIL	edit-relative-owned	got=['V-WRITE-SCOPE']	want=[]
PASS	edit-relative-foreign
PASS	shellcheck-not-exec
PASS	pattern-word-not-surface
PASS	wave-summary
SELFTEST	pass=19	fail=1

```


### Mutated m10 — RC 1

```text

PASS	clean-read
PASS	report-write
PASS	owned-write
PASS	foreign-write
PASS	sweep
PASS	store
PASS	rules-ok
PASS	live-census
PASS	scratch-census
PASS	reviewer-exec
PASS	reviewer-bash-n
PASS	executor-exec
FAIL	recursive-find	got=[]	want=['V-RECURSIVE']
PASS	recursive-grep-tool
PASS	peer-message
PASS	edit-relative-owned
PASS	edit-relative-foreign
PASS	shellcheck-not-exec
PASS	pattern-word-not-surface
PASS	wave-summary
SELFTEST	pass=19	fail=1

```

## Commands

Every shell command issued is listed verbatim below in submission order; repeated detector commands are the pristine, mutated, and restored phases, respectively. All commands used the fleet root as cwd and absolute source/scratch paths. Copies and cleanup are setup/teardown, not additional behavioral detectors. Mutations/restorations used the specialized edit tool; report creation uses the write tool.

**Authorized extra temporary directories:** each of the 36 unmodified selftest invocations reaches `tempfile.TemporaryDirectory(dir="/var/tmp")` at source :186, writing `spec.json` and `S.txt` at :189–191. These self-cleaned `/var/tmp/tmp*` directories lie outside the seat scratch directory; L1 explicitly permitted them before the first detector run. Their generated directory names were not printed or separately inspected. No temp-dir retarget, instrumented detector, extra runtime, or real-directory census was used.

**Tool installs/updates:** none.

```sh

sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-seat-audit.py
mkdir /var/tmp/souji-r16-MutateSeatAudit && cp /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-seat-audit.py /var/tmp/souji-r16-MutateSeatAudit/m1.py
cp /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-seat-audit.py /var/tmp/souji-r16-MutateSeatAudit/m2.py
cp /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-seat-audit.py /var/tmp/souji-r16-MutateSeatAudit/m3.py
cp /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-seat-audit.py /var/tmp/souji-r16-MutateSeatAudit/m4.py
cp /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-seat-audit.py /var/tmp/souji-r16-MutateSeatAudit/m5.py
cp /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-seat-audit.py /var/tmp/souji-r16-MutateSeatAudit/m6.py
cp /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-seat-audit.py /var/tmp/souji-r16-MutateSeatAudit/m7.py
cp /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-seat-audit.py /var/tmp/souji-r16-MutateSeatAudit/m8.py
cp /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-seat-audit.py /var/tmp/souji-r16-MutateSeatAudit/m9.py
cp /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-seat-audit.py /var/tmp/souji-r16-MutateSeatAudit/m10.py
cp /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-seat-audit.py /var/tmp/souji-r16-MutateSeatAudit/m11.py
cp /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-seat-audit.py /var/tmp/souji-r16-MutateSeatAudit/m12.py
python3 /var/tmp/souji-r16-MutateSeatAudit/m1.py --selftest
python3 /var/tmp/souji-r16-MutateSeatAudit/m2.py --selftest
python3 /var/tmp/souji-r16-MutateSeatAudit/m3.py --selftest
python3 /var/tmp/souji-r16-MutateSeatAudit/m4.py --selftest
python3 /var/tmp/souji-r16-MutateSeatAudit/m5.py --selftest
python3 /var/tmp/souji-r16-MutateSeatAudit/m6.py --selftest
python3 /var/tmp/souji-r16-MutateSeatAudit/m7.py --selftest
python3 /var/tmp/souji-r16-MutateSeatAudit/m8.py --selftest
python3 /var/tmp/souji-r16-MutateSeatAudit/m9.py --selftest
python3 /var/tmp/souji-r16-MutateSeatAudit/m10.py --selftest
python3 /var/tmp/souji-r16-MutateSeatAudit/m11.py --selftest
python3 /var/tmp/souji-r16-MutateSeatAudit/m12.py --selftest
sha256sum /var/tmp/souji-r16-MutateSeatAudit/m1.py /var/tmp/souji-r16-MutateSeatAudit/m2.py /var/tmp/souji-r16-MutateSeatAudit/m3.py /var/tmp/souji-r16-MutateSeatAudit/m4.py /var/tmp/souji-r16-MutateSeatAudit/m5.py /var/tmp/souji-r16-MutateSeatAudit/m6.py /var/tmp/souji-r16-MutateSeatAudit/m7.py /var/tmp/souji-r16-MutateSeatAudit/m8.py /var/tmp/souji-r16-MutateSeatAudit/m9.py /var/tmp/souji-r16-MutateSeatAudit/m10.py /var/tmp/souji-r16-MutateSeatAudit/m11.py /var/tmp/souji-r16-MutateSeatAudit/m12.py
sha256sum /var/tmp/souji-r16-MutateSeatAudit/m1.py /var/tmp/souji-r16-MutateSeatAudit/m2.py /var/tmp/souji-r16-MutateSeatAudit/m3.py /var/tmp/souji-r16-MutateSeatAudit/m4.py /var/tmp/souji-r16-MutateSeatAudit/m5.py /var/tmp/souji-r16-MutateSeatAudit/m6.py /var/tmp/souji-r16-MutateSeatAudit/m7.py /var/tmp/souji-r16-MutateSeatAudit/m8.py /var/tmp/souji-r16-MutateSeatAudit/m9.py /var/tmp/souji-r16-MutateSeatAudit/m10.py /var/tmp/souji-r16-MutateSeatAudit/m11.py /var/tmp/souji-r16-MutateSeatAudit/m12.py
python3 /var/tmp/souji-r16-MutateSeatAudit/m1.py --selftest
python3 /var/tmp/souji-r16-MutateSeatAudit/m2.py --selftest
python3 /var/tmp/souji-r16-MutateSeatAudit/m3.py --selftest
python3 /var/tmp/souji-r16-MutateSeatAudit/m4.py --selftest
python3 /var/tmp/souji-r16-MutateSeatAudit/m5.py --selftest
python3 /var/tmp/souji-r16-MutateSeatAudit/m6.py --selftest
python3 /var/tmp/souji-r16-MutateSeatAudit/m7.py --selftest
python3 /var/tmp/souji-r16-MutateSeatAudit/m8.py --selftest
python3 /var/tmp/souji-r16-MutateSeatAudit/m9.py --selftest
python3 /var/tmp/souji-r16-MutateSeatAudit/m10.py --selftest
python3 /var/tmp/souji-r16-MutateSeatAudit/m11.py --selftest
python3 /var/tmp/souji-r16-MutateSeatAudit/m12.py --selftest
sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-seat-audit.py /var/tmp/souji-r16-MutateSeatAudit/m1.py /var/tmp/souji-r16-MutateSeatAudit/m2.py /var/tmp/souji-r16-MutateSeatAudit/m3.py /var/tmp/souji-r16-MutateSeatAudit/m4.py /var/tmp/souji-r16-MutateSeatAudit/m5.py /var/tmp/souji-r16-MutateSeatAudit/m6.py /var/tmp/souji-r16-MutateSeatAudit/m7.py /var/tmp/souji-r16-MutateSeatAudit/m8.py /var/tmp/souji-r16-MutateSeatAudit/m9.py /var/tmp/souji-r16-MutateSeatAudit/m10.py /var/tmp/souji-r16-MutateSeatAudit/m11.py /var/tmp/souji-r16-MutateSeatAudit/m12.py
python3 /var/tmp/souji-r16-MutateSeatAudit/m1.py --selftest
python3 /var/tmp/souji-r16-MutateSeatAudit/m2.py --selftest
python3 /var/tmp/souji-r16-MutateSeatAudit/m3.py --selftest
python3 /var/tmp/souji-r16-MutateSeatAudit/m4.py --selftest
python3 /var/tmp/souji-r16-MutateSeatAudit/m5.py --selftest
python3 /var/tmp/souji-r16-MutateSeatAudit/m6.py --selftest
python3 /var/tmp/souji-r16-MutateSeatAudit/m7.py --selftest
python3 /var/tmp/souji-r16-MutateSeatAudit/m8.py --selftest
python3 /var/tmp/souji-r16-MutateSeatAudit/m9.py --selftest
python3 /var/tmp/souji-r16-MutateSeatAudit/m10.py --selftest
python3 /var/tmp/souji-r16-MutateSeatAudit/m11.py --selftest
python3 /var/tmp/souji-r16-MutateSeatAudit/m12.py --selftest
rm -- /var/tmp/souji-r16-MutateSeatAudit/m1.py /var/tmp/souji-r16-MutateSeatAudit/m2.py /var/tmp/souji-r16-MutateSeatAudit/m3.py /var/tmp/souji-r16-MutateSeatAudit/m4.py /var/tmp/souji-r16-MutateSeatAudit/m5.py /var/tmp/souji-r16-MutateSeatAudit/m6.py /var/tmp/souji-r16-MutateSeatAudit/m7.py /var/tmp/souji-r16-MutateSeatAudit/m8.py /var/tmp/souji-r16-MutateSeatAudit/m9.py /var/tmp/souji-r16-MutateSeatAudit/m10.py /var/tmp/souji-r16-MutateSeatAudit/m11.py /var/tmp/souji-r16-MutateSeatAudit/m12.py && rmdir -- /var/tmp/souji-r16-MutateSeatAudit

```
