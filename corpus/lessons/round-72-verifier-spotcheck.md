# Round 72 — verifier spot-check

author: hyaku closure (non-author integrator, @m_zfl)

Dispatched 2026-11-06T17:28:30-03:00, completed 2026-11-06T18:50:34-03:00 (`launch souji round=72 pgid=155257 driver=hyaku-inline attempt=1` / `complete souji round=72; hyaku-inline attempt=1`, `.ufo/watchdog.log`; digest copied because the log is mutable). Lane base `0bf098dde7e6eafb62a9ce62b7c16a6291ee1e8e`, lane tip `39e6656bd2869d1a76aee794e02bd0c2c02e68f9`. The closure did not author any round byte; it ran no lane gate or counter (PROTOCOL §Gate standard, Closure consequence).

## Conformance

| check | command | result |
|---|---|---|
| report landed by lane identity | `git -C /home/vgpnk/Projects/shokunin log --format='%an <%ae> %H %ci' -- .ufo/reports/round-72/souji.md` | `souji-shokunin <souji@shokunin.local>` `a5190f62caadb673cccb55942858299ccc7c03eb`, 18:49:30 -0300. After the last lane commit (18:48:09) and before the `complete` line (18:50:34) |
| `SHONEN` heading, one line per box | read report §SHONEN | 4 `[~]` lines, each with a pointer; no `[x]` |
| cited lane commits exist and are ancestors of the branch ref | `git cat-file -e <c>` and `git merge-base --is-ancestor <c> master` for `0bf098dd`, `23372f36`, `06df4f97`, `2ec8b63d`, `0395202f`, `39e6656b` | all 6 `anc-ok`; `0bf098dd..master` is exactly the 5 round commits, all authored and committed by `souji-shokunin <souji@shokunin.local>` |
| no uncommitted round work | `git -C <lane> status --porcelain` | empty |
| pushed | `scripts/hyaku/jj-lane.sh state <lane>` | `branch=master local=39e6656b… remote=39e6656b… ahead=0 behind=0 head=detached tracked=0 untracked=0`; `git ls-remote origin refs/heads/master` → `39e6656bd2869d1a76aee794e02bd0c2c02e68f9` |
| prompt carries the template contract | `diff <(sed -n 1,140p .ufo/prompts/souji-round-72.md) <(sed -n 1,140p kimi-shokunin/templates/round-prompt.md)` | 22 differing lines, all `{{LANE}}`/`{{ROUND}}`/`{{FLEET_ROOT}}`/`{{AXES}}` substitutions; §1–§5 present, hyaku addendum §6 follows. Prompt committed `b20cecd7` 17:28:28, 2 s before the launch line |
| freeze precedes candidate | `git cat-file -e 23372f36:census/round-72/c1-counter.py` (and `c1-matrix.tsv`) | both rc=128 (absent at freeze); r71 routed D1 answered |
| frozen inputs unchanged after the freeze | `git diff --stat 23372f36 39e6656b -- census/round-72/{preregistration.txt,c1-mutants.json,battery,battery-manifest.tsv,controls,probes} census/round-71/c2-harness.py` | empty diff |
| writer bytes unchanged | `git show <rev>:tools/souji-receipt-write.py \| sha256sum` | `0bf098dd` and `39e6656b` → `b7790001…244d`; reference-weak `8b9345b1` → `118597e0…e71f`. Both equal the `# slot base=`/`# slot new=` shas in `c1-Y6-main-arm.txt` and `c2-honest-writer.txt` |
| instrument shas bind receipts to committed bytes | `sha256sum` of committed files vs receipt headers | harness `6c7bf41d…75fb` = `c1-after.txt instrument_sha256`; counter `7578447d…a912` = `counter_sha256` in `c1-after.txt` and `instrument_sha256` in `c2-after-battery.txt`, `c2-honest-writer.txt`, `counter-selftest.txt`; matrix `cd8490b4…3b8` = every receipt's `matrix sha256`; mutants `cfc40608…a754` = prereg and receipt |
| pointer check | `git show 39e6656b:census/round-72/records/pointer-check-r72.txt` | `SUMMARY files=3 checked=75 missing=0 skipped=5 dead_declared=0`, `EXIT=0` |

Conformance defect (status-neutral): S72Reviewer did not write its seat report file; its final output is mirrored as `seats/S72Reviewer-final-output.txt` (disclosed in the report).

## Claim re-checks

**C1 — calibration (lowest owned axis, 7): the counter's selftest kills the six r71 seat survivors and its verdict binds the base slot.** VERIFIED: re-measured over committed receipts and bytes; gate evidence verified, not executed.

- `grep -E '^(SUMMARY|EXIT=)' census/round-72/records/c1-after.txt` at `39e6656b` → `SUMMARY label=c1-after-r72 positive_selftest=PASS x_mutants=11 x_killed=11 x_survived=0 cm_mutants=4 cm_killed=4 cm_survived=0 score=0`, `EXIT=0`. Byte-equal to frozen predicate (i).
- Per-mutant fates (`grep '^MUTANT'`): X6 X7 X8 X9 X10 Y1 Y4 Y6 Y9 Y10 Z1 CM1–CM4 all `fate=killed`.
- Before, `controls/c1-before-r71.txt` → `x_killed=5 x_survived=6 … score=6`, `EXIT=1`; CF1 control → `positive_selftest=FAIL`, `EXIT=2`. As reported.
- `grep -E '^(SUMMARY|EXIT=)' census/round-72/records/c1-Y6-main-arm.txt` → `SUMMARY matrix=75 base_forgeries=2 base_honest=19 base_mismatches=10 … regress=PASS`, `EXIT=1`. Predicate (ii): `base_mismatches=10` > 0 and EXIT=1. Before, `controls/c1-Y6-main-arm-r71.txt` → `matrix=70 base_forgeries=2 …` with no `base_mismatches` field, `EXIT=0`.
- Y6 variant: `diff c1-counter.py records/variants/r72-Y6-counter.py` → one line, 237: `FORGED_SAMESIZE = b"counter v2\n"` → `b"counter FORGED\n"`, exactly the `c1-mutants.json` Y6 edit.
- Mutant provenance (closure python over committed bytes): every one of the 11 `old` strings occurs once in `census/round-71/c1-counter.py`; Y1 Y4 Y6 Y9 Y10 Z1 applied to it are byte-identical to their cited r71 seat files (6/6). X6–X10 cite r70 seat files that edit the r70 counter; carried as regression, as the prereg says.
- Gate evidence: `records/counter-selftest.txt` → `SELFTEST cases=44 pass=44 fail=0`, `EXIT=0`, instrument `7578447d…a912`; SKILL.md registry rows added (`git diff 0bf098dd 39e6656b -- SKILL.md`, +2 lines).
- Qualifications accepted as disclosed, not passes: the harness kills on any selftest failure (a generic digest check would also score 0); narrowing `WITNESS_ROWS` keeps the selftest green; neighbouring clean_env defects pass 44/44; predicate (ii) is one-sided. They narrow C1 to this mutant set; they do not falsify it.

**C2 — coverage (8): five writer filter-witness protections become forging matrix rows (sourced S312–S314).** VERIFIED: re-measured over committed receipts and bytes; one mechanism reproduced by the closure.

- `grep -E '^(BATTERY|EXIT=)' census/round-72/records/c2-after-battery.txt` → `BATTERY mutants=5 kills=5 label_only=0 over_refusal=0 echo_violation=0 survived=0 error=0 all_match=true`, `EXIT=0`. Byte-equal to predicate (i). Each of WM3 WM4 WM5 WM6 WM8 prints `outcome=forgery expected=forgery`.
- Before, `controls/c2-before-r71-battery.txt` → `kills=0 … survived=5 … all_match=false`, `EXIT=1`.
- `grep -E '^(SUMMARY|EXIT=)' census/round-72/records/c2-honest-writer.txt` → `new_forgeries=0 new_honest=19 class_mismatches=0 new_echo=0 errors=0 regress=PASS`, `EXIT=0`. Accept-row count `awk -F'\t' 'NR>1 && $2=="accept"' c1-matrix.tsv | wc -l` → 19, so `new_honest` equals it as predicate (ii) requires.
- Matrix: `grep -vc '^#' census/round-72/c1-matrix.tsv` → 76 (header + 75 rows); r71 matrix → 71 (header + 70). The 5 new rows are FWr FWi FWp FWw FWs, each `refuse RECEIPT-FILTER-DRIVER-SET`, `base_expect accept`.
- Qualifications accepted as disclosed: nothing checks that a refuse row's fixture actually forges (S72MutCounter MF); the matrix is closed only causally (S72Connector). They do not falsify C2.
- Mechanism (closure, fresh repo in `/dev/shm`, git 2.56.0, removed): committed empty `.gitattributes`, worktree copy `f filter=set` → `git check-attr filter f` → `filter: set`; `git check-attr --cached filter f` → `filter: unspecified`. This is the FWw/WM8 route. The driver value also prints as `set`, the same spelling `check-attr` uses for a boolean-set attribute, which is why WM6's boolean exemption is forgeable (FWs).

**Operability (8):** no claim. `git diff 0bf098dd 39e6656b -- SCORECARD.md` is additive only (two capability rows, an r72 bullet, a measurement table); no axis score line changed; `git diff --stat 0bf098dd 39e6656b -- tools` empty.

## Per-axis verdicts

| axis | verdict | basis |
|---|---|---|
| calibration | improved | C1 re-measured: `x_killed` 5 → 11 of 11, score 6 → 0; Y6 main arm EXIT 0 → 1 with `base_mismatches=10` |
| coverage | improved | C2 re-measured: battery kills 0 → 5 of 5, honest writer EXIT=0 with `new_honest=19` of 19 |
| operability | unchanged | no claim; no writer byte, no score line changed |

No owned axis harmed.

## Discernment spot-check

| item | gate decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S312 git-check-attr(1) `--cached` | admit (A, mined) | `curl -sL https://git-scm.com/docs/git-check-attr` → 200, 34571 bytes; committed capture sha256 `6fe0df4e…348d` | agree | Quote "Consider .gitattributes in the index only, ignoring the working tree." (10 words) is in the live page (tag-stripped) and at offset 2608 of the committed `.txt`. Scope (the option only) matches the text, and the closure's fresh-repo run shows `--cached` blind to a worktree-only attribute |
| S314 gitattributes(5) index fall-back | admit (A, mined), teaches narrowed in-round | `curl -sL https://git-scm.com/docs/gitattributes` → 200; capture sha256 `0a1e8015…6aee` | agree | Quote (20 words) present live and at offset 5164. The next sentence reads "During checkout process, .gitattributes in the index is used and then the file in the working tree is used as a fall-back", so the narrowed teaches cell ("outside checkout") is correct and the original was an over-reach |
| `Documentation/technical/long-running-process-protocol.adoc` (v2.56.0) | considered, not appended | `curl -sL https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/technical/long-running-process-protocol.adoc` → 200, 51 lines | agree | It covers the handshake, version negotiation and capability lists (lines 9–38). No r72 row rests on the protocol; FWp needs only that `process` replaces `clean`, which S313 grounds |
| git `read-cache.c` v2.56.0 lines 344–348 / 486–489 | considered, not appended (cited in knowledge as seat-located code) | `curl -sL https://raw.githubusercontent.com/git/git/v2.56.0/read-cache.c` | agree | The lines are the racily-smudged size-0 re-check (`if (!ce->ce_stat_data.sd_size) … DATA_CHANGED`) and the `sd_size != 0` gate before `ce_modified_check_fs`. They are implementation, not documentation; keeping them out of SOURCES and citing them as located lines is the right tier call |

New-row quote check: S313 quote "a long running process filter is used in place of clean and/or smudge filters, then Git can process all blobs" — 20 words (≤25), present in the live page and at offset 16953 of the committed capture (the re-anchored offset). Agree with the re-anchor: the first anchor did not carry "in place of clean".

Census: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` → `souji ok …/corpus/SOURCES.md`, EXIT=0; W04 duplicate-URL warnings only (S312–S314 included, expected: same pages, different scopes). Row count `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` → 234 at `0bf098dd`, 237 at `39e6656b`.

## Trend verdicts

- **expansion: improved.** Three mined tier-A rows (S312–S314) on ground no earlier row held (`--cached` scope, `process` substitution, worktree/index attribute order). A new r72 section in `corpus/knowledge/filter-filemode-witness.md` cites them in its table. Two SCORECARD capability rows (base-slot bound verdict, filter-witness matrix rows).
- **quality: improved.** Own material found false and corrected in-round with names: S313 anchor and scope, S314 teaches cell, the knowledge "every status read" sentence (lesson M5, fixture 1/0/0). r71 instrument defects mined as M1/M2 with fixes shown able to fail (Y6 EXIT 0 → 1; Y1/Y9 killed). No admitted entry failed the closure's re-check.
- **discernment: improved.** The non-author spot-check agrees with the gate on 2 admits and 2 non-admits, and on both in-round corrections. Not graded higher than that: the lane's own disagreements came from its seats, and no `QUALITY.md` criterion was added this round.

## Routed defects (lane must fix next round)

- **D1 (knowledge header):** `corpus/knowledge/filter-filemode-witness.md` line 1 `source:` lists S306 S307 S308 S310 S311 only; S312–S314 are cited only in the r72 section body, and `verified-at:`/`recheck:` still name r71 commits and the r71 counter. Add S312–S314 to `source:` and an r72 `verified-at`/`recheck` (the r72 counter command).
- **D2 (frozen over-reach):** `census/round-72/c1-counter.py:28` still says "status reads the worktree file, S314". It is frozen; correct it in the next counter's bytes and name it in that round's lesson.
- **D3 (HIGH, writer):** index stat-cache forgery (S72Sentinel) and WM7 reachable through a crafted `../` index path (S72ExecFailOpen); FIFO hang and OOM in `check-attr` (MEDIUM). Lesson route (a)/(b).
- **D4 (instrument):** refuse-row fixture validity (WM4 still scored `forgery` with FWi's in-run bytes equal to the committed bytes); defect-specific harness kills and a pinned witness population; clean_env neighbours. Lesson route (c)/(d).
- **D5 (receipts, M4):** receipt `command=` lines are not literally replayable (`<scratch>` work dirs, absolute scratch slot paths); the sha256 is the only binding. Lesson route (f).
- **D6 (operator note):** all four SHONEN boxes carry `[~]` with pointers a non-author can check (registry rows, LOG entry with receipts, seat reproductions, PROVINCE unchanged). Promotion is operator-owned; this closure writes no `[x]`.
