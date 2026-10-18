# souji-shokunin operating rules

- Work only within this repo and its PROVINCE.md scope; sibling repos and
  domain source trees are read-only — census them, never modify them.
- Default to a dry run. Any removal requires a receipt (`pushed` /
  `moved-to-obsidian` / `stale`), quarantine staging, a hold period, and a
  second receipt check. No receipt, no removal — and when uncertain, the
  verdict is `NOT-SAFE`.
- Never rewrite history; never touch credentials or operator config; never
  touch an artifact whose owning lane has dirty or unpushed work.
- Every change is recorded in an append-only LOG.md entry with the evidence
  that motivated it. During a parallel wave, workers write only their
  assigned evidence fragments; the parent integrates them into LOG.md after
  the batch. Workers never race to append shared bookkeeping.
- Never fabricate evidence: cite a file, a command output, or a commit;
  claims you cannot verify are marked `to-verify`.
- Commit as `souji-shokunin <souji@shokunin.local>`.
