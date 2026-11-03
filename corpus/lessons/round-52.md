# Round 52 — declared-count annotations re-derived, and a read-only fleet-root census with a verifiable capture

Fresh-start reading: not applicable (round 52 of a lane with no streak block). The r51
non-author spot-check (corpus/lessons/round-51-verifier-spotcheck.md, verdict ok/admitted)
routed four items: defect 1 (the 78-vs-79 annotation) is this round's C1; defect 2 (the
freeze-commit message) is mined below; defect 3 is a prereg-plan note with nothing to fix;
item 4 (SHONEN boxes asserted by the author) stays operator-owned.

Claims (frozen in census/round-52/preregistration.txt, freeze df7d1300; base f778b9d1):
- C1 calibration 7 (the lowest-scoring axis): enumerated declared-count annotations agree
  with the recomputed value, each mismatch filed by an append-only R52-CORRECTION line.
- C2 coverage 8 (capability acquisition): tools/souji-fleet-root-census.py, a read-only
  census of the fleet root's top-level entries, with a committed capture verified by
  census/round-52/c2-counter.py.
No exploratory claim. No assimilation (shokuknow's merge/souji package stays held by the open
L0 question on mass id drift). considerthese/: no such directory in this lane.

## Gate

- Admitted: S275 — git(1) manual, environment variables, GIT_OPTIONAL_LOCKS.
  URL https://git-scm.com/docs/git; access date 2026-11-03; `curl -sSL` HTTP 200, 244355 bytes,
  sha256 0c126da2c94842a6118944dcf85b038dc8aeb1b7f344d9ffe820f551fab01664 (census/round-52/sources/
  s275-git-page.html). Located quote, 25 words, ENVIRONMENT section, entry GIT_OPTIONAL_LOCKS:
  "If this Boolean environment variable is set to false, Git will complete any requested operation
  without performing any optional sub-operations that require taking a lock." (census/round-52/
  sources/s275-located-quote.txt). Use is the census's read-only git calls (knowledge entry
  fleet-root-stray-census.md, "Why every git call sets GIT_OPTIONAL_LOCKS=0"). The variable's value
  `0` is the lane's boolean-false spelling; that spelling was not separately located.
- Admitted (knowledge): corpus/knowledge/fleet-root-stray-census.md, source S275.
- Rejected this round: none. Reject sample: the round opened exactly one page (S275). No candidate
  was screened and rejected, because none beyond S275 was opened. The discovery scan's three
  mismatches (LOG.md:18, corpus/README.md:40) are dated observations, not sources.
- Status changes old→new: none (no existing row changed; S275 is new, status mined).
- Quote check (independent): the located quote is a substring of census/round-52/sources/s275-git-page.html
  after tag stripping (scribe seat verify_quote.py; L1 re-check `grep -c` on the stripped capture).
- Spot-check result: pending the round's non-author closure (LEARNING.md). The lane does not
  claim it.

## Claim evidence

C1 (calibration). Before (base f778b9d1): `SUMMARY sites=2 mismatches=2 filed=0 unfiled=2`, exit 1
(census/round-52/controls/c1-control-donothing.txt). The two sites: SCORECARD.md:1196 and
census/round-51/preregistration.txt:125, both stating 78 for `grep -c "^ADDED"
census/round-51/records/ws-drift-vs-r46.tsv`, which recomputes 79.
Filing, appended to SCORECARD.md at the end: R52-CORRECTION lines for both sites. The frozen counter
at the content tip: see the round report's measurement table.

C2 (coverage, capability). Before: `PRISTINE FAIL FLEET-CENSUS-ABSENT`, exit 1
(census/round-52/controls/c2-control-donothing.txt). After: capture census/round-52/records/
fleet-root-census.tsv (ENTRIES=49, tracked 22, ignored 22, untracked-stray 5, symlink 0; untracked
strays .jj, .local, .ruff_cache, kumitate-shokinin, tools; all report-only), run receipt
census/round-52/records/fleet-root-census-run.txt, counter verdict in the round report.

## Wave findings (the 13-seat wave; attacks and what they changed)

- Reviewer01 (C1 counter attack, 18 runs): the frozen counter reads the FIRST annotation within 16
  characters after the anchor, so a planted `→ 79` before a stale `(78)` yields unfiled=0 with no
  correction; the recompute source is not pinned by the counter's own digest; a correction inside a
  code fence is accepted; an in-place rewrite of the stale annotation is accepted at one revision.
  Disposition: NAMED LIMITS of the frozen counter (counter not edited after freeze). The L1 checks
  the same holes at the tip by hand: exactly one annotation per site line (command in the report),
  base→tip SCORECARD.md diff has zero deleted lines, no correction line inside a fence, every
  correction names a line that reads its stale value. The amendment belongs to the next round.
- Critic01 (falsification): C1 survives; C1's kill rule is weakened for an inert correction (a
  correction naming a line that no longer reads its stale value exits 0 under the frozen counter,
  while the prereg text says it kills). The tip has no inert correction (checked by hand). C2 grammar
  survives; "verifiable capture" is weakened: a hand-written capture with the right tool bytes
  verifies (the counter binds grammar and tool bytes, not a run). Disposition: named limit; the run
  receipt is the provenance; a counter amendment is for the next round. "sorted by name" is
  uninstrumented (reversed rows verify).
- Reviewer02 (C2 spec attack): a `#`-leading data row is read as a comment by the counter; CRLF
  and tab-in-name captures cannot satisfy the grammar (no escaping defined); FLEET_HEAD is
  format-checked only. Disposition: named limits; the lane's capture has none of these shapes.
- Sentinel01 (security review of the candidate tool; findings S1-S8): S1 HIGH repo-local
  core.fsmonitor was EXECUTED by git ls-files during the census; S2 HIGH repo-local include.path
  made git open files outside the root; S3 HIGH no protected-namespace refusal; S4 MEDIUM the
  ignored set walked the operator-protected .ufo/state/ subtree; S5 MEDIUM credential-shaped
  names printed verbatim; S6 MEDIUM a timeout killed only the direct child; S7/S8 LOW --out inside
  the root, and a repo subdirectory accepted as root. Disposition: S1-S4, S6, S7, S8 FIXED in
  tools/souji-fleet-root-census.py (hardened lane copy; the wave candidate is not committed).
  S3 widened to a credential-name refusal and a credential-namespace refusal, both exit 2; S5 is
  refused rather than redacted, pending an operator ruling (l0-questions.md). Discrimination control
  for S1 (census/round-52/records/discrimination-s1.txt): the wave candidate executed a planted
  fsmonitor (marker written); the hardened tool did not.
- Connector01 (sibling overlap): no sibling claims the fleet-root census surface. It found the
  derivation gap: two honest derivations of `ignored` (listing vs check-ignore) disagree on three
  rows and both verify under the frozen counter. The lane tool keeps check-ignore because the listing
  walks the protected subtree. Named limit (knowledge entry, "Derivation of ignored").
- Scout02 (discovery scan of the six lane records): six annotated counting commands; three
  mismatches: SCORECARD.md:1196 (the C1 site S1), LOG.md:18 (dated 2026-10-18 worktree count;
  recomputes 1 from live state, not a transcription defect) and corpus/README.md:40 (self-dated and
  superseded in place). Only S1 is a transcription defect; S2 is the frozen prereg line. The two
  extra items are routed to the next round's census of dated observations, not counted here.
- Mutation01 (mutation test of the frozen C1 counter, six mutants on two arms): the two prescribed
  arms kill 2 of 6 mutants; the four survivors are killed by supplementary arms. The mutant with a
  200-character window inverts a fail-closed exit 2 into a measured value on one state. Named
  kill-power limit; the counter's logic holds on both prescribed arms.
- Executor03 (C1 feasibility): the frozen counter reproduces the preregistered numbers on a
  synthetic repo: unfiled=2 exit 1 before any correction; filed=2 unfiled=0 exit 0 after both
  correct corrections; unfiled=1 exit 1 with a wrong recomputed value.
- Executor01/02 (tool candidate and its fixture): selftest 34/34 and fixture 8/8 on the candidate;
  the hardened lane copy passes selftest 39/39 and the fixture 8/8 (controls fail for the named
  reason).
- Scribe01 (S275) and Scribe02 (knowledge entry draft): the S275 row and the draft entry; the lane
  corrected the draft's `verified-at` placeholder and the variable wording (the entry states that
  applying the variable to ls-files and check-ignore is the lane's reading).
- Scout01 (fleet-root recon): the 49-entry facts match the capture; kumitate-shokinin is an untracked
  directory whose name differs from the tracked kumitate-shokunin by one letter; no removal proposed.

## Mistakes

| class | evidence | captured-by | fix |
|---|---|---|---|
| a pasteable count annotation carried a stale value through a round: the r51 record states `grep -c "^ADDED" census/round-51/records/ws-drift-vs-r46.tsv` as 78 at two sites (SCORECARD.md:1196, census/round-51/preregistration.txt:125); the command recomputes 79 at the r51 base and tip, and the r51 SUMMARY `added=79` was right throughout. The r51 counter checked the SUMMARY and never the prose annotations beside it. | `python3 -B census/round-52/c1-counter.py --root . --rev f778b9d131574d3ff09c0cc8a077643c0fc84bb4` → `SUMMARY sites=2 mismatches=2 filed=0 unfiled=2`, exit 1 (census/round-52/controls/c1-control-donothing.txt); r51 spot-check defect 1 (round-51-verifier-spotcheck.md §8) | none (the r51 gate read the SUMMARY tuple only) | C1 counter, shown able to fail by the base control (unfiled=2, exit 1). Status at the tip: the two sites are filed by R52-CORRECTION lines; the stale text stays (append-only). The counter's first-annotation reading and unpinned recompute source are named limits (reviewer01); amendment for the next round. |
| a freeze commit's message names artifacts the commit does not contain: the r51 freeze message (851093b) says "S274 captures", but the two census/round-51/sources/s274-* files first land in the content commit d9aa24f. | `git -C souji-shokunin show --stat --format= 851093b` lists no sources/ paths; r51 spot-check defect 2 | none | none landed: commit messages are immutable, and the inaccuracy is named here. Process note for future freezes: write the message from `git diff --cached --stat` after staging. Not shown able to fail, so it is not counted as a fix. |
| a wave candidate shipped a git-config execution path: the round-52 candidate census ran `git ls-files` on the fleet root with repo-local core.fsmonitor enabled, so a repository-controlled program ran during a census, and its own selftest (34/34) passed because the selftest never planted one. | sentinel01 S1, `FSMONITOR-EXECUTED` marker and execve trace; discrimination control census/round-52/records/discrimination-s1.txt (candidate: marker written; hardened tool: no marker) | none (selftest coverage gap; no security review was in the candidate's acceptance) | every git call now carries core.fsmonitor=false and core.hooksPath=/dev/null, repo config with include/worktree is refused, and the selftest plants a fsmonitor and checks its marker (shown able to fail on the candidate's bytes). |
| a name-level refusal rule was broader than the namespace it protects: `.omp` was refused as a credential-shaped top-level name, but the fleet root's `.omp` is a tracked project OMP directory (agents/executor.md, mcp.json), not the credential namespace (`~/.omp/agent`). The fail-closed capture run caught it before any capture was committed. | the first real capture run: `REFUSED credential-shaped top-level name '.omp'` (exit 2) | the real-root capture run (fail-closed design working as intended) | `omp` removed from the top-level name rule; the root-namespace check still refuses roots under ~/.omp. Not yet shown able to fail with a dedicated control (open: the selftest's namespace case uses a home-root fixture, not a top-level `.omp`). |
| a kill rule in prose was not implemented by the frozen counter: the prereg says a correction naming a line that no longer reads its stale value kills C1, but the counter ignores such a line (exit 0) and reports only unfiled mismatches; critic01 probe. | critic01 attack (b); census/round-52/preregistration.txt C1 kill rule vs census/round-52/c1-counter.py | none | checked by hand at the tip (every correction names a line that reads its stale value; command in the report). The counter amendment (a new frozen version with the inert-correction kill) is the next round's claim, not an edit of this one. |
