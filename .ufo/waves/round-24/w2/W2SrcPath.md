# W2SrcPath — S120/S121 (git.git path.c at v2.56.0 / v2.30.0) re-opened live

## Status
STATUS: PASS — every quote, line number, tag commit and snapshot hash in S120/S121 and the entry survives against live bytes. Two findings: one range-label mismatch in the entry header, and one unstated precondition in the census rule (item 7). Neither affects the tool or any C1 counter.

## Evidence
Revisions: lane tip `c3ca7ad3f8722d5e92ba350e49b4ebb96e8bface` (not ca7fc1c: the wave-1 reports commit landed on top). `git diff --stat 778747e master -- corpus/SOURCES.md corpus/knowledge/count-objects-linked-worktree-garbage.md census/round-24/sources tools/souji-size-census.py` printed nothing, so the attacked bytes are the after-state's bytes. Host git 2.56.0. Scratch /var/tmp/souji-r24-W2SrcPath (removed).

1. Snapshots: `cd census/round-24/sources && sha256sum -c SHA256SUMS` → all 6 `OK`. `git cat-file -p {master,778747e}:census/round-24/sources/git-v2.{56,30}.0-path.c | sha256sum` gives the same hashes as the working tree.
2. Live raw: `curl https://raw.githubusercontent.com/git/git/{v2.56.0,v2.30.0}/path.c` → 200 at both tags. sha256 `f98ba3446d76…5d21d2` (v2.56.0) and `7c5b07107804…c62d4a` (v2.30.0). Both are byte-equal to the snapshots and match the row prefixes and suffixes `f98ba344…21d2` and `7c5b0710…2d4a`.
3. Live blob URLs: `curl https://github.com/git/git/blob/{v2.56.0,v2.30.0}/path.c` → 200 at both tags. The page's embedded `rawLines` array equals the raw file line for line: v2.56.0 has 1657 lines, `equal True`; v2.30.0 has 1538 lines, `equal True`. So the line numbers on the blob URL are the raw line numbers.
4. Tag commits: `git ls-remote https://github.com/git/git.git` returned `a018953688f1b10bddf91bff8747068f5f4746a4 refs/tags/v2.56.0^{}` and `71ca53e8125e36efbda17293c50027d31681a41f refs/tags/v2.30.0^{}`. Both match the rows and the entry's short ids.
5. Per-line checks (v2.56.0 / v2.30.0), all matching:
   - struct: L89 / L101 `struct common_dir {`; the struct runs through L96 / L108.
   - Comment: L90 / L102 "Not considered garbage for report_linked_checkout_garbage".
   - Table: L98 / L110 `static struct common_dir common_list[] = {`, closing `};` at L124 / L136.
   - Table rows:
     - info L102 `{ 0, 1, 1, "info" },`
     - info/sparse-checkout L103 `{ 0, 0, 0, "info/sparse-checkout" },`
     - logs L104 / L116 `{ 1, 1, 1, "logs" },`
     - logs/HEAD L105 / L117 `{ 1, 0, 0, "logs/HEAD" },`
     - logs/refs/* L106-108 / L118-120, flag 0
     - refs L111 / L123 `{ 0, 1, 1, "refs" },`
     - refs/bisect, refs/rewritten, refs/worktree L112-114 / L124-126, flag 0
     - gc.pid L120 / L132 `{ 1, 0, 1, "gc.pid" },`
   - Sweep: L365 `void report_linked_checkout_garbage(struct repository *r)` / L376 `void report_linked_checkout_garbage(void)`. The function closes at L385 / L396.
   - Early return: L371 `if (!r->different_commondir)` / L382 `if (!the_repository->different_commondir)`.
   - Walk: L375-383 (the report call is at L382 / L393).
6. Byte-identity claim (S121 teaches column):
   - `diff <(sed -n 89,124p v2.56.0) <(sed -n 101,136p v2.30.0)` → `IDENTICAL`.
   - The sweep diff is exactly 3 lines: the signature `(struct repository *r)` versus `(void)`, `r->different_commondir` versus `the_repository->different_commondir`, and `r->gitdir` versus `get_git_dir()`. The claim "differs only in signature and repository access" holds.
7. Entry gate ADMIT quotes from path.c: L90 (v2.30.0 L102), `{ 0, 1, 1, "refs" },` L111 and L123, `{ 0, 1, 0, "refs/bisect" },` L112, `{ 0, 1, 0, "refs/worktree" },` L114, and logs/refs/worktree L108. All are byte-exact at those lines.
8. Probe for Finding 2. The repo was a throwaway one under /var/tmp, with `env -i` and git 2.56.0:
   - `git -C wt count-objects -v` read `garbage: 1` (`.../worktrees/wt/refs`).
   - `git --git-dir=$C count-objects -v` read `garbage: 0`.
   - `GIT_COMMON_DIR=$C git --git-dir=$C count-objects -v` read `garbage: 6` (hooks, info, objects, refs, worktrees, config).
   - `python3 -B tools/souji-size-census.py --repo <wt>` printed `garbage=0 size_garbage=0 unreachable=0 alternates=0` with exit 0, both without and with `GIT_COMMON_DIR=$C` exported.

## Findings
1. **Range-label mismatch (low).** `corpus/knowledge/count-objects-linked-worktree-garbage.md` line 2 reads "line 101-136 (common_list)". In S121, L101-108 is `struct common_dir` and `common_list[]` is L110-136, as the S121 row itself says ("struct common_dir L101-108; common_list[] L110-136"). The range bytes are right but the label is not. It is also inconsistent with line 1's S120 label, "line 89-124 (struct common_dir, common_list)". The fix is a label edit only.
2. **Unstated precondition in the census rule (medium, entry only).** Entry item 7 (lines 80-87) says the private-gitdir sweep never runs against the common dir and cites "S120 line 371". It also says "The rule is exact for every trigger in items 3–4". Line 371 only tests the flag. The flag is set in git v2.56.0 `repository.c` L160-161, "if (commondir) { repo->different_commondir = 1;". That `commondir` comes from `GIT_COMMON_DIR` (`setup.c` L1066 `.commondir = getenv_safe(&to_free, GIT_COMMON_DIR_ENVIRONMENT),`). So `git --git-dir=<common> count-objects -v` runs the sweep against the common dir itself whenever `GIT_COMMON_DIR` is exported, and a healthy repo reads `garbage: 6` (Evidence 8). The rule as written in the entry is therefore exact only when `GIT_COMMON_DIR` is unset. `tools/souji-size-census.py` is not affected: it builds a fresh environment ("not the caller's env minus GIT_*", line 13; env dict at lines 90-94), and the probe confirmed `garbage=0` with the variable exported. S120/S121 bytes are correct; the gap is that neither row nor the entry cites `repository.c` for when the flag is set.
3. **No finding: "104-108".** No artifact cites L104-108 as a single range. The entry cites L104 and L105 (`ignore_garbage = 1`, item 2) separately from L106-108 (flag 0, item 4), and that split is correct. Reading 104-108 as one range would mix flagged and unflagged rows.
4. **No finding: row metadata.** S120 and S121 have class `code`, grade `A`, date `2026-10-25` and recheck `on-release`. The teaches cells agree with the bytes: S120's "refs and info are such names, logs and gc.pid are not" and S121's byte-identity claim (Evidence 6).

## Attack log
- **A1 (snapshot is not the live source):** survives. Raw, blob page and snapshot are byte-equal at both tags (Evidence 2, 3).
- **A2 (tag moved or wrong commit):** survives (Evidence 4).
- **A3 (off-by-n line citations; the asked set was 89-124, 111, 104-108, 112-114, 365-385, 371, plus every other cited line):** survives, apart from the header label in Finding 1 (Evidence 5).
- **A4 (byte-identity overclaim at v2.30.0):** survives (Evidence 6).
- **A5 (gate quotes not verbatim):** survives (Evidence 7).
- **A6 (S120 L371 does not carry the census rule's weight):** lands against the entry text (Finding 2). The tool and the C1 counters are unaffected.

Tooling: no installs or updates.
