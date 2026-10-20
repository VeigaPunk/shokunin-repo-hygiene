STATUS: DONE — the decision to keep census `unpushed` branch-based holds; a separate keep-only column fails on four structural harms; disclosure belongs in the tool header, not a new field.

# ConnCensusJjColumns — should the census `unpushed` column change for jj lanes?

Seat: connector (leaf, advisory) · 2026-10-20 · lane `souji-shokunin` · base `5fa6017ddcae9f6bd4412df44765f6360cb16294` · census bytes `64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c` (identical at `5fa6017` and in the worktree at read time).

Question put to this seat: the round-17 context leaves the census `unpushed` column branch-based in jj repos ("disclosed, not changed"). Is that right? Would a separate informational column (keep-only commit count) harm live-fleet preservation, given that rows change for every jj lane?

**Verdicts.** (V1) keeping `unpushed` branch-based: **holds**. (V2) adding a keep-only informational column to the census TSV: **fails** — it harms operability, calibration and the verification instruments for a nominal coverage gain. (V3) the disclosure as currently placed: **partial** — true in corpus, absent from the instrument that emits the number.

---

## 1. What the column actually is (census `5fa6017`)

| anchor | line | text |
|---|---|---|
| column list | `tools/souji-census.sh:24` | `repo  worktrees  unpushed  dirty  scratch_bytes  mtime_iso  verdict_flags` |
| semantics | `:29-33` | `unpushed  commits on any local branch not reachable from any remote-tracking ref (git rev-list --count --branches --not --remotes)` |
| counter | `:921-934` | `count_unpushed`; no-remote arm `rev-list --count --branches` (:927), has-remote arm `rev-list --count --branches --not --remotes` (:931) |
| verdict coupling | `:1236`, `:1244` | `has_problem=1` for `unpushed`; `clean` only when that flag set is empty |
| row emission | `:1252-1254` | one `printf` of exactly seven tab-separated fields |
| header constant | `:170` | `HEADER=$'repo\tworktrees\tunpushed\tdirty\tscratch_bytes\tmtime_iso\tverdict_flags'` |
| help text | `:182-185` | `usage()` prints every leading `#` line of the script via `awk` — the header block **is** the `--help` contract |

The column answers one question exactly: *is there commit work on a local branch that no remote-tracking ref contains?* It is not a claim about commits that only jj holds, and it was never a claim about reachability for garbage collection.

## 2. Measured state of the jj lanes (read-only git; no census run)

| repo | `.jj` | keep refs | keep-only commits¹ | keep-only with deletions² | branch `unpushed` (census form) |
|---|---|---:|---:|---:|---:|
| `souji-shokunin` | yes | 8 | **6** | **4** (2 paths each) | 0 |
| `kama-shokunin` | yes | 22 | 10 | — | 0 |
| `mado-shokunin` | yes | 39 | 23 | — | 0 |
| `tameshi-shokunin` | yes | 27 | 13 | — | 0 |
| `chousa-shokunin` (plain control) | no | 0 | 0 | — | 0 |

¹ `git rev-list --count --glob='refs/jj/keep/*' --not --branches --remotes` (one `--not`; see §5).
² `git diff-tree -r --no-commit-id --diff-filter=D --name-only <sha>` per keep-only commit.

The context's figure — "6 keep-only commits in this lane, 4 with phantom deletions" — reproduces exactly. The four commits delete the same two paths, and both still exist in HEAD:

```text
0254661 deletions: tests/vault/vadv54-run/p/p6repo/inner/keep.txt[in-HEAD] tests/vault/vadv54-run/p/p6repo/one.txt[in-HEAD]
1e0d8d1 deletions: ...same two paths...
719154d deletions: ...same two paths...
41ab059 deletions: ...same two paths...
dcc1512 deleted=0
dd2e322 deleted=0
```

Those are the nested-empty-`.git` phantom deletions recorded in `corpus/knowledge/jj-colocation-receipts.md` §7 (`JjTrialSouji.md:76`, commit `c31a345`). All six are *superseded rewrites*, not work awaiting a push: `HEAD = master = origin/master = 5fa6017`, and `git rev-list --count --branches --not --remotes` is 0 on all four lanes.

## 3. V1 — keeping `unpushed` branch-based: holds

Four independent reasons, each observable:

1. **Predicate mismatch.** `unpushed` is a branch inventory (`:29-33`). Keep refs answer a durability question — *can this commit be collected?* — which round-17 C3(a)/(b) already routes to `souji-verify.sh`, `souji-vault-verify.sh` and `souji-quarantine.sh`, where refusing is conservative and correct. One column cannot answer both; folding keep refs in makes `unpushed` mean "branch work OR collectible commit", which is neither question.
2. **The population is dominated by rewrites.** 4 of this lane's 6 keep-only commits contain deletions of tracked files that are *present on disk* (§2). Counting them would report **6 unpushed commits on a fully pushed lane**. That is the same false-positive class round 17's C2 is removing from the seat audit — a lane would be shipping one FP class while claiming to remove another.
3. **It destroys the clean signal fleet-wide.** `clean` requires `unpushed=0` (`:1236`, `:1244`). Today every jj lane has branch `unpushed` 0; keep-only is 6/10/23/13. Folded in, no jj lane can ever be `clean`; `kama-shokunin`'s live `clean` row (`census/round-16/live-fleet-final.json`, changed arm) flips, and `mado`'s already-nonzero row (`unpushed=8`) would add today's 23 keep-only commits on top.
4. **The number is volatile by construction.** jj keep refs are GC grace pins, not lane state: 15 after one commit cycle (`JjTrialSouji.md:61`), 7/12/21 at audit (`JjAuditSouji.md` F2), 22/39/27 today. A `--compare` diff (`:1443-1466`) would then report hygiene drift caused by jj's internal pinning, not by the lane's tree — corrupting the instrument that exists to detect real drift.

The safety dependency matters: "disclose" is sound **because** C3(b) lands the keep-rooted refusal in the receipt tools. If that claim fails verification, the census's branch-only column becomes the only fleet-wide surface and its blind spot (an unbookmarked `jj commit` reads `unpushed=0`) turns material. Tripwire: if C3(a)/(b) does not verify, reopen this disposition.

## 4. V2 — a separate informational keep-only column: fails

The question asks whether rows changing for every jj lane is the harm. Row churn alone is not: rows already move as lanes advance (`mado` read `unpushed=8` at r16 and 0 now). The harm is that the column would break the instruments that *prove* preservation and *detect* regressions, and would inject a semantically ambiguous number into a field consumers diff.

| # | harm | evidence |
|---|---|---|
| H1 | **One header for all rows.** The census has a single `HEADER` (`:170`) and one 7-field `printf` (`:1252`). A keep-only column cannot be emitted only for jj repos: every row widens, including the 17 plain repos. That contradicts C3(b)'s "plain repos must behave byte-identically" and changes the serialization of all 21 live-fleet rows, not just jj lanes. |
| H2 | **Cross-arm oracle collapse.** The C1 matrix runs *the same current fixtures* against every arm (`census/round-16/run-matrix.py:5-9`, `suite()`). Both fixtures hard-code the schema: `HEADER` literal (`tests/fixtures/r15-census-config.py:123`, `r14-census-boundary.py:42`), header `startswith` (`r15:928,:1067`; `r14:511`), exact width `len(fields) != 7` (`r15:940`; `r14:519`), positional `fields[2]` (`r15:945`; `r14:524`). A changed arm emitting 8 columns makes `pre-harm`/`r14-harm`/`r15-baseline` fail *"row has 7 columns, want 8"* on every case — indistinguishable from the `b410186` collapse the round exists to avoid. The only alternative is a dual-schema oracle, which weakens the exact comparisons that currently separate 16/20 harm from preservation. |
| H3 | **`--compare` baseline break.** `load_census` hard-errors on header mismatch (`:1365`, `:1390`) and on `tabs -ne 6` (`:1373`), and `--compare` maps exactly six fields by position (`names=(...)` at `:1443`, loop `1..6` at `:1459`). After a schema change the tool cannot read any pre-round census TSV, and an appended field would be folded into `verdict_flags` by the 6th-of-6 `rest` rule in any path not updated — a silent corruption, not just an error. |
| H4 | **Live-fleet preservation becomes unprovable.** The r16 preservation evidence is row-identical across tool revisions over the same fleet at the same moment: `rows_identical_excluding_mtime: true`, 21 rows per arm, `rc=0`, `stderr_lines=0` (`census/round-16/live-fleet-final.json`). A schema change makes every row differ *by construction*; the check would report "preservation lost" for a tool that preserved every semantic. The comparator would have to become schema-aware before the evidence could be used again. |

Additional costs: `st_row_field` hard-codes `-le 7` (`:1515`) and the selftest asserts column indices 2–7 (`:1645-1710`); every stored baseline acquires a schema-version problem; and the number itself is ambiguous — it merges superseded rewrites (4/6 here) with unbookmarked working-copy commits, so it answers neither "what needs pushing" nor "what could be lost". Its magnitude (6/10/23/13 against 0 branch work) would be read by any operator as commits to push, manufacturing the exact misreading the disclosure exists to prevent.

**Axis accounting for the column move:** operability − (clean flips for jj lanes, new field, baseline break), calibration − (counts phantom-deletion rewrites as work, same FP class as D4), verification − (H2/H4), coverage + nominal only (ambiguous number), depth 0, freshness 0, adjacency 0. It fails "improve one axis, harm none".

## 5. Non-obvious trap if a keep-only number is ever computed

`--not A --not B` is **not** two exclusions: the second `--not` flips the sense back, so `X --not --branches --not --remotes` means *X plus remote refs, minus branches*. Measured:

```text
chousa (HEAD = master = origin/master):
  rev-list --count HEAD --not --branches --not --remotes          -> 8
  rev-list --count --remotes --not --branches                     -> 8   (origin/cursor/*, origin/devin/* only)
  rev-list --count HEAD --branches --not --remotes                -> 0
kama:
  rev-list --count --glob='refs/jj/keep/*' --not --branches --not --remotes -> 18
  rev-list --count --glob='refs/jj/keep/*' --not --branches --remotes       -> 10
kama remote-only commits: 8  (18 - 10, exactly)
```

So the correct keep-only primitive is one `--not --branches --remotes`: 10/23/13/6 today, 0 on the plain control. The shorthand quoted in `JjAuditSouji.md` F2 (`--all --not --branches --not --remotes`) overcounts as soon as a lane carries remote-only branch refs (it gives 18/31/21 today). The audit's older figures are consistent with correct-at-the-time counts; this is a caution for any future implementation, not a claim of error there.

## 6. V3 — the disclosure is right, its placement is partial

`corpus/knowledge/jj-colocation-receipts.md` §4 already states the exact limitation ("The lane's census `unpushed` column is branch-based and will read 0 here … That is disclosed, not a fix"), and operating rule 5 states the conservative receipt check. That is the durable corpus half.

What is missing is the instrument half: the census's own bytes at `5fa6017` and in the worktree contain no `jj`/keep reference (`grep -n 'jj|keep'` returns only unrelated "keeps"/"keep the" prose at `:579`, `:727`). `usage()` prints the leading comment block (`:182-185`), so `--help` — the surface an operator actually reads before trusting `clean` — carries no warning that `unpushed=0` is not a completeness statement in a colocated lane.

**Smallest fix (advisory, behaviour-free):** add 3–4 comment lines to the header block next to `:29-33`, e.g.:

```
#   In a jj-colocated repo this column is branch inventory only: commits
#   held solely by refs/jj/keep/* (rewritten predecessors, or an
#   unbookmarked working-copy commit) are NOT counted and HEAD is not a
#   root. A receipt must refuse such a commit; see
#   corpus/knowledge/jj-colocation-receipts.md §3-§4.
```

Zero output bytes change: stdout, row width, header constant, `--compare`, every fixture assertion, every matrix arm and every live-fleet row are untouched. It does change the script digest (already changing this round for D1/D2) and the `--help` text, which no fixture asserts.

**Optional, gated (wave 2/next round, not silently in wave 1):** if a live signal is wanted, emit one conditional stderr line only when `.jj` exists and keep-only > 0 — `souji-census: jj-keep-only <repo> <n>` — using the §5 single-`--not` primitive. It matches the D2 stderr-diagnostic pattern, leaves rows and headers untouched, and cannot fire in fixtures (neither fixture creates `.jj`; `grep -n '\.jj'` over both returns none), so the cross-arm oracle stays byte-identical. Cost: `live-fleet-final.json`'s `stderr_lines=0` would become 4 on a jj fleet, a disclosed evidence change, and honesty requires a fixture case (plain repo: no line; jj repo: exact line). That is a real fixture addition, so it belongs to a declared claim, not an advisory add-on.

## 7. Second-order effects (why the header fix is free and the column is not)

| surface | header comment (recommended) | keep-only column (rejected) |
|---|---|---|
| runtime | none | +1 `for-each-ref` +1 `rev-list` per jj repo (negligible) |
| output contract | unchanged; digest/`--help` only | header+width change for all 21 rows; schema version needed |
| fixtures | untouched | `len(fields)!=7`/`HEADER` fail on every old arm (H2) |
| `--compare` | untouched | cannot read pre-round baselines (`:1365,:1373`) |
| live-fleet proof | untouched | row-identity proof fails by construction (H4) |
| verdicts | unchanged | every jj lane loses `clean`; kama flips today |
| semantics | predicate distinction documented where read | ambiguous, volatile number read as "to push" |

## 8. Recommendation (advisory)

1. **Uphold "disclose, not change" for the `unpushed` column.** Do not add keep refs to the count and do not add HEAD: HEAD-rooted `rev-list --count HEAD --branches --not --remotes` is 0 on all four jj lanes today, but jj working-copy commits sit at HEAD, so a `jj new`/`describe` empty commit would add a false unpushed+1 — trading a disclosed blind spot for an undocumented false positive.
2. **Do not add a keep-only column to the census TSV**, this round or as an "informational" eighth field. It fails H1–H4 and the axis test in §4.
3. **Move the disclosure to the instrument:** the header block at `:29-33` (printed by `--help` via `:182-185`), as in §6. This is the one bounded move that improves coverage/depth at zero measured harm and keeps C3's plain-repo byte-identity intact.
4. **Defer the stderr diagnostic** to a declared claim with its own fixture cases and four-arm run; do not fold it into wave 1.
5. **Tripwire:** if round-17 C3(a)/(b) does not verify (keep-rooted refusal not landed in verify/vault/quarantine), reopen §3's soundness argument — the census blind spot would then be the fleet's only surface.

## 9. Commands run (exact) and outputs

All git commands were read-only and ran against named repos/paths. No census, verify, vault-verify or quarantine tool was executed; no `jj` subcommand was run; no file was written outside this report.

```text
git show 5fa6017:tools/souji-census.sh | grep -n 'unpushed' etc.        -> anchors in §1
git show 5fa6017:tools/souji-census.sh | sed -n '880,960p'             -> count_unpushed :921-934
git show 5fa6017:tools/souji-census.sh | sed -n '1330,1382p'           -> load_census :1365,:1373,:1390
git show 5fa6017:tools/souji-census.sh | sed -n '1440,1470p'           -> names :1443, loop :1459
git show 5fa6017:tools/souji-census.sh | sed -n '1500,1520p'           -> st_row_field -le 7 :1515
git show 5fa6017:tools/souji-census.sh | sed -n '/^usage()/,/^}/p'     -> awk prints leading # block
git show 5fa6017:tools/souji-census.sh | sha256sum                     -> 64a60fd0b0ed...7fe8d07c
sha256sum tools/souji-census.sh                                        -> 64a60fd0b0ed...7fe8d07c (worktree equal)

cd souji-shokunin
git rev-parse HEAD; git symbolic-ref -q HEAD                           -> 5fa6017...; DETACHED
git rev-parse master origin/master                                     -> 5fa6017... / 5fa6017...
git for-each-ref --format='%(refname)' refs/jj/keep | wc -l            -> 8
git rev-list --count --branches --not --remotes                        -> 0
git rev-list --count --glob='refs/jj/keep/*' --not --branches --remotes -> 6
git log --format='%h %s' --glob='refs/jj/keep/*' --not --branches --remotes
                                                                       -> 0254661 1e0d8d1 719154d 41ab059 dcc1512 dd2e322
git for-each-ref --contains <sha> --format='%(refname)' refs/jj/keep   -> 1 each
git diff-tree -r --no-commit-id --diff-filter=D --name-only <sha>      -> 2,2,2,2,0,0; both paths present in HEAD

for kama/mado/tameshi:
  keep refs                                                           -> 22 / 39 / 27
  rev-list --count --glob='refs/jj/keep/*' --not --branches --remotes -> 10 / 23 / 13
  rev-list --count --branches --not --remotes                         -> 0 / 0 / 0
  rev-list --count --remotes --not --branches                         -> 8 (kama)
  keep with double --not                                              -> 18 / 31 / 21
chousa (plain): .jj absent, keep 0, keep-only 0, remote-only 8, branch 0
HEAD == master == origin/master on souji/kama/mado/tameshi/chousa

grep -n 'HEADER|startswith(HEADER|row has |unpushed=' tests/fixtures/{r15-census-config,r14-census-boundary}.py
  -> r15:123,:928,:940,:945,:1067 ; r14:42,:511,:519,:524,:527
grep -n 'stderr|\.jj' tests/fixtures/{r15-census-config,r14-census-boundary}.py
  -> no .jj anywhere; stderr assertions are presence-of-diagnostic only
grep -n 'jj|keep' tools/souji-census.sh                                -> only :579 "keeps", :727 "keep the"
python3 -c 'json.load(census/round-16/live-fleet-final.json)'          -> 21 rows/arm; rows_identical_excluding_mtime=true;
                                                                          stderr_lines=0; r14-harm cc21683 vs changed 0a70bef
ls tests/fixtures/r17-census-hygiene.py                                -> No such file or directory (wave-1 build not yet landed)
```

## 10. Probe disclosure

Outside the enumerated allowlist, read-only, no writes: one `git -C chousa-shokunin --no-optional-locks status --porcelain | wc -l` (diagnostic only, output `0`; it does not support any finding above), and `git diff-tree -r` (plumbing adjacent to the allowed `git diff`/`git show`, records the keep-only deletion counts in §2). Directory listings of `census/round-16/` and `.ufo/waves/round-17/w1/` were read via `ls`. No `jj` invocation, no index or ref write, no tool install or upgrade in this seat.

## 11. Files read (evidence)

- `tools/souji-census.sh` at `5fa6017` (via `git show`) and in the worktree
- `tests/fixtures/r15-census-config.py`, `tests/fixtures/r14-census-boundary.py`
- `census/round-16/run-matrix.py`, `census/round-16/live-fleet-final.json`
- `SKILL.md:168-178`, `corpus/knowledge/jj-colocation-receipts.md` (§§1-11, operating rules, limits)
- `corpus/lessons/round-16-verifier-spotcheck.md`
- `.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md`, `JjTrialSouji.md`
