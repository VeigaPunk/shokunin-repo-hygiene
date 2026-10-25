STATUS: PASS

PASS covers this slice only: after repair, every class-A assertion in rows 16–20 resolves at
the measured revision and at both later tips. It is not a pass of C1 as a whole — F1 records an
enumeration gap in the counter itself, and F2 records a stale quoted output plus a false
identity claim in the C1 row's own wording.

Slice: capability data rows 16–20 of `SCORECARD.md` (reproducible seat audit r17,
bounded repository-content census r18, evidence-pointer gate r18, process-residue
observations r18/r21, paragraph-aware carry gate r19).

Measured revision: `4edb25dfe262515d0da63224bbba71e02e36cba5` (frozen base, lane master
tip at preregistration). The lane advanced three times during this audit
(`70af563` → `3216c19` → `5ff5041` → `d6a75bad`), so point-in-time after-states are recorded at
two of those tips and no "final tip" exists yet; the after-state below is a snapshot, not a
closure receipt.

Audited instance: the frozen counter reads the declaration **from the named revision's
tree** (`tools/souji-declared-evidence.py`, `Repo.read_declaration`: "From the revision when
tracked there, else from the filesystem"). `SCORECARD.md` is tracked at the base rev, so the
audited bytes are the base blob. In that blob rows 16–20 are **lines 60–64**; in the current
worktree/HEAD blob they are lines 65–69. The TSV's `file` column carries the revision so the
line numbers are unambiguous.

`SCORECARD.md` was not edited by me, and every measurement here is revision-pinned (`--rev`), so
the counter always reads the committed blob, never the worktree. Receipts: at `3216c19` the
worktree matched HEAD (`git show HEAD:SCORECARD.md | cmp - SCORECARD.md` → IDENTICAL; sha256
`71507c608d3ea54b22378fd98bb6b5e4c98d7f946715e9eda471e0b80178e2a0` for both). By the end of the
audit the worktree carried another seat's uncommitted edit in rows 3, 4 and 10 — outside this
slice (`git diff --stat -- SCORECARD.md` → 2 insertions, 2 deletions), so the worktree digest is
not a receipt; the receipts are the blobs at `4edb25d`, `3216c19` and `d6a75bad`. Nothing in
rows 16–20 was drafted or changed while this audit ran.

## Exact command per frozen class

- Class A (backticked repo-relative path, optional `:line`, optional glob):
  `git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file -e <rev>:<path>`
  (glob form, not needed in this slice: `git -C … ls-tree -r <rev> --name-only` then match).
- Class B (bare 7..40-hex token in a revision-context cell):
  `git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file -e <token>^{commit}`.
- Class C (64-hex digest in a cell with exactly one backticked path):
  `git -C … show <rev>:<path> | sha256sum` compared to the token. **Unexercised**: rows
  60–64 contain no 64-hex token, so this slice makes zero digest claims. No C check is
  reported as passed.

## Executed measurements

1. Frozen counter, base rev (exit 1):
   `python3 -B tools/souji-declared-evidence.py --root . --file SCORECARD.md --rev 4edb25dfe262515d0da63224bbba71e02e36cba5 --format counts`
   → `assertions=56 resolved=53 skipped=33 mismatches=3`
   Its TSV rows in this slice: line 61 `census/round-18/c1-matrix-4800fd7.json` resolved;
   line 62 `census/round-18/final-verification-4800fd7.json` resolved;
   line 63 `reason-after.txt` **mismatch:path-absent**;
   line 64 `tests/fixtures/r19-carry-wrap.py` resolved; line 64 `census/round-19/c1-carry.txt`
   resolved. The committed before receipt agrees byte-for-byte on these five rows:
   `awk -F'\t' '$1>=60&&$1<=64' census/round-22/attempt2/declared-evidence-before.tsv`.
2. Class-A presence at base for every path in the slice:
   `census/round-17/seat-audit-replay.py` OK, `census/round-17/transcript-manifest.py` OK,
   `census/round-18/c1-matrix-4800fd7.json` OK, `census/round-18/final-verification-4800fd7.json` OK,
   `census/round-21/reason-after.txt` OK, `tests/fixtures/r19-carry-wrap.py` OK,
   `census/round-19/c1-carry.txt` OK; `git cat-file -e 4edb25d…:reason-after.txt`
   → `fatal: path 'reason-after.txt' does not exist` (rc 128).
3. After-state, tip `3216c19`: same command with `--rev 3216c1998fe04d7e23793ffd4e135bd37c3a11f4`
   → `assertions=56 resolved=56 skipped=36 mismatches=0`, exit 0. Slice rows: lines 66–69 all
   four instrument-recognized assertions `resolved`; line 65 produces no row (see F1).
   Re-measured at the later tip `d6a75bad` → `assertions=58 resolved=58 skipped=36 mismatches=0`,
   exit 0; the slice rows are unchanged (lines 66–69 resolved, line 65 no row), and all seven
   class-A paths of the slice return OK under `git cat-file -e d6a75bad…:<path>`.
4. Intermediate tip `70af563` (measured before the lane moved): `assertions=57 resolved=56
   skipped=37 mismatches=1`, exit 1, the single mismatch being line 83
   `.ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md` — outside this slice.

## Slice census (base instance, lines 60–64)

| class | rows | resolved | mismatch | skipped |
|---|---|---|---|---|
| A | 7 | 6 | 1 (`reason-after.txt`) | — |
| B | 0 | — | — | 2 (`4800fd7` ×2, embedded in filenames; `cat-file -e` resolves either way) |
| C | 0 | — | — | — |
| no frozen class | — | — | — | 17 (counts, word-numeral, `V-WRITE-RELATIVE`, directory path, registry ids) |

Per-token rows: `.ufo/waves/round-22/attempt2/w1/evidence/AuditCap4.tsv` (26 rows).
Note the divergence from the counter's own slice count (5 assertions): the two backticked
command spans on line 60 carry real repo-relative paths that the counter drops to `skipped`
(see F1). No token was silently dropped; every count, word-numeral, hex-looking stamp and
registry id has its own `skipped:<reason>` row.

## Mismatch and minimal truth-preserving repair

Base line 63, cell *process-residue observations (r18; r21 synthetic repair)*, evidence column:

    r21 synthetic27/27 (old emissions6/27, leaks19→0), `reason-after.txt`, S100/S101; r18 live-proc fixture not run

Token `reason-after.txt` (class A) is absent at the measured revision; no tree path of that name
exists at the base or at the tip (`grep -c '^reason-after.txt$'` over `git ls-tree -r` → 0 at
both). [INFERENCE] this is the base mismatch the preregistration labels the "unnamed receipt":
it is the receipt named by basename with no directory, and it is the only non-path-pointer
mismatch among the three.

Repair (already applied at the tip, verified truth-preserving):
`reason-after.txt` → `census/round-21/reason-after.txt`. That path is present at the measured
revision (class A resolved at both `4edb25d` and `3216c19`), is 1828 bytes of committed receipt,
and its bytes substantiate the number it is cited for: 27 `CASE` rows, all `pass`, closing line
`total=27` → matches "synthetic27/27" (`git show 4edb25d:census/round-21/reason-after.txt`).
Nothing is deleted or renamed; the same artifact is addressed with its committed directory, so
the capability claim is corrected rather than dropped. No further mismatch exists in this slice.

## Findings (bounded)

F1 — **instrument under-enumerates class A in this slice (calibration gap, material).**
Base line 60 / tip line 65 cite `python3 census/round-17/seat-audit-replay.py …` and
`census/round-17/transcript-manifest.py --check census/round-16/transcripts`. Both contain
repo-relative `.py` paths, which is the frozen class-A shape, and both paths resolve at the
measured revision (`git cat-file -e` OK at base and tip). The counter emits **no row** for that
line: `PATH_RE` must match the whole backticked span, so any span carrying command text or
arguments falls into `skipped`. Observed, not inferred: line 65 is absent from the tool's TSV at
`3216c19` while its two paths are present in the tree.

The same shape is demonstrably false-green on other committed bytes. At `d6a75bad`, file
`census/round-11/S08-fragment.md` cites one absent basename twice:

    line 37: | `bash -n cand-census-08.sh` | exit 0 |                       -> no row, no mismatch
    line 94: ... `cand-census-08.sh` is the certified, self-consistent option ...  -> mismatch:path-absent

`git cat-file -e d6a75bad:cand-census-08.sh` fails, and the counter run on that file emits
`assertions=11 resolved=7 skipped=46 mismatches=4` with line 37 producing no row at all: the
bare citation is caught, the command-form citation of the identical absent path is invisible.
[INFERENCE] therefore a SCORECARD line of the form `python3 tools/<absent>.py …` would still
print `mismatches=0`, so the kill rule cannot fail on that shape. Two honest repairs, both
truth-preserving: (a) extend the scanner to extract path-shaped tokens from command spans
(raises N honestly), or (b) state in the round lesson that the frozen enumeration is span-exact
and that command-form pointers are disclosed as uncovered. Silently leaving it is what must not
happen, and the C1 row's `assertions=` figure should not be read as the class-A population.

F2 — **the C1 row's own quoted counter output no longer reproduces, and its "same 56" identity
claim is false.** Two measured defects in the calibration row's text; neither removes a
capability claim.

(a) Stale quoted output. The row prints `→ assertions=56 resolved=56 skipped=36 mismatches=0,
exit 0` as the output of its own counting command at "the final tip". That line reproduced at
`3216c19`, the commit that landed it; at the tip now, `d6a75bad`, the identical command prints
`assertions=58 resolved=58 skipped=36 mismatches=0`, exit 0. A reader who re-runs the named
command gets a different line than the one quoted, so the quoted receipt is already stale inside
the round that quotes it.

(b) False identity. "repaired to 0 mismatches over **the same 56 assertions** at the final tip":
the population is not the same 56. Between the base rev and `3216c19` five assertion rows left
and five entered; between `3216c19` and `d6a75bad` two more entered (the only SCORECARD change
in that span touches rows 2–5, outside this slice). The 56→56 equality at `3216c19` was churn
that cancelled, not identity.

Rows that left base→`3216c19`: `AXES.md` (A; now written as the fleet-root absolute path, which
`PATH_RE` does not match), `.ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md` (A; now
unbackticked prose — legitimate, the cell asserts absence), `reason-after.txt` (A; qualified, in
this slice), plus class-B tokens `41553adb139d06511dc386bb3ce4326aebfba675` and
`b912328d00d19f26918240710d0b5e0f334880ff`. Rows that entered:
`census/round-21/reason-after.txt` (A), `census/round-22/attempt2/declared-evidence-before.tsv`
(A, cited twice), `corpus/lessons/round-22-verifier-spotcheck.md` (A),
`4edb25dfe262515d0da63224bbba71e02e36cba5` (B). Command: token-set diff of the two
`--format tsv` outputs on `$2"|"$3` under `LC_ALL=C`.

The instrument cannot catch this: a counts line is `skipped` under the frozen enum (counts are
not class A/B/C tokens), so a copied output line is outside the audit's own surface. The file was
also still being edited in the worktree at the end of this audit, which is exactly why a literal
count cannot serve as a durable receipt. It must be fixed by wording. Minimal truth-preserving
repair: quote the counts line only after the tip is frozen, or replace the literal numbers with
the committed counts receipt (path + line) so they resolve by path instead of being copied; and
replace "the same 56 assertions" with "the 56 assertions of the base file" (plus the repaired
file's own N, with any churn disclosed). Two of the three removals are the prereg's own
sanctioned repair menu ("wording that stops presenting the token as evidence"), so nothing here
costs a capability.

F3 — **tip-state note, no action required.** At `70af563` the counter still reported
`mismatches=1` from `.ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md` (line 83, outside
this slice); `2a130b4`/`3216c19` removed the backticks and the counter now reaches 0. Recorded so
the closure reader knows the 0 was reached after this slice was already clean.

F4 — **class C has no in-slice subject.** Zero 64-hex tokens in rows 60–64 at either revision;
the digest path of the counter is not exercised by this slice and is not claimed to pass here.

## Residual risk / verification gaps

- The after-state is measured at `3216c19` and `d6a75bad`, not at a closure tip; the lane moved
  three times mid-audit and can move again, so the closure reader must re-run the counter at the
  tip it names.
- The two assertions that entered between `3216c19` and `d6a75bad` live in rows 2–5, outside
  this slice; the changed rows were identified from the diff but their new tokens are not audited
  here.
- The instrument's `skipped=36` accounting at the tip was audited only inside this slice; the
  rest of the file's skips are unaudited here.
- F1's remedy touches the frozen counter; whether it is a round-23 instrument change or a
  disclosure-only lesson entry is the round owner's call, but the current `assertions=` number
  must not be presented as the class-A population.
- No tool installed or upgraded; no writes inside the lane except this report and
  `.ufo/waves/round-22/attempt2/w1/evidence/AuditCap4.tsv` (two scratch TSVs under `/tmp` were
  used for the token-set diff and deleted); no git write, no process signal, no deletion
  authority created, `SCORECARD.md` untouched.
