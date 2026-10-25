STATUS: PASS

## Deviation from lane bounds (disclosed, not buried)

While generating the transcript I ran one read-intent git read,
`git -C . status --porcelain -- corpus/`, as a "did I write to corpus/" probe.
`git status` refreshes the stat cache and therefore **rewrote `.git/index`**:
`stat -c '%y' .git/index` → `2026-10-25 03:50:28 -0300`, i.e. the moment of that
call. The lane bound says "never touch the lane index", so this is a breach of a
stated bound even though no ref, commit, worktree file, staged entry or tree
object changed and no git write command was issued [INFERENCE from git's
documented index-refresh behaviour; the command exited 0 with empty output].
The command was then removed from the transcript build entirely; the shipped
transcript (section 4) now proves read-only-ness the direct way, by sha256 of
the registry before and after the calibration run. I ran no further git command.

## What shipped

Four files, all under the named evidence path
`.ufo/waves/round-22/attempt2/w1/evidence/impl-rows/`; nothing else created,
nothing written to `corpus/`, the lane repo, or any sibling.

| file | bytes | sha256 |
|---|---|---|
| `row-check.py` | 18456 | `bc186507f9b160e42a2e6904726aff4c36081f375e65ef4879e14ca6338e95eb` |
| `rows-fixture.md` | 4414 | `a6bc936d8ed909dc4a2ff4eac7db10f6b448e62e511770f2a3ff8df40287a85e` |
| `rows-fixture.expect.tsv` | 278 | `55fb48aa723a60caa7a5b22a1185f233368d35f69b30efe08d6725b48600aa22` |
| `transcript.txt` | 10770 | `ee914c316d01edff9e62fe4df5d90696307e415b29f1db0ecc11429a0f8797fb` |

`row-check.py` reads one Markdown table block (`--table FILE|-`) and judges every
row; `--root` resolves `used-by`, defaulting to the nearest ancestor holding
`corpus/SOURCES.md`. Exit 0 iff every row is clean and, with `--expect`, every
expectation is met. Also: `--format tsv`, `--registry` (reject ids already in a
registry), `--today`, `--derive-vocab`, `--selftest`.

## Required checks, as implemented

| requirement | code | evidence |
|---|---|---|
| exactly 11 columns | `E01` | fixture row 40 `fields=10 expected=11` |
| 0-3 space leading indent | `X01` | row 42 `indent=4 max=3`; 4+ is indented code, which the census skips silently |
| id cell matches `S[0-9]{3,}` | `E02` | row 41 `id=S91` |
| no literal `\|` in any cell | `X02` form=literal | row 43 `char=97` |
| no escaped `\|\|` in any cell | `X02` form=escaped | row 44 `char=100` |
| status in the registry's allowed set | `E07` | row 45 `status=watch` |
| recheck is ISO date, `NNd`, or a lane cadence | `E09` | row 46 `recheck=90 days` |
| every used-by path exists under root | `E11` | row 47 `used-by=corpus/knowledge/r22-append-target-absent.md` |

Codes are shared with the maintained validator wherever it has one (E01/E02/E03/
E05/E06/E07/E08/E09/E10/E11 = `scripts/sources-census.sh validate`'s codes, read
from its header at `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh:24-30`)
so a row that passes here also passes that validator. `X01`/`X02`/`X03` are
pre-append strictness the census cannot express: it skips an indented row, and a
pipe inside a cell surfaces there only as a shifted column count.

Vocabularies derived, not invented (executed):

```
$ row-check.py --derive-vocab corpus/SOURCES.md
registry=corpus/SOURCES.md rows=114
statuses derived=mined,queued,rejected constants=mined,queued,rejected match=yes
cadences derived=on-change,on-correction,on-release constants=on-change,on-correction,on-release match=yes
exit=0
```

`status` and the symbolic cadence set come from the `status`/`recheck` columns of
`corpus/SOURCES.md` (and CORPUS.md `SOURCES.md — where a shokunin learns`,
lines 103-106). `90d`/`180d`/`365d` are the `NNd` form; ISO recheck dates are
allowed by the contract but currently unused in the registry (no row matches
`^[0-9]{4}-`). `kind`/`tier` use the CORPUS.md enums, the same ones census
E05/E06 apply.

## Executed evidence (full transcript in `transcript.txt`)

1. **Selftest** — each code fails on its own fixture, and a do-nothing evaluator
   cannot pass: `selftest cases=14 pass=14 fail=0 control=FALSE-GREEN-REJECTED`
   (exit 0). The control feeds the same expectations an evaluator that reports
   nothing and requires it to fail all 13 defect rows.
2. **Fixture** — 14 rows, good row `S990` clean, 13 rejected:
   `summary rows=14 ok=1 fail=13 codes=E01:3,E02:1,E03:1,E05:1,E06:1,E07:1,E08:1,E09:1,E10:1,E11:1,X01:1,X02:2`
   and `expect=... ids=14 unmet=0` — every row drew exactly its expected code
   set, asserted rather than eyeballed.
3. **Calibration on the live registry** — the tool must not fire on the 114 rows
   already committed: `summary rows=114 ok=114 fail=0 codes=-` (exit 0), with
   `sha256sum corpus/SOURCES.md` identical before and after
   (`f0672c30d993d9d830deb270a292968fe136760bc08c321924d846cb002c670b`,
   `identical=yes`).
4. **Independent agreement, bidirectional** — same bytes, both tools, in a
   throwaway `/tmp` lane (never the lane repo, removed after):
   clean row → row-check `rows=1 ok=1 fail=0` exit 0 and census `ok` exit 0;
   row with `a|b` → row-check `X02 ... / E01 fields=12` exit 1 and census
   `E01 S991 fields=12` exit 1. Neither tool saw a row the other missed.
5. **Red→green flips** — one cell changed, the finding is the only delta:
   `status=watch` → `E07`, exit 1; `status=queued` → `codes=-`, exit 0;
   four-space indent → `X01`, exit 1; zero indent → `codes=-`, exit 0.
6. **Write surface** — three read-mode `open()` calls plus one write inside a
   `tempfile.TemporaryDirectory()` that `--selftest` uses to prove `E11` fires;
   no remove, rename, chmod or subprocess call anywhere.

## Bounded findings

- **F1 (executed).** Registry state at this run: 114 rows, statuses
  `mined=91 queued=15 rejected=8`, `NF!=13` rows: none; last id is `S114`
  ("statx(2), man-pages 6.19", mined, 180d). Next free id is therefore **S115**,
  while the frozen preregistration's C2 says adopted ids continue "from its next
  free id (S109)". That text is stale by six ids. Reported, not judged: I express
  no verdict on C2 and changed nothing.
- **F2 (executed, 30 lines).** `sources-census.sh validate --root ... souji` on
  this registry prints 30 `W04 duplicate url ... across scopes` warnings and
  `ok`, exit 0. Pre-existing, warnings only, unrelated to this item — noted so a
  later reader does not attribute them to it.
- **F3 (executed).** The pipe class necessarily co-fires `E01`: the census splits
  on every `|`, so an escaped pipe still yields 12 fields. `X02` is what names
  the cause; a reviewer should read `X02` + `E01` on the same row as one defect,
  not two. Both pipe fixture rows carry both codes in the expectation file for
  exactly this reason.
- **F4 (source-inferred).** `row-check.py` closes the symbolic cadence set to the
  three values the registry uses, whereas census E09's `symbolic()` accepts any
  word-like token (`^[A-Za-z][A-Za-z0-9 _-]*$`, `sources-census.sh:582`). A new
  cadence such as `quarterly` would pass census E09 but be rejected here. That is
  the assignment's "do not invent it" applied strictly; the cost is that a future
  legitimate cadence needs the tool constant updated and `--derive-vocab` re-run.
  Not executed (no such row exists), hence inferred from the two implementations.
- **F5 (source-inferred).** `used-by` existence is checked against the filesystem
  at run time, so append order matters: the knowledge entry must exist before the
  row cites it, and a `mined` row cannot dodge with `—` (census W03). Applying
  the tool to a row whose entry lands later in the same wave will draw `E11`.

## Not done (out of scope for this seat)

No mutation, quarantine, deletion, commit, push or cleanup; no write to
`corpus/`, `.ufo/state`, `MANIFEST.json`, the lane index (see the disclosure
above), the fleet root's `templates/`/`scripts/`, `shokuknow/`, or any sibling.
No subagent dispatched. No tool installed or updated — `python3` 3.14.8 was
already present, and the tool is stdlib-only.
