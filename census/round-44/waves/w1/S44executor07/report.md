# S44executor07 — C1 partition 7/16

Axes: calibration (primary), operability, coverage. This is a registration artifact only; it does not claim admission or a newly established factual correction. Historical SCORECARD line references remain unchanged.

## Output

- `corrections.txt` contains emitted zero-based positions 6, 22, 38 and 54 of 66 unique emitted rows (modulo 16 = 6): R44-07, R44-23, R44-39, R44-55. Position 70 has no row.
- Each correction has exact `CORRECTION-R44` syntax, `file=SCORECARD.md`, `scope=base-SCORECARD-token-referents`, and `rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f`. No optional fields.

## Evidence

Command run:

```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-44/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev d314fd6e85d62565344fa6c4b102f52f62297884 --scratch /fast/scratch/hyaku/souji-r44/S44executor07 --emit
```

Observed output contained 66 unique records, sequentially R44-01 through R44-66. The selected exact rows:

```text
R44-07 line=68 class=mismatch:path-absent stale=count-objects-garbage-readings-r25.md derived=multi:.ufo/waves/round-26/assimilation/validate/corpus/knowledge/count-objects-garbage-readings-r25.md;census/round-26/waves/assimilation/validate/corpus/knowledge/count-objects-garbage-readings-r25.md;corpus/knowledge/count-objects-garbage-readings-r25.md
R44-23 line=424 class=mismatch:path-absent stale=c3-after-c3-counter-v3.txt derived=census/round-31/records/c3-after-c3-counter-v3.txt
R44-39 line=701 class=mismatch:path-absent stale=c3-after3.txt derived=census/round-38/records/c3-after3.txt
R44-55 line=763 class=mismatch:path-absent stale=c3-after.txt derived=multi:census/round-36/records/c3-after.txt;census/round-37/records/c3-after.txt;census/round-38/records/c3-after.txt;census/round-39/records/c3-after.txt;census/round-40/records/c3-after.txt;census/round-41/records/c3-after.txt;census/round-42/records/c3-after.txt
```

Independent committed-byte check:

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 55d7af6f5a22340f7a3de1c386e514ababfaa75f:SCORECARD.md

git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -r --name-only 55d7af6f5a22340f7a3de1c386e514ababfaa75f
```

Observed matching basename referents from `ls-tree`: R44-07 had exactly the three listed candidate paths; R44-23 only `census/round-31/records/c3-after-c3-counter-v3.txt`; R44-39 only `census/round-38/records/c3-after3.txt`; R44-55 the seven listed records (rounds 36–42). SCORECARD lines 68, 424, 701, and 763 were read from `git show` at the base and contain their corresponding stale tokens.

Q76 historical coverage probe:

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin grep -n -E 'CORRECTION-R4[23].*(count-objects-garbage-readings-r25|c3-after-c3-counter-v3|c3-after3\\.txt|c3-after\\.txt)' 55d7af6f5a22340f7a3de1c386e514ababfaa75f -- census/round-42 census/round-43 corpus/lessons
```

Observed: exit 1, no matches. Therefore this probe found no r42/r43 correction-registration coverage for these selected token strings. This is bounded search evidence, not evidence that there were no prior factual corrections elsewhere; mere registration does not establish a new correction.

## Limits

No whole C1 counter acceptance gate or unrelated tests were run. Counter `--emit` is dry-run. No SCORECARD or production file was changed. The base-byte derivations are independently corroborated by `show`/`ls-tree`; the indexed instrument-specific derivation itself comes from the stated frozen counter.
