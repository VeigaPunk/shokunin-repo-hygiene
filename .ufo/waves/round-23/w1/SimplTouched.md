# SimplTouched — YAGNI pass over what round 23 touches

## Status

STATUS: PASS — YAGNI answer delivered for all three questions with a keep/merge/delete verdict
and a line estimate per item; no lane bytes changed (read-only seat), one accidental bytecode file
disclosed below.

Scope read: `.ufo/waves/round-23/preregistration.txt`; `tools/souji-declared-evidence.py`,
`tools/souji-gate-check.py`, `tools/souji-rev-pin.py`, `tools/souji-landing-gate.py`, plus the two
round-23 instruments as they existed at read time (`tools/souji-record-agreement.py` 327 lines,
`tools/souji-receipt-run.py` 218 lines — both untracked, both being edited by sibling seats while I
read them; all anchors below are function names and quoted text, not line numbers, for that reason).
`SCORECARD.md`, `corpus/README.md`, `LOG.md`, `corpus/pointer-exemptions.tsv`,
`census/round-22/attempt2/*`.

## Evidence

Base revision for every `git` read: `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd`
(`git rev-parse HEAD`, branch `HEAD` → `master`, clean of the round's own artifacts).

E1 — `rev-pin` already yields exactly the digest C2's receipt must bind:

```
input_snapshot -> {'tools/souji-declared-evidence.py': '65817d0d0d4874e8fab83ef11ae29297a865a8359f554e2ff7d2a753f21448f4'}
cat-file sha256 -> 65817d0d0d4874e8fab83ef11ae29297a865a8359f554e2ff7d2a753f21448f4
MATCH True
```

`python3 -c 'import souji-rev-pin; input_snapshot(root, rev, [tool])'` at
`1208bfb`, compared against `git cat-file blob <rev>:<path>` piped through sha256.

E2 — the K4 exemption convention breaks the existing parser of the same file:

```
plain row -> {'tools/x.sh'}
uncommitted: row -> EvalError corpus/pointer-exemptions.tsv:1 malformed exemption row (expected unique path<TAB>reason)
```

`souji-landing-gate.load_pointer_exemptions` called against a /var/tmp fixture; the predicate is
`fields[0].startswith(POINTER_ROOTS)` with
`POINTER_ROOTS = ("census/", "tests/", "tools/", "corpus/", ".ufo/waves/", ".ufo/quarantine/")`.

E3 — the new instrument's own output at base (observation of the tool, not a C1 verdict; the
`RC=` on the next line is `head`'s status, not the tool's):

```
MISMATCH	K1	census/round-23/records/declared-evidence-after.tsv	receipt-absent	not in tree at 1208bfb...
MISMATCH	K2	LOG.md:1478	uncorrected	'assertions=56 resolved=53 skipped=33 mismatches=3' has no later 'superseded by' line
MISMATCH	K2	LOG.md:1495	uncorrected	'1 present' has no later 'superseded by' line
MISMATCH	K2	LOG.md:1495	uncorrected	'1 refused' has no later 'superseded by' line
MISMATCH	K3	corpus/README.md:440	tally-disagree	1 present != receipt 2 present
MISMATCH	K3	corpus/README.md:440	tally-disagree	1 refused != receipt 0 refused
MISMATCH	K4	.ufo/waves/round-23/	uncommitted-path	??
MISMATCH	K4	census/operator-sweep-20261019/	uncommitted-path	??
MISMATCH	K4	tools/__pycache__/	uncommitted-path	??
MISMATCH	K4	tools/souji-receipt-run.py	uncommitted-path	??
MISMATCH	K4	tools/souji-record-agreement.py	uncommitted-path	??
keys=4 records=3 occurrences=10 mismatches=18
```

E4 — the receipt tallies the frozen predicates compare against:

```
slice-verdicts.tsv: 5 accepted, 2 present, 0 refused, 1 unverifiable   (8 rows)
declared-evidence-before-final.tsv: assertions=55 resolved=52 skipped=33 mismatches=3
declared-evidence-before.tsv:       assertions=56 resolved=53 skipped=33 mismatches=3
```

E5 — the duplicated counter tuples on SCORECARD's r22 row:

```
$ grep -oE 'assertions=[0-9]+ resolved=[0-9]+ skipped=[0-9]+ mismatches=[0-9]+' SCORECARD.md | sort | uniq -c
      2 assertions=55 resolved=52 skipped=33 mismatches=3
      2 assertions=63 resolved=63 skipped=40 mismatches=0
```

Both pairs sit on the same physical line, `SCORECARD.md:14` (verdict cell + counting-command cell).

Side effect I caused, disclosed: the E1 probe imported `souji-rev-pin.py` without `-B` and wrote
`tools/__pycache__/souji-rev-pin.cpython-314.pyc` (05:12:51). The directory pre-existed
(`souji-gate-check.cpython-314.pyc`, 05:11:07, from another seat's import). I did not remove it —
`rm` is outside my seat — and it is one K4 row. Every later probe used `python3 -B` /
`PYTHONDONTWRITEBYTECODE=1`. Nothing else was written inside the lane; scratch was
`/var/tmp/souji-r23-SimplTouched*/`, removed.

## Findings

### (1) Which of the two NEW instruments duplicates an existing one

**`tools/souji-receipt-run.py` (C2) duplicates `tools/souji-rev-pin.py`.**
`souji-record-agreement.py` (C1) does **not** duplicate an existing predicate — no existing
instrument compares a declaration against a receipt, so it earns its file.

Per-function duplication in `souji-receipt-run.py` (218 lines), with the rev-pin owner:

| receipt-run function | rev-pin owner | verdict |
|---|---|---|
| `git()` (8 lines) | `_env()` + `_git()` (`souji-rev-pin.py:49-77`, 29 lines) | **delete**, import |
| `durable_rev()` (6 lines, `for-each-ref --contains`) | `durable_tips()` + the `merge-base --is-ancestor` loop in `resolve_durable` | **delete**, import — a second technique for one predicate |
| `blob_sha_bytes()` (7 lines) | `input_snapshot()`'s `cat-file blob` + sha256 | **delete**, import (E1 proves identical output) |
| rev-format + `^{commit}` + durability preamble in `cmd_run` (~8 lines) | `resolve_durable()` | **delete**, import |

Genuinely new in receipt-run and worth keeping: the private `--no-local` clone detached at `<rev>`
(~15 lines, rev-pin only *compares* a worktree, it never materializes one), the receipt v1 format +
`parse_receipt` + `cmd_verify` (~60 lines), the `/tmp`-and-in-repo `--out` refusals.

**Verdict: MERGE — 218 → ~150 lines (est. −65), and one convention instead of three.**
Concretely: add `committed_digests(root, rev, paths) -> dict[str, str]` to `souji-rev-pin.py`
(extract the existing blob-digest loop out of `input_snapshot`, ~8 lines; `input_snapshot` keeps the
worktree-equality assertion and calls it), then `receipt-run` is
`resolve_durable(root, rev, [], tree_check=False)` + `committed_digests(root, rev, [tool])` + clone +
run + receipt + verify. `souji-rev-pin.py` 406 → ~420. **Net across the pair: −51 lines.**

The merge is not cosmetic: it closes a real hole. `receipt-run.blob_sha_bytes` calls
`subprocess.run(["git", ...])` with **no `env=` at all**, so the digest the receipt binds inherits
`GIT_DIR`, `GIT_OBJECT_DIRECTORY` and `GIT_ALTERNATE_OBJECT_DIRECTORIES` — in the one instrument
whose claim is "the recorded digest is the committed blob at the named revision". Its sibling
`git()` in the same file does scrub (partly), and `souji-rev-pin._env()` scrubs every `GIT_*` and
pins `GIT_CONFIG_NOSYSTEM`/`GIT_CONFIG_GLOBAL=/dev/null`/`GIT_NO_LAZY_FETCH`/
`GIT_NO_REPLACE_OBJECTS`/`LC_ALL=C`. Importing rev-pin makes the strictest existing scrub the only
one.

**`souji-record-agreement.py` (327 lines): MERGE the plumbing, KEEP the predicate.**
Delete `git()` (8 lines) and `read_at()` (6) in favour of rev-pin's `_git`, and `resolve_rev()`
(11 lines) in favour of `resolve_durable` — `resolve_rev` currently accepts a revision with *no*
durability proof and falls back to `HEAD`, which is strictly weaker than the helper the lane
already certified at r19 (`SCORECARD.md` Capabilities row "durable revision stamps (r19)").
K1/K2/K3/K4 themselves (35+67+21+24 lines) are new work; keep.

**KEEP + ADD: `souji-record-agreement.py` has no `--selftest`.** Preregistration C1 says "the
fixture's cases 2-6 each require >=1 mismatch, so an always-zero emitter is rejected by the same
harness (control=FALSE-GREEN-REJECTED)". No such harness exists in the file. Borrow the *shape* of
`souji-declared-evidence.selftest()` (fixture repo + `case()` + the always-zero control), ~60 lines.
Net for this file: 327 → ~302 → ~362. This is the one place where the YAGNI pass adds lines, and
it is mandatory, not optional.

### (2) Which existing helper could host the new checks with fewer lines

- **`tools/souji-rev-pin.py` hosts all of C2's digest/durability work** — E1 proves
  `input_snapshot` already returns the exact `tool_sha256=` value; after the `committed_digests`
  split, `cmd_verify`'s three-line core
  (`actual = committed_digests(...); if actual != header["tool_sha256"]: refuse(...)`) replaces
  `blob_sha_bytes` + its unscrubbed subprocess. It is the correct host because its own docstring
  draws the line this round needs: "This tool is a resolution helper, not a verdict".
- **`tools/souji-declared-evidence.py` is the host for the missing C1 fixture harness**, not for
  the C1 predicate. Its `Repo.read_declaration` already refuses a worktree read when the file is
  absent at `--rev` — the exact failure mode K1 would otherwise have when
  `census/round-23/records/declared-evidence-after.tsv` is uncommitted.
- **`tools/souji-gate-check.py` is NOT the host for K3.** It reads the same
  `slice-verdicts.tsv` and owns the same four-class vocabulary (`CLASSES`), but `check_slice`
  derives `verified/total` from register ids while K3 derives a per-class tally; folding K3 in
  would give one tool two output contracts. Reuse the constant, not the function.
- **`tools/souji-landing-gate.py` is NOT a host for K4** — it is the *victim* of K4's convention;
  see A3.

### (3) Dead weight to DELETE rather than correct

All three deletions are in `SCORECARD.md`, the lane's live claim surface. Nothing in
`corpus/` (filed evidence) or `LOG.md` (append-only) is a deletion candidate, and the four places
where the temptation exists are named under "Refused" below.

**D1 — `SCORECARD.md:14`, the two duplicated historical counter tuples. DELETE all four
occurrences, keep one.**
`assertions=55 resolved=52 skipped=33 mismatches=3` appears twice and
`assertions=63 resolved=63 skipped=40 mismatches=0` appears twice, both pairs on this one physical
line (E5). *Why dead:* each fact is stated twice in the same row — once in the verdict cell, once
in the counting-command cell — and the frozen K1 predicate requires **every** 4-tuple on an
`r22`/`round-22` line to equal the round-23 after receipt *and* to name that receipt's rev. No
historical value can satisfy that, and the row's own "measured at 4edb25d (before)" column plus the
receipt path already carry the base provenance. *Superseded by:* the counting-command cell's
receipt names — `census/round-22/attempt2/declared-evidence-before-final.tsv` carries
`assertions=55 resolved=52 skipped=33 mismatches=3` verbatim (E4), and
`declared-evidence-before.tsv` carries the 56/53 reading — plus the round-23 after receipt, whose
single tuple replaces them. Est. −3 occurrences, −~60 chars, no line count change.

**D2 — `SCORECARD.md:107` (r18 plan), `:109` (r19 plan), `:111` (r20 plan). DELETE, 3 lines.**
Each is a forward plan block immediately followed by its own outcome block (`:108` "— done",
`:110` "— done", `:112` "— admitted"), which repeats the round number and records what actually
happened. Two authorities for one round's outcome. Every open residual in them survives:
`:108` carries `:(optional)` core.worktree, nested-layout pathspec excludes, carry-gate wrap
truncation and the HEAD-pinned r13/r14 runners; keep-ref lifetime is in
`corpus/lessons/round-17.md:88`; the pid-recycle window is in
`corpus/lessons/round-18-verifier-spotcheck.md:149` and verbatim in
`.ufo/waves/round-22/attempt2/residual/evidence/ResClaims-SCORECARD-c1664fc.md:111`.

**D3 — nothing else.** `SCORECARD.md:100-105` (the r17 plan block) is the same shape as D2 but
**KEEP**: `:103` is the only place the option-(a) operability residual list
("git-metadata symlinks resolving inside the gitdir, hardlink/alternates refusals → per-repo
degrade, `~user` expansion") exists as a *routed item*; `corpus/lessons/round-16.md:107` records
the contractions as open but does not route them. Deleting `:100-105` would drop an open-item list.

### Refused — where the temptation exists

- **`corpus/README.md:40` (the r12 F2 row) must NOT be deleted.** The file's own heading at
  `:64` says "supersedes the r12 F2 row", so the row looks dead — but
  `census/round-13/baseline-measures.md:39` pins it as the *before* half of a measured pair
  (`| corpus/README.md F2 row | "frontier, no entry" at HEAD | ... | line 40 at HEAD |`).
  Deleting it destroys the baseline of a filed receipt pair — the exact D2/D5 defect class this
  round repairs. Same for `:68` (the after half).
- **`corpus/README.md:440-441` and `corpus/lessons/round-22.md:355` must NOT be deleted.** The
  frozen K3 predicate requires each of the four class words to occur at least once in each record
  ("class-absent" otherwise). `:440-441` is *wrong* (1 present / 1 refused vs the receipt's
  2 present / 0 refused, E4) and must be corrected, not removed; `round-22.md:355`'s "0 refused"
  already agrees.
- **`LOG.md:1478` and `LOG.md:1495` must NOT be deleted.** Preregistration C1's K2 makes deleting
  a filed historical occurrence a mismatch in its own right ("filed bytes are append-only"). The
  repair is an appended later line carrying `superseded by` and the same 4-tuple.
- **`census/operator-sweep-20261019/`, `census/round-22/attempt2/*` receipts,
  `corpus/pointer-exemptions.tsv`'s operator rows, `.ufo/waves/round-22/attempt2/w1/evidence/*`**
  — filed evidence and operator-owned paths. K4 lists them as untracked; that is a K4 artifact,
  not a cleanup mandate. Never delete, move or quarantine them.
- **`SCORECARD.md:116-120`, the "formerly said 6/7" parenthetical — KEEP.** It is the only record
  of that drift: `grep -n '6/7\|formerly said' LOG.md corpus/lessons/round-9.md` returns nothing.

### Totals

| item | verdict | est. |
|---|---|---|
| `souji-receipt-run.py` | merge into `souji-rev-pin.py` | 218 → ~150 (−65) |
| `souji-rev-pin.py` | host: `committed_digests` + `--digest` | 406 → ~420 (+14) |
| `souji-record-agreement.py` plumbing | merge (`git`, `read_at`, `resolve_rev`) | 327 → ~302 (−25) |
| `souji-record-agreement.py` `--selftest` | **add** (prereg C1 requires it) | ~302 → ~362 (+60) |
| `SCORECARD.md:14` tuples | delete 3 of 4 occurrences | −~60 chars |
| `SCORECARD.md:107,109,111` | delete | −3 lines |
| `corpus/`, `LOG.md`, exemptions | keep (refused) | 0 |
| **net across tools** | | **−51** |

## Attack log

**A1 — K2 punishes a truthful, receipt-bound number.** `K2_RECEIPT` is a single file
(`census/round-22/attempt2/declared-evidence-before-final.tsv`), but the LOG section legitimately
quotes a *different, named* receipt: `LOG.md:1478` says
`assertions=56 resolved=53 skipped=33 mismatches=3 (receipt census/round-22/attempt2/declared-evidence-before.tsv)`
and that file carries exactly `assertions=56 resolved=53 skipped=33 mismatches=3` (E4). The counter
reports `uncorrected` for a line that is correct about its own receipt. A per-named-receipt
resolution would fix it; the predicate is frozen, so this is reported, not edited.

**A2 — K4 cannot reach zero before landing and cannot fail after it.** K4 counts
`git status --porcelain` paths against a committed exemption file, so at the round tip it counts the
round's own artifacts: `.ufo/waves/round-23/`, `tools/souji-record-agreement.py`,
`tools/souji-receipt-run.py` (E3). Those cannot be exempted — the prereg restricts exemptions to
"operator-owned paths only". After landing the tree is clean by definition, so K4=0 is tautological.
The key measures the *moment*, not the record, and cannot discriminate a repaired lane from a
lucky one.

**A3 — K4's `uncommitted:` prefix breaks `souji-landing-gate`.** `corpus/pointer-exemptions.tsv`
already has a grammar — `path<TAB>reason`, first field under `POINTER_ROOTS`, unique, no `<*>` — and
`souji-landing-gate.load_pointer_exemptions` raises `EvalError` on any deviation (proved, E2).
An `uncommitted:`-prefixed row is not merely redundant state (the row's *presence* in a committed
exemption file already asserts the exemption; the reason column already says why) — it makes every
later landing-gate evaluation exit 2 (could-not-evaluate) for the whole lane. Two grammars, one
file. If K4 needs the distinction, it belongs in the reason column, not the path.

**A4 — K1 turns a history row into a current-only row.** Requiring every 4-tuple on an `r22` line
to equal the round-23 after receipt means `SCORECARD.md:14` cannot retain the r22 before/after pair
at all — the row must be rewritten, not corrected. That is a defensible contract (the receipt is
the evidence), but it should be stated: the round is deleting measurement history from the scorecard
and re-homing it in `census/`. D1 above does exactly that.

**A5 — the C3 theme cites a superseded row.** Preregistration C3 says
`corpus/README.md F2: "frontier, no entry"`. That string is `corpus/README.md:40`, which the file's
own heading at `:64` declares superseded by `:68` ("bounded structure-census capability acquired;
wider size attribution remains frontier"). The theme survives — F2's *size census read side* is
still entryless — but the citation names the pre-r13 row, not the live one.

**A6 — three git-env conventions in two new files.** `souji-record-agreement.git()` and
`souji-receipt-run.git()` each scrub only `GIT_DIR`/`GIT_WORK_TREE`; `souji-receipt-run.blob_sha_bytes`
scrubs nothing; `souji-rev-pin._env()` scrubs every `GIT_*` and pins six config/behaviour
variables; `souji-landing-gate` documents `GIT_ENV` as the reason "committed bytes are exact". The
two weakest of these are in the two instruments this round is adding, and the weakest of all
(`blob_sha_bytes`, no `env=`) is the one that produces the digest C2's whole claim rests on.
