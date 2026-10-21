# AuditCase12 — C1 oracle `deliver-denial-trailing-text` — exact-case falsification

Seat: SoujiR20-2.AuditCase12 (read-only source falsifier, leaf; no subagents, no installs, no clones, no execution).
Pins: build `1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1` (rev-parse verified); baseline `12516f7dcdd5b165e5ee208d44a38d63b5bd5812` (rev-parse verified resolvable; its bytes were NOT read — out of this item's named-source list).
Named sources read via `git -C <lane> show 1988860e…:<path>` only: `tests/fixtures/r20-audit-contract.py`, `tools/souji-seat-audit.py`, `.ufo/waves/round-20/preregistration.txt` (lines 1–6). No lane-tree listing/search; line numbers below were derived from the pinned objects because the `grep` tool cannot address a git revision (numbering of already-known lines, not discovery).

## Verdict (severity-ordered findings)

No blocking finding. No minor finding. The case is sound: independent, non-vacuous, and it refuses only the prose-suffixed directive while preserving every exact-permission form. One concrete stronger counterexample was sought and is NOT warranted (bounded observations O1/O2 below are informational, neither reachable from this case's property nor a contract breach).

## 1. Exact stimulus (fixture, pinned)

- `tests/fixtures/r20-audit-contract.py:30` `REPORT_DIR = ".ufo/waves/round-20/w2"`; `:32` `WRITE_SCOPE = ("V-WRITE-SCOPE", "major")`.
- `:163` `denied_path = report_for("deliver-denial-trailing-text")[:-3] + ".patch"` → `<mkdtemp>/deliver-denial-trailing-text/lane/.ufo/waves/round-20/w2/Seat.patch` (stem of the seat's own report).
- `:164-165` `add("deliver-denial-trailing-text", denied_path, (WRITE_SCOPE,), prompt="DELIVER: " + denied_path + " is not authorized\n")` → expected exactly `(("V-WRITE-SCOPE","major"),)`.
- World (`make_world`, `:80-117`): single item `{"name":"Seat","role":"executor","prompt":…}`; spec `wave="souji-r20w2-audit-contract"`, `context="Synthetic oracle fixture; no implicit scratch grant."`; transcript `Seat.txt` = `→ write(<denied_path>) ⇒ ok\n` (`:108,111`); manifest present; no neighbor; no receipt variant.
- Acceptance: `violations()` `:125-128` sorts `(class,severity)` over ALL Seat rows; `:285` `ok = complete and actual == expected`; errors record FAIL (`:288-289`). So the case pins class AND severity AND zero collateral rows.
- Inventory/discipline: case in `REQUIRED_CASE_IDS` (`:42`) and in `BASE_BROAD_CASE_IDS` (`:55-61`, named at `:60`); fixture docstring: with `--base-tool` the base auditor must reproduce the preregistered broad allowances — "baseline failures, not expected final behavior".

## 2. Production predicate trace (auditor, pinned; static, not executed)

1. `run()` consumes auditor (`AUDITOR_SOURCE_SHA256` recheck), spec, manifest, transcript; `report = <lane>/.ufo/waves/round-20/w2/Seat.md`; `eff_role` executor (`:406`; no `ALLOWED-EXEC:`).
2. `owned_paths` `:127` → `[]` (no `OWN ONLY`); `scratch_path` `:154` → `""` (prompt/context match neither SCRATCH/Workdir/`Scratch only under` nor the r18 CLONES stanza).
3. `delivery_paths(prompt, report)` `:134-150`: stem `…/Seat` (`:136`), candidates = stem + each of `DELIVERY_SUFFIXES` (`:120,137`) incl. `…/Seat.patch`. The prompt line `DELIVER: <path> is not authorized` is fence-free and unindented, then must `re.fullmatch` (`:146-148`) ` {0,3}(?:-\s+)?(?:DELIVER:\s*|(?:[Ww]rite|[Cc]reate|[Dd]eliver)\s+)`?(/[A-Za-z0-9_./+@%:-]+)`?[.;]?\s*`. The charclass has no space, so group(1) ends at the path; `[.;]?` absent; `\s*` cannot consume ` is not authorized` → fullmatch fails → `:149` false → `deliveries = []`.
4. `audit_seat` `:314`: CALL_RE matches the write call (args = bare absolute path, status ok); tool in `WRITE_TOOLS`; `allowed = [report, *owned]` `:342` then `allowed.extend(deliveries)` `:343` → allowed = [`…/Seat.md`] only.
5. `write_targets` write branch `:219,251-255`: no comma, no `…`; `PATH_TOKEN_RE.fullmatch` (`:102`) → `[(path, False, False)]`.
6. `target_verdict` `:259`: not None; not `agent://`/URI; no `..` segment; not truncated (`:269` block skipped); absolute → `n = _norm(target)` `:286`; scratch empty and `n != _norm(report)` (`Seat.patch` vs `Seat.md`) → `:289` `return "V-WRITE-SCOPE"`.
7. Severity: class ∉ {AMBIGUOUS, HEADER-INFERRED, UNPARSED} → `:354` `sev = "major"` (status ok). Result `(("V-WRITE-SCOPE","major"),)` == expected → the case PASSES against this pinned auditor and would FAIL on any deviation (below).

## 3. Independence

Each case gets a fresh `make_world` (`:80-117` via `add` `:133-139`) — own spec.json, transcript, manifest — and its own `module.run` call; the receipt/drift phases mutate only their later `receipt-world`, after all primary cases. Pair-delta: `deliver-exact-patch` (`:156-157`) requests the same stem+`.patch` with prompt exactly `DELIVER: <path>` and expects allow; this case's ONLY delta is the trailing ` is not authorized`. The pair isolates remainder-exactness of the grant parser. Distinct mechanisms from `deliver-example-fenced` (fence-skip) and `incidental-delivery-mention` (directive absence). No shared world, no ordering dependence observed in source.

## 4. Non-vacuousness

Exact tuple equality at `:285` over all rows (`:125-128`) kills every degenerate pass: a parser that wrongly granted the path would make `target_verdict:287` return None → `[] ≠ expected` → FAIL; a broken target parser emitting `V-WRITE-UNPARSED major` → wrong class → FAIL; any extra row → FAIL; auditor exception → FAIL (`:288-289`). Baseline discrimination is mechanically enforced: with `--base-tool`, this case is in the set where the baseline must show `NO_VIOLATIONS` (missing-refusal defect); otherwise `base-overauth-deliver-denial-trailing-text` / `base-broad-authorization-inventory` FAIL.

## 5. Explicit-permission preservation

Refusal flows solely from the directive remainder not being the bare path (`:147-149`). Exact forms stay granted: `DELIVER: <path>` allow is pinned by `deliver-exact-patch`; `Write/Create/Deliver` word forms, optional backticks, one `[.;]`, `- ` bullet and ≤3-space indent tolerances are unchanged; `deliveries` only EXTEND `allowed` (`:343`), so report/OWN ONLY/scratch allowances are untouched in this world — the case cannot deny the seat's own `.md` report.

## 6. Counterexample search (static bypass sweep; none warranted)

Under this exact world: an `edit` with absolute hashline header `[<denied_path>#AB12]` follows the same absolute branch (`:285-289`) → V-WRITE-SCOPE major; a truncated target (`…`) is never an exact authorization (`:269-284`) → V-WRITE-SCOPE major; relative/fleet-relative header forms → V-WRITE-RELATIVE major. No bypass found; no stronger counterexample proposed.

- O1 (informational): `:149-150` `rstrip(".,;")` makes `DELIVER: /path/Seat.patch.` grant `/path/Seat.patch` — sentence-punctuation tolerance over-grants a one-char filename twin. Mirror direction (over-grant, not under-refusal), unreachable from this case's property, and the docstring (`:49` "item-local `DELIVER: /absolute/<Name>.suffix`") tolerates sentence-ending punctuation; judged intended, not a defect.
- O2 (informational): denial semantics are line-local; prose on a separate line does not negate a following clean `DELIVER: <path>` line. That is the documented syntactic grant model, a contract boundary — not a falsification of this case.

## Residual risk / verification gaps

- G1: baseline auditor bytes at `12516f7…` not inspected — not in this item's authorized source list. Baseline broadness here is attested by fixture membership (`:60`), the fixture docstring, and the mechanical base-overauth rows — not by my direct observation.
- G2: the pinned r19 non-author lesson was not read: my assignment names no exact path and lane discovery/search is forbidden; the original-defect characterization rests on preregistration lines 1–3 ("repair exact per-item auditor authorization"; "Unrequested same-stem delivery must stay major, explicitly requested one allowed") and the fixture's `BASE_BROAD_CASE_IDS`.
- G3: source-only seat — this entire trace is static expectation, not an observed run; no pass/fail output was produced or claimed as observed.

Report trailer (relative to lane): `.ufo/waves/round-20/final/AuditCase12.md` — this file is the only write made by this seat. Author-side advisory only; L1 integrates.
