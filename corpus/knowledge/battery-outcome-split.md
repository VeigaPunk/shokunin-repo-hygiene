source: S302 (git-status(1), https://git-scm.com/docs/git-status, anchor "BACKGROUND REFRESH", page revision "git-status last updated in 2.53.0") and S303 (git(1), https://git-scm.com/docs/git, anchor "OPTIONS", `--no-optional-locks` (dt anchor Documentation/git.txt---no-optional-locks), revision "git last updated in 2.56.0"); the battery counter census/round-69/c1-counter.py, frozen at 1412037c9fac1cd18381075d22fefbac06ae5bac
verified-at: 1412037c9fac1cd18381075d22fefbac06ae5bac (2026-11-05, git 2.5x on this host; sources accessed 2026-11-05)
recheck: `python3 -B census/round-69/c1-counter.py --root . --matrix census/round-69/c1-matrix.tsv --base-rev 3639087917eaeb28719d7603110a6ec22782100e --work <scratch> --battery-manifest census/round-69/battery-manifest.tsv --battery-dir census/round-69/battery` must reproduce `BATTERY mutants=26 kills=18 label_only=5 over_refusal=2 echo_violation=1 survived=0 error=0` and `EXIT=0` (census/round-69/records/c1-after-battery.txt); the source re-check is `sha256sum` of a fresh fetch against S302 af1fbb49… and S303 534c674f…

# A battery refutation is only a declared-protection kill when it is an outcome

A writer protection is "declared" in prose; it is "tested" only when a single-edit mutant of the
writer is refuted by a row of the matrix. The round-68 battery reported 14 of 14 refutations, and four
of them were not outcome kills. Round 69 splits every refutation into the class its rows actually
produced, so a count cannot be read off a label.

| observed class | what the rows show | counts as a declared-protection kill |
|---|---|---|
| forgery | a row expected to refuse was accepted (a receipt written over a refused state) | yes |
| echo-violation | a refusal printed a caller value the row forbids (`noecho_env`) | no (own line) |
| over-refusal | a row expected to accept was refused | no (own line) |
| label-only | a row was refused, but with a class other than its expected class | no (own line) |
| survived | every row matched its expectation | no (the protection is not tested) |
| error | a row could not be built or run | no (the battery fails) |

Precedence (the first class that has a row wins): error, forgery, echo-violation, over-refusal,
label-only, survived. The precedence is part of the frozen predicate: a mutant that both forges and
over-refuses is a forgery kill, and the over-refusal is still visible in its MUTANT line.

The battery's expected outcome per mutant is committed in `census/round-69/battery-manifest.tsv`. A
mutant whose observed class differs from its expectation fails the receipt (EXIT=1), so the class
split cannot drift silently. The round-69 receipt has 18 forgery, 5 label-only, 2 over-refusal and 1
echo-violation outcomes, with 0 survived.

## What the split does not cover

- Protections with no honest single-edit row are named limits, not kills. D18 (`GIT_OPTIONAL_LOCKS=0`)
  is one. The docs describe contention for background `git status`: S302 says "Scripts running status
  in the background should consider using git --no-optional-locks status (see git[1] for details)", and
  S303 says `--no-optional-locks` "require locks. This is equivalent to setting the GIT_OPTIONAL_LOCKS
  to 0". Two grounds, and both are required to read the `survived` outcome:

  1. **Harness artefact (S69Scribe, HIGH).** The counter's `clean_env()` pins `GIT_OPTIONAL_LOCKS=0`
  into every writer slot, so the D18 mutant inherits the counter's pin and hands git exactly the
  environment the honest writer hands it. No row in this harness could observe a lock-contingent
  verdict for D18, contention or not; a successor row needs a PK7-style caller-env override plus a
  contention-observable design.
  2. **Git behaviour on this host.** By default `git status` refreshes the index and writes it out,
  and the page says the lock held during that write may conflict with other processes (S302). The
  round's probe found git status rc 0 with the same output under a held `.git/index.lock`, with or
  without the pin (`census/round-69/probes/lock-and-commondir-probe.txt`); a GIT_TRACE2 probe shows
  the index write is skipped, not attempted-and-failed (`do_write_index` 0 vs 2). The docs do not
  say what happens when `index.lock` already exists, so the held-lock behaviour is undocumented on
  this host.

  The pin remains declared; its battery outcome is `survived`.
- D29 (`:(top)` pathspec) is a named limit for a different reason: the mutant drops `:(top)` from
  the flag-check `ls-files` only, and that call runs with `-C <toplevel>`, so its working directory is
  already the toplevel and the pathspec changes no verdict (S69Scribe verified the narrower scope).
- A battery is single-edit mutants of one candidate blob. It measures the protections the rows reach,
  not the protections declared in prose. The declared-coverage table (census/round-69/records/
  declared-coverage.tsv) names which declared protections have a battery row and which are limits.

## Relation to the other rules

This entry adds a measurement rule to the existing ones: Q131 (a kill counts only through an outcome)
is now mechanized by the counter's classifier, and Q132 (a fixture row must build the shape its value
names) stays the rule that caught the round-68 W4 path error. The entry does not change the writer.
