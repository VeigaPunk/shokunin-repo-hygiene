# R42scout01 — cause analysis: SCORECARD rev-unresolved tokens `65817d0d` (L14) and `09bb8e0d` (L92)

Lane: /home/vgpnk/Projects/shokunin/souji-shokunin · base bf618f6c5c09d302994871c94903abbea2deb60d · freeze afe17f416eec04dcf3f480b580a8f928de61d19d
Population rows: census/round-42/c1-items.tsv rows `14  65817d0d  B  mismatch:rev-unresolved` and `92  09bb8e0d  B  mismatch:rev-unresolved`.
All commands read-only in the lane/fleet; no mutation, no writers. Scratch /fast/scratch/hyaku/souji-r42/R42scout01 was created and deleted unused (no fixture needed).

## Verdict (both tokens)

Both tokens are **truncated sha256 file digests written with a trailing ellipsis** in SCORECARD prose (`65817d0d…`, `09bb8e0d…`), used as tool-provenance pins. The declared-evidence instrument's class-B scanner reads 8-hex as a revision token, so a 64-hex sha256 prefix + `…` becomes `mismatch:rev-unresolved`. Neither prefix ever named a git object: `git cat-file -t` fails for both, no commit in `--all` shares either prefix, and the full 64-hex strings are invalid object names (sha256, not sha1). Not a typo, not a jj-rewritten commit, not a placeholder.

## Token `65817d0d` — SCORECARD.md line 14

What the token was meant to be: the sha256 of `tools/souji-declared-evidence.py` (the r22 pinned instrument).

Evidence line in SCORECARD (base bf618f6c…): `census/round-23/records/declared-evidence-after.tsv (tool_sha256 65817d0d…, rev 9301d98c…)` — mid-line 14, the r22 attempt-2 calibration row.

Commands run and observed output:

```
$ git -C <lane> show bf618f6c…:SCORECARD.md | sed -n '14p'
| calibration | 7 | R22 **attempt 2** C1 declared-evidence calibration … now bound by the receipt
  `census/round-23/records/declared-evidence-after.tsv` (tool_sha256 65817d0d…, rev 9301d98c…) … |  [full line on record; token context verbatim]

$ git -C <lane> show bf618f6c…:census/round-23/records/declared-evidence-after.tsv | head -8
receipt=v1
rev=9301d98c1c689c79741f0f1ba1f171138d20af07
tool=tools/souji-declared-evidence.py
tool_sha256=65817d0d0d4874e8fab83ef11ae29297a865a8359f554e2ff7d2a753f21448f4
cmd=python3 tools/souji-declared-evidence.py --rev 9301d98c1c689c79741f0f1ba1f171138d20af07 --file SCORECARD.md
rc=0

$ git -C <lane> show bf618f6c…:census/round-22/attempt2/instrument-digests.txt
65817d0d0d4874e8fab83ef11ae29297a865a8359f554e2ff7d2a753f21448f4  tools/souji-declared-evidence.py
d5ed0805b10f283fcc240a2daa628681a9c76bec7df1fe1cbc7e204754ecdc9d  tools/souji-gate-check.py
round=22 attempt=2 date=2026-10-25 …

$ git show c9f1fe3caf642dfe3a9e00de94caf1d4bf86503f:tools/souji-declared-evidence.py | sha256sum
65817d0d0d4874e8fab83ef11ae29297a865a8359f554e2ff7d2a753f21448f4  -
$ git show 9301d98c1c689c79741f0f1ba1f171138d20af07:tools/souji-declared-evidence.py | sha256sum
65817d0d0d4874e8fab83ef11ae29297a865a8359f554e2ff7d2a753f21448f4  -   (identical blob at the after-rev)
$ git cat-file -t 4edb25dfe262515d0da63224bbba71e02e36cba5 ; git cat-file -t 9301d98c1c689c79741f0f1ba1f171138d20af07
commit / commit   (the line's real revision tokens resolve; only the digest prefix does not)
```

Negative sweeps for `65817d0d`: `git cat-file -t 65817d0d` → `fatal: Not a valid object name`; `git log --all --format=%H | grep -E '^65817d0d'` → empty; `git cat-file -t 65817d0d0d4874e8fab83ef11ae29297a865a8359f554e2ff7d2a753f21448f4` → `fatal: Not a valid object name` (64-hex); fleet `git -C /home/vgpnk/Projects/shokunin log --all -S'65817d0d' --oneline` → no commits; `jj --ignore-working-copy op log --no-graph | grep -cE '65817d0d|09bb8e0d'` → `0`. Lane pickaxe `git log --all -S'65817d0d' --oneline` hits only prose/census commits that introduce the digest text (r22 `f8f0b4a2…`, r23 receipts, r24 onward, r42 instruments commit `410316c9…`) — never a revision reference.

Note: the current worktree `tools/souji-declared-evidence.py` hashes `a3324916…` — the tool changed after r23; the digest pin refers to the r22/r23 instrument blob, which is intact at `c9f1fe3…` and `9301d98c…`.

## Token `09bb8e0d` — SCORECARD.md line 92

What the token was meant to be: the sha256 of `tools/souji-size-census.py` at the r24 lane-bound size measurement.

Evidence line in SCORECARD (base bf618f6c…): `` … `unreachable=1093 alternates=0`, tool sha256 `09bb8e0d…`) describes this repository at the moment of … `` — line 92, the lane-bound size-census row.

Commands run and observed output:

```
$ git -C <lane> show bf618f6c…:census/round-24/size-census-lane.txt | head -8
# lane-bound C1 measurement: this repository only, at the moment of the run …
rev=778747eb671f8e85ef5387bc3d7023337b30467c
tool=tools/souji-size-census.py
tool_sha256=09bb8e0d9906b0dfef44775a9e5cd7c8f8a27d9bcdf559e2d371a3ef7ff1ed6d
cmd=python3 -B tools/souji-size-census.py --repo /home/vgpnk/Projects/shokunin/souji-shokunin
utc=2026-10-25T09:34:49Z

$ git show 778747eb671f8e85ef5387bc3d7023337b30467c:tools/souji-size-census.py | sha256sum
09bb8e0d9906b0dfef44775a9e5cd7c8f8a27d9bcdf559e2d371a3ef7ff1ed6d  -
$ git cat-file -t 778747eb671f8e85ef5387bc3d7023337b30467c
commit
```

Negative sweeps for `09bb8e0d`: `git cat-file -t 09bb8e0d` → `fatal: Not a valid object name`; `git log --all --format=%H | grep -E '^09bb8e0d'` → empty; full 64-hex `cat-file -t` → `fatal: Not a valid object name`; fleet pickaxe `-S'09bb8e0d'` → no commits; jj op log grep → `0`. Lane pickaxe hits are prose/census commits carrying the digest text (r24 receipts `ca7fc1cb…`/`315422ba…` onward, r35, r42 instruments commit `410316c9…`).

Note: current worktree `tools/souji-size-census.py` hashes `c5690681…` — tool changed after r24; the pinned blob at `778747eb…` matches the digest exactly.

## Confidence and residual unknowns

- Both cause-class determinations rest on the token's immediate textual context in the base SCORECARD line (`tool_sha256 <prefix>…` / `` tool sha256 `<prefix>…` ``) plus a committed receipt carrying the full 64-hex value whose blob re-derivation matches. No counter-evidence found anywhere (lane history, fleet history, jj op log). Confidence high.
- Residual (not blocking): the class-B scanner of `tools/souji-declared-evidence.py` classifying an ellipsis-suffixed 8-hex digest as a revision token is the mechanism by which these became `rev-unresolved`; I observed the classification via the c1 population, not by re-running the instrument — the instrument and its reads are frozen and outside this seat's scope.
- The remaining 3 unresolved items of the 5 are outside this ticket.

## Final lines

65817d0d | sha256 prefix mistaken for a revision (truncated tool digest of tools/souji-declared-evidence.py, full value 65817d0d0d4874e8fab83ef11ae29297a865a8359f554e2ff7d2a753f21448f4, not a git object) | - (no git candidate; file sha256 as above) | high
09bb8e0d | sha256 prefix mistaken for a revision (truncated tool digest of tools/souji-size-census.py, full value 09bb8e0d9906b0dfef44775a9e5cd7c8f8a27d9bcdf559e2d371a3ef7ff1ed6d, not a git object) | - (no git candidate; file sha256 as above) | high
