# S44executor04 — C1 correction-register partition 4/16

Axis: calibration.

## Result

Wrote `corrections.txt` with the five emitted zero-based indexes 3, 19, 35, 51, and 67 (R44-04, R44-20, R44-36, R44-52, R44-68). Every line uses the required `scope=base-SCORECARD-token-referents`, pinned `rev=55d7af6f5a22340f7a3de1c386e514ababfaa75f`, and contains no optional fields. Historical SCORECARD line numbers are preserved; no SCORECARD edit was made.

## Evidence

Read `census/round-44/preregistration.txt`; its C1 block pins base `55d7af6f5a22340f7a3de1c386e514ababfaa75f`, counter/population checksums, and the emission target of 70 derivations without failures. Read `census/round-44/c1-counter.py` grammar and derivation rules, plus `c1-population.tsv`.

Exact bounded command run from the `souji-shokunin` lane directory (scratch explicitly located under this seat's scratch directory):

```sh
python3 -B census/round-44/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev d314fd6e85d62565344fa6c4b102f52f62297884 --scratch /fast/scratch/hyaku/souji-r44/S44executor04 --emit
```

Observed output included the following selected derivations:

```text
R44-04 line=23 class=mismatch:path-absent stale=c3-after.tsv derived=multi:census/round-24/records/c3-after.tsv;census/round-25/records/c3-after.tsv;census/round-26/records/c3-after.tsv;census/round-27/records/c3-after.tsv;census/round-28/records/c3-after.tsv
R44-20 line=314 class=mismatch:path-absent stale=excluded.tsv derived=multi:census/round-26/waves/excluded.tsv;census/round-42/waves/excluded.tsv
R44-36 line=673 class=mismatch:path-absent stale=consumers-after2.txt derived=census/round-38/records/consumers-after2.txt
R44-52 line=762 class=mismatch:path-absent stale=c2-before.txt derived=multi:census/round-37/records/c2-before.txt;census/round-38/records/c2-before.txt;census/round-39/records/c2-before.txt;census/round-43/controls/c2-before.txt
R44-68 line=821 class=mismatch:path-absent stale=controls/c1-control.txt derived=multi:census/round-41/controls/c1-control.txt;census/round-42/controls/c1-control.txt
```

The frozen counter derives using committed base-tree tracked paths; the emitted path/multi candidates therefore record the counter's committed `ls-tree` derivation, not current workspace paths. For these path-absent cases, the exact candidate paths shown were observed in emitted output. No independent full `git show`/`ls-tree` re-derivation was separately performed beyond the counter's own pinned-byte derivation, so independent verification of each path candidate remains a limitation.

## Earlier correction status (Q76)

No matching earlier round-42 or round-43 correction entry was found for any of these five `(line, token)` pairs in the inspected historical correction material. This is a report of the search, not a claim that registration changes the underlying historical fact. Round-44 registration alone is not a new factual correction or evidence of a new calibration gain.

## Limitations

The `--emit` invocation was used as the assigned derivation probe; the full registered-correction counter against a landed r44 lesson was not run because this seat owns only this partition and does not write the lesson. No whole-suite check was run. No tools were installed or updated. The counter's run may have left scratch material; it is removed below before handoff.
