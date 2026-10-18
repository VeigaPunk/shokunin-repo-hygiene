# souji-shokunin corpus

Memory of the fleet's hygiene state. Index rows are claims — write the row
when the file exists, not before.

## knowledge/

- `obsidian-ledger.tsv` — the Obsidian-preservation ledger. Columns:
  `source_path`, `source_sha256`, `vault_path`, `vault_sha256`,
  `exported_at`, `note`. A removal qualifies as `moved-to-obsidian` only
  with a matching row (both hashes). Rows enter only when the operator
  records an export; nothing automated writes here.
- (census tables land here from r1 onward)

## lessons/

- per-round training lessons, one file per round, each with a `## Gate`
  section (candidates / admitted / rejected / spot-check).

## Known gaps

- No census data yet (r1).
- No gate tool yet (r2).
- Numeric rubric: axis scores start at 0 with explicit counting commands;
  a calibrated numeric rubric is a standing gap, per the kotodama precedent.
