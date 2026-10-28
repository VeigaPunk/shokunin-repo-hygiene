# W1ExecSources — SOURCES census at both ends of round 39

Seat: executor (leaf). Scope: run the fleet SOURCES census (`scripts/sources-census.sh validate`)
against the souji-shokunin registry before and after the round-39 wave, report row count, W04 count
and exit code, and compare with the round-38 spot-check's closing reading.

Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`
- lane base (prereg): `ed30b7f5b77939c9073348d810730bc4f355708d`
- lane HEAD while measuring: `c0b007b42af9a03d7edc32533bcac27484223997`
  (`round-39: C1 — 14 routed-defect corrections, r39 lesson with Gate/Mistakes, three source rows, gate-registry rows`);
  re-confirmed unchanged at `094e531` (see §8 final run) — the registry was not touched by the
  three commits that landed in between.
- working tree at measure time: `corpus/SOURCES.md` clean (`git status --porcelain -- corpus/SOURCES.md`
  printed nothing), so the readings below are the committed bytes at `c0b007b`.
- Scratch: `/fast/scratch/hyaku/souji-r39/W1ExecSources` (removed at seat exit; see §7).
- No tool installs or upgrades were needed; nothing was installed.

Assignment literal used throughout:
`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji`

---

## 1. Census at the wave head (now)

Command:

```
bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji; echo "EXIT=$?"
```

Output (48 lines: 47 `W04` + 1 `ok`), first and last lines quoted verbatim plus the terminator:

```
souji	W04	S035 duplicate url git-scm.com/docs/git-repo across scopes
souji	W04	S036 duplicate url git-scm.com/docs/git across scopes
souji	W04	S038 duplicate url www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html across scopes
...
souji	W04	S244 duplicate url git-scm.com/docs/git-merge-base across scopes
souji	W04	S245 duplicate url man7.org/linux/man-pages/man2/open.2.html across scopes
souji	W04	S246 duplicate url man7.org/linux/man-pages/man7/pipe.7.html across scopes
souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
EXIT=0
```

Class histogram (`awk -F'\t' '{print $2}' … | sort | uniq -c`):

```
      1 ok
     47 W04
```

**Verdict S1: PASS.** `validate` exits 0, the lane is `ok` (no E-codes: no E01/E02/E03/E04/E05–E12
findings), and the 47 W04 warnings are the warning class the script documents as not affecting a
clean lane.

## 2. Registry row count

The assignment's grep was run literally, then re-run with a corrected repetition operator, then
cross-checked against the census tool's own `rows` metric (the authoritative parser).

```
grep -cE '^\|[[:space:]]*S[0-9](3,)[[:space:]]*\|' corpus/SOURCES.md
0                      # rc=1
grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md
173
bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --root /home/vgpnk/Projects/shokunin souji
souji	rows	173
souji	tier.A	164
souji	tier.B	6
souji	tier.C	3
souji	status.mined	143
souji	status.queued	14
souji	status.rejected	16
FLEET	rows	173
...
FLEET	missing	0
EXIT=0
```

**Advisory (defect in the assignment text, not in the lane):** `S[0-9](3,)` is ERE group syntax
("`S`, one digit, then the literal run `3,`"), not a repetition — it can never match a registry row
and returns `0` with rc 1. The intended pattern is `S[0-9]{3,}`, which agrees with the tool
(`173`). Any report quoting the literal pattern's `0` would be wrong.

**Verdict S2: PASS** — registry row count is **173** (`grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'`
= 173 = `census … rows` 173 = 164 A + 6 B + 3 C; `FLEET.rows` 173, `FLEET.missing` 0).

## 3. Base-revision control (registry state at `ed30b7f`)

Read-only blob extraction plus a reconstructed lane root, so E11 (`-e "$dir/$path"`) resolves
faithfully:

```
S=/fast/scratch/hyaku/souji-r39/W1ExecSources
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show ed30b7f5b77939c9073348d810730bc4f355708d:corpus/SOURCES.md > "$S/base-SOURCES.md"
wc -l "$S/base-SOURCES.md"                     -> 279
grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' "$S/base-SOURCES.md"  -> 170
# reconstructed root: $S/baseroot/corpus/SOURCES.md = base blob, corpus/{lessons,knowledge} +
# every other lane top-level entry symlinked from the lane, nothing else
bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root "$S/baseroot" --file "$S/baseroot/corpus/SOURCES.md"
file	ok	/fast/scratch/hyaku/souji-r39/W1ExecSources/baseroot/corpus/SOURCES.md
EXIT=0   (48 lines, 47 W04)
bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --root "$S/baseroot" --file "$S/baseroot/corpus/SOURCES.md"
file	rows	170
file	tier.A	161
file	tier.B	6
file	tier.C	3
file	status.mined	140
file	status.queued	14
file	status.rejected	16
EXIT=0
```

Method note (so no one reads it as a base defect): a first attempt passed `--file` a copy sitting
in a bare scratch directory; the script derives the lane dir as `dirname(file)/..`
(`scripts/sources-census.sh:500-502`), so E11 resolved the relative used-by paths inside scratch and
printed five spurious `E11 … missing used-by` lines (exit 1). With the reconstructed root those
disappear (`file ok`, exit 0). The base registry itself is E-clean and W-clean apart from W04.

**Verdict S3: PASS** — base state: 170 rows (161 A / 6 B / 3 C; 140 mined / 14 queued / 16 rejected),
47 W04, exit 0.

## 4. Delta against the round-38 spot-check closing reading

Assignment's comparison target: `162 -> 170` rows, 47 W04. Source of that reading in the lane:

```
.ufo/waves/round-38/w2/W2CritFrontier.md:342:  tip       fcdecaa  170 rows  rc 0  W04 47  (real root, 48 lines)
.ufo/waves/round-38/w2/W2CritFrontier.md:136:  rows 162 → 170 | tier.A 153 → 161 (+8) | tier.B 6 → 6 | tier.C 3 → 3
```

Re-verified that revision directly (read-only):

```
git -C … rev-parse fcdecaa                     -> fcdecaaf293f0fee3c39cc148ae91389e04ef63c
git -C … show fcdecaa:corpus/SOURCES.md | grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'  -> 170
git -C … merge-base --is-ancestor fcdecaa HEAD -> fcdecaa is ancestor of HEAD
```

Row-level delta base → HEAD (whole registry diff is 5 added lines in `corpus/SOURCES.md`):

```
git -C … diff ed30b7f..HEAD --stat -- corpus/SOURCES.md
 corpus/SOURCES.md | 5 +++++
+Round-39 provenance: new S247-S249 were opened live on 2026-10-28 for the C2 revision-resolution claim and its two disc…
+| S247 | gitrevisions(7) § SPECIFYING REVISIONS `<rev>^{<type>}` — https://git-scm.com/docs/gitrevisions | … | mined | 2026-10-28 | 365d | corpus/lessons/round-39.md |
+| S248 | Python docs, ast.get_docstring — https://docs.python.org/3/library/ast.html#ast.get_docstring | … | mined | … | corpus/lessons/round-39.md |
+| S249 | Python docs, argparse exit status — https://docs.python.org/3/library/argparse.html#exit-on-error | … | mined | … | corpus/lessons/round-39.md |
no removed rows
```

Distribution delta base → HEAD: rows 170 → 173, tier.A 161 → 164, tier.B 6 → 6, tier.C 3 → 3,
mined 140 → 143, queued 14 → 14, rejected 16 → 16.

W04 set identity (ids only, base vs HEAD):

```
grep W04 <base-validate> | … | sort > w04-base.ids ; wc -l -> 47
grep W04 <head-validate> | … | sort > w04-head.ids ; wc -l -> 47
diff … -> (no output)  W04 SET IDENTICAL
head W04: souji	W04	S035 duplicate url git-scm.com/docs/git-repo across scopes
tail W04: souji	W04	S246 duplicate url man7.org/linux/man-pages/man7/pipe.7.html across scopes
```

**Verdict S4: the lane's registry is NOT unchanged since the round-38 spot-check.** Three rows were
added at the r39 base→HEAD step: **S247, S248, S249** (all tier A, status `mined`, opened
2026-10-28, `365d` recheck, used-by `corpus/lessons/round-39.md`, with a one-line provenance note
above them). Row count moved **170 → 173**; the W04 warning count did **not** move (**47 → 47**) and
the W04 id set is byte-identical, so no new duplicate-URL warning was introduced by the new rows.
Exit code is 0 at both ends.

Consequence for round-39 prose: `170` is the correct *base-of-round* reading but is stale as a
*round-39 closing* reading; a round-39 report, SCORECARD row or lesson that states 170 (or that the
registry was untouched this round) is contradicted by `c0b007b`. `162 → 170` remains accurate only
for round 38.

## 5. Second reading (post-wave re-run)

Same command re-run at the end of the seat's work, after the peers' in-flight changes:

```
bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji
# 48 lines, 47 W04, "souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md"
EXIT=0
grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md -> 173
```

Identical to §1/§2: **173 rows, 47 W04, exit 0**. No further rows appeared between the two readings;
the only uncommitted lane changes at that moment were `M corpus/lessons/round-39.md` and four new
`census/round-39/records/*.txt` receipts from other seats, none of which touch `corpus/SOURCES.md`.

**Verdict S5: PASS** — reading is stable across the wave window; the +3 delta (§4) is entirely
inside committed bytes (`c0b007b`).

## 6. Integrity checks on the three new rows

```
# no duplicate URL+scope (E04), no duplicate id (E03), id shape (E02), enum (E05-E07), community tier (E10):
validate exit 0 with only W04 -> none of E01-E12 fired at HEAD
# no new duplicate-URL warning:
diff of W04 ids base vs head -> empty (47 both)
# used-by paths exist (E11):
ls corpus/lessons/round-39.md -> -rw-r--r-- 1 vgpnk vgpnk 10616 Oct 28 14:55 corpus/lessons/round-39.md
# URL uniqueness for the new rows (Registry-table full-URL occurrences):
grep -oE 'git-scm.com/docs/gitrevisions[^|]*\|' corpus/SOURCES.md | sort | uniq -c  -> 1
# raw string hits, checked line by line so no double count is implied:
grep -nF 'ast.get_docstring' corpus/SOURCES.md        -> :20 (provenance note) and :197 (the S248 row)
grep -nF 'gitrevisions'      corpus/SOURCES.md        -> :20 (provenance note), :188 (S239 prose, URL is git-merge-base), :196 (the S247 row)
grep -cF 'argparse.html#exit-on-error' corpus/SOURCES.md -> 1
```

**Verdict S6: PASS** — the three new rows are well-formed and warning-neutral; the E11 used-by
target (`corpus/lessons/round-39.md`) exists at HEAD (it did not exist at `ed30b7f`, which is
consistent: no base row referenced it).

## 7. Scratch / environment hygiene

- Scratch root used: `/fast/scratch/hyaku/souji-r39/W1ExecSources` (`base-SOURCES.md`,
  `baseroot/` symlink tree, `*-validate*.txt`, `w04-*.ids`). Removed at seat exit.
- `/tmp` used for nothing. No git/jj mutation of any kind was run: only `show`, `diff`, `diff
  --stat`, `rev-parse`, `merge-base --is-ancestor`, `cat-file -e`, `status --porcelain`, `log`.
- Writes: this report only, inside `.ufo/waves/round-39/w1/`. The fleet repo, other lanes,
  `census/round-39/preregistration.txt`, `census/round-39/*-items.tsv`, the `*.json` specs and
  frozen receipts were not touched.
- No tool installed or upgraded (none needed).

## 8. Summary of verdicts

| # | Check | Observed | Verdict |
|---|-------|----------|---------|
| S1 | `validate --root <fleet> souji` at head | 48 lines, 47 `W04`, `souji ok`, EXIT=0 | PASS |
| S2 | registry row count | `173` (`{3,}` grep = 173 = tool `rows` 173; 164 A / 6 B / 3 C) | PASS |
| S2a | assignment's literal grep `S[0-9](3,)` | `0`, rc 1 (malformed pattern, not a lane fact) | advisory |
| S2b | base control at `ed30b7f` | 170 rows, 47 W04, `file ok`, EXIT=0 | PASS |
| S4 | compared with r38 closing (`fcdecaa`: 170 / 47 / rc 0, `W2CritFrontier.md:342`) | **changed**: 170 → 173 (+S247-S249); W04 47 → 47, id set identical; rc 0 → 0 | registry NOT unchanged |
| S5 | post-wave re-run | 173 / 47 / EXIT=0, identical | PASS |
| S6 | integrity of S247-S249 | no E-codes, no new W04, used-by file exists | PASS |

Final confirmation run at seat exit, after the lane advanced `c0b007b → 094e531` (three more commits:
`50972f0`, `094e531`, `790d16b`):

```
git -C … log --oneline c0b007b..HEAD
790d16b round-39: C2 — drop unreachable EISDIR from the RECORD-MISSING line (wave-1 W1ExecC2Docstring)
094e531 round-39: C1 — R7 line names the reaped path as $HYAKU_SCRATCH, not a literal scratch root
50972f0 round-39: C1 — single-line anchor bullets for R5/R7/R15 closures
git -C … diff --stat c0b007b..094e531 -- corpus/SOURCES.md   -> (no output: registry untouched)
bash …/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji ; echo $?
FINAL_EXIT=0        (47 W04)
grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md -> 173
```

So the registry reading is invariant over `c0b007b` → `094e531`: 173 rows, 47 W04, exit 0.

**Bottom line:** the souji registry is **clean and warning-stable** (exit 0, 47 W04) but **not
unchanged** since the round-38 spot-check: S247, S248, S249 were added (170 → 173 rows, tier A
161 → 164, mined 140 → 143). Any round-39 claim that quotes 170 as a closing number, or that the
round's source registry was untouched, must be corrected before the L1 integrates.

**Risks / blockers:** none for this item. Residual: the census was taken at `c0b007b`; if the L1
lands further `corpus/SOURCES.md` bytes after this seat, the reading needs one more run (the command
in §1). The assignment's row-count grep is malformed and should be fixed at source so the next seat
does not report `0`.
