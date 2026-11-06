# S69CriticClaims — post-freeze falsification of round-69 C1, C2, C3

Freeze 1412037c. Lane tip 893b8ef4 (writer blob b811ee2a…, verified). Base writer 3639087 (sha256 a8c47d36…). Read-only except scratch `/fast/scratch/hyaku/souji-r69/S69CriticClaims`. No tool installs (none needed).
Receipts copied to `.ufo/waves/round-69/w1/S69CriticClaims-receipts/` (cand, bat, dn, self, cand-ambient, dn-ambient, lit-literal, lit-d29, mut-gen, fx-lit, per-variable ambient runs `attr disc shallow flush lang execp quar ceil nolazy`).

## Verdicts
- C1 (battery outcome split): **SURVIVES** — reproduced; every forgery is a real receipt over a refused candidate state; no mis-class under the frozen precedence. Notes: manifest unhashed in receipt (LOW); W5 base-side unmeasured (LOW).
- C1 do-nothing control: **SURVIVES** — base writer run is red (EXIT=1, new_forgeries=3, class_mismatches=4), byte-identical to controls/c1-do-nothing.txt.
- C2 (ambient tuple): **BROKEN** — frozen tuple passes (0-line diff), but the tuple omits `GIT_LITERAL_PATHSPECS`, which changes the candidate's verdict and makes the writer forge receipts (HIGH).
- C3 (coverage table): **SURVIVES on count, qualified** — 12 mutant + 2 limit reproduced; covered=12 includes 4 non-kill refutations (kill-coverage 8/14); D06 kill mostly carried by other protections' rows (MEDIUM); D29 limit false outside default env (MEDIUM).

## Commands run (cwd lane, -B)
1. `python3 -B census/round-69/c1-counter.py --root $L --matrix census/round-69/c1-matrix.tsv --base-rev 3639087… --rev 893b8ef4… --tool tools/souji-receipt-write.py --work $S/cand` → SUMMARY matrix=47 base_forgeries=3 base_honest=11 new_forgeries=0 new_honest=11 class_mismatches=0 new_echo=0 errors=0 regress=PASS, EXIT=0 (matches P1).
2. Same with `--work $S/bat --battery-manifest census/round-69/battery-manifest.tsv --battery-dir census/round-69/battery` → `BATTERY mutants=26 kills=18 label_only=5 over_refusal=2 echo_violation=1 survived=0 error=0`, EXIT=0.
3. Same with `--new-tool $S/base-writer.py` (no --rev/--tool) → SUMMARY … new_forgeries=3 … class_mismatches=4, EXIT=1.
4. `--selftest --work $S/self` → `SELFTEST cases=16 pass=16 fail=0`, EXIT=0.
5. Ambient frozen tuple: `env -i PATH HOME=<.gitconfig showUntrackedFiles=no> XDG_CONFIG_HOME=<git/config mirror> GIT_TRACE=1 GIT_TRACE2_EVENT=… GIT_TRACE2_PERF=…` counter candidate and do-nothing runs → `diff` of ^(CASE|SUMMARY|REGRESS|EXIT=) lines vs clean = 0 (candidate and do-nothing); also 0 vs L1 records/c2-clean.txt and c2-ambient.txt and controls/c2-do-nothing-ambient.txt.
6. Member bytes: `python3 -B census/round-69/mutate-writer.py $S/cand-writer.py $S/mut` → 28 mutants; each sha256 equals battery/<m>.py; `sha256sum -c battery/SHA256SUMS` → 28×OK.
7. Standalone writer probe (fixture from `mktemp -d -p $S`, toplevel asserted equal to fixture dir before commit, skip-worktree on tools/counter.py with forged bytes): `env -i PATH python3 -B cand-writer.py --root D --rev R --instrument tools/instr.sh --out … --allow-outside -- /bin/echo hi` → `refused: RECEIPT-INDEX-FLAG-CONCEALED … rc=2`; with `GIT_LITERAL_PATHSPECS=1` → `RECORD … rc=0`, receipt written, `EXIT=0`. Same row with mutant D29 refuses in both envs.
8. Counter candidate under `env -i PATH GIT_LITERAL_PATHSPECS=1` (fresh work) → SUMMARY … new_forgeries=5 class_mismatches=6, EXIT=1.
9. Ambient-variable sweep (candidate counter, one variable each): GIT_ATTR_NOSYSTEM, GIT_DISCOVERY_ACROSS_FILESYSTEM, GIT_SHALLOW_FILE, GIT_FLUSH, LANG/LANGUAGE/LC_ALL=de, GIT_EXEC_PATH, GIT_CEILING_DIRECTORIES, GIT_NO_LAZY_FETCH → all SUMMARY identical to clean, EXIT=0. GIT_QUARANTINE_PATH=/nonexistent → errors=47 regress=FAIL EXIT=1 (fail-closed, verdict-changing).
10. `env -i … GIT_LITERAL_PATHSPECS=1 counter --battery-manifest battery-limits.tsv --only D29` → MUTANT D29 outcome=over-refusal honest=11 label=2 regress=FAIL, EXIT=1.
11. HOME/XDG pin check: `git config --get status.showuntrackedfiles` with hostile HOME → `no`; with GIT_CONFIG_GLOBAL=/dev/null → unset (git 2.56.0).
12. Read-only: `git show`, `git rev-parse`, `git diff --stat 1412037c HEAD -- census/round-69 tools` (only the 3 after-arm receipts added post-freeze; tools unchanged), `grep`, `awk` over records/declared-coverage.tsv and the r68 inventory.

## C1 — battery outcome split
- Reproduced: my bat.txt equals records/c1-after-battery.txt on every CASE/MUTANT/BATTERY/EXIT line (diff 0); full-file diff is only my appended `SHELL_EXIT=0`. Counts: forgery 18, label-only 5, over-refusal 2, echo 1, W4 `base=accept` 26.
- Forgery reality (decisive lines): all 26 forgery rows are `new=accept` with `new_rc=0`, empty `new_stderr`, and a `receipt.txt` on disk (e.g. `work/battery/D01/D/new/out/receipt.txt`); the candidate refuses the same row (`CASE … new=refuse new_findings=RECEIPT-…`) in cand.txt. Examples: K8 W5 (`candidate: RECEIPT-ENV-COMMONDIR-MISMATCH`), D01 G1 (`candidate: RECEIPT-GITLINK-CONCEALED`), D10 SY3 (`candidate: RECEIPT-STATE-CHANGED-DURING-RUN`).
- Label-only and over-refusal are classes, not forgeries: K1 E1,E2 refused `lane worktree is dirty` (class ≠ CONFIG-SET; the dirty check still blocks); M-CD-ROOTREL W4 refused `RECEIPT-ENV-COMMONDIR-MISMATCH`; D02/D03/D04 U1/G1/A9 refused with a different class; M-CD-NCABS W6 and M-CD-NCRAW W3/W6 honest refusals (over-refusal). No label-only mutant contains a forgery. Precedence (forgery > echo > over-refusal > label) applied as frozen: M-CD-CALL and M-CD-SCRUB have label rows but are forgery kills.
- Member integrity: 28 members regenerate byte-identically from the candidate writer; SHA256SUMS all OK.
- W4 r68→r69 mutant labels unchanged: new verdict for M-CD-SCRUB/M-CD-ROOTREL/M-CD-NCRAW W4 is `refuse` with non-dirty class (matches r68 `CAND/M-*.txt` new=refuse new_findings=-). Base W4 moved refuse→accept (fixture repair, as stated).
- Do-nothing: base writer → EXIT=1; SUMMARY identical to controls/c1-do-nothing.txt. The r68 counter has no battery arm: `grep -rc '^MUTANT \|^BATTERY '` over census/round-68/records/c1-after/ = 0 (verified).

## C2 — ambient tuple
- Frozen tuple: candidate clean vs ambient diff = 0; do-nothing ambient matches controls; selftest 16/16; EXIT=0. Discriminating power is limited: the counter's `clean_env` drops HOME, XDG_CONFIG_HOME and GIT_TRACE* outright, and the writer and counter both pin GIT_CONFIG_GLOBAL (hostile HOME config is honoured without the pin, unset with it), so the tuple passes by construction for those names.
- Omitted variable that changes a verdict: **GIT_LITERAL_PATHSPECS**. The writer's `git(top,"ls-files","-v","-z",":(top)")` (and the `-s` and post-run reads) become literal under it, so the flag listing is empty and every flag-class row is accepted: counter candidate new_forgeries 0→5 (D, T1, N4, G1, A9), EXIT 0→1, 16 lines differ from clean; standalone writer writes a receipt over the skip-worktree row (rc=0). Base also forges under it (base_forgeries 3→8), so it predates r69. The writer refuses other caller env routes by presence (INDEX-ENV, CONFIG-SET, REDIRECT-SET, COMMONDIR) and has zero PATHSPECS handling.
- Other omitted variable: GIT_QUARANTINE_PATH=/nonexistent → fail-closed errors (EXIT 0→1). Eight other variables tested: no verdict change.

## C3 — coverage table
- Reproduced: `awk -F'\t' 'NR>1{print $5}' declared-coverage.tsv | sort | uniq -c` → 12 mutant, 2 limit; observed-outcome column matches my battery for all 12 (D01 f, D02/D03/D04 l, D05/D06/D07/D08/D10/D19/D21 f, D30 e). Population: r68 inventory has exactly these 14 `none` rows (awk → `14 none`).
- Count honesty: covered=12 = 8 forgery kills + 3 label-only (D02 D03 D04) + 1 echo (D30). Under C1's own rule only the 8 are declared-protection kills. Headline "covered=12" is honest only under the frozen refutation wording. (MEDIUM)
- Kill attribution per row (from detail lines):
  - D01 → D, N4 (own gate), G1, A9 (rows of D03/D04, which sit behind the same gate). OK, LOW.
  - D05 → T1 (own). D07 → V1 (own). D08 → MOD, MOD2, MOD3 (own). D10 → SY3 (own). D19 → F1 (own). D21 → W7 (own). D30 → N3, P13 echo (own). D02/D03/D04 → U1/G1/A9 label (own class rows).
  - **D06 → N1 (own), MOD, MOD2, MOD3, SY2, SY3**: 5 of 6 forgery rows are mode and symlink rows, i.e., the D08/D10 protections inside the same snapshot. The content-only protection has one isolating row (N1). (MEDIUM)
- Limits: **D29 limit is false outside the default env.** The `:(top)` pathspec is observable under GIT_LITERAL_PATHSPECS=1: candidate forges 5 flag rows, the D29 mutant refuses them but over-refuses 11 honest rows (regress=FAIL). The stated reason (cwd already toplevel) holds for cwd only. (MEDIUM)
- D18 limit not re-probed (no verdict-affecting observation found by reasoning: writer reads only flags/status, never index bytes). Unfalsified, not verified.
- Do-nothing C3 control: controls/c3-do-nothing.txt is a hand-typed ID list, not awk output (LOW); the awk over the r68 inventory does reproduce `14 none` with the same 14 IDs.

## Kill-rule check
- No frozen number is satisfiable by labels alone: a forgery needs `new=accept` with rc 0 and a receipt on disk (judge()).
- Gaps: (a) battery EXIT ignores per-mutant `regress` (rc = all_match ∧ survived=0 ∧ error=0); a forgery-kill with regress=FAIL still counts (LOW; none observed in the 26). (b) `class_ok` is a substring test (`klass in stderr`); a message containing the token passes as the right class (LOW; not exploited by any of the 26). (c) BATTERY survived=0 excludes D18/D29 by population, by design (noted).
- Manifest is pinned only by its freeze commit: the receipt records the manifest path, not its sha; EXIT=0 holds for any manifest whose expectations match observation. Post-freeze diff shows the manifest unchanged (LOW).

## Findings
- HIGH — Writer (tools/souji-receipt-write.py at 893b8ef4; also base 3639087): an ambient GIT_LITERAL_PATHSPECS=1 makes the `:(top)` flag reads empty; a skip-worktree/gitlink/absent/unmerged row is written as a receipt (rc=0). Fix direction: refuse GIT_*PATHSPECS presence like the other caller routes, or scrub it in git() and add it to the counter's tuple and a matrix row.
- MEDIUM — C2 tuple incomplete (GIT_LITERAL_PATHSPECS; GIT_QUARANTINE_PATH fail-closed).
- MEDIUM — C3 `covered=12` counts 4 non-kill refutations; declared kills 8/14.
- MEDIUM — C3 D06 kill carried by D08/D10 rows (5 of 6).
- MEDIUM — C3 D29 limit false under GIT_LITERAL_PATHSPECS=1.
- LOW — C1 manifest/member pinning in receipt; W5 base refusal is an unrelated rev-check failure (`not a git repository`), same defect class as Q132; battery EXIT ignores regress; substring class match; C3 do-nothing control is a list.

Probe scope note: lane and fleet tracked files unchanged; no git mutation; scratch fixtures only.
