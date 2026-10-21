# Round 20 — independent auditor oracle fixture

**Status: OPEN — the fixture is authored but deliberately unexecuted; the parent post-integration gate must run it.** No implementation blocker was observed in the read-only source review. No build, test, lint, formatter, smoke run, or target execution was performed.

## Scope and source findings

- The preregistered C1 oracle at `.ufo/waves/round-20/preregistration.txt:3` requires exact per-item grants and refusal of unrequested artifacts, foreign-seat outputs, traversal, and ungranted scratch. The expanded fixture also checks positive grants for all supported delivery suffixes, OWN line/fence boundaries, scratch prefix separation, URI classification, comma-cut write targets, and edit MV destinations.
- The inspected parser surface is at `tools/souji-seat-audit.py:121-131` (OWN extraction), `:134-178` (delivery/scratch fence handling), and `:219-256` (edit target extraction). New cases falsify prose/fence grant leakage, sibling suffix leakage, missing MV paths, and hidden comma tails; call counts are compared to generated transcript-line counts, not a parser-mirroring regex.
- `tools/souji-seat-audit.py:70-72` pins auditor bytes at import; `:374-382` rejects differing bytes on repeated resolved-path reads; `:384-385` refuses a source mismatch before auditing; `:406-420` rechecks consumed bytes and returns SHA-256 receipts. The fixture checks the four-path receipt, reimports a changed source copy for a changed receipt, injects second-read drift for each input, tests an already-imported source copy after append, and aliases spec/transcript reads with controlled bytes to require the repeated-read refusal.
- The historical failure is documented at `corpus/lessons/round-19-verifier-spotcheck.md:66-70`. The frozen baseline auditor unconditionally adds every suffix at `/var/tmp/souji-r20-audit-12516f7/tools/souji-seat-audit.py:275-277`, making the five unrequested suffixes, four requested-artifact alternatives, trailing-denial directive, and fenced example its eleven named broad-authorization failures. Its per-seat scratch root is derived separately at `:309-326`; those scratch cases are not counted as baseline over-authorizations.

## Deliverable and verification boundary

Changed only the assigned fixture, `/var/tmp/souji-r20-audit-12516f7/tests/fixtures/r20-audit-contract.py`, and this exclusive report. It creates only synthetic specs, transcripts, manifests, and auditor copies under fresh `/var/tmp` data; no transcript command or audited target is executed. There are now 64 required primary case IDs, including 10 final controls for CLONES/ALLOWED-EXEC scope, URI and comma parsing, explicit suffix grants, foreign-seat delivery, and Seat2 scratch containment.

Per the wave instruction, this authoring seat did not run the fixture. There is no fresh execution receipt or observed pass count. Static case inventory predicts `SUMMARY total=77 pass=77 fail=0 base_discriminating=11` with `--base-tool`, and `SUMMARY total=65 pass=65 fail=0 base_discriminating=0` without it; these are expectations only. Baseline discriminators remain the eleven same-stem suffix over-authorizations. The migrated existing `r19-seat-audit-shapes.py` fixture, including its bounded shell-signal/root cases, remains a separate required parent acceptance check and was not modified here.

Suggested parent command against the integrated auditor and this worktree's baseline auditor:

```text
python3 /var/tmp/souji-r20-audit-12516f7/tests/fixtures/r20-audit-contract.py --tool /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-seat-audit.py --base-tool /var/tmp/souji-r20-audit-12516f7/tools/souji-seat-audit.py
```

The parent should also run the preserved migrated `tests/fixtures/r19-seat-audit-shapes.py` from the integrated tree as a separate acceptance case, as directed by the coordinator.
