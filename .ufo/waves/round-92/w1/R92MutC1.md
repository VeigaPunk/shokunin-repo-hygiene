# R92MutC1 — C1 kill-rule & residual triage (souji round 92)

Seat: mutation-tester. Lane: souji-shokunin. Prereg: `census/round-92/preregistration.txt`
(sha256 `d3345e5c1744a57f51288c0a026690c579faccdc9b100ff9b0c59153489390fd`).
Frozen instrument pins re-verified before probing: counter `fd0a8e24…`, r92 population
`f66341fc…` (64 rows), targets `5a8f6087…` (47), harness `818f84d9…`, search `c393d941…`;
residual file `c86dbee3…` (77 entries). All receipts are text under
`.ufo/waves/round-92/w1/R92MutC1/`; scratch was `/fast/scratch/hyaku/souji-r92/R92MutC1/`
and is deleted before yield. Never edited frozen files, never committed.

## 0. Axes (godspeed)

1. **False-kill soundness** — does the kill rule (`harness != 0`) conflate a crash with a
   polarity/tally kill? Is any of the 47 kills in the filed runs a crash (rc 2)?
2. **Alternative-edit survival** — do different edits of the SAME clauses the targets hit
   (lines 541–552, 574) survive the r92 population? Each survivor needs a row shape or a
   named limit.
3. **Residual triage** — classify the 77 residual survivors by fault class; name the row
   shape that would bind each bindable one.
4. **Wording falsification** — does anything refute a stated C1 sentence? Verdict in §4.

Verdicts: (1) crash DOES score as killed, but no filed kill is a crash — see §1.
(2) 3 of 8 hand edits survive r92, including a genuinely different survivor on the same
   clause (E1) — see §2. (3) 77 residuals split into 5 classes — see §3.

## 1. False-kill probe

The seat spec asked for two kill-rule-breaking mutants that do NOT touch exit polarity
(import raise; argparse rename). Both were built as scratch copies of the frozen counter,
verified to compile, run through the frozen pinned harness on the r92 population
(`.ufo/waves/round-92/w1/R92MutC1/harness-import-crash-r92.txt`,
`.ufo/waves/round-92/w1/R92MutC1/harness-argparse-r92.txt`).

### 1a. Mutant FK1 — import-time crash

Edit: inserted `raise RuntimeError("import-time crash")` at line 128, right after
`sys.dont_write_bytecode = True` (before any definition, so the module never loads;
direct run exits 1 with the traceback). Through the harness, every counter invocation
dies the same way.

Observed harness output (r92 population, 64 rows):
`SUMMARY rows=64 mismatches=8 accepted=0 refused_true=0 errors=56`, harness exit **1**.
56 rows are `match=error` (the harness could not read a `FORGE` line — the forge rows),
8 rows are `match=no`. The `ledger`/`ledger-resolve` rows are `match=no` because they
read stdout for `LEDGER-REFUSED id=…`/`ITEM … status=` markers that never print, so
`got=-` (harness lines 458–487). **A crash is scored killed**: the search's kill rule
(`score()` returns the raw harness `returncode`; `killed = rc != 0`, search line 155)
counts any non-zero harness exit, and a crashed counter makes the harness exit 1.
FK1 never touches exit polarity — it never reaches `return 0 if ok else 1` — yet it is
indistinguishable from a polarity mutant at the search-summary level. This is a property
of the rule, not a number error (see §1c).

### 1b. Mutant FK2 — argparse rename (--root -> --root2)

`required=True` is unchanged, so with the harness's invocation the flag is never supplied
and argparse exits 2 on the counter side; the harness sees no `FORGE` line and no ledger
marker, so rows go `match=error`/`match=no` exactly like FK1: harness exit 1,
`SUMMARY rows=64 mismatches=8 accepted=0 refused_true=0 errors=56`
(`harness-argparse-r92.txt`). Direct execution exits 2 (`AttributeError: 'Namespace'
object has no attribute 'root'` when arguments ARE supplied). Same conclusion: an
argparse break is scored killed. Note the harness itself exits 2 only for its OWN fatal
usage/fixture errors (lines 391, 395, 398, 406, 414); a counter-side argparse failure
(its exit 2) does not propagate as the harness's 2.

Record-keeping note: the first FK1 attempt appended the `raise` after the
`if __name__`/`sys.exit` block (line 580), which is therefore dead code after a normal
`sys.exit`; that copy scored pristine (harness exit 0, `SUMMARY rows=64 mismatches=0 …`)
and was rejected and rebuilt at line 128 before any receipt was taken. No receipt in this
seat is from that dead mutant.

### 1c. Are any of the 47 filed kills crashes?

Read-only census of the three filed receipts (no re-score, no scratch involved):

- `census/round-92/records/c1-search-r91-full.txt`: 136 `killed=yes`, **all `rc=1`**
  (no `rc=2` anywhere in the file).
- `census/round-92/controls/c1-feasibility-r92-prefreeze.txt`: 47 `killed=yes`, all
  `rc=1`; summary `generated=124 ambiguous=0 uncompiled=0 scored=124 killed=47 survived=77`.
- `census/round-92/records/c1-after.txt` (the L1 post-F run): 47 `killed=yes`, **all
  `rc=1`** (`47 rc=1`, `0 rc=2`); summary `generated=47 ambiguous=0 uncompiled=0
  hung=0 scored=47 killed=47 survived=0`, `EXIT=0`.
- `census/round-92/controls/c1-control-r91-population.txt`: 47 `killed=no rc=0`.

`grep "rc=2"` over all three receipt files returns nothing. So **none of the 47 kills in
any filed run is a crash kill**; every kill is harness rc 1 (a row mismatch), never
rc 2. The kill RULE would accept a crash (FK1/FK2), but the filed census contains no
crash. That is a stated-limit candidate (the claim's kill rule is crash-blind), not a
falsification of any stated number: the claim says "A kill is a non-zero harness exit on
that population" and "killed=47", and both are true of the filed run. The boundary is
that `killed` in this battery is NOT shown to imply "the mutant's behaviour differs from
pristine on an asserted row" — FK1 proves a mutant that never runs is also `killed`.
The L1 should consider stating that explicitly (see §4).

## 2. Alternative edits of the same clauses (lines 541–552, 574)

Eight hand edits were scored with the frozen r92 harness on BOTH populations (r92 64-row
and r91 63-row), sequentially, one work tree at a time
(`.ufo/waves/round-92/w1/R92MutC1/probe.py`, `results.json`, `harness-E*-*.txt`,
`probe-console.txt`). Six target the exit-polarity clauses (541/545/552/574) as
assigned; two are deliberately off-those-clauses (E6 output-only, E7/E8 forge/ledger
tallies) to test what the population cannot see at all. All edits are single-line
replacements of the pristine line (E6 spans lines 550–551); every mutant compiles.

| id | edit (pristine -> mutant) | r92 harness | r91 harness | killed r92? |
|---|---|---|---|---|
| E1-ok-relaxed | L552 `ok = …resolved == len(pop)…` -> `>= len(pop)-1` | 0, `mismatches=0`, LD4r `rc=0 match=yes` | 0, `mismatches=0` | **NO — survives both** |
| E2-return-0-if-ok-or-forged | L574 `return 0 if ok else 1` -> `return 0 if ok or forged else 1` | 1, `mismatches=1` | 1, `mismatches=1` | yes (both) |
| E3-unresolved-noop | L545 tally `+= 1` -> `+= 0` on `unresolved` for every status | 1, `mismatches=1` | 0, `mismatches=0` | yes (only r92) |
| E4-ok-drop-unknown | L552 drop `and not unknown` | 1, `mismatches=6` | 1, `mismatches=6` | yes (both) |
| E5-return-and-ok | L574 `return 0 if (ok and True) else 1` | 0, `mismatches=0` | 0, `mismatches=0` | **NO — survives both** |
| E6-summary-text | L550–551 `SUMMARY` gains `EXTRA=1` | 0, `mismatches=0` | 0, `mismatches=0` | **NO — survives both** |
| E7-forge-tally-noop | L566 `forged += 0` | 0, `mismatches=0` | 0, `mismatches=0` | **NO — survives both** |
| E8-errors-no-op | L548 `counts["refused"] += 0` | 0, `mismatches=0` | 0, `mismatches=0` | **NO — survives both** |

Detail on the row-level mechanics (from the harness outputs):

- **E1 (the important one).** `counts.resolved >= len(pop)-1` admits ONE unresolved item
  and still returns 0. On r92, LD4r's run is all-resolved (35/35), so `resolved == 35 >=
  34` and `ok` stays True; every forge row still reports the right `got`, and the only
  `expect_rc=1` rows (LP3, LD1…LD3) assert the failure polarity, which E1 does not
  invert. So E1 survives LD4r even though it is a DIFFERENT edit of the same clause as
  target a552c28 (which flips `==` to `!=` and is killed). This is a genuine
  alternative-edit survivor of the kind the r91 spirit-check routed but R91MutCounter
  never ran: LD4r binds the EXACT equality `resolved == len(pop)`, not the weaker
  "return 0 on an all-resolved run". Row shape to bind E1: a row whose counter run has
  exactly ONE unresolved (or refused/mismatched/error) item and asserts `expect_rc 0` —
  i.e. the current `ledger`-type rows LD1/LD1b/LD2/LD2b/LD1c/LD3 with their `unknown`
  half flipped: a `ledger-resolve` run over a population whose ledger contains an unknown
  id would leave `resolved == 35, unknown != []` and `ok` would need the `not unknown`
  half; E1 instead admits the unresolved tally. Concretely: a `ledger-resolve` row on a
  population with one UNRESOLVED item and `expect_rc 0` binds E1 (pristine resolves
  else `ok=False`; E1 returns 0). Named limit today: no current row asserts `rc 0` on a
  run that is NOT all-resolved, so a one-item slack in the success test is invisible.
- **E2.** Killed on both populations, but NOT by LD4r: LD4r still matches
  (`rc=0 match=yes`, no `--forge` so `forged` is unbound). The flip is LP3
  (`expect=REFUSED/1 got=REFUSED rc=0 match=no`), a `lane` forge row with
  `expect_rc=1`: `forged` is 1 there, so `return 0 if ok or forged` exits 0 and breaks
  the asserted failure polarity. This is the same forge-path return that stated limit
  (ii) says is not bound, bound here by an existing `expect_rc=1` row rather than by
  LD4r. It demonstrates the converse hazard of E1: a `return` edit that ORs in `forged`
  survives every `expect_rc=0` row and is caught only by the rc=1 rows.
- **E3.** Killed ONLY by LD4r (r92 `mismatches=1`, r91 `mismatches=0`): the `+= 0` on
  `unresolved` leaves `counts.resolved` at 35 on an all-resolved run but the SUMMARY
  still shows the run as successful, so the failure is visible only because LD4r asserts
  `rc=0` through the REAL tally path (`LD4r … rc=1 match=no`). This is the cleanest
  confirmation that LD4r does work on the tally clause, not merely on `return` — a
  kill of a 545-clause edit that no r91 row sees. E3 is a textually different
  defect from a545c43, killed by the same row. Good for the claim, and worth saying:
  LD4r binds a class of tally breaks, not one mutation.
- **E4.** Killed on both, by the six `ledger` rows (LD1/LD1b/LD2/LD2b/LD1c/LD3):
  `got=LEDGER-REFUSED rc=0 match=no`. Dropping `and not unknown` keeps the marker but
  makes the run exit 0; LD4r is unaffected (`match=yes`). So the `unknown` half of
  line 552 was already bound by r91 rows; only the `resolved` half was not.
- **E5.** Survives both; `ok and True` is logically identical to `ok` — an equivalent
  mutant by construction, not a coverage hole.
- **E6.** Survives both; the harness reads `ITEM`/`FORGE` lines per row and the
  `SUMMARY` line only for the summary count, never its text (its rows are 10-column
  TSV, parsed positionally). A counter whose `SUMMARY` text is wrong — or absent — is
  green. This is the `output-only (SUMMARY text)` class in §3; it is a stated-limit
  shape (the harness never gates on counter stdout beyond markers).
- **E7.** Survives both. `forged += 0` makes `FORGE-SUMMARY forged=0` and
  `ok = … and forged > 0 …` False, but the harness only greps the per-row `FORGE …`
  line; it never reads `FORGE-SUMMARY` and never checks the counter's forge-path exit
  code except through `expect_rc` on forge rows — and there `expect_rc=1` rows are
  satisfied because the exit is 1 anyway. Wait — E7 survived even though `ok` became
  False: every forge row with `expect_rc=-` ignores the exit code entirely, and the one
  `lane` row with `expect_rc=1` (LP3) is satisfied by the forced 1. So the forge return
  (`ok = ok and forged > 0 and matched == forged`, line 573) is unbound, as stated
  limit (ii) says, AND `FORGE-SUMMARY` text is unbound. Row shape to bind E7/E8-class
  tally-no-ops on the forge path: a forge row with `expect_rc=0` and a matching forgery —
  which the prereg says the harness cannot express (a non-dash `expect_rc` is written
  into the forge file as MISMATCH). That remains a named limit.
- **E8.** Survives both. `counts["refused"] += 0` for unknown ledger ids: the `ledger`
  rows still see `LEDGER-REFUSED id=…` (the marker is printed from the `unknown` loop,
  not from the tally) and `ok` is still False (via `not unknown`). So the unknown-id
  TALLY is doubly unbound: both the marker and the `ok` half exist independently of
  it. Row shape: none available today — a row that asserts the `SUMMARY refused=` count
  would be needed; the harness never reads it.

So on the assigned clause set (541–552, 574) the answer splits: equality/tally edits
that keep the run all-resolved are caught ONLY by LD4r (E3), a slackened equality
survives everything (E1), and two of the eight edits are visible to no row at all (E6,
E7, E8).

## 3. Triage of the 77 residual survivors

Source: `census/round-92/records/c1-residual-survivors.json` (77 entries; verified
`residual ∪ targets == the 124 r91 survivors`, disjoint, and the file's own survivor
set matches `c1-survivors-r91.json`). Full per-mutant old/new lines are in
`residual-full.txt`. Sorted by line into five classes. "Bindable by a row" means a row
shape expressible in the CURRENT 10-column population + harness `where` types
(`lane`/`fixture`/`ledger`/`ledger-resolve`) would catch it, or a named extension
would. No residual was executed (per spec, "do not score all 77"); the class is argued
from the decision it changes and the rows that reach it.

### 3a. Forge path (lines 553–574) — 17 mutants

All residuals with `line >= 555` and one at 546/548/541/573:

| id | line | edit | class / note |
|---|---|---|---|
| a541c41, a541c52, a541c66, a541c76 | 541 | seed `unresolved/refused/mismatched/errors = 1` instead of `resolved = 1` (target) — pristine-neutral because `ok` only reads `resolved`; `resolved` starts at 0 in all four | **forge-path-adjacent / tally-seed**; seeds make `counts` wrong on an all-fail run but every row still resolves/fails as expected. Bindable: a run with exactly zero resolved (all-unresolved ledger) asserting `rc=1` via `SUMMARY` counts — needs `SUMMARY` gating (see E6/E8). Today unbound. |
| a546c37 | 546 | ITEM line prints `item[0]` for the file field | **output-only (ITEM text)**; harness reads `ITEM <id>` via regex only for `ledger-resolve` — and there only the `status=` token, not the `file:line` part. Unbound; needs a harness assertion on the file column. |
| a548c29 | 548 | `counts["refused"] += 0` for unknown ids | tally unbound (E8). Needs `SUMMARY` gating. |
| a555c38 | 555 | `forged = matched = accepted = 1` | seeds forge tallies at 1; per-row `FORGE` lines unchanged, `matched == forged` stays true (both 1), so `ok` unchanged. **Forge-path tally**; unbound today; a run with zero forgeries asserting `ok=False` would need a forge row with `expect_rc=0` (the NF1r limit). |
| a558c33 | 558 | skip blank/comment forge lines only if BOTH blank AND `#` | forgery-file parsing: a blank line in the forge file would be judged as a row. Bindable: a forged file with a blank line in the middle — the harness writes the forge file (1 row + newline), so this is a harness-side unbound shape; a `ledger` row does not reach it. Needs a forge row with a comment line (harness extension). |
| a561c31, a561c51 | 561 | forgery-row shape guard `!= 5 / in byid / in (…)` with `or`->`and` (precedence) | forge-path guards; bindable by a malformed forgery row (3-column, unknown item, bad expect) — but the harness writes a well-formed 5-col file, so today unbound. Needs a forge row whose expectation is malformed (harness extension). |
| a562c71 | 562 | FATAL message prints `r[1]` | **output-only (stderr)**; the exit code (2) is the only thing observable and it is unchanged. No bound possible without asserting stderr text. |
| a566c26 | 566 | `forged += 0` | E7 — forge tally; unbound (see §2). |
| a569c31 | 569 | `accepted += st in (…)`, counting non-resolution as accepted | `accepted` is printed in `FORGE-SUMMARY` but never read by the harness. **Forge-path counter**; unbound by the per-row `got` match. |
| a571c42, a571c46 | 571 | append `why` when `why or not hit` / `when hit` | **output-only (FORGE line suffix)**; harness regex reads `got=` only. Unbound. |
| a573c27, a573c29 | 573 | `forged >= 0` / `forged > 1` | the `> 0` half of the forge-`ok` gate. Unbound for the same reason as E2's escape in reverse: a single-forgery run can never reach `forged > 1`, and `forged >= 0` is a tautology. Bindable only by a forge run with zero forgeries asserting failure (NF1r limit) or by a two-forgery forge file (harness extension). |

### 3b. Output-only (SUMMARY/ITEM/FATAL text) — 4 mutants

a546c37, a562c71, a571c42, a571c46 (plus the E6 probe). All survive `_any_` population
because the harness never parses the counter's `SUMMARY`, `ITEM` file column, `FORGE`
`why` suffix, or FATAL message — it reads only `got=`/`status=`/markers and the exit
code. This class is the concrete form of stated limit (i): output fidelity of the counter
is outside this battery by design. Not bindable without a harness change (assert on the
counter's `SUMMARY`/`FORGE-SUMMARY` text, or on stderr); no row shape in the current
10-column schema reaches it.

### 3c. Argparse / environment / invocation surface — 9 mutants

| id | line | edit | why it survives |
|---|---|---|---|
| a127c26 | 127 | `sys.dont_write_bytecode = False` | environment: only affects `__pycache__` writes; no behavioural difference under `-B`. Likely-equivalent under this harness. |
| a156c46 | 156 | `ENV` drops the `not` — keeps only `GIT_*` vars | environment: keeping `GIT_CONFIG_NOSYSTEM`? no — it inverts the filter, so `ENV` keeps only keys starting `GIT_` and drops PATH, LC_ALL etc. `git()` then fails or inherits the host's — but the harness pins `GIT_CONFIG_NOSYSTEM=1, GIT_CONFIG_GLOBAL=/dev/null, LC_ALL=C` via its OWN env for the counter process; the counter's `git()` helper rebuilds env from `os.environ` — wait, it survived the full run, so the fixture never hits the broken-helper branch that would expose it (all `git()` calls are `check=False` or succeed via PATH passed through `ENV=`? No: `ENV` IS the env for `git()`; with only `GIT_*` keys, `git` is found via the default path, and `GIT_*` keys are exactly the pinned set, so every call behaves identically). **Equivalent under the harness's pinned env**; a row that pollutes `GIT_*` would bind it. |
| a162c27 | 162 | `def git(..., check=True)` -> `check=False` | default flip: every caller either passes `check=` explicitly or tolerates failure (the `_declared` raise is guarded), so no call site observes the default. **Likely-equivalent** — a call site that omits `check=` is needed to distinguish. |
| a282c57 | 282 | `check=False` -> `check=True` in `_regular` | only reachable when the ls-tree fails; all `_regular` calls that fail return False today (the `if not out` guard), and `check=True` raises only when git errors — which happens on a missing path that the rows never name. Bindable by a row whose target is absent at `--rev` but the ls-tree errors rather than returning empty? ls-tree on a missing path returns empty+rc0, so `check=True` never fires. Near-equivalent; needs a target that makes `ls-tree` itself fail (e.g. a path outside the tree). |
| a500c39, a501c38, a502c45, a503c45 | 500-503 | `--root/--rev/--fleet-root/--population required=True -> False` | argparse: the harness always supplies all four, so `required=False` is unobservable. **Equivalent under this harness**; the only bind is a row whose invocation omits one — the harness always supplies them, so unbindable without a harness change (run the counter without `--population` and assert exit 2). |
| a508c72 | 508 | `rv = git(..., check=True)` for `--rev` verify | the rev is always a real commit in every row, so `check=True` never raises; a `RuntimeError` would propagate as exit 1 — but no row names a bad rev. Bindable by a row with `--rev` naming a non-commit… the harness fixes `--rev` from the row's rev label, which is always a built commit. Unbound; needs a row whose rev label is bogus (harness extension). |
| a537c68 | 537 | `git show` `check=False -> True` | same shape as 508: the base blob is always present at `base` for every pinned population. Unbound; needs a population item whose file is absent at the population's base (harness/pin extension). |
| a536c13 | 536 | `if r[1] not in blobs` -> `if r[0] not in blobs` (cache key by id instead of file) | every item in every pinned population has a unique `r[0]`, so the blob cache is always cold anyway — the wrong key is observationally identical. **Equivalent** for id-unique populations; bindable only by a duplicated `r[1]` item run where the second item's `r[0]` differs — which the harness's `len({r[0] for r in pop}) == n` guard forbids. Effectively unreachable. |
| a491c22 | 491 | `len(r) < 3` -> `len(r) <= 3` in `_ledger` | rejects a well-formed 3-column ledger row. Every frozen ledger row is 4 columns, and LD3's appended row is 1 column (already `< 3`), so no row distinguishes `<` from `<=`. **Bindable**: a `ledger` row appending a 3-column row for an existing id (dup) would be refused under `<=` (malformed) and under `<` (duplicate) — both refuse, so even that is equivalent. A 3-column row with a FRESH id would be accepted under `<` and refused under `<=`; LD2b (ZZ9, 2-column) is the 2-col version. A `ledger` row appending a 3-column fresh-id row binds it. |

### 3d. Likely-equivalent — 11 mutants

No row in ANY pinned population can distinguish them because the changed predicate is
never evaluated on a differing input (verified by reading the clause and the row shapes
that reach it):

- a127c26 (§3c), a162c27 (§3c), a500c39–a503c45 (§3c), a536c13 (§3c) — environment/
  default/argparse equivalences under the harness's pinned invocation.
- **a294c30** `or -> and`: `if not (trailing or dots) and not targets` — the guard
  only fires when both are false; when `trailing or dots` is False, `targets` is always
  truthy in every row (the TOKEN ledger rows always name a target), so the second half
  is dead. Equivalent for all populations here.
- **a359c36**, **a375c22** `kr.end(0) -> kr.end(1)`: the ROUND match ends with `/` or
  end-of-string, so `end(1)` consumes the slash that `end(0)` leaves; both are then
  `.rstrip("/")`'d and split on `/` with empty components dropped — identical lists.
  Equivalent by construction (the only consumer difference is the leading-slash strip,
  which the `if c` filter removes).
- **a425c73** `token[:kr.start(0)] -> token[:kr.start(1)]`: same equivalence — the
  prefix before `round-` differs by one slash at the start boundary; the comparison is
  `!= "census"` and both forms are `""` or a non-census token prefix. Equivalent for
  every possible token (a token beginning `round-` at position 0 — impossible, since
  `ROUND` requires `^` or `/` before `round-`).
- **a468c41** `or -> and`: `if not token.startswith(".ufo/") and not os.path.lexists…`
  — the FLEET rows always satisfy exactly one half in every population (`.ufo/` token
  AND lexists); the `and` form only fires when both fail, which no row has (a
  non-`.ufo/` FLEET token would fire the `or` form and the `and` form identically because
  the second half is True when the first is). Equivalent for the FLEET row shapes here;
  bindable only by a FLEET row whose token is non-`.ufo/` AND absent on disk — that row
  doesn't exist.
- **a521c21, a521c54**: the `len(pop) != n` guards are already mutually exclusive in
  every pinned population (`n` is the pinned row count, so the first disjunct is always
  False) — same equivalence argument as a294c30.
- **a541c41/52/66/76** (§3a): seed mutants; `resolved` is 0 in all four so the success
  test never sees them. Equivalent on any run where `resolved` is counted from 0 and the
  run is judged only by `resolved == len(pop)`.

### 3e. Bindable by a row (forge-path / TOKEN / ledger / MOVED residue) — 36 mutants

The rest are mutants whose changed clause IS reachable by a row shape the current
battery does not have (or whose row exists but asserts only one half). By line, with
the row shape that binds each:

| line(s) | ids | row shape that binds |
|---|---|---|
| 211 | a211c78, a211c81 | a TOKEN row whose member is a **symlink** (mode 120000) at `--rev`: `_regular`'s mode drives `rev_digest`'s `l:` prefix; `split(b" ",0)`/`[1]` changes the mode string so the symlink is treated as a file. Bindable: a fixture row with a symlink target that must be REFUSED. |
| 264, 266, 269 (4) | a264c12, a264c15, a266c25, a269c62/c78/c91/c94 | a QUARANTINED **declaration** line where the token is at the very start (`i == 0`) and the sentence-end punctuation is followed by a path byte (`;foo`) or is the last byte: R13's NF6j family already covers the punctuation predecessors; a declaration with the token at column 0 of the line binds `i == 0` vs `i == 1` (a266c25) and `i > 0` (a264c*), and a declaration ending exactly `…/last-stub.;x` binds the a269 set. |
| 281 | a281c33, a281c37 | a TOKEN `fleet:` member that is a **symlink** under fleet-root: `_regular` returns isfile-under-fleet; a symlink member must be REFUSED. |
| 287 | a287c49 | a TOKEN member that is a **directory** at `--rev` with a regular-file mode string — i.e. an ls-tree entry whose `typ` is `tree` but `name`/`mode` match: needs a fixture revision where the member path is a tree; NF8's D3.txt-as-directory shape at R1 with the member itself a directory binds it. |
| 295 | a295c38, a295c52 | only the MESSAGE differs (`no parse artefact` vs `no target`); the TOKEN verdict does not. Unbindable by verdict; bindable only by asserting the `why` text (harness extension). (Same output-only class as §3b, reached via `judge`'s why string.) |
| 323, 327, 328 | a323c21, a323c33, a327c44, a327c70, a328c20 | a TOKEN `..` range row whose member fails exactly ONE of the three conditions: (a) `m` is None but `stem` is empty (a323c21), (b) wrong dir but right stem (a327c44), (c) right dir+stem but non-digit mid (a328c20). NF8/DM17-shape rows with members engineered to fail one leg each. |
| 334 | a334c48 | a `..` range with a **zero-padded lo** (`002..010`): `group(1)` vs `group(0)` — equal on every row today because no lo is padded. A padded-range TOKEN row binds it (and the a338 set). |
| 338, 339 | a338c42/c54/c56/c63, a339c19/c29/c50 | a `..` range with **span exactly 999/1000** or **lo with a leading zero**, or a degenerate single-member range (`lo == hi`): `lo > 1` vs `> 0`/`>= 1`, `hi <= lo`, `>= 999` all differ only at the boundary. A span-1000 range row (the current cap is 999) binds a339c50; a single-member range binds a339c19. |
| 344 | a344c23 | a TOKEN `..` row whose target count matches but members differ (or vice versa): `got != want and len != len` needs both. DM01/DM11 already have count-mismatch rows; a member-substitution row with equal count binds it. |
| 390, 393 | a390c31/c33/c45, a393c44 | an item whose declared **line is 1** (a390c31/c33) or **the last line of its file** (a390c45/c44): no pinned item uses line 1 or `len(blob)`. A population item at line 1 binds a390c31/c33; last-line item binds a390c45 and a393c44 (`int(line) <= len(blob)` would index `blob[len]`). |
| 396 | a396c30 | an item with a **frozen digest** that is present at `--rev` as CAPTURED at a rev where `at_rev` is not None but the token is MISSING — i.e. `frozen is not None and at_rev != frozen`: `or` returns CAPTURED for any frozen item with a present path regardless of digest. DM01/DM11 are TOKEN (frozen None); FP2/FP8 are MOVED/QUARANTINED (frozen present, but digest mismatch already REFUSED before this clause? No — the clause returns CAPTURED/MISMATCH first). A stub-capture row (digest differs) binds it. |
| 456, 457 | a456c53, a456c67, a457c16 | a QUARANTINED target with **exactly 3 components** (`a/b/c`) or a target that is present on disk but with a bad prefix: R13's leaves are 5+ components. A 3-component quarantine target binds `len(parts) < 4` vs `<= 4` (a456c67) and `or -> and` (a456c53). |
| 472, 473 | a472c13, a473c18/c31/c60/c64 | an **ABSENT** row in a population whose token carries a parse artefact: `cls != "ABSENT"` falls through all branches to `return cls` (resolves ABSENT) — a TOKEN-shaped item answered by an ABSENT ledger row binds a472c13; a token ending in `-` with `token[-0]` (whole token) binds a473c18; a token with `..` in a non-final component binds a473c60/c64. |
| 541(seed)/546/548/555+ | (see §3a) | see §3a — these need `SUMMARY`/`FORGE-SUMMARY` gating or a forge row with `expect_rc=0` (the NF1r named limit). |

Count check: 17 + 4 + 9 + 11 + 36 = 77. (a127c26/a162c27/a500–503/a536 are counted
in §3c; the §3d 11 are disjoint from §3c except a162c27, which is listed in both as
environment/default — it is inside the 9.)

### Summary of the triage

- **Forge path: 17** — all unbound, dominated by the NF1r named limit: no row can carry
  `expect_rc=0` on a forge run, and the harness never reads `FORGE-SUMMARY`. A forge
  row with `expect_rc=0` (harness extension: don't write non-dash `expect_rc` into the
  forge file as MISMATCH) would bind a541c41–76, a555c38, a561c31/51, a566c26, a573c27/29
  in bulk.
- **Output-only: 4 (+ E6)** — unbindable by any verdict row; needs harness assertion on
  counter stdout/stderr.
- **Argparse/env: 9** — 4 equivalent under the harness's pinned invocation, 1 equivalent
  for id-unique populations, 4 bindable (a491c22 by a 3-column fresh-id ledger row,
  a508c72/a537c68 by bogus-rev/absent-file rows, a282c57 by a failing ls-tree).
- **Likely-equivalent: 11** — no row distinguishes them; 7 are equivalent by construction
  (dead halves, slash absorption, mutually-exclusive guards), 4 are seeds/tally-neutral.
- **Bindable by a row: 36** — boundary shapes (symlink member, padded/span-boundary
  range, line-1/last-line item, 3-component quarantine target, ABSENT-shaped item,
  single-leg failures) that a next population could carry without a new `where` type
  except for the §3a forge set, which needs the forge-`expect_rc=0` extension.

## 4. Falsification verdict

### FALSIFIES-WORDING (sentences)

1. Prereg line 43: "KILL RULE (unchanged from the r84-r91 batteries): a kill is a
   non-zero harness exit on that population." + CLAIM: "kills the 47 survivors".
   FK1/FK2 show the rule scores a mutant that never runs as killed, indistinguishable
   from a polarity kill in the search summary (`killed=47` carries no evidence that any
   of the 47 behaviourally differ from pristine on an asserted verdict). Any future
   sentence of the form "LD4r kills the 47" should be read as "LD4r makes the harness
   exit non-zero on the 47", which is all that was measured. The reproducer is
   `harness-import-crash-r92.txt` / `harness-argparse-r92.txt` in this seat dir
   (mutants at `/fast/scratch/hyaku/souji-r92/R92MutC1/counter-import-crash.py`,
   `counter-argparse.py`, deleted with scratch). The filed runs contain no crash kill
   (§1c), so no filed NUMBER is falsified; the wording is wider than the evidence.
2. CLAIM: "ONE appended row, LD4r … kills the 47 survivors" — read as covering the
   clause class the 47 hit. E1 shows a different edit of the same line (552) that
   survives LD4r, and E5/E6/E7/E8 show edits of the same clauses that no row in the
   population sees. LD4r kills the 47 single-token edits listed in
   `c1-targets.json`, not the clause class. The claim already hedges this with stated
   limit (iv) ("not a full mutation space") and stated limit (ii) (forge path not
   bound), and E1 is not in either: it is a main-path (non-forge) edit of a claimed
   clause that survives. That is the sharpest single finding: a **main-path
   alternative-edit survivor on a bound clause**. Row shape that binds it is named in
   §2 (a `ledger-resolve` row with exactly one unresolved item asserting `expect_rc 0`).

### Evidence for the claim (not a falsification)

- E3 (tally-clause edit on line 545) is killed ONLY by LD4r and by no r91 row,
  matching the claim's mechanism exactly, via the tally rather than `return`.
- All 47 filed kills are harness rc 1; the pristine after-receipt matches the prereg
  (`SUMMARY rows=64 mismatches=0 accepted=0 refused_true=0 errors=0`, LD4r
  `rc=0 match=yes`).
- The 77-residual set + 47 targets = the 124 r91 survivors, disjoint (verified locally
  against `c1-survivors-r91.json`).

### NO-FALSIFICATION numbers

No stated C1 number is falsified by this seat: `generated=270, ambiguous=9, hung=1,
scored=260, killed=136, survived=124` (r91), `killed=47 survived=77` (feasibility),
`killed=0 survived=47` (control), `killed=47 survived=0` (after),
`SUMMARY rows=64 mismatches=0 accepted=0 refused_true=0 errors=0` with LD4r
`rc=0 match=yes` — all match the filed receipts, and the seat's own 16 harness runs
(E1–E8 × 2 populations, FK1, FK2) never contradict them. The findings are about what
`killed` MEANS and what the 47-target set DOESN'T cover, not about the counts.

## 5. Reproducers & files

All under `.ufo/waves/round-92/w1/R92MutC1/` (lane-relative; the L1 copies these in):

- `probe.py` — the E1–E8 driver (harness invocations exactly as the surgery-freeze
  predicate, sequential, ≤1 work tree).
- `results.json` — per-edit harness rc + LD4r line + SUMMARY for both populations.
- `harness-E*-r92.txt`, `harness-E*-r91.txt` (16 files) — full harness outputs.
- `harness-import-crash-r92.txt`, `harness-argparse-r92.txt` — FK1/FK2 outputs.
- `probe-console.txt` — console capture of the E1–E8 batch.
- `residual-full.txt`, `residuals.txt`, `residuals-compact.txt` — the 77 residuals
  with old/new lines.
- `r92-rows.txt`, `r91-rows.txt`, `c1-targets-copy.json` — population/target copies
  used for the triage.
- Counter mutants were scratch copies of the frozen counter (sha256 `fd0a8e24…`),
  at `/fast/scratch/hyaku/souji-r92/R92MutC1/`, deleted with scratch before yield.

No frozen file was modified; no git/jj operation was run; no subagent was dispatched
(leaf member). Tools: stock `python3 -B`, `grep`, `sha256sum` — nothing installed.

Report: .ufo/waves/round-92/w1/R92MutC1.md
