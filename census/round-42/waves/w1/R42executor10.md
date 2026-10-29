# R42executor10 — C3 candidate fixture (executor)

Candidate: `.ufo/waves/round-42/w1/R42executor10/r42-drift-conditions.py`
sha256 `03392c7d75daaec14f7ac03f8074dd489d8ac7c7efe1d17eb340d13c7f353f45`, 8741 bytes, 13 cases.
The fixture never reads the tool source, bytes, digests, labels or the counter; each case builds a scenario under `--work` and runs `python3 -B <tool>`. It refuses uid 0 (rc 2, no traceback).

## Command
`bash census/round-42/score-candidate.sh c3 /fast/scratch/hyaku/souji-r42/R42executor10 tests/fixtures/r42-drift-conditions.py=<candidate>`  
Exit 0; counter wall time 174 s (host heavily loaded). Receipt: `.ufo/waves/round-42/w1/R42executor10/score-c3.txt`.

SUMMARY (verbatim):
`SUMMARY mutants=13 killed=13 survived=0 pristine=ok prior=8/8 old_killed=0 equiv=6 equiv_killed=0 anchors=ok cases=13 tool_sha=b2a603cf4247`

All 13 `MUTANT <id> candidate=killed prior=-`; all 6 `EQUIV <id> candidate=survived prior=-` (B3 B4 E5 E7 E9 H4). Full lines in score-c3.txt.

## Mutant -> case map (measured)
The counter prints only which prior fixtures kill (none). The per-case map is from my own scratch harness (applies each counter MUTANTS/EQUIV row to a copy of the tool, runs the fixture; receipt `mutant-case-map.txt`; it is a seat measurement, not the counter's):
- B1 fifo-record-is-refused-not-blocked (FIFO record, RECORD-MALFORMED rc 2 within 25 s)
- E2 root-sibling-prefix-is-outside (row `../root2`, RECORD-OUTSIDE-ROOT)
- E4 gitdir-sibling-prefix-is-outside (gitdir in `rootX`, RECORD-OUTSIDE-ROOT)
- G2 timeout-of-one-is-accepted (+ list-timeout-is-reported-unreachable, which also passes `--timeout 1`)
- G3 default-timeout-outlasts-a-blocked-git (FIFO HEAD, no --timeout: UNREACHABLE:list-timeout and elapsed >= 5 s; default 20 s vs 1 s is 20x)
- G4 list-timeout-is-reported-unreachable (+ default-timeout case)
- G5 list-nonzero-rc-is-reported-unreachable (empty `.git` dir)
- H1 root-option-is-required; H2 record-option-is-required (rc 2 + "required")
- I1 symlinked-child-is-not-discovered (UNRECORDED u2 reported, lnk not)
- J9 two-digit-regs-are-read-whole (`regs=10` -> `record=10 live=1`)
- M1 longer-old-json-is-truncated-on-write (5000-byte old file must become valid JSON)
- D4 invalid-utf8-in-record-becomes-replacement-char (row name `a\xffb`: stdout holds `a\xef\xbf\xbdb`, no literal `\xff`; --json repo parses to `a\ufffdb`)
- B3 B4 E5 E7 E9 H4: no case fails (fail set empty, rc 0).
Pristine in that harness: `SUMMARY cases=13 pass=13 fail=0`, rc 0, 43.4 s wall under load (about 25 s of it is the 20 s default-timeout wait); every mutant run <= 68 s.

## Risks
- G3 case relies on a 5 s lower bound only (no upper wall bound); a host stall can only lengthen, never fail, it.
- B1 case on the mutant waits out its 25 s timeout (subprocess killed by subprocess.run).
- Scratch /fast/scratch/hyaku/souji-r42/R42executor10 removed after report copy.

Verdict: target met (13/13 killed, 6/6 equivalents survive, pristine ok).
