# SwarmExecutor08 — round 28 w1 report (S119 zh-Hans git-fetch edition disposal)

## Status
STATUS: PASS — staged S119 (zh-Hans git-fetch(1) edition) disposed with a decision-time pin: live snapshot opened 2026-10-25, byte-exact record installed and sha256-pinned, Chinese quote located, decision ADMIT as row snippet S215; decision + evidence written to `census/round-28/records/s119-disposition.tsv`. No package bytes edited; no lane files outside the three named delivery files touched.

## Evidence
1. Fetch (today, decision-time pin):
   - Command: `curl -sSL --fail --compressed -A "Mozilla/5.0 ..." -o /var/tmp/souji-r28-SwarmExecutor08/git-fetch-zh-HANS-CN.html -w ...` https://git-scm.com/docs/git-fetch/zh_HANS-CN
   - Output: `http=200 final=https://git-scm.com/docs/git-fetch/zh_HANS-CN size=26215 type=text/html; charset=utf-8`; bytes=156713.
   - Page stamp: `git-fetch last updated in 2.56.0` (present), `<html lang="zh_HANS-CN"` (present).
2. Snapshot installed + pinned:
   - `cp -p` scratch → `census/round-28/sources/git-fetch-zh-HANS-CN.html` (lane), then `sha256sum`:
   - `a7f4742d99fd515f1811aabd830a61840939ebe3e12cf1e6792662181b574042  /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-28/sources/git-fetch-zh-HANS-CN.html` (matches scratch bytes).
   - `census/round-28/sources/SHA256SUMS` written (same hash, filename `git-fetch-zh-HANS-CN.html`).
3. Quote (verbatim visible text from snapshot bytes, parsed this run; § OPTIONS of the zh-Hans page; whitespace tokens = 12 ≤ 25):
   - `--auto-maintenance --no-auto-maintenance 在最后运行 git maintenance run --auto，以在需要时执行自动仓库维护。（与 "--[no-]auto-gc" 选项效果一样。）这个功能默认启用。`
   - Chinese default statement: `这个功能默认启用。` = this feature is enabled by default.
4. Decision record written: `census/round-28/records/s119-disposition.tsv` (header + one row for S215; fields: id, decision, opened, url, snapshot, sha256, quote, reason, flip).
5. Lane state checked read-only `git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain=v1 --untracked-files=all`: my three delivery files present (`?? census/round-28/records/s119-disposition.tsv`, `?? census/round-28/sources/SHA256SUMS`, `?? census/round-28/sources/git-fetch-zh-HANS-CN.html`); also visible mid-wave: peer-created round-28 files (`.gitignore`, `c1-counter.sh`, `q57-sites.txt`, records), tracked r26 w1 mods (C3 revert scope, another seat), `M corpus/QUALITY.md` (another seat). My report file is not listed because a peer's new `.gitignore` already excludes `.ufo/waves/`. `corpus/SOURCES.md` untouched (appending S215 is the L1 integrator's step; prereg C2 counts only S212–S214, S119-derived row excluded).

## Findings
1. Staged row location: `merge/souji/SOURCES.append.md:17` — S119, git-fetch(1) Chinese edition, `https://git-scm.com/docs/git-fetch/zh_HANS-CN`, docs/A, opened 2026-10-23, teaches: switch default-on in the project's own Simplified Chinese edition.
2. Prior reject reason (round-26 lesson `round-26-verifier-spotcheck.md:47`) was "version alignment unprovable, build stamps ambiguous"; the verifier already noted the page then carried "git-fetch last updated in 2.56.0" and the switch. Today's decision-time pin resolves the mirror-state concern: HTTP 200, final URL identical, page stamp `2.56.0` (matches host git 2.56.0), byte-exact snapshot + sha256.
3. ADMIT per assignment schema: row snippet S215, 11-col schema, kind=docs, tier=A, scope=zh-Hans edition corroborating S128's switch for Chinese readers, status=mined, opened=2026-10-25, recheck=on-release, used-by=`corpus/knowledge/git-auto-maintenance-trigger-set.md` (admitted entry exists in lane; kill-rule safe).
4. Flip condition recorded: later zh-Hans release drops the switch or changes the default → recheck on-release covers; then REJECT with reason in the lesson Gate.
5. Counter impact: prereg C2 counts registry rows 135→138 for the three POSIX rows (S212–S214) only; S215 (from staged S119) is explicitly excluded from that counter, consistent with the disposition record being the delivery and `corpus/SOURCES.md` append left to the L1 integrator.
6. Tooling: no installs this run (curl present; used for the fetch). Scratch `/var/tmp/souji-r28-SwarmExecutor08/` held snapshot copy; removed at close. No pacman, no credentials, no /proc census, no `.scratch/` read, no `agent://all`.

## Attack log
None — item is a disposition, not an attack; no counter/predicate found wrong.
