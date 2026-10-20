STATUS: DONE — D1–D7 mapped to the bar: 3 extension rows (Q27→Q22 for D1+D2, Q28→Q10 for D3, Q29→Q25(c)/Q26 for D4+D5+D6), D7 already covered by Q17; no criterion rewritten, no fourth row needed.

# Review — QUALITY criteria fit for routed defects D1–D7 (round 17, wave 1)

Scope: the closure's routed items only (`corpus/lessons/round-16-verifier-spotcheck.md`
"Routed defects"). Claims C1–C3 are the build's; this file judges only which
criterion should have caught each defect and what the bar needs so the next
round catches it. Read-only. No lane tool, fixture, matrix, audit or census was
executed. No git write, no `jj`. Tool installs: none.

## Base state verified at `5fa6017`

`git rev-parse HEAD` → `5fa6017ddcae9f6bd4412df44765f6360cb16294`.
`sha256sum tools/souji-census.sh` → `64a60fd0b0ed4101…` (the claim's "unchanged
census bytes"). The worktree has no round-17 changes yet:
`git status --porcelain` → `?? .ufo/waves/round-17/`, `?? census/operator-sweep-20261019/`.
`corpus/lessons/round-17.md` does not exist; `tests/fixtures/r17-*` and
`census/round-17/` do not exist. The criteria below are therefore drafted against
the *declared* r17 build, and their tests can only run after that build lands.

## Per-defect attribution

| D | defect (closure's words, condensed) | criterion that should have caught it | why it did not, as written | disposition |
|---|---|---|---|---|
| D1 | repo-local/included/`config.worktree` `status.showUntrackedFiles=no` gives a dirty repo a clean row | **none.** Nearest: Q22 ("Configuration treatment is value/effect-aware") | Q22's operative clause covers a *harmless or already-neutralized* value that aborts or suppresses rows; a value that silently changes what the row reports is outside it. Q22's test says "preserve meaningful dirty counts", but no case exercises a repo-local semantics-changing key, and the false clean is a row-value falsification, not an abort. Q25 says a gate pass is consistency, not behavior; nothing owns row semantics | extend Q22 (Q27). Code fact: `count_dirty` (`tools/souji-census.sh:1021`) calls `git … status --porcelain --ignore-submodules=all` (`:1035-1037`) with `-c` overrides for fsmonitor/hooksPath/excludesFile/attributesFile only; `grep -n 'untracked-files\|showUntrackedFiles' tools/souji-census.sh` returns nothing. `dirty=0` with no problem flag appends `clean` (`:1217-1239`) |
| D2 | hardlinked/non-regular `$GIT_DIR/info/attributes` aborts the whole fleet run | **none in letter.** Nearest: Q22's "must not … suppress unaffected fleet rows" | That clause is scoped to configuration *values*; a fixed-metadata file shape is not config. No criterion states which per-repo conditions degrade and which are run-fatal. Q19 owns special files only in deletion paths | extend Q22 (Q27). Code fact: `guard_git_files` (`:519-535`) lists `info/attributes` beside `config HEAD index packed-refs commondir info/exclude objects/info/alternates`; every guard failure reaches `protected_fail` (`:200-208`), which exits 2; the five call sites (`:790 :831 :849 :873 :891`) all append `|| exit 2` |
| D3 | `LOG.md:902` says 28 uncarried (re-derived 29); `LOG.md:858-859` says pre-harm fails "only refusal/safety" (it also fails 03, 18) | **none.** Q10 is the bookkeeping criterion | Q10's clause is "the bookkeeping matches the repo", but its test is SCORECARD-prose-vs-table plus `## Planned` and cert-note; it never re-derives a LOG number or an "only/exactly" set. Q5 re-derives verdict *tables*, not LOG prose. The fleet floor ("a count carries its command") is prose, not a Q row | extend Q10 (Q28) |
| D4 | 3 wave-2 `V-WRITE-SCOPE` majors are false positives; audited transcripts uncommitted and undigested | **Q26, partially** ("Every flagged row is confirmed by reading the call before voiding") | Q26 requires confirmation but has no durability clause (retained bytes + digest) and no clause that an observed false-positive shape becomes a control. Its own text already discloses imprecision ("4 of 20 … were not violations"), which normalizes the FP rate instead of fixing it. The w2 audit JSON carries exactly the three FP shapes | extend Q26 (Q29). Code fact: `write_target` splits on the first comma (`tools/souji-seat-audit.py:68-73`); `allowed_target` uses `target.lstrip("./")` (`:76-82`), which strips `.ufo`'s leading dot. Verified w2 majors: `.ufo/waves/round-16/w2/ConnReadmeIndex.md`; `\| 2 \| stale pin \| …`; `N6 is the exact harm …` |
| D5 | `round-16.md:54` has `resolved:` with no `@<hex>`; two quotes stop at a line wrap; r15 :91/:93 joined/paraphrased; one more uncarried non-vocabulary line | **Q25(c), partially** | Q25(c) names `open`/`resolved@<rev>` and "verbatim", but defines the channel as `STATUS:` + a word from `FAILURE_STATUS_WORDS` and the unit as one physical line. `STATUS: skeleton only.` has a first word outside that set, so the gate never sees it; only the first physical line of a statement is the needle, so continuation truncation passes. All three observed defects are outside the criterion as written | extend Q25(c) (Q29) |
| D6 | gate replay verdicts only as seat transcripts/prose; selftest asserts exit + membership, not exact sets; `regenerate.py` writes a literal verdict | **none.** Q6/Q18 pin digests and authorship, not verdict evidence | `check()` in `tools/souji-landing-gate.py:766-774` is `all(i in ids …)` plus opt-in `forbid_ids`; an over-firing gate passes. `tests/fixtures/r15-preservation-frozen/regenerate.py:130` writes `"verdict": "clean"`. No row requires a committed `--json` run keyed to the revision it measured | new obligation family inside Q29 (extends Q25/Q26) |
| D7 | report says `gate-landing.json` "(gate at `6ff91f5`)" — the file lands at `c46eabf` and records a run over `6ff91f5` blobs | **Q17** ("must resolve … at the measured revision") | Q17's *text* catches it: the file is absent at `6ff91f5` (verified). Its *test* resolves only admitted entries' recheck paths, not report prose; the closure caught it by reading | no new row. Fix is application: the round Gate resolves every evidence path a report attaches a revision to, at that revision. Verified: `git cat-file -e c46eabf:census/round-16/gate-landing.json` → present; at `6ff91f5` → absent; the file's `resolved_rev` is `6ff91f534eece9ad…` |

## Proposed rows (Q27–Q29)

Rules of `QUALITY.md` allow no in-place rewrite; each row below is a new row that
names its parent(s), as Q19 did for Q8 and Q25 for Q17/Q23. Lesson ids are my
proposal (D1→M1 … D7→M7); L1 assigns the final `R17-M<n>`, and the rows must cite
the ids L1 lands — so the round-17 lesson rows must exist before these rows land.

```markdown
| Q27 | Extends Q22's configuration clause, retaining Q22's namespace, preservation and contraction rules: a repository condition may change neither what its row reports nor whether the run completes. A config value that changes a removal-relevant measurement (`status.showUntrackedFiles=no`) is neutralized on the command line (`--untracked-files=normal`), and if it cannot be pinned the row degrades — it never reads clean. A per-repository Git-metadata condition (hardlinked or non-regular fixed metadata) degrades only that repository: `error` row, a stderr diagnostic naming the reason and a redacted path, exit 0, neighbours byte-identical, and no git call that could read the refused file; a whole-run abort stays for run-level preconditions (unsafe root, missing tool) and the protected-namespace refusals Q21/Q22 retain. | census, row producers | `python3 census/round-17/run-matrix.py --changed <rev> --output <new.json>` over `tests/fixtures/r17-census-hygiene.py` with arms `a31642d`, `cc21683`, `5fa6017`, changed: the direct-key repo reads 0 on `a31642d`, `cc21683` and `5fa6017`, and its true nonzero count on changed; the `include` and `config.worktree` carriers read 0 or refuse on the baseline arms and the true count on changed, neighbours identical; a hardlinked `info/attributes` (linked to an attributes file binding a canary filter) yields `error`, the diagnostic, exit 0, no canary, unchanged neighbours, while a hardlinked `config` still exits 2. | corpus/lessons/round-17.md R17-M1 (D1), R17-M2 (D2) |
| Q28 | Extends Q10: a correction entry is itself a claim, appended and naming the line it corrects, never an in-place rewrite. Every count a correction states, every `only`/`exactly` failure set it asserts, and every published range (`Q1–Qn`) names the command and revision that derive it and is re-derived before the entry lands; a correction that miscounts needs a further correction. | LOG, README, round evidence | the round Gate re-runs each correction's named command at its named revision and fails on mismatch (`LG-LOG-COUNT`) and on a range endpoint that differs from the counted rows; the r16 instances fail: `LOG.md:902` states 28 where `79bbe7a` re-derives 29, and `LOG.md:858-859`'s "only refusal/safety" set omits 03 and 18 (actual `a31642d` ids 02,03,08,11,14,17,18,19); `grep -cE '^\| Q[0-9]+ \|' corpus/QUALITY.md` equals the README range endpoint. | corpus/lessons/round-17.md R17-M3 (D3) |
| Q29 | A verifier's counts are evidence only when its input is retained at the bytes it audited and its oracle is exact. Seat-audit transcripts are committed (or copied under `census/round-<N>/`) with a sha256 manifest whose entry count equals the audit's audited-seat count, and two runs over the copy are byte-identical; every false-positive shape a round observes becomes a committed selftest control before its counts are published. A carry is matched against the retained transcript's full failure statement — the `STATUS` first word is a channel floor, not its boundary, and a quote truncated before the statement ends needs an ellipsis — with `open` or a resolving `resolved@<40-hex>`. Every claimed gate replay is a committed machine-readable run naming the revision it measured and the exact finding-id set, where an extra id fails as well as a missing one; a generator never writes a verdict literal. Extends Q25(c) and Q26. | tools, round evidence | `tools/souji-landing-gate.py --selftest` fails when one extra finding id is added to a case (exact set, both directions) and when one expected id is omitted; each claimed replay (`b410186`→5, `a31642d`/`cc21683`→0, `79bbe7a`→29 uncarried, selftest 18/18, fixture 15/15, checker 24/47) is a committed `--json` run with its expected id set and the prose count equals `findings|length`; `grep -c '"verdict": "clean"' tests/fixtures/*/regenerate.py` → 0 (or the verdict is computed); `python3 tools/souji-seat-audit.py --selftest` carries the r16 `.ufo`-path and comma-prose unflagged controls, two runs over the committed r16 copy are identical, and `jq '.seats|length'` equals the manifest entries; a `resolved:` with no `@<hex>` and a no-ellipsis truncation fail carry. | corpus/lessons/round-17.md R17-M4 (D4), R17-M5 (D5), R17-M6 (D6) |
```

## Minimality

- **Three rows, two amendments and one extension of a named parent.** No
  criterion is rewritten. D1 and D2 share Q27 because both are "one repository's
  state decides its row or the run" — splitting them would put two criteria on
  the same obligation and the next metadata guard would fall between them.
- **D3 is not a new subject.** It is Q10's own claim ("bookkeeping matches the
  repo") with a test that reaches LOG corrections, "only" sets and published
  ranges; Q10's SCORECARD/Planned clauses stay.
- **D5 did have a criterion naming its format.** Q25(c) already says
  `resolved@<rev>` and "verbatim"; what it lacks is a channel not defined by a
  vocabulary and a unit larger than the first physical line. Folding that into
  Q29 is smaller than a fourth carry criterion, and it keeps one owner for
  "verifier evidence is the retained bytes and an exact oracle".
- **D7 gets no row.** Q17's text already fails the artifact if applied to
  report prose; adding a row would duplicate it. The fix is the Gate resolving
  prose-named evidence at the revision the prose names.
- **No new row for C3's jj edge class.** It is not a routed D-item, and Q22's
  mixed-fleet preservation is the nearest existing obligation. See residual risk.

## Sequencing (this is the part most likely to be missed)

1. `corpus/lessons/round-17.md` does not exist. LEARNING.md: "when no criterion
   caught it, a `QUALITY.md` criterion citing that lesson". Land the D1–D7
   `## Mistakes` rows first; Q27–Q29 must cite the ids L1 assigns, not my
   D-number mapping.
2. `corpus/README.md:31` says "Q1–Q26 since r16" and `:200` says "now runs
   Q1–Q26". Both must become Q1–Q29 in the same landing. Round 16 already
   shipped this exact defect (`ConnQuality2.md:206`, resolved@4f9a4e8), so Q28's
   range clause should be checked against the landed count, not written from
   memory.
3. Q27's test needs `tests/fixtures/r17-census-hygiene.py` and the matrix
   runner; Q29's test needs committed transcripts + manifest and committed `--json`
   replays. None exists at `5fa6017`. A criterion whose test cannot run at
   landing is not admitted; land artifacts first, or the row lands with the
   artifact commit.
4. Q25(b)'s known open item ("a dangling `measured_commit` is not yet flagged by
   the gate: open, r17") is **not** in the D6 list. If r17 lands exact-set
   oracles but not that check, Q25 is still knowingly incomplete; do not report
   Q25 as fully satisfied.

## Residual risk and verification gaps

- **C2's own evidence count is already unbound.** The claim says the r16
  transcripts are "w1 70 + w2 77 files"; the retained directory has
  `find …/w1 -type f | wc -l` → 65 and w2 → 79, and the committed audit JSONs
  say `seats_audited: 65` and `79` with `missing_transcripts: 0`. The declared
  counts do not match either source. Q29's manifest (entry count equals audited
  seats) is not hygiene here: the claim's counts are already wrong, and without
  the manifest the audit's "majors w2 3→0" cannot be replayed at the bytes it
  measured.
- **C3 (jj) has no criterion of its own.** The durable-roots rule (`refs/heads`,
  `refs/tags`, `refs/remotes`; never `refs/jj/*`, `refs/stash`, HEAD) and the
  `--glob=refs/jj/keep/*` addition to every unpushed-touching check are a new
  ref-class edge. Q22's mixed-fleet preservation is the nearest obligation, but
  it does not state that a plain repo (no `refs/jj`) must be byte-identical under
  the added glob. Claim (b) requires that control; no Q row does. If the cap is
  full at three, this is the next round's row; do not let the plain-repo
  control be dropped from the r17 Gate in the meantime.
- **D7's coverage is only as good as the Gate's application.** Q17's text
  resolves evidence at the measured revision; the r16 closure applied it to
  admitted entries' recheck paths only. Unless the r17 Gate resolves prose-named
  evidence at the revision the prose attaches, the same sentence passes again
  and "Q17 covered it" is a paper claim.
- **Verification gaps.** I ran no lane tool, fixture, matrix, census, audit or
  landing gate (probe rule), so every behavioural statement above is a source
  read or the closure's recorded re-measurement; the r16 transcript counts come
  from `find`/`ls` on the named `/var/tmp` directory (flat dirs, disclosed) and
  from the committed JSONs, not from re-running the audit. The r16 report file
  cited by the closure (`85f2aa9…`) is not in this repo's object store
  (`git cat-file -e 85f2aa9` fails), so D7's sentence is taken from the closure's
  quotation plus the file-presence check (`c46eabf` present, `6ff91f5` absent,
  `resolved_rev` = `6ff91f5…`). I did not re-derive the 29 count or the matrix
  failure ids; those are cited from the closure and `LOG.md`.

## Commands run (load-bearing, with output)

```text
git -C <lane> rev-parse HEAD                     → 5fa6017ddcae9f6bd4412df44765f6360cb16294
git -C <lane> status --porcelain=v1              → ?? .ufo/waves/round-17/ ; ?? census/operator-sweep-20261019/
sha256sum tools/souji-census.sh                  → 64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c
grep -n 'guard_git_files\|count_dirty' tools/souji-census.sh → 519,790,831,849,873,891,1021,1162,1205
grep -n 'status --porcelain\|untracked-files\|showUntrackedFiles' tools/souji-census.sh → 35,58,1037; no untracked-files/showUntrackedFiles hit
sed -n '1034,1040p' tools/souji-census.sh       → status --porcelain at :1037, no untracked mode
sed -n '519,537p' tools/souji-census.sh         → guard list incl. info/attributes; hardlink/nonregular → protected_fail
sed -n '1190,1245p' tools/souji-census.sh       → unverifiable→0; dirty>0 flags; no problem → clean (:1232-1239)
grep -n '28 uncarried\|pre-harm fails only' LOG.md → 902 ; 858
sed -n '40,60p' corpus/lessons/round-16.md      → :54 "resolved:" (no @rev)
grep -n 'CARRY_TOKEN_RE' -A12 tools/souji-landing-gate.py → :83 resolved@[0-9a-f]{7,}; :239-245 norm; :248-270 first word; :338 needle in nl
sed -n '766,774p' tools/souji-landing-gate.py   → all(i in ids ...) + opt-in forbid_ids
grep -n '"verdict"' tests/fixtures/r15-preservation-frozen/regenerate.py → :130 "verdict": "clean"
git cat-file -e c46eabf:census/round-16/gate-landing.json → present
git cat-file -e 6ff91f5:census/round-16/gate-landing.json → absent
git show c46eabf:census/round-16/gate-landing.json | jq -r '.resolved_rev' → 6ff91f534eece9ad…
jq '.summary' census/round-16/seat-audit-w1.json → seats 65, major 1, seats_with_major [SrcGitNoLazyFetch]
jq '.summary' census/round-16/seat-audit-w2.json → seats 79, major 3, minor 42
jq w2 major args → ".ufo/waves/round-16/w2/ConnReadmeIndex.md" ; "| 2 | stale pin | …" ; "N6 is the exact harm …"
find /var/tmp/souji-r16/transcripts/w1 -type f | wc -l → 65 ; w2 → 79
```

Verdict: **holds** as a criteria fit — 3 rows cover D1–D6, D7 is Q17's, no row
rewritten. It does not hold until the r17 lesson rows, the fixture/manifest
artifacts and the README range land with it; and Q29's manifest is not optional
given C2's counts (70/77 declared vs 65/79 retained and committed).
