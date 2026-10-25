# SwarmExecutor06 — Exec-C2AppendBlock (SOURCES S212–S214 append block)

## Status
STATUS: PASS — normalized fleet-schema SOURCES append block for S212 (open()) / S213 (rename()) / S214 (fsync()) built in scratch, inserted into a lane mirror (corpus/ + admitted knowledge files + tools/souji-size-census.py), and `sources-census.sh validate` on the mirror exits 0 (35 pre-existing W04 warnings only; zero E findings; none touching S212–S214). Registry rows 135 → 138 in the mirror. Lane untouched except this report file.

## Evidence
- Mirror built at `/var/tmp/souji-r28-ExecC2AppendBlock/mirror` (`git init`; `git -C <mirror> rev-parse --show-toplevel` = `/var/tmp/souji-r28-ExecC2AppendBlock/mirror`) by copying the lane `corpus/` (base 3a2a80d0d18940a5e352ebc526da22a57dad83c4), then placing staged entries `corpus/knowledge/origin-record-exclusivity-r28.md` and `origin-record-durability-r28.md` from `/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/` and `tools/souji-size-census.py` from the lane (fixes E11 on inherited S120/S122 used-by).
- Row count check: `grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' <mirror>/corpus/SOURCES.md` → `138`; `grep -n '^| S21[234] '` → NF=13 for each new row (11 columns, no literal/escaped `|` in any cell; verified via `awk -F'|'` = 13 fields).
- POSIX pages re-opened today (2026-10-25) into scratch: `open.html` (sha256 57b770918aa3e0c25186972675df8c96da119cf4b973335ed4487405e260dc3a), `rename.html` (06671610134b0a52cdf4dcdaf382f72fef85ef51088b8a52b8679c7f03829318), `fsync.html` (5c2975abbb2d65fcad92a4da5241f4f4001f0e5d8cf57f752d9486073ca49747). Located quotes (text line numbers from stripped page text): open O_EXCL “If O_CREAT and O_EXCL are set, open() shall fail if the file exists.” (L69, § DESCRIPTION); rename “If the rename() function fails for any reason other than [EIO], any file named by new shall be unaffected.” (L53, § DESCRIPTION) and “That specification requires that the action of the function be atomic.” (L176, § RATIONALE); fsync “all data up to the time of the fsync() call is recorded on the disk” (L50) and “It is explicitly intended that a null implementation is permitted.” (L54, § RATIONALE). All ≤25 words; no pipes.
- Gate command and result:
  `$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file /var/tmp/souji-r28-ExecC2AppendBlock/mirror/corpus/SOURCES.md; echo rc=$?` → rc=0; output tail line `file	ok	/var/tmp/souji-r28-ExecC2AppendBlock/mirror/corpus/SOURCES.md`; W04 count = 35 (all inherited lane rows S035–S210; none from S212–S214); `grep -E $'\tE[0-9]+\t'` → none.

## Append block (exact rows inserted after S211 in the mirror Registry)
```
| S212 | IEEE Std 1003.1-2024 (POSIX.1-2024) · open() — https://pubs.opengroup.org/onlinepubs/9799919799/functions/open.html | spec | A | the guarantee POSIX gives for exclusive creation of a per-item origin record: creating a file with O_CREAT and O_EXCL both set is atomic against a concurrent creator, and a second creator sees EEXIST; not the record's content or format (S022/S146/S152 hold those) and not rollback discipline | § DESCRIPTION O_EXCL entry, § ERRORS [EEXIST], § RATIONALE atomicity; IEEE Std 1003.1-2024 / The Open Group Base Specifications Issue 8; snapshot census/round-28/sources/open.html | exclusive creation is atomic, so a per-item origin record needs no lock to stay unique: with O_CREAT and O_EXCL set, open() fails when the name exists, the existence check and creation are one atomic step, and an already-existing name is detectable as EEXIST rather than silent | mined | 2026-10-25 | 365d | corpus/knowledge/origin-record-exclusivity-r28.md, corpus/knowledge/origin-record-durability-r28.md |
| S213 | IEEE Std 1003.1-2024 (POSIX.1-2024) · rename() — https://pubs.opengroup.org/onlinepubs/9799919799/functions/rename.html | spec | A | the guarantee POSIX gives for publishing a per-item record: rename is atomic and a failed rename leaves the target untouched; not exclusive creation (S212) and not the record's format | § DESCRIPTION failure clause, § RATIONALE atomicity clause; IEEE Std 1003.1-2024 / The Open Group Base Specifications Issue 8; snapshot census/round-28/sources/rename.html | rename is atomic and a failed rename leaves the target untouched: the specification requires the action of the function to be atomic, and if rename() fails for any reason other than EIO any file named by new shall be unaffected, so a receipt written privately and renamed into place cannot leave a half-written record visible | mined | 2026-10-25 | 365d | corpus/knowledge/origin-record-exclusivity-r28.md, corpus/knowledge/origin-record-durability-r28.md |
| S214 | IEEE Std 1003.1-2024 (POSIX.1-2024) · fsync() — https://pubs.opengroup.org/onlinepubs/9799919799/functions/fsync.html | spec | A | the durability half of publishing a per-item origin record: what the specification can and cannot promise about a record surviving a crash, and why atomicity alone does not give it; not exclusive creation (S212) and not the record's format | § DESCRIPTION, § RATIONALE null-implementation sentence; IEEE Std 1003.1-2024 / The Open Group Base Specifications Issue 8; snapshot census/round-28/sources/fsync.html | atomicity is not durability: fsync() forces queued data out and is intended to assure that after a system crash or other failure all data up to the time of the call is recorded on the disk, but a null implementation is explicitly permitted, so a record's crash-safety is bounded by the platform's guarantee and cannot be asserted from the record's own structure | mined | 2026-10-25 | 365d | corpus/knowledge/origin-record-durability-r28.md |
```

## Census output (validate, paste)
```
file	W04	S035 duplicate url git-scm.com/docs/git-repo across scopes
file	W04	S036 duplicate url git-scm.com/docs/git across scopes
file	W04	S038 duplicate url www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html across scopes
file	W04	S049 duplicate url git-scm.com/docs/git across scopes
file	W04	S057 duplicate url git-scm.com/docs/git-config across scopes
file	W04	S058 duplicate url git-scm.com/docs/git-worktree across scopes
file	W04	S059 duplicate url git-scm.com/docs/gitattributes across scopes
file	W04	S063 duplicate url git-scm.com/docs/git-gc across scopes
file	W04	S065 duplicate url www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html across scopes
file	W04	S072 duplicate url www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html across scopes
file	W04	S073 duplicate url man7.org/linux/man-pages/man2/kill.2.html across scopes
file	W04	S075 duplicate url man7.org/linux/man-pages/man5/proc_pid_stat.5.html across scopes
file	W04	S076 duplicate url man7.org/linux/man-pages/man5/proc_pid_exe.5.html across scopes
file	W04	S077 duplicate url man7.org/linux/man-pages/man2/open.2.html across scopes
file	W04	S086 duplicate url man7.org/linux/man-pages/man5/proc_pid_fd.5.html across scopes
file	W04	S087 duplicate url man7.org/linux/man-pages/man5/proc_pid_wchan.5.html across scopes
file	W04	S088 duplicate url man7.org/linux/man-pages/man5/proc_pid_status.5.html across scopes
file	W04	S089 duplicate url git-scm.com/docs/git across scopes
file	W04	S090 duplicate url git-scm.com/docs/git-filter-branch across scopes
file	W04	S091 duplicate url git-scm.com/docs/git-rev-parse across scopes
file	W04	S092 duplicate url git-scm.com/docs/git-for-each-ref across scopes
file	W04	S093 duplicate url git-scm.com/docs/git-diff across scopes
file	W04	S094 duplicate url www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html across scopes
file	W04	S095 duplicate url man7.org/linux/man-pages/man5/proc_pid_fd.5.html across scopes
file	W04	S096 duplicate url man7.org/linux/man-pages/man5/proc_pid_fd.5.html across scopes
file	W04	S097 duplicate url git-scm.com/docs/git-filter-branch across scopes
file	W04	S098 duplicate url www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html across scopes
file	W04	S099 duplicate url git-scm.com/docs/git-rev-parse across scopes
file	W04	S106 duplicate url docs.python.org/3/library/json.html across scopes
file	W04	S108 duplicate url docs.python.org/3/builtins/exceptions.html across scopes
file	W04	S123 duplicate url git-scm.com/docs/git-worktree across scopes
file	W04	S124 duplicate url git-scm.com/docs/gitrepository-layout across scopes
file	W04	S125 duplicate url git-scm.com/docs/git across scopes
file	W04	S126 duplicate url git-scm.com/docs/git-worktree across scopes
file	W04	S210 duplicate url raw.githubusercontent.com/GNOME/glib/2.84.0/gio/glocalfile.c across scopes
file	ok	/var/tmp/souji-r28-ExecC2AppendBlock/mirror/corpus/SOURCES.md
```
rc=0.

## Findings
1. Exec C2 row ids S212/S213/S214 are unused in the lane registry (grep over lane `corpus/SOURCES.md` confirms no S212+ rows; tail is S211), so the block appends cleanly; mirror count 135→138 matches the frozen counter.
2. Campaign-schema → fleet-schema deltas applied: fleet anchors name snapshot paths `census/round-28/sources/{open,rename,fsync}.html` matching Exec-C2Slice's snapshot naming; `opened=2026-10-25` (re-grounded today); `recheck=365d` bare cadence; used-by exactly the two admitted entries for S212/S213, durability entry only for S214; all escaped pipes from campaign cells (e.g. `O_CREAT\|O_EXCL`, `curl ... \| grep`) rewritten without pipes (NF=13, E01 clean).
3. E11 on S120/S122 (`tools/souji-size-census.py`) is a mirror-artifact of copying only `corpus/`; fixed by adding the lane tool into the mirror; the lane registry at base carries the same used-by but the lane has the tool, so the lane itself is unaffected. Not a row defect.
4. W04 warnings (35) are all inherited from lane rows S035–S210; none involve S212–S214; they are warnings, allowed (exit 0).
5. `posix-quotes.tsv` is absent from the lane (`census/round-28/records/` has no such file); notified SwarmScribe21 with S212/S213/S214 row facts and same-day fetched quote/digest data.

## Attack log
None — this item is not an attack; no frozen predicate/target/counter challenged.

## Tooling record
No tools installed (curl, git, gawk preinstalled; `RULES.md` read; no pacman transaction attempted).
