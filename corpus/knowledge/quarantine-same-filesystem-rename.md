source: S025 https://www.gnu.org/software/coreutils/manual/html_node/mv-invocation.html (para 3 "To move a file, mv ordinarily simply renames it…"; `--no-copy`); S024 https://www.gnu.org/software/coreutils/manual/html_node/rm-invocation.html (`--one-file-system`, `--preserve-root[=all]`, Warning on recovery); host `/usr/bin/mv --help`, `/usr/bin/rm --help`; fixture run 2026-10-19 (Evidence)
verified-at: 2026-10-19; GNU coreutils 9.11 (`/usr/bin/mv --version`), strace 7.0, kernel 7.2.3-arch1-3; manual pages sha256 mv e106679f…, rm 2ce751f1…
recheck: bash -c 'd=$(mktemp -d /var/tmp/souji-k5-XXXXXX); s=$(mktemp -d /dev/shm/souji-k5-XXXXXX); trap "rm -rf -- $d $s" EXIT; stat -c "%d %m %n" /var/tmp /tmp "$s"; mkdir "$d/a" "$d/b"; echo x >"$d/a/f"; strace -e trace=rename,renameat,renameat2,unlink,unlinkat mv "$d/a/f" "$d/b/f" 2>&1 | grep -c "rename.*= 0$"; strace -e trace=rename,renameat,renameat2,unlink,unlinkat mv "$d/b/f" "$s/f" 2>&1 | grep -cE "EXDEV|unlinkat\(AT_FDCWD, \"$d/b/f\", 0\) = 0"; mv --no-copy "$s/f" "$d/f"; echo no-copy-exit=$?; /usr/bin/rm --help | grep -c -e --one-file-system -e "preserve-root\[=all\]"'   # expect: devices, 1, 2, "Invalid cross-device link", no-copy-exit=1, 2

# Quarantine staging is a rename only on one file system; across devices mv copies then unlinks

## Claim
- GNU `mv` first tries `renameat2(…, RENAME_NOREPLACE)`. Same device: one syscall, nothing copied. Different device: the rename fails EXDEV, `mv` copies (as `cp -a`) and then unlinks the source, exiting 0 in both cases; the caller cannot tell which path ran from the exit status.
- A failed multi-source cross-device move can be left split between the two file systems (manual).
- `mv --no-copy` turns the cross-device case into a hard failure (exit 1, source untouched): a fail-closed guard for staging.
- `rm --one-file-system` skips directories on another file system during recursive removal; `rm --preserve-root=all` rejects any argument on a separate device from its parent.
- So a quarantine root gives atomic staging only when `stat -c %d` of target and quarantine root are equal.

## Evidence
- S025 mv: "To move a file, mv ordinarily simply renames it. However, if renaming does not work because the destination's file system differs, mv falls back on copying as if by cp -a, then (assuming the copy succeeded) it removes the original." — agree.
- S025 mv: "If you were to copy three directories from one file system to another and the copy of the first directory succeeded, but the second didn't, the first would be left on the destination file system and the second and third would be left on the original file system." — agree.
- S025 `--no-copy`: "If a file cannot be renamed because the destination file system differs, fail with a diagnostic instead of copying and then removing the file."
- S024 rm `--one-file-system`: "When removing a hierarchy recursively, do not remove any directory that is on a file system different from that of the corresponding command line argument." Host `rm --help`: "skip any directory that is on a file system different from that of the corresponding command line argument".
- S024 `--preserve-root[=all]`: "When 'all' is specified, reject any command line argument that is not on the same file system as its parent." Host: "with 'all', reject any command line argument on a separate device from its parent". — agree.
- S024 Warning: "If you use rm to remove a file, it is usually possible to recover the contents of that file."
- FIXTURE (scratch-only script, not committed; `recheck:` is its self-contained equivalent): `mktemp -d /var/tmp/souji-k5-XXXXXX` + `/dev/shm/souji-k5-XXXXXX`, trap-removed, residue count after run 0. Output lines verbatim; headers, version lines, `ls` listing and strace `+++ exited with 0 +++` markers dropped; `$D`/`$S` substituted by the script:
```
31 / /var/tmp
31 / /var/tmp/souji-k5-Apk7DH
30 /home /home/vgpnk/Projects/shokunin/.tower/worktrees/kaika/souji-shokunin
57 /tmp /tmp
33 /dev/shm /dev/shm/souji-k5-xgBlAy
renameat2(AT_FDCWD, "$D/a/f", AT_FDCWD, "$D/b/f", RENAME_NOREPLACE) = 0
exit=0
renameat2(AT_FDCWD, "$D/b/f", AT_FDCWD, "$S/f", RENAME_NOREPLACE) = -1 EXDEV (Invalid cross-device link)
unlinkat(AT_FDCWD, "$S/f", 0) = -1 ENOENT (No such file or directory)
unlinkat(AT_FDCWD, "$D/b/f", 0) = 0
exit=0
src left: 0  dst: f
mv: cannot move '$S/f' to '$D/b/f': Invalid cross-device link
exit=1
src still: f  dst: 0
```

## Failure case (Q3)
- The manual's split multi-directory move (above). Fixture shows the window: after EXDEV the source survives until the final `unlinkat`, so an interrupted cross-device staging leaves a partial copy plus the original [INFERENCE: copy syscalls were not traced].

## Lane link
- census/round-12/scout-surfaces.md:94: lane worktree, all 21 `*-shokunin` repos, `$HOME/.souji-quarantine`, `~/.local/share/Trash` = device 30 (`/home`); `/var/tmp` = 31; `/tmp` = 57. :100-101: `/home` and `/` are the same btrfs block device yet report different `%d`, so a `/home`→`/var/tmp` move would hit the copy path [INFERENCE: not run; fixtures may not write /home].
- tools/souji-quarantine.sh (sha256 141c0fdc…) stages inside the target repo (`<repo>/.ufo-quarantine/<utc-date>/`, :42-45) with plain `mv --` (:536) or `git mv` (:529), and deletes with `rm -rf --` (:576): no `--no-copy`, no `--one-file-system`. Same-repo staging is a rename unless a mount or symlink intervenes. Adding either flag is a tool change: OPERATOR DECISION.
- Operator-sweep hang (LOG.md:373-378: staging "hung", 2 files missing after the timeout): those moves went into `.ufo-quarantine/` inside the fleet root, i.e. same repo; whether any crossed a device is unknown [INFERENCE, unverified].

## Limits
- Fixture is one regular file on tmpfs (`/dev/shm`) vs btrfs (`/var/tmp`); directory trees, xattrs, and interrupted copies were not exercised. `/dev/shm` is outside Q4's `/var/tmp`-only rule; used solely as the second device, created and removed by the fixture.
