# R40executor50 — C2 operability attack

- Axis: operability.
- Distinct edge case: **token-led continuation shadowing** — a wrapped continuation starts with a second frozen class token and can be mistaken for that class's actual entry.
- Verdict: **bounded measurement plan; no concrete r40 falsifier established.** Committed r39 artifacts confirm the edge case and also show that the real r39-tip docstring already has `EACCES` on the first `RECORD-MISSING` line. Thus the required r40-vs-r39 discrimination must use the synthetic wrap probe; a real-tool-only comparison would not establish that control.

## Evidence pointers

1. Frozen target: `census/round-40/preregistration.txt:7-8` requires joining wrapped lines and verifying observed class/trigger pairs; its control is the r39 one-line analyzer.
2. Committed r39 analyzer: `census/round-39/c2-counter.py:133-146` uses `ast.get_docstring(..., clean=False)`, splits on newlines, and stores only the first stripped line starting with each of `RECORD-MISSING` and `RECORD-MALFORMED`.
3. Committed r39-tip drift source: `tools/souji-worktree-drift.py` at revision `0242085909fb6a4ee041c5443d76316ac6d59d4b`, module-docstring lines 43-50. The `RECORD-MISSING` first line itself says `EACCES`; the `RECORD-MALFORMED` entry wraps onto further lines. Runtime code at lines 131-139 maps `ENOENT` to `RECORD-MALFORMED` and other open errors to `RECORD-MISSING`.
4. Applying the committed r39 helper to the committed tip source returned:
   `{'RECORD-MISSING': 'RECORD-MISSING         EACCES or ELOOP opening the record path: the path', 'RECORD-MALFORMED': 'RECORD-MALFORMED       a missing (ENOENT) or non-regular record path, a line'}`.
   This establishes that the r39 one-line analyzer already observes the real tool's first-line EACCES/missing words; it does not establish the synthetic wrapped-trigger result.
5. Synthetic probe `token-led-continuation.py` (scratch only) contained a `RECORD-MISSING` entry ending in `for`, then a continuation `RECORD-MALFORMED handling is documented elsewhere`, then the actual `RECORD-MALFORMED` entry. The committed r39 helper mapped `RECORD-MALFORMED` to the intermediate line, proving the shadowing behavior. This probe is a distinct failure mode from merely placing a trigger on an ordinary indented continuation line.
6. The simple synthetic token-split probe showed r39 leaves the split `RECORD-` / `MISSING` token unrecognized; no r40 analyzer was available here to measure how its join policy handles it.

## B bounded measurement plan

At the candidate revision, run the r40 counter's actual analyzer on a synthetic module docstring with (a) an ordinary continuation carrying the trigger, and (b) a continuation beginning with another frozen class token before that class's true entry. Record parsed maps and the complete counter receipt. Verify that the second token-led line is not silently accepted as a mapping inconsistent with the runtime class/trigger pair, and that the ordinary wrapped-trigger probe is detected while the committed r39 helper misses it. State and exercise the exact continuation boundary and separator rule; otherwise two readings of “joins wrapped continuation lines” can produce different maps. Keep the r39 source bytes and helper as the control. Do not infer candidate success from this plan.

## Commands and observed outputs

- Read `/home/vgpnk/.omp/agent/RULES.md`, `skill://godspeed`, and `census/round-40/preregistration.txt`.
- Read committed artifact sources/receipt with `read`: `census/round-39/c2-counter.py:100-260`, `census/round-39/records/c2-after.txt`; located the class documentation/runtime sites in `tools/souji-worktree-drift.py`.
- Ran read-only extraction with `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 0242085909fb6a4ee041c5443d76316ac6d59d4b:<path>` for `tools/souji-worktree-drift.py` and `census/round-39/c2-counter.py`; `git cat-file -t` returned the base object type `commit`. The first attempt failed before execution because the specified scratch cwd did not yet exist; the successful retry created it first. No git mutation.
- Evaluated the extracted r39 helper against the extracted tool and two scratch-only synthetic docstrings. Exact observed helper maps are recorded above. No candidate r40 analyzer/counter was run.
- No installs or updates; no build, lint, formatter, or tests. Scratch was `/fast/scratch/hyaku/souji-r40/R40executor50` with `TMPDIR` set there and was removed before handoff.

## Limits

No r40 counter/candidate bytes or receipt were inspected or executed. The shadowing probe establishes a concrete r39 parser edge case and a test target, not that the frozen r40 predicate is already falsified. Candidate wrap-joining semantics, full observed-pair agreement, and the synthetic control comparison remain unmeasured.
