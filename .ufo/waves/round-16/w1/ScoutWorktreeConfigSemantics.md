# Scout — extensions.worktreeConfig / config.worktree read semantics (r16 C1)

Target: `tools/souji-census.sh` at `cbf688ab2ab28e38103e5a9417ca525b5f2ed423`
(1784 lines, sha256 `fed43c710b755b02373be812a267679dfbf72bcf8a7f315884003c487b709757`).
Read-only recon. Web docs/source accessed 2026-10-20. No census run, no fixture run.

## Verdict

The census's gate — read `<gitdir>/config.worktree` only when the boolean
`extensions.worktreeConfig` is *true* — matches git's actual read rule, including at
`core.repositoryformatversion = 0`, and the invalid-boolean branch maps git's own
fatal setup error to one per-repo `error` row. Three narrower divergences remain
(F1–F3), plus two observability gaps (F4–F5) that are advisory only. No blocker to C1.

## Git read rules (observed)

### Location and gate

- `$GIT_DIR/config.worktree` is "optional and is only searched when `extensions.worktreeConfig`
  is present in $GIT_DIR/config." — git-config(1), FILES
  <https://git-scm.com/docs/git-config> (accessed 2026-10-20). The prose says "present";
  the authoritative `extensions.worktreeConfig` entry is value-aware: "If enabled, then
  worktrees will load config settings from the `$GIT_DIR/config.worktree` file" — same page.
- Order/override: "The settings in the `config.worktree` file will override settings from any
  other config files." — same page. git-worktree(1) DETAILS: "When `extensions.worktreeConfig`
  is enabled, the config file `.git/worktrees/<id>/config.worktree` is read after `.git/config`
  is." <https://git-scm.com/docs/git-worktree> (accessed 2026-10-20).
- Main vs linked: "`$GIT_COMMON_DIR` and `$GIT_DIR` are the same for the main working tree"
  (git-config(1), extensions entry). So the main worktree's file is `<common>/config.worktree`;
  a linked worktree's file is `<common>/worktrees/<id>/config.worktree`.
- Source confirmation (git v2.51.0): `do_git_config_sequence` reads exactly
  `$GIT_COMMON_DIR/config` then `$GIT_DIR/config.worktree`
  (`repo_config = mkpathdup("%s/config", opts->commondir)`;
  `worktree_config = mkpathdup("%s/config.worktree", opts->git_dir)`;
  read only under `repo->repository_format_worktree_config`) —
  <https://github.com/git/git/blob/v2.51.0/config.c#L1504-L1558> (accessed 2026-10-20).
  A linked admin's own `$GIT_DIR/config` is **not** in that read set.

### repositoryformatversion

No version gate for this extension. setup.c routes `extensions.worktreeConfig` through
`handle_extension_v0`, whose comment reads: "It handles extensions which are respected even in
v0-format repositories for historical compatibility."
<https://github.com/git/git/blob/v2.51.0/setup.c#L608-L638> (accessed 2026-10-20).
`verify_repository_format` rejects only *v1-only* extensions (`objectFormat`,
`compatObjectFormat`, `refStorage`, `relativeWorktrees`) at version 0 and *unknown*
extensions at version ≥ 1 — <https://github.com/git/git/blob/v2.51.0/setup.c#L857-L891>.
gitrepository-layout(5) is consistent: "a git implementation which supports version 1 MUST
also read any configuration keys found in the `extensions` section"
<https://git-scm.com/docs/gitrepository-layout> (accessed 2026-10-20).
Therefore gating the file read on `core.repositoryformatversion` would be wrong; the census
does not, and is correct.

### Invalid boolean

`extensions.worktreeConfig` is parsed with `data->worktree_config = git_config_bool(var, value)`
(setup.c#L628-L630); `git_config_bool` does
`die(_("bad boolean config value '%s' for '%s'"), value, name)` when the value does not parse
<https://github.com/git/git/blob/v2.51.0/config.c#L1264-L1270> (accessed 2026-10-20).
Effect: **repository setup dies**, exit 128, before any command work — for every command that
opens the repo, and for every worktree, because the key comes from the common config.
`git config --file` performs no repo setup, so it does not die on unrelated keys; with
`--type=bool` it calls the same `git_config_bool` (builtin/config.c#L283-L284) and dies on the
same value. That is exactly the probe the census uses.

Doc anchoring for `--get`/`--type`: "If key is present multiple times in the configuration,
emits the last value." (git-config(1), `get`); `--type` "ensure that incoming and outgoing
values are canonicalize-able" (same page). Implementation detail checked because it decides
whether a *shadowed* invalid occurrence is missed: `collect_config` runs `format_config` for
every matching value, so `--get --type=bool` type-checks all occurrences and only prints the
last — <https://github.com/git/git/blob/v2.51.0/builtin/config.c#L341-L366>. Same shape in
v2.40.0. So the census probe validates every occurrence, like git's format parser.

## Relation to census lines

| Git rule | Census |
|---|---|
| extension true enables the file; false/off/empty disables; bare key = true | 633–640: bare → `CFG_WT_ENABLED=1`; otherwise `git config --file … --type=bool --get`; `true` → 1 else 0. Matches `git_parse_maybe_bool` (bare/NULL = true, empty = false). |
| file location: `$GIT_DIR/config.worktree`, `$GIT_COMMON_DIR/config.worktree` for main | 676–680 (`guard_git_config` scans `$dir/config` then `guard_wt_config "$dir"`); main worktree `dir == commondir` (line 771). Correct. |
| linked worktree: common config gates, `<admin>/config.worktree` is read | 741 (`guard_git_config "$admin" "$CFG_WT_ENABLED"`), 789–790 and 828–829 (`guard_git_config "$commondir"` then `guard_wt_config "$first"`). Correct file, correct gate source. |
| invalid boolean fatal at setup | 635–636 soft-fails with `git-config-unparsed`; 1086–1090 emits `config-unsupported: git-config-unparsed (<repo>)` and one `error` row, exit 0. Faithful and cheaper than letting every later git call die. |
| version 0 honors the extension | no `core.repositoryformatversion` condition anywhere in the scan. Correct; fixture `r-wtc-hostile` (config `[extensions] worktreeConfig = true`, no version) expects exit 2, i.e. the v0 read is exercised. |
| `core.excludesFile`/`core.attributesFile` can live in config.worktree and are effective for status | `scan_config_file` handles them (619–625) on the same file, before `status_info_file` queries `git config --get` (876). Guard precedes use. |

Checked non-findings (deliberately tested against the code): bare key (634) equals
`git_config_bool(NULL)=1`; empty value parses false both in git and via `--type=bool`;
missing or unreadable file — `[ -e ]`+`tr` failure path yields the same soft row git's
`access_or_die`/open failure would make fatal; `--no-includes` is correct because the census
follows includes itself (and resolves relative include paths against the including file,
`${cfg%/*}` at 611, which is git's rule).

## Findings (advisory)

**F1 — symlinked `config.worktree` is a whole-run exit 2, stricter than both git and the
script's own contract.** Lines 657–659 call `protected_fail "git-metadata-symlink"` on any
symlink at `<gitdir>/config.worktree`, before resolution, whenever the extension is enabled.
Git follows the symlink. The header contract (lines 86–88) and `guard_git_links` (490–503)
permit git-metadata symlinks that resolve *inside* the gitdir; a dotfiles-managed
`config.worktree` symlink therefore aborts the entire census while an intra-gitdir symlink is
policy-legal everywhere else. Also inconsistent with the degrade list at line 97, where a
hardlinked `config.worktree` is a soft `error` row (`guard_config_file_kind`, 561–569).
Confidence: high on code path; medium on real-world frequency.

**F2 — linked admin's `$GIT_DIR/config` is scanned although git never reads it.** In the
commondir/gitfile paths the census calls `guard_git_config "$admin"` (771, 828) before the
common config; inside, line 673–679 scans `$admin/config` and line 680 `$admin/config.worktree`
with the flag still 0. Git's read set is `$COMMON/config` + `$GIT_DIR/config.worktree`
(config.c#L1522-L1558), so a file at `.git/worktrees/<id>/config` is invisible to git but can
produce a per-repo `error` row or an `include-protected` exit 2 for the whole run. Git never
creates that path, so likelihood is low; the over-scan is the only divergence. Confidence: high.

**F3 — `CFG_WT_ENABLED` is global and is mutated by files/conditions git would not evaluate.**
`scan_config_file` sets it from any scanned file, including `config.worktree` itself and
`includeIf` targets whose condition is false. Git's gate comes only from the common config
with conditions honored ("`includeIf` sections may be ignored if their condition does not
evaluate to true", git-config(1)). Consequences: (a) a non-matching include setting
`worktreeConfig=false` after `true` flips the flag for the linked-worktree pre-scan at 741
(mitigated because `worktree_extra_flags` re-guards each worktree via `guard_git_surface` and
`git worktree list` does not read worktree config); (b) the opposite direction opens a
`config.worktree` git would never open, which can yield a spurious `error` row or, if that
file holds a protected include, a spurious exit 2 — the only harmful-for-operability
direction. The fixture pins condition-blind *path refusal* ("includeIf conditions are not
evaluated for safety") but does not pin condition-blind *extension state*; no fixture carries
`extensions.worktreeConfig` inside a non-matching include. Confidence: high on code; medium on
whether this is intended policy (it is not stated in the header, lines 98–108).

**F4 — an invalid boolean *inside* `config.worktree` produces a false `error` row.** Git reads
`config.worktree` only after the gate is already true and its `read_worktree_config` callback
internally ignores `extensions.*` (setup.c#L586-L599); the normal sequence also never
re-validates the extension key from that file. The census scans it and applies
`--type=bool` (635), soft-failing the repo. Git would run the repo normally.
Likelihood is very low (the key is pointless there), but it is the one case where the
value-aware guard is stricter than git rather than equal. Confidence: high.

**F5 — linked-worktree config failures are swallowed as `wt-dirty` with no diagnostic.**
`worktree_extra_flags` converts a `guard_git_surface` failure on a linked worktree into
`saw_dirty=1` (1068–1071) and continues; `census_one` only prints
`config-unsupported: <reason>` for the row repo itself (1086–1090). A linked admin whose
`config.worktree` is non-regular/hardlinked/unparsable therefore degrades the main row to
`wt-dirty` with no reason line — the opposite of R3's "carry failures verbatim". The main
row's own guard is unaffected, so this is observability, not correctness. Confidence: high.

## Remaining unknowns

- Whether F1/F3(b) are deliberate fail-closed policy choices for round 16; the header states
  condition-blind *include guarding* but is silent on condition-blind extension state and on
  refusing intra-gitdir `config.worktree` symlinks. Fixture review shows no case pinning
  either, and `CONFIG_REASONS` (fixture 954–967) does not admit `git-metadata-symlink`, so
  adding a symlinked-`config.worktree` case would need that vocabulary too.
- Real-fleet frequency of a linked admin `config` file or a symlinked `config.worktree`
  (needs a census run, which this seat may not perform).

STATUS: no acceptance check executed (read-only scout); findings are static, doc- and
source-grounded; F1–F5 advisory, none contradicting the C1 read-rule claim.

## Commands

```sh
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | wc -l
cd /home/vgpnk/Projects/shokunin && git -C souji-shokunin grep -n -E 'worktreeConfig|config\.worktree|repositoryformatversion|fsmonitor|hooksPath|alternateRefsCommand|promisor|partialClone' cbf688ab2ab28e38103e5a9417ca525b5f2ed423 -- tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin && git -C souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh > /var/tmp/r16-census-cbf688.sh && wc -l /var/tmp/r16-census-cbf688.sh && sha256sum /var/tmp/r16-census-cbf688.sh
cd /home/vgpnk/Projects/shokunin && grep -n -E 'cfg_soft|guard_config_file_kind|scan_config_file|CFG_WT_ENABLED|expand_config_path|guard_config_path' souji-shokunin/tools/souji-census.sh | head -60
cd /home/vgpnk/Projects/shokunin && sed -n '840,960p' souji-shokunin/tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin && grep -n -E 'CFG_SOFT_REASON|config-unsupported|status-skipped|status-unverifiable|error' souji-shokunin/tools/souji-census.sh | sed -n '1,80p'
curl -sS https://raw.githubusercontent.com/git/git/v2.51.0/config.c | grep -n -B4 -A10 'bad boolean config value'
curl -sS https://raw.githubusercontent.com/git/git/v2.51.0/setup.c | grep -n -B6 -A10 'worktreeconfig'
curl -sS https://raw.githubusercontent.com/git/git/v2.51.0/repo-settings.c | grep -n -B4 -A16 'worktree_config'
curl -sS https://raw.githubusercontent.com/git/git/v2.51.0/config.c | grep -n -B8 -A20 'worktree_config\|config\.worktree'
curl -sS https://raw.githubusercontent.com/git/git/v2.51.0/setup.c | grep -n -B4 -A12 'worktree_config'
curl -sS https://raw.githubusercontent.com/git/git/v2.51.0/setup.c | grep -n -B5 -A30 'int verify_repository_format'
curl -sS https://raw.githubusercontent.com/git/git/v2.51.0/setup.c | grep -n 'EXTENSION_V1_ONLY\|v1_only_extensions\|EXTENSION_UNKNOWN\|extensions\.'
curl -sS https://raw.githubusercontent.com/git/git/v2.51.0/builtin/config.c | grep -n -B6 -A14 'bad boolean config value'
cd /home/vgpnk/Projects/shokunin && sed -n '380,480p' souji-shokunin/tools/souji-census.sh
curl -sS https://raw.githubusercontent.com/git/git/v2.51.0/builtin/config.c | grep -n -B4 -A10 'git_parse_maybe_bool\|CONFIG_TYPE_BOOL' | head -80
cd /home/vgpnk/Projects/shokunin && grep -n -A14 '^protected_fail()' souji-shokunin/tools/souji-census.sh
curl -sS https://raw.githubusercontent.com/git/git/v2.51.0/setup.c | sed -n '694,730p;795,830p'
curl -sS https://raw.githubusercontent.com/git/git/v2.51.0/builtin/config.c | sed -n '255,298p'
curl -sS https://raw.githubusercontent.com/git/git/v2.51.0/setup.c | sed -n '598,650p'
cd /home/vgpnk/Projects/shokunin && grep -n 'guard_worktree_registrations\|guard_git_surface\|guard_git_config' souji-shokunin/tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin && sed -n '1000,1120p' souji-shokunin/tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin && sed -n '763,840p' souji-shokunin/tools/souji-census.sh
curl -sS https://raw.githubusercontent.com/git/git/v2.51.0/builtin/config.c | grep -n -B8 -A22 'static int collect_config\|static char \*get_value\|config_get_value'
curl -sS https://raw.githubusercontent.com/git/git/v2.51.0/builtin/config.c | grep -n -A80 '^static int get_value(' | sed -n '1,110p'
curl -sS https://raw.githubusercontent.com/git/git/v2.51.0/builtin/config.c | sed -n '448,530p'
curl -sS https://raw.githubusercontent.com/git/git/v2.51.0/builtin/config.c | sed -n '341,368p'
curl -sS https://raw.githubusercontent.com/git/git/v2.51.0/setup.c | grep -n -A24 'static int read_repository_format'
cd /home/vgpnk/Projects/shokunin && sed -n '628,690p' souji-shokunin/tools/souji-census.sh | cat -n | sed 's/^/  /'
curl -sS https://raw.githubusercontent.com/git/git/v2.40.0/builtin/config.c | grep -n -A22 'static int collect_config'
curl -sS https://raw.githubusercontent.com/git/git/v2.51.0/setup.c | sed -n '646,694p'
cd /home/vgpnk/Projects/shokunin && grep -n 'guard_wt_config "\$first"\|guard_wt_config() {\|CFG_WT_ENABLED" = 1 \] || return 0\|extensions:worktreeconfig)\|config-unsupported: %s' souji-shokunin/tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin && git -C souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r15-census-config.py | grep -n 'worktree\|includeIf\|repositoryformatversion\|promisor' | head -60
cd /home/vgpnk/Projects/shokunin && sed -n '760,800p;805,835p' souji-shokunin/tools/souji-census.sh | grep -n '' | head -70
cd /home/vgpnk/Projects/shokunin && git -C souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r15-census-config.py | sed -n '1,70p'
cd /home/vgpnk/Projects/shokunin && git -C souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r15-census-config.py | sed -n '595,650p'
cd /home/vgpnk/Projects/shokunin && git -C souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r15-census-config.py | grep -n 'worktree add\|worktrees/\|linked'
cd /home/vgpnk/Projects/shokunin && git -C souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r15-census-config.py | grep -n 'r-wtc'
cd /home/vgpnk/Projects/shokunin && git -C souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r15-census-config.py | sed -n '1160,1200p'
cd /home/vgpnk/Projects/shokunin && git -C souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r15-census-config.py | sed -n '470,500p;1060,1092p'
cd /home/vgpnk/Projects/shokunin && git -C souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r15-census-config.py | grep -n -A22 '^def unsafe_repo\|^def soft_repo\|^CONFIG_REASONS'
cd /home/vgpnk/Projects/shokunin && grep -n 'config-worktree-protected\|git-metadata-symlink\|git-config-unparsed' souji-shokunin/tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin && git -C souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r15-census-config.py | sed -n '976,1000p'
cd /home/vgpnk/Projects/shokunin && grep -n 'val=$(git -C "$wt" config --get\|^count_dirty()\|^count_worktrees()\|^worktree_extra_flags()\|for rel in config HEAD\|guard_git_config "$admin"' souji-shokunin/tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin && grep -n 'core:excludesfile|core:attributesfile\|core:worktree)\|include:path|includeif:path' souji-shokunin/tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin && grep -n 'if ! guard_git_surface "$cpath"\|saw_dirty=1\|wt_extra=$(worktree_extra_flags' souji-shokunin/tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin && sed -n '1064,1075p;1112,1145p' souji-shokunin/tools/souji-census.sh
```
