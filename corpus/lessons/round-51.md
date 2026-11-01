# Round 51 — the r50-closure routed record-accuracy corrections land append-only, and the session-workspace live census refresh

Fresh-start reading done first (round prompt §7): the last three REJECTED
closures (r43, r44, r45 — lessons) were re-read and spot-checked before
anything was declared; the ruling table is in the round report. The r50
non-author closure (round-50-verifier-spotcheck.md, verdict `ok, admitted`)
routed three items; the two lane-owned ones are this round's claim C1: item 1
(the duplicated `## Gate` "Reject sample" bullet in corpus/lessons/round-50.md
— fixed by the appended `R51-CORRECTION` line naming the duplication, the
duplicated bytes preserved verbatim, exactly as the closure directed: never an
in-place edit) and item 3 (the NTFS tip receipt omits the base's
`quoted_d_rows` line — fixed by the appended field plus a provenance note, the
six-path listing untouched, both proven by the frozen c1-counter's
listing/dup legs). Item 2 (the census conf-form rc-2 host state) stays
operator-owned (the consolidated r50 L0 proposal; routed around again,
nothing assumed answered). The closure also directed the standing
landing-suite receipt to run after the terminal repair — part of C1's target
this round. Claim C2 is the session-workspace live census refresh (the round
contract's census surface per the round dispatch). Two claims, two axes; C1
works the lowest non-retired axis (calibration 7). No exploratory claim.
Preregistration frozen before any claim receipt exists (freeze 851093b670e3fd1416df326d0479168222959ed1,
freeze-check claims=2 findings=0 at the freeze); do-nothing controls committed
control-first in the freeze commit. No wave was dispatched: this host has no
seat dispatch surface (standing L0 questions; dispatched=0, completed=0,
dead=0; no WAVE-DONE claimed; nothing assumed answered).

## Gate

- S274 admitted: https://git-scm.com/docs/git-cherry opened live 2026-11-01
  by this session (curl -sSL, HTTP 200, no redirect, 27219 bytes, sha256
  abe223069d94dda86990eaa958c684c18742e23bcfde026b2b0a576ad9ab73e3;
  full-page capture census/round-51/sources/s274-git-cherry-page.html).
  Located quote (15 words, counted by the pasted command in the capture —
  tags stripped display-faithfully with empty replacement, whitespace
  flattened): "git-cherry therefore detects when commits have been "copied"
  by means of git-cherry-pick[1], git-am[1] or git-rebase[1]." Context: the
  DESCRIPTION's preceding sentence states the equivalence test is based on
  the diff after removing whitespace and line numbers — git-cherry exists
  precisely to detect patch-equivalent (copied) history that sha comparison
  cannot see, which is the named limit of the workspace census's pushed
  receipt (HEAD vs the local refs/remotes/origin/master). The row was opened
  from the standing Leads list (which names git-cherry(1) as "a source of
  false negatives for the pushed receipt"). The page grounds the equivalence
  semantics only; the census's classification labels and default-ref shape
  stay the census's own method (S270). The page's version stamps ("git-cherry
  last updated in 2.0.5"; "2.1.4 → 2.56.0 no changes") confirm the served
  manual text matches the host's git 2.55 manual for this section.
- Reject sample (stated explicitly, the r48-closure carry-in practice): this
  Gate opens exactly ONE new source (S274, the only candidate fetched,
  admitted) and lands ZERO new reject rows. The sweep that bounds the reject
  sample to one fetch: the round fetched exactly one page (the capture above;
  the round-start census runs and the workspace census are local metadata
  reads, not fetches); no candidate was screened-and-rejected because none
  beyond S274 was opened; the Leads list item is discharged by S274's
  admission.
- Census before→after: before taken at round start both ways — raw adapter
  capture census/round-51/records/census-before.txt (adapter exit 0; the conf
  form's raw rc-2 `souji missing` verdict recorded inside — the documented
  host state, L0 open since r48) and the digest-bound v1 receipt
  census/round-51/records/census-before-receipt.txt (FLEET-SCRIPT-SHA256
  3fb72615…4e30, ADAPTER-SHA256 a159f2db…f74b, CONF-RC=2, DIR-RC=0,
  DIR-RESULT=ok, DIR-WARN-W04=59; `verify` ok over every check including both
  script hashes). After: the end-of-round receipt lands with the round's end
  receipts, exit 0 required.
- NTFS exclusion set re-derived at base: exactly the six pinned paths
  (census/round-51/records/ntfs-exclusion-check-base.txt, the r50 byte shape
  including quoted_d_rows=6). The inherited integrator-landing drift (the r50
  spotcheck file staged-deleted beside its untracked twin; porcelain receipt
  records/porcelain-at-base.txt, 8 rows) was repaired at round start this
  time — unlike r50, where in-progress round files forced the fail-closed
  refusal — receipt records/idx-repair-base-51.txt (BEFORE rows=8 -> AFTER
  rows=6 unexpected=0, exit 0); the tolerance is not widened. Repairs ran
  after every landing (freeze and end receipts receipts staged in session
  scratch per the r48 discipline); the terminal repair receipt is quoted in
  the round report.

## Mistakes

| class | evidence | captured-by | fix |
|---|---|---|---|
| a two-sided derivation that filters a TSV header row on one side only reads the format artifact as a workspace-drift row: the drift-file generation grep-filtered the `surface` header while the counter's key derivation parsed it as data, so the counter demanded a `REMOVED surface classification` row that is a table header, not a removed workspace surface (removed got=2 want=3) | the first pre-freeze feasibility green run of census/round-51/c2-counter.py over the synthetic tip: `DRIFT-KEYS-MISMATCH added got=79 want=79 removed got=2 want=3`, exit 1 | the pre-freeze feasibility leg (the r45/r50 discipline doing its job) | header rows are excluded in the counter's key derivation (single derivation source, both sides); the fixed counter's synthetic green run is the committed receipt records/feasibility-c2-green-synth.txt |
| a declared drift count whose derivation was not pinned to one definition reads 2 where the receipt says 1: `new-top-level-candidates` was derived as the whole top-level key delta (which includes the `scratch` container's own new classification row) while the receipt line counts only the new candidate root | the same first feasibility run: `DRIFT-COUNT-MISMATCH … ('new-top-level-candidates', (0, 2)) vs (0, 1)` | the pre-freeze feasibility leg | the receipt line's definition is pinned (new top-level surfaces classified `-NEW`, i.e. candidate roots) and the counter derives exactly that; a drift count whose class filter is not in its own line text cannot land |
| a line-anchored regex that assumes LF vacates itself on the host's CRLF receipts: the committed r50 sibling receipts carry CRLF line endings, so the quoted-path regex `^'".*"'$` matched nothing on either compared side and the listing leg compared two empty sets — a green leg that proves nothing | byte review of the staged NTFS base receipt vs the r50 blob (r50 `ntfs-exclusion-check-base.txt` ends `quoted_d_rows=6\r\ncount=6\r\n`); the pre-fix counter read listing=ok over receipts whose quoted-path sets were empty | the pre-freeze receipt review (the r50 lesson's numbers-without-listing class, caught one step earlier this time: before the numbers were derived at all) | both compared blobs are CRLF->LF normalized identically at read time in the counter (disclosed in its docstring); the fixed counters' synthetic green/red runs are the committed feasibility receipts |

Also disclosed, not mined as a fourth row: the workspace census's first take
included the host tooling dir `.zcode` (os.listdir sees dot-entries; the r46
comparable scope is non-hidden), breaking capture comparability (124 vs 126
rows); the take was discarded in session scratch and the scope rule is
disclosed in census/round-51/workspace-census.txt. And the live workspace
grew 86 -> 89 foreign scratch dirs between two r51 takes — a census row is a
point-in-time fact; the committed capture is the frozen one and the drift
receipt derives from committed bytes only.

Fresh-start sweep (three rejected closures, re-checked this round): r43's
shape was instruments-committed-before-preregistration (irreversible timing
defect) plus counters that could not bind their captured tokens — ruled out
by freezing prereg + counters + populations + controls in ONE commit before
any claim receipt exists, and by counters whose every value is parsed from
committed bytes at named revisions. r44's shape was a frozen predicate honest
work could not meet (register identities disagreed with the frozen counter) —
ruled out by deriving every target from states the base honestly exhibits
(blob absence, the routed defect's own text) and by pre-freeze feasibility
runs of every legged command against a synthetic tip containing exactly the
claimed byte shapes (which caught two real defects this round before they
could become frozen). r45's shape was the different-instrument limit — ruled
out structurally: the SAME counter bytes measure both arms (red at the base
rev, green at the tip rev; only the world moves), and both claims' repair
direction is the r50 non-author closure's own routed items plus the round
contract's own census surface, not new instruments invented to flip verdicts.

## Admission distinction

C1 is a record-accuracy repair landing a calibration verdict: the two routed
defects were textual (a duplicated bullet, a missing receipt field) and the
repair is append-only with the untouched bytes proven by the frozen counter
at both revs; plus the standing suite receipt restored to green at the tip —
the ordering the r50 closure directed. No new factual correction credit is
asserted beyond the routed items (the underlying records were already
correct or already disclose their state). C2 is a coverage move: the round
contract's census surface re-censused on the live workspace with per-artifact
receipts and a drift receipt whose every number re-derives from committed
captures; it runs installed tools over live targets (the r47 precedent — no
capability row), proposes no removal, takes no authority, and names its
pushed-receipt limit on S274. Numeric axis scores unchanged (calibration 7,
operability 8, coverage 8): no reproducible 0-10 mapping exists, no new
province surface, no Core promotion. Certification OFF, K5 HELD, NAMESPACE
and reap holds unchanged.
