# R94ReviewerC1 — C1 crash-sentinel correctness review

## NO-FALSIFICATION

No artifact produced by this seat falsifies any sentence of the C1 claim or of its predicate. Every
question below was answered against the frozen instrument bytes and against live runs; the predicate
re-derived byte-for-byte as claimed and the three non-crash verdicts held.

## Instruments examined

- Search (r94): `census/round-94/c1-survivor-search.py` (sha256 `97b8defa…`, lines 59–75 sentinel,
  113–123 `verdict()`, 209–218 precondition check, 259–263 summary tally).
- Harness (r93, unchanged): `census/round-93/c1-false-row-harness.py` (sha256 `1868a570…`).
- Counter (r87, unchanged): `census/round-87/c1-pointer-counter.py` (sha256 `fd0a8e24…`).
- Stated limits verified against SOURCES rows S357/S358 and
  `corpus/knowledge/mutant-crash-is-not-a-kill.md` (present).

## Q1 — Does every harness branch that runs the counter print `rc=<counter rc>`?

Verdict: **yes for all four counter-launch branches; rc=70 is visible on every branch.**

The harness has exactly four `subprocess.run([sys.executable, "-B", counter, …])` sites. Each one
prints `rc={p.returncode}` on every ROW line it emits:

| Branch (where) | Launch site | ROW-with-rc line | rc=70 visible? |
|---|---|---|---|
| `ledger-drop` / `ledger-trim` | harness:458–460 | `rc={p.returncode} match=` at 471–472 | yes |
| `ledger` (LD1/LD1b/LD1c/LD2/LD2b/LD3) | harness:499–501 | `rc={p.returncode} match=` at 512–513 | yes |
| `ledger-resolve` (LD4) | harness:519–522 | `rc={p.returncode} match=` at 533–534 | yes |
| forge path (`lane`/`fixture` rows) | harness:540–542 | `rc={p.returncode} match=` at 557–558 | yes |

The precision matters and the search's matcher is exact: `verdict()` (search:117) looks for
`f" rc={CRASH_RC} match="` — i.e. ` rc=70 match=`. Three of the four launch branches can also emit
**`rc=2 match=error`** lines (harness:466–468, 507–509, 527–529, where `p.returncode == 2` is
intercepted as a refused-counter error); those are the ONLY ROW lines that do **not** carry the
counter's true `rc=<n>` verbatim — they hard-code `rc=2`. But a counter killed by the sentinel exits
**70**, not 2, so it never takes the `rc=2 match=error` intercept: it falls through to the normal
`rc={p.returncode} match=` print and shows `rc=70`. A crash on any of the four branches therefore
surfaces as `ROW … rc=70 match=…` and is caught by `verdict()` line 117.

Live proof: the `h-crash-index` run (receipt `h-crash-index-harness.out`) produced exactly ONE
`rc=70` line, on `ROW LD6 where=ledger-trim … rc=70 match=no` (the 3-column-ledger row walks the
mutated `ledger[r[0]] = (r[1], r[2], r[3])[:2]` and `r[3]` raises IndexError). The `h-crash-late`
run (receipt `h-crash-late-harness.out`) produced **66** `rc=70` lines — every one of the 66
population rows — spread across all six `where` values (51 `fixture`, 5 `lane`, 6 `ledger`,
1 `ledger-drop`, 2 `ledger-resolve`, 1 `ledger-trim`), confirming the late-final-`return` crash is
caught no matter which branch fires first. `grep -c " rc=70 "` = 66; per-`where` distribution
quoted above. **No branch hides a counter crash.**

## Q2 — Can a non-crash mutant reach rc=70?

Verdict: **no, for the pinned counter/harness/population. The `rc=70 match=` token is therefore a
unambiguous crash signal; the claimed non-crash verdicts reconcile.**

- Counter `git()` (counter:162–167): every `git` call with the default `check=True` raises a
  `RuntimeError` on non-zero exit. A git that returned 70 would therefore raise — and the exception
  would itself be converted to exit 70 by the sentinel. The `check=False` sites (counter:206, 249,
  282, 508, 537) read stdout/exit status but **never return that rc as the program's exit**: the
  only program-exit sites are `return 2` (fatal), `return 0 if ok else 1` (574), and the
  `sys.exit(main(…))` at 578. No item of `POP_PINS` or of the harness (`BONANZA`-free enumeration:
  harness `return 2`/`return 0 if mism==0 and errs==0 else 1`) returns or propagates 70.
- So a mutant whose counter reaches `rc=70` got there via the `sys.excepthook` sentinel (crash) —
  not via git, not via a forged population. The claim's stated limit (ii) — *“a counter that
  legitimately exits 70 is not distinguished”* — is the only theoretical alias, and the pinned
  counter has no such exit. On these instruments the alias is vacuous.

## Q3 — Is the precondition check equivalent to how the harness starts the counter?

Verdict: **equivalent on the axes that matter (interpreter flags, site machinery, env ordering,
cwd-independence). The harness's cwd and its ENV hygiene do not change the sentinel outcome.**

- Precondition (search:212): `[sys.executable, "-B", "-c", "raise RuntimeError('souji-r94-sentinel-check')"]`
  with `PYTHONPATH = hook + (os.pathsep + existing if existing)` (search:210–211).
- Harness launch (harness:458/499/519/540): `[sys.executable, "-B", counter, "--root", …]`
  with an inherited environment — the search exports `PYTHONPATH=hook:…` into the harness process
  (search:139–144 `score()` `env=`), and the harness passes that environment through (it only
  filters `GIT_*` into its own `ENV` for its own `git()` calls at harness:167–171; the counter
  launches inherit the process environment, not `ENV`).
- Axes compared: interpreter **flags** identical (`-B` only, both sides); **site machinery**
  identical (both start from the same `sys.executable` with site enabled — `-B` does not disable
  site; `PYTHONPATH` ordering is hook-first on both paths); **env values** equal modulo the
  existing `PYTHONPATH` suffix (the check reproduces the exact export the harness inherits);
  **cwd** differs (check runs in the search's cwd; harness launches the counter with `cwd=lane` at
  harness:460/501/522/542) — but a `cwd` does not affect the `sys.excepthook` machinery, and the
  precondition's job is to prove the hook *fires*, not to reproduce the counter's working directory.

## Q4 — Is `errored` counted in S = E + K + V?

Verdict: **yes — the summary total is exactly the sum, with `errored` a disjoint third verdict, and
the run reconciles: `scored=5 errored=2 killed=2 survived=1` and 2 + 2 + 1 = 5.**

- `score()` (search:162) calls `verdict()` only when `state == "scored"`, so `ambiguous`,
  `uncompiled` and `hung` never enter score.
- `verdict()` (search:113–123) returns in order: 70 → `"errored"`; then `rc==0 → "no"`;
  then `rc==1 with a match=no row → "yes"`; else `"errored"`. The three return values are
  disjoint by construction (the 70-check precedes the rc==0/rc==1 arms, and `"errored"` is the
  fallthrough).
- Tally (search:259–263): `errd`, `kill`, `surv` are independent counts over the
  `scored` list; the emitted `SEARCH-SUMMARY` fields `errored=`, `killed=`, `survived=` are these
  counts, and `scored` (search:258) is the denominator. Note the summary's `survived` is
  `len([m for m,v in scored if v=="no"])` — so `errored=2 killed=2 survived=1` does NOT overlap
  `killed=`: `killed` in the summary means `verdict=="yes"` only (crash fixtures are `"errored"`,
  not `"yes"`). 2 + 2 + 1 = 5 = `scored`; there is no double count.

## Q5 — Does the claim sentence say anything the predicate does not check?

Verdict: **no material overreach. The sentence is exactly the four quantities the predicate prints:
the crash-sentinel line, `errored=2 killed=2 survived=1`, the five per-id `killed=` verdicts, and
`EXIT 0`. Two phrasings were scrutinised and both check out.**

- The claim sentence — *“scores both crash fixtures `errored` while keeping the two semantic kills
  killed and the survivor surviving. Counted quantity: crash fixtures the search scores killed —
  before 2, after 0 — with the three non-crash verdicts unchanged.”* — is exactly what the predicate
  output asserts: `SEARCH h-crash-late … killed=errored`, `SEARCH h-crash-index … killed=errored`,
  `killed=yes` for `h-ok-admits-one`/`a491c22-<-to-<=`, `killed=no` for `a127c26-True-to-False`,
  `SEARCH-SUMMARY … errored=2 killed=2 survived=1`, `EXIT 0`. The count *“crash fixtures the search
  scores killed”* moving 2 → 0 is precisely `errored` on those two ids plus `killed=` no longer
  holding them. “Do-not-reach-errored” is guarded by the controls the prereg states (FA `errored=4`),
  which go beyond the bare sentence.
- The parenthetical rule statement (*“a harness exit 70 or any ROW `rc=70` is `errored`”*) matches
  `verdict()` (search:117) verbatim, including *harness exit 70* as an OR-arm. That arm is reachable
  in principle (a crash in the harness itself, which inherits the hook) but the pinned harness has
  no such crash under these targets; it is a stated rule, not a silent extra claim, and the
  predicate verifies the rule's effect through the two ROW-based crashes.
- *“inherited by the harness and the counter it spawns”* is checked by the precondition line
  (`# crash-sentinel rc=70 check=pass`, search:218) and by the live outcome (both crashes reached
  `rc=70` exactly where the sentinel put them). The stated limits (i)–(iii) bound the five-verdict
  scope explicitly; I found no sentence beyond it that the predicate fails to verify.

## Live runs (fresh, this seat)

1. **Predicate (r94 search, all five targets, `--jobs 5`, scratch work dir):**
   `# crash-sentinel rc=70 check=pass`, `SEARCH-SUMMARY generated=5 ambiguous=0 uncompiled=0
   hung=0 scored=5 errored=2 killed=2 survived=1`, `EXIT 0` — identical to the prereg predicate.
   Receipt: `.ufo/waves/round-94/w1/R94ReviewerC1/predicate-r94-search.txt`.
   Tool versions: python3 `-B` with the system interpreter; no installs (per seat note).
2. **Single `h-crash-late`:** `killed=errored rc=1`, `errored=1 killed=0 survived=0`.
   `harness.out`: 66 `rc=70` lines, one per population row, all six `where` values represented.
   Receipts: `single-h-crash-late.txt`, `h-crash-late-harness.out`.
3. **Single `h-crash-index`:** `killed=errored rc=1`, exactly **1** `rc=70` line —
   `ROW LD6 where=ledger-trim … rc=70 match=no` (the 3-column ledger row), the other 65 rows
   `rc=0` (4) / `rc=1` (61). Receipts: `single-h-crash-index.txt`, `h-crash-index-harness.out`.
4. **Three non-crash (`h-ok-admits-one`, `a491c22-<-to-<=`, `a127c26-True-to-False`):**
   `killed=yes`, `killed=yes`, `killed=no`; `errored=0 killed=2 survived=1` — zero `rc=70` on any
   ROW (verified by `grep -o " rc=[0-9]* "` counts: only `rc=0` and `rc=1`).
   Receipt: `noncrash-three.txt`.

## Residual risk (what this seat did not, and could not, run)

- The controls (r93-rule `c1-control-r93-rule.py`, forgeries `c1-forgery-controls.py`) were not
  re-run here (frozen intent and pinned outputs already corroborated in `c1-control-r93-rule.txt`
  in the control commit P2). The single-target runs above corroborate their claims on the
  receipted shard only.
- A full-population re-score was not run (stated as *reported, not claimed* — prereg limit (i)).
- Host pacman state untouched; no tools installed; scratch under
  `/fast/scratch/hyaku/souji-r94/R94ReviewerC1/` created and deleted before yielding; all durable
  receipts in this seat dir.
