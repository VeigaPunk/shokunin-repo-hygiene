# W1ScoutOverlap — sibling overlap (souji r39 C1/C2/C3)

Axes walked: exact-name absence, then the three binding surfaces (revision resolution for a citation counter; a record-file parser with a documented class map; a mutant battery over a parser). Each hit is contested only if it binds the same contract; otherwise adjacent.

Scope: 20 sibling lanes under `/home/vgpnk/Projects/shokunin/*-shokunin/` excluding `souji-shokunin`. Read-only. No sibling file was written. No LSP server covers this cross-lane text scan.

Local surface (souji, comparison only):

- `tools/souji-citation-reconcile.py` — `--rev` / `--register-rev`; non-commit is `REFUSAL REV-UNRESOLVED`, exit 2 (`ancestor_status`, lines 204-211).
- `tools/souji-worktree-drift.py` — census TSV. Docstring lines 42-61: `RECORD-MISSING` (EACCES/ELOOP), `RECORD-MALFORMED` (ENOENT / non-regular / schema), `RECORD-EMPTY`, `RECORD-OUTSIDE-ROOT`, plus JSON-* and `USAGE`.
- Battery: `tests/fixtures/r39-drift-record-rules.py` (M11-M14). Absent from every sibling.

## Commands and observed output

Scratch `/fast/scratch/hyaku/souji-r39/W1ScoutOverlap` held the sibling list and grep dumps. Removed with `rm -rf` at the end of this seat; not left on disk.

### Check 1 — exact tool and fixture names

```
grep -rlI --exclude-dir=.git --exclude-dir=.jj --exclude-dir=node_modules --exclude-dir=__pycache__ \
  -e souji-citation-reconcile -e souji-worktree-drift -e r39-citation-rev -e r39-drift-record-rules \
  <20 sibling lanes>
```

Observed: `exit=0`, `0` files (whole trees, `.ufo` included).

Verdict: no sibling binds these four names. Not contested.

### Check 2 — `record-parse`

```
grep -rlI --exclude-dir=.git --exclude-dir=.jj --exclude-dir=node_modules --exclude-dir=__pycache__ \
  record-parse <20 sibling lanes>
```

Observed: `0` files (whole trees, `.ufo` included).

Variant, `.ufo` excluded:

```
grep -rlI --exclude-dir=.git --exclude-dir=.jj --exclude-dir=node_modules \
  --exclude-dir=__pycache__ --exclude-dir=.ufo \
  -e record-parse -e record_parse -e parse_record <20 sibling lanes>
```

Observed two files:

```
/home/vgpnk/Projects/shokunin/game-dev-2d-shokunin/reports/round-103/mutations/mut04.py
/home/vgpnk/Projects/shokunin/mori-shokunin/tools/mori-journal-window.py
```

```
grep -n -E 'record-parse|record_parse|parse_record' mori-journal-window.py mut04.py
```

- `mut04.py:369` `def parse_record(text: str):` — Godot PCK header-census echo mutant. Adjacent.
- `mori-journal-window.py:362` `def _parse_records(raw):` — JSONL; reasons `empty-capture` and `malformed-json` (lines 362-378). Adjacent.

Verdict: literal `record-parse` is absent. Not contested.

### Check 3 — word `citation`

Narrow roots: each sibling `tools/`, `tests/`, `fixtures/`, `corpus/`, `scripts/` that exists (32 roots).

```
grep -rlI -e citation <narrow roots>
```

Observed: `1867` files. Almost all lesson/corpus prose. Binding entry points were taken from tool filenames and then read. Not 1867 contested surfaces.

### Check 4 — phrase `mutation battery`

Same narrow roots: `34` files.

Whole sibling trees, `.ufo` excluded, counted by lane:

```
     11 audio-shokunin
      3 game-dev-2d-shokunin
      6 game-dev-3d-shokunin
      1 kaidoku-shokunin
      1 kama-shokunin
      1 kasegi-shokunin
     26 kengaku-shokunin
      5 kotoba-shokunin
      3 kotodama-shokunin
      5 kumitate-shokunin
      1 mori-shokunin
      2 tabi-shokunin
      2 tsukuroi-shokunin
```

Most hits are prose. Runnable batteries are under surface (c).

### Check 5 — souji class tokens

```
grep -rlI --exclude-dir=.git --exclude-dir=.jj --exclude-dir=node_modules \
  --exclude-dir=__pycache__ --exclude-dir=.ufo \
  -e RECORD-MALFORMED -e RECORD-MISSING -e RECORD-OUTSIDE-ROOT \
  -e REV-UNRESOLVED -e souji-citation-reconcile -e souji-worktree-drift \
  <20 sibling lanes>
```

Observed: `files=3`, all tsukuroi, none the souji tool names:

```
/home/vgpnk/Projects/shokunin/tsukuroi-shokunin/corpus/lessons/round-26.md
/home/vgpnk/Projects/shokunin/tsukuroi-shokunin/corpus/QUALITY.md
/home/vgpnk/Projects/shokunin/tsukuroi-shokunin/tools/measure-update-recheck.py
```

Quoted:

- `measure-update-recheck.py:765` `raise Cannot("E-C2-RECORD-MISSING", RECORD, "record absent while snapshot exists")`
- `QUALITY.md:125` rule id `R26-GATE-RECORD-MISSING`
- `round-26.md:64` and `:87` the same rule id

`RECORD-MALFORMED`, `RECORD-OUTSIDE-ROOT`, and `REV-UNRESOLVED` did not appear. Substring collision only. Adjacent. Not the drift class map.

## Surface (a) — revision resolution for a citation counter

No sibling implements the souji contract (cell register, `commit` vs `receipt_rev`, `--rev` and `--register-rev`, non-commit refused as `REFUSAL REV-UNRESOLVED` exit 2). Closest entry points, all adjacent:

| Path | Entry | What it binds | Class |
|---|---|---|---|
| `tsukuroi-shokunin/tools/_revision.py` | imported by `--revision` gates; `python3 tools/_revision.py --selftest` | Landed-commit binder. Lines 11-24: hex 7-64 else `E-REVISION-INVALID`; non-commit peel fails the same id; `merge-base` rc>=2 is `E-GIT-FAILED`, "never not an ancestor"; exit class 2. Judge: `tools/check-revision-binding.py`. | Adjacent. Same failure shape as r39 R11, different ids, not a citation register. |
| `tsukuroi-shokunin/tools/check-section-citations.py` | `--revision` | Section-citation errata (`tsukuroi-section-citation-errata-v1`). Lines 18-26: git objects only, explicit hex, binding owned by `_revision.py`. Exit 0/1/2. | Adjacent. |
| `kake-shokunin/scripts/citation_lint.py` | `--root PATH [--revision REV]` | Commit citations in `SCORECARD.md` and `LOG.md`. Lines 19-20: exit 0/1/2/64. `--revision` is `git show` (`read_population` lines 85-90); a miss is `InputError` `cannot read`. Tokens use `git cat-file -e` (any object, lines 126-136). | Adjacent. |
| `kama-shokunin/tools/citation-provenance.py` | `--registry --docs --lane` | Tokens `cite(<rev>, <path>, sha256=…)`. Lines 11-20: `git cat-file` at `<rev>:<path>`; exit 2 is unusable inputs. No `REV-UNRESOLVED`. | Adjacent. |
| `kama-shokunin/tools/round53-cited-path-check.py` and `round54-cited-path-check.py` | ledger at `--tip` | Citation tokens plus a row `class` vocabulary. Exit 0/1/2. | Adjacent. |
| `kumitate-shokunin/scripts/cite-check.mjs` | `node scripts/cite-check.mjs` | Path/line/symbol pins (`kumitate-cite-check-v1`). Exit 2 is a bad directory, not git rev resolution. | Adjacent. |
| `kotodama-shokunin/tools/check-cited-lines.py` | markdown source-id scan | No git revision argument. | Adjacent. |

Verdict (a): not contested. Do not absorb `_revision.py`. The r39 predicate is 40-hex `REFUSAL REV-UNRESOLVED` on the souji reconciler.

## Surface (b) — record-file parser with a documented class map

No sibling documents `RECORD-MALFORMED` or `RECORD-OUTSIDE-ROOT`. Adjacent parsers:

| Path | Entry | Class map | Class |
|---|---|---|---|
| `chousa-shokunin/tools/store-record-audit.py` | `--record` `--store` | Docstring lines 4-10: `ORPHAN`, `RECORD_ONLY`, `BYTES_STALE`, `STORE_BUT_RECORD_DENIES` over `refetch.tsv`. | Adjacent. |
| `kaidoku-shokunin/tools/round-47/record.py` | C2 counter `--rev` | Lines 7-19 and line 38 `CLASSES = ("seats", "window", "path", "rev", "axes")`. SCORECARD sections; hex must be an ancestor of `--rev`. | Adjacent. |
| `tsukuroi-shokunin/tools/measure-update-recheck.py` | update recheck | `E-C2-RECORD-MISSING` when the record is absent and the snapshot exists (line 765). | Adjacent name collision. |
| `mori-shokunin/tools/mori-journal-window.py` | `_parse_records` | `empty-capture`, `malformed-json`. | Adjacent. |

Verdict (b): not contested. Souji's docstring class map stays lane-local.

## Surface (c) — mutant battery over a parser

No sibling battery targets `souji-worktree-drift.py` or `r39-drift-record-rules.py` (check 1 empty).

| Path | Entry | What is mutated | Class |
|---|---|---|---|
| `kumitate-shokunin/scripts/gate-mutants.mjs` | `--target cite-check\|wave-census`, `--selftest` | Contract `kumitate-gate-mutants-v2`. Lines 3-11: kill iff selftest exits non-zero, stdout has `VERDICT: FAIL`, second run agrees. Line 36 targets `cite-check` and `wave-census`. Manifest from line 154 patches `cite-check.mjs`. | Adjacent. Battery over a citation parser, not the drift record parser. |
| `tameshi-shokunin/tools/mutate-and-run.sh` | regression leg `js-cite-check` | Lines 16-18 and 1096-1102: replays `kumitate-shokunin/scripts/cite-check.mjs` at rev `1205c662…` via `git show`. Also sources-check, round-gate, kagi `drift-pins.sh`. | Adjacent method runner. |
| `audio-shokunin/corpus/live/r89-critic/mutate.py` | r89 critic | Lines 2-5: mutates one receipt entry, execs the verdict block. | Adjacent. Not a parser. |
| `kengaku-shokunin/corpus/evidence/round12-fleet/r12-mutation.md` | prose | Title "Round-12 mutation battery". | Adjacent prose. |
| `kama-shokunin/tools/shortcut-tally.py` | tally | Line 8 counts mutants that survived "their mutation battery". Does not run one. | Adjacent mention. |
| `game-dev-2d-shokunin/reports/round-103/mutations/mut04.py` | `setup\|probe\|forges\|check` | Own `parse_record` for PCK probe records (line 369). | Adjacent one-off. |

Verdict (c): not contested. M11-M14 does not collide with kumitate's cite-check battery or tameshi's replay of it.

## Seat verdict

All three surfaces are uncontested. Exact tool and fixture names, `record-parse`, `REV-UNRESOLVED`, `RECORD-MALFORMED`, and `RECORD-OUTSIDE-ROOT` are absent outside souji. Adjacent mechanisms that must not be absorbed: tsukuroi `_revision.py`, kake `citation_lint.py`, kama `citation-provenance.py`, chousa `store-record-audit.py`, kaidoku `round-47/record.py`, kumitate `gate-mutants.mjs`, tameshi `mutate-and-run.sh` leg `js-cite-check`.

Confidence: high on the empty exact-name and class-token searches. High on the adjacent rows whose lines were read. Not claimed: every one of the 1867 `citation` prose files was opened.

Tooling: no install.
