STATUS: DONE — At ddb7347/d7e648d, C3 is receipt-safety work plus a committed fixture; none of the coverage counters moved (admitted_knowledge 5, 0 jj lines on every coverage surface). (b') is file-precise on all 4 live lanes, but it over-refuses directory targets on every lane. The knowledge draft is stale against the landed code.

Seat `SoujiR17-3.CriticC3Coverage2` · 2026-10-20 · landed `ddb7347` + `d7e648d` (HEAD = master = origin/master = d7e648d). Static review, read-only git, one read-only Python replay of `jj_keep_novel`'s own queries. No lane tool, fixture, selftest or `count-claims.py` was executed, and no `jj` was run. Nothing was installed. Axes: **coverage** (judged); calibration and operability only where C3 touches them.

## 1. Verdict: is C3 a coverage move?

- **At the landed revisions: no.** Every coverage counter is at its base value.
- **Coverage definitions used:**
  - `PROVINCE.md:50-51` (d7e648d): a frontier row moves to Core "only with an admitted `corpus/knowledge/` entry and a SKILL rule".
  - `SCORECARD.md:105`: "Source-row growth is not knowledge growth".
- **What `ddb7347` actually changes.** Its C3 content is `tools/souji-{verify,vault-verify,quarantine}.sh` and `tests/fixtures/r17-jj-receipts.sh`. Those are receipt-verdict code plus a fixture: operability and safety, not coverage.
- **The coverage carriers are not in any commit.**
  - `corpus/knowledge/jj-colocation-receipts.md` is `??`. It is 16,253 B, mtime 13:35.
  - No PROVINCE, SKILL, README, SOURCES or SCORECARD edit exists in either commit.

### Counters at d7e648d (and ddb7347)

| counter | command | value | base 5fa6017 |
|---|---|---:|---:|
| knowledge `.md` files | `git ls-tree --name-only d7e648d corpus/knowledge/` | 6 | 6 |
| HELD entries | only `quarantine-same-filesystem-rename.md:51` `## Admission status — HELD …` | 1 | 1 |
| `admitted_knowledge` (count-claims.py:20-21 logic, reproduced by hand; script not run) | 6 − 1 | **5** | 5 |
| jj/jujutsu/coloc lines | `git show d7e648d:<f> \| grep -ciE 'jj\|jujutsu\|coloc'`, for PROVINCE.md, SKILL.md, corpus/SOURCES.md, corpus/README.md, corpus/QUALITY.md, SCORECARD.md | **0, 0, 0, 0, 0, 0** | 0 everywhere |
| coverage-map rows | `git show d7e648d:corpus/README.md \| grep -nE '^\| F[0-9]'` | 5 lines: F1–F4 at :39-42, plus an F2 status row at :68. No jj row. | identical |
| S-rows | anchored `^\|\s*S[0-9]{3,}\s*\|` | 50 | 50 |

### Planned "5→6" counter

- **It holds only at a future commit.** It is still author inventory. The draft's admission block (`:122-124`) is:
  ```
  ## Admission status

  candidate — pending round-17 gate
  ```
  The HELD regex `^## Admission status.*\bHELD\b` (count-claims.py:20) is line-anchored, so this block does **not** match.
- Committing the draft as-is therefore prints `admitted_knowledge: 6` for an entry that says "candidate". That is the prior counterexample, still live.
- The "author inventory, closure decides" label is the right wording. It must be measured at the commit that adds the entry, not at ddb7347, where the value is 5.

### Fixture shapes

- **The claim "J1–J9 red at base / green changed" is overstated.** Source: `census/round-17/jj-receipts-base5fa6017.txt` and `-ddb7347.txt` (untracked). I checked their TOOL sha256 values against `git show <rev>:tools/<f> | sha256sum`, and all six match the committed blobs.
- **Red at base:** only shapes **J1, J3, J9**. That is 7 cases: J1, J1-vault, J3, J3-vault, J3-quarantine, J9-file, J9-worktree.
- **Green in both arms:** J2, J4, J5, J7, J8.
- **Skipped at base:** J6, because there is no baseline dir.
- So 3 shapes are base-discriminating, and 6 are controls.
- **J4/J5 cannot fail at base.** Base has no keep check, so they pass trivially there. Their discriminating arm is the w1 `--glob`-without-novelty variant, and no record of that arm exists. Report them as precision controls with no red arm, not as "red at base".
- **Q17 (`QUALITY.md:41`).** Both run records, and `seat-audit-r16-replay-*.json` / `gate-replays-ddb7347.json`, are `??` at d7e648d. The fixture file is committed; its run evidence is not.

### Double-count risk

- The same J1/J3/J9 runs are the safety evidence for (a')/(b').
- Count them once: either as the new edge-class shapes (coverage, conditional on the entry and the rule landing) or as receipt-safety evidence. Not both.

## 2. New counterexample: (b') refuses directory targets on every live colocated lane

The novelty test compares a **tree id** when the target is a directory:

- `tools/souji-verify.sh:252`, `tools/souji-vault-verify.sh:444` and `tools/souji-quarantine.sh:988` (ddb7347) all do `obj=$(git rev-parse -q --verify "$c:$rel")`.
- They check `obj` against `rev-list --objects --remotes -- "$rel"`.
- Directory targets reach this code: `evaluate_artifact` (verify:422-426) calls `try_pushed` with `isdir=1`, and `try_pushed` calls `jj_keep_novel` at verify:719-721.

A keep-only predecessor's directory tree can be a combination of blobs that was never pushed, even when every blob in it was pushed. One example is the working-copy snapshot taken before `jj commit -- <paths>` splits it. A deletion inside the directory also gives a new tree id, which contradicts the header claim "Deletions … do not refuse" (verify.sh:71-74).

**Read-only replay of the function's exact queries.** Python subprocess running `for-each-ref`, `rev-list --glob=refs/jj/keep/* --not --branches --tags --remotes`, `rev-list --objects --remotes -- <d>`, `rev-parse -q --verify C:<d>`, `log --remotes --raw` and `diff-tree -r --name-only`:

| lane | keep refs | keep-only commits | (commit, file) pairs | file: deletion | file: blob already pushed | **file: novel** | dirs checked | **dirs with a novel tree** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| souji | 17 | 13 | 369 | 22 | 347 | **0** | 17 (all) | **6**: `census`, `tests`, `tests/fixtures`, `tests/vault`, `tests/vault/vadv54-run`, `tests/vault/vadv54-run/p` |
| kama | 22 | 10 | 414 | 0 | 414 | **0** | 9 (depth ≤ 2) | **7**: `.ufo`, `.ufo/waves`, `corpus`, `tests`, `tests/llamacpp-live`, `tests/probe-verdicts`, `tools` |
| tameshi | 34 | 18 | 1100 | 0 | 1100 | **0** | 7 (depth ≤ 2) | **6**: `.ufo`, `.ufo/evidence`, `.ufo/waves`, `corpus`, `corpus/knowledge`, `tools` |
| mado | 53 | 34 | 1287 | 0 | 1287 | **0** | 6 (depth ≤ 2) | **4**: `.ufo`, `.ufo/waves`, `corpus`, `corpus/lessons` |

- **File targets hold.** (b') clears all 3,170 (commit, file) pairs and has 0 file-level positives. The w1 demand (§3.1) is met for files.
- **Directory targets fail.** 23 of the 39 directories checked carry a novel tree id, built only from already-pushed blobs. The souji `tests/vault/vadv54-run/p` case comes from the p6repo phantom deletion (`41ab059d`).
- **[INFERENCE] about verdicts.** I did not run verify; running it on a real directory is forbidden. A clean, pushed, ancestor directory receipt such as `tools/` or `corpus/` would read SAFE(pushed) at base. At ddb7347 it reads `NOT-SAFE … jj-keep-novel` on all four lanes, with zero novel content behind it.
- **No directory-target case exists in any arm** (fixture J3–J5, verify J1–J3, vault J1–J3, quarantine JJ1–JJ5 all target files). So the 20/0, 45/0, 57/0 and 101/0 results do not cover this.
- **Smallest fix (one line, applied identically at all three sites).** Compare leaf blobs instead of the object at `C:rel`:
  ```
  while IFS= read -r obj; do printf '%s\n' "$known" | grep -Fxq -- "$obj" || return 0
  done < <(git -C "$repo" ls-tree -r --format='%(objectname)' "$c" -- "$rel")
  ```
  - For a file target, `ls-tree -r` returns the same single blob, so file behaviour is identical.
  - For a deletion, it returns nothing, so there is no refusal.
- **Fixture:** add J10 (directory with a keep-only mix of pushed blobs → SAFE(pushed)) and J11 (directory with one novel blob → NOT-SAFE).
- If the lane rejects the fix, it must publish the table above as a measured contraction for directory receipts (Q22, `QUALITY.md:56`).

## 3. jj residue that stays ungoverned at ddb7347

"jj-colocated repositories as a governed edge class" overreaches. What is governed is **receipt roots + keep-blob novelty (file targets) in verify/vault/quarantine, and the quarantine index recipe**.

| residue | location at ddb7347 | state |
|---|---|---|
| census `unpushed` column | `tools/souji-census.sh:997-1007` `rev-list --count --branches --not --remotes`; header :30-31 | ungoverned; no jj token or disclosure in the census header (`grep jj` = 0 in non-unpushed lines) |
| repo-root evidence `unpushed=N` | `souji-verify.sh:360`; vault header :59 "unchanged: keep-only commits are not counted there" | disclosed in the vault header only. Evidence-only: repo-root is always NOT-SAFE without an obsidian row (verify:357-366), so there is no safety hole. |
| repo-structure ref/object inflation | `tools/souji-repo-structure.sh:31` "seeds its walk from references (builtin/repo.c:722)"; no `refs/jj` handling (0 matches) | ungoverned; keep-held objects are counted as reachable |
| HEADPIN consumers | `census/round-14/count-claims.py:12-15` (defaults to `rev-parse HEAD`); **new r17** `census/round-17/gate-replays.py:222` `lane_head = rev-parse HEAD` (record `gate-replays-ddb7347.json` has `lane_head` = d7e648d); `census/round-13/run-verification.py:384`; `census/round-14/cache-demonstration.py:166` (labelled harness_revision) | ungoverned. Only `run-matrix.py:174-175` is jj-aware: it pins `refs/heads/master` and labels `git_head` "detached under jj colocation". |
| index ownership | quarantine: `q_jj_colocated` :243, jj-lane recipe CMD, `index-cleanup-skipped … jj-owns-index` :615 | **partly governed** (quarantine only). There is no census of staged entries vs jj. |
| hook/filter/eol bypass | census pins `core.hooksPath=/dev/null` and filter-driver checks on git reads (:123-128, :181, :1116); nothing covers jj's write path | ungoverned; the draft §11 says so, but no SKILL rule has landed |
| auto-track / intent-to-add | no tool reads the jj `snapshot.auto-track` setting; the rule exists only in the uncommitted draft §6 | ungoverned |
| jj secondary workspaces (new) | `q_jj_colocated` requires `-e "$1/.git"` (quarantine:243). `docs/working-copy.md@v0.45.1:74-80`: `jj workspace add` creates a working copy with "a `.jj/` directory linked to the main repo", i.e. no `.git` | ungoverned and invisible to `git worktree list`. NOT-SAFE by default, so this is a coverage gap, not a safety gap. Live exposure not enumerated (fleet-root listing not allowed). |
| keep-ref lifetime / gc | `jj-lane.sh` has no `op abandon`/`util gc` (w1 §3.1) | residue, expected |

## 4. Prior attack (w1 `CriticC3Coverage.md`): demands met at ddb7347

| w1 demand | status | evidence |
|---|---|---|
| (b) blob-novelty filter, not `--glob` alone (§3.1, §7) | **met for files; fails for directories** | `jj_keep_novel` verify:236-258; file novel = 0 on all lanes (§2) |
| (a) keep `refs/stash`/`refs/original` roots, or J7 + disclose | **met** | `for-each-ref --exclude='refs/jj/'` verify:854; J7 PASS in both arms; vault J5 and quarantine JJ6 (refs/stash → SAFE(metadata-prune)) |
| count only effective sites; drop or label dead duplicates | **half met** | Dead sites are untouched by code (base `try_pushed` :219 shadowed by :655; `evaluate_worktree` :333 shadowed by :1004; vault :400/:499 shadowed by :843/:1192). They are neither deleted nor labelled, and the draft still cites them (draft :106 → `souji-verify.sh:351` and `souji-vault-verify.sh:517`, both inside the shadowed definitions). |
| J1–J8 committed fixture, `/var/tmp` + trap, effective functions via CLI | **met (fixture)**; **not met (evidence)** | `tests/fixtures/r17-jj-receipts.sh:14-15, 53-64`; run records are untracked (Q17) |
| knowledge entry admitted with Q1/Q2/Q3/Q4/Q17/Q23 grounding | **not met** | see §5 |
| PROVINCE frontier row (F5) + coverage-map row; Core = bounded receipt-root rule only | **not met** | 0 jj lines; README F-rows unchanged |
| remove `refs/jj/bookmarks` prose | **met in code** | the vault header now lists keep/, remote-tags/ and root only |
| keep refs are "every jj-written commit", not "abandoned predecessors" | **met in code, not in draft** | verify:61-63 says "every commit it creates, visible or hidden"; draft :28 still says retention is undocumented and "Abandoned or hidden predecessors are not described" |
| do not cite JjAuditSouji F3 `HEAD --not --all → empty` | **not met** | draft :31 still offers it as observed keep-ref evidence; it is vacuous because `--all` includes HEAD |
| disclose plan substitution (F2 → jj) | **not checkable** | no SCORECARD edit has landed |

## 5. The draft knowledge entry is stale against the landed code (would fail closure as written)

- **Rule 5 (:92) describes the rejected recipe.** It says "add `--glob=refs/jj/keep/*` … Hidden rewritten predecessors that touched the target also refuse". The landed rule is novelty-filtered (verify:69-77).
  - Rule 7 (:94) "the `--glob` addition is empty for them" and Limits :101 "no fixture … proves it" are also stale.
  - Q23 (`QUALITY.md:57`): the wording must match the exercised boundary.
- **Limits :99 and :100 contradict the record.**
  - :99 says "None is in a committed fixture". `tests/fixtures/r17-jj-receipts.sh` is committed, and J9 runs real jj 0.45.1.
  - :100 and §7 :58 say nested-`.git` skipping is "not described in any jj page read". It is sourced: `CHANGELOG.md@v0.45.1:1268-1269` (0.36.0): "Sub-repos are no longer tracked. Any directory containing `.jj` or `.git` is ignored." That is the planned S056, and it explains the phantom deletions.
- **Q1/Q2 (`QUALITY.md:25-26`).**
  - Every jj citation is `docs.jj-vcs.dev/latest/…`, and the recheck (:3) `curl`s `latest`. Upstream v0.46.0 shipped after v0.45.1 (w1 §4), so `latest` drifts.
  - No `lib/src/git_backend.rs@v0.45.1` row appears, although the landed tool headers cite it (vault header "git_backend.rs@v0.45.1:868-871") and it is the planned S054.
  - Fix: cite `@v0.45.1` paths, and make the recheck `bash tests/fixtures/r17-jj-receipts.sh --tool-dir tools` with `jj --version`.
- **Q4/Q17 (`QUALITY.md:28, :41`).**
  - The source header (:1) and rows :118-120 rest on `/home/vgpnk/Projects/shokunin/.ufo/waves/hyaku/jj-w1/reports/*`, which is not contained in the lane revision.
  - The behavioural recheck (:3) asks to "rebuild … sequences" instead of naming the committed fixture.
- **Count drift in own observations.** The draft cites "JjTrialSouji.md:61 counts 15 keep refs". The souji lane now has 17 keep refs and 13 keep-only commits; w1 counted 8 and 6. Keep any count dated and n-labelled, or drop it.
- **Source rows.** The draft lists 10 `S0??` rows (6 docs at `latest`, git-rev-list, 3 own-work). The plan numbers S051–S063, 13 rows; S057–S063 are C1/C2/git sources. Per SCORECARD:105, none of these rows counts as coverage.

## 6. Smallest safe corrections

1. **(b') directories.** Replace `rev-parse C:rel` with `ls-tree -r --format='%(objectname)' C -- rel` at verify:252, vault:444 and quarantine:988. Add fixture J10/J11. Otherwise, publish §2 as a measured directory-receipt contraction.
2. **Coverage claim.**
   - Measure only at the commit that adds the entry, the PROVINCE F5 row, the README F5 row and the SKILL rule.
   - Report `admitted_knowledge 6 (author inventory; candidate, closure decides)`.
   - Word the scope as "bounded receipt-root + keep-novelty rule for jj-colocated lanes (Core, file targets); jj colocation otherwise frontier", followed by the §3 residue table.
3. **Fixture wording.** "J1, J3, J9 red at base (7 cases) → green; J2, J4, J5, J7, J8 controls; J6 byte-identity changed-arm only." Commit both run records (Q17).
4. **Draft revision before closure.**
   - Rewrite rules 5/7 and Limits :99-101 to the landed novelty rule.
   - Drop the F3 vacuous citation (:31) and the dead-site citations (:106).
   - Pin docs/source to `@v0.45.1`; add `git_backend.rs@v0.45.1` and CHANGELOG 0.36.0.
   - Point the recheck at the committed fixture.
5. **HEADPIN.** `gate-replays.py:222` is new r17 code. Pin it to `refs/heads/master` the way run-matrix.py:174 does, or label it.

## 7. Commands run (read-only) and probe-rule disclosure

- `git -C <lane> show --stat ddb7347`, `show --stat d7e648d`, `rev-parse HEAD master origin/master`, `ls-tree --name-only {ddb7347,HEAD} census/round-17/ corpus/knowledge/`, `log --oneline -5`.
- `git show d7e648d:<f> | grep -ciE 'jj|jujutsu|coloc'` for the 6 surfaces → 0 each. README F-rows at 5fa6017 and d7e648d were identical. The S-row count was 50.
- `git show ddb7347:census/round-14/count-claims.py`. `git show d7e648d:corpus/knowledge/quarantine-same-filesystem-rename.md | grep -n '^## Admission'` → `:51 … HELD`.
- `git diff 5fa6017 ddb7347 -- tools/souji-{verify,vault-verify,quarantine}.sh`; `git show ddb7347:<tool> | sed -n …` / `grep -n …` on exact files.
- `git show <rev>:tools/<f> | sha256sum` for both arms → all six match the TOOL lines in the records.
- `cat` / `sha256sum` of `census/round-17/jj-receipts-{base5fa6017,ddb7347}.txt` (e572fcac…, 72844551…).
- `read` of the exact files `.ufo/waves/round-17/w1/CriticC3Coverage.md` and `corpus/knowledge/jj-colocation-receipts.md`.
- `python3 -c json.load(...)` on `census/round-17/gate-replays-ddb7347.json` → `lane_head` d7e648d.
- Python (eval kernel) subprocess running read-only git over souji/kama/tameshi/mado: `for-each-ref`, `rev-list`, `log --raw`, `rev-parse`, `diff-tree` → §2 tables.
- Web, read-only: `raw.githubusercontent.com/jj-vcs/jj/v0.45.1/{CHANGELOG.md, docs/working-copy.md}`.
- **Deviations, disclosed:**
  - I ran `git -C <lane> status --porcelain=v1 --untracked-files=normal -- census/round-17 corpus tests/fixtures PROVINCE.md SKILL.md` once. `status` is not on the read-only allow-list and may refresh index stat data.
  - `git diff-tree` (read-only plumbing) is not named on the list.
  - The CHANGELOG was saved briefly to `/var/tmp/souji-r17-CriticC3Coverage2-CHANGELOG.md`, moved into `/var/tmp/souji-r17-CriticC3Coverage2/`, grepped, and the directory was deleted (`stat` → No such file).
- Not run: `count-claims.py` (its value is reproduced by hand from its own regex), any lane tool, selftest or fixture, and `jj`. The directory-verdict change in §2 is an inference from replaying the function's queries, not an executed verdict.
