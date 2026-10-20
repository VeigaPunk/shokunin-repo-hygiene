STATUS: DONE — 12 isolated single mutants probed: 8 killed, 4 survived, 0 inconclusive; all 12 restored byte-for-byte, with pristine/restored selftests 49/49.
# MutateSeatAudit2 — C2 calibration mutation probe
## Scope and axes
Primary axis: **calibration**. Probe controls: mutation sensitivity, bounded execution, and exact byte restoration. This is a detector-coverage report, not an admission judgment or a finding that the landed auditor currently implements any mutant. No production fixes, commits, integrations, or sibling-source changes were made.
- Source: `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-seat-audit.py` at `ddb73474433977ff54b015ac3e77669ff2537353` (`ddb7347`). Every source line below is from those exact committed bytes, not the mutable worktree.
- Source size: **22308 bytes**; SHA-256: `8268212db158186d3d6dedc22ffb4755c89d7e62cfff2210b7c6329ca58d5f54`.
- Scratch: `/var/tmp/souji-r17-MutateSeatAudit2/`; twelve independent copies, one behavior-bearing mutation each. M08 is the explicitly requested selftest/meta mutation; the other eleven mutate production behavior. No paired/stacked mutants.
- Detector, unchanged across each pristine/mutated/restored triplet: `python3 <absolute-copy-path> --selftest`, 30-second per-invocation bound. Twelve independent calls ran concurrently per phase; all completed.
- All 24 pristine/restored runs: rc **0**, `SELFTEST\tpass=49\tfail=0`. All 36 invocations: empty stderr. No baseline failure, timeout, exception, or syntax-error kill.
- **Raw result:** 8 killed / 4 survived / 0 inconclusive. **Production-only:** 8 killed / 3 survived / 0 inconclusive; separately, 1 selftest/meta survivor. Do not mix the meta-mutant into a claimed production mutation score.
## Mutation results
All rows used the exact same selftest before mutation and after exact restoration. The output cell is the actual mutated summary; full stdout follows below.
| ID | Source at ddb7347 | Single defect | Expected detector | Mutated output / rc | Verdict |
|---|---|---|---|---|---|
| M01 (production) | `tools/souji-seat-audit.py:169` | Restore relative suffix matching before the header-only resolution branch. | h2-bare-write-ok | `SELFTEST pass=48 fail=1` / 1 | **KILLED** |
| M02 (production) | `tools/souji-seat-audit.py:207` | Make every unparsed target minor, irrespective of call status. | h4-trunc-lane-report; h5-unparsed-ok | `SELFTEST pass=47 fail=2` / 1 | **KILLED** |
| M03 (production) | `tools/souji-seat-audit.py:129` | Audit only the first extracted edit header. | h6-multi-header; h8-trunc-header-rel | `SELFTEST pass=47 fail=2` / 1 | **KILLED** |
| M04 (production) | `tools/souji-seat-audit.py:88` | Remove path normalization while retaining trailing-slash trimming. | h7-dotdot-scratch | `SELFTEST pass=48 fail=1` / 1 | **KILLED** |
| M05 (production) | `tools/souji-seat-audit.py:163` | Allow any absolute /var/tmp target instead of seat-scoped scratch. | scratch-other-seat | `SELFTEST pass=48 fail=1` / 1 | **KILLED** |
| M06 (production) | `tools/souji-seat-audit.py:217` | Remove V-PROBE emission without removing recursive-probe detection. | recursive-find; probe-realpath-lane; probe-strace-fleet; probe-find-dot | `SELFTEST pass=45 fail=4` / 1 | **KILLED** |
| M07 (production) | `tools/souji-seat-audit.py:207` | Downgrade relative-write attempts from major to minor. | edit-relative-foreign; report-edit-relative-dotufo; h1-rel-write-ok; h2-bare-write-ok; h8-trunc-header-rel | `SELFTEST pass=44 fail=5` / 1 | **KILLED** |
| M08 (selftest/meta) | `tools/souji-seat-audit.py:332` | Drop severity from the selftest equality check. | No independent comparator canary exists; selftest-only mutation expected to survive. | `SELFTEST pass=49 fail=0` / 0 | **SURVIVED** |
| M09 (production) | `tools/souji-seat-audit.py:170` | Restore lstrip character-set stripping for relative edit headers. | No current case has a dot-directory or parent-traversal relative header; expected coverage gap. | `SELFTEST pass=49 fail=0` / 0 | **SURVIVED** |
| M10 (production) | `tools/souji-seat-audit.py:246` | Lose seat-specific scratch scope at the production run() callsite. | Direct audit_seat scratch cases do not cover run() wiring; expected wave-summary gap. | `SELFTEST pass=49 fail=0` / 0 | **SURVIVED** |
| M11 (production) | `tools/souji-seat-audit.py:93` | Treat string-prefix neighbors as descendants of allowed scratch. | scratch-other-seat uses Other, not an S-prefixed foreign seat; expected boundary gap. | `SELFTEST pass=49 fail=0` / 0 | **SURVIVED** |
| M12 (production) | `tools/souji-seat-audit.py:143` | Silently allow unresolved (None) write/edit targets. | report-edit-table-prose; report-edit-sentence-prose; h5-unparsed-ok; h5b-unparsed-error | `SELFTEST pass=45 fail=4` / 1 | **KILLED** |

## Findings and smallest detector fixes
### F1 — parent/dot-directory header normalization is not protected (M09 survives)
At `tools/souji-seat-audit.py:170`, replacing `removeprefix("./")` with `lstrip("./")` still returns rc 0 / 49 passed. The landed implementation itself remains correct at this point; the current selftest does not distinguish prefix removal from character-set stripping.
**Smallest fix:** add relative-header cases to the existing case table. [INFERENCE, not executed] `[.ufo/waves/round-9/w1/S.md#AB12]` should resolve to the allowed report with no violation; the lstrip mutant removes the leading dot and falsely flags it. [INFERENCE, not executed] `[../tools/x.py#AB12]` should be `V-WRITE-RELATIVE/major`; the mutant strips `../` and incorrectly permits the owned `tools/x.py`. These cases would distinguish the implementations without changing the contract. Verdict: **partial detector coverage**.
### F2 — run() seat-scratch wiring is not protected (M10 survives)
At `tools/souji-seat-audit.py:244-246`, hardcoding `scratch="/var/tmp/"` passes all 49 cases. Direct seat-scoped checks exercise `audit_seat`, but `selftest`'s integration fixture (`:338-345`) only writes a foreign lane file and lacks a real round scratch context. It therefore cannot detect losing the scoped scratch argument in `run()`.
**Smallest fix:** expand that existing integration fixture with a `souji-r9-` context and own-seat plus foreign-seat scratch writes, checking exact violation class/severity and summary counts. [INFERENCE, not executed] a seat S write to `/var/tmp/souji-r9-Other/out.txt` should be `V-WRITE-SCOPE/major` through `run()`; M10 would allow it. Verdict: **partial detector coverage**.
### F3 — scratch-directory component boundary is not protected (M11 survives)
At `tools/souji-seat-audit.py:93`, `path.startswith(prefix)` passes all 49 cases. Existing `scratch-other-seat` uses Other, which does not share the allowed S prefix; it does not test a prefix-neighbor seat.
**Smallest fix:** add one existing-style case with scratch `/var/tmp/souji-r9-S/` and target `/var/tmp/souji-r9-Sibling/out.txt`, expecting `V-WRITE-SCOPE/major`. [INFERENCE, not executed] the landed component-boundary implementation rejects it, whereas M11 would allow it. Verdict: **partial detector coverage**.
### F4 — the selftest cannot police removal of its own severity oracle (M08 survives)
At `tools/souji-seat-audit.py:332`, comparing only class names still returns rc 0 / 49 passed. This is a **selftest/meta survivor**, not an observed production severity defect: with otherwise-correct production behavior, discarding the severity half does not alter any case outcome. M07 independently demonstrates that the unmodified oracle does catch a production major→minor regression (five exact-severity failures).
**Smallest fix:** retain an external mutation/canary check for the severity comparison, or exercise a shared comparator with equal-class/different-severity values from an independent oracle. Merely adding another passing production fixture cannot make a class-only oracle reject an otherwise-correct auditor. No paired severity-corruption mutant was run, because this assignment called for single mutants only. Verdict: **meta-coverage limitation**, not evidence that the landed comparator is severity-blind.
### Branches challenged successfully
The bounded detector kills restored suffix matching (M01), status-blind unparsed severity (M02), first-header-only parsing (M03), missing normpath (M04), blanket absolute /var/tmp allowance (M05), removed V-PROBE emission (M06), relative→minor severity (M07), and missing unresolved-target refusal (M12). M04 retains trailing-slash trimming so its sole failure is the intended dotdot escape, not an unrelated positive-control failure. Verdict: **holds for these eight injected defects only**. No claim of universal calibration or complete mutation coverage follows.
## Exact mutations
- **M01**, `tools/souji-seat-audit.py:169`: Insert `if any(p.endswith("/" + target.lstrip("./")) for p in allowed): return None`.
- **M02**, `tools/souji-seat-audit.py:207`: `if cls == "V-WRITE-UNPARSED" and status != "ok":` → `if cls == "V-WRITE-UNPARSED":`
- **M03**, `tools/souji-seat-audit.py:129`: `return headers` → `return headers[:1]`
- **M04**, `tools/souji-seat-audit.py:88`: `return os.path.normpath(p)` → `return p.rstrip("/")`
- **M05**, `tools/souji-seat-audit.py:163`: `_under(n, _norm(scratch))` → `_under(n, _norm("/var/tmp/"))` in the absolute-target branch only
- **M06**, `tools/souji-seat-audit.py:217`: `flag("V-PROBE", "minor")` → `pass`
- **M07**, `tools/souji-seat-audit.py:207`: Add `cls == "V-WRITE-RELATIVE" or (...)` to the minor-severity condition.
- **M08**, `tools/souji-seat-audit.py:332`: `if got == sorted(want):` → `if sorted(c for c, _ in got) == sorted(c for c, _ in want):`
- **M09**, `tools/souji-seat-audit.py:170`: `rel = target.removeprefix("./")` → `rel = target.lstrip("./")`
- **M10**, `tools/souji-seat-audit.py:246`: `scratch=scratch_base + name + "/"` → `scratch="/var/tmp/"`
- **M11**, `tools/souji-seat-audit.py:93`: `return path == prefix or path.startswith(prefix + os.sep)` → `return path.startswith(prefix)`
- **M12**, `tools/souji-seat-audit.py:143`: `return "V-WRITE-UNPARSED"` → `return None` in the target-is-None branch

## Commands and confinement
The source command below was run twice (initial displayed source, then binary capture for exact copies), both rc 0 with empty stderr. Its stdout was the complete source (22308 bytes; digest above). Copies/restoration used the write tool; mutations used surgical hashline edits. No git write or jj invocation was used.
```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show ddb7347:tools/souji-seat-audit.py
```
The following twelve **literal commands were each run three times**, once pristine, once mutated, once restored. Their CWD was the scratch directory. The table and output blocks give all three phase results.
```sh
python3 /var/tmp/souji-r17-MutateSeatAudit2/M01-restore-suffix-matching.py --selftest
python3 /var/tmp/souji-r17-MutateSeatAudit2/M02-status-blind-unparsed-minor.py --selftest
python3 /var/tmp/souji-r17-MutateSeatAudit2/M03-first-header-only.py --selftest
python3 /var/tmp/souji-r17-MutateSeatAudit2/M04-no-normpath.py --selftest
python3 /var/tmp/souji-r17-MutateSeatAudit2/M05-blanket-var-tmp.py --selftest
python3 /var/tmp/souji-r17-MutateSeatAudit2/M06-remove-v-probe.py --selftest
python3 /var/tmp/souji-r17-MutateSeatAudit2/M07-relative-to-minor.py --selftest
python3 /var/tmp/souji-r17-MutateSeatAudit2/M08-drop-severity-comparison.py --selftest
python3 /var/tmp/souji-r17-MutateSeatAudit2/M09-restore-lstrip.py --selftest
python3 /var/tmp/souji-r17-MutateSeatAudit2/M10-drop-run-seat-scratch.py --selftest
python3 /var/tmp/souji-r17-MutateSeatAudit2/M11-prefix-without-boundary.py --selftest
python3 /var/tmp/souji-r17-MutateSeatAudit2/M12-allow-unparsed-target.py --selftest
```
For each phase, the following literal command was also run once (three invocations total, rc 0, empty stderr); the before/mutated/restored digests are recorded below.
```sh
sha256sum /var/tmp/souji-r17-MutateSeatAudit2/M01-restore-suffix-matching.py /var/tmp/souji-r17-MutateSeatAudit2/M02-status-blind-unparsed-minor.py /var/tmp/souji-r17-MutateSeatAudit2/M03-first-header-only.py /var/tmp/souji-r17-MutateSeatAudit2/M04-no-normpath.py /var/tmp/souji-r17-MutateSeatAudit2/M05-blanket-var-tmp.py /var/tmp/souji-r17-MutateSeatAudit2/M06-remove-v-probe.py /var/tmp/souji-r17-MutateSeatAudit2/M07-relative-to-minor.py /var/tmp/souji-r17-MutateSeatAudit2/M08-drop-severity-comparison.py /var/tmp/souji-r17-MutateSeatAudit2/M09-restore-lstrip.py /var/tmp/souji-r17-MutateSeatAudit2/M10-drop-run-seat-scratch.py /var/tmp/souji-r17-MutateSeatAudit2/M11-prefix-without-boundary.py /var/tmp/souji-r17-MutateSeatAudit2/M12-allow-unparsed-target.py
```
**Confinement:** the committed selftest explicitly uses `TemporaryDirectory(dir="/var/tmp")` (`:338`). To respect this seat's tighter scratch-only write bound without modifying source bytes, all 36 Python commands used `PYTHONPATH=/var/tmp/souji-r17-MutateSeatAudit2/support` and `PYTHONDONTWRITEBYTECODE=1`. The identical `sitecustomize.py` below redirected only that temporary-directory parent into this seat's scratch. It did not change auditor logic, fixture lines, assertions, return codes, or results. The selftest removed its own temporary directories.
```python
import tempfile

_original_temporary_directory = tempfile.TemporaryDirectory

def _seat_temporary_directory(*args, **kwargs):
    if kwargs.get("dir") == "/var/tmp":
        kwargs["dir"] = "/var/tmp/souji-r17-MutateSeatAudit2"
    return _original_temporary_directory(*args, **kwargs)

tempfile.TemporaryDirectory = _seat_temporary_directory
```
## Before / mutated / restored SHA-256
`B` below denotes the full digest `8268212db158186d3d6dedc22ffb4755c89d7e62cfff2210b7c6329ca58d5f54`. Each pristine and restored entry was actually returned by `sha256sum`, not inferred from the write call.
| ID | Before | Mutated | Restored | Pristine rc | Mutated rc | Restored rc |
|---|---|---|---|---|---|---|
| M01 | B | `69bb187a76c1121c29e93d9dd972ee92a5bb9993ee9bb9e96e67c5fe2a4d1322` | B | 0 | 1 | 0 |
| M02 | B | `75888b73b24f176d62eca832ef07e2829d630bdc1463813a81f6346a9be60e6e` | B | 0 | 1 | 0 |
| M03 | B | `21118674b7f8c8d6a748bbd8bea21b8262d0671913ca289ae7a640f92e8b428f` | B | 0 | 1 | 0 |
| M04 | B | `172297f01d5ad551c163e5c7350e911ceead27bc3f849dda3e5af503d273e061` | B | 0 | 1 | 0 |
| M05 | B | `77fc15deb02411dc58b8b0109acd046838d786daff1fc233a5d091b7c3faa2f1` | B | 0 | 1 | 0 |
| M06 | B | `66b9d72dc6b8e159c0928cd07592e0fd8e076c64b26593820bbc167692e7be86` | B | 0 | 1 | 0 |
| M07 | B | `cb2858a6ae105b719cd9ebdb2883c492b2e82e20a6dd4dc25a75043e5b8e57c2` | B | 0 | 1 | 0 |
| M08 | B | `3e1cbb0406d4441a484737dd0a4e9d32a0046721f13e3aab57bbcf9f3885a204` | B | 0 | 0 | 0 |
| M09 | B | `1809efdc138f795aa6fd089c73a8ac34b463920ff479bcd04600fa2f7466d63a` | B | 0 | 0 | 0 |
| M10 | B | `ea7ec1aa5b46da48642ea9b99f297b3bda3a2be5de7000eec694c49501b26099` | B | 0 | 0 | 0 |
| M11 | B | `1640dd2817b71b92e365187c1465da4ebe14b5b2097fa8792f4d03aca76f3d61` | B | 0 | 0 | 0 |
| M12 | B | `b4115d26c32b7ddc3f4e9269accf112ce575fb62fcc7fb2d0324311c7659fea6` | B | 0 | 1 | 0 |

## Actual detector stdout
### Common pristine and restored output (all 24 invocations)
The complete stdout below was byte-identical for every pristine and restored run. SHA-256 of this stdout: `3f5895727d9d01db631f4a459d313682bfeabbbc77555865d035dea010dad4fb`. Stderr was empty.
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
PASS	report-edit-relative-dotufo
PASS	report-edit-table-prose
PASS	report-edit-sentence-prose
PASS	edit-abs-foreign-placeholder
PASS	state-path
PASS	reviewer-standalone-selftest
PASS	reviewer-shell-exec
PASS	foreign-write-report-as-content
PASS	edit-header-relative-owned
PASS	recursive-glob-tool
PASS	recursive-grep-root-slash
PASS	probe-realpath-lane
PASS	probe-strace-fleet
PASS	probe-readlink-scratch
PASS	probe-find-dot
PASS	h1-rel-write-ok
PASS	h2-bare-write-ok
PASS	h3-trunc-foreign-abs
PASS	h3b-trunc-header-foreign
PASS	h4-trunc-lane-report
PASS	h5-unparsed-ok
PASS	h5b-unparsed-error
PASS	h6-multi-header
PASS	h7-dotdot-scratch
PASS	h8-trunc-header-rel
PASS	scratch-seat-write
PASS	scratch-other-seat
PASS	scratch-unscoped-executor
PASS	scratch-trunc-header
PASS	wave-summary
SELFTEST	pass=49	fail=0
```

### M01 mutated — KILLED, rc 1

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
PASS	report-edit-relative-dotufo
PASS	report-edit-table-prose
PASS	report-edit-sentence-prose
PASS	edit-abs-foreign-placeholder
PASS	state-path
PASS	reviewer-standalone-selftest
PASS	reviewer-shell-exec
PASS	foreign-write-report-as-content
PASS	edit-header-relative-owned
PASS	recursive-glob-tool
PASS	recursive-grep-root-slash
PASS	probe-realpath-lane
PASS	probe-strace-fleet
PASS	probe-readlink-scratch
PASS	probe-find-dot
PASS	h1-rel-write-ok
FAIL	h2-bare-write-ok	got=[]	want=[('V-WRITE-RELATIVE', 'major')]
PASS	h3-trunc-foreign-abs
PASS	h3b-trunc-header-foreign
PASS	h4-trunc-lane-report
PASS	h5-unparsed-ok
PASS	h5b-unparsed-error
PASS	h6-multi-header
PASS	h7-dotdot-scratch
PASS	h8-trunc-header-rel
PASS	scratch-seat-write
PASS	scratch-other-seat
PASS	scratch-unscoped-executor
PASS	scratch-trunc-header
PASS	wave-summary
SELFTEST	pass=48	fail=1
```

Stderr: empty.

### M02 mutated — KILLED, rc 1

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
PASS	report-edit-relative-dotufo
PASS	report-edit-table-prose
PASS	report-edit-sentence-prose
PASS	edit-abs-foreign-placeholder
PASS	state-path
PASS	reviewer-standalone-selftest
PASS	reviewer-shell-exec
PASS	foreign-write-report-as-content
PASS	edit-header-relative-owned
PASS	recursive-glob-tool
PASS	recursive-grep-root-slash
PASS	probe-realpath-lane
PASS	probe-strace-fleet
PASS	probe-readlink-scratch
PASS	probe-find-dot
PASS	h1-rel-write-ok
PASS	h2-bare-write-ok
PASS	h3-trunc-foreign-abs
PASS	h3b-trunc-header-foreign
FAIL	h4-trunc-lane-report	got=[('V-WRITE-UNPARSED', 'minor')]	want=[('V-WRITE-UNPARSED', 'major')]
FAIL	h5-unparsed-ok	got=[('V-WRITE-UNPARSED', 'minor')]	want=[('V-WRITE-UNPARSED', 'major')]
PASS	h5b-unparsed-error
PASS	h6-multi-header
PASS	h7-dotdot-scratch
PASS	h8-trunc-header-rel
PASS	scratch-seat-write
PASS	scratch-other-seat
PASS	scratch-unscoped-executor
PASS	scratch-trunc-header
PASS	wave-summary
SELFTEST	pass=47	fail=2
```

Stderr: empty.

### M03 mutated — KILLED, rc 1

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
PASS	report-edit-relative-dotufo
PASS	report-edit-table-prose
PASS	report-edit-sentence-prose
PASS	edit-abs-foreign-placeholder
PASS	state-path
PASS	reviewer-standalone-selftest
PASS	reviewer-shell-exec
PASS	foreign-write-report-as-content
PASS	edit-header-relative-owned
PASS	recursive-glob-tool
PASS	recursive-grep-root-slash
PASS	probe-realpath-lane
PASS	probe-strace-fleet
PASS	probe-readlink-scratch
PASS	probe-find-dot
PASS	h1-rel-write-ok
PASS	h2-bare-write-ok
PASS	h3-trunc-foreign-abs
PASS	h3b-trunc-header-foreign
PASS	h4-trunc-lane-report
PASS	h5-unparsed-ok
PASS	h5b-unparsed-error
FAIL	h6-multi-header	got=[]	want=[('V-WRITE-SCOPE', 'major')]
PASS	h7-dotdot-scratch
FAIL	h8-trunc-header-rel	got=[]	want=[('V-WRITE-RELATIVE', 'major')]
PASS	scratch-seat-write
PASS	scratch-other-seat
PASS	scratch-unscoped-executor
PASS	scratch-trunc-header
PASS	wave-summary
SELFTEST	pass=47	fail=2
```

Stderr: empty.

### M04 mutated — KILLED, rc 1

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
PASS	report-edit-relative-dotufo
PASS	report-edit-table-prose
PASS	report-edit-sentence-prose
PASS	edit-abs-foreign-placeholder
PASS	state-path
PASS	reviewer-standalone-selftest
PASS	reviewer-shell-exec
PASS	foreign-write-report-as-content
PASS	edit-header-relative-owned
PASS	recursive-glob-tool
PASS	recursive-grep-root-slash
PASS	probe-realpath-lane
PASS	probe-strace-fleet
PASS	probe-readlink-scratch
PASS	probe-find-dot
PASS	h1-rel-write-ok
PASS	h2-bare-write-ok
PASS	h3-trunc-foreign-abs
PASS	h3b-trunc-header-foreign
PASS	h4-trunc-lane-report
PASS	h5-unparsed-ok
PASS	h5b-unparsed-error
PASS	h6-multi-header
FAIL	h7-dotdot-scratch	got=[]	want=[('V-WRITE-SCOPE', 'major')]
PASS	h8-trunc-header-rel
PASS	scratch-seat-write
PASS	scratch-other-seat
PASS	scratch-unscoped-executor
PASS	scratch-trunc-header
PASS	wave-summary
SELFTEST	pass=48	fail=1
```

Stderr: empty.

### M05 mutated — KILLED, rc 1

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
PASS	report-edit-relative-dotufo
PASS	report-edit-table-prose
PASS	report-edit-sentence-prose
PASS	edit-abs-foreign-placeholder
PASS	state-path
PASS	reviewer-standalone-selftest
PASS	reviewer-shell-exec
PASS	foreign-write-report-as-content
PASS	edit-header-relative-owned
PASS	recursive-glob-tool
PASS	recursive-grep-root-slash
PASS	probe-realpath-lane
PASS	probe-strace-fleet
PASS	probe-readlink-scratch
PASS	probe-find-dot
PASS	h1-rel-write-ok
PASS	h2-bare-write-ok
PASS	h3-trunc-foreign-abs
PASS	h3b-trunc-header-foreign
PASS	h4-trunc-lane-report
PASS	h5-unparsed-ok
PASS	h5b-unparsed-error
PASS	h6-multi-header
PASS	h7-dotdot-scratch
PASS	h8-trunc-header-rel
PASS	scratch-seat-write
FAIL	scratch-other-seat	got=[]	want=[('V-WRITE-SCOPE', 'major')]
PASS	scratch-unscoped-executor
PASS	scratch-trunc-header
PASS	wave-summary
SELFTEST	pass=48	fail=1
```

Stderr: empty.

### M06 mutated — KILLED, rc 1

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
FAIL	recursive-find	got=[('V-RECURSIVE', 'minor')]	want=[('V-PROBE', 'minor'), ('V-RECURSIVE', 'minor')]
PASS	recursive-grep-tool
PASS	peer-message
PASS	edit-relative-owned
PASS	edit-relative-foreign
PASS	shellcheck-not-exec
PASS	pattern-word-not-surface
PASS	report-edit-relative-dotufo
PASS	report-edit-table-prose
PASS	report-edit-sentence-prose
PASS	edit-abs-foreign-placeholder
PASS	state-path
PASS	reviewer-standalone-selftest
PASS	reviewer-shell-exec
PASS	foreign-write-report-as-content
PASS	edit-header-relative-owned
PASS	recursive-glob-tool
PASS	recursive-grep-root-slash
FAIL	probe-realpath-lane	got=[]	want=[('V-PROBE', 'minor')]
FAIL	probe-strace-fleet	got=[]	want=[('V-PROBE', 'minor')]
PASS	probe-readlink-scratch
FAIL	probe-find-dot	got=[('V-RECURSIVE', 'minor')]	want=[('V-PROBE', 'minor'), ('V-RECURSIVE', 'minor')]
PASS	h1-rel-write-ok
PASS	h2-bare-write-ok
PASS	h3-trunc-foreign-abs
PASS	h3b-trunc-header-foreign
PASS	h4-trunc-lane-report
PASS	h5-unparsed-ok
PASS	h5b-unparsed-error
PASS	h6-multi-header
PASS	h7-dotdot-scratch
PASS	h8-trunc-header-rel
PASS	scratch-seat-write
PASS	scratch-other-seat
PASS	scratch-unscoped-executor
PASS	scratch-trunc-header
PASS	wave-summary
SELFTEST	pass=45	fail=4
```

Stderr: empty.

### M07 mutated — KILLED, rc 1

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
FAIL	edit-relative-foreign	got=[('V-WRITE-RELATIVE', 'minor')]	want=[('V-WRITE-RELATIVE', 'major')]
PASS	shellcheck-not-exec
PASS	pattern-word-not-surface
FAIL	report-edit-relative-dotufo	got=[('V-WRITE-RELATIVE', 'minor')]	want=[('V-WRITE-RELATIVE', 'major')]
PASS	report-edit-table-prose
PASS	report-edit-sentence-prose
PASS	edit-abs-foreign-placeholder
PASS	state-path
PASS	reviewer-standalone-selftest
PASS	reviewer-shell-exec
PASS	foreign-write-report-as-content
PASS	edit-header-relative-owned
PASS	recursive-glob-tool
PASS	recursive-grep-root-slash
PASS	probe-realpath-lane
PASS	probe-strace-fleet
PASS	probe-readlink-scratch
PASS	probe-find-dot
FAIL	h1-rel-write-ok	got=[('V-WRITE-RELATIVE', 'minor')]	want=[('V-WRITE-RELATIVE', 'major')]
FAIL	h2-bare-write-ok	got=[('V-WRITE-RELATIVE', 'minor')]	want=[('V-WRITE-RELATIVE', 'major')]
PASS	h3-trunc-foreign-abs
PASS	h3b-trunc-header-foreign
PASS	h4-trunc-lane-report
PASS	h5-unparsed-ok
PASS	h5b-unparsed-error
PASS	h6-multi-header
PASS	h7-dotdot-scratch
FAIL	h8-trunc-header-rel	got=[('V-WRITE-RELATIVE', 'minor')]	want=[('V-WRITE-RELATIVE', 'major')]
PASS	scratch-seat-write
PASS	scratch-other-seat
PASS	scratch-unscoped-executor
PASS	scratch-trunc-header
PASS	wave-summary
SELFTEST	pass=44	fail=5
```

Stderr: empty.

### M08 mutated — SURVIVED, rc 0

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
PASS	report-edit-relative-dotufo
PASS	report-edit-table-prose
PASS	report-edit-sentence-prose
PASS	edit-abs-foreign-placeholder
PASS	state-path
PASS	reviewer-standalone-selftest
PASS	reviewer-shell-exec
PASS	foreign-write-report-as-content
PASS	edit-header-relative-owned
PASS	recursive-glob-tool
PASS	recursive-grep-root-slash
PASS	probe-realpath-lane
PASS	probe-strace-fleet
PASS	probe-readlink-scratch
PASS	probe-find-dot
PASS	h1-rel-write-ok
PASS	h2-bare-write-ok
PASS	h3-trunc-foreign-abs
PASS	h3b-trunc-header-foreign
PASS	h4-trunc-lane-report
PASS	h5-unparsed-ok
PASS	h5b-unparsed-error
PASS	h6-multi-header
PASS	h7-dotdot-scratch
PASS	h8-trunc-header-rel
PASS	scratch-seat-write
PASS	scratch-other-seat
PASS	scratch-unscoped-executor
PASS	scratch-trunc-header
PASS	wave-summary
SELFTEST	pass=49	fail=0
```

Stderr: empty.

### M09 mutated — SURVIVED, rc 0

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
PASS	report-edit-relative-dotufo
PASS	report-edit-table-prose
PASS	report-edit-sentence-prose
PASS	edit-abs-foreign-placeholder
PASS	state-path
PASS	reviewer-standalone-selftest
PASS	reviewer-shell-exec
PASS	foreign-write-report-as-content
PASS	edit-header-relative-owned
PASS	recursive-glob-tool
PASS	recursive-grep-root-slash
PASS	probe-realpath-lane
PASS	probe-strace-fleet
PASS	probe-readlink-scratch
PASS	probe-find-dot
PASS	h1-rel-write-ok
PASS	h2-bare-write-ok
PASS	h3-trunc-foreign-abs
PASS	h3b-trunc-header-foreign
PASS	h4-trunc-lane-report
PASS	h5-unparsed-ok
PASS	h5b-unparsed-error
PASS	h6-multi-header
PASS	h7-dotdot-scratch
PASS	h8-trunc-header-rel
PASS	scratch-seat-write
PASS	scratch-other-seat
PASS	scratch-unscoped-executor
PASS	scratch-trunc-header
PASS	wave-summary
SELFTEST	pass=49	fail=0
```

Stderr: empty.

### M10 mutated — SURVIVED, rc 0

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
PASS	report-edit-relative-dotufo
PASS	report-edit-table-prose
PASS	report-edit-sentence-prose
PASS	edit-abs-foreign-placeholder
PASS	state-path
PASS	reviewer-standalone-selftest
PASS	reviewer-shell-exec
PASS	foreign-write-report-as-content
PASS	edit-header-relative-owned
PASS	recursive-glob-tool
PASS	recursive-grep-root-slash
PASS	probe-realpath-lane
PASS	probe-strace-fleet
PASS	probe-readlink-scratch
PASS	probe-find-dot
PASS	h1-rel-write-ok
PASS	h2-bare-write-ok
PASS	h3-trunc-foreign-abs
PASS	h3b-trunc-header-foreign
PASS	h4-trunc-lane-report
PASS	h5-unparsed-ok
PASS	h5b-unparsed-error
PASS	h6-multi-header
PASS	h7-dotdot-scratch
PASS	h8-trunc-header-rel
PASS	scratch-seat-write
PASS	scratch-other-seat
PASS	scratch-unscoped-executor
PASS	scratch-trunc-header
PASS	wave-summary
SELFTEST	pass=49	fail=0
```

Stderr: empty.

### M11 mutated — SURVIVED, rc 0

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
PASS	report-edit-relative-dotufo
PASS	report-edit-table-prose
PASS	report-edit-sentence-prose
PASS	edit-abs-foreign-placeholder
PASS	state-path
PASS	reviewer-standalone-selftest
PASS	reviewer-shell-exec
PASS	foreign-write-report-as-content
PASS	edit-header-relative-owned
PASS	recursive-glob-tool
PASS	recursive-grep-root-slash
PASS	probe-realpath-lane
PASS	probe-strace-fleet
PASS	probe-readlink-scratch
PASS	probe-find-dot
PASS	h1-rel-write-ok
PASS	h2-bare-write-ok
PASS	h3-trunc-foreign-abs
PASS	h3b-trunc-header-foreign
PASS	h4-trunc-lane-report
PASS	h5-unparsed-ok
PASS	h5b-unparsed-error
PASS	h6-multi-header
PASS	h7-dotdot-scratch
PASS	h8-trunc-header-rel
PASS	scratch-seat-write
PASS	scratch-other-seat
PASS	scratch-unscoped-executor
PASS	scratch-trunc-header
PASS	wave-summary
SELFTEST	pass=49	fail=0
```

Stderr: empty.

### M12 mutated — KILLED, rc 1

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
PASS	report-edit-relative-dotufo
FAIL	report-edit-table-prose	got=[]	want=[('V-WRITE-UNPARSED', 'minor')]
FAIL	report-edit-sentence-prose	got=[]	want=[('V-WRITE-UNPARSED', 'minor')]
PASS	edit-abs-foreign-placeholder
PASS	state-path
PASS	reviewer-standalone-selftest
PASS	reviewer-shell-exec
PASS	foreign-write-report-as-content
PASS	edit-header-relative-owned
PASS	recursive-glob-tool
PASS	recursive-grep-root-slash
PASS	probe-realpath-lane
PASS	probe-strace-fleet
PASS	probe-readlink-scratch
PASS	probe-find-dot
PASS	h1-rel-write-ok
PASS	h2-bare-write-ok
PASS	h3-trunc-foreign-abs
PASS	h3b-trunc-header-foreign
PASS	h4-trunc-lane-report
FAIL	h5-unparsed-ok	got=[]	want=[('V-WRITE-UNPARSED', 'major')]
FAIL	h5b-unparsed-error	got=[]	want=[('V-WRITE-UNPARSED', 'minor')]
PASS	h6-multi-header
PASS	h7-dotdot-scratch
PASS	h8-trunc-header-rel
PASS	scratch-seat-write
PASS	scratch-other-seat
PASS	scratch-unscoped-executor
PASS	scratch-trunc-header
PASS	wave-summary
SELFTEST	pass=45	fail=4
```

Stderr: empty.

## Restoration, cleanup, and scope
All twelve copies were restored in a finally block to the captured committed source, then hashed and run through the identical detector. Every restored hash equals the committed-source hash; all twelve restored runs returned 0 / 49 passed. No detector result was counted as killed solely because it errored.
No tools were installed or updated. No network writes, fleet-root writes, production-tool execution against live repositories, production-source changes, or additional-runtime invocations were used. The only retained lane write is this assigned report.
After the restoration measurements, the edit tool removed all twelve restored copies plus the confinement module. The following final command removed both now-empty directories, proving no scratch residue remained (rc 0; stdout and stderr empty):

```sh
rmdir /var/tmp/souji-r17-MutateSeatAudit2/support /var/tmp/souji-r17-MutateSeatAudit2
```
