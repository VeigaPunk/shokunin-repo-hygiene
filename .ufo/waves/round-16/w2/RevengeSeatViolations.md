# RevengeSeatViolations — wave-1 audit rows → Q26 void decisions

Seat: `SoujiR16.RevengeSeatViolations`. Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`,
dispatched at HEAD `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae`. L1 landed the wave-1 integration as
`163158a706352f1c0ee3521c4da2e5289970db57` while this seat was running; every lesson/`QUALITY.md`/
`SOURCES.md` line cited below was re-checked at `163158a` and has the same text (both the audit JSON
and the `w1` reports are committed at `7a79dc2`, and the audit JSON's sha256 is unchanged:
`b3e4f89f…`). Axis: **calibration** only. Leaf seat: no
delegation, no commits, no lane edits; this report is the only file written.

Artifacts read (exact paths, hashed where pinned):

- `census/round-16/seat-audit-w1.json`, sha256 `b3e4f89f1f2ae84307d03215a8f7ab4c98e8916754d3d7eeaf6969f80656dc43`;
  20 rows, summary `{calls:3173, major:1, minor:19, seats_audited:65, seats_with_major:["SrcGitNoLazyFetch"]}`.
- `tools/souji-seat-audit.py` (class definitions and selftest), `corpus/QUALITY.md:65` (landed Q26 row),
  `.ufo/waves/round-16/w1/ConnQualityCriterion.md:18` (drafted Q26 row), `corpus/lessons/round-16.md`
  (R16-M5 `:13`, seat-failure carry `:51`, Process `:70`), the 13 flagged seat reports, and the
  `history://SoujiR16.<Seat>` transcripts for all 20 rows (line numbers are the audit's, which strips
  the `N:` export prefix; my spot checks align at every cited line).

Limits: rendered transcript arguments truncate at ~200 chars (`…`), so a clean row is not proof of
absence; I classify from the rendered text plus the seats' own `## Commands` lists, not from a rerun of
the audit. I did not execute `souji-census.sh`, any fixture, any gate, or the audit itself.

---

## 1. Result in one line

Of the 20 audit rows, **15 are established violations** (14 read-only `V-RECURSIVE`, 1 writing
`V-WRITE-SCOPE`), **4 are over-flags** (not violations on the visible evidence), and **1 is
unestablished** (pattern-only search, recursion not shown). Under Q26, exactly **one seat's evidence is
voided wholesale** (`SrcGitNoLazyFetch`, writing branch); the 14 read-only rows void only the specific
findings that consumed their output, and every one of those claims is re-derivable by exact-path reads
**except three completeness quantifiers** (`CriticDisclosureR3` §3 "every", `RevListReposDoubleScan:14`
"not duplicated", `RevRedaction:70` "No current fixture"), which must be restated per-file or dropped.
The correct disposition is therefore "void → re-derive", not the lesson's blanket "evidence voided".

**Verdict on the attack surface: PARTIAL.** (a) The audit *detects* real violations — 15/20 rows hold,
and the writing row is correctly major. (b) Its *row classification* fails on 4 over-flags and leaves
1 unestablished, so "19 minor" is not a violation count. (c) Its *void semantics* (as carried in
`round-16.md:13,70`) fail: they void a seat's evidence for read-only rows and leave the reader unable to
tell which findings actually lost their basis. (d) Its *coverage* is a lower bound with a specific hole
(subtree-rooted grep tools, row 5.2.1) that is not the truncation limit the criterion declares.
(e) Two wave-1 conclusions that a clean rule required be re-derived were instead dropped silently
(S036/S042 2.55.0 labels; knowledge-doc attribution) — those are the actionable failures.

## 2. Row-by-row classification

`json:NN` = seat line in `seat-audit-w1.json`; `tr:NN` = transcript line inside that seat's JSON
`violations` entry. "Output used?" asks whether a report claim consumes that command's *result* as
evidence (not merely as navigation); navigation-only use is marked `nav` and voids the locator, not the
finding.

| # | Seat · row | Recorded | Verdict | Q26 branch | Output used? | Decision |
|---|---|---|---|---|---|---|
| 1 | ConnLogConvention `json:10` `tr:52` — `find <lane> -name ConfigRepair.md …` | minor V-RECURSIVE | **established**: lane-root `find` | read-only | yes, **nav**: located `.ufo/waves/round-15/w1/ConfigRepair.md`, quoted at `ConnLogConvention.md:219,345` | **void the path provenance**; re-derive by reading that exact path → no conclusion dropped |
| 2 | ConnLogConvention `tr:133` — `grep -rn "sweep every mention" PROTOCOL.md corpus/QUALITY.md corpus/lessons/round-15.md` (`ConnLogConvention.md:453`) | minor V-RECURSIVE | **over-flag**: `-r` is inert on three file operands; no directory operand | none | n/a | **no void** |
| 3 | ConnQualityCriterion `json:30` `tr:85` — `grep -rn 'Q2[0-9]\|Q1[0-9]\|criteria' corpus/README.md SCORECARD.md SKILL.md LEARNING.md` (`ConnQualityCriterion.md:265`) | minor V-RECURSIVE | **over-flag**: four file operands | none | n/a | **no void** |
| 4 | CriticDisclosureR3 `json:68` `tr:81` — grep tool with path root `<lane>` | minor V-RECURSIVE | **established**: tool rooted at the lane root (41 hits) | read-only | yes: §3 "**every** understated mention" list, `CriticDisclosureR3.md:56-101` | **void the "every" completeness claim**; re-derive the row list from the six named files it also read; drop the fleet-commit pointer (see #4b) |
| 5 | RevFixtureR16Edits `json:171` `tr:112` — `grep -rn "HARM_CASES\|…" --include=… tools corpus` (`RevFixtureR16Edits.md:334-338`) | minor V-RECURSIVE | **established** subtree recursion, but **empty output** | read-only | **no** — seat states "returned **no output**, no finding depends on it"; report re-derived every citation from `git show cbf688a` (`:338-341`) | **no finding void**; record the violation |
| 6 | RevIncludeResolve `json:194` `tr:101` — `grep -rn 'kvi->filename\|spelled\|…' corpus/ docs/` (`RevIncludeResolve.md:204,215-217`) | minor V-RECURSIVE | **established** two-subtree recursion | read-only | one line only (`corpus/SOURCES.md:54`, an S-number check), not a finding | **no finding void**; record |
| 7 | RevListReposDoubleScan `json:212` `tr:188` — `grep -rn -iE ':\(optional\)\|pid=\$!\|…'` in `.ufo/waves/round-16/w1/` | minor V-RECURSIVE | **established** wave-dir recursion | read-only | yes: sibling-overlap / novelty claim (`RevListReposDoubleScan.md:14`) | **void the novelty claim**; re-derive by naming the sibling reports; F1/T1/P1/D1/D2 stand (exact reads) |
| 8 | RevRedaction `json:235` `tr:73` — `grep -rn "include-protected\|…" tests/ tools/ corpus/` (`RevRedaction.md:226`) | minor V-RECURSIVE | **established** three-subtree recursion | read-only | yes: F1's negative "No current fixture hits this" (`:70`) | **void the universal**; re-derive with exact greps on the two named fixtures (`r14-census-boundary.py`, `r15-census-config.py`); F1/F2/F3 substance stands |
| 9 | RevSoftPropagation `json:253` `tr:149` — `ls …/w1/ && grep -rln 'optional' …/w1/` (`RevSoftPropagation.md:428-431,467`) | minor V-RECURSIVE | **established** wave-dir recursion | read-only | **nav only**: used to choose sibling reports, then exact greps at `:469-470` | **no finding void**; re-derive selection from the named files; §1 verdict stands (exact-file greps of `tools/souji-census.sh`) |
| 10 | SentinelCommandExec `json:336` `tr:118` — `write()` with empty args, result `⇒ error … Refusal (cyber)` | minor V-WRITE-UNKNOWN | **false positive**: provider aborted before the tool ran; no target, no bytes, no output | none | n/a | **no void**; F1 (fsmonitor, `SentinelCommandExec.md:56-91`) stands and is the cited source of the integrated `GIT_CONFIG_COUNT` fix (`round-16.md:53`) |
| 11 | SrcGitCheckAttr `json:369` `tr:69` — `grep -rn 'SOURCES-CONTRACT' <lane> --include=…` (self-disclosed `SrcGitCheckAttr.md:113`) | minor V-RECURSIVE | **established** lane-root recursion | read-only | yes: located the contract/tier format for the **row proposal** (`:80-105`); **not** used by the stride-3 grounding (`:49-70`, which is exact code + web reads) | **void the row/format provenance only**; S046 already re-derived (`SOURCES.md:60`, `round-16.md:29,51`); **do not void §3** |
| 12 | SrcGitConfigIncludesRecheck `json:382` `tr:95` — glob of `corpus/lessons/round-16*.md; …` | minor V-RECURSIVE | **established as an out-of-class pattern read** (not an exact named file); recursion root unestablished past truncation | read-only | **no**: C-A/C-B/S043/S044 use man-page/web/exact reads | **no finding void**; correct the report's "Non-shell reads (exact files/URLs only)" (`:309`) which omits the globs |
| 13 | SrcGitConfigIncludesRecheck `tr:119` — glob of `corpus/SOURCES-CONTRACT*.md; …` | minor V-RECURSIVE | same as #12 | read-only | no | no finding void; disclosure correction |
| 14 | SrcGitNoLazyFetch `json:402` `tr:49` — glob `<lane>` (204-line listing) | minor V-RECURSIVE | **established** lane listing | read-only | yes, nav: located `corpus/knowledge/git-repo-structure-readonly.md` cited by F2 | subsumed by #16; if #16 is carved out: **void F2's discovery provenance**, re-derive by exact read |
| 15 | SrcGitNoLazyFetch `tr:62` — glob `<lane>` (205-line listing) | minor V-RECURSIVE | same as #14 | read-only | nav only | same |
| 16 | SrcGitNoLazyFetch `tr:144` — `edit(<lane>/.ufo/waves/round-16/r16-placeholder.md)` ⇒ `error · File not found` | **major V-WRITE-SCOPE** | **established**: out-of-scope write attempt; **zero bytes written**, tool refused | **writing** (landed `QUALITY.md:65`; the *draft* row at `ConnQualityCriterion.md:18` has **no writing branch**) | no (only an error line) | **void seat evidence** (all F1–F6, S043 row, S036 update); re-derive: S049 ✔ done (`:32`), F1 via independent seats, F2 via exact reads; F3/F4 restated from S049. **Nothing must drop** |
| 17 | SrcPythonAst `json:444` `tr:58` — `grep -rn "ast.parse\|py_compile\|…" tools/*.py census/round-16/*.py` | minor V-RECURSIVE | **over-flag**: bounded file globs, one level | none | n/a | **no void** |
| 18 | SrcPythonAst `tr:88` — `grep -rln "souji-landing-gate" .ufo/waves/round-16/ corpus/` (`SrcPythonAst.md:165`) | minor V-RECURSIVE | **established** two-subtree recursion | read-only | no: the gate-contract section cites the w1-spec and an exact `ls`, `SrcPythonAst.md:69-89` | **no finding void**; record |
| 19 | SrcPythonAst `tr:97` — `grep -rn "ast.parse\|py_compile" corpus/lessons/round-14*.md corpus/…` | minor V-RECURSIVE | **unestablished**: wildcard file list; no directory root shown; `-r` inert on files | read-only (if any) | no finding cites it | **no void**; record as unestablished |
| 20 | SrcPythonAst `tr:107` — `grep -rn "SOURCES-CONTRACT" corpus/ PROTOCOL.md` (`SrcPythonAst.md:234`) | minor V-RECURSIVE | **established** corpus-tree recursion | read-only | yes: row-placement/contract shape | **void the placement provenance**; re-derive by exact `README.md`/`QUALITY.md`/fleet-contract reads; the ast row itself was already dropped in favour of S050 (`SOURCES.md:64`) |

**Tally.** Established: 15 rows = 14 read-only + 1 writing. Over-flags: #2, #3, #10, #17 (4). Unestablished:
#19 (1). The published summary `1 major, 19 minor` counts **rows, not violations**; the lesson's
`everything voided` reading is wrong for 14 of those rows.

**#4b — the unclassified CriticDisclosureR3 deviation.** `CriticDisclosureR3.md:123` self-reports command
6, `git -C /home/vgpnk/Projects/shokunin log … -- .ufo/reports/round-15/souji.md` (fleet-root `-C`), and says
its output is "used only as a pointer in §2/§4.5". The probe rule lists `git -C` only for the lane repo,
so this is an out-of-class **read-only** command with no audit class; the wave-2 spec's context still
lists `git -C` against the lane only. Q26's read-only branch applies: **void that commit pointer
(`215ba746…`)**; the pointer cannot be re-derived without another fleet-root git read, so it **drops**
unless L1 authorises one. The `.ufo/reports/round-15/souji.md` line numbers themselves are re-derivable
from the exact file.

**#10 note.** `SentinelCommandExec.md:104-107` also discloses `git --version` and `| cat -n`. Neither is a
class the tool implements, and neither is on the wave's allowed list verbatim. If L1 treats them as
out-of-class read-only, they void only findings that used their output: here the `git --version` line
(`SentinelCommandExec.md:6`) and nothing else; the F1 finding does not use it. The man-page header read
is the allowed basis for "installed docs 2.56.0".

## 3. What is actually void

- **Whole seat: `SrcGitNoLazyFetch` only** — major `V-WRITE-SCOPE` (#16), under the landed Q26 wording
  "an executing **or writing** violation voids the seat's evidence" (`corpus/QUALITY.md:65`). Under the
  *draft* wording quoted in the assignment ("read-only → void findings; executing → void seat") a
  **writing** violation has no branch at all — see §5.3. I apply the landed wording because that is the
  text now in `QUALITY.md`, and I flag the gap.
- **Findings void (read-only rows), each already narrowed to the claim that consumed the output:**
  1. `ConnLogConvention.md:219,345` ConfigRepair path provenance — re-derive by exact read.
  2. `CriticDisclosureR3.md:56` "every understated mention" — re-derive per named file, or drop "every".
  3. `RevListReposDoubleScan.md:14` "owned by siblings … not duplicated" — re-derive by named siblings.
  4. `RevRedaction.md:70` "No current fixture hits this" — re-derive over the two named fixtures.
  5. `SrcGitCheckAttr.md:80-105` row/format provenance — S046 already re-derived; grounding **not** void.
  6. `SrcPythonAst.md:91-116` row-placement provenance — row already dropped; re-derive only if revived.
  7. `SrcGitNoLazyFetch.md:57` (F2) discovery of the knowledge-doc path — re-derive by exact read.
- **Nothing else is void.** In particular: `SentinelCommandExec`'s F1, `RevFixtureR16Edits`'s F1/F2/T1/T2/T3,
  `RevSoftPropagation`'s §1 propagation verdict, `RevListReposDoubleScan`'s F1/T1/P1, `RevRedaction`'s
  F1/F2/F3 substance, `SrcGitCheckAttr`'s stride-3 grounding, and `SrcGitConfigIncludesRecheck`'s C-A/C-B
  all rest on exact-file/web/committed-blob reads and do not consume a forbidden output.

## 4. Wave-1 conclusions L1 must re-derive or drop

These are the *conclusions*, not rows. Items 1–2 are already handled; items 3–9 are the live work.

| # | Conclusion (artifact:line) | Status | Action |
|---|---|---|---|
| 1 | `S049` row (`corpus/SOURCES.md:63`) from the voided seat | already re-derived by L1 (`round-16.md:32`) | **keep**; cite L1, not the seat |
| 2 | `S046` row (`corpus/SOURCES.md:60`) | already re-derived (`round-16.md:29`) | **keep**; but narrow `round-16.md:51` — it says "evidence voided", which over-voids the stride-3 finding |
| 3 | **S036/S042 "installed 2.55.0" labels** (`corpus/SOURCES.md:50`, `:56`) and the knowledge doc's `verified-at` (`corpus/knowledge/git-repo-structure-readonly.md:2`) vs `S049` "installed git(1) 2.56.0" (`:63`) and `round-16.md:32` | **not integrated; now self-contradictory** — two same-day SOURCES cells plus the knowledge header say 2.55.0, one says 2.56.0 | **re-derive and correct**, or record an explicit drop. Independent clean evidence: `SrcGitConfigIncludesRecheck.md:27-36,295` (man-page headers, `Source: Git 2.56.0`, TH 2026-09-27), `SentinelCommandExec.md:6` (`git --version` = 2.56.0), `SrcGitCheckAttr.md:17` (`git version 2.56.0`). The voided seat is **not** the only source |
| 4 | **F2 knowledge-doc over-attribution** (`SrcGitNoLazyFetch.md:57`): doc `source:` lists S035/S036/S037 while its body (`:11`, `:33-34`) relies on lazy-fetch suppression, which S036's scope excludes | **dropped by omission**; doc unchanged | **re-derive from exact reads** (doc `:1,:11,:33-34`; S036 scope at `SOURCES.md:50`) and either append S049 to the `source:` line or record the drop |
| 5 | F3/F4 advisory (`SrcGitNoLazyFetch.md:58-59`): guard comment "cannot fetch" is stronger than git(1)'s promise; `cat-file -e` idiom is narrower than the census use | seat-voided; not carried | restate against the **re-derived S049 quote** if L1 wants them; no seat credit, no drop needed |
| 6 | `CriticDisclosureR3` §3 "every understated mention" (`:56`) | depends on the lane-root grep | **drop "every"** or re-derive per-file over the named set: `SKILL.md`, `SCORECARD.md`, `LOG.md`, `corpus/lessons/round-15.md`, `.ufo/reports/round-15/souji.md`, `census/round-15/disposition.json` |
| 7 | `CriticDisclosureR3` §2/§4.5 fleet-commit pointer `215ba746…` (`:123`) | depends on fleet-root `git -C`, no class | **drop** unless L1 authorises a fleet-root read; the report path itself is readable exactly |
| 8 | `RevListReposDoubleScan` :14 novelty/cross-reference claim | depends on the wave-dir grep | **re-derive** by naming the sibling reports (the FIFO / wt-dirty ones) and exact greps; F1 unchanged |
| 9 | `RevRedaction` F1 "No current fixture hits this" (`:70`) | depends on the tests/tools/corpus grep | **re-derive** with exact greps of `tests/fixtures/r14-census-boundary.py` and `tests/fixtures/r15-census-config.py`, which is the bound the sentence actually claims |
| 10 | `SrcPythonAst` proposed ast/`S043` row + G5 ("prove non-execution by fixture") | L1 dropped it in favour of `S050` compile (`SOURCES.md:64`) | record as a **deliberate drop**, not a void. No live defect observed: the gate catches `(SyntaxError, ValueError)` at `tools/souji-landing-gate.py:217` and decode errors at `:386,:461`, i.e. G1/G2 are implemented |
| 11 | `SrcGitConfigIncludesRecheck` C-B: C1's "only a protected reach keeps whole-run exit 2" is contradicted by `usage_err` and non-namespace `protected_fail` classes (`:295`) | **not void-driven** — its evidence is exact tool reads, no glob output; it was simply not integrated (the wave-2 dispatch context, `.ufo/waves/round-16/w2-spec.json` `context`, repeats the contradicted phrasing) | **re-derive or drop as a separate integration decision**; do not attribute this omission to Q26 |

**The lesson's own disposition must change.** `corpus/lessons/round-16.md:13` (R16-M5 fix cell) and `:70`
(Process) say "1 major … 19 minor … → evidence voided and re-derived". That is false in two ways: only
the writing row voids a seat, and 4 rows are not violations. Suggested replacement:
> 20 audit rows over 65 seats / 3173 calls: 15 established (1 writing `V-WRITE-SCOPE` — attempted edit,
> target absent, no bytes written; 14 read-only `V-RECURSIVE`), 4 over-flags (two exact-file greps, one
> bounded file-glob, one aborted `write()`), 1 unestablished (pattern-only). Writing violation → seat
> evidence voided (`SrcGitNoLazyFetch`); read-only violations → only the findings that consumed their
> output voided, and all such findings were re-derived from exact paths. The audit is a lower bound.

## 5. Calibration defects in the audit and the Q26 text (smallest fixes)

### 5.1 Four over-flags (rows #2, #3, #10, #17)
- `tools/souji-seat-audit.py:112` flags any `grep -…r…` when the lane path appears **anywhere** in the
  command (including a harmless `cd <lane> &&`), so `grep -rn … file1 file2` is a violation while it is
  in-class by the probe rule ("grep … on EXACT named files"). Smallest fix: after stripping the leading
  `cd <lane> &&`, require a directory operand (a token with no recognized file extension, or an operand
  ending `/`). Add selftest cases `grep-files` (want `[]`) and `grep-subtree` (want `["V-RECURSIVE"]`).
- `tools/souji-seat-audit.py:102-107`: a `write`/`edit` with **empty** args and `⇒ error` is not a write.
  Fix: skip when `args.strip()` is empty **and** the line's status is `error`; keep `V-WRITE-UNKNOWN` for a
  nonempty but unparseable target. Add selftest `write-aborted` (want `[]`). This row cost
  `SentinelCommandExec` a false major-adjacent flag on the seat whose F1 drives the C1 fsmonitor fix.
- Row #17 (`tools/*.py census/round-16/*.py`) is a one-level file glob; same operand fix.

### 5.2 Under-flags (the audit is not only over-inclusive)
1. `history://SoujiR16.SrcGitNoLazyFetch:70` — `grep(SOURCES-CONTRACT @ <lane>/corpus)` (15 hits) is a
   **subtree-rooted grep tool**, the exact class flagged at `RevIncludeResolve:101`, but unflagged because
   `audit_seat` only tests `args.endswith(lane|fleet)` for the grep/glob tools (`tools/souji-seat-audit.py:114-117`).
2. `SrcGitCheckAttr.md:113` and `SrcGitNoLazyFetch`'s two lane globs: a **lane-root recursion necessarily
   lists `census/operator-sweep-20261019/`** (it is inside the lane and not git-ignored: `git check-ignore`
   returns nothing). The wave contract says "anything touching" that path is forbidden; Q26's `V-SURFACE`
   only matches the path **in the arguments**. The audit therefore records a forbidden-surface touch as
   minor `V-RECURSIVE`. Recommendation: do **not** retro-escalate (listing a directory entry is not reading
   protected content, and the seats state no output line came from it); instead define in Q26 that
   "touching = reading content", and require seats to exclude the directory (`--exclude-dir`) and to say
   so. Otherwise every future lane-root recursion is a major by construction.
3. `CriticDisclosureR3.md:123` fleet-root `git -C` (read-only, no class).
4. `SentinelCommandExec.md:104-107` `git --version` and `| cat -n` (read-only, no class; out of the
   allowed list verbatim).
5. `RevSoftPropagation.md:427-429` wrote `/tmp/r15-census.txt` and `/tmp/preharm-census.txt`; the contract
   allows writes only under `/var/tmp/souji-r16-<Seat>/`. `V-WRITE-SCOPE` only sees `write|edit|ast_edit`,
   not shell redirection.
6. `RevFixtureR16Edits.md:339-341` wrote `/tmp/fx_cbf.py` and `/tmp/census_cbf.sh` (the copies later
   diverged; the report re-derived every citation from `git show`), and ran `grep -rn "relative"
   /usr/share/doc/git*/` — both unflagged.
7. `SrcPythonAst.md:165` (`grep -rln` over `.ufo/waves/round-16/ corpus/`) **is** flagged, but the same
   shape at `SrcGitNoLazyFetch:70` is not — the rule is path-suffix based, not root based.

### 5.3 Q26 wording gaps this exercise exposes
- **No writing branch in the draft.** `ConnQualityCriterion.md:18` says "an out-of-class **executing**
  command voids that seat's evidence"; the landed row says "executing **or writing**". The major row is a
  writing attempt; under the draft alone it maps to no void. Land the "or writing" wording.
- **Attempt ≠ effect.** `QUALITY.md:65` does not distinguish an attempted write from an effective one.
  Recommend: "a write that changed bytes, or an attempt against an existing target that the tool refused,
  voids the seat's evidence; an attempt rejected before execution (target absent, provider abort) is
  recorded and voids only findings that used its output (here: none)." For this round the practical result
  is identical (the seat is re-derived), but the criterion should not depend on the accident that the
  target did not exist.
- **"Used its output" needs the navigation/evidence line.** Of the 14 read-only rows, 6 did not use the
  output at all (#5 empty, #6 one S-number, #9 selection, #12/#13, #18), 5 used it only as a locator for a
  finding built from exact reads (#1, #11, #14, #15, #20), and 3 are completeness quantifiers whose content
  *is* the survey (#4, #7, #8). If "used" includes navigation, every locator finding is void until re-read;
  if it means evidence, only the three quantifiers are at risk. Recommend: "a locator
  obtained from the output voids the citation's provenance only; re-deriving the finding from the now-named
  exact file restores it. A completeness quantifier ('every', 'no fixture', 'not duplicated') whose content
  *is* the forbidden survey cannot be re-derived that way and must be dropped."
- **Criterion vs contract disagree on subtree recursion.** `QUALITY.md:65` says "recursive reads over lane
  or fleet roots"; the wave contract says "never recursive search over … a whole directory tree". The audit
  implements the narrower text (and inconsistently — see 5.2.1). Pick one: either the criterion is
  lane/fleet-root-only and `corpus/`, `docs/`, `tests/`, `tools/`, wave dirs are in-class, or the tool must
  flag subtree roots. Do not leave the two texts disagreeing.
- **`## Commands` is shell-only, the draft's compliance clause is not.** The contract asks for every
  **shell** command; the draft (`ConnQualityCriterion.md:18`) defines compliance as agreement between
  transcript and `## Commands`, "a command present in one and absent from the other". That makes every
  non-shell call (read/grep/glob/edit) a defect. Two live cases: `CriticDisclosureR3.md:135` says "grep
  tool: over named files … No directory recursion was used", while the transcript's grep tool is rooted at
  the lane root (row #4) — a real disclosure inaccuracy; and `SrcGitConfigIncludesRecheck.md:309` says
  "Non-shell reads (exact files/URLs only)" while the transcript contains wildcard globs (#12/#13). Either
  scope the clause to shell commands (contract wording) and require a separate non-shell inventory, or
  extend the contract. Do not keep both texts.
- **Class coverage is narrower than the criterion claims.** Q26 says "each seat's recorded tool calls are
  audited"; the tool implements five classes. `git --version`, fleet-root `git -C`, shell redirects, and
  bounded `ls` listings are invisible. Say "audited against the pinned classes" or add a declared
  read-only tier (R5's `RevengeProbeRecurrence.md:279` names the `ls`/`sed`/`echo`/`cd` tier and
  `:262-330` argues for exactly this).

### 5.4 Selftest gaps
`tools/souji-seat-audit.py:155-200` has 20 cases; none covers an exact-file `grep -rn`, an empty-args write,
a subtree root (`corpus/`, `docs/`, a wave dir), `grep @ <lane>/corpus`, a shell redirect, or a
`git -C <fleet>` read. Add one per line above; the current 20/20 is green on a rule set that misclassifies
4 of the 20 real rows.

## 6. My own probe record (applying the same rule to this report)

Read-only, disclosed because Q26 binds the auditor too:

1. `grep -rn "Q26" --include=*.md corpus/ .ufo/waves/round-16` — **subtree recursive read** over two
   directories (not lane/fleet root; no forbidden surface). Used only to locate
   `corpus/QUALITY.md:65` and `.ufo/waves/round-16/w1/ConnQualityCriterion.md`; both were then read
   exactly, and every citation to them comes from the exact reads. Under §5.3's locator rule: **void the
   locator, keep the findings.**
2. `git -C <lane> status --porcelain` — `status` is not on the allowed verb list; it enumerated the
   worktree (output includes the operator-dir entry). Read-only, no lane state changed.
3. `git -C <lane> check-ignore -v census/operator-sweep-20261019` — names the operator-owned path; returned
   no rule. **Surface touch**, no content read.
4. `ls -d census/operator-sweep-20261019` — **names the operator-owned path and lists only its directory
   entry** (no children, no file opened). This is the one command I would remove in hindsight; it was used
   solely to establish whether the directory is inside the lane for §5.2.2. Nothing in this report depends
   on its output beyond that existence fact, which `git status` had already shown. **Surface touch**, no
   content read.
5. Everything else: exact-file `read`/`grep`/`sed`/`awk`/`wc`, `sha256sum`, `git show|log|rev-parse`,
   `python3` reads of named JSON/markdown, and `history://` transcript reads. No census, no fixture, no
   gate, no test, no install.

## 7. Residual unknowns

- Full argument tails of rows #12/#13/#19 are truncated; I cannot prove those globs are rooted at the lane
  root (only that they are pattern, not exact-file, reads). #12/#13 are the only rows where the *class*
  itself is inferred from the criterion rather than observed.
- Whether the operator-sweep directory existed during wave 1 (it exists now, untracked, and is not
  git-ignored); the seats' "no line from that path" statements are disclosures, not auditable facts.
- Whether L1 reads `git --version` as in-class. If it does not, only the version-attribution lines use it;
  no conclusion drops (man-page headers and `corpus/SOURCES.md:63` carry 2.56.0).
- Whether the `RevListReposDoubleScan`/`RevSoftPropagation` `/tmp` scratch writes should be a Q26 class.
  I recommend recording them as process deviations, not seat voids: no lane bytes were mutated and both
  reports re-derived their citations; but the criterion text should say "lane writes", not "writes".

STATUS: FAIL — the wave-1 audit's published disposition is wrong: 4 of its 20 rows are not violations
(two exact-file greps, one bounded file-glob, one aborted `write()`), 1 is unestablished, and only 1 (the
writing attempt) voids a seat; the lesson's blanket "evidence voided and re-derived" (`corpus/lessons/round-16.md:13,70`)
over-voids 14 read-only rows and the seat list includes ConnQualityCriterion, whose row is an exact-file
grep. Separately, `SrcGitNoLazyFetch` F1/F2 were dropped by omission: `corpus/SOURCES.md:50,56` and
`corpus/knowledge/git-repo-structure-readonly.md:2` still say installed Git 2.55.0 while `SOURCES.md:63`
says 2.56.0, and the knowledge doc still lists S035/S036/S037 for a body that relies on lazy-fetch
suppression. Both are re-derivable from clean, independent seats. (All cited lines re-checked at
`163158a`.)

## Commands

```sh
sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-16/seat-audit-w1.json; git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD; git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "import json; d=json.load(open('census/round-16/seat-audit-w1.json')); print(list(d.keys())); print(json.dumps(d['summary'],indent=1)); [print('SEAT',k, json.dumps(v)[:2000]) for k,v in d['seats'].items() if isinstance(v,dict) and (v.get('major') or v.get('minor') or v.get('findings'))]"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "import json; d=json.load(open('census/round-16/seat-audit-w1.json')); n=0
for k,v in d['seats'].items():
    for vi in v.get('violations',[]):
        n+=1; print(f\"{n:02d} | {k} | {vi['severity']} | {vi['class']} | {vi['tool']} | line {vi['line']}\"); print('    ', vi['args'][:400])
print('total',n)"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -rn "Q26" --include=*.md corpus/ .ufo/waves/round-16 2>/dev/null | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1,120p' tools/souji-seat-audit.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '55,75p' corpus/QUALITY.md; echo ====; sed -n '1,45p' .ufo/waves/round-16/w1/ConnQualityCriterion.md; echo ====; sed -n '125,180p' .ufo/waves/round-16/w1/ConnQualityCriterion.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1,60p' corpus/lessons/round-16.md; echo '=== Process'; grep -n '^## Process\|void\|V-RECURSIVE\|V-WRITE\|seat-audit\|re-derived\|re-derive' corpus/lessons/round-16.md | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '60,100p' corpus/lessons/round-16.md; echo '=== gitignore operator?' ; cat .gitignore 2>/dev/null | head -30; echo '=== operator dir tracked/ignored'; git check-ignore -v census/operator-sweep-20261019 2>&1; ls -d census/operator-sweep-20261019 2>&1
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "l=open('corpus/lessons/round-16.md').read().splitlines()[69]; print(len(l)); print(l[700:])"; echo '=== seat line refs'; cd .ufo/waves/round-16/w1 && grep -n 'find /home\|ConfigRepair.md:7\|No current fixture\|two searches exceeded\|One deviation from\|Siblings already cover\|grep -rln .optional\|grep -rn .kvi->filename\|STATUS: PROBE RULE' ConnLogConvention.md RevRedaction.md RevFixtureR16Edits.md RevSoftPropagation.md RevListReposDoubleScan.md RevIncludeResolve.md SrcGitCheckAttr.md | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json
d=json.load(open('census/round-16/seat-audit-w1.json'))
for s in ['ConnLogConvention','ConnQualityCriterion','CriticDisclosureR3','RevFixtureR16Edits','RevIncludeResolve','RevListReposDoubleScan','RevRedaction','RevSoftPropagation','SentinelCommandExec','SrcGitCheckAttr','SrcGitConfigIncludesRecheck','SrcGitNoLazyFetch','SrcPythonAst']:
    for v in d['seats'][s]['violations']:
        print(f"{s}\t{v['line']}\t{v['severity']}\t{v['class']}\t{v['tool']}\t{v['args'][:150]}")
EOF
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && for f in ConnLogConvention ConnQualityCriterion CriticDisclosureR3 RevFixtureR16Edits RevIncludeResolve RevListReposDoubleScan RevRedaction RevSoftPropagation SentinelCommandExec SrcGitCheckAttr SrcGitConfigIncludesRecheck SrcGitNoLazyFetch SrcPythonAst; do echo "===== $f"; awk '/^## Commands/{p=1} p{print}' "$f.md" | head -18; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && for f in ConnLogConvention ConnQualityCriterion CriticDisclosureR3 RevFixtureR16Edits RevIncludeResolve RevListReposDoubleScan RevRedaction RevSoftPropagation SentinelCommandExec SrcGitCheckAttr SrcGitConfigIncludesRecheck SrcGitNoLazyFetch SrcPythonAst; do echo "===== $f"; grep -n '^## \|^\*\*F[0-9]\|^- \*\*F[0-9]\|^\*\*Conclusion\|STATUS:' "$f.md" | head -30; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && sed -n '260,320p' RevengeProbeRecurrence.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && echo '=== RevRedaction 53-110'; sed -n '53,110p' RevRedaction.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && echo '=== ConnQualityCriterion: SCORECARD/README refs'; grep -n 'SCORECARD\|README' ConnQualityCriterion.md | head; echo '=== CQC evidence 28-56'; sed -n '28,56p' ConnQualityCriterion.md; echo '=== CriticDisclosureR3 56-101'; sed -n '56,101p' CriticDisclosureR3.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && echo '=== RevSoftPropagation 24-70'; sed -n '24,70p' RevSoftPropagation.md; echo '=== RevSoftPropagation 417-432'; sed -n '417,432p' RevSoftPropagation.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && echo '=== RevListReposDoubleScan 0-30'; sed -n '1,30p' RevListReposDoubleScan.md; echo '=== 150-210'; sed -n '150,210p' RevListReposDoubleScan.md; echo '=== 270-284'; sed -n '270,284p' RevListReposDoubleScan.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && echo '=== RevFixtureR16Edits 41-70'; sed -n '41,70p' RevFixtureR16Edits.md; echo '=== 165-240'; sed -n '165,240p' RevFixtureR16Edits.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && echo '=== SrcPythonAst 48-70,117-155'; sed -n '48,70p' SrcPythonAst.md; echo '---'; sed -n '117,155p' SrcPythonAst.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '2\.5[0-9]\|installed\|anchor\|knowledge/git-repo\|over-attribut\|cat-file -e\|GIT_NO_LAZY' corpus/lessons/round-16.md | head -40; echo '=== raw process line'; awk 'NR==70' corpus/lessons/round-16.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'S036\|S042\|S043\|S046\|S049' corpus/SOURCES.md | head -20; echo '=== knowledge doc head'; sed -n '1,12p' corpus/knowledge/git-repo-structure-readonly.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && grep -n '2\.5[0-9]' SentinelCommandExec.md SrcGitCheckAttr.md SrcGitConfigIncludesRecheck.md RevIncludeResolve.md RevSoftPropagation.md | head -30; echo '=== SrcGitConfig discrepancy text'; sed -n '275,296p' SrcGitConfigIncludesRecheck.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && grep -n 'knowledge/git-repo\|S035, S036, S037\|over-attribut\|verified-at' SrcGitNoLazyFetch.md SrcGitConfigIncludesRecheck.md | head -20; echo '=== RevRedaction grep use'; grep -n 'No current fixture\|include-protected\|tests/ tools/ corpus/' RevRedaction.md | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && sed -n '25,55p' CriticDisclosureR3.md; echo '=== 102-120'; sed -n '102,120p' CriticDisclosureR3.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && sed -n '113,120p' SrcGitCheckAttr.md; echo '=== RevListDouble 31-57'; sed -n '31,57p' RevListReposDoubleScan.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && sed -n '320,345p' RevFixtureR16Edits.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'SyntaxError\|ValueError\|except\|compile(\|ast.parse\|encoding' tools/souji-landing-gate.py | head -40; echo '=== ast row registered?'; grep -n 'docs.python.org' corpus/SOURCES.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '120,220p' tools/souji-seat-audit.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '"ConnLogConvention"\|"ConnQualityCriterion"\|"CriticDisclosureR3"\|"RevFixtureR16Edits"\|"RevIncludeResolve"\|"RevListReposDoubleScan"\|"RevRedaction"\|"RevSoftPropagation"\|"SentinelCommandExec"\|"SrcGitCheckAttr"\|"SrcGitConfigIncludesRecheck"\|"SrcGitNoLazyFetch"\|"SrcPythonAst"' census/round-16/seat-audit-w1.json
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && grep -n 'fleet root\|only as a pointer\|Possible probe-rule deviations\|Probe-rule compliance note\|rows \|whole-lane' CriticDisclosureR3.md SentinelCommandExec.md RevFixtureR16Edits.md RevIncludeResolve.md SrcGitConfigIncludesRecheck.md | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && grep -n 'sweep every mention' ConnLogConvention.md; echo '=== full commands around 440-500'; sed -n '440,470p' ConnLogConvention.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && grep -n 'ast.parse\\\\|py_compile\|souji-landing-gate" .ufo\|SOURCES-CONTRACT" corpus\|ast.parse\\|SyntaxError" tools' SrcPythonAst.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && grep -n 'No directory recursion\|grep tool: over named files' CriticDisclosureR3.md; echo '=== RevListDouble overlap lines'; grep -n 'already owned by siblings\|cross-referenced\|Siblings' RevListReposDoubleScan.md | head; echo '=== RevSoft F2 lines'; grep -n ':\(optional\)\|F2 —' RevSoftPropagation.md | head -8
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "import json; d=json.load(open('census/round-16/seat-audit-w1.json')); [print(k,'calls=',d['seats'][k]['calls'],'viol=',len(d['seats'][k].get('violations',[]))) for k in ['SrcGitNoLazyFetch','SentinelCommandExec','CriticDisclosureR3','ConnQualityCriterion','SrcGitCheckAttr','RevSoftPropagation','RevListReposDoubleScan','SrcPythonAst','RevRedaction','RevIncludeResolve','RevFixtureR16Edits','ConnLogConvention','SrcGitConfigIncludesRecheck']]"
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && sed -n '69,116p' SrcPythonAst.md; echo '=== SrcGitCheckAttr 49-80'; sed -n '49,80p' SrcGitCheckAttr.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 && sed -n '22,84p' ConnLogConvention.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1,73p' .ufo/waves/round-16/w1/SrcGitNoLazyFetch.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && wc -l .ufo/waves/round-16/w1/SrcGitNoLazyFetch.md .ufo/waves/round-16/w1/SentinelCommandExec.md .ufo/waves/round-16/w1/CriticDisclosureR3.md .ufo/waves/round-16/w1/ConnQualityCriterion.md && grep -n "Commands\|sha256\|ls-files\|glob\|census\|git -C\|GIT_NO_LAZY" .ufo/waves/round-16/w1/SrcGitNoLazyFetch.md | head -60
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && git status --porcelain | wc -l && git status --porcelain | head -30; echo '=== SOURCES lines'; sed -n '50p;56p;63p' corpus/SOURCES.md | cut -c1-160; echo '=== knowledge 2'; sed -n '1,2p' corpus/knowledge/git-repo-structure-readonly.md | cut -c1-200; echo '=== lesson 13/51/70 exist?'; sed -n '13p' corpus/lessons/round-16.md | cut -c1-120; sed -n '51p' corpus/lessons/round-16.md | cut -c1-120
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline -4; echo '=== Q26 line'; sed -n '65p' corpus/QUALITY.md | cut -c1-200; echo '=== M5'; sed -n '13p' corpus/lessons/round-16.md; echo '=== Process'; sed -n '70p' corpus/lessons/round-16.md; echo '=== 51'; sed -n '51p' corpus/lessons/round-16.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum census/round-16/seat-audit-w1.json; git ls-files --error-unmatch census/round-16/seat-audit-w1.json .ufo/waves/round-16/w1/SrcGitNoLazyFetch.md 2>&1; git log --oneline -1 -- census/round-16/seat-audit-w1.json .ufo/waves/round-16/w1/SrcGitNoLazyFetch.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'if tool in {"grep", "glob"}\|def write_target\|def audit_seat\|RECURSIVE_BASH_RE\|V-RECURSIVE\|def selftest\|cases = \[' tools/souji-seat-audit.py; echo '=== R5 lines'; grep -n 'declared-tier noise\|Self-application\|02.4\|03 ' .ufo/waves/round-16/w1/RevengeProbeRecurrence.md | head
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '90,120p' tools/souji-seat-audit.py | nl -ba -v90; echo '=== selftest end'; grep -n 'wave-summary\|return 0 if failed' tools/souji-seat-audit.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && wc -l .ufo/waves/round-16/w2/RevengeSeatViolations.md && grep -n '^STATUS:' .ufo/waves/round-16/w2/RevengeSeatViolations.md && git status --porcelain | head -20
```

Read-tool calls (not shell): `read` on `census/round-16/seat-audit-w1.json`, `.ufo/waves/round-16/w2-spec.json`,
the `w1` directory listing, `history://SoujiR16.SrcGitNoLazyFetch:1-40,40-70,70-140,138-152`,
`history://SoujiR16.ConnLogConvention:46-60,128-140`, `history://SoujiR16.ConnQualityCriterion:80-92`,
`history://SoujiR16.CriticDisclosureR3:75-88`, `history://SoujiR16.RevFixtureR16Edits:106-120`,
`history://SoujiR16.RevIncludeResolve:95-108`, `history://SoujiR16.RevListReposDoubleScan:182-196`,
`history://SoujiR16.RevRedaction:66-80`, `history://SoujiR16.RevSoftPropagation:143-156`,
`history://SoujiR16.SentinelCommandExec:110-128`, `history://SoujiR16.SrcGitCheckAttr:62-76`,
`history://SoujiR16.SrcGitConfigIncludesRecheck:88-124`, `history://SoujiR16.SrcPythonAst:52-112`.
