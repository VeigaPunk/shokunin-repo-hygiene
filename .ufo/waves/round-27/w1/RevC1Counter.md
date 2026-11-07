## Status
STATUS: PASS — the C1 counter is sound under the exact frozen invocation (findings=2 reproduced byte-for-byte at e78ac7c, exemptions load from the rev-pinned tree, wildcards structurally rejected, unused exempt rows flagged stale), but it is gameable through one precise mutation: a committed exact-path exemption row silently clears a real dangling citation; only the manual kill rule catches it. All four questions answered with evidence below.

## Evidence

1. Base reproducibility (frozen invocation, read-only, scratch mirror `git init` + fetch of the lane):
   `python3 -B tools/souji-landing-gate.py --root /var/tmp/souji-r27-RevC1Counter/lane --rev e78ac7c4837b81b634db4a927605a751a7f006ba --round 27 --fleet-root /home/vgpnk/Projects/shokunin`
   → `LG-DANGLING-PTR\tcorpus/knowledge/registry\tcorpus/QUALITY.md:143 cites path absent at e78ac7c4837b`, `LG-DANGLING-PTR\tcorpus/lessons/round-24.md:232:S118\tcorpus/QUALITY.md:141 cites path absent at e78ac7c4837b`, `SUMMARY\tfindings=2`. JSON: `checked_ptrs=828 ptr_exempt=4 ptr_fleet=3`. Reproducible.
   Caveat: the run exits rc=2 `COULD-NOT-EVALUATE no .md reports under .ufo/waves/round-27/` because the base tree contains no round-27 `.md` reports (`git ls-tree -r --name-only HEAD | grep -c round-27` → 0; attempt-2 files are uncommitted worktree). The findings token still prints.

2. findings=N semantics: `len(result["findings"])` across ALL classes (LG-PARSE-REG, LG-MISSING-REG, LG-PARSE-CHANGED, LG-FROZEN-PIN, LG-FROZEN-MEASURED, LG-SEAT-UNCARRIED, LG-OPEN-ADMITTED, LG-DANGLING-PTR, LG-DANGLING-PTR-EXEMPT-STALE) — not PTR-only. Evidence:
   - `--round 26` same rev → `findings=20` = 18 `LG-SEAT-UNCARRIED` + the 2 PTR, rc=1.
   - no `--fleet-root` same rev → `findings=5` = 3 more PTR rows (`../.ufo/waves/hyaku/jj-w1/reports/JjAuditSouji.md`, `JjTrialSouji.md`, `.ufo/waves/hyaku/jj-w1/reports/`) that classify as fleet-only when the root is supplied (source lines corpus/README.md:217, corpus/knowledge/jj-colocation-receipts.md:148).
   - `--round 16` same rev → `findings=0` rc=0, because pointer/exemption checks are gated `if round_no >= 18` (line 1030, 1089): the same two true dangling citations go GREEN.
   At base under the exact invocation, N=2 and both findings are PTR rows; N is not intrinsically "PTR count".

3. Exemption loader (lines 876-902): row must be exactly 2 tab fields; first field non-empty, stripped, starts with a POINTER_ROOT, `_safe_pointer_path`, contains no `<` `>` `*`, and unique — otherwise EvalError (exit 2). Matching is exact: `if path in exemptions: continue` (line 959). Stale rows are themselves findings (lines 1106-1114, ID LG-DANGLING-PTR-EXEMPT-STALE).

4. Gaming battery (scratch commits):
   - A: new scanned-source entry `corpus/knowledge/attack-source.md` citing absent `corpus/knowledge/attack-real.md` → `findings=3`.
   - B: commit exemption row `corpus/knowledge/attack-real.md\tattack demo: exact path exemption` → `findings=2`, no warning, no staleness: the REAL break vanished silently. Over-match is real and machine-invisible.
   - C: `corpus/*` row → `COULD-NOT-EVALUATE corpus/pointer-exemptions.tsv:6 malformed exemption row`, exit 2: broad/wildcard vectors are structurally blocked.
   - D: `corpus/README.md` (resolves) row → `LG-DANGLING-PTR-EXEMPT-STALE`, `findings=3`: unused exemptions cannot be parked.
   So the only game vector is the exact-path row; it converts a true defect into a silent pass. The kill rule (over-match fails C1) is purely human-enforced by the tool.

5. Byte pinning: `sha256sum tools/souji-landing-gate.py` (installed) = `02b58f81c8dab4a7c67fdcfc88f1120892719e906c8117b0122aaf6163f785cd` = `git show e78ac7c:tools/souji-landing-gate.py | sha256sum`. The gate has no self-pin (`__file__`/argv0 used only to re-invoke itself in selftests, lines 1590-1636); the executed bytes are whoever sits at `tools/souji-landing-gate.py` in cwd. Data is rev-pinned (`list_tree(root, resolved)`), tool bytes are not.

## Findings
1. [SOUND] findings=2 at e78ac7c reproduces with the exact frozen invocation; the findings are exactly the two internal LG-DANGLING-PTR rows, both from QUALITY.md (143, 141). No other class fires at base.
2. [SOUND] Data is rev-pinned: corpus, exemptions, and wave reports all come from the tree at `--rev`; worktree dirt cannot alter N (mirror run used the committed tree; identical result).
3. [SOUND] Exemption breadth is structurally limited: wildcard/`<>` chars rejected (malformed → exit 2), unused rows flagged stale; you cannot add junk rows.
4. [GAMEABLE] Exact-path over-match: a committed exemption row suppresses a citation regardless of whether the absence is a true defect. Demonstrated: real break `corpus/knowledge/attack-real.md` cleared silently (findings 3→2) with no machine flag. Only the per-round kill rule (ign review of the reason column) catches this; the counter itself cannot.
5. [INVOCATION-SENSITIVE] N is not an intrinsic property of the rev: `--round 16` → 0 (green) at the same rev; dropping `--fleet-root` → 5. Any re-run must use the exact frozen shape; a wrong `--round` (<18) vacuously passes.
6. [GAP] Tool bytes are unpinned: no sha256 check of the executing script exists; an uncommitted edit of tools/souji-landing-gate.py would change N undetected. At base, installed == committed (02b58f81…), so the frozen before-value was computed with the committed bytes.
7. [NOTE] The before-run exits rc=2 (could-not-evaluate) due to no round-27 `.md` reports at base; the findings token prints regardless. The after-run at tip will carry reports, so the after=0 evaluation will be complete.

## Attack log
- MUTATION (gameable): commit an exemption row whose first field equals the exact cited path of a real defect (e.g. `corpus/knowledge/attack-real.md`). The gate clears the finding silently; no staleness, no over-match detection. Kill rule dependency: manual.
- The preregistration kill rule "an exemption that over-matches a real citation break fails C1" is enforced by review, not by the instrument. Recommend (outside scope, report-only): the gate cannot self-verify truthfulness; keep the two-row resolution honest.
- Everything above was run read-only against the lane (scratch mirror under /var/tmp/souji-r27-RevC1Counter, created with `git init` + fetch, all git calls `-C`); no lane file touched, no lane git/index mutation, no signals.
