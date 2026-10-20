STATUS: DONE — C2 is a defensible calibration claim only under a scoped reading; the unguarded count and the sweep scope have four live gaming lanes and two verification-blindness defects.

Seat: `SoujiR18.CriticC2Calibration` (critic, leaf, read-only). Base `b576341`. Axis attacked: **calibration**. No installs; no executions of governed tools; reads and read-only `git ls-tree/log/cat-file/for-each-ref/merge-base` on the lane repo only (probe-rule permitted).

## 1. Is pointer-truthfulness calibration, freshness, or depth? — partial

AXES.md:15 defines calibration as self-assessment honesty: *"SHONEN.md/SCORECARD entries match observed repo state."* Freshness (:14) is drift re-verification; depth (:11) is verifiable detail. A dangling pointer is therefore **two different defects wearing one finding**:

- **Authored-wrong** (cited bytes never existed under that name) = calibration: the entry never matched repo state; the claim of verifiability was overstated at authoring time.
- **Drifted** (existed at `measured_commit`, renamed later) = freshness: the claim was true when recorded, stale now.

Local evidence puts the two headline defects squarely in calibration:

```
git log --all --oneline -- census/round-17/gate-replays-ddb7347.json \
    census/round-17/jj-receipts-ddb7347.txt        → (empty)
git ls-tree b576341 census/round-17/             → gate-replays-4f48343.json,
                                                   jj-receipts-4f48343.txt exist;
                                                   *-ddb7347.* never committed
```

`git log --all` sees `refs/jj/*` too (38 jj refs present), so "never committed" includes jj-held commits. `LOG.md:916` and `corpus/knowledge/jj-colocation-receipts.md:2,44,126,148` cite records that were never in any commit — **self-assessment entries asserted evidence that did not exist**. That is the textbook calibration signal.

**But the swept file set mixes axis signatures.** `SCORECARD.md`, `LOG.md`, `corpus/lessons/round-N.md` are self-assessment → calibration. `corpus/QUALITY.md` (doctrine rules) and `corpus/README.md` (province table) citations are domain surfaces → a dangling pointer there is depth/freshness, not a self-assessment mismatch. The claim counts them together. Smallest safe correction: the C2 evidence must publish the finding split **self-assessment cells vs domain prose**; only the former is the calibration delta, the rest is supporting hygiene. If the residual after splitting is ~2 pointers, the honest claim text is "self-assessment evidence pointers now resolve" — still real (calibration is the lane's lowest axis precisely because of entries like these), but the round report must not present 18→0 as a calibration movement.

## 2. The before→after count is gameable — holds

L1's sweep numbers (281 tokens, 18 unresolved) already conflate classes. Breakdown from the goal text itself: ~2 authored-wrong true findings (`gate-replays-ddb7347.json`, `jj-receipts-ddb7347.txt`), several deliberate non-files (`.ufo/state`, `.ufo/watchdog.log` — verified untracked and absent in the worktree; the operator sweep dir is likewise untracked), several fleet-relative (`.ufo/scopes/…`, `.ufo/waves/hyaku/…` — verified: `.ufo/waves/` in the lane tree contains only `round-13..17`; `hyaku` and `scopes` are fleet-repo paths). "18 → 0" as the measurement is a **before-count inflated ~9× by tokens that were never defects**. A calibration claim measured by an uncalibrated count reproduces the R17-M2 mistake class (LOG :908-926, "29 not 28") it exists to catch. Guard: report `tokens / resolved / findings / fleet / exempted / skipped` separately — the same vacuity rule the gate already applies to falsy `files` pins (`tools/souji-landing-gate.py:464-473`).

Concrete gaming lanes, cheapest first:

1. **`corpus/pointer-exemptions.tsv` as a finding sink.** A "deliberate non-file" row is one line of TSV; anyone can shrink findings by exempting rather than fixing. Verified the file does not yet exist (`ls` → ENOENT), so its contract is written this round. Guards needed: (a) every exemption row must match ≥1 swept token — an unmatched row is itself a finding (dead exemptions hide scope drift); (b) the exempted path must **not** resolve at REV — an exemption for an existing file is a stale-exemption finding; (c) `reason` drawn from a small closed set, non-empty; (d) the gate prints the exemption count and list in its output — silent exemptions are unaudited; (e) optional but cheap: a token inside a SCORECARD axes-row evidence cell may not be exempted — "the evidence is deliberately absent" is self-contradictory for a verdict row.
2. **Delete the pointer instead of fixing it.** Removing "`census/round-17/jj-receipts-ddb7347.txt`" from a knowledge line erases the finding and the evidence hook. Guard: gate diff report must list **tokens removed vs tokens re-pointed** between `--base` and `--rev`; a removed evidence-cell pointer in SCORECARD/SHONEN that is not replaced by a resolving one is a finding (row left unverifiable). For LOG (append-only convention, see §3), deletion is not the repair anyway — a superseding correction is; the count must show corrections appended, not tokens vanished.
3. **Launder through `fleet`.** A dangling lane pointer rewritten to a fleet-resolving path (or the bare claim "see the fleet copy") converts a finding into a non-finding class. Guard: `fleet` tokens are emitted in gate output (listed, capped), never silently suppressed; a token that changed lane→fleet between base and rev is a report item.
4. **Silent skips.** `*`-globs, `<`/`>` placeholders, `round-N` literals, unbalanced braces are skipped — a glob that matches nothing at REV is invisible. Observed live case: `corpus/lessons/round-17.md` cites `census/round-17/jj-receipts-*.txt` (glob → skipped) and `round-17-verifier-spotcheck.md` cites lane paths but is outside the swept file set (the pattern is `round-N.md`, not `round-N-*.md`). Guards: glob tokens must match ≥1 path at REV or be findings; every skip is counted; `round-18` (concrete) must NOT match the `round-N` skip — `census/round-18/leaked-procs-before-1631.txt` exists in the worktree but is untracked (`git status --porcelain` → `?? census/round-18/`; `git ls-tree b576341 census/round-18/` → empty), so it must resolve at the measured REV only after the integration commit — that is the intended check and must not be skipped away.

## 3. Verification-blindness defects in the sweep scope — fails

**D1 — LOG scope is self-contradictory with the count.** The finding applies to "LOG.md's round-N section" only. The before-count's flagship defect sits at `LOG.md:916`, inside the round-16 corrections block (LOG structure: `## 2026-10-20 — round 16 correction…` :908, `## …round 17…` :944). Under a literal reading the new gate can never verify the R2 repair — its own before-number includes a token outside its sweep. Worse, LOG is append-only: the lane's own correction entries (:886 `:908` `:927`) stand "as written" with the fix appended. If round-18 appends a correction, `LOG.md:916`'s dangling token stays forever — the gate must either (a) sweep all of LOG.md (preferred: a historical dangling pointer is still a calibration defect; the repair is that the correction entry's *new* pointer resolves, and the finding text should name the superseding line), or (b) exempt `LOG.md:916` — which is exactly the exemptions-sink abuse in §2. Pick (a) and the honest before→after is the full-LOG count.

**D2 — SHONEN.md is outside the swept set.** AXES.md:15 names SHONEN.md first as the calibration surface; the sweep list omits it. Today its pointers all resolve (verified: `tests/fixtures/r13-repo-structure.sh`, `census/round-13/verification.json`, `.ufo/waves/round-13/w1/Overlap.md`, `corpus/SOURCES.md`, `corpus/lessons/round-13.md` all `cat-file -e` clean at b576341) — but a calibration claim whose gate cannot see the canonical self-assessment file is a scope miss on the claim's own axis. Add it; costs one row.

**D3 — `LG-FROZEN-MEASURED` extension must reuse the existing resolve check AND harden it.** `tools/souji-landing-gate.py:545-567` already runs `git rev-parse --verify --quiet <measured>^{commit}`; a resolving commit enables the pin cross-check, a non-resolving one currently just sets `measured_ok=False` and silently contributes zero checks. Closing Q25(b) = emit `LG-FROZEN-MEASURED` on that silent path — correct, but note the subtler trap: `rev-parse --verify` also resolves commits held **only by `refs/jj/keep/*`** (38 jj refs present at b576341). The lane's own rule (`corpus/knowledge/jj-colocation-receipts.md:79-80`) says such commits are not durably replayable — a jj `util gc` can delete them, turning a verified record into a dangling one post-admission. The durable form is `git merge-base --is-ancestor <c> refs/heads/master` (the closure itself used this shape, `round-17-verifier-spotcheck.md:35`). Requiring durable-ref reachability for `measured_commit` is the smallest change that makes the finding mean "replayable forever," not "visible today."

**D4 — vacuity.** If every swept file is deleted or the tokenizer matches zero tokens, "0 findings" must be exit-2 could-not-evaluate, not clean — same fail-closed shape as the falsy-`files` rule at `tools/souji-landing-gate.py:469-473`. Also: a `--round 17` run of the changed gate must not report a clean sweep it never performed; emit a `checks-skipped` diagnostic so replay silence isn't mistaken for zero findings.

## 4. Impacted axes

- **calibration** — the claim's axis and the target of every guard above: exemption sink, deletion-vs-fix, count inflation, LOG/SHONEN scope, silent skips.
- **operability** — a `fleet`-laundered or glob-skipped citation is also an operability defect (the command the reader was told to run doesn't exist); the finding classes must not let those vanish.
- **coverage** — neutral; the sweep is a new governed surface, already claimed under C3's pattern of residue governance. No harm found to C1/C3.

## 5. Verdict and smallest safe correction

**Verdict: partial.** The claim targets a real calibration defect class (authored-wrong self-assessment evidence — proven never-committed at base) and the mechanism is sound. But as specified, (a) the measurement mixes calibration with freshness/depth findings and inflates the before-count with deliberate/fleet tokens; (b) the LOG-section scope cannot even observe the repair of `LOG.md:916` it counts as a before-finding; (c) exemptions, token deletion, fleet-laundering and silent skips each provide a cheaper path to "0" than fixing anything.

**Smallest safe correction (all implementable inside the declared contract):**

1. Report the sweep as `tokens / resolved / findings / fleet / exempted / skipped`; "0 findings" is only valid with a nonzero token count (exit 2 otherwise).
2. Sweep all of LOG.md (or split the finding into `LG-DANGLING-PTR` for current-section and a carried `superseded` class for historical sections whose repair is an appended resolving correction); add SHONEN.md.
3. Exemptions: must-match-token, must-not-resolve, closed reason set, counted and listed; never allowed in SCORECARD/SHONEN evidence cells.
4. Glob tokens: ≥1 match at REV or a finding; `fleet` tokens listed not suppressed; removed-vs-repointed tokens diffed against `--base`.
5. `LG-FROZEN-MEASURED`: emit on non-resolving `measured_commit` (existing `rev-parse` path) and require durable-ref ancestry, not bare `^{commit}` visibility — per the lane's own jj-keep rule.
6. Publish the authored-wrong vs drifted split: authored-wrong = calibration delta; drifted = freshness hygiene riding along. The r18 residue is almost entirely authored-wrong, so the claim survives honest accounting — but only that accounting makes it a calibration claim rather than a lint count.
