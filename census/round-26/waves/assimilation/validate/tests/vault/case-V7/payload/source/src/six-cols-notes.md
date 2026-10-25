# Six-column control notes (case-V7)

Baseline control for case-V7: the ledger row for this note carries exactly
the six canonical columns (source_path, source_sha256, vault_path,
vault_sha256, exported_at, note). The source copy and the vault copy are
byte-identical and both match the recorded hashes.

case-V7 control: expected VERIFIED (proves a 7-column success is not the
result of a loosened parser).
