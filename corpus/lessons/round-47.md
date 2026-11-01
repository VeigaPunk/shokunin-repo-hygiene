# Round 47 — r46 carry-in corrections, standing suite receipt, per-artifact receipts

Fresh-start round on the Windows host. The last three rejected closures
(r43, r44, r45 — MANIFEST entries plus the committed reports) were read and
spot-checked before anything was declared; the rulings out are in the round
report. Two claims, two distinct axes; C1 works the lowest non-retired axis
(calibration 7). Preregistration frozen at 0027c977452e06d041a750a5a8c33b1fd5de57db
before any after-data existed; freeze-check reads claims=2 findings=0, exit 0;
both do-nothing controls are committed in the freeze commit (control-first).
No wave was dispatched: this host has no seat dispatch surface (standing L0
question, routed around; dispatched=0, completed=0, dead=0, no WAVE-DONE).

## Gate

- S270 admitted: https://git-scm.com/docs/git-clone opened live 2026-10-31 by
  this session (HTTP 200; capture
  `census/round-47/sources/git-clone-located-quote.txt`). Located quote
  (18 words): "Clones a repository into a newly created directory, creates
  remote-tracking branches for each branch in the cloned repository".
  Context: DESCRIPTION, first paragraph. Grounds only the naming half of the
  C2 reading: a clone's remote-tracking refs mirror the remote's own branch
  names, so the r46 census label `no-origin-master` records the upstream's
  default branch name (main), not an unreceiptable remote. The page never
  mentions `refs/remotes/origin/HEAD`; default-ref resolution stays
  tool-internal (tools/souji-verify.sh), not source-grounded. Page states
  "last updated in 2.54.0" with 2.55.0→2.56.0 no changes; host git is
  2.55.0.windows.3. Limits: documents naming, not verdicts; the receipts'
  verdicts are tool data, certification OFF.
- Census before→after: before
  `census/round-47/records/census-before.txt` — the explicit-lane-directory
  form, rc 0, 57 W04 duplicate-url warnings, `shokunin-repo-hygiene ok`;
  the contract's conf-name form stays rc 2 on this host (`souji missing`,
  PROVINCE host correction; this receipt is the host-valid base the r46
  report lacked — carry-in item 3). After: the end-of-round receipt
  lands in this round's final end-receipts commit, exit 0 required (the
  round-47 report carries the shas). SOURCES rows
  193 → 194 (S270 appended; no existing cell changed).
- Amendment-1 NTFS exclusion set (carry-in item 4) re-derived at the base:
  exactly the six pinned paths (`census/round-47/records/ntfs-exclusion-check-base.txt`),
  matching the campaign record `state/hyaku/ntfs-excluded/shokunin-repo-hygiene.txt`;
  tip re-check lands with the end receipts. Not widened.

## Mistakes

| class | evidence | captured-by | fix |
|---|---|---|---|
| integrator landing left the host worktree outside the frozen tolerance | after e469084b (the r46 spot-check commit), `git status --porcelain` here shows eight rows: the six tolerated control-char-named staged deletions PLUS a staged `D ` and an untracked `??` row for corpus/lessons/round-46-verifier-spotcheck.md (the file entered HEAD at e469084 but this host's frozen index never gained the entry). census/round-46/c1-counter.py's Amendment-1 tolerance covers only control-char-named HEAD paths, so the standing counter would exit 2 could-not-evaluate at every revision — the r46 "standing instrument" would have been dead on arrival | round-47 pre-flight: the L1 ran the frozen counter at the base before drafting C1 and hit `dirty worktree at run time: 2 unexpected rows` | targeted plumbing repair of the one named path: worktree bytes verified sha256-identical to the HEAD blob (0d1a4721…) first, then `git update-index --add --cacheinfo 100644,2162b581dc05f0075a8a0e61e57638576c6aeb1f,corpus/lessons/round-46-verifier-spotcheck.md`; porcelain restored to exactly the six tolerated rows; the counter then reads green at the base (`census/round-47/records/c1-base-green.txt`). No content change, no commit touched, disclosed here and in the report. Sweep for other drift found none beyond these two rows (same pre-flight). |
| tools/souji-verify.sh `find_repo_for` spins forever on this host for an artifact outside any git repository | the T4 (helpers-r74) receipt run never returned: two bounded probes exceeded 120 s with no output, and a bash worker burned 200+ s CPU. Cause: MSYS `dirname` bottoms out at `.` (dirname "C:/" → "C:", dirname "C:" → "."), so the walk-up loop's `= "/"` break never fires and `while :; [ -e "$d/.git" ] …` spins at "." — on Linux dirname "/" = "/" so the loop always terminated and the defect was invisible there | captured-by: the round-47 T4 feasibility probe (two 120 s timeouts) plus a per-level `-e` probe table (each ancestor answers in milliseconds; no `.git` exists up the chain) | minimal termination guard in find_repo_for (break on `/`, `//`, empty, `.`, or when `dirname` stops shrinking); on Linux the first stop is `/` — identical behavior. Consumer checks (Q73): `bash -n` parse OK; tool selftest base-vs-candidate in-place byte swap — identical exit 1, identical `47 checks, 8 failed` and the same failing case multiset (F6 + R9 family: pre-existing host baseline, not the repair; receipts `census/round-47/records/verify-selftest-{base,repaired}.txt` differ only in scratch paths and random fixture hashes); registered gate `bash tests/fixtures/r17-jj-receipts.sh --tool-dir tools` run with the repaired bytes (`census/round-47/records/r17-jj-receipts-repaired.txt`). The repair is strictly narrowing (termination only), committed before the T4 receipt it enables; the frozen preregistration text is unchanged. |

Fresh-start sweep (three rejected closures): r43's defect shape was
preregistration-after-ready-handoff plus instruments that cannot bind their
tokens — ruled out by freezing at 0027c977 with runnable, digest-pinned
instruments and red controls committed before any after-receipt. r44's shape
was a frozen predicate that honest work could not meet (registered=0) —
ruled out by deriving both targets from receipts that already exist at the
base (the r46 counter's own predicate) or are produced by running an
installed tool (the receipts), with targets reachable pre-data. r45's shape
was the different-instrument limit (0-to-green by swapping instruments) —
ruled out by re-using the r46 instrument unchanged for C1's standing
receipt; no new instrument is introduced this round, so no 0-to-green swap
exists. The full ruling table is in the round-47 report.

## Admission distinction

C1 is calibration of the record: the three routed r46 defects are bookkeeping
defects in already-filed artifacts; the correction rows make the filed record
match the receipts. No outstanding false-belief count changes beyond the
three named cells (the verifier had already re-derived 533 and 57 — the
round files the corrections the closure routed). C2's receipts classify four
live/protected targets; every verdict is NOT-SAFE, nothing is moved, deleted
or proposed for removal — coverage of the receipt surface over the r46
census rows, with the sourced naming half from S270. Numeric axis scores
unchanged (calibration 7, operability 8, coverage 8).
