source: S302 — git-status(1), https://git-scm.com/docs/git-status (page header "git-status last updated in 2.53.0"; version list "2.54.0 -> 2.56.0 no changes"; sha256 af1fbb494104a6bcbfb44d65f8d75b2dad850fc9e9b5d43501cc2a6c995f58f6, 99934 bytes; captured census/round-69/srcs/git-status.html) and S303 — git(1), https://git-scm.com/docs/git (page header "git last updated in 2.56.0"; sha256 534c674f9929280db76c6f32bb3da5c6711b9475cb9dbb324cd88d2a2769f9d1, 244227 bytes; captured census/round-69/srcs/git-manual.html); and the round-69 counter census/round-69/c1-counter.py, frozen at 1412037c9fac1cd18381075d22fefbac06ae5bac (sha256 40757709e5adef00ef86c63fb4b554c03cce80e197747e389d76f58d4c2f5130), the manifest census/round-69/battery-manifest.tsv (sha256 8e7c3c0b819a33f4e87fe4b96bf07bb36fcdee443ba01159c2437df89a6e17ba) and the matrix census/round-69/c1-matrix.tsv (sha256 b173c9c93561b491a89d41c021d54ed0999753d414a2522097a0cf9764830b8b, 47 rows)
verified-at: 1412037c9fac1cd18381075d22fefbac06ae5bac (2026-11-05, host git 2.5x; sources accessed 2026-11-05; every number below re-derived by an independent seat run of the frozen counter at that commit, not copied from the L1's receipt)
recheck: `python3 -B census/round-69/c1-counter.py --root . --matrix census/round-69/c1-matrix.tsv --base-rev 3639087917eaeb28719d7603110a6ec22782100e --work DIR --battery-manifest census/round-69/battery-manifest.tsv --battery-dir census/round-69/battery` must emit `BATTERY mutants=26 kills=18 label_only=5 over_refusal=2 echo_violation=1 survived=0 error=0` and `EXIT=0`; the ambient half re-checks with `env -i PATH="$PATH" HOME=<dir with .gitconfig> XDG_CONFIG_HOME=<dir> GIT_TRACE=1 GIT_TRACE2_EVENT=<file> GIT_TRACE2_PERF=<file> python3 -B census/round-69/c1-counter.py --root . --matrix census/round-69/c1-matrix.tsv --base-rev 3639087917eaeb28719d7603110a6ec22782100e --rev 893b8ef4e73b3fde45f712df3437a032b1d92d42 --tool tools/souji-receipt-write.py --work DIR` twice (clean, then ambient) and `diff <(grep -E '^(CASE|SUMMARY|REGRESS|EXIT=)' CLEAN) <(grep -E '^(CASE|SUMMARY|REGRESS|EXIT=)' AMBIENT) | grep -c '^[<>]'` must print 0

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

## Why only forgery counts

The six classes are not six labels of equal weight. A forgery is the only class in which a row
expected to refuse was accepted — the writer produced a receipt over a state it had promised to
refuse, so the protection the row stands for did not hold. Every other class leaves the protection
intact and reports a different defect:

- `label-only` — the writer still refused, so the protection held; it named a different class than
  the row expected, which is a message-classification defect, not a protection failure.
- `over-refusal` — the writer refused a state the row expected it to accept. That is a false
  refusal, the opposite failure direction from the protection the row tests.
- `echo-violation` — the writer refused correctly but printed a caller value the row's `noecho_env`
  forbids. The refusal stands; the message leaks.
- `survived` — nothing was refuted at all: every row matched its expectation.
- `error` — the row could not be built or run, so it says nothing about the protection.

This is what Q131 already decided for the round-68 predicate, and round 69 mechanizes it: the
counter's own classifier implements the precedence above and the frozen manifest states each mutant's
expected class, so a kill count is a measured outcome rather than a hand label. The count this entry
reports is 18 — the number of *mutants* whose observed class is forgery, not a sum over rows. The
same receipt's `forgeries=` fields sum to a different number, because several mutants forge on more
than one row; a reader must take the class tally, not the per-row sum.

## What the split does not cover

- Protections with no honest single-edit row are named limits, not kills. D18 (`GIT_OPTIONAL_LOCKS=0`)
  is one, and D29 (`:(top)` pathspec) is another.
- D29 is a limit for a mechanical reason: every writer `ls-files` runs with `-C <toplevel>`, so the
  working directory is already the toplevel and dropping the pathspec changes no verdict.
- D18 is a limit for a different reason, and the reason is about the harness rather than about the
  writer's behaviour. The docs describe contention for background `git status`: S302 says

  > "Scripts running status in the background should consider using git --no-optional-locks status" (S302, git-status(1) § BACKGROUND REFRESH; raw byte 93859 of census/round-69/srcs/git-status.html; the section heading is at raw byte 93059)

  and S303 says

  > "require locks. This is equivalent to setting the GIT_OPTIONAL_LOCKS to 0" (S303, git(1) § OPTIONS, `--no-optional-locks`; raw byte 102863 of census/round-69/srcs/git-manual.html; the section heading is at raw byte 90637)

  The counter's own environment pins `GIT_OPTIONAL_LOCKS=0` for every git call it makes and for every
  writer slot it launches, so the mutant's deleted pin line is masked by the harness that runs it: the
  mutant's `git()` helper inherits the counter's `GIT_OPTIONAL_LOCKS=0` from the environment instead of
  setting it, and the resulting git environment is identical to the honest writer's. The pin is
  therefore not observable on this path at all, and the round's probe found git status rc 0 with empty
  stderr under a held `.git/index.lock`, with or without the pin
  (`census/round-69/probes/lock-and-commondir-probe.txt`). The pin remains declared and its battery
  outcome is `survived`.
- A battery is single-edit mutants of one candidate blob. It measures the protections the rows reach,
  not the protections declared in prose. The declared-coverage table
  (census/round-69/records/declared-coverage.tsv) names which declared protections have a battery row
  and which are limits.

## What this entry does NOT establish

- **No claim of ambient immunity in general, only under the frozen tuple.** The counter scrubs
  `HOME`, `XDG_CONFIG_HOME` and every `GIT_TRACE*` variable, and pins `GIT_CONFIG_GLOBAL` to the null
  device and `GIT_CONFIG_NOSYSTEM=1`, so the hostile `HOME`/XDG config files and the trace variables
  in the frozen tuple never reach a git call; that is what the zero-diff clean-vs-ambient comparison
  measures. It says nothing about ambient variables outside that tuple, and it is not a claim that the
  writer is immune to a hostile environment in general.
- **No claim that the S302/S303 sentences are about this writer.** The two quoted sentences are the
  documentation for git's optional-lock behaviour and its `GIT_OPTIONAL_LOCKS` equivalent. They are
  cited here to name the variable the D18 mutant removes and the documentation gap that gap leaves;
  they do not assert that `git status` writes a lock in the configuration this round measured, and no
  per-command lock behaviour is claimed beyond the two quoted sentences.
- **No claim about any mutant other than the 26 named in the manifest.** The battery is 26 single-edit
  mutants of one candidate blob; a protection that no mutant touches is not tested by it, and a
  protection with no honest single-edit row is a named limit rather than a kill.
- **No claim that the round-69 count is comparable to a round-68 count.** The two rounds ran different
  matrices (47 rows against 42) and different manifests, so "18 kills here" is not "more kills than
  round 68's 10"; the numbers are counts within a frozen predicate, not a trend.
- **No behavioural claim beyond the frozen predicate.** Every outcome here is what the frozen counter
  emitted on the frozen matrix and manifest at the named commit; this entry does not claim what the
  writer does on inputs no row reaches.

## Relation to the other rules

This entry adds a measurement rule to the existing ones: Q131 (a kill counts only through an outcome)
is now mechanized by the counter's classifier, and Q132 (a fixture row must build the shape its value
names) stays the rule that caught the round-68 W4 path error. The entry does not change the writer.
