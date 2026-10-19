# Round 12 — gate record (kaika campaign, 2026-10-19)

Steered round 12 (orchestrator steer table `fleet-ledger/.ufo/waves/kaika/steer.md`). The
operator cancelled the 12-round goal after r11; r11's carry (re-certification under a
no-relay protocol, `corpus/lessons/round-11.md:22-24`) is NOT this round's work — it stays
Planned, certification stays OFF. Evidence fragments: `census/round-12/`.

Declared claims (restructured after the r12 critic, `census/round-12/critic.md`, so each
verifies alone):
- **C1 calibration** (lowest axis, 7): mine souji's own mistakes into `## Mistakes` below and
  give every unlearned class a captured-by criterion (`corpus/QUALITY.md` Q5–Q14). Measured as
  *mapped-criteria coverage* (a row counts when its captured-by cell names a rule), not as
  demonstrated catches: 28/52 → 51/53 (command below). Enforcement is separate — e.g. M43's
  Q8 has no tool fix yet.
- **C2 coverage + capability**: `corpus/SOURCES.md` (contract v1) and 5 knowledge entries on
  three new frontier rows (F1, F3, F4). Admission rests on the seed bar Q1–Q4 (+ Q15 for K5)
  and on re-opened sources; K1 is admitted on tagged git source, its recheck is a source grep,
  and C3's gate is cited only as corroboration. The census verdict holds without the C3-derived
  row S031 (32 rows, same checks). Counts:
  `bash -c 'for f in corpus/knowledge/*.md; do head -3 "$f" | grep -cE "^(source|verified-at|recheck):"; done' | grep -c '^3$'`
  → 0 at dcc8b9e, 5 now; frontier rows holding ≥1 entry:
  `grep -cE '^\| F[0-9] .*\| frontier, entr' corpus/README.md` → 0 at dcc8b9e (no table), 3 now.
- **C3 operability**: `tests/fixtures/r12-maintenance-guard.sh`, a registered gate (exit 0/1/2,
  `--selftest` asserts its pinned finding ids), plus executable Pre-quarantine checklist rows.
  Counts: `bash tests/fixtures/r12-maintenance-guard.sh; echo $?` → absent at dcc8b9e, 0 now;
  `grep -cE 'maintenance\.auto=false|rev-parse --show-toplevel|worktree lock --reason' SKILL.md`
  → 0 at dcc8b9e, 3 now.

## Incident

During this round an L2 seat's shell `cd` failed silently (the harness aliases `cd` to a
missing function, `type cd` → "cd is aliased to `__fnmcd'"), so its first fixture probe ran
in the FLEET ROOT main checkout: 4 throwaway commits on master (c095ea1 "base" adding file
`f`, 551478a, 4b2123b, b21278d; author `r12 <r12@test>`; read-only check
`git -C /home/vgpnk/Projects/shokunin reflog -8`), two throwaway worktree registrations
created there and, per that seat's report, then pruned by git's own auto-maintenance (the very hazard C3 gates; both are absent from the fleet-root `worktree list`), and
three seats' source downloads landed at the fleet root (RelNotes-2.54.0.txt, rmlint.1.rst,
dedupe.rs, jdupes-README.md, gc-v2.53.0.c, gc-v2.54.0.c, `f`; four more were written and
deleted by their seat). Nothing was pushed. The lane did not touch the fleet root: the
L1 reported the exact list to the orchestrator, which owns the repair. Row M53 below; rules
Q7(a), Q13 and `SKILL.md:98`.

## Mistakes

Rows M01–M52 were mined by an independent seat (R12Scribe) at the baseline commit dcc8b9e,
with every evidence pointer re-verified by grep (`census/round-12/mistakes.md`, tables 2–3).
Its captured-by column is the BEFORE state. In this copy the L1 changed the captured-by
cell of 22 of the 24 rows that were `none` (M27 and M39 stay `none`, external, with the
reason rewritten), after `corpus/QUALITY.md` existed, and added M53. Two other cells were
rewritten so the table splits cleanly: M25's evidence (an `ls … | grep` command became a
prose pointer) and M32's captured-by (escaped pipes in a grep pattern became commas).

Counting command (C1), run from the lane root:

    sed 's/\\|/%7C/g' <file> | awk -F'|' '/^\| M[0-9]+ \| (defect|process|honest-stop|caught) \|/{n++; if ($6 !~ /^[[:space:]]*none/) c++} END{print c"/"n}'

Before (`census/round-12/mistakes.md`): 28/52. After (this file): 51/53 (re-run 2026-10-19 by the L1 and by R12PostReviewer before M27 was set back to `none`, which then read 52/53). The count is mapped-criteria coverage, not demonstrated capture.
Every `QUALITY.md Q<n>` cited below must resolve:
`grep -oE 'QUALITY\.md Q[0-9]+' corpus/lessons/round-12.md | sort -u | while read -r _ q; do grep -qE "^\| $q \|" corpus/QUALITY.md || echo "dangling $q"; done` prints nothing.

| id | kind | class | evidence pointer | captured-by | fix |
|---|---|---|---|---|---|
| M01 | defect | Default branch hardcoded `origin/main` — pushed receipts unverifiable | corpus/lessons/round-1.md:11 | SKILL.md:21 (prose; tool resolves it) | criteria: a receipt resolves the default ref per repo, never hardcodes it |
| M02 | defect | `unreachable → NOT-SAFE` misfires on worktree metadata (absent dir IS the prune condition) | corpus/lessons/round-1.md:17 | SKILL.md:16 + selftest F4 (tools/souji-verify.sh:1235) | criteria: every receipt branches on artifact kind |
| M03 | defect | Reference sweeps self-pollute via the census's own fragments | corpus/lessons/round-1.md:20 | SKILL.md:23 (sweep excludes `census/**`, `tests/**`) | criteria: sweeps exclude the lane's own evidence surfaces |
| M04 | caught | Blind-seat disagreement with the final table (traced to D1, not missed evidence) | LOG.md:58 | QUALITY.md Q5 | criteria: blind pairs re-derive independently; disagreement is adjudicated with its cause named |
| M05 | process | Seat write-scope overstep (a seat synthesized and installed `tools/souji-verify.sh`) | corpus/lessons/round-2.md:8 | AGENTS.md:13 (prose, no-check) | rule: seat output is a named fragment; only the parent installs |
| M06 | process | Fixture/segment schema chaos — 2/10 cases emitted the contracted protocol; 4 shards used 3 schemas | corpus/lessons/round-2.md:12 + corpus/lessons/round-3.md:25 | QUALITY.md Q11 | criteria: one machine-readable fixture/shard schema, checked by the runner |
| M07 | defect | Compliance checker over-strictness false-flagged clean impls (literal marker greps) | corpus/lessons/round-2.md:19 | QUALITY.md Q11 | criteria: compliance checks parse behavior, not spellings |
| M08 | caught | Signal hierarchy: impl-09 scored 60/60 on review probes but failed F7/F8 in 16 runner matrices | corpus/lessons/round-2.md:17 | tests/results/INSTALL.json:5 (recorded decision rule) | criteria: redundant independent execution outranks any single review |
| M09 | process | Approval list contained 15 already-removed rows; contract re-cut mid-round | corpus/lessons/round-3.md:22 | QUALITY.md Q11 | criteria: approval-list contracts tolerate already-removed rows |
| M10 | process | `/tmp` fixture residue ~2,100 dirs, routed outside the lane | corpus/lessons/round-3.md:27 | QUALITY.md Q4 | criteria: fixtures default `TMPDIR=/var/tmp` + quota preflight |
| M11 | defect | Metadata prune left 8 unreachable blobs in the owner's object store | corpus/lessons/round-3.md:29 | QUALITY.md Q12 | criteria: a prune receipt records object-level residue |
| M12 | honest-stop | 4/8 judges dissented NO-CLEAN-CANDIDATE over fixture rot; adjudicated by parent re-derivation, not majority | corpus/lessons/round-4.md:15 | corpus/lessons/round-4.md:17 (the round's lesson) | keep: dissent is preserved; adjudication by re-derivation |
| M13 | process | Seat-made fixture scripts rotted (exit 127, stale `/tmp` roots) | corpus/lessons/round-4.md:21 | QUALITY.md Q4 | criteria: fixtures self-contained or regenerated by a committed build script |
| M14 | defect | Symlink false-SAFE class — `find -type f` silently omitted symlinks from digests | corpus/lessons/round-5.md:9 | SKILL.md:22 (prose) + tools/souji-verify.sh:157 (r5 fix) | criteria: every path component a removal writes through gets an lstat gate, fail-closed |
| M15 | defect | Local-master pushed fallback — SAFE(pushed) from a local ref alone | corpus/lessons/round-5.md:15 | SKILL.md:21 (prose) + selftest E7 (tools/souji-verify.sh:1248) | criteria: no remote-tracking ref → `pushed-unverifiable` |
| M16 | defect | Deleted-file SAFE row (`logs_tier.txt`) — existence not re-checked at correction time | corpus/lessons/round-5.md:20 | SKILL.md:21 ("the path exists now") | criteria: a corrected verdict re-verifies existence at correction time |
| M17 | caught | LOG append-only violation (r1 commit 652b6f8 inserted a section mid-file) | corpus/lessons/round-5.md:32 | AGENTS.md:11 (prose, no-check) | criteria: LOG entries append at EOF; one order check over `git log -p LOG.md` |
| M18 | caught | GUI-launch incident — a harness spawned Obsidian, rewriting `.obsidian` metadata | corpus/lessons/round-5.md:35 | AGENTS.md:17 (prose, no-check) | keep + criteria: harness selftest refuses GUI/config writes |
| M19 | caught | SKILL.md receipt guidance drifted from installed tools | corpus/lessons/round-5.md:38 | SKILL.md:15 (behavior wins over prose; r6 reconciliation) | criteria: prose is reconciled in the round that finds the drift |
| M20 | defect | Pin risk — the 3 gd2d pins were left unlocked and bare-prune-eligible | corpus/lessons/round-5.md:26 | SKILL.md:100 (prose, no-check) + live lock state (3 locked, reason recorded) | rule: every pin carries `git worktree lock --reason`; surface rows cite lock state with a command |
| M21 | honest-stop | K1: a live tree is not classifiable to 0 — honest claim form is a timestamped snapshot RANGE | corpus/lessons/round-6.md:11 | corpus/lessons/round-6.md:11 (the round's lesson) | criteria: live targets yield snapshot ranges, not zero-claims |
| M22 | caught | Handoff draft carried claims the evidence didn't support — stripped | corpus/lessons/round-6.md:13 | AGENTS.md:15 (prose) | keep |
| M23 | process | 32/128 seat failures (waits + provider limits) gutted census/scratch shards mid-flight | corpus/lessons/round-6.md:8 | QUALITY.md Q5 | criteria: critical roles carry a redundancy budget |
| M24 | caught | Bare `--not --remotes` silently returns nothing on git 2.55 (would emit false pushed receipts) | corpus/lessons/round-6.md:20 | SKILL.md:21 (pitfall named in prose) | criteria: version-pinned idioms (Q1-style) |
| M25 | process | Evidence-layout drift — r2 evidence lives in `tests/results/`, `census/round-2/` does not exist | `census/` holds no `round-2/` dir (`ls census` listing; r2 evidence is in `tests/results/`) | QUALITY.md Q10 | criteria: one evidence layout per round (`census/round-N/`); README claim corrected |
| M26 | honest-stop | r7: receipts denied every candidate; nothing forced; quarantine left UNEXERCISED | corpus/lessons/round-7.md:4 | corpus/lessons/round-7.md:30 (the round's lesson) | keep: never manufacture removal claims |
| M27 | honest-stop | Lane remote 404 — every pushed receipt in the lane was unverifiable until the operator created/origin landed | corpus/lessons/round-7.md:15 | none (external: remote creation is operator-owned; the pre-existing `pushed-unverifiable` refusal, SKILL.md:21, already failed closed) | keep: report the gate, do not work around it |
| M28 | caught | Parent column misread (lore "worktrees=3" was unpushed=3) caught by blind seat S02 | corpus/lessons/round-7.md:19 | QUALITY.md Q5 | criteria: blind pairs re-derive; a misread candidate is refused, never manufactured |
| M29 | caught | Parent awk bug produced empty receipt pins; the tool's fail-closed refusal caught it | corpus/lessons/round-8.md:31 | tools/souji-quarantine.sh:652 + selftest U5 (tools/souji-quarantine.sh:1478) | criteria: pin lists get schema-validated before use |
| M30 | process | Host `/tmp` hit DISK QUOTA mid-round; fixture runs corrupted, two seat failures misattributed | corpus/lessons/round-8.md:24 | QUALITY.md Q4 | criteria: quota preflight; fixtures under `/var/tmp` |
| M31 | process | r7 "gate2 contradiction" dissolved — `.tmp` was never a scratch class (taxonomy misunderstanding) | corpus/lessons/round-8.md:28 | SKILL.md:23 (taxonomy names `*.tmp` as excluded) | criteria: taxonomy drift is reconciled when a contradiction dissolves |
| M32 | defect | r9 false-SAFE class union (23 classes): locale `id_*` bypass · disappearing git · hidden live refs · ledger revocation-after-capture · linked-worktree HEAD skew · non-`*-shokunin` owner names · index-write contract | corpus/lessons/round-9.md:8 | tools only, partial — LC_ALL/GIT_OPTIONAL_LOCKS tools/souji-verify.sh:62; ledger pin tools/souji-quarantine.sh:303,340,369; owner-name + registration conflicts scan tools/souji-verify.sh:962; gaps: no `command -v git` guard in souji-quarantine.sh (exists in verify:1308, census:818); SKILL.md has no pattern for any of them (`grep -cE nested, NUL or maintenance SKILL.md` → 0) | criteria: every closed reproducible class lands as a SKILL.md error pattern or a `tests/` fixture in the round that closes it |
| M33 | defect | NUL/tab authorization forgery — NUL-in-list and tab-spliced rows read as SAFE | corpus/lessons/round-9.md:10 | tools only: tools/souji-quarantine.sh:637 (NUL gate), :652 (malformed row) + selftest U5 (:1478) | criteria: paths travel NUL-delimited end to end; human-readable formats are never parsed |
| M34 | defect | Nested dirty/unpushed repos deleted on the strength of an ancestor's receipt | corpus/lessons/round-9.md:12 | tools only: tools/souji-verify.sh:418 (`nested-repo-or-unverifiable`) | criteria: a nested `.git` is its own receipt scope and never inherits one |
| M35 | defect | TOCTTOU — a fresh child inside an aged container was DELETED (r10 G2, 6/6 reproduced) | census/round-10/S13-fragment.md:72 | SKILL.md:46 (second check — partial; no descendant rule) | criteria: the second check pins each descendant's length, mtime and digest |
| M36 | honest-stop | r9 dissent-24 preserved (rubric zeroing semantics, dirty-file SAFE reading, exploration-vs-coverage) | corpus/lessons/round-9.md:29 | corpus/lessons/round-9.md:29 (the round's lesson) | keep: dissent is recorded, never re-rolled |
| M37 | caught | SCORECARD prose said 6/7 where rows said 8/7; judges caught it; corrected r9 | SCORECARD.md:45 | QUALITY.md Q10 | criteria: SCORECARD prose and tables agree — one grep over both |
| M38 | defect | `census --compare` accepted empty/near-empty priors (3 unsafe outcomes, the last open r9 class) | corpus/lessons/round-10.md:4 | tools/souji-census.sh:359 (hard error) + selftest cases `bad/empty/blank-lead/blank-before-header` (:767) | criteria: every contract refusal ships with a regression fixture |
| M39 | process | Hyper provider ~14 min/agent — functionally unusable for batch work (operator test) | corpus/lessons/round-10.md:16 | none (external: provider routing is operator-owned; recorded, no lane rule can capture it) | record operator routing results; criteria: routing notes name the measured failure |
| M40 | defect | Certifier shared-relay overwrites (`cert-16.json`); CERTIFIED verdicts attached to bytes other than those measured | corpus/lessons/round-11.md:14 | QUALITY.md Q6 | criteria: each certifier writes its own fragment; verdicts attach only to hash-verified installed bytes |
| M41 | defect | Candidate-selection rule contradicted the class under test (most selftest checks picked a candidate that fails it) | corpus/lessons/round-11.md:16 | QUALITY.md Q6 | criteria: the selection rule must exercise the class being certified |
| M42 | defect | Pre-removal `git add -A` swept 10 live `.scratch/*.out`, the in-flight r11 report and a `.gitignore.tmp` into hygiene commit e20f4fa (two corrective commits: 9c220bf, 99819ec) | LOG.md:381 | QUALITY.md Q7 + SKILL.md:99 (checklist row) | rule: hygiene commits stage exactly the approved pathspec list; never `git add -A` over live lanes |
| M43 | defect | Quarantine staging loop hung after 3 files to the 20-min driver timeout; the tool has no per-target bound | LOG.md:373 | QUALITY.md Q8 (tool fix still open: `grep -c timeout tools/souji-quarantine.sh` → 0) | rule: bounded per-target staging; fail-closed abort with diagnostics |
| M44 | defect | 3 orphaned judge fixtures stuck ~9 h on `sha256sum` of a FIFO (`wait_for_partner`), ppid=systemd | LOG.md:403 | QUALITY.md Q8 | criteria: digest readers accept regular files only, under a bounded timeout |
| M45 | defect | Own debris committed at the lane root — census stderr captures `err4.nl2`/`err4.z2` (tracked), `.ufo-reports-placeholder` (0 B), `.scratch/s29-freeze-dir.txt`, `results/.s54-write-probe.txt` (all tracked in 1ccf11b) | err4.nl2:1 + commit 1ccf11b | QUALITY.md Q13 | rule: tool diagnostics land under `census/round-N/`, never the lane root; no-receipt debris is swept before any hygiene commit |
| M46 | caught | 2 quarantine-staged files (launch-chousa/kagi.json) were missing post-timeout; the hash-vs-origin second check caught it and both were restored from origin | LOG.md:377 | SKILL.md:46 (second check) + manual protocol | keep: hash-vs-origin second check is the equivalent-or-stronger path when the tool hangs |
| M47 | honest-stop | Sweep: kotodama `.scratch` — every child receipt-denied (newest mtime < 24 h; big three additionally `secrets-refusal` → kagi) | LOG.md:411 | census/round-6/kotodama-scratch-handoff.md (exists) | keep: re-sweep when the tree ages past 24 h (scheduled ≈2026-10-20) |
| M48 | honest-stop | Sweep: 107 pushed-receipt strays denied at the pre-removal reference gate (cited by 8+ reports, plans, PREDICTIONS/HYGIENE) | LOG.md:420 | SKILL.md:23 (zero-live-references gate) + census/operator-sweep-20261018/stay-strays-verdicts.tsv | keep: reference gate outranks the receipt |
| M49 | honest-stop | Sweep: `.tower/comms/log/activity.log` (engine SAFE/stale) refused as operator-tooling runtime | LOG.md:421 | QUALITY.md Q14 | rule: operator-tooling runtime is report-only, refused by zone spirit |
| M50 | defect | ShellCheck gates ran `-S error`; SC2115/SC2114 are warnings, so empty-variable removal hazards are invisible; no shellcheck gate exists under `tests/` | census/round-10/S02-cluster-A.md:19 | QUALITY.md Q9 | criteria: removal/verification shell passes `shellcheck -S warning` incl. SC2115/SC2114 |
| M51 | defect | Latent: on git ≥2.54 a plain `git commit` (quarantine is "a normal commit", SKILL.md:44) can auto-run maintenance with the geometric default and prune worktree metadata with no souji receipt | tools/souji-census.impl-46.sh:111 (the only guard in the tree, a draft) | QUALITY.md Q7 + SKILL.md:77 (error pattern) + SKILL.md:99 + gate tests/fixtures/r12-maintenance-guard.sh | rule: hygiene commits run `git -c maintenance.auto=false`; pinned registrations carry `git worktree lock --reason` |
| M52 | process | Bookkeeping surfaces went stale — SCORECARD `## Planned` stops at r5 while r6–r11 ran; certification note says "until the r10 hardening" while r10+r11 happened (no-relay carry recorded only in LOG) | SCORECARD.md:35 + SCORECARD.md:50 / LOG.md:356 | QUALITY.md Q10 | rule: the closing commit updates `## Planned` and the certification note; one grep per round |
| M53 | defect | Silent wrong-cwd: in the r12 harness `cd` is an alias to a missing function, so an L2 fixture's `git init/commit` and three seats' downloads ran in the FLEET ROOT main checkout (4 commits c095ea1..b21278d by `r12 <r12@test>` on master, ~10 stray files; auto-maintenance there pruned the throwaway registrations) | corpus/lessons/round-12.md `## Incident` + `git -C /home/vgpnk/Projects/shokunin reflog -8` (read-only) | QUALITY.md Q7 + QUALITY.md Q13 + SKILL.md:98 (right-repo check) | rule: never rely on `cd`; absolute paths or the tool's cwd; `rev-parse --show-toplevel` before any commit |

Not captured, on purpose: M27 (remote creation is operator-owned) and M39 (provider routing
is operator-owned). M43's criterion exists but the tool fix does not
(`grep -c timeout tools/souji-quarantine.sh` → 0) — Planned.

## Gate

Candidates: the six W1 ART candidates C1–C6 (`fleet-ledger/.ufo/waves/kaika-w1/souji-art.md`
§4) plus 33 SOURCES rows. Re-derivation (Q5): the r12 reviewer re-opened the load-bearing
sources and reproduced the git behaviour independently of the fixture author
(`census/round-12/reviewer-preflight.md`); a post-integration reviewer and critic re-derive
this Gate (`census/round-12/postreview.md`).

| candidate | verdict | reason |
|---|---|---|
| ART C1 → K1 `knowledge/git-auto-maintenance-prunes-worktrees.md` (F1) | admit | Q1 (git 2.55.0 + tag v2.55.0), Q2 (gc.c/worktree.c/run-command.c/commit.c lines at v2.55.0; recheck is a read-only source grep), Q3 (fleet-root incident M53, seat-reported); Q4 n/a (no fixture in its admission — the C3 gate is corroboration only); ART's "MANUAL-type" corrected to `SCHEDULED \| MANUAL` |
| ART C2 → K2 `knowledge/git-grace-periods-and-expire-to.md` (F1/F4) | admit | Q1 (installed man pages 2.55.0), Q3 (`--prune=now` warning + fixture deletion under forced expiry); facts only, hold change left to operator |
| ART C3 `size-census-git-repo-structure` (F2) | reject (defer) | ART §9 open question unresolved: whether `git repo structure` writes or takes locks was not tested; the command is EXPERIMENTAL; a read-only census claim without that test fails Q2/Q4. Flip: a /var/tmp fixture diffing `find .git -newer` around a `GIT_OPTIONAL_LOCKS=0 git repo structure` run |
| ART C4 → K3 `knowledge/dupe-finders-detect-then-act.md` (F3) | admit | Q2 (dedupe.rs/main.rs at a74f90d), Q3 (rmlint Cautions demos, jdupes -Q); ART's "aborts a group if any file changed" corrected: per-file skips + group abort via the CLI-defaulted `modified_before` |
| ART C5 → K4 `knowledge/trash-spec-restorable-quarantine.md` (F4) | admit | spec text v1.0 with located MUST quotes; Q3 (r10 symlinked quarantine root) |
| ART C6 → K5 `knowledge/quarantine-same-filesystem-rename.md` (F4) | admit | Q1 (coreutils 9.11), Q2 (strace run; the pasteable recheck line is the committed fixture), Q3 (split cross-device move); its `/dev/shm` second device needs Q15, which was written when this entry surfaced the need — first item for the non-author spot-check |
| SOURCES S001–S029, S031, S033 | admit as rows | opened 2026-10-19; grounding quotes below. S031 is own-work at tier A, which contract v1 allows for "the lane's own re-runnable gate output" (SOURCES-CONTRACT-v1.md:27-28) |
| SOURCES S030 (OneNine size-reduction post), S032 (git-filter-branch as a cleanup technique) | reject (kept as rejected rows) | S030 contradicts S002 (`--prune=now`, filter-branch); S032 is history rewriting, refused by PROVINCE; flips recorded in the rows |

Status/used-by changes: none in place — every row is new this round.

Lane-internal re-derivation (Q5; R12PostReviewer and R12PostCritic, dispatched seats — still
the lane, `census/round-12/postreview.md`):

| item | verdict | cause | disposition |
|---|---|---|---|
| K1 admit | agree | every cited v2.55.0 line checks | — |
| K3 admit | agree on content, disagree on form | cited `main @ a74f90d`, not a tag; tool versions missing | fixed: `@v0.35.0` (byte-identical, sha256 compared), versions named |
| K5 admit | agree on behaviour, disagree on Q4 form | `/dev/shm` clause added to Q4 after the need surfaced | fixed: Q4 restored, Q15 added as its own row and flagged; S025 re-fetch failed at review time (gnu.org unreachable) |
| C3 size-census reject | agree, premise stale | reviewer's scratch run left `.git` unchanged; reject still holds on EXPERIMENTAL + no committed fixture | reason kept, premise noted; flip unchanged |
| S030, S032 rejects; S029, S014, S002 rows | agree | quotes match | — |
| M10→Q4, M23→Q5 | disagree | criterion tests too weak to catch the class | fixed: Q4 test checks `TMPDIR:-/tmp`; Q5 test checks the second-seat record |
| M27→SKILL.md:21 | disagree | pre-existing prose, not a criterion | fixed: back to `none` (external) |
| M43→Q8, M52→Q10 | weak | test satisfiable without catching the class | fixed: Q8 test pins the wrapped call; Q10 test given commands |
| C2 separability | critic: falsified | K1 admitted via C3's gate | fixed: K1 admitted on source; recheck is a source grep |
| C3 checklist + self-test | critic: holds-if-fixed | lock command lacked its operand; `grep -c` exits 1 on 0; `--selftest` asserted nothing | fixed: `<worktree-path>` + awk count; selftest asserts pinned ids |

Non-author spot-check (≥1 admit, ≥1 reject): pending — the orchestrator's verification after
this round lands.

### SOURCES rows — grounding (contract rule 1; copied from `census/round-12/sources-gate.md`, author R12SourcesExec2)

### S001 — git-maintenance(1)
- URL: https://git-scm.com/docs/git-maintenance (live page fetched; it reports 2.56.0). Row anchor: installed 2.55.0 page. Accessed 2026-10-19.
- Quote, § CONFIGURATION › maintenance.strategy › geometric (roff :591 and the following entry): "The strategy expires data in the reflog and removes worktrees that cannot be located anymore." … "This is the default strategy for manual maintenance."
- ART: agrees.

### S002 — git-gc(1)
- URL: https://git-scm.com/docs/git-gc. Accessed 2026-10-19 (installed 2.55.0).
- Quote, § OPTIONS --prune (roff :113): "--prune=now prunes loose objects regardless of their age and increases the risk of corruption if another process is writing to the repository concurrently"
- ART: agrees. `gc.worktreePruneExpire` is at roff :333-340 ("calls git worktree prune --expire 3.months.ago"). The reflog defaults (90 and 30 days) are at :346 and :352; the rerere defaults (60 and 15 days) at :399 and :407.

### S003 — git-worktree(1)
- URL: https://git-scm.com/docs/git-worktree. Accessed 2026-10-19 (installed 2.55.0).
- Quote, § COMMANDS lock (roff :167): "lock it to prevent its administrative files from being pruned automatically. This also prevents it from being moved or deleted."
- ART: agrees. The `-z` porcelain text is at roff :596 ("If -z is given then the lines are terminated with NUL rather than a newline").

### S004 — git-repack(1)
- URL: https://git-scm.com/docs/git-repack. Accessed 2026-10-19. Sources: the installed 2.55.0 page, and `Documentation/git-repack.adoc` at tag v2.56.0, byte-identical to master on that date.
- Quote, § OPTIONS --expire-to (installed, roff :132): "This option is useful for keeping a copy of any pruned objects in a separate directory as a backup."
- ART: agrees.
- `--drop-filtered` exists only at v2.56.0 (adoc :186-220): "refuses to drop any blob that the current index references". It is absent from the host's 2.55.0.

### S005 — git-repo(1)
- URL: https://git-scm.com/docs/git-repo. Accessed 2026-10-19 (installed 2.55.0).
- Quote, § COMMANDS structure --format table (roff :166): "This format may change and is not intended for machine parsing."
- ART: agrees. Roff :44 reads "THIS COMMAND IS EXPERIMENTAL". The report bullets (refs, reachable counts, inflated size, disk size, largest objects) are listed after roff :103.

### S006 — git(1)
- URL: https://git-scm.com/docs/git. Accessed 2026-10-19 (installed 2.55.0).
- Quote, § ENVIRONMENT GIT_OPTIONAL_LOCKS (roff :2195-2200): "this will prevent git status from refreshing the index as a side effect"
- ART: agrees.

### S007 — git-clean(1)
- URL: https://git-scm.com/docs/git-clean. Accessed 2026-10-19 (installed 2.55.0).
- Quote, § DESCRIPTION (roff :57): "Git will refuse to modify untracked nested git repositories (directories with a .git subdirectory) unless a second -f is given."
- ART: agrees.

### S008 — git-last-modified(1)
- URL: https://git-scm.com/docs/git-last-modified. Accessed 2026-10-19 (installed 2.55.0).
- Quote, § DESCRIPTION (roff :41): "Shows which commit last modified each of the relevant files and subdirectories."
- ART: agrees on content. The ART note "(2.52+)" was not re-verified this session, so it is omitted from the row.

### S009 — git/git source at v2.55.0
- URL: https://github.com/git/git/blob/v2.55.0/builtin/gc.c (tag v2.55.0 = 5ce91c0). Accessed 2026-10-19.
- Byte check: the local `gc.c`, `worktree.c`, `run-command.c` and `commit.c` copies each pass `cmp` against `raw.githubusercontent.com/git/git/v2.55.0/<path>`.
- Quote, builtin/gc.c:1974-1975: "strategy = geometric_strategy; type = MAINTENANCE_TYPE_MANUAL;"
- Quote, worktree.c:1004: "if (stat(file.buf, &st) || st.st_mtime <= expire) {"
- ART: differs in wording only, per the reviewer preflight. The geometric table entries for worktree-prune and reflog-expire are `MAINTENANCE_TYPE_SCHEDULED | MAINTENANCE_TYPE_MANUAL` with WEEKLY schedule (gc.c:1912-1919). `--auto` runs as type MANUAL and selects them (gc.c:1975, :1989). The task is at gc.c:379-389 (ART says 379-388) and the condition at :391-427 (ART says 391-420). Conclusion unchanged.
- Other call sites:
  - `builtin/commit.c:1965` holds `run_auto_maintenance`.
  - am.c, fetch.c, merge.c and rebase.c at v2.55.0 each hold one call (`grep -c run_auto_maintenance` → 1 each).

### S010 — Git release notes
- URL: https://github.com/git/git/tree/master/Documentation/RelNotes. Accessed 2026-10-19.
- Revisions:
  - 2.50.0–2.54.0: byte-identical to master.
  - 2.55.0: matches tag v2.55.0.
  - 2.56.0: matches tag v2.56.0.
- Quote, 2.54.0.adoc:58: " * "git maintenance" starts using the "geometric" strategy by default."
- ART: agrees. ART status was `watch`; the contract has no such value, so it became `queued`, and the row is now `mined` per the K1 plan.

### S011 — Git BreakingChanges
- URL: https://git-scm.com/docs/BreakingChanges. The adoc was fetched at master c514088. Accessed 2026-10-19.
- Quote, § Git 3.0 › Changes (BreakingChanges.adoc:219-220): "The default value of `safe.bareRepository` will change from `all` to `explicit`."
- ART: agrees. ART `watch` became `queued`.

### S012 — git-filter-repo(1)
- URL: https://github.com/newren/git-filter-repo/blob/main/Documentation/git-filter-repo.txt (main d7b75ac). Accessed 2026-10-19.
- Quote, :418: "Every time filter-repo is run, files are created in the `.git/filter-repo/` directory."
- ART: agrees. Line :97 reads "Will not modify your repo." Lines :582-584 read "It is a really bad idea to get in the habit of always specifying `--force`".

### S013 — git-sizer README
- URL: https://github.com/github/git-sizer (README at master 56a6df5). Accessed 2026-10-19.
- Quote, README.md:176: "If you'd like the output in machine-readable format, including exact numbers, use the `--json` option."
- Release date: the v1.5.0 release page shows `datetime="2021-11-16T16:14:39Z"`.
- ART: agrees. ART `watch` became `queued`.

### S014 — GitLab blog, What's new in Git 2.53.0
- URL: https://about.gitlab.com/blog/whats-new-in-git-2-53-0/ ("Published on: February 2, 2026", Justin Tobler). Accessed 2026-10-19.
- Quote: "The intent of this command was to collect information about the repository and eventually become a native replacement for tools such as git-sizer(1)"
- ART: agrees. The source is community, so it stays tier B.

### S015 — GitHub Docs, Removing sensitive data
- URL: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository. Accessed 2026-10-19.
- Quote, § About removing sensitive data from a repository: "as a first step you need to revoke and/or rotate that secret."
- ART: agrees. ART `watch` became `queued`.

### S016 — rmlint(1)
- URL: https://github.com/sahib/rmlint/blob/master/docs/rmlint.1.rst (master 3a44e63; the local copy passes `cmp`). Accessed 2026-10-19.
- Quote, rmlint.1.rst:28: "``rmlint`` itself WILL NOT DELETE ANY FILES."
- ART: agrees.

### S017 — rmlint docs, Cautions
- URL: https://rmlint.readthedocs.io/en/latest/cautions.html (page says rmlint 2.11.0). Accessed 2026-10-19.
- Quote, § Consider safe removal options: "Rather than deleting duplicates, consider moving them to a holding area or trash folder."
- ART: differs on tier only, A → B. This is the rmlint project describing failure modes of other tools (fdupes demo under Symlinks). That makes it a strong secondary with reproducible detail, not a primary for those tools. Content agrees.

### S018 — jdupes README
- URL: https://codeberg.org/jbruchon/jdupes (README at master d198306; the local copy passes `cmp`).
- Release: the Codeberg API reports v1.31.2 published 2026-09-02T15:16:04+02:00. Accessed 2026-10-19.
- Quote, README.md:249-250: "The `-t`/`--no-change-check` option disables file change checks during/after scanning. This opens a security vulnerability that is called a TOCTTOU"
- ART: agrees.

### S019 — fdupes(1)
- URL: https://github.com/adrianlopezroche/fdupes/blob/master/fdupes.1 (byte-identical at tag v2.4.0, released 2025-03-30, and master a7c1da4). Accessed 2026-10-19.
- Quote, fdupes.1:131-132 and § CAVEATS :175-176: "Log file deletion choices to LOGFILE." … "a user could accidentally preserve a symlink while deleting the file it points to."
- ART: agrees.

### S020 — fclones README
- URL: https://github.com/pkolaczk/fclones/blob/main/fclones/README.md (main a74f90d; the local copy passes `cmp`). Accessed 2026-10-19.
- Quote, README.md:22: "There is also a `--dry-run` option that can tell you exactly what changes on the file system would be made."
- ART: agrees.

### S021 — fclones src/dedupe.rs
- URL: https://github.com/pkolaczk/fclones/blob/main/fclones/src/dedupe.rs. Tag v0.35.0 and main are byte-identical. Accessed 2026-10-19.
- Quote, dedupe.rs:844-845: "We need to skip the whole group, because we don't know if these files are really different. if let Some(max_timestamp) = config.modified_before {"
- ART: differs. ART says "aborts a group if any file changed after the report". The code does two things:
  - Non-regular files (:814-824) and length-changed files (:826-841) are skipped one at a time.
  - The whole group aborts only when `config.modified_before` is set (:843-847).

### S022 — FreeDesktop.org Trash Specification
- URL: https://specifications.freedesktop.org/trash/latest/ ("Publication Date: 2014-01-02, Version: 1.0"). Accessed 2026-10-19.
- Quote, § 5 and § 6: "The implementation also MUST check that this directory is not a symbolic link." … "MUST create the corresponding file in $trash/info first."
- ART: agrees. § 6 also says "opening with O_EXCL" and "each subsequent trashing must not overwrite a previous copy".

### S023 — trash-cli README
- URL: https://github.com/andreafrancia/trash-cli (README.rst at master bfb1595; release 0.26.9.29 shows `datetime="2026-09-29T20:32:57Z"`). Accessed 2026-10-19.
- Quote, README.rst:122-125: "Can I alias `rm` to `trash-put`? … You can but you shouldn't."
- ART: agrees.

### S024 — GNU coreutils, rm invocation
- URL: https://www.gnu.org/software/coreutils/manual/html_node/rm-invocation.html (page title "GNU Coreutils 9.12"; host 9.11). Accessed 2026-10-19.
- Quote, § 11.5 --preserve-root: "When ‘all’ is specified, reject any command line argument that is not on the same file system as its parent."
- ART: agrees. The host's `/usr/bin/rm --help` lists `--one-file-system` and `--preserve-root[=all]`.

### S025 — GNU coreutils, mv invocation
- URL: https://www.gnu.org/software/coreutils/manual/html_node/mv-invocation.html (GNU Coreutils 9.12). Accessed 2026-10-19.
- Quote, § 11.4: "mv falls back on copying as if by cp -a, then (assuming the copy succeeded) it removes the original."
- ART: agrees.

### S026 — find(1)
- Source: installed `man find`, /usr/share/man/man1/find.1.gz, owned by findutils 4.11.0-1. Accessed 2026-10-19.
- Quote, § ACTIONS -delete (roff :1270-1277): "As in turn -depth makes -prune ineffective, the -delete action cannot usefully be combined with -prune."
- ART: agrees.

### S027 — ShellCheck wiki SC2115
- URL: https://github.com/koalaman/shellcheck/wiki/SC2115 (wiki HEAD d9486e5). Accessed 2026-10-19.
- Quote, SC2115.md § Rationale (link markup removed): "If `STEAMROOT` is empty, this will end up deleting everything in the system's root directory."
- ART: agrees. Local run on shellcheck 0.11.0:
  - Input: `printf '#!/bin/bash\nrm -rf "$X/"*\n'` piped to `shellcheck`.
  - With `-S error`: rc=0, no output.
  - At default severity: rc=1, with "SC2115 (warning)".

### S028 — GitLab postmortem of January 31
- URL: https://about.gitlab.com/blog/2017/02/10/postmortem-of-database-outage-of-january-31/ ("Published on: February 10, 2017"). Accessed 2026-10-19.
- Quote: "Unfortunately this process was executed on the primary instead." … "When we went to look for the pg_dump backups we found out they were not there."
- ART: agrees. The page also says "around 300 GB of data had already been removed".

### S029 — Google SRE book ch. 26
- URL: https://sre.google/sre-book/data-integrity/. Accessed 2026-10-19.
- Quote, § First Layer: Soft Deletion: "Common choices of soft deletion delays are 15, 30, 45, or 60 days."
- ART: differs. ART says "lazy deletion behind it". The text reads "The first layer is soft deletion (or "lazy deletion" in the case of developer API offerings)", which makes lazy deletion another name for soft deletion, not a later layer. The second layer is backups.

### S030 — OneNine (rejected)
- URL: https://onenine.com/how-to-reduce-git-repository-size-safely/. Accessed 2026-10-19.
- Quote: "running git gc --aggressive --prune=now on a monthly basis helps keep your repository in check"
- ART: agrees. The page also offers "git filter-branch – Built into Git – Well-documented Suitable for simpler tasks". It contradicts:
  - S002 roff :113 (`--prune=now` corruption risk);
  - S002 :153 ("probably not worth it" for `--aggressive` without benchmarks);
  - S032.

### S031 — r12 maintenance guard fixture (own-work)
- Path: `tests/fixtures/r12-maintenance-guard.sh`. Result: `tests/results/r12-maintenance-guard.txt`, generated 2026-10-19T21:53:39Z on git 2.55.0. Opened 2026-10-19.
- Quote, result :11 and :13: "case=plain-commit-sync before=2 after=1 expect=1 verdict=PASS" … "case=auto-off before=2 after=2 expect=2 verdict=PASS"
- ART: this confirms C1's falsifying fixture. It also settles what ART §4 C1 left as [INFERENCE] about the detached HEAD. Result :36-40 shows the commit with no ref and no reflog entry, listed by fsck as unreachable. It is still present after `gc --prune=2.weeks.ago` and absent after `--prune=now`.

### S032 — git-filter-branch(1) (rejected)
- URL: https://git-scm.com/docs/git-filter-branch. Accessed 2026-10-19 (installed 2.55.0, `cmp` match).
- Quote, § WARNING (roff :46): "git filter-branch has a plethora of pitfalls that can produce non-obvious manglings of the intended history rewrite … its use is not recommended."
- ART: agrees with ART §6 item 1, which was not a §3 row there and is new here. PROVINCE.md § Refuses: "Git history rewrite in any repo … — operator-owned".

### S033 — gitrepository-layout(5)
- URL: https://git-scm.com/docs/gitrepository-layout. Accessed 2026-10-19 (installed 2.55.0, `cmp` match).
- Quote, § worktrees/<id>/locked (roff :387-392): "The presence of this file prevents worktrees/<id> from being pruned either automatically or manually by git worktree prune."
- ART: agrees with the ART lead. New in this round: the page has no `worktrees/<id>/index` entry; the 3 per-id entries are gitdir, locked and config.worktree. Yet `worktree.c:1001-1008`@v2.55.0 ages registrations by that file.

### Omitted
None. All 30 ART rows were opened this session.
