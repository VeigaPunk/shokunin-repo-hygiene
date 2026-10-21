STATUS: PARTIAL — The round-20 carry copies its catalogue faithfully (26/26), but its "complete visible" claim has no denominator, cites reports it does not carry, and under-reports the one seat deviation whose transcript it cites. Blocking for that completeness claim only; no runtime, admission, or promotion statement is made or implied.

# FinalCarryConvention — round-20 final falsification (pinned build 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1)

Source-only and read-only. Every fact below comes from `git show 1988860ed28a460f4e5228dfcdb3a7a6c5b8d8f1:<path>` or `git cat-file -e` at that commit. No build, test, lint, smoke, gate run, directory listing, or operator-sweep path was touched. Advisory author-side observation, not non-author closure.

## Finding: carry completeness is asserted, not bounded or reconciled

Lesson `corpus/lessons/round-20.md:249-279` opens `## Seat-reported failures` with "Complete visible source STATUS paragraphs are retained below" (L251). The retained set is the 26-entry `census/round-20/recovery-status-catalog.json`. Four defects sit under that claim:

1. **ConsumerSkill under-reports its search scope.** The carried paragraph (lesson L267; catalogue `line 20`; whitespace-normalized equal to `.ufo/waves/round-20/recovery/ConsumerSkill.md:20`) says "I issued one recursive `grep` rooted at the repository". The transcript that lesson R20-M14 (L25) cites, `census/round-20/transcripts/recovery/ConsumerSkill.txt:47-50`, shows four search calls:
   - L47 `glob(/home/vgpnk/Projects/shokunin/souji-shokunin) ⇒ ok · 129 lines`: a root-level listing (Q45 class), not mentioned in the carried text.
   - L48 and L49 `grep` calls whose root paths are truncated at render (`…/souji-shokunin/t…`, `…/tools…`), not mentioned in the carried text.
   - L50 `grep(... @ /home/vgpnk/Projects/shokunin/souji-shokunin) ⇒ ok · 415 lines`: the one grep the report describes as root-scoped.

   Of 25 rendered tool-call lines in that transcript, two are visibly root-scoped (L47, L50). The carried "one" undercounts the search calls the cited range shows. The rendered summary does not show the `gitignore=false` argument the report asserts, so that part stays unverified. R20-M14 cites the range without reconciling the count.

2. **Coverage has no denominator.** Neither the lesson nor the round-20 LOG entries state the recovery outcome in `census/round-20/recovery-seat-outcomes.json` (started 64, completed 39, dead 25; `rendered_history_limit` says provider failures are omitted from history://). "Visible" is never defined: there is no scanned-report list, no count, and no statement that the 25 provider-dead seats' partial output, if any, is unobservable. The LOG gives no count; its only provider-failure line is "Failed provider seats are not replaced" (`LOG.md:1112`). Lesson L100 ("not 64 completed or provider-dead seats") concerns the earlier pending handles, not this wave.

3. **Cited reports with no catalogue row and no negative record.** `.ufo/waves/round-20/recovery/InputBeforeAfter.md` (lesson L114, R20-M5) and `.ufo/waves/round-20/recovery/TruncatedTargets.md` (L26, R20-M15; also L220) both exist at the pin (`git cat-file -e`: present) and have no catalogue row. Backticked identifiers the lesson adjudicates as findings, with no row either: `F5ReadSet` (L186), `InputAdded` (L193), `InputDemo` (L198), `ReceiptManifest` (L201), `OutputExclusive` (L206). They may be seat-report names; that is inferred, not confirmed. Whether any of these reports holds a STATUS line is not verified here, and the carry is silent, so absence from the catalogue cannot be read as "no STATUS line".

4. **Two entries carry no defect content.** `ContainmentLimit` (lesson L275; `ContainmentLimit.md:40`) carries only `## STATUS: OPEN` (15 characters). `F5Authority` (L270; `F5Authority.md:64`) carries only its heading, which asserts "four concrete signal shapes" without naming them. Their bodies were outside my read set, so I cannot tell whether extraction dropped them or they never existed. Either way the carried text does not state the open item.

Calibration note (minor): all 26 entries share one disposition string, "open; source/limit retained pending pinned runtime and independent closure", including `SourceTimeout` (L273: "STATUS: no blocker. S094 verified as claimed"), whose own text is not open.

## Scoped agreements

- Lesson vs catalogue, text and pointers: 26/26 bullets (L253–L278) match name, path and line. Each contains its full normalized paragraph, and none ends in an ellipsis. Catalogue vs seat report is verified for ConsumerSkill only.
- Zero-marker discipline: `canonical_failure_markers: 0` carries an explanation that gate zero is not absence of findings, repeated at lesson L251. From LOG L1000 on, the only "clean" hits are a historical r19 phrase (L1021) and a round-20 negation, "not rerun or laundered into a clean-source claim" (L1162). No round-20 entry claims a clean, zero-finding, or landing-gate result.
- Excerpt pointer `census/round-20/coordinator-start-excerpt.txt:43` resolves to `read(/home/vgpnk/Projects/shokunin/souji-shokunin) ⇒ ok · 80 lines`, the bare lane-root read.
- **Not verified: "OPEN is not a landing-gate failure word."** The lesson attributes this to the existing gate, whose implementation is outside this seat's permitted reads. The allowed docs mention "failure word" only at `corpus/QUALITY.md:64` (Q25(c)) and do not list the words. SKILL, PROVINCE, SCORECARD and corpus/README define no OPEN or PARTIAL class. The premise is a disclosed assumption here.

## Closure route for L1 (not applied)

1. State the scanned population: which of the 39 completed recovery reports were read, and that the 25 dead seats produced no committed report.
2. For InputBeforeAfter, TruncatedTargets and each named identifier, add a catalogue row or an explicit "no STATUS line" negative with its scan.
3. Carry the ContainmentLimit and F5Authority bodies verbatim, or mark them unrecoverable.
4. Carry the transcript-visible calls for ConsumerSkill (L47 glob, L48–L50 greps) beside the seat's own disclosure, and state the disposition.
5. Assign per-entry dispositions and mark SourceTimeout not open.

## Verification and residual risk

- Executed, read-only, each returning successfully: `git show` of the named lesson, catalogue, outcomes JSON, scope-deviation JSON, excerpt (L41–L45), LOG, SKILL, QUALITY, PROVINCE, SCORECARD, corpus/README, the ConsumerSkill report, and the ConsumerSkill transcript (L45–L51); `git cat-file -e` on three paths (existence only); Python string comparison over those bytes. Nothing was written except this report. No tool installed or updated.
- Residual: bodies of ContainmentLimit, F5Authority, InputBeforeAfter, TruncatedTargets and the named identifiers were not read, so F-3 and F-4 are bounded accordingly. Transcript paths are truncated at render, so the root-scope count is a lower bound. The gate's failure-word vocabulary was not read.
- No SHONEN marks. No score.
