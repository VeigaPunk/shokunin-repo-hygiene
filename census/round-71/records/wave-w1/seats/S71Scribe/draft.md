# S71Scribe — draft material for corpus/lessons/round-71.md (L1 owns the lesson)

Read at 52e8c3faf678b0f3d2f18cc6d41a365dc91123f7 (worktree HEAD). Every number below was
re-derived from committed bytes at that rev; lane commit range read: aa91d1ca → a1db6c85 → 52e8c3fa.

## 1. Disposition of the r70 routed list (corpus/lessons/round-70.md:78, items (a)-(i))

| item | r70 text (abbrev.) | r71 status | evidence (committed bytes at 52e8c3fa) |
|---|---|---|---|
| (a) | HIGH F1: `filter` attribute + local `filter.<x>.clean` (GIT_ATTR_SOURCE or committed `.gitattributes`) hides a modified tracked file; writer writes the receipt | **closed** | a1db6c85: `GIT_ATTR_SOURCE` added to the scrub set (tools/souji-receipt-write.py:124), `_filter_drivers`/`_filter_refusal` + `RECEIPT-FILTER-DRIVER-SET` pre- and post-run; `records/c1-after.txt` CASE FC1/FC2/FC3 `expect=refuse base=accept new=refuse new_findings=RECEIPT-FILTER-DRIVER-SET`; `records/writer-selftest.txt:43` `case ok: filter-driver` |
| (b) | MEDIUM F2: repository-local `core.fileMode=false` hides an in-run mode flip | **closed** | every writer git call carries `-c core.fileMode=true`; `records/c1-after.txt` CASE FM1/FM2 `base=accept -> new=refuse`; `records/writer-selftest.txt:44` `case ok: filemode-pin` |
| (c) | MEDIUM F3/F4/F5: battery member names and harness labels unvalidated (`../` escapes `--work`) | **closed** | `census/round-71/c1-counter.py:1262-1287` `MEMBER_RE` on every member name and on every SHA256SUMS line; selftest cases `member name '../M1' is not a plain file name`, `SHA256SUMS line 1 names a non-plain file`, `member M1.py is a symlink` (records/counter-selftest.txt); `census/round-71/c2-harness.py:108-126` `LABEL_RE` + `label escapes --work`; control `c2-CF1` EXIT=2 |
| (d) | MEDIUM X7/X8: counter rc does not bind `base_forgeries`/`base_honest`; no selftest case asserts the ambient pathspec scrub | **partial — second clause closed, first open** | X7/X8 both `fate=killed` (records/c2-after.txt); selftest `clean_env: ambient pathspec variables are scrubbed \| leaked=[]`. But `claim_upheld` (c1-counter.py:1164-1169) binds only `new_forgeries/new_honest/class_mismatches/new_echo/regress/all_new_match`; no frozen expected base constant exists (`grep -nE 'BASE_(FORG\|HONEST)\|base_expect'` → 0), so the base slot can still move silently |
| (e) | regenerate the battery from the r70 writer so its manifest matches the 59-row matrix | **open** | the only battery artefact in the lane is `census/round-70/probes/battery-r69-members-r70-counter.txt`; no file named `*battery*` exists under census/round-71/ (`ls records probes controls \| grep -i battery` → none), and the only `battery` occurrences in r71 records are the X6 mutant description and the selftest case names (records/c2-after.txt:9, counter-selftest.txt:28-34). `records/census-before.txt` is the sources census (`souji ok …/corpus/SOURCES.md`, `EXIT=0`), not a battery |
| (f) | a NOGLOB-observable row or a named limit for it | **open** | `records/c1-after.txt:121` `CASE NGA expect=accept base=accept … new=accept`, `:123` `CASE NGD expect=refuse base=refuse … new=refuse` — both inert in both slots; preregistration.txt "Named limits" names `attr.tree`, `core.attributesFile`, `filter.<d>.process` and in-run driver creation, never NOGLOB |
| (g) | writer case 38 must enumerate the variables independently of `PATHSPEC_ENV` | **open** | `tools/souji-receipt-write.py:1558` still `for var in PATHSPEC_ENV:`; the candidate diff (a1db6c85) adds only `git()`, `_filter_drivers`, `_filter_refusal`, cases 39-40 |
| (h) | r69 D5 (ambient receipt records no tuple), r69 list (d) D06 isolating row, (g) writer `verify` subcommand | **open** | writer diff aa91d1ca→52e8c3fa contains no ambient-tuple write and no `verify` parser (`grep -n 'add_parser("verify")\|"verify"'` → 0 hits) |
| (i) | cross-lane: kaidoku `round-42/prefile-gate.py:311-327`, kumitate `round-gate.mjs:491,562` read the index with caller pathspec vars unscrubbed | **open (documented, out of lane)** | no r71 commit touches a sibling repo; read-only by rule |

## 2. Disposition of the r70 spot-check defects D1-D5 (corpus/lessons/round-70-verifier-spotcheck.md)

| defect | r71 status | evidence |
|---|---|---|
| D1 SCORECARD:181 says `pointer-check-r69.txt (5 missing, EXIT=1)`; receipt says 8 | **open** | `sed -n '181p' SCORECARD.md` still reads `(5 missing, EXIT=1)`; `git show 52e8c3fa:census/round-70/records/pointer-check-r69.txt` → `SUMMARY files=2 checked=59 missing=8 skipped=1 dead_declared=0`, `EXIT=1`; `git diff --stat aa91d1ca 52e8c3fa` touches no SCORECARD.md |
| D2 round-70.md:55 contradicts :75 (S296 `used-by` changed) | **closed at 1c2239cd** (open in the after-arm commit 52e8c3fa that the C1/C2 receipts bind) | `git show 1c2239cd:corpus/lessons/round-70.md \| grep -c 'R70-D2 erratum'` → 1; `git show 52e8c3fa:corpus/lessons/round-70.md \| grep -c …` → 0; `git diff --name-status 52e8c3fa 1c2239cd` → `M corpus/lessons/round-70.md` |
| D3 pointer-check: no SKILL.md registry row, no self-test mode | **open — and this was the declared round milestone ("D3 pointer-check selftest build")** | `grep -n 'pointer-check' SKILL.md` → 0 hits; SKILL.md r71 rows are only :928 (C1) and :929 (C2); `python3 -B tools/souji-pointer-check.py --selftest` → argparse usage error, rc=2 |
| D4 carried F1/F2/F3-F5/X7-X8/NOGLOB | **see table 1** (a)(b)(c) closed, (d) partial, (f) open | as above |
| D5 fleet-root commit by a wave seat (operator-owned) | **open / operator** | no lane file carries an empty-`-C`/toplevel guard; `.ufo/prompts` has no tracked files in this lane (`git ls-files .ufo/prompts` → empty), so the guard lives only in the dispatch prompt |

## 3. Two candidate `## Mistakes` rows (lane format; neither is in round-70.md M1-M7)

| # | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|
| M-a | **one receipt key, three referents**: `rev=` in the c1-counter writer is the candidate writer rev, in the counter's selftest receipt it is the instrument rev, and in the c2-harness receipt it is `--base-rev` — at which revision the instrument it names does not exist, so the header cannot reproduce the run | `records/c1-after.txt:1` (`rev=a1db6c85…`, candidate writer) vs `records/counter-selftest.txt:3` (`rev=aa91d1ca…`, instrument) vs `records/c2-after.txt:1` (`rev=8b9345b1…`, `--base-rev`); `census/round-71/c2-harness.py:211` writes `rev={ns.base_rev}`; `git cat-file -e 8b9345b1:census/round-71/c1-counter.py` → absent (both the counter and the harness first exist at aa91d1ca) | the scribe re-deriving the receipts against committed bytes; no gate resolves a receipt's `rev=` to a path, unlike the pointer check for prose | emit `base-rev=` and `instrument-rev=` as separate keys (or drop `rev=`), and add a selftest case asserting `git cat-file -e <instrument-rev>:<instrument>` before the receipt is written |
| M-b | **routed-list amnesia between rounds**: the freeze carries three of the nine items the previous lesson routed — and the ones it drops are exactly the ones whose absence cannot be seen from the round's own SUMMARY (`matrix=70` counts inert rows as coverage) | `corpus/lessons/round-70.md:78` items (e)(f)(g)(h)(i); `census/round-71/preregistration.txt` "Routed inputs this round acts on" names only (a)-(d); `records/c1-after.txt:121,123` (NGA/NGD identical base and new) against the "matrix=70" headline; `tools/souji-receipt-write.py:1558` (`for var in PATHSPEC_ENV`) as (g) still open | the scribe's routed-item table (no instrument reads the previous lesson's routed list; the pointer check only proves the cited paths exist) | the prereg must carry a disposition row per carried item — `closed by <commit/row>` or `open + one limit sentence` — and the counter must report `inert=<n>` beside `matrix=<n>` so a mechanism-inert row is never counted as coverage |

## 4. Pointer check (task item 4)

Command (run from /home/vgpnk/Projects/shokunin/souji-shokunin):

    python3 -B tools/souji-pointer-check.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
      --rev 52e8c3faf678b0f3d2f18cc6d41a365dc91123f7 \
      census/round-71/preregistration.txt corpus/knowledge/filter-filemode-witness.md

Output:

    SUMMARY files=2 checked=37 missing=0 skipped=1 dead_declared=0
    EXIT=0

No missing pointer. The one skipped token is `census/round-71/controls/c1-*.txt`
(`corpus/knowledge/filter-filemode-witness.md:1`) — skipped because it holds `*`, per the checker
docstring (tools/souji-pointer-check.py:11); it is not a broken pointer. Re-run at the later lane tip
`1c2239cd13c8b1c9a2e0786509940754d58664d5` → identical `SUMMARY files=2 checked=37 missing=0
skipped=1 dead_declared=0`, `EXIT=0` (neither file changed after 52e8c3fa).

## 4b. Post-freeze commit seen after my first read (chronology update)

`1c2239cd` (16:57:11 -0300) adds `census/round-71/probes/attr-filemode-probe-sizechange.txt` and the
round-70 D2 erratum. The probe file is a **re-run** of the probe's first form (`sed`-rewritten from
`census/round-71/probes/attr-filemode-probe.sh`, `s/FORGED/v1/`), not the original overwritten
output — so the prereg's "that output was overwritten" stays true and the evidence is now durable as
a reproduction. Instrument, matrix and receipts are unchanged by it (`git diff --name-status
52e8c3fa 1c2239cd` → 2 files, neither under `census/round-71/records/`).

## 5. Numbers re-derived (for the lesson's Measured section)

- `awk -F'\t' 'NR>1' census/round-71/c1-matrix.tsv | wc -l` → 70; classes 19 accept / 51 refuse; r70
  matrix subset fully carried (`comm -23` over case names → empty); r70 rows 59.
- `grep -c '^CASE ' records/c1-after.txt` → 70. The 7 base forgeries are exactly AS1 AS2 FC1 FC2
  FC3 FM1 FM2 (`expect=refuse base=accept`), each `new=refuse` with its frozen class; matches the F2
  control (5 = FC1..FM2) and the F3 control (5 = AS1 AS2 FC1 FC2 FC3) derivations.
- Instrument shas at 52e8c3fa equal the receipts: counter `7e5a694a…`, matrix `e1a3c00b…`, harness
  `6c7bf41d…`, mutants `3e4945bf…`; candidate writer `56b6be03…` (= `slot new` in c1-after, and
  `git show a1db6c85:tools/souji-receipt-write.py | sha256sum`); base control
  `controls/base-writer-8b9345b1.py` `118597e0…` = prereg line 5.
- Touch surface of the round: `git diff --stat aa91d1ca 52e8c3fa` → 10 files (SKILL.md, 4 records,
  README, SOURCES, 2 knowledge entries, tools/souji-receipt-write.py); no SCORECARD, no LOG, no
  census instrument file after the freeze. The later `1c2239cd` adds one probe file and the round-70
  erratum only.
