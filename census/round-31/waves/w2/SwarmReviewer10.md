# SwarmReviewer10 — wave 2, C2 gate diff review (souji round 31)

## Status

STATUS: PASS — the landed C2 gate change (single commit 8024b54, identical to the base→tip diff for this file) re-derives every landed number (`fp=0 real=2 cne=0 r26=495` at base content; fixture 10/10 with the always-zero control rejected; REDARM pattern exact; `--selftest` byte-identical base↔tip), and the line-by-line review found six hiding mechanisms plus one new false-fail regression — all reproduced on scratch repos, all latent at current lane content (the live-content differential hides exactly the 13 sanctioned false-positive shapes and nothing else).

## Evidence

- Diff reviewed: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc 2c16d018e40db7c23420a2c3bb546b52957bcc25 -- tools/souji-landing-gate.py` (136 insertions, 24 deletions). `git log --oneline 9f17a1e..2c16d01 -- tools/souji-landing-gate.py` → only `8024b54`; the 8024b54→tip diff for the file is empty, so landing diff = reviewed diff.
- Contract read first: census/round-31/records/preregistration.txt (C2 block, cases G1-G10, REDARM, REAL pair) and census/round-31/records/amendments.txt (A3 discloses the letters-only blind spot and the fence patch provenance; A5 logs the v3 counter).
- Behavior-unchanged: `python3 -B base-gate.py --selftest` and the tip gate's `--selftest` → byte-identical stdout and stderr, rc=0, last line `SELFTEST pass=65 fail=0`. COULD-NOT-EVALUATE (no-reports world): identical stderr and rc=2 on both. `--json`: byte-identical payloads on the same repo/rev; overwrite refusal identical (rc=2, file untouched). Exit codes 0/1/2 consistent across all worlds.
- Fixture re-derivation: tip gate → `cases=10 pass=10 control=FALSE-GREEN-REJECTED` rc=0; base gate → fails G1 G3 G4 G5 G6 G7 G8, passes G2 G9 G10, `cases=10 pass=3 control=FALSE-GREEN-REJECTED` rc=1 (exact REDARM).
- Lane re-derivation at tip (direct gate runs, `--fleet-root /home/vgpnk/Projects/shokunin`): rounds 19/20/24/28 zero LG-DANGLING-PTR; round 23 exactly the two REAL pointers (`census/round-3/garbage-census.out` at corpus/lessons/round-23-verifier-spotcheck.md:28, `tools/__pycache__/` at corpus/lessons/round-23.md:69); round 26 `checked_reports=495` findings=0; round 28 findings=0 (M1 carry sections read).
- Lane at base content with the tip tool: dangling=0 rounds 19/20/24/26/28, 2 REAL at round 23, round 26 `checked_reports=495` → `fp=0 real=2 cne=0 r26=495` re-derived.
- Live-content differential (both gates, rounds 13-30, tip content): base reports 15 dangling, tip 2; the 13 lost are exactly the sanctioned shapes (r19: two `...seat-audit...json` placeholders, one en-dash range, `tools/tests/census/corpus`; r20: two en-dash ranges, `corpus/authority`, `corpus/helper`, `corpus/source/QUALITY`, `tools/kill/killpg`; r24: `corpus/census/tools`; r28: `vadv-49/.gitignore:fixture/` and `corpus/knowledge/registry`). Nothing else is suppressed at current lane content.
- Scratch: /fast/scratch/hyaku/souji-r31/w2-SwarmReviewer10/ (clone with origin dropped, base/tip gate copies, 13 synthetic case worlds plus the COULD-NOT-EVALUATE/`--json`/prose-count checks from a first driver revision, driver `attacks.py`, differential `diff-dangling.py`); removed after deliveries copied.

## Findings

1. **[HIGH — operability, latent] Ellipsis skip is overbroad and regresses against base.** Location tools/souji-landing-gate.py:921 (`or "..." in raw`), evaluated before `_trim_pointer_token`, while the pointer charset (tools/souji-landing-gate.py:144-149) keeps dots inside a token. Any real dangling citation carrying `...` anywhere is never checked; base trimmed trailing dots and reported the real path. Smallest input: cite the C2 REAL-leg path as `census/round-3/garbage-census.out...` → base rc=1 `LG-DANGLING-PTR census/round-3/garbage-census.out`, tip rc=0 (world `ellipsis-trailing`); embedded form `census/round-3/garbage...census.out` likewise (world `ellipsis-embedded`). G4 sanctions only placeholder shapes; a trailing ellipsis is not one. Smallest stricter-only correction: trim first, then skip only tokens with an internal ellipsis.
2. **[MEDIUM — operability, latent] Printf class widened past the sanctioned template shapes.** Location tools/souji-landing-gate.py:946 (`TEMPLATE_POINTER_RE.search(part)`) with the class at tools/souji-landing-gate.py:160-162: a token containing any printf conversion is skipped wholesale. G7 freezes two template shapes; an incidental span inside an ordinary filename is not a template. Smallest input: absent `corpus/notes/50%done.md` cited → base rc=1 `LG-DANGLING-PTR corpus/notes/50%done.md`, tip rc=0 (world `template-incident`). Latent: no such token exists in current lane content (differential clean).
3. **[MEDIUM — operability, latent] `.captured` mapping is not scoped to capture directories.** Location tools/souji-landing-gate.py:987-1010, applied at tools/souji-landing-gate.py:1023 (`stored = _captured_pointer_path(candidate)`): any component named `.git` and any last component `.gitignore`/`.gitattributes` maps onto a `<name>.captured` twin anywhere in the tree. Smallest input: commit `tools/.gitignore.captured`, cite absent `tools/.gitignore` → base rc=1 `LG-DANGLING-PTR tools/.gitignore`, tip rc=0 (world `captured-anywhere`). Mechanism pre-warned by wave-1 SwarmCritic29 finding 5; the landed scope is wider than the capture semantic requires (the lane's five real `.captured` files all sit under census/round-26/waves/).
4. **[MEDIUM — operability, latent] Fence awareness is incomplete: phantom carry sections survive under `~~~` fences and indented code blocks.** Location tools/souji-landing-gate.py:421-424 (`in_fence = not in_fence` on stripped ``` lines only). A quoted `## Seat-reported failures` heading inside a `~~~` fence or a 4-space-indented block still starts a phantom section whose example carry lines satisfy `carries()`, hiding a real uncarried failure. Smallest inputs: worlds `fence-tilde` and `fence-indent` — lesson quotes a carry entry for uncarried failing report Z → base AND tip both rc=0, finding hidden. Control `fence-backtick-control` proves the landed fix does close the backtick shape (tip rc=1 reports Z; base rc=0 hid it). Neither gap is exercised by G1-G10.
5. **[LOW-MEDIUM — operability] New false-fail regression: an unclosed fence blinds every later carry section.** Same location (tools/souji-landing-gate.py:421-424): the toggle never resets at EOF and fires on fence-shaped content. Smallest inputs: worlds `fence-unclosed` (unclosed ``` before a real carry section) and `fence-indent-close` (a 4-space-indented ``` line, which CommonMark treats as content) → base rc=0, tip rc=1 `LG-SEAT-UNCARRIED` for a properly carried report. Base passed both.
6. **[LOW — operability, latent] Union dedupe trusts "the capture is a copy of it" without verifying.** Location tools/souji-landing-gate.py:528-529 (`if wins or suffix not in chosen:`) with the assumption at tools/souji-landing-gate.py:519 (`capture is a copy of it`). When one relative suffix exists in both trees with divergent bytes, the wave copy wins and the capture copy's failure channel is never read. Smallest input: world `dedupe-divergent` (wave copy `STATUS: PASS`, capture copy `STATUS: FAIL - b`, lesson carries nothing) → both gates `checked_reports=1 findings=0` rc=0. Pre-existing at base; the fixture tests identical bytes only (tests/fixtures/r31-landing-gate-precision.py:243-244, `identical bytes at the same relative path in both trees`); wave-1 SwarmExecutor07 risk (b) flagged the same fixture gap.
7. **[INFO — residual, contract-sanctioned] A `:<text>` slot suffix is stripped and never verified to exist inside the file.** Location tools/souji-landing-gate.py:878 (`token = re.sub(r":(?![0-9])[^:\s]*$", "", token)`). World `slot-unverified`: committed `census/r31demo.txt` cited as `census/r31demo.txt:NOSUCHSLOT` → tip rc=0; base rc=1 reported the whole token (one of the false positives the rule removes). G6 freezes the `:fixture/` shape as PASS, so the blindness is by contract; recorded as residual.
8. **[INFO — disclosed] Letters-only prose rule hides absent extension-less all-letters paths.** Location tools/souji-landing-gate.py:1118 (`if _prose_pointer(path):`). World `prose-letters`: absent `corpus/knowledge/missingnote` → base rc=1, tip rc=0; still counted (`checked_ptrs=2` both gates, world `prose-count`). Disclosed by amendment A3 and wave-1 SwarmCritic29 finding 4; reproduced here against the landed gate. No new defect.

## Attack log

| # | World | Input (smallest) | BASE 9f17a1e | TIP 2c16d01 | Verdict |
|---|-------|------------------|--------------|-------------|---------|
| 1 | dedupe-divergent | wave A.md PASS + capture A.md FAIL, no carry | rc=0 reports=1 findings=0 | rc=0 reports=1 findings=0 | hides at both (pre-existing; F6) |
| 2 | fence-tilde | quoted carry section in ~~~ fence | rc=0 (hidden) | rc=0 (hidden) | hides at both; fix incomplete (F4) |
| 3 | fence-indent | quoted carry section, 4-space indent | rc=0 (hidden) | rc=0 (hidden) | hides at both; fix incomplete (F4) |
| 4 | fence-backtick-control | quoted carry section in ``` fence | rc=0 (hidden) | rc=1 LG-SEAT-UNCARRIED Z | landed fix works for ``` |
| 5 | fence-unclosed | unclosed ``` before real carry section | rc=0 | rc=1 false LG-SEAT-UNCARRIED | new false-fail (F5) |
| 6 | fence-indent-close | 4-space-indented ``` line (content) then real section | rc=0 | rc=1 false LG-SEAT-UNCARRIED | new false-fail (F5) |
| 7 | ellipsis-trailing | `census/round-3/garbage-census.out...` | rc=1 LG-DANGLING-PTR (real path) | rc=0 | regression-hiding (F1) |
| 8 | ellipsis-embedded | `census/round-3/garbage...census.out` | rc=1 LG-DANGLING-PTR | rc=0 | regression-hiding (F1) |
| 9 | template-incident | absent `corpus/notes/50%done.md` | rc=1 LG-DANGLING-PTR | rc=0 | regression-hiding (F2) |
| 10 | prose-letters | absent `corpus/knowledge/missingnote` | rc=1 LG-DANGLING-PTR | rc=0 (counted) | disclosed blind spot (F8) |
| 11 | captured-anywhere | absent `tools/.gitignore` + committed `tools/.gitignore.captured` | rc=1 LG-DANGLING-PTR | rc=0 | regression-hiding (F3) |
| 12 | slot-unverified | committed file cited with `:NOSUCHSLOT` | rc=1 (base FP) | rc=0 | intended fix; slot unverified (F7) |
| 13 | clean-control | absent `tools/missing.py` | rc=1 LG-DANGLING-PTR | rc=1 LG-DANGLING-PTR | precision intact |
| 14 | cne-control | no reports | rc=2 CNE | rc=2 CNE (identical stderr) | unchanged |
| 15 | json-control / json-refuse | `--json` on findings world; pre-existing output | identical payload; identical refusal rc=2 | identical | unchanged |

Live-content differential (both gates, rounds 13-30 at tip content): 13 rows lost base→tip, all sanctioned shapes (listed under Evidence); 0 rows gained; the two REAL pointers survive. No hiding mechanism fires on current lane content — every finding above is a constructible input, not a live lane state.

## Deliveries

- .ufo/waves/round-31/w2/SwarmReviewer10.md — this report.
- .ufo/waves/round-31/w2/deliver-c2-diff-review.md — per-rule review with line citations and smallest inputs.
- .ufo/waves/round-31/w2/deliver-c2-attacks.py — the 13-world driver (base vs tip on identical commits); the COULD-NOT-EVALUATE, `--json` and prose-count checks ran in a first driver revision and are quoted under Evidence.
- .ufo/waves/round-31/w2/deliver-c2-attacks.out — full driver output.
- .ufo/waves/round-31/w2/deliver-c2-dangling-differential.py — rounds 13-30 dangling-set differential.
- .ufo/waves/round-31/w2/deliver-c2-dangling-differential.out — differential output.

Toolchain: system Python 3.14.8, git 2.56.0; no tools installed or upgraded; no pacman. Lane untouched (read-only seat); scratch removed.
