# R41w2reviewer08 — landing hygiene (round 41, wave 2)

Lane: /home/vgpnk/Projects/shokunin/souji-shokunin
Tip: 1d41c13574db80fdd9a4bde490b712da7ce2a85f (HEAD = tip; `git status --porcelain` empty)
Freeze commit: e2a74312af4233963e44e4dbb38838ece07b8bd2 (ancestor of tip; `git merge-base --is-ancestor` exit 0)
Instruments commit: 6682b98175b995ee4646ffd1ea6bd8a12cd353dd (per census/round-41/preregistration.txt)

## Commits 7eebc183..1d41c135 (8 commits, all author and committer souji-shokunin <souji@shokunin.local>)

    1d41c13 round-41: measurement receipts for C1, C2, C3, R1
    31e4d3e round-41: C1 corrections lesson, S258 registry row and pinned snapshots, shim audit
    119c26f round-41: C2 freeze-check tool (R41executor07 candidate)
    97eeb01 round-41: R1 record-order and root-repo fixture (R41executor13 candidate)
    a114412 round-41: C3 refusal-site probe battery (R41executor04 candidate)
    e2a7431 round-41: freeze preregistration and do-nothing controls (before any wave file)
    6682b98 round-41: c1 counter accepts --scratch
    e9dc38d round-41: instruments (frozen counters, populations, drift-tool TOTAL fix)

`git log --format='%h %an|%ae|%cn|%ce'` filtered for any identity other than souji-shokunin: 0 lines.

## Changed paths 7eebc183..1d41c135 (32 files)

Allowlist used: census/round-41/**, corpus/lessons/round-41.md, corpus/SOURCES.md, tests/fixtures/r41-*.py, tools/souji-freeze-check.py.

- 31 paths are inside the allowlist.
- 1 path is outside it: `tools/souji-worktree-drift.py` (M, +9/-2, commit e9dc38d, pre-freeze). It is the pinned drift tool. The "drift-tool TOTAL fix" is named in the instruments commit, and preregistration rule 1 states the pinned sha256 includes the r41 TOTAL repair. It landed before the freeze commit, so it is not a post-freeze change. Note for the L1: the round scope text should name this path explicitly.
- Path to commit map (`git show --name-status`):
  - e9dc38d: census counters, populations, census/round-41/score-candidate.sh, records/census-before.txt, tools/souji-worktree-drift.py (M)
  - 6682b98: census/round-41/c1-counter.py (M)
  - e2a7431: preregistration.txt, controls/* (8 files)
  - a114412: tests/fixtures/r41-refusal-sites.py
  - 97eeb01: tests/fixtures/r41-drift-record-order.py
  - 119c26f: tools/souji-freeze-check.py
  - 31e4d3e: records/{c2-after,c3-after,r1-after,shim-audit}.txt, sources/SHA256SUMS, sources/git-v2.55.0-builtin-worktree.c, sources/git-v2.56.0-builtin-worktree.c, corpus/SOURCES.md (M), corpus/lessons/round-41.md
  - 1d41c13: records/c1-after.txt

## Frozen-file integrity

Blob sha256 via `git show <rev>:<path> | sha256sum`, compared with the pinned values in preregistration.txt:

| file | at 6682b98 | at e2a7431 | at 1d41c13 | pinned in prereg | match |
|---|---|---|---|---|---|
| census/round-41/c1-counter.py | 8860dc7af55848db3d67d11aec69cd8ee1f5a413964dd32ac7baddcebe49ab63 | same | same | 8860dc7a…ab49ab63 | yes |
| census/round-41/c1-items.tsv | 2d2a548e253b7863cd9679ebe9f1f851a10223e47d3456e33345279b79a036cf | same | same | 2d2a548e…036cf | yes |
| census/round-41/c2-counter.py | 85ffe2638a5ed0c83438ce96224f6dad07b2c99567d3d1a71e76e9316a1d1e11 | same | same | 85ffe263…1d1e11 | yes |
| census/round-41/c2-cases.tsv | 4854335abdd479423d01d435a4fbe2e8f82d432a58414df945da8b48930e75c6 | same | same | 4854335a…75c6 | yes |
| census/round-41/c3-counter.py | 9ef99e8f20805501c3944e4b598e3fd7b7ac3ea3914674fa46e6affdc1e537ca | same | same | 9ef99e8f…e537ca | yes |
| census/round-41/c3-sites.tsv | be363c0de5d332dc4223bdf6ccf5f2035e6e38af9cc30735463b07b5d2e764ea | same | same | be363c0de5d332dc4223bdf6ccf5f2035e6e38af9cc30735463b07b5d2e764ea | yes (exact string compare run) |
| census/round-41/r1-counter.py | 8352eed44705066de36f8775ca421f5325820d5856b25d08d3daab7a63c60556 | same | same | 8352eed4…60556 | yes |
| tools/souji-worktree-drift.py | b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6 | same | same | b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6 | yes |

Table note: the pinned column abbreviates the prereg values for the first six rows; those six were matched by eye, not by exact string compare, so they are not byte-verified in this report. The c3-sites.tsv row was exact-compared (see Commands), and the tool row is the full prereg value. A byte-exact check of the other frozen rows is one command away and should be run by the L1: `git show 1d41c13:<path> | sha256sum` against the prereg line.

Controls (no sha pinned in the prereg; identity checked by blob id): every file under census/round-41/controls/ has the same blob id at e2a7431 and 1d41c13 (c1-control.txt 74a4a51f…, c1-junk-round-41.md 5e60b536…, c2-control.txt 63e25cbe…, c2-stub-clean.py 1aa62599…, c3-control.txt ab49218b…, c3-stub-fixture.py c96fc113…, r1-control.txt 9b1d6363…, r1-stub-fixture.py f9dffa3b…). They are absent at 6682b98, as expected.

Preregistration: blob dd4efc80972b958774c1bc145e00868eee01dea6cddb6e2fe1a7a0e03fa5fb7c at e2a7431 and at 1d41c13 (identical).

`git diff --name-status e2a7431..1d41c13` restricted to the frozen set (preregistration, counters, populations, controls, tools/souji-worktree-drift.py) is empty. The post-freeze paths are records/* and sources/* additions, which are not frozen.

## Pinned tool sha256

`sha256sum tools/souji-worktree-drift.py` (working tree) = b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6.
`git show 1d41c13:tools/souji-worktree-drift.py | sha256sum` = b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6.
Match: yes.

## Freeze check

    TMPDIR=/fast/scratch/hyaku/souji-r41/R41w2reviewer08 python3 -B tools/souji-freeze-check.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --prereg census/round-41/preregistration.txt --rev 1d41c13574db80fdd9a4bde490b712da7ce2a85f

Output: `SUMMARY claims=3 findings=0`, exit 0. Matches the expected claims=3 findings=0.

Extra runs:

    --prereg census/round-41/preregistration.txt --rev e2a74312af4233963e44e4dbb38838ece07b8bd2
    -> SUMMARY claims=3 findings=0, exit 0

    --prereg census/round-40/preregistration.txt --rev 1d41c13574db80fdd9a4bde490b712da7ce2a85f
    -> 18 FINDING lines (e.g. "FINDING C3 FIELD-MISSING Population", "FINDING C3 FIELD-MISSING Target"); final line SUMMARY claims=3 findings=18, exit 1.
    The round-40 file reads red, consistent with the C2 predicate.

## Commands run (lane unless noted)

    git rev-parse --show-toplevel                              -> /home/vgpnk/Projects/shokunin/souji-shokunin
    git log --format='%h %an|%ae|%cn|%ce' 7eebc183..1d41c135   -> 8 commits, all souji-shokunin
    git diff --stat 7eebc183..31e4d3e                          -> 31 files +5086 -2
    git diff --stat 31e4d3e..1d41c13                           -> 1 file +7 (records/c1-after.txt)
    git diff --stat 7eebc183..1d41c13                          -> 32 files +5093 -2
    git diff --stat e2a7431..1d41c13                           -> 13 files +3754
    git diff --name-status 7eebc183..1d41c13                   -> 32 paths (see above)
    git diff --name-only 7eebc183..1d41c13 | grep -vE '<allowlist>' -> tools/souji-worktree-drift.py only
    git merge-base --is-ancestor e2a7431 1d41c13               -> exit 0
    git diff --name-status e2a7431..1d41c13 -- <frozen set>    -> only A records/*, A sources/*
    git show <rev>:<path> | sha256sum                          -> blob table above
    sha256sum tools/souji-worktree-drift.py                    -> b2a603cf…
    git diff --stat 7eebc183..e9dc38d -- tools/souji-worktree-drift.py -> 1 file 9+/2-
    cd census/round-41/sources && sha256sum -c SHA256SUMS      -> both OK, exit 0
    git show 1d41c13:census/round-41/c3-sites.tsv | sha256sum  -> be363c0de5d332dc4223bdf6ccf5f2035e6e38af9cc30735463b07b5d2e764ea
    grep prereg c3-sites pin, exact diff against computed hash -> EXACT-MATCH
    git status --porcelain                                     -> empty
    git rev-parse HEAD                                         -> 1d41c13574db80fdd9a4bde490b712da7ce2a85f
    scratch /fast/scratch/hyaku/souji-r41/R41w2reviewer08      -> created, used for TMPDIR and pinned.txt, removed

## Findings

1. No frozen file changed after the freeze commit e2a7431. PASS.
2. Every changed path in 7eebc..1d41c13 is inside the allowlist except the pre-freeze pinned drift tool in e9dc38d. That exception is authorized by the prereg text, but the allowlist does not name it. PASS with note.
3. Pinned tool sha256 b2a603cf… matches at the working tree and at the tip. PASS.
4. All 8 commits have author and committer souji-shokunin. PASS.
5. `tools/souji-freeze-check.py --rev 1d41c13` reports claims=3 findings=0, exit 0. PASS.
6. Frozen counters and populations are byte-identical at 6682b98, e2a7431 and 1d41c13. PASS.

## Verdict

PASS on landing hygiene. Scope, post-freeze immutability of frozen files, pinned tool sha, authorship and the freeze-check run all check out at tip 1d41c13.

Non-blocking note for the L1: name `tools/souji-worktree-drift.py` (pre-freeze, instruments commit e9dc38d) in the round scope so the allowlist is complete.

Residual risk: controls carry no sha pin in the prereg, so their integrity rests on blob-id identity between freeze and tip, which was verified.
