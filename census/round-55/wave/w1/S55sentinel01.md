# S55sentinel01 — souji round 55 wave 1 — sentinel (write-scope + hardening review)

**VERDICT: CONDITIONAL PASS**

Report: .ufo/waves/round-55/w1/S55sentinel01/S55sentinel01-report.md

The r55 v4 counters are sound on every surface the preregistration claims to instrument.
CONDITIONAL on the L1 routing the acceptance-escape classes below into the round's
named-limit ledger and the r56 instrument work. No frozen byte was edited; each defect is a
named limit with a reproduction receipt. No finding invalidates either claim.

## Findings

| id | severity | surface | summary |
|---|---|---|---|
| S55-S1 | HIGH | C1 correction file | A NUL byte makes the file binary to git: the numstat binary marker `-` is reported as `deletions=-1` (a fabricated deletion, and the bogus corrections in the same file go unjudged, bogus=0); with the file unchanged base->rev the same bogus correction flips the verdict from exit 1 `BOGUS-RECOMPUTED` to exit 0. One byte flips the verdict. |
| S55-S2 | MEDIUM | C1 LOG/README pair scan | `hidden_lines()` opens an HTML-comment region on a `<!--` that is not at column 0, so a 4-space-indented (or nested) opener hides a live SOURCES overstatement from the pair scan: v4 exit 0 where the v3 arm still exits 1 `UNFILED-SOURCES-ANNOTATION`. A v3->v4 regression on this surface; the r54 disclosure only covers the fence side. |
| S55-S3 | MEDIUM | C1 correction lexer | A correction outside the {0,3}-space / one-line-wrapper tolerance (4 spaces, a tab, a nested `<!--`) does not lex, and a non-lexing correction is therefore never audited. The 4-space case is the task's stated expectation (must not lex) and is measured as such. Named limit; route to r56 wording + a committed boundary fixture. |
| S55-S4 | LOW | C1/C2 counters | Under a non-`-B` invocation the builder import writes `census/round-55/fixtures/__pycache__/` inside the lane, outside --work. All committed invocations use `python3 -B`; .gitignore covers it. |
| S55-S5 | LOW | C2 receipt grammar | The receipt KV regex requires a non-empty value (`\\S+?`), so an unknown key written with an empty value (`# BUILDHOST=`) is silently ignored instead of refused; the same key with a value is refused `RECEIPT-UNKNOWN-KEY`. |

## Clean results (task items 1 and 3)

- All six frozen pins verified byte-identical before and after the peer edits; the r54 v3
  acceptance-control counters also match their r54-published digests.
- No frozen byte edited; no commit/push/mutating git or jj; no write outside my scratch and
  seat dir; no pacman; no network; no tool install; no subagent dispatch.
- Lane worktree shows only peers' in-flight lesson/knowledge edits (none mine); the seat dir is
  gitignored (`.gitignore:1:.ufo/waves/`). Fleet root shows only orchestrator `.scratch/` files;
  no tracked fleet-root file is content-modified. Zero stray souji processes.
- Write scope: no `open(...,'w')`, no write_text, no mkdir outside --work; no network surface; all
  subprocess calls are argument-list form with timeouts and scrubbed git env.
- `--scratch` steers for BOTH counters (selftest with only --scratch: C1 `SELFTEST pass cases=27`,
  C2 `SELFTEST pass cases=15`, work tree under the --scratch path, exit 0). Pin refusal is
  fail-closed before exec: wrong builder/expected pin -> `CANNOT-EVALUATE PIN-MISMATCH`, rc 2.
- Real-lane legs at the measured revision reproduce byte-identically to the committed records
  (c1-tip.txt / c2-tip.txt), run from a scratch cwd with the lane worktree unchanged.
- Every exit=1 row of c1-matrix-v4.tsv (27) and c2-matrix-v4.tsv (13) names its finding;
  the v3 acceptance control kills none of the eight acceptance attacks (non-vacuous).

## Receipts

`.ufo/waves/round-55/w1/S55sentinel01/receipts/` — pins.txt, cleanliness.txt, writescope.txt,
attacks-nul.txt, attacks-hidden.txt, c2-emptykey.txt, harness/ (the four scratch harnesses
plus raw JSON results, kept as the reproduction scripts).
