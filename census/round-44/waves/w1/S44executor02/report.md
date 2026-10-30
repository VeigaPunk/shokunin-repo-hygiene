# S44executor02 — C1 correction-register partition 2/16

## Result

Produced `corrections.txt` with the five emitted records whose one-based emitted IDs have zero-based index congruent to 1 modulo 16: R44-02, R44-18, R44-34, R44-50, R44-66. Each line uses the required `CORRECTION-R44` grammar, base revision `55d7af6f5a22340f7a3de1c386e514ababfaa75f`, and `scope=base-SCORECARD-token-referents`; no optional disposition/capture/register fields were included. No SCORECARD/history content was modified.

## Exact bounded probe

Command:

```sh
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-44/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev d314fd6e85d62565344fa6c4b102f52f62297884 --scratch /fast/scratch/hyaku/souji-r44/S44executor02 --emit
```

Observed exit 0; emitter produced 66 unique records R44-01 through R44-66. Selected records (exact fields):

```text
R44-02 line=21 class=mismatch:path-absent stale=c1-after.tsv derived=multi:census/round-24/records/c1-after.tsv;census/round-25/records/c1-after.tsv;census/round-26/records/c1-after.tsv;census/round-27/records/c1-after.tsv;census/round-28/records/c1-after.tsv
R44-18 line=221 class=mismatch:path-absent stale=git-auto-maintenance-prunes-worktrees.md derived=multi:.ufo/waves/round-26/assimilation/validate/corpus/knowledge/git-auto-maintenance-prunes-worktrees.md;census/round-26/assimilation/validate/corpus/knowledge/git-auto-maintenance-prunes-worktrees.md;corpus/knowledge/git-auto-maintenance-prunes-worktrees.md
R44-34 line=668 class=mismatch:path-absent stale=c3-before.txt derived=multi:census/round-37/records/c3-before.txt;census/round-38/records/c3-before.txt;census/round-39/records/c3-before.txt
R44-50 line=733 class=mismatch:path-absent stale=c3-arms-filed.txt derived=census/round-38/records/c3-arms-filed.txt
R44-66 line=832 class=mismatch:path-absent stale=tip-remeasure.txt derived=census/round-41/records/tip-remeasure.txt
```

## Independent base-bytes check and prior-correction status (Q76)

The counter's `derive()` rule was checked against the frozen base commit's tracked-name semantics: for basename-only path tokens, candidates are all tracked paths with the same basename; `multi:` retains all candidates in sorted path order, and one candidate is emitted directly. This independently matches the named paths in all five derived fields; the base commit `SCORECARD.md` lines corresponding to 21, 221, 668, 733, and 832 carry the listed tokens. The path-resolution behavior and candidate names were also visible in the emitted output, which the counter computes from `git show`/`git ls-tree` at the BASE_REV (not the tip).

Earlier rounds 42 and 43 do not already correct any selected SCORECARD token/referent pair. Round 42's `CORRECTION-DE` items include SCORECARD lines 14, 68, 92 and 175, but not these five lines/tokens; round 43's `CORRECTION-R39` items concern census receipt counts/header revision, not these SCORECARD entries. Thus none of this partition is already covered by an earlier factual correction. This is registration of base-token referents, not a new factual correction about the historical claims.

## Evidence and limitations

- Read the R44 preregistration, C1 counter and population. Preregistration declares the frozen counter/population digests and the 70/66 population-to-unique-key distinction.
- Counter emit ran against the specified freeze; source implementation reads population and rederives from base commit blobs/tree. It deliberately returns after emitting and does not prove full lesson registration or overall R44 C1 target.
- Prior-coverage inspection used the carried round-42 lesson snapshot under `census/round-43/waves/w1/R43reviewer05/corpus__lessons__round-42.md` and `corpus/lessons/round-43.md`. Historical descriptions are not rewritten.
- No tools installed or updated. Scratch used: `/fast/scratch/hyaku/souji-r44/S44executor02` (removed before handoff).
