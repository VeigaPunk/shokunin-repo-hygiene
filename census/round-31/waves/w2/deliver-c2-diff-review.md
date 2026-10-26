# C2 gate diff review — tools/souji-landing-gate.py, 9f17a1e → 2c16d01

Reviewer: SwarmReviewer10-2 (wave 2, falsification seat). Read-only; all runs in
/fast/scratch/hyaku/souji-r31/w2-SwarmReviewer10/ (removed after delivery).
Driver: 13 synthetic case worlds plus the COULD-NOT-EVALUATE / --json /
prose-count checks (first driver revision), each world run under both gates.

Scope: the gate file is touched by exactly one commit in the range —
`git log --oneline 9f17a1e..2c16d01 -- tools/souji-landing-gate.py` →
`8024b54 round-31: C2 landing-gate reading precision (union discovery, all carry
sections, tokenizer false positives) + fixture G1-G10 + red-before`; the landing
diff and the base→tip diff for this file are identical (post-landing diff empty).

## Per-rule review (can it hide a real finding?)

### R1. Union discovery with suffix dedupe — `_report_paths` (tools/souji-landing-gate.py:509-530)

Union of `.ufo/waves/round-N/` and `census/round-N/waves/`, one entry per
distinct relative suffix. Improves base (base read the wave dir alone whenever
it held any report, hiding capture-only reports; re-derived: base round-26
`checked_reports=466`, tip `checked_reports=495`).

Can hide: **yes, when the two copies of one suffix diverge.** Line 528
`if wins or suffix not in chosen:` makes the wave-dir copy win unconditionally;
docstring line 519 asserts `capture is a copy of it` but nothing verifies byte
equality. A stale/divergent capture's failure channel is never read.
Smallest input (world `dedupe-divergent`): `.ufo/waves/round-31/w1/A.md` =
`STATUS: PASS`, `census/round-31/waves/w1/A.md` = `STATUS: FAIL - b`, lesson
carries nothing → both base and tip: `checked_reports=1 findings=0` (rc=0). The
capture copy's failure is invisible at both revisions — pre-existing at base,
not closed by the landed change. The fixture tests only identical bytes
(tests/fixtures/r31-landing-gate-precision.py:243-244 `identical bytes at the
same relative path in both trees`); wave-1 SwarmExecutor07 risk (b) flagged the
same gap. Latent at current lane content.

### R2. Every-section carry reading with fence awareness — `failures_section_lines` (tools/souji-landing-gate.py:407-438)

Reads every `## Seat-reported failures` section (base read the first only) and
toggles a fence flag on lines whose stripped form starts with ``` (lines
421-424, `in_fence = not in_fence`).

Can hide: **yes — the fence rule is incomplete.** Only backtick fences toggle;
a `~~~` fence or a 4-space-indented code block still lets a quoted
`## Seat-reported failures` heading start a phantom section whose example carry
lines satisfy `carries()`, hiding a real uncarried failure.
Smallest inputs (worlds `fence-tilde`, `fence-indent`): lesson quotes a carry
section inside `~~~` / 4-space indentation, quoting report Z's
`STATUS: FAIL` line with `open`; report Z committed and uncarried → base AND
tip both rc=0, finding hidden. Control `fence-backtick-control` shows the
landed fix does close the backtick shape (tip rc=1, correctly reports Z; base
rc=0 hid it). So the r29-patch direction is right but covers one fence syntax.

Can false-fail: **yes — new regression.** A fence the gate opens and never
closes makes every later real section invisible, so carried reports are
reported uncarried. Worlds `fence-unclosed` (unclosed ``` before the real
section) and `fence-indent-close` (a 4-space-indented ``` line, which
CommonMark treats as content, not a fence): base rc=0, tip rc=1 with
`LG-SEAT-UNCARRIED` for a properly carried report. Base passed both.

### R3. Ellipsis skip — `_pointer_paths` (tools/souji-landing-gate.py:921)

Line 921 `or "..." in raw` skips any raw token containing ASCII `...`, before
`_trim_pointer_token` runs.

Can hide: **yes — and this is a regression against base.** The POINTER_PATH_RE
charset (tools/souji-landing-gate.py:144-149) includes `.`, so a trailing
ellipsis stays inside the token; the skip then kills the whole check. Base had
no ASCII-ellipsis skip, and its trim (`rstrip(".,;:!?")`) stripped trailing
dots, so base resolved and reported the real path.
Smallest input (world `ellipsis-trailing`): spotcheck cites
`census/round-3/garbage-census.out...` (the C2 REAL-leg path with a trailing
ellipsis) → base rc=1 `LG-DANGLING-PTR census/round-3/garbage-census.out`, tip
rc=0. Same for an embedded ellipsis (world `ellipsis-embedded`:
`census/round-3/garbage...census.out`; base rc=1, tip rc=0). The G4 contract
case (`census/round-18/...seat-audit...json`) requires placeholder tokens to
pass, but the implementation is broader than any placeholder shape: any real
dangling citation carrying `...` anywhere goes unchecked. Latent at current
lane content (see differential below).

### R4. Line-range and `:<text>` stripping — `_trim_pointer_token` (tools/souji-landing-gate.py:868-880)

Line 878 `token = re.sub(r":(?![0-9])[^:\s]*$", "", token)` strips a trailing
`:non-digit` suffix; the earlier regex strips `:N`, `:N-M`, `:N–M`, `:N—M`,
`:N,M` ranges.

Can hide: only in the sanctioned sense — the stripped base path is still
resolved and reported when absent; what is never verified is that the stripped
slot exists inside the file (world `slot-unverified`: committed
`census/r31demo.txt` cited as `census/r31demo.txt:NOSUCHSLOT` → tip rc=0; base
rc=1 reported the whole token — that base report was one of the false positives
this rule exists to remove, per prereg `13 false dangling pointers across
rounds 19, 20, 24 and 28`). G6 freezes the `:fixture/` shape as PASS, so the
unverified-slot blindness is contract-sanctioned. Residual, not a defect.

### R5. `.captured` mapping — `_captured_pointer_path` / `_pointer_candidates` (tools/souji-landing-gate.py:987-1027)

Maps any path component named `.git` to `.git.captured` and a last component
`.gitignore`/`.gitattributes` to `<name>.captured`; `check_pointers` resolves
through the candidate list (line 1023 `stored = _captured_pointer_path(candidate)`).

Can hide: **yes — the mapping is not scoped to capture directories.** Any
committed `<name>.captured` file anywhere in the tree masks a dangling pointer
at the live name. Smallest input (world `captured-anywhere`): commit
`tools/.gitignore.captured`, cite absent `tools/.gitignore` → base rc=1
`LG-DANGLING-PTR tools/.gitignore`, tip rc=0. Wave-1 SwarmCritic29 finding 5
warned exactly this (`tools/alpha.py` absent with `tools/alpha.py.captured`
present: base flags, rules silent); the landed gate implements the fallback
anyway, with wider scope than the capture semantic requires (the lane's five
real `.captured` files all live under census/round-26/waves/, so latent today).

### R6. Printf templates — `TEMPLATE_POINTER_RE` (tools/souji-landing-gate.py:160-162), applied at tools/souji-landing-gate.py:946

Line 946 `TEMPLATE_POINTER_RE.search(part)` skips the whole token when any
printf conversion occurs in it. Base skipped only `%s`, `<N>`, `{N}`; the new
class adds `%d`, `%0Nd`, `%02d`, `%.3f`, `%%`, `%c`, `%p`, … .

Can hide: **yes — regression against base for non-template names.** G7 freezes
two template shapes (`census/round-%d/waves/`, `corpus/lessons/round-%02d.md`)
as PASS, but the class matches incidental spans inside ordinary filenames.
Smallest input (world `template-incident`): absent `corpus/notes/50%done.md`
cited → base rc=1 `LG-DANGLING-PTR corpus/notes/50%done.md` (no `%s`/`<N>`/`{N}`
in it), tip rc=0 (`%d` matches inside `50%done`). Latent at current lane
content.

### R7. Letters-only prose — `_prose_pointer` (tools/souji-landing-gate.py:882-890), applied at tools/souji-landing-gate.py:1118

Line 1118 `if _prose_pointer(path):` suppresses reporting (after counting and
exemption bookkeeping) for any token with no trailing `/` whose components are
all letters.

Can hide: **yes — absent extension-less all-letters paths are never reported.**
Smallest input (world `prose-letters`): absent `corpus/knowledge/missingnote`
cited → base rc=1, tip rc=0; the pointer is still counted
(`checked_ptrs=2` both gates in world `prose-count`). This is the disclosed
blind spot: amendment A3 ("the letters-only prose rule cannot tell
`corpus/authority` from a real dangling `census/waves`") and wave-1
SwarmCritic29 finding 4. Reproduced here against the landed gate; disclosed,
not new.

## Unchanged-behaviour checks (all verified this run)

- `--selftest`: base and tip byte-identical stdout and stderr, rc=0, last line
  `SELFTEST pass=65 fail=0` (C1 items L06/L40 binding preserved).
- COULD-NOT-EVALUATE: world with SKILL.md + lesson and no reports → both gates
  rc=2, identical stderr `COULD-NOT-EVALUATE no .md reports under
  .ufo/waves/round-31/ or census/round-31/waves/ at <rev>` (same message text as
  base; check_carry's raise kept).
- `--json`: same repo/rev, base and tip payloads byte-identical; overwrite
  refusal identical (rc=2, `--json output <path> exists; refusing to overwrite`
  on stderr, file untouched).
- Exit codes: 0 clean / 1 findings / 2 could-not-evaluate consistent across all
  worlds and both gates.
- Precision intact: world `clean-control` (absent `tools/missing.py`) reported
  by both gates; the letters-only skip still counts the pointer.

## Live-content differential (is anything hidden in the lane today?)

Both gates run over rounds 13-30 at tip content (rev 2c16d01), LG-DANGLING-PTR
path sets diffed. Base reports 15, tip reports 2; the 13 lost rows are exactly
the sanctioned shapes — round 19: two `...seat-audit...json` placeholders, one
en-dash range, `tools/tests/census/corpus`; round 20: two en-dash ranges,
`corpus/authority`, `corpus/helper`, `corpus/source/QUALITY`, `tools/kill/killpg`;
round 24: `corpus/census/tools`; round 28: the `vadv-49/.gitignore:fixture/`
capture name and `corpus/knowledge/registry`. Round 23 keeps both REAL members
(`census/round-3/garbage-census.out`, `tools/__pycache__/`). No other
suppression: none of the six hiding mechanisms above fires on current lane
content. All are latent — constructible inputs, none live.

## Landed-claim re-derivation (independent)

- Fixture at tip: `cases=10 pass=10 control=FALSE-GREEN-REJECTED`, rc=0.
- Fixture at base (REDARM): fails G1 G3 G4 G5 G6 G7 G8, passes G2 G9 G10
  (`cases=10 pass=3 control=FALSE-GREEN-REJECTED`, rc=1) — exactly the prereg
  REDARM requirement.
- Lane at tip, direct gate runs: rounds 19/20/24/28 zero LG-DANGLING-PTR;
  round 23 exactly the two REAL pointers; round 26 `checked_reports=495`
  findings=0; round 28 findings=0 (M1 carry sections read).
- Lane at base content with the tip tool: dangling=0 for rounds 19/20/24/26/28,
  2 REAL at round 23, round 26 `checked_reports=495` — `fp=0 real=2 cne=0
  r26=495` re-derived.

Versions: Python 3.14.8 (system python3), git 2.56.0. No tools installed or
upgraded; no pacman. Scratch removed after deliveries were copied.
