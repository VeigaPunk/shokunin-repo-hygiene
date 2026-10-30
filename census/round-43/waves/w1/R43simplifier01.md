# R43simplifier01 — frozen-instrument complexity review

Axes: operability (less duplicate execution machinery), calibration (unchanged verdicts, explicit evidence limits), complexity (less dead state).

Verdict: **findings only; no deletion applied, no instrument edited, no outcome-equivalence test run**. All four reviewed working files matched the frozen commit f8c805dbfa7f45814cf9a7270fa8bbffb41a8373 byte-for-byte. Every proposed change below is marked **NFO [INFERENCE]**: no frozen case/leg outcome should change by local dataflow reasoning, NOT a measured pass. Freeze remains authoritative; these are findings for L1, not authorization to amend current scoring instruments.

## Candidates

Line numbers refer to frozen bytes. Deltas count physical source lines, excluding optional whitespace cleanup. Zero-line candidates simplify expressions/state without claiming LOC savings.

### census/round-43/c1-counter.py

| Simplification | Why safe / preserved contract | Estimated delta | Outcome |
|---|---|---:|---|
| Delete line 231, `raw = raw`. | The loop already binds the same string; no transformation, validation, or output is removed. Retain the surrounding fence boundary and correction checks. | -1 | NFO [INFERENCE] |
| Delete line 266, initial `new_mismatches = -1`. | Both arms of `if rev != BASE` assign before the summary or target reads it: line 276 assigns 0, line 278 restores -1 on evaluation refusal, and line 285 assigns 0 in the BASE arm. Preserve the refusal sentinel assignment at 278. | -1 | NFO [INFERENCE] |
| Replace lines 223–225 (`if lesson_b is None: pass; else:`) with `if lesson_b is not None:`. | The existing else body remains at its existing indentation. Absent lessons still retain initialized missing/registered counts; present lessons execute the exact same parser. | -2 | NFO [INFERENCE] |

### census/round-43/c2-counter.py

| Simplification | Why safe / preserved contract | Estimated delta | Outcome |
|---|---|---:|---|
| Delete line 82, `GOOD_PREREG_CLAIM`. | Literal reference search across the lane found only its definition. The actual synthetic claim is constructed at 138–140. No semantic-reference server is available; this is literal evidence only. | -1 | NFO [INFERENCE] |
| Change line 168 to `commit("freeze")`, removing the unused `freeze` binding. | Retain the commit call AND its internal rev-parse, preserving fixture history and subprocess sequencing; the returned revision is never read. Do not delete the freeze commit itself. | 0 | NFO [INFERENCE] |
| Make lines 191–197 a two-line `run_tool` wrapper returning `run_script(["python3", "-B", tool_path] + args, cwd, scratch, timeout)`. | Both existing helpers run the same subprocess options and catch only TimeoutExpired, returning the identical `(process, False)` / `(None, True)` shape. Preserve the timeout default and literal `python3` interpreter selection. `run_script` is defined before main invokes the wrapper. No new shared module. | -5 | NFO [INFERENCE] |

### census/round-43/c3-counter.py

| Simplification | Why safe / preserved contract | Estimated delta | Outcome |
|---|---|---:|---|
| Delete line 73, `PRE42 = PRIOR[:-1]`. | Literal lane-wide search found only the definition. No executed loop uses PRE42. This is unused state, NOT permission to switch the old_killed loop to eight fixtures. | -1 | NFO [INFERENCE] |
| Delete lines 366–367, `if fx_path == FIXTURE: continue`. | Under the frozen constants, every fx_path is one of the nine explicit PRIOR paths (68–72), and none equals `tests/fixtures/r43-drift-survivors.py` (64). The branch cannot execute; keep ALL nine oldscore iterations and their current outcomes, despite the eight-fixture prose description. | -2 | NFO [INFERENCE], frozen constants only |
| Decode stdout once at 344–345: first assign `txt = p.stdout.decode("utf-8", "replace")`, then `m = SUMMARY_RE.search(txt)`. | Existing code decodes the same immutable process stdout twice with identical parameters. Both consumers receive the same string; summary parsing, fail names, and all scoring remain unchanged. | 0 | NFO [INFERENCE] |

### tests/fixtures/r43-correction-prose.py

| Simplification | Why safe / preserved contract | Estimated delta | Outcome |
|---|---|---:|---|
| At 190 retain only `not l.startswith("CORRECTION-")`; remove the conjunct testing `CORRECTION-DE`. | Every string starting CORRECTION-DE also starts CORRECTION-. The conjunction rejects exactly the same lines, so clone lesson bytes and commits are unchanged. Preserve the historical HONEST42 provenance and both r42/r43 columns. | 0 | NFO [INFERENCE] |
| Replace lines 219–220 with a direct dict comprehension using the exact existing conversion: `fields = {k: (x if k == "population" else int(x)) for k, x in zip(keys, m.groups())}`. | The keys tuples are unique; conversion order remains left-to-right. The temporary pairs list has no other consumer. Population remains text; other fields remain integers. | -1 | NFO [INFERENCE] |
| At 221 store only `(p.returncode, fields)` in outs, dropping `out`. | All reads at 224 and 229 use indices 0 and 1; no reader accesses element 2. Keep `out` itself at 213 because regex parsing still needs it. Printed diagnostics already use rc/fields, not stored stdout. | 0 | NFO [INFERENCE] |

Aggregate estimated delta: **-14 physical lines**, plus four expression/state simplifications with zero LOC delta. No historical prose or anchor string is proposed for removal. Stop here: deleting refusal paths, controls, r42 signatures, or merging independent fixture oracle logic into a counter would risk calibration. Identical env/git wrappers across c1/c3 are intentionally retained: extracting them creates a new dependency/convention for little benefit and conflicts with standalone use.

## Evidence and exact operations

No shell counter invocation, clone, fixture commit, test, scorer, install, or scratch directory was created. Therefore there is no discarded scratch evidence or cleanup pending. No runtime outcome is reported as passing.

1. Read `skill://godspeed`, `skill://agent-self-evaluation`, and `/home/vgpnk/.omp/agent/RULES.md` using read. Attempted `read(path="xd://lsp")`: observed **`No such tool: xd://lsp`**. `read(path="xd://")` listed 330 devices and no lsp device. Thus no server status/references/warmup request was possible; no empty cold-index result was used. Literal search below is expressly not semantic proof.
2. Source reads (read tool, absolute lane prefix `/home/vgpnk/Projects/shokunin/souji-shokunin/`): `census/round-43/c1-counter.py:1-240`, `:244-298`; `census/round-43/c2-counter.py:1-260`, `:264-408`; `census/round-43/c3-counter.py:1-260`, `:264-425`; `tests/fixtures/r43-correction-prose.py:1-260`. Observed the definitions, initialization/assignment paths, and consumers cited above. Tool context included the adjacent lines at range boundaries.
3. Exact shell command run:

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree f8c805dbfa7f45814cf9a7270fa8bbffb41a8373 census/round-43/c1-counter.py census/round-43/c2-counter.py census/round-43/c3-counter.py tests/fixtures/r43-correction-prose.py
```

Observed exit 0:

```text
100755 blob 7eff5b00a030674d9c17012d81f4e97ecd3a6612 census/round-43/c1-counter.py
100755 blob 09bd4580be0717eabf8e514c39c00e9854d049df census/round-43/c2-counter.py
100755 blob 5429d5d9fd1752a34b900035770af6d81e9ab4ed census/round-43/c3-counter.py
100755 blob d2afec19e8c53868c8c792a3eaa6399257ba0ceb tests/fixtures/r43-correction-prose.py
```

4. Literal grep calls (case=true, gitignore=true):
   - pattern `GOOD_PREREG_CLAIM|freeze =|raw = raw|\bcid\b|\belapsed\b`, path `<lane>/census/round-43;<lane>/tests/fixtures/r43-correction-prose.py`;
   - pattern `\b(GOOD_PREREG_CLAIM|PRE42)\b|c[123]-counter|r43-correction-prose`, path `<lane>/census/round-43;<lane>/tests/fixtures`;
   - pattern `\b(GOOD_PREREG_CLAIM|PRE42)\b`, path `<lane>`.
   Final search observed exactly two matches: c2 line 82 and c3 line 73, both definitions. First searches exposed the unused local binding and consumers. No semantic absence claim is made.
5. Exact Python eval cell run to compute digests/baseline (no source executed):

```python
import os, subprocess, hashlib, pathlib
lane = pathlib.Path('/home/vgpnk/Projects/shokunin/souji-shokunin')
files = ['census/round-43/c1-counter.py','census/round-43/c2-counter.py','census/round-43/c3-counter.py','tests/fixtures/r43-correction-prose.py']
rev='f8c805dbfa7f45814cf9a7270fa8bbffb41a8373'
tracked=subprocess.check_output(['git','-C',str(lane),'ls-files','-z']).decode().split('\0')[:-1]
def snapshot():
    result={}
    for f in tracked:
        p=lane/f
        result[f]=hashlib.sha256(os.readlink(p).encode() if p.is_symlink() else p.read_bytes()).hexdigest() if p.exists() or p.is_symlink() else 'MISSING'
    return result
before=snapshot()
for f in files:
    frozen=subprocess.check_output(['git','-C',str(lane),'show',rev+':'+f])
    current=(lane/f).read_bytes()
    print(f, 'frozen_equal='+str(current==frozen), 'sha256='+hashlib.sha256(current).hexdigest())
print('TRACKED_BASELINE files='+str(len(before)))
print('LSP unavailable: xd://lsp returned No such tool; no cold empty result used.')
```

Observed all four `frozen_equal=True`; SHA256 in file order:

```text
fe2a8d4afe414ab96a21f08b717f578c36d680d3848921caf59531d9706d4e4d
7249969604c0a8d46788a980732f8b162f1d7f4a4387439876b4c623e0f6ee6b
66188cccb23bd35df69238cc05c2b5d84612e89590f09537b9f5c498a388b63f
d48a74238507ebe8b4638b4a20e3d234f2b4abbe84b7ba6b4914ab2aa86d4a4b
TRACKED_BASELINE files=14003
```

6. Exact final comparison eval cell:

```python
after=snapshot()
changed=[f for f in tracked if before[f]!=after[f]]
print('TRACKED_BYTE_COMPARISON files=%d changed=%d' % (len(tracked),len(changed)))
for f in changed: print(f)
print('SCRATCH_CREATED=False; no scratch to delete; no tool installed; no counter or fixture executed.')
```

Observed:

```text
TRACKED_BYTE_COMPARISON files=14003 changed=1
corpus/SOURCES.md
SCRATCH_CREATED=False; no scratch to delete; no tool installed; no counter or fixture executed.
```

**Shared-tree caveat:** a byte-identical whole-lane claim is NOT available: corpus/SOURCES.md changed during the observation window. This seat had made no writes at all at that point; the change is external to these read-only operations. The other 14,002 tracked paths, including all four reviewed instruments, compared equal. This report is the seat's sole write.

## Retained contract / proof boundary

All frozen parsing, finding classes, SUMMARY formatting, exit codes, controls, mutation anchors, and fixture cases remain untouched. The changes proposed above preserve logical outcomes by inspection; they do not promise byte-identical nondeterministic load/timing readings or traceback source line numbers. No empirical improvement is claimed. If L1 ever authorizes a new freeze, its existing correction-prose discrimination fixture and C1/C2/C3 controls/counters must be rerun in approved scratch, comparing every case/leg outcome; current frozen scoring must not be patched to enact these suggestions.

Self-evaluation: accuracy 4 (local dataflow evidence, no dynamic equivalence proof); completeness 4 (all four files covered, LSP unavailable); clarity 4 (NFO labels separate inference from measurement); actionability 4 (line-specific proposals, freeze authorization remains L1's); conciseness 4 (command evidence intentionally detailed). Overall 4.0/5. Primary improvement would be L1-authorized narrow differential execution before adopting any candidate; not performed in this findings-only seat.
