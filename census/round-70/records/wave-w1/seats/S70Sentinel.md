# S70Sentinel — round-70 security / fail-closed falsification

VERDICT: C1 reproduced byte for byte; C2 reproduced byte for byte. Both frozen claims stand.
All seven findings are scope or containment gaps in the instruments' own inputs; none changes a
frozen predicate, and F1/F2 are pre-existing writer holes the pathspec scrub does not touch (and
does not declare). Scratch: /fast/scratch/hyaku/souji-r70/S70Sentinel (removed).

## Claims re-derived (from the lane root /home/vgpnk/Projects/shokunin/souji-shokunin)
1. C1 PASS — `python3 -B census/round-70/c1-counter.py --root <lane> --matrix census/round-70/c1-matrix.tsv
   --base-rev e063a2fc… --rev 93a051b2… --tool tools/souji-receipt-write.py --work <S>/c1` printed
   `SUMMARY matrix=59 base_forgeries=4 base_honest=13 new_forgeries=0 new_honest=15 class_mismatches=0
   new_echo=0 errors=0 regress=PASS` / `EXIT=0` = census/round-70/records/c1-after.txt.
2. C2 PASS — frozen harness invocation printed `SUMMARY label=c2-after-r70 positive_selftest=PASS
   positive_battery=PASS mutants=4 killed=4 survived=0 tamper=detected score=0` / `EXIT=0` =
   census/round-70/records/c2-after.txt.
3. Writer selftest `--selftest --work <S>/wst` (TMPDIR=<S>/wst) → `SELFTEST cases=38 pass=38 fail=0`,
   `EXIT=0`, case 38 ok = records/writer-selftest.txt. Counter selftest 29/29, `EXIT=0` = records/counter-selftest.txt.
4. S304's located quote reproduces verbatim with the capture's sha256 534c674f…d9f1 and is 20 words;
   S305's rejection reason reproduces (ENVIRONMENT VARIABLES entry: "literally, rather than as glob patterns",
   never "magic"). Provenance of the text stands (offset field: F7).
5. Before-arms also reproduced: `--label c2-before-r69 --counter census/round-69/c1-counter.py --matrix
   census/round-69/c1-matrix.tsv --base-rev 36390879…` → `SUMMARY label=c2-before-r69 … killed=0 survived=4
   tamper=undetected score=5` / `EXIT=1` (claim: score=5, EXIT=1); r70 counter `--new-tool <base writer bytes>` →
   `SUMMARY matrix=59 base_forgeries=4 base_honest=13 new_forgeries=4 new_honest=13 class_mismatches=5 new_echo=0
   errors=0 regress=PASS` / `EXIT=1` (claim: 4/13/5, EXIT=1).

## Assigned probes that found nothing
- GIT_LITERAL_PATHSPECS=true|yes|on|0 on a skip-worktree fixture: candidate refuses rc=2 RECEIPT-INDEX-FLAG-CONCEALED
  for every spelling (base writer rc=0 and a written receipt under =1 = the documented forgery).
- GIT_GLOB_PATHSPECS=1 + GIT_NOGLOB_PATHSPECS=1: git dies (`fatal: global 'glob' and 'noglob' pathspec settings are
  incompatible`, rc=128) and the base writer refuses (`cannot read index flags of …`), so no forge or over-refusal is
  reachable; the candidate scrubs both and reaches the unset verdict (skip-worktree refused, honest tree accepted).
- Only one writer read is pathspec-magic-bearing (`ls-files -v -z ':(top)'`, tools/souji-receipt-write.py:393, 506); the
  `ls-tree … -- <rel>` read post-filters on exact path equality, so GLOB/ICASE over-matching cannot forge.
- verify_members: a sums file listing `../x.py` while the manifest names D01 → `member D01.py is not listed`; duplicate
  lines with both ` `/`*` markers → `SHA256SUMS line 2 lists D01.py twice`; CRLF line ends verify (EXIT=0) and CRLF with
  a 64-hex wrong digest is refused. No CRLF defect, no sums-name traversal by itself.

## Findings
F1 HIGH — an attribute-driven clean filter forges the clean-tree witness (the receipt's whole subject).
  (a) one env var, no worktree .gitattributes: repo-local `filter.t.clean=sed s/v2/v1/` plus `GIT_ATTR_SOURCE=<commit
      that adds "tracked.txt filter=t">`; `git status --porcelain` → empty while tracked.txt=v2 vs HEAD=v1; the writer
      printed `RECORD … rc=0` and wrote the receipt (tools/souji-receipt-write.py:405,507 read that witness).
      The writer neither scrubs nor refuses GIT_ATTR_SOURCE (:108-120) although the counter's clean_env scrubs it
      (census/round-70/c1-counter.py:394) — the instrument and the tool under test disagree on the same route.
  (b) no env var: a committed .gitattributes plus the same local filter config; an IN-RUN edit by the wrapped command
      (the case-15 class) is accepted rc=0 with worktree=v2, HEAD=v1, status empty; the same run without the filter
      refuses `RECEIPT-STATE-CHANGED-DURING-RUN` rc=2.
  Pre-existing; the named limits (:60) name only ignore routes. Remediation: refuse when the rev or worktree assigns a
  `filter` attribute (or the repo defines filter.*.clean), or pin attribute resolution before trusting status.
F2 MEDIUM — repo-local `core.fileMode=false` blinds the same witness: in-run `chmod 0755` accepted rc=0 (mode 755,
  status empty); the identical run without the config refuses RECEIPT-STATE-CHANGED-DURING-RUN. The matrix's
  global/system/git-dir fileMode rows only inject env config, which the writer pins off; `.git/config` is uncovered.
F3 MEDIUM — verify_members trusts the manifest name and the SHA256SUMS that travels with it (no name validation:
  c1-counter.py:1096-1122, 1139-1172, 1524). Manifest `../escaped` + dir-local sums listing `../escaped.py` (digest of
  the outside file) → the counter executed it (marker written), `MUTANT ../escaped … EXIT=0`; a symlinked `D01.py ->
  ../escaped.py` is likewise verified and the out-of-dir bytes run. The sums sha256 is only echoed, never anchored.
F4 MEDIUM — the same unvalidated name escapes the counter's work dir: `--work <S>/vm/w9`, name `../../pwn` → fixtures
  written to `<S>/vm/pwn` (outside --work), EXIT=0. c1-counter.py:1442-1452 validates only --work; :1525-1526 joins
  the raw name. The docstring's "writes only under --work / lane never written" is unenforced for battery inputs.
F5 MEDIUM — c2-harness.py:106-108 joins `--label` into `work/label` and `shutil.rmtree`s it unvalidated:
  `--label ../hv/victim` deleted hv/victim/precious.txt and repurposed that directory as the run base, while the run
  still printed a normal SUMMARY and EXIT=0. Only --base-rev is validated; --work is realpath-checked, --label is not.
F6 LOW — the harness leaves its base: 387 MB in 14 entries under --work after EXIT=0, no cleanup in main(); nothing
  outside --work was created by the harness itself (the counter's out-of-work writes are F4).
F7 LOW — S304/S305 text offsets do not reproduce under a plain tag-strip of the capture (claimed 12133 / 47046;
  observed 48706 / 84756 for the same strings). Offsets are extractor-dependent, so a reviewer cannot recheck them
  from srcs/ alone; the quoted text itself does reproduce.

Files written: this file plus S70Sentinel/ (c1.out, c1dn.out, c2.out, c2b.out, e1-e4.out,
f1a-attr-source.log, f1b-inrun-filter.log, f2-filemode.log). Scratch removed. No tools installed.
