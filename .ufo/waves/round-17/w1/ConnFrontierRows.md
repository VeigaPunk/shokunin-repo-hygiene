STATUS: DONE — the jj-colocation entry advances F1 as a named edge class and needs one PROVINCE `## Work surfaces` line, not a new frontier row F5.

Author: `SoujiR17-3.ConnFrontierRows` (connector, wave 1). Read-only: no tool, fixture or repo byte was written; no `jj` call and no git write was made. Report path is the only file I created. Installs/upgrades: none.

## 1. Ruling

**Primary row: F1 (git-native housekeeping vs receipts), as a sub-ground, not a closure.** The knowledge entry's load-bearing claim is "a native VCS's retained object is not a durable root for a deletion receipt". F1 is defined as exactly that question for git's deleters (`PROVINCE.md:52-54`: `maintenance --auto` worktree-prune, gc/reflog grace periods). `refs/jj/keep/*` is jj's gc grace ref; the audited defect is `--not --all` treating it as durable and granting `SAFE(metadata-prune)` where the honest verdict is NOT-SAFE (`JjAuditSouji.md` F3, production sites verify :351, vault :517, and the `rev-list --not "${roots[@]}"` twins verify :809-813, vault :997-1001, quarantine :1069-1073). Same question, different maintainer. C3(b) is the same F1 question on the receipt side (unpushed-touching refusal must see commits only jj holds).

**Secondary, disclosed-only: F2 (repository size census).** Colocated repos inflate the structure census: `references.others.count=15` (`refs/jj/keep/*`) and `objects.commits.count` 55 vs 44 on the plain clone (`JjTrialSouji.md` step 5). C3 does not claim F2; this belongs in the index as a caveat so a later round does not misread a colocated/plain delta as repository growth. No F2 capability is claimed.

**Why not a new frontier row F5.** A frontier row moves to Core only with an admitted `corpus/knowledge/` entry *and* a SKILL rule (`PROVINCE.md:50-51`). Minting F5 would (a) create a second row gated on the same entry, (b) leave F1's own next-step (`corpus/README.md:46`, the auto-maintenance exposure census, still 0 prunable / 3 locked from r12) silently attached to two rows, and (c) invite a later reader to believe jj colocation is a separate *question* when it is the same question on a second substrate. However, **the substrate is genuinely unnamed today**: `## Work surfaces` (`PROVINCE.md:19-23`) lists only the fleet root, `<lane>-shokunin/` paths and GitHub remotes. That list is "resolve and re-verify each round", so a lane whose git dir is a jj workspace belongs there — as a surface, not as a frontier claim. This is the r13 precedent shape (F2 got `## Round 13 boundary refinement` + a SKILL section + a superseding README row, `PROVINCE.md:72-80`), scaled to one bullet plus one appended section.

**Consequence for `corpus/README.md:39` and `:46`: do not edit them in place.** They are dated index rows; the file's own rule is "write the row when the file exists, not before" (`:2-3`). Appending a Round 17 section that supersedes the jj subset of F1 preserves the r12 row as history and keeps the claim honest. Adding `knowledge/jj-colocation-receipts.md` as a third entry to the F1 row at `:39` without a supersede note would claim F1 coverage the round does not measure.

## 2. PROVINCE.md draft (current file: 93 lines)

### 2a. Insert after `PROVINCE.md:23` (fourth bullet of `## Work surfaces`, heading at :19)

```
- jj-colocated lane repos (`$SHOKUNIN_ROOT/<lane>-shokunin/.jj` — present in
  kama, mado and tameshi today): the git directory is a jj workspace. HEAD is
  normally detached at `@-`, the index is jj-owned, and `refs/jj/*` exists.
  `refs/jj/keep/*` is a garbage-collection grace ref, not durable history:
  receipt roots are `refs/heads`, `refs/tags` and `refs/remotes` only.
  Re-resolve per round; a repo without `.jj`/`refs/jj` is a plain git repo
  and every receipt path is unchanged.
```

### 2b. Append after `PROVINCE.md:93` (new section; file currently ends at :93)

```
## Round 17 boundary refinement (jj-colocated lanes)

`refs/jj/keep/*` is jj's gc grace ref and is never a durable receipt root: a
commit held only by `refs/jj/keep` cannot justify `SAFE(metadata-prune)`, and
`--not --all` or any all-ref `for-each-ref` root list must exclude it
(durable = `refs/heads`, `refs/tags`, `refs/remotes`; `refs/stash` and HEAD
are not roots either). Unpushed-touching refusals additionally scan
`refs/jj/keep/*` heads. That is deliberately conservative: a rewritten
predecessor jj hides can refuse an artifact no branch carries, and the census
`unpushed` column stays branch-based and is disclosed, not silently widened.
A repo with no `refs/jj` must produce byte-identical output. This section
names the substrate; it does not close F1 (no admitted entry at wave 1) and
it does not make souji a jj mutator — commits stay operator/helper-owned, and
`## Refuses` (PROVINCE.md:26) is unchanged.
```

Wording constraints I applied, and why:
- No expiry time is claimed. `JjAuditSouji.md` F3 shows `refs/jj/keep` is a grace ref; neither audit measures when jj drops it. Do not add "expires after N".
- "not a receipt root" is scoped to receipts/prune verdicts, not to a claim that keeping refs is wrong or removable. Removing them is a jj mutation and stays refused.
- "byte-identical for plain repos" is the C3 testable boundary; keep it in the surface text so a verifier can check it, not only in the claim.

## 3. corpus/README.md draft (current file: 203 lines)

### 3a. Append after `corpus/README.md:203` (new superseding section)

```
## Round 17 — jj-colocated lane repos as a governed edge class

Supersedes the F1 row at :39 and the F1 Frontier next-step at :46 for the
jj-colocated subset only; both lines stand for plain repos. F2's row at :68
gains a caveat, not a capability. No other coverage row changes.

| ground | status | entries / runnable evidence |
|---|---|---|
| F1-jj jj-colocated lane repos (edge class of F1; F1 itself stays frontier) | bounded receipt-root rule acquired and measured; no F1 closure claimed | `knowledge/jj-colocation-receipts.md`; `tests/fixtures/r17-jj-receipts.sh`; `census/round-17/verification.json` |
| F2 colocated-repo accounting caveat | observed, not claimed: `refs/jj/keep` inflates `references.others` and commit counts versus a plain clone | `../.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md` step 5 (15 refs; 55 vs 44 commits); `JjAuditSouji.md` F3 |

Disclosure carried with the row, not in a footnote: the census `unpushed`
column remains branch-based; this lane holds 8 `refs/jj/keep` refs, 6 of them
not ancestors of `master`, and 4 of those carry phantom deletions. An absent
worktree head held only by a keep ref is NOT-SAFE, never `SAFE(metadata-prune)`.

### Frontier (r17)

- F1 — plain repos: unchanged (:46). Colocated repos: next is a keep-ref
  expiry measurement (what makes a keep-only commit unreachable) plus a
  fixture that returns NOT-SAFE where `--not --all` used to return
  SAFE(metadata-prune); both are unrun at wave 1.
- F2 — unchanged (:47); add a colocated/plain byte-comparison as a
  precondition for any `git repo structure` baseline.
```

### 3b. Commit-order condition (hard)

The coverage row is a claim that the entry and fixture exist (`README.md:2-3`). Land it **only** in the same commit as `corpus/knowledge/jj-colocation-receipts.md` and the fixture it names; otherwise drop the table row and ship only:

```
| F1-jj jj-colocated lane repos | frontier, no entry yet; PROVINCE surface line added | — |
```

and the two Frontier lines. This is the only difference between variant A (entry committed) and variant B (entry held or rejected at wave 2). Do not ship variant A's row on the strength of a wave-1 draft.

### 3c. Four lengths in the draft are deliberate and must not be "tightened" by a scribe

1. `F1 itself stays frontier` — the round measures a keep-ref edge, not the r12 auto-maintenance exposure question at `:46`.
2. `observed, not claimed` on the F2 row — the inflation is one sandbox measurement (`JjTrialSouji.md` step 5), not a fixture in this lane's registry.
3. `NOT-SAFE, never SAFE(metadata-prune)` — the pair is the auditable verdict, not rhetorical emphasis.
4. `byte-identical` for plain repos — the C3(b) acceptance boundary; it is the one sentence a verifier can execute.

## 4. Evidence (exact commands and observed output)

| check | command | observed |
|---|---|---|
| jj substrate is live in this lane | `git -C <lane> rev-parse --abbrev-ref HEAD` | `HEAD` — detached, as the surface bullet states |
| `.jj` present | `test -d <lane>/.jj` | present |
| keep refs exist | `git -C <lane> for-each-ref --format='%(refname)' refs/jj/keep \| wc -l` | `8` |
| keep-only commits are real here | `git -C <lane> for-each-ref --format='%(objectname)' refs/jj/keep \| while read -r c; do git -C <lane> merge-base --is-ancestor "$c" master \|\| echo "$c"; done \| wc -l` | `6` — matches the claim's "6 keep-only commits" |
| branch-based unpushed count is blind to them | `git -C <lane> rev-list --count --branches --not --remotes` | `0` — so the `unpushed` column says clean while 6 keep-only commits exist; disclosure is mandatory |
| stash is not a root either | `git -C <lane> for-each-ref --format='%(refname)' refs/stash \| wc -l` | `0` (still named in the surface text because the rule is general) |
| base revision | `git -C <lane> rev-parse HEAD` | `5fa6017ddcae9f6bd4412df44765f6360cb16294` |
| PROVINCE anchors | `grep -n '^## \|^  - F[0-9]' PROVINCE.md` | `## Work surfaces` :19; bullets :21-23; `## Refuses` :26; F1 :52-54; F2 :55-57; F3 :58-59; F4 :60-61; r13 refinement :72; r14 clarification :82; EOF 93 (`wc -l`) |
| README anchors | `grep -n '^\| F[0-9]\|^## Frontier\|^- F[0-9]' corpus/README.md` | coverage table header :36; rows :38-42 (F1 :39, F2 :40, F3 :41, F4 :42); `## Frontier` :44; items :46-49; r13 F2 superseding row :68; `## Round 16` :189; EOF 203 (`wc -l`) |
| no jj ground already indexed | `grep -rIl -i 'jj\|jujutsu' corpus/*.md SKILL.md PROVINCE.md`; `ls corpus/knowledge/` | only `corpus/lessons/round-16-verifier-spotcheck.md` matches (path text); no `corpus/knowledge/*jj*`; no SKILL `frontier` mention at all |
| SKILL surface that C3 makes stale | `grep -n 'Unpushed-lane trap' SKILL.md` | `SKILL.md:76-79` names `git log --branches --not --remotes --oneline` as the trap test, which is exactly the blind query; the README Frontier lines should point at it |
| F2 SKILL precedent shape | `grep -n '^#' SKILL.md` | `## Known surfaces` :158, `## Repository structure census (F2, bounded r13 capability)` :176 — the shape a jj section would mirror if C3(d) lands it |

**Observed contradiction, outside my scope but relevant to the landed row:** `stat -c '%F %n' <lane>/tests/vault/vadv54-run/p/p6repo/.git` → `cannot stat ... No such file or directory` (exit 1) at this probe. C3(e) names that path as the empty stub that makes jj see phantom deletions; it does not exist in the current worktree (a `Vadv54StubFix` seat is dispatched). Do **not** cite that path in the PROVINCE or README text unless re-verified at landing — the docs above deliberately name neither the stub nor its count, so they survive either outcome.

## 5. Axes

| axis | effect | basis |
|---|---|---|
| coverage | **improves** | the substrate is named in the surface list resolvable each round, the F1-jj ground gets an index row iff its entry lands, and the F2 colocated caveat prevents a false "repository grew" reading. No capability is counted as knowledge before admission. |
| operability (C1) | no harm | no tool, fixture or command path is touched; the docs add no refusal and change no exit code. |
| calibration (C2) | no harm | no audit rule or verdict vocabulary is added; `SAFE(metadata-prune)`/NOT-SAFE wording is reused, not redefined. |
| depth | neutral | the boundary section cites F3/branch-vs-keep evidence rather than restating the audits. |
| freshness | neutral | no source row or "verified-at" claim is asserted here; the entry's own header owns that. |
| adjacency | neutral | no sibling province claim; kumitate lock, kagi credential and operator-owned rewrite boundaries are untouched. |

## 6. Risks and smallest fixes

1. **Overclaim risk (highest).** A reader can take "F1-jj" for "F1 closed". Fix: the exact phrase `F1 itself stays frontier` in both the status cell and the Frontier line; the r12 row at `:39` is superseded, not rewritten.
2. **Row-before-file risk.** The variant-A table row asserts `knowledge/jj-colocation-receipts.md` exists. Fix: §3b commit-order condition; ship variant B if the entry is held.
3. **Substrate line read as write authorization.** The Work-surfaces bullet describes a workspace, not a permission. Fix: the appended section's last sentence keeps commits operator/helper-owned and leaves `## Refuses` (:26) unchanged.
4. **`unpushed` column misread as jj-aware.** Live `0` unpushed with 6 keep-only commits is precisely the trap. Fix: the disclosure sentence is part of the coverage row, not a footnote.
5. **Keep-ref expiry implied.** No audit measures when jj drops a keep ref. Fix: no duration language anywhere; the F1 next-step explicitly says the expiry measurement is unrun.
6. **Doc drift if C3(b) does not land the `--glob=refs/jj/keep/*` change.** The PROVINCE section states the refusal behavior; if the tool change is cut, the section must move to a Frontier "next" rather than stay as present-tense behavior. This is the one dependency between my draft and an executor's file.

## 7. Verification for L1 (unrun here)

- Re-run the six `git -C` reads in §4 at the landed commit; they are the only numeric claims in the prose (8 keep refs, 6 keep-only, unpushed 0).
- After insertion, `grep -n '^## ' PROVINCE.md` must show `## Work surfaces` before the new bullet and `## Round 17 boundary refinement` as the last section; `wc -l PROVINCE.md` becomes 93 + the inserted lines + 14.
- For every path in the landed README row: `git -C <lane> ls-tree -r --name-only <landed> -- <path>` returns it. Any miss falsifies the row under `README.md:2-3`.
- Confirm no diff touches `PROVINCE.md:39/46` equivalents (i.e. `corpus/README.md:39` and `:46`): `git diff <base> <landed> -- corpus/README.md` must show additions only after :203.
