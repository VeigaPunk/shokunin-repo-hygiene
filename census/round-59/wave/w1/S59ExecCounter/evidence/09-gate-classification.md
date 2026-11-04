# Gate classification of the r58 assessment comparator

Scope: read-only classification of `census/round-58/c1-counter.py` (blob
sha256 `52ccdb1be66dd8379fb7bf81eae7e28965f156aa50e1e4573b82adb23bd0dea7`,
identical at `da5af55b` and worktree) against the canonical standard at fleet
root `PROTOCOL.md:375-408` (`## Gate standard`), plus the lane's local gate map
in `SKILL.md:196-204`. No file was edited.

## What the comparator does (read directly)

| anchor | behavior |
|---|---|
| `census/round-58/c1-counter.py:8` | reads every surface through `git -C root show REV:path` — blobs at the named revision, no worktree read |
| `:10-12` | loads the two committed r57 matrices `census/round-57/records/c1-matrix-v5.tsv` and `-v6.tsv` as TSV |
| `:14-19` | derives `exit_zero` per matrix from positional column 5, and `carry_identical` from pairwise `exit`/`findings_all` equality over `zip(*tables)` |
| `:20-22` | interpolates those derived values into two literal `R58-CALIBRATION ...` note strings |
| `:23` | `mismatches = sum(note not in text for note in notes)` against `SCORECARD.md` at the same revision |
| `:24-25` | prints `MATCH`/`MISSING` per note plus `SUMMARY assertions=2 mismatches=N ... rev=REV`, returns `int(bool(mismatches))` |
| `:29-33` | argparse `--root`/`--rev` mandatory; usage errors exit 2 |

Observed return discrimination over committed blobs (receipt
`evidence/r58-source-returns.out`):

- `--rev 83d3813...` (r58 base): `MISSING` twice, `mismatches=2`, `EXIT=1`.
- `--rev da5af55b...` (r59 base): `MATCH` twice, `mismatches=0`, `EXIT=0`.

## Clause-by-clause against PROTOCOL §Gate standard

| clause (`PROTOCOL.md`) | verdict | basis |
|---|---|---|
| Definition (`:377-379`): committed, re-runnable, lane-owned verdict script; reads surfaces, compares against expected values persisted in its own repo, returns a verdict | **satisfied** | committed at `census/round-58/c1-counter.py`; survives rerun at both revisions above; expected values persist as the committed matrices plus the note templates inside the committed source; returns 0/1 |
| Probe (`:379-380`): "a tool that cannot fail is a probe" | **not satisfied** | it fails: `EXIT=1`, `mismatches=2` at `83d3813`; r58 wave mutation receipts also record failures |
| Verdict map (`:380-384`): 0 clean, 1 failed, other codes declared and mapped onto clean/failed/could-not-evaluate | **satisfied at the interface** | 0/1 direct (`:25`); 2 declared in the row as `CLI usage` and the lane gate map (`SKILL.md:198`) maps 2 to could-not-evaluate. Note: an unresolvable `--rev` is not 2 — it raises from `check_output` and exits 1 with a traceback (receipt `evidence/error-path-probes.out`), i.e. data error is classified `failed`, not `could-not-evaluate` |
| Self-test (`:385-389`): every gate exposes a self-invocation mode over isolated fixtures asserting both the exit code and a stable expected finding-id, expected values committed in the owning repo and independent of recomputation | **not satisfied** | the source has no self-invocation flag at all (argparse accepts only `--root`/`--rev`, `:29-33`). The base row's own self-test cell says `external discrimination fixture supplied with the round; counter has no self-invocation certification` (`SKILL.md:776`). The r58 discrimination fixture lived in wave receipts, not as a committed pinned expected file for this script |
| Two evidences (`:390-397`): verdict names the revision; committed input snapshot with committed expected verdict; digests pinned | **satisfied for revision naming** | `SUMMARY ... rev=REV` is printed (`:24`); all inputs are committed blobs at that revision. No mutable fleet artifact is graded, so the snapshot-digest clause does not add an input here. Committed receipts exist (`census/round-58/c1-before.txt`, `c1-control-binding.txt`, `c1-after.txt`, `c1-final.txt`) |
| Registry (`:398-404`): row fields name, `gate|probe`, entry command, verdict map, self-test command/spelling, pinned-value path, write scope, owner, at the lane's own `SKILL.md` | **fields present; kind field is the defect** | the base row (`SKILL.md:776` at `da5af55b`) carries all eight fields, but its kind cell reads `evidence`, a lane-local third kind defined at `SKILL.md:204` for measurement producers whose exit 1 means "unused by code" |
| Scope / closure (`:405-414`) | **satisfied / out of scope** | read-only over git blobs; no external action; red status is routed, not enforced here |

## Classification returned

`census/round-58/c1-counter.py` is a **gate-interface comparator**: it reads
surfaces, compares persisted expected values, and returns a fail-capable
verdict (0/1, 2 usage). It is therefore neither `probe` (it can fail) nor
`evidence` in the lane's own sense (its exit 1 is a runner-style failure
consumed as a red arm, not "unused by code"; it produces no record file).
Its registration as `evidence` at the base revision is the one
REGISTRY-KIND-MISMATCH that the frozen counter counts.

Limit that must travel with that verdict: the source does **not** meet the
PROTOCOL Self-test clause (no self-invocation, no committed stable
finding-id expectation for this script), so "gate" here is a classification
of interface and return semantics, not a claim of full conformance. The
frozen Implementation clause resolves this correctly by classifying the r58
source as *historical* gate and superseding it with a new gate that carries
the public `--selftest`; a kind-cell edit alone would pass the counter
without curing that debt. The counter's own note says as much: it counts
classification, not execution authentication.

## Comparison-semantics limits read from the source (lane-owned vocabulary)

- `zip(*tables)` (`:19`) truncates to the shorter matrix and joins by position,
  not by fixture identity; a changed identity or an appended row in one matrix
  is invisible.
- Note matching is substring presence (`:23`); a duplicated note passes, and
  the superseded r57 claims need not be absent.
- Positional column 5 (`list(row.values())[4]`, `:18`) depends on the committed
  TSV header order, which the matrix itself supplies; it is not a header-name
  lookup.
- No timeout and no stderr capture: a hung `git` hangs the comparator; a git
  failure surfaces as a traceback with exit 1.

These do not change the gate/evidence classification — PROTOCOL pins only the
outer interface — but they bound what a green run of that comparator ever
certified.
