# S44executor05 — C1 correction partition 5/16

Axes: calibration (assigned); operability and coverage were not tested or claimed.

## Result

Wrote `corrections.txt` with the four emitted records whose zero-based distinct-record indices satisfy `index % 16 == 4` (indices 4, 20, 36, 52; IDs R44-05, R44-21, R44-37, R44-53). Each record has the required class, stale token and counter-derived token; `rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f`; and `scope=base-SCORECARD-token-referents`. No optional fields are included. Historical SCORECARD lines were not edited.

Command run:

```sh
python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-44/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev d314fd6e85d62565344fa6c4b102f52f62297884 --scratch /fast/scratch/hyaku/souji-r44/S44executor05 --emit
```

Observed emitter rows, verbatim:

```text
R44-05 line=31 class=mismatch:path-absent stale=c1-after.tsv derived=multi:census/round-24/records/c1-after.tsv;census/round-25/records/c1-after.tsv;census/round-26/records/c1-after.tsv;census/round-27/records/c1-after.tsv;census/round-28/records/c1-after.tsv
R44-21 line=314 class=mismatch:path-absent stale=symlinks.tsv derived=census/round-26/waves/symlinks.tsv
R44-37 line=699 class=mismatch:path-absent stale=c1-vacuity4.txt derived=census/round-38/records/c1-vacuity4.txt
R44-53 line=762 class=mismatch:path-absent stale=c2-after.txt derived=multi:census/round-36/records/c2-after.txt;census/round-37/records/c2-after.txt;census/round-38/records/c2-after.txt;census/round-39/records/c2-after.txt;census/round-40/records/c2-after.txt;census/round-41/records/c2-after.txt;census/round-42/records/c2-after.txt
```

The counter code and population file were read. Counter `--emit` itself derives these referents using committed base-revision bytes (`git ls-tree` for tracked paths and `git show` for SCORECARD/token data); this is independent of the working tree. Additional base checks run:

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 55d7af6f5a22340f7a3de1c386e514ababfaa75f:SCORECARD.md | cut -n -b 1-220 | awk 'NR==31 || NR==314 || NR==699 || NR==762 {print NR ":" $0}'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -r --name-only 55d7af6f5a22340f7a3de1c386e514ababfaa75f | awk '/(^|\/)c1-after\.tsv$|(^|\/)symlinks\.tsv$|(^|\/)c1-vacuity4\.txt$|(^|\/)c2-after\.txt$/'
```

Observed relevant tracked paths included `census/round-24/records/c1-after.tsv` through `census/round-28/records/c1-after.tsv`, `census/round-26/waves/symlinks.tsv`, `census/round-38/records/c1-vacuity4.txt`, and `census/round-36/records/c2-after.txt` through `census/round-42/records/c2-after.txt`; the full emitter provides the exact candidate sets above. The selected historical SCORECARD lines were present at the supplied numbers; line numbering remains historical.

## Q76 — prior correction coverage

No selected item is already covered by the earlier round-42 or round-43 correction content: round 42's correction prose/register covers distinct records (including `CORRECTION-DE` for line 175 and hash/revision items, plus separate `CORRECTION-SC` statements); round 43 corrects dated census self-assessments, not these SCORECARD referents. Thus each of the four R44 registrations adds a registration for this token-referent population, not a claim that a new factual falsehood was discovered or newly corrected. The round-43 report also notes its corrections address dated records, not the current registry.

## Evidence and limits

`--emit` returned the complete 66-row population and exit success; only the four assigned modulo-partition rows were written. No full counter acceptance run was performed because this artifact is not yet registered in the frozen lesson. No tools were installed. No source, SCORECARD, counter, shared bookkeeping, or sibling output was changed. Scratch was removed before handoff.