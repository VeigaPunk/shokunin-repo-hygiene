# A receipt writer's clean-tree check must not be steered by a repository replace ref

source: S301 — git-replace(1) at https://git-scm.com/docs/git-replace (page header "git-replace last updated in 2.55.0", version list "2.56.0 no changes"; accessed 2026-11-05; HTTP 200; 38351 bytes html sha256 70ca75f4…; recipe-stripped text 6975 bytes sha256 96d141fd…) and S298 — git(1) ENVIRONMENT VARIABLES at https://git-scm.com/docs/git (opened 2026-11-05; committed capture census/round-66/sources/git-environment.txt, sha256 624e85ef…8035, GIT_NO_REPLACE_OBJECTS located-quote rows census/round-66/sources/quotes.tsv:12-13, offset 46334)
verified-at: 2026-11-05 at freeze commit 8b393b1911558932eab29e74635361256afdd6e3 (census/round-68/preregistration.txt); writer tools/souji-receipt-write.py at blob f70da577eb1e1624cc63ab8fd0468565927d9b6a, sha256 b811ee2a7a67d8d3ea6d00fb3a44780ccb807113b9eeaf28f09e01448715a725; host git 2.56.0
recheck: `python3 -B census/round-68/c1-counter.py --root . --matrix census/round-68/c1-matrix.tsv --base-rev 3639087917eaeb28719d7603110a6ec22782100e --rev f70da577eb1e1624cc63ab8fd0468565927d9b6a --tool tools/souji-receipt-write.py --work DIR --receipt FILE` must print `SUMMARY matrix=42 base_forgeries=2 base_honest=11 new_forgeries=0 new_honest=11 class_mismatches=0 regress=PASS` and exit 0 (the C1 Target block of census/round-68/preregistration.txt); row PK6 inside that receipt is this entry's re-verification point. The replace-ref source check is the S68ScoutReplace seat's report, .ufo/waves/round-68/w1/S68ScoutReplace/replace-check.md (its captures under that seat's `captures/`; the L1 mirrors them to a committed path at landing, as round 67 mirrored `.ufo/waves/round-67/w1/` to `census/round-67/wave/w1/`).

ground: F4-adjacent — receipt hygiene. The receipt writer decides "clean" by reading the repository through git, so any repository state that changes what git reads changes the verdict. A replace ref is such a state, and unlike an environment variable it needs no cooperation from the caller: it lives in the repository itself.

## Claim

A `refs/replace/` ref changes what git reads, by default:

> "Replacement references will be used by default by all Git commands except those doing reachability traversal (prune, pack transfer and fsck)." (S301, git-replace(1) § DESCRIPTION)

The same page states the documented way to turn that off:

> "The GIT_NO_REPLACE_OBJECTS environment variable can be set to achieve the same effect as the --no-replace-objects option." (S301, git-replace(1) § DESCRIPTION)

Both sentences were re-opened independently this round and match byte-for-byte in the recipe-stripped page text (S68ScoutReplace `captures/git-replace-recipe.txt`, and this seat's own re-fetch of the same URL: identical html sha256 70ca75f4…, identical stripped-text sha256 96d141fd…; located at text offsets 2896 and 3383, byte offsets 2953 and 3440). S298 records `GIT_NO_REPLACE_OBJECTS` as an entry of git(1) § ENVIRONMENT VARIABLES, with its located quote and byte offset (46334) in the committed capture census/round-66/sources/git-environment.txt (sha256 624e85ef…8035); the registry row is corpus/SOURCES.md row S298.

## Rule (round 66 C1, still the candidate's behaviour at round 68)

The receipt writer pins `GIT_NO_REPLACE_OBJECTS=1` on **every** git call it makes. The pin lives in the single `git()` helper — tools/souji-receipt-write.py:97-106, the assignment at line 104 — and every read goes through that helper (the call sites at lines 119, 158, 304, 347, 372, 381, 393, 414, 433, 494 and 495). The reason is the sentence above: with the pin absent, git reads the replaced object, so a repository whose HEAD is replaced by a forged commit can present a clean tree to the writer's dirty check.

The pin is a declared protection with a mutant of its own: census/round-68/mutate-writer.py:28-29 names mutant `K6` as "remove git() GIT_NO_REPLACE_OBJECTS=1 pin", and census/round-68/battery/SHA256SUMS carries its digest (698fedc2143cecdbd15a36e59da749ec598be344d020cd81930189afe08713b7).

## The fixture that exercises the route

Row **PK6** of census/round-68/c1-matrix.tsv (line 40) is `refuse` / `lane worktree is dirty`; its honest twin PK6h (line 41) is `accept` / `-`. The counter builds it at census/round-68/c1-counter.py:581-628: it writes a forged instrument blob, commits a replacement tree over the current HEAD, publishes `refs/replace/<HEAD>` (line 616), then puts the same forged bytes in the worktree and the index, so a replacement-honouring read sees a clean, matching tree while the real HEAD does not. The case is registered as `replace-ref-head` at line 322 and carries no caller environment (lines 710-712), which is the point: this route needs no environment at all. The counter's own header records the same expectation at census/round-68/c1-counter.py:32-37.

## What this entry does NOT establish

- **No claim about any command's behaviour beyond the two quoted sentences.** S301 states a general default and one exception class (reachability traversal: prune, pack transfer, fsck). This entry does not claim what `git status`, `git ls-files -v`, `git show`, `git fsck`, `git prune` or any other command does with a replace ref. The per-command man pages are silent on the matter — git-status(1) and git-ls-files(1) contain no occurrence of "replace" at all (S68ScoutReplace `replace-check.md`), so the only documentation basis for those commands is the general default-use rule quoted above, and this entry does not turn that rule into a per-command behaviour claim.
- **No claim on submodules.** Nothing here is measured for a submodule, a nested repository, a linked worktree or a superproject; the writer's own scope is the root repository it is given.
- **No doc basis is claimed for `GIT_REPLACE_REF_BASE`.** That name appears in neither git(1) nor git-replace(1) (S68ScoutReplace `replace-check.md`; the lane's own census records the absence at census/round-66/sources/absences.tsv:20). The writer refuses it by presence with `RECEIPT-ENV-REDIRECT-SET` (tools/souji-receipt-write.py:325; counter row E6, census/round-68/c1-counter.py:75-76), which is a caller-environment route, a different mechanism from PK6's repository-state route.
- **No behavioural claim is made here.** The dirty-check outcome of PK6 is measured by the counter run named in `recheck:`; this entry cites the fixture's committed bytes and the two documentation sentences, and asserts nothing beyond them.
