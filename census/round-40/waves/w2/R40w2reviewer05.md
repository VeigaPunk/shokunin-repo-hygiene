# R40 wave 2 — C2 L4 trigger/runtime falsification

## Attack and verdict: SAFE (for the assigned L4 claim)

Attacked the C2 L4 claim that each frozen (class, trigger) mapping is re-derived from actual behavior of the audited `souji-worktree-drift.py` bytes, and cannot be counted as passing when its trigger is absent from the joined docstring entry. Landed instrument: `128e412b0ced3c243dc27c3dd3332054a611bc2e`.

Frozen pairs are `census/round-40/c2-counter.py:72-78`: `(RECORD-MALFORMED, ENOENT)`, `(RECORD-MISSING, EACCES)`, `(RECORD-OUTSIDE-ROOT, --root)`. The runtime derivation is at `census/round-40/c2-counter.py:170-192`: missing path probe at 177; permission-denied probe at 178-180; outside-root row probe at 181-184; pair-to-probe association at 185-190. L4 refuses a pair whose observed raised class differs (`:288-291`), requires the trigger in joined new and old entries (`:292-297`), and requires the one-line analyser to miss at least one pair (`:298-301`). The audited docstring entries are `tools/souji-worktree-drift.py:44-51`; `ENOENT` is on the `RECORD-MALFORMED` entry continuation (line 46), `EACCES` on the `RECORD-MISSING` entry (line 44), and `--root` on the `RECORD-OUTSIDE-ROOT` continuation (line 51).

## Exact command and output

Command:

```sh
S=/fast/scratch/hyaku/souji-r40/w2/R40w2reviewer05 && mkdir -p "$S" && trap 'rm -rf -- "$S"' EXIT && TMPDIR="$S" python3 -B /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/c2-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 128e412b0ced3c243dc27c3dd3332054a611bc2e --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --scratch "$S"
```

Real output:

```text
LEG L1 PASS new rc=2 class=True old rc=1 class=False
LEG L2 PASS new rc=2 class=True old rc=1 class=False
LEG L3 PASS new rc=2 old rc=2
LEG L4 PASS pairs=3 missing_new=[] missing_old=[] missed_by_one_line=['RECORD-OUTSIDE-ROOT(--root)']
LEG L4b PASS joined=True one_line=False
LEG L5 PASS new=(9, 9, 0, 0) old(one-line)=(9, 6, 3, 1)
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r39-drift-record-rules=7/7(base 7/7) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14) r39-citation-rev=8/8(base 8/8)
SUMMARY legs=7 pass=7 fail=0 harm=0 drift_sha=e48ed08e6728 fixture_sha=0dc6c789a741
```

L4 output shows all three runtime-derived mappings matched (`missing_new=[]`), no old-doc trigger failures, and the expected one-line miss. No pair is passing vacuously in this execution: each pair must first match a runtime probe's raised class and then satisfy joined-doc trigger membership. The individual pair-specific refusal identity is enforced by the mapping and equality check; `ENOENT`/`EACCES` are documented as the trigger tokens for the exception conditions in the audited docstring (lines 44-48).

Scratch directory `/fast/scratch/hyaku/souji-r40/w2/R40w2reviewer05` was removed by the command's EXIT trap. No tools installed. No edits to committed files.
