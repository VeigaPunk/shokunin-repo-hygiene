# S61RevTagDegeneracy — r60 `forgery-rev-at-freeze` degeneration reconstructed

Lane: /home/vgpnk/Projects/shokunin/souji-shokunin · 2026-11-05 · scratch:
/fast/scratch/hyaku/souji-r61/S61RevTagDegeneracy (removed after receipts copied; see Limits).

## 1. Construction (evidence: path:line)

`census/round-60/build-matrix.py`:

- :22-26 (docstring, disclosed): "A commit tree cannot contain its own hash, so the
  forgery-rev-at-freeze case names the freeze commit through the lightweight tag `freezemark`
  placed on the freeze commit; the receipt's `rev=freezemark` resolves to the freeze commit
  itself, which is not a strict ancestor of anything."
- :157-159 `_gen_rev_at_freeze`: `receipt_bytes(b"counter.py", shaC.encode(), TAG.encode(), COUNTER_CMD, HONEST_OUT)`
  — i.e. the ctl receipt carries the **correct** instrument digest; its only forgery is `rev=freezemark`.
- :193-195 CASES entry: `"tag": True`, `"expect": "refuse"`, `"class": "forgery"`.
- :237-250 `build_case`: commit 1 = counter.py+pop.tsv (the ancestor); commit 2 = pre.txt+ctl.txt
  (the freeze — **the receipt is added by the freeze commit itself**); `git tag freezemark <freeze>`.
- Fixed identity/date/tree ⇒ deterministic hashes: ancestor `14ab27ee557cddce1c2735a7ed1e5a960d6ec342`,
  freeze `dc1f00d9a098e2cb424f7baeb3a456afb3284977` (frozen `matrix/forgery-rev-at-freeze/expected.txt`
  pins `ancestor=14ab27ee…`; freeze hash recorded by the r60 executor:
  `census/round-60/wave/w1-results.json`, S60ExecMatrix entry).

Frozen receipt `census/round-60/matrix/forgery-rev-at-freeze/ctl.txt`:
`instrument=counter.py / instrument_sha256=ec07e0ce…(=counter bytes) / rev=freezemark / command=… / EXIT=1`.

## 2. Peel behavior (evidence: path:line)

`tools/souji-freeze-check.py`:

- :93-97 `Repo.commit(rev)` = `rev-parse --verify -q <rev>^{commit}` → it **does** peel: `freezemark^{commit}`
  resolves to the freeze commit `dc1f00d9…` (measured: `peel_equals_freeze=true`).
- :261-271 substance rev check:
  ```
  rv = first("rev=")
  cid = repo.commit(rv) if FULL40.match(rv) else None   # :266 — the gate
  if cid is None:      → CONTROL-REV-INVALID            # :268
  elif cid == freeze or not repo.is_ancestor(cid, freeze):
                       → CONTROL-REV-NOT-BEFORE-FREEZE # :269-271
  ```
  `FULL40.match("freezemark")` fails ⇒ `Repo.commit` is **never called** for the tag ⇒
  `CONTROL-REV-INVALID`, not the intended class. Had the tag reached `Repo.commit`, peel ⇒
  `cid == freeze` ⇒ `CONTROL-REV-NOT-BEFORE-FREEZE` (:269 first disjunct). The top-level gate
  refuses tags too: `--rev freezemark` ⇒ rc=2 `--rev must be a full 40-hex commit id` (measured).
- :140-144 `freeze_rev` already runs `git log --diff-filter=A --no-renames --full-history --reverse
  --format=%H <rev> -- <path>` — but only for the **prereg**, not for Control receipts (the seam C1 r61 extends).
- :475 selftest builds the constructible non-ancestor: `orphan = git("commit-tree", "HEAD^{tree}", "-m", "o")`,
  substituted for `%` (:477-480); SUBSTANCE_CASES `substance-rev-not-before` (:444-445) expects
  `C1:CONTROL-REV-NOT-BEFORE-FREEZE` off that orphan. So a full-40 non-ancestor IS constructible and the
  ancestry branch is live — the frozen matrix case simply never exercised it.

## 3. Which class the committed r60 receipts recorded

- `census/round-60/records/c1-after.txt:11`: `CASE forgery-rev-at-freeze expect=refuse base=accept new=refuse`
  — verdicts only, **no class pinned** (matches SCORECARD.md:1537-1539 "does not assert the finding class").
  Base there = tool bytes at commit `1e8bfd87a9f6ea9a1db4ad34f6e4cdd2b218bcd4` ("round-59 verifier
  spot-check", pre-substance; content sha256 `d1ca06fd…`; has no `--substance` flag: rc=2 if forced).
- The r60 candidate's per-case class is only in wave-seat evidence:
  `census/round-60/wave/w1/S60CriticRound/evidence/c1-candidate-classes.txt:16-18` →
  `FINDING C1 CONTROL-REV-INVALID ctl.txt rev='freezemark' does not resolve to a commit` — and the
  candidate bytes are exactly the r61 base bytes (commit `c7228424c3919ecf142bab1aec8181722d86467b`,
  "round-60 verifier spot-check"; content sha256 `05e9a591…` = current lane tool bytes).

## 4. Reproduction (scratch fixture; throwaway identity; toplevel asserted)

Rebuilt the single case byte-faithfully from the builder constants: `hash_match=true` — ancestor
`14ab27ee…` and freeze `dc1f00d9…` reproduced exactly; generated ctl.txt sha256 `6f2c981a47328b18…`
equals the frozen wave `SHA256SUMS` entry for `matrix/forgery-rev-at-freeze/ctl.txt`; pop.tsv `514c822b…`,
counter `ec07e0ce…` likewise. Observed on the rebuilt case:

| tool bytes | argv | rc | output |
|---|---|---|---|
| c7228424 (r61 base) | `--substance` | **1** | `FINDING C1 CONTROL-REV-INVALID ctl.txt rev='freezemark' does not resolve to a commit` + `SUMMARY claims=1 findings=1` |
| c7228424 | default | 0 | `SUMMARY claims=1 findings=0` |
| c7228424 | `--rev freezemark` | 2 | `REFUSAL COULD-NOT-EVALUATE: --rev must be a full 40-hex commit id` |
| 1e8bfd87 (r60 matrix base) | default | 0 | `SUMMARY claims=1 findings=0` (= c1-after `base=accept`) |
| 1e8bfd87 | `--substance` | 2 | argparse `unrecognized arguments: --substance` |
| current lane bytes | `--substance` | 1 | identical `CONTROL-REV-INVALID` line |
| (peel probe) | `rev-parse --verify -q freezemark^{commit}` | 0 | `dc1f00d9a098e2cb424f7baeb3a456afb3284977` == freeze |

Receipt: `repro-output.json` (this dir), produced by `repro.py`.

## 5. Mutation corroboration

`census/round-60/wave/w1/S60MutMutation/mutants/diffs/c1-m3-rev-at-freeze.diff` deletes the
`cid == freeze` disjunct from :269; `results/c1/c1-m3-rev-at-freeze/triplet.json` verdict **SURVIVED**
(pristine and mutant outputs byte-identical, sha `068677a1…`). Consistent with §2: the case's refusal
comes from the FULL40 gate, so the ancestry clause is dead code for this input — the case has zero
discriminating power over `cid == freeze` semantics.

## 6. Verdict

**The case passed for an accidental reason, not the intended one.** Intended per its name/spec: `rev`
resolves to the freeze commit itself, which is not a strict ancestor ⇒ `CONTROL-REV-NOT-BEFORE-FREEZE`.
Observed (r60 evidence + my reproduction): `CONTROL-REV-INVALID` — the raw string `'freezemark'` is
rejected as non-40-hex before ancestry is ever evaluated; any non-40-hex garbage would pass the case
equally. The tag-peel to the freeze commit never happens in the shipped code path.

Implications for the r61 orphan-commit replacement:

1. The orphan stand-in is the correct replacement shape: a full-40-hex, resolvable, non-ancestor rev
   passes the FULL40 gate, resolves via `^{commit}`, and forces the :269 ancestry branch — exactly what
   the selftest's `%`-orphan already proves and what kills `c1-m3`-class mutants. The S60ExecControls
   rebuild (census/round-60/wave/w1/S60ExecControls/build-matrix.py:133-135) used precisely this.
2. Chronology caveat for the C1 owner [INFERENCE from construction + declared rule]: the r61 rule keys on
   the commit that ADDS the receipt being a strict ancestor of freeze. In all eight r60 matrix shapes the
   Control receipt is added BY the freeze commit (`build_case` commits pre.txt+ctl.txt together), and
   freeze is not a strict ancestor of itself — a strict-ancestor-only rule would fire
   `CONTROL-ADDED-NOT-BEFORE-FREEZE` on the honest shapes too, unless the honest cases are rebuilt with
   pre-freeze receipt commits or the rule admits add==freeze. The real-record expectation (≥2 findings on
   `census/round-60/preregistration.txt`) is consistent with firing at add==freeze; the matrix honest
   shapes then need restructuring to match.
3. Class pinning per case (as the round claims now do) is what r60 lacked — c1-after.txt recorded only
   accept/refuse, so the accidental class was invisible in the committed receipt (SCORECARD.md:1535-1539
   already routes this).

## 7. Named limits

- Read-only on the lane: no production file edited; no git mutation outside the scratch fixture
  (`git rev-parse --show-toplevel` asserted == fixture dir before the first commit); throwaway identity
  `S60ExecMatrix Fixture` only in the fixture.
- Scratch removal was an explicit `rm -rf` after copying receipts, not a `trap`/`finally` guard (shell
  calls here are one-shot pipelines).
- No tools installed or updated (none needed); git 2.56.0 host.
- Observed artifact difference, not investigated (out of scope): frozen
  `census/round-60/matrix/forgery-rev-at-freeze/expected.txt` carries only 4 lines (`case/expect/class/ancestor`),
  without the `freeze=`/`prereg=`/`control_rev=` lines `build-matrix.py:148-155 expected_bytes` emits.
- `census/round-60/records/c1-after.txt` metadata `base-tool=…@1e8bfd87a9f6` is a **commit** id
  ("round-59 verifier spot-check"), not a blob; the object still resolves (`rev-parse --verify …^{commit}`).
