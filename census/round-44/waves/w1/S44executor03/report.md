# S44executor03 — C1 partition 3/16

## Axes
- **Calibration:** emitted and independently checked four assigned token-to-base-referent records; no SCORECARD rewrite or new factual claim.
- **Operability:** records are exact frozen-counter grammar, scoped to base SCORECARD token referents.
- **Coverage:** modulo partition covers zero-based emitted indices 2, 18, 34, 50 (R44-03, -19, -35, -51); population output contains 66 unique keys, so no further index in this partition.

## Evidence and commands
Working tree root used: `/home/vgpnk/Projects/shokunin/souji-shokunin`. Scratch was `/fast/scratch/hyaku/souji-r44/S44executor03`.

Command:
`python3 /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-44/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev d314fd6e85d62565344fa6c4b102f52f62297884 --scratch /fast/scratch/hyaku/souji-r44/S44executor03 --emit`

Observed emitted inventory: 66 rows, R44-01 through R44-66; assigned rows are R44-03 (line 22 stale `c2-after.tsv`), R44-19 (line 221 stale `git-grace-periods-and-expire-to.md`), R44-35 (line 668 stale `c3-after2.txt`), R44-51 (line 761 stale `c1-after.txt`). Counter derivations were respectively `multi:census/round-24/records/c2-after.tsv;census/round-25/records/c2-after.tsv;census/round-26/records/c2-after.tsv;census/round-27/records/c2-after.tsv;census/round-28/records/c2-after.tsv;census/round-42/waves/w1/R42critic01/k4/c2-after.tsv`; `multi:.ufo/waves/round-26/assimilation/validate/corpus/knowledge/git-grace-periods-and-expire-to.md;census/round-26/waves/assimilation/validate/corpus/knowledge/git-grace-periods-and-expire-to.md;corpus/knowledge/git-grace-periods-and-expire-to.md`; `census/round-38/records/c3-after2.txt`; `multi:census/round-36/records/c1-after.txt;census/round-37/records/c1-after.txt;census/round-38/records/c1-after.txt;census/round-39/records/c1-after.txt;census/round-41/records/c1-after.txt;census/round-42/records/c1-after.txt;census/round-43/records/c1-after.txt`.

Independent source checks:
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 55d7af6f5a22340f7a3de1c386e514ababfaa75f:SCORECARD.md | awk 'NR==22 || NR==221 || NR==668 || NR==761 {print NR ":" $0}'` showed historical lines 22, 221, 668, 761, each carrying the corresponding stale token and report evidence reference. Those line numbers are retained as historical anchors; SCORECARD was not edited.
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -r --name-only 55d7af6f5a22340f7a3de1c386e514ababfaa75f | awk '$0 ~ /(^|\/)c2-after\.tsv$/ || $0 ~ /(^|\/)git-grace-periods-and-expire-to\.md$/ || $0 ~ /(^|\/)c3-after2\.txt$/ || $0 ~ /(^|\/)c1-after\.txt$/'` showed all listed paths. c2-after candidates were census/round-24 through round-28 records plus census/round-42/waves/w1/R42critic01/k4; git-grace candidates were the three emitted matches; c3-after2 was census/round-38/records/c3-after2.txt; c1-after candidates were census rounds 36,37,38,39,41,42,43. This independently confirms the emitted base-tree candidate sets.

## Q76 prior correction coverage
A source search for `CORRECTION-(R42|R43)`/line anchors in the prior lesson corpus found no matching correction lines for these selected items. Round-43 verifier-spotcheck.md:23-34 documents its C1 correction target as three historical self-assessment values and the round-39 register; its notes at lines 78 and 81 explicitly distinguish token-binding and fixture limitations. Round-44 lesson’s existing correction lines are not evidence of a prior R42/R43 correction and are not counted here. Therefore Q76 classification for R44-03, R44-19, R44-35 and R44-51: **no prior R42/R43 correction located**. The registration itself is bookkeeping for token referents, not a new factual correction or measured calibration gain.

## Output and limits
- Register: `S44executor03/corrections.txt` (four exact CORRECTION-R44 rows; no optional disposition/capture/register fields).
- No tools installed. No tests/build/formatters run; only the assigned counter emit and base-byte probes were run.
- This evidence establishes token referents and presence/ambiguity in the base tree, not underlying historical runtime truth or factual correction. No source tree, counter, SCORECARD, shared bookkeeping, git index, or jj state modified.
