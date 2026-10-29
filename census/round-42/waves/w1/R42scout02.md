# R42scout02 — cause analysis: SCORECARD line 68 digests and line 175 `c2-after.tsv`

Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`, freeze commit `afe17f416eec04dcf3f480b580a8f928de61d19d`, base `bf618f6c5c09d302994871c94903abbea2deb60d`.
Read-only scout. No files outside this report were written in the lane; no git/jj mutation anywhere in the lane; no tool installs were needed (tooling authorization 2026-10-19: nothing installed, nothing upgraded). All work ran under `/fast/scratch/hyaku/souji-r42/R42scout02/` (deleted before yield; every output cited below is pasted verbatim, so no scratch path is evidence).

---

## 0. Ground truth reproduced first

Command (read-only; TMPDIR pointed at scratch):

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin
TMPDIR=$S/tmp python3 -B tools/souji-declared-evidence.py --root . \
  --rev bf618f6c5c09d302994871c94903abbea2deb60d --file SCORECARD.md --format tsv
```

Observed: `rc=1`, last line `assertions=474 resolved=404 skipped=780 mismatches=70` — byte-identical to the preregistered population (preregistration.txt, C1 predicate). The rows this ticket owns:

```
68	42259756a06538a5dfb81cb82fba20737eacdcfd5c06b9b36594071b26f9da44	C	mismatch:digest	sha256 is bb506469be860f994f74f4c7d6eb1c949a4931b676cdb60f9f79de041d12f27f
68	71b89eb3c7ce417979c5fce2c759dafe023af21d6310fde49197c766b8f28897	C	mismatch:digest	sha256 is bb506469be860f994f74f4c7d6eb1c949a4931b676cdb60f9f79de041d12f27f
175	c2-after.tsv	A	mismatch:path-absent	not in tree at bf618f6c5c09d302994871c94903abbea2deb60d
175	c2-fixture-after.tsv	A	mismatch:path-absent	not in tree at bf618f6c5c09d302994871c94903abbea2deb60d
```

(The sibling rows at 68/175 — `count-objects-garbage-readings-r25.md`, `repo-size-census-readonly.md`, the three `census/round-24/records/*` paths, `1efe406`, `a65fac9`, `778747e` — resolve or are another seat's items; `c2-fixture-after.tsv` at 175 is resolved by the counter, see §3.)

## 1. The pairing rule (instrument source, frozen)

`tools/souji-declared-evidence.py`, `classify()` cell pass:

```python
for cell in cells_of(line):
    scan = SPAN_RE.sub(... keep 7-64 hex spans ...)  # digests stay findable
    digests = {d.lower() for d in HEX64_RE.findall(scan)}
    if digests:
        path_spans = [p for p in SPAN_RE.findall(cell) if PATH_RE.match(p)]
        if len(path_spans) == 1:
            for d in sorted(digests):
                assertions.append(dict(..., cls="C", rev=rev, path=path_spans[0]))
        else:
            skipped += len(digests)
```

and `evaluate()` class C: `sha256(blob(rev, path))` at the audited revision, `"mismatch:digest"` with detail `sha256 is <got>`.

**Pairing is strictly per table cell: every 64-hex digest in a cell is bound to the cell's only PATH_RE-matching backticked span, then hashed at the audited rev.** A digest never sees paths named in sibling cells.

## 2. Line 68 — the two digests

Line 68 at base (r24 C2 row, `### Round 24 measurements`, line 63) ends with the cell:

```
| tool `tools/souji-coverage-agreement.py` sha256 `71b89eb3c7ce417979c5fce2c759dafe023af21d6310fde49197c766b8f28897`; fixture sha256 `42259756a06538a5dfb81cb82fba20737eacdcfd5c06b9b36594071b26f9da44` |
```

One path span (`tools/souji-coverage-agreement.py`) + two digests → both class-C items bound to the tool path. At base the tool hashes `bb506469…` (verified: `git show bf618f6c…:tools/souji-coverage-agreement.py | sha256sum`), hence both rows read `bb506469…`.

### 2a. Digest sweep (global, complete)

Command: sweep of **every blob object in the repo** (`git cat-file --batch-all-objects --batch-check` → 8457 blobs → `git cat-file --batch` → sha256 of each content), then path/commit mapping via `git rev-list --all --objects` and `git log --all --find-object=<oid> --name-only`. Output (verbatim):

```
blob objects: 8457
hits: 2

DIGEST 42259756a06538a5dfb81cb82fba20737eacdcfd5c06b9b36594071b26f9da44
  blob object: add3917e87d23a4c5095916ccc7f22f294bce645 size: 15459
  paths (rev-list --all --objects): ['.ufo/waves/round-24/w1/r24-coverage-agreement.py']
  ... touches tests/fixtures/r24-coverage-agreement.py @ 0cc6bba7, 98e5203d (2026-10-26),
      census/round-26/waves/assimilation/validate/... @ 37e7fd95, 765fe8bd,
      .ufo/waves/round-26/assimilation/validate/... @ 2e0a2688, 50443f57, 6845bab6,
      .ufo/waves/round-24/w1/r24-coverage-agreement.py @ 1b52a886, c3ca7ad3,
      tests/fixtures/r24-coverage-agreement.py @ 1efe406e, 24ede803 (2026-10-25)

DIGEST 71b89eb3c7ce417979c5fce2c759dafe023af21d6310fde49197c766b8f28897
  blob object: 16c44d7c305be43b7bdef11459bfe46c0535f2bf size: 6470
  paths (rev-list --all --objects): ['.ufo/waves/round-24/w1/souji-coverage-agreement.py']
  ... touches tools/souji-coverage-agreement.py @ 38419f83, 7e4dbef9, 99b622c5, 604cd441,
      .ufo/waves/round-24/w1/souji-coverage-agreement.py @ 1b52a886, c3ca7ad3,
      tools/souji-coverage-agreement.py @ 1efe406e, 24ede803 (2026-10-25)
```

Per-revision hashing of both canonical paths over all refs (`git log --all --format='%H %ad' --date=short -- <path>` × `git show <c>:<path> | sha256sum`), verbatim:

```
tools/souji-coverage-agreement.py
2026-10-25 38419f83… bb506469be860f994f74f4c7d6eb1c949a4931b676cdb60f9f79de041d12f27f
2026-10-25 7e4dbef9… bb506469…
2026-10-25 99b622c5… bb506469…
2026-10-25 604cd441… bb506469…
2026-10-25 1efe406e… 71b89eb3c7ce417979c5fce2c759dafe023af21d6310fde49197c766b8f28897
2026-10-25 24ede803… 71b89eb3c7ce417979c5fce2c759dafe023af21d6310fde49197c766b8f28897
tests/fixtures/r24-coverage-agreement.py
2026-10-26 0cc6bba7… 65d2d681813f5c093ed31e29981ea817763d563d454f9f3ebac532099c17f669
2026-10-26 98e5203d… 65d2d681…
2026-10-25 1efe406e… 42259756a06538a5dfb81cb82fba20737eacdcfd5c06b9b36594071b26f9da44
2026-10-25 24ede803… 42259756a06538a5dfb81cb82fba20737eacdcfd5c06b9b36594071b26f9da44
```

Base cross-check: `tool@base = bb506469…`, `fixture@base = 65d2d681…`, `tool@1efe406 = 71b89eb3…`, `fixture@1efe406 = 42259756…`. Each digest exists as exactly ONE blob object in the entire object store — the sweep is exhaustive, nothing unmatched.

### 2b. Verdicts, line 68

- **`68:71b89eb3…`** — pairing is CORRECT (digest declared as the tool's sha256; cell's only path is that tool). Cause: **stale declared digest**. The row pins the r24 run, whose before-cell even says "with the tool bytes of `1efe406`", and at `1efe406`/`24ede803` the tool really hashes `71b89eb3…`. The tool was edited later on 2026-10-25 (first `bb506469…` revision: `604cd441`) and is unchanged since, so at the audited base it hashes `bb506469…`. SCORECARD was true when written and false at base — the line declares a revision-pinned truth without carrying the revision.
- **`68:42259756…`** — declared as the **fixture** sha256; the fixture (`tests/fixtures/r24-coverage-agreement.py`) is named only in the counting-command cell, never in the digest cell. The class-C rule binds the digest to the only path in its own cell — the tool — so it could never resolve this digest, even against r24-era bytes. Two stacked causes: (1) **instrument class-C pairing false positive** (cross-cell reference invisible to the per-cell rule); (2) the fixture bytes also changed 2026-10-26 (`65d2d681…` at base), so the digest is additionally stale at base. At `1efe406` the fixture truly hashes `42259756…` — the SCORECARD cell text was accurate when written.

## 3. Line 175 — bare `c2-after.tsv`

Line 175 (r24 row of the `## Capabilities` table) counting-command cell:

```
`python3 -B tools/souji-coverage-agreement.py --root . --rev <full40>`; `census/round-24/records/c2-control-base.tsv` (2 at base), `c2-after.tsv` (0); `tests/fixtures/r24-coverage-agreement.py` 9/9 (`c2-fixture-after.tsv`)
```

**Which round it means: `census/round-24/records/c2-after.tsv`.** Four independent in-cell/row signals: the row label "(r24)", the trailing `| r24 |` column, the sibling fully-qualified `census/round-24/records/c2-control-base.tsv` in the same cell, and the sibling shorthand `c2-fixture-after.tsv` whose only committed match is round-24. Line 68 (same round's measurement row) cites the same artifact fully qualified.

**Why the counter's rules do not resolve it** (`census/round-42/c1-counter.py`, `derive()`): the token is path-absent at base, so the basename rules run. At base the basename matches **five** committed paths:

```
census/round-24/records/c2-after.tsv
census/round-25/records/c2-after.tsv
census/round-26/records/c2-after.tsv
census/round-27/records/c2-after.tsv
census/round-28/records/c2-after.tsv
```

(`git ls-tree -r --name-only bf618f6c… | grep -E '/c2-after\.tsv$'` — verbatim list above.) The context rule takes the round from the nearest preceding heading matching `^#{1,4}\s.*?\bRound\s+(\d+)\b`; headings before 175 are `### Round 24 measurements` (63) → `### Round 23 measurements` (97) → `## Capabilities` (143, no round → does not reset). So `context[175] = 23`, the `round-23/` filter selects zero of the five, `len(ends) != 1`, and `corpus/knowledge/c2-after.tsv` does not exist → `unresolved`. The sibling `c2-fixture-after.tsv` resolves because its basename is unique at base (only `census/round-24/records/c2-fixture-after.tsv`) — uniqueness, not context, is what saves it. Note the counter rule limit, not a SCORECARD error: had the context been 24, the round-24 filter would have selected exactly one path.

Wave-input cross-check (`.ufo/waves/round-42/w1/inputs/c1-register-candidate.tsv`), verbatim rows: `175 c2-after.tsv unresolved -`, `175 c2-fixture-after.tsv resolved census/round-24/records/c2-fixture-after.tsv`, `68 42259756… unresolved -`, `68 71b89eb3… unresolved -` — consistent with this analysis and with the 65/5 split.

## 4. Summary lines

```
68:42259756a06538a5dfb81cb82fba20737eacdcfd5c06b9b36594071b26f9da44 | class-C pairing binds each digest to its own cell's only backticked path (tools/souji-coverage-agreement.py); the fixture is named only in the sibling counting-command cell; fixture bytes also changed 2026-10-26 (65d2d681… at base) | tests/fixtures/r24-coverage-agreement.py@1efe406e7f39b8fe736be2a566053703a571ffc0 (also @24ede8033e86e5bd7d5381a5a45adc84abeb24d5; candidate copy .ufo/waves/round-24/w1/r24-coverage-agreement.py) | instrument false-positive (cross-cell pairing); the SCORECARD cell text was true at the pinned rev 1efe406
68:71b89eb3c7ce417979c5fce2c759dafe023af21d6310fde49197c766b8f28897 | stale declared digest: r24-era tool bytes; tool edited later on 2026-10-25 (first bb506469… revision 604cd441) and unchanged through base, where the correct pairing hashes bb506469… | tools/souji-coverage-agreement.py@1efe406e7f39b8fe736be2a566053703a571ffc0 (also @24ede8033e86e5bd7d5381a5a45adc84abeb24d5) | neither: SCORECARD true when written, instrument faithful at base (no pairing error)
175:c2-after.tsv | bare basename matches 5 committed paths census/round-{24,25,26,27,28}/records/c2-after.tsv and the counter's heading-context rule holds Round 23 for the ## Capabilities table (last Round-N heading is line 97), so no rule narrows to one | census/round-24/records/c2-after.tsv | neither — counter rule limit (cross-round basename collision + heading-context); the line means the r24 artifact
```

Frozen-instrument observations (findings for the L1, no edits made): the class-C per-cell pairing cannot express digest↔path declarations that live in different cells (cause of the 42259756 false positive), and `derive()`'s context rule inherits a round number across a heading that carries none. Both are named limits of the frozen instrument/counter, reported here per preregistration rule 1.
