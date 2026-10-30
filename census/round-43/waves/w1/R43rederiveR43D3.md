# R43rederiveR43D3 — independent committed-byte review

Axes: calibration accuracy, evidence reproducibility, scope isolation.

## Commands and observed output

All three commands below completed successfully; no counter implementation was read or executed.

### Frozen register

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show f8c805dbfa7f45814cf9a7270fa8bbffb41a8373:census/round-43/c1-required.tsv
```

Relevant observed row (tab-separated):

```text
R43-D3	census/round-39/records/final-tip-measure.txt	header-rev	0242085909fb6a4ee041c5443d76316ac6d59d4b	544104503a3ad70687ba399fcafd12bd30648169	0242085909fb6a4ee041c5443d76316ac6d59d4b	receipt-header-rev
```

### Receipt at the register's revision

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 0242085909fb6a4ee041c5443d76316ac6d59d4b:census/round-39/records/final-tip-measure.txt
```

Observed output:

```text
# final-tip re-measure at 544104503a3ad70687ba399fcafd12bd30648169 (instruments and receipts unchanged since 2f6e981)
SUMMARY items=16 open=0 register_cells=6 register_mismatches=0 commit_distinct=6 items_sha=d892b74f8358
SUMMARY legs=6 pass=6 fail=0 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=e555d8281484
SUMMARY mutants=4 killed=4 survived=0 pristine=ok base_killed=0 cases=7 tool_sha=e48ed08e6728 fixture_sha=567c37a679f5
```

### Relevant tree difference

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --stat 5441045 0242085 -- census tools tests
```

Observed output:

```text
 census/round-39/records/final-tip-measure.txt | 4 ++++
 1 file changed, 4 insertions(+)
```

## Findings and verdict

- **Derived-value match: YES.** Independently reading the committed header at `census/round-39/records/final-tip-measure.txt:1` yields `544104503a3ad70687ba399fcafd12bd30648169`, exactly the frozen register's derived field.
- **Stale-value check: NO.** The receipt does not print the register's stale value `0242085909fb6a4ee041c5443d76316ac6d59d4b`; it prints `544104503a3ad70687ba399fcafd12bd30648169`. This attacks any assertion that the receipt itself claims the later revision. It does not invalidate a correction of prose that misattributes that receipt to the later revision.
- The requested stat comparison shows only the receipt addition under `census tools tests`, not a change to those tools/tests between the two revisions. It does not establish equivalence outside those paths or independently validate the SUMMARY measurements.

Residual risk / verification gaps: confined to R43-D3; R43-D1/D2 counting is outside this seat's target and was not performed. `read xd://lsp` returned `No such tool: xd://lsp`; semantic references/definitions/diagnostics were unavailable. This review uses direct committed data, not semantic caller claims. The working-tree register was also read at lines 1–4 before the frozen register was obtained; the D3 values agreed. No runtime, candidate scoring, fixture, installation, git mutation, or scratch directory was used. No tracked lane file was changed.

Self-evaluation: accuracy 5 (literal header and frozen row), completeness 5 (header, stat, derived match and stale check), clarity 4 (the stale field's prose provenance remains outside this target), actionability 5 (exact reproducible commands and scoped verdict), conciseness 4 (full four-line receipt retained for auditability); overall 4.6/5. Improvements: preserve the distinction between stale prose and receipt bytes in any downstream correction; omit unrelated SUMMARY lines if a shorter downstream summary is needed. User-agreement self-check: the requested independent D3 evidence is present without counter-code dependence.
