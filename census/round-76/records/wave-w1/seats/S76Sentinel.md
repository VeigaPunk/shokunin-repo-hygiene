# S76Sentinel — W gate e827d2bf: fail-closed / security / resource review
Gate blob `7a8eec51` (same at e827d2bf and 113b0072:`tools/souji-pre-report-gate.sh`), writer `70bbf1c2`; line refs are to that blob. Fixtures/scripts in `.ufo/waves/round-76/w1/S76Sentinel/` (scratch removed).
## Route table (verdict = gate's check-clean on a fresh fixture)
| route | verdict |
|---|---|
| repo-local `core.fsmonitor=<script>` | **EXEC** + `check-clean=PASS` (HIGH-1) |
| `alias.check-ignore`/`alias.ls-files`, `core.hooksPath`(+4 hooks), `core.pager` | SKIP: no marker (aliases cannot shadow builtins; status/ls-files/check-ignore run no hook) |
| caller `GIT_EXEC_PATH=<dir>`, https origin | **EXEC** via `ls-remote`'s `git-remote-https` (MEDIUM-1) |
| FIFO as untracked `cache/.gitignore` / as `core.excludesFile` | **HANG** >20 s, rc=124 (base gate ee59aa4 hangs too; MEDIUM-2) |
| f7 self-ignoring dir; f9 nested; f14 untracked-in-tracked-dir; symlinked `.gitignore` | clean-refuse `UNDECLARED-IGNORE: 2` (git itself ELOOPs a symlinked .gitignore) |
| `info/exclude`-only; repo-local `core.excludesFile`-only | clean-refuse before the block: `LOCAL-EXCLUDE: 1` / `pinned git status lists 1 record(s)` |
| f2 broad committed `*`; f11 tracked `toolcache/`; f12 tracked `sub/.gitignore`; untracked embedded repo under tracked `emb/` | ok=PASS (f2 = prereg stated limit; trailing-slash path frames correctly) |
| 200k ignored files / depth 2000 / 50k self-ignoring | ok: 819 ms PASS 87 MB RSS / 285 ms / 271 ms `UNDECLARED-IGNORE: 50001` — no `check-ignore --stdin` deadlock (`run(input=)` → communicate) |
| ANSI/CTL/tab/newline names in an ignored dir | ok: count only, 0 raw ESC bytes; status echo is C-quoted, then `tr -c '[:print:]' '?'` |
| domain trial, real lane, read-only | ok: `check-clean=PASS`, 26376 ignored paths, undeclared=0, 4.8 s |
| replica over siblings | refuses all: kumitate 11285/11285, kasegi 10155/10164, kagi 4726/7451, kama 16669/16691, tabi 8453/9625, tsukuroi 13903/13906, mado 17686/17998 — deciding source is an untracked `.jj/.gitignore` (+`.ruff_cache/.gitignore`) every time |
## Findings
**HIGH-1 — the block's new subprocess runs repo-configured code and flips its own refusal to PASS.** `tools/souji-pre-report-gate.sh:116` omits the `-c core.fsmonitor=false` its siblings carry (`:100`, `:124`), so a repo-local `core.fsmonitor` executes there (logged parent cmdline: `git --no-optional-locks -C <lane> ls-files -z --cached`) *after* the byte-truth check (`:63-84`) and *before* check-ignore; appending `cache/` to the tracked root `.gitignore` in that hook makes check-ignore report `src=.gitignore` (tracked, dir `""`, non-negated) → undeclared=0. Repro `w-gate-fsmonitor-bypass.sh`: control `check-clean=FAIL … UNDECLARED-IGNORE: 2` → armed `check-clean=PASS`, lane left `M .gitignore`. Same hook also fires at `:61` (`status`; that one is pre-existing — base gate reproduces it). Smallest fix: `-c core.fsmonitor=false` on `:116` (and `:61`) plus a byte-truth re-check after the block.
**MEDIUM-1 — `GIT_EXEC_PATH` is not in the unset list (`:4-9`)**: `git ls-remote` (check 1, `:32`) runs `git-remote-https` from it; `w-gate-exec-probes.sh git-execpath` fires the marker. Fix: `unset GIT_EXEC_PATH`.
**MEDIUM-2 — no timeout; a FIFO `.gitignore`/`core.excludesFile` blocks the gate forever** (pre-existing, the new block only adds another reader). Fix: reject non-regular exclude sources before listing.
**LOW-1 — `tracked` is index membership, not HEAD (`:121`)**: an intent-to-add or staged `.gitignore` passes the attribution test (replica: undeclared=0 for a rule with no committed bytes); only `:61-62` catches it, so a concurrent stage between `:61` and `:116` reads as declared. Fix: derive `tracked` from `git ls-tree -r HEAD`.
**LOW-2 (report-only, not a souji defect)** — all siblings carry an untracked `.jj/.gitignore` + `.ruff_cache/.gitignore`; souji reads 0 only because e827d2bf added `.jj/` and `.ruff_cache/` to its tracked `.gitignore`. Operator action needed before reusing this gate there (kasegi also has 1 `info/exclude` path).
## Commands
`git show e827d2bf:tools/souji-pre-report-gate.sh > G/souji-pre-report-gate.sh` (same for the writer), then `bash G/souji-pre-report-gate.sh --lane <fx> --branch main --report R --prereg P`;
`bash w-gate-{probes,exec-probes,resource-probes,fsmonitor-bypass}.sh <route>`; `python3 -B attrib-replica.py --lane /home/vgpnk/Projects/shokunin/<lane>-shokunin --quiet`; `git diff --stat e827d2bf 113b0072 -- tools/` (empty; blob stable).
## Files written
`.ufo/waves/round-76/w1/S76Sentinel.md`, `S76Sentinel/attrib-replica.py`, `S76Sentinel/w-gate-probes.sh`, `S76Sentinel/w-gate-exec-probes.sh`, `S76Sentinel/w-gate-resource-probes.sh`, `S76Sentinel/w-gate-fsmonitor-bypass.sh`. No tools installed.
VERDICT: the attribution logic itself is fail-closed on every non-exec route and does close f7/f9/f14 as claimed, but the new subprocess is not pinned against repo-configured code execution (HIGH-1: demonstrated PASS on a lane the block itself refuses), so the r76 C1 claim does not hold against an adversary who controls the lane's `.git/config`.
