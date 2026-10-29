# R42w2mutationtester02 — mutation test of the LANDED `tools/souji-freeze-check.py` (part B)

Seat: `R42w2mutationtester02` · role mutation-tester · axis **operability** · wave 2 (falsify).
Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin` · base `bf618f6c5c09d302994871c94903abbea2deb60d` ·
freeze `afe17f416eec04dcf3f480b580a8f928de61d19d` · landed tip under attack `3105a63b23481fccf7df58e74d14a6681e0ea0c8`.

**What this attacks.** The detection power of the landed C2 instrument, not the tool's behaviour. The
frozen counter `census/round-42/c2-counter.py` (sha256 `fa44392d11338daa73b3b4b9b2fc8f89879c099e9bf278d7b45fa55dea5d0ac1`)
and the tool's own `--selftest` claim that the tool is checked. Each mutant is one single-point change
to a copy of the landed bytes; the question is whether the frozen counter or `--selftest` turns red.

**Verdict in one line.** The landed tool is not refuted: 57 of 88 single-point mutants are killed. The
frozen instrument has **31 survivors**; 20 of them are real coverage gaps (each shown by a pristine-vs-mutant
run), 11 are behaviour-equivalent under the frozen contract. No frozen file, and no lane file, was edited.

---

## 1. Method and baseline

**Baseline (the green reference the instrument must protect).**

```
$ bash /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-42/score-candidate.sh c2 <scratch>
real ok rc=0 findings=0 summary=(3, 0)
retro red rc=1 findings=19 summary=(3, 19)
retro_clean ok rc=0 findings=0 summary=(3, 0)
selftest ok rc=0 summary=(31, 31, 0)
SUMMARY cases=37 pass=37 fail=0 control_clean=REJECTED control_findings=REJECTED real=ok retro=red retro_clean=ok selftest=ok patches=3/3 tool_sha=9ddd596b98fb
exit 0
$ python3 -B tools/souji-freeze-check.py --selftest
SELFTEST cases=31 pass=31 fail=0        (exit 0)
```

Receipts: `receipts/` is in the seat directory; the baseline stdout is `logs/PRISTINE.counter.txt` and
`logs/PRISTINE.selftest.txt`.

**Mutant generation.** `gen_mutants.py` (55 mutants, `M01`–`M55`) and `gen_mutants_b.py` (33 mutants,
`N01`–`N33`) read the pristine bytes with `git -C <lane> show 3105a63…:tools/souji-freeze-check.py`
and apply exactly one string replacement per mutant. The generator asserts `src.count(old) == 1` and
`compile(...)` on the result, so every mutant is a single, syntactically valid point change. 88 mutants
are in `mutants/` (+ `INDEX.tsv`, `INDEX-partB.tsv`).

**Part B coverage.** Lines ≥ 188 (the second half of the 375-line file) receive **53** of the 88 mutants
(`table.tsv`, column `part`). Two of the N-series mutants (N12, N13) change `evaluate()` at lines
178–181, which sits just above the half-way line; they are counted in the N-series, not in the line-based
53. The part-B set covers every area the assignment named: the `KEY-DUPLICATE` code (M06–M09, N01), the
`HEADING-MALFORMED` regexes (M01–M03, M27, N12), the symlink mode test `120000` (M10–M14), the widened
dispatch-name test (M15–M22, N11, N16), and the `--selftest` implementation: the fixtures and digest
literals (M55, N14–N18), the case table (M48, N19, N20), `selftest_case()`'s repository construction
(M46, M47, N21–N25), the accounting and output (M49–M54, N26–N28), and `main()`'s CLI and refusal
contract (N29–N33).

**Scoring.** Every mutant was scored twice, in its own scratch work directory:

1. the tool's **own** `--selftest` on the mutant bytes: `python3 -B <mutant> --selftest` (its exit code is stored as `selftest_exit`);
2. the **frozen counter** over the committed tip plus the mutant: `bash census/round-42/score-candidate.sh c2 <work> tools/souji-freeze-check.py=<mutant>` (its exit code is `counter_exit`).

Harness: `run_mutants.sh` (M series, 6-way parallel), `run_partb.sh` (N series, 6-way parallel).
Per-mutant record: `results/<name>.py.tsv` / `results/<name>.tsv`. Raw output: `logs/<name>.counter.txt`,
`logs/<name>.selftest.txt`.

**Verdict rule.** **KILLED** = the counter's `SUMMARY` is not the target (counter exit 1) **or** the mutant's
own `--selftest` exits non-zero. **SURVIVED** = counter exit 0 **and** own `--selftest` exit 0. The
baseline is green, so no verdict is inconclusive.

**Column meaning in §3.** `counter cases` is `pass/37` from the counter's `SUMMARY`. `--selftest` is the
verdict the counter's **selftest leg** reports for the mutant's printed `SELFTEST` line (`ok` or `FAIL`);
where the mutant's own `--selftest` exit differs from that leg, the verdict says so. Five mutants (M49,
M50, N26, N27, N29) exit 0 on their own `--selftest`; they are killed by the counter's selftest leg or
patches leg, not by their own exit code.

---

## 2. Headline numbers

| | count |
|---|---|
| mutants generated | **88** |
| mutants landing at line ≥ 188 (part B by line) | **53** (36 killed, 17 survived) |
| **killed** | **57** |
| — with ≥ 1 counter case red | 34 |
| — with all 37 counter cases green (killed by the self-test or patches legs) | 23 |
| **survived** | **31** (`survivor count: 31`) |

The 23 killed with all counter cases green: M33, M46, M47, M48, M49, M50, M52, M53, M55, N14, N15, N16,
N17, N18, N21, N22, N23, N24, N25, N26, N27, N28, N29. Of these, 18 are reddened by their own
`--selftest` exit code (exit 1); M49 and N26 are reddened only by the `patches=0/3` leg (their own exit is 0
and the counter's selftest leg reads `ok`); M50 prints `SELFTEST n=` (a label the counter does not parse), N27 prints
swapped pass and fail counts, and N29 prints nothing; each exits 0 on its own, so the counter's selftest leg reads `FAIL`.


---

## 3. The table

Full machine-readable table with each mutant's line and sha256-12: `table.tsv`.

| mutant | change | counter cases | --selftest | verdict |
|---|---|---|---|---|
| M01-header-no-boundary | `HEADER` drops the space/EOL boundary; `## C2x` becomes a claim | 36/37 | FAIL | KILLED |
| M02-badhead-never | `BADHEAD` can never match; HEADING-MALFORMED never reported | 33/37 | FAIL | KILLED |
| M03-badhead-digit-optional | `BADHEAD` digit optional; every `## C<n>` heading also malformed | **37/37** | **ok** | **SURVIVED** |
| M04-keyline-drop-kill | `KEYLINE` no longer recognises `Kill` | 3/37 | FAIL | KILLED |
| M05-keyline-allow-indent | `KEYLINE` accepts indented key lines | **37/37** | **ok** | **SURVIVED** |
| M06-dup-never-recorded | repeated key never added to the duplicate set | 34/37 | FAIL | KILLED |
| M07-dup-class-renamed | KEY-DUPLICATE reported under another class | 34/37 | FAIL | KILLED |
| M08-dup-key-still-evaluated | duplicated key no longer deleted before evaluation | **37/37** | **ok** | **SURVIVED** |
| M09-dup-unsorted | duplicates reported in set order, not sorted | **37/37** | **ok** | **SURVIVED** |
| M10-symlink-mode-no-space | symlink mode test drops the trailing space | **37/37** | **ok** | **SURVIVED** |
| M11-symlink-mode-wrong | symlink mode test uses `12000 ` | 35/37 | FAIL | KILLED |
| M12-symlink-at-rev-not-freeze | symlink tested at REV, not FREEZE-REV | **37/37** | **ok** | **SURVIVED** |
| M13-symlink-class-renamed | symlink finding class renamed | 35/37 | FAIL | KILLED |
| M14-symlink-any-type | `is_symlink` accepts any tree entry type | 3/37 | FAIL | KILLED |
| M15-dispatch-drop-dispatch | dispatch name test drops `-dispatch` | 35/37 | FAIL | KILLED |
| M16-dispatch-drop-ready | dispatch name test drops `.ready` | 36/37 | FAIL | KILLED |
| M17-dispatch-drop-json | dispatch name test drops `-spec.json` / `-results.json` | 35/37 | FAIL | KILLED |
| M18-dispatch-name-is-full-path | dispatch name test uses the full path, not the basename | **37/37** | **ok** | **SURVIVED** |
| M19-dispatch-ancestor-only-freeze | dispatch check drops the ancestor test | 32/37 | FAIL | KILLED |
| M20-dispatch-ancestor-only | dispatch check drops the `c == freeze` shortcut | **37/37** | **ok** | **SURVIVED** |
| M21-dispatch-first-setdefault | oldest adding commit no longer kept | **37/37** | **ok** | **SURVIVED** |
| M22-dispatch-tree-no-slash | dispatch tree pathspec loses its trailing slash | **37/37** | **ok** | **SURVIVED** |
| M23-dispatch-missing-round-silent | a missing `Round:` no longer yields FIELD-MISSING C0 | **37/37** | **ok** | **SURVIVED** |
| M24-no-claims-removed | NO-CLAIMS never raised | 36/37 | FAIL | KILLED |
| M25-keys-drop-kill | `KEYS` drops `Kill` | 35/37 | FAIL | KILLED |
| M26-field-empty-never | empty key value never FIELD-EMPTY | 36/37 | FAIL | KILLED |
| M27-heading-label-c1 | HEADING-MALFORMED labelled C1 not C0 | 33/37 | FAIL | KILLED |
| M28-claim-label-shifted | claim labels off by one | 16/37 | FAIL | KILLED |
| M29-base-commit-no-full40 | Base resolved even when not full 40-hex | **37/37** | **ok** | **SURVIVED** |
| M30-base-not-ancestor-drop | BASE-NOT-ANCESTOR loses the ancestor comparison | 36/37 | FAIL | KILLED |
| M31-base-ancestor-inverted | the ancestor comparison is inverted | 6/37 | FAIL | KILLED |
| M32-population-empty-threshold-1 | POPULATION-EMPTY needs 1 line, not 2 | 36/37 | FAIL | KILLED |
| M33-population-empty-threshold-3 | POPULATION-EMPTY needs 3 lines, not 2 | **37/37** | **FAIL** (own exit 1) | KILLED (self-test leg only) |
| M34-control-first-line | control receipt read from its first line | 5/37 | FAIL | KILLED |
| M35-control-exit-inverted | the red-control test is inverted | 4/37 | FAIL | KILLED |
| M36-control-at-rev | control receipt read at REV, not FREEZE-REV | **37/37** | **ok** | **SURVIVED** |
| M37-path-sha-no-spaces | `PATH_SHA` no longer accepts a path with spaces | **37/37** | **ok** | **SURVIVED** |
| M38-path-sha-uppercase-hex | `PATH_SHA` accepts uppercase hex | **37/37** | **ok** | **SURVIVED** |
| M39-digest-compare-inverted | the stated digest compared for equality | 3/37 | FAIL | KILLED |
| M40-no-sha256-not-reported | a value without `sha256=` is not separately reported | **37/37** | **ok** | **SURVIVED** |
| M41-frozen-edited-never | FROZEN-EDITED never raised | 35/37 | FAIL | KILLED |
| M42-frozen-blob-at-rev | freeze blob read at REV | 35/37 | FAIL | KILLED |
| M43-counter-missing-class | missing-counter class renamed | 36/37 | FAIL | KILLED |
| M44-keyline-trailing-space-kept | `KEYLINE` keeps trailing whitespace in the value | **37/37** | **ok** | **SURVIVED** |
| M45-population-blank-counted | POPULATION-EMPTY counts blank lines as content | **37/37** | **ok** | **SURVIVED** |
| M46-selftest-no-git-init | the self-test no longer initialises a git repository | 37/37 | **FAIL** (own exit 1) | KILLED (self-test leg only) |
| M47-selftest-commit-without-staging | the self-test commits without staging its files | 37/37 | **FAIL** (own exit 1) | KILLED (self-test leg only) |
| M48-selftest-cases-truncated | the self-test runs only 5 of its cases | 37/37 | **FAIL** (own exit 1) | KILLED (self-test leg only) |
| M49-selftest-always-exit-0 | the self-test always exits 0 | 37/37 | ok (own exit 0) | KILLED (patches leg only: `0/3`) |
| M50-selftest-print-label | the self-test prints `SELFTEST n=` (label the counter does not parse) | 37/37 | **FAIL** (own exit 0) | KILLED (counter selftest leg) |
| M51-selftest-exception-passes | **a self-test case that raises is counted as a pass** | **37/37** | **ok** | **SURVIVED** |
| M52-selftest-placeholder-swap | the `@`/`%` placeholders are swapped | 37/37 | **FAIL** (own exit 1) | KILLED (self-test leg only) |
| M53-selftest-no-orphan-commit | the self-test no longer creates the non-ancestor commit | 37/37 | **FAIL** (own exit 1) | KILLED (self-test leg only) |
| M54-selftest-expectation-ignored | **the self-test compares exit codes only, ignoring expected findings** | **37/37** | **ok** | **SURVIVED** |
| M55-selftest-sha-literal-wrong | a literal fixture digest in the self-test is wrong | 37/37 | **FAIL** (own exit 1) | KILLED (self-test leg only) |
| N01-dup-key-becomes-empty | the duplicated key is blanked instead of deleted | 34/37 | FAIL | KILLED |
| N02-field-empty-skips-kill | the FIELD-EMPTY loop stops before `Kill` | **37/37** | **ok** | **SURVIVED** |
| N03-base-unresolved-class | BASE-UNRESOLVED class renamed | 36/37 | FAIL | KILLED |
| N04-base-not-ancestor-class | BASE-NOT-ANCESTOR class renamed | 36/37 | FAIL | KILLED |
| N05-base-unresolved-detail | the BASE-UNRESOLVED detail loses the value | **37/37** | **ok** | **SURVIVED** |
| N06-base-not-ancestor-detail | the BASE-NOT-ANCESTOR detail loses "strict" | **37/37** | **ok** | **SURVIVED** |
| N07-population-never-read | the Population path is never checked | 32/37 | FAIL | KILLED |
| N08-population-empty-too-many-lines | a population with > 100 lines is also reported empty | **37/37** | **ok** | **SURVIVED** |
| N09-control-exit-gt-zero | `!= 0` replaced by `> 0` on the EXIT value | **37/37** | **ok** | **SURVIVED** (equivalent, §4b) |
| N10-control-missing-detail | the CONTROL-MISSING detail loses path and revision | **37/37** | **ok** | **SURVIVED** (equivalent, §4b) |
| N11-dispatch-leg-no-round | the dispatch leg is fed an empty text | 2/37 | FAIL | KILLED |
| N12-heading-malformed-never | the malformed-heading list is discarded | 2/37 | FAIL | KILLED |
| N13-no-claims-never | the NO-CLAIMS finding is never raised | 36/37 | FAIL | KILLED |
| N14-sha-p-literal-wrong | the population fixture digest literal is wrong | 37/37 | **FAIL** (own exit 1) | KILLED (self-test leg only) |
| N15-sha-p1-literal-wrong | the one-line population digest literal is wrong | 37/37 | **FAIL** (own exit 1) | KILLED (self-test leg only) |
| N16-spec-path-wrong | the self-test's dispatch marker path is wrong | 37/37 | **FAIL** (own exit 1) | KILLED (self-test leg only) |
| N17-prereg-format-glues-keys | the synthetic prereg glues key lines onto the heading | 37/37 | **FAIL** (own exit 1) | KILLED (self-test leg only) |
| N18-prereg-no-kill-key | the synthetic prereg has no `Kill` key | 37/37 | **FAIL** (own exit 1) | KILLED (self-test leg only) |
| N19-selftest-case-counter-symlink-dropped | the self-test drops its counter-symlink case (cases=30) | **37/37** | **ok** | **SURVIVED** |
| N20-selftest-case-population-empty-dropped | the self-test drops its population-empty case (cases=30) | **37/37** | **ok** | **SURVIVED** |
| N21-selftest-no-committer-identity | the self-test's git env has no committer identity | 37/37 | **FAIL** (own exit 1) | KILLED (self-test leg only) |
| N22-selftest-prereg-filename-wrong | the self-test looks for a prereg filename never committed | 37/37 | **FAIL** (own exit 1) | KILLED (self-test leg only) |
| N23-selftest-rev-override-ignored | the self-test ignores the per-case `--rev` override | 37/37 | **FAIL** (own exit 1) | KILLED (self-test leg only) |
| N24-selftest-pre-files-not-committed | the self-test does not commit its pre-freeze files | 37/37 | **FAIL** (own exit 1) | KILLED (self-test leg only) |
| N25-selftest-symlink-not-created | the self-test writes its symlink case as a regular file | 37/37 | **FAIL** (own exit 1) | KILLED (self-test leg only) |
| N26-selftest-pass-count-always | the self-test counts every case as a pass | 37/37 | ok (own exit 0) | KILLED (patches leg only: `0/3`) |
| N27-selftest-pass-fail-swapped | the self-test prints pass and fail swapped | 37/37 | **FAIL** (own exit 0) | KILLED (counter selftest leg) |
| N28-selftest-expectations-never-compared | the self-test collects no findings | 37/37 | **FAIL** (own exit 1) | KILLED (self-test leg only) |
| N29-main-selftest-mode-short-circuits | `--selftest` returns 0 without running the self-test | 37/37 | **FAIL** (own exit 0) | KILLED (counter selftest leg) |
| N30-main-findings-unsorted | the FINDING lines are printed in discovery order, not sorted | **37/37** | **ok** | **SURVIVED** |
| N31-main-exit-only-when-two-findings | the tool exits 0 when exactly one finding is reported | 7/37 | FAIL | KILLED |
| N32-main-refusal-detail-lost | the refusal message loses the revision and root | **37/37** | **ok** | **SURVIVED** (equivalent, §4b) |
| N33-main-rev-format-not-checked | `--rev` is not checked for the full 40-hex form | **37/37** | **ok** | **SURVIVED** |

**Survivor count: 31** (M03, M05, M08, M09, M10, M12, M18, M20, M21, M22, M23, M29, M36, M37, M38, M40,
M44, M45, M51, M54, N02, N05, N06, N08, N09, N10, N19, N20, N30, N32, N33).

---

## 4. The survivors: real gaps and equivalent mutants

A survivor is a finding only if the mutant's observable behaviour differs from the pristine tool on some
input. Each real gap below was shown by a pristine-vs-mutant run; the receipts are in `receipts/`.

### 4a. Real coverage gaps (20)

| mutant | scenario | pristine | mutant | why the instrument is blind |
|---|---|---|---|---|
| **M03** | `##` heading with `C` and no digit (`## Claim notes`) | `SUMMARY claims=1 findings=0` | `FINDING C0 HEADING-MALFORMED line=10` | the frozen grammar requires `C`/`c`, optional spaces, **a digit**; all four counter heading cases carry a digit |
| **M05** | an indented key line (`    Target: t`) | `FINDING C1 FIELD-MISSING Target` | `SUMMARY claims=1 findings=0` | the frozen grammar says a key line is `Key: value` **at column 0**; no case has an indented key |
| **M08** | duplicated `Base:` whose **first** occurrence is `0000…0` | `FINDING C1 KEY-DUPLICATE Base` | `FINDING C1 BASE-UNRESOLVED 0000…0` + `FINDING C1 KEY-DUPLICATE Base` | the counter's `dup-base-differs` puts the resolvable base first, so "first occurrence wins" and "last occurrence wins" read the same |
| **M12** | Counter path a regular file at FREEZE, a symlink at REV | `FINDING C1 FROZEN-EDITED c.py differs between freeze … and …` | `FINDING C1 COUNTER-SYMLINK c.py is a symlink at freeze …` | every counter symlink case creates the symlink before the freeze commit |
| **M18** | a file under a directory named `-dispatch-dir/` | `SUMMARY claims=1 findings=0` | `FINDING C0 DISPATCH-BEFORE-FREEZE .ufo/waves/round-7/-dispatch-dir/notes.md …` | the dispatch test is documented as a basename test; no case has a dispatch-looking directory name |
| **M21** | a dispatch-named file added before freeze, deleted, re-added after freeze | `FINDING C0 DISPATCH-BEFORE-FREEZE … w1-spec.json first added at cdfe25e163da` | `SUMMARY claims=1 findings=0` | the dispatch cases add each file once; oldest-vs-newest adding commit is never distinguished |
| **M23** | preregistration with no `Round:` line | `FINDING C0 FIELD-MISSING Round` | `SUMMARY claims=1 findings=0` | the r41 hardening (R41critic01 D1/D10) has no case in the 37 |
| **M29** | `Base: main` (symbolic, not 40-hex) | `FINDING C1 BASE-UNRESOLVED main` | `FINDING C1 BASE-NOT-ANCESTOR main is not a strict ancestor of freeze …` | the counter's base-unresolved case uses `0`×40, which fails at resolution, not format; the two classes coincide only by accident |
| **M36** | control receipt red at FREEZE, green at REV | `SUMMARY claims=1 findings=0` | `FINDING C1 CONTROL-NOT-RED ctl.txt last line 'EXIT=0' …` | no counter case edits the control after the freeze |
| **M37** | counter path with a space (`my counter.py`) | `SUMMARY claims=1 findings=0` | `FINDING C1 COUNTER-MISSING my not present at freeze …` | the r41 "repo paths may contain spaces" rule has no case in the 37 |
| **M44** | trailing whitespace after a key value | `SUMMARY claims=1 findings=0` | `FINDING C1 BASE-UNRESOLVED 15478ec4…` | no case has trailing whitespace on a key line |
| **M45** | population `h\n\n` (one content line, one blank) | `FINDING C1 POPULATION-EMPTY p.tsv has 1 non-blank line(s)` | `SUMMARY claims=1 findings=0` | the counter's population-empty case has no blank line |
| **N02** | `Kill:` with an empty value | `FINDING C1 FIELD-EMPTY Kill` | `SUMMARY claims=1 findings=0` | the counter's field-empty case empties `Target`, never `Kill` |
| **N08** | population with 120 non-blank lines | `SUMMARY claims=1 findings=0` | `FINDING C1 POPULATION-EMPTY p.tsv has 120 non-blank line(s)` | no case has a population larger than two lines |
| **N30** | two findings whose discovery order ≠ sorted order | `COUNTER-DIGEST` then `FIELD-MISSING` | `FIELD-MISSING` then `COUNTER-DIGEST` | the counter sorts the pairs itself, so output order is invisible to it |
| **N33** | `--rev HEAD` (not 40-hex) | `rc=2 REFUSAL COULD-NOT-EVALUATE: --rev must be a full 40-hex commit id` | `rc=1` with a full findings report | the refusal leg tests an unresolvable 40-hex rev and an absent prereg, never the 40-hex format |
| **M51** | a self-test case that **raises** (digest function raises at runtime) | `rc=1 SELFTEST cases=31 pass=3 fail=28` | `rc=0 SELFTEST cases=31 pass=31 fail=0` | the counter's three patches (P1 digest reversed, P2 `git log` neutered, P3 `merge-base` failing) never make a case raise, so the `except` branch that marks a case failed is never exercised |
| **M54** | the self-test ignores expected findings, and a finding class is renamed at print time (patch P4) | `rc=1 SELFTEST cases=31 pass=30 fail=1` | `rc=0 SELFTEST cases=31 pass=31 fail=0` | the counter's patches P1–P3 all change the exit code, so an exit-code-only comparison still fails them; P4 (exit code unchanged, findings corrupted) separates M54 from the pristine tool and is not in the counter |
| **N19** | the self-test drops its counter-symlink case (cases=30) | `SELFTEST cases=31 pass=31` | `SELFTEST cases=30 pass=30` | the counter's selftest leg only requires `cases >= 12` |
| **N20** | the self-test drops its population-empty case (cases=30) | `SELFTEST cases=31 pass=31` | `SELFTEST cases=30 pass=30` | the same `>= 12` floor |

### 4b. Behaviour-equivalent survivors (11)

| mutant | basis for equivalence |
|---|---|
| **M09** | `sorted(dups)` → `dups`: `main()` sorts every FINDING line anyway, so the output is byte-identical. Probe: `probe_survivors.py` scenario O, identical output on pristine, M09 and M08 (`receipts/probe_partA_survivors.txt`). |
| **M10** | `startswith(b"120000 ")` → `startswith(b"120000")`: git tree modes are six digits, so any entry starting `120000` is exactly mode 120000. Probe Q: identical `FINDING C1 COUNTER-SYMLINK …` (`receipts/probe_partA_survivors.txt`). |
| **M20** | dropping `c == freeze`: a commit is its own ancestor, so `merge-base --is-ancestor c c` already returns 0. Probe R: identical output. |
| **M22** | dropping the trailing `/` from the dispatch pathspec: probe P (nested dispatch file) identical in both; the sibling-directory run (`round-421/`, must not match `round-42`) is clean in both (`receipts/probe_extra.txt`). |
| **M38** | uppercase digest: pristine and mutant both report `COUNTER-DIGEST` for a case that differs only in the case of the digest (the mutant accepts the uppercase form and then compares it with lowercase hex). The class and exit are identical on every probed input; only the detail string differs (`receipts/probe_partA_survivors.txt`, probe L). |
| **M40** | a value without `sha256=`: pristine reports `COUNTER-DIGEST … has no sha256=`, the mutant reports `COUNTER-DIGEST … stated None`. Same class and exit on every probed input (probe M). |
| **N09** | `int(m.group(1)) != 0` → `> 0`: `EXIT_LINE` is `^EXIT=(\d+)$`, so the captured group is non-negative and `!= 0` ≡ `> 0` on every input the regex admits. Probe C (`EXIT=-1`, which the regex does not match) identical in both. |
| **N05, N06, N10, N32** | each changes only the detail string of a finding or refusal, never its class, count or exit code. The counter compares `(claim, class)` pairs and the `COULD-NOT-EVALUATE` substring. **Not probed separately; equivalence is by construction of the change.** |

**Net:** 20 real gaps (M03, M05, M08, M12, M18, M21, M23, M29, M36, M37, M44, M45, M51, M54, N02, N08,
N19, N20, N30, N33) and 11 equivalents (M09, M10, M20, M22, M38, M40, N05, N06, N09, N10, N32) = 31.

---

## 5. What the kills say about the landed tool

The `--selftest` leg earns its place. Eight mutants (M33, M46, M47, M48, M52, M53, M55 and M50) and the N-series
self-test kills N14–N18, N21–N25, N28 pass all 37 counter cases and are reddened by their own `--selftest` exit or by
the counter's selftest leg. Two (M49, N26) are reddened only by the `patches=3/3` leg.

* **M46 / M47** — "a mutant selftest that no longer builds repos" — **killed**. M46 removes
  `git("init", "-q")`, M47 removes `git("add", "-A")`; both print
  `selftest clean: CalledProcessError: Command '['git', '-C', …` and the counter reads `selftest=FAIL … patches=0/3`
  (`logs/M46-selftest-no-git-init.counter.txt`, `logs/M47-selftest-commit-without-staging.counter.txt`).
* **M48** — truncating the case table to five cases is caught (`SELFTEST cases=31 pass=5 fail=26`).
* **N19 / N20** — dropping one case is **not** caught (30 ≥ 12): the exact boundary of the counter's floor.
* **M51** — with the exception-raising patch the pristine tool reads `rc=1 pass=3`, M51 reads `rc=0 pass=31`
  (`receipts/probe_extra.txt`). The counter has no such patch.
* **M54** — with P4 (findings corrupted, exit code kept) the pristine tool reads `pass=30 fail=1` and M54 reads
  `pass=31 fail=0` (`receipts/probe_extra.txt`). The counter has no such patch.

---

## 6. Commands actually run, and lane integrity

```
# baseline
bash <lane>/census/round-42/score-candidate.sh c2 <scratch>        -> SUMMARY cases=37 pass=37 … selftest=ok patches=3/3, exit 0
python3 -B <lane>/tools/souji-freeze-check.py --selftest           -> SELFTEST cases=31 pass=31 fail=0, exit 0

# generation (writes only under the seat directory)
python3 -B gen_mutants.py                                          -> wrote 55 mutants
python3 -B gen_mutants_b.py                                        -> wrote 33 part-B mutants

# scoring
bash run_mutants.sh 6                                              -> DONE (55 records)
bash run_partb.sh 6                                                -> DONE (33 records)

# survivor probes
python3 -B probe_survivors.py      > receipts/probe_partA_survivors.txt
python3 -B probe_survivors_b.py    > receipts/probe_partB_survivors.txt
bash probe_receipts.sh             -> wrote receipts/probe_extra.txt  (N30, N33, M22, P-raise, P4)
```

Each run's observed output is in `logs/`, `receipts/` and the scoring tables above. The
`score-candidate.sh` clone commits happen inside its own scratch clone (the frozen wrapper's own behaviour).
No `git commit`, `git push`, `jj`, or `git config` was run in the lane or the fleet.

**Lane integrity, observed after every run:**

```
$ cd <lane> && git rev-parse HEAD
3105a63b23481fccf7df58e74d14a6681e0ea0c8
$ git status --porcelain --ignored=matching .ufo/waves/round-42/w2
!! .ufo/waves/round-42/
$ git check-ignore -v .ufo/waves/round-42/w2/R42w2mutationtester02/results/M01-header-no-boundary.py.tsv
.gitignore:1:.ufo/waves/  …
$ sha256sum tools/souji-freeze-check.py
9ddd596b98fbf41b67f98a389c488b1e84d2ef4a7b5fdb0c8711451a007acec6  tools/souji-freeze-check.py
$ git show 3105a63…:tools/souji-freeze-check.py | sha256sum
9ddd596b98fbf41b67f98a389c488b1e84d2ef4a7b5fdb0c8711451a007acec6  -
```

The landed tool is byte-identical to the tip it was read at. The seat directory is git-ignored
(`.gitignore:1` covers `.ufo/waves/`), so nothing in the seat is tracked and nothing tracked was changed.
The frozen counter, population, control and preregistration were only read; their digests were not
modified (`c2-counter.py` `fa44392d…`, `c2-cases.tsv` `148b7b87…`, `controls/c2-control.txt` `45af0cc9…`).

**Scratch.** All clones, fixture repositories, patch directories and work directories lived under
`/fast/scratch/hyaku/souji-r42/R42w2mutationtester02/`. That directory was removed (`rm -rf`) after the
last receipt was copied into the seat, and `ls` afterwards reports it absent. No `/tmp` path is cited.

**Installs/updates:** none. The task needed only `python3` 3.14.8 and `git` already on the host.

---

## 7. Verdict

**The landed C2 tool is not refuted.** 57 of 88 single-point mutants are killed. Against the four
targets the assignment named:

* **KEY-DUPLICATE** — killed: M06, M07, N01. Survived: **M08** (real gap: first-occurrence rule not pinned), **M09** (equivalent).
* **HEADING-MALFORMED regexes** — killed: M01, M02, M27, N12. Survived: **M03** (real gap: the digest requirement is unpinned).
* **Symlink mode test `120000`** — killed: M11, M13, M14. Survived: **M10** (equivalent), **M12** (real gap: symlink at FREEZE vs REV is not distinguished).
* **Widened dispatch-name test** — killed: M15, M16, M17, N11, N16. Survived: **M18** (real gap: basename vs full path), **M21** (real gap: oldest vs newest adding commit), **M20** and **M22** (equivalent).
* **`--selftest` implementation** — killed: M46 and M47 (the mutant self-test that no longer builds repos), M48, M52, M53, M55, N14–N18, N21–N25, N28, plus M33 and the counter-leg kills M50, N27, N29. Survived: **M51** and **M54** (real gaps: a raising case and an expectation-free comparison pass the self-test), **N19** and **N20** (real gap: the `cases >= 12` floor admits a dropped case).

The frozen instrument has **20 named coverage gaps** (§4a), each shown by a pristine-vs-mutant run, and 11
behaviour-equivalent survivors (§4b). None is a defect of the landed tool: the landed bytes are correct on
every probed scenario. They are limits of the frozen counter and of the `--selftest` leg, and are offered
to the L1 as named limits. Per the preregistration (rule 1), no frozen file is amended.

The two that bound the `patches=3/3` and `selftest=ok` claims most directly are **M51/M54** (a self-test
that swallows exceptions or ignores its expected findings still reads `ok`) and **N19/N20** (the `>= 12`
floor). The first is separated from the pristine tool only by a raising patch or a findings-corrupting
patch, neither of which the counter runs.

---

## Files in the seat directory (`.ufo/waves/round-42/w2/R42w2mutationtester02/`, git-ignored)

| path | what |
|---|---|
| `../R42w2mutationtester02.md` | this report |
| `gen_mutants.py`, `gen_mutants_b.py` | mutant generators (one replacement each, count asserted, compile-checked) |
| `mutants/*.py` (88), `mutants/INDEX.tsv`, `mutants/INDEX-partB.tsv` | the mutants and their descriptions |
| `run_mutants.sh`, `run_partb.sh` | the scoring harnesses |
| `results/*.tsv` (88) | per-mutant result records (`selftest_exit`, `counter_exit`, `counter_summary`, failed case names) |
| `logs/*.counter.txt`, `logs/*.selftest.txt`, `logs/PRISTINE.*` | raw counter and self-test output |
| `table.tsv` | the machine-readable table behind §3 (line, part, sha256-12, verdict) |
| `probe_survivors.py`, `probe_survivors_b.py`, `probe_receipts.sh` | the survivor probes |
| `receipts/probe_partA_survivors.txt`, `receipts/probe_partB_survivors.txt`, `receipts/probe_extra.txt` | probe output (pristine vs mutant), including the N30, N33, M22, P-raise and P4 runs |
