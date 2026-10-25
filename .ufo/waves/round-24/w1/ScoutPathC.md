# ScoutPathC — git.git path.c `common_dir` / `report_linked_checkout_garbage` at v2.56.0 and v2.30.0

Seat: L1Souji24.ScoutPathC (read-only scout). Access date 2026-10-25 (fetched 2026-10-25 09:19 UTC).
Scratch: /var/tmp/souji-r24-ScoutPathC/ (removed at end). No tools installed or upgraded.

## Status
STATUS: PASS — `path.c` fetched from both tags off two independent hosts (byte-identical per tag). Every requested item is located below with line numbers. The two tags agree on the struct, the four entries and the comment; only the function signature changed.

## Evidence
- Fetch: `curl -sSfL https://raw.githubusercontent.com/git/git/<tag>/path.c` and `curl -sSfL "https://git.kernel.org/pub/scm/git/git.git/plain/path.c?h=<tag>"`, for tag in v2.56.0 and v2.30.0.
  - v2.56.0: 1657 lines, sha256 `f98ba3446d768e3cd9ce8411d5707e35af576a7bd7ad2e7365d26759125d21d2` (GitHub raw = kernel.org plain).
  - v2.30.0: 1538 lines, sha256 `7c5b0710780498264d3771ae85b38e679e7ad733028835ccf18cee7d36c62d4a` (GitHub raw = kernel.org plain).
- Tag oids (`git ls-remote https://github.com/git/git.git`):
  - v2.56.0: tag `2478544319491bbd2a42cc57a83e3d2f4730a280`, peeled commit `a018953688f1b10bddf91bff8747068f5f4746a4`.
  - v2.30.0: tag `2d9685d47a7e516281aa093bf0cddc8aafa72448`, peeled commit `71ca53e8125e36efbda17293c50027d31681a41f`.
- HTTP 200 (curl `-w %{http_code}`): https://github.com/git/git/blob/v2.56.0/path.c, https://github.com/git/git/blob/v2.30.0/path.c, https://git.kernel.org/pub/scm/git/git.git/tree/path.c?h=v2.56.0, https://git.kernel.org/pub/scm/git/git.git/tree/path.c?h=v2.30.0.
- Agreement check: `diff <(sed -n 101,136p path-v2.30.0.c) <(sed -n 89,124p path-v2.56.0.c)` returned no differences (printed `STRUCT+LIST-IDENTICAL`). The function diff (v2.30.0 lines 376-398 against v2.56.0 lines 365-388) shows exactly three changed lines: signature, the `different_commondir` source, and the gitdir source.
- Caller, `builtin/count-objects.c` at the same tags (GitHub raw): v2.56.0 lines 116-119; v2.30.0 lines 110-113.
- Tool note: the harness Read tool refused the 42 KB file even with offset/limit ("exceeds maximum allowed characters (100000 characters). The file is 41992 bytes"), so the ranges were printed with `awk`/`sed -n` (read-only).

## Findings
1. **`struct common_dir`.** v2.56.0 lines 89-96; v2.30.0 lines 101-108; identical bytes at both tags.
   ```
   struct common_dir {
   	/* Not considered garbage for report_linked_checkout_garbage */
   	unsigned ignore_garbage:1;
   	unsigned is_dir:1;
   	/* Belongs to the common dir, though it may contain paths that don't */
   	unsigned is_common:1;
   	const char *path;
   };
   ```
   Field comments: `ignore_garbage` has the comment above it (v2.56.0 line 90, v2.30.0 line 102). `is_dir` has no comment. `is_common` has the comment "Belongs to the common dir, though it may contain paths that don't" (v2.56.0 line 93, v2.30.0 line 105). Initializer order is `{ ignore_garbage, is_dir, is_common, path }`.

2. **`common_list[]` entries.** The array opens at v2.56.0 line 98 / v2.30.0 line 110 and ends at 124 / 136. The four entries are identical at both tags; every line is shifted by −12 at v2.56.0.

   | entry | v2.56.0 line | v2.30.0 line | ignore_garbage | is_dir | is_common |
   |---|---|---|---|---|---|
   | `{ 0, 1, 1, "refs" },` | 111 | 123 | 0 | 1 | 1 |
   | `{ 1, 1, 1, "logs" },` | 104 | 116 | 1 | 1 | 1 |
   | `{ 1, 0, 0, "logs/HEAD" },` | 105 | 117 | 1 | 0 | 0 |
   | `{ 1, 0, 1, "gc.pid" },` | 120 | 132 | 1 | 0 | 1 |

   `refs` is the only one of the four with `ignore_garbage` = 0. That makes it reportable as linked-checkout garbage; `logs`, `logs/HEAD` and `gc.pid` are skipped.

3. **Located `ignore_garbage` quote.** https://github.com/git/git/blob/v2.56.0/path.c line 90: "Not considered garbage for report_linked_checkout_garbage". The same bytes are at v2.30.0 line 102.

4. **`report_linked_checkout_garbage()` body.** v2.56.0 lines 365-385, signature `void report_linked_checkout_garbage(struct repository *r)`. v2.30.0 lines 376-396, signature `void report_linked_checkout_garbage(void)`.
   - It returns early when the repository does not have a separate common dir: `if (!r->different_commondir) return;` at v2.56.0 lines 371-372. At v2.30.0 lines 382-383 the check reads `the_repository->different_commondir`.
   - It builds the prefix `"<gitdir>/"` from `r->gitdir` (v2.56.0 line 373) or from `get_git_dir()` (v2.30.0 line 384). In a linked worktree this gitdir is the per-worktree `<common>/worktrees/<id>` [INFERENCE: standard gitdir layout; not traced in setup.c this run].
   - It loops over `common_list` (v2.56.0 line 375, v2.30.0 line 386) and skips any entry with `ignore_garbage` set (v2.56.0 lines 377-378, v2.30.0 lines 388-389).
   - For each remaining entry it appends the path. If `file_exists()` is true for that path under the worktree gitdir, it calls `report_garbage(PACKDIR_FILE_GARBAGE, sb.buf)` (v2.56.0 lines 381-382, v2.30.0 lines 392-393).
   - It ends with `strbuf_release` (v2.56.0 line 384, v2.30.0 line 395).
   - Caller: `count-objects` calls it only under `-v`, right after it installs `real_report_garbage`. v2.56.0 `builtin/count-objects.c` lines 116-118 read `if (verbose) { report_garbage = real_report_garbage; report_linked_checkout_garbage(the_repository);`. v2.30.0 lines 110-112 are the same except the call takes no argument.

5. **SOURCES row URL.** https://github.com/git/git/blob/v2.56.0/path.c#L89-L124 for the struct and list, and https://github.com/git/git/blob/v2.56.0/path.c#L365-L385 for the function. Pin the commit as `a018953688f1b10bddf91bff8747068f5f4746a4` and the access date as 2026-10-25. Mirror with identical bytes: https://git.kernel.org/pub/scm/git/git.git/tree/path.c?h=v2.56.0.

6. **Do the tags agree?** Yes on everything the claim depends on: the struct with its comments, all four entries and their flags, the `ignore_garbage` comment, and the control flow of the function. The differences are limited to:
   - line numbers (−12 for the struct and list, −11 for the function at v2.56.0);
   - the signature, `(void)` at v2.30.0 and `(struct repository *r)` at v2.56.0;
   - `the_repository->different_commondir` and `get_git_dir()` at v2.30.0 becoming `r->different_commondir` and `r->gitdir` at v2.56.0.

7. **Mechanism behind the F2 false positive** [INFERENCE from the bytes above plus the preregistration's pre-freeze probe; not executed by this seat]:
   - In a linked worktree, `different_commondir` is true, so every `common_list` path that has `ignore_garbage` = 0 and exists under `worktrees/<id>/` is counted as garbage. `refs` (v2.56.0 line 111) is such a path, which matches the probe's `warning: garbage found: <common>/worktrees/<id>/refs`.
   - When `count-objects` runs with `--git-dir=<common dir>`, `different_commondir` is false, so the function returns at lines 371-372. This matches the probe's `garbage: 0`, and it is the source-level basis for C1's rule that the census runs against the common dir.
   - The report is gated on `-v`, so the C1 tool must pass `-v` for any garbage figure to be meaningful.

## Attack log
- A1 (C1 case 4, low): the predicate assumes that `git -C <linked> count-objects -v` reads `garbage: 1` because of `worktrees/<id>/refs`. From the source, that witness depends on `<common>/worktrees/<id>/refs` existing. Whether `git worktree add` creates that directory at v2.56.0 was not traced (worktree.c and builtin/worktree.c not opened) [INFERENCE]; the only support is the preregistration's probe. If a git version or ref backend does not create it, the witness goes to 0 and case 4's precondition fails without any defect in the tool. No change proposed; this is reported as a dependency of the frozen case.
- A2 (none on C2/C3): out of scope for this seat.
