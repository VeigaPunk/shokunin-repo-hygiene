# r12 executor (re-dispatch) — K3/K4/K5 verification notes

Author: W2RoundSouji-8.R12ExecFs2 (L2, read-only); transcribed verbatim by the L1 from its final output (session-scoped `agent://W2RoundSouji-8.R12ExecFs2`; this committed copy is the durable form). 2026-10-19.

I wrote K3, K4 and K5 into `corpus/knowledge/` in the lane worktree (40, 44 and 39 lines; all untracked, nothing staged or committed). Each starts with `source:`/`verified-at:`/`recheck:` and has Claim, Evidence, Failure cases (Q3), Lane link and Limits. I ran the three `recheck:` commands on the host and they returned the expected values: K3 `1 1 1`, K4 `1` on all six lines, and K5 the device lines, `1`, `2`, EXDEV, `no-copy-exit=1`, `2`. I removed my scratch dir `/var/tmp/souji-r12-MTLlax` and both fixture dirs, and checked that none are left.

**Correction to the reviewer's fclones note.** It is right about the code in `dedupe.rs`: non-regular files are skipped at :814-824, files whose length changed are skipped at :826-841, and the whole group is aborted only inside `if let Some(..) = config.modified_before` at :843-847. But I fetched `main.rs` and `config.rs` (fclones main @ a74f90d, 2025-03-03), and `main.rs:184-185` sets `modified_before` to the report header's timestamp when none is given. So through the CLI, the group abort is on by default. Also, fclones never re-hashes or byte-compares at act time; it only checks file type, length and mtime. K3 records both facts.

**Per-quote verification**
- **rmlint.1.rst**
  - :28 "WILL NOT DELETE ANY FILES": agree.
  - The default algorithm is blake2b (:150); I added that.
  - `-p` byte-by-byte is at :191-194: agree.
  - `-k` (:431-435) and `-m` (:437-440): agree.
- **rmlint Cautions:** agree with all of these.
  - Path Doubles: `fdupes -r -H --delete --noprompt dir dir` → "Oh dear, our file is gone!"
  - Symlinks: `ln -s dir link`, then fdupes empties `dir/`.
  - Hardlinks: rdfind `-makehardlinks` on `dir dir` empties it.
  - Collision: an MD5 pair makes `rmlint -a md5` schedule an `rm`.
  - Holding area: "Rather than deleting duplicates, consider moving them to a holding area or trash folder."
- **jdupes README:** :249-251 TOCTTOU agree, with the quote extended to :253 ("checks immediately before scanning or taking action"). :320-324 `-Q`: agree.
- **fdupes.1:** `-D` :102-104, `-I` :116-118, `--log` :131-132 and CAVEATS :163-181 all agree. The man page has no version string; the version comes from the ART row.
- **fclones README:** `--dry-run` :22 and :286-287, and group → remove/move/link at :243-244: agree.
- **Trash spec:** agree with all of these.
  - The page header reads "Publication Date: 2014-01-02, Version: 1.0".
  - §5: "MUST check that this directory is not a symbolic link".
  - §6: info file first; the spec's own text says "Unix-line systems … opening with O_EXCL".
  - §6: "must not overwrite a previous copy" and "emergency case".
  - Layout: `Path=` / `DeletionDate=`.
- **trash-cli README:** commands at :14-18 and the FAQ "You can but you shouldn't" (:122-130): agree.
- **coreutils mv:** the copy-then-remove quote and the split-move quote agree. I added `--no-copy`, which fails with a diagnostic instead of copying.
- **coreutils rm:** `--one-file-system` and `--preserve-root=all` agree with both the manual and host `rm --help` (coreutils 9.11).
- **Lane lines:**
  - PROVINCE.md:12 "duplicate configs"; SKILL.md:19-23 receipt table; SKILL.md:67-70 `cmp` drift.
  - census/round-10/S06-cluster-C-member2.md:53-63; LOG.md:445 and :447-451 (Trash emptied); LOG.md:373-378 (staging hang).
  - scout-surfaces.md:94 and :100-101.
  - `tools/souji-quarantine.sh`: :478 collision refusal, :536 plain `mv`, :576 `rm -rf`, :1111 symlink containment check.

**K5 fixture output, verbatim** (`$D` is the `/var/tmp` mktemp dir, `$S` the `/dev/shm` one):
```
== versions
mv (GNU coreutils) 9.11
strace -- version 7.0
7.2.3-arch1-3
== devices (stat -c '%d %m %n')
31 / /var/tmp
31 / /var/tmp/souji-k5-Apk7DH
30 /home /home/vgpnk/Projects/shokunin/.tower/worktrees/kaika/souji-shokunin
57 /tmp /tmp
33 /dev/shm /dev/shm/souji-k5-xgBlAy
== same-fs: mv /var/tmp/souji-k5-Apk7DH/a/f -> /var/tmp/souji-k5-Apk7DH/b/f
renameat2(AT_FDCWD, "$D/a/f", AT_FDCWD, "$D/b/f", RENAME_NOREPLACE) = 0
+++ exited with 0 +++
exit=0
$D/a:

$D/b:
f
== cross-device: mv /var/tmp/souji-k5-Apk7DH/b/f -> /dev/shm/souji-k5-xgBlAy/f
renameat2(AT_FDCWD, "$D/b/f", AT_FDCWD, "$S/f", RENAME_NOREPLACE) = -1 EXDEV (Invalid cross-device link)
unlinkat(AT_FDCWD, "$S/f", 0) = -1 ENOENT (No such file or directory)
unlinkat(AT_FDCWD, "$D/b/f", 0) = 0
+++ exited with 0 +++
exit=0
src left: 0  dst: f
== cross-device with --no-copy: mv --no-copy /dev/shm/souji-k5-xgBlAy/f -> /var/tmp/souji-k5-Apk7DH/b/f
mv: cannot move '$S/f' to '$D/b/f': Invalid cross-device link
exit=1
src still: f  dst: 0
residue: 0
```
The entry's own recheck run gave: `31 / /var/tmp`, `57 /tmp /tmp`, `33 /dev/shm …`, `1`, `2`, `mv: cannot move … Invalid cross-device link`, `no-copy-exit=1`, `2`.

**What the integrator should know**
- **Not run:** no dupe finder (none is installed), no `gio trash` or `trash-put`, and no write under `/home`. The operator-sweep hang link stays [INFERENCE]: those moves went into `.ufo-quarantine/` inside the same repo.
- **`/home` vs `/var/tmp`:** both sit on the same btrfs device but report device numbers 30 and 31, so a move between them should go through copy-then-delete. That is [INFERENCE]; I didn't test it because fixtures can't write to `/home`.
- **K5 and Q4:** the cross-device demo uses `/dev/shm`, which is outside Q4's `/var/tmp`-only rule. You allowed it for this demo, and K5's Limits says so.
- **Operator decisions, named as such in the entries:** a `duplicate` receipt class (K3), trashinfo-style quarantine records (K4), and `--no-copy` / `--one-file-system` in `souji-quarantine.sh` (K5).
- **Checks to run:**
  - `wc -l corpus/knowledge/*.md` (each entry ≤60 lines)
  - `head -3` on each entry (header lines)
  - each entry's `recheck:` line
