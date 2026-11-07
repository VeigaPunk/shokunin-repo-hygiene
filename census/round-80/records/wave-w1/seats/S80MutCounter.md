# S80MutCounter — r80 C1 counter (W1 bd263c3f, sha256 90ed9031…066069f1 = worktree) mutation probe

VERDICT: every frozen C1 number reproduces, but the frozen artefact set kills only 3 of 9 rule mutants — its calibration evidence does not bind the three r80 rules. 2 MEDIUM, 2 LOW. $S=/fast/scratch/hyaku/souji-r80/S80MutCounter.

Re-derived (pristine bytes): harness `--counter $S/mut/base.py --lane <lane> --fleet-root /home/vgpnk/Projects/shokunin --work $S/work/h-base` -> `SUMMARY rows=18 mismatches=0 accepted=0 errors=0` rc=0, fixture F0=6436db6a…; r78 verbatim -> 22/22 + `forged=12 matched=12` rc=0; r77 verbatim -> 35/35 + `forged=7 matched=7` rc=0.
Controls verbatim: K-a r79 counter `mismatches=3 accepted=3` (NF6b/NF8/NF10); K-b 18/0/0 + r78 `resolved=3 refused=19` rc=1; K-c without-regular/capture-root/whole each `mismatches=1` (NF8/NF10/NF6b); r79 harness 9/9. No claim number is falsified.

Mutant panel ($S/mut; one change each; diffs+sha256 in S80MutCounter/mutant-diffs.txt; detectors = r80 harness | r78 | r77):
M01 modes+=120000,160000         green|green|green           killed by NF11b (new)
M02 anyblob (mode test deleted)  green|green|green           killed by NF11b (new)
M03 fleet: -> return True        green|green|green           killed by NF16 (new)
M04 root tuple += "corpus"       RED NF10 got=MOVED rc=1      killed by NF10 (frozen)
M05 root membership -> startswith green|green|green          killed by NF12b (new)
M06 _whole before_ok = True      green|green|green           killed by NF13/NF13b (new)
M07 _whole after_ok = True       RED NF6b got=QUARANTINED    killed by NF6b (frozen), NF15b (new)
M08 punct allowance widened      green|green|green           killed by NF15b (new)
M09 token check dropped          RED NF6c got=QUARANTINED    killed by NF6c (frozen), NF13 (new)
Kill ratio: frozen artefacts 3/9; frozen + new rows 9/9.

NF11+ rows ($S/probe_rows{,2,3,4}.py; frozen build_fixture F0..R3 + R4=5da04747, R5=d3ae1e7f, R6=4e009114):
NF11b R5 D2.txt mode 120000, P19 TOKEN D1..D5 -> REFUSED "range member is not a regular file: …c2-after-D2.txt"
NF11c R6 D4 gitlink (160000 commit)           -> REFUSED same message (M01 refuses too)
NF12  R4 P04 MOVED census/round-32/decoy/SwarmExecutor08.md (byte-equal decoy) -> got=MOVED [ACCEPTED]
NF12b R4 P04 MOVED census-archive/round-32/decoy/… -> REFUSED (base) / MOVED (M05)
NF13  R4 L06 QUARANTINED …/uri-stub, token only inside https://….git -> REFUSED
NF13b R4 L06 …/backtick-stub, token as `sub/tests/…/.git note`     -> REFUSED
NF14  R4 L06 …/bracket-stub, text "(…/bracket-stub)"               -> got=QUARANTINED [ACCEPTED]
NF15  R4 L06 …/dot-stub, text "…/dot-stub. confirmed"              -> got=QUARANTINED [ACCEPTED, stated]
NF15b R5 L06 …/bak-stub, text "…/bak-stub.bak"                     -> REFUSED
NF16  R5 fleet:D1..D5, D2 a symlink under a staged fleet root      -> REFUSED (M03 accepts)

Findings
MEDIUM — the calibration set cannot see the r80 NF8 mode test (counter:219): M02 deletes `mode in (100644,100755)` and still scores 18/0/0, 22/22+12/12, 35/35+7/7, because no frozen row holds a symlink member (NF8's D3 is a directory, already refused by `typ == blob`). M01 survives likewise; the 160000 arm is also dead (a gitlink's type is `commit`). Coverage gap, not behaviour: pristine refuses NF11b/NF11c.
MEDIUM — the NF10 capture-root rule (counter:312) binds nothing inside census/: a byte-equal decoy at census/round-32/decoy/ is ACCEPTED (NF12 got=MOVED) while the real capture is census/round-32/waves/a2w1/. The prereg's "or census/round-<N>" sanctions this = stated limit, but the limit was unmeasured and is wide.
LOW — counter:200-201 accepts any non-path byte after a path: a declaration quoting "(…/bracket-stub)" resolves (NF14), where the prereg allows only one trailing `.` `,` `;` `:`.
LOW — no frozen row exercises the before-check (counter:198): in NF6b both paths are preceded by a backtick, so M06 survives all three detectors and dies only to NF13/NF13b; M08 survives NF6b (the token's after byte is "i") and dies only to NF15b.

Files written: .ufo/waves/round-80/w1/S80MutCounter/{summary.txt, mutant-diffs.txt, probe2.txt, probe3.txt, probe4.txt, controls.txt}; this report .ufo/waves/round-80/w1/S80MutCounter.md. Scratch removed; no lane/fleet file edited by me; nothing left running.
Coordination: `git status` shows tools/souji-quarantine.sh dirty (a sibling C2 seat's in-flight r80 repair, mtime 05:01) — not mine; untouched.
