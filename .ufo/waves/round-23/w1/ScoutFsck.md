# ScoutFsck — git-fsck read/write boundary for the reachability census

STATUS: PASS — live page (https://git-scm.com/docs/git-fsck, opened 2026-10-25) and installed `man git-fsck` (git 2.56.0) agree on all four options, the default head set, and the single writing option; exactly one option writes, into `.git/lost-found/commit/` or `.git/lost-found/other/`.

## Evidence

- Lane revision at run: `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd` (detached HEAD, `git status --porcelain` = 10 paths), queried 2026-10-25T08:11:01Z.
- Live page fetched natively from `https://git-scm.com/docs/git-fsck`; page header `git-fsck last updated in 2.53.0`, version list `2.54.0 → 2.56.0 no changes`. Access date 2026-10-25.
- Installed manual: `man -w git-fsck` → `/usr/share/man/man1/git-fsck.1.gz`; `git --version` → `git version 2.56.0`. Rendered via `man git-fsck | col -bx` (485 lines, scratch copy `/var/tmp/fsck-man.txt`, removed at end of run).
- Read-only behavioural check in the lane (no writes, no `--lost-found`):
  `cd /home/vgpnk/Projects/shokunin/souji-shokunin && timeout 120 git fsck --no-dangling --no-reflogs --unreachable --no-progress`
  → `rc=0`; output tail: `unreachable tree b43fc27b25b05311433095c580a165b1a732b18e` … `unreachable tree e5ffb1167843439c39b11cce202d283bd9935a62`. `.git` mtime identical before and after (`2026-10-25 05:09:42.409876032 -0300`), and `.git/lost-found` does not exist after the run (`ls` → No such file or directory). Total unreachable count not measured (output was tailed, not counted).

## Findings

1. **`--unreachable`** — https://git-scm.com/docs/git-fsck § OPTIONS, and `/usr/share/man/man1/git-fsck.1.gz` lines 24-26:
   > "Print out objects that exist but that aren’t reachable from any of the reference nodes."
   Pure print; no repository write.

2. **`--dangling` / `--no-dangling`** — page § OPTIONS, man lines 28-30:
   > "Print objects that exist but that are never directly used (default)."
   > "--no-dangling can be used to omit this information from the output."
   Print-only. The page's `--connectivity-only` block adds: "Unreachable tags, commits, and trees will also be accessed to find the tips of dangling segments of history." — i.e. `--no-dangling` is a cost lever for the census, not a safety lever.

3. **`--no-reflogs`** — page § OPTIONS, man lines 42-46:
   > "Do not consider commits that are referenced only by an entry in a reflog to be reachable."
   Changes the head set only; no write.

4. **`--lost-found`** — page § OPTIONS, man lines 79-82:
   > "Write dangling objects into .git/lost-found/commit/ or .git/lost-found/other/, depending on type."
   Follow-on sentence (page, same paragraph): "If the object is a blob, the contents are written into the file, rather than its object name."

5. **Default head set (DESCRIPTION)** — page § OPTIONS `<object>`, man lines 18-21:
   > "git fsck defaults to using the index file, all SHA-1 references in the refs namespace, and all reflogs"
   > "(unless --no-reflogs is given) as heads."
   (`refs` is rendered monospace on the page; quote given as rendered text.) Operationally: the lane's dirty index (10 porcelain paths at base) contributes head nodes, so a census run without `--no-reflogs`/`--cache` reasoning is not a pure "reachable from refs" measurement.

6. **WHICH OPTION WRITES, AND WHERE** — **only `--lost-found`.** The page names the path pattern exactly as `.git/lost-found/commit/` or `.git/lost-found/other/`, chosen "depending on type"; blobs are materialised as file *contents*, everything else as object names. Nothing else in the page or the man page writes: `--unreachable`, `--dangling`/`--no-dangling`, `--no-reflogs`, `--root`, `--tags`, `--cache`, `--full`/`--no-full`, `--strict`, `--verbose`, `--connectivity-only`, `--name-objects`, `--references`/`--no-references` (runs read-only `git refs verify`) and the default `core.commitGraph` inspection (`git commit-graph verify`) are read paths. `--progress` writes to the **standard error stream** only, never the object database. [INFERENCE] With `GIT_DIR` set elsewhere the pattern generalises to `$GIT_DIR/lost-found/{commit,other}/`; the page itself names only the `.git/...` form.

7. **Installed man agrees — verdict: AGREES, no drift.** All four option blocks and the default-head paragraph match the live page word for word (modulo man's hyphenation and double-spacing: "re‐flog", "corre‐sponding", and the line-wrapped `.git/lost-found/commit/     or`). Version reconciliation: installed 2.56.0, page last updated 2.53.0, and the page's own changelog says `2.54.0 → 2.56.0 no changes` — so the installed manual cannot be behind on this command. No page-only or man-only clause found.

8. **Consequence for the census (may / may not).** MAY run: the default form plus `--unreachable`, `--no-dangling`, `--no-reflogs`, `--connectivity-only`, `--no-progress` — read-only, demonstrated by the unchanged `.git` mtime and the absent `.git/lost-found` in Finding 0/Evidence. MAY NOT run under the round's read-only receipts: `--lost-found`, in any spelling, because it creates `.git/lost-found/commit/` and `.git/lost-found/other/` inside the repository under measurement. This is the write-side-effect distinction the preregistration cites as its sourced ground for S115/S116/S117.

9. **Cross-reference (not a claim of this item):** `corpus/SOURCES.md` max row is `S114` (line 134, statx); no `S115`-`S117` rows exist yet, so the fsck row this report grounds is still to be appended by the scribe under the preregistration's id assignment. Quote cells here contain no literal or escaped `|`.

## Attack log

None. The frozen predicates were not exercised by this item; no counter was re-run and nothing in the preregistration was edited.
