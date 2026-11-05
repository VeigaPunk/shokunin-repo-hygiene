# S62ReviewerCandidate — timeline (round 62, wave w1, delivered)

Verdict recorded in `report.md`: **SPEC: admit-with-named-limits**. sha256 of independent reconstruction: `c4f52dbe8a1a47092878a9a1fbc1965e17086596c708db6c737cf646be530736`.

## Delivered paths (absolute, all inside `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-62/w1/S62ReviewerCandidate/`)

- `report.md` — findings table F1–F16, verdict, named limits
- `ag-final.json` — full A–G + ordering/corrupt-index probe results (candidate and un-patched base control)
- `probe_ag.py`, `probe_names.py` — reusable probe sources

## Commands actually run (all with exit codes in hand)

- `git clone --shared -q …` rc 0; `checkout -q 16fa821…` rc 0; HEAD printed `16fa821fdce00e709d6895ccfc7aaffa465af195`
- base lane file sha256 `367a0ca3bdea35714f1c1dba7bca407f05e8ec8d8f6e9c16f071d6e20e503d2c` = lane copy (clone equal-identity confirmed before edit)
- `python3 -m py_compile clone/tools/souji-receipt-write.py` rc 0
- `git -C <lane> ls-files -v -z` + candidate parse → `{H: 17350}`, nonH=0, rc 0
- `python3 clone/tests/fixtures/r60-receipt-write.py --tool clone/tools/souji-receipt-write.py --work r60work` rc 0, `cases=8 pass=8 fail=0` with both controls rejected
- `python3 probe_ag.py clone/tools/souji-receipt-write.py base-tool.py agwork-final` rc 0 → matrix summary (see `ag-final.json`):
  A=ACCEPT/cand+base rc0 · B=ACCEPT rc0 · C=dirty rc2 · D=indexFlag rc2 (base=differs rc2) · E=indexFlag rc2 (base=differs rc2) · F=indexFlag rc2 (base=ACCEPT rc0, receipt written) · G=indexFlag rc2 when instrument properly bound (base=differs rc2); dirty+flagged falls to flag class with or without `--allow-dirty`; corrupt index → `fatal: index file corrupt` rc2, no receipt
- `python3 probe_names.py` rc 0 → dash-name, space-name, newline-name (via `update-index -z --stdin`), non-UTF8-name all refused rc 2 with `RECEIPT-INDEX-FLAG-CONCEALED:` prefix, path repr'd, no `--out` created; unit tag-census confirms any byte ≠ `H` refuses; end-to-end non-H tags other than S/h unreachable on this git (limit L1)
- GIT_INDEX_FILE env passthrough → `cannot read index flags of <root>: fatal: … index file smaller than expected` rc 2, `--out` absent (F11); not-a-repo root refuses earlier at rev check (F12)
- scratch `rm -rf` applied; delivery dir contains KEPT copies only

## Limits worth L1's attention

- F10 (ordering) and F12 (failure-path message precedence at not-a-repo roots) are spec-real findings: the frozen design's row orderings hold, but the `cannot read index flags` text only surfaces through index-level failures (or env passthrough), not whole-repo failures.
- Unconditional flag-refusal is intentionally strict: today's lane has 17350/17350 `H` entries (F1), so no honest run is blocked; the constraint is forward-facing.
