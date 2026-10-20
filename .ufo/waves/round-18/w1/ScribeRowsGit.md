STATUS: DONE — two draft SOURCES rows (S064 attr.c, S065 cat-file -e) drafted from opened primary sources; no registry edit made, L1 integrates.

# Scope

Frontier step for C1 (operability) and calibration: two primary-source rows the round-18 C1 lesson can cite. Rows are drafts for L1 to paste into `corpus/SOURCES.md`; I did not edit `SOURCES.md`, the fleet repo, or any other lane file (scribe is a leaf).

# Draft rows

Shape follows the registry columns in `corpus/SOURCES.md` (`id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by`).

```
| S064 | git/git source at tag v2.56.0: attr.c — https://github.com/git/git/blob/v2.56.0/attr.c (raw: https://raw.githubusercontent.com/git/git/v2.56.0/attr.c) | code | A | how `$GIT_DIR/info/attributes` is opened during attribute lookup at v2.56.0; not what any particular porcelain command does | tag v2.56.0 attr.c:711 `fd = open(path, O_RDONLY);` (read_attr_from_file, :699); :718 `fstat(fd, &st)` after the open; :948 `e = read_attr_from_file(git_path_info_attributes(), flags);` (bootstrap_attr_stack, :916); call chain git_check_attr:1330 → collect_some_attrs:1171 → prepare_attr_stack:1192 → bootstrap_attr_stack:979 | the info file is opened with a plain `open(O_RDONLY)` before any file-type check, and fstat runs only after the open returns, so a FIFO at `$GIT_DIR/info/attributes` blocks inside open(2) before git can reject it; every attribute lookup reaches this line when a repository is present (have_repository) | mined | 2026-10-20 | on-release | — (C1 lesson pending; L1 to fill) |
| S065 | git-cat-file(1) — https://git-scm.com/docs/git-cat-file (code: https://raw.githubusercontent.com/git/git/v2.56.0/builtin/cat-file.c) | docs+code | A | exit status of `cat-file -e` for an existing, absent and unresolvable object name at v2.56.0; not whether the object is complete or readable | web manual "git-cat-file last updated in 2.56.0", opened 2026-10-20, § OPTIONS -e: "Exit with zero status if <object> exists and is a valid object." Code at tag v2.56.0 builtin/cat-file.c:158-160 (name unresolvable → `die("Not a valid object name %s", ...)`, exit 128), :195-198 (`case 'e': ret = !odb_has_object(..., ODB_HAS_OBJECT_RECHECK_PACKED \| ODB_HAS_OBJECT_FETCH_PROMISOR);`) | `-e` exits 0 only when the object is present; a well-formed but absent object exits 1 silently (`ret = !odb_has_object`); a name that does not resolve dies with 128 and a `fatal:` line, which the doc's "non-zero" wording does not distinguish; the lookup flags include FETCH_PROMISOR, so a promisor repository may fetch a missing object (flag name only; runtime effect not measured here, cf. S049) | mined | 2026-10-20 | on-release | — (pointer-resolution lesson pending; L1 to fill) |
```

# Evidence and commands run

All commands are read-only per the probe rule.

1. `read` of `corpus/SOURCES.md` (registry S001–S063 read; ids S064/S065 unused).
2. `read https://raw.githubusercontent.com/git/git/v2.56.0/attr.c` (full file, 1372 lines in the returned artifact `artifact://89115`).
3. `read https://git-scm.com/docs/git-cat-file` ("last updated in 2.56.0"; § OPTIONS -e text as quoted).
4. `grep` over `artifact://89115` for `info/attributes|GIT_DIR|read_attr_from_file|open\(|…`; then `read artifact://89115:699-722` and `artifact://89115:944-955`, confirming `open` at :711, `fstat` at :718, `git_path_info_attributes()` at :948.
5. `grep` over `artifact://89115` for `prepare_attr_stack\(|git_check_attr|collect_some_attrs` → :1171, :1192, :1330.
6. `read https://raw.githubusercontent.com/git/git/v2.56.0/builtin/cat-file.c` (`artifact://89250`), then `grep` for `case 'e':|Not a valid object name|ret = !odb_has_object` → :158-160, :195-198, :224.
7. Host probes (bash, read-only `git -C … cat-file -e`, run on the lane root, which is a real repo — no writes):

```
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file -e 0000000000000000000000000000000000000001; echo "rc_missing=$?"
rc_missing=1
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file -e HEAD; echo "rc_head=$?"
rc_head=0
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file -e b5763415cc67ecff1e8fe56c58c39a6fb106d7a3^{commit}; echo "rc_base=$?"
rc_base=0
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file -e HEAD:nonexistent-path-xyz; echo "rc_badpath=$?"
fatal: path 'nonexistent-path-xyz' does not exist in 'HEAD'
rc_badpath=128
$ git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file -e deadbeef; echo "rc_shortbad=$?"
fatal: Not a valid object name deadbeef
rc_shortbad=128
$ git --version
git version 2.56.0
```

Notes on the probe: the missing-object case (rc 1) is silent on stderr; the unresolvable-name cases (rc 128) print `fatal:`. Only the first form is "object absent"; the other two are "name not resolvable", a different class for pointer resolution.

# Verdicts

- S064 (attr.c): **holds** for the stated scope. Line numbers are from the raw v2.56.0 file (`artifact://89115`); the open-before-fstat ordering is read directly at :711 and :718. Whether a FIFO blocks is grounded by S062 (fifo(7)), not measured here; the measured hang is the L1 reproduction the C1 lesson cites.
- S065 (cat-file -e): **holds** for exit codes: 1 for a well-formed absent object, 128 for an unresolvable name, 0 for present; confirmed both by source (:158-160, :195-198) and by the probe above. The FETCH_PROMISOR implication is **partial** — the flag name is the only evidence; no promisor probe was run (the lane has none).

# Findings for L1

1. Host git is **2.56.0** (`git --version`), while earlier rows (S001–S063) say "installed git 2.55.0". Rows that cite "installed 2.55.0" for exit or doc semantics are not wrong, but any new C1 probe should record the version it ran against. [observed]
2. S065's `-e` row is the right place to keep the 1-vs-128 split; the existing S049 (GIT_NO_LAZY_FETCH) row does not state whether `cat-file -e` honours it. Whether `GIT_NO_LAZY_FETCH=1` suppresses the `FETCH_PROMISOR` path in `cat-file -e` is **not verified** here. [INFERENCE from the flag name]
3. S064 gives a source anchor for the C1 mechanism that S062 alone does not: the open at attr.c:711 precedes the type check at :718. The C1 fix (`:546-585` guard and the census watchdog) should not rely on `git check-attr` to avoid the FIFO; the open happens inside any `git_check_attr` call.

# Routed or out of scope

- No `corpus/SOURCES.md` edit (scribe drafts only; L1 integrates).
- No probe against `info/attributes` in any repo; no FIFO was created outside a fixture (none was needed; the probes above touched no `info/attributes`).
- No tools installed or updated.
