# R93Connector — cross-claim / cross-lane pattern scan + planning data-walk

Seat: R93Connector (leaf, no subagent dispatch). Lane repo `/home/vgpnk/Projects/shokunin/souji-shokunin`,
read-only except this file and `.ufo/waves/round-93/w1/R93Connector/`. Scratch
`/fast/scratch/hyaku/souji-r93/R93Connector/` (deleted at exit; receipts copied here). No tool installs, no
git/jj mutation, no fleet-root writes.

Round contract read first: `census/round-93/preregistration.txt`. Lane base `91c9bcb1`, P1 `2c82d362`, P2
`0d6442cc`, F `9a4ab88f`, A `7bdb96b7`.

---

## 1. Sibling overlap verdict — NO sibling owns any of the three surfaces

Scanned every sibling lane under `/home/vgpnk/Projects/shokunin/*-shokunin/` (read-only): audio, chousa,
game-dev-2d, game-dev-3d, kagi, kaidoku, kake, kama, kasegi, kengaku, kotoba, kotodama, kumitate, lore, mado,
mori, revenger, tabi, tameshi, tsukuroi.

**(a) A WHATWG Encoding Standard source.** One sibling holds such a row, and its scope is not this surface.

| sibling | path | what it covers | why it is not this surface |
|---|---|---|---|
| kake | `kake-shokunin/corpus/SOURCES.md:98` (row S090) | WHATWG Encoding Standard, §4.2 *Names and labels* + §6.1 *Legacy hooks*; label trimming, ASCII case-insensitivity, BOM override | the row's own scope cell excludes the decoder: "not HTTP charset-header precedence or an implementation-specific subset of supported encodings". §8.1.1 is not cited |
| kake | `kake-shokunin/.ufo/waves/round-36/sources/S090.txt` | the full page capture (contains §8.1.1 text) | capture text, not a mined row; no instrument reads it for a decoder |
| kama | `.ufo/waves/round-23/falsify/advice/RowC08CrOnly.md` | incidental mention | no source row, no decoder |
| tabi | `.ufo/waves/round-19/w1/SrcWhatwgConstraints.md` | WHATWG constraints (URL/infra lineage) | not the Encoding Standard |

`grep -rn '8\.1\.1' --include=SOURCES.md` across the fleet returns **zero** sibling hits; `grep -rln
'utf-8-decoder|UTF-8 decoder algorithm'` returns only kake's S090 capture. **S356 is souji's; no sibling row
supersedes or duplicates it.**

**(b) A reference UTF-8 decoder in a test.** None. Fleet-wide `grep -rln 'lower boundary|upper boundary'
--include=*.py` returns four files: `mado-shokunin/.ufo/waves/round-44/w1/ExecC1ExtraMutants/write_survivors.py`
(json bounds, unrelated), and three souji r93 files (`tests/fixtures/r93-k4-flagfail.py`,
`.ufo/waves/round-93/build-spec.py`, `.ufo/waves/round-93/w1/R93ScoutSources/s356_check.py`). No sibling test
implements a WHATWG-decoder-derived reference cut.

**(c) A ledger-edit mutation row.** None. `grep -rn 'ledger-drop|ledger-trim|ledger-resolve'` fleet-wide outside
souji → one unrelated hit (kotodama `reports/round-28/audit/x57-lessons-audit.py:696`, a defect *kind* name
`ledger-dropped-from-acceptance-surface`). The near-miss strings `len(r) < 3` in
`kaidoku-shokunin/.ufo/waves/round-18/tools/routed-defects.py:762` and
`kengaku-shokunin/plans/round97_gate_selftest_census.py:135` are incidental TSV-shape checks in unrelated
scripts, not a counter-under-test guarded by a mutation row. No sibling carries a copy of
`c1-false-rows*`/`c1-pointer-counter.py` (`grep -rln` outside souji → empty).

Verdict: **no overlap; no cross-lane duplication to reconcile.** r93's surface (WHATWG §8.1.1 as a *source*,
a decoder-derived reference cut as a *fixture*, a ledger-row edit as a *mutation row type*) is souji-only.

---

## 2. Cross-claim pattern: C1 and C2 are one failure, measured on two sides

Both claims are the same sentence about the instrument, not about the subject:

> **the instrument's inputs never exercise the distinguishing condition** — so a whole family of wrong
> implementations is scored as right.

- **C1** is the *input-reach* side: the population contains no run that reaches the clause, so an edit to that
  clause cannot change any observed output (`census/round-92/preregistration.txt:31-40` — "no r91 row asserts the
  counter's exit code 0 on a successful run"; `census/round-92/preregistration.txt:55-56` — 77 survivors unbound).
- **C2** is the *assertion-strength* side: the inputs reach the code, but the predicate is a property weaker than
  equality, so a family of wrong outputs is accepted (`tests/fixtures/r92-k4-flagfail.py:348`:
  `full.startswith(head) and full.endswith(tail)`).

The r93 fix is asymmetric and correct in direction: C1 adds **inputs that reach the clause** (LD5/LD6,
`census/round-93/c1-false-rows.tsv:69-70`); C2 adds **equality against an independent reference**
(`tests/fixtures/r93-k4-flagfail.py:367,435-446` KFF19; `:451` KFF20). Neither fix widens the claim.

### Other lane instruments with the same shape

| # | path | the check | the family it cannot see |
|---|---|---|---|
| 1 | `tests/fixtures/r92-k4-flagfail.py:348` | head is *some* prefix, tail *some* suffix | every cut-position error: `surrogatepass` (F5), `len(...) >= 1` (F6), head cut moved forward (F7) — 20/20 pass (`census/round-92/preregistration.txt:72-80`; `.ufo/waves/round-92/w1/R92MutC2.md`) |
| 2 | `census/round-92/c1-false-rows.tsv` (64 rows) | no row reaches `resolved == len(pop)`; no row reaches the `len(r) < 3` guard with a 3-column row | `h-ok-admits-one` and `a491c22-<-to-<=` (`census/round-92/records/c1-residual-survivors.json`; `census/round-92/preregistration.txt:31-40`) |
| 3 | `census/round-90/preregistration.txt:19-25` | the r89 set's sole survivor `len(r) < 3` (dropped by `m17c-no-malformed`) | no r89 population row had exactly 2 columns — same unreached-clause family, bound only in r90 by LD2b |
| 4 | `census/round-91/preregistration.txt:22-30` | six edits (`ld1c`, `ld1d`, `nf6i2`, `nf6j`, `s1-exact-width`, `s3-equal-two`) survived *every* pinned population | duplicate-key variants, last-occurrence, path-char narrowing, exact-width and 2-column guards — five rows added before any could be called bound |
| 5 | `census/round-91/preregistration.txt:109-110` | `c2-variant-probe.py --fixture r90` → `detected=0` | the r90 fixture cannot see *any* of the three r91 variants — a whole family by construction, recorded as a do-nothing control |
| 6 | `plans/round-82.md:43` and `:127`; `census/round-83/c2-tree-walk-counter.py:8` | a monitor branch keyed on `rid.startswith("m-")` | the branch is **dead for this population**: no row id begins `m-`, so the monitor leg can never fire (r82 A7; retired in r83) |
| 7 | `census/round-88/preregistration.txt:76` | `_capture_ok`'s `bool(want)` and `len(want) <= len(have)` arms | measured as **belts, not rows** — the lane's own words: "a dead clause is not a certified one" |
| 8 | `census/round-92/preregistration.txt:43` | the r84–r92 kill rule: "a kill is a non-zero harness exit" | a *crash* is scored as a kill, so any mutant that raises anywhere is "killed" for the wrong reason (`corpus/lessons/round-92-verifier-spotcheck.md:61`) |

Instances 1–5 are input/predicate gaps; 6–8 are gaps in the *scoring* rule. r93 closes 1, 2 and 8 (its kill rule
now requires exit 1 **and** at least one `ROW ... match=no`, `census/round-93/preregistration.txt` KILL RULE).

### The shape survives inside r93, narrowed — LD5's clause is described but not asserted

`census/round-93/c1-false-rows.tsv:69` states the run's consequence ("P04 is UNRESOLVED and the other 34 items
resolve, no id is unknown"), but the harness matches only that one item's line and the exit code:

```
census/round-93/c1-false-row-harness.py:462  m = re.search(rf"^ITEM {re.escape(item)} \S+ status=(\S+)", out, re.M)
census/round-93/c1-false-row-harness.py:469  ok = got == exp_got and (exp_rc == "-" or p.returncode == int(exp_rc))
```

So a mutant that turns **every** item `UNRESOLVED` whenever P04's row is missing still passes LD5 (P04 is
`UNRESOLVED`, exit is 1). This is a **limit on discriminating power, not a false statement**: the prereg says LD5
"asserts UNRESOLVED, exit 1", which is exactly what it does; the "exactly one / no id unknown" half is a
description of the pristine run. **I measured that description and it holds** — see §5. The residual is a
same-shape gap, of exactly the kind this round exists to name, and it belongs in the r94 plan (§3).

---

## 3. Planning data-walk (the L1 planner seat's delegated item)

### 3a. `corpus/lessons/round-92-verifier-spotcheck.md` §7, routed items 1–5

| # | routed item | mark | r93 file that answers it |
|---|---|---|---|
| 1 | C2 maximality case: a row that turns surrogatepass / multi-character span / forward-head forgeries red | **answered** | `tests/fixtures/r93-k4-flagfail.py` KFF19 (exact equality against an independent reference cut, `:367,435-446`) + KFF20 (`:451`); forgery probe `census/round-93/c2-forgery-probe.py` rejects F5/F6/F7 (`census/round-93/records/c2-forgery-after.txt`) |
| 2 | C1 E1 binding row: a ledger-resolve run with exactly one unresolved item asserting rc 1; classify or bind the 77 residual survivors and name equivalent mutants | **partly** | LD5 (`census/round-93/c1-false-rows.tsv:69`) binds the E1 *shape*. The residual set is run but only **reported, not claimed** (`census/round-93/c1-residual-plus-e1.json`, 78 ids, on both populations — prereg "REPORTED, NOT CLAIMED"; no receipt under `census/round-93/records/` at my read). Equivalent-mutant naming and binding: **carried** |
| 3 | Survivor-search robustness (R92Sentinel M1/L1/L2): cleanup on SIGKILL/SIGINT, bare-`/tmp` guard | **partly** | SIGINT/SIGTERM handler + `killpg` + per-mutant `rmtree` + `try/finally`: `census/round-93/c1-survivor-search.py:10-11,100-144,190-192`; the `--work`/`--emit` `/tmp`, `/var/tmp`, `/dev/shm` guard: `:164-168`. **SIGKILL is unhandleable**; the mitigation is fail-closed — a non-empty `--work` is refused (`:170-172`), so a killed run's tree must be removed by hand. The prereg text says "SIGINT/SIGTERM", so the claim is accurate; the *routed item* asked for "on kill" and that half is not achievable and is not documented as a limit |
| 4 | SOURCES rule 2: no silent in-place edit of non-mutable cells | **answered** | §4 below: r93's whole `SOURCES.md` delta is one added S356 row, zero removed lines |
| 5 | Seat write scope (M5): wave artifacts under the lane, never the fleet root | **partly (mid-wave)** | `find /home/vgpnk/Projects/shokunin -maxdepth 1 -name 'R93*'` → empty at my check; the L1 must re-run it at closure (the wave was still running) |

### 3b. `SCORECARD.md` `### Planned (r93)` (lines 2267–2279), item by item

| planned item | mark | evidence |
|---|---|---|
| classify or bind the 77 residual survivors, name equivalent mutants | **carried** | run on both populations, reported only (prereg "REPORTED, NOT CLAIMED"); no classification |
| bind the forge return (limit ii) through a separate exit-expectation channel, not a row | **carried (explicitly)** | prereg STATED LIMITS (ii): "The forge path's return (counter lines 553-574) stays unbound … LD5/LD6 run without `--forge`" |
| make exit polarity a required field of resolving rows | **answered for new rows** | LD5 carries `exp_rc=1`, LD6 `exp_rc=0` (`census/round-93/c1-false-rows.tsv:69-70`); the harness honours `exp_rc` for every row type (`:469,510,531,551`) |
| search robustness: try/finally on kill, SIGINT cancel, bare-`/tmp` guard | **answered (see routed item 3 for the KILL gap)** | `census/round-93/c1-survivor-search.py:10-11,100-144,164-168,190-192` |
| C2 maximality case so a cut that moves too far goes red | **answered** | KFF19 exact |
| an ill-formed lead before the HEAD cut | **answered** | KFF20, overlong `E0 80 80` across the head cut (`tests/fixtures/r93-k4-flagfail.py:451`) |
| retire or re-point the r91 variant tools | **carried** | `census/round-91/variants/{keep-helper,double-backslash,raw-newline}-tool.py` still last touched at `7fb865d8` (r91); unused by r93 |
| Carried list (p2 basename granularity, p3 punctuation lookahead, p7 `_regular` symlink leg, p8 `token_ok` hyphen marker, `fleet:` symlink leg, battery `--only`/`--expect-killed` stale defaults, r85/r86 C2 list, `_regular` pathspec framing, quarantine intro-blob digest row, r79 gate re-measurement, check-4 300 s backstop, r76 K03/K04, r17 240 s runners, r85–r87 K4 counters' print-only `rc=`) | **carried, unmoved** | no r93 artifact names any of them |

### 3c. Draft `### Planned (r94)` (for the L1 to paste or edit)

```markdown
### Planned (r94)

- C1 (calibration): bind the two clauses rather than two spellings (limit i) — a second edit family on the same
  rules (success test `!=`, `>`, `len(pop) - 2`; width guard `len(r) == 3`, `len(r) < 2`) scored with the r93 kill
  rule on the r93 population; classify the 78-id residual set (`census/round-93/c1-residual-plus-e1.json`) into
  bound / equivalent / genuinely clause-free and name the equivalents; assert LD5's descriptive half — read
  `unresolved=` / `errors=` off the counter's `SUMMARY` line, so a mutant that turns every item UNRESOLVED fails
  (today only `ITEM P04` is matched, `census/round-93/c1-false-row-harness.py:462,469`); bind the forge return
  (limit ii) through a separate exit-expectation channel, not a row; state the SIGKILL limit and give the operator
  a documented stale-tree sweep (a killed run refuses a non-empty `--work` by design,
  `census/round-93/c1-survivor-search.py:170-172`).
- C2 (operability/coverage): KFF19 is one payload length (230) and a 33-token pairwise sweep (limit i) — add a
  second length class and an off-boundary filler; defeat the per-payload hardcode route (limit iii) with a payload
  generated at run time from the same reference; extend KFF20's mirror to `ED A0 80` and `F4 90` leads; re-point or
  retire the three r91 variant tools (`census/round-91/variants/*.py`), still the obvious before-arms and still
  unowned.
- Carried (unmoved by r93): p2 basename granularity, p3 the punctuation lookahead, p7 `_regular`'s symlink leg,
  p8 `token_ok`'s hyphen marker, the `fleet:` symlink leg, the battery `--only`/`--expect-killed` stale defaults,
  the r85/r86 C2 list (pid-reuse row, parent-before-child, termign-fork/p5-late-term, strace-robust settle),
  `_regular` pathspec framing, the quarantine intro-blob digest row, the r79 gate re-measurement, check-4 300 s
  backstop, r76 K03/K04, the r17 240 s runners, the r85-r87 K4 counters' print-only `rc=`.
```

---

## 4. Routed item 4 — SOURCES rule 2 (`CORPUS.md:116`)

Rule as written: *"Append-only. Only `status`, `recheck` and `used-by` change in place, and each change is logged
old→new in the round lesson. A correction is a new row whose `teaches` opens `supersedes S0NN —`."*

Check: `git diff 91c9bcb1041b18be154ca466ac3c047ac7862fe1 -- corpus/SOURCES.md`

```
--numstat              1  0  corpus/SOURCES.md
removed lines            0        (grep -c '^-[^-]')
added S-rows             1        (+| S356)
row count  base 277 -> now 278
```

- **No non-mutable cell of any existing row was edited: 0 deletions, 0 renumbered rows.** The entire delta is
  the r93 S356 row.
- Placement: S356 sits immediately after S355 (the previous newest), i.e. the same shape r92 used for S355
  (`git show e5059168 -- corpus/SOURCES.md` is likewise one `+` line, no `-` line). No existing row's position
  changed.
- r92's note 1(a) (S355's `anchor` cell corrected in place at `e5059168 → d64c0260`) has **no r93 counterpart**:
  r93 has not edited any existing cell, before or after filing.
- **Verdict: compliant.** The only in-place change r93 could still make (a same-round correction of a cell of its
  own new row) would need the old→new log the rule demands; none was made.

---

## 5. Reproducer: LD5/LD6's stated consequence, measured on the pristine counter

The harness's own assertion is narrow (§2). I measured the *description* directly, without a clone: the counter
reads the lane's git objects, so dropping the row needs no fixture tree.

Scratch: `/fast/scratch/hyaku/souji-r93/R93Connector/`. Ledgers derived exactly as the harness derives them
(`census/round-93/c1-false-row-harness.py:439-462`): copy `census/round-77/c2-pointer-ledger.tsv`, find the single
row whose first column is `P04` (index 4, 4 columns:
`P04	MOVED	census/round-32/waves/a2w1/SwarmExecutor08.md	r32 wave capture, byte-equal`), then delete it
(LD5) or truncate it to three columns (LD6).

```
python3 -B census/round-87/c1-pointer-counter.py --root . \
  --rev e65538e73c7f1a8f7570bc24a2215da8a90043f3 --fleet-root /home/vgpnk/Projects/shokunin \
  --population $PWD/census/round-77/c2-population.tsv --ledger <ledger>
```

| arm | rc | ITEM lines | UNRESOLVED | SUMMARY |
|---|---|---|---|---|
| pristine (`census/round-77/c2-pointer-ledger.tsv`) | 0 | 35 | 0 | `items=35 resolved=35 unresolved=0 refused=0 mismatched=0 errors=0` |
| LD5 (`ledger-drop.tsv`) | **1** | 35 | **1** (`ITEM P04 SCORECARD.md:598 status=UNRESOLVED`) | `items=35 resolved=34 unresolved=1 refused=0 mismatched=0 errors=0` |
| LD6 (`ledger-trim.tsv`) | **0** | 35 | 0 | `items=35 resolved=35 unresolved=0 refused=0 mismatched=0 errors=0`; `ITEM P04 … status=MOVED` |

Receipts: `.ufo/waves/round-93/w1/R93Connector/{pristine,drop,trim}.txt`. Both stated consequences hold:
**exactly one** item unresolved under the drop (34 resolve, no id unknown), and P04 MOVED with exit 0 under the
trim. The rows' assertions are therefore true, and LD5/LD6 do bind the two named edits by the mechanism the claim
states.

Population consistency datum (reviewer's stated limit iv, cheap to confirm): the r93 population is the r92 file
byte-identical as a prefix (`cmp -n <size r92>` → equal), 66 non-comment rows, sha256
`d6439f65a632cf83fb9d47c78bd0d32d1f9104d2f6443bdfd770e1c1c5e1a88e` — matches the prereg.

---

## 6. Falsification ledger entry

**NO-FALSIFICATION.**

What I tried, and what it returned:

- *C1 wording* — "exactly one item is UNRESOLVED and no id is unknown", "LD5 … asserts UNRESOLVED, exit 1",
  "LD6 … asserts MOVED, exit 0", population 66 rows / sha256: all re-derived in §5; all hold.
- *C1 wording* — "no r92 run reaches their clause": the r92 population has no exit-0-on-success row and no
  3-column row; the r93 rows add exactly those two reaches (rows read at `census/round-93/c1-false-rows.tsv:69-70`).
  Consistent.
- *C2 wording* — "the r92 fixture checks that the excerpt's head is SOME prefix and its tail SOME suffix":
  literal, `tests/fixtures/r92-k4-flagfail.py:348`. KFF19's exactness is real (`:435-446` compares against the
  reference-cut cell, not a prefix/suffix property). Consistent.
- *C2 wording* — "22 cases": case table at `tests/fixtures/r93-k4-flagfail.py:483-484` plus the KFF1-KFF18 block;
  no contradiction found.
- *SOURCES rule 2* — no in-place edit (§4).

The one thing I found that a reader could mistake for a falsification is the harness's narrow match (§2/§3c):
LD5's "exactly one / no id unknown" is **not asserted by the instrument**. It is a limit of discriminating power,
not a false sentence, and I measured the described behaviour instead (§5). It is routed to the r94 draft rather
than raised as an amendment.

---

## 7. Reports / hand-off

- Seat artifacts: this file; receipts `pristine.txt`, `drop.txt`, `trim.txt` under
  `.ufo/waves/round-93/w1/R93Connector/`.
- Nothing under `/home/vgpnk/Projects/shokunin/` (fleet root), `.scratch/`, `MANIFEST.json`, `.ufo/state/*`.
- Scratch `/fast/scratch/hyaku/souji-r93/R93Connector/` removed before yield; peak size < 1 MB (text only, no
  clone).
- For the L1: §1 overlap verdict can be pasted into the report as "no sibling owns the surface"; §3c is the r94
  draft; §4 is the rule-2 answer; §5 is an independent, clone-free re-derivation of the LD5/LD6 consequence that a
  reviewer can re-run in under a second.
