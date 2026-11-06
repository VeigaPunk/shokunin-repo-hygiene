# S73Reviewer — round-73 diff a789486d..312e8f29 review (souji r73, wave w1)

Scope: falsify the frozen round-73 claims by re-deriving every number from committed bytes; review the
writer diff, mk-counter/counter, prereg-vs-receipts, and selftest case 43/44 falsifiability.
All runs used my scratch under /fast/scratch/hyaku/souji-r73/S73Reviewer/ (removed before yield); no lane
tracked file touched; read-only git only. No tools installed (none needed).

## Verdicts

1. Writer diff (tools/souji-receipt-write.py, stages W): **SOUND** — no defect found.
   - Refusal-before-write ordering: write_receipt order is env checks → rev/command → toplevel →
     `ls-files -v` flag classes (r62/r63) → `_witness_refusal` (filter/ident/wte, r71) → dirty check →
     `pre_truth = _truth_refusal(top)` (writer :612-615) → pre snapshot → run → post `_witness_refusal`
     → post_fl/post_st compare → content-snapshot compare → `post_truth` (:738-740) → instrument
     re-read vs rev bytes (:741-747) → overflow → only then is the receipt composed and mkstemp'd
     (:749+). Every refusal (incl. `refuse()` inside `_truth_refusal` on status/ls-files/hash-object
     failure or unknown object format) happens before any receipt byte exists; case 43 asserts
     `os.path.exists(out)` false after each refusal and passed in the 44/44 rerun.
   - Exception paths fail closed; `hash-object` runs with `-c core.safecrlf=false` so an operator
     `safecrlf=abort` cannot over-refuse honest CRLF trees; the shared `git()` helper (:147) scrubs
     GIT_DIR/GIT_WORK_TREE/GIT_COMMON_DIR/GIT_ATTR_SOURCE and pathspec env, pins fsmonitor/fileMode/
     checkStat/trustctime — operator config cannot skew the re-hash, and it sees the same repo-local
     conversion config `git status` sees.
   - Porcelain -z parsing (`_porcelain_paths` :244): live fixture produced `R  b.txt\0a.txt\0` and the
     parser captured both paths; the parse is order-independent, and a hypothetically missed listed
     path only routes a status-listed path into the re-hash (no false accept; --allow-dirty listed
     paths are covered by the content snapshot).
   - Symlink hashing: direct `blob <len>\0` hash with the algo from `rev-parse --show-object-format`
     (:269), compared to `ls-files -s` oid; sha1 path exercised by selftest cases 29/44 (44/44 pass).
     LOW: the sha256 branch is unreachable through the CLI — write_receipt refuses non-40-hex revs
     (`REV_RE = ^[0-9a-f]{40}$`, :136) before any truth check. Fail-closed, harmless.
   - Performance on the lane: 18987 tracked files (verified `git ls-files | wc -l`); a faithful replica
     of one `_truth_refusal` pass = 0.81 s (status -z + ls-files -s 0.036 s; `hash-object
     --stdin-paths` over 18934 regular files 0.71 s); the writer does 2 passes per receipt write →
     ~1.6 s overhead; 0 mismatches, 0 bad paths → no false refusal on the lane's clean paths.
2. census/round-73/mk-counter.py + generated counter: **SOUND**.
   - Regenerated in scratch from the frozen r72 bytes (sha prefixes 7578447d / cd8490b4 asserted by
     mk-counter itself): output counter sha256 3809ee7d…eaed3 and matrix sha256 f2ced976…f8080 are
     byte-identical to the committed files (COUNTER-IDENTICAL / MATRIX-IDENTICAL) — every rep() landed
     deterministically where intended; spot-verified: `import stat` at :207, INDEX_STAT_CODE :314,
     inrun dispatch :595-599, `_r73_prerun` call after `mutate()` :1034, tree_divergence :1063,
     witness wiring :1398-1414 (pre+post, fail-closed unwitnessed), claim_upheld :1477-1483,
     SUMMARY :1485-1494, classifier :1497-1535, selftest section (10) :1990-2028.
   - D2 docstring correction (counter :51) is accurate to S314 (corpus/SOURCES.md:273: "When the
     .gitattributes file is missing from the work tree, the path in the index is used as a
     fall-back") — the r72 "status reads the worktree file" over-reach is corrected; S316
     (SOURCES.md:275, git-hash-object --no-filters quote) grounds the writer's conversion claim.
   - INDEX_STAT_CODE (:314): `>10I` 40-byte stat block + oid(20) + flags(2) = 62-byte fixed part;
     padding formula yields min 1 NUL / pad to 8 (correct); rewrites only the entry whose name equals
     the target (hit flag, error exit otherwise), preserves oid+flags and all extensions, recomputes
     the sha1 checksum, moves the index mtime 5 s past the entry — it forges the intended entry only.
     LOW: sha1-only (hardcoded hashlib.sha1/62-byte layout, versions 2/3), exits with error on any
     other index shape — fail-closed; all frozen fixtures are sha1, so no impact.
3. Preregistration vs receipts: **ZERO mismatches**. Every frozen value re-derived by rerunning the
   frozen invocations from the lane root:
   - Main arm (--rev b84ff90b): `SUMMARY matrix=80 base_forgeries=15 base_honest=21 base_mismatches=0
     base_unwitnessed=0 new_unwitnessed=0 new_forgeries=0 new_honest=21 class_mismatches=0 new_echo=0
     errors=0 regress=PASS` EXIT=0 == census/round-73/records/c1-after.txt (C1 i).
   - Do-nothing (--rev a789486d): new_forgeries=3 (CASE FX1/FX2/FX3 new=accept, all witnessed)
     base_unwitnessed=0 base_forgeries=15 EXIT=1 == controls/c1-K-a-do-nothing.txt (C1 ii + C2 ii).
   - Blanket refusal: new_honest=0 class_mismatches=59 EXIT=1 == controls/c1-K-b-blanket-refusal.txt;
     forger (--new-tool weak-base 118597e0…): new_forgeries=15 EXIT=1 == controls/c1-K-c-forger.txt
     (C1 iii).
   - Writer selftest rerun: `SELFTEST cases=44 pass=44 fail=0` == records/writer-selftest.txt (C1 iv);
     counter selftest rerun: `SELFTEST cases=52 pass=52 fail=0` == records/counter-selftest.txt
     (C2 iii), including the five new witness checks and three claim/classifier checks.
   - D1..D5 (apply-edit count==1, src sha 3809ee7d… each): `base_unwitnessed=1` and base_witness=no on
     FWr/FWi/FWp/FWs/FC3 respectively == records/c2-after-D1..D5.txt (C2 i; EXIT=1 from
     claim_upheld requiring base_unwitnessed==0 — expected).
   - Before-controls receipts: 5× `matrix=75 base_forgeries=12 base_mismatches=0 … EXIT=0` ==
     prereg "detected 0 of 5".
   - Probes: fx-index-stat.txt — 3 routes `verdict=FORGERY` on BOTH the weak-base and lane-base
     writers; fx-honest.txt — FXh raw_equal=true, FXc raw_equal=false, accept on both writers;
     witness-weak-base.txt — refuse_rows_accepted=12 witnessed=12 unwitnessed=0;
     witness-defang-D1..5 — accepted=1 witnessed=0 unwitnessed=1. All as prereg states.
   - Frozen sha256s verified from committed bytes: lane-base writer b7790001…244d, weak-base writer
     118597e0…e71f, stage-W writer d1ad5c79…f7c39 (worktree == b84ff90b bytes), r72 counter 7578447d…,
     r72 matrix cd8490b4…; matrix = 81 lines / 80 rows / 21 accept; FX rows match prereg verbatim.
   - Slot identity in my reruns: counter bound slot base.py sha 118597e0… (from 8b9345b1) and new.py
     sha d1ad5c79… (== b84ff90b bytes == worktree tool bytes) — same-identity held.
   - Non-defect semantics worth recording: in the Dk SUMMARYs `errors=0` is the judge-error counter;
     the unwitnessed-accept→error rule lives in the battery classifier (classify_outcome /
     outcome_counts) and in claim_upheld (base_unwitnessed==0 → EXIT=1), exactly as the prereg freezes.
4. Selftest cases 43/44 falsifiability: **VERIFIED (case 43 kills; case 44 is a guard by design)**.
   Grafted TRUTH_CLASS + _stat_forge_code + case_43/44 + CASES entries into a scratch copy of the
   lane-base writer (a789486d) and ran its selftest:
   `case FAIL: stat-cache-forgery … AssertionError: pre-run stat forge rc=0` — the base writer ACCEPTED
   the stat-concealed forgery and wrote a receipt; `SELFTEST cases=44 pass=43 fail=1`. Case 44 passed
   there (43/44): it asserts honest trees are accepted, so it cannot fail without the check — its
   discriminating power is against over-refusal in the new writer (stale stat, autocrlf CRLF
   re-staged, symlink, newline filename), which is exactly its role.

## Findings

- HIGH: none.
- MEDIUM: none.
- LOW 1: `_truth_refusal`'s sha256 branch is unreachable via the CLI (REV_RE 40-hex gate at
  tools/souji-receipt-write.py:136 precedes the algo detection at :269); fail-closed, defensive only.
- LOW 2: counter INDEX_STAT_CODE / writer _stat_forge_code are sha1-only index forgers; they exit with
  an error on any other index layout — fail-closed, and all frozen fixtures are sha1 repos.

## Commands rerun (all from /home/vgpnk/Projects/shokunin/souji-shokunin)

- python3 -B census/round-73/c1-counter.py --selftest --root . --matrix census/round-73/c1-matrix.tsv
  --base-rev 8b9345b1… --work <scratch>/st  → 52/52
- git show b84ff90b:tools/souji-receipt-write.py → <scratch>/ws/writer.py;
  python3 -B … --selftest --work <scratch>/ws/work → 44/44
- python3 -B census/round-73/c1-counter.py --root . --matrix census/round-73/c1-matrix.tsv
  --base-rev 8b9345b1… --rev b84ff90b… --tool tools/souji-receipt-write.py --work <scratch>/main
  (and the K-a variant with --rev a789486d…; K-b with printf always-refuse stub; K-c with git-show
  weak-base stub) → SUMMARY/EXIT as listed above
- for D1..D5: python3 -B census/round-73/apply-edit.py --set census/round-73/c2-defang.json --id Dk
  --src census/round-73/c1-counter.py --out <scratch>/dK/counter-Dk.py, then that file as main arm
  with --rev a789486d…
- mk-counter regen in a scratch tree (r72 counter+matrix from 1eac307f) → byte-identical outputs
- lane-base-writer graft run of cases 43/44; lane perf replica; rename-parse and sha256 fixtures.

Scratch /fast/scratch/hyaku/souji-r73/S73Reviewer removed before this report.
