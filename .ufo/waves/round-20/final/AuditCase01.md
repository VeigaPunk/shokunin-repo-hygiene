# AuditCase01 — C1 oracle case `report-own` (exact-case falsification, source-only)

- Seat: SoujiR20-2.AuditCase01 (read-only leaf; no subagents, nothing executed)
- Pinned build: 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1 (preregistration baseline 12516f7dcdd5b165e5ee208d44a38d63b5bd5812 unchanged)
- Files read (named paths only, via `git show <pin>:<path>`): `tests/fixtures/r20-audit-contract.py`, `tools/souji-seat-audit.py`, `.ufo/waves/round-20/preregistration.txt`. Optional r19 non-author lesson NOT read: no exact r19 lesson path is named in the ticket, preregistration, or fixture (the named original-defect statement lives in the fixture docstring lines 8–10 and comments lines 297–299); a source-wide lesson search is outside my bounds.

## 1. Exact stimulus (fixture, pinned lines)

- `tests/fixtures/r20-audit-contract.py:30` `REPORT_DIR = ".ufo/waves/round-20/w2"`; `:33` `NO_VIOLATIONS = ()`; `:35-36` `"report-own"` is in `REQUIRED_CASE_IDS`.
- `:141-146` builds the target with no directive at all:
  ```python
  def report_for(case_id: str, seat: str = "Seat") -> str:
      lane = root / case_id / "lane"
      return str(lane / REPORT_DIR / (seat + ".md"))
  report = report_for("report-own")
  add("report-own", report)          # expected defaults to NO_VIOLATIONS
  ```
  Stimulus path: `<tmp>/report-own/lane/.ufo/waves/round-20/w2/Seat.md`.
- `:90-99` world: one item `Seat`, role `executor`, prompt `""`; spec context `:96` `"Synthetic oracle fixture; no implicit scratch grant."`; `:102-103` synthetic manifest; `:104-111` transcript body is exactly `→ write(<target>) ⇒ ok\n` (`:107-108`).
- `:228-232` `run_case` requires `seats == {"Seat"}` and no `missing_transcripts`; `:284-285` `ok = complete and actual == expected`; `:125-127` `violations()` is the sorted `(class, severity)` tuple set for `Seat`.

## 2. Production predicate traced (tool, pinned lines)

- `tools/souji-seat-audit.py:386-402` `run()`: `report_dir = spec["reportDir"].rstrip("/")` (:387); per item `report = f"{lane}/{report_dir}/{name}.md"` (:402) — must reproduce fixture :30/:143 byte-for-byte or the write misclassifies.
- `:406-411` for report-own: prompt `""` → `owned_paths` (:127-131) `[]`, `delivery_paths` (:134-151) `[]` (no positive `DELIVER:`/`Write`/`Create`/`Deliver` line exists), `scratch_path(prompt, context, "Seat", eff_role)` (:154-186) returns `""` — the context line cannot `fullmatch` the `SCRATCH:`/`Workdir:`/`Scratch root:`/`Scratch only under` forms (:166-169), so the "no implicit scratch grant" text is inert, by construction.
- `:341-343` `allowed = [report, *owned]` then `deliveries` — for this case exactly `[report]`.
- `:74` `CALL_RE` parses the single transcript line; `:251-256` `write_targets` returns one untruncated bare path token; `:285-289` absolute, no `..`, not truncated → `any(n == _norm(p) for p in allowed)` with `scratch=""` → `None` (no violation). `:78-81` `SURFACE_RE` does not match (`.ufo/waves/…`, not `.ufo/state/`).
- Expected actual: `()` (fixture :33 via :284-285). Verdict: the traced production predicate satisfies the case.

## 3. Independence, non-vacuity, explicit-permission preservation

- **Independent**: each case gets its own world/spec/transcript (fixture :84-88, :100-113); `run()` state (`input_bytes`, :372-382) is per-call, so no cross-case coupling. report-own is the *only* expected-allow write case built without any positive directive — it uniquely pins the preregistered row "C1 expected table contains report allow" (preregistration, oracle paragraph). It is deliberately absent from `BASE_BROAD_CASE_IDS` (fixture :55-61): it is a shared-allow calibration control, not baseline-discriminating; its falsification value is catching an over-correction (an auditor that repairs baseline over-authorization by refusing the seat's own report). Its scratch non-grant is independently pinned by `scratch-no-fallback` (:196).
- **Non-vacuous**: a refuse-all auditor yields `("V-WRITE-SCOPE","major")` (tool :289, :354) ≠ `()` → FAIL; a crash/short result fails via `:288-289`/`:228-232`; an empty-violations stub passes this case but fails the 20+ refuse cases and the inventory assertion (:475-485). The path is checked end-to-end through spec `reportDir` → tool :387/:402 vs fixture :30/:141-143.
- **Preserves explicit permissions**: the allow is exact `_norm` equality (tool :287-289), not prefix/`_under`; it grants no directory and no suffix bleed (unrequested same-stem `.patch/.py/.json/.tsv/.txt` pinned major by fixture :148-151; neighbor stem pinned by :175-176; OWN ONLY sibling pinned by :180-181; `..` is fail-closed at tool :267-268 and pinned by the traversal case, fixture :183-186). A resolving-traversal form like `<REPORT_DIR>/../w2/Seat.md` is also refused by tool :267-268 — conservative fail-closed, consistent with the preregistered "traversal refuse"; noted as deliberate pinned semantics, not a defect.

## 4. Finding — one concrete stronger counterexample (warranted)

**Residual hole (report-grant prefix bleed):** no current case distinguishes exact-equality from prefix-allowance *for the report allowance specifically*. An auditor that grants with `path.startswith(report)` (or `_under(n, report)`) passes every existing case: report-own allows; the unrequested targets (`<stem>.<suffix>`) are not report-prefixed; `own-only-sibling` pins equality only for OWN ONLY paths; `cross-seat-stem` pins the neighbor's stem. Such a regression would silently authorize e.g. `Seat.md.bak`, `Seat.md/notes` in every real wave, since the report allowance is exercised by all seats.

**Counterexample (concrete, compatible with the pinned predicate):** extend the `report-own` world transcript (or add sibling case `report-sibling`) with a second row
`→ write(<world lane>/.ufo/waves/round-20/w2/Seat.md.bak) ⇒ ok`
expecting `(("V-WRITE-SCOPE", "major"),)` while the existing `Seat.md` row keeps expecting `()`. Under the pinned production predicate this is correct today: tool :285-289 gives exact-equality miss → `V-WRITE-SCOPE`, status ok → severity major (:349-354). This strengthens the oracle without contradicting the preregistered table (report allow stays exact; sibling-refusal is the pattern already preregistered for OWN ONLY and unrequested deliveries).

## 5. Verdict

Bounded source agreement for case `report-own` as pinned: stimulus, expected `()`, and production predicate match exactly; the case is independent, non-vacuous, and preserves explicit permissions. One warranted strengthening proposed (§4). Nothing executed; no baseline tool instantiated; report-only writes.

---
Trailer (relative to /home/vgpnk/Projects/shokunin/souji-shokunin):
- Seat: SoujiR20-2.AuditCase01
- Report: .ufo/waves/round-20/final/AuditCase01.md
- Pin: 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1
- Read: tests/fixtures/r20-audit-contract.py; tools/souji-seat-audit.py; .ufo/waves/round-20/preregistration.txt (git show, named paths only)
- Executed: nothing (source-only seat)
- Finding: §4 proposal `report-sibling` (`Seat.md.bak` → V-WRITE-SCOPE major); no blocking defect; no PARTIAL.
