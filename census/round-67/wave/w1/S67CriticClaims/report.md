# S67CriticClaims — round-67 attack on the frozen claims (C1 operability, C2 calibration)

Seat: critic (leaf, no subagent dispatch). Lane HEAD at review: `4c61efcb` (freeze attempt 4). Base `3639087917` (= `36390879`, the round-66 spot-check commit; SKILL.md and writer bytes identical to `c13fbb4e`, writer sha256 `a8c47d36…97fc`). Instruments `05eb2cee`.
Lane tree is dirty (` M corpus/QUALITY.md`, not written by this seat; left untouched). Lane was read only (`git show`, `git for-each-ref`, counter runs that write nothing to the lane). No git mutation anywhere; no tools installed or upgraded. Candidate bytes do not exist yet: every "candidate" below is a probe mutant built by this seat from base bytes, in scratch, and is labelled as such. Receipts: `receipts.txt` beside this file (88 lines, machine output). Scratch removed at exit.

## Verdicts

| claim | verdict | one-line reason |
|---|---|---|
| C1 operability (receipt-binding) | **would-reject as worded** | The frozen target is met (`SUMMARY matrix=31 base_forgeries=2 base_honest=6 new_forgeries=0 new_honest=6 class_mismatches=0 regress=PASS`, `EXIT=0`) by a probe candidate that value-checks `GIT_COMMON_DIR` and never scrubs it. The claim's "every git call scrubs the variable" and "empty value refuses" clauses have no falsifier in the frozen matrix. The value-check sub-claim (W1/W2 refuse, W3 accepts) is sound and measured. |
| C2 calibration (bookkeeping-file, lowest axis 7) | **would-accept on substance, with three defects the L1 must disclose** | The corrected counter discriminates: at the pinned state it prints `FINDING SCOPE-OVERREACH s5` and `findings=1 verdict=FAIL`; the reverted-rule mutant fails `--selftest` on `m10-s5-assertion-line-not-live` (MISMATCH, `fail=1`); the enum-weakened mutant prints `findings=0 verdict=PASS`. Defects: (i) the target literal `cases=17 pass=17` is not printed by the counter; (ii) the committed do-nothing control is at the wrong revision and the base state meets the target shape; (iii) "enumeration-bound" is cosmetic — `REDIRECT_ENUM` is defined and never iterated. |

Per-claim detail follows. Items are numbered to the seven attack lines in the seat brief.

---

## 1. Causal separability

**C2 reads only pinned bytes.** `c2-counter.py` reads the population as a blob at `--tsv-rev 05eb2cee`, then `SKILL.md` and `tools/souji-receipt-write.py` as blobs at `--rev c13fbb4e` (`git -C ROOT show REV:PATH`). It never opens a working-tree file for the measured content. A C1 landing creates a commit that descends from `4c61efcb`; it cannot change the blob at `c13fbb4e`. Would C2 verify if the candidate never landed? Yes — the counter output at `36390879` (same bytes) is identical to the pinned-state output (see §2).

**C1 reads no C2 byte.** `c1-counter.py` uses `c1-matrix.tsv`, the base writer blob, the candidate bytes and the `tests/fixtures/r60-receipt-write.py` regress fixture. It imports nothing from `census/round-67/c2-*`. Would C1 verify if C2's instruments were deleted? Yes.

**Couplings found (none is a byte-level coupling of the two verdicts; all are environment or revision-binding defects):**

- **(a) Ambient `GIT_*` leaks into both counters.** `c2-counter.py` `git_show` inherits `os.environ` with no scrub. `c1-counter.py` `clean_env` removes `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`, the object/alternate/replace variables and the config variables, but **not `GIT_COMMON_DIR`**, so the counter's own fixture builds and `git show` calls honour a caller-set common dir. Current shell: no `GIT_COMMON_DIR` or `GIT_DIR` set; the lane has 0 `refs/replace` entries, so no replacement is in effect today. Probe: `GIT_COMMON_DIR` pointing at a scratch copy of the lane `.git` makes the C1 counter fail closed (`C1-COUNTER-FATAL: regress fixture unavailable: lane clone failed`). Fail-closed for that value only; the code shows no scrub, so another value is not guaranteed to fail closed. [observed for one value; code-read for the rest]
- **(b) C1 regress fixture is read from the lane clone's HEAD, not from `--rev`.** `fixture_from_clone` clones the lane (`git clone --shared`, default HEAD) and takes the fixture from that checkout. The base-blob cross-check is printed as `cross-check=DIVERGES …` and is **not part of the verdict**. This violates Q37 (a consumer reads every byte from the revision) and makes C1's regress arm depend on whatever HEAD is at measurement time. Defect, low-medium.
- **(c)** Nothing else is shared between the two counters beyond the lane object store and the `--work` directory (each must be distinct and outside `--root`, which the counters enforce).

## 2. Do-nothing controls

**C1.** The committed do-nothing `census/round-67/controls/c1-do-nothing.txt` (base bytes in the new slot) prints `new_forgeries=2 class_mismatches=2`, `EXIT=1`. It fails the target. Good. The control is not the whole story: a value-check candidate **without scrub** also meets the target exactly (§4 below), so the frozen target does not separate "value-check + scrub" from "value-check only". That is the hole that matters for C1.

**C2 — answer to the specific question.** The base state `36390879` (= `3639087917`, the C2 `Base:` in the prereg) prints, with the frozen counter and population:

```
FINDING SCOPE-OVERREACH s5: stable wording: claim redirects_closed needs writer markers cdred; writer blob lacks them
MARKERS flag=1 inrun=1 env=1 unmerged=1 envcfg=1 envred=1 cdred=0
SUMMARY rows=5 findings=1 verdict=FAIL rev=3639087917eaeb28719d7603110a6ec22782100e
EXIT=1
```

This is the target shape, identical to the pinned-state output apart from the `rev=` suffix. So **yes, the base state meets the target shape.**

Does the frozen kill rule exclude it? **Only through the literal `--rev c13fbb4e…` in the target command.** The kill words ("findings=0 at the pinned state", "findings>1", "any other kind") do not name a revision. Consequence: the target is a single-revision measurement and a reader who re-derives it at the C2 base gets a green-looking identical result. That is not a claim failure (the counter does detect the r66 s5 overreach on that state, which is what C2 claims), but it means the committed do-nothing control is **not** a no-work discriminator for C2:

- The committed C2 do-nothing control is the r67 counter at `045e103478…` (`controls/c2-do-nothing.txt`): `FINDING GOVERNED-STATEMENT-UNRESOLVED s5`, `findings=1`, `EXIT=1`. I reproduced it. It is red for a different reason (s5 absent at that state). The prereg names `3639087917` as C2's Base; a control at `045e1034` violates the Q58 rule that a numeric target is derived at the named base.
- The genuine no-work world for calibration is "counter not corrected": the r66 counter at the pinned state prints `SUMMARY rows=5 findings=0 verdict=PASS`, `EXIT=0` (`controls/c2-do-nothing-r66.txt`, committed). That is the discriminator, and it already exists. **The L1 must cite this file, not the `045e1034` control, as the do-nothing arm in the report.**

Verdict on this item: derivation/documentation hole, not a kill hole.

[INFERENCE, not run] A counter that hard-codes the `s5` finding in `run()` would also meet the frozen C2 target and pass the selftest (the selftest does not exercise `run()`). It is caught only by the enum-weakened recipe: that recipe still applies to the anchor `"redirects_closed": ("envred", "cdred"),`, and the mutant would still score the finding — which the kill rule names as a failure. So the kill rule covers it, but only through that one recipe.

## 3. Universal-clause and scope scan (Q59 R4, Q59 R2)

**3a. The Q59 R4 scan reads only the MACHINE BLOCK.** `parse_prereg` collects only lines inside `## MACHINE BLOCK … END` into `raw`, and R4 searches only `raw`. The claim prose ("every git call scrubs", "mismatching or empty value", "closed for the caller-injected config and object-redirect routes") is never scanned. R4 flags=0 is therefore structurally silent on the claim sentences. Verified by reading the code.

**3b. Receipt-binding is neutral in R2, so C1's axis is not checked by any instrument.** `NEUTRAL_SURFACES = {"receipt-binding", "measurement"}`. I flipped the C1 block's `axis:` from `operability` to `coverage` in a scratch copy of the frozen prereg: `claims=2 flags=0`, `EXIT=0`. A misattributed axis passes. This is a Q59 defect: the instrument cannot falsify the axis for the surface class C1 declares. (Note: `R3` passes because C2 declares the lowest axis, calibration.)

**3c. C1 universal and unenumerated shapes.** The C1 machine block's `enumerate:` line names matrix rows A…W3; it names no `GIT_COMMON_DIR` caller shape. Shapes outside the rows that the claim wording covers:

| shape | covered by a row? | measured? |
|---|---|---|
| relative value (`main/.git`) with writer cwd ≠ root | no | **yes, by my probe W4 (§4)**: the scrub is the only protection; the value check's base is wrong |
| empty value `GIT_COMMON_DIR=` | no | probed, not a row: base refuses with `rev is not a commit object` (a different class); a candidate refuses with `RECEIPT-ENV-COMMONDIR-MISMATCH: empty GIT_COMMON_DIR`. The claimed class is reached only by a candidate; nothing in the matrix would notice a different class |
| linked worktree root | no | probed (§5): honest equal value accepted, mismatch refused, scrub safe |
| submodule root (`.git` file → superproject `modules/<name>`, no `commondir` file) | no | [INFERENCE] equal-value honest run should be accepted; a candidate comparing against `--git-dir` in a submodule would be fine, against `--git-dir` in a linked worktree would false-refuse. Not probed |
| other git-resolution names (`GIT_NAMESPACE`, `GIT_CEILING_DIRECTORIES`) | not in the claim's "GIT_COMMON_DIR" scope | named limit L3 (correctly out of scope) |

**3d. C2 `s5` universal claim ("closed for the caller-injected config and object-redirect routes").** Two halves, both checked only at marker level:

- **Object-redirect half.** `REDIRECT_ENUM = (GIT_OBJECT_DIRECTORY, GIT_ALTERNATE_OBJECT_DIRECTORIES, GIT_REPLACE_REF_BASE, GIT_COMMON_DIR)` is defined. **It is never referenced by any code path** (grep: definition and comments only). The `redirects_closed` claim requires the literal markers `RECEIPT-ENV-REDIRECT-SET` and `RECEIPT-ENV-COMMONDIR-MISMATCH`. A writer that refuses only `GIT_OBJECT_DIRECTORY` and prints the shared class literal satisfies the claim. The "enumeration-bound" wording (prereg, counter docstring, and as I read the truncated Q130 row) overstates what is checked. This is the r66 M5 defect class again, one level down. Defect, medium.
- **Config half.** `RECEIPT-ENV-CONFIG-SET` is one literal for every config name. A writer refusing only `GIT_CONFIG_COUNT` still satisfies `envcfg`. Named "config routes" are not enumerated at all. Also, `GIT_CONFIG_GLOBAL` is repointed to the null device (E3 row, refusal class `lane worktree is dirty`), not refused with `RECEIPT-ENV-CONFIG-SET`, so the sentence "closed … by the refusals RECEIPT-ENV-CONFIG-SET and RECEIPT-ENV-REDIRECT-SET" is mechanism-inaccurate for that name. Defect, low-medium.

**3e. Limit text that overstates a hole (L1).** The prereg's named limit L1 says repository-local `core.excludesFile` still hides untracked content on both slots. At base, `git()` already passes `-c core.excludesFile=<null device>` on every call, which overrides repository-local config. Probe (§6): a repository-local `core.excludesFile` hiding `hidden.txt` → base writer **refused** `dirty` (rc 2). The surviving ignore route is `.git/info/exclude`: base writer **wrote** a receipt with the hidden untracked file present (rc 0). A tracked `.gitignore` was not probed. L1 should say so in the lesson, with the `reading:` line Q60 requires.

## 4. The scrub: what the frozen target can and cannot see (Q22 no-harm, attack 4)

I built two probe candidates from base bytes, identical except for the scrub, both with a value check inserted before the `rev` check:

- `mut-noscrub.py`: value check only. The check canonicalises the caller value against the writer's cwd and compares with the repository's own common dir (`git -C root rev-parse --git-common-dir`, run with `GIT_COMMON_DIR` removed from the child environment).
- `mut-scrub.py`: the same plus `GIT_COMMON_DIR` added to the `git()` scrub tuple.

**Frozen target on each (run from the lane, `--new-tool` scratch bytes, `--base-rev 3639087917`):**

```
no-scrub:  SUMMARY matrix=31 base_forgeries=2 base_honest=6 new_forgeries=0 new_honest=6 class_mismatches=0 regress=PASS   EXIT=0
scrub:     SUMMARY matrix=31 base_forgeries=2 base_honest=6 new_forgeries=0 new_honest=6 class_mismatches=0 regress=PASS   EXIT=0
```

Both meet the target. The reason: with W1/W2 the value check refuses before any git call (so the scrub never runs); with W3 the value equals the real common dir (so the scrub changes nothing); no other row carries a caller value. **The scrub clause of C1 is observationally inert in the frozen matrix.** That is the critic's central finding for C1.

**Probe W4 — the scrub is load-bearing for a relative value.** Lane-independent fixture: `main/` repository with a tracked 755→644 change; a poisoned copy at `main/main/.git` (`core.fileMode=false`), hidden from status by `.git/info/exclude`. Writer cwd = parent of `main`, `GIT_COMMON_DIR=main/.git`, `--root main`, no `--allow-dirty`:

```
base-writer.py   rc=0  WROTE    (receipt over a dirty tree: forgery)
mut-noscrub.py   rc=0  WROTE    (value check passes: canonicalised against cwd; git, run with -C main, reads the poison)
mut-scrub.py     rc=2  ABSENT   refused: lane worktree is dirty
```

Why: `git -C root` changes git's working directory before it resolves `GIT_COMMON_DIR`, so a relative value is resolved against **root**. Probe: `(cd $P && GIT_COMMON_DIR=main/.git git -C $main rev-parse --git-common-dir)` prints `main/.git`, which is `$main/main/.git`, the poison. The writer's value check resolves the same string against its **own** cwd. The two bases disagree. The prereg's L2 sentence ("a relative value is canonicalised against the writer process's cwd, the rule git applies") is therefore **factually wrong**: the rule git applies is the `-C` root. With the scrub the mismatch is harmless (git never sees the value); without it the check passes a value git then honours. Q22's "effect-aware" standard is not met by a cwd-based check.

Consequence for no-harm: a writer started from a cwd other than root with an honest relative value `.git` would be refused by the cwd-based check [INFERENCE from the canonicalisation base; not run].

**Recommended fix for the candidate and the next counter (not applied; the candidate is the wave's):** canonicalise against `--root`, refuse any relative value, and add W4 (expected class `RECEIPT-ENV-COMMONDIR-MISMATCH` with a root-based check; the probe above is the fixture) to the next frozen counter.

## 5. Linked worktree (attack 4, scrub safety)

Probe (scratch linked worktree `wt` of `main`; mutants from §4):

```
no-scrub: none=WROTE  equal=WROTE  wt-gitdir value=refused COMMONDIR-MISMATCH  copy(fileMode=false) value=refused COMMONDIR-MISMATCH
scrub:    none=WROTE  equal=WROTE  wt-gitdir value=refused COMMONDIR-MISMATCH  copy(fileMode=false) value=refused COMMONDIR-MISMATCH
```

Reason (git semantics): when `GIT_COMMON_DIR` is unset, git resolves a linked worktree's common dir from the worktree gitdir's `commondir` file, which is exactly the directory the scrubbed child then uses. Scrubbing therefore cannot break a linked worktree, and the equal-value run is accepted. The attack on linked worktrees is **not** a defect of the scrub. It is an unmeasured shape: no frozen row covers a linked-worktree honest run, so a candidate that compared the caller value with `--git-dir` (the worktree's gitdir) instead of the common dir would false-refuse honest linked-worktree runs and the matrix would not notice. Named limit proposal.

## 6. Other probes (scratch, machine-observed)

- `git rev-parse --git-common-dir` in a plain repo prints `.git` (relative). The value check must realpath both sides, which the probe mutants do.
- Empty `GIT_COMMON_DIR` makes git itself fail (`not a git repository`, rc 128). Base writer refuses it with a non-COMMONDIR class (`rev is not a commit object`).
- Repository-local `core.excludesFile` is neutralised by the base's `-c` pin (see §3e). `.git/info/exclude` is not.

## 7. Claim sizing and machine-checkability (attack 5)

- **Two claims, distinct axes** (operability, calibration). Calibration is the lowest axis (7) and C2 declares it: `claims=2 flags=0`, `EXIT=0` on the frozen prereg (R3 passes). Reproduced.
- **C2 "no other row or kind" is machine-checkable from the counter output alone**: count lines beginning `FINDING ` (must be 1) and check the prefix `FINDING SCOPE-OVERREACH s5:` (the detail text after the colon is not part of the claim). Verified on the pinned-state output.
- **C2 literal defect.** The target says the declared counter's `--selftest` "prints `cases=17 pass=17`, `EXIT=0`". It prints `SELFTEST pass cases=17 fail=0` and `EXIT=0` (observed). The semantic (17/17 cases pass, `STUB-ALWAYS-ZERO REJECTED`) holds; the literal does not. The mutant literals (`SELFTEST-CASE m10-s5-assertion-line-not-live: findings=0 want=1 MISMATCH`, `SELFTEST pass cases=17 fail=1`, `EXIT=1`) match exactly. Under a strict literal reading the selftest sub-check fails. The prereg is frozen and must not be edited; the L1 must disclose this.
- **C1 literal.** The `SUMMARY matrix=31 … regress=PASS` line and `EXIT=` match the counter's output format (observed on both probe candidates and the do-nothing control).
- **No retroactive narrowing hooks found** in the frozen text beyond L1 (overstated, §3e) and the Q60 exclusion-reading duty: L1–L6 and the counter's "not probed as rows" list are exclusion clauses. Q60 requires a `reading:` line in the round lesson head, before any after-data, listing the excluded ids and the target. No `corpus/lessons/round-67*` file exists yet (checked). L1 must write it.

## Counter-measured kill power (C2, pinned state)

| run | result | expected |
|---|---|---|
| frozen counter, `--rev c13fbb4e` | `FINDING SCOPE-OVERREACH s5`, `SUMMARY rows=5 findings=1 verdict=FAIL`, `EXIT=1` | matches |
| frozen counter, `--rev 3639087917` (base) | identical shape | see §2 |
| frozen counter `--selftest` | `SELFTEST pass cases=17 fail=0`, `EXIT=0` | literal `cases=17 pass=17` not printed (§7) |
| reverted-rule mutant `--selftest` | `SELFTEST-CASE m10-s5-assertion-line-not-live: findings=0 want=1 MISMATCH`, `SELFTEST pass cases=17 fail=1`, `EXIT=1` | matches |
| enum-weakened mutant at `c13fbb4e` | `SUMMARY rows=5 findings=0 verdict=PASS`, `EXIT=0` | matches |
| enum-weakened mutant `--selftest` | `SELFTEST-CASE redirects-closed-scope-overreach-at-r66: findings=0 want=1 MISMATCH`, `fail=1` | not a frozen target; the kill is also visible here |
| do-nothing, r67 counter at `045e1034` | `FINDING GOVERNED-STATEMENT-UNRESOLVED s5`, `findings=1`, `EXIT=1` | red, different kind (§2) |

## Defects and limits, consolidated

Defects (the L1 must record them; none is fixed here):
1. **C1 scrub clause unmeasured** (§4). Frozen target is met by a no-scrub candidate. Add a relative-value row (W4) and an empty-value row in the next frozen counter; until then, record "scrub" and "empty" as unmeasured named limits and do not count them as passes.
2. **C1 relative-value base is wrong** (§4): L2 misstates git's resolution base; the check should be root-relative.
3. **C1 axis unchecked** (§3b): `receipt-binding` is neutral in R2; the Q59 instrument cannot falsify the axis. Instrument defect for the axis-check owner.
4. **Q59 R4 scans only the machine block** (§3a): prose is never scanned.
5. **C2 enumeration is cosmetic** (§3d): `REDIRECT_ENUM` never iterated; the check is one literal per class. The Q130 wording (as far as I could read it truncated) claims an enumeration check that the counter does not perform. Q130 is in the uncommitted `corpus/QUALITY.md` edit; the lane must not land that sentence as-is.
6. **C2 literal** (§7): `cases=17 pass=17` not printed.
7. **C2 do-nothing control at the wrong revision** (§2): cite the r66-counter before-arm as the do-nothing.
8. **C1 regress fixture not read from `--rev`** (§1b, Q37).
9. **Counter hermeticity** (§1a): `GIT_COMMON_DIR` not scrubbed in `c1-counter.py clean_env`; not scrubbed in `c2-counter.py git_show`.
10. **L1 overstates a closed route** (§3e): repository-local `core.excludesFile` is already closed by the base pin.

Named limits recommended (not counted as passes, for the lesson's `reading:` line):
- scrub of `GIT_COMMON_DIR` on every git call: not measured by the frozen matrix (§4).
- empty value: not a row (§3c).
- relative value: base wrong; not measured (§4).
- linked-worktree and submodule honest runs: not rows (§3c, §5).
- `.git/info/exclude`: a live route, measured (§3e). `.gitignore` tracked: not probed.

## Notes on what this seat did not do

- No candidate writer exists in the lane; probe mutants were built from base bytes in scratch and are not the wave's candidate. The candidate's real scrub and value-check code must be re-probed with the W4 fixture when it lands.
- The C1 regress arm was not re-run against the lane HEAD fixture; §1b is a code-read finding.
- No edits to frozen files, MANIFEST, `.ufo/state`, watchdog, fleet templates/scripts, or sibling repos. No commit, push, or mutating git/jj command. Scratch removed; receipts kept in this directory.
