# S77ExecC2 — C2 falsification (re-derive from committed bytes + lane disk)

## Verdicts (all REPRODUCED; no mismatch)
1. Counter at A + ledger / base no-ledger — REPRODUCED. A (`--rev ef04ca6c… --ledger census/round-77/c2-pointer-ledger.tsv`): `SUMMARY items=35 resolved=35 unresolved=0 refused=0 mismatched=0 errors=0` EXIT=0, ITEM lines identical to `records/c2-after.txt:12-46`. Base (`--rev d4f51563…` no ledger): `SUMMARY items=35 resolved=0 unresolved=35 refused=0 mismatched=0 errors=0` EXIT=1, identical to `controls/c2-K-a-no-ledger.txt`. Digests re-verified: counter `8904de85…` (prereg:56), population `bbc19ac6…` (prereg:57), ledger `011faa0e…` (c2-after.txt:11); K-b `eeb518c6…`, K-c `b8a07119…`, K-e `adab12bb…`, K-d `a82e69de…` match `# bind` lines.
2. Controls K-b/K-c/K-e/K-d — REPRODUCED (red). K-b blanket ABSENT: `resolved=4 refused=31` EXIT=1, ITEM lines identical to `c2-K-b-blanket-absent.txt`. K-c no-capture: `unresolved=31 refused=4` EXIT=1, identical to `c2-K-c-no-capture.txt`. K-e name-only MOVED: `unresolved=32 refused=3` EXIT=1, identical to `c2-K-e-name-only-moved.txt`. K-d: `c2-K-d-stub-build.sh` into fresh `/fast/scratch/hyaku/souji-r77/S77ExecC2/fx.5j4OtG/stubclone` (commit `69167c16…`, L1's `0b29b453…` differs only by timestamp), counter `--root <clone> --rev HEAD` → `unresolved=31 mismatched=4` EXIT=1; MISMATCH exactly P09,P10,P11,P18, matching `c2-K-d-stub-capture.txt`.
3. Independent recomputation — REPRODUCED. P09/P10: `sha256sum .ufo/waves/round-63/w1/S63ExecWriter/souji-receipt-write.py` = `eba4f7e0…9586f`; `git cat-file blob 6690cb5a…:<path>` = same (pop c2-population.tsv:10-11). P11/P18: `git ls-tree -r` at K lists 13 files under `.ufo/waves/round-64/w1/S64ExecFreeze/`; lane-disk `find` lists same 13; all 13 per-file sha256 equal (chronology-probe `180d8032…`, freeze-diff `6c012e5c…`, … souji-freeze-check `7d2cd741…`; pop `d:63bc0c82…` :12,19). Every MOVED row `cmp` disk vs `git cat-file blob A:<target>` BYTE-EQUAL; disk hashes equal pop `f:` (P04 `d0693448…`, P05 `5abc0a0f…`, P07 `5212878d…`, P25 `8845a942…`, P26 `9708c647…`, P29/P34 `eb55f7e5…`, P30/P35 `12064e9f…`, P31 `dabe4d2d…`).
4. Pointer check — REPRODUCED. Base: `missing=35` (checked=2198, skipped=142) EXIT=1. A: `missing=31` EXIT=1, MISSING lines identical to `records/c2-pointer-check-after.txt`. Dropped exactly `SCORECARD.md:1713`, `:1714`, `:1743`, `SKILL.md:857` = P09,P10,P11,P18.
5. FLEET — REPRODUCED. `ls -ld` at `/home/vgpnk/Projects/shokunin` shows `.ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md`, `.ufo/l0-questions.md`, `.ufo/state`, `.ufo/watchdog.log` exist (P01,P08,P12,P13,P17,P20,P32,P33). Stat only.

## Digest table (recomputed)
| item | disk sha256 | committed | verdict |
|---|---|---|---|
| P09/P10 file | eba4f7e0…9586f | eba4f7e0…9586f | EQUAL |
| P11/P18 dir (13 files) | per-file above | same 13 | EQUAL |
| P04/P05/P07 | d0693448…/5abc0a0f…/5212878d… | same | EQUAL |
| P25/P26 | 8845a942…/9708c647… | same | EQUAL |
| P29/P34, P30/P35 | eb55f7e5…/12064e9f… | same | EQUAL |
| P31 report.md | dabe4d2d…b5c56a12 | same | EQUAL |
| FLEET 8 rows | existence only | — | EXIST |

## Findings
- None (HIGH/MEDIUM/LOW: none). Every frozen C2 number reproduced; controls red at stated values. No installs (RULES.md read). Commands: counter (A/base/K-b/K-c/K-e/K-d), pointer check (base/A), sha256sum/cmp/git cat-file/ls-tree/find/ls -ld, ITEM/MISSING diffs vs receipts.

## Files written
- `.ufo/waves/round-77/w1/S77ExecC2.md` (this report, 28 lines).
- Scratch (removed): `/fast/scratch/hyaku/souji-r77/S77ExecC2/`.
