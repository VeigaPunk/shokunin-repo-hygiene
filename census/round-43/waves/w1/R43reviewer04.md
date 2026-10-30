# R43reviewer04 — frozen hidden-audit review

Axes: operability (grammar-correct expectations), coverage (each named fixture actually exercises its shape).
Scope: `census/round-43/c2-hidden-audit.py` at `f8c805dbfa7f45814cf9a7270fa8bbffb41a8373`; findings only. No lane source changes, installs, candidate creation, scoring/admission, or other agent runtime.

## Findings, severity first

### High — h4 compares a literal repetition marker instead of four findings
Attacks: C2 hidden audit expectation, `census/round-43/c2-hidden-audit.py:115-116,100-106,160`.
The builder correctly creates one unattached Target followed by valid C2 with only Target and Kill. C2 therefore lacks Base, Counter, Population and Control, producing four separate `C2:FIELD-MISSING` findings. The frozen expected list instead contains the single string `C2:FIELD-MISSING*4`. Unlike the table loader in `census/round-43/c2-counter.py:218-233`, this audit never expands repetition markers. Its exact list comparison rejects the grammar-correct output. The preserved probe constructs the normative six-line finding emission (one malformed heading, one unattached key, four missing fields) and observes `h4 normative_emission_accepted=False`. This is a scoring blocker, not an old-tool defect.

### High — h6 edits the preregistration after FREEZE but omits the mandatory edit finding
Attacks: C2 hidden audit builder/expectation, `census/round-43/c2-hidden-audit.py:87,118,143-154,160`.
`build()` already commits the one-Base preregistration. h6 then inserts two Base lines and commits again. The canonical FREEZE selector is the oldest adding commit (`tools/souji-freeze-check.py:116-120`), not the final duplicate commit. Actual git blobs show `freeze_Base_count=1 rev_Base_count=3 prereg_changed=True freeze_is_tip=False`. Thus h6 builds the named duplicate shape at REV, but also a post-freeze preregistration edit: it is defective as an isolated duplicate fixture. The r43 grammar explicitly requires `C0:FROZEN-EDITED` for that difference (`census/round-43/c2-counter.py:22-24`). Its expected two `C1:KEY-DUPLICATE` findings omit that additional mandatory finding. A compliant implementation reporting both duplicates and the edit is rejected. This is distinct from the pinned old tool reporting only one duplicate, which is an intended r43 behavior gap.

## Per-scenario assessment
All file:line references below are to frozen `census/round-43/c2-hidden-audit.py` unless qualified. “Expectation OK” is a grammar/source conclusion, not a claim that an r43 candidate was run.

| Scenario | Builder | Expectation | Evidence / file:line |
|---|---|---|---|
| h1 trailing-space-round | OK | OK | `111,73-86`: trailing whitespace is outside the numeric Round value; inherited Round whitespace handling is `tools/souji-freeze-check.py:48`. Pinned tool exits 0, no findings. |
| h2 round-spelled-x | OK | OK | `112`: `1729x` is not strict ASCII positive decimal; normative `c2-counter.py:18-19` requires one ROUND-MALFORMED, not a missing Round. Pinned old tool's FIELD-MISSING is expected nonconformance, not an audit defect. |
| h3 two-unattached-keys | OK | OK | `113-114`: malformed `##C2` followed by Population and Control, no intervening valid heading. Normative `c2-counter.py:15-17` implies one heading finding and two unattached keys. |
| h4 unattached-before-valid-claim | OK | **Defect** | `115-116,160`: malformed heading, unattached Target, then valid C2 with Target/Kill; missing-four shorthand is never expanded. See high finding. |
| h5 control-symlink-exit0-text | OK | OK | `82-83,117`: observed committed mode 120000; link blob exactly `EXIT=0`. Normative `c2-counter.py:20-21` requires CONTROL-SYMLINK and no red-control read. Pinned old tool reports CONTROL-NOT-RED, an intended old-tool gap. |
| h6 duplicate-three-occurrences | **Defect (extra post-freeze edit)** | **Defect** | `87,118,143-154`: observed one Base at FREEZE versus three at REV. Two duplicate findings are correct at REV, but C0:FROZEN-EDITED is missing from expected list. |
| h7 dispatch-notes-ready | OK | OK | `66-69,119`: committed `.ufo/waves/round-1729/notes.ready` before prereg creation. Inherited dispatch recognizer matches `.ready` (`tools/souji-freeze-check.py:123-148`); observed one finding, exit 1. |
| h8 crlf-prereg | OK | OK | `86,120`: observed 11 CRLF, 11 LF, zero bare LF; valid content otherwise. Pinned tool exits 0 with no findings. |
| h9 dispatch-depth-three | OK | OK | `66-69,121`: committed `w9/w8/deep-spec.json` beneath round directory before FREEZE. Inherited recursive history and basename suffix recognition apply at arbitrary depth (`tools/souji-freeze-check.py:130-147`); observed one finding, exit 1. |
| h10 missing-prereg-refusal | OK | OK | `136-142`: normal valid repo, resolved tip, but requested `census/absent-prereg.txt` absent. Canonical refusal path `tools/souji-freeze-check.py:353-366` reads the missing blob and raises Refusal before evaluation. Observed rc=2, empty stdout, stderr `REFUSAL COULD-NOT-EVALUATE: census/absent-prereg.txt is absent at ...`; the scenario actually refuses for the intended reason. |

## Commands and observed evidence

Lane absolute path used for every git read: `/home/vgpnk/Projects/shokunin/souji-shokunin`.

Exact source-reading commands (all exit 0):
```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show f8c805dbfa7f45814cf9a7270fa8bbffb41a8373:census/round-43/c2-hidden-audit.py
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show f8c805dbfa7f45814cf9a7270fa8bbffb41a8373:census/round-43/c2-counter.py
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show f8c805dbfa7f45814cf9a7270fa8bbffb41a8373:tools/souji-freeze-check.py
```
The first two were issued directly, then all three via Python `subprocess.run([...], capture_output=True, check=True)` to preserve exact frozen snapshots as `R43reviewer04/hidden.py` (7550 bytes), `counter.py` (19908), `freeze.py` (18550). These copies retain original source line numbers.

Exact behavioral probe command (cwd was the seat directory):
```
env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/fast/scratch/hyaku/souji-r43/R43reviewer04 python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-43/w1/R43reviewer04/probe.py
```
Observed process exit 0; nested frozen audit exit 1, `SUMMARY scenarios=10 pass=5 fail=5`. Complete observed stdout, tool stderr, scenario classes, h6 blob-shape measurements and h4 class comparison are preserved in `.ufo/waves/round-43/w1/R43reviewer04/receipt.txt`; reproducible driver is adjacent `probe.py`. Driver runs the unmodified frozen audit builders/checker, wrapping subprocess calls only to assert exact repository roots before every add/commit, and wrapping audit `run()` to record git shape/output. No fixture identity is exported to the shell. Every fixture is under seat scratch; `finally` removed the entire scratch directory (`scratch_removed=True`). Source snapshots and receipts are in the seat, not scratch.

LSP: `read xd://lsp` returned `No such tool: xd://lsp`; no semantic server/status/references/definition/diagnostics device was available. Source review used explicit pinned git blobs and tool `read` ranges, not grep as semantic proof.

## Verdict and residual gaps

Recommendation: hidden audit is not a valid all-green acceptance instrument as frozen: h4 and h6 reject grammar-compliant behavior. h10 is sound and demonstrably refuses. No fixes made to frozen instruments.

No full c2 counter, candidate score, or new compliant implementation was run; old checker 5/10 is not presented as candidate acceptance or saturation. Round-value whitespace interpretation for h1 inherits existing grammar handling; the new strict-digit rule does not explicitly redefine surrounding whitespace. h10 only checks rc=2 and stderr substring REFUSAL, so this establishes the frozen canonical tool's correct refusal, not universal proof of every possible candidate's refusal cause. Resume continuity, rerouting and runtime admission are outside this fixture-builder assignment.

Self-evaluation: accuracy 4 (compliant h6 rejection follows normative grammar and observed blobs, not a candidate execution); completeness 5 (all ten builders and expectations assessed); clarity 4 (source and runtime conclusions separated but report necessarily detailed); actionability 5 (two precise frozen defects with locations/receipts); conciseness 4 (per-scenario acceptance requires a table). Overall 4.4/5. Highest-impact future verification is L1 testing the eventual candidate against corrected instrument expectations, not altering these frozen bytes here. No tools installed or updated.
