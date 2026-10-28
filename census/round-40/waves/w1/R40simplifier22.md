# R40simplifier22 — C1 item-set denominator attack

- Seat: simplifier, leaf; no subagent dispatch.
- Distinct item 22: **caller-supplied item-set substitution** (the expected C1 denominator and definition set are not revision-bound).
- Axis: calibration — evidence-source integrity and completeness of the measured item set.

## Evidence

Frozen contract: `census/round-40/preregistration.txt:5` requires evidence-bound anchored item lines, a strict-descendant register relation, and the forged token-only item to remain OPEN. The r39 control is the committed C1 counter.

Committed r39 behavior:

- `census/round-39/c1-counter.py:203-210` reads `--items` with ordinary `open(args.items)` and hashes whichever bytes the caller supplied; it does not extract that table from `--rev` or compare its hash to a frozen expected hash.
- `census/round-39/c1-counter.py:107-133` validates row shape, unique IDs, and nonempty input, but has no required row count or required-ID-set check. Lines `:251-259` define success using `open_count`, register floors, and mismatches; they do not assert an expected `items` count.
- The committed full r39 table has 16 rows (`census/round-39/c1-items.tsv:6-21`). Its committed after receipt reports `SUMMARY items=16 open=0 ... items_sha=d892b74f8358` (`census/round-39/records/c1-after.txt:20`).
- The source used for the run below is the committed r39 counter at `0242085909fb6a4ee041c5443d76316ac6d59d4b`: `git rev-parse <rev>:census/round-39/c1-counter.py` and `git hash-object` of the working-tree file both returned `37184ddad309283028d242c8419ac18c83fdb98f`. The analogous item-table blob IDs also matched (`5a6ee2639a0eaed85bafbe49acf937e0ddc569a2`).

I supplied a scratch `--items` file containing only the otherwise-valid `R39-C1-10` row, while leaving `--rev` and the committed six-cell register unchanged. The r39 counter returned:

```text
ITEM R39-C1-10 CLOSED
REGISTER cells=6 mismatches=0 commit_distinct=6
SUMMARY items=1 open=0 register_cells=6 register_mismatches=0 commit_distinct=6 items_sha=2cddf1519712
rc=0
```

The canonical table SHA-256 was `d892b74f83587a79a83b0c39aff89d1e93a0f8ac0d523f5d02b8a55c76769f34`; the one-row scratch table SHA-256 was `2cddf1519712ab662e974572423991170aa2396a7cadcea8fdbab5ad8191e517`. This is a concrete r39 control false-green for the *intended 16-row coverage denominator* when the caller can substitute the input table. It is not the token-only forgery: the one retained row is valid; the other 15 checks have been removed from the measurement input.

## Verdict and bounded r40 measurement

**Verdict: bounded measurement plan; r40 candidate behavior NOT MEASURED.** The experiment shows the r39 control accepts a caller-selected subset, so a green `open=0` result does not, by itself, prove the intended frozen item set was measured. It does not falsify an unobserved r40 implementation. The frozen r40 text should be measured with an explicit expected item-set identity, not only the supplied file's self-reported digest.

At the named r40 base and candidate revisions, once the r40 item ledger and counter are committed:

1. Record the expected item-ledger revision, full SHA-256 (or Git blob ID), row count, and IDs from the frozen ledger.
2. Run the counter with that exact ledger; verify the result names the expected count and identity as well as all-closed status.
3. Repeat with a scratch copy omitting one item while keeping all remaining rows valid. The candidate must refuse the noncanonical ledger or fail the expected count/identity check; `items=1 open=0`-style success is insufficient.
4. Keep the preregistered token-only forgery and strict-descendant/equal/backwards cases as separate arms. Do not count their results as a substitute for testing denominator binding.

This is a measurement-input integrity check; it does not prescribe a new evidence-pointer format or claim that the frozen C1 predicate requires arbitrary item-table mutation tests beyond establishing the intended ledger.

## Commands actually run

All paths are absolute. No git/jj mutation was made in the lane.

```text
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse --show-toplevel
→ /home/vgpnk/Projects/shokunin/souji-shokunin

git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD
→ be4cb61e84ebcbf05814d3dfe6ba00b6f730f10e

git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --short
→ ?? census/round-40/

printf 'committed-counter='; git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse 0242085909fb6a4ee041c5443d76316ac6d59d4b:census/round-39/c1-counter.py; printf 'worktree-counter='; git -C /home/vgpnk/Projects/shokunin/souji-shokunin hash-object /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/c1-counter.py; printf 'committed-items='; git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse 0242085909fb6a4ee041c5443d76316ac6d59d4b:census/round-39/c1-items.tsv; printf 'worktree-items='; git -C /home/vgpnk/Projects/shokunin/souji-shokunin hash-object /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/c1-items.tsv
→ committed-counter=37184ddad309283028d242c8419ac18c83fdb98f
  worktree-counter=37184ddad309283028d242c8419ac18c83fdb98f
  committed-items=5a6ee2639a0eaed85bafbe49acf937e0ddc569a2
  worktree-items=5a6ee2639a0eaed85bafbe49acf937e0ddc569a2

mkdir -p /fast/scratch/hyaku/souji-r40/R40simplifier22/tmp && TMPDIR=/fast/scratch/hyaku/souji-r40/R40simplifier22/tmp python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --items /fast/scratch/hyaku/souji-r40/R40simplifier22/items-one.tsv --register census/round-39/cells.tsv --scratch /fast/scratch/hyaku/souji-r40/R40simplifier22/tmp; printf 'rc=%s\n' "$?"
→ (output quoted in Evidence)

sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/c1-items.tsv /fast/scratch/hyaku/souji-r40/R40simplifier22/items-one.tsv
→ d892b74f83587a79a83b0c39aff89d1e93a0f8ac0d523f5d02b8a55c76769f34  canonical table
  2cddf1519712ab662e974572423991170aa2396a7cadcea8fdbab5ad8191e517  scratch one-row table
```

Scratch input used: `/fast/scratch/hyaku/souji-r40/R40simplifier22/items-one.tsv`; it contained only the canonical `R39-C1-10` row and has been removed. No tools were installed or updated.
