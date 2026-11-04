# S59Scribe — round-59 SOURCES row drafts (S286 mined, S287 rejected)

Draft only. No production registry, lesson, QUALITY, SKILL or census byte was
edited by this seat. Integration is L1 SoujiR59's sole authority.

Both rows cite the same opened source with distinct scopes, so the fleet census
reports the same-URL/different-scope W04 warning (not an E04 finding).

## Draft rows

Registry-shape rows (11 columns; `|` separators), ready to paste into
`corpus/SOURCES.md` `## Registry`:

| S286 | Python subprocess return codes — https://docs.python.org/3/library/subprocess.html | docs | A | public child-process return-code assertions in the assessment gate selftest | subprocess.CompletedProcess.returncode; Python 3.15.2 documentation opened 2026-11-04, curl -sSL HTTP 200 (no redirect) 208648 bytes, sha256 31f573c59a215fbad7e12dd81b41715f38b600eed240b84b9a42bd4e4a1685b1 (capture .ufo/waves/round-59/w1/S59Scribe/subprocess.html); located quote .ufo/waves/round-59/w1/S59Scribe/quotes.txt, 17 words | `Exit status of the child process. Typically, an exit status of 0 indicates that it ran successfully.` (located quote, 17 words) — child exit status is a separate attribute from captured stdout, so a gate selftest that asserts only printed findings cannot establish child success | mined | 2026-11-04 | on-release | corpus/lessons/round-59.md |
| S287 | Python subprocess check default — https://docs.python.org/3/library/subprocess.html | docs | A | rejected inference that check=False itself asserts the child's success | subprocess.run; check paragraph; Python 3.15.2 documentation opened 2026-11-04, curl -sSL HTTP 200 (no redirect) 208648 bytes, sha256 31f573c59a215fbad7e12dd81b41715f38b600eed240b84b9a42bd4e4a1685b1 (capture .ufo/waves/round-59/w1/S59Scribe/subprocess.html); located quote .ufo/waves/round-59/w1/S59Scribe/quotes.txt, 19 words | `If check is true, and the process exits with a non-zero exit code, a CalledProcessError exception will be raised.` (located quote, 19 words) — REJECTED: the documented exception is conditioned on check being true and the run() signature defaults check=False, so check=False asserts no exit status; flip: compare CompletedProcess.returncode with an independently persisted expected rc | rejected | 2026-11-04 | on-release | — |

## Scope distinctness (census W04 semantics)

Both rows carry the normalized URL `docs.python.org/3/library/subprocess.html`.
Their scope cells differ, so the census emits
`souji W04 S286 duplicate url docs.python.org/3/library/subprocess.html across scopes`
and the same for S287 — the same warning class as S261, which already cites this
URL under an env/stderr scope. No E04 (duplicate URL within one scope) is
reachable because the two scopes are not equal.

## Machine-checkable rows file

`rows.tsv` beside this file holds the same two rows in registry pipe shape.
`verify-quotes.py` checks each draft row against the captured page: quote
verbatim in the tag-stripped/entity-decoded/whitespace-collapsed capture, word
count at or below 25, anchor label present on the page, one shared URL, and
distinct scopes.

## Divergence from the uncommitted working-tree rows (reported, not applied)

The lane working tree already carries S286/S287 in `corpus/SOURCES.md`
(uncommitted at the time of this seat's read) and a `corpus/lessons/round-59.md`
Gate with located quotes. Two differences are reported for L1's decision:

1. The working-tree S287 `scope` cell reads "rejected inference that capturing
   stdout with the default check setting proves child success"; this seat's
   assigned scope is "rejected inference that check=False itself asserts the
   child's success". The working-tree `teaches` cell already states the
   check=False point, so the two cells describe one rejection with different
   scope wording. The draft above uses the assigned scope wording and keeps the
   two scopes distinct from S286.
2. The working-tree lesson records the S287 located quote as 23 words. The
   quoted sentence "If check is true, and the process exits with a non-zero
   exit code, a CalledProcessError exception will be raised." is 19
   whitespace-separated words (the counted token list is in `quotes.txt`). The
   r57 precedent is the same class of defect (S279 quote-2 recorded 17, later
   established 19).

Neither divergence was repaired by this seat: both files are production files
owned by L1.
