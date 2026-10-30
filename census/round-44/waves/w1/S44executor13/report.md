# S44executor13 — C1 correction-register partition 13/16

Axes: calibration. Output consists of `corrections.txt` (four emitted records); no production or frozen counter files were changed.

## Evidence and exact commands

Repository identity and freeze resolution:

```text
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse --show-toplevel
/home/vgpnk/Projects/shokunin/souji-shokunin
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse d314fd6e85d62565344fa6c4b102f52f62297884
d314fd6e85d62565344fa6c4b102f52f62297884
```

Ran the frozen counter with emit against the required freeze, directing its scratch to the seat's designated scratch directory:

```text
python /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-44/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev d314fd6e85d62565344fa6c4b102f52f62297884 --scratch /fast/scratch/hyaku/souji-r44/S44executor13 --emit
```

Exit was zero; output had 66 records. Applied zero-based indices `i % 16 == 12`; selected rows were:

```text
index=12 R44-13 line=103 class=mismatch:path-absent stale=git-repo-structure-readonly.md derived=multi:.ufo/waves/round-26/assimilation/validate/corpus/knowledge/git-repo-structure-readonly.md;census/round-26/waves/assimilation/validate/corpus/knowledge/git-repo-structure-readonly.md;corpus/knowledge/git-repo-structure-readonly.md
index=28 R44-29 line=525 class=mismatch:path-absent stale=.ufo/waves/round-33/make-spec-w2.py derived=UNHELD
index=44 R44-45 line=721 class=mismatch:path-absent stale=c1-vacuity6.txt derived=census/round-38/records/c1-vacuity6.txt
index=60 R44-61 line=811 class=mismatch:path-absent stale=c2-after-h.txt derived=census/round-40/records/c2-after-h.txt
```

Independently checked the immutable base SCORECARD lines and committed paths with `git show` / `git ls-tree` (read-only):

```text
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 55d7af6f5a22340f7a3de1c386e514ababfaa75f:SCORECARD.md
git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -r --name-only 55d7af6f5a22340f7a3de1c386e514ababfaa75f
```

Observed line/token presence at 103, 525, 721, 811. The line-103 basename has exactly the three emitted suffix matches listed above. Exact stale token `.ufo/waves/round-33/make-spec-w2.py` is absent at base (UNHELD); the counter's basename-only fallback also yielded no candidate. `c1-vacuity6.txt` and `c2-after-h.txt` each have the one emitted committed basename path. Thus each record's derived result was confirmed against the frozen base's bytes/tree, not the current worktree.

## Earlier correction coverage (Q76)

Inspected base-revision `corpus/lessons/round-42.md` and `round-43.md` for prior correction records and searched their available texts for the four line/token pairs. No prior `CORRECTION-R42`, `CORRECTION-R43`, or `CORRECTION-R44` records were found in those lesson files; the searched line/token pairs also had no hits. Accordingly none of these four items is evidenced as already covered by an earlier round-42/43 correction. The base line-525 text itself mentions Q76 and the earlier correction-row idea, but that is not a correction record for this token. Registration records the measured token referent only; it is not an independent new factual correction.

## Deliverable and limits

`corrections.txt` uses the exact R44 grammar, sequential emitted IDs, `file=SCORECARD.md`, required base revision and `scope=base-SCORECARD-token-referents`; it contains no optional disposition/capture/register fields. Historical line numbers are retained; SCORECARD was not rewritten. No tools were installed or updated. No whole-suite check was run; parent owns integration verification. Counter derivations establish token referents, not the semantic truth of the SCORECARD statements.
