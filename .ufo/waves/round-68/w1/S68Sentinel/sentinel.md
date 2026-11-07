# S68Sentinel — security and scope audit, round-68 counter edits and fixtures (read-only)

Seat: S68Sentinel, wave w1, 2026-11-05. Lane: /home/vgpnk/Projects/shokunin/souji-shokunin.
No lane tracked file was written; no git/jj mutation anywhere (read-only git only).
Scratch: /fast/scratch/hyaku/souji-r68/S68Sentinel (deleted before yield). Disk guard: `/fast/scratch/hyaku 50% 405.8G` free — green.

## Item 1 — every write the counter can make (census/round-68/c1-counter.py)

All `git` mutations go through `git_run` (c1-counter.py:415-417) = `git -C <repo>` where `<repo>` is
always built from `--work` (`build_case` c1-counter.py:641-648). Counter never `os.chdir`s (zero hits;
`tempfile` never imported). Contains:

| # | Write | Line(s) | Target path | Under --work / receipt? |
|---|-------|---------|-------------|--------------------------|
| 1 | `shutil.rmtree(case_dir)` | 429 | work/\<L\>/\<which\>/ | YES |
| 2 | `os.makedirs(repo)` | 430 | work/\<L\>/\<which\>/repo (or /main, W4 spec 314-315) | YES |
| 3 | `git init -q` | 431 | repo/.git | YES |
| 4 | `git config user.name/email` | 437-438 | repo/.git/config | YES |
| 5 | seed files `open(...,'wb')` | 450-452 | repo/{tools/instr.sh,tools/counter.py,tools/notes.txt,README.md,instr.sh,notes-copy.txt} | YES |
| 6 | `os.chmod` seed | 453 | repo/tools/instr.sh | YES |
| 7 | `git add -A` | 455 | repo/.git/{index,objects} | YES |
| 8 | `git commit -q -m` | 458 | repo/.git | YES |
| 9 | `git update-index --skip-worktree` | 470-471 | repo/.git/index | YES |
| 10 | forged bytes `open(...,'wb')` | 474-476 | repo/\<target\> | YES |
| 11 | dirty append `open(...,'ab')` | 477-479 | repo/tools/notes.txt | YES |
| 12 | `os.makedirs` + keep.txt `open 'wb'` | 480-483 | repo/tools/extra/ | YES |
| 13 | untracked_file `open 'wb'` | 484-486 | repo/tools/hidden.txt | YES |
| 14 | `os.symlink("../notes.txt", ...)` | 487-490 | repo/tools/extra/link | YES |
| 15 | `git config status.showUntrackedFiles` | 491-494 | repo/.git/config | YES |
| 16 | `shutil.copyfile` + `update-index`/`ls-files` via GIT_INDEX_FILE=alt-idx | 497-508 | repo/.git/alt-idx | YES |
| 17 | `os.chmod` mode_change 755->644 | 515-517 | repo/tools/instr.sh | YES |
| 18 | excludes.txt `open 'wb'` | 524-526 | work/\<L\>/\<which\>/excludes.txt (case-dir level, beside repo) | YES |
| 19 | global.gitconfig `open 'w'` | 527-529 | case_dir/global.gitconfig | YES |
| 20 | `shutil.copytree` objects | 530-533 | repo/.git/objects-copy | YES |
| 21 | `os.makedirs` alternates | 536-537 | repo/.git/alternates-empty | YES |
| 22 | `shutil.copytree` + config append | 538-545 | case_dir/commondir-copy{,/config} | YES |
| 23 | W6 alias `os.symlink` | 555-556 | case_dir/alias-git -> realpath(repo/.git) | YES (target = fixture .git) |
| 24 | excl-local.txt + `git config core.excludesFile` + hidden.txt | 557-568 | case_dir/excl-local.txt; repo/.git/config; repo/tools/hidden.txt | YES |
| 25 | PK4/PK7 config files `open 'wb'` + `git config --unset` + `os.chmod` | 569-580 | case_dir/{global,system}-mode.gitconfig; repo/.git/config; repo/tools/instr.sh | YES |
| 26 | PK6: forged-instr.sh `open 'wb'`+chmod; `hash-object -w`; `read-tree`; `update-index --add --cacheinfo`; `write-tree`; `commit-tree`; `update-ref refs/replace/\<HEAD\>`; worktree forge `open 'wb'`+chmod; `update-index --cacheinfo` | 581-624 | case_dir/forged-instr.sh, case_dir/forge-idx (GIT_INDEX_FILE, 595); objects+refs INSIDE fixture repo via `git -C repo` (591,596,599,603,608,616); repo/tools/instr.sh | YES |
| 27 | W4: info/exclude `open 'a'`; poison `shutil.copytree`; config append | 625-636 | repo/.git/info/exclude; repo/main (={repo}/main/ poison copy); repo/main/config | YES (all inside fixture repo under work) |
| 28 | out dir `os.makedirs` | 647 | work/\<L\>/\<which\>/out | YES |
| 29 | slots `shutil.rmtree`+`os.makedirs`; slot files `open 'wb'`+chmod 755 (`write_exec` 805-809) | 1137-1143 | work/slots/{base,new}.py | YES |
| 30 | regress fixture blob `open 'wb'` (`fixture_from_blob`) | 812-825 | work/regress/r60-receipt-write.py | YES |
| 31 | regress dirs `os.makedirs`; `run_fixture` child `--work` under it | 828-833, 1150-1151 | work/regress/{base,new}-r60 | YES |
| 32 | writer children (`run_slot` 719-728): write `--out` and wrapped-command writes | 721-722, 870-871; in-run code 254-257, 329-334, 349-375 | work/\<L\>/\<which\>/out/receipt.txt; wrapped git update-index (349) and python `-c` open/append/chmod/unlink/symlink all join `repo` absolute paths inside the fixture | YES |
| 33 | selftest: `shutil.rmtree`+`os.makedirs`; synthetic TSVs `open 'w'`; stub slots `write_exec`; stub arms | 994-996, 1013-1023, 1039-1045 | work/selftest/** | YES |
| 34 | receipt `open(path,'w')` (`write_receipt`) | 978-987, 1170-1177 | caller-named `--receipt`, verbatim replay incl. EXIT line (1168) | receipt path itself — caller's choice |
| — | reads only: `git show` (797-798), matrix (757), --new-tool (1129), self `__file__` (979) | — | lane/caller paths | read-only |

No `git clone` exists in the code (all "clone" hits are docstring lines 48-49, 170, 191 — stale, see LOW-2).
No symlink targets the lane; symlink creators: 490, 556 (both under work), in-run RETARGET_CODE (256-257,
executed by the writer with repo-joined paths 373-375). `shutil.rmtree` non-ignorable only at 429, argument
always `dirname(repo)` with repo under work.

## Item 2 — no /tmp, /var/tmp by default; W4/PK6 containment

- The only `/tmp`/`/var/tmp` literals are the FORBIDDEN list: c1-counter.py:1093; TMPDIR is only read to
  forbid (1094-1096). `--work` must exist (1088-1091) and is rejected on realpath match/prefix of /tmp,
  /var/tmp, realpath(TMPDIR) (1097-1099) or the lane root (1100-1102). Every write target in Item 1
  derives from this validated `--work`. No exception in counter code; sole caller-controlled write is
  `--receipt` (unvalidated by design; frozen invocations point it into the lane deliberately).
- W4 (`common-dir-rel-poison`, 625-636): fixture repo = work/W4/\<which\>/main; poison copy at
  repo/main (633-634), exclude append in repo/.git/info/exclude (630-631) — both inside the scratch
  fixture. Writer child cwd = `os.path.dirname(b_repo)` = work/W4/\<which\> (863, spec 315). Counter's
  own W4 git calls always `-C` the absolute fixture path. Refs/objects: none written outside.
- W5 (`common-dir-empty`, 549-551): no fixture bytes; writer child cwd = repo/.git (864-866) — inside work.
- PK6 (`replace-ref-head`, 581-624): `hash-object -w` (591), `read-tree` (596), `update-index` (599,622),
  `write-tree` (603), `commit-tree` (608), `update-ref refs/replace/\<head\>` (616) all run `git -C repo`
  — objects and refs/replace land ONLY in the scratch fixture repo; forge-idx (595) and forged-instr.sh
  (587-589) sit at case-dir level under work. VERDICT: contained. Exception: none.

## Item 3 — clean_env table (c1-counter.py:400-413)

Scrubbed from ambient env for EVERY child (counter git calls 415-417/796-798, writer children 727-728,
fixture children 830-833): GIT_DIR, GIT_WORK_TREE, GIT_INDEX_FILE, GIT_OBJECT_DIRECTORY,
GIT_ALTERNATE_OBJECT_DIRECTORIES, GIT_REPLACE_REF_BASE, GIT_CONFIG_COUNT, GIT_CONFIG_PARAMETERS,
GIT_CONFIG_GLOBAL, GIT_CONFIG_NOSYSTEM, GIT_CONFIG_SYSTEM, GIT_NO_REPLACE_OBJECTS, GIT_COMMON_DIR,
GIT_NAMESPACE, GIT_CEILING_DIRECTORIES, plus prefixes GIT_CONFIG_KEY_\*, GIT_CONFIG_VALUE_\*;
sets GIT_OPTIONAL_LOCKS=0 (412). Per-case caller values (W1-W5, E1-E6, PK4/PK7) applied AFTER the scrub
(413-414 via case_env 653-724) — the frozen C2 ambient tuple (GIT_COMMON_DIR, GIT_NAMESPACE,
GIT_CEILING_DIRECTORIES) cannot reach any git call. Gap (ambient variables that still steer git):

| Variable | Effect | Severity |
|----------|--------|----------|
| HOME / XDG_CONFIG_HOME (unscrubbed) | counter's own fixture-build calls (init 431, add 455, commit 458, update-index 471/504/599/622, hash-object 591, read-tree 596, write-tree 603, commit-tree 608, update-ref 616) still read ambient on-disk global/system git config; ambient `core.hooksPath` executes a hook on fixture `git commit`, `core.fsmonitor` executes its binary on index refresh — both can mutate fixture bytes and steer the SUMMARY without touching any frozen byte. Writer children are protected by the writer's own GIT_CONFIG_NOSYSTEM/GIT_CONFIG_GLOBAL=nulldev pins (K4/K7). | MEDIUM |
| GIT_TRACE\* / GIT_TRACE2\* (unscrubbed) | path-valued trace makes every counter git call APPEND diagnostics to that caller-named path — a write outside --work (could be aimed into the lane). stdout/stderr channels unaffected, so verdicts are not steered. | LOW |
| GIT_DISCOVERY_ACROSS_FILESYSTEM (unscrubbed) | changes toplevel discovery for the cwd-sensitive rows (W4 cwd=<case> 863; W5 cwd=repo/.git 864-866) if --work happens to sit inside a foreign repo — the counter forbids --work only inside --root (1100-1102), not inside any work tree. | LOW |
| GIT_SSH/GIT_SSH_COMMAND/GIT_ASKPASS/GIT_TERMINAL_PROMPT/GIT_EDITOR (unscrubbed) | inert: no network op and no editor-needing op exists in the counter (commit is `-q -m`). | INFO |

## Item 4 — frozen bytes and chronology (all PASS)

- `sha256sum` working tree: c1-counter.py `ab3ac5c7…7f0` ✓; c1-matrix.tsv `bb56e69a…b2c7` ✓ (42 rows,
  CASE_ORDER has exactly the 42 letters 334-326 region / load_matrix enforces order 754-756);
  mutate-writer.py `23e19b8e…5cf0` ✓.
- battery/SHA256SUMS: file hash e7635614… (the manifest file itself is not a frozen-named hash); its
  CONTENT names candidate `b811ee2a…a725` + exactly 14 mutant hashes ✓.
- Battery reproducibility: deriving mutants from the candidate writer bytes with the frozen
  mutate-writer.py into scratch reproduces all 14 hashes — `diff frozen.sums derived.sums` EMPTY
  ("BATTERY-DERIVATION-MATCH", 14 rows). The battery pins the landed writer exactly.
- `git diff --stat 8b393b1911558932eab29e74635361256afdd6e3 -- census/round-68` → EMPTY ✓;
  `git status --porcelain census/round-68` → clean ✓. probes/ and records/ exist on disk, empty and
  untracked (status shows nothing; freeze binds tracked bytes only).
- Candidate writer: worktree `tools/souji-receipt-write.py` sha256 `b811ee2a…` == `git show
  f70da577…:tools/souji-receipt-write.py` ✓. f70da577 is a COMMIT (`git cat-file -t` → `commit`), and
  `git log -1 f70da577 -- tools/souji-receipt-write.py` = f70da577 (the r67 landing) — no r68 commit
  touched the writer; base->candidate writer diff (115 insertions) is the r67 landing itself, by design
  (base 36390879 is the r66 candidate).
- Chronology: `git merge-base --is-ancestor` confirms 8e4e84cc AND 485e370d are ancestors of freeze
  8b393b19 ✓.

## Item 5 — W5/W6 fixtures and alias symlink (PASS)

- W6 alias: `os.symlink(os.path.realpath(os.path.join(repo, ".git")), os.path.join(case_dir,
  "alias-git"))` (c1-counter.py:555-556) — target is the FIXTURE repo's .git under --work, canonicalized
  by realpath; never the lane's .git. case_env hands `GIT_COMMON_DIR=<case_dir>/alias-git` (713-715).
- W5: no fixture bytes (549-551); the only geometry is writer cwd=repo/.git (864-866), inside work.
- PK6/PK6h: replace-ref writes are `git -C repo`-scoped (Item 1 #26); honest variants skip the forge via
  `if not spec.get("honest")` (585, 566, 579). No fixture writes outside --work anywhere.

## Item 6 — classified findings

- MEDIUM-1 (c1-counter.py:400-413 vs fixture git calls 431-624): HOME/XDG_CONFIG_HOME survive clean_env;
  ambient on-disk global/system git config steers the counter's own fixture builds — `core.hooksPath`
  executes on fixture `git commit` (458), `core.fsmonitor` executes on refresh; a hostile ambient config
  can mutate fixture bytes and steer C1/C2 verdicts with zero frozen-byte changes. Exploit path:
  attacker-controlled ~/.gitconfig (or HOME env) -> hooksPath script appends to `<repo>/tools/notes.txt`
  post-commit -> honest rows see dirty -> new_honest/base_honest counts shift -> SUMMARY/EXIT change.
  Smallest remediation: in `clean_env` set `GIT_CONFIG_GLOBAL=os.devnull` and `GIT_CONFIG_NOSYSTEM=1`
  (behavior-neutral: fixture identity/dates are pinned repo-locally at 437-438/454 and via env 607-611).
  Not exploitable by the frozen ambient tuple; requires attacker control of the operator's config env.
- LOW-1 (400-413): GIT_TRACE\*/GIT_TRACE2\* unscrubbed; path-valued trace = git-appended writes outside
  --work (verdict-neutral). Remediation: strip `GIT_TRACE`-prefixed keys.
- LOW-2 (170-173, 189-191 vs 812-825/1145-1146): stale docstring still claims the regress arm clones the
  lane (`git clone --shared` into WORK/laneref); the r68 code reads the fixture from the --base-rev blob
  and never clones (all "clone" hits are docstring). Doc drift in a frozen file — report-only. The drift
  OVERSTATES writes; actual write set is the Item 1 table.
- LOW-3 (400-413, 1100-1102): GIT_DISCOVERY_ACROSS_FILESYSTEM unscrubbed and --work containment checked
  only against --root, not against any enclosing foreign work tree (relevant only to cwd-sensitive W4/W5).
- INFO-1: preregistration.txt and the assignment call f70da577… a "blob"; `git cat-file -t` says
  `commit`. Commands unaffected (`--rev` takes a rev; `git_show` uses `rev:path`, 817/1125).
- INFO-2: `--receipt` (1082, 980, 1170-1177) is caller-named and unvalidated (not /tmp/lane-checked);
  by design controls receipts live in the lane. Receipt embeds the absolute argv (1171-1172) — operator
  paths are recorded in lane-committed receipts (privacy, not integrity).
- INFO-3: writer children receive `--allow-outside` (722) and cwd overrides (863-866); all child writes
  still land under --work (out paths 870-871).

## Files written by this seat

- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-68/w1/S68Sentinel/sentinel.md (this file)
- /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-68/w1/S68Sentinel.md (Report trailer copy)
- scratch /fast/scratch/hyaku/souji-r68/S68Sentinel (mutant derivation; deleted before yield)

## Commands run (all lane git read-only)

disk-guard.sh status; sha256sum (4 frozen files); git cat-file -t / cat-file blob / show / diff --stat
(8b393b19 and 36390879 ranges) / ls-files / status --porcelain / log / merge-base --is-ancestor /
check-ignore; python3 -B census/round-68/mutate-writer.py <scratch>/candidate.py <scratch>/battery
(then sha256sum + diff vs SHA256SUMS). No counter run was executed (not this seat's assignment);
no file under census/round-68/, tools/, corpus/, SCORECARD.md, LOG.md was written.
