# C1 base-state verification and draft-edit feasibility (ExecC1Verify-2)

Lane repo `/home/vgpnk/Projects/shokunin/souji-shokunin`, lane base `0eca7c8a5d10bcbfdae50d0c390d277deec63bfd`,
prereg landing commit under test `89e0fceeefcf28db313c94120be6d25e03c60094` (SCORECARD blob
`4b564bc628d40328d276476c4171c30817cd6e75`, 42296 bytes, 254 lines). Every lane path below is absolute;
every command was run from `/home/vgpnk/Projects/shokunin/souji-shokunin`.

## (a) K1 base literal at 89e0fce

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin grep -cE '^(Insert the table below directly above|Optional same-landing correction)' 89e0fceeefcf28db313c94120be6d25e03c60094 -- SCORECARD.md
89e0fceeefcf28db313c94120be6d25e03c60094:SCORECARD.md:2
$ git cat-file -p 89e0fce:SCORECARD.md | grep -cE '^(Insert the table below directly above|Optional same-landing correction)'
2
```

Markers are at base lines 172 and 217 (each exactly once). `Optional same-landing correction`
occurs once, not twice. Base K1 = 2, as frozen.

K2 base literal, same bytes:

```
$ git cat-file -p 89e0fce:SCORECARD.md | awk '/^### Round (23|24|25) measurements/{printf "%s ", NR} END{print ""}'
17 175 231
```

Exactly three headings; base K2 = `17 175 231`, as frozen. Round 24 exists only inside the fenced
block (`175` is the line after the fence opener at `174`).

## (b) payload extraction and byte-diff against the landing

```
$ git cat-file -p 89e0fce:SCORECARD.md | sed -n '172,228p' > payload-172-228.txt
$ wc -lc payload-172-228.txt ; sha256sum payload-172-228.txt
      57 11521 payload-172-228.txt
be1d2b157f65892f1c35cc5ec8df7473e0e4ffb935215571c3001970442d8760  payload-172-228.txt
$ sed -n '175,207p' base.md > payload-r24-table.txt ; wc -lc ; sha256sum   # 33 6749  4f6977d55e8697c6e84971b7a488c40646fef726fa9142b06659f69e4f1a3aa1
$ sed -n '213,214p' base.md > payload-caprows.txt  ; wc -lc ; sha256sum   #  2 1782  92d0d95c6b230b30b70e77004794d1431750f3e85910a90879f00cb5bf94b843
$ sed -n '225,226p' base.md > payload-bullets.txt  ; wc -lc ; sha256sum   #  2 2165  1d075fd2c26b8065891072b0a4d50a67569f143396c60044549c8526182614e9
```

No `ExecC1Surgery` draft appeared in `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-26/w1/`
during this seat, so the fragments were byte-diffed against the landed integration instead
(`a529c762c81272d398727e6a623c801a230ac157`, SCORECARD blob `2518e34b…`, identical at HEAD `0833de95…`):

```
payload fragment                                  occurrences in landed SCORECARD.md
1-16 title+axes (4108 B)                          1
231-254 Round 25 block (4303 B)                   1
175-207 Round 24 payload block (6749 B)           1
17-62 Round 23 block (4850 B)                     1
63-91 + 93 Capabilities rows (no line 92)         27 rows base / 27 rows landed  (line 92 carries R3 note)
213-214 two r24 capability rows (1782 B)          0        <-- MISSING
95-136 Planned body (5558 B)                      1
225-226 two planned bullets (2165 B)              1
138-169 Saturation..None. (1581 B)                1
```

Round 24 block and planned bullets landed verbatim; the two capability rows did not land anywhere
(`git grep 'debris census (r24)' HEAD` finds only wave drafts/lessons, never `SCORECARD.md`).

## (c) post-edit heading positions under the frozen awk counter

Three constructions were built from base bytes and scored with the literal counter
`awk '/^### Round (23|24|25) measurements/{printf "%s ", NR} END{print ""}'`:

| construction | markers | K2 triple | predicate `n25<n24<n23` |
|---|---|---|---|
| literal task recipe: delete base 170-229, insert r24 table (175-207) above base 17, leave Round 25 at the end | 0 | `17 50 204` | **FAIL** (Round 25 lands last) |
| amendment-2 order, spans abutted with no separators | 0 | `17 41 74` | PASS |
| amendment-2 order + `blank`,`---`,`blank` before the r24 block + one blank after it (= landed shape) | 0 | **`17 44 78`** | PASS |

The landed file (`a529c76` and HEAD) measures `markers=0` / `headings=17 44 78`, i.e. the third
construction: lines 41-43 are `blank`,`---`,`blank` and line 77 is the blank after the r24 block.

Consequence for the surgery seat: the base instruction at line 172 ("insert the table below directly
above `### Round 23 measurements`") is NOT sufficient — the frozen K2 predicate forces the Round 25
block (base 231-254) above the Round 24 block. Deleting the scaffold and inserting the table only
above Round 23 yields `17 50 204` and fails the claim's own kill rule.

## (d) fence-only rows and the planned-bullet duplication trap

```
$ grep -nE 'debris census \(r24\)|coverage-map agreement \(r24\)' base.md
213:| debris census (r24) | read `count-objects -v` garbage / size-garbage ...
214:| coverage-map agreement (r24) | at a full 40-hex revision, from committed bytes only, ...
$ grep -nE 'debris census \(r24\)|coverage-map agreement \(r24\)' base.md | awk -F: '$1<212 || $1>215' | wc -l
0
```

Both r24 capability rows exist only inside the `212`/`215` fence. Planned share of the check:

```
$ grep -nF -e 'r24 (planned r23) — done' -e 'r25 (planned r24):' base.md
225:- **r24 (planned r23) — done, see `corpus/lessons/round-24.md`:** ...
226:- **r25 (planned r24):** (a) calibration: make C2's per-entry kill rule ...
$ grep -nF -e 'r24 (planned r23) — done' -e 'r25 (planned r24):' base.md | awk -F: '$1<174 || $1>227' | wc -l
0
$ grep -nE '^- \*\*r2[45]' base.md
134:- **r24 — planned:** carry the F2 actable remainder ...
136:- **r25 — attempted, honest stop; C1 verified at independent candidate; ...
225:- **r24 (planned r23) — done, see `corpus/lessons/round-24.md`:** ...
226:- **r25 (planned r24):** (a) calibration: ...
```

The two fenced bullet texts are absent outside the fence, BUT `## Planned` already carries r24/r25
bullets under different prefixes at base 134 (`- **r24 — planned:**`) and 136
(`- **r25 — attempted, honest stop;...`). The anchor instruction at base 222 says to keep line 134
and append the two payload bullets after it — appending a second `- **r24 — planned:**` would be a
duplication; only the exact payload texts (`(planned r23) — done` / `(planned r24):`) may be added.
Landed file: each of the four lines occurs exactly once (`- **r24 — planned:**` 1, `- **r25 —
attempted…` 1, payload r24 bullet 1, payload r25 bullet 1); the pair was inserted after line 136's
equivalent with one extra blank line before it.

## Commands used (all read-only)

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin grep -cE ... 89e0fce -- SCORECARD.md
git -C ... cat-file -p 89e0fce:SCORECARD.md | nl -ba | sed -n '160,260p'
git -C ... cat-file -p 89e0fce:SCORECARD.md | awk '/^### Round (23|24|25) measurements/{...}'
git -C ... log --oneline 89e0fce..HEAD ; git -C ... show --stat --oneline a529c76
git -C ... diff -U2 89e0fce a529c76 -- SCORECARD.md
bash census/round-26/c1-counter.sh            # markers=0 ; headings=17 44 78 ; rc 0
```

Scratch `/var/tmp/souji-r26-ExecC1Verify` was removed after the reported values were recorded.
No tool was installed or upgraded for this seat.
