## Status
STATUS: PARTIAL — both requested receipt directories are absent, so checksum and file-set verification cannot run.

## Evidence
- Revision observed: lane `HEAD` = `0c96332932e66bbaf9cf1c246091d3275a0ab612`.
- `sha256sum -c manifest.sha256` from `census/round-26/waves/` and `census/round-27/waves/`: both attempts returned `Working directory does not exist`.
- Existence/file-set check: round 26 `receipt=MISSING`, `live=present`, `summary=MISSING`, `file-set-diff=NOT-RUN (receipt unavailable)`; round 27 same.
- `git status --porcelain -- .ufo/waves | wc -l` returned `11`; tracked round-26 wave changes remain. These are not the requested final hygiene state.

## Findings
1. Required captured receipts for rounds 26 and 27 were unavailable at verification time. Consequently no `manifest.sha256` checks passed, relative file sets were not compared, and `summary.tsv` was not confirmed. Locations: `census/round-26/waves/` and `census/round-27/waves/` (absent); live sources `.ufo/waves/round-26/` and `.ufo/waves/round-27/` exist.

## Attack log
None.