# S78CriticDiscern — C1 source rows / C2 ledger classes (souji r78, lane souji)
VERDICT: 19/19 ledger classes agree with the frozen grammar, and I reproduced every C2 number and the C1 17-row number from committed bytes. No frozen predicate flips. Two claim defects (HIGH tilde/%(prefix) include gap; MEDIUM config-set misattribution) and one claimed-work failure (HIGH missing LOG.md correction); 3 LOW notes. Axes: C1 operability, C2 calibration.

## SOURCES
S323 (corpus/SOURCES.md:282) grounds includes and the relative base (capture 99-103) and, inside its own scope word "tilde expansion", `~/`, `~user/` and `%(prefix)/` (census/round-78/srcs/git-config.adoc-v2.56.0:401-408). The W gate expands only `~/` (tools/souji-pre-report-gate.sh:63): `~user/` and `%(prefix)/` values are never stat'd. git expands both (probe: relative decoy unread; "unable to access '/root/probe.cfg'"; `%(prefix)` decoy unread). HIGH: "every file an include.path names" is not met; a FIFO there falls to the 45 s RECEIPT-GIT-TIMEOUT, not NONREGULAR-GITSOURCE. The frozen 17 rows do not cover it.
S323 does NOT ground "the system, global, repository and worktree config files": its filed scope is "which further files git reads while it reads a config file". Capture 4-10 names .git/config, config.worktree, $HOME/.gitconfig, /etc/gitconfig, but the XDG base file appears only as an example (capture:187; S058 covers config.worktree read order only). MEDIUM over-attribution: the XDG base file is measured (`git config --list --show-origin`) but has no row this round.
S324 (corpus/SOURCES.md:283) grounds commondir (quote 327-329, strbuf_read_file) and HEAD validation by validate_headref (scope: line 350 read but not quoted; open O_RDONLY at 373 is blocking). It does not ground the config set nor "every git command" (code-path inference; rows g1-g4 measure only check-1 rev-parse). Tier-A code is the right tier for file+call identity; execution is the fixtures' job (K-a 12 HANG; W 17/17), so the split is sound — LOW wording only.
S062 (corpus/SOURCES.md:97) is the block-on-open; S323/S324 name the files. packed-refs (row g3) is grounded by neither and is absent from the claim sentence; corpus/knowledge/git-discovery-sources.md cites only the row — LOW.

## LEDGER (census/round-78/c2-pointer-ledger.tsv; LOG line opened at a8558d41)
L01 FLEET agree — fleet mint-roster-scan.json present (scanned_by orchestrator); lane absent.
L02 L03 LOCAL-POLICY agree — lane census/operator-sweep-20261019 present; .gitignore:2 rule.
L04 ABSENT agree — lane .ufo/waves/round-16/build absent; it was untracked (census/round-15/disposition.json:17 "??"), "absent now" (.ufo/waves/round-18/w1/PointerSweepKnowledge.md:117).
L05 ABSENT agree — no file named gate-replays-ddb7347 anywhere; census/round-17 committed gate-replays-4f48343.json instead; LOG:916 calls it uncarried.
L06 QUARANTINED agree — lane .ufo/quarantine/round-17/tests/.../dot-git-empty-stub exists as an empty dir; r77 P14 same target (census/round-77/c2-pointer-ledger.tsv:12). LOW: placeholder only, content unverified.
L07 L08 ABSENT prose agree — r31 already adjudicated both prose/extensionless (census/round-31/waves/w1/deliver-c2-fp-map.md:19,22); no such path in history.
L09 FLEET agree — fleet .ufo/scopes/souji-mint-20261018/ present.
L11 L12 L15 L21 MOVED agree — census/round-42/waves/w3, round-44/waves/w1-results.json ("round":44), round-54/wave/S54critic01.md, round-69/records/wave-w1/w1-results.json ("round":69) exist at A with the frozen digests and the bound round/last component.
L13 TOKEN agree — token ends "-", LOG:2309 continues "located-quote.txt"; target exists at rev.
L16 L18 FLEET agree — fleet .ufo/l0-questions.md present; lane absent.
L17 ABSENT removed agree — census/round-56/__pycache__ absent; LOG:2756 records the removal and `git ls-files` is empty.
L19 ABSENT agree — corpus/README.md exists; corpus/README never existed (git log --all empty). LOW: it is a dropped-.md path reference, not prose.
L22 FLEET agree — fleet .ufo/watchdog.log:3072 carries "lane-dead-no-report souji round=73".

## FINDINGS
HIGH the prereg's claimed "append-only LOG.md correction naming each item's class" is not landed at the measured after revision: LOG.md blob is 18c26087c595cd55fde555cd09df282e896ffbab at base and at A, and no commit in base..A touches LOG.md. The lost/prose/removed distinctions live only in ledger notes, while the counter's ABSENT proves absence only (c2-pointer-counter.py judge() ABSENT branch). Land it in the report commit or the claimed work is unmet; kill predicates unaffected.
MEDIUM the L commit subject's counts are wrong: "FLEET 6, ABSENT 7 [lost 3]..." sums to 21 for a 19-row ledger; actual FLEET 5, ABSENT 6 [lost 2], MOVED 4, LOCAL-POLICY 2, QUARANTINED 1, TOKEN 1. Do not copy into the report.
LOW a dangling config/include symlink is refused (gate:49 tests -L as well; fixture prints check-gitsource=FAIL) although git works (rev-parse rc 0) and the rule says "a symlink counts by its target"; the fail-closed reading is within policy, but pin it with a q6 positive.
LOW L04's "lost" is an absence inference (round 18 calls it "deliberate ... build dir gone"); class ABSENT is unaffected.

## GATE
ADMIT `~user/` and `%(prefix)/` include forms named by S323 (capture 401-408) are not expanded by gitsrc_one (gate:63); fix = fail closed on any include value starting "~" (not "~/") or "%("; no population change.
REJECT "L04 should be FLEET because .ufo/waves/round-16/build exists" — the three dirs found are kama/tsukuroi/mori's own round-16 dirs; this lane's token was an untracked artifact and is absent under this lane and the fleet root.

## COMMANDS / EVIDENCE
C2: python3 -B census/round-78/c2-pointer-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev 319109b0 --fleet-root /home/vgpnk/Projects/shokunin --population census/round-78/c2-population.tsv --ledger census/round-78/c2-pointer-ledger.tsv --forge census/round-78/c2-forge-r78.tsv; pointer check --root . --rev <base|A> LOG.md; controls K-a..K-e as committed (K-c via c2-forge-legacy.py, K-e via g6-collision.sh).
C2 output: "SUMMARY items=22 resolved=22 unresolved=0 refused=0 mismatched=0 errors=0"; "FORGE-SUMMARY forged=12 matched=12 accepted=0"; pointer check missing=22 (base) / 19 (A); K-a 0/22; K-b 19/22 refused=3; K-c accepted=7; K-d EXIT=2; K-e r77_accepts=yes r78_refuses=yes; r77 population "items=35 resolved=35" / "forged=7 matched=7".
C1: gate blob 5795d655… (sha256 b746bd9d…), counter sha e53dd0ca…: "SUMMARY rows=17 mismatches=0 errors=0 hangs=0"; ROW/SUMMARY lines identical to census/round-78/records/c1-after.txt (only scratch paths and per-row seconds differ). I did not re-run the ~15-min base-gate hang arm; K-a is cited from its receipt.
Files written: .ufo/waves/round-78/w1/S78CriticDiscern.md (this report). Scratch /fast/scratch/hyaku/souji-r78/S78CriticDiscern removed; no receipt needed copying (all cited evidence is committed).
