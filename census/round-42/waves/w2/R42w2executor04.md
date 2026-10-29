# R42w2executor04 — what souji-declared-evidence.py does NOT read in SCORECARD.md at the tip

Tip: 3105a63b23481fccf7df58e74d14a6681e0ea0c8 (SCORECARD.md = 865 lines, 72 headings, 0 code fences). Instrument: tools/souji-declared-evidence.py (sha at tip, read-only). Seat evidence dir: `.ufo/waves/round-42/w2/R42w2executor04/` (scripts `skip-reasons.py`, `hex-census.py`, `hex-where.py`, `hist-prefix-search.py`; outputs `declared-evidence-scorecard-tip.tsv`, `skip-reasons.out`, `hex-census.out`, `hex-uncounted.json`). The scripts import the instrument's own regexes/`classify` via importlib and read `de.tsv` (= the TSV file above) from the cwd. Nothing was written to the lane outside this dir; scratch deleted.

## Commands run
1. `python3 -B tools/souji-declared-evidence.py --root <lane> --rev 3105a63… --file SCORECARD.md --format tsv > de.tsv` → rc=1, last line verbatim:
   `assertions=490 resolved=420 skipped=810 mismatches=70`
   Per class/outcome (awk over the TSV): A resolved 284, A mismatch:path-absent 66, B resolved 136, B mismatch:rev-unresolved 2, **C resolved 0, C mismatch:digest 2**.
2. `skip-reasons.py` re-implements the skip branches of `classify()` with a reason label per skip. First run gave 812, then 811-vs-810 corrections: the instrument's `seen_hex` set is per *line* (shared across cells) and is also filled by class-B assertions; after matching that, `TOTAL skipped reproduced 810` = the instrument's count. The reproduction is exact.
3. `hex-census.py` + `hex-where.py`: all maximal hex runs of length ≥7 bounded by `(?<![0-9A-Za-z_])…(?![0-9A-Za-z_])` on every SCORECARD line, minus the (line, token) pairs the instrument asserts as class B/C → 163 uncounted tokens. Each tested with `git cat-file -e <tok>^{commit}` (≤40 chars) and, for 64-hex, against sha256 of all 11778 blobs at the tip (`git ls-tree -r` + `git cat-file --batch`). Non-resolving ones were also searched against sha256 of all 9057 blobs in all history (`hist-prefix-search.py`, `git rev-list --objects --all`).

## A. The 70 mismatches by SCORECARD section × class
All counts are of one class each unless noted (A = backticked path absent at tip, B = hex not a commit, C = sha256 differs).

| section (heading) | n | classes |
|---|---|---|
| ## Axes | 1 | 1 B |
| ### Round 23 measurements | 1 | 1 A |
| ### Round 24 measurements | 6 | 3 A, 1 B, 2 C |
| ### Round 25 append-only corrections | 1 | 1 A |
| ### Round 27 measurements | 1 | 1 A |
| ### Round 28 measurements | 3 | 3 A |
| ## Capabilities | 3 | 3 A |
| ## Planned | 3 | 3 A |
| ### Round 29 capability rows | 2 | 2 A |
| ### Round 31 capability rows | 2 | 2 A |
| ### Round 32 measurements | 1 | 1 A |
| ### Round 32 capability rows | 2 | 2 A |
| ### Round 33 measurements | 2 | 2 A |
| ### Planned (appended at round 33) | 1 | 1 A |
| ### Round 34 measurements | 1 | 1 A |
| ### Round 38 measurements | 8 | 8 A |
| ### Round 38 receipt pointer update | 5 | 5 A |
| ### Round 38 final receipt pointers | 3 | 3 A |
| ### Round 38 measured-revision block | 3 | 3 A |
| ### Round 38 filed-state measurement | 3 | 3 A |
| ### Round 39 measurements | 5 | 5 A |
| ### Round 39 capability rows | 2 | 2 A |
| ### Round 40 measurements | 5 | 5 A |
| ### Round 40 finality correction | 2 | 2 A |
| ### Round 41 measurements | 3 | 3 A |
| ### Round 41 capability rows | 1 | 1 A |
| **total** | **70** | 66 A + 2 B + 2 C |

No mismatch sits in the Round 26/35/36/37 sections. Of the 66 A mismatches, 60 are bare basenames (`c1-after.tsv`, `git-repo-structure-readonly.md`, …: the instrument only tests the repo-root path, so a basename cited from a directory-qualified cell is absent by construction) and 6 carry a slash (`w2/RevR3Counter.md` L50, `.ufo/waves/round-32/a2w1/SwarmExecutor08.md` L478, `.ufo/waves/round-33/make-spec-w2.py` L525, `controls/c{1,2,3}-control.txt` L821-823 — the last three are relative to census/round-42/ and the repo-root test cannot see them).
The 2 B mismatches are **sha256 prefixes misread as commits**, not dangling commits: `65817d0d` (L14; `tool_sha256 65817d0d…` = prefix of the sha256 of `.ufo/waves/round-26/assimilation/validate/tools/souji-declared-evidence.py`) and `09bb8e0d` (L92; prefix of sha256 of historical `tools/souji-size-census.py`, blob a710dfa). Found by `hist-prefix-search.py`. The 2 C mismatches (L68, `42259756…`, `71b89eb3…`) are stale digests; the tip file hashes to `bb506469be86…`.

## B. The 810 skipped spans by reason (reproduced exactly, sum = 810)
Decision rule (tools/souji-declared-evidence.py `classify`, lines 118-164): for each backticked span: if `rev:path` with an allowed extension, glob, or path matching `PATH_RE` (extensions py|sh|json|tsv|md|txt only) → assertion; if the span is entirely 7-40 or 64 lowercase hex → left for the cell pass; **anything else → `skipped += 1`**. Cell pass (table cells split on unescaped `|`; the whole line otherwise): 64-hex tokens need **exactly one** path-matching span in the *same cell* to become class C, else `skipped += len(digests)`; 7-40 hex tokens need a revision word or `census/round-N/` in the same cell, else skipped. Hex hidden in non-hex backtick spans is blanked out of the scan and never examined.

| reason class | spans | examples |
|---|---|---|
| backtick span with whitespace (commands, receipts `cases=8 pass=8`, prose) | 400 | L13 `bash tests/fixtures/r21-reason-canary.sh --tool …`; L14 `assertions=55 resolved=52 skipped=33 mismatches=3` |
| backtick single token that is not a path (flags, `key=value`, identifiers) | 240 | L14 `--selftest`; L21 `findings=2`, `checked_reg=52` |
| hex 7-40 in a cell with no revision word / census path | 96 | L17 `3a2a80d0…`, L27 `e78ac7c4…`, L41 `1efe406` |
| backtick path-like with no allowed extension (dirs, globs, refs) | 45 | L23 `.ufo/waves`; L69 `refs/jj/keep`; L70 `census/round-24/sources/*` |
| backtick bare name/ext not matching `PATH_RE` or other extension (`.md`, `…-worktree.txt`, config keys) | 19 | L84 `.md`; L101 `…-worktree.txt`; L160 `status.showUntrackedFiles`; L221 `core.fsmonitor` |
| backtick path with extension outside py/sh/json/tsv/md/txt, or brace/ellipsis path | 4 | L3 `/home/vgpnk/Projects/shokunin/AXES.md` (absolute), L102 `census/round-23/records/{a,b,…}`, L174 `objects/pack/*.promisor`, L197 `corpus/lessons/round-{6..11}.md` |
| 64-hex digest in a cell with ≥2 path spans (class C refused) | 3 | L67 `373ef1f0…`, `09bb8e0d…`; L101 `dd53c228…` |
| 64-hex digest in a cell with 0 path spans | 3 | L69 `f8c4c391…`; L70 `d5ed0805…`; L71 `b6bf5205…` |
| **total** | **810** | |

(Instrument defect, line 156: the `len(h)==64 → skipped` branch inside the class-B loop is unreachable because `HEX_B_RE` is capped at 40 chars with a trailing boundary.)

## C. Hex tokens ≥7 chars not counted as assertions: 163
Location of the 163 (hex-where.py): 59 inside a non-hex backtick span (`rev=eb1aa49…`, `git cat-file -e a65fac9:tests/…`); 51 in plain text of a cell without revision context; 44 bare-span hex in a cell without revision context (e.g. L74 `ce5971c`, L262 `a6d2d15`, L265 `a529c76`); 6 are 64-hex (4 in cells *with* revision context, 2 without); 2 are 8-char truncated digests inside non-hex spans (L69); 1 is an 8-digit number (L184).
- 154 of 163: `git cat-file -e <tok>^{commit}` succeeds — **all unasserted commit tokens resolve at the tip** (no dangling hidden commit).
- 64-hex: 6 tokens; **0 of 6 equals the sha256 of the cited path at the tip**. Three equal a *different committed path's* sha256 at the tip: L67 `373ef1f0…` = `.ufo/waves/round-24/w1/r24-size-census.py` (it is `tests/fixtures/r24-size-census.py` at 1efe406/778747e; tip bytes of that fixture hash `eae7f032…`), L69 `f8c4c391…` = r24-receipt-verify.py copies under `.ufo/waves/round-24/w1/`, `.ufo/waves/round-26/assimilation/validate/tests/fixtures/` and `census/round-26/waves/assimilation/validate/tests/fixtures/` (tip `tests/fixtures/r24-receipt-verify.py` hashes `c4a976aa…`), L70 `d5ed0805…` = souji-gate-check.py under round-26 assimilation copies (tip `tools/souji-gate-check.py` hashes `ea268127…`). Three equal no tip file.

**Non-commit, non-tip-digest hex tokens (the residue):**

| line | token | what it is (history search, `git rev-list --objects --all`) |
|---|---|---|
| 67 | `09bb8e0d9906b0dfef44775a9e5cd7c8f8a27d9bcdf559e2d371a3ef7ff1ed6d` | sha256 of `tools/souji-size-census.py` at 778747e (blob a710dfa); tip bytes hash `c5690681…` — stale pin |
| 69 | `e13d0c83` (8, truncated in `` `e13d0c83…` ``) | prefix of sha256 of `tools/souji-receipt-run.py` at a65fac9 and 1efe406 (blob a7eeb43); tip `0ed30d44…` |
| 69 | `9df0738c` (8, truncated) | prefix of sha256 of `tools/souji-receipt-run.py` at 778747e (blob 32290d9) |
| 71 | `b6bf52056d037b2251632b409be3d31852588480c392ddc50ca8f8dbf101179f` | sha256 of `tests/fixtures/r13-repo-structure.sh` at a65fac9 (blob 39b488a); tip `1a3e012d…` — stale |
| 101 | `dd53c228b8cca68cfe6dd51630c4ed3473a7c20db36a0effcf5a18259049bb0f` | sha256 of `tools/souji-record-agreement.py` at eb1aa49 (blob 3a90ddc); tip `ec5b809d…` — stale |
| 184 | `20261018` | date in the filename `.ufo/scopes/souji-mint-20261018/…`; not a hash |

Every one of the five digest-like residues was a true digest of the cited file when written and is now not the tip bytes; none is an invention.

## Verdict
The calibration instrument reads 490 of 1300 candidate tokens (490 assertions vs 810 skipped, 38%). Its "mismatches=70" is not a complete measure of SCORECARD decay, in four measured ways:
1. **Class C is vacuous at the tip**: 0 of 2 asserted digests resolve and 6 more 64-hex digests are skipped by the exactly-one-path-per-cell rule; none of the 8 sha256 digests in SCORECARD.md matches its cited path at the tip (they are historical pins, valid at their named revisions only). Instrument pins at revision-of-writing are not re-checkable by `--rev tip`.
2. **Revision-qualified hex is invisible when wrapped in a backtick span with other text** (59 tokens, e.g. `rev=<40hex>`), and hex without a revision word in its own cell is skipped (51 plain-text + 44 bare-span tokens; 59+51+44 = the 154 uncounted commit tokens); all 154 resolve now, so this blind spot hides no current defect.
3. **Two of the 70 "mismatches" are false** (sha256 prefixes read as commits: L14 `65817d0d`, L92 `09bb8e0d`); the corrected true mismatch count of resolvable-by-the-instrument-design is 68, and 60 of the A mismatches are basename-only citations the root-path test can never resolve.
4. **640 of 810 skips are non-path spans (command text, key=value, flags)** that carry no checkable assertion by design (reasonable); the 68 that name something path-like but fail `PATH_RE` (dirs, globs, braces, other extensions, absolute paths) are real unread citations.
Attacked: tools/souji-declared-evidence.py `classify`, SCORECARD.md at 3105a63 lines 14, 67-71, 92, 101, 184, 821-823. No file outside this report directory was written; unrun checks: none outstanding.
