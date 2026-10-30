# S44executor10 — C1 partition 10/16

Axes: calibration (assigned); operability and coverage unchanged.

## Result

Wrote `corrections.txt` with emitted unique records at zero-based indices 9, 25, 41, and 57 (R44-10/26/42/58), selected from the counter's ordered unique-key emission. Each line uses the required exact grammar, `scope=base-SCORECARD-token-referents`, base revision `55d7af6f5a22340f7a3de1c386e514ababfaa75f`, and no optional fields. No SCORECARD or production bytes were changed.

Earlier coverage (Q76): R44-10 **already covered** by r42: committed `corpus/lessons/round-42.md` line 71 has CORRECTION-DE for the same line 68 token. R44-26, R44-42, R44-58: **not found covered** by the r42 correction section or r43 C1 correction section; r43's C1 records address R39-D1/D2/D3, not these token referents. Registration is not asserted to be a new factual correction.

## Evidence / exact run

Ran:

`python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-44/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev d314fd6e85d62565344fa6c4b102f52f62297884 --scratch /fast/scratch/hyaku/souji-r44/S44executor10 --emit`

Exit 0. Relevant exact output:

```
R44-10 line=68 class=mismatch:digest stale=71b89eb3c7ce417979c5fce2c759dafe023af21d6310fde49197c766b8f28897 derived=sha256:bb506469be860f994f74f4c7d6eb1c949a4931b676cdb60f9f79de041d12f27f
R44-26 line=489 class=mismatch:path-absent stale=SwarmCritic26.md derived=multi:census/round-30/waves/w1/SwarmCritic26.md;census/round-31/waves/w2/SwarmCritic26.md;census/round-32/waves/a2w1/SwarmCritic26.md;census/round-33/waves/w1/SwarmCritic26.md;census/round-34/waves/w2/SwarmCritic26.md
R44-42 line=709 class=mismatch:path-absent stale=c1-vacuity5.txt derived=census/round-38/records/c1-vacuity5.txt
R44-58 line=792 class=mismatch:path-absent stale=fixtures-after.txt derived=census/round-40/records/fixtures-after.txt
```

The emitted register contains 66 unique keys; selection follows one-based emitted R44 ordinals minus one modulo 16 equals 9. The source counter documents that derivations read committed base bytes, using base instrument output, base SCORECARD, and base `ls-tree` paths.

Independent spot checks: `git show 55d7af6...:corpus/lessons/round-42.md` contains the exact R44-10 token at its prior CORRECTION-DE line. `git show 55d7af6...:census/round-38/records/c1-vacuity5.txt` succeeded, corroborating the exact referent path for R44-42. `git show 55d7af6...:census/round-40/records/fixtures-after.txt | sha256sum` returned `7cccc76ba1d4d97cf7e510157af41b7632ebc3ce8416dd328fa22f5820aa7b37`; this confirms the blob is present but is not a full independent basename-search derivation. For R44-26 the corresponding path under `census/round-32/waves/w1/` does not exist at base (git show exited 128); counter-derived candidate list uses `waves/a2w1/` and other listed directories. The exact candidate set is inherited from the counter's base `ls-tree` derivation, not independently enumerated by a separate implementation.

The supplied freeze receipt records `claims=3 findings=0 EXIT=0` for freeze `d314fd6e85d62565344fa6c4b102f52f62297884`. No install/update performed. Bounded assigned emission and base-byte probes only; no unrelated suite run.

## Limits and cleanup

The `--emit` run proves only the counter's emitted derived values and this seat's partition registration; it does not establish substantive truth of the underlying historical scorecard claims or the overall C1 target. No r44 lesson registration was made here. Scratch was created explicitly at `/fast/scratch/hyaku/souji-r44/S44executor10`; cleanup is performed before handoff.
