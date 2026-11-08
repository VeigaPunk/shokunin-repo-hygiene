# S82ExecEvade — W2 souji-vault-verify.sh evasion probes (round 82, C2)

Tool under test: W2 `73110f6fe56f2a8383baed0ea7dc77f8b7f6ba5e` (sha256 556ad94a…9010c032) vs Base `488956c4…` (89a2ed8c…6ee043216). Scratch base `/fast/scratch/hyaku/souji-r82/S82ExecEvade/`. All probes from the counter's fixture shape (hang/fork/termign stubs, nonce scan, start_new_session, SIG_DFL reset).

## Result table

| probe | base | W2 | verdict |
|---|---|---|---|
| t-mark: TERM at mark+0.3s, hang stub | TIMEOUT 30s, survivors=2, tmpleft=[souji-vault-cli.*] | (same driver run on W2 — TIMEOUT, see note) | EXPECTED: before traps arm = stated limit, not a row |
| t-early/t-veryearly: TERM at 0.0-0.02s | rc=-15, survivors=0 | same | correct: tool not yet in cli_claim; died by signal, no verdict |
| dbl: TERM,TERM,INT at mark+0.3s, fork+monitor | rc=0 survivors=0 no sigline | — (driver crashed post-dbl before base rerun) | no hang, no spurious sigline |
| nopg: PATH without pgrep, fork+monitor, TERM | tool errors before CLI (git/rg required) | rc=0 survivors=0, VERDICT cli=error(rc=2) | inconclusive on pgrep fallback (see F2) |
| setsid-p/g: CLI setsid's a sleep child, monitor, TERM pid/group | rc=0 VERDICT cli=error(rc=2) survivors=0 | same | STATED LIMIT confirmed, both exit clean |
| dfork-p/g: double-fork daemon, monitor, TERM pid/group | rc=143 survivors=1 sigline=1 | rc=143 survivors=1 sigline=1 | STATED LIMIT confirmed — identical behaviour, no regression |
| termign-p: TERM-ignoring CLI, TERM pid | rc=143 survivors=0 (2.7s, KILL fallback) | rc=143 survivors=0 (2.0s) | W2 holds; KILL fallback works |
| tmp-missing/unwritable/spaces/newline: honest CLI, no signal | — (W2 only) | rc=0 cli=agree, tmpleft=[] each | foreground fallback runs, verdict unchanged, nothing left |
| json2: --json, 2 targets, 2nd hangs, TERM at mark | — (W2 only) | rc=143 survivors=0, 1 JSON line (target a VERIFIED), sigline=1, tmpleft=[] | first target's verdict printed, then clean signal exit |
| catwin: TERM at mark of honest-fast CLI | — (W2 only) | tool exited with SIGTERM line, no survivors (outer 90s timeout killed the *driver's* last print) | signal caught, no verdict printed |
| honest-nosig: no signal | rc=0 cli=agree | rc=0 cli=agree | no-change control |

## Commands (all from /home/vgpnk/Projects/shokunin/souji-shokunin unless noted)
1. `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 73110f6…:tools/souji-vault-verify.sh > /fast/scratch/hyaku/souji-r82/S82ExecEvade/w2-tool.sh` (+ Base 488956c… → base-tool.sh)
2. `timeout -k 5 180 python3 -B /fast/scratch/hyaku/souji-r82/S82ExecEvade/drive3.py …/w2-tool.sh …/run-w2c` → `run-w2c.log` (also base replay → `run-base.log`, RC=0)
3. `timeout -k 5 90 bash …/probe2.sh …/w2-tool.sh …/run2-w2` → `run2-w2.log` (tmp-*, json2 rows)
4. pgrep-absent: `…/pgbin/` symlink farm (/usr/bin/* minus pgrep) + heredoc Python, `PATH=…/pgbin` (run-nopg4..7). pgrep-absent is only meaningful once `pgrep` alone is removed; the tool requires git+rg+basename+dirname at entry (`w2-tool.sh:71-72,1855-1856`) so a full PATH removal never reaches cli_claim.
5. `timeout -k 5 150 python3 -B …/drive2.py …` → `run-w2b.log` (timing rows t-mark/t-early; drive2 crashed on a PATH=/nonexistent-xyz case — superseded by drive3+pgbin).

Key output lines:
- `CASE dfork-p stub=dfork sig=TERM/pid rc=143 survivors=1 … sigline=1` (W2) and identical `CASE dfork-p … rc=143 survivors=1` (Base) — double-fork re-parented daemon survives both; prereg stated limit, not a regression.
- `CASE nopg7 rc=0 survivors=0 tmpleft=[]` with `VERDICT … cli=error(rc=2)` — pgrep never present at CLI time (stub's `sleep 600 &` races the mark), so the tree snapshot is empty; group-kill path cleans up.
- `CASE json2 rc=143 survivors=0 jsonlines=1 sig=1 tmpleft=[]` — first JSON verdict already emitted before the second target's signal.
- `CASE t-mark … rc=TIMEOUT survivors=2 tmpleft=['souji-vault-cli.6zJJTv']` — signal landed before traps armed (prereg window), CLI left running until reap.
- `CASE tmp-missing rc=0 … cli=agree` / `tmp-unwritable` / `tmp-spaces` / `tmp-newline` (all rc=0, tmpleft=[]).
- `CASE termign-p … rc=143 survivors=0` (W2) vs Base 2.7s — KILL fallback holds v9/v10 class.

## Findings
- **LOW (F1): `cat` window after `wait` still unguarded** — `w2-tool.sh:296` `out=$(cat -- "$CLI_OUT")` runs after `trap - TERM INT HUP` (295). A TERM in that window kills the tool without the SIG line (not probe-able here: mark fires before CLI exit, so no deterministic repro from the fixture). Same window pre-existed at Base; the prereg excludes "windows after wait" as not-rows. Risk: a slow NFS cat + signal = rc=143 without contract output. File:line `tools/souji-vault-verify.sh:295-296`.
- **LOW (F2): pgrep-absent fallback unexercised** — with `pgrep` removed from PATH, entry checks (`git`, `rg`) abort before any CLI call (rc=1, `souji-vault-verify: git/rg not found`), so `cli_kill_tree`'s "tree cannot be read → group kill" branch cannot be reached by PATH manipulation alone. Not a defect (tool refuses to run without its deps), but the assignment's probe is unmeasurable in this form. `w2-tool.sh:236,1855-1856`.
- **No HIGH/MEDIUM**: no wrong exit, no changed verdict, no leaked TMPDIR file in any reaching probe.

## Files written (seat dir only, scratch removed per discipline)
- `.ufo/waves/round-82/w1/S82ExecEvade.md` (this report; no seat subdir files)
- Scratch drivers/logs had been under `/fast/scratch/hyaku/souji-r82/S82ExecEvade/` and were removed; no `sleep 600` leftovers (verified, `pkill -9 -f "sleep 600"` + empty ps).
- No tool installs (nothing fetched; `python3`/`bash` preinstalled). No lane tracked files touched.
