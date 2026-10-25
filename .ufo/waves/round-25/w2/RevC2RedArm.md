# RevC2RedArm — W2 re-run of the C2 red arms against both old blobs

Seat: L1Souji25.RevC2RedArm (leaf reviewer; no subagents, no edits, no lane writes beyond this report).
Assignment: re-run C2's 12-case fixture against `1efe406` and the actual regressed `778747e`; verify case ids
and exact red outputs; compare to prereg amendment 2 and the C2 receipts; judge the red-arm requirement.

## Status

STATUS: PASS. Both red arms reproduce the W1 receipts byte-for-byte (same fixture bytes, same tool blob bytes,
same per-case verdicts, same rc). The red-arm requirement of amendment 2 is satisfied by BOTH blobs:
- `1efe406` fails **only case 11 (subdir)** — cases 9, 10, 12 pass.
- `778747e` fails **cases 9 and 10 (bare-nonempty, bare-empty)** — cases 11 and 12 pass.
No mismatch vs amendment 2 or against either receipt set. The only discrepancy is the original prereg parenthetical
("the bare cases discriminate" vs `1efe406`), which amendment 2 already corrected; it is a wording artifact, not a
claim narrowing.

## Environment and method

- Lane root: `/home/vgpnk/Projects/shokunin/souji-shokunin`. Git 2.56.0 (fixture precondition >= 2.46 met).
- Fixture under test: the integrated working-tree `tests/fixtures/r24-size-census.py`, sha256
  `9c8a512f94d5682efee725dc7ed7519c127fde6a775a038ec3292374970bd528` (12 cases; identical to W1 draft
  `w1/ExecC2-2/r24-size-census.py`; `git diff` vs HEAD shows only the frozen 9–12 extension).
- Blob extraction (method from amendment 2 §1): `git show <blob>:tools/souji-size-census.py` into
  `/var/tmp/souji-r25-RevC2RedArm/` (removed at end). Recorded hashes match the receipts:
  - `1efe406e7f39b8fe736be2a566053703a571ffc0` -> sha256 `7ad5cc763b346c8d13b20d53e56a8e2986a395425ac94201d79bd896912f4578` (= c2-red.tsv `arg_tool_sha256`).
  - `778747eb671f8e85ef5387bc3d7023337b30467c` -> sha256 `09bb8e0d9906b0dfef44775a9e5cd7c8f8a27d9bcdf559e2d371a3ef7ff1ed6d` (= c2-mid.tsv / c2-regressed.tsv `tool_sha256`).
- Commands: `python3 -B tests/fixtures/r24-size-census.py --tool <blob-copy>` (one per arm).

## Results (my re-run)

| arm | tool blob | rc | failing cases | last line |
|---|---|---|---|---|
| red | `1efe406` | 1 | CASE 11 subdir only | `cases=12 pass=11 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED` |
| regressed | `778747e` | 1 | CASE 9 bare-nonempty, CASE 10 bare-empty | `cases=12 pass=10 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED` |

Exact red outputs (my run):
- `1efe406`: `CASE 11 subdir FAIL exit=0 counts=0,0,0,0 manifest_changed=0 stderr_must_name_repo=False`
  (old tool silently censuses the enclosing repo: exit 0 + counts line, no refusal marker). All 11 others PASS.
- `778747e`: `CASE 9 bare-nonempty FAIL exit=2 counts=none manifest_changed=0 invoked_from_bare=False` and
  `CASE 10 bare-empty FAIL exit=2 counts=none manifest_changed=0 stderr_git_failure=False stderr_no_default_references=False stdout_counts_line=False`
  (over-refusal: exit 2 "not a repository" on bare repos; no counts line, no git-failure diagnostic). Cases 11 and 12 PASS.
- All 12 case ids present in frozen order (1 clean … 8 control, 9 bare-nonempty, 10 bare-empty, 11 subdir,
  12 partialClone-only); both control and detector flags stay correct on both arms.

## Comparison to C2 receipts

- ExecC2-2 receipts (`w1/ExecC2-2/receipts/c2-red.tsv`, `c2-regressed.tsv`; fixture sha256 `9c8a512f…`):
  my stdout is **byte-identical** to both (per-case lines and last line), rc identical.
- ExecC2 receipts (`w1/ExecC2-receipts/c2-red.tsv`, `c2-mid.tsv`; fixture sha256 `5bd7e74f…`): same per-case
  verdicts and same exit codes; only cosmetic print-label differences between the two drafts
  (`counts_line=True`/`must_name_repo` vs `counts=…`/`stderr_must_name_repo`), no semantic difference.
- Green case (tip tool) and stub receipts are out of this seat's scope (other W2 seats cover them).

## Comparison to prereg amendment 2

- Amendment 2 §1: "against 1efe406 only case 11 fails" — **confirmed exactly** (11/12, only 11 FAIL).
- "against 778747e cases 9 and 10 fail" — **confirmed exactly** (10/12, only 9 and 10 FAIL).
- "each arm must fail >=1 of cases 9–12": 1efe406 fails 11; 778747e fails 9 and 10 — **both satisfied**.
- "the 778747e arm must fail case 9 or 10 (the bare regression witness)": satisfied (both 9 and 10).
- Cross-check with the routed regression itself: `corpus/lessons/round-24.md:59` records that the after-state tool
  "refuses every bare repository with exit 2 'not a repository' … a regression against 1efe406", matching 778747e's
  red pattern (exit 2 over-refusal on bare repos).

## Findings

1. No mismatch: both red arms reproduce the recorded receipts and satisfy amendment 2's red-arm requirement.
2. The original prereg C2 parenthetical "(the bare cases discriminate)" was false for the named `1efe406` blob —
   it is discriminated only by case 11, not by the bare cases; the bare cases discriminate `778747e`. Amendment 2
   already corrected this; the frozen "fail >=1 of 9–12" predicate is met either way. Report-only, no edits.
3. Red-arm detail worth keeping: `1efe406` fails *under*-refusal (silently censuses a subdir, exit 0), while
   `778747e` fails *over*-refusal (refuses bare repos, exit 2). Case 12 (partialClone-only) passes on both old
   blobs, so it is coverage-only, not a discriminator between them — consistent with ExecC2's note.

## Attack log

- A1 (verdict): re-ran both arms; red split confirmed. No case dropped/re-specified.
- A2 (bytes): verified extracted blobs hash to the receipted `tool_sha256` values before running; verified the
  integrated fixture hash equals the 9c8a512f receipt fixture before running.
- A3 (outputs): compared my full stdout to both receipt sets; byte-identical vs the same-fixture receipts.

Scratch `/var/tmp/souji-r25-RevC2RedArm/` removed. No tool installs; no lane/git/jj mutations.
