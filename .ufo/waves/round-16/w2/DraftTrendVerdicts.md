# DraftTrendVerdicts — souji round 16 (leaf seat, draft)

Seat: SoujiR16.DraftTrendVerdicts-4 (leaf, lane-dispatched). Lane HEAD `a6ec781`, baseline `58ace9f`. Definitions: `/home/vgpnk/Projects/shokunin/LEARNING.md` §The three trends. This is a draft for L1 and the non-author closure. A lane-dispatched seat is not an outside verifier, so nothing here counts as discernment evidence. No gate, census, selftest, fixture or recheck was run.

## Verdicts (draft)

| Trend | Draft verdict | Basis (one line) |
|---|---|---|
| expansion | **unchanged** | admitted knowledge 5→5; r16 adds source rows and authored capability rows only; no non-author admission |
| quality | **harmed** (narrow: stale-unmarked, not shown false) | three admitted entries name host Git 2.55.0; host is 2.56.0 and the entries' own recheck-on-release rule is unmet; no mark |
| discernment | **unchanged** (no verdict of improvement possible yet) | round-16 lesson has no non-author agree/disagree record; r15 disagreements are learned (Q25) but the gate has two inert/unchecked paths |

Calibration note: the quality verdict is the one most likely to be contested. If L1 re-runs the entries' rechecks on 2.56.0 before closure and they pass with verified-at updated, the honest verdict drops to **unchanged**. It does not rise to improved, because no entry was re-verified or superseded in r16.

## Expansion — unchanged

Evidence:
- Admitted knowledge did not change. `git ls-tree --name-only 58ace9f corpus/knowledge/` and `… a6ec781 …` both list six `.md` entries plus `obsidian-ledger.tsv`. Admitted = 5; `quarantine-same-filesystem-rename.md` remains HELD (its `## Admission status — HELD` section). `git diff --stat 58ace9f a6ec781` over the six entries is empty.
- Source rows: S043–S050 are added in the worktree (`git diff --stat a6ec781 -- corpus/SOURCES.md`: 13 lines). Six are `mined`, tier A (S043, S045, S046, S047, S049, S050); two are `rejected` (S044, S048). Source-row growth alone is not knowledge growth (`corpus/lessons/round-15.md`; `round-15-verifier-spotcheck.md:104`).
- Capabilities: `SCORECARD.md:46–48` adds three r16 rows (value/effect-aware census; landing-claim gate; seat transcript audit). The lesson labels C1 and C2 "candidate admit" and says "outside admission pending" (`corpus/lessons/round-16.md:18–21`). An unadmitted capability does not meet the `improved` clause.
- Frontier: `corpus/README.md` `## Frontier` still lists F1–F4 with no r16 section. Bash `set -n`, check-attr, excludes and lazy-fetch are preconditions of the census, not coverage-map ground.
- New kind of source: none. All r16 rows are `docs`.

Why not `improved`: none of the four `improved` observables is met by an admitted item. Why not `harmed`: no admitted entry fails its admission bar as shown; staleness is a quality matter (below), not an expansion failure.

## Quality — harmed (narrow)

Harm clause: "an entry is found false or stale and left unmarked" (LEARNING.md, quality row).

Evidence:
- Host Git is 2.56.0. `/var/lib/pacman/local/git-2.56.0-1/desc` records `VERSION 2.56.0-1` and `INSTALLDATE 1792498597`. That converts to 2026-10-20 12:16:37 UTC [INFERENCE: manual conversion, not a `date` run]. The pacman local DB holds no `git-2.55.0` record.
- The r16 census was measured on 2.56.0: `census/round-16/c1-matrix-final.json:666` `"git_version": "git version 2.56.0"`.
- The r16 source row S049 says "installed git(1) 2.56.0" (`corpus/SOURCES.md`, S049 row).
- Admitted entries that still name host 2.55.0 with no mark and no re-verification on 2.56.0:
  - `corpus/knowledge/git-repo-structure-readonly.md:2` — "verified-at: 2026-10-20; host Git 2.55.0 (package 2.55.0-1)". Its own line 9 says "record the Git version and recheck on releases". 2.56.0 was already the cited web-manual version when S035/S036 were opened on 2026-10-20.
  - `corpus/knowledge/git-auto-maintenance-prunes-worktrees.md:2` — "host git 2.55.0; source tag v2.55.0". Its claim is pinned to the tag, so the tagged-source claim is not shown false. Its recheck (line 3) runs on `git --version`, so it is version-sensitive and has not been run on 2.56.0.
  - `corpus/knowledge/git-grace-periods-and-expire-to.md:2` — "installed Git man pages 2.55.0; host git 2.55.0". The recheck is `man git-gc`, which reads the installed page and is now 2.56.0 content.
- Lower severity, HELD entry: `corpus/knowledge/quarantine-same-filesystem-rename.md:2` names coreutils 9.11 and kernel 7.2.3-arch1-3. `/var/lib/pacman/local/` holds `coreutils-9.12-2` and `linux-7.2.11.arch1-1`. The HELD marker marks status, not freshness, so this is recorded but not counted in the verdict.
- No r16 re-verification exists: the admitted-entry diff is empty (above), so the `improved` clause (re-verify or supersede) is not met.

Offsets, not netted in this verdict: the R1 sweep corrected `SKILL.md` and the `SCORECARD.md` operability row (not knowledge entries). The r16 census now parses and is measured on 2.56.0, which is an operability gain. `LEARNING.md` §Relation to the axes names operability as a quality input, but the quality Observable column is entry-specific. A reader who nets operability in gets **unchanged**; that alternative is stated, not preferred.

Smallest fix (L1 action, not run here): re-run each entry's recheck on host 2.56.0 and update `verified-at` to the observed version. Where a recheck fails or cannot run, mark the entry "verified on 2.55.0; host 2.56.0 unverified". Do not rewrite the historical 2.55.0 tag citations.

## Discernment — unchanged (no improvement can be recorded yet)

Improvement requires either an agree/disagree record from a non-author spot-check (at least one admit and one reject) or a disagreement that becomes a grounded criterion. LEARNING.md §Discernment. Findings:

1. **Required record absent.** `corpus/lessons/round-16.md` has no spot-check section. The lesson says "outside admission pending" (line 18). No agree/disagree entry exists for r16 gate decisions, so the per-round obligation is unmet.
2. **Learned path exists.** The r15 outside closure disagreed on quality and on a disclosure omission (`round-15-verifier-spotcheck.md:30,49,105`). That became R16-M1 (`round-16.md:7–8`), Q25 (`corpus/QUALITY.md:64`), and gate findings LG-PARSE-REG and LG-SEAT-UNCARRIED. The lesson's replay shows `--rev b410186 --round 15` exits 1 with 5 findings (`round-16.md:21`). This path is grounded. It is author-run evidence and still needs the outside check.
3. **Gate defect: LG-OPEN-ADMITTED is inert under current wording.** It fires only on the literal `admitted: true` (`tools/souji-landing-gate.py:84` ADMITTED_TRUE_RE, used at :347). `round-16.md` never writes that string; it writes "candidate admit" (:20–21). The lesson carries open seat items at lines 44, 50 and 52, and line 46 mixes "resolved@0a70bef" with "m2 open". By reading the code, the gate reports zero LG-OPEN-ADMITTED for this lesson [INFERENCE from code; not executed]. Smallest fix: treat any `admit` decision as an admitted declaration, or require an explicit `admitted: true|false` line, and add a selftest case of "candidate admit" plus an open carry.
4. **Gate defect: carry token is format-only.** `CARRY_TOKEN_RE` (`tools/souji-landing-gate.py:83`) accepts `resolved@` followed by any 7+ hex, and line 338 uses it without resolving the hex. The four cited tokens do resolve (`rev-parse --verify` for `0a70bef`, `c6207bd`, `a6ec781`, `cbf688a` all succeeded, see Commands). A made-up hex would pass. Smallest fix: resolve the hex at the landing revision and require it to be an ancestor.
5. **Missing criteria for three of six r16 mistakes.** R16-M3 (never-executed fixture admitted with oracle bugs, `round-16.md:11`), R16-M4 (checker self-test shipped at 24/47, `:12`) and R16-M6 (reviews bound to a moving target, `:14`) each say "captured-by: none". Q25 and Q26 have no test column that would catch them. LEARNING requires a QUALITY criterion citing a lesson when no criterion caught the mistake. Smallest fix: a new Q27 (a fixture or checker is admitted only after its first run at the landing revision with every arm recorded; a check failing on every arm is investigated before it counts) citing R16-M3/M4, and a Q28 (each review cites its revision) citing R16-M6. New rows, not rewrites.

Candidate sample for the non-author closure (not performed here):
- admit: C2 landing gate — re-derive by running it at `b410186`, `a31642d`, `cc21683` (the lesson's replay).
- reject: "disclosure enforcement" as a C2 label (`round-16.md:22`) — checkable against the 42-line count claim.
- reject: "the audit proves absence" (`round-16.md:22`).
- reject: K5 re-admission (held).

## Trend history — author vs outside (context for calibration)

| round | expansion author / outside | quality author / outside | discernment author / outside | outside basis |
|---|---|---|---|---|
| r12 | improved / improved | improved / improved | improved / improved | `round-12-verifier-spotcheck.md:12–13,17`: admit K1–K4 agree; reject K5 agree |
| r13 | improved / improved | unchanged / unchanged | improved / improved | `round-13-verifier-spotcheck.md:88–91,124–126`: admit F2 agree; three rejects agree |
| r14 | improved / improved | unchanged / unchanged | improved / unchanged | `round-14-verifier-spotcheck.md:7,154–157`: C1 admit agree; C2 rejected-harmed |
| r15 | unchanged / unchanged | unchanged / harmed | improved / improved | `round-15-verifier-spotcheck.md:74–106`: S041/S042 admits agree; git-status, C1/C2, sources-draft rejects agree |
| r16 | not written / drafted unchanged | not written / drafted harmed | not written / drafted unchanged | no non-author sample yet |

Calibration observations on prior verdicts:
- r12 quality "improved" was accepted with admitted entries going 0→4. Under the LEARNING quality Observable (re-verified, deepened, superseded) there was nothing prior to re-verify or supersede, so that is an expansion gain, not a quality gain. Suggest the next lesson records the basis for each quality verdict.
- r14 author discernment "improved" was downgraded to unchanged by the outside. The author overclaimed; the correction is recorded.
- r15 quality "harmed" rested on operability (census non-parsing) and SKILL prose. LEARNING names operability as a quality input, so the outside verdict is reasonable. It is not evidence of a knowledge-entry harm.

## Findings for L1

- Quality (narrow harm): three admitted entries cite host 2.55.0; host is 2.56.0-1; the F2 entry's own rule says recheck on releases. Smallest fix in the Quality section above.
- Discernment: no non-author record in r16; LG-OPEN-ADMITTED keys on a string this lesson does not write; carry token not resolved; three r16 mistakes lack criteria. Smallest fixes in items 1–5.
- Expansion: unchanged; no action needed beyond the non-author admission of the r16 capabilities, if they are judged better.
- Operator-tooling and pacman: no install, upgrade or pacman transaction was made by this seat. The git 2.56.0 upgrade is observed in the pacman local DB; its cause is outside this seat's scope. Recorded per the tooling directive; no tool was installed.

## Commands

Shell commands run by this seat, verbatim, in order (all read-only; `git -C` on named revisions and paths):

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse --verify --quiet 0a70bef^{commit}
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse --verify --quiet c6207bd^{commit}
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse --verify --quiet a6ec781^{commit}
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse --verify --quiet cbf688a^{commit}
git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree --name-only 58ace9f corpus/knowledge/
git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree --name-only a6ec781 corpus/knowledge/
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --stat 58ace9f a6ec781 -- corpus/knowledge/git-repo-structure-readonly.md corpus/knowledge/git-auto-maintenance-prunes-worktrees.md corpus/knowledge/git-grace-periods-and-expire-to.md corpus/knowledge/dupe-finders-detect-then-act.md corpus/knowledge/trash-spec-restorable-quarantine.md corpus/knowledge/quarantine-same-filesystem-rename.md
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --stat a6ec781 -- corpus/SOURCES.md corpus/lessons/round-16.md corpus/knowledge/git-repo-structure-readonly.md corpus/knowledge/git-auto-maintenance-prunes-worktrees.md corpus/knowledge/git-grace-periods-and-expire-to.md
```

Non-shell reads (exact paths or non-recursive listings): `LEARNING.md`; `souji-shokunin/corpus/{README.md,QUALITY.md,SOURCES.md}`; `corpus/knowledge/` and `corpus/lessons/` directory listings; `corpus/knowledge/{git-repo-structure-readonly,git-auto-maintenance-prunes-worktrees,git-grace-periods-and-expire-to,dupe-finders-detect-then-act,trash-spec-restorable-quarantine,quarantine-same-filesystem-rename}.md`; `corpus/lessons/round-{12,13,14,15,16}.md` and `round-{12,13,14,15}-verifier-spotcheck.md` (grep for gate, spot-check, trend, admit); `SCORECARD.md`; `tools/souji-landing-gate.py` (lines 326–346 and grep); `census/round-16/c1-matrix-final.json` (grep for git version); `/var/lib/pacman/local/git-2.56.0-1/desc`; `/var/lib/pacman/local/` globs for `git-*` and `{coreutils-*,linux-7*,bash-*}`.

Not run: the landing gate, the census, any selftest or fixture, any knowledge recheck, any pacman command, any install or upgrade. Nothing under `census/operator-sweep-20261019/` was touched.

STATUS: PARTIAL — discernment cannot be verdicted improved: round-16 has no non-author agree/disagree record; expansion and quality are drafted with evidence above. Verdict drafts are advisory and await the non-author closure.
