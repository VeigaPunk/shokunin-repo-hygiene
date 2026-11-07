# S76CriticClaims — r76 falsification (C1 gate ignore-source, C2 tally receipt binding)

HEAD eef6f30c; gate 7a8eec51 (=W); writer 70bbf1c2; C1 counter 618e4f9a; C1 pop 937e4a9b; C2 counter e22f634e; C2 pop c46ea8ff;
tally fcaaec1b — all hashes match the prereg/receipts; no number failed to reproduce. Commands (cwd lane; S=/fast/scratch/hyaku/souji-r76/S76CriticClaims):
git show <rev>:tools/souji-pre-report-gate.sh >D/...; git show <rev>:tools/souji-receipt-write.py >D/...; python3 -B census/round-76/c1-evade-counter.py --gate-dir D --work S/w;
python3 -B census/round-76/c2-binding-counter.py --tally <t>; python3 -B tests/fixtures/r36-report-gate.py --gate tools/souji-pre-report-gate.sh --work S/r36;
TMPDIR=S/r27 bash tests/fixtures/r27-pre-report-gate.sh; bash tools/souji-pre-report-gate.sh --lane <lane> --branch HEAD --report S/probe.md --prereg census/round-76/preregistration.txt.

C1 f7 relabel — HOLDS. W refuses f7; a PASS label would force a W mismatch, so FAIL is entailed by the rule; it is pre-registered at F
(prereg:37-38) before W. Not manufactured.
C1 f11/K-c — HOLDS. f11 is the only row separating K-c (reproduced: K-c SUMMARY rows=30 mismatches=1) and mirrors the lane's own .jj
shape; its PASS rests on gitignore(5) parent-exclusion (census/round-75/srcs/gitignore.adoc:84-88), delegated to by S320 (adoc:42).
C1 .gitignore edit — QUALIFIED. Domain trial is non-discriminating: candidate and Base both print check-clean=PASS on the lane (no
round-76 receipt records it). The edit is load-bearing for W: without it .jj/.ruff_cache/.gitignore would decide and W would fail f7.
C1 population — QUALIFIED. Reproduced Base ef3b04e4 SUMMARY rows=30 mismatches=4 errors=0 [f7 f9 f10 f14] EXIT=1; W 18587bd2
mismatches=0 EXIT=0; K-b 4; K-c 1; r36 cases=21 pass=21; r27 cases=4 pass=4. No untracked-rule shape found that W passes (symlinked
tracked .gitignore: git refuses, ELOOP; non-self-ignoring untracked .gitignore: status catches). Gaps: lane's real .jj pattern is /*.
NEW MEDIUM: .gitignore:4-5 unanchored; .jj/ also hides sub/.jj/payload (measured: unanchored base/W check-clean=PASS, anchored
/.jj/ FAIL, no rule FAIL); it declares any nested tool dir, not "the two"; no current path affected (find: root only). Fix: /.jj/, /.ruff_cache/.

C2 axis — QUALIFIED (exit-code agreement, not binding); do-nothing no (r75 tally 5 mismatches), trivial tally YES (0): FALLS.
Reproduced tally cases=10 mismatches=0; K-b 2; h-honest killed=6; b-swap unbound=2; b-exit-disagree unread=1. The real tally binds
(derive() from frozen edit sets, instrument_sha256, --selftest, duplicate digest: c2-kill-tally.py:46-96); the counter compares exit
codes only (c2-binding-counter.py:64-71). cheat-tally-by-filename.py (reads no receipt, ignores ID= labels, matches six basenames)
scores SUMMARY cases=10 mismatches=0 errors=0. MEDIUM. cheat-tally-killed1.py prints h-honest mutants=1 killed=1 and still scores 10/10
("killed=6" observed, not asserted; LOW — the real tally exits 0 only if killed==len(rows)). Smallest fix: one case copying M08 bytes to
c2-after-X09-selftest.txt (real tally: bind=instrument-mismatch verdict=UNBOUND, exit 1, measured; filename cheat accepts); assert killed=6.

S320 — HOLDS: code runs git check-ignore -v -n -z (gate:125) and parses the 4-field NUL record exactly as S320 OUTPUT states (source:81,
-z format:92); host git 2.56.0. Used, not just cited. Universal clauses not counter-enumerated: C1 domain trial (no receipt; I ran PASS);
C1 later-gate amendment (process); C2 killed=6; C2 command= must carry --selftest (no case); C2 EXIT-agreement sampled but filename-separated.
Findings: MEDIUM C2 cheat separability; MEDIUM unanchored .jj/.ruff_cache; LOW killed=6 unasserted; LOW domain trial; LOW lane /* unsampled.
Files: .ufo/waves/round-76/w1/S76CriticClaims.md; .ufo/waves/round-76/w1/S76CriticClaims/cheat-tally-by-filename.py; .../cheat-tally-killed1.py.
Scratch /fast/scratch/hyaku/souji-r76/S76CriticClaims removed.
