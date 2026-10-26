# SwarmMutationTester34 — C3 counter mutation test (souji r31 w1)

## Status

STATUS: PASS — all 8 assigned mutants (14 counter instances: 6 shared legs × v1+v2, 2 L12-only × v2) are killed by reproduced adversarial states; zero survivors; no counter defect found. Two provenance findings recorded (F1, F2). Lane bytes untouched (hashes below).

## Evidence

Scratch: `/fast/scratch/hyaku/souji-r31/MutateC3Counter/` (clone `c` of the lane, origin dropped, detached at prereg rev; TMPDIR under scratch; counter runs always with `--scratch $D/ctr`). No tool installs needed: jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5 and git 2.56.0 already on host (`jj --version`, `git --version`).

Baseline detector (pristine copies, sha256 `c978ad7ce620c066…` v1, `72a946e3cc2cc53d…` v2 — equal to lane bytes) reproduces both frozen controls byte-for-byte:

```
python3 -B muts/pristine-v1.py --root c --rev 1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525 --base 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc --scratch ctr
→ SUMMARY legs=11 fail=10 f1_entries=3 rev=1d45496…   (controls.tsv C3-do-nothing c3: identical)
python3 -B muts/pristine-v2.py … → SUMMARY legs=12 fail=11 f1_entries=3 rev=1d45496…   (controls.tsv c3v2: identical)
```

Junk state A rebuilt in scratch from the controls.tsv description (sourceless entry + typed record + cat fixture + F1 map row), rev `a076d7f111f49e80fd464eab20c1b5da7597a033`; pristine reproduces the committed junk control lines exactly: v1 `legs=11 fail=4 f1_entries=4`, v2 `legs=12 fail=5 f1_entries=4` (controls.tsv C3-junk rows: identical). The committed junk rev itself is unresolvable — see F1.

Kill protocol per mutant: run pristine and mutated counter on the same state; a mutant is killed where its target leg flips FAIL→PASS on state work the pristine counter rejects. Do-nothing baseline failures are inconclusive (counter is supposed to fail there) and were not used as kills.

| # | Mutant (defect) | Instances | Junk control kills? | Killing state (scratch rev) | Pristine → mutant on that state |
|---|---|---|---|---|---|
| M1 | count `ground: F1` anywhere (drop `-- corpus/knowledge/` pathspec, c3-counter.py:82 / v2:89) | v1+v2 | NO — flips *stricter* at junk rev: L1 FAIL f1_entries=14 (10 non-knowledge `^ground: F1` files at prereg) | B1 `5244072765b14acdb0843e31587219e0af5a3dba` (probe file `census/round-31/records/ground-anywhere-probe.md` with `ground: F1`; the 10 other non-knowledge matches neutralized to `ground: F10`, which `^ground: F1\b` does not match) | L1 FAIL f1_entries=3 → L1 PASS f1_entries=4 |
| M2 | L6 drops absent-at-base (`i not in base_rows` removed, :149/:171) | v1+v2 | NO — junk entry is sourceless, cited=[] both | B2 `6695f1a4fa2c98abfd167286299a0c804f8266f7` (entry cites S002; S002's opened cell moved 2026-10-19→2026-10-26) | L6 FAIL new_opened_today=[] → L6 PASS new_opened_today=['S002'] |
| M3 | L8 accepts record without `object_present=no` (conjunct dropped, :157-159/:179-181) | v1+v2 | NO — junk record carries both =yes and =no | B3 `f4a4e7f9dcac1fa233324b01f1b30cf6f97205fd` (record with 4 RESULT lines, all `object_present=yes`) | L8 FAIL → L8 PASS |
| M4 | L9 compares replay as a set (`sorted(lines) == sorted(rl)`, :161/:183) | v1+v2 | NO — junk fixture differs in content, not order | B4 `040920576a8f6dadc285f5452891efe3ff116c4f` (fixture replays the same 4 RESULT lines in order 2,1,4,3 vs record 1,2,3,4) | L9 FAIL replays=[(0,4,False),(0,4,False)] → L9 PASS (same leg line, verdict flipped by sorted compare) |
| M5 | L10 whole-line rule → substring (`s not in run`, :164/:186) | v1+v2 | NO — junk spans are whole record lines | B5 `090884ecc8ede95ae6798ac81114e9258ec32c00` (3 backticked spans trimmed of their ` seconds=…` tail — substrings of record lines, not whole lines) | L10 FAIL not_in_record=[3 spans] → L10 PASS not_in_record=[] |
| M6 | L12 accepts shim log without `reflog expire` (`"git reflog expire": True`, v2:193) | v2 only (v1 has no L12) | NO — junk log is empty; jj abandon/util gc/gc/cat-file needs still unmet | B6 `b4ce50d54b4d7816990f60c50a10720a011f3e61` (fixture logs `jj abandon`, `jj util gc`, `git gc`, `git cat-file -e` through the PATH shim, never `reflog expire`; rc 0, RESULT lines equal record) | L12 FAIL missing=['git reflog expire'] → L12 PASS missing=[] |
| M7 | L12 passes when git bypasses the shim (absolute `/usr/bin/git`): git needs vacuous when no `git ` call is logged (`all(v for k,v in need.items() if k.startswith("jj") or gt)`, v2:195) | v2 only | NO — jj needs still unmet at junk | B7 `0073497f27ef8420912dcc5ac76355d43741b575` (fixture calls jj via PATH but every git call as absolute `/usr/bin/git`, incl. `reflog expire`; shim log has jj_calls=2 git_calls=0) | L12 FAIL git_calls=0 missing=[3 git needs] → L12 PASS |
| M8 | L11 skipped (`leg("L11", True, …)`, :166/:188) | v1+v2 | NO — junk registry validates, rc=0 both | B8 `4d109f5b77cc013e078e2554f02892964289473e` (S001 id → `SX01`; `sources-census.sh validate` → E01/E02 class failure, rc=1) | L11 FAIL sources-census rc=1 → L11 PASS sources-census rc=1 |

Survivors: **none**. Every mutant instance flipped permissive on its targeted state while pristine rejected the same bytes.

Restoration: mutants were separate copies; lane files never edited. After all runs, lane hashes re-checked identical (`c978ad7c…`, `72a946e3…`) and pristine re-run at the do-nothing rev again printed both frozen control SUMMARY lines exactly.

## Findings

1. **F1 — committed C3-junk control bytes are unresolvable.** controls.tsv (census/round-31/records/controls.tsv, rows `C3-junk…`) pins rev `1f183e359d6013bd9f92fe9688ee984742459f1a`, but `git -C <lane> cat-file -t 1f183e35…` → `fatal: git cat-file: could not get object info` at lane tip 1b811368461785040e955f41f9c97e62f61fd67c, and the same cat-file fails in the fleet repo `/home/vgpnk/Projects/shokunin`. The junk control's bytes cannot be re-verified from any repo I can read; only its SUMMARY lines are pinned. I rebuilt a state from the row's own description that reproduces both committed SUMMARY lines exactly (state A above) — the kill verdicts do not depend on the missing object, but the control as committed is not independently re-runnable. Quote (controls.tsv, C3-junk row): `SUMMARY legs=11 fail=4 f1_entries=4 rev=1f183e359d6013bd9f92fe9688ee984742459f1a`.
2. **F2 — the junk control kills none of the 8 counter mutants.** It separates junk deliveries from real work, not weakened counters from real ones: on state A every mutant returns pristine's verdict (M1 even stricter, f1_entries=14). Coverage consequence: counter-predicate regressions are invisible to the committed control set; they are caught only by targeted states like B1–B8. Locations: controls.tsv C3-junk rows; counter legs cited in the table.
3. **F3 — L1's pathspec is load-bearing for the `==4` target.** At prereg rev, `^ground: F1\b` matches 10 files outside corpus/knowledge (8 round-26 wave-record copies, census/round-30/controls.sh:62 heredoc, census/round-30/waves/w1/deliver-entry-jj-keep-ref-expiry.md:7); a whole-tree L1 would read f1_entries=13 at the do-nothing rev (observed 14 at the junk rev). Quote (c3-counter.py:82): `r"^ground: F1\b", V, "--", "corpus/knowledge/"`.
4. No tool installs or upgrades were performed (none needed).

## Attack log

- A1–A8: the eight mutants above, run as adversarial counter variants against junk state A and targeted scratch states B1–B8; all killed (FAIL→PASS flips recorded); no surviving weakening of either counter; no change to any counter, predicate or case set proposed.
- A9: ATTACK against the control set (not the counters) — controls.tsv pins a C3-junk rev absent from the lane and fleet ODBs (reproduced: `git cat-file -t` fatal in both, see F1). Disposition for the L1: either land the junk state's bytes in the lane (or record its full tree hash) so the control is re-runnable, or accept the rebuilt-state reproduction above as the standing reproduction.

## Deliveries

- `.ufo/waves/round-31/w1/SwarmMutationTester34.md` — this report (only file written in the lane).
