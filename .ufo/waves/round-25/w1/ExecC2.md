# ExecC2 — round 25 C2 (operability): size-census refusal surfaces in the frozen fixture

Seat: L1Souji25.ExecC2 (leaf; no subagents, no labrat used). Lane base rev 6e4737eab43d8fde1b85eb9f57023d29046705b4.
Scratch: /var/tmp/souji-r25-ExecC2/ (copies of tool blobs + run outputs; no live lane writes beyond
this report, the draft and the receipts dir). tests/ and tools/ untouched (`git status --short tests tools` empty).
Installs/updates: none.

## Verdict

C2 draft meets all three validation targets.

| arm | --tool | last line | rc |
|---|---|---|---|
| green (tip) | tools/souji-size-census.py @6e4737e (sha256 c5690681…) | cases=12 pass=12 control=FALSE-GREEN-REJECTED lost_found=WRITE-DETECTED | 0 |
| red (OLD) | 1efe406e…:tools/souji-size-census.py (sha256 7ad5cc76…) | cases=12 pass=11 … | 1 |
| supplemental | 778747eb…:tools/souji-size-census.py (sha256 09bb8e0d…) | cases=12 pass=10 … | 1 |
| stub emitter as --tool | constant all-zero counts line | cases=12 pass=4 … | 1 |

Subset check: cases 1–8 lines of the green run are byte-identical to the r24 committed fixture
(sha256 373ef1f0…) run against the same tool (`SUBSET-8-IDENTICAL`), 8/8.

## Draft

`.ufo/waves/round-25/w1/r24-size-census.py`, sha256
`5bd7e74fb7344e2b583858eaeee761272aadc0d3a0a4cfbbec89fd8f68754238`.

Diff vs `tests/fixtures/r24-size-census.py` (373ef1f0…), insert-only apart from two lines:
- docstring line 2 retitled (`…, extended by r25 C2.`), plus 6 inserted docstring lines naming cases 9–12;
- `Scratch.invoke` (runs tool, returns full CompletedProcess + manifest delta) and `Scratch.bare`
  (git init --bare -b main; optional single commit via hash-object/mktree/commit-tree/update-ref);
- `has_counts`, `describe_proc`, `case_bare_nonempty`, `case_bare_empty`, `case_subdir`, `case_partial_only`;
- `CASES` list extended with the four new entries (the only changed code line).
Functions for cases 1–8, `case_control` body, `run`, `precondition`, `main`, `manifest`, `changed`
are byte-identical. The last-line format and exit rule are unchanged.

Case predicates (from the prereg; L1 design-probe outputs):
- 9 bare-nonempty: rc==0 AND last stdout line fullmatches COUNTS AND `census.invoked_from=bare`
  is a stdout line AND the bare git-dir manifest is unchanged.
- 10 bare-empty: rc==1 AND stderr contains `git failure` and `No default references` AND no counts line.
- 11 subdir (`--repo <worktree>/sub`): rc==2 AND stderr contains `--repo must name the repository itself`.
- 12 partialClone-only (`extensions.partialClone=origin` on a plain init): rc==2 AND stderr contains
  `partial-clone repository`.
Cases 10–12 report `manifest_changed` but do not gate on it (it is not in the frozen predicate).
Adding that gate would be a new spec, so it is up to L1.

## Red arm — which cases discriminate

- OLD 1efe406 fails **case 11 subdir** only (exit=0, a counts line, no refusal: the old tool resolved any
  subdir via `rev-parse`). Cases 9 and 10 **pass** on 1efe406 because the bare regression came in later.
- 778747e (where the bare regression landed; fixed in 315422b) fails **cases 9 and 10** (both exit=2
  refusal) and passes 11/12. That means the bare cases do catch the regression the verifier routed (R24-M24/D2).
- Case 12 passes on all three real tool blobs, so it is coverage only and does not discriminate between them.
  The stub emitter fails it.

Prereg note for L1: the C2 text says the red arm's "bare cases discriminate" against 1efe406. In fact,
1efe406 is caught only by case 11, and the bare cases discriminate 778747e. The frozen red-arm requirement
(fail >=1 of 9–12) is still met. ExecC2-2 independently got the same split (1efe406 fails 11 only;
778747e fails 9 and 10).

## Stub control

Case 8 (internal stub) unchanged: `stub_failed=dangling,garbage,alternates`. Using the stub as `--tool`
also fails 9–12, so each new case rejects a constant emitter.

## Receipts

`.ufo/waves/round-25/w1/ExecC2-receipts/`: `c2-green.tsv`, `c2-red.tsv`, `c2-mid.tsv`, `c2-stub.tsv`
(receipt=v1; rev, fixture path + sha256, --tool source + sha256, cmd, rc, utc, stdout, stderr).
All four were generated with the fixture at the canonical w1 path, sha256 5bd7e74f….

## Coordination

The sibling seat ExecC2-2 had the same item and briefly overwrote `w1/r24-size-census.py` (sha 9c8a512f…).
It moved its work to `w1/ExecC2-2/`. I then restored my draft and regenerated all receipts. Both drafts
score 12/12 at tip with the same red split; L1 picks one by sha.

## Disclosed limits (unchanged + new)

- The no-write envelope excludes atime/ctime, so a write that restores mtimes is invisible. Hostile
  config/env still have no case.
- Cases 10–12 do not gate on no-write (see above).
- Case 11 checks only a plain subdirectory, not a non-repository directory nested below a repository.
