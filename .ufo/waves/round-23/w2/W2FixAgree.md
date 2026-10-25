# W2FixAgree — attack on `tests/fixtures/r23-record-agreement.py` (round 23, w2, C1)

Seat: L1Souji23.W2FixAgree (mutation-tester, leaf). Mode: READ-ONLY; every write below went to
`/var/tmp/souji-r23-w2-FixAgree/` (removed before this report was written). Lane bytes were not
modified: digests re-checked after all probing, identical to the pre-probe values.

Pinned bytes (measured, not quoted from another seat):

```
$ sha256sum tests/fixtures/r23-record-agreement.py tools/souji-record-agreement.py
3b1bc5e6236af638621e51d6bf0dbc4f1d1f35080901c6aedee611802aa66537  tests/fixtures/r23-record-agreement.py   (501 lines)
617f4c9618c06254c0fd9503d76f681e56452bfff7fa3888009737ddfcdfa8c9  tools/souji-record-agreement.py          (350 lines)
```

The instrument digest is the one `MutCounter.md` pins, so its clause list is scored against the
bytes that actually landed.

---

## 1. The claim's own counting command, re-run

```
$ python3 tests/fixtures/r23-record-agreement.py
tool_sha256=617f4c9618c06254c0fd9503d76f681e56452bfff7fa3888009737ddfcdfa8c9
case=1 expect=rc=0 mismatches=0 keys=4 json-bound got=rc=0 mismatches=0 keys=4
case=2 expect=rc!=0 K1 receipt-absent>=1 got=rc=1 mismatches=1 keys=4 [K1/receipt-absent]
case=3 expect=rc!=0 K1 value-disagree>=1 rev-disagree=0 got=rc=1 mismatches=1 keys=4 [K1/value-disagree]
case=4 expect=rc!=0 K1 rev-disagree>=1 got=rc=1 mismatches=2 keys=4 [K1/occurrence-absent,K1/rev-disagree]
case=5 expect=rc!=0 K2 uncorrected*>=1 got=rc=1 mismatches=3 keys=4 [K2/uncorrected]
case=6 expect=rc!=0 K2 filed*>=1 got=rc=1 mismatches=4 keys=4 [K2/filed-occurrence-missing]
case=7 expect=rc!=0 K3 tally-disagree>=1 got=rc=1 mismatches=1 keys=4 [K3/tally-disagree]
case=8 expect=rc!=0 K4 uncommitted-path naming the stray round path got=rc=1 mismatches=1 keys=4 [K4/uncommitted-path]
case=9 expect=K4 rows=0 (exempted operator path is not a mismatch) got=rc=0 mismatches=0 keys=4
selftest=9/9
control=FALSE-GREEN-REJECTED
EXIT=0
```

The fixture creates and removes its own hard-coded `/var/tmp/souji-r23-ExecFixtureAgreement`
(`ls` after the run: absent). Every probe below ran a *copy* whose only fixture delta is
`SCRATCH_ROOT` (diffed against the landed file, `FIXTURE-COPY-IDENTICAL-BUT-SCRATCH-ROOT`), and a
copy of the instrument at the pinned digest.

The predicate itself, run on the lane's own bytes (this is the only thing C1 asserts):

```
$ python3 tools/souji-record-agreement.py --rev $(git rev-parse HEAD) --root .../souji-shokunin
MISMATCH	K4	.ufo/waves/round-23/report-draft.md	uncommitted-path	??
keys=4 records=4 occurrences=17 mismatches=1
EXIT=1
```

Base control (`census/round-23/records/agreement-control-base.txt`, which is the file that exists;
the prereg names `agreement-control-base.tsv`, absent): `mismatches=6`, `occurrences=13`,
`--no-worktree`. So the control arm is sound (>=1) and K1-K3 are green at the tip; K4 is not.

---

## 2. The three clauses the nine cases do not kill

Mutant = one-line removal of the clause in the instrument copy; detector = the whole fixture.
`selftest=9/9` on a mutant means the clause is untested by every case.

| # | clause | file:line | mutant | output | verdict |
|---|---|---|---|---|---|
| C-a | K2 **tally** staleness arm | `tools/souji-record-agreement.py:233` | `if n != want_tally.get(cls, 0):` → `if False:` | `selftest=9/9` | **survives** |
| C-b | K4 exemption leg — source + allowlist | `tools/souji-record-agreement.py:57`, `:288-291` | delete `if path not in K4_ALLOWED: … continue` | `selftest=9/9` | **survives** |
| C-c | K3 per-class occurrence presence | `tools/souji-record-agreement.py:272` | delete `missing = sorted(...)` + `class-absent` | `selftest=9/9` | **survives** |

### C-a — K2 tally staleness (`:233`): CONFIRMED uncovered, and it is the live arm

Case 5 (`uncorrected-log`, fixture `:289-292`) strips *every* `superseded by` line, so all three
stale scalars fire (`mismatches=3`). But `case_k2` (`fixture:352-354`) asserts only
`any(cls.startswith("uncorrected")) and rc != 0` — the 4-tuple arm still fires on its own, so the
tally arm can be deleted with no observable change. Probe: `selftest=9/9`.

This matters because the base control's six mismatches split 1 (K1) + 3 (K2) + 2 (K3), and two of
the three K2 rows are the tally arm (`LOG.md:1495 '1 present'`, `'1 refused'`). Deleting `:233`
halves K2's live signal and the fixture stays green. `MutCounter` M24 predicted exactly this.

### C-b — K4 exemption leg (`:57`, `:288-291`): CONFIRMED uncovered, and stronger than `MutCounter` said

Not merely untested — **unreachable by construction**. Two independent facts:

1. The fixture writes the exemption file at the *preregistration's* path with the frozen
   `uncommitted:` prefix (`fixture:68` `K4_EXEMPT = "corpus/pointer-exemptions.tsv"`,
   `fixture:191-196`). The instrument reads `census/round-23/records/uncommitted-exemptions.tsv`
   (`tool:57`). The tool never opens the file the fixture writes.
2. Case 9's defect is a no-op: `fixture:306-307` — `if variant == "exempted-dirty": return`.
   `build()` already committed every payload file (`fixture:329-338`), so case 9's repo has a
   **clean** worktree. `case_k4_exempt` (`fixture:367-369`) therefore asserts "no K4 rows" on a
   tree that has nothing for K4 to report, exemption or not.

Decisive probe (fixture-side, not a tool mutant): strip *all* exemption rows from `f_exemptions()`
so the file holds only its comment line — the tool then has nothing to allow —

```
=== probe=fx9 tool_sha256=617f4c9618c06254   (instrument bytes unchanged)
selftest=9/9
control=FALSE-GREEN-REJECTED
```

`selftest=9/9` with the exemption mechanism entirely removed. Case 9 is a second copy of case 1.
Consequence: `K4_ALLOWED` — the round's counter to "declare a giant exemption list" — and the
tab-split, directory-match, blank/comment-skip and empty-path clauses have no witness at all.

### C-c — K3 class-absent (`:272`): CONFIRMED uncovered

No case removes every occurrence of a class from `corpus/README.md` or `corpus/lessons/round-22.md`;
all three K3 payloads (`fixture:172-190`) carry all four classes. Probe: `selftest=9/9`. A record
that silently drops `refused` (or any class) still reports `mismatches=0`.

---

## 3. Further survivors found while confirming (same method, same 9/9)

| clause | file:line | mutant | output | note |
|---|---|---|---|---|
| K2 receipt selection | `tool:50` | `-before-final.tsv` → `-before.tsv` (the prereg's name) | `selftest=9/9` | see F4 |
| K2 paragraph grouping | `tool:221` | `paragraphs(...)` → per-physical-line tuples | `selftest=9/9` | M15: the fixture *does* wrap the filed tuple (`fixture:206-207`) but no assertion pins it |
| K2 correction window | `tool:238` | `lines[k:k+6]` → `lines[k:k+1]` | `selftest=9/9` | M14: fixture corrections are single-line, so width is untested |
| K3 tally regex tolerance | `tool:63` | drop `\*{0,2}` and `\s+`→` ` | `selftest=9/9` | M44: no fixture tally is bold or tab-separated |

## 4. `MutCounter.md` claims this run refutes or corrects

- **M02 (case 2 must assert the class string) — REFUTED, it is now killed.** `fixture:341-345`
  pins `cls` exactly, and case 2 passes `"receipt-absent"`. Probe (downgrade `receipt-absent` to
  `receipt-malformed` via `or ""`): `case=2 … got=rc=1 mismatches=1 keys=4
  [K1/receipt-malformed] -> FAIL`, `selftest=8/9`.
- **M52 (filed-occurrence join) — CONFIRMED killed.** `" ".join` → `"\n".join` at `tool:245`:
  `case=1 … [K2/filed-occurrence-missing] -> FAIL`, `selftest=8/9`.
- **M38 (exit code always-zero) — CONFIRMED killed, and the control is real.** `return 0`:
  `selftest=2/9`, `control=NOT-REJECTED`. So `control=FALSE-GREEN-REJECTED` is a genuine signal,
  not decoration. `MutCounter`'s "conditional" reading is wrong: `run_tool` records `returncode`
  (`fixture:311`) and every case asserts `rc`.
- **M15/M14 — CONFIRMED uncovered, `MutCounter`'s `killed-by-case` verdict is wrong.** It called
  them conditional on the fixture wrapping the tuple; the fixture wraps it on purpose
  (`fixture:206-207`) and still does not kill either, because case 5 asserts a class prefix rather
  than a count and case 1's corrections are single-line.
- **M51 / A12 — REFUTED: the clause does not exist in the landed bytes.** `MutCounter` says the
  instrument "now carries" `receipt-unbound` at `:148-150`. Measured at the digest it pins:

  ```
  $ grep -n 'receipt-unbound\|tool_sha256\|RECEIPT_TOOL' tools/souji-record-agreement.py
  ABSENT
  ```

  There is no tool-digest binding in K1. The "receipt the author writes by hand" attack that
  `CritC1Gameable` raised is open in shipped bytes, and `A12`'s "two strongest anti-gaming guards"
  is false for one of the two — the guard was lost in the final edit (`66ee7ecf` → `617f4c96`, both
  350 lines) while the anchor map carried the old line numbers forward. `selftest=9/9` cannot
  notice, because a clause that is not in the tool cannot be killed.

---

## 5. Findings the round must act on

- **F1 — fix.** `tools/souji-record-agreement.py:233`: add fixture case 5b, a stale `<n> <class>`
  tally inside the `Round22 attempt2` section with no `superseded by` line, asserting the *count*
  of `uncorrected` rows (not just the prefix).
- **F2 — fix.** `tests/fixtures/r23-record-agreement.py:68` + `:306-307`: write the exemption file
  the instrument reads (`census/round-23/records/uncommitted-exemptions.tsv`), make
  `exempted-dirty` actually dirty a path *under* `census/operator-sweep-20261019/`, and add a case
  whose exemption row names a non-operator path that is then dirtied — that is the only input that
  kills `:288-291`. Until then case 9 witnesses nothing (proved: `fx9`, 9/9 with no exemptions).
- **F3 — fix.** `tools/souji-record-agreement.py:272`: add a case removing every `refused`
  occurrence from both K3 records.
- **F4 — disclose.** `fixture:70` and `:235-236` write `declared-evidence-before.tsv` and
  `…-before-final.tsv` from the *same* `f_receipt_before()`, so receipt selection is unobservable
  (`selftest=9/9` when the tool is pointed at the prereg's name). Live bytes disagree
  (plain `56/53`, `-final` `55/52`) and `MutCounter` A5 is still undeclared: prereg K2 names the
  plain file, `tool:50` reads `-final`. Either declare the pre-data contract change in the round
  record or write the divergent shapes into the fixture.
- **F5 — fix or disclose.** No K1 tool-digest binding exists in `tools/souji-record-agreement.py`
  (§4, M51). Restore the guard, or state in the round record that C1's counter does not bind the
  receipt to a tool digest.
- **F6 — disclose at landing.** The predicate is currently `mismatches=1`
  (`.ufo/waves/round-23/report-draft.md`, untracked since 05:37, not named by
  `census/round-23/records/uncommitted-exemptions.tsv`). C1 may not report `M_after=0` until that
  path is committed or explicitly exempted; the instrument is behaving correctly, the round is not.
- **F7 — disclose.** The base control runs `--no-worktree` and the prereg names
  `agreement-control-base.tsv` while the tree holds `agreement-control-base.txt`. K4 has no
  before-arm at all, so the control clause covers K1-K3 only.

---

## 6. Verdict

**`selftest=9/9` is not an adequate witness for C1's counter predicate.** Falsified on four
independent grounds, each measured:

1. **Scope.** The fixture only ever runs the instrument on nine synthetic repos it builds itself.
   The predicate is `M_after=0` at the round tip and `M_base>=1` at the base revision *on the
   lane's own bytes*. 9/9 says nothing about either end; the tip run in §1 reports `mismatches=1`.
2. **Coverage.** Seven behavior-bearing clauses survive a one-line deletion while the fixture
   stays 9/9 (`:233`, `:288-291` + `:57`, `:272`, `:50`, `:221`, `:238`, `:63`). Two of those —
   the K4 exemption allowlist and the K2 tally arm — are the clauses that make `M=0` mean
   "repaired" rather than "not looked at".
3. **A vacuous case.** Case 9 is a no-op defect (`fixture:306-307`) against a file the tool never
   reads; with the exemption mechanism removed entirely the fixture still prints `selftest=9/9`.
4. **A missing guard.** The receipt→tool-digest binding `MutCounter` reports as shipped is absent
   from the landed bytes, so the counter accepts a hand-written counts line.

What the fixture *does* witness honestly: the instrument is not an always-zero emitter (M38 →
2/9, `control=NOT-REJECTED`), and each of K1-K4 has at least one firing class on a shape the round
cares about (cases 2-8). That is a real but much narrower statement than "C1's predicate holds".
Round action: fix F1-F3 and F5, disclose F4, F6, F7; re-run this fixture and the predicate after
landing.

---

## Restoration / cleanup evidence

```
$ sha256sum tools/souji-record-agreement.py tests/fixtures/r23-record-agreement.py   # after all probes
617f4c9618c06254c0fd9503d76f681e56452bfff7fa3888009737ddfcdfa8c9  tools/souji-record-agreement.py
3b1bc5e6236af638621e51d6bf0dbc4f1d1f35080901c6aedee611802aa66537  tests/fixtures/r23-record-agreement.py
$ git status --porcelain
?? .ufo/waves/round-23/report-draft.md
?? census/operator-sweep-20261019/
```

Both are the pre-existing entries observed before any probe. `/var/tmp/souji-r23-w2-FixAgree/`
removed; the fixture's own `/var/tmp/souji-r23-ExecFixtureAgreement/` self-cleaned on each run.
No installs were needed (pacman paused host-wide; nothing required). Eleven probes total:
m24, m49, m26, m43, m15, m14, m44, fx9 (survive, 9/9); m02 (8/9), m52 (8/9), m38 (2/9,
`control=NOT-REJECTED`) (killed).
