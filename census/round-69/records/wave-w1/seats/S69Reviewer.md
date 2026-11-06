# Seat S69Reviewer — lane souji round 69 — counter diff (r68 -> r69) review — post-freeze falsification

## Verdict per review target (all grounded in my own run + committed bytes; the L1's after-arm receipts were read only after my runs)

diff scope: `git show 893b8ef:census/round-68/c1-counter.py` (1191 ln) vs `census/round-69/c1-counter.py` (1434 ln).
Counter bytes at tip == freeze-commit bytes: sha256 40757709e5adef00ef86c63fb4b554c03cce80e197747e389d76f58d4c2f5130
for both `1412037c:census/round-69/c1-counter.py` and the working file (verified). AST-verified both counters
(`py_compile`, `ast.parse`). No uncommitted change to census/round-69/c1-counter.py or the matrix (git status:
only `census/round-69/srcs/S-opening.txt` modified by another seat; ignored `__pycache__/` regenerated).

### W4 rebuild (copytree target) — SOUND
r68 counter built the poison at `dst = os.path.join(repo, "main")` (r68 file, common-dir-rel-poison branch):
a copy of `.git` INTO `<repo>/main`, so the relative caller value `main/.git` resolved against the parent cwd
actually names `<repo>/main/.git` — which did not exist as a git dir; r68 CAND.txt line (records/c1-after/CAND.txt)
shows `CASE W4 ... base=refuse ... new=refuse lane worktree is dirty` (base refuse = broken fixture, rev check).
r69 counter: `os.makedirs(os.path.join(repo,"main")); dst = os.path.join(repo,"main",".git")` (c1-counter.py:563-565),
plus `if not os.path.isdir(dst): raise CaseError` (line 568) and `main/` in info/exclude (line 558) — the
repo_name="main" fixture + cwd_parent semantics now make the caller value name the real common dir, matching the
comment. My candidate run (own scratch /fast/scratch/hyaku/souji-r69/S69Reviewer/review-deep/wYMgf): `CASE W4
expect=refuse base=accept base_findings=- new=refuse new_findings=lane worktree is dirty new_echo=false`,
SUMMARY `base_forgeries=3` (W1 W2 W4), `base_honest=11` — the preregistration predicate reproduces at the
landing tip.

### No-echo judge (echo_violation) — SOUND
`echo_violation()` (c1-counter.py:774-782) compares verbatim substring of the caller value (`env_extra[key]`)
in the new-slot stderr only; accept rows have empty stderr by construction. `case_env` for every noecho_env key
(N3/P13 -> GIT_INDEX_FILE, W1-W6 -> GIT_COMMON_DIR relative "main/.git" or absolute paths, W7 -> GIT_DIR) supplies
the value; selftest check (5) verifies key presence at debounce. D30 battery receipt from MY full battery run
(/fast/scratch/hyaku/souji-r69/S69Reviewer/review-deep/bfVe4/battery.out): `MUTANT D30 outcome=echo-violation
expected=echo-violation ... echo=2` — exactly the two noecho rows (N3 one run, P13 same run) print `new_echo=true`;
all 25 other runs show `new_echo=false` on N3/P13 (24 false + 1 accept each in K7's D-gate forgery rows).

### classify_outcome precedence — SOUND as built; one LOW finding
`classify_outcome` (c1-counter.py:988-1001) precedence error>forgery>echo-violation>over-refusal>label-only>
survived, matching the preregistration Q131 wording and the six selftest classifier assertions (all 6 pass in
my run). LOW finding: a run that is BOTH echo-violating AND forging is classified "forgery" — the echo evidence
is subsumed and its kill-collapse is invisible except via `outcome_counts` echo= column on the MUTANT line.
Not contradicted by the frozen predicate (precedence is frozen), but any future consumer reading only `outcome=`
will not see the echo. Tagged LOW (informational; frozen vocabulary order, not a defect vs prereg).

Also: `classify_outcome` counts `label` missing only class_ok flip for `refuse/refuse` (correct), and
`outcome_counts` agrees line-for-line with `classify_outcome`'s sum components — no divergence found.

### load_battery_manifest — SOUND
`load_battery_manifest` (c1-counter.py:1024-1042) header exactly `mutant<TAB>expected_outcome`, unique names,
outcome whitelist = the Q131 vocabulary plus survived/error. The 26-row battery-manifest.tsv is well formed;
all 26 of my battery outcome lines match their manifest expectation (`MUTANT <name> outcome=X expected=Y`:
0/26 mismatches verified line-by-line).

### battery branch in main() — SOUND
`--battery-manifest`/`--battery-dir` interlock (`if bool(ns.battery_manifest) != bool(ns.battery_dir)`
line ~1297); battery members are read as files under `--battery-dir/<name>.py`, missing member is a fatal
(line ~1345); work dir goes under `--work`; each member runs `evaluate(rows, base_slot, mpath, mwork, fixture)`.
BATTERY EXIT=0 iff all-match and no survived and no error — matches the preregistration counting command and my
observed BATTERY line (below). Battery arm never touches the lane tree (verified against --work residue:
`work/battery/<name>/{A..W7}/{base,new}` only; the lane git status above shows no noise).

### selftest additions (checks 4-6) — SOUND
(4) six classifier assertions all pass in my run. (5) noecho consistency passes for all noecho rows. (6) main()
on a two-row matrix emits header/# slot new/# matrix/SUMMARY matrix=2/EXIT and rc_line==rc — check passes
(rc=1 for the accept stub on refuse rows is correct). FULL selftest from my own run:
```
command: python3 -B census/round-69/c1-counter.py --selftest --root /home/vgpnk/Projects/shokunin/souji-shokunin --matrix census/round-69/c1-matrix.tsv --base-rev 3639087917eaeb28719d7603110a6ec22782100e --work <scratch>
output tail: SELFTEST cases=16 pass=16 fail=0
EXIT=0 (selftest subprocess exit code 0)
```
16 checks = 3 spec + 2 cli-disagreement + 3 stubs + 6 classifier + 1 noecho + 1 main-emit. Matches prereg.

### Five new fixture kinds (unmerged-index / gitlink-flag / absent-flag / fsmonitor-silent / git-dir-copy) — SOUND
Each builds only under its own `case_dir` (unmerged-index & gitlink-flag & absent-flag mutate only the fixture
repo; fsmonitor-silent writes the silent hook beside the repo at `os.path.dirname(repo)`; git-dir-copy writes
under `case_dir/gitdir-copy`; verified no cross-letter/which collisions: separate `base`/`new` subtrees per letter,
none collide. Comment vs build comparison (Q132 clause):
- unmerged-index builds exactly "two conflicting stages on tools/notes.txt via --index-info" (lines 579-599:
  hash-object -w --stdin x2, then update-index --index-info with 1 and 2 stages for the same path).
- gitlink-flag builds "160000 gitlink on tools/sub committed then skip-worktree" (lines 601-613).
- absent-flag builds "skip-worktree on tools/notes.txt whose worktree file is removed" (lines 615-620).
- fsmonitor-silent builds "repo config core.fsmonitor names a silent hook printing one timestamp line and no
  changed paths, and --fsmonitor-valid on the dirty entry" (lines 622-639); probe P3 evidence committed at
  census/round-69/probes/fsmonitor-hook-probe.txt.
- git-dir-copy builds "byte copy of .git beside the repo whose config sets core.fileMode=false and names the
  fixture repo as core.worktree" (lines 641-649).
Agree with their matrix rows' expected_class: U1=RECEIPT-INDEX-UNMERGED, G1=RECEIPT-GITLINK-CONCEALED,
A9=RECEIPT-INDEX-CONCEALED-ABSENT, F1=W-lane-dirty, W7=W-lane-dirty (c1-matrix.tsv lines 44-48).
All five new rows behave as comments promise in MY candidate run (u1/g1/a9/f1/w7 CASE lines above: base=refuse
and new=refuse with the exact frozen class on 4 of them, F1/W7 both 'lane worktree is dirty' as frozen
predicate states — no merge or shopwork issues found).

### clean_env preserved scrub tuple — SOUND
`clean_env` (c1-counter.py:319-340) has all r68 scrub keys (verified by assert over the extracted body:
GIT_DIR, GIT_WORK_TREE, GIT_INDEX_FILE, GIT_OBJECT_DIRECTORY, GIT_ALTERNATE_OBJECT_DIRECTORIES,
GIT_REPLACE_REF_BASE, GIT_CONFIG_COUNT, GIT_CONFIG_PARAMETERS, GIT_CONFIG_GLOBAL, GIT_CONFIG_NOSYSTEM,
GIT_CONFIG_SYSTEM, GIT_NO_REPLACE_OBJECTS, GIT_COMMON_DIR, GIT_NAMESPACE, GIT_CEILING_DIRECTORIES,
plus GIT_CONFIG_KEY_/VALUE_ and GIT_TRACE* prefixes and `e["GIT_OPTIONAL_LOCKS"]="0"` — exactly the r68 tuple
plus the new HOME/XDG_CONFIG_HOME/GIT_TRACE* scrub). Also `e["GIT_CONFIG_GLOBAL"]=os.devnull` and
`e["GIT_CONFIG_NOSYSTEM"]="1"` devnull pins are new (not in r68's clean_env; they are the C2 addition whose
ambient immutability is the C2 claim). EXTRA event env vars scrubbed: also `GIT_TRACE2_EVENT`, `GIT_TRACE2_PERF`
are consumed by the r69 predicate — verified as r68 additions not present in r68 clean_env but present in r69;
this is the intended behavior round.

### My own full battery run (frozen invocations, no DO-NOTHING receipt — my seat didn't get one; falsification via the frozen candidate + battery calls only)
```
battery cmd: python3 -B census/round-69/c1-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --matrix census/round-69/c1-matrix.tsv --base-rev 3639087917eaeb28719d7603110a6ec22782100e --work <scratch>/work --battery-manifest census/round-69/battery-manifest.tsv --battery-dir census/round-69/battery
observed: BATTERY mutants=26 kills=18 label_only=5 over_refusal=2 echo_violation=1 survived=0 error=0
EXIT=0
```
Per-mutant observed==expected on 26/26 (no attack).

### Screened precedences (approved, no defect)
`classify_outcome`'s swap of outcome-precedence vs one_line(160) truncation of `# detail` lines (160-char loss
for the K1 / NCABS / M-CD-ROOTREL runnable mutant W4 detail lines is by DESIGN of one_line(text, 160), 26 lines
at 268 chars max = the three W4 rows whose stderr is >160 get '...' — everything is present in the in-memory
`res.detail` list; nothing lost). No defect.

### Before-arm crosschecks performed
* r68 records: `grep -rc '^MUTANT \|^BATTERY ' census/round-68/records/c1-after/` = 0 total (my own run).
* r68 CAND.txt W4: `CASE W4 expect=refuse base=refuse ...` (base refusal) — the r68 predicate as stated.
* r68 counter has no `--battery-manifest` arg (verified: `grep -n `battery`` on r68.py returns nothing) — so
  "before arm has no MUTANT/BATTERY outcome lines" is structurally true, not only empirically.
* Frozen-base r68 counter's clean_env DOES contain `e["GIT_OPTIONAL_LOCKS"]="0"` (verified body_old.py line 211
  and body_new.py line 238) — the L1 pin survives into r69 counter's writer calls (my assertion, byte-verified).

## Findings
1. LOW (informational; no defect vs frozen predicate): classify_outcome collapses echo-violation into
   forgery when a row is both. The echo evidence stays visible in outcome_counts echo= column; frozen
   precedence is honored. c1-counter.py:988-1001 + 1012-1022.
2. LOW (observability): 26 battery runs emit 47 CASE rows each; `# detail` lines are one_line(160)-truncated
   which is fine, but the `--work` residue directory (per-case fixture trees) is not deleted at END of battery,
   leaving 26 × ~40 fixtures under scratch; acceptable for audit (they ARE the evidence for W4-rebuild checking),
   but worth knowing before disk budget planning.

## Files written under my seat directory (round-69/w1/)
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-69/w1/S69Reviewer.md  (this report)
No other tracked-file writes. No mutation of the lane. No mutation of the freeze, matrix, counter,
battery, or controls. Carried pins cross-checked: base writer scrub tuple (GIT_DIR/GIT_WORK_TREE only —
GIT_COMMON_DIR unscrubbed = W1/W2/W4 base forgeries expected; candidate has scrub+check = refused).

## Scratch
/fast/scratch/hyaku/souji-r69/S69Reviewer/{r68.py, hunks.lean.txt, body_old.py, body_new.py, body.ctx.diff,
review-deep/{wYMgf (candidate run + cand.out), bfVe4 (battery run + battery.out), wcLZF (aborted first attempt)},
base-writer.py, cand.scratch.txt, report/}. Disk-guard precheck: /fast/scratch/hyaku 53% used, 381.4G free.

No HIGH or MEDIUM findings. Verdicts sound on every review axis assigned. No frozen number I re-derived
diverges from my own run's observation.
