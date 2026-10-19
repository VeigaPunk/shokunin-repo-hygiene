# Round 12 — mistakes mined (souji-shokunin, kaika W2 R12)

author: W2RoundSouji-8.R12Scribe (L2, leaf) · date: 2026-10-19 · lane HEAD `dcc8b9e8382b74825363c75d641798c81dceb387` (branch `kaika/round`)

Scope: souji's own mistakes, mined from round 1–11 lessons (`corpus/lessons/round-*.md`), the full
`LOG.md` including the 2026-10-19 operator sweep, and the operator-sweep evidence directory
(`census/operator-sweep-20261018/`). Start sets: STATE dossier §4 classes 1–10; ART dossier §7
M1–M8 lane analogues. Every row's evidence pointer was opened and verified in this session; the
verification command is in table 2.

Conventions:

- `kind`: `defect` (a wrong claim/action by the lane) · `process` (gate/dispatch/bookkeeping
  failure) · `honest-stop` (a refusal kept on purpose; evidence of taste, not a defect, per the
  round brief — captured-by may be the round's own lesson) · `caught` (found and corrected in
  round, calibration win).
- `captured-by`: an existing artifact at a verified `path:line` that could catch a recurrence —
  AGENTS.md / SKILL.md prose, a tool check, a tool selftest case id, or a `tests/` fixture. A rule
  that exists but has no check is listed with its pointer plus the note `no-check`. `none` = no
  such rule exists; near-misses are recorded as `none (partial: …)` and still count as `none`
  under the strict counting.
- Evidence pointers are lane-relative. Commands in table 2 were run **from the lane worktree as
  cwd** (this harness's `cd` is broken — orchestrator notice 2026-10-19; use the bash tool's `cwd`
  parameter or absolute paths, never a bare `cd`). Counts were run under `bash -c` (harness
  builtins caveat).
- Axis impact: no round's verdict block claims an axis harmed; these are claim-level failures plus
  process/evidence-hygiene failures.

## Table 1 — classes

| id | kind | class | evidence pointer | captured-by | fix (proposed QUALITY.md criterion or SKILL/AGENTS rule) |
|---|---|---|---|---|---|
| M01 | defect | Default branch hardcoded `origin/main` — pushed receipts unverifiable | corpus/lessons/round-1.md:11 | SKILL.md:21 (prose; tool resolves it) | criteria: a receipt resolves the default ref per repo, never hardcodes it |
| M02 | defect | `unreachable → NOT-SAFE` misfires on worktree metadata (absent dir IS the prune condition) | corpus/lessons/round-1.md:17 | SKILL.md:16 + selftest F4 (tools/souji-verify.sh:1235) | criteria: every receipt branches on artifact kind |
| M03 | defect | Reference sweeps self-pollute via the census's own fragments | corpus/lessons/round-1.md:20 | SKILL.md:23 (sweep excludes `census/**`, `tests/**`) | criteria: sweeps exclude the lane's own evidence surfaces |
| M04 | caught | Blind-seat disagreement with the final table (traced to D1, not missed evidence) | LOG.md:58 | none | criteria: blind pairs re-derive independently; disagreement is adjudicated with its cause named |
| M05 | process | Seat write-scope overstep (a seat synthesized and installed `tools/souji-verify.sh`) | corpus/lessons/round-2.md:8 | AGENTS.md:13 (prose, no-check) | rule: seat output is a named fragment; only the parent installs |
| M06 | process | Fixture/segment schema chaos — 2/10 cases emitted the contracted protocol; 4 shards used 3 schemas | corpus/lessons/round-2.md:12 + corpus/lessons/round-3.md:25 | none (partial: fixture schema field tests/fixtures/case-F3/expected.json:3, unenforced) | criteria: one machine-readable fixture/shard schema, checked by the runner |
| M07 | defect | Compliance checker over-strictness false-flagged clean impls (literal marker greps) | corpus/lessons/round-2.md:19 | none | criteria: compliance checks parse behavior, not spellings |
| M08 | caught | Signal hierarchy: impl-09 scored 60/60 on review probes but failed F7/F8 in 16 runner matrices | corpus/lessons/round-2.md:17 | tests/results/INSTALL.json:5 (recorded decision rule) | criteria: redundant independent execution outranks any single review |
| M09 | process | Approval list contained 15 already-removed rows; contract re-cut mid-round | corpus/lessons/round-3.md:22 | none | criteria: approval-list contracts tolerate already-removed rows |
| M10 | process | `/tmp` fixture residue ~2,100 dirs, routed outside the lane | corpus/lessons/round-3.md:27 | none (partial: runner scripts default `${TMPDIR:-/tmp}`, tests/runner-23.sh:38) | criteria: fixtures default `TMPDIR=/var/tmp` + quota preflight |
| M11 | defect | Metadata prune left 8 unreachable blobs in the owner's object store | corpus/lessons/round-3.md:29 | none | criteria: a prune receipt records object-level residue |
| M12 | honest-stop | 4/8 judges dissented NO-CLEAN-CANDIDATE over fixture rot; adjudicated by parent re-derivation, not majority | corpus/lessons/round-4.md:15 | corpus/lessons/round-4.md:17 (the round's lesson) | keep: dissent is preserved; adjudication by re-derivation |
| M13 | process | Seat-made fixture scripts rotted (exit 127, stale `/tmp` roots) | corpus/lessons/round-4.md:21 | none | criteria: fixtures self-contained or regenerated by a committed build script |
| M14 | defect | Symlink false-SAFE class — `find -type f` silently omitted symlinks from digests | corpus/lessons/round-5.md:9 | SKILL.md:22 (prose) + tools/souji-verify.sh:157 (r5 fix) | criteria: every path component a removal writes through gets an lstat gate, fail-closed |
| M15 | defect | Local-master pushed fallback — SAFE(pushed) from a local ref alone | corpus/lessons/round-5.md:15 | SKILL.md:21 (prose) + selftest E7 (tools/souji-verify.sh:1248) | criteria: no remote-tracking ref → `pushed-unverifiable` |
| M16 | defect | Deleted-file SAFE row (`logs_tier.txt`) — existence not re-checked at correction time | corpus/lessons/round-5.md:20 | SKILL.md:21 ("the path exists now") | criteria: a corrected verdict re-verifies existence at correction time |
| M17 | caught | LOG append-only violation (r1 commit 652b6f8 inserted a section mid-file) | corpus/lessons/round-5.md:32 | AGENTS.md:11 (prose, no-check) | criteria: LOG entries append at EOF; one order check over `git log -p LOG.md` |
| M18 | caught | GUI-launch incident — a harness spawned Obsidian, rewriting `.obsidian` metadata | corpus/lessons/round-5.md:35 | AGENTS.md:17 (prose, no-check) | keep + criteria: harness selftest refuses GUI/config writes |
| M19 | caught | SKILL.md receipt guidance drifted from installed tools | corpus/lessons/round-5.md:38 | SKILL.md:15 (behavior wins over prose; r6 reconciliation) | criteria: prose is reconciled in the round that finds the drift |
| M20 | defect | Pin risk — the 3 gd2d pins were left unlocked and bare-prune-eligible | corpus/lessons/round-5.md:26 | SKILL.md:100 (prose, no-check) + live lock state (3 locked, reason recorded) | rule: every pin carries `git worktree lock --reason`; surface rows cite lock state with a command |
| M21 | honest-stop | K1: a live tree is not classifiable to 0 — honest claim form is a timestamped snapshot RANGE | corpus/lessons/round-6.md:11 | corpus/lessons/round-6.md:11 (the round's lesson) | criteria: live targets yield snapshot ranges, not zero-claims |
| M22 | caught | Handoff draft carried claims the evidence didn't support — stripped | corpus/lessons/round-6.md:13 | AGENTS.md:15 (prose) | keep |
| M23 | process | 32/128 seat failures (waits + provider limits) gutted census/scratch shards mid-flight | corpus/lessons/round-6.md:8 | none | criteria: critical roles carry a redundancy budget |
| M24 | caught | Bare `--not --remotes` silently returns nothing on git 2.55 (would emit false pushed receipts) | corpus/lessons/round-6.md:20 | SKILL.md:21 (pitfall named in prose) | criteria: version-pinned idioms (Q1-style) |
| M25 | process | Evidence-layout drift — r2 evidence lives in `tests/results/`, `census/round-2/` does not exist | `ls census \| grep -c '^round-2$'` → 0 | none | criteria: one evidence layout per round (`census/round-N/`); README claim corrected |
| M26 | honest-stop | r7: receipts denied every candidate; nothing forced; quarantine left UNEXERCISED | corpus/lessons/round-7.md:4 | corpus/lessons/round-7.md:30 (the round's lesson) | keep: never manufacture removal claims |
| M27 | honest-stop | Lane remote 404 — every pushed receipt in the lane was unverifiable until the operator created/origin landed | corpus/lessons/round-7.md:15 | none (external, operator-owned) | keep: report the gate, do not work around it |
| M28 | caught | Parent column misread (lore "worktrees=3" was unpushed=3) caught by blind seat S02 | corpus/lessons/round-7.md:19 | none | criteria: blind pairs re-derive; a misread candidate is refused, never manufactured |
| M29 | caught | Parent awk bug produced empty receipt pins; the tool's fail-closed refusal caught it | corpus/lessons/round-8.md:31 | tools/souji-quarantine.sh:652 + selftest U5 (tools/souji-quarantine.sh:1478) | criteria: pin lists get schema-validated before use |
| M30 | process | Host `/tmp` hit DISK QUOTA mid-round; fixture runs corrupted, two seat failures misattributed | corpus/lessons/round-8.md:24 | none (partial: tests/runner-*.sh default `${TMPDIR:-/tmp}`) | criteria: quota preflight; fixtures under `/var/tmp` |
| M31 | process | r7 "gate2 contradiction" dissolved — `.tmp` was never a scratch class (taxonomy misunderstanding) | corpus/lessons/round-8.md:28 | SKILL.md:23 (taxonomy names `*.tmp` as excluded) | criteria: taxonomy drift is reconciled when a contradiction dissolves |
| M32 | defect | r9 false-SAFE class union (23 classes): locale `id_*` bypass · disappearing git · hidden live refs · ledger revocation-after-capture · linked-worktree HEAD skew · non-`*-shokunin` owner names · index-write contract | corpus/lessons/round-9.md:8 | tools only, partial — LC_ALL/GIT_OPTIONAL_LOCKS tools/souji-verify.sh:62; ledger pin tools/souji-quarantine.sh:303,340,369; owner-name + registration conflicts scan tools/souji-verify.sh:962; gaps: no `command -v git` guard in souji-quarantine.sh (exists in verify:1308, census:818); SKILL.md has no pattern for any of them (`grep -cE "nested\|NUL\|maintenance" SKILL.md` → 0) | criteria: every closed reproducible class lands as a SKILL.md error pattern or a `tests/` fixture in the round that closes it |
| M33 | defect | NUL/tab authorization forgery — NUL-in-list and tab-spliced rows read as SAFE | corpus/lessons/round-9.md:10 | tools only: tools/souji-quarantine.sh:637 (NUL gate), :652 (malformed row) + selftest U5 (:1478) | criteria: paths travel NUL-delimited end to end; human-readable formats are never parsed |
| M34 | defect | Nested dirty/unpushed repos deleted on the strength of an ancestor's receipt | corpus/lessons/round-9.md:12 | tools only: tools/souji-verify.sh:418 (`nested-repo-or-unverifiable`) | criteria: a nested `.git` is its own receipt scope and never inherits one |
| M35 | defect | TOCTTOU — a fresh child inside an aged container was DELETED (r10 G2, 6/6 reproduced) | census/round-10/S13-fragment.md:72 | SKILL.md:46 (second check — partial; no descendant rule) | criteria: the second check pins each descendant's length, mtime and digest |
| M36 | honest-stop | r9 dissent-24 preserved (rubric zeroing semantics, dirty-file SAFE reading, exploration-vs-coverage) | corpus/lessons/round-9.md:29 | corpus/lessons/round-9.md:29 (the round's lesson) | keep: dissent is recorded, never re-rolled |
| M37 | caught | SCORECARD prose said 6/7 where rows said 8/7; judges caught it; corrected r9 | SCORECARD.md:45 | none | criteria: SCORECARD prose and tables agree — one grep over both |
| M38 | defect | `census --compare` accepted empty/near-empty priors (3 unsafe outcomes, the last open r9 class) | corpus/lessons/round-10.md:4 | tools/souji-census.sh:359 (hard error) + selftest cases `bad/empty/blank-lead/blank-before-header` (:767) | criteria: every contract refusal ships with a regression fixture |
| M39 | process | Hyper provider ~14 min/agent — functionally unusable for batch work (operator test) | corpus/lessons/round-10.md:16 | none | record operator routing results; criteria: routing notes name the measured failure |
| M40 | defect | Certifier shared-relay overwrites (`cert-16.json`); CERTIFIED verdicts attached to bytes other than those measured | corpus/lessons/round-11.md:14 | none | criteria: each certifier writes its own fragment; verdicts attach only to hash-verified installed bytes |
| M41 | defect | Candidate-selection rule contradicted the class under test (most selftest checks picked a candidate that fails it) | corpus/lessons/round-11.md:16 | none | criteria: the selection rule must exercise the class being certified |
| M42 | defect | Pre-removal `git add -A` swept 10 live `.scratch/*.out`, the in-flight r11 report and a `.gitignore.tmp` into hygiene commit e20f4fa (two corrective commits: 9c220bf, 99819ec) | LOG.md:381 | none (partial: the idiom is normalized by tool selftests — tools/souji-verify.sh:1077, tools/souji-quarantine.sh:1225, tools/souji-vault-verify.sh:1276) | rule: hygiene commits stage exactly the approved pathspec list; never `git add -A` over live lanes |
| M43 | defect | Quarantine staging loop hung after 3 files to the 20-min driver timeout; the tool has no per-target bound | LOG.md:373 | none (`grep -c timeout tools/souji-quarantine.sh` → 0) | rule: bounded per-target staging; fail-closed abort with diagnostics |
| M44 | defect | 3 orphaned judge fixtures stuck ~9 h on `sha256sum` of a FIFO (`wait_for_partner`), ppid=systemd | LOG.md:403 | none (partial: vault-verify rejects non-regular targets at tools/souji-vault-verify.sh:608; the stuck readers were elsewhere) | criteria: digest readers accept regular files only, under a bounded timeout |
| M45 | defect | Own debris committed at the lane root — census stderr captures `err4.nl2`/`err4.z2` (tracked), `.ufo-reports-placeholder` (0 B), `.scratch/s29-freeze-dir.txt`, `results/.s54-write-probe.txt` (all tracked in 1ccf11b) | err4.nl2:1 + commit 1ccf11b | none | rule: tool diagnostics land under `census/round-N/`, never the lane root; no-receipt debris is swept before any hygiene commit |
| M46 | caught | 2 quarantine-staged files (launch-chousa/kagi.json) were missing post-timeout; the hash-vs-origin second check caught it and both were restored from origin | LOG.md:377 | SKILL.md:46 (second check) + manual protocol | keep: hash-vs-origin second check is the equivalent-or-stronger path when the tool hangs |
| M47 | honest-stop | Sweep: kotodama `.scratch` — every child receipt-denied (newest mtime < 24 h; big three additionally `secrets-refusal` → kagi) | LOG.md:411 | census/round-6/kotodama-scratch-handoff.md (exists) | keep: re-sweep when the tree ages past 24 h (scheduled ≈2026-10-20) |
| M48 | honest-stop | Sweep: 107 pushed-receipt strays denied at the pre-removal reference gate (cited by 8+ reports, plans, PREDICTIONS/HYGIENE) | LOG.md:420 | SKILL.md:23 (zero-live-references gate) + census/operator-sweep-20261018/stay-strays-verdicts.tsv | keep: reference gate outranks the receipt |
| M49 | honest-stop | Sweep: `.tower/comms/log/activity.log` (engine SAFE/stale) refused as operator-tooling runtime | LOG.md:421 | none | rule: operator-tooling runtime is report-only, refused by zone spirit |
| M50 | defect | ShellCheck gates ran `-S error`; SC2115/SC2114 are warnings, so empty-variable removal hazards are invisible; no shellcheck gate exists under `tests/` | census/round-10/S02-cluster-A.md:19 | none (partial: shellcheck appears only as `disable` comments in two drafts) | criteria: removal/verification shell passes `shellcheck -S warning` incl. SC2115/SC2114 |
| M51 | defect | Latent: on git ≥2.54 a plain `git commit` (quarantine is "a normal commit", SKILL.md:44) can auto-run maintenance with the geometric default and prune worktree metadata with no souji receipt | tools/souji-census.impl-46.sh:111 (the only guard in the tree, a draft) | none (partial: draft guard above; r12 guard fixture landed by a sibling seat after baseline) | rule: hygiene commits run `git -c maintenance.auto=false`; pinned registrations carry `git worktree lock --reason` |
| M52 | process | Bookkeeping surfaces went stale — SCORECARD `## Planned` stops at r5 while r6–r11 ran; certification note says "until the r10 hardening" while r10+r11 happened (no-relay carry recorded only in LOG) | SCORECARD.md:35 + SCORECARD.md:50 / LOG.md:356 | none | rule: the closing commit updates `## Planned` and the certification note; one grep per round |

Tally by kind: defect 22 · process 11 · honest-stop 8 · caught 11 — total 52.
`captured-by = none`: **24 of 52** (M04, M06, M07, M09, M10, M11, M13, M23, M25, M27, M28, M30, M37,
M39, M40, M41, M42, M43, M44, M45, M49, M50, M51, M52). Every `none` that has a near-miss carries
a `partial:` pointer; none of those pointers is a check.

## Table 2 — evidence verification (run from the lane worktree as cwd)

| id | command | observed |
|---|---|---|
| M01 | bash -c "grep -n 'hardcoded' corpus/lessons/round-1.md" | `11:- D1: receipt procedure hardcoded \`origin/main\`; fleet default branch is` |
| M02 | bash -c "grep -n 'artifact kind' corpus/lessons/round-1.md" | `17:  the prune condition. r2's tool must branch on artifact kind.` |
| M03 | bash -c "grep -n 'self-pollutes' corpus/lessons/round-1.md" | `20:  self-pollutes the zero-references condition (this falsified 5 author` |
| M04 | bash -c "grep -n 'Blind seats S54' LOG.md" | `58:21 metadata-prune + 2 root strays), 0 false-SAFE survive. Blind seats S54–61` |
| M05 | bash -c "grep -n 'write-scope overstep' corpus/lessons/round-2.md" | `8:- **Seat write-scope overstep**: a seat synthesized and installed its own` |
| M06 | bash -c "grep -n 'Fixture interface chaos' corpus/lessons/round-2.md" + bash -c "grep -n '3 different schemas' corpus/lessons/round-3.md" | `12:- **Fixture interface chaos**: only 2/10 fixture cases emitted the` + `25:- 4 approval shards used 3 different schemas — next round: one TSV schema` |
| M07 | bash -c "grep -n 'over-strictness' corpus/lessons/round-2.md" | `19:- **Compliance checker over-strictness class**: literal D1/D2/D3 marker` |
| M08 | bash -c "grep -n 'redundant independent' corpus/lessons/round-2.md" | `17:  failed F7/F8 stale receipts in 16 runner matrices — redundant independent` |
| M09 | bash -c "grep -n 'already removed' corpus/lessons/round-3.md" | `22:- 15 of the 111 approval targets were already removed by fleet commit` |
| M10 | bash -c "grep -n 'fixture residue' corpus/lessons/round-3.md" | `27:- \`/tmp\` accumulates fixture residue (~2,100 dirs from r2) — host hygiene` |
| M11 | bash -c "grep -n 'unreachable blobs' corpus/lessons/round-3.md" | `29:- r87-M1-myth prune leaves 8 unreachable blobs in lore's object store` |
| M12 | bash -c "grep -n 'NO-CLEAN-CANDIDATE' corpus/lessons/round-4.md" | `15:  NO-CLEAN-CANDIDATE (stale /tmp fixture roots and schema variance); the` |
| M13 | bash -c "grep -n 'rotted fast' corpus/lessons/round-4.md" | `21:- Seat-made fixture scripts rotted fast (exit 127, stale /tmp roots):` |
| M14 | bash -c "grep -n 'Symlink false-SAFE' corpus/lessons/round-5.md" | `9:1. **Symlink false-SAFE class (both tools)** — \`dir_digest\` used` |
| M15 | bash -c "grep -n 'Local-master pushed fallback' corpus/lessons/round-5.md" | `15:2. **Local-master pushed fallback (both tools)** — zero remote-tracking` |
| M16 | bash -c "grep -n 'logs_tier' corpus/lessons/round-5.md" | `20:3. **r1 false-SAFE row (logs_tier.txt)** — recorded SAFE(pushed) after` |
| M17 | bash -c "grep -n 'append-only' corpus/lessons/round-5.md" | `32:- r1 commit 652b6f8 inserted a LOG.md section mid-file — an append-only` |
| M18 | bash -c "grep -n 'Obsidian app' corpus/lessons/round-5.md" | `35:  harness launching the Obsidian app during adversarial tests (config` |
| M19 | bash -c "grep -n 'drifted' corpus/lessons/round-5.md" | `38:- SKILL.md receipt guidance drifted from the installed tools — routed to` |
| M20 | bash -c "grep -n 'Pin risk' corpus/lessons/round-5.md" | `26:4. **Pin risk (r3 follow-up)** — the 3 gd2d named-branch registrations` |
| M21 | bash -c "grep -n 'moving target' corpus/lessons/round-6.md" | `11:  580k/20.56GiB) — a moving target is not classifiable to 0; the honest` |
| M22 | bash -c "grep -n 'stripped' corpus/lessons/round-6.md" | `13:- One handoff draft carried claims the evidence didn't support — stripped.` |
| M23 | bash -c "grep -n 'seat failures' corpus/lessons/round-6.md" | `8:- 32/128 seat failures (waits + provider limits) gutted the census/scratch` |
| M24 | bash -c "grep -n 'returns nothing on git 2.55' corpus/lessons/round-6.md" | `20:  returns nothing on git 2.55 — recorded as a tool-authors' pitfall).` |
| M25 | bash -c "ls census \| grep -c '^round-2$'" | `0` |
| M26 | bash -c "grep -n 'Nothing was forced' corpus/lessons/round-7.md" | `4:verified, O1 NOT-MET.** Nothing was forced.` |
| M27 | bash -c "grep -n '404' corpus/lessons/round-7.md" | `15:  shokunin-repo-hygiene\` → 404, never pushed — operator-owned creation).` |
| M28 | bash -c "grep -n 'column misread' corpus/lessons/round-7.md" | `19:- **Calibration win:** S02 caught the parent's column misread (lore` |
| M29 | bash -c "grep -n 'awk unquoted' corpus/lessons/round-8.md" | `31:- Parent bug caught in verification: awk unquoted variable produced` |
| M30 | bash -c "grep -n 'DISK QUOTA' corpus/lessons/round-8.md" | `24:- Host /tmp hit DISK QUOTA mid-round; fixture runs corrupted (two seat` |
| M31 | bash -c "grep -n 'gate2 contradiction' corpus/lessons/round-8.md" | `28:- r7's \"gate2 contradiction\" dissolved: impl-01's dirty gate is` |
| M32 | bash -c "grep -n 'linked-worktree' corpus/lessons/round-9.md" + bash -c "grep -cE 'nested\|NUL\|maintenance' SKILL.md" | `14:revalidation; linked-worktree HEADs making unique=0 wrong on git 2.55;` + `0` |
| M33 | bash -c "grep -n 'NUL-in-list' corpus/lessons/round-9.md" | `10:ledger revocation after row capture (delete-after-revoke); NUL-in-list` |
| M34 | bash -c "grep -n 'nested dirty' corpus/lessons/round-9.md" | `12:tab-spliced rows read as SAFE; nested dirty/unpushed repos deleted via` |
| M35 | bash -c "grep -n 'fresh child in aged container' census/round-10/S13-fragment.md" | `72:\| fresh child in aged container \| SAFE \| **DELETED**, survives=False \| NOT-SAFE \| NOT-AUTHORIZED, survives=True \|` |
| M36 | bash -c "grep -n 'dissent-24' corpus/lessons/round-9.md" | `29:- Dissent preserved (dissent-24.md): rubric zeroing semantics, dirty-file` |
| M37 | bash -c "grep -n 'formerly' SCORECARD.md" | `45:rows above: coverage 8, operability 8, calibration 7 (this prose formerly` |
| M38 | bash -c "grep -n 'empty/near-empty' corpus/lessons/round-10.md" | `4:census --compare accepts empty/near-empty prior censuses); certification` |
| M39 | bash -c "grep -n 'Hyper lane' corpus/lessons/round-10.md" | `16:- Hyper lane tested for the operator: functional but ~14 min/agent —` |
| M40 | bash -c "grep -n 'shared relay' corpus/lessons/round-11.md" | `14:  cert-16.json was used as a shared relay and overwritten repeatedly;` |
| M41 | bash -c "grep -n 'candidate-selection' corpus/lessons/round-11.md" | `16:  one candidate-selection rule (most selftest checks) picked a candidate` |
| M42 | bash -c "grep -n 'add -A' LOG.md" | `381:(\`9c220bf\`, \`99819ec\`): \`git add -A\` had swept in 10 live \`.scratch/*.out\`` (also `432`) |
| M43 | bash -c "grep -n 'staged 3 files then hung' LOG.md" | `373:\`resume-verdicts.tsv\`). Flow: souji-quarantine.sh staged 3 files then hung` |
| M44 | bash -c "grep -n 'FIFO' LOG.md" | `403:ppid=systemd, do_wait) each stuck on \`sha256sum\` of a **FIFO**` |
| M45 | bash -c "grep -n 'compare file header mismatch' err4.nl2" + bash -c "git log --oneline -1 -- err4.nl2" | `1:souji-census: compare file header mismatch (want 7 census columns)` + `1ccf11b pre-reboot sweep: remaining r11 fragments + results` |
| M46 | bash -c "grep -n 'restored from origin' LOG.md" | `377:(launch-chousa/kagi.json) missing post-timeout, **restored from origin** and` |
| M47 | bash -c "grep -n 'receipts deny every child' LOG.md" | `411:B/s) but receipts deny every child — 256 children all have newest-file mtime` |
| M48 | bash -c "grep -n 'stay-strays' LOG.md" | `420:logs cited by PREDICTIONS.md/HYGIENE.md (\`stay-strays-verdicts.tsv\`).` |
| M49 | bash -c "grep -n 'activity.log' LOG.md" | `421:(3) \`.tower/comms/log/activity.log\` (engine SAFE/stale) treated as` |
| M50 | bash -c "grep -n 'shellcheck' census/round-10/S02-cluster-A.md" | `19:All three exit 0; \`bash -n\` and \`shellcheck -x -S error\` clean.` |
| M51 | bash -c "grep -n 'maintenance.auto' tools/souji-census.impl-46.sh" | `111:    -c maintenance.auto=false \` |
| M52 | bash -c "grep -n 'r5 (verification round' SCORECARD.md" + bash -c "grep -n 'no-relay protocol' LOG.md" | `35:- **r5 (verification round, all axes):** audit rounds 1–4 verdicts and` + `356:stay UNRATED. Re-certification under a no-relay protocol is the next` |

## Table 3 — capture verification (the `captured-by` pointers)

| pointer | command | observed |
|---|---|---|
| SKILL.md:21 | bash -c "grep -n 'resolved default ref' SKILL.md" | `21:\| \`pushed\` \| the path exists now; … the resolved default ref (…` |
| SKILL.md:22 | bash -c "grep -n 'Symlinks in a digest scope' SKILL.md" | `22:… Symlinks in a digest scope → \`symlink-present\`. No row → no qualification. \|` |
| SKILL.md:23 | bash -c "grep -n 'sweep excludes' SKILL.md" | `23:\| \`stale\` \| … sweep excludes \`.git\`, \`souji-shokunin/census/**\`, …` |
| SKILL.md:16 | bash -c "grep -n 'metadata-prune' SKILL.md" | `16:\`SAFE(metadata-prune)\` for dead worktree registrations and fail-closed` |
| SKILL.md:15 | bash -c "grep -n 'behavior wins' SKILL.md" | `15:behavior wins over this prose; r6 reconciliation). Verdicts also include` |
| SKILL.md:44 | bash -c "grep -n 'normal commit' SKILL.md" | `44:… quarantine is a normal commit in the owning repo.` |
| SKILL.md:46 | bash -c "grep -n 'Second check' SKILL.md" | `46:5. Second check: re-run the receipt command; receipt must still hold.` |
| SKILL.md:100 | bash -c "grep -n 'PINNED' SKILL.md" | `100:  registrations PINNED (locks held; each branch has 1 unpushed commit) —` |
| SKILL.md (prose-only, no-check) rows M17/M18 | bash -c "grep -n 'append-only' AGENTS.md" + bash -c "grep -n 'stay headless' AGENTS.md" | `11:- Every change is recorded in an append-only LOG.md entry with the evidence` + `17:- Seat harnesses (adversarial test rigs) stay headless: launching GUI apps` |
| AGENTS.md:13/15 | bash -c "grep -n 'assigned evidence fragments' AGENTS.md" + bash -c "grep -n 'Never fabricate' AGENTS.md" | `13:  assigned evidence fragments; the parent integrates them into LOG.md after` + `15:- Never fabricate evidence: cite a file, a command output, or a commit;` |
| tools/souji-verify.sh:157 | bash -c "grep -n 'r5 fix' tools/souji-verify.sh" | `157:  # r5 fix: any symlink in the digest scope fails closed (return 2);` (also `148`) |
| tools/souji-verify.sh:1235 | bash -c "grep -n 'st_case F4' tools/souji-verify.sh" | `1235:  st_case F4 SAFE metadata-prune \"dir=absent unique=0\" \"\$ST_TMP/wt-f4\"` |
| tools/souji-verify.sh:1248 | bash -c "grep -n 'st_case E7' tools/souji-verify.sh" | `1248:  st_case E7 NOT-SAFE pushed-unverifiable \"unverifiable\" …` |
| tools/souji-verify.sh:418 | bash -c "grep -n 'nested-repo-or-unverifiable' tools/souji-verify.sh" | `418:      R_RECEIPT=nested-repo-or-unverifiable` |
| tools/souji-verify.sh:62 | bash -c "grep -n 'GIT_OPTIONAL_LOCKS=0' tools/souji-verify.sh" | `62:export LC_ALL=C GIT_OPTIONAL_LOCKS=0` |
| tools/souji-verify.sh:962 | bash -c "grep -n 'not named' tools/souji-verify.sh" | `962:# A linked worktree whose owner directory is not named \`*-shokunin\` was never` |
| tools/souji-verify.sh:1308 / tools/souji-census.sh:818 | bash -c "grep -n 'command -v git' tools/souji-verify.sh tools/souji-census.sh" | `tools/souji-verify.sh:1308:` / `tools/souji-census.sh:818:` (absent in souji-quarantine.sh) |
| tools/souji-quarantine.sh:637/652/1478 | bash -c "grep -n 'NUL byte' tools/souji-quarantine.sh" + bash -c "grep -n 'U5 malformed' tools/souji-quarantine.sh" | `637:      usage_err \"list contains a NUL byte\"` + `1478:  st_check \"U5 malformed list row rc=2\" …` |
| tools/souji-quarantine.sh:340 | bash -c "grep -n 'ledger_pin=\$(file_sha' tools/souji-quarantine.sh" | `340:      ledger_pin=$(file_sha \"$SV_LEDGER\")` (re-check at `:369`) |
| tools/souji-census.sh:359/767 | bash -c "grep -n 'hard error (exit 2)' tools/souji-census.sh" + bash -c "grep -n 'compare baseline exits 2' tools/souji-census.sh" | `359:# an empty, blank-led or malformed baseline is a hard error (exit 2) — a` + `767:    if [ \"\$cmp_st\" = 2 ]; then st_ok \"$f compare baseline exits 2\"` |
| tools/souji-census.sh:73 | bash -c "grep -n 'GIT_OPTIONAL_LOCKS' tools/souji-census.sh" | `73:export GIT_OPTIONAL_LOCKS=0` |
| tools/souji-quarantine.sh timeout absence | bash -c "grep -c timeout tools/souji-quarantine.sh" | `0` |
| add -A idiom (partial) | bash -c "grep -n 'add -A' tools/souji-verify.sh tools/souji-quarantine.sh tools/souji-vault-verify.sh" | `1077`, `1225`, `1276` |
| tools/souji-quarantine.sh:652 selftest U5 | (see row M29 above) | `1478` |
| tests/fixtures/case-F3/expected.json:3 | bash -c "grep -n 'schema' tests/fixtures/case-F3/expected.json" | `3:  \"schema\": \"souji-verify-fixture/1\",` |
| tests/results/INSTALL.json:5 | bash -c "grep -n 'decision_rule' tests/results/INSTALL.json" | `5: \"decision_rule\": \"runner pass-rate (16 matrices) -> review probes (36/impl) -> …\"` |
| tests/runner-23.sh:38 | bash -c "grep -n TMPDIR tests/runner-23.sh" | `38:TMP=\"$(mktemp -d \"${TMPDIR:-/tmp}/souji-runner-23.XXXXXX\")\"` |
| corpus/lessons/round-4.md:17 | bash -c "grep -n 'Parent re-ran' corpus/lessons/round-4.md" | `17:  rationales. Parent re-ran a decisive 4-case battery + real-vault live` |
| corpus/lessons/round-6.md:11 | (see row M21 above) | `11:… a moving target is not classifiable to 0; the honest` |
| corpus/lessons/round-7.md:30 | bash -c "grep -n 'A hygiene lane' corpus/lessons/round-7.md" | `30:A hygiene lane that has done its job arrives exactly here: **nothing left` |
| corpus/lessons/round-9.md:29 | (see row M36 above) | `29:- Dissent preserved (dissent-24.md): …` |
| census/round-6/kotodama-scratch-handoff.md | bash -c "test -f census/round-6/kotodama-scratch-handoff.md; echo $?" | `0` |
| census/operator-sweep-20261018/stay-strays-verdicts.tsv | bash -c "test -f census/operator-sweep-20261018/stay-strays-verdicts.tsv; echo $?" | `0` |
| live gd2d locks (M20) | bash -c "GIT_OPTIONAL_LOCKS=0 git -C /home/vgpnk/Projects/shokunin/game-dev-2d-shokunin worktree list --porcelain \| grep -c '^locked'" | `3` (reason: "souji r5: pinned until game-dev-2d pushes wt branches or operator dispositions") |
| tools/souji-census.impl-46.sh:111 | (see row M51 above) | `111:    -c maintenance.auto=false \` |
| tests/fixtures/r12-maintenance-guard.sh (state at write time) | bash -c "test -f tests/fixtures/r12-maintenance-guard.sh; echo $?" | `0` — landed by a sibling L2 after the dcc8b9e baseline |

## Notes, corrections and limits

**Honest stops (M12, M21, M26, M27, M36, M47, M48, M49).** They are counted separately and are
evidence of taste, per the round brief: each is a refusal that held the line (dissent preserved,
moving target not claimed to 0, nothing forced, external gate reported, reference gate outranking
the receipt). Their `captured-by` is the round's lesson (or `none` where the stop was situational
judgement, M27/M49).

**Operator sweep provenance (verified read-only at the fleet root).** `git -C
/home/vgpnk/Projects/shokunin log --oneline -1 <sha>`: `9c220bf` = "souji: correction — untrack
files swept in by e20f4fa (git add -A overshoot)"; `99819ec` = "souji: drop .gitignore.tmp
scaffold accidentally committed in 9c220bf"; `e20f4fa` = "souji: remove 96 pushed-receipt
checkpoint artifacts (operator sweep 2026-10-18)". All three exist and match LOG.md:381-383.

**STATE/ART claims found wrong or imprecise (found while verifying):**

1. **ART §7 M4 — "Already captured? No" is wrong as stated.** The nested-repository class *is*
   captured in the tools since r10: `tools/souji-verify.sh:418` emits
   `nested-repo-or-unverifiable` (same gate in `tools/souji-vault-verify.sh`, and the S17/S18
   nested-metadata gate in `souji-quarantine.sh`). Only SKILL.md lacks the pattern — which is what
   ART's own grep actually measured.
2. **ART §7 M3/M5 — "captured in the tools" is true but incomplete**: the tools-only capture has a
   gap. `souji-quarantine.sh` has **no** `command -v git` presence guard (verify:1308 and
   census:818 have one), so the "disappearing git" sub-class of M32 is only half-closed in the
   flow that stages and deletes.
3. **ART §8 D7 (gd2d lock ambiguity) — resolved by measurement.** `worktree list --porcelain`
   shows 5 registrations: 3 locked with the r5 reason text (wt-r98/99/100), 2 unlocked = the main
   checkout and the campaign lane worktree `.tower/worktrees/kaika/game-dev-2d-shokunin`
   (branch `kaika/round`). SKILL.md:100 is current; LOG.md:134-136 describes the r3 state before
   the r5 re-lock.
4. **STATE §5.6 — "strays at lane root (reported, never touched)" understates them:** `err4.nl2`,
   `err4.z2`, `.ufo-reports-placeholder`, `.scratch/s29-freeze-dir.txt` and
   `results/.s54-write-probe.txt` are all **tracked and committed** (commit `1ccf11b` "pre-reboot
   sweep: remaining r11 fragments + results"), i.e. the lane's own debugging residue entered its
   history, not merely its worktree (row M45).
5. **ART §7 M6 pointer verified**: `census/round-10/S02-cluster-A.md:19` records
   `shellcheck -x -S error` as the clean gate, so the SC2115/SC2114 invisibility is real; there is
   no shellcheck invocation anywhere under `tests/` (row M50).
6. **Baseline nuance (not a dossier error):** the r12 baseline (`census/round-12/baseline.txt`,
   measured on `dcc8b9e`) records `tests/fixtures/r12-maintenance-guard.sh` as absent; at my
   measurement time the file exists — a sibling L2 landed it during this wave. The "before" state
   in the C3 claim belongs to the baseline, not to the current worktree.

**Limits.** (a) M32 aggregates 23 judge classes into one row; individual tool fixes were not
re-verified beyond the pointers listed (the r9/r10/r11 lessons and the r10 certifier suites are the
authority). (b) M44's link to the failed manual staging (LOG.md:373-378) is documented in LOG but
the FIFO readers' provenance (`souji-vault-verify.impl-17.sh` fixtures) is quoted from LOG, not
re-derived. (c) `[INFERENCE]` M51's consequence chain (auto-maintenance pruning worktree
registrations on git ≥2.54) is source-derived in ART §7 M8 and is the subject of this round's C3
fixture; it is not re-run here. (d) No live target was mutated while verifying; the only commands
against repos outside the lane were read-only `git -C`, with `GIT_OPTIONAL_LOCKS=0` where the
target was live.
