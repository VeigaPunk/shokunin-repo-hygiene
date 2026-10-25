## Gate

- Candidates/admit/reject: [AFTER — L1 to fill from committed decision-time source snapshots and gate records].
- S119 decision: [AFTER — L1 to fill from the decision-time pin, digest, located quote, and committed disposition].
- F4 recheck: [AFTER — L1 to fill from comparison against `census/round-27/sources/SHA256SUMS`].
- Frozen gate context: preregistration requires opened-this-round POSIX.1-2024 `open()`, `rename()`, and `fsync()` rows S212–S214; S119 ADMIT requires S215, while REJECT requires reason and flip condition.

## Findings

- C1 precondition: frozen landing-gate baseline `findings=2`, checked_reg=52, at `3a2a80d0d18940a5e352ebc526da22a57dad83c4`; target is findings=0 without exemptions.
- C2 preconditions: grounded F4 4, registry rows 135; targets grounded F4 6, rows 138, gate ok=2, sources-census rc=0.
- C3 precondition: dirty `.ufo/waves` count 163; targets captured round-26/27 receipts, fixture six passing cases with tamper rejection, and dirty count 0. Base receipt presence and fixture results: [AFTER].
- After-state values: [AFTER — L1 fills only from committed tip evidence].

## Residuals

- [AFTER — L1 records unresolved issues from committed evidence; do not infer completion.]

## Receipts

- `census/round-28/records/preregistration.txt`
- `census/round-28/records/c1-before.tsv`
- `census/round-28/records/c1-control.tsv`
- `census/round-28/records/c2-before.tsv`
- `census/round-28/records/c2-control.tsv`
- `census/round-28/records/c3-before.tsv`
- `census/round-28/records/c3-control.tsv`
- `census/round-28/records/axis-check-before.txt`
- `census/round-28/records/s119-disposition.tsv`
- `census/round-28/records/log-entry-draft.md`
- `census/round-28/records/assimilation/collisions`
- `census/round-28/records/assimilation/staged-ids`
- `census/round-28/records/assimilation/reg-ids`

## Mistakes

- Exec-MistakeMine: [AFTER — no matching source was present among files opened for this draft; L1 to fill from the actual executor report if committed/present].

## Wave

- Shape placeholder: [AFTER — L1 records committed/present wave shape, report location, and receipt paths].
