# RevGatePointerCode — static review of `tools/souji-landing-gate.py` (b576341 → 5efb519)

STATUS: DONE — static review complete; no blocker-level defect; 3 medium, 6 low findings, all latent or narrow; the claimed C2 behaviors (pointer grammar, `../`+`path[3:]` rule, exemption loading, measured_commit handling, checked_measured totality, emit totality) are confirmed statically and consistent with the committed before-record.

Attacked claim: C2 calibration — `tools/souji-landing-gate.py`: LG-DANGLING-PTR / LG-DANGLING-PTR-EXEMPT-STALE at `--round ≥ 18`, unresolvable `measured_commit` → LG-FROZEN-MEASURED, exemptions `corpus/pointer-exemptions.tsv`, `--fleet-root`, CLI early-error totality fix (`checked_measured`).

Method: byte-exact blobs of both revisions extracted via `git archive | tar -x` to `/var/tmp/souji-r18w2-RevGatePointerCode/{base,new}/tools/` (base 1392 lines, new 1989 lines); full diff reviewed (artifact://106410, 837 lines); no lane code executed (no ALLOWED-EXEC on this item); static reasoning cross-checked against committed evidence files and `git grep` at 5efb519. Line numbers below are 5efb519 blob lines (= my extraction, byte-exact).

## Verified-good (evidence per area)

- Grammar, braces: `_expand_braces` (669-680) recurses innermost-first; `tools/{good.sh,missing.sh}` → both leaves; nested `{a,{b,c}}` → 4 leaves (bash-equivalent). `ROUND_RANGE_RE` (130) handles `round-{16..18}` and `round-16..18`; descending range stays literal. `round-N` placeholder (131) and `<>*` tokens (721-722) skipped before expansion — selftests `pointer-placeholder-skip` / `pointer-round-range` (1355-1366) match the implementation.
- `:N` line refs: `_trim_pointer_token` (700-708) strips `path:12`, `path:12-14`, `path:2,3`, `path:73,74-78` suffixes (but see M2 for ordering).
- `../` normalization + fleet `path[3:]` rule: `_normalize_pointer_path` (710-715) joins on `posixpath.dirname(source)` then normpaths; worked examples — `corpus/README.md` + `../../census/x` → `../census/x`, `path[3:]` → `census/x` = `<fleet>/census/x` (correct: corpus→lane→fleet is 2 up); `corpus/knowledge/x.md` + `../../../census/x` → `../census/x` → `census/x` (knowledge→corpus→lane→fleet is 3 up; also correct). Escapes of ≥2 levels above the lane fail `_safe_pointer_path` (752-756) and stay findings, never silent passes. Directory citations resolve via the parent-set built at 800-804 (`tools/...` prose → rstripped to `tools` → in parent set).
- Exemption loading: `load_pointer_exemptions` (763-790) enforces exact 2 TSV fields, non-empty path/reason, no surrounding whitespace, POINTER_ROOTS prefix, safe path, uniqueness; non-UTF-8 → EvalError. Consumed by both the pointer branch (865-869) and the measured branch (592-594); staleness = committed minus used, evaluated once at 974-983.
- LOG round-section extraction: start = first heading whose number == N, end = next round-numbered heading (`_round_log_lines` 651-667). Real LOG.md at 5efb519: round-18 heading is line 949, file ends at 950, no numbered subheading inside → the whole r18 section is scanned today.
- measured_commit: regex-gated (4-64 hex, 566-568), `rev-parse --verify --quiet …^{commit}` with rc 1 = dangling / any other rc = EvalError (571-587) — same fail-closed contract as `blob_at_path`. Base-vs-new confirms the change is exactly "dangling was silent, now a finding at r18, exemption-aware" (base comment at old 548-552 vs new 566-570; new gate block 589-606). r14-cache-frozen at 5efb519 pins the placeholder `0123…67` in `record.json` and consumes exemption row 3 via `record_repo in exemptions` — consistent with 0 findings at 5efb519.
- Counters/emit totality: base `result` dict lacked `checked_measured` (base 614-618) while base `emit` printed it (base 711-717) → every early EvalError crashed with KeyError after exit was already 1 — the r18 fix (init at 899, main() fallback dict 1958-1976, unconditional SUMMARY in emit 1032-1053) is real and total; SUMMARY prints all ten counters on every path; `--json` r18-only keys guarded (1067-1072).
- Cross-check vs `census/round-18/gate-pointers-before-b576341.json`: exit 2, 10 findings (8 LG-DANGLING-PTR incl. `census/operator-sweep-20261019/` — exemptions file absent at b576341 (`git ls-tree b576341 -- corpus/pointer-exemptions.tsv` → 0 entries), 1 LG-DANGLING-PTR `tests/vault/vadv54-run/p/p6repo/.git`, 1 LG-FROZEN-MEASURED r14-cache-frozen), `checked_ptrs=319`, `ptr_fleet=3`, `checked_measured=3` — every value matches what the new code statically predicts for `--rev b576341 --round 18`. Duplicate finding paths (`gate-replays-ddb7347.json` ×2, `jj-receipts-ddb7347.txt` ×5) confirm per-occurrence counting.
- Selftest delta: exactly 20 new cases added (dangling-skill-pointer … measured-record-exemption + 2 CLI totality + fleet-json) → 33→53 consistent with the claim (static count; execution not re-run here).

## Findings (severity-ordered)

### MEDIUM

M1 — LOG extraction silently drops same-round continuation sections and stops at numbered sub-headings (`_round_log_lines` 651-667, `_round_heading_number` 644-648).
(a) Start = FIRST heading numbered N only. LOG.md's established append-only correction pattern repeats the same round in later sections (5efb519 LOG.md: round 16 at lines 836, 886, 908, 927; round 13 at 514, 562, 605; round 14 at 618, 671, 716). (b) The end boundary fires on ANY round-numbered heading — including a same-round correction heading or a `###`-subheading carrying a round number (e.g. LOG.md:657 `### Round 14 historical-runner provenance correction` already terminates the 618 section today). So a future `## 2026-10-2x — round 18 correction: …` section would be excluded from the r18 scan: start stays 949, end jumps to the correction heading, and every pointer cited in the correction section escapes LG-DANGLING-PTR. (c) Conversely non-round headings (`## 2026-10-19 — operator sweep`, LOG.md:362) do not terminate. Today's r18 section is 2 lines (949-950), so the recorded 0 at 5efb519 is unaffected — latent silent under-scan that contradicts the lane's own LOG conventions.
Smallest fix: start = first heading numbered N; end = next heading numbered M where M != N is a different round OR treat all same-number sections as one union (scan every heading numbered N up to the next heading with a different number).

M2 — Line-reference trim runs before the comma split, so a line-ref on a non-final citation survives into the candidate (`_trim_pointer_token` applied at 720, split loop 727-738, parts consumed 739-749).
Citation `` `tools/x.sh:12,tools/y.sh` ``: token = `tools/x.sh:12,tools/y.sh`; the anchored suffix regex (707) fails because after `:12,` comes `t`, not a digit → no strip; depth-0 split yields parts `tools/x.sh:12` and `tools/y.sh`; the first part is never re-trimmed → candidate `tools/x.sh:12` → `_path_exists_in_tree` false → LG-DANGLING-PTR although `tools/x.sh` exists. False positive; the pinned wave-1 grammar note (704-706) covers only pure line-lists `path:2,3`. A trailing line-ref (`tools/a.sh,tools/b.sh:12`) is handled correctly, so the defect is exactly "line-ref on any non-final comma-separated citation". No selftest case covers `path:N,path2`.
Smallest fix: apply `_trim_pointer_token` per part after the split (or re-trim each part inside the part loop).

M3 — Interior `..` is never normalized; only `../`-prefixed tokens are (`_normalize_pointer_path` 710-715).
Citation `` `corpus/../tools/x.sh` `` (legal, resolvable, used in shell semantics): token unchanged (doesn't start `../`) → `_safe_pointer_path` false (`..` component, 752-756) → the skip branch (743-747) can't take it → yielded verbatim → absent from tree → LG-DANGLING-PTR for a path whose target exists. Same for any mid-path `..`. Related under-scan: `./tools/x.sh` is unmatchable entirely — the lookbehind at 125 excludes a preceding `/`, so no token starts at `tools` inside `./tools`. Precision defect (false positives + blind spot), low frequency in lane prose.
Smallest fix: normpath whenever `..` or `.` appears in any component (keeping the escape>1-level → finding behavior), and allow an optional `./` prefix in POINTER_PATH_RE.

### LOW

L1 — Fleet classification precedes exemption consumption (851-864 before 865-869): an exempted path that resolves under `--fleet-root` is emitted as `fleet` AND its exemption then flagged LG-DANGLING-PTR-EXEMPT-STALE (974-983) — one run emits contradictory classifications for the same path. Latent: verified no current collision (`<fleet>/census/operator-sweep-20261019` and `<fleet>/tests/vault/…` do not exist on this host; the sweep dir lives inside the lane). Smallest fix: consult `exemptions` before the fleet branch (or count fleet-resolved exempt paths as used).

L2 — `--fleet-root` performs no identity check (792-795 + 849-853): any directory is accepted, including `--root` itself; classification is `os.path.exists` on live disk, so pointing fleet-root at a lane checkout converts dangling-at-REV pointers whose paths exist untracked in the working tree into `fleet` data — pure suppression, defeating the committed-bytes-at-REV contract. Docstring declares fleet entries "not findings" (38-39) and the recorded runs used the real fleet root, so residual risk is misuse only. Smallest fix: refuse `--fleet-root` equal to (or inside) `--root`, or require it to be a git repo.

L3 — Exemption keys are not trailing-slash-normalized while tree existence is (865-869 / 763-790 vs 759-760 `_path_exists_in_tree` rstrips `/`): committed row 1 `census/operator-sweep-20261019/` suppresses only because corpus/README.md:81 cites the byte-identical trailing-slash form; a slash-less citation of the same path would dangle, and a slash-less exemption could never match a slash-less directory citation. Fragile exact-string coupling. Smallest fix: rstrip `/` on both exemption keys and pointer candidates before comparison.

L4 — `_expand_braces` refuses single-choice `{a}` and empty-alternative `{a,}` groups, leaving them literal (675-676): bash expands `{a,}` to `a` (+empty), so `` `tools/{good.sh,}` `` flags LG-DANGLING-PTR although the referenced file exists; sequence braces `{1..3}` are likewise unexpanded (only `round-N..M` is). Narrow false-positive surface, undeclared. Smallest fix: treat `{a,}` as expanding to `a` (and document `{a}`/sequence-brace literalness).

L5 — `emit()` returns 2 (refuse-overwrite 1054-1056, write failure 1084-1087) after findings+SUMMARY are already printed (1033-1053): the process rc stops reflecting the computed verdict (0/1 → 2) whenever the `--json` target exists; a wrapper keying on rc reads could-not-evaluate for a fully-evaluated run. Smallest fix: print the refusal and still return the evaluation exit (or write to stdout when the target exists).

L6 — `check_frozen_pins` (459): `rev` parameter is unused (dead param), and the record blob is read twice per frozen dir (539 and the walrus at 559) — two `cat-file` subprocesses where one suffices. Cosmetic/efficiency only.

### Compliance observations (not defects)

- Blank lines in `pointer-exemptions.tsv` → exit 2 (empty row fails `len(fields) != 2`, 772-774). Strict but covered by the documented exit-2 class ("malformed … pointer-exemptions.tsv shape", docstring 31-32).
- Pointer sources (806-822) omit `.ufo/waves/round-N/**` reports, lane-root README, and the round's own census JSON records — the C2 claim text enumerates no source list, so this is declared-behavior coverage shape, not a violated claim; noting as residual risk (report-trailer path citations are unchecked by this axis).
- Pointer candidates are counted per occurrence (`checked_ptrs=319` at b576341, duplicate paths in the before-record) — matches the docstring's "expanded citation candidates"/"occurrences" wording (40-42).

## Exact commands run (all read-only; no lane code executed)

1. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin archive b5763415cc67ecff1e8fe56c58c39a6fb106d7a3|5efb519f00075d958c3d1109ef6fcb24c487eb87 tools/souji-landing-gate.py | tar -x -C /var/tmp/souji-r18w2-RevGatePointerCode/{base,new}` — 1392 / 1989 lines.
2. `python3 -m py_compile /var/tmp/souji-r18w2-RevGatePointerCode/new/tools/souji-landing-gate.py` → OK.
3. `git … diff -U3 b576341 5efb519 -- tools/souji-landing-gate.py` → 837 lines (artifact://106410).
4. `git … grep -n 'operator-sweep-20261019' 5efb519 -- SKILL.md SHONEN.md SCORECARD.md PROVINCE.md corpus LOG.md` → citations at LOG.md:556,745; corpus/README.md:81; r13-r15 lessons (non-scanned sources at r18 except README).
5. `git … grep -n 'vadv54-run/p/p6repo/.git' 5efb519 -- …` → SKILL.md:110 (scanned) — exemption row 2 consumption confirmed.
6. `git … ls-tree b576341 -- corpus/pointer-exemptions.tsv` → 0 entries (absent at baseline).
7. `git … show 5efb519:LOG.md | grep -n '^#'` + `wc -l` → r18 heading at 949, file ends 950, no numbered subheading in section.
8. `git … show 5efb519:tests/fixtures/r14-cache-frozen/{record,expected}.json` → placeholder `measured_commit` present; exemption row 3 consumed via measured branch.
9. `python3 -c` read of `census/round-18/gate-pointers-before-b576341.json` → exit 2, 10 findings, summary as quoted above.
10. `git … show 5efb519:LOG.md | sed -n '944,1100p' | grep -n -E '^#|round-?1[78]'` → section contents verified.

No tool installs or upgrades were performed (git/python3/grep sufficed; pacman untouched per host pause).

## Verdict

Holds — the C2 calibration claim's implementation matches its declared behavior on every attacked axis; no finding invalidates the recorded numbers (before 10 / after 0 shape, checked_measured totality, exemption mechanics). The three medium findings (M1 LOG section scoping, M2 colon-trim ordering, M3 interior-`..` normalization) are latent precision defects that will start emitting wrong answers as LOG correction sections and comma+line-ref citations appear; smallest fixes are each ≤ 6 lines in the functions cited. Residual verification gap: this seat did not execute the gate (no ALLOWED-EXEC); dynamic confirmation of the after-record rests with the rerun seats.
