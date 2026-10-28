# Round 40 — lesson (souji)

Round: souji round 40, hyaku run 11, attempt 3. Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Base revision (frozen in `census/round-40/preregistration.txt`): `0242085909fb6a4ee041c5443d76316ac6d59d4b`.
Non-author review read first: `corpus/lessons/round-39-verifier-spotcheck.md`.

## Gate — sources opened this round

Every row below was opened on **2026-10-28** by the L1 (the round's own access date; the campaign
package's dates prove nothing about this lane). The fetched bytes are pinned under
`census/round-40/sources/` with their sha256 in `census/round-40/sources/SHA256SUMS`.

| id | url | access date | located quote (<=25 words) | location | admitted for |
|---|---|---|---|---|---|
| S251 | https://git-scm.com/docs/git-merge-base | 2026-10-28 | "Check if the first <commit> is an ancestor of the second <commit>, and exit with status 0 if true, or with status 1 if not" | installed man page git 2.56.0-1, `MANWIDTH=100 man git-merge-base` lines 41-43; snapshot `census/round-40/sources/git-merge-base.1.txt` (sha256 `45f91e37e113df8651fb125c93e293bb48d8cc46140e4ac95c553547c9ddb043`) | C1's strict-descendant register arm and `corpus/knowledge/git-strict-descendant-relation-r40.md` |
| S252 | https://docs.python.org/3/library/inspect.html | 2026-10-28 | "Any whitespace that can be uniformly removed from the second line onwards is removed" | `inspect.cleandoc`, installed interpreter Python 3.14.8; snapshot `census/round-40/sources/inspect-cleandoc.txt` (sha256 `aab0711daa22215875bf559d3ce8d641062646d9946ad232dee70484e7b9a093`) and the page `census/round-40/sources/inspect.html` (sha256 `9e740c60462d2648ecd5b9ae1cf5ee96f2fed5e312fb56cae639385c5415a0d6`) | C2's joined class reading and `corpus/knowledge/docstring-class-continuation-lines-r40.md` |
| S253 | https://docs.python.org/3/library/codecs.html | 2026-10-28 | "Replace with a replacement marker. On decoding, use U+FFFD, the official REPLACEMENT CHARACTER" | § Error Handlers, the `replace` entry; snapshot `census/round-40/sources/codecs.html` (sha256 `023ec448648e7089efe4b4c25a167e491fa7f93d1cbf116662c6596e71158a4c`) | C3's invalid-UTF-8 record branch and `corpus/knowledge/drift-record-invalid-utf8-r40.md` |
| S254 | https://raw.githubusercontent.com/GNOME/gvfs/1.62.0/daemon/trashlib/trashitem.c | 2026-10-28 | "trashinfo = g_strdup_printf (\"%s/info/%s.trashinfo\", trashpath, basename);" | `daemon/trashlib/trashitem.c` at tag 1.62.0, line 158 (with lines 173, 180, 182, 193 for the group, the keys and the relative-path branch); snapshot `census/round-40/sources/gvfs-trashitem-1.62.0.c` (sha256 `3a8f8cbb057ac3bb8d4ba4901d43f8fd1abcd89b9ff095ef927999154af3d25b`) | the assimilated F4 entry `corpus/knowledge/origin-record-format-gvfs-r40.md` |

PEP 257 (`https://peps.python.org/pep-0257/`, § Multi-line docstrings) was also fetched and read this
round; it is screened and NOT cited: the `cleandoc` contract (S252) states the continuation rule
more precisely, and one row per source keeps the registry honest. The gate records it as a screened
non-row.

### Assimilation gate (`merge/souji/`)

- **ADMIT — staged entry `origin-record-format-gvfs-r26.md` (staged row id S146), re-pointed to this
  lane's S254.** The GVFS file was fetched and the quoted lines (158, 173, 180, 182, 193) read at
  tag 1.62.0; the entry was re-grounded by DOCUMENT, not by arithmetic: the lane's ids for the
  normative specification (S022) and for POSIX exclusive creation (S212) are named explicitly.
  Ground: F4, a second reference implementation that only READS the per-item origin record — new
  ground the lane did not hold.
- **REJECT — staged entry `near-duplicate-operating-point-r28.md` (staged row id S172, Manku et al.,
  WWW '07).** A published near-duplicate OPERATING POINT is document-similarity ground; the lane's
  F3 scope is byte-identical duplicates only, and the r24/r25 rounds refused the same family for the
  same reason. Flip: a lane ruling that adopts a similarity threshold for the `duplicate` receipt
  class would make this admissible.
- **REJECT — staged entry `fleet-prune-safety-r28.md` (staged row id S160, git v2.56.0
  `worktree.c`).** The lane already holds git's prune gate (`worktree.c` appears in 9 rows of
  `corpus/SOURCES.md`); adopting it again would be a duplicate, not new ground. Flip: none.
- **Id collision census (the reason the adoption is one entry and not a bulk append).** The §10
  command and its receipts are stored under `census/round-40/assimilation/`:
  `reg-ids` 177 ids, `staged-ids` 134 ids, `collisions` **58** ids (S109-S242), and every collision
  is a DIFFERENT document: the lane's S109 is its round-2 `RENAME_NOREPLACE` probe while the
  package's S109 is `git-fetch(1)`; the lane's S110 is `rename(2)` while the package's S110 is git's
  `builtin/fetch.c`. This is the mass id-drift case §10 sends to an L0 question
  (`souji | round-40`, filed in `.ufo/l0-questions.md`); only the one entry whose document the lane
  does not hold was adopted, with a fresh id.

## Mistakes

### M40-1 — the r39 C3 scoring contract could score a DETECTED mutant as SURVIVED

- **class:** instrument / scoring-contract defect (a kill verdict that is not earned).
- **evidence pointer:** `census/round-40/waves/w1/R40reviewer18.md` (wave-1 seat R40reviewer18,
  finding F1) — the committed r39 counter scores a kill at `census/round-39/c3-counter.py`
  (`crash = "Traceback (most recent call last)" in (proc.stdout + proc.stderr)`), while the committed
  r39 fixture ECHOES the tool's combined stdout+stderr into its OWN stdout
  (`tests/fixtures/r39-drift-record-rules.py:76`, `:79-80`, `:103-104`). A tool traceback is therefore
  laundered through the fixture's stdout and trips the crash probe, so a mutant the fixture DID
  detect is scored `killed=no`. The seat demonstrated the flip with one character of tool defect
  (`totol` for `total`): `killed=no` with the echo, `killed=yes` with both echo sites neutralised,
  same fixture bytes, same `fail=4`, same exit 1.
- **captured-by:** the r38 A5 contract (`census/round-38/preregistration.txt:189-195`): "a kill now
  requires the fixture's own `SUMMARY … fail=N` with `N > 0` and no `Traceback` on either stream".
  The rule was written for the FIXTURE's crash, and the r39 implementation applied it to the union of
  both streams — the criterion was right, the implementation read the wrong stream.
- **fix:** the r40 counter (`census/round-40/c3-counter.py`, `score()`) reads the crash marker from
  the fixture's STDERR ONLY — a Python traceback is written there and never to the fixture's stdout —
  and prints the failing case names so a kill is attributable to the branch case that covers it.
  **Shown able to fail:** the r40 battery's four mutants are scored `killed=yes` under the repaired
  contract while the same mutants are `killed=no` under the r39 contract (the seat's K1/K2 pair is
  reproduced by the r40 counter's own output, `census/round-40/records/c3-after.txt`).

### M40-2 — three calibration defects the round-39 spot-check routed to this lane

- **class:** calibration (self-assessment cells that do not match observed repo state).
- **evidence pointer:** `corpus/lessons/round-39-verifier-spotcheck.md` § "Routed defects the lane
  must fix next round" — D1 (the r39 "after" census receipt reads `rows=173` while the filed
  registry holds 174 rows, so the receipt cannot reproduce the filed number), D2 (the report says all
  three claims were re-read at the tip `0242085` while the receipt's own header names `5441045`),
  D3 (`commit_distinct=6` reads as six distinct commits when it is a ROW count over ONE commit
  hash).
- **captured-by:** the r37/r38 citation-reconciler contract (`tools/souji-citation-reconcile.py`,
  the `commit` arm and the receipt arm) — it binds a self-assessment cell to a receipt AND to a
  revision, which is exactly what D1 and D2 lack; D3 is a naming defect the same contract's register
  shape can carry (one row per cell, each naming its own expected token).
- **fix:** the r40 C1 counter (`census/round-40/c1-counter.py`) requires each anchored closure line
  to carry a resolvable, revision-bound evidence pointer and prints the register's row count and
  distinct-hash count as SEPARATE fields (`commit_rows=` / `commit_hashes=`); the r40 round re-measures
  the census after the final registry append and names the revision it measured. The three defects
  are the round's C1 items, and their closure lines carry their evidence pointers.


### M40-3 — the frozen C2 predicate did not freeze its pair set or the join grammar

- **class:** calibration / operability measurement-input defect.
- **evidence pointer:** `census/round-40/waves/w1/R40sentinel23.md` F1-F4, `R40sentinel11.md` (probe-name/oracle control), `R40executor14.md` (the chmod-0 probe changes class under a privileged runner), and `census/round-40/waves/w1/R40mutationtester08.md`. The r39 one-line analyzer already sees `EACCES` on the first `RECORD-MISSING` line at the frozen base; the preregistration did not freeze the synthetic docstring bytes, complete class/trigger pair list, entry-start/join rule, or a non-root observation precondition. The r40 L4 list was authored after the wave had scored.
- **captured-by:** the run's own pre-data-freeze rule (§9: “A rule changed after any seat has scored is not the claim's rule”) and the round contract's requirement that the frozen predicate, counter condition, and receipt label match. The r40 prompt required a “frozen list” but no list was in `preregistration.txt`.
- **fix:** none within this frozen round; do not rewrite the preregistration after scoring. The claim's counter and fixture measure one chosen reading (`census/round-40/records/c2-after-d.txt`), but the frozen claim remains **unprovable** because the observation set and join grammar were not declared before data. Future C2 claims must commit the exact list, probe bytes, entry-boundary grammar, and privilege/environment conditions in the preregistration before dispatch.

### M40-4 — the frozen C3 base-fixture identity is ambiguous and the pristine TOTAL contract disagrees with the tool

- **class:** calibration / coverage claim-definition and baseline identity defect.
- **evidence pointer:** `census/round-40/waves/w1/R40connector09.md` F1-F3, `R40connector21.md` F1-F2, `R40connector33.md` F1-F3, `R40connector45.md`, and `census/round-40/waves/w1/R40reviewer54.md`. “r39 base fixture” can mean the r39 battery's base input (`r38-drift-record.py`) or the r39 candidate fixture (`r39-drift-record-rules.py`), which already kills M11-M14. The r40 counter chose the latter; the frozen wording does not name that file. Separately, `tools/souji-worktree-drift.py:162-178` overwrites each TOTAL row, so a mismatching TOTAL followed by a matching TOTAL is accepted although the docstring at `:47-48` says a TOTAL row that disagrees is malformed.
- **captured-by:** the frozen-claim sizing rule (§9: one concrete after-state and one re-derivable counter), plus the fixture-contract rule Q85: each named branch needs a case whose assertion is load-bearing and a base fixture whose identity is pinned.
- **fix:** none to the frozen claim after data. The measured battery (`census/round-40/records/c3-after-d.txt`) proves its four chosen mutants against the chosen r39 fixture, but does not resolve the alternate baseline reading, retain the four prior mutants as regression controls, or test first-disagreeing/last-agreeing TOTAL order. Report C3 as **unprovable**, not as an admitted coverage move. Future preregistration must name the exact base fixture and include both TOTAL orderings; the tool-contract discrepancy is routed for a separately frozen repair.
## Frontier

- The round moved the lane's INSTRUMENTS, not the domain surfaces: F1 and F4 stay frontier, the
  four new knowledge entries sit on ground the lane already held, and no ground was promoted to Core.
- Remaining for the next round (from the r39 planned row): the C1 counter's evidence binding
  accepts any resolvable ancestor as the evidence revision — it does not yet require the evidence to
  be the receipt's own revision — and the C3 battery still scores four of the drift record's
  branches (comment/blank skipping, optional TOTAL) only through the r39 fixture.
- Certification OFF, K5 HELD, NAMESPACE hold unchanged.
