# ScoutCountObjectsC — git.git `count-objects` garbage semantics at v2.56.0

## Status
STATUS: PASS — every question answered from the v2.56.0 source, fetched live on 2026-10-25, and backed by a local git 2.56.0 probe. One correction to the brief: at v2.56.0, `report_garbage`/`report_pack_garbage` are defined in `odb/source-packed.c`, not `packfile.c`.

## Evidence
- Tag: `git ls-remote https://github.com/git/git.git refs/tags/v2.56.0 'refs/tags/v2.56.0^{}'` returned `2478544319491bbd2a42cc57a83e3d2f4730a280` (tag) and `a018953688f1b10bddf91bff8747068f5f4746a4` (commit).
- Fetched with `curl -sSfL https://raw.githubusercontent.com/git/git/v2.56.0/<path>`. The kernel.org copy of `builtin/count-objects.c` (`?h=v2.56.0`) was compared with `cmp` and is `IDENTICAL` (178 lines).
- sha256 of the fetched files: `count-objects.c` ec13ae40…e03e, `odb/source-packed.c` bfb57f4c…21d2, `path.c` f98ba344…d2, `object-file.c` e011ce18…708, `packfile.c` 021b1b9b…032, `packfile.h` 20456fb3…ddf4.
- Symbol search: `git grep -n report_garbage v2.56.0` in a `--filter=blob:none --depth=1` scratch clone. Definitions found: `odb/source-packed.c:702` (hook), `:714` (report_pack_garbage), `path.c:365` (report_linked_checkout_garbage), `packfile.h:219` (extern). `packfile.c` only matches `for_each_file_in_pack_dir` at line 849.
- Probe: local `git version 2.56.0`, scratch under /var/tmp, btrfs, `LC_ALL=C`. Each `count-objects -v` output is excerpted below:
  - main worktree, clean: `garbage: 0`, `size-garbage: 0`.
  - `git -C <linked>`: `warning: garbage found: …/r/.git/worktrees/wt/refs`, `garbage: 1`, `size-garbage: 0`.
  - linked worktree without `-v`: `3 objects, 12 kilobytes`, with no warning.
  - `--git-dir=<common dir>`: `garbage: 0`.
  - 1500-byte stray file `objects/stray`: `garbage: 0`, `size-garbage: 0`.
  - `objects/pack/junk` (1023 B): `garbage: 1`, `size-garbage: 0`.
  - `junk` (1023 B) + `junk2` (1025 B): `garbage: 2`, `size-garbage: 2`.
  - `objects/12/zz` (3000 B): `garbage: 1`, `size-garbage: 2`.
  - a directory at `objects/ab/<38 hex>`: `garbage: 1`.
  - orphan `pack-x.pack`: `warning: no corresponding .idx: …`, `garbage: 1`.
  - alternate whose `objects/pack/altjunk` is 2048 B: `warning: garbage found: …/alt/.git/objects/pack/altjunk`, `garbage: 1`, `size-garbage: 2`.
  - `stat` on the worktree `refs` dir: `0 directory`.
- Lane revision when this report was written: `f9db2181647d91470a724a12d626bd6106805076`. Nothing in the lane was modified apart from this report.

## Findings
1. **Call site and condition for `report_linked_checkout_garbage`.** It is called only under `-v`, right after the hook is installed, and before any loose or pack scan. `builtin/count-objects.c:116-119`: "if (verbose) { report_garbage = real_report_garbage; report_linked_checkout_garbage(the_repository);". Inside the function, it returns unless the repo has a separate common dir. `path.c:371-372`: "if (!r->different_commondir) return;". It then walks `common_list`, skips entries flagged `ignore_garbage`, and reports each path that exists under `r->gitdir`. `path.c:377-382`: "if (p->ignore_garbage) continue;" and "if (file_exists(sb.buf)) report_garbage(PACKDIR_FILE_GARBAGE, sb.buf);". The `refs` entry is not ignored, which is why `worktrees/<id>/refs` gets flagged. `path.c:111`: "{ 0, 1, 1, "refs" },". `logs` is ignored (`path.c:104` "{ 1, 1, 1, "logs" },"). Probe: a linked worktree reports `garbage: 1`; pointing `--git-dir` at the common dir reports `garbage: 0`. Confidence: high.
2. **How `garbage` and `size_garbage` accumulate.** Both are file-scope statics (`count-objects.c:18-19`), incremented only in `real_report_garbage`. `count-objects.c:49-52`: "if (!stat(path, &st)) size_garbage += st.st_size; warning("%s: %s", desc, path); garbage++;". A `seen_bits` value of `PACK|IDX` maps to NULL and is skipped (`count-objects.c:35-37`, `:46-47`). `size_garbage` is `st_size` from `stat()`, not on-disk blocks; loose objects use `on_disk_bytes` instead (`:69`). `stat` follows symlinks. A directory adds its own `st_size`, which depends on the filesystem: 0 on btrfs in this probe. [INFERENCE] ext4 typically reports 4096 for a directory, which would make the linked-worktree case print `size-garbage: 4`.
3. **Loose `objects/<2hex>/` garbage.** `for_each_loose_file_in_source` visits subdirs 0..255, each as `%02x` (`object-file.c:1121-1123`, `:1060`). A name counts as an object only if its length is `hexsz-2` and it parses as hex. `object-file.c:1080-1082`: "if (namelen == algop->hexsz - 2 && !hex_to_bytes(oid.hash + 1, de->d_name, algop->rawsz - 1)) {". Any other name goes to `cruft_cb` (`:1094-1095`). In count-objects that is `count_cruft`, which calls `loose_garbage` (`count-objects.c:77-80`). An object-named entry that is not a regular file is also garbage. `count-objects.c:66-67`: "if (lstat(path, &st) ¦¦ !S_ISREG(st.st_mode)) loose_garbage(path);" (the source has two pipe characters where ¦¦ appears). `loose_garbage` reports only under verbose (`:57-58` "if (verbose) report_garbage(PACKDIR_FILE_GARBAGE, path);"). Probe: `objects/12/zz` and a 38-hex directory each count as `garbage: 1`. Confidence: high.
4. **Pack-dir garbage (`odb/source-packed.c`, not `packfile.c`).**
   - Directory scanned: `packfile.c:824-825` fixes it to `<objdir>/pack` ("strbuf_addstr(&path, objdir); strbuf_addstr(&path, "/pack");"). `for_each_file_in_pack_dir` passes `subdir` NULL (`packfile.c:853`). The scan is called from `prepare_packed_git_one` (`odb/source-packed.c:797-799`).
   - Classification in `prepare_pack` (`odb/source-packed.c:768-786`): with no hook installed, nothing is reported. `multi-pack-index` and its `.d` directory are exempt, as are `multi-pack-index*` names ending `.bitmap`/`.rev` (`:771-776`). Files ending `.idx .rev .pack .bitmap .keep .promisor .mtimes` are queued for pairing (`:777-784`). Anything else is reported immediately (`:786` "report_garbage(PACKDIR_FILE_GARBAGE, full_name);").
   - Pairing in `report_pack_garbage` (`:714-746`): queued names are sorted and grouped by the basename up to the last dot. A name with no dot is reported (`:733-734`). A group missing either `.pack` or `.idx` has every member reported with its `seen_bits` (`report_helper` `:707-711` "if (seen_bits == (PACKDIR_FILE_PACK¦PACKDIR_FILE_IDX)) return;"; the source has a pipe character where ¦ appears).
   - Messages: `bits_to_msg` (`count-objects.c:24-38`) prints "no corresponding .idx" or "no corresponding .pack". Probe: an orphan `.pack` counts as `garbage: 1`.
   - Separate hook: `builtin/gc.c:67` defines its own static `report_pack_garbage`, used only by gc (`gc.c:728`).
   - Confidence: high.
5. **Alternates' pack dirs are scanned too.** The scan runs per packed source and is triggered by `repo_for_each_pack` (`count-objects.c:132`). The probe showed junk in an alternate's `objects/pack` counted (`garbage: 1`, `size-garbage: 2`), even though line 133 then skips non-local packs for the `in-pack`/`size-pack` totals. [INFERENCE] By code, `for_each_loose_file_in_source` is given only `the_repository->objects->sources` (`count-objects.c:121`), the first source, so an alternate's loose `<2hex>/` dirs are not scanned. This was not probed. Relevance to C1 case 5 (alternates): if that fixture's alternate contains pack junk, the census `garbage=` value includes it.
6. **A stray file directly in `objects/` is never scanned.** No path enumerates the top level of `objects/`. The loose walk only `opendir`s `<objdir>/%02x` (`object-file.c:1060-1062`). The pack walk only opens `<objdir>/pack` (`packfile.c:825-828`). `report_linked_checkout_garbage` only tests `common_list` names under the per-worktree gitdir; `objects` there is `path.c:110` "{ 0, 1, 1, "objects" },", which is about `<gitdir>/objects` itself existing in a linked gitdir, not its contents. Probe: a 1500-byte `objects/stray` gives `garbage: 0`, `size-garbage: 0`. Confidence: high.
7. **Unit of `size-garbage`.**
   - Default: KiB, truncated (floor) from the summed byte total. `count-objects.c:151-152`: "strbuf_addf(&garbage_buf, "%lu", (unsigned long)(size_garbage / 1024));".
   - With `-H`: `strbuf_humanise_bytes` (`:145`).
   - No `size-garbage` line is printed without `-v`; it is inside `if (verbose)` (`:124`, `:162`).
   - The floor is applied to the sum, not per file. Probe: 1023 B prints 0. 1023+1025 B prints 2, whereas flooring each file would give 0+1. 3000 B prints 2.
   - Confidence: high.
8. **Non-verbose mode never counts garbage.** The hook is installed only under `-v` (`:117`), `loose_garbage` is gated on verbose (`:57`), and both pack paths return early when `report_garbage` is NULL (`odb/source-packed.c:718-719`, `:768-769`). A census must therefore pass `-v`.

## SOURCES rows (accessed 2026-10-25)
| id | URL | locator | quote (≤25 words, verbatim) |
|---|---|---|---|
| CO1 | https://github.com/git/git/blob/v2.56.0/builtin/count-objects.c#L116-L119 | L116-119 | `report_garbage = real_report_garbage; report_linked_checkout_garbage(the_repository);` |
| CO2 | https://github.com/git/git/blob/v2.56.0/builtin/count-objects.c#L49-L52 | L49-52 | `if (!stat(path, &st)) size_garbage += st.st_size; warning("%s: %s", desc, path); garbage++;` |
| CO3 | https://github.com/git/git/blob/v2.56.0/builtin/count-objects.c#L55-L59 | L55-59 | `static void loose_garbage(const char *path) { if (verbose) report_garbage(PACKDIR_FILE_GARBAGE, path);` |
| CO4 | https://github.com/git/git/blob/v2.56.0/builtin/count-objects.c#L151-L152 | L151-152 | `strbuf_addf(&garbage_buf, "%lu", (unsigned long)(size_garbage / 1024));` |
| CO5 | https://github.com/git/git/blob/v2.56.0/builtin/count-objects.c#L121-L122 | L121-122 | `for_each_loose_file_in_source(the_repository->objects->sources, count_loose, count_cruft, NULL, NULL);` |
| PA1 | https://github.com/git/git/blob/v2.56.0/path.c#L371-L372 | L371-372 | `if (!r->different_commondir) return;` |
| PA2 | https://github.com/git/git/blob/v2.56.0/path.c#L377-L382 | L377-382 | `if (p->ignore_garbage) continue;` … `if (file_exists(sb.buf)) report_garbage(PACKDIR_FILE_GARBAGE, sb.buf);` |
| PA3 | https://github.com/git/git/blob/v2.56.0/path.c#L111 | L111 | `{ 0, 1, 1, "refs" },` |
| OF1 | https://github.com/git/git/blob/v2.56.0/object-file.c#L1080-L1082 | L1080-1082 | `if (namelen == algop->hexsz - 2 && !hex_to_bytes(oid.hash + 1, de->d_name, algop->rawsz - 1)) {` |
| SP1 | https://github.com/git/git/blob/v2.56.0/odb/source-packed.c#L785-L786 | L785-786 | `else report_garbage(PACKDIR_FILE_GARBAGE, full_name);` |
| SP2 | https://github.com/git/git/blob/v2.56.0/odb/source-packed.c#L718-L719 | L718-719 | `if (!report_garbage) return;` |
| PF1 | https://github.com/git/git/blob/v2.56.0/packfile.c#L824-L825 | L824-825 | `strbuf_addstr(&path, objdir); strbuf_addstr(&path, "/pack");` |

Mirror (byte-identical for count-objects.c): https://git.kernel.org/pub/scm/git/git.git/plain/builtin/count-objects.c?h=v2.56.0

## Remaining unknowns
- The `size-garbage` contribution of the linked-worktree `refs` directory depends on the filesystem (0 on btrfs here). The ext4 value is [INFERENCE], not probed.
- Whether alternates' loose `<2hex>/` dirs are excluded is [INFERENCE] from `count-objects.c:121` passing only the first source; no probe was run.

## Tooling
No installs or updates.
