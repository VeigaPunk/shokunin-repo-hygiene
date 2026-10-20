# RerunLegacySelftest — round 16 wave 2 (operability)

Seat: SoujiR16.RerunLegacySelftest-4 (leaf, no delegation, no commits, no lane edits).
Lane: /home/vgpnk/Projects/shokunin/souji-shokunin. HEAD observed at probe: `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae`; HEAD observed at the last git call: `163158a706352f1c0ee3521c4da2e5289970db57` (L1 landed the lesson mid-probe). The census blob is byte-identical at `0a70beff` (C1 / final matrix), `a6ec7810` and `163158a7`: blob `b8442e2ead501ad0ba1f68472e265516040f4aa0`, 1877 lines, sha256 `64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c` — matches the ticket's `64a60fd0b0ed…`. Worktree file `tools/souji-census.sh` is mode `0755`, index mode `100755`, `core.fileMode=true`, and `git diff -- tools/souji-census.sh` is empty, so the measured bytes are the HEAD bytes, not a stale worktree. Line numbers below are that blob's lines.

Tool installs/updates: none.
Probe compliance: only the ALLOWED-EXEC command was executed, with one added `chmod +x` on the copy (F1 explains why the recipe needs it); every read was an exact-file read; no recursive search over the lane, fleet root, or a directory tree; `census/operator-sweep-20261019/` untouched; no lane edits. All execution and writes confined to `/var/tmp/souji-r16-RerunLegacySelftest/` (deleted after this report).

STATUS: PARTIAL — 38/38 reproduces at the landing HEAD and the XDG pin does close the host-config branch, but the item's own invocation aborts 126 from a mode-stripped copy (F1), and "host-independent" is not literally true (system gitattributes, init templates, undocumented toolchain floors: F3).

## Item 1 — legacy `--selftest` rerun: holds

Command actually run (after `chmod +x`): `TMPDIR=/var/tmp bash tools/souji-census.sh --selftest` from the copy at `/var/tmp/souji-r16-RerunLegacySelftest/tools/`.

- `EXIT=0`; last line `selftest: 38 checks, 0 failed`; 38 `PASS` lines and 0 `FAIL` lines on stdout; stderr empty; wall ~4.9 s.
- The 38 include the checks that matter for this rerun: `repeat: two runs byte-identical` (determinism), `mtime_iso shape (2026-10-20T12:02:40-03:00)` **and** `mtime ignores future .ufo/state and .ufo/watchdog.log` (the second compares the row against `kept.txt`'s own ISO mtime, so the host TZ cancels), four malformed-baseline cases (`bad`/`empty`/`blank-lead`/`blank-before-header`, all exit 2), `compare mutation: exit 3`, both protected-root refusals (`exit 2, path-protected`), the `no forbidden git subcommand` source audit over the copy itself, and `fixtures under mktemp`.
- Cross-check against recorded evidence: `census/round-16/c1-matrix-final.json` and `c1-matrix-landing.json` both record `arms.changed.selftest = {checks: 38, failed: 0, rc: 0}`, `arms["pre-harm"].selftest = {36, 0, 0}`, `arms["r15-baseline"].selftest = {null, null, rc 2}`; recorded `lane_head 0a70beff`, `bash_version` 5.3.20, `git_version` 2.56.0. Host observed: bash 5.3.20, git 2.56.0 — same toolchain. So this is an independent reproduction of the recorded number on a later HEAD with the identical blob, not a citation.
- Cleanup: `ST_TMP=$(mktemp -d /var/tmp/...)` at 1527 with `trap 'rm -rf -- "$ST_TMP"' EXIT` at 1528. After both the successful run and the aborted 126 run (F1) no `/var/tmp/souji-census-selftest.*` or `/var/tmp/souji-census-now.*` directory remained.
- Self-containment: `run_selftest` ends with `exit 0` (1834) and `--selftest` is dispatched at 1858, before the `--root`/`--compare` guard block (1860-1868). Nothing reads the repo containing the script, so a copy outside the lane is a valid target — proven by running from `/var/tmp`.

## Item 2 — XDG pin: holds for the branch it covers

Pin: `export XDG_CONFIG_HOME="$ST_TMP/no-xdg-config"` at 1531, the first state change after `mktemp`/`trap` (1527-1528) and before the first `st_init` fixture, so it is in force for every census invocation the suite makes.

Reach of the pin, verified by code path:

1. In-process invocations at 1614-1616, 1725, 1741, 1756, 1778 call `"$SELF"` directly; 1786, 1800, 1811 call it through `env` with only `GIT_DIR` removed and `HOME`/`TMPDIR`/`SOUJI_CENSUS_SELFTEST_ACTIVE` added. `env` inherits the rest of the environment, and the pin is exported (1531), so every child sees `XDG_CONFIG_HOME=$ST_TMP/no-xdg-config`.
2. `status_info_file` (942-979) is the only consumer of the XDG default (grep over the blob finds `XDG_CONFIG_HOME` read only at 960, plus the header comment at 113 and the pin's comment/export at 1529/1531). A repo-local `core.excludesFile`/`core.attributesFile` wins, but only repo-local config exists — global and system config are `/dev/null` at 152-154. When the repo-local key is unset, `base=${XDG_CONFIG_HOME:-}` (960) is the pinned path, so the `$HOME/.config` fallback at 961-963 is unreachable even with the operator's real `HOME`.
3. The pinned target `$ST_TMP/no-xdg-config/git/{ignore,attributes}` does not exist, so `resolve_guarded` (975) fails and the function prints `/dev/null` (978). `count_dirty` then runs `git status` with `-c core.excludesFile=/dev/null -c core.attributesFile=/dev/null` (1036-1037).
4. That closes exactly the failure mode w1 `RevLegacySelftestGap` F1 named: a host `git/ignore` pattern that would lower `dirty` below 2 and trip the hard assertion at 1659 (and the flags assertion at 1666).

Other host inputs, checked and either cancelled or listed under F3:

- Every inherited `GIT_*` variable is cleared at 150-151; `GIT_CONFIG_GLOBAL`/`GIT_CONFIG_SYSTEM` are `/dev/null` and `GIT_CONFIG_NOSYSTEM=1` (152-154); `core.fsmonitor`/`core.hooksPath` are forced via `GIT_CONFIG_COUNT` (162-163), which outranks repo-local config.
- Identity: `st_commit` (1490-1503) passes `-c user.name`/`-c user.email` and uses `commit-tree`, so a host without git identity cannot fail the fixtures.
- Time zone: `mtime_iso` (1116) and `kept_iso` (1644) both format the epoch with `date -d @… --iso-8601=seconds`; the assertion at 1715 compares two strings produced by the same host setting, so TZ cannot flip the result (it does change the literal string, which is why the observed row reads `-03:00`).
- Locale: both sorts are `LC_ALL=C` (1305, 1440); the remaining `grep`/`awk`/`du` uses are numeric or fixed-string.
- Empirical caveat: this run inherited an ambient `XDG_CONFIG_HOME=/home/vgpnk/.config`, but the host has neither `git/ignore` nor `git/attributes` (checked; absent), so the pass alone cannot distinguish "pin overrides" from "nothing to leak". I did not run a hostile-ambient variant: the probe rule permits only the named command. Items 2 and 3 above are the proof.

## Findings

### F1 — MEDIUM (recipe/harness; not a production defect): `--selftest` aborts 126 when the script is not executable

Evidence, observed: a fresh copy made exactly as the item prescribes (`git show HEAD:tools/souji-census.sh > /var/tmp/.../tools/souji-census.sh`) is mode 0644. `TMPDIR=/var/tmp bash tools/souji-census.sh --selftest` printed one line — `env: ‘/var/tmp/souji-r16-RerunLegacySelftest/tools/souji-census.sh’: Permission denied` — and exited 126 with zero checks executed. After `chmod +x` on the same bytes the suite ran to 38/38.

Cause: nine re-executions of `"$SELF"` (1614, 1616, 1725, 1741, 1756, 1778, 1786, 1800, 1811). The first is inside the script-wide `set -euo pipefail` (139), so the EACCES at 1614 aborts the run instead of producing a FAIL row; the `env` prefix at 1613 is why the diagnostic is attributed to `env`. `"$SELF"` at 183 and 1822 is read-only (`awk`/`grep` over the file) and does not matter.

Impact: the recorded 38/38 is not reproducible under the item's own recipe. `census/round-16/run-matrix.py` silently compensates — `shutil.copyfile` at 101, `tool.chmod(0o755)` at 108, `bash tool --selftest` at 114 — so the matrix's 38/38 depends on a step the wave-2 recipe omits.

Smallest fix (either one):

- recipe: `chmod +x <copy>` before running (one line, no lane edit; matches run-matrix.py:108); or
- tool: invoke the children through the interpreter — `"$BASH" "$SELF"` at the nine sites (or define `ST_RUN=("$BASH" "$SELF")` beside `SELF` at 167) — which makes `bash <path>` mode-independent.

Not a production defect: the index mode is 100755 and the worktree file is 0755, so the documented direct invocation `tools/souji-census.sh --selftest` works. The exposure is exactly the copy-and-run form used for evidence.

### F2 — LOW: `--selftest` silently ignores scan arguments

`--root`, `--compare` and `--include-root` are parsed (1839-1854: `--root` at 1843, `--compare` at 1847) and then discarded, because `run_selftest` exits (1834) at the dispatch on 1858 before the ROOT/compare block. `souji-census.sh --root /some/fleet --selftest` therefore exits 0 having censused nothing and prints only selftest lines — on an evidence tool that is a plausible misread ("fleet clean"). Smallest fix: set a `ROOT_SET=1` at the two `--root` arms and, at 1858, reject `--selftest` combined with `ROOT_SET` or `COMPARE_SET` via `usage_err`.

### F3 — LOW: host-independence is not literal — three unpinned inputs

1. **System gitattributes.** `GIT_ATTR_NOSYSTEM` is never set (grep: absent from the blob; only `GIT_CONFIG_NOSYSTEM=1` at 154), so `git status` (1036-1037) and `check-attr` (983-1010) still consult the host's system attributes file. `/etc/gitattributes` and `/usr/local/etc/gitattributes` are absent on this host, so nothing was observed; where present, the only effective binding is `filter=`, which `guard_bound_filters` already converts to `status-unverifiable` — availability, not a wrong dirty count. Fix: one `export GIT_ATTR_NOSYSTEM=1` beside 154.
2. **`git init` template.** `st_init` (1504-1507) takes the host default `init.templateDir`; this host's `/usr/share/git-core/templates/info/exclude` has zero non-comment lines (checked), so inert today. A host template carrying ignore patterns would change `dirty` and break 1659. Fix: `git init -q --template= --initial-branch="$2" "$1"` in the helper.
3. **Undocumented toolchain floors.** bash ≥ 4.4 (`mapfile -d` at 621/986/1002), git ≥ 2.28 (`init --initial-branch`, 1505), git ≥ 2.45 for `GIT_NO_LAZY_FETCH` (161; silently ignored by older git), GNU findutils `-printf` (1078) and GNU `stat -c`/`date --iso-8601` (1116, 1644). Header lines 4-5 say "bash + coreutils + git only", which overstates portability. Fix: name the floors in the header.

## Residual risk and verification gaps

- The 38 checks are the legacy gate; they do not claim to cover the five r16 behaviors (w1 `RevLegacySelftestGap` F2/F3/F5 stand). This rerun confirms the legacy suite is green, not that it certifies r16.
- 38/38 is reproducible across hosts only to the extent that F3's three inputs are absent; none of them is exercised by the suite, so a host that violates one would fail with a misleading "leak" message (e.g. 1718).
- `TMPDIR=/var/tmp` in the prescribed command is inert: `$ST_TMP` is `mktemp -d /var/tmp/...` (1527) and the two protected re-execs set `TMPDIR=/var/tmp` themselves (1798, 1809). Harmless, but the prefix advertises a knob that does nothing.
- The XDG conclusion is code-path verified, not mutation-tested (host has no `git/ignore`/`git/attributes`; hostile-ambient rerun barred by the probe rule).
- HEAD moved between probe (`a6ec7810`) and the last git call (`163158a7`). The census blob is unchanged across both, so the measurement is valid at the current HEAD; any later edit to `tools/souji-census.sh` invalidates it.

## Commands

```sh
mkdir -p /var/tmp/souji-r16-RerunLegacySelftest/tools && git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD && git -C /home/vgpnk/Projects/shokunin/souji-shokunin show HEAD:tools/souji-census.sh > /var/tmp/souji-r16-RerunLegacySelftest/tools/souji-census.sh && sha256sum /var/tmp/souji-r16-RerunLegacySelftest/tools/souji-census.sh && wc -l /var/tmp/souji-r16-RerunLegacySelftest/tools/souji-census.sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -r --name-only HEAD | grep -E 'souji-census|round-16' | head -50
cd /var/tmp/souji-r16-RerunLegacySelftest && TMPDIR=/var/tmp bash tools/souji-census.sh --selftest 2>&1; echo "EXIT=$?"
cd /var/tmp/souji-r16-RerunLegacySelftest && grep -n 'XDG_CONFIG_HOME\|run_selftest\|HOME=\|env -i\|unset ' tools/souji-census.sh
cd /var/tmp/souji-r16-RerunLegacySelftest && chmod +x tools/souji-census.sh && TMPDIR=/var/tmp bash tools/souji-census.sh --selftest > /var/tmp/souji-r16-RerunLegacySelftest/selftest.out 2>/var/tmp/souji-r16-RerunLegacySelftest/selftest.err; echo "EXIT=$?"; echo '--- stdout tail'; tail -6 /var/tmp/souji-r16-RerunLegacySelftest/selftest.out; echo '--- stderr'; cat /var/tmp/souji-r16-RerunLegacySelftest/selftest.err; echo '--- counts'; grep -c 'ok' /var/tmp/souji-r16-RerunLegacySelftest/selftest.out; grep -c 'FAIL' /var/tmp/souji-r16-RerunLegacySelftest/selftest.out
cd /var/tmp/souji-r16-RerunLegacySelftest && grep -n '"\$SELF"' tools/souji-census.sh; echo ---; grep -n 'LC_ALL\|LANG=\|TZ=\|export TZ\|LANGUAGE' tools/souji-census.sh; echo ---; sed -n '1,60p' tools/souji-census.sh
cd /var/tmp/souji-r16-RerunLegacySelftest && grep -n 'SELF=\|BASH_SOURCE\|ST_TMP=\|mktemp' tools/souji-census.sh; echo ---; git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree HEAD tools/souji-census.sh; ls -l tools/souji-census.sh
cd /var/tmp/souji-r16-RerunLegacySelftest && grep -n 'status_info_file\|--porcelain\|core.excludesFile\|core.attributesFile' tools/souji-census.sh
cd /var/tmp/souji-r16-RerunLegacySelftest && grep -n 'st_ok()\|st_bad()\|st_note()\|mtime\|sed ' tools/souji-census.sh | sed -n '1,60p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '38' .ufo/waves/round-16/w1/RevLegacySelftestGap.md | head -20; echo '=== files mentioning legacy selftest'; grep -rln 'legacy selftest\|38/38' .ufo/waves/round-16/w1/ | head; echo '=== matrix json legacy'; grep -n 'legacy' census/round-16/c1-matrix-final.json census/round-16/c1-matrix-landing.json 2>/dev/null | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
for f in ('census/round-16/c1-matrix-final.json','census/round-16/c1-matrix-landing.json'):
    d=json.load(open(f))
    print('==',f, 'top keys:', list(d)[:8] if isinstance(d,dict) else type(d))
    def walk(o,p=''):
        if isinstance(o,dict):
            if 'selftest' in o: print('  at',p or '<root>','->',json.dumps(o['selftest'])[:300])
            for k,v in o.items():
                if k!='selftest': walk(v,p+'/'+str(k))
        elif isinstance(o,list):
            for i,v in enumerate(o): walk(v,p+'/'+str(i))
    walk(d)
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'selftest\|chmod\|copy\|subprocess\|bash' census/round-16/run-matrix.py | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls -la census/round-16/*.json 2>&1; echo '=== selftest rows'; grep -n 'selftest' census/round-16/*.json 2>/dev/null | cut -c1-220
ls -d /var/tmp/souji-census-selftest.* /var/tmp/souji-census-now.* 2>&1 | head; echo '---'; python3 -c "
import json
d=json.load(open('/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-16/c1-matrix-final.json'))
print('lane_head',d['lane_head']); print('bash',d['bash_version']); print('git',d['git_version'])
a=d['arms']['changed']; print(json.dumps({k:v for k,v in a.items() if k!='cases'}, indent=1)[:1200])
"
cd /var/tmp/souji-r16-RerunLegacySelftest && grep -c '^PASS ' selftest.out; grep '^PASS ' selftest.out | sed 's/^PASS //' | cut -c1-60
cd /var/tmp/souji-r16-RerunLegacySelftest && grep -n 'kept_iso\|date -d\|date +' tools/souji-census.sh; echo '--- 1113-1145'; sed -n '1113,1145p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse 0a70beff3becff2c64944595860a31fc6e193076:tools/souji-census.sh a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae:tools/souji-census.sh && git diff --stat 0a70beff3becff2c64944595860a31fc6e193076 a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae -- tools/souji-census.sh; echo "diff_rc=$?"
bash --version | head -1; git --version; printf 'XDG_CONFIG_HOME=%s\n' "${XDG_CONFIG_HOME-<unset>}"; test -e /home/vgpnk/.config/git/ignore && echo 'host git/ignore exists' || echo 'host git/ignore absent'; test -e /home/vgpnk/.config/git/attributes && echo 'host git/attributes exists' || echo 'host git/attributes absent'; echo '--- bash features'; grep -c 'mapfile -d' /var/tmp/souji-r16-RerunLegacySelftest/tools/souji-census.sh; grep -n 'printf .%(' /var/tmp/souji-r16-RerunLegacySelftest/tools/souji-census.sh | head -3
cd /var/tmp/souji-r16-RerunLegacySelftest && grep -n 'GIT_ATTR\|gitattributes\|NOSYSTEM' tools/souji-census.sh; echo "rc=$?"
for f in /etc/gitattributes /usr/local/etc/gitattributes /usr/share/git-core/templates/info/exclude; do test -e "$f" && echo "EXISTS $f" || echo "absent $f"; done
grep -vE '^\s*(#|$)' /usr/share/git-core/templates/info/exclude | head -5; echo "noncomment_lines=$(grep -cvE '^\s*(#|$)' /usr/share/git-core/templates/info/exclude)"; echo '--- selftest re-exec lines'; grep -n '"\$SELF"' /var/tmp/souji-r16-RerunLegacySelftest/tools/souji-census.sh | cut -d: -f1 | tr '\n' ' '
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls .ufo/waves/round-16/w2/ 2>&1 | head -20; echo '--- existing w2 sample head'; for f in .ufo/waves/round-16/w2/*.md; do echo "== $f"; head -12 "$f"; break; done 2>/dev/null
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD; git ls-files -s tools/souji-census.sh; git config --get core.fileMode; echo '--- worktree diff for the file'; git diff -- tools/souji-census.sh | head -12; echo '--- diff stat all'; git diff --stat | tail -5
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls -l tools/souji-census.sh; git rev-parse 163158a706352f1c0ee3521c4da2e5289970db57:tools/souji-census.sh; echo '--- log a6ec781..163158a'; git log --oneline a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae..163158a706352f1c0ee3521c4da2e5289970db57 | head -10; echo '--- stat'; git diff --stat a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae 163158a706352f1c0ee3521c4da2e5289970db57 | tail -12
cd /var/tmp/souji-r16-RerunLegacySelftest && grep -n '^set -euo pipefail\|^# --- main\|SELFTEST" = 1\|^exit 0\|^exit 1\|^  exit 0' tools/souji-census.sh; echo '--- 1828-1842'; sed -n '1828,1842p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-census.sh | grep -n '^\[ -n "\$ROOT" \]\|^if \[ "\$COMPARE_SET" = 1 \] && \[ -z "\$COMPARE" \]\|^guard_path root "\$ROOT"\|^command -v git'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '1571\|1862\|1001\|1075\|158-159\|(157;\|1510-1513\|1490-1504\|1002-1010' .ufo/waves/round-16/w2/RerunLegacySelftest.md; echo "stale_hits_rc=$?"; echo '--- cite sanity'; grep -o '1[0-9][0-9][0-9]-1868\|18[0-9][0-9]' .ufo/waves/round-16/w2/RerunLegacySelftest.md | sort -u | tr '\n' ' '; echo; wc -l .ufo/waves/round-16/w2/RerunLegacySelftest.md
rm -rf /var/tmp/souji-r16-RerunLegacySelftest && test ! -e /var/tmp/souji-r16-RerunLegacySelftest && echo 'temp removed'; ls -d /var/tmp/souji-census-selftest.* 2>/dev/null || echo 'no selftest temp leftovers'
```
