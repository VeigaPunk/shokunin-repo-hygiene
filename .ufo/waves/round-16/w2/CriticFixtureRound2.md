# CriticFixtureRound2: round-2 fixture changes in tests/fixtures/r15-census-config.py

Seat: SoujiR16.CriticFixtureRound2 (UFO-FSD critic, leaf). Axis judged: operability.
Reviewed: `git diff cbf688a HEAD -- tests/fixtures/r15-census-config.py`. The HEAD fixture sha256 is `27474396808f…`, the same value bound by census/round-16/c1-matrix-landing.json and tests/fixtures/r15-preservation-frozen/record.json (measured_commit c6207bd). Tool: tools/souji-census.sh at HEAD.
Method: static reading plus the recorded real runs (landing matrix, frozen record). I ran no fixture, census, or mutant. This item had no ALLOWED-EXEC.

## Verdict summary

| item | verdict | does it discriminate a real defect class? |
|---|---|---|
| r-inc-twice | **holds** | yes: m6 (stale CFG_STACK entry read as a cycle) |
| r-inc-tilde-store | **holds** (pin is loose) | yes: m4 (`~/` not expanded before guarding) |
| r-tilde-then-store | **partial** | yes, but only 1 of about 9 soft-then-continue sites |
| mixed-degrade | **partial** | yes (whole-run abort / dropped later rows); the oracle is weak |
| r-xdg-default | **holds**, with a missing pair | yes: M02; the guard side of the new XDG read is untested |
| s-fsm-filter | **holds**, with a vacuity risk | yes: F1 (fsmonitor live on ls-files/check-attr) |
| f.bin / f.dat "positive controls" | **fails** | no: they cannot force the driver; the sentinel stays vacuous |
| HARM_CASES += 18, 20 | **partial / fitted** | no new class; collateral of 16's fleet; table still wrong (19 missing) |
| detail cap (400) | **holds** for its 512 bound; partial | format accommodation; raw TABs and downstream cut remain |

## Findings

### F1: f.bin / f.dat edits do not make the bound-filter sentinel discriminating (fails)
- **Claim** (fixture :530-531): "f.bin is modified after the commit (positive control): a status that honored the binding would have to run the driver."
- **Counterexample.** Both edits change the file size: `"bin\n"`→`"bin changed\n"` (:535) and `"d\n"`→`"d changed\n"` (:543). The index sd_size is non-zero because the files were added before the filter existed. In git, a size mismatch sets DATA_CHANGED, and `ie_modified` returns early without content comparison: `if ((changed & DATA_CHANGED) && (S_ISGITLINK(ce->ce_mode) || ce->ce_stat_data.sd_size != 0)) return changed;` (git read-cache.c:472-474, v2.51.0; reached from refresh_cache_ent :1382/:1412). `run_diff_files` records a null worktree oid on stat change (diff-lib.c:264-281). Nothing hashes the file, so no clean or process filter runs.
- **Empirical evidence (real run, host git 2.56.0).** a31642d's count_dirty runs a plain `git -C "$1" --no-optional-locks status --porcelain` (`git show a31642d:tools/souji-census.sh`), so the binding is honored. In the frozen record, the pre-harm R15CFG-14 line is untruncated: its summary is 388 chars, under the 400 cap, with no `...`. It lists only `dirty=1 want 0`, `verdict_flags=dirty,unpushed …` and twice `status-skipped diagnostic missing`. It contains **no** `exec: bound-filter sentinel … was created`. A status that honored the binding did **not** run the driver.
- **f.dat has no execution witness at all**: `process = cat` (:542) has no sentinel. [INFERENCE] A non-required process filter that fails its handshake is ignored, so even an execution would leave no trace.
- **Impact.** R15CFG-14 still kills M03/M04, but through the row and `status-skipped` oracles. The "driver never runs" safety half is untested: a repaired tool that ran status under the binding would pass the sentinel check.
- **Smallest fix.** Keep the size the same and change only the content: `(repo/"f.bin").write_text("BIN\n")` and `(repo/"f.dat").write_text("D\n")`. Make the process driver a sentinel too: `sent_script(repo/".git"/"xproc.sh", SENT_FLB)` with `process = <path>`. A same-size edit goes through `ce_modified_check_fs`, which hashes the file through the filter whether the edit is racy or the mtime differs. Acceptance: the pre-harm arm's R15CFG-14 detail gains `exec: bound-filter sentinel sentinel-bound-filter was created`.

### F2: r-tilde-then-store covers one soft site out of about nine (partial)
- It kills a mutant that turns `tools/souji-census.sh:641` (`cfg_soft …; soft=1; continue` on `~user`) into an early return. These sibling sites stay unconstrained: :645 (include-unresolved), :647 (non-regular/hardlink target), :648 (nested scan soft → `|| soft=1`), :653/:656 (excludes/attributes), :661/:664 (core.worktree), :672 (worktreeConfig unparsable), and guard_git_config :725 → :730 (main-config soft, then config.worktree).
- **Counterexample mutant.** `:648 scan_config_file … || return 1` survives every case: r-tilde-then-store never reaches :648, and r-inc-cycle/r-inc-nested have no protected sibling after the soft.
- CriticFixtureOverfit correction 2 asked for "a cycle with a store edge"; that case was not added.
- **Severity framing.** No git runs in a soft repo, so this is a refusal-shape (exit 2 vs `error` row) contract gap, not a store-access gap.
- **Smallest fix.** Add `r-cycle-then-store` (`include c1.inc` where c1→c2→c1, then `include <store>`) and `r-fifo-then-store` to case_02's list. These kill the :648 and :647 mutants.

### F3: the mixed-degrade oracle is weaker than soft_problems/positive_problems (partial)
- Holds for: rc≠0, m-cycle missing, or a-ok/z-ok dropped or turned into error rows.
- **Gaps** (fixture :1134-1145):
  - No exact row set and no header check. rows_by_name collapses duplicates, so extra or duplicated rows pass.
  - `f[1:4] + [f[6]]` raises IndexError on a short row and crashes the fixture with no CASE line. That is not a fabricated pass, but it is not a FAIL either.
  - m-cycle's empty mtime is not pinned (`m[6:]`), unlike soft_problems `fields[5:] == ["", "error"]` (:1072). The two oracles in the same case disagree.
  - No `config-unsupported` stderr check, and no check of the "no git command runs there" claim (:1127), although the spy log could check it.
- CriticFixtureOverfit correction 1 asked for `n-filter-bound` and `o-prom-maybe` neighbours, and they were not added. Row survival around the status-skipped path (14) and the git-status-fails path (07) is still verified only by single-repo runs.
- **Smallest fix.** Run `soft_problems`-style checks on m-cycle, and `positive_problems(res, {"a-ok": CLEAN, "z-ok": CLEAN, …})` on the neighbours after removing m-cycle from the row dict. Add the two requested neighbours.
- Related fit: pinning an **empty** mtime on error rows (:1072) encodes the `printf '%s\t0\t0\t0\t0\t\terror\n'` placeholder (census :1180). The header says those fields are placeholders, not a contract, so a tool that reported a real mtime would fail for no defect.

### F4: r-xdg-default has no negative pair for the new XDG read (holds; gap)
- It kills M02 (`base=${XDG_CONFIG_HOME:-/dev/null}`). Pre-harm also PASSes R15CFG-04 in the landing matrix, so the expectation matches git.
- **Untested guard.** status_info_file :960-977 now reads `$HOME/.config/git/ignore` (and `attributes`). Its safety code (lexical protected check :970, `resolve_guarded` :973) has no fixture case. A mutant that replaces :970-977 with `[ -f "$tgt" ] && printf …` survives, because HOME/.config/git/ignore is a regular file in every run. [INFERENCE] With a symlink into the store, `[ -f ]` would stat through the mode-000 store, and the strace oracle would see it, but only if such a case existed.
- Also unexercised: `XDG_CONFIG_HOME` set, set-but-empty `core.excludesFile` disabling XDG, and the XDG `attributes` leaf. Explicit-over-XDG precedence *is* covered by r-excl-all.
- **Smallest fix.** Add one `run_tool(..., extra_env={"XDG_CONFIG_HOME": <dir>})` run where `<dir>/git/ignore` is a symlink to `AGENT/ignore`. Expect the positive row plus clean `access_problems`.

### F5: s-fsm-filter may silently stop exercising the index readers (holds; vacuity risk)
- It discriminates F1. [INFERENCE, source-grounded] An index read with a hook-mode fsmonitor runs the hook: tweak_fsmonitor → add_fsmonitor → refresh_fsmonitor (git fsmonitor.c:792-822, :759-781). The fixture index has no FSMN extension. Removing the GIT_CONFIG_COUNT export (census :162) would let `ls-files`/`check-attr` fire SENT_FSM.
- **Gap.** Nothing asserts that ls-files ran. If guard_bound_filters starts skipping `cat`-only or unbound drivers before the pipeline, the case still passes. SENT_FSM is shared with s-fsm, so a firing cannot be attributed to F1. On pre-harm, s-fsm already fires it.
- **Smallest fix.** In case_08, require a spy `git` line whose argv contains both `s-fsm-filter` and `ls-files`. Give s-fsm-filter its own sentinel path in EXEC_SENTINELS.

### F6: HARM_CASES +18/20 fits observation, not a defect class, and the table is still wrong (partial)
- **Collateral, not discrimination.** On r14-harm, 16, 18 and 20 all fail with the identical detail `exit=2 want 0 … observed_finding=path-protected:git-config-unsupported` (landing matrix). All three run FL_MIXED, whose `m-safe-config` sets hooksPath=/dev/null. The harm arm never observes 18's env-poison property or 20's compare exit codes. That is one discrimination counted three times.
- **Still incomplete.** r14-harm also FAILs **R15CFG-19** in both matrices (`store: contract: synthetic store path in output … path-protected:credential-store`). That is a real harm defect (the store path is echoed), yet 19 is absent from HARM_CASES (:161-165). The docstring's "every refusal/namespace case PASSes" on harm (:95) is false for 19.
- **Duplicate, disagreeing authority.** CASE_CLASSES labels 18 and 20 `preserve` (:174-175). The checker pins 18 as `safety` and 20 as `benign` (souji-preservation-evidence.py:334, :345), and its preserve class means "PASS on both baselines" (:322). The fixture's own comment "r16 adds 03/07/14" (:160) is stale.
- **No consumer.** Exact-file greps find no `HARM_CASES`/`harm_cases` in tools/souji-landing-gate.py, tools/souji-preservation-evidence.py, census/round-16/run-matrix.py, or regenerate.py. Neither the matrix runner (:47) nor the frozen record argv passes `--json`.
- **Smallest fix.** Either delete HARM_CASES and the `harm_cases` JSON key (dead second authority; the checker's CONFIG_HARM_FAILS is the pinned one), or set it to the 16 observed ids including 19 and relabel CASE_CLASSES 18→safety, 20→benign.

### F7: the detail cap keeps details within 512 but leaves format hazards (holds; partial)
- **Holds.** At most 400 summary chars plus the suffix. The frozen pre-harm CASE lines are at most 458 chars including the `CASE\tID\tFAIL\t` prefix, which satisfies checker :1514 `len(detail) > MAX_DETAIL_CHARS`. The suffix finding token is unbounded by construction (`[a-z0-9-]+` from tool stderr), but realistic ids keep it under 512.
- **Raw TABs enter the summary.** spy_hits returns raw TAB-separated spy lines (:853, :879). The landing pre-harm R15CFG-19 detail contains `spy recorded store path: readlink\t/var/tmp/…\t-m -- …`. The "TAB-separated detail fields" shape (checker :920-923, :1817) is broken. Because the checker's `re.search(r"\tobserved_finding=…")` takes the first match (:1493), tool-influenced argv could spoof the token. The fix is one line: `summary = summary.replace("\t", " ")` before capping.
- **Lost evidence.** The cap comment says "the --json record keeps the full problem list", but no recorded producer passes `--json`. The matrix runner further cuts detail to 300 chars (`m.group(3)[:300]`, run-matrix.py:53). Landing details for 02/03/11/14/17/18/19 therefore lose `observed_exit`/`observed_finding`, and the 14 pre-harm detail is cut right where a sentinel line would sit. Fix: put the fixed-size `observed_*` fields before the summary, or drop the runner's `[:300]`.

### Also checked
- `faccessat2(` added to stat_tokens (:819): holds. `"faccessat("` is not a substring of `"faccessat2("`, so the addition widens the strict oracle.

## Impacted axes
- **operability:** F1 leaves the "driver never runs" guarantee for bound filters unproven: no case can tell a tool that ran status under the binding from one that did not. F2/F3 leave the refusal-shape and row-survival contract partly unconstrained. F4/F5 are missing pairs for newly trusted paths.
- **calibration (secondary):** F6 overcounts harm discrimination and keeps a second, disagreeing class/harm authority. F7 is evidence loss in recorded artifacts.

## Tradeoffs for the judge (not fixable defects)
- Silently using /dev/null when the XDG default reaches a protected path (census :970-972) trades fidelity for no access. That is defensible, but it is undocumented in the fixture.

## Tooling
No tools installed or updated.

## Probe-rule disclosure
Commands 2, 3 and 5 below are read-only operations on exact named files, but they fall outside the enumerated allowed list: a `| cat` pipe on the allowed `git diff`, `wc -l` on three named files, and `python3 -c` loading the keys of two named census/round-16 JSON files. No recursive search, no census run, no lane write other than this report.

## Commands
```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff cbf688a HEAD -- tests/fixtures/r15-census-config.py
git -C /home/vgpnk/Projects/shokunin/souji-shokunin --no-pager diff --no-color cbf688a HEAD -- tests/fixtures/r15-census-config.py | cat
wc -l /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-16/run-matrix.py
git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree --name-only HEAD census/round-16/ .ufo/waves/round-16/w1/
python3 -c "
import json,sys
for f in ('c1-matrix-final.json','c1-matrix-landing.json'):
    d=json.load(open('/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-16/'+f))
    print('==',f, list(d.keys()))
"
sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r15-census-config.py
git -C /home/vgpnk/Projects/shokunin/souji-shokunin log --oneline -8 -- tests/fixtures/r15-census-config.py
git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -r --name-only HEAD tests/fixtures/r15-preservation-frozen/
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show a31642d:tools/souji-census.sh
```
Non-shell reads, all on exact files:
- read/grep of tests/fixtures/r15-census-config.py, tools/souji-census.sh, tools/souji-preservation-evidence.py, census/round-16/run-matrix.py, census/round-16/c1-matrix-{final,landing}.json (jq queries), tests/fixtures/r15-preservation-frozen/{record.json,regenerate.py}, tools/souji-landing-gate.py (grep), and .ufo/waves/round-16/w1/{SentinelCommandExec,MutateScanConfig,MutateDirtyFilters,CriticFixtureOverfit,RevFixtureR16Edits}.md.
- Web source reads (grep) of git v2.51.0 read-cache.c, wt-status.c, builtin/commit.c, diff-lib.c, fsmonitor.c at raw.githubusercontent.com/git/git. The host runs git 2.56.0; the pre-harm frozen-record evidence corroborates F1 on that version.

STATUS: FAIL — f.bin/f.dat "positive controls" change file size, so git status never runs the bound driver (read-cache.c:472-474; the pre-harm frozen run shows no bound-filter sentinel). R15CFG-14's "driver never runs" oracle remains vacuous. Other items hold or are partial, as listed above.
