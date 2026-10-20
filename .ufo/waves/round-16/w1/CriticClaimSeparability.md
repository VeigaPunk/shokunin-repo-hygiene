# CriticClaimSeparability — round 16 w1 (critic, calibration)

Scope: the round's claim structure (C1 operability, C2 calibration landing gate) against
`/home/vgpnk/Projects/shokunin/AXES.md:27-41`, `SCORECARD.md:11-15`, and
`corpus/lessons/round-15-verifier-spotcheck.md`. I inspected sources and committed bytes only.
Nothing was executed from the lane. `tools/souji-landing-gate.py` is **absent** from the
worktree and from every commit. My read of it failed with "not found". So this review covers
the gate's **contract** (`.ufo/waves/round-16/w1-spec.json` item `LandingGate`), not its code.

Note on wording: this report avoids the literal strings in the gate's pinned marker regex on
purpose (see F4). It is itself a small demonstration that the marker check can be avoided by
rewording.

## Verdict summary

| question | answer |
|---|---|
| Can C1 be verified without C2? | **Yes.** `run-matrix.py` (arms a31642d / cc21683 / b410186 / changed, plus the fixtures, the legacy selftest, `bash -n` and shellcheck) never consults the gate. |
| Can C2 be verified without C1? | **No, as declared.** The after-state is "green at round end", and that depends on C1's bytes in two places (F1). This violates AXES.md:30-32 as written. The fix is to restate the measurement. |
| Does C2 work the lowest axis? | **Nominally yes.** Calibration is 7, against coverage 8 and operability 8 (SCORECARD.md:13-15). **In substance, partly.** Of the three checks, one is core calibration, one duplicates an existing authority, and one detects an operability fault (F2). |
| Real calibration move or a process gate? | **A capability with no binding.** The r15 failure was not missed detection: a seat detected it and L1 landed anyway. The gate changes calibration only if its output binds landing (F3). |
| Is "before 0/3 detected" honest? | **No, as phrased.** The 0 is true by definition, because the tool did not exist. Of the three defects, one was detected before landing by a seat, and one could be detected by a lane checker already committed but not run (F5). |

## Findings

### F1 — C2's after-state depends on C1 (separability violation, fixable)

Counterexample: assume C2's gate is perfect but C1 is rejected, or C1 receives one more patch.
- **LG-PARSE-REG.** `SKILL.md` cites 18 paths that match the gate regex at both b410186 and
  cbf688a. All 18 exist at both revisions (`git cat-file -e`, command 6). One of them is
  `tools/souji-census.sh`. It parses at round end only because of C1, which the spec context
  measures as "parse clean" at cbf688a. If C1 had not landed (b410186 bytes), C2 would show red
  at round end even with a perfect gate.
- **LG-FROZEN-PIN.** Round-end green needs routed fix R4 (the PreservationRepin item) to re-pin
  `tools/souji-census.sh` to the C1 bytes. DraftLessonMistakes.md:15 records the cbf688a
  digest as `fed43c71…`. Fourteen operability reviewers in this wave are proposing "minimal
  patches" to `tools/souji-census.sh`. Any patch L1 integrates after the re-pin invalidates the
  pin, turns C2 red, and requires another re-pin. So C2's verdict depends on C1's final bytes.
- **Double credit.** "census parses at round end" is evidence for C1 (parse clean) and for C2
  (green) at the same time. One state change is booked on two axes.
- **Only post-C1 negative controls exist for pins.** At cc21683 the tree has no
  `tests/fixtures/r15-preservation-frozen` (command 7: `ls-tree` returns only
  `.ufo/waves/round-14` and `corpus/lessons/round-14.md`). LG-FROZEN-PIN is therefore vacuous
  there, with 0 pins checked. That contradicts DraftLessonGate.md:17, which says "the
  pin-defect check fires at `cc21683` too". The same holds for a31642d, which predates the
  frozen directory. The only historical non-vacuous green for that check is the round-end HEAD,
  which depends on C1. Every C1-independent negative control is synthetic.

Smallest correction: measure C2 at the instrument level, on inputs C1 cannot change.
1. `--rev b410186 --round 15` exits 1 with LG-PARSE-REG on `tools/souji-census.sh`,
   LG-FROZEN-PIN on the r15 census pin, and LG-SEAT-UNCARRIED on
   `.ufo/waves/round-15/w1/ConfigRepair.md`.
2. The held-out cases and the no-tool vacuity guard in `tests/fixtures/r16-landing-gate.py`.
3. A synthetic clean repository per check as the negative control, with `checked_reg`,
   `checked_pins` and `checked_markers` all greater than 0, so the control is not vacuous.

Report "green at round-end HEAD" separately, as a conformance line (the Q25 candidate) that is
conditional on C1 and R4. It is not C2's after-state. Then rejecting C1 leaves C2's verdict
intact. If L1 keeps "green at round end" as C2's after-state, the judge has to treat the claims
as non-separable under AXES.md:30-32. That is a structural reject, not a tradeoff.

### F2 — one of the three checks is core calibration, and one duplicates an existing authority

AXES.md:15 defines calibration as "gaps named honestly … overreach caught; SHONEN/SCORECARD
entries match observed repo state".
- **LG-SEAT-UNCARRIED (disclosure carried into the lesson).** This is core calibration. It is
  routed defect R3 / D1.
- **LG-PARSE-REG.** Whether a script runs is operability by definition (AXES.md:13, "scripts
  that run"). The r15 closure booked this exact fault as **operability harmed** (spotcheck
  :35, :49). It touches calibration only through the claim that "the SKILL row matches the
  repo".
- **LG-FROZEN-PIN.** This is a **third** pin authority. The r13 `souji-cert-evidence.py`
  already rejects "tampered frozen inputs" (SCORECARD.md:42). The r15
  `tools/souji-preservation-evidence.py --frozen` already turns a pin mismatch into
  `snapshot_tampered` (b410186 :1641-1705, commands 4-5). The semantics also diverge. The
  checker resolves every `files` entry **under `--root` only** (`_open_regular_beneath(root_fd,
  …, rel)`, :1688-1689). The gate contract resolves it "relative to the frozen dir if that file
  exists there, else relative to the snapshot root".
  - Counterexample: commit `tests/fixtures/r15-preservation-frozen/tools/souji-census.sh` with
    the pinned bytes. The gate reports LG-FROZEN-PIN green, while the authoritative checker
    returns `snapshot_tampered` (exit 2). This is fail-open shadowing, and two authorities
    disagree on the same pin.
  - Correction: the gate should use the checker's root-only resolution, or delegate to the
    checker's `evaluate_frozen` logic. It must never resolve inside the frozen directory.

Impact: C2 does work the lowest axis, but only one check carries the calibration weight. That
check is also the most easily gamed one (F4).

### F3 — process gate without binding (the r15 failure mode is not addressed)

The evidence shows r15 did not lack a detector. `b410186:.ufo/waves/round-15/w1/ConfigRepair.md`
contains a seat-run `bash -n` result, an explicit "revert to `cc21683`" instruction, and a
Checklist line saying the parse currently fails. L1 had that text and landed the file anyway
(spotcheck :7, :30, :124). Routed fix R5 is the same pattern: Q24 was recorded but not enforced.

No round-16 item binds the gate to landing. There is no hook (and hooks are deliberately inert
in this lane), no driver step, and no closure step. L1 runs the gate at its own discretion,
which is exactly the decision point that failed. As specified, C2 is therefore a **capability
acquisition** (AXES.md:40-41, 57-64). It is not yet a calibration move.

Smallest correction, either of:
- (a) Make the report contract require the gate's verbatim SUMMARY and exit code, run at the
  landing commit, so a non-author can re-run it and an author-run green is checked from outside.
- (b) Declare C2 as a capability. It then enters the capability table on its passing
  demonstration, and the calibration score stays 7 under the lane's legacy-unmapped policy
  (SCORECARD.md:14; DraftReportSkeleton.md:43 already says "numeric deltas 0").

The gate itself is additive and harms no axis.

### F4 — the round-end green state measures copying, not disclosure

LG-SEAT-UNCARRIED requires every marker line in any committed `.ufo/waves/round-16/**.md` to
appear verbatim in `corpus/lessons/round-16.md`.
- **Quoted history counts as failures.** Only 9 of 65 r16 seat reports were present when I
  checked. `DraftR15Correction.md` alone already contains 6 marker-matching lines, and all six
  quote **r15 history** (the line-1368 parse error and the closure wording), not r16 failures.
  Critics and revengers dissecting r15 will add more. Green therefore requires L1 to paste
  quotation table rows into the lesson. A wholesale paste-dump turns the check green without
  any disclosure taking place.
- **Rewording avoids the check.** "parse fails", "rc=2", or a `STATUS:` line without the four
  pinned words all pass. This report avoids every marker literal and is not flagged.
- **An absent wave directory passes.** "no wave dir passes" is a pinned selftest case. Landing
  the lesson before committing the seat reports gives a vacuous green.

Smallest correction:
- Exempt quoted, back-ticked or cited-revision text.
- Report `checked_markers`, and treat 0 markers with an existing `w*-spec.json` as exit 2.
- Cross-check the spec's item names against the report files present, so a missing report
  becomes a finding.

CriticGateVacuity owns the detailed regex/held-out analysis. My point here is that "green at
round end" is not evidence of improved disclosure.

### F5 — the "before 0/3 detected" baseline is not honest as phrased

The phrase is not in any committed lane file (I checked LOG.md, SCORECARD.md and the r15/r16
lessons for it). It is L1's framing in this item. The 0 is definitional: no counting command
produces it, because the instrument did not exist. The defect-level facts are:

| defect | detected before landing? | could an existing tool detect it? | detected by |
|---|---|---|---|
| R1 census does not parse | **yes**, by seat ConfigRepair (`bash -n`, b410186 report §STATUS) | yes, `bash -n` / shellcheck | the seat, and the closure by hand |
| R4 pin matches no committed bytes | no | **yes**: the committed r15 checker `--frozen` gives `snapshot_tampered` (b410186 :1641-1705; spotcheck :56) but was never run | the closure by hand |
| D1/R3 seat failure not carried | no | no | the closure by hand |

Honest before-state:
- At landing, L1 carried, disclosed or blocked **0/3**.
- **1/3** was detected before landing (by a seat).
- **1/3** could be detected mechanically by an existing, unrun lane checker.
- **3/3** were detected after landing, by hand, by the non-author closure.

After-state: "3/3 on b410186" is in-sample by construction. The marker regex contains the
ConfigRepair phrasing, and the checks were written from the closure's three findings. Only the
held-out fixture cases are falsifiable.

### F6 — "committed bytes" via `git archive` is not byte identity (relevant to F1/F2)

The installed Git 2.56.0 man page (`/usr/share/man/man1/git-archive.1.gz`, ATTRIBUTES section)
says: `export-ignore` omits files, `export-subst` rewrites placeholders, and attributes come
from the archived tree **and from `$GIT_DIR/info/attributes`**. So uncommitted local state can
hide `.ufo/waves/**`, which triggers the vacuous no-wave-dir green, or change pinned bytes. The
lane currently has no `.git/info/attributes` (read: not found) and no `.gitattributes` at
cbf688a (`ls-tree` empty), so the risk is latent.

[INFERENCE, not verified] `git archive` also applies working-tree conversion, including smudge
filters, to blobs. That would contradict "never executes repository code" for exactly the
filter-driver class C1 guards.

Smallest correction: read blobs with `git -C LANE ls-tree -r -z REV` plus `git cat-file blob`
(or `git show REV:path`), with no attribute processing.

## Impacted axes

- **calibration:** C2's verdict validity (F1, F3), the honesty of its baseline (F5), its
  disclosure semantics (F4), and the duplicate pin authority (F2).
- **operability:** coupling, because further C1 patches void the R4 re-pin and with it C2 (F1).
- **adjacency:** none.

## Smallest safe correction set (for L1; advisory)

1. Restate C2's before→after at the instrument level (F1, items 1-3). Keep the round-end green
   as a separate conformance line, conditional on C1 and R4.
2. Replace "before 0/3 detected" with the four-line baseline in F5.
3. Gate: use root-only pin resolution, matching the checker (F2). Read bytes with blob reads,
   not `git archive` (F6). Make a vacuous `checked_*=0` exit 2, and exempt quoted text from the
   marker check (F4).
4. Either bind the gate in the report contract, or declare C2 a capability with calibration
   kept at 7 (F3).
5. Correct DraftLessonGate.md:17: the frozen-pin check is vacuous at cc21683 and a31642d.

STATUS: advisory review complete. Every check this seat ran succeeded. The gate has not been run
or observed by this seat, because it does not exist yet.

Tool installs/updates: none.

## Commands

Shell commands, verbatim:
1. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline -8`
2. `L=/home/vgpnk/Projects/shokunin/souji-shokunin; for r in b410186 cbf688a; do echo "== $r"; git -C $L ls-tree -r --name-only $r -- .ufo/waves/round-15/w1/ConfigRepair.md corpus/lessons/round-15.md corpus/lessons/round-16.md tests/fixtures/r15-preservation-frozen tools/souji-preservation-evidence.py tools/souji-landing-gate.py .ufo/waves/round-16; done; git -C $L show --stat --format='%H %an %ad' cbf688a`
3. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:.ufo/waves/round-15/w1/ConfigRepair.md`
4. `L=/home/vgpnk/Projects/shokunin/souji-shokunin; git -C $L show b410186:tools/souji-preservation-evidence.py | grep -nE 'snapshot_tampered|--frozen|def .*frozen|sha256' ; git -C $L show b410186:tests/fixtures/r15-preservation-frozen/expected.json`
5. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b410186:tools/souji-preservation-evidence.py | sed -n '1641,1730p'`
6. `L=/home/vgpnk/Projects/shokunin/souji-shokunin; for r in b410186 cbf688a; do echo "== $r"; P=$(git -C $L show $r:SKILL.md | grep -oE '(tools|tests/fixtures|census/round-[0-9]+)/[A-Za-z0-9_.-]+\.(sh|py)' | sort -u); echo "$P" | wc -l; for p in $P; do git -C $L cat-file -e $r:$p 2>/dev/null || echo "MISSING $p"; done; done`
7. `L=/home/vgpnk/Projects/shokunin/souji-shokunin; git -C $L ls-tree --name-only cc21683 -- tests/fixtures/r15-preservation-frozen corpus/lessons/round-14.md .ufo/waves/round-14 .gitattributes; git -C $L ls-tree --name-only cbf688a -- .gitattributes; git -C $L rev-parse --git-path info/attributes`

Non-shell reads, all on exact named files:
- SCORECARD.md
- /home/vgpnk/Projects/shokunin/AXES.md
- corpus/lessons/round-15-verifier-spotcheck.md
- .ufo/waves/round-16/w1-spec.json, read plus Python `json.load` to print item texts
- tools/souji-landing-gate.py (not found)
- /home/vgpnk/Projects/shokunin/.ufo/prompts/souji-round-16.md (grep)
- /usr/share/man/man1/git-archive.1.gz
- .git/info/attributes (not found)
- A Python regex scan of `.ufo/waves/round-16/w1/<ItemName>.md` for each of the 65 spec item names (exact paths, existence-checked), plus LOG.md, SCORECARD.md and corpus/lessons/round-1{5,6}.md, for the `0/3` wording
- A grep of DraftReportSkeleton.md, DraftLessonGate.md and DraftLessonMistakes.md

No lane code was executed. Nothing was written except this report.
