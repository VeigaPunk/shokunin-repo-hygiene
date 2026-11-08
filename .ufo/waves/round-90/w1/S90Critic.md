# S90Critic — r90 falsification report (C1 calibration-7 binding, C2 operability-8 pair)

Seat: S90Critic (critic). Lane: `souji-shokunin` (id `souji`), `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Lane HEAD at measurement: `fd25bfc5430cf27c1af5e4c8b8f6d5899e91a20f` (F, the preregistration alone).
Chain: base `bd760432` → P1 `1952c1c7` → C2 repair `4cb3a06f` → P2 `e2a11c73` → F `fd25bfc5`.
Worktree at measurement was dirty from other seats (`M SCORECARD.md`, `M corpus/README.md`, `M corpus/SOURCES.md`,
untracked `plans/round-90.md`, `corpus/knowledge/nel-byte-character-pair.md`, `census/round-90/records/{c1-after,c2-after,prefreeze-c1-both}.txt`);
I touched none of it.

All instruments re-hashed at HEAD and match the frozen prereg exactly:

```
d64d76954daea7da5d36e6f5eda96ae343bdd37db5071ea50bd55b30a1844b45  census/round-90/c1-false-rows.tsv
fd0a8e244a5e0afe58f9e8bfa85d314722b77a1bcbe6837298683f74a755220b  census/round-87/c1-pointer-counter.py
392522489bc6f22a9747f64d311dbde7528dd0e8b481159db15d3eb038066dd5  census/round-90/c1-mutants.json
e7265335e4458e68d2277dd0ad4f36e68999a7ba70363d60dc2155bd9cfa2d39  census/round-90/c1-clause-battery.py
c3664747ffe712fde8f61c34562df2f0e92f2a0378b151bd0b4d74e91d629cbe  census/round-90/c1-false-row-harness.py
d44172132f0a0c707d47e9522df8502f8d84859eb3e82d13e09809450c94aeaa  tests/fixtures/r90-k4-flagfail.py
d095b52fa5d90e3e563542eb6cea309e82ace59bde36e5992ede847059968561  tools/souji-record-agreement.py
f6fce6d147165d1baf3d8d0343f46c1ab913b23947f3edaa28b61cdd6caa18dd  census/round-90/controls/c2-before-tool.py
296df5332aefe695b4951b511288b118bc6a7b43db7fadfd60f6062096acc7c0  census/round-90/srcs/tr14.html (226166 bytes)
```

## Verdict

**No frozen sentence is falsified by this wave's artifacts.** Both after arms and both do-nothing controls
reproduce fresh at HEAD, byte-identical to the committed receipts; the C1 mechanism and the C2 pair behave
exactly as the prereg predicts.

Two **discriminant gaps** and one **disclosed scoring asymmetry** are real, and are findings against the
`COUNTER` block rather than against the claims' prose:

1. **C1 — the battery does not bind itself.** The battery prints the counter, harness, mutants and population
   hashes but **not its own**. A battery that prints the target `SUMMARY` and exits 0 scores the literal
   predicate with zero runs (reproduced). Only the prereg's external pin `e7265335…` catches it.
2. **C2 — the predicate does not test the dead-code half.** A tool that applies only the U+0085 spelling change
   and **keeps `_one_line`** scores `tool_pass=12 before_pass=10` EXIT 0. Conversely a broad C1-class repair
   (`0x80..0x9F → \uNNNN`) also scores while changing unclaimed spellings. Both reproduced.
3. **C2 — `before_pass=10` is fair but only at CASE granularity.** On the r89 tool KFF10's own raw-byte spelling
   is already correct; it fails only the new pair check. The prereg discloses the pair binding to KFF10
   (STATED LIMITS iii, plans A0.1), so this is an honest asymmetry — but the SUMMARY line alone reads as if two
   cases were repaired when one branch changed.

## 1. Reproductions (commands and exact tails)

### C2 after arm — target met

```
python3 -B tests/fixtures/r90-k4-flagfail.py --tool tools/souji-record-agreement.py \
  --before census/round-90/controls/c2-before-tool.py --work /fast/scratch/hyaku/souji-r90/S90Critic/r1
```
tail (full file `.ufo/waves/round-90/w1/S90Critic/receipts/c2-after.txt`):
```
CASE KFF9 tool=pass before=fail
CASE KFF10 tool=pass before=fail
SUMMARY cases=12 tool_pass=12 before_pass=10
EXIT 0
```

### C2 do-nothing control — the r89 bytes as BOTH arms

```
python3 -B tests/fixtures/r90-k4-flagfail.py --tool census/round-90/controls/c2-before-tool.py \
  --before census/round-90/controls/c2-before-tool.py --work /fast/scratch/hyaku/souji-r90/S90Critic/r2
```
tail (`receipts/c2-control-both-arms.txt`):
```
CASE KFF9 tool=fail before=fail
CASE KFF10 tool=fail before=fail
SUMMARY cases=12 tool_pass=10 before_pass=10
EXIT 1
```
Identical to the committed `census/round-90/records/prefreeze-c2-control.txt` (tail compared byte-for-byte).

### C2 regression (not part of the target) — reproduced

```
python3 -B census/round-87/c2-k4-counter.py --tool tools/souji-record-agreement.py --work <scratch>
```
tail (`receipts/c2-k4-regression.txt`): `SUMMARY rows=12 mismatches=0 errors=0` / `EXIT=0`, counter sha
`4e2b7c06…`, matching `census/round-90/records/prefreeze-c2-k4-regression.txt`.

### C1 after arm — target met, fresh at HEAD

```
python3 -B census/round-90/c1-clause-battery.py --counter census/round-87/c1-pointer-counter.py \
  --work /fast/scratch/hyaku/souji-r90/S90Critic/c1w2 --only r89,r90 --expect-killed 31
```
tail (`receipts/c1-after-fresh.txt`; 793 s — serial fixture builds):
```
ARM pristine pop=r89 rows=57 mismatches=0 errors=0 exit=0
ARM pristine pop=r90 rows=58 mismatches=0 errors=0 exit=0
MUTANT m17c-no-malformed pop=r89 killed=no mismatches=0 errors=0 exit=0
MUTANT m17c-no-malformed pop=r90 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR m17c-no-malformed pop=r89 killed=no mismatches=0 errors=0 exit=0 | pop=r90 killed=yes mismatches=1 errors=0 exit=1
SUMMARY mutants=16 sets=r89,r90 pristine_r89=ok pristine_r90=ok killed_r89=15 killed_r90=16 killed_total=31
EXIT=0
```

### C1 do-nothing control — passes its own (non-target) predicate, fresh at HEAD

```
python3 -B census/round-90/c1-clause-battery.py --counter census/round-87/c1-pointer-counter.py \
  --work /fast/scratch/hyaku/souji-r90/S90Critic/c1ctl --only r89 --expect-killed 15
```
tail (`receipts/c1-control-fresh.txt`; 568 s):
```
MUTANT-PAIR m17c-no-malformed pop=r89 killed=no mismatches=0 errors=0 exit=0
SUMMARY mutants=16 sets=r89 pristine_r89=ok killed_r89=15 killed_total=15
EXIT=0
```

Both fresh files are byte-identical to the committed receipts (excluding the `EXIT=` line this seat appends):
after `cmp`s equal to `census/round-90/records/prefreeze-c1-both.txt`, control `cmp`s equal to
`census/round-90/controls/c1-before-r89-population.txt`. The committed prefreeze receipt carries the same target:

```
ARM pristine pop=r89 rows=57 mismatches=0 errors=0 exit=0
ARM pristine pop=r90 rows=58 mismatches=0 errors=0 exit=0
MUTANT-PAIR m17c-no-malformed pop=r89 killed=no mismatches=0 errors=0 exit=0 | pop=r90 killed=yes mismatches=1 errors=0 exit=1
SUMMARY mutants=16 sets=r89,r90 pristine_r89=ok pristine_r90=ok killed_r89=15 killed_r90=16 killed_total=31
```
and the committed control `census/round-90/controls/c1-before-r89-population.txt` reads
`SUMMARY mutants=16 sets=r89 pristine_r89=ok killed_r89=15 killed_total=15` with
`MUTANT-PAIR m17c-no-malformed pop=r89 killed=no … exit=0`; it is byte-identical to
`records/prefreeze-c1-control.txt` (`cmp` → identical).

### C1 mechanism — direct, no fixture build (attribution)

Command pattern (`receipts/c1-mechanism.txt`): r77 population + a ledger copy = r77 ledger + one appended row,
pristine and the m17c mutant (the mutation is exactly the frozen text `if r[0] in ledger:` — the length guard
dropped).

```
=== c1-pointer-counter.py ledger=ledger-r89  rc=0 ===  SUMMARY items=35 … refused=0 …
=== c1-pointer-counter.py ledger=ledger-ld2  rc=1 ===  LEDGER-REFUSED id=P02 why=unknown or duplicate id
=== c1-pointer-counter.py ledger=ledger-ld2b rc=1 ===  LEDGER-REFUSED id=ZZ9 why=unknown or duplicate id
=== counter-m17c.py      ledger=ledger-r89  rc=0 ===  SUMMARY items=35 … refused=0 …
=== counter-m17c.py      ledger=ledger-ld2  rc=1 ===  LEDGER-REFUSED id=P02 why=unknown or duplicate id
=== counter-m17c.py      ledger=ledger-ld2b rc=1 ===  IndexError: list index out of range   (no marker)
```
This is exactly the prereg's MECHANISM paragraph: LD2 (`P02`) is refused by the duplicate leg on both pristine
and m17c, so m17c survives r89; LD2b (`ZZ9`, absent from `census/round-77/c2-pointer-ledger.tsv`) reaches the
length guard, and m17c crashes with no marker. Attribution to LD2b is therefore forced: the r89 scored
population leaves m17c green, and the only r89→r90 population delta is LD2b.

### Population arithmetic

`diff <(r89 population) <(r90 population)` → exactly `59a60 > LD2b …`; deleting the LD2b line from the r90 file
reproduces the r89 file's sha256 `04570a64…` byte-for-byte. `ZZ9` does not occur in the r77 ledger; `P02` does
(line 3). The counter at HEAD hashes `fd0a8e24…`, the same pin as `census/round-89/preregistration.txt`.

### Mutant-set arithmetic

`census/round-90/c1-mutants.json` members are equal to `census/round-89/c1-mutants.json` members (16/16, same
order, same text); only the file's `note` differs, which is why the whole-file sha differs (`bc7e6bb1…` at
base vs `39252248…` at r90). The frozen sentence "the r89 sixteen byte-identical" is true at member granularity;
read at whole-file granularity it is not, and the file's own note says exactly which unit is identical.

### C2 source (S353) provenance

`census/round-90/srcs/tr14.html` hashes `296df533…` (226166 bytes) and contains the quote, 18 words. The stated
"tag-stripped offset 82360" reproduces exactly under: strip tags with `<[^>]*>`→``, `html.unescape`, keep
whitespace, and locate the sentence with per-word `\s+` (the source wraps lines). Character offset = 82360
(byte offset 82555). Other tag-strip methods give 68483/68640; the offset is method-dependent, the quote and word
count are not. Not falsified.

## 2. Cheat table

Scored against the literal predicates. Evidence files in `.ufo/waves/round-90/w1/S90Critic/receipts/`.

| # | Cheat | Result | Score | Evidence |
|---|---|---|---|---|
| C1.1 | no-work: `--only r89 --expect-killed 15` and stop | `killed_total=15` | no | fresh control §1; `receipts/c1-control-fresh.txt` |
| C1.2 | edit the r90 population: drop LD2b | `BATTERY-FATAL: r90 population sha256 04570a64… is not the pin d64d7695…`, EXIT 1 | no | `c1-cheat-population-pin.txt` |
| C1.3 | edit the counter instead of the population | receipt prints `# counter … sha256=` ≠ `fd0a8e24…`; and any edit that keeps pristine green and r89=15 must still die on the r90-only row, i.e. on LD2b | no | static + §1 mechanism |
| C1.4 | edit the harness | receipt prints `# harness … sha256=` ≠ `c3664747…`; same structural argument as C1.3 | no | static |
| C1.5 | edit the mutants | receipt prints `# mutants … sha256=` ≠ `39252248…`; and m17c must stay alive on r89 to keep 15 | no | static |
| C1.6 | edit the battery to print the target `SUMMARY` and exit 0 | `SUMMARY mutants=16 … killed_total=31`, EXIT 0 | **yes** (literal) | `c1-cheat-battery-print.txt`; `variants/c1-battery-print-cheat.py` |
| C2.1 | no-work: r89 tool as `--tool` | `tool_pass=10`, EXIT 1 | no | `c2-control-both-arms.txt` |
| C2.2 | delete `_one_line` only, keep the r89 spelling | `tool_pass=10 before_pass=10`, EXIT 1 | no | `c2-cheat-delete_only.txt` |
| C2.3 | spell U+0085 `\u0085` but **keep `_one_line`** | `tool_pass=12 before_pass=10`, EXIT 0 | **yes** | `c2-cheat-spellonly_keep_one_line.txt` |
| C2.4 | broad repair: every `0x80..0x9F` → `\uNNNN` | `tool_pass=12 before_pass=10`, EXIT 0 | **yes** | `c2-cheat-broad_c1_class.txt` |
| C2.5 | fixture edit: relax KFF9 to the before spelling, keep the pair | `tool_pass=10 before_pass=10`, EXIT 1 | no | `c2-fixture-cheat-relax_keep_pair.txt` |
| C2.6 | fixture edit: relax KFF9 and drop the pair binding | `tool_pass=12 before_pass=12`, EXIT 1 (the fixture's own `b >= a` guard) | no | `c2-fixture-cheat-relax_drop_pair.txt` |
| C2.7 | fixture edit: forge the control's failure (`old["KFF9"]=old["KFF10"]=False`), tool untouched | `tool_pass=12 before_pass=10`, EXIT 0 | **yes** | `c2-fixture-cheat-forge_control_fail.txt` |

Reading of the three **yes** rows:

- C1.6 is the degenerate cheat; it is not a work change to the instrument's subject. It scores only because the
  battery never prints its own sha256; the prereg pin catches it. It is a **receipt-binding gap**, not a claim
  defect. Smallest fix: print `# battery path=… sha256=…` as the battery's first line (one line; the after
  receipt then carries the battery's identity).
- C2.3 is the important one: the C2 predicate is **half-blind**. The claim has two conjuncts — the injective
  spelling and the `_one_line` deletion — and `cases=12` tests only the first. A tool with the repair half done
  scores the target. This does not falsify the claim's prose (the filed tool does delete the helper: grep
  `def _one_line(` = 0, call sites = 0), but the `COUNTER` block does not certify half of the claim. Smallest
  fix: one extra fixture case that asserts `not hasattr(module, "_one_line")` on the tool copy (or a
  `grep -c 'def _one_line('` conjunct in the target).
- C2.7 shows the fixture's own guards are load-bearing: relaxing the expectation alone trips `b >= a`
  (C2.6 → EXIT 1), so the cheapest fixture cheat must forge the *control arm*, which changes the fixture sha
  (printed) and is caught by the prereg pin `d4417213…`. This is a **receipt-binding gap of the same shape as
  C1.6**: the fixture prints its own sha, so it is detectable in the receipt, but only against the external pin.

C2.4 is not a cheat in the falsification sense (a superset repair still satisfies the claim's sentence); it is
evidence that the target does not discriminate the minimal rule from a broader one that changes spellings the
claim never mentions. I did not run the broad variant through the r87 K4 regression (the filed tool was run:
12/0/0), so a regression from that breadth is not excluded here (§7).

## 3. Axis verdict — C1 is a calibration move, not a coverage move

`AXES.md` (fleet root) defines the two axes:

> `| **coverage** | Fraction of the domain's real surfaces the skill governs (repo paths, tools, edge classes) | PROVINCE.md lists every surface; none unexplored without reason |`
>
> `| **calibration** | Self-assessment quality: gaps named honestly, confidence graded, overreach caught | SHONEN.md/SCORECARD entries match observed repo state |`

The move: the counter, its kill rule and the mutant texts are unchanged; only the pinned population grows, and
the number that moves is the **mutant kill tally** (15/16 → 16/16), i.e. a graded statement of how much of the
counter's own clause set the counter's killer battery can certify. That is calibration's "confidence graded" and
"gaps named honestly" (r89 named `m17c` as the sole survivor; r90 closes it). The row adds no governed surface:
the prereg's own limit (iv) says "The population is a fixture population, not a census of the lane's ledgers",
and the row's id `ZZ9` is absent from the frozen ledger — it exists only to exercise the guard.

Verdict: **calibration 7 is the correct label**; a coverage label would require the row to be a real lane
surface (a real ledger's corruption class), which limit (iv) disclaims. The strongest counterargument — AXES'
coverage clause literally lists "edge classes", and a 2-column ledger row is one — fails on the measurement: the
claim's target is a kill tally of the instrument against itself, not a count of governed domain surfaces. Note
the axis **score does not move** (7 before and after), so this is not score inflation either way.

## 4. C2 before_pass arithmetic — what the 10 means

On the r89 tool (the `--before` arm), per CASE: KFF1–KFF8 pass, KFC1/KFC2 pass (10), KFF9 fails, KFF10 fails.
Instrumented directly (`receipts/c2-collision-sweep.txt`):

```
r89-before byte0x85   = '\\x85'      r89-before charU+0085 = '\\x85'
r90-after  byte0x85   = '\\x85'      r90-after  charU+0085 = '\\u0085'
r89-before KFF9_own=False  KFF10_own=True  pair_distinct=False
r90-after  KFF9_own=True   KFF10_own=True  pair_distinct=True
```

So **KFF10's own check already passes on the r89 tool**; it is the r90 pair rule (detail cells must differ) that
turns it red on the before arm. Only KFF9's spelling check fails on its own merits. `before_pass=10` is therefore
a *fair* control under the frozen rule — the rule is applied to both arms symmetrically (plans A0.1 discloses
exactly this, and with the old one-arm pair rule the same run read `before_pass=11`) — but the summary alone
**hides that exactly one spelling changed**.

Honest sentence (the one the report should carry):

> On the r89 tool, 10 of 12 cases pass: KFF9 fails because the character U+0085 renders `\x85` instead of
> `\u0085`; KFF10's raw-byte spelling is already `\x85` and correct, and KFF10 fails only the new pair check
> because the r89 tool gives KFF9 and KFF10 the same cell. The repair changes one spelling; two case scores move.

The prereg's CLAIM sentence already states the correct narrow fact ("the CHARACTER U+0085 … now takes the
`\u0085` spelling") and KILL RULE (iii) discloses the pair binding; the misleading reading exists only if the
`SUMMARY` line is quoted without the CASE lines.

## 5. Collision sweep, 0x80..0xFF

`receipts/c2-collision-sweep.txt`: for every `NN` in `0x80..0xFF`, compare
`_escape_text(_decode_record(bytes([NN])))` with `_escape_text(chr(NN))`:

```
r89-before 0x80..0xFF byte/char collisions: [('0x85', "'\\\\x85'")]
r90-after  0x80..0xFF byte/char collisions: NONE
```

No other pair in that range collides, and none can: the raw byte always decodes to a lone surrogate
`U+DC80..U+DCFF` and is spelled `\xNN` by the surrogate branch; no character in `U+0080..U+00FF` reaches that
branch (the only special-cased character is `U+0085`, now `\u0085`; the rest pass through raw), so the two arms
cannot produce the same string. The r89 collision was exactly one character (`U+0085`), so the repair is
complete **for the enumerated 0x80..0xFF pair**.

Disclosed, not falsified: (a) the elided-middle collision survives — two >200-byte stderrs differing only in
the middle render identically (`receipts` shows `elided-middle identical: True`, 200-char cell); (b) a raw
window that cuts the `C2 85` pair spells `\xc2`/`\x85` instead of `\u0085`, which limit (ii) covers; (c) the
characters `U+0080..U+009F` other than `U+0085` still pass through raw on both tools — not a byte collision, but
invisible control characters in a record cell (no line-splitting hazard: `splitlines()` splits only on `0x85`,
`0x0B`, `0x0C`, `0x1C–0x1E`, `U+2028`, `U+2029`).

## 6. Sentences I think are falsified

**None.** For completeness, the sentences I tested and the verdict:

- C1 "the SOLE surviving clause … is bound by LD2b (`ZZ9\tABSENT`, absent id)": **verified** (§1).
- C1 "58 rows = the r89 57 byte-for-byte plus LD2b": **verified** (diff `59a60`; reverse-delete restores the r89
  sha).
- C1 "counter … UNCHANGED" / "16 mutants … the r89 sixteen byte-identical": **verified** at the stated units;
  the whole-file mutants sha differs only because the file's `note` differs (precision note, not falsified).
- C1 predicate and do-nothing control: **reproduced** fresh at HEAD (§1); both fresh receipts `cmp`-identical to
  the committed receipts.
- C1 MECHANISM and STATED LIMITS (ii)–(iv): **verified** (§1; the marker does not attribute the branch — the
  marker text is literally `why=unknown or duplicate id`).
- C2 "raw byte 0x85 keeps `\x85`, CHARACTER U+0085 takes `\u0085`": **verified** by direct import on both arms.
- C2 "`_one_line` (zero callers) is deleted": **verified** — the r89 filed bytes have one definition and zero
  call sites; the filed tool has zero of each (`receipts/c2-dead-helper-grep.txt`: `0`, `0`).
- C2 predicate `cases=12 tool_pass=12 before_pass=10` EXIT 0, control 10/10 EXIT 1, r87 regression 12/0/0 EXIT 0:
  **reproduced**.
- C2 SOURCE quote, 18 words, tag-stripped offset 82360: **verified** (method named in §1).
- C2 STATED LIMITS (i)–(v): **verified** as stated; (ii)'s elided-middle collision and the 202-byte window were
  re-measured.

## 7. What I could NOT check

- The L1's `census/round-90/records/c1-after.txt` in the working tree was **truncated** at measurement
  (3690 bytes, ending mid-run at `m8`): it is an in-progress after receipt, not a complete run. My fresh full run
  is `receipts/c1-after-fresh.txt` (63 lines, byte-identical to `records/prefreeze-c1-both.txt`). The L1 must
  commit a complete `records/c1-after.txt` of its own; the truncated file would otherwise be a false receipt.
- The broad-repair variant (C2.4) was not run through the r87 K4 regression; the minimal filed tool was (12/0/0).
- The r83–r88 population pins were not re-derived (only printed by the battery); the claim's target scores only
  r89,r90.
- Host tool versions, `git` version, and the r77 ledger's provenance beyond the id checks were not re-audited
  (outside this seat's four attack items).

## 8. Smallest safe corrections (recommendations, not edits)

1. C1: print `# battery path=… sha256=…` in `c1-clause-battery.py` so the after receipt binds the instrument it
   names (closes C1.6; one line, no behavior change).
2. C2: add one case or one conjunct that asserts `_one_line` is absent from the tool copy (closes C2.3; the
   claim's operability half then has a measured target instead of a separate grep).
3. C2: in the report, quote `before_pass=10` together with the CASE attribution sentence of §4 (no instrument
   change; prevents the "two cases repaired" misreading).
4. Both: the after receipts should carry the fixture/battery hashes in a `# … sha256=` line the report cites;
   fixture- and battery-forgery cheats (C1.6, C2.7) then fail without an external pin.

## 9. Scratch, tools, isolation

Scratch root `/fast/scratch/hyaku/souji-r90/S90Critic/` (clones/fixtures/work dirs only; never `/tmp`).
Receipts and variant tools were copied to `.ufo/waves/round-90/w1/S90Critic/` and the scratch root was **deleted
before yield** (`rm -rf /fast/scratch/hyaku/souji-r90/S90Critic`; verified gone) — nothing is left behind.
No git/jj mutation in the lane or the fleet root; fixture clones were built by the lane's own harnesses under
`--work`. No tool installs, no pacman, no sudo, no host changes. Lane `census/`, `corpus/`, `tools/`, `tests/`
read-only; no sibling-lane or fleet files edited.
