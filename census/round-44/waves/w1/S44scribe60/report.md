# S44scribe60 — round44 Gate/Mistakes fragment

Result: completed documentary fragment, not an admission decision or executed gate. Axes: calibration / operability / coverage; assigned axis: operability. Frozen assignment: d314fd6e85d62565344fa6c4b102f52f62297884, planner/integration owner L1, one v2 wave / 64 seats.

## Behavior and findings

Deliverable: `.ufo/waves/round-44/w1/S44scribe60/lesson-fragment.md` contains candidate Gate and Mistakes prose, concrete admit/reject rationale, historical red-before evidence, Q106 failability, and explicit outside-admission limits.

1. Oracle multiplicity error: r43 h4 expected literal `C2:FIELD-MISSING*4`, while its class collector returns four distinct entries. h6 omitted the `C0:FROZEN-EDITED` triggered by its own later preregistration commit. Frozen historical receipt has scenarios=10 pass=8 fail=2, EXIT=1. No product defect is inferred from those two oracle errors.
2. Prior verifier `corpus/lessons/round-43-verifier-spotcheck.md:36-40` evidence-verified that red and judged operability unchanged. Its routed item 2 rejects the memorizer control's missing-import crash as discrimination evidence. Its previous outside source agreement does not supply round44 admission.
3. R44 counter requires retained r43 red, new v2 audit, clean/findings stub rejection, control execution, self-test and missing-TMPDIR behavior. These are declared predicates; no seat execution claim is made.
4. Provenance limit discovered: `records/c2-first.txt` exists on disk and claims full-target success at the freeze revision, but is NOT a blob at that revision (git show exit 128 below). Therefore this report labels its success as an inherited on-disk receipt, never a frozen committed result or independent rerun.
5. Calibration remains a 70-row token-bound registration target, not 70 newly incorrect historical facts. C3 remains joint leaf-refusal/legacy-caller cutover, not deletion authorization or closure of sixteen historical survivor classes. These delimit the lesson fragment rather than assert their execution.

## Evidence inspected

Read with the file reader: `census/round-44/preregistration.txt`; r44 counter docstrings for C1/C2/C3; complete r44 C2 counter and hidden audit; C2 scenario table and do-nothing control; `records/{freeze,c1-before,c2-first,census-before}.txt`; r43 C2 counter contract and audit expectations; r43 `records/{c2-hidden-full,c2-landed,capture-committed-red}.txt`; `corpus/lessons/round-43.md` Gate/M43-1; full `round-43-verifier-spotcheck.md`; Q102/Q106 in `corpus/QUALITY.md`. Directory/glob/search calls located these artifacts. Also read godspeed, self-evaluation skill and host RULES.md. No tool installed or updated.

The inherited `records/freeze.txt` reports `SUMMARY claims=3 findings=0 EXIT=0`; the inherited `records/c1-before.txt` reports missing=70, lesson=absent, EXIT=1. Neither was executed by this seat. R44 `records/c2-first.txt` reads exactly:

```text
# rev=d314fd6e85d62565344fa6c4b102f52f62297884
SUMMARY tool=present population=ok retention=ok hidden_v2=10/10 clean_stub=REJECTED findings_stub=REJECTED controls_ran=ok selftest=ok tmpdir=ok
EXIT=0
```

## Exact shell commands and observed outcomes

Commands 2–5 used cwd `/fast/scratch/hyaku/souji-r44/S44scribe60/`; commands 1 and 6 used the fleet root. Commands were read-only except creating/removing the empty seat scratch. No fixture or gate runtime was invoked.

1. `mkdir -p /fast/scratch/hyaku/souji-r44/S44scribe60/` — exit 0, no output.
2. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show d314fd6e85d62565344fa6c4b102f52f62297884:census/round-44/records/c2-first.txt` — exit 128:

```text
fatal: path 'census/round-44/records/c2-first.txt' exists on disk, but not in 'd314fd6e85d62565344fa6c4b102f52f62297884'
```

3. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show d314fd6e85d62565344fa6c4b102f52f62297884:census/round-44/c2-counter.py | sha256sum` — exit 0:

```text
0cb6ce80a23b460d1a03e0530ca2ef0866af773bdb7f5b88f6dc84bd0f525252  -
```

Matches the preregistered counter SHA256.

4. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show d314fd6e85d62565344fa6c4b102f52f62297884:census/round-43/records/c2-hidden-full.txt` — exit 0; exact blob output:

```text
$ python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-43/c2-hidden-audit.py --tool /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-freeze-check.py --work /fast/scratch/hyaku/souji-r43/l1/hidden-full
scenario-h1-trailing-space-round=PASS
scenario-h2-round-spelled-x=PASS
scenario-h3-two-unattached-keys=PASS
scenario-h4-unattached-before-valid-claim=FAIL
#   got rc=1 classes=C0:HEADING-MALFORMED,C0:UNATTACHED-KEY,C2:FIELD-MISSING,C2:FIELD-MISSING,C2:FIELD-MISSING,C2:FIELD-MISSING
scenario-h5-control-symlink-exit0-text=PASS
scenario-h6-duplicate-three-occurrences=FAIL
#   got rc=1 classes=C0:FROZEN-EDITED,C1:KEY-DUPLICATE,C1:KEY-DUPLICATE
scenario-h7-dispatch-notes-ready=PASS
scenario-h8-crlf-prereg=PASS
scenario-h9-dispatch-depth-three=PASS
scenario-h10-missing-prereg-refusal=PASS
SUMMARY scenarios=10 pass=8 fail=2

EXIT=1
```

The Python command above is text in the historical receipt, not a command executed by S44scribe60. Git retrieval exit 0 is not the historical audit exit 1.

5. `sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-44/c2-counter.py /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-44/c2-scenarios.tsv` — exit 0:

```text
0cb6ce80a23b460d1a03e0530ca2ef0866af773bdb7f5b88f6dc84bd0f525252  /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-44/c2-counter.py
6a68a10161745c7974e93afe9724853f1a61fc192185c128c88840b1977a7054  /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-44/c2-scenarios.tsv
```

Both match preregistration. Only the counter's frozen blob was independently hashed here; the population hash is a worktree-byte observation.

6. `rmdir /fast/scratch/hyaku/souji-r44/S44scribe60/` — exit 0, no output; seat scratch removed.

## Gates, limits and instruction conflicts

No gates rerun, no independent round44 PASS asserted. The higher-priority scribe role says “Do not rerun work merely to decorate the report” and “Do not edit product code, judge, commit, push, publish, deploy, or invoke another runtime.” The assignment says “You are explicitly assigned to run the relevant bounded checks/probes.” This seat performed bounded documentary/hash/provenance checks only; runtime counter execution was intentionally not substituted for the scribe contract. Retained receipts are evidence of their authors' recorded runs, not this seat's execution.

Output-path conflict, quoted verbatim: “Output only in /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-44/w1/S44scribe60/; write report.md there.” and “Report: write your scoped findings to .ufo/waves/round-44/w1/S44scribe60.md”. Both explicitly named report locations are supplied; the trailer is a pointer to this full report. No sibling output is modified.

Touched surfaces: own fragment, this report, required trailer pointer, own empty scratch (removed). Product, frozen counters, sources, shared LOG, git index/jj state, sibling/fleet files unchanged by this seat. No commit/push/deploy, no pacman transaction, no provider-denial bypass, no delegation. Fresh source fetching, runtime verification, score changes, final lesson integration and non-author admission are outside this scribe execution.

## Self-evaluation (not a gate)

Accuracy 4/5: provenance distinguishes retrieval success from historical gate failure; new audit not executed. Completeness 4/5: requested fragment and rationale supplied; runtime checks constrained by role. Clarity 4/5: historical and current claims separated, though evidence block is long. Actionability 4/5: L1 receives ready-to-integrate prose, not admission clearance. Conciseness 4/5: exact receipt repeats existing evidence to preserve an auditable handoff. Overall 4.0/5. Improvements: bind the inherited success receipt to its actual carrier revision during integration; keep all historical reds verbatim; obtain independent round44 closure outside this seat. Would the user agree? The report makes those limits explicit rather than claiming approval.
