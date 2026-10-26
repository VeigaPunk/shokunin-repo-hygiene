# Round-30 instrument sprawl — YAGNI review (read-only, proposals only)

Seat SwarmSimplifier34, wave 2, attempt 1. **No edits, no deletion, no git/jj mutation performed.**
Everything below is a proposal for round 31.

Lane tip read: `9dcd367655fc28ba73d679a0e2cadaff96d2bcb8`; frozen v1 blobs read at
`d4928ec86b667e3d1ed0adb07fb088e500cf1631`; base `9420341d9a814cb6089c25fb03a4cc9b23dc0d1b`.

Method. Overlap is measured mechanically (set intersection of non-blank lines, per pair), not eyeballed.
The one behavioural claim (D1) is proven with a micro-test built from the committed format strings.
The `lsp` device is **not mounted in this session** (`read xd://lsp` → `No such tool: xd://lsp`), so caller
analysis is text grep and is labelled as such — it is not presented as semantic proof.

## 1. Inventory and fate

| Piece | Size | Fate | Why |
|---|---|---|---|
| `tools/souji-capability-agreement.py` | 246 lines | **KEEP tools/ home**, parameterize 2 literals | Semantics (stated count vs observed, append-only corrections) recur on the calibration axis; the round-30 row path and the `R30-` marker are the only round-bound bytes. |
| `census/round-30/c2-counter.py` (v1) | 124 lines | **ONE-ROUND** — keep as r30 provenance, do not recreate the pattern | Every leg it runs is also run by v2; it has no discriminating power v2 lacks. |
| `census/round-30/c2-counter-v2.py` | 178 lines | **ONE-ROUND**, carries the reusable *shape* | Claim-specific literals (`--round 29`, `expected == 86`); its one defect is D1. |
| `census/round-30/c3-counter.py` (v1) | 130 lines | **ONE-ROUND** | Hardcodes `ENTRY`, `RUN`, `FLEET_CENSUS`, two exact stdout strings (D3). |
| `census/round-30/c3-counter-v2.py` | 108 lines | **ONE-ROUND** | Additive legs; E1/E2/E3 duplicate existing authorities (§4). |
| `census/round-30/controls.sh` | 68 lines | **CONSOLIDATE** with the amended file | Same prologue as `controls-amended.sh`; r29 has the identical quartet. |
| `census/round-30/controls-amended.sh` | 51 lines | **CONSOLIDATE** | No C3 arm and no A2 discriminator (D2). |
| `tests/fixtures/r30-landing-gate-discovery.py` | 554 lines | **KEEP** (lane fixture convention) | Not sprawl by itself; it is *forced* to exist by the REGRESS leg's design (§5 P5). |
| `census/round-29/waves/make-spec.py`, `census/round-30/waves/make-spec-w1.py`, `.ufo/waves/round-30/make-spec-w2.py` | 121 + 111 + 93 = 325 lines | **CONSOLIDATE into `tools/`** (P1) | Four generator instances over two rounds, each rewriting the same rendering loop; pairwise shared distinct lines: 10 (r29/w1), 21 (w1/w2). |

Reusable next round, worth a `tools/` home: `souji-capability-agreement.py` (already homed — needs §5 P6) and
a new `souji-wave-spec.py` (P1). **Not** worth promoting: any of the four claim counters (their literals are
claim-specific by construction) and the controls pair (its content is round-specific; only its *shape* recurs).

## 2. Duplication measured

- **c2 pair**: v1 108 / v2 149 distinct non-blank lines, 54 shared. v2 re-runs all four v1 legs
  (`GATE`, `FIXTURE`, `REDARM`, `REGRESS`); v1-only substance is the dropped `other=` diagnostic. The
  54 "unique" v1 lines are docstring plus the same plumbing under different names (`export` vs `clone`).
- **c3 pair**: 120 / 98 lines, 33 shared. Legs are **disjoint** (v2 is additive), so under the sibling-file
  convention this pair is *necessary* — the weight is in the convention, not in either file.
- **controls pair**: 68 / 51 lines, 18 shared (clone, toplevel check, `g()`, three counter wrappers).
- **generators**: 325 lines across three files, near-orthogonal text — every round re-derives the spec renderer.
- r29 carries the same quartet (`census/round-29/c2-counter.py`, `-v2.py`, `controls.sh`, `controls-amended.sh`;
  `ls` of that directory), so the quartet is a **recurring scaffold**, not a round-30 accident.

## 3. Reuse already achieved — do not disturb

`census/round-30/c3-counter.py` legs L2, L3, L9 are *calls*, not reimplementations:
`tools/souji-coverage-agreement.py`, `tools/souji-gate-check.py`, fleet `scripts/sources-census.sh`.
That is 3 of 9 legs delegating and is the pattern to extend, not to repair.

`c2` cannot delegate: `tools/souji-landing-gate.py` is its *subject*. Its BIND leg counts the capture with
`git ls-tree` instead of reading `census/round-29/waves/manifest.sha256` (86 member entries) — that
independence is correct and is **not** duplication; a counter that trusts the receipt it validates proves nothing.

## 4. Duplicate authorities (a stricter copy shadowing a shared tool)

| Round-30 code | Existing lane tool it re-derives | Consequence |
|---|---|---|
| `c3-counter-v2.py` E1 (`ground: F1` exact token, exactly 3 files) | `tools/souji-coverage-agreement.py:34` `FRONT_GROUND = re.compile(r"^ground:\s*F([0-9]+)")` — captures `F1` from `ground: F1-jj` | The shared tool is *lax*; the counter is strict. A future seat that reuses coverage-agreement alone regains the suffix bug A2 was written to close. |
| `c3-counter-v2.py` E2 (entry named in the plain `F1 ` row) | same tool, `GROUND_TOKEN` accepts any `F<k>` followed by a separator, so the `F1-jj` row satisfies F1 | Same split authority; E2's docstring states the intent: "(the plain F1 row; the `F1-jj` edge-class row does not satisfy it)". |
| `c3-counter-v2.py` E3 (replay fixture@REV, compare lines to record) | `tools/souji-receipt-run.py:4` "A counter run is only evidence if the bytes that produced it are pinned." | A fifth hand-rolled clone+run+compare, while the lane already ships the receipt form. |
| `c3-counter.py` L6 (`source:` ids are registry rows, opened date, URL bound to source cell) | `tools/souji-registry-agreement.py:9` K1 (every `used-by` path must exist; every `S###` on `source:` lines must be a row) | Directional overlap only; merging would change the enumerated set. |
| `c3-counter.py` L5 (quote spans 4..25 words) | `tools/souji-gate-check.py` check3 caps quotes at 25 words per gate line | Upper bound duplicated; the 4-word floor is new. |
| capability tool K2 (SHONEN pointer is a blob at REV, optional `:line`) | `tools/souji-declared-evidence.py` class A (backticked repo-relative path, optional `:line`, must exist at `--rev`) | Duplicate path-existence authority; K2 adds the line-count test and the correction layer. |

Merging the registry/declared-evidence overlaps would move an enumerated set, so they are **recorded for
round 31, not proposed for it**.

## 5. Proposals for round 31

**P1 — `tools/souji-wave-spec.py` (highest saving).** One renderer, `--round-dir <abs> --seats <json>`, seat
table as data; ship a `tools/souji-wave-spec.spec.md` binding spec in the style already used by
`tools/souji-verify.spec.md`. Replaces three files (325 lines) with one tool plus per-round JSON. Risk: the
generated spec is evidence (it lands inside the capture), so the renderer's own bytes must be pinned; pin the
renderer's sha256 in the round's `amendments`/records line the way `souji-receipt-run.py` pins tool blobs.

**P2 — one counter file per claim, amended in place.** Round 31 writes `census/round-31/<claim>-counter.py`
frozen at the prereg commit; an amendment edits it in place and `amendments.txt` records the **frozen blob's
sha256**. This is the lane's own licensed form — amendments.txt: "the frozen v1 instrument still runs
unchanged (from its preregistration blob" — and the r29 `tools/` precedent (`souji-registry-agreement.py:3`,
"AMENDED v2 (r29, stricter-only; the frozen v1 bytes are blob b8cb4b31"). It removes the `-v2` twin
convention and its reconciliation step (two `SUMMARY` formats, two runs, one claim).
Tradeoff, stated honestly: the sibling file keeps v1 runnable without an extraction step; the in-place form
requires `git show <prereg>:<path>` to re-run v1. The extraction is one command against a revision that is
already mandatory to cite.

**P3 — one controls file with an arm table.** `controls.sh --set frozen|amended`, arms as rows
(`C1-bypass`, `C1-banner`, `C2-stub`, `C2-cheat`, **`C3-typed-record`**, **`C3-stub-entry`**). Today the
amended file has C1 and C2 arms only (D2), and the A2 discriminators exist only inside seat receipts.

**P4 — teach `souji-coverage-agreement.py` exact ground tokens** (`--exact-ground`, stricter-only, with new
fixture cases for `F1` vs `F1-jj` on both the entry side and the map-row side). Then E1/E2 disappear from
every future C3 counter and the strictness lives in the one shared authority instead of a per-round copy.
Needs its own round and its own fixture delta; the r24/r25 contract makes an unflagged change to that tool
unavailable.

**P5 — REGRESS as case-id subset equality.** Today the C2 REGRESS leg requires base and REV selftest output to
be *identical*, which penalizes adding selftest coverage for new behavior and therefore forces the 554-line
external fixture to exist as a second test surface. Requiring instead "every case id present at base is present
at REV with the same verdict" lets discovery cases live in the gate's `--selftest`. Stated tradeoff: subset
equality is weaker than identity, so pair it with a case-count floor and a `CASE`-id set comparison, and
accept that this is a gate change needing the r16 fixture updated in the same round.

**P6 — parameterize the two round literals in the capability tool.** `--rows <path>` (default
`census/round-30/c1-rows.tsv`) and `--marker <prefix>` (default `R30`). Defaults preserve the frozen command
line byte-for-byte, so the frozen target stays runnable unchanged; only the reuse case changes. One line of
substance: `tools/souji-capability-agreement.py:8` "Each row of `census/round-30/c1-rows.tsv` (at --list-rev)
names a SCORECARD.md line".

### Stop condition — what must stay duplicated

The clone-at-rev + normalize + last-digit-line plumbing appears in four places
(`tools/souji-capability-agreement.py:77-91,149-160`, `census/round-30/c2-counter.py:33-60`,
`census/round-30/c2-counter-v2.py:42-77`, `census/round-30/c3-counter-v2.py:34,61-64`). **Do not extract a shared
library for it.** A frozen counter must stay runnable years later from committed bytes plus a Python
interpreter; a shared `tools/lib` would make round-30's instrument depend on bytes outside its own revision,
so a later lib edit would silently change what a re-run measures. Mutation-tester seats also mutate the
counter, not a library. This duplication is cheaper than the invariant it would buy back. The receipt-producing
form of the same primitive already exists as `tools/souji-receipt-run.py` and is the right route when the
artifact is a *record*, not a counter verdict (P4 above is the round-31 decision point, and it changes the
committed record format, so it is not a deletion now).

## 6. Defects found this run

**D1 (proven, not inferred) — `census/round-30/c2-counter-v2.py:69` `strip_err` can never strip.**
The regex is `re.sub(r"\terr=.*$", "", l)`; the line it must match is built by
`tools/souji-landing-gate.py:1423` as `exit=%d ids=%s paths=%s fleet=%s err=%s`, so `err=` is preceded by a
space, never a tab. Witness built from the committed format string:

```
line = "CASE\tpass\tno-reports\texit=1 ids=3 paths=2 fleet=0 err=no .md reports under ..."
strip_err(line) changed the line?  False
```

Consequence: the REGRESS-FULL leg compares exactly the free-text tail it documents as dropped. I did not run
the counter; the recorded L1 outcome (`regress_full=differs`) is consistent with this mechanism, and any pair
whose selftest error text differs will report `differs` regardless of behavior. `[INFERENCE]` on the outcome,
proven on the mechanism.

**D2 — `census/round-30/controls-amended.sh` has no C3 arm.** It defines `c3()` and calls it only for the
do-nothing base; the A2 discriminators (typed run record, stub entry, `F1-jj` token) have no committed control.

**D3 — `census/round-30/c3-counter.py:67,75` compares whole stdout strings for exact equality**
(`cov == "grounded=16 mapped=16 dangling=0 mismatches=0"`, `line == ["entries=1 ok=1 slice_verdicts=0 ..."]`).
Acceptable for a frozen one-round counter; it is the reason this file must not be reused as a template.

## 7. Observed, outside this seat's list (no proposal attached)

- `.ufo/waves/round-30/make-spec-w2.py` (93 lines) is the fourth generator copy; it enters the round-30
  capture unless P1 lands first.
- `tools/` holds 140 entries, 118 of them `cand-*.sh` probe scripts from earlier rounds (directory listing).
  Untouched here; that is the hygiene lane's own next-round decision, not an instrument question.

## Deliveries

This file only. No lane bytes changed by this seat.
