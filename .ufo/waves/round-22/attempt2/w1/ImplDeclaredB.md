STATUS: PASS

# ImplDeclaredB — second, independent candidate of `tools/souji-declared-evidence.py`

Seat: L1Souji22.ImplDeclaredB (leaf executor). Round 22 attempt 2, wave 1.
Claim exercised: C1 (calibration) as frozen in
`.ufo/waves/round-22/attempt2/preregistration.txt`. Base revision
`4edb25dfe262515d0da63224bbba71e02e36cba5`.

Axes named before the work: **calibration** (the instrument itself, primary),
**operability** (read-only, git-plumbing-only, `/var/tmp` scratch, typed
exit codes), **coverage** (every excluded candidate is enumerated with a
reason instead of silently dropped; no axis harmed). Every write in this seat
is confined to the named evidence directory and this report; the lane repo,
`.ufo/state`, the fleet root's `templates/`/`scripts/`, skipuknow and all
sibling repos are untouched. No git/jj write, no commit, no cleanup action.

## Deliverables and pins (executed)

```
$ sha256sum .ufo/waves/round-22/attempt2/w1/evidence/impl-b/souji-declared-evidence.py
021d90e9946a5cf6d9d82bf8d5d5f49286e4aa4dc1d5b08dd1e45c3ff1f6dcbc  .../impl-b/souji-declared-evidence.py
$ git cat-file -p 4edb25d:SCORECARD.md | sha256sum
b3cecc977b1cdc716c2bef030007983b5100498782cb307c46a69d6eb9682530  -
$ git ls-tree -r --name-only 4edb25d | grep -c .
3545
```

Evidence files (all under the named path):
`selftest.txt`, `base-counts.txt`, `base-assertions.tsv`, `base-skips.tsv`,
sha256 `bea2f404…` / `f02f5d32…` / `3be660e1…` / `f6b64231…` respectively.

Interface: `--root DIR --file FILE --rev REV [--format counts|tsv|skips] [--selftest]`.
`--format counts` prints exactly one stdout line; `--format tsv`/`skips` are
diagnostic (tsv = frozen assertion rows, skips = the reconciliation view) and
also end with the same counts line. Exit 0 iff `mismatches == 0`, 1 if
`> 0`, 2 on tool error (verified: invalid `--rev` → exit 2). Scratch is
`mkdtemp(dir="/var/tmp")` with a hard refusal if the path does not start
`/var/tmp/`, removed in a `finally`; no `/tmp` use anywhere. No network;
subprocess is git plumbing plus `init/add/commit` inside the selftest
scratch repo only. No tool installed, no package transaction.

## Selftest transcript (executed, verbatim from `evidence/impl-b/selftest.txt`)

```
# selftest transcript: python3 -B souji-declared-evidence.py --selftest
fixture 1 all-good                         assertions=5 resolved=5 skipped=0 mismatches=0 (want mismatches 0) PASS
fixture 1 class coverage                      assertions=5 classes=['A', 'B', 'C'] PASS
fixture 2 nonexistent path                 assertions=1 resolved=0 skipped=0 mismatches=1 (want mismatches >0) PASS
fixture 3 dangling revision                assertions=1 resolved=0 skipped=0 mismatches=1 (want mismatches >0) PASS
fixture 4 wrong digest                     assertions=2 resolved=1 skipped=0 mismatches=1 (want mismatches >0) PASS
fixture 5 path only at other rev           assertions=1 resolved=0 skipped=0 mismatches=1 (want mismatches >0) PASS
control always-zero rejected               PASS (4/4 red fixtures reject mismatches=0)
counts line format                          PASS (assertions=5 resolved=5 skipped=0 mismatches=0)
exit-code semantics                       PASS (M=0 -> 0, M=2 -> 1)
selftest 8/8 PASS
control=FALSE-GREEN-REJECTED
selftest_exit=0
```

Five fixtures on a synthetic repository under `/var/tmp` (three commits:
base, removal of `docs/old-only.md` + addition, then the fixture documents).
Fixture 1 additionally requires `assertions=5` and all three classes present,
so a parser that drops B or C but still prints `mismatches=0` fails. The
always-zero control is rejected by fixtures 2–5, four independent red
behaviors.

## Base run (executed)

```
$ python3 -B .ufo/waves/round-22/attempt2/w1/evidence/impl-b/souji-declared-evidence.py \
    --root . --file SCORECARD.md --rev 4edb25dfe262515d0da63224bbba71e02e36cba5 --format counts
note: worktree SCORECARD.md differs from 4edb25dfe262515d0da63224bbba71e02e36cba5:SCORECARD.md; auditing committed bytes
assertions=54 resolved=51 skipped=25 mismatches=3
counts_exit=1
```

`M_before = 3 > 0`, exit 1 — the preregistration's before-condition holds.
The three mismatches are the three the scorecard itself names as repaired:
`AXES.md` (fleet-relative pointer), `reason-after.txt` (unnamed receipt), and
`.ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md` (absent banked file).
Rerun is byte-identical (determinism checked twice).

Declaration-byte provenance is visible in the run: the worktree SCORECARD has
already been edited by a sibling seat (`git diff --stat 4edb25d -- SCORECARD.md`
→ 15 insertions/6 deletions), and its `reason-after.txt` cell now sits on
line 68 as `census/round-21/reason-after.txt`. This run reports line 63,
which is base's line: the tool audited `4edb25d:SCORECARD.md`, not the
worktree, and said so on stderr.

## Per-assertion TSV (executed, verbatim from `base-assertions.tsv`)

```
3	AXES.md	A	mismatch:path-absent	not in tree at 4edb25dfe262515d0da63224bbba71e02e36cba5
14	41553adb139d06511dc386bb3ce4326aebfba675	B	resolved	commit/object resolves
14	b912328d00d19f26918240710d0b5e0f334880ff	B	resolved	commit/object resolves
19	census/round-21/r20-closure-excerpt.json	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
21	census/round-22/r21-closure-excerpt.json	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
28	corpus/lessons/round-12.md	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
37	census/round-14/cache-demonstration.py	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
39	corpus/lessons/round-13-verifier-spotcheck.md	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
45	census/round-1/census-summary.json	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
45	census/round-1/census.tsv	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
46	census/round-13/verification.json	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
46	tests/results/INSTALL.json	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
46	tests/results/parent-harness-live.json	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
46	tools/souji-verify.sh	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
47	census/round-3/seat-61.json	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
47	census/round-3/seat-62.json	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
48	census/round-13/verification.json	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
48	tests/results/parent-vault-battery.json	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
48	tools/souji-vault-verify.sh	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
49	31984f4	B	resolved	commit/object resolves
49	census/round-13/verification.json	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
49	corpus/SOURCES.md	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
50	tests/results/r12-maintenance-guard.txt	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
51	census/round-13/verification.json	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
52	census/round-13/verification.json	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
53	corpus/knowledge/git-repo-structure-readonly.md	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
54	census/round-14/verification*.json	A	resolved	3 match(es) at 4edb25dfe262515d0da63224bbba71e02e36cba5
54	corpus/lessons/round-14-verifier-spotcheck.md	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
55	census/round-16/c1-matrix-final.json	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
55	corpus/lessons/round-16.md	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
56	corpus/lessons/round-16.md	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
57	census/round-21/oracle-acceptance.json	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
58	census/round-17/c1-matrix-4f48343.json	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
59	5fa6017	B	resolved	commit/object resolves
59	census/round-17/jj-receipts-*.txt	A	resolved	2 match(es) at 4edb25dfe262515d0da63224bbba71e02e36cba5
61	census/round-18/c1-matrix-4800fd7.json	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
62	census/round-18/final-verification-4800fd7.json	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
63	reason-after.txt	A	mismatch:path-absent	not in tree at 4edb25dfe262515d0da63224bbba71e02e36cba5
64	census/round-19/c1-carry.txt	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
64	tests/fixtures/r19-carry-wrap.py	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
65	tests/fixtures/r19-rev-pin.py	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
68	census/round-21/accepted-matrix.json	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
75	tools/souji-vault-verify.sh	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
77	.ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md	A	mismatch:path-absent	not in tree at 4edb25dfe262515d0da63224bbba71e02e36cba5
88	corpus/lessons/round-16.md	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
97	corpus/lessons/round-17.md	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
98	corpus/lessons/round-17.md	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
99	corpus/lessons/round-18.md	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
100	.ufo/waves/round-18/w1/ScoutCarryWrap.md	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
101	census/round-19/final-verification-63bb887.json	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
101	corpus/lessons/round-19.md	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
104	census/round-22/r21-closure-excerpt.json	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
122	census/round-10/cert-16.json	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
129	corpus/lessons/round-14-verifier-spotcheck.md	A	resolved	present at 4edb25dfe262515d0da63224bbba71e02e36cba5
assertions=54 resolved=51 skipped=25 mismatches=3
```

## Skipped candidates, with reasons (executed, verbatim from `base-skips.tsv`)

```
13	tests/fixtures/r21-reason-canary.sh	-	skipped	path token inside a command span
13	tools/souji-proc-census.sh	-	skipped	path token inside a command span
14	41553adb139d06511dc386bb3ce4326aebfba675:census/round-21/run-acceptance.py	-	skipped	path token inside a command span
14	census/round-21/run-acceptance.py	-	skipped	path token inside a command span
14	census/round-22/mutation-adequacy.py	-	skipped	path token inside a command span
14	census/round-22/mutation-adequacy.py	-	skipped	path token inside a command span
14	tests/fixtures/r22-result-oracle.py	-	skipped	path token inside a command span
32	census/round-13/run-verification.py	-	skipped	path token inside a command span
33	6f8ee0f	-	skipped	hex token outside a table cell (class B/C are cell-scoped)
35	census/round-N/<new>.json	-	skipped	path token inside a command span
50	tests/fixtures/r12-maintenance-guard.sh	-	skipped	path token inside a command span
51	tools/souji-cert-evidence.py	-	skipped	path token inside a command span
52	tests/fixtures/r13-quarantine-bounds.sh	-	skipped	path token inside a command span
53	tests/fixtures/r13-repo-structure.sh	-	skipped	path token inside a command span
53	tools/souji-repo-structure.sh	-	skipped	path token inside a command span
56	tests/fixtures/r16-landing-gate.py	-	skipped	path token inside a command span
56	tools/souji-landing-gate.py	-	skipped	path token inside a command span
58	tests/fixtures/r17-census-hygiene.py	-	skipped	path token inside a command span
58	tools/souji-census.sh	-	skipped	path token inside a command span
59	tests/fixtures/r17-jj-receipts.sh	-	skipped	path token inside a command span
60	census/round-17/seat-audit-replay.py	-	skipped	path token inside a command span
60	census/round-17/transcript-manifest.py	-	skipped	path token inside a command span
65	tools/souji-rev-pin.py	-	skipped	path token inside a command span
87	corpus/lessons/round-{6..11}.md	-	skipped	brace pattern, not a * glob over tracked files
105	29c1f7e8df849be8ee1b2d62d2351e17ec9d21a8	-	skipped	hex token outside a table cell (class B/C are cell-scoped)
assertions=54 resolved=51 skipped=25 mismatches=3
```

`N + S = 54 + 25 = 79` candidates enumerated; every candidate is either an
assertion (resolved or mismatched) or a skipped row with a reason. The
`N = R + M` invariant is asserted in code.

## Where this strategy can disagree with a raw-text scanner

This candidate splits a table cell into backticked spans first and classifies
each span; a raw scanner reads the same bytes in token order. The observable
differences on this document, all executed:

1. **Prose revision tokens (lines 33 and 105).** `6f8ee0f` (“named measured
   revision `6f8ee0f`”, prose) and `29c1f7e8df849be8ee1b2d62d2351e17ec9d21a8`
   (“Preregistration `…`”, bullet) are backticked hex tokens outside any
   Markdown table row. Frozen class B is explicitly “inside a table cell”, so
   this candidate records them as skipped. A line/paragraph-scoped scanner
   counts them as B; both resolve, so **M is identical (3) while N differs by
   two (54 here, 56 under the line-scoped reading)**. This is the main
   reconciliation item: the scorecard's repaired row must be labelled with
   whichever N the adopted implementation prints.
2. **Paths inside command spans (21 of the 25 skipped rows).** Class A is “a
   backticked repo-relative path …”, i.e. the whole span. `python3 -B
   tests/fixtures/r22-result-oracle.py …` is a command span; its inner
   `tests/fixtures/r22-result-oracle.py` is enumerated as skipped, not scored.
   A substring scanner that extracts path-shaped tokens anywhere inside
   backticks would add those to A. All of them exist at base, so that reading
   changes N but not M.
3. **Brace pattern (line 87).** `corpus/lessons/round-{6..11}.md` is a shell
   brace pattern. The frozen class admits only `*` as a glob metacharacter, so
   it is skipped rather than expanded. All six `round-{6..11}.md` files are
   tracked at base, so brace expansion would also leave M unchanged.
4. **Token boundaries.** A hex run glued to word characters
   (`from195715439a…`, `r21 final195715439a…`), to `-`
   (`<6ff3413-proc-file>`, `c1-matrix-4f48343.json`) or to `/`/`.`
   (a path component) is not a standalone token here and is not enumerated. A
   substring scanner would over-count those. Conversely, the token inside
   `git show 41553adb…:census/round-21/run-acceptance.py` **is** counted as B,
   because the kill rule says a quoted/historical token in a cell that names
   its revision is still class B.
5. **Extension-only filter.** `status.showUntrackedFiles` ends in a
   dotted suffix but not one of `.py/.sh/.json/.tsv/.md/.txt`, so it is not a
   path candidate at all.

## Class ambiguities and how this candidate resolves them

1. **“Bare” hex token** = a standalone token (not glued to word characters,
   `-`, `.` or `/`); backticks do **not** disqualify it. Basis: the frozen kill
   rule (“a token that is quoted as an example … is still class B/C”).
2. **“Table cell”** is a Markdown table cell, not a line or paragraph. B and C
   are therefore cell-scoped; A is document-wide. (This is the source of
   disagreement 1 above; it is the literal reading of the frozen enum.)
3. **Class A scope**: the backticked span must *be* the path (optionally
   `:<line>`, optionally with `*`). The `:<line>` suffix is accepted but the
   line number is **not** verified, because the frozen predicate only requires
   path presence at `--rev`.
4. **Glob semantics**: only `*` is a metacharacter, and it may cross `/`
   (git-pathspec-like). Zero matches is a mismatch (`mismatch:glob-absent`),
   not a skip. `census/round-14/verification*.json` → 3 matches;
   `census/round-17/jj-receipts-*.txt` → 2 matches.
5. **Class C adjacency**: “exactly one backticked path” counts backticked
   whole-span path tokens in the cell. Zero or more than one path → the
   64-hex token is skipped with the count in the reason. If the single path is
   absent at `--rev`, the digest is undefined and the row is
   `mismatch:path-absent`.
6. **Declaration bytes** are read from `--rev` (`git cat-file blob
   <rev>:<file>`), never from the worktree while the file exists at that
   revision. This is what makes `--rev 4edb25d` reproducible after the repair
   has landed in the worktree: the base measurement still reports the base
   three mismatches. A worktree fallback exists only for files absent at
   `--rev`, and a stderr note is printed when the worktree bytes differ from
   the audited bytes. The note is not part of the counts line.
7. **Class B resolution** requires a commit (`<tok>^{commit}` peels), not just
   any object; annotated tags and blobs do not satisfy B.

## Bounded findings / risks

- This seat produces a candidate instrument only. It does **not** claim the
  repaired `SCORECARD.md` reaches `mismatches=0`; that requires the repaired
  file to be committed at the final tip and the counter re-run there. If the
  repair is still uncommitted, this tool audits the committed bytes and prints
  the divergence note plus `mismatches=3` — by design, not a failure.
- N is implementation-defined at the edges listed above (54 here). The frozen
  counter fixes M and the exit code, not N, so the adopted implementation's N
  must be the one written into the scorecard row; M_before = 3 under both the
  cell-scoped and line-scoped readings.
- The tool enumerates only the frozen token shapes. It does not prove the
  absence of other evidence forms (bare URLs, digests without adjacent paths,
  revision words without hex), and it does not authenticate author identity or
  command execution.
- `--format skips` is a diagnostic extension for reconciliation, not part of
  the frozen counter; `counts`/`tsv` behave as specified.
- [INFERENCE] The three mismatches are exactly the pre-registration's named
  before-state (“fleet-relative pointer, unnamed receipt, absent banked file”)
  — inferred from the token identities, since the pre-registration does not
  enumerate the three tokens.
- Read-only compliance: no lane file changed; no git/jj write; no process
  signalled; no deletion authority created; no credentials, `/proc`, `.tower`
  or private TSV read. Exploration scratch (`/var/tmp/sc-base.md`,
  `/var/tmp/implb-tsv.txt`, `/var/tmp/st.txt`) was removed; the tool's own
  `/var/tmp` scratch is removed by its `finally` block (verified: no
  `souji-declared-evidence-*` directory remains). No tool was installed or
  updated, so there is nothing to record under the tooling directive.
- Orientation disclosure: I read the pre-existing committed artifact
  `census/round-22/attempt2/declared-evidence-before.tsv` (lane evidence, not
  the sibling candidate) before writing the parser. The strategy here
  (cell-first splitting) is independent, and every number in this report comes
  from running this candidate, not from that file.
