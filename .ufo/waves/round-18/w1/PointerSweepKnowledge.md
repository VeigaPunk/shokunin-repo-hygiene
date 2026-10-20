STATUS: DONE — blind token sweep of `corpus/SOURCES.md` + the seven `corpus/knowledge/*.md` at b576341 finds exactly one dangling pointer family (`census/round-17/jj-receipts-ddb7347.txt`, 4 citations, never committed, intended file proven to be `…-4f48343.txt`); everything else unresolved is fleet-relative, deliberate, or a grammar false positive. C2's "281 tokens / 18 unresolved" count does not reproduce under any grammar I can state; the unresolved *set* does.

# Scope and rev

- Rev: `b5763415cc67ecff1e8fe56c58c39a6fb106d7a3` (base of round 18). Tree: `git ls-tree -r --name-only b576341` → 2246 entries.
- Files swept (8): `corpus/SOURCES.md` and every `corpus/knowledge/*.md` in the tree (dupe-finders-detect-then-act, git-auto-maintenance-prunes-worktrees, git-grace-periods-and-expire-to, git-repo-structure-readonly, jj-colocation-receipts, quarantine-same-filesystem-rename, trash-spec-restorable-quarantine). `corpus/knowledge/obsidian-ledger.tsv` excluded: not `.md`, and not an authority document.
- All reads via `git -C <lane> show b576341:<path>` / `ls-tree` / `rev-list --all --objects` / `log --all --name-status` / `cat-file -p` / `grep <rev>`. No file in any repo was written except this report.

# Grammar used

Token = `((census|tests|tools|corpus|\.ufo|\.github|scripts)/[^\s\`'"()\[\]|;]+)` or a bare `[A-Z][A-Z0-9_]*.{md,json,tsv,sh,py,txt,yml,yaml}`. Then:

1. strip trailing `.,:`; strip a trailing line ref `:N`, `:N-M`, or `:N,M,…`;
2. split colon-joined path lists (`--specs a.json:b.json`) on `:`; expand `{a,b}` and `{d..d}` (zero-padding preserved);
3. resolve if the path equals a tree entry **or is a directory prefix of one**;
4. skip (per C2) tokens containing `<`, `>`, `*`, or literal `round-N`; also skip unbalanced `{`.

Rules 1–4 are not decoration: every one is forced by text in the authority files (see F5). A gate that omits any of them emits false findings.

# Counts (independently re-derived)

| set | path-like occurrences | under governed prefixes | resolved (occ / distinct) | unresolved (occ / distinct) | skipped by rule 4 |
|---|---|---|---|---|---|
| my 8 files | 123 | 101 | 95 / 43 | **6 / 5** | 0 |
| full C2 authority set (15 files: SKILL, SCORECARD, PROVINCE, corpus/QUALITY, corpus/README, SOURCES, lessons/round-17, LOG, 7 knowledge) | 552 | 477 | 444 / 179 | **20 / 12** | 13 |

In my 8 files all 6 unresolved occurrences belong to 3 paths; 4 of the 6 occurrences are the same one dangling file.

The unresolved columns count only tokens under the governed prefixes. Path-like tokens outside them are not gate candidates: `scripts/hyaku/jj-lane.sh` (fleet-only), and the bare `README.md`/`CHANGELOG.md`/`SC2115.md`/`QUALITY.md` names, all of which resolve or are external/bare references (classified in the table below).

`git log --all --name-status -- 'census/round-17/*'` shows only `A`/`M` records (zero `D`): `git log --all --diff-filter=D --name-status -- 'census/round-17/*'` is empty. No `*-ddb7347.*` file has ever been added or deleted.

# F1 — HIGH (calibration): `census/round-17/jj-receipts-ddb7347.txt` is dangling, never existed in any commit

Citations (all in `corpus/knowledge/jj-colocation-receipts.md`, nothing in SOURCES):

- `:2` verified-at: "In-lane fixture `tests/fixtures/r17-jj-receipts.sh` run at landed revision ddb7347 (`census/round-17/jj-receipts-ddb7347.txt`) …"
- `:44` "… It returns `NOT-SAFE` at ddb7347 (`census/round-17/jj-receipts-ddb7347.txt`)."
- `:126` "Landed at ddb7347: `NOT-SAFE` for all of these (`census/round-17/jj-receipts-ddb7347.txt:18-19, 22-24, 31-32`)."
- `:148` "… fixture outputs `census/round-17/jj-receipts-{base5fa6017,ddb7347}.txt`."

Existence checks (all negative):

```
$ git -C <lane> stat -c '%F %n' census/round-17/jj-receipts-ddb7347.txt
stat: cannot stat '…/census/round-17/jj-receipts-ddb7347.txt': No such file or directory
$ git -C <lane> rev-list --all --objects | grep ddb7347
ddb73474433977ff54b015ac3e77669ff2537353        # the commit object, and nothing else
$ git -C <lane> log --all --format=%h --name-status -- '*ddb7347*'
(none)
$ stat /home/vgpnk/Projects/shokunin/census/round-17/jj-receipts-ddb7347.txt
No such file or directory          # not in the fleet root either
```

`census/round-17/` tree at b576341: `c1-matrix-4f48343.json, c1-matrix.json, gate-landing.json, gate-replays-4f48343.json, gate-replays-expected.json, gate-replays.py, jj-receipts-4f48343.txt, jj-receipts-base5fa6017.txt, live-fleet.json, run-matrix.py, seat-audit-r16-replay-4f48343.json, seat-audit-r16-replay-base5fa6017.json, seat-audit-replay.py, transcript-manifest.py`. No `*-ddb7347.*` file has ever been added or deleted: `git log --all --name-status -- 'census/round-17/*'` shows only `A` records (the `4f48343`/`base5fa6017` records at 95519a7, a6cac8e, c21f255; the gate files at ddb7347, 0a21361, be4e630, e30ceec) and `M` records for `census/round-17/seat-audit-replay.py`; zero `D` records.

## The file it most likely meant: `census/round-17/jj-receipts-4f48343.txt`

Two independent proofs, both against committed bytes:

1. **Line numbers match exactly.** `git show b576341:census/round-17/jj-receipts-4f48343.txt | grep -nE '^CASE\t(J1|J1-vault|J3|J3-vault|J3-quarantine|J9-file|J9-worktree)\b'`:
   - `18:CASE J1 PASS … verdict=NOT-SAFE`, `19:CASE J1-vault PASS … verdict=NOT-SAFE`
   - `22:CASE J3 PASS … verdict=NOT-SAFE`, `23:CASE J3-vault PASS`, `24:CASE J3-quarantine PASS exit=3 result=DRY-RUN-BLOCKED`
   - `31:CASE J9-file PASS … verdict=NOT-SAFE`, `32:CASE J9-worktree PASS … verdict=NOT-SAFE`
   These are exactly the `:18-19, 22-24, 31-32` ranges the entry cites. The base file's `:15-16, 19-21, 28-29` also match its citations exactly, so the entry's line refs were copied from committed records.
2. **Tool digests match 4f48343, not ddb7347.** The record header lists `tools/souji-verify.sh sha256=f88fed23…`, `souji-vault-verify.sh sha256=5cb0fb13…`, `souji-quarantine.sh sha256=83cc3ce1…`. Blob hashes by rev:
   ```
   5fa6017  verify=9adb17645a5f  vault=f9e778ca478c  quar=df4075112c36   # = base5fa6017 record
   ddb7347  verify=92743004912a  vault=bbca35a142cb  quar=24c7cf059f23
   4f48343  verify=f88fed23e2c8  vault=5cb0fb13fc9b  quar=83cc3ce1331b   # = jj-receipts-4f48343 record
   b576341  verify=f88fed23e2c8  vault=5cb0fb13fc9b  quar=83cc3ce1331b
   ```
   The file-name convention is therefore the *tool state* (`base5fa6017` really is the 5fa6017-tool run), so `jj-receipts-ddb7347.txt` would denote a ddb7347-tool run — which was never committed. The committed 4f48343 record is a 35-case run (`SUMMARY total=35 failed=0 skipped=0`, 54 lines), and its J1/J3/J9 rows are the ones the entry quotes.

## Why the name survived in prose

The ddb7347-state records existed only as **untracked working-tree artifacts** during wave 2. Committed wave-2 reports say so:

- `.ufo/waves/round-17/w2/RevReplayBinding.md:7-11`: "the records are not committed"; `git show ddb7347:census/round-17/seat-audit-r16-replay-base5fa6017.json` → absent; `git status --porcelain` shows `?? …-ddb7347.json` etc.
- `.ufo/waves/round-17/w2/ScribeReportSections.md:79`: lists `jj-receipts-*.txt` and `gate-replays-ddb7347.json` among artifacts that are "untracked; none exis[t]" at the commit.
- `.ufo/waves/round-17/w2/ScribeLessonDraft.md:139`: `glob census/round-17/*` output shows `jj-receipts-ddb7347.txt` on disk in that workspace.

So the entry cites a workspace artifact as if it were a committed path, and the artifact was later regenerated at the wave-2 tip 4f48343 and committed under that name.

**Verdict: holds (dangling).** Smallest fix: in `jj-colocation-receipts.md` replace the four path citations with `census/round-17/jj-receipts-4f48343.txt`, and reword `:2` "run at landed revision ddb7347" / `:126` "Landed at ddb7347" to say the record was taken at the wave-2 tip `4f48343` (the behaviour still landed at ddb7347; the record is not a ddb7347-state run). Regenerating and committing a true ddb7347-tool record is the alternative, but then every quoted line number must be re-derived — they currently belong to the 4f48343 record.

# F2 — no finding, fleet-relative confirmed: `.ufo/waves/hyaku/jj-w1/reports/`

`jj-colocation-receipts.md:148`. Lane path absent; fleet path present:
`stat /home/vgpnk/Projects/shokunin/.ufo/waves/hyaku/jj-w1/reports` → `directory`; the cited fleet file `JjTrialSouji.md:76` carries exactly the nested-`.git` claim the entry uses. C2's `fleet` class covers it; it is not a finding. Same class: `scripts/hyaku/jj-lane.sh` (knowledge `:67,74,108`) exists only at the fleet root; note it is *outside* C2's governed prefixes (`scripts/`), so a gate with the stated prefix set will not sweep it at all.

# F3 — no finding, grammar only: `.ufo/waves/round-17/w2/ReopenS0NN.md`

`SOURCES.md:11`. `S0NN` is a numeric placeholder: 13 concrete files `ReopenS051.md … ReopenS063.md` are **committed** at b576341 in that same directory (`git ls-tree -r --name-only b576341 .ufo/waves/round-17/w2/ | grep -c Reopen` → `13`). Only the literal placeholder name does not resolve. Class: grammar (`S0NN` is not covered by the literal `round-N` skip; no `deliberate` claim is needed because the concrete bytes exist). A gate that does not skip `S0NN` will emit a false finding. Fix: skip tokens containing `S0NN`/`NN`, or have the source write `ReopenS0{51..63}.md`.

# F4 — calibration: C2's "281 tokens, 18 unresolved" does not reproduce

Over the same 15-file authority set C2 names (the round's lesson is `corpus/lessons/round-17.md`; no round-18 lesson exists at b576341), my grammar yields **552 path-like occurrences, 477 under the governed prefixes, 444 resolved occurrences (179 distinct), 20 unresolved occurrences (12 distinct tokens), 13 skipped** — not 281/18. The *unresolved set* is stable and small; the *count* depends entirely on tokenisation choices that the C2 contract does not pin (occurrence vs distinct; directory prefixes; line-ref forms; `*`/`<` capture; brace lists; bare-root names). Consequences for the claim "changed gate `--rev b576341 --round 18` findings before → 0":

- The gate must print its own token census, e.g. `TOKENS total=N governed=N resolved=N skipped=<by-reason> unresolved=N`, and the round evidence must pin that output. Otherwise the "before → 0" claim is not independently re-derivable and a verifier will reject it exactly as I could not reproduce 281/18.
- The dangling set that matters is stable: `census/round-17/gate-replays-ddb7347.json` (3 citations: `LOG.md:916`, `SKILL.md:163`, `SKILL.md:165`) and `census/round-17/jj-receipts-ddb7347.txt` (4 citations, F1). Both are the wave-2 untracked names; the committed records are `gate-replays-4f48343.json` (its `lane_head` and `gate.gate_rev_arg` are `4f4834390ad4…`, and it contains zero occurrences of `ddb7347`) and `jj-receipts-4f48343.txt`. `gate-replays-ddb7347.json` likewise never existed in any commit: `git rev-list --all --objects | grep gate-replays` → only `gate-replays-4f48343.json`, `gate-replays-expected.json`, `gate-replays.py`.

**Verdict: partial** — the finding set reproduces, the advertised counts do not.

# F5 — gate grammar hazards found in actual corpus text (each would be a false finding)

1. **`*`/`<`/`>` must be captured before the skip test.** If capture stops at those chars, prefix fragments survive the skip rule:
   - `SCORECARD.md:45` `census/round-14/verification*.json` → fragment `census/round-14/verification` (file exists as `verification.json`, but the fragment is not a path);
   - `corpus/QUALITY.md:37` `census/round-<N>/` → fragment `census/round-`;
   - `LOG.md:145` `census/round-3/{seat-01..64.json, approvals-*.tsv,` → fragment `census/round-3/{seat-01..64.json`.
2. **Line-ref forms beyond `:N`:** trailing colon (`census/round-12/scout-surfaces.md:94:` — a sentence opener in `quarantine-same-filesystem-rename.md:44`, and parenthesized at `trash-spec-restorable-quarantine.md:34`), comma lists (`census/round-16/transcripts/w2/ConnReadmeIndex.txt:167,180,185`), ranges (`:18-19`). A naive `:\d+$` strip leaves the first and second unresolved.
3. **Colon-joined path lists** (CLI arguments): `.ufo/waves/round-16/w1-spec.json:.ufo/waves/round-16/w2-spec.json` (SKILL/LOG `--specs` examples) must split on `:`, not be read as a line ref.
4. **Directory tokens must resolve by tree prefix:** `census/round-16/transcripts`, `tests/fixtures/r15-preservation-frozen/`, `tests/vault/vadv54-run` (29 committed files at b576341). Exact-membership-only resolution false-flags these.
5. **Braces:** `{a,b}` expand; numeric ranges `{6..11}`/`{1..11}` expand; a space-bearing/unbalanced brace list (`census/round-3/{seat-01..64.json, approvals-*.tsv`) cannot be resolved and must be skipped, not reported.
6. **The skip rule does not cover these, so `corpus/pointer-exemptions.tsv` must list them:**
   - `census/operator-sweep-20261019/` — operator-owned, untracked (`LOG.md:556,745`; `corpus/README.md:81`; `corpus/lessons/round-17.md:91`);
   - `.ufo/waves/round-16/build/` — historical build dir, absent now (`LOG.md:796`; `corpus/lessons/round-15.md:82`);
   - `.ufo/waves/round-21/` — future round, absent (`LOG.md:796`);
   - `tests/vault/vadv54-run/p/p6repo/.git` — a stub the harness creates for case P6 and `rmdir`s immediately (`tests/vault/vadv54-harness.sh:46,275-281`; `corpus/lessons/round-17.md:16` R17-M3). The parent `tests/vault/vadv54-run/p/p6repo/` **does** resolve (its `one.txt` and `inner/keep.txt` are committed); only the `.git` child is transient.
7. **Slash-lists of surface names are not paths:** `census/verify/vault/quarantine selftests` (`corpus/lessons/round-17.md:80`) has a `census/` prefix but no path-shaped tail. Require an extension or a resolvable directory prefix before classifying.
8. **Fleet lookups** must be a separate class, not findings: `.ufo/waves/hyaku/jj-w1/reports/` (exists fleet-side), `scripts/hyaku/jj-lane.sh` (exists fleet-side; prefix outside the governed set).

# Classification of every unresolved token (full 15-file set; scoped set flagged)

| token | class | evidence |
|---|---|---|
| `census/round-17/jj-receipts-ddb7347.txt` (+ `:18-19`, brace form) | **dangling** (scoped) | F1 |
| `census/round-17/gate-replays-ddb7347.json` | **dangling** (R2 corroborated) | F4; `SKILL.md:163,165`, `LOG.md:916` |
| `.ufo/waves/hyaku/jj-w1/reports/`, `…/reports/JjTrialSouji.md:76` | fleet | fleet dir exists; line 76 matches the claim |
| `scripts/hyaku/jj-lane.sh` (scoped, outside gate prefixes) | fleet | fleet regular file; lane has no `scripts/` |
| `.ufo/waves/round-17/w2/ReopenS0NN.md` | grammar | placeholder `S0NN`; the 13 concrete `ReopenS051…063.md` are committed (scoped) |
| `census/operator-sweep-20261019/` (×4 lines) | deliberate | operator-owned, untracked, explicitly never opened |
| `.ufo/waves/round-16/build/`, `.ufo/waves/round-21/` | deliberate | build dir gone; future round |
| `tests/vault/vadv54-run/p/p6repo/.git` (×3 lines) | deliberate (transient) | harness creates/removes the stub; parent dir committed |
| `census/verify/vault/quarantine` | grammar | slash-joined surface list, not a path |
| bare `README.md` ×2, `CHANGELOG.md` ×3, `SC2115.md`, `QUALITY.md` | grammar (external/bare) | git-sizer/jdupes READMEs, jj CHANGELOG, ShellCheck wiki page; `QUALITY.md` is `corpus/QUALITY.md` (Q16 at `:40` withdraws Q15, matching the quarantine entry's claim) |

# Smallest fixes (advisory)

1. `corpus/knowledge/jj-colocation-receipts.md:2,44,126,148` → cite `census/round-17/jj-receipts-4f48343.txt`; adjust the two "ddb7347" record attributions at `:2` and `:126`. This alone turns the knowledge slice's dangling count to 0.
2. `SKILL.md:163,165` and `LOG.md:916` → cite `census/round-17/gate-replays-4f48343.json` (routed R2; independently confirmed here).
3. Before landing `LG-DANGLING-PTR`, pin the token grammar in the gate and emit the token census (F4); implement F5.1–F5.5 or the gate will flag committed, correct prose at round 18.
4. Commit `corpus/pointer-exemptions.tsv` rows for the four deliberate paths in F5.6 (plus `S0NN` as a skip pattern if the grammar keeps it).

# Limits

- Single grammar instance, one rev; no gate run (forbidden) and no tools from the landing-gate family executed. The counts in the table are from my reimplementation, not from L1's gate.
- I did not attempt semantic validation of resolved pointers (line numbers inside existing files) except where they decided F1; e.g. `census/round-10/S06-cluster-C-member2.md:53-63` and `tests/results/r12-maintenance-guard.txt:11-16` resolve as paths but their line ranges were not checked.
- `corpus/knowledge/obsidian-ledger.tsv` was not swept (not `.md`).
- Tool installs/updates: none.
