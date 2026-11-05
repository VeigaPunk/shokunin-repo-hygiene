# S61ConnSibling — sibling-overlap scan (read-only)

Seat: S61ConnSibling (connector, leaf). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Fleet root: `/home/vgpnk/Projects/shokunin`. Read-only: no git/jj mutation, no production file, no fleet file written.
Scratch: `/fast/scratch/hyaku/souji-r61/S61ConnSibling/` (id lists only; no receipts; removed at end).
No tool was installed or upgraded.

## 1. Which lanes touch the freeze-check / receipt-writer / control-chronology instruments

Command (as specified):

```
grep -rIl 'souji-freeze-check\|souji-receipt-write\|CONTROL-ADDED-NOT-BEFORE-FREEZE' /home/vgpnk/Projects/shokunin \
  --include='*.md' --include='*.py' -l --exclude-dir=.git --exclude-dir=souji-shokunin | head -30; echo EXIT=$?
```

Output: 18 files, `EXIT=0`. `head -30` did not truncate. Zero hits for `CONTROL-ADDED-NOT-BEFORE-FREEZE` anywhere outside souji.

| lane | file(s) (grep hit lines) | what it cites | class |
|---|---|---|---|
| fleet root (not a lane) | `.ufo/reports/round-{41,42,44,47,48,49,55,59,60}/souji.md` | souji's own round reports filed at the fleet root | consumption (souji work) |
| kagi-shokunin | `.ufo/waves/round-33/build/ConnOverlap.md:209,273,348` | comparison scan; names souji's `CONTROL-NOT-RED` clause as "closest, different object" | consumption (scan citing souji) |
| kaidoku-shokunin | `.ufo/waves/round-84/w1/ConnectorScope.md:43,142` (+ identical copy in `ConnectorScope/`) | "stricter shapes" comparison naming souji's ancestry / DISPATCH-BEFORE-FREEZE checks | consumption (scan citing souji) |
| kengaku-shokunin | `.ufo/waves/round-78/w1/ConnectorR78.md:3416` | table row citing souji's round-42 wave copy `souji-freeze-check.py:387` as `unrelated` | consumption (citation) |
| kumitate-shokunin | `.ufo/waves/round-82/w1/K82Connector.md:262` | cites `tools/souji-freeze-check.py:27,152` as filename contract only | consumption (citation) |
| tabi-shokunin | `.ufo/waves/round-43/w1/ConnSiblingProc.md:90` (+ `report.md`) | summary of souji rounds 38–42 landed tools | consumption (summary) |
| tameshi-shokunin | `.ufo/waves/round-77/w1/T77W1CN1.md:345` | records sha256 `d1ca06fd…` of souji's tool as a bound input | consumption (hash pin) |

Verdict on the grep: six sibling lanes, all consumption or citation; no lane holds a byte-fork of `souji-freeze-check.py` or `souji-receipt-write.py`.

Name-based own forks (not matched by the grep's exact strings; found by a `find` for `*freeze*check*` / `*receipt*write*` outside souji):

- `kasegi-shokunin/corpus/instruments/freeze-check.py` (and round-30/45/46/47 drafts): own instrument. Its header says it replays `kasegi-round-claims-v2` counters at base, born from kasegi's own round-44 defect. Different object, different format. Class: overlap by name, not by object.
- `kaidoku-shokunin/tools/round-84/freeze-precheck.py` and `tools/round-87/freeze-precheck.py`: own container-claim freeze gate. Class: overlap by name, not by object (the r60 connector recorded the same).
- `kake-shokunin/.ufo/waves/round-43/verification/freeze/registry-count-r43-freeze-check.txt`: a text record, not an instrument. Not an overlap.
- `audio-shokunin/corpus/live/r79-boundary/host/freeze-phase-check.txt`: a text record. Not an overlap.

Answer 1: six citing lanes (kagi, kaidoku, kengaku, kumitate, tabi, tameshi) are consumption; kasegi and kaidoku keep their own differently-shaped freeze gates (overlap by name only). Nothing in the fleet implements the Control-receipt-to-Counter binding or the commit-ancestry-of-control-receipt check this round adds, so the claim C1 mechanisation has no sibling duplicate.

## 2. Assimilation interface — id collision with the registry

The prompt's exact recipe was not in the seat spec. Recipe used: take line-anchored ids `^\| *S[0-9]+` from each file, sort -u, intersect.

- Registry `/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md`: 213 row ids, no duplicate ids, max **S289**, next free id **S290**. Registry ids are S001–S132, S152, S210–S289.
- Staged `/home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md`: 134 row ids, no internal duplicates, range S109–S242, `mined` in 132 rows (the other 2 rows have pipes inside cells and were not parsed for status).
- **Collisions (staged id already registered): 58 ids.** S109–S132 (24), S152 (1), S210–S242 (33).
- **Collisions with the registry's next ids S290/S291: 0.** No staged row uses S290 or S291.
- Staged-only ids (collision-free): 76, namely S133–S151 and S153–S209. These fill the registry's unused gap.
- Content check, by eye on 5 of the 58: S109 (registry: souji round-2 RENAME_NOREPLACE probe; staged: git-fetch(1) docs), S132 (registry: souji round-2 r23 worktree census; staged: souji round-3 r24 fleet-config census), S242 (registry: open(2) ENXIO; staged: a Japanese git-gc translation). These are different sources under one id, not duplicates. S152 and S210 share the GLib `g_local_file_trash` URL with the registry row but carry different scope text. The other 53 were not compared.

Answer 2: the staged file still collides, 58 of 134 rows (43%), but with already-registered ids S109–S132, S152 and S210–S242, not with S290/S291. The 76 gap ids are clean. L1 decides renumbering; nothing was adopted.

## 3. Cross-claim pattern: most valuable uncovered class for r62

Surveyed: r56–r60 wave directories (about 20 files each), the r60 ConnectorRound and CriticRound reports, the r60 MutMutation report, the r57 mutation01 table, and the r59 critic findings.

Classes that recur:

- **Chronology/ancestry**: r59 critic F1 (one-cell edit reaches the frozen counter target) and r60 critic finding 1 (control receipts added at the freeze commit). Covered by claim C1.
- **Visibility/publication**: r60 mutants c2-m1 direct-stream (killed only by an in-flight case), c2-m6 digest-worktree (survived), c2-m8 link-to-replace, c2-m9 no-stale-sweep, c2-m10 outside-outdir. r57 M19 pin-working-tree and M20 ref-tip-equality also survive. Claim C2 covers only (a) worktree digest and (b) chunked direct publish.
- **Mutant-kill of the oracle itself**: r57 had 12 of 21 mutants surviving with `SELFTEST pass cases=8`; r60 §7 found six mutants surviving both the instrument selftest and the frozen fixture. Recurring cause: assertions compare a prefix, an aggregate count or an exit code, not the finding identity.

The uncovered pattern: **publication atomicity and residue under concurrent or killed writers.** The r60 surviving mutants c2-m8 (`os.replace` in place of EEXIST-safe `os.link`, a TOCTOU window where a concurrent creator is silently overwritten), c2-m9 (no sweep of a `*.tmp` left by SIGKILL) and c2-m10 (OUT outside the lane root accepted) pass both the tool selftest (`pass=12 fail=0`) and the frozen fixture. The r60 MutMutation report says c2-m8 needs an injectable hook between fsync and publication. Neither C1 nor C2 touches this: C2(b) tests only a chunk-visible direct write, not a link-versus-replace race or stale-tmp residue. The single most valuable r62 move is an opt-in, default-off pause hook in `tools/souji-receipt-write.py` (a test-only argument or environment variable), with two new cases: a two-writer race on the same OUT, and a SIGKILL-residue case followed by a rerun. These kill c2-m8 and c2-m9 and reuse the continuous-reader harness that C2(b) needs, so one hook serves both.

## Limits

- The prompt's id-collision recipe was not in the seat spec; the recipe above is a reconstruction.
- Content comparison of the 58 collisions was by eye on 5 ids only.
- The grep covered `*.md` and `*.py` as specified; `.sh`, `.json` and `.txt` hits were not searched, so a non-md/py mention of the instruments could be missing.
- No tool was run against any candidate; every answer rests on read-only grep, find and file reads.
- Registry gap ids were derived from a `comm` run that printed sort-order warnings; the printed id list was checked against the counts (213 present, 76 absent in S133–S209) and the two agree.
