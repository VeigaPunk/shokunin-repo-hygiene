author: hyaku closure (non-author integrator, zcode subagent (fresh session, non-author))

# souji round 46 — non-author verifier spot-check

Closed from lane tip `32f48da04846489aeb8f6c5662e9bacd742bf245` (branch `master`, pushed;
local `refs/heads/master` == `origin/refs/heads/master`), base `7f8fa3cad068` (the freeze
tip). All git access index-free (`rev-parse`, `cat-file`, `ls-tree`, `diff-tree`,
`merge-base --is-ancestor`, `show`, `log`, `ls-remote`); instruments were run from
`git show <rev>:<path>` bytes extracted to closure scratch, never from a checkout.

## 1. Step-1 conformance — PASS

| check | result |
|---|---|
| Report committed in fleet repo by lane identity | PASS — `.ufo/reports/round-46/souji.md` last touched by `souji-shokunin <souji@shokunin.local>`, fleet commit `41e4f9596eb842d8babbbef874016411cdfb3435` |
| `SHONEN` heading | PASS — `## SHONEN` with one `[~]` line per box (4 boxes); no `[x]` written by the lane (correct — non-author verifiers write `[x]`) |
| Every cited lane commit exists and is an ancestor of `refs/heads/master` | PASS — all 9 (8a793e7a, 42d86abf, 3144c16b, 8eabfba3, 4b316f22, bc50661f, 3f586352, 5cb9aaa2, 32f48da0) `cat-file -e` + `merge-base --is-ancestor` ok |
| Lane tip pushed | PASS — `git ls-remote origin refs/heads/master` = `32f48da04846489aeb8f6c5662e9bacd742bf245` = local |
| Round work inside `7f8fa3ca..32f48da0` | PASS — exactly the 9 reported commits, every one authored `souji-shokunin` |
| Report is a real report, not a marker | PASS — names work, receipts, and 9 checkable commits |
| Dispatch/complete digest | matches contract inputs: launch 2026-10-31T18:57:58-07:00, complete 2026-10-31T20:32:46-07:00 head=32f48da04846 pushed=True |

## 2. Preregistration and Amendment 1 — LEGITIMATE

- The prereg (`census/round-46/preregistration.txt`) exists at the base `7f8fa3ca`, dated
  2026-10-30, with predicates, kill rules, do-nothing controls, and before-arms for C1–C3;
  `55402501` (its named round base) is an ancestor of `7f8fa3ca`, and
  `census/round-46/c1-counter.py` is absent at `55402501` (C1 before-arm holds).
- The do-nothing control receipt `records/c1-control-donothing.txt` (unfiled=70, FAILS) was
  committed at the freeze base — before any after-data existed. Control-first holds.
- **Amendment 1 (8a793e7a + 42d86abf) and addendum (3144c16b) legitimacy:**
  - *Disclosed*: appended to the prereg itself with host-fact receipts
    (`c1-host-before.txt` exit-2, `c1-host-uncheckoutable.txt` — six HEAD paths with
    embedded `\n` fail checkout even with `core.protectNTFS=false`); restated in the round
    report and LOG.md.
  - *Committed before after-receipts*: amendment commits 02:32:04Z/02:34:42Z/02:37:08Z
    precede every after-receipt commit (8eabfba3 03:03:57Z, 4b316f22 03:04:02Z, 3f586352
    03:18:32Z, 5cb9aaa2 03:23:35Z, 32f48da0 03:27:26Z); the C1 receipts were re-taken at
    the final tip after all amendment commits.
  - *Kill rule implemented as promised*: the addendum's `INSTRUMENT_PIN` hard kill is in the
    committed counter; the pin `a332491607129195…` equals my own `sha256` of
    `tools/souji-declared-evidence.py` at the round base, and the instrument bytes are
    unchanged base→tip (empty `diff-tree`). Strictly strengthening; the frozen text stands.
  - *Narrow*: the tolerance set is computed from `ls-tree -r` at the measured rev; my count
    of control-char-named paths at the tip is exactly 6 (three `\n`-named fixture pairs
    under `tests/vault/vadv54-run/`); every other porcelain row still kills.

## 3. Per-claim re-check (all three RE-MEASURED by this verifier)

### C1 — calibration (lowest axis, 7): tip landing-suite receipt — VERIFIED

Commands run from extracted committed bytes
(`git show 32f48da0:census/round-46/c1-counter.py`):

- `python -B c1-counter.py --root <lane> --rev 32f48da04846… --work <scratch>` →
  `SUMMARY assertions=533 mismatches=70 registered=70 corrected=0 exempted=0 unfiled=0 instrument_sha256=a3324916…`, exit **0** —
  identical to `records/c1-tip-green.txt`. Sanity holds (mismatches=70>0, assertions=533>500).
- Pin kill mutation witness at r28 rev `ed270c42161cd62829783a5e5d2ef4e27089331c` →
  `COULD-NOT-EVALUATE instrument sha256 65817d0d… != pinned a3324916…`, exit **2** —
  identical to `records/c1-pin-mutation.txt`.
- Do-nothing control: evidence-verified — receipt committed at the freeze base (raw
  instrument output, unfiled=70, FAILS), pre-after by construction.
- Before arm (Amendment 1 subject): `records/c1-host-before.txt` exit 2 could-not-evaluate
  on this host; six-path uncheckoutability re-derived by my own `ls-tree -z` count (=6) and
  the committed checkout-failure probe receipt.

### C2 — operability (8): r45 register-verifier selftest — VERIFIED

Commands run from extracted committed bytes
(`git show 32f48da0:census/round-45/c1-counter.py`):

- `python -B c2-counter.py --selftest --scratch <scratch>` → `SUMMARY cases=11 pass=11 fail=0`, exit **0**
  (= `records/c2-selftest.txt`; the 11 pinned cases in `records/c2-selftest-expected.tsv`
  pin per-case exits and finding ids — two evidences, per gate standard).
- `--root <lane> --rev 019bccc9ac97f3cec1a1dea574cc2f81f57fc967 --scratch <scratch>` →
  `SUMMARY population=70 unique=66 registered=66 missing=0 derived_mismatches=0 …`, exit **0** — SUMMARY+exit
  byte-identical to the frozen r45 receipt `census/round-45/records/c1-after.txt`.
- Wrong-token control with a register fixture I built myself (one `derived=` value at
  `019bccc9` replaced by `MUTATED-TOKEN`) → `registered=65 derived_mismatches=1`, exit **1** —
  identical to `records/c2-repro-wrong.txt`.
- Before arm re-run: frozen r45 bytes (`7f8fa3ca:census/round-45/c1-counter.py`) with
  `--selftest` → `error: unrecognized arguments: --selftest`, exit **2**.
- SKILL.md registry row's self-test cell updated (r45 disclosed debt closed).

### C3 — coverage (8): F4 restore-collision knowledge entry — VERIFIED

- `git grep -lE '^ground: F4' <rev> -- corpus/knowledge | wc -l` → **8** at base
  `7f8fa3ca`, **9** at suite rev `5cb9aaa2` and at tip `32f48da0`.
- `python -B tools/souji-gate-check.py --root <lane> --round-date 2026-10-30 --entries
  corpus/knowledge/quarantine-restore-path-reoccupied.md --snapshot-dir census/round-46/sources` →
  `entries=1 ok=1 slice_verdicts=8 slice_total=8 fail=0`, exit **0** (= `records/c3-gate-check.txt`).
- `python -B tools/souji-coverage-agreement.py --root <lane> --rev 5cb9aaa2…` →
  `grounded=27 mapped=27 dangling=0 mismatches=0`, exit **0**.
- SOURCES rows `191 → 193` (`grep -cE '^ {0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'` over
  committed bytes at base and tip); the base→tip diff of `corpus/SOURCES.md` adds exactly
  S268 + S269, no existing cell changed (append-only holds).
- Knowledge entry carries the provenance trio (`source:` S268+S110, `verified-at:`,
  `recheck:`), a Gate with located quotes, and explicit non-claims (no tool change, no
  receipt class, no deletion/restore authority).

Worktree fidelity: the lane worktree files the tools read (knowledge entry, both tools,
SOURCES, SCORECARD, SKILL, README, lesson, LOG, PROVINCE) are byte-identical to the tip
commit (sha1 blob comparison) — worktree runs measured committed state.

## 4. Per-axis verdicts

| axis | verdict | basis |
|---|---|---|
| calibration | **improved** | C1 verified by re-measurement: the frozen counter was could-not-evaluate on this host; it now runs pinned, kill-ruled, and green at the tip (unfiled=0), with a mutation witness and the promised sha256 kill implemented. No numeric change claimed (stays 7) — honest. |
| operability | **improved** | C2 verified by re-measurement: gate-standard selftest over isolated fixtures with a committed expected table; default path proven byte-behavior-identical to the frozen r45 bytes; before arm reproduced (exit 2). Disclosed r45 interface debt closed. |
| coverage | **improved** | C3 verified by re-measurement: grounded-F4 8→9 with gate-check ok and coverage-agreement clean; one sourced entry on F4 restore-side collision ground; census exit 0. |
| depth / freshness / adjacency | not souji-owned this round | lane owns calibration+operability+coverage; no owned-axis score changed (SCORECARD diff is append-only; scores 7/8/8 unchanged); no cross-domain bleed (PROVINCE host corrections recorded; quarantine-before-delete respected — dry-run workspace census only). |

No axis is harmed. capabilities table gained no row (C2 recorded as registry repair —
correct; `capabilities_added` = none).

## 5. Discernment spot-check (non-author, from outside)

Sampled the round lesson's `## Gate`: one admit and one reject, both re-opened live
2026-11-01 (UTC):

| item | decision | re-opened source | agree/disagree | reason |
|---|---|---|---|---|
| S268 renameat2(2) man page | ADMIT | https://man7.org/linux/man-pages/man2/renameat2.2.html — HTTP 200 live | **agree** | All three quoted sentences found verbatim in the served page: "Don't overwrite newpath of the rename. Return an error if newpath already exists." (§ DESCRIPTION, RENAME_NOREPLACE), "EEXIST flags contains RENAME_NOREPLACE and newpath already exists." (§ ERRORS — current wording), and rename(2)'s "If newpath already exists, it will be atomically replaced" (also confirmed on the live rename.2 page, HTTP 200). The S268 row quote is 13 words (≤25), located, verbatim. Grounds exactly the F4 restore-side refusal claim made. |
| S269 freedesktop trash-spec /latest/ | REJECT | https://specifications.freedesktop.org/trash-spec/latest/ — HTTP **404** live | **agree** | The rejection reason reproduces exactly: the URL serves the freedesktop 404 page, so no restore-collision rule could be grounded at that access; the flip condition is recorded. A rejection that keeps the reason and flip is correct curation. |

New-row quote check: S268's ≤25-word quote re-opened and verified (above). Census validator:
the contract's conf-name form (`validate --root <fleet-root> souji`) prints `souji missing`
and exits 2 on this host — a disclosed host fact (receipt `census-conf-name-host.txt`,
PROVINCE/lesson correction); the documented explicit-lane-directory form exits **0**
(`shokunin-repo-hygiene ok …`, 193 rows, 57 W04 duplicate-url warnings), matching
`records/census-after.txt`.

## 6. Trend verdicts (verifier-checked)

- **expansion: unchanged** — agree with the lane. The one knowledge entry lands on existing
  F4 frontier ground (no Core promotion, no new frontier row, no capability row; F4 already
  held 8 grounded entries). The 32-seat wave plan remains undispatched (dispatched=0).
- **quality: unchanged** — agree. No admitted entry was re-verified or superseded this
  round; `bc50661f` restored CRLF-churned bytes to LF (content-neutral; net diff = intended
  lines). No admitted entry failed a re-check — so not harmed either.
- **discernment: improved** — agree, and independently witnessed: the lane's own pre-filing
  spot-check caught two real defects (the prereg's promised kill rule never implemented +
  stale pin target; CRLF churn), both fixed under the disclosed amendment and mined into
  `## Mistakes` with evidence pointers. This verifier reproduced the kill rule's necessity
  (r22 pin `65817d0d…` vs round-base `a3324916…`) and its function (exit-2 mutation witness).
  Three mistakes mined; no self-awarded axis score.

## 7. Routed defects (status-neutral; lane must fix next round)

1. **SCORECARD number drift**: the r46 C1 row says `assertions=522`; the measured value is
   **533** (receipt `c1-tip-green.txt`, report, and this verifier's re-run all agree).
   Repair the cell append-only (correction entry), per the corrections-sweep rule.
2. **Report prose W04 count**: the report says "56 W04 duplicate-url warnings"; the
   committed receipts and this verifier's live run show **57**. Correct in the next round's
   report or an erratum.
3. **Before-census citation imprecision**: the report cites `records/census-before.txt` for
   the new-host before state; that file is the old-host conf-name receipt (unchanged since
   the freeze base; `souji ok /home/vgpnk/…`). The new-host before evidence is
   `records/census-conf-name-host.txt` (rc=2) plus the committed-bytes row count (191,
   re-derived here). Commit an explicit-lane-directory before receipt next time the census
   narrative needs one.
4. **Operator items (not lane debt)**: (a) the contract's census validator command fails on
   this host (conf resolves `souji` → absent `souji-shokunin/`) — operator-side conf path or
   standing PROVINCE note; (b) the MISSION L2 floor has no dispatch surface here — L0
   question filed (line: "L2 floor on this Windows host…"), operator to rule
   waive/provide/keep-unmet; the frozen 32-seat w1 plan remains undispatched (dispatched=0).
5. **SHONEN note for the operator**: all four boxes remain author `[~]` assertions; this
   verifier finds all four plausibly checkable by a non-author (decision tables + cited
   sources present; end-to-end dry-run workspace census logged; counting commands
   self-contained; no cross-domain bleed observed) — a promotion review is available to a
   future non-author verifier. No `[x]` written here (promotion review is not this round's
   closure duty).

## 8. Closure

All three declared claims verify by re-measurement; no axis is harmed; the preregistration
discipline (freeze before after-data, control-first, one disclosed, pre-after, strictly
strengthening amendment) held. Verdict: **admitted**, lane-round ok. Defects above are
recorded in the closure notes and routed for the next round; none bars admission under the
closure contract.
