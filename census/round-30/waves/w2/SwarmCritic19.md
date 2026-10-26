# SwarmCritic19 — attack on the round-30 amendments A1-A3 (souji r30, wave 2)

## Status
STATUS: PASS — the attack ran on all three amendments at both scored revisions with both the frozen v1 instrument and the amended instrument. The "before any after-state" ordering holds (02aea48 is a strict ancestor of all three landings), A3 and A1 leave the frozen C1/C2 target literals unmet nowhere by design, and C1/C3 still meet target under v1 and the amended instrument at landing and tip. Three located defects: A1's REGRESS-FULL is broken against its own declared scope and makes the amended C2 target unmet at the C2 landing and at the lane tip; A2's E4 is not a superset of v1's L4 (a corrupted `SHA256SUMS` passes E4); A3's "banner is never accepted" rule is enforced only on the correction path. No defect relaxes a frozen target literal.

## Evidence
Tools (no installs/updates this run): Python 3.14.8, git 2.56.0, jj 0.45.1-7c41cdeb, curl 8.23.0. Contract read: `census/round-30/records/preregistration.txt` (blob of d4928ec) and `census/round-30/records/amendments.txt` (02aea48). Instruments extracted from blobs: v1 C1 = `d4928ec:tools/souji-capability-agreement.py` (4073c97), A3 = 02aea48 copy (9b74d73); v1 C2 = `d4928ec:census/round-30/c2-counter.py`; A1 = `census/round-30/c2-counter-v2.py`; v1 C3 = `d4928ec:census/round-30/c3-counter.py`; A2 = `census/round-30/c3-counter-v2.py`. Runs against a scratch `git clone --no-local` with origin removed; lane read-only.

1. Ordering: amendments.txt:3-4 says "Each amendment adds an instrument; the frozen v1 instrument still runs unchanged" and "2026-10-26 between wave-1 delivery and the first claim landing; no claim's after-state had been measured". Committer chain: 02aea48 02:11:10 → 7b16731 02:11:13 → 68447af 02:11:37 → aea0525 02:12:56 → 76c94eb 02:14:37; `git merge-base --is-ancestor 02aea48 <each landing>` = yes for all three; no landing/capture SHA occurs inside the amendments commit. Author dates are derived (each equals its parent's committer date), so only the committer chain carries order (receipt `SwarmCritic19-timing.txt`).
2. A1 declares the err tail dropped — c2-counter-v2.py:22 "the free-text ` err=<message>` tail of a selftest `CASE` line is dropped" — but implements `re.sub(r"\terr=.*$", "", l) if l.startswith("CASE\t")` (line 69). The real selftest CASE line is `CASE	pass	no-wave-dir-exit2	exit=2 ids=[] paths=[] fleet=[] err=no .md reports under .ufo/waves/round-16/ at <HEX>`: `\terr=` matches False, ` err=` matches True (receipt `SwarmCritic19-regex-tests.txt`).
3. The only base→tip selftest text differences are the two reworded no-reports messages in the `err=` field (receipt `SwarmCritic19-regress-diff.txt`). Consequence, measured: A1 at 68447af `bind=fail dangling=1 ... regress_full=differs`; at tip `bind=ok ... dangling=0 ... regress_full=differs` (receipts `-a1-landing.txt`, `-a1-tip.txt`). With the one-character fix ` err=` the same code prints `regress_full=same` at tip and the exact amended target line, and at landing `dangling=1 bind=fail` only (receipts `-a1-fix-tip.txt`, `-a1-fix-landing.txt`).
4. Frozen v1 C2: landing `SUMMARY reports=86 cne=0 dangling=1 other=7 fixture=ok redarm=ok regress=same` (target miss); tip `dangling=0 other=0` exit 0 (target met). The landing dangling pointer is `LG-DANGLING-PTR	.ufo/waves/round-30/w1/deliver-c1-literal-history.tsv	SCORECARD.md:322 cites path absent at 68447afef62e`, added by the C1 landing (parent commit) and carried only at aea0525 (receipts `-c2-v1-landing.txt`, `-c2-landing-gate.txt`, `-c2-v1-tip.txt`).
5. A3 observation rule: `s = summary_line(normalize(out, work))` then `return rc, (s if s != "NONE" else summary_line(normalize(err, work)))` (lines 173-174). Witness at base: R18 v1 MISMATCH (observed the stderr `Usage: bash ...` banner), A3 MATCH (observed `cases=15 pass=15 control=TAMPER-REJECTED`). At 7b16731 v1 accepts R18 only through the committed banner correction, A3 by direct match. Both instruments still print the target `SUMMARY k1=0 k2=0 mismatches=0 rows=18 pointers=10` at 7b16731 and 9dcd367 (receipts `-c1-*`).
6. A3 tightening works where declared: fixture printing `18/80` with stated `8/8` → v1 MATCH, A3 MISMATCH (receipt `-a3-digit-mutant.txt`).
7. A3 banner rule is correction-only: `BANNER.search(rs)` sits inside the correction loop (line 196); a fixture replaced by `Usage: 9/9` with rc 0 → A3 ROW MATCH (and v1 MATCH) at a rev with no corrections (receipt `-a3-banner-mutant.txt`).
8. A3 KINDS: v1 used an ordered-subsequence test (`all(n in it for n in nums_s)` over an iterator), A3 uses containment `all(n in nums_o for n in nums_s)` (line 206) while the module still describes "the stated integers occur / in S in order" (lines 15-16).
9. A2 E1 is a strict subset of v1 L1: `^ground: F1([ \t]|$)` vs `git grep -lE '^ground: F1\b'`; on `ground: F1-jj` the v1 form matches (1 file), the A2 form does not (0). At tip both count 3 files, entry carries `ground: F1 — ...`.
10. A2 E4 vs v1 L4: E4 `if live != want or b is None or hashlib.sha256(b).hexdigest() != want:` (v2:96) drops v1 L4's `sums.get(...) != h ... fr.get(...)[0] != "200"` (v1:106). Mutant on 76c94eb (first SHA256SUMS hash zeroed): v1 `L4 FAIL`, A2 `E4 PASS` (receipt `-c3-a2-e4-mutant.txt`).
11. A2 target holds at 76c94eb and 9dcd367: `SUMMARY-V2 e1=ok e2=ok e3=ok e4=ok f1_exact=3`; v1 `SUMMARY legs=9 fail=0 f1_entries=3` at both (receipts `-c3-a2-tip.txt`, `-c3-v1-tip.txt`; E3 replay independently rc=0, 10 keep-lines equal).
12. Pre-landing controls committed in 02aea48 (receipt `SwarmCritic19-timing.txt`): C1-A3 base k1=12 vs v1's 13 (the R18 artifact); A3 bypass and banner-correction arms reject (k1=1 each); C2-A1 base `reports=0 ... regress_full=same` (BASE==REV, trivially same) and one stub state with `regress_full=same`; C3-A2 base all legs fail. No arm rewords the no-reports message, and no A2 arm exercises E1's suffix rule, E3's binding, or E4's fetch failure.

## Findings
1. **A1 cannot meet its own target at the C2 landing or the lane tip.** c2-counter-v2.py:69 implements the opposite of :22 (`\terr=` never matches the selftest's ` err=`), so REGRESS-FULL always compares the reworded message. Measured `regress_full=differs` at 68447af and at 9dcd367 with all other legs ok at tip. The amended target (amendments.txt:13) is therefore unmet at the tip; at the landing it is also missed independently (dangling=1). Fixable defect, not a target move: the declared scope at :22 is the authority, so the correction is the one-character bug fix (` err=`), logged with 02aea48 and re-run at both revisions; C2 stays a kill-rule miss from the landing dangling pointer.
2. **A1 was never exercised against the state its declared rule exists for.** The only pre-landing runs are the do-nothing base (BASE==REV, so any comparator is trivially `same`) and a scratch stub commit that changes no selftest text. A1's own text anticipates the reworded message, yet no control rewords it; the first real exposure is the after-measurement at 68447af. That is why the dead regex survived landing.
3. **C2's landing miss is cross-claim ordering, not measurement.** The C1 landing (68447af's parent) added SCORECARD.md:322 citing `.ufo/waves/round-30/w1/deliver-c1-literal-history.tsv`, which aea0525 captured only afterwards; the prereg claims each counter is evaluable at its own landing commit, and C2's is not. A1's BIND cannot repair this and no arm detects it as an ordering artifact.
4. **A1's arms do not distinguish capture-reading of pointers from live-fleet reading.** BIND+NOCAP+PTRARM would all pass a gate that prints COULD-NOT-EVALUATE when the capture is absent but resolves `.ufo/waves/round-N/` pointers from `--fleet-root`; no capture-only pointer is planted. Latent only: the committed gate at 68447af only fleet-resolves `../` and `.ufo/waves/hyaku/` (lines 1017-1021), and the r29 capture's `.md` set equals the live set.
5. **A3's observation rule is not a strict superset of v1's; the amendment's "stricter-only" wording is false as a set relation.** R18 at base is the stable witness (v1 MISMATCH → A3 MATCH). The C1 claim survives only because the v1 instrument is also run, and it was (k1=0 at 7b16731 and 9dcd367 for both). The amendment should state the relation as conjunctive, not inclusion.
6. **A3's "never accepted" banner rule is not implemented on the MATCH path** (line 196 is correction-only). A command that prints a usage banner to stdout, exits 0 and contains the stated digits MATCHes (mutant evidence); v1 does too, so this is a false declaration plus a residual calibration-instrument limit, not a v1 widening.
7. **A3 loosened a diagnostic while its own K1 description still promises order.** Containment at line 206 vs "in order" at lines 15-16; KINDS is not in the target, but the module and the amendment disagree about what the instrument does.
8. **A2's E4 is not a superset of the corresponding v1 leg.** E4 drops v1's local SHA256SUMS and http-column checks; a tree with a corrupted `SHA256SUMS` passes E4 and fails v1 L4. No net target effect (both instruments must pass), but the amendment's per-leg relation is again conjunctive, not inclusion.
9. **A2's pre-landing evidence is negative-only.** The amended control runs C3-v2 at base where every leg fails, which an always-fail instrument also satisfies; E1's `F1-jj` rejection, E3's record binding and E4's could-not-evaluate branch have no committed red arm. All four legs do pass at landing and tip under my independent runs, so this is a receipt gap, not a defect in behaviour.
10. **Tip receipts are missing for all three claims.** c1/c2/c3-after-* are landing-only; the prereg targets also bind the final lane tip, and the tip verdicts exist nowhere in the repo. My measurements: C1 target met at 9dcd367 under both instruments; C2 frozen target met at tip (exit 0) but amended target not met (A1 `regress_full=differs`); C3 met at tip under both. Also, A3 edits the frozen instrument path in place, so at REV `tools/souji-capability-agreement.py` is A3 and v1 is reachable only as the d4928ec blob (declared at :32-34, but unlike the C2/C3 `-v2` siblings no v1 runner is committed beside it).

## Attack log
- A1 timing / "written before after-state": **HOLDS** — strict ancestor of all three landings; controls are base and stub states only; the surviving err bug is itself evidence no after-state run informed A1.
- A1 stricter-only (no accept-widening): **HOLDS** as declared; committed bytes: **BROKEN** — rejects the err-only change at 68447af and 9dcd367, so its own target is unreachable.
- A1 pre-landing test coverage: **BROKEN** — the drop-err branch is dead code and no control exercises a reworded message.
- A2 timing: **HOLDS**. A2 E1 tightening: **HOLDS** (strict subset; `F1-jj` witness). A2 E3/E4 target at landing and tip: **HOLDS** (verified). A2 E4 as a superset of v1 L4: **DEFECT-NOT-FATAL** (SHA256SUMS mutant diverges).
- A3 timing: **HOLDS**. A3 target at landing and tip under v1 and A3: **HOLDS** (both `k1=0`). A3 as a predicate superset (stdout-first): **DEFECT-NOT-FATAL** (R18 witness; held only by the dual-instrument requirement). A3 banner rule: **DEFECT-NOT-FATAL** (MATCH path unguarded). A3 KINDS/docstring order: **DEFECT-NOT-FATAL** (diagnostic only).
- C1 target both instruments, landing + tip: **HOLDS**. C3 target both instruments, landing + tip: **HOLDS**. C2 frozen target: **BROKEN** at landing (`dangling=1`), holds at tip; C2 amended target: **BROKEN** at landing and tip with committed bytes.

## Deliveries
- `.ufo/waves/round-30/w2/SwarmCritic19.md`
- `.ufo/waves/round-30/w2/SwarmCritic19-timing.txt`
- `.ufo/waves/round-30/w2/SwarmCritic19-regex-tests.txt`
- `.ufo/waves/round-30/w2/SwarmCritic19-regress-diff.txt`
- `.ufo/waves/round-30/w2/SwarmCritic19-a1-landing.txt`
- `.ufo/waves/round-30/w2/SwarmCritic19-a1-tip.txt`
- `.ufo/waves/round-30/w2/SwarmCritic19-a1-fix-landing.txt`
- `.ufo/waves/round-30/w2/SwarmCritic19-a1-fix-tip.txt`
- `.ufo/waves/round-30/w2/SwarmCritic19-c2-v1-landing.txt`
- `.ufo/waves/round-30/w2/SwarmCritic19-c2-landing-gate.txt`
- `.ufo/waves/round-30/w2/SwarmCritic19-c2-v1-tip.txt`
- `.ufo/waves/round-30/w2/SwarmCritic19-c1-a3-landing.txt`
- `.ufo/waves/round-30/w2/SwarmCritic19-c1-v1-landing.txt`
- `.ufo/waves/round-30/w2/SwarmCritic19-c1-a3-tip.txt`
- `.ufo/waves/round-30/w2/SwarmCritic19-c1-v1-tip.txt`
- `.ufo/waves/round-30/w2/SwarmCritic19-a3-banner-mutant.txt`
- `.ufo/waves/round-30/w2/SwarmCritic19-a3-digit-mutant.txt`
- `.ufo/waves/round-30/w2/SwarmCritic19-c3-a2-tip.txt`
- `.ufo/waves/round-30/w2/SwarmCritic19-c3-v1-tip.txt`
- `.ufo/waves/round-30/w2/SwarmCritic19-c3-a2-e4-mutant.txt`

Report: .ufo/waves/round-30/w2/SwarmCritic19.md
