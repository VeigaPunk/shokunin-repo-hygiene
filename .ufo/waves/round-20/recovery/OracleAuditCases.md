# Round 20 — independent auditor oracle fixture

**Status: OPEN — the fixture is authored but deliberately unexecuted; the parent post-integration gate must run it.** No implementation blocker was observed in the read-only source review. No build, test, lint, formatter, smoke run, or target execution was performed.

## Scope and source findings

- The preregistered C1 oracle at `.ufo/waves/round-20/preregistration.txt:3` requires report allowance; major refusals for each unrequested `.patch/.py/.json/.tsv/.txt`; one explicitly requested exact artifact with its four sibling alternatives refused; cross-seat, OWN ONLY, traversal and slot-qualified scratch cases; receipt provenance for auditor/spec/manifest/transcript bytes; and rejection of read drift. The fixture asserts those primary IDs exactly, separately refuses incidental/denied/fenced delivery mentions, and requires the major unparsed result for a truncated target prefix inside granted scratch.
- `tools/souji-seat-audit.py:133-150` fullmatches standalone positive delivery directives and skips fenced examples; `:153-178` handles explicit scratch grants including historical `Scratch only under` and role-gated `CLONES`. `target_verdict` treats a truncated prefix inside scratch as `V-WRITE-UNPARSED` at `tools/souji-seat-audit.py:269-284`; `audit_seat` makes that major on success at `:349-355`.
- `tools/souji-seat-audit.py:70-72` pins auditor bytes at import; `:374-382` rejects differing bytes on repeated resolved-path reads; `:384-385` refuses a source mismatch before auditing; `:406-420` rechecks consumed bytes and returns SHA-256 receipts. The fixture checks the four-path receipt, reimports a changed source copy for a changed receipt, injects second-read drift for each input, tests an already-imported source copy after append, and aliases spec/transcript reads with controlled bytes to require the repeated-read refusal.
- The historical failure is documented at `corpus/lessons/round-19-verifier-spotcheck.md:66-70`. The frozen baseline auditor unconditionally adds every suffix at `/var/tmp/souji-r20-audit-12516f7/tools/souji-seat-audit.py:275-277`, making the five unrequested suffixes, four requested-artifact alternatives, trailing-denial directive, and fenced example its eleven named broad-authorization failures. Its per-seat scratch root is derived separately at `:309-326`; those scratch cases are not counted as baseline over-authorizations.

## Deliverable and verification boundary

Changed only the assigned fixture, `/var/tmp/souji-r20-audit-12516f7/tests/fixtures/r20-audit-contract.py`, and this exclusive report. The fixture creates only synthetic specs, transcripts, manifests, and auditor copies beneath a fresh `/var/tmp` directory; it does not execute transcript contents or write any audited target. It contains 37 required oracle/provenance case IDs, including the truncated-inside-scratch exact-class case, spec/transcript alias refusal, explicit-delivery denial/fence cases, literal r19w2 grant, generic-wave-name-only refusal, role-gated CLONES cases, and stale-import source refusal.

Per the wave instruction, this authoring seat did not run the fixture. There is no fresh execution receipt or observed pass count. Static case inventory predicts `SUMMARY total=50 pass=50 fail=0 base_discriminating=11` with `--base-tool`, and `SUMMARY total=38 pass=38 fail=0 base_discriminating=0` without it; these are expectations only. The migrated existing `r19-seat-audit-shapes.py` fixture, including its explicit DELIVER/SCRATCH and bounded shell-signal/root cases, remains a required separate parent acceptance check; it was not replaced or modified here.

Suggested parent command against the integrated auditor and this worktree's baseline auditor:

```text
python3 /var/tmp/souji-r20-audit-12516f7/tests/fixtures/r20-audit-contract.py --tool /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-seat-audit.py --base-tool /var/tmp/souji-r20-audit-12516f7/tools/souji-seat-audit.py
```

The parent should also run the preserved migrated `tests/fixtures/r19-seat-audit-shapes.py` from the integrated tree as a separate acceptance case, as directed by the coordinator.
