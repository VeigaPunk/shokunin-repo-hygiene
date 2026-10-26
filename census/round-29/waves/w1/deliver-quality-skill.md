# deliver-quality-skill.md — Souji r29 w1 SwarmScribe28

Merge-ready text for two files: `corpus/QUALITY.md` criteria Q60–Q62 and three rows of the
`## Gate registry` table in `SKILL.md`. Lane base `691dd29211c53d0ef94fa072394cb9c8a69fe92e`;
preregistration `b8cb4b31ce80e2e3314b88e85d40ea9873180804`. Nothing was written outside this
file; the L1 copies these blocks in.

Column shapes were taken from the files as they stand at `b8cb4b31…`: QUALITY.md's last section
is `## Round 25 criteria` (`:137`, ending at `:143`) with header `| id | criterion | applies to | check | motivating
evidence |` (`:139`), and SKILL.md's gate table columns are `name | kind | entry command |
verdict map (code → class) | self-test command | pinned-value path | write scope | owner`
(last row `souji-pre-report-gate`, SKILL.md:224).

## Insert 1 — `corpus/QUALITY.md`

Append after the Q59 row (end of file, QUALITY.md:143):

```markdown

## Round 29 criteria

| id | criterion | applies to | check | motivating evidence |
|---|---|---|---|---|
| Q60 | A frozen counter's exclusion clause is applied as written, and the lane records that reading — the excluded row ids and the target count the clause leaves — in the same round's lesson's head section (before any `## Receipts`, `## Mistakes`, `## Residuals` or `## Wave` heading) on a line starting `reading:` (a leading `- ` is allowed), before any after-data is produced. Applying an exclusion the preregistration declared before data is not narrowing the counter; narrowing it after data is. Prose agreement does not substitute: a clause with no reading line, or a reading that omits one of the clause's ids or its target, fails. The clause is read from the frozen preregistration text, not paraphrased. | frozen round counters carrying an exclusion clause; the round lesson | `python3 -B -c 'import re,subprocess,sys;R,rev,rd=sys.argv[1:4];g=lambda p:subprocess.run(["git","-C",R,"cat-file","blob",f"{rev}:{p}"],capture_output=True,text=True).stdout;pre=g(f"census/round-{rd}/records/preregistration.txt");les=g(f"corpus/lessons/round-{rd}.md");cl=[(sorted(set(re.findall(r"S\d{3,}",m.group(1)))),(re.findall(r"\d+\u2192(\d+)",line[:m.start()]) or [""])[-1]) for line in pre.splitlines() for m in re.finditer(r"\(([^()]*not counted in this claim[^()]*)\)",line)];head=re.split(r"^## (?:Receipts\|Mistakes\|Residuals\|Wave)\b",les,flags=re.M)[0];rdg=[l for l in head.splitlines() if re.match(r"\s*(?:-\s+)?reading:",l)];bad=[c for c in cl if not any(all(x in l for x in c[0]) and (not c[1] or c[1] in l) for l in rdg)];print(f"Q60 clauses={len(cl)} readings={len(rdg)} unread={len(bad)}");[print("UNREAD"," ".join(c[0]),c[1]) for c in bad];sys.exit(0 if cl and not bad else (2 if not cl else 1))' <lane> <full40> <round-N>` — exit 0 with `unread=0`; exit 1 with one `UNREAD <ids> <target>` line per clause the lesson does not read; exit 2 when the round's preregistration carries no exclusion clause (not applicable). Witness: r28 clause `(the three POSIX rows; S119 row, if appended, is not counted in this claim)` → at 691dd29 `clauses=1 readings=0 unread=1` / `UNREAD S119 138`, rc 1; at the repaired lesson 69b06858 `clauses=1 readings=1 unread=0`, rc 0. r29 itself: `clauses=0`, rc 2. | corpus/lessons/round-29.md `## Mistakes` (r28 C2: a frozen counter's exclusion clause misread by its author); corpus/lessons/round-28-verifier-spotcheck.md:49 and :124; census/round-28/records/preregistration.txt; `.ufo/waves/round-29/w1/deliver-q60-q62-red-before.tsv` q60 arm |
| Q61 | A receipt or manifest counter reads the committed bytes at the landed revision, never the lane's working tree; and the capture that produces the receipt accounts for every path it did not copy — nested ignore rules, ignored names and symlinks — in committed bookkeeping files the counter can check (`renames.tsv`, `excluded.tsv`, `symlinks.tsv`). A receipt that verifies only against the disk copy is a record defect, not a measurement; a committed regular file or symlink under the receipt with no manifest record is uncovered, not clean. Scope is the declared `census/round-N/waves/` receipt at a named revision; a receipt that never lands cannot be verified. | round wave-evidence receipts, capture tools, manifest counters | `python3 -B census/round-29/c2-counter.py --root <lane> --rev <full40>` exits 0 only on `SUMMARY manifests=<m> failed=0 uncovered=0 floor_violations=0` with `m` ≥ 1; exit 1 on any failed or uncovered record, any floor violation, and also on could-not-evaluate — the counter defines no code 2 (`--rev deadbeef` prints `COULD-NOT-EVALUATE rev must be a full 40-hex revision`, rc 1). Floors: r26 ≥ 1230, r27 ≥ 124, r28 ≥ 75 records. Failure witness at b8cb4b31: `manifests=3 failed=152 uncovered=14 floor_violations=0`, rc 1. Discriminating arms: deleting the two GNU-escaped r26 records → `uncovered=16`; zeroing one r27 record hash → `failed=153` (`.ufo/waves/round-29/w1/deliver-c2-history.tsv`). | corpus/lessons/round-29.md `## Mistakes` (r28 C3: a receipt verified over the lane's disk); corpus/lessons/round-28-verifier-spotcheck.md:63-80 (152 records absent from git; r26 symlinks carry no record); census/round-29/records/preregistration.txt C2 |
| Q62 | A used-by/source citation is bidirectional: every `corpus/SOURCES.md` row's `used-by` path must exist at the revision and name that row id, and every S-id an entry's front-matter `source:` lines cite must be a row that lists that entry in `used-by`. One direction is not evidence of the other — a row may not name an entry that never cites it, and an entry may not cite a row that does not name it. Corrections to a stale statement are append-only: the phrase stays and an `R29-CORRECTION <file:line>` line naming it is added after it. | corpus/SOURCES.md rows; corpus/knowledge entries' `source:` lines; stale-statement records | `python3 -B tools/souji-registry-agreement.py --root <lane> --rev <full40>` exits 0 with `SUMMARY k1=0 k2=0 mismatches=0`; exit 1 prints one line per disagreement (`K1 used-by-missing`, `used-by-no-cite`, `cited-not-in-used-by`, `cited-no-row`, `K2 file-missing`, `phrase-moved-or-edited`, `uncorrected`); exit 2 is could-not-evaluate (non-40-hex or unresolvable rev, unreadable stale list, list line that is not 3 TSV fields). Add `--list-rev <prereg-commit>` when REV predates `census/round-29/stale-statements.tsv`: at 691dd29 the bare command exits 2 (`COULD-NOT-EVALUATE stale list … unreadable`), with `--list-rev b8cb4b31…` it prints `k1=6 k2=4 mismatches=10`, rc 1. Witness line: `K1 used-by-no-cite S215 corpus/knowledge/git-auto-maintenance-trigger-set.md`. | corpus/lessons/round-29.md `## Mistakes`; corpus/lessons/round-28-verifier-spotcheck.md:60-61 (S215 used-by names an entry that never cites it) and routed defect :123 |
```

## Insert 2 — `SKILL.md` gate-registry rows

Append after the `souji-pre-report-gate` row (SKILL.md:224, immediately before
`Sources for this skill:`):

```markdown
| souji-registry-agreement | gate | `python3 -B tools/souji-registry-agreement.py --root LANE --rev REV [--list-rev REV] [--stale-list PATH]` | 0 `mismatches=0`; 1 `mismatches>0`, one line per K1/K2 disagreement; 2 could-not-evaluate (usage, non-40-hex or unresolvable rev, unreadable stale list, list line not 3 TSV fields). Reads `git cat-file`/`-e` only: the working tree is never consulted | `python3 -B tests/fixtures/r29-registry-agreement.py --tool tools/souji-registry-agreement.py` → `cases=12 pass=12 control=FALSE-GREEN-REJECTED`, rc 0; red arm: the same fixture against a copy with the entry→row reverse check deleted → `cases=12 pass=9`, rc 1 | fixture's literal 12-case table; `census/round-29/stale-statements.tsv` (4 frozen statements); base witness `mismatches=10` in `census/round-29/records/preregistration.txt` | committed bytes only, never writes; fixture scratch under `/var/tmp/souji-r29-C1Fixture` | souji |
| souji-wave-evidence-capture v2 (committed-bytes) | probe | `bash tools/souji-wave-evidence-capture.sh <lane-abs> <round-N> [--verify [--rev <full40>]]` | 0 captured+verified, or `verified:` / `verify-rev … failed=0 uncovered=0`; 1 usage error, `--rev` without `--verify`, non-40-hex or unknown revision; 2 source directory missing; 3 refusal (special file, path escape, nested src-dst, stored-name collision); 4 verification failed (manifest mismatch, missing or uncovered record, receipt/source set mismatch, lane not a git repository under `--verify --rev`); 5 copy/receipt write failure. A verify verdict is data; the gate is `r29-c2-counter` | `bash tests/fixtures/r28-wave-evidence-capture.sh` → `cases=12 pass=12 control=TAMPER-REJECTED`, rc 0 against these tool bytes; red arm `SOUJI_CAPTURE_TOOL=tools/souji-wave-evidence-capture.sh` at base 691dd29 → `cases=12 pass=6 control=TAMPER-REJECTED`, rc 1 (cases 7–12 are the committed-bytes layout) | fixture's 12 literal cases (1–6 preserved from the r28 six-case file); limits from the C2 fixture: symlinks.tsv column 1 is the bare path relative to `census/round-N/waves` | writes only `<lane>/census/round-N/waves/`; `--verify` read-only (git plumbing, no mutation); never network; fixture scratch under `/var/tmp/souji-r29-C2FixtureV2` | souji |
| r29-c2-counter | gate | `python3 -B census/round-29/c2-counter.py --root LANE --rev REV` | 0 `SUMMARY manifests=<m> failed=0 uncovered=0 floor_violations=0` with m ≥ 1; 1 any failed/uncovered record or floor violation, and also could-not-evaluate — no code 2 exists (bad revision or git failure prints `COULD-NOT-EVALUATE …` and exits 1) | red arm reproducible from committed history: at `691dd29211c53d0ef94fa072394cb9c8a69fe92e` → `manifests=3 failed=152 uncovered=14 floor_violations=0`, rc 1; green arm: the round's landing tip must print `failed=0 uncovered=0`, rc 0. Discriminating scratch arms in `.ufo/waves/round-29/w1/deliver-c2-history.tsv`: dropped escaped records → `uncovered=16`; zeroed hash → `failed=153` | embedded `FLOORS` (r26 1230, r27 124, r28 75) frozen by `census/round-29/records/preregistration.txt` C2 | `git ls-tree`/`cat-file` only, never the working tree, never writes | souji |
```

## Provenance and what was measured

- **Q60 checker** is the executor's literal from
  `.ufo/waves/round-29/w1/deliver-q60-q62-red-before.tsv` line 8 (`QCriteriaRedBefore`, repair
  branch `69b06858c4f327e443cf03167be01abef6fc78fa`), reproduced here with only the escaped table
  pipes. This scribe re-ran the base arm against the lane: `691dd29… 28` →
  `Q60 clauses=1 readings=0 unread=1` / `UNREAD S119 138`, rc 1 (matches the recorded
  `base_result`); `b8cb4b3… 29` → `clauses=0 readings=0 unread=0`, rc 2. The repaired arm
  (`clauses=1 readings=1 unread=0`, rc 0 at 69b06858) is the executor's record, not re-run here.
- **Q61 command** was run by this scribe at `b8cb4b31…` →
  `r26 records=1382 failed=152 uncovered=14 floor_violation=0`, `r27 records=124 failed=0`,
  `r28 records=75 failed=0`, `SUMMARY manifests=3 failed=152 uncovered=14 floor_violations=0`,
  rc 1; `--rev deadbeef` → `COULD-NOT-EVALUATE rev must be a full 40-hex revision`, rc 1 (no code
  2). The 152/14 figures match `census/round-29/records/preregistration.txt` C2.
- **Q62 command** was run by this scribe: bare form at `b8cb4b31…` → `k1=6 k2=4 mismatches=10`,
  rc 1; at `691dd29…` the bare form exits 2 (`stale list … unreadable`) and with
  `--list-rev b8cb4b31…` → `k1=6 k2=4 mismatches=10`, rc 1. The `--list-rev` caveat in the cell
  exists because of that measurement.
- **Capture fixture row**: run by this scribe with
  `SOUJI_R29_C2FIXTURE_BASE=/var/tmp/souji-r29-SwarmScribe28/c2fix` against
  `deliver-souji-wave-evidence-capture.sh` (sha256 `3db37453e0fd…`, md5
  `d00c545fcd2be2aecf93319e1f4a7c7f`) → `cases=12 pass=12 control=TAMPER-REJECTED`, exit 0; red
  arm with `SOUJI_CAPTURE_TOOL=tools/souji-wave-evidence-capture.sh` (the committed base v1) →
  `cases=12 pass=6 control=TAMPER-REJECTED`, exit 1. Both runs used this seat's scratch root; the
  fixture's trap removed each run directory.
- **Registry fixture row**: `cases=12 pass=12 control=FALSE-GREEN-REJECTED` / red
  `pass=9` are `SwarmExecutor01`'s recorded runs of the delivered fixture (sha256
  `eea7388922b1…`), not re-run here — its scratch root is hard-coded to
  `/var/tmp/souji-r29-C1Fixture`, outside this seat's allowed scratch namespace.

## Integration notes for the L1

1. Landing paths: the capture fixture's own header and `SwarmExecutor04` name
   `tests/fixtures/r28-wave-evidence-capture.sh` (v2 replaces the six-case file in place); the
   registry fixture's planned path is `tests/fixtures/r29-registry-agreement.py`
   (`SwarmExecutor12` baseline note). The gate rows above use those two paths.
2. `corpus/lessons/round-29.md` does not exist at `b8cb4b31…` (it lands with the round), so all
   three rows' pointers resolve only at the landing revision — a Q31 check must run after the
   lesson lands, not at the prereg commit.
3. Q60 is **not applicable to r29**: the r29 preregistration has no `not counted in this claim`
   clause (`clauses=0`, rc 2). The criterion is admitted for the class, with the r28 witness.
4. The capture row is a `probe` because a verify verdict is data about one receipt; the gate over
   receipts is `r29-c2-counter`. Do not promote the capture row to `gate` without a self-test
   whose failure is a certification failure.
