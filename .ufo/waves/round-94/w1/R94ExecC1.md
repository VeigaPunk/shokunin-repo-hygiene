# R94ExecC1 — independent re-derivation of C1 (calibration 7) on committed bytes

Seat: R94ExecC1 (leaf executor). Lane base eddb1be6; instruments P1 24cd67b0; controls P2 39d4163a; prereg F 4ad74b9d.
Scope: read-only on the lane. Receipts in `.ufo/waves/round-94/w1/R94ExecC1/receipts/`. Scratch
`/fast/scratch/hyaku/souji-r94/R94ExecC1/` deleted before yield. No tool installs, no git/jj mutation, no background jobs left.

Verdict: **NO-FALSIFICATION** for C1. Every count in the prereg predicate, both controls and both forgeries re-derived on the
committed bytes. No prereg mismatch found.

## 1. Pin table (sha256, re-computed at seat time)

| instrument | re-derived sha256 | prereg / P2 receipt | match |
|---|---|---|---|
| census/round-94/c1-survivor-search.py | 97b8defa5c3c007cc10814483fe6dae6fe0f0a0bdb066b0f14169561b9f374ae | 97b8defa5c3c007c... (prereg), printed by after receipt | yes |
| census/round-94/c1-targets.json | 0117cad7fce69d274c2c9b615542553b0821dfad64198f70867906bd1ef514d7 | 0117cad7fce69d27... | yes |
| census/round-94/c1-control-r93-rule.py | b733032f2b5b9e19e2286f65f5f348340223af43f55672bb2eb5906982de8736 | b733032f... | yes |
| census/round-94/c1-forgery-controls.py | bee948af5c94f84df8bffff78f8379c76d3c647b2193cdfd319f990c0e17277d | bee948af... | yes |
| census/round-93/c1-false-row-harness.py | 1868a570b9100559637ab454e6f7737bfdc881339cf8045d75cc22b3060a84a4 | 1868a570... | yes |
| census/round-93/c1-false-rows.tsv | d6439f65a632cf83fb9d47c78bd0d32d1f9104d2f6443bdfd770e1c1c5e1a88e | d6439f65... | yes |
| census/round-87/c1-pointer-counter.py | fd0a8e244a5e0afe58f9e8bfa85d314722b77a1bcbe6837298683f74a755220b | fd0a8e24... | yes |
| census/round-93/c1-survivor-search.py (r93 rule) | 6089260be7d18c5f48c5bf1289e159efba534f2ef1c5d730f9b4f356d37ed71d | 6089260b... (P2 control receipt) | yes |

The after and forgery receipts print the same search hash (97b8defa...), and the control receipt prints 6089260b..., matching the r93 search.
The forgery FA/FB search copies are 655624cc... (FA) and 8f63120e... (FB). These are one-edit derivatives, so no prereg pin applies.

## 2. Receipts (verbatim, exit codes)

### 2a. After arm: `c1-survivor-search.py` (EXIT 0, wall 21.97 s)
```
# crash-sentinel rc=70 check=pass
# counter path=.../census/round-87/c1-pointer-counter.py sha256=fd0a8e244a5e0afe58f9e8bfa85d314722b77a1bcbe6837298683f74a755220b
# harness path=.../census/round-93/c1-false-row-harness.py sha256=1868a570b9100559637ab454e6f7737bfdc881339cf8045d75cc22b3060a84a4
# population path=.../census/round-93/c1-false-rows.tsv sha256=d6439f65a632cf83fb9d47c78bd0d32d1f9104d2f6443bdfd770e1c1c5e1a88e
# search sha256=97b8defa5c3c007cc10814483fe6dae6fe0f0a0bdb066b0f14169561b9f374ae
# ids path=.../census/round-94/c1-targets.json sha256=0117cad7fce69d274c2c9b615542553b0821dfad64198f70867906bd1ef514d7 n=5
SEARCH a127c26-True-to-False line=127 killed=no rc=0
SEARCH a491c22-<-to-<= line=491 killed=yes rc=1
SEARCH h-ok-admits-one line=552 killed=yes rc=1
SEARCH h-crash-late line=574 killed=errored rc=1
SEARCH h-crash-index line=494 killed=errored rc=1
SEARCH-SUMMARY generated=5 ambiguous=0 uncompiled=0 hung=0 scored=5 errored=2 killed=2 survived=1
EXIT=0
```
Predicate check: first line `# crash-sentinel rc=70 check=pass` ✓; SUMMARY matches exactly ✓; crash fixtures `killed=errored` ✓; semantic kills `killed=yes` ✓; survivor `killed=no` ✓; EXIT 0 ✓.

### 2b. Do-nothing control: `c1-control-r93-rule.py` (EXIT 0, wall 55.02 s)
```
# search sha256=6089260be7d18c5f48c5bf1289e159efba534f2ef1c5d730f9b4f356d37ed71d
SEARCH a127c26-True-to-False line=127 killed=no rc=0
SEARCH a491c22-<-to-<= line=491 killed=yes rc=1
SEARCH h-ok-admits-one line=552 killed=yes rc=1
SEARCH h-crash-late line=574 killed=yes rc=1
SEARCH h-crash-index line=494 killed=yes rc=1
SEARCH-SUMMARY generated=5 ambiguous=0 uncompiled=0 hung=0 scored=5 errored=0 killed=4 survived=1
EXIT 0
```
Predicate check: `errored=0 killed=4 survived=1` ✓; both crash fixtures `killed=yes` ✓; EXIT 0 ✓.

### 2c. Forgeries: `c1-forgery-controls.py` (EXIT 0, wall 68.47 s; ran as a background job, output retrieved complete)
```
# search path=.../census/round-94/c1-survivor-search.py sha256=97b8defa5c3c007cc10814483fe6dae6fe0f0a0bdb066b0f14169561b9f374ae
FORGERY FA sha256=655624ccc834a3c869300f181822d89353b2d4de9da0cbe0bde3e27e0bffbfb6 exit=0 summary=generated=5,ambiguous=0,uncompiled=0,hung=0,scored=5,errored=4,killed=0,survived=1 refused=yes
  FA SEARCH a127c26-True-to-False line=127 killed=no rc=0
  FA SEARCH a491c22-<-to-<= line=491 killed=errored rc=1
  FA SEARCH h-ok-admits-one line=552 killed=errored rc=1
  FA SEARCH h-crash-late line=574 killed=errored rc=1
  FA SEARCH h-crash-index line=494 killed=errored rc=1
FORGERY FB sha256=8f63120ea138caf0e692cfdf21096b4ffa21b13abca113e149e2c509a54492b1 exit=0 summary=generated=5,ambiguous=0,uncompiled=0,hung=0,scored=5,errored=0,killed=4,survived=1 refused=yes
  FB SEARCH a127c26-True-to-False line=127 killed=no rc=0
  FB SEARCH a491c22-<-to-<= line=491 killed=yes rc=1
  FB SEARCH h-ok-admits-one line=552 killed=yes rc=1
  FB SEARCH h-crash-late line=574 killed=yes rc=1
  FB SEARCH h-crash-index line=494 killed=yes rc=1
C1-FORGERY-SUMMARY forgeries=2 refused=2
EXIT 0
```
Predicate check: FA and FB each differ from the predicate ✓; `C1-FORGERY-SUMMARY forgeries=2 refused=2` ✓; EXIT 0 ✓.

Forgery controls cannot be read as a second copy of the predicate: FA turns the two semantic kills into `errored`, and FB turns both crash fixtures back into `killed=yes`. Each one-edit copy therefore fails the predicate, as the prereg requires.

## 3. Hunk inventory: `diff census/round-93/c1-survivor-search.py census/round-94/c1-survivor-search.py` (exit 1, = differences present)

| # | r93 lines → r94 lines | class | note |
|---|---|---|---|
| H1 | 2,4-11 → 2-15 | docstring | new r94 header text (declared in prereg, sentinel+rule+hand edits) |
| H2 | 4-11 → 17-18 | docstring | r92-era kill-rule docstring replaced by "Inherited from r93" line |
| H3 | 47a → 55-57 | hand edit (declared) | `h-crash-late` (`raise RuntimeError("h-crash-late")` in place of `return 0 if ok else 1`) and `h-crash-index` (`(r[1], r[2], r[3])[:2]`) tuples, inserted into HAND |
| H4 | 48a → 59-75 | sentinel (declared) | `CRASH_RC = 70` (EX_SOFTWARE) and `HOOK` sitecustomize writing `sys.excepthook` → `os._exit(70)` |
| H5 | 87c → 114-121 | kill rule (declared) | r94 rule: `rc == 70` or any `ROW ... rc=70 match=` → errored, else killed only on rc 1 + `match=no` row |
| H6 | 90-91 → 121 | kill rule, refactor | the r93 check `any(l.startswith("ROW ") and l.endswith(" match=no") ...)` is now `any(l.endswith(" match=no") for l in rows)` over a pre-filtered ROW list. Behaviour-neutral on the non-crash path (same predicate, same lines). Not in prereg prose; classed as an implementation detail of H5, not a new rule. |
| H7 | 108a → 139-140 | sentinel plumbing | `env["PYTHONPATH"]` prefixed with `ns.hook` |
| H8 | 112c → 144 | sentinel plumbing | `Popen(..., env=env)` |
| H9 | 172a → 205-218 | sentinel plumbing + precondition | writes `hook/sitecustomize.py`, then spawns a child `raise RuntimeError` and returns 2 with `C1-SEARCH-FATAL` if the child exit ≠ 70; prints `# crash-sentinel rc=70 check=pass`. The env construction is guarded by `.get`, so no KeyError when PYTHONPATH is unset. |

UNEXPECTED hunks: **none**. Every hunk maps to a prereg-declared item (sentinel, rule, two crash hand edits, docstring) or is the behaviour-neutral refactor in H6.

## 4. Per-target row table (harness.out kept from the after arm, `--work` m0000–m0004)

Counts on each `harness.out` (`grep -c '^ROW '` = 66 per target; the split of 66 into harness states was not counted):

| id (mutant) | rows | `rc=70` rows | `rc=70 ... match=no` rows | `match=no` rows | got= semantic row | search verdict |
|---|---|---|---|---|---|---|
| a127c26-True-to-False (m0000) | 66 | 0 | 0 | 0 | — (0 mismatches; SUMMARY mismatches=0) | survived, killed=no ✓ |
| a491c22-<-to-<= (m0001) | 66 | 0 | 0 | 1 | `ROW LD6 where=ledger-trim rev=BASE item=P04 class=- expect=MOVED/0 got=UNRESOLVED rc=1 match=no` | killed=yes ✓ |
| h-ok-admits-one (m0002) | 66 | 0 | 0 | 1 | `ROW LD5 where=ledger-drop rev=BASE item=P04 class=- expect=UNRESOLVED/1 got=UNRESOLVED rc=0 match=no` | killed=yes ✓ |
| h-crash-late (m0003) | 66 | 66 | 10 | 10 | crash rows: all 66 carry `rc=70` (the counter's uncaught RuntimeError surfaced via the sentinel) | errored ✓ |
| h-crash-index (m0004) | 66 | 1 | 1 | 1 | crash row carries `rc=70`; its `match=no` is the crash row itself | errored ✓ |

Notes:
- For the two semantic kills the `got=` field is not `-` (it is `UNRESOLVED`), and no row carries `rc=70`. Both are killed by a real semantic mismatch, as the prereg requires. Note for the record: the `expect/got` values themselves are not re-derived against the population.
- h-crash-late shows 66 `rc=70` rows against 10 `match=no` rows, so the crash is not confined to a single row. This is consistent with the rule (errored on any `rc=70`). [INFERENCE] that the counter is re-run for each row is not checked here.
- m0000 (survivor) `SUMMARY rows=66 mismatches=0 ... errors=0`. m0001/m0002 each show `mismatches=1`. m0003 `mismatches=10`. m0004 `mismatches=1`.

## 5. Control wrapper check

`census/round-94/c1-control-r93-rule.py` loads the frozen r93 search as module `r93search` and the r94 search as `r94search`. It sets `r93.HAND = r93.HAND + extra` where `extra = tuple(h for h in r94.HAND if h[0] in ("h-crash-late", "h-crash-index"))` (asserted len 2), then calls `sys.exit(r93.main(sys.argv[1:]))`.
- It does **not** override `verdict()`, `score()` or `main()`; the r93 functions run unchanged.
- Its HAND extension is byte-identical to the r94 tuples by construction: the two tuples are read from the r94 HAND object, not re-typed.
- The r93 search prints its own file's sha256 via `__file__`, so the control receipt shows `search sha256=6089260b...` (the r93 search). Also confirmed: the r93 search has no sentinel, so its `main` never prints `# crash-sentinel`.

## 6. Limits and checks not done

- Full-population re-score (not required by the predicate; prereg STATED LIMITS (i)) was not run.
- The `got=` expectations (`expect=MOVED/0`, `expect=UNRESOLVED/1`) were not re-derived against the population file; only the match and rc fields were counted.
- The forgery run reused the search through its own `--work`; the harness.out copies for FA/FB were not retained (scratch deleted).

## 7. Falsification statement

FALSIFIES-WORDING: none.
FALSIFIES-NUMBER: none.
NO-FALSIFICATION: C1 after arm (errored=2 killed=2 survived=1; crash fixtures errored, semantic kills killed, survivor survives), do-nothing control (errored=0 killed=4 survived=1; both crash fixtures killed=yes), forgeries FA/FB (refused=2) all reproduce exactly on committed bytes with pins matching the prereg. Tried: full rerun of the three predicate commands, pin re-computation, a diff classification of every hunk, per-target harness.out row counts, and inspection of the control wrapper.

Tool installs: none. Host/pacman untouched. Scratch deleted.
