# SwarmCritic12 — round 31, wave 2 — C2 counter attack (SHIFT / A3 / A5) and the r26=495 judgment

## Status
STATUS: PASS — four cheat gates built and scored in scratch; three meet the frozen C2 v3 target with no tokenizer work in the measured path (two of them with the committed real fixture), one meets it with no false-positive tokenizer at all. The landed C2 reading itself is re-derived green at both the landing commit and the tip; the defect is leg discrimination, not the L1's arithmetic.

## Evidence
Lane base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`; C2 landed `8024b540b04d677d47cf51a0d1132ec8705ef14a`; tip `2c16d018e40db7c23420a2c3bb546b52957bcc25`. Scratch clone `/fast/scratch/hyaku/souji-r31/w2-AttackC2Amended/c` (`--no-local`, origin removed, toplevel verified). All counters run serially from the live lane script with `python3 -B`; lane touched by `git log/show/ls-tree/rev-parse` only.

Honest re-derivation of the landed claim under v3 (one random draw each):
- `counter-v3 --root $D/c --rev 8024b540... --base 9f17a1ef... --fleet-root /home/vgpnk/Projects/shokunin` → exit 0, `SUMMARY fp=0 real=2 cne=0 r26=495 fixture=ok redarm=ok regress=same shift=ok`.
- same command with `--rev 2c16d018...` → exit 0, identical SUMMARY. The L1's landed reading is not refuted.

Attack B (SHIFT only), scratch rev `d3acc63610aea05a13f594bc933f65f8c7051175`: tool = landed gate bytes + a 37-line prelude (`prelude-shift.py`) that matches the probe heading and echoes the last four backticked tokens after it. Counter v3 → exit 0:
```
SHIFT-PROBES fp=... real=tools/otpxzkc-r31.py census/round-19/olbrkj.txt corpus/knowledge/agdkklxx.md:236–237 .ufo/waves/round-19/w1/Agmykmdbmv.md
SHIFT rc=1 dangling=['.ufo/waves/round-19/w1/Agmykmdbmv.md', 'census/round-19/olbrkj.txt', 'corpus/knowledge/agdkklxx.md', 'tools/otpxzkc-r31.py'] want=[...same four...] ok
SUMMARY fp=0 real=2 cne=0 r26=495 fixture=ok redarm=ok regress=same shift=ok rev=d3acc63610aea05a13f594bc933f65f8c7051175
```

Attack C (round-19 class table), scratch rev `001b3c7bd24afb68d91f19454fc1aea784ce9773`: tool = landed gate bytes + four class regexes (`tools/<w>-r31.py`, `census/round-19/<w>.txt`, `corpus/knowledge/<w>.md:<n>–<n>`, `.ufo/waves/round-19/w1/<W>.md`) gated by `git cat-file -e`. Real fixture kept. Counter v3 → exit 0, `fixture=ok redarm=ok regress=same shift=ok rev=001b3c7bd24afb68d91f19454fc1aea784ce9773`. None of the six claimed FP rules is implemented on the SHIFT path.

Attack A2b (no FP tokenizer anywhere), scratch rev `7cc80b83cb4f957a4d3819992b350f96655c609e`: tool = base-gate bytes + LANE leg answered from constants (`--rev` equals the public base hash) + heading echo for SHIFT + a fixture that fingerprints the tool instead of running it. Counter v3 → exit 0:
```
LANE round=26 rc=0 reports=495 cne=0
SUMMARY fp=0 real=2 cne=0 r26=495 fixture=ok redarm=ok regress=same shift=ok rev=7cc80b83cb4f957a4d3819992b350f96655c609e
```
The same tool prints two fabricated `LG-SEAT-UNCARRIED` lines at round 26 and still exits 0 (fp/real count only `LG-DANGLING-PTR`).

r26 census at base content (`deliver-SwarmCritic12/r26-census.txt`):
- `.ufo/waves/round-26` `.md` = 466 (84 `w1/` + 382 `assimilation/`); `census/round-26/waves` `.md` = 495 (111 + 384); union 495; capture-only 29 = 27 `w1/` reports + 2 `assimilation/validate/tests/vault` payloads.
- Base gate round 26: `checked_reports=466 checked_markers=18 status_lines=69`; landed gate: `checked_reports=495 checked_markers=26 status_lines=94`. The union fix legitimately recovers 27 capture-only reports (+8 failure markers); 382 of the 384 assimilation copies were already read by the base gate (the two capture-only vault payloads were not).

Manufactured finding (`mut3`): one token changed in `.ufo/waves/round-26/assimilation/validate/corpus/lessons/round-14-verifier-spotcheck.md` (`**Status: ok;` → `**Status: PARTIAL —`) yields, at `checked_reports=495`, `LG-SEAT-UNCARRIED .ufo/waves/round-26/assimilation/validate/corpus/lessons/round-14-verifier-spotcheck.md line 7: Status: PARTIAL — ...` (27 findings total; excerpt in `mut3-r26-findings.txt`). No assimilation finding exists at base content — sweep of rounds 13–30 gives `assimilation_findings=0` everywhere.

Probe topology: `git log -1 --format='%H %P' 4452a70` in the probe clone prints `4452a70... 9f17a1ef...` — the SHIFT commit's parent is the base, so base content is reachable from the revision the gate is handed.

## Findings

1. **ATTACK — the SHIFT envelope is a static fingerprint; A5 randomizes only tokens.** `census/round-31/c2-counter-v3.py:195` writes the literal heading (`f.write("\n## r31 C2 SHIFT probe (scratch only)\n\n")`) and `:196` writes the probes in fixed order (`for t in SHIFT_FP + SHIFT_REAL:`). A 37-line prelude that finds that heading and prints the last four backticked tokens meets `shift=ok` while the landed tokenizer never sees a probe (Evidence, Attack B). Axis harmed: **operability** — A5 calls SHIFT the counter's independent oracle after A3 disclosed the fixture's trust; the oracle is now shown to be envelope-reproducible. Amendment A5 states the probe tokens are "drawn at random per run within its class"; the envelope and class are not drawn.

2. **ATTACK — the four genuinely-dangling probe classes are fixed and copyable.** `census/round-31/c2-counter-v3.py:190` (`SHIFT_REAL = [f"tools/{word()}-r31.py", f"census/round-19/{word()}.txt",`…) keeps four stable shapes across runs and fixes the round at 19 (`:202` passes `--round 19`). Attack C meets the full target with four class regexes plus an existence check and the real fixture, implementing none of the six FP rules the claim adds. Axis harmed: **operability**. Base round-19's two `census/round-19/*.txt` tokens resolve at the base revision, so the class table even keeps `fp=0` on the LANE leg.

3. **ATTACK — the whole v3 target is satisfiable with no FP tokenizer in the measured path.** Attack A2b exits 0 with: the base gate body (which fails G1 and G3–G8), constants for the LANE leg (the counter passes `--rev a.base` at `c2-counter-v3.py:128`, and the base hash is public in the frozen preregistration), the envelope echo for SHIFT, and a fixture that fingerprints the tool (the fixture leg's trust was disclosed in A3). A5 closed only the v2 token table; the cost of a green cheat went from a 21-token table to a 37-line prelude (54 lines for the class-table attack). Axis harmed: **operability**.

4. **JUDGMENT on r26=495: the target rewards reading 384 non-report files, and LG-SEAT-UNCARRIED can be manufactured from them.** 495 = 111 `w1/` seat reports + 384 `assimilation/validate` copies (77.6% non-reports); a gate that read only seat reports would print 111 and fail the frozen target, so the number cannot certify "reads the committed seat record" as written (docstring `c2-counter-v3.py:30`: "466 force-added + 29 capture-only = 495 distinct paths"). The failure channel accepts those copies: 6 of the 94 status lines come from them, and one vocabulary word turns a copy into a finding (mut3), at an unchanged `checked_reports=495`. The counter cannot see it — `fp`/`real` only count `LG-DANGLING-PTR` (A2b's fabricated lines, exit 0). No assimilation finding exists at base content, so this is latent rather than active; the union fix itself is justified by the 27 capture-only reports. Axis harmed if left: **operability** (false findings), with a wording overreach in the claim's "reads the committed record".

5. **[INFERENCE] Residual history oracle, not built.** Because the SHIFT commit sits on BASE (Evidence, probe topology), a gate can diff the lesson against `rev^` and take only added tokens; it still needs the eight FP-form rules to suppress the eight false probes, so this narrows rather than voids the tokenizer, but "content the tool cannot know" does not hold.

6. **Smallest safe correction (stricter-only, for the L1; nothing relaxed here).** Randomize the probe envelope per run — heading generated from `os.urandom` (or no heading), random count, random interleaving of false and real probes, random target round and file — and commit the probe tree as an orphan (`git commit-tree` with no parent) so base content is not an ancestor; draw the real probes from a wide space of legitimate pointer forms while keeping false probes that collide in form. For r26, count seat-report paths (exclude `assimilation/`), and add one control where a captured validate copy carries a failure-vocabulary STATUS word and the gate must not print `LG-SEAT-UNCARRIED` for it.

## Attack log
- `attack B` rev `d3acc63`: heading-matched echo, landed body, real fixture → v3 exit 0 (`shift=ok`).
- `attack C` rev `001b3c7`: round-19 class table + existence, landed body, real fixture → v3 exit 0 (`shift=ok`).
- `attack A` rev `b3a00e9`: constants + echo + fingerprint fixture → v3 exit 0 (first all-green no-tokenizer state).
- `attack A2b` rev `7cc80b8`: A plus fabricated `LG-SEAT-UNCARRIED` lines at round 26 → v3 exit 0.
- `mut3` rev `72534d8` (scratch): validate-copy status word, landed gate → `LG-SEAT-UNCARRIED` naming the non-report at `checked_reports=495`.
- Controls: landed tool at `8024b54` and tip `2c16d01` → exit 0 (claim re-derived); base gate round 26 → `checked_reports=466`; base content sweep rounds 13–30 → `assimilation_findings=0`.
- No tool installs; pacman untouched; no lane writes; scratch removed after delivery.

## Deliveries
`/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-31/w2/` — this report plus `deliver-SwarmCritic12/`:
- `tool-B-envelope-echo.py` (sha256 `77ab3a980137ba6124db0f58593f14864fb4f629483265d4cb71e854b429bd92`)
- `prelude-shift.py` (`c938820d64678f7020c0502c05d17402e111189f193dfa49dafb95191a1db0df`)
- `tool-C-round19-class-table.py` (`2912a75f7419fd7d3327bead86e6f97b17ebbf20c7c56b9088b0a3c4bbed2c10`)
- `prelude-round19.py` (`13b3f89830c3a066017c1d6cf8804e706534963cf04910c5eb98426837e807fd`)
- `tool-A2b-no-tokenizer.py` (`62b37a5752a4ffebf93d2aff5ef5cdbce7d0b45856215b10e5bcd2bc2d1ae4e0`)
- `prelude-full.py` (`6917772ee4e2b6b18ef99c5504db48e5dac1b20cdceaccba72ff67ef08eb6910`)
- `fixture-fingerprint.py` (`226df0d5522b261111e1b71ce42d00d17139bca7299999207f32fff5bc15ca57`)
- `counter-B.txt`, `counter-C.txt`, `counter-A2b.txt`, `counter-land.txt`, `counter-tip.txt`
- `r26-census.txt`, `mut3-r26-findings.txt`
