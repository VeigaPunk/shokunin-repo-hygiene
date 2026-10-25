# ScoutLocalHost — host facts for the C3 entries (read-only)

## Status
STATUS: PASS — all three required git man pages are installed from git 2.56.0-1, `git --version`
is 2.56.0, and one lane-only `git count-objects -v` returned `garbage: 0` / `size-garbage: 0`.
One contract-relevant caveat: the installed `git-count-objects` page contains **no** literal
"read-only" sentence, so C3's S115 quote must be the DESCRIPTION line, not a read-only claim.

## Evidence

### E1 — git version and package (host, 2026-10-25)
```
$ git --version
git version 2.56.0
$ pacman -Qo $(command -v git)
/usr/bin/git is owned by git 2.56.0-1
$ pacman -Q git
git 2.56.0-1
```

### E2 — man pages installed, with owner package/version
```
$ man -w git-count-objects git-fsck git-prune   (run per page)
/usr/share/man/man1/git-count-objects.1.gz
/usr/share/man/man1/git-fsck.1.gz
/usr/share/man/man1/git-prune.1.gz

$ pacman -Qo /usr/share/man/man1/git-count-objects.1.gz ... 
/usr/share/man/man1/git-count-objects.1.gz is owned by git 2.56.0-1
/usr/share/man/man1/git-fsck.1.gz is owned by git 2.56.0-1
/usr/share/man/man1/git-prune.1.gz is owned by git 2.56.0-1

$ ls -l /usr/share/man/man1/git-{count-objects,fsck,prune}.1.gz
-rw-r--r-- 1 root root 1102 Sep 28 14:57 git-count-objects.1.gz
-rw-r--r-- 1 root root 6233 Sep 28 14:57 git-fsck.1.gz
-rw-r--r-- 1 root root 1463 Sep 28 14:57 git-prune.1.gz
```
Renderer: `man-db 2.13.1-2` (`man --version` → `man 2.13.1`).

### E3 — `git count-objects -v`, run exactly ONCE, lane repo only
```
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin && git count-objects -v ; echo rc=$?
count: 5051
size: 35828
in-pack: 1544
packs: 3
size-pack: 8791
prune-packable: 0
garbage: 0
size-garbage: 0
rc=0

$ git rev-parse HEAD
1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd
```
Scope: `/home/vgpnk/Projects/shokunin/souji-shokunin` (the lane) and nowhere else. The fleet repo,
`.scratch/`, `.ufo/state/`, sibling lanes and the jj state were not queried.

### E4 — no `fsck --lost-found`, and no lost-found write exists
```
$ test -d .git/lost-found && echo PRESENT || echo ABSENT
ABSENT
$ git status --porcelain | wc -l
10
$ git rev-parse --is-bare-repository
false
```

## Findings

1. **Field values observed (E3), 8 lines, no `alternate:` line present:**
   `count=5051`, `size=35828` KiB, `in-pack=1544`, `packs=3`, `size-pack=8791` KiB,
   `prune-packable=0`, `garbage=0`, `size-garbage=0`. Exit code 0.
   Location: /home/vgpnk/Projects/shokunin/souji-shokunin/.git (working tree at HEAD 1208bfb).
2. **`garbage` is 0 — yes, zero.** `size-garbage` is also 0, so the object database holds no
   file that is "neither valid loose objects nor valid packs" (the page's own definition, F6
   below). There is no non-zero garbage datum to report and nothing to reconcile against
   `count`/`in-pack`.
3. **`count-objects -v` is read-only.** I state this as the operational fact: it is a census that
   prints counts and sizes, and the page's SYNOPSIS admits only `-v` and `-H | --human-readable`
   — there is no option that mutates the object database, refs, index, or working tree. My run
   changed nothing: `git status --porcelain` still shows the same 10 pre-existing paths (E4) and
   `.git/lost-found` does not exist.
   Confidence on the mechanism: high. Confidence on the *citation*: see F5 — this is
   **[INFERENCE]** from the option surface, not a sentence the page states.
4. **I ran no `fsck --lost-found`.** No `git fsck` of any form, no `git prune`, no `git gc`, no
   `git repack`, no `git pack-refs`, no `git gc --auto`-triggering command. `.git/lost-found/`
   is ABSENT in the lane repo (E4), which is the observable that would have appeared had a
   `--lost-found` run occurred. This is the distinction the round's read-only receipts rest on:
   `fsck --lost-found` writes, `count-objects -v` does not.
5. **ATTACK (narrow, on the C3 citation plan, not on a predicate).** The preregistration's C3
   re-grounding rule requires "a <=25-word located quote" per cited source, and C1's sourced
   ground cites S115/S116/S117 for "the write-side-effect distinction". The installed
   `git-count-objects` page (E2) contains **no** occurrence of "read-only" or "read only" —
   `grep -i 'read-only\|read only\|does not\|without'` over the rendered page returns nothing
   (rc=1). A C3 row that quotes S115 as *saying* it is read-only would be an unfaithful quote.
   The honest S115 quote is the DESCRIPTION sentence (F6); the read-only conclusion is ours.
   This does not require changing any predicate — it constrains what the entry may quote.
6. **Verified quote candidates** (copied this run from the rendered pages; each <=25 words, no
   `|` character):
   - git-count-objects, DESCRIPTION: "Counts the number of unpacked object files and disk space
     consumed by them, to help you decide when it is a good time to repack." (25 words)
   - git-count-objects, `-v` option, `garbage`: "the number of files in the object database that
     are neither valid loose objects nor valid packs" (18 words)
   - git-fsck, `--lost-found`: "Write dangling objects into .git/lost-found/commit/ or
     .git/lost-found/other/, depending on type." (13 words) — this is the write-side effect.
   - git-prune, `-n, --dry-run`: "Do not remove anything; just report what it would remove."
     (10 words)
   - git-fsck, DESCRIPTION: "Verifies the connectivity and validity of the objects in the
     database." (10 words)
7. **Host reproducibility datum for the C3 `## Gate`.** `git --version` 2.56.0 and package
   `git 2.56.0-1` agree, and the man pages are the packaged ones (mtime Sep 28 14:57, owned by
   that exact package), so a quote taken from these pages is bound to the installed version, not
   to a web snapshot.
8. **No install or upgrade was performed** in this seat. Nothing was added to `~/.local/bin`, no
   `uv tool`, no `npx`, no `pacman` invocation of any kind (transactions are paused host-wide
   anyway). Only `pacman -Q`/`-Qo` read queries were used, which do not touch the sync database.

## Remaining unknowns
- None for the assigned question. If a *literal* "read-only" citation is required for S115 by a
  later wave, the installed page cannot supply it and the upstream docs must be re-checked — but
  under the <=25-word rule F6's DESCRIPTION quote is the faithful alternative.
