STATUS: PASS

# ImplDeclaredA — candidate A of `tools/souji-declared-evidence.py` (round 22, attempt 2, C1)

Scope: implement candidate A of the declared-evidence calibration tool to the frozen
contract in `.ufo/waves/round-22/attempt2/preregistration.txt` (claim C1), with selftest,
base-revision measurement and full skipped-token enumeration. I did not edit
`SCORECARD.md`, `tools/`, `.ufo/state`, the index, or any sibling repo. No tool was
installed or updated (no pacman/uv/npx/cargo/npm transaction was run).

## Files written (only these)

| path | sha256 |
|---|---|
| `.ufo/waves/round-22/attempt2/w1/evidence/impl-a/souji-declared-evidence.py` | `fdde02759a281aba003358636ec02707afcfe240df83ec7de0f91a359d6aae8c` |
| `.ufo/waves/round-22/attempt2/w1/evidence/impl-a/selftest.txt` | `d3363b18de352c0ec35f4668f69fdfee48c80522bbb2025cd33c2f4d2975254d` |
| `.ufo/waves/round-22/attempt2/w1/evidence/impl-a/base-4edb25d.counts` | `616e9f59ab45e878ab5cbc41fedae90e2a51e8881ebcdc50f40b8209a03030d5` |
| `.ufo/waves/round-22/attempt2/w1/evidence/impl-a/base-4edb25d.tsv` | `8838663f28dd28b04f0cda35001b8c921c785433c79b67fdf47d3ea73dd42e65` |
| `.ufo/waves/round-22/attempt2/w1/evidence/impl-a/base-skipped.txt` | `7abf02f84c0569cfeb2941467dd08d1d79eac081e143441d508391313649d1fc` |
| `.ufo/waves/round-22/attempt2/w1/evidence/impl-a/tip-70af563.counts` | `d11de402d850e81a86489ae6babb60ef638528d49dd9bdd8cd69f434af511fef` |
| `.ufo/waves/round-22/attempt2/w1/evidence/impl-a/tip-70af563.tsv` | `51c7a99b97e9c39dd17d85937208174eb119bbe25c2698755e8dd3ee7d400714` |
| `.ufo/waves/round-22/attempt2/w1/ImplDeclaredA.md` | this report |

## Interface implemented (as frozen)

`python3 -B souji-declared-evidence.py --root DIR --file FILE --rev REV [--format counts|tsv] [--selftest]`

* counts line, exactly: `assertions=<N> resolved=<R> skipped=<S> mismatches=<M>`; exit 0 iff M == 0, else 1; exit 2 for an unresolvable `--rev`, a `--file` absent at `--rev`, or an absolute `--file`.
* The declaration is read from committed bytes at `--rev` (`git show <rev>:<file>`), never from the worktree.
* Classes exactly as frozen: A = backticked repo-relative path with a class extension, optional `:<line>`, optional glob, present among tracked files at `--rev`; B = bare 7..40-hex token in a revision-context cell resolved by `git cat-file -e <tok>^{commit}`; C = 64-hex token in a cell with exactly one backticked path, compared to sha256 of that path's bytes at `--rev`.
* Runtime subprocesses: only `git -C <root> cat-file`, `git -C <root> ls-tree -r --name-only`, `git -C <root> show`, with `--no-optional-locks -c maintenance.auto=false`. No network. sha256 via `hashlib`.
* Scratch: only `tempfile.mkdtemp(dir="/var/tmp")` in `--selftest`, removed by `shutil.rmtree` in a `finally`; no `/tmp` use. Verified after the run: `ls -d /var/tmp/souji-declared-evidence-*` → no scratch residue.
* `--format tsv` is my own extension for the required skipped enumeration: `#line<TAB>token<TAB>class<TAB>verdict<TAB>detail`, then the counts line last.

## Selftest transcript (executed, exit 0)

Command: `python3 -B .ufo/waves/round-22/attempt2/w1/evidence/impl-a/souji-declared-evidence.py --selftest`

```
PASS 1 all-good declaration -> 0 mismatches [assertions=5 resolved=5 skipped=0 mismatches=0]
PASS 2 nonexistent path -> >=1 [assertions=2 resolved=1 skipped=0 mismatches=1]
PASS 3 dangling revision -> >=1 [assertions=2 resolved=1 skipped=0 mismatches=1]
PASS 4 wrong digest -> >=1 [assertions=3 resolved=2 skipped=0 mismatches=1]
PASS 5 path present only at a different revision -> >=1 [assertions=1 resolved=0 skipped=0 mismatches=1]
PASS control always-zero -> FALSE-GREEN-REJECTED [FALSE-GREEN-REJECTED]
selftest=6/6
control=FALSE-GREEN-REJECTED
exit=0
```

Fixture shape: one synthetic repo under the `/var/tmp` scratch dir with three commits (`present.sh` + `revonly.md`; `later.md`; the declaration fixtures). Fixture 1 exercises all three classes positively (A twice, B twice, C once); fixture 4's digest is 64 zeros on a present file; fixture 3 uses `deadbeef`×5. The control is an in-process always-zero "tool": it satisfies fixture 1 trivially but cannot produce the `>=1` that fixtures 2–5 require, so the same fixture set rejects it — this is the mech­anism reported as `control=FALSE-GREEN-REJECTED`, not a separate binary.

## Real base run (executed)

Command:
`python3 -B .ufo/waves/round-22/attempt2/w1/evidence/impl-a/souji-declared-evidence.py --root . --file SCORECARD.md --rev 4edb25d --format counts`

```
assertions=56 resolved=53 skipped=45 mismatches=3
exit=1
```

The three mismatches (all class A, `path absent at 4edb25d`) are the three the preregistration
names in prose (fleet-relative pointer, unnamed receipt, absent banked file):

| line | token | class | detail |
|---|---|---|---|
| 3 | `AXES.md` | A | path absent at 4edb25d (fleet `/home/vgpnk/Projects/shokunin/AXES.md`, not repo-relative in intent) |
| 63 | `reason-after.txt` | A | path absent at 4edb25d (the real file is `census/round-21/reason-after.txt`; the span names no receipt) |
| 77 | `.ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md` | A | path absent at 4edb25d (banked file never committed) |

Class distribution at base: A=50, B=6, C=0. Glob expansion exercised: `census/round-17/jj-receipts-*.txt` → `glob matches 2 tracked file(s) at 4edb25d`. The six B tokens (`41553adb139d06511dc386bb3ce4326aebfba675`, `31984f4`, `b912328d00d19f26918240710d0b5e0f334880ff`, `5fa6017`, `6f8ee0f`, `29c1f7e8df849be8ee1b2d62d2351e17ec9d21a8`) all resolve. Class C has no instance in the real document (no 64-hex token in `SCORECARD.md` at either revision); it is exercised only by the fixtures.

## Tip measurement at 70af563 (executed; bounded finding, not my repair)

Command: same with `--rev 70af563`.

```
assertions=57 resolved=56 skipped=46 mismatches=1
exit=1
```

Class distribution: A=52, B=5 (`4edb25dfe262515d0da63224bbba71e02e36cba5`, `6f8ee0f`, `31984f4`, `5fa6017`, `29c1f7e8df849be8ee1b2d62d2351e17ec9d21a8`, all resolved), C=0. The single
mismatch is `SCORECARD.md:83`, `.ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md`, class A,
path absent at 70af563 — the Planned-r4 bullet whose own sentence says the file is absent.
C1's M_after=0 therefore depends on that line's repair, which is outside my write authority
(I may write only this report and `evidence/impl-a/`). Both frozen repair branches are
available to its owner: drop the evidence role (de-backtick), or supply a committed receipt;
naming a revision would be false because the file exists at none. [INFERENCE, from the single
observed mismatch and the frozen repair rule: after a truth-preserving repair, M_after = 0.]
I told `L1Souji22.DraftScorecard` the same in one line; it owns/carries the drafted text, I do not.

## Every token classified `skipped` at base 4edb25d (45 tokens, with reason)

N+S = 56+45 = 101 candidate tokens. Duplicate tokens appear once per occurrence. Reasons are
the exact `detail` strings in `base-4edb25d.tsv` / `base-skipped.txt`.

| line | token | reason |
|---|---|---|
| 13 | `bash tests/fixtures/r21-reason-canary.sh --tool tools/souji-proc-census.sh --base <6ff3413-proc-file>` | span is a command or prose phrase, not a bare path |
| 13 | `6ff3413` | hex-shaped run embedded in an identifier or path (not bare) |
| 13 | `4d5bf78432de7f4afe38e6bf195fd7843bdcb7e3` | hex-shaped run embedded in an identifier or path (not bare) |
| 14 | `python3 -B tests/fixtures/r22-result-oracle.py --runner census/round-21/run-acceptance.py` | span is a command or prose phrase, not a bare path |
| 14 | `git show 41553adb139d06511dc386bb3ce4326aebfba675:census/round-21/run-acceptance.py \| python3 -B census/round-22/mutation-adequacy.py --grade-stdin` | span is a command or prose phrase, not a bare path |
| 14 | `python3 -B census/round-22/mutation-adequacy.py` | span is a command or prose phrase, not a bare path |
| 14 | `e41553adb139d06511dc386bb3ce4326aebfba675` | hex-shaped run embedded in an identifier or path (not bare) |
| 14 | `4f83fd222ffbd8825340221a8c426550ef891191` | hex-shaped run embedded in an identifier or path (not bare) |
| 14 | `473e98a498dbdb7315604251ab5a19a0823e7818` | hex-shaped run embedded in an identifier or path (not bare) |
| 15 | `195715439a08165ed7319ee6348844fcfba60029` | hex-shaped run embedded in an identifier or path (not bare) |
| 15 | `195715439a08165ed7319ee6348844fcfba60029` | hex-shaped run embedded in an identifier or path (not bare) |
| 29 | `## Post-review fixes` | span is a command or prose phrase, not a bare path |
| 32 | `python3 census/round-13/run-verification.py --retry-failed` | span is a command or prose phrase, not a bare path |
| 35 | `--round N --output census/round-N/<new>.json` | span is a command or prose phrase, not a bare path |
| 50 | `-c maintenance.auto=false` | span is a command or prose phrase, not a bare path |
| 50 | `worktree lock` | span is a command or prose phrase, not a bare path |
| 50 | `bash tests/fixtures/r12-maintenance-guard.sh --selftest` | span is a command or prose phrase, not a bare path |
| 51 | `python3 tools/souji-cert-evidence.py --selftest` | span is a command or prose phrase, not a bare path |
| 52 | `bash tests/fixtures/r13-quarantine-bounds.sh` | span is a command or prose phrase, not a bare path |
| 53 | `bash tests/fixtures/r13-repo-structure.sh --selftest --probe tools/souji-repo-structure.sh` | span is a command or prose phrase, not a bare path |
| 55 | `error` | span is not a path with a class extension, a glob, or a hex token |
| 55 | `info/attributes` | span is not a path with a class extension, a glob, or a hex token |
| 56 | `python3 tools/souji-landing-gate.py --selftest` | span is a command or prose phrase, not a bare path |
| 56 | `python3 tests/fixtures/r16-landing-gate.py` | span is a command or prose phrase, not a bare path |
| 58 | `status.showUntrackedFiles` | span is not a path with a class extension, a glob, or a hex token |
| 58 | `info/attributes` | span is not a path with a class extension, a glob, or a hex token |
| 58 | `python3 tests/fixtures/r17-census-hygiene.py --census tools/souji-census.sh` | span is a command or prose phrase, not a bare path |
| 58 | `4f48343` | hex-shaped run embedded in an identifier or path (not bare) |
| 59 | `refs/jj/*` | glob span is not a clean repo-relative path |
| 59 | `bash tests/fixtures/r17-jj-receipts.sh --tool-dir tools` | span is a command or prose phrase, not a bare path |
| 60 | `V-WRITE-RELATIVE` | span is not a path with a class extension, a glob, or a hex token |
| 60 | `python3 census/round-17/seat-audit-replay.py …` | span is a command or prose phrase, not a bare path |
| 60 | `census/round-17/transcript-manifest.py --check census/round-16/transcripts` | span is a command or prose phrase, not a bare path |
| 61 | `4800fd7` | hex-shaped run embedded in an identifier or path (not bare) |
| 62 | `4800fd7` | hex-shaped run embedded in an identifier or path (not bare) |
| 65 | `tools/souji-rev-pin.py --selftest` | span is a command or prose phrase, not a bare path |
| 77 | `20261018` | hex-shaped run embedded in an identifier or path (not bare) |
| 83 | `/tmp` | absolute or home-relative path; class A requires repo-relative |
| 87 | `corpus/lessons/round-{6..11}.md` | span is not a path with a class extension, a glob, or a hex token |
| 94 | `~user` | absolute or home-relative path; class A requires repo-relative |
| 98 | `:(optional)` | composite or annotated span outside frozen class A |
| 98 | `jj util gc` | span is a command or prose phrase, not a bare path |
| 99 | `:(optional)` | composite or annotated span outside frozen class A |
| 100 | `HEAD` | span is not a path with a class extension, a glob, or a hex token |
| 101 | `63bb887` | hex-shaped run embedded in an identifier or path (not bare) |

Reason totals: 21 command/prose spans, 12 embedded hex runs, 7 non-path non-hex spans,
2 absolute/home paths, 2 composite spans, 1 non-clean glob. At tip (70af563) the same
enumeration runs to 46 skipped (`tip-70af563.tsv`): 21 command/prose, 10 non-path non-hex,
9 embedded hex runs, 3 absolute/home, 2 composite, 1 non-clean glob.

## Class ambiguity resolutions (and why)

1. **Cell unit.** A table row is a line whose first non-space character is `|`; each field between delimiters is one cell. Any other line is one context unit. The frozen text says "cell", but prose in `SCORECARD.md` presents revision evidence too (e.g. line 113, Preregistration `29c1f7e8…`); treating prose as one cell keeps that evidence enumerated instead of silently invisible. A `|` inside a backticked span never splits a cell (line 14 carries `\|` inside a command span).
2. **"Bare" hex.** A candidate is a maximal `[0-9a-f]` run whose neighbours are outside `[A-Za-z0-9_.-]`; backticks do not disqualify it, because the prereg says a token "quoted as an example … is still class B/C". Hex-shaped runs that *are* glued into identifiers/paths (`base41553adb…`, `at473e98a…`, `…-4800fd7.json`, `souji-mint-20261018/`) are excluded as not bare and still counted as skipped with that reason. Length 7..40 → B, 64 → C, any other ≥7 → skipped (`hex run length is neither 7..40 … nor 64`); 41..63-hex is therefore never silently treated as a revision.
3. **`<rev>:<path>` composites.** Frozen class A has no such form, so a span of that shape is skipped (`composite or annotated span outside frozen class A`), not resolved at the named revision; class A requires presence at `--rev` only. On this document the choice is invisible: the only composite span is inside a command span, while its inner bare 40-hex token is still asserted (class B) and resolves.
4. **`:<line>` suffix.** Stripped before presence, and not validated (the frozen rule requires only presence of the path); `tools/x.py:120` and `tools/x.py` assert the same path.
5. **Glob.** `*` is expanded with `fnmatch.fnmatchcase` over `ls-tree -r --name-only <rev>`, so `*` may cross `/`; a glob (possibly matching several files) is never a class-C digest target.
6. **Class C "exactly one backticked path".** Counts clean non-glob repo-relative paths in the same cell; 0 or ≥2 paths → the 64-hex token is skipped with the count in the reason, never asserted against an arbitrary path.
7. **Revision context.** Case-insensitive word-boundary match on `commit|rev|revision|measured|at`, plus the plural inflections `commits|revisions` (same word), plus `census/round-<N>/` anywhere in the cell. `at` alone is enough, as frozen.
8. **Limits, stated rather than hidden.** Uppercase hex is not scanned (no uppercase SHA exists in the document); a class-A path is present iff it is a tracked file entry at `--rev` (a directory-only path would read absent — none occurred); escaped `\|` outside backticks would split a cell (none occurred); an unmatched backtick yields no candidate token.

## Cross-check against the landed tool (executed)

`tools/souji-declared-evidence.py` at 70af563, same revisions:

* base 4edb25d: landed `assertions=56 resolved=53 skipped=33 mismatches=3`; candidate A `56/53/45/3`. The per-assertion `(line, token, class)` multisets are identical (`comm -3` after dropping my TSV header: empty). The +12 skipped is exactly my enumeration of the 12 embedded hex runs listed above, which the landed tool does not emit as rows.
* tip 70af563: landed `57/56/37/1`; candidate A `57/56/46/1`; assertion multisets identical, +9 skipped = the 9 embedded runs at tip.

So on the real corpus the two implementations agree on every assertion, its class and its verdict; they differ only in how exhaustively excluded tokens are enumerated, which the prereg's `N+S` sentence asks for.

## Operability / read-only receipts (executed)

* Absolute `--root` from `/var/tmp` reproduces the base line (56/53/45/3, exit 1).
* Bad `--rev deadbeef…` → `error: revision does not resolve as a commit: …`, exit 2. Missing `--file nosuch.md` at 4edb25d → `error: declaration file not present at 4edb25d: nosuch.md`, exit 2. Both are non-zero, so neither can read as green.
* Runtime path writes nothing: the only writes in the file are in `selftest()` (fixture files and the mkdtemp dir, both under the removed scratch dir). [Source-inspected; the repo was not re-audited for writes beyond the absence of scratch residue.]
* `--selftest` necessarily runs `git init/add/commit/rev-parse` in the disposable `/var/tmp` repo (a synthetic git history cannot be built with read plumbing alone). It never targets `--root`; the audit path itself uses only `cat-file`, `ls-tree`, `show`.

## Risks / open items (bounded)

1. Tip 70af563 is still red (`mismatches=1`) on line 83; C1's M_after=0 is unreachable until that span loses its evidence role. Not my file to edit, and not a defect of the instrument.
2. My skipped accounting is a superset of the landed tool's (+embedded runs). If a reviewer expects `S` to match the landed number, the +12/+9 is the whole explanation and is enumerated line by line above.
3. Class C is not exercised by the real document, only by fixtures (correct and wrong digest). The real-corpus C evidence is therefore fixture-only, not production.
4. Fixture repo construction depends on `git init -b` (git 2.56.0 here) and a writable `/var/tmp`; failure of either aborts selftest with a non-zero exit rather than a false pass.
