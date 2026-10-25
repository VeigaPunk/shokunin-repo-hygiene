# r15-preservation-frozen — pinned input for tools/souji-preservation-evidence.py

`record.json` is a DECLARED paired-evidence record for the r15 census-config
admission claim (schema `souji-preservation-record-v1`). `expected.json` pins
the record bytes plus the three measured payload digests under `--root <lane>`.

These pins were authored before the C1 repair of `tools/souji-census.sh`
landed. As shipped they describe a pre-integration snapshot, so evaluating
this directory against the post-integration lane correctly yields
`snapshot_tampered` (exit 2) until the integrator refreshes:

1. `record.json`: set `measured_commit`, `runs.changed.tool.commit`,
   `namespace_controls.tool.commit` to the integration commit; set
   `runs.changed.tool.sha256`, `namespace_controls.tool.sha256`, and
   `fixture.sha256` to the final file digests.
2. `expected.json`: set `record_sha256` to the new `record.json` digest and
   each `files` entry to the final payload digest; verdict `clean` is
   correct once the repaired tool and fixtures satisfy the pinned matrix.

A frozen input that does not match the live checkout is *not* silently
stale: the gate refuses it (exit 2) rather than admitting old evidence.
