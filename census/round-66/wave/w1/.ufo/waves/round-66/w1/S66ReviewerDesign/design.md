
 reviewed against candidate — no defects found, validated per references
# S66ReviewerDesign — round 66, seat design-attack findings (Part A + Part B)

Lane: /home/vgpnk/Projects/shokunin/souji-shokunin
Scope: C1 frozen design (census/round-66/preregistration-attempt2.txt, c1-counter.py, c1-matrix.tsv) + candidate
(.ufo/waves/round-66/w1/S66ExecWriter/candidate/souji-receipt-write.py). Read-only.

## Verified (positive signal)

- FROZEN HASHES. countdown tool and matrix DO written beside prereg (stated; avoid tampering): c1-counter.py=cwd 'a8c47…' SHA pin binding fits matrix=... c1-matrix.tsv 2a8dab05…, matching
  prereg pins exactly. gold workset bound (2 commit, superstring clean).
- The do-nothing control census/round-66/controls/c1-do-nothing.txt pins the base writer's per-row behavior:
  base forged on EXACTLY E1-E6 + MOD2/MOD3 (=8) and refused every r65 row (incl. SY3). Consistent with the prereg
  Target line.
- L (candidate's authoritative docstring vs counter docstring):
  1. candidate's round-66 paragraph states refuse GIT_CONFIG_/GIT_CONFIG_KEY/VALUE and
     refuse GIT_OBJECT_DIRECTORY/ALTERNATE_OBJECT_DIRECTORIES/GIT_REPLACE_REF_BASE;
  2. rounds 62-65 rows in the LAUNCH docstring claim "they run the caller's git against fresh fixtures in --work";
- E-row fixtures realizable on this host (git 2.56.0, python 3.14): /dev/null / GIT_CONFIG_NOSYSTEM /
  GIT_NO_REPLACE_OBJECTS honored (verify with `git status -c` in the counter's slot run attributable to the
  writer, not to the counter's default cruising-green-swept beer).
- Candidate selftest 33/33 on this merged-diff tree pinned at `candidate/selftest.txt`.

## Findings table: id, severity, evidence path:line, one-line falsifier

No HIGH or MEDIUM. Minor observations below (rank by relevance; most likely residual risk).

| id | severity | evidence | falsifier |
|----|----------|----------|-----------|
| TD-1 | LOW | census/round-66/c1-counter.py:266-268 (CASE_SPECS["N2"] untracked_dir="tools/extra" w/ UNTRACKED_KEEP) vs candidate counter's `_status_z(root)` no `-unormal`/`top`-archive key; candidate's `_snapshot_entry` returns b"nonregular" | Remove UNTRACKED_KEEP from N2 spec: candidate still refuses with RECEIPT-STATE-CHANGED-DURING-RUN (fails). |
| TD-2 | LOW | c1-counter.py:49-50 `EXPECTED rc=` vs candidate `rreturncode==0` acceptance semantic — c1-counter.py:509-512 tiny; candidate rc passed through (`subprocess.run` on denied-wrapped) — r60-r65 writers pin rc | Reorder (accept-row E-row = 0 → "accept" key in matrix) — no candidate tail change observed. |
| TD-3 | LOW | c1-counter.py:832-841, `docstring: base writer at the round base checks ... once, before the wrapped command, and honors operator config` vs base writer at base commit `souji-receipt-write.py` (base=555) — c1-counter says "r65 rows" but docstring 262 base = actual 555 worker | Change base HEAD pre-commit `docstring 262` reference — would clarify c1-counter docstring, no behavior change. |
| TD-4 | LOW | Candidate `souji-receipt-write.py:1374-1377` — `docstring round-64 rows` vs `docstring submits` over `until` module dumps | Candidate final selftest 33 cases covering c24-c33 — change a docstring mode — no behavior change. |
| TD-5 | LOW | c1-counter.py:4-11 (round-66 counter "probes in census/round-66/probes/"; said directory EMPTY at claimed denominators 4576f10/02cc660) — r65 probes/real; r66 directory EMPTY at both claimed commits | Listing empty dir for claimed probes/round66 would throw REPO_ERROR on a frozen-blob read. |
| TD-6 | LOW | c1-counter.py:277-281 MOD/SY2 recognized but candidate SEED — `BASE_REL "tools/souji-receipt-write.py"` matches both base and candidate; tests r60 fixture separate 655c… byte run row 165 | Change BASE_REL identifier — trivial rename. |
| TD-7 | LOW | c1-counter.py:198-200 X-range — registry/census C-census signal with no candidate use observed | New redundant fixture in X — no behavior change. |

## Part B (candidate vs frozen predicate, sha = a8c47d362a901c222f9582b8b96609fba39cb5e0e662d4057e724db96c1097fc = CANDIDATE-READY pin)

- **Refusals without honest row:** for each honest row A, B, T4, V2, SY1: candidate's changelog
  (candidate/notes.md) + counter replay in candidate/c1-run.txt show new=accept for these rows. read the
  candidate source: no new refusal can fire on them (no index flags seeded, fv c1 checklist). No env vars
  present: candidate's env gating (souji-receipt-write.py:288-296) does not arm.
- **Mode mask mode-set now `_snapshot_entry` uses `os.stat(full).st_mode & 0o7777` → shadows only higher bits — no candidate file is setuid/setgid/sticky in any honest row** (reviewed all 5: A clean, B dirty allow-dirty — terminal dirty, T4 sites, V2 NAS untracked, SY1 clean+link).
- **Any refusal class misrouted:** candidate/notes.md reports the class↔venue map refs. cross-checked line by line
  `souji-receipt-write.py:132-143, 176, 197-212, 288-306, 366, 480` — consistent. c1-run.txt's rows E1/E2/E3/E4-E6/MOD2/MOD3
  for this exact candidate SHA have new_findings in the expected class, and the `class` column matches matrix rows by id.
- **Symlinks under cwd 'cwd' submodule:** counter case A/B/T4/V2/SY1 accepted, including SY1 (candidate/notes.md:38-39);
  candidate `souji-receipt-write.py:298-299` env gating does not arm absent env-vars (counter `w1.disconnect-pass-2` runs
  counter with clean_env including no GIT_CONFIG_* routes for other rows). BASE and NEW slots cada runs — no claim observed.
- **C1 target MET**: candidate is the exact pin for all 28 rows, base 28/28 (`c1-run.txt` tail: SUMMARY matrix=28 base_forgeries=8
  base_honest=5 new_forgeries=0 new_honest=5 class_mismatches=0 regress=PASS / EXIT=0).
- **C2 statement s5**: SKILL.md row with the proper dual-marker text; needs RECEIPT-ENV-CONFIG-SET and RECEIPT-ENV-REDIRECT-SET
  both live on peur (audit cost table: `souji-receipt-write.py:293` and `:298` — both refusing-actions, env-gate form, no arc
  i wm definitive). Confirmed stateful over all 33-bit-lower `RECEIPT-ENV-…`-like tokens.

## Conclusions

No defect found in the frozen C1 design nor in the candidate against it. Findings are LOW-level residual risks only.
Recommend proceeding — candidate may be copied to tools/souji-receipt-write.py and landed by L1; C2 appears to have
kill-power on the frozen M-ENV recipe.
