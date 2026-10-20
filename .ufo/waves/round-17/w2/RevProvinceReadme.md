STATUS: DONE — W1's ruling and file structure hold (surface bullet + appended PROVINCE section + superseding README round section, no new F5 row), but its durable-root wording contradicts the landed code, its keep-ref counts are stale at the landing rev, and three evidence pointers are broken; corrected final text for both files is in §4/§5 with exact before/after line numbers at ddb7347.

Reviewer: `SoujiR17-3.RevProvinceReadme-2` (wave 2, leaf). Read-only seat: the only file written is this report; PROVINCE.md and corpus/README.md are NOT edited — L1 integrates. No `jj` run, no git write, no tool run against any real directory. Installs/upgrades: none.

Axes (godspeed): **coverage** (judged — substrate named in the re-resolve-each-round list; F1-jj indexed Core-bounded iff the landing condition is met; residue named), **correctness** (every doc sentence must match landed code + fixtures at ddb7347), **rot-resistance** (no unversioned live counts, no line-number cross-refs that the insertion itself shifts), **honesty** (Core is conditional with a printed fallback, so no world-state overclaims).

## 1. Verified ground (exact commands and outputs)

All `git` calls read-only, `git -C /home/vgpnk/Projects/shokunin/souji-shokunin` (lane root; ddb7347 = `4433977ff…` full id `ddb73474433977ff54b015ac3e77669ff2537353`, HEAD = `d7e648d5a1931e6dbacfd5be0587547afee15de3`, base = `5fa6017ddcae9f6bd4412df44765f6360cb16294`).

| # | check | command | observed |
|---|---|---|---|
| 1 | doc drift vs ddb7347 | `git … diff --stat ddb7347 -- PROVINCE.md corpus/README.md` | empty — working tree byte-identical to ddb7347 for both docs, so line numbers below serve for both |
| 2 | PROVINCE anchors | `grep -n -e '^## ' -e '^- ' PROVINCE.md`; `wc -l` | `## Owns` :6, `## Work surfaces` :19, bullets :21–:24 (third bullet **wraps to :24**), `## Refuses` :26, `## Core / Frontier / Adjacent` :47, promotion rule :50–51, F1 :52–54, r13 :72, r14 :82, EOF **93** |
| 3 | README anchors | `grep -n -e '^| F' -e '^## ' -e '^- F' corpus/README.md`; `wc -l` | r12 F1 row :39, F2 :40, `## Frontier` :44, F1 next-step :46, r13 superseding row :68, `## Round 16` :189, EOF **203**; index rule "write the row when the file exists, not before" at **:3–4** (`grep -n 'when the file exists'`) |
| 4 | jj substrate live | `test -d <lane>-shokunin/.jj` for kama, mado, tameshi, souji | all four present; `git rev-parse --abbrev-ref HEAD` → `HEAD` (detached) |
| 5 | keep-ref probes at HEAD d7e648d | `for-each-ref --format='%(refname)' refs/jj/keep \| wc -l` → **17**; non-ancestors of master (`merge-base --is-ancestor` loop) → **13**; `rev-list --count --branches --not --remotes` → **0**; `for-each-ref refs/stash \| wc -l` → **0** | W1 measured 8/6 at 5fa6017; counts drifted (+9/+7) from the round's own lane activity |
| 6 | landed root-site code | `grep -n 'refs/jj\|jj_keep_novel\|exclude=refs/jj' tools/souji-verify.sh tools/souji-vault-verify.sh tools/souji-quarantine.sh` | durable roots = **every ref except `refs/jj/*`**: `souji-verify.sh:64` ("durable receipt roots are EVERY ref except refs/jj/*"), :854; `souji-vault-verify.sh:46–50`, :1061; `souji-quarantine.sh:115–116`, :1155. `jj_keep_novel` at verify :241–250 (call :719–721), vault :433–441 (:914), quarantine :977–985 (:1017); novelty gate + history-unverifiable rc 2 in all three; quarantine header :119–125 and vault header :51–58 state deletions/identical-blob predecessors do not refuse |
| 7 | stash stays a root (fixture-pinned) | grep output #6 | `souji-verify.sh:1292` "J5: absent-worktree head held only by refs/stash (a durable root)"; `souji-vault-verify.sh:1689` "J5: the same shape held by refs/stash stays a durable root" |
| 8 | fixture + records exist | `glob tests/fixtures/r17-jj-receipts.sh`; `read census/round-17/jj-receipts-ddb7347.txt:-15` | fixture present; record ends `SUMMARY total=20 failed=0 skipped=0` (J1 `NOT-SAFE … unique=1 … owner=keeprepo`); `jj-receipts-base5fa6017.txt` = 30 lines |
| 9 | round-17 census inventory | `glob census/round-17/` | 12 entries: c1-matrix.json, live-fleet.json, jj-receipts-*.txt ×2, seat-audit-*.json ×2 + replay.py, gate-replays-*.json ×2 + .py, run-matrix.py, transcript-manifest.py — **no `verification.json`** |
| 10 | entry tracking state | `git status --porcelain -- corpus/knowledge/jj-colocation-receipts.md …`; `git ls-files -- <entry>` | only `?? corpus/knowledge/jj-colocation-receipts.md`; ls-files empty → **untracked**; entry header: "candidate — pending round-17 gate" |
| 11 | SKILL state | `grep 'jj\|jujutsu\|refs/jj' SKILL.md` | **no matches** — no SKILL jj rule exists in the tree; `Unpushed-lane trap` (`git log --branches --not --remotes --oneline`) confirmed at SKILL.md:76–79 |
| 12 | hyaku report location | `glob` lane `.ufo/waves/hyaku/jj-w1/reports` → **path not found**; `glob` fleet `/home/vgpnk/Projects/shokunin/.ufo/waves/hyaku/jj-w1/reports` → present, incl. `JjTrialSouji.md`, `JjAuditSouji.md` | reports are **fleet-rooted**; from `corpus/README.md` the correct relative prefix is `../../.ufo/…`, not W1's `../.ufo/…` |
| 13 | cited report content | `read JjTrialSouji.md:50-68`; `read JjAuditSouji.md:117-133` | step 5: `references.others.count=15` (refs/jj/keep/*), `objects.commits.count=55` vs 44, `unpushed=0` with `dirty=1`; F3: `--not --all` treats `refs/jj/keep` as durable, granting `SAFE(metadata-prune)` at `souji-verify.sh:351`, vault :517 — cites check out |
| 14 | no prior jj mention | `grep -i 'jj\|jujutsu' PROVINCE.md` | rc 1 — the bullet is genuinely new ground |

## 2. Findings (severity-ordered)

**F1 · MAJOR — W1's durable-root set contradicts the landed code.** W1 §2a ("receipt roots are `refs/heads`, `refs/tags` and `refs/remotes` only") and §2b ("durable = `refs/heads`, `refs/tags`, `refs/remotes`; `refs/stash` and HEAD are not roots either") describe a semantics the round did NOT ship. Landed: durable roots = every ref except `refs/jj/*` (`souji-verify.sh:64,854`; `souji-vault-verify.sh:46–50,1061`; `souji-quarantine.sh:115–116,1155`), and the fixtures pin `refs/stash` as a durable root (`souji-verify.sh:1292`, `souji-vault-verify.sh:1689`). W1's own evidence table even rationalized the error ("stash … 0 (still named in the surface text because the rule is general)"). A reader of W1's text would expect a stash-only absent-worktree head to refuse; the landed tool + J5 fixture treat the stash ref as durable. Smallest fix: adopt §4's wording ("every ref except `refs/jj/*`"). Same correction needed in the untracked entry before commit: `corpus/knowledge/jj-colocation-receipts.md` §3 consequence ("Durable roots are `refs/heads`, `refs/tags`, `refs/remotes`") and Operating rule 4 disagree with the tools; the heads/tags/remotes set is a stricter *unlanded* variant, and rule 4's "do not use `--not --all`" is right while its positive list is wrong. Advisory to the entry owner (I do not edit another seat's file).

**F2 · MAJOR — W1's refusal sentence overstates the landed gate.** §2b "Unpushed-touching refusals additionally scan `refs/jj/keep/*` heads" reads as any-keep-commit-refuses. Landed: the refusal fires only when the keep-only commit introduces **novel content at the target** (`C:<rel>` exists and its object id is absent from every remote-reachable blob at the path) — `jj_keep_novel` verify :241–250/vault :433–441/quarantine :977–985; quarantine header :119–124 spells out "keep-only deletions and metaedit/rebase predecessors (identical blob) do not refuse"; fixture JJ2 (keep-only deletion → rc 1, no novelty) and the J2 same-blob case pin it. Fix: carry the novelty qualifier (§4 text does).

**F3 · MAJOR — volatile live counts pinned unversioned in a durable row.** W1's README disclosure: "this lane holds 8 `refs/jj/keep` refs, 6 of them not ancestors of `master`, and 4 of those carry phantom deletions" — true at 5fa6017, stale at the landing HEAD: the same probes return **17 / 13** (unpushed 0 unchanged, probe #5). The "4 carry phantom deletions" figure is not re-derivable at this seat (needs a jj audit against the live lane — forbidden) and belongs to `JjTrialSouji.md:76`/entry §7, not to the coverage row. Fix: disclose the structural blindness (query pair + measured-at revision), drop rotting/unverifiable counts from the durable text.

**F4 · MAJOR — two broken evidence pointers in the row that must land.** (a) W1's F1-jj row cites `census/round-17/verification.json` — no such file exists (probe #9). (b) The F2 caveat row cites `../.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md` — from `corpus/README.md`, `../` is the lane root and the lane has no `.ufo/waves/hyaku` (probe #12); the reports are fleet-rooted, correct prefix `../../.ufo/…`. Both violate the index rule at `corpus/README.md:3–4` (a row claims its named evidence exists). Fix: cite the two `jj-receipts-*.txt` records (both exist, probe #8) and the corrected `../../` paths (content verified, probe #13).

**F5 · MINOR — broken insertion anchor, twice.** (a) W1 §2a says "Insert after `PROVINCE.md:23`", but the third Work-surfaces bullet wraps to :24; inserting after :23 splits the bullet mid-sentence. Bullets are :21–24; insert after :24. (b) W1's §2b text cross-references "`## Refuses` (PROVINCE.md:26)" inside the very section that shifts `## Refuses` to :32 — the inserted text must not carry line numbers that its own insertion invalidates. Fix: insert after :24; drop the ":26" from the inserted prose (§4 does).

**F6 · MINOR — cite drift.** The index rule is `corpus/README.md:3–4`, not W1's ":2-3" (probe #3).

**F7 · MINOR — stale frontier residue.** W1's Frontier line lists as unrun "a fixture that returns NOT-SAFE where `--not --all` used to return SAFE(metadata-prune)". That fixture landed and ran: `census/round-17/jj-receipts-ddb7347.txt` SUMMARY 20/0, J1 `NOT-SAFE … unique=1 … owner=keeprepo` (probe #8). The honest F1-jj residue is the keep-ref **expiry** measurement (entry Limits: no jj doc read states when jj drops `refs/jj/keep/*`) plus the disclosed conservative-refusal cost. Fix: rename the residue (§5 does).

**F8 · INFO — landing condition sharpened to three-way.** The entry is untracked and candidate-status (probe #10); SKILL.md contains no jj rule at all (probe #11); `PROVINCE.md:50–51` gates a Core move on an admitted entry **and** a SKILL rule. Therefore the README section + Core marking may land only in the same integration commit as (i) the tracked entry, (ii) the SKILL jj rule, (iii) the PROVINCE changes — otherwise ship variant B (§5b) and keep F1-jj frontier. W1's §3b condition covered only the entry; the SKILL half was missing.

**Verified holds (no re-litigation needed):** the no-new-F5 ruling (same question, second substrate; r13 precedent shape `PROVINCE.md:72–80` / `corpus/README.md:64–68`); the substrate-is-unnamed observation (probe #14: zero jj mentions in PROVINCE.md); every other PROVINCE/README anchor W1 cites; W1 risk 6 (doc drift if C3(b) is cut) does **not** fire — the change is landed in all three tools, so a present-tense PROVINCE section is sound; byte-identical-for-plain-repos is fixture- and code-backed.

Verdict on `ConnFrontierRows.md`: **PARTIAL** — ruling and file structure hold; the prose as written would misdocument landed behavior (F1, F2), rot on contact with the lane (F3), and cite missing or mispathed evidence (F4), plus two anchor drifts (F5, F6) and one stale residue claim (F7). All smallest fixes are incorporated in the final text below.

## 3. Context: exact current bytes at the insertion points (ddb7347 = working tree)

`PROVINCE.md:19–26`:
```
19 | ## Work surfaces (resolve and re-verify each round)
20 |
21 | - `$SHOKUNIN_ROOT` (fleet repo, cwd `.`)
22 | - `$SHOKUNIN_ROOT/<lane>-shokunin/` for every rostered + probation lane
23 | - GitHub remotes (`origin`) of the fleet and lane repos — read-only, for
24 |   `pushed` receipt checks only
25 |
26 | ## Refuses
```
`corpus/README.md:202–203` (EOF):
```
202 | SOURCES gains S043–S050 (six
    | mined, two rejected). No frontier row advances and no knowledge entry is
    | added: admitted knowledge stays five, K5 HELD, certification OFF.
203 | (end of file; last line is the Round 16 paragraph's final line)
```
(README :203 = "added: admitted knowledge stays five, K5 HELD, certification OFF." — the Round 16 paragraph's last line; append after it.)

## 4. Deliverable A — PROVINCE.md final text

**Change A1.** Insert the following bullet as the fourth Work-surfaces bullet **after line 24** (between :24 and the blank :25). Not after :23 (finding F5a).

```
- jj-colocated lane repos (`<lane>-shokunin/.jj` beside `.git` — every lane
  checked r17: kama, mado, tameshi, souji): HEAD is normally detached, the
  git index is not a signal, and `refs/jj/keep/*` pins jj-created commits
  as garbage-collection grace refs — never durable receipt roots.
  Re-resolve per round; a repo without `.jj`/`refs/jj` is a plain git repo
  and every receipt path is unchanged.
```

Wording constraints honored: no expiry/duration claim (entry Limits: keep-ref lifetime undocumented — do not add "expires after N"); "not a signal" is the entry §5 finding (jj ignores the staging area), not "jj owns the index"; the lane list names exactly what this round verified (W1's kama/mado/tameshi plus souji itself, probe #4); the root-set rule stays in the boundary section, not the bullet; the last sentence is the C3 testable boundary a verifier can execute (byte-identical plain-repo claim, tool-backed at verify :66–67/75–77, vault :50, quarantine :124–125).

**Change A2.** Append after line 93 (EOF; :99 after A1 shifts nothing before it — A1 adds 6 lines, so the section actually begins at :101 with a blank line separator) exactly:

```
## Round 17 boundary refinement (jj-colocated lanes)

Core now includes the bounded jj receipt-root rule (entry
`corpus/knowledge/jj-colocation-receipts.md`, the matching SKILL rule,
fixture `tests/fixtures/r17-jj-receipts.sh`): in a colocated repo the
durable receipt roots are every ref except `refs/jj/*`
(`for-each-ref --exclude='refs/jj/'`) — `refs/stash`, `refs/original` and
every other ref keep their pre-r17 root status, so a repository without
`refs/jj` produces byte-identical output. `refs/jj/keep/*` is jj's
garbage-collection grace ref, never a receipt of record: an
absent-worktree head held only by keep refs is NOT-SAFE, never
`SAFE(metadata-prune)`. The unpushed-touching refusal additionally refuses
a keep-only commit only when it introduces novel content at the target
(`C:<path>` exists and no remote-reachable blob at the path matches);
keep-only deletions and identical-content predecessors do not refuse, and
a git failure keeps the existing history-unverifiable path. The census
`unpushed` column stays branch-based and reads 0 while this lane holds
keep-only commits — disclosed, not widened. This is not a jj capability:
souji's tools never invoke `jj`, commits stay operator/helper-owned, and
`## Refuses` is unchanged. F1 as a whole stays frontier; how long jj keeps
a `refs/jj/keep/*` ref remains unmeasured.
```

Every sentence is code- or fixture-grounded: root set (verify :64/:854, vault :46–50/:1061, quarantine :115–116/:1155), NOT-SAFE-never-SAFE (verify :67–68, vault :48–49, quarantine :117–118), novelty gate + deletions/predecessors + rc-2 history-unverifiable (verify :69–77, vault :51–57, quarantine :119–125 and :974–975), branch-based unpushed (vault header :58ff), tools-never-invoke-jj (fixtures synthesize `refs/jj/keep/*` with `git update-ref` — vault :1425, quarantine JJ0–JJ2 :1693–1701). No sentence carries a line-number cross-ref (finding F5b). If the entry or SKILL rule does NOT land in the same commit, keep this section but replace its first two words: "Core now includes" → "Round 17 acquired" (the rule description stays true; only the Core marking is conditional).

## 5. Deliverable B — corpus/README.md final text

**Change B1.** Append after line 203 (EOF). Do NOT edit :39, :44 or :46 in place — the supersede-by-append pattern is the file's own convention (r13 did the same at :64–68). Exact text:

```
## Round 17 — jj-colocated lane repos (bounded receipt-root rule Core; F1 stays frontier)

Supersedes the r12 F1 row (:39) and the F1 next-step (:46) for the
jj-colocated subset only; both stand unchanged for plain repos. Landing
condition (index rule at :3-4): this section and its Core marking land
only in the same commit as `knowledge/jj-colocation-receipts.md` and the
SKILL jj rule; otherwise ship the variant-B row below and F1-jj stays
frontier.

| ground | status | entries / runnable evidence |
|---|---|---|
| F1-jj jj-colocated lane repos (edge class of F1) | Core: bounded receipt-root rule — durable roots exclude exactly `refs/jj/*`; keep-only novel-content refusal; plain repos byte-identical. F1 itself stays frontier; keep-ref expiry unmeasured | `knowledge/jj-colocation-receipts.md`; `../tests/fixtures/r17-jj-receipts.sh`; `../census/round-17/jj-receipts-base5fa6017.txt`, `../census/round-17/jj-receipts-ddb7347.txt` (SUMMARY 20/0) |
| F2 caveat, disclosed only: colocated repos inflate structure counts versus a plain clone (`references.others.count` 15 from `refs/jj/keep/*`; `objects.commits.count` 55 vs 44, sandbox) — no F2 capability claimed | observed, not claimed | `../../.ufo/waves/hyaku/jj-w1/reports/JjTrialSouji.md` step 5; `../../.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md` F3 |

Disclosure carried with the row, not in a footnote: the census `unpushed`
column is branch-based and reads 0 while this lane holds keep-only commits
(structural pair, measured at d7e648d: `git rev-list --count --branches
--not --remotes` → 0; `git for-each-ref refs/jj/keep` refs that are not
ancestors of `master` → 13 of 17). An absent-worktree head held only by a
keep ref is NOT-SAFE, never `SAFE(metadata-prune)`.

### Frontier (r17)

- F1 — plain repos: unchanged (:46). jj-colocated residue: a keep-ref
  expiry measurement (no jj doc read states when jj drops
  `refs/jj/keep/*`; entry Limits) — unrun. The conservative-refusal cost
  stays disclosed, not narrowed: a rewritten predecessor jj hides can
  refuse an artifact no branch carries.
- F2 — unchanged (:47); a colocated/plain byte-comparison is a
  precondition for any `git repo structure` baseline.

Variant B — entry or SKILL rule not landed in the same commit; ship this
row instead of the F1-jj row above:

| F1-jj jj-colocated lane repos | frontier, entry and SKILL rule unlanded; PROVINCE surface bullet added | — |
```

Differences from W1's draft, all four of its "deliberate lengths" preserved: (1) `F1 itself stays frontier` kept in the status cell and the F1 Frontier line; (2) `observed, not claimed` kept on the F2 caveat; (3) the `NOT-SAFE, never SAFE(metadata-prune)` pair kept verbatim; (4) `byte-identical` kept as the executable boundary. Fixes applied: verification.json citation replaced with the two existing jj-receipts records (F4a); `../.ufo/...` corrected to `../../.ufo/...` (F4b, probe #12); sandbox numbers retained only where the cited report states them (verified, probe #13); the live-lane disclosure rebuilt as a structural query pair pinned to d7e648d — 13 of 17 — replacing W1's rotting 8/6 and the unverifiable "4 phantom deletions" (F3); landing condition extended to the SKILL rule (F8); F1-jj residue renamed from the stale "fixture unrun" to the expiry measurement (F7).

## 6. L1 integration checklist

1. Land in ONE commit: tracked entry (with the F1 semantic correction applied to its §3 consequence and Operating rule 4 first — or an explicit note that the tools implement the minimal `--exclude='refs/jj/'` rule and heads/tags/remotes is a stricter unlanded variant), SKILL jj rule, PROVINCE changes A1+A2, README change B1. If either entry or SKILL rule slips: ship PROVINCE A1 + A2 (with the "Round 17 acquired" rewording), README B1 with the variant-B row.
2. Do not edit `corpus/README.md:39/46` in place; append only (B1 already obeys).
3. After landing verify: `git show <landed>:PROVINCE.md | grep -n '^## '` shows `## Round 17 boundary refinement (jj-colocated lanes)` as the last section and `## Refuses` at :32; `wc -l PROVINCE.md` = 93 + 6 + 23 = **122**; every path in the B1 table resolves via `git -C <lane> ls-tree -r --name-only <landed> -- <path>` (any miss falsifies the row under README:3–4).
4. Re-run the four live probes (#5) at the landing commit; if the keep/non-ancestor counts moved again, update only the parenthetical "measured at d7e648d … 13 of 17" to the new rev and numbers — the structural claim is what must not change.
5. Any other doc citing `PROVINCE.md:26` for `## Refuses` needs the :32 shift noted (A1 adds 6 lines above it).
6. Entry-owner advisory (not mine to edit): fix `jj-colocation-receipts.md` §3 consequence + Operating rule 4 to the landed every-ref-except-`refs/jj/*` semantics before commit (finding F1), and give the entry's `S0??` rows their real numbers when SOURCES lands S051–S063.

## 7. Residual risk and verification gaps

- The "4 of those carry phantom deletions" figure from W1's draft remains unverified at this seat (needs a jj audit on the live lane — forbidden); it is excluded from the durable text and stays citable at `JjTrialSouji.md:76` / entry §7, whose citation lines I did verify (probe #13).
- The `@-` label for the detached-HEAD commit is the entry's own `[INFERENCE]`; the bullet deliberately says only "normally detached" (observed, probe #4).
- I did not run the r17 fixture or any souji tool (forbidden against real dirs; ALLOWED-EXEC not granted to this seat); the 20/0 SUMMARY is taken from the committed record `census/round-17/jj-receipts-ddb7347.txt` and cross-checked against the landed code comments, not re-executed.
- Keep-ref counts (17/13) will drift with any jj activity in the lane; the disclosure is built so drift invalidates only the parenthetical, never the claim.
