# S67RevengerProbe — host git probes around GIT_COMMON_DIR (round 67, seat w1)

Host: `git version 2.56.0` (recorded by the probe driver as the first line of `probe-log.txt`). Base writer
`tools/souji-receipt-write.py` extracted read-only from base `3639087917eaeb28719d7603110a6ec22782100e` via
`git show`; sha256 `a8c47d362a901c222f9582b8b96609fba39cb5e0e662d4057e724db96c1097fc` (matches the frozen base).

Method: every fixture was a throwaway repo under `/fast/scratch/hyaku/souji-r67/S67RevengerProbe/` created with
`mktemp -d -p` + `git init`, with `rev-parse --show-toplevel` verified before the first commit; identity was set
repo-locally (not `-c`, which would itself set `GIT_CONFIG_PARAMETERS` in children). The only lane access was
read-only `git show`. The scratch was removed by the driver's EXIT trap. Raw output:
`probe-log.txt` (P1–P6) and `probe-log-relative.txt` (P2i). Row-per-probe table: `probes.tsv`.
No tools were installed or upgraded. No pacman, sudo or sysctl was used.

Fixture notes (what I got wrong on first runs, so the final numbers are not misread):
- A first `submodule add` failed `transport 'file' not allowed` (git sets `GIT_PROTOCOL_FROM_USER=0` for submodule clones);
  the final run passes `-c protocol.file.allow=always` on that one command, which is why the submodule child env shows
  `GIT_CONFIG_PARAMETERS` in the filter captures. The foreach and hook captures were taken without `-c`.
- The first subdirectory-root writer probe failed on `instr.sh absent` before reaching any ceiling check; the final
  run places the instrument at the repo top and runs the writer from the subdirectory (P5c).

## P1 — does git export GIT_COMMON_DIR to child processes?  Answer: no, in every context measured.

| context | GIT_COMMON_DIR in child env | what git DID export (decisive) |
|---|---|---|
| pre-commit hook, main worktree (P1a) | absent | `GIT_INDEX_FILE=.git/index` (relative) |
| GIT_EDITOR child, `commit --amend` (P1b) | absent | `GIT_EDITOR=sh -c ...`, `GIT_INDEX_FILE=.git/index` |
| clean filter, main worktree (P1c) | absent | `GIT_EXEC_PATH`, `GIT_PAGER`, `GIT_SEQUENCE_EDITOR`, … (no GIT_DIR) |
| smudge filter, linked worktree (P1c) | absent | `GIT_DIR=.../.git/worktrees/wt`, `GIT_WORK_TREE=.` |
| `submodule foreach` child shell (P1d) | absent | `GIT_DIR=.git` (relative), `GIT_PROTOCOL_FROM_USER=0` |
| hook in submodule commit (P1d) | absent | `GIT_DIR=.../.git/modules/sub`, `GIT_INDEX_FILE` absolute |
| hook in linked worktree commit (P1e) | absent | `GIT_DIR=.../.git/worktrees/wt`, `GIT_INDEX_FILE` absolute |

So the only producers of `GIT_COMMON_DIR` in the child env are callers. Git does not export it to hooks, editors,
filters or submodule shells on this host. The candidate's scrub of the variable on every git call is therefore a
defence against a caller-injected value, not a fix for a git-exported route. Git does export `GIT_DIR` and
`GIT_INDEX_FILE` (and `GIT_WORK_TREE` to filters in a linked worktree); the base writer already scrubs `GIT_DIR` and
`GIT_WORK_TREE` on every call, and `GIT_INDEX_FILE` is refused on presence.

Caller-injected values reach children verbatim, with no rewrite of shape: an absolute `GIT_COMMON_DIR` arrives as the
same absolute string and a relative `.git` arrives as `.git` (P1f-abs, P1f-rel). Git does not canonicalize the value
for its children.

## P2 — linked-worktree shape of the writer (W1, W2, W3 in the worktree shape)

- P2a (no env), P2b (equal absolute value): base rc 0 both. An honest equal absolute value is accepted on base, so
  W3 is an honest row in the worktree shape too.
- P2c (a clone of the same repo at a different `.git` path, same objects): base rc 0. The base accepts a different repo's
  common dir whenever the rev exists there. The candidate's value check must refuse this (value mismatch).
- P2d (an unrelated repo that lacks the rev): base rc 2, `rev is not a commit object`.
- P2e (relative `.git` written from the main repo as cwd, root = linked worktree): base rc 2. Git resolved `.git`
  against the linked worktree (`-C` root), found the gitfile `wt/.git`, and failed. See the relative-path analysis below.
- P2f (control, tracked 755→644, no env): base rc 2 dirty.
- P2g (the same mode flip, with GIT_COMMON_DIR pointed at a clone whose config sets `core.fileMode=false`): base rc 0.
  The W1 forgery reproduces in the worktree shape: the writer accepts a receipt over a hidden divergence.

Trade for the worktree shape: none. The honest equal value (P2b) is accepted on base, and the candidate's W3 row keeps it.
The worktree shape gives no honest-run refusal beyond what the main-worktree shape already gives.

## P2h / P2i — relative GIT_COMMON_DIR: which directory does the value name?

This is the finding that matters most for the candidate's value check. The frozen L2 wording says a relative value "is
canonicalized against the writer process's cwd, the rule git applies". The probes show that the second clause is false
under the writer's own invocation. Git applies a relative `GIT_COMMON_DIR` against the `-C` root, not against the
writer's cwd, because every writer git call is `git -C <root>`.

- P2h-h2: from cwd `p7/cwd`, `GIT_COMMON_DIR=../real/.git`, root `p7/real/wt`. The writer-cwd reading names
  `p7/real/.git` (the real common dir). Git, run `-C wt` with the same env, reads `p7/real/real/.git` (a decoy clone
  whose config sets `core.fileMode=false`). Base rc 0: the mode flip is hidden and the receipt is accepted.
  A value check that canonicalizes against the writer cwd would see "equal" and accept this forgery. That is a
  forgery route the W1 row does not cover, and the candidate's value-check rule must not be the writer-cwd rule.
- P2h-h3 (control): the absolute real common dir with the same flip is refused dirty (base rc 2). The decoy path is
  what hides the flip; the value's name is what changes the outcome.
- P2i-R1 (honest relative value): cwd elsewhere, root = repo, `GIT_COMMON_DIR=.git`. Base rc 0, and git reads the
  repo's own common dir (`git -C root --path-format=absolute --git-common-dir` under the env: the repo's `.git`).
  A writer-cwd check would compare `elsewhere/.git` against the real dir (equal=False) and refuse an honest run.
  The root-relative check (`realpath(join(root, value))`) gives equal=True and accepts it.

Consequences for the candidate (recorded here; the candidate bytes are the executor's and were not run by this seat):
1. Resolve a relative value against the `-C` root, or refuse every non-absolute value with RECEIPT-ENV-COMMONDIR-MISMATCH.
   The writer-cwd rule is wrong in both directions: it admits the decoy (P2h-h2) and refuses an honest run (P2i-R1).
2. Compare canonical paths on both sides. `git rev-parse --git-common-dir` returns the relative string `.git` in the
   main worktree (P1 main, P2 main) and an absolute path in a linked worktree (P2 wt). A raw string compare against an
   absolute caller value would refuse honest main-worktree runs. Use `--path-format=absolute` (git ≥ 2.31) with the
   caller env scrubbed, then `realpath`.
3. Limit text for L2 should read: a relative value is resolved by git against the `-C` root. The current frozen wording
   ("the rule git applies") does not say this, and the frozen prereg cannot be edited. Route this to the operator as a
   named-limit wording defect (round-66 M2 class), not as a probe result that changes the claim.

## P3 — empty GIT_COMMON_DIR (grounds the candidate's empty-value refusal)

Git does not default-resolve an empty value. It treats the variable as set-to-empty and fails:
- main worktree, `git -C REPO status`: rc 128, `fatal: not a git repository (or any parent up to mount point /)`
  (unset baseline rc 0);
- linked worktree: rc 128, `fatal: gitfile does not point to a valid repository: .../p2/wt/.git`;
- nonexistent value: rc 128, the same class as empty.

The base writer already refuses an empty value (rc 2), but with the misleading text `rev is not a commit object`.
The candidate's RECEIPT-ENV-COMMONDIR-MISMATCH is the honest refusal for this case; no honest run is affected, because
git itself fails rc 128 on an empty value. The L2/limit text can cite this as git's own behaviour: an empty
GIT_COMMON_DIR is not a default, git fails on it.

## P4 — GIT_NAMESPACE (limit L3 grounding)

Every read the writer makes returns identical rc and output with and without `GIT_NAMESPACE=ns`: `status --porcelain`,
`ls-files -s`, `cat-file -t`, `rev-parse HEAD`, `show-ref`, `ls-tree -r <sha>`, `cat-file blob <sha>:a`,
`ls-files -v -z :(top)`, `rev-parse --show-toplevel`. The base writer gives rc 0 clean and rc 2 dirty in both cases.

The positive control (P4b) shows why: a ref created at `refs/namespaces/ns/refs/heads/nsonly` is not visible to
`GIT_NAMESPACE=ns git rev-parse --verify refs/heads/nsonly` (rc 1), and `for-each-ref` lists it under its raw name. On
this host the namespace is not applied to local reads. So `GIT_NAMESPACE` has no observable effect on the writer's
reads here. That supports the L3 position (neither refused nor pinned) for the reads tested; it does not prove
inertness for every git command.

## P5 — GIT_CEILING_DIRECTORIES (limit L3 grounding)

- A ceiling at the repository's parent does not change `-C REPO` resolution (rc 0, same toplevel).
- A ceiling equal to the repository root makes discovery from a subdirectory fail: `git -C REPO/sub2 rev-parse
  --show-toplevel` rc 128, `not a git repository`. A ceiling at `sub2` or the parent still resolves.
- With `--root` at the repo top and the writer run from `sub2`, every ceiling variant gives rc 0 (P5c). The writer's
  own `-C root` discovery is unaffected by the ceiling when the root is the top.
- With `--root` at the subdirectory, the base writer refuses without any env (`instr.sh absent`, rc 2). That is a
  base behaviour unrelated to this round. Under a root ceiling it refuses again (`rev is not a commit object`, rc 2).
  The subdirectory root is therefore not a valid honest shape on base in this probe; it is reported, not analysed further.

Honest-run answer for L3: a ceiling can change behaviour only for a subdirectory root, and that shape already refuses on
base. Top-level roots are unaffected in every ceiling variant measured.

## P6 — the r66 `git -c` refusal (limit L0 360, unchanged)

`git -c core.quotepath=false` sets `GIT_CONFIG_PARAMETERS` in the child environment. Under that wrapper the base writer
refuses rc 2 with `RECEIPT-ENV-CONFIG-SET: GIT_CONFIG_PARAMETERS set in the writer's environment`. The same wrapped
`git status` is rc 0, and the writer run directly is rc 0. This confirms the r66 predicate on the base bytes. It is
the honest-run trade named in L6 (L0 360), and no probe here changes it. It remains an operator ruling.

## The honest-run answer (the C1 no-trade question, P1–P3)

Does the candidate's value check (refuse mismatch or empty before any git call; accept equal; scrub on every call)
cost any honest run, as far as these probes can tell?

- Caller env unset: no effect (P2a, P3 baseline).
- Equal absolute value, main or linked worktree: accepted on base (P2b); the candidate keeps it (W3). No trade, provided
  the comparison is canonical on both sides (finding 2 above). A raw string compare would be a trade in the main worktree.
- Equal relative value interpreted against the `-C` root (P2i-R1): accepted on base. A writer-cwd check refuses it, a
  trade. The root-relative check accepts it. So the candidate must use the root-relative rule, or refuse all relative
  values and name the trade.
- Empty value: git itself fails rc 128; no honest run is lost (P3).
- `git -c` wrapper: the r66 trade stands (P6, L0 360).

Forgeries the same probes expose (not closed by the frozen W1–W3 rows):
- a relative value that a writer-cwd check reads as equal while git reads a decoy (P2h-h2, rc 0 on base). The candidate
  must not accept it under the writer-cwd rule.
- a different repo whose objects match (P2c, rc 0 on base) is a value mismatch the candidate must refuse; that is covered
  by the W1/W2 mismatch class once the candidate compares the path.

## Confidence and limits

- Measured on git 2.56.0 only. Other git versions may print the `rev-parse` path forms or the empty-value errors
  differently; the `--path-format=absolute` form needs git ≥ 2.31.
- The P1 table covers the contexts asked for (hook, GIT_EDITOR amend, clean/smudge, submodule, linked worktree). It
  does not cover `git gc`, `git fsck`, `git replace`, or the remote helper paths, which git may treat differently.
- I did not run the candidate writer (not landed; the executor seat owns it). The P2h-h2 and P2i-R1 predictions for the
  candidate are measured for the base writer's git calls and for the rule the candidate would need; the candidate's own
  results are for the L1 to measure with the frozen counter.
- The report path in the trailer (`.ufo/waves/round-67/w1/S67RevengerProbe.md`) sits outside the seat's delivery directory
  and the hard bounds limit delivery to `.../w1/S67RevengerProbe/`. This report is therefore delivered at
  `.ufo/waves/round-67/w1/S67RevengerProbe/report.md`; the L1 should decide whether to index it from the trailer.
