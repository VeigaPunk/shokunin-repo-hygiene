# R40executor26 — C2 operability attack

- Seat: executor (leaf; no dispatch). Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
- Frozen contract read first: `census/round-40/preregistration.txt` (C2 at lines 7–8).
- **Distinct item 26 edge case, named: join-termination underspecification on the *under-join* side — internal blank lines and tab-indented continuations split a wrapped class entry so the wrapped trigger is orphaned, and the probe-pair control validity.** This is the opposite failure direction from R40executor38's over-join across class boundaries, and distinct from R40executor62's class-like-token continuation lines: here nothing class-like is present, and a compliant analyzer still loses the trigger depending on which natural termination rule it implements.
- No production files, frozen claims, fleet paths, or git/jj state touched. Scratch was `/fast/scratch/hyaku/souji-r40/R40executor26` (explicit `TMPDIR`), removed before yield. Tool installs/upgrades: none; pacman untouched.

## Verdict

**The frozen C2 measurement is insufficient as specified: it is satisfiable by analyzers that violate the join half on untested wrap shapes, and its control holds for only one probe pair.** Concrete falsifiers F1–F3 below are measured on committed r39 base bytes; the r40 candidate does not exist yet (`census/round-40/` contains only `preregistration.txt`), so no r40 behavior is claimed as measured. Bounded measurement plan M1–M4 specifies what the r40 receipt must add to be kill-proof on this edge.

## Committed evidence base

| Artifact | Revision | Blob | sha256 |
|---|---|---|---|
| `tools/souji-worktree-drift.py` | `0242085909fb6a4ee041c5443d76316ac6d59d4b` (prereg base) | `5a2b32941bc5c3da628ee92f75be1c33192ca311` | `e48ed08e672824e225e165a34d5659b244babfa1ea55cb88721059fa6a0c2f76` |
| `census/round-39/c2-counter.py` | same | `953810db16fa0f7f308311b0aa65a49ad1d80223` | `732b1e425a6ddc37a9632431269c9c679b32cbe18a22cb35b5b4f4cec151ee11` |

Lane HEAD at attack time: `be4cb61e84ebcbf05814d3dfe6ba00b6f730f10e` (base is its parent revision's tree content for both files; both files unmodified in the working copy, `git status --porcelain` empty on them).

Grounding reads: `docstring_classes` at `census/round-39/c2-counter.py:133-146` (ast, `clean=False`, per-line `strip()`, `startswith(cls)`, first line per token stored whole); r39 L4 conjuncts at `:230-239` (`missing in new_classes and "missing" in new_classes.get(missing,"").lower() and locked in new_classes and "EACCES" in new_classes.get(locked,"")`); the real refusal-class block sits in the module docstring with **adjacent entries and no blank lines** (`RECORD-MISSING`/`RECORD-MALFORMED` entries at docstring lines 43–47, each with one deep-indented continuation).

## Commands actually run (all others were file reads)

```text
mkdir -p /fast/scratch/hyaku/souji-r40/R40executor26
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 0242085909fb...:tools/souji-worktree-drift.py > $T/drift_base.py
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 0242085909fb...:census/round-39/c2-counter.py > $T/c2_counter_base.py
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD   # be4cb61e...
TMPDIR=$T python3 -B $T/attack.py
TMPDIR=$T python3 -B $T/attack2.py
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse 0242085...:tools/souji-worktree-drift.py 0242085...:census/round-39/c2-counter.py 0242085...^{commit}
```

`attack.py`/`attack2.py` (scratch, quoted in full in the chat transcript; deleted with the scratch) import the committed counter as a module (its `main` is `__main__`-guarded) and call **its own** `docstring_classes`, `classify`, and `run_drift` for every r39-column cell — no reimplementation stands in for the counter where the counter's code is available. My joiner/verdict helpers were cross-checked against `cc.docstring_classes` on the base bytes before use (`cross-check ... : True` in output).

## Measured facts

**1. Control replication on committed base bytes (r39 analyzer):**

```text
RECORD-MISSING   -> 'RECORD-MISSING         EACCES or ELOOP opening the record path: the path'
RECORD-MALFORMED -> 'RECORD-MALFORMED       a missing (ENOENT) or non-regular record path, a line'
```

First-line-only storage confirmed; both trigger substrings (`EACCES`; `missing`) happen to sit on those first lines at the r39 tip.

**2. Runtime observed pairs (tip tool actually executed, not read):** `classify(absent path) = RECORD-MALFORMED`; `classify(chmod-0 path) = RECORD-MISSING` — the same pairs the r39 L4 expression encodes (`parse_record` at `tools/souji-worktree-drift.py:129-137`: ENOENT → `RECORD-MALFORMED`, other open `OSError` → `RECORD-MISSING`).

**3. Probe-placement scan over the real docstring (control validity):** exactly two docstring lines carry trigger substrings — line 43 (`RECORD-MISSING` entry: `EACCES` + token substring `missing`) and line 45 (`RECORD-MALFORMED` entry: prose `a missing (ENOENT)`). Consequence (**F3**): a probe built on the RECORD-MALFORMED/"missing" pair is r39-*caught regardless of wrapping*, because `missing` is already on its stored first line. The frozen control "the r39 one-line analyzer misses it" is **pair-dependent**: it holds only for the (RECORD-MISSING, EACCES) pair, which the receipt does not pin.

**4. Joiner × shape matrix** — three natural implementations of "joins wrapped continuation lines into one class entry" (J1 closes an entry at a blank line, J2 at a dedent measured in spaces with blanks skipped, J3 only at the next known class token), evaluated on the untouched base docstring (S0) and on the same entry rewrapped three ways (S1 frozen-shape single wrap; S2 one internal blank line before the trigger continuation; S3 trigger continuation indented with a tab; S4 blank+tab):

| case | r39 (`cc.docstring_classes`) | J1 blank-close | J2 dedent-close | J3 token-close |
|---|---|---|---|---|
| S0 untouched base | PASS | PASS | PASS | PASS |
| S1 frozen probe shape | MISS | PASS | PASS | PASS |
| S2 internal blank line | MISS | **MISS** | PASS | PASS |
| S3 tab-indented continuation | MISS | PASS | **MISS** | PASS |
| S4 blank + tab | MISS | **MISS** | **MISS** | PASS |

`probe` = `EACCES` attributable to the RECORD-MISSING entry; `L4` = both r39 conjuncts on the pinned runtime pairs. Orphaned-trigger strings, measured verbatim:

```text
S2/J1 RECORD-MISSING entry: 'RECORD-MISSING         opening the record path failed:'
S3/J2 RECORD-MISSING entry: 'RECORD-MISSING         opening the record path failed:'
S4/J2 RECORD-MISSING entry: 'RECORD-MISSING         opening the record path failed:'
```

## Falsifiers

- **F1 (kill-clause implementation lottery):** J1 passes the frozen single-shape probe (S1 row) yet misses the wrapped trigger on S2 — a legitimate wrapped shape the predicate's text ("joins wrapped continuation lines into one class entry") plainly covers. A receipt that only demonstrates the frozen probe cannot distinguish J1 from J3; the frozen kill condition "wrapped trigger is missed" fires for one compliant implementation and not another.
- **F2 (indent-rule sensitivity):** J2 passes S1 yet misses S3: an indentation-measured joiner that counts spaces only loses tab-wrapped continuations. The predicate does not state the whitespace rule.
- **F3 (control validity is pair-dependent):** measured scan shows `missing` already on the RECORD-MALFORMED first line (line 45), so only the (RECORD-MISSING, EACCES) probe pair makes the "r39 misses it" control true. Unpinned, a receipt could satisfy the frozen sentence with a probe pair for which the control is vacuous.
- J3's all-shape survival is not free: it joins until the next token of the counter's own two-token set, so its coverage is bounded by that token list (a new refusal class added to the tool is invisible to it), and it absorbs everything after `RECORD-MALFORMED` into that entry in S0 — measured keys stay correct for the two pinned pairs only.

## Bounded measurement plan (what the r40 receipt must pin for this edge)

1. **M1:** pin the probe pair to (RECORD-MISSING, EACCES) and demonstrate on base bytes that r39 `docstring_classes` misses exactly that pair (makes F3 impossible).
2. **M2:** run the candidate joiner on the shape matrix S1+S2+S3 (frozen wrap, internal blank, tab indent): candidate must detect all three; r39 base must miss all three. J1 fails S2, J2 fails S3, so this matrix actually discriminates termination rules; the frozen S1-only receipt does not.
3. **M3:** keep S0 (untouched base docstring bytes) green under the candidate — no false kill on correct input.
4. **M4:** state the analyzer's entry-termination rule and its class-token set explicitly in the receipt, so a new refusal class in the tool cannot silently fall outside the analyzer's token bound.

## Risks / blockers

- The r40 candidate counter is not yet in the census tree, so predicates 1–4 of the frozen C2 receipt could not be executed against it; the falsifiers above constrain its implementation space, they do not assert r40 failure.
- The r39 stored lines embed the class token, so any `"missing" in line.lower()` conjunct is trivially true for a RECORD-MISSING-keyed entry (known from r39 review); this attack measured only non-token triggers (`EACCES`, and prose `missing` on line 45) and did not re-litigate that finding.
