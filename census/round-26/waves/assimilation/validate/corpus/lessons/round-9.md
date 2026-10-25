# Round 9 — gate record
Declared: O1 (adversarial hardening), K1 (differential audit), C1 (numeric
rubric). Outcome: **REJECTED — O1 NOT-MET** (all four judges); K1 and C1
MET within bounds.

## What the strongest model did to us

23 root/invariant defect classes found (dedup'd union across judges), incl.:
disappearing-git → false metadata-prune; Turkish-locale `id_*` bypass;
ledger revocation after row capture (delete-after-revoke); NUL-in-list
authorization forgery; hidden live references missed by stale sweeps;
tab-spliced rows read as SAFE; nested dirty/unpushed repos deleted via
ancestor receipts; quarantine's second check missing default-ref
revalidation; linked-worktree HEADs making unique=0 wrong on git 2.55;
non--shokunin owner names hiding registrations; read-only contract
violation (index rewrites); SCORECARD numeric contradictions (parent's
own drift, corrected).

## State at closure

- S17 patches applied to the installed tools + shared selftest runner:
  selftests 40/51/91 + census 32; the S08 universe went 10→0 false-SAFE,
  7→0 false-DELETE. **But** fresh S09/S10/S11 replays still reproduce
  unsafe deletions on the patched tools (>=16 classes open per S24).
- S18's candidate variants (tools/*.r9-s18.* + guard): NOT promotable
  as-is (loses S17's NUL/ledger protections); compose in r10.
- rubric-final.md banked (S13-based merged scorer, 12/12 checks);
  current axis scores are LEGACY-UNMAPPED; new scores UNRATED.
- Dissent preserved (dissent-24.md): rubric zeroing semantics, dirty-file
  SAFE interpretation, exploration-vs-coverage.

## r10 mission

Compose S17+S18 repairs, close the open classes with the differential
corpora as the regression gate, re-freeze bytes, certify only what the
corpora pass. Deletion authorization stays OFF until then.
