# Scout — `core.alternateRefsCommand` / `core.alternateRefsPrefixes` consumers

Seat: `SoujiR16.ScoutAltRefsConsumers` (read-only recon; leaf, no dispatch).
Target: `tools/souji-census.sh` at `cbf688ab2ab28e38103e5a9417ca525b5f2ed423`
(`rev-parse HEAD` returned that commit, so working-tree line numbers equal the
committed file). Access date for all URLs: **2026-10-20**.

## Question

Which git commands consume `core.alternateRefsCommand` /
`core.alternateRefsPrefixes` (receive-pack, upload-pack, fetch negotiation with
alternates)? Do any of `rev-parse`, `worktree list`, `for-each-ref`,
`rev-list`, `status`, `config`, `ls-files`, `check-attr` consume them?

## Answer — consumer inventory (git v2.51.0, cross-checked master)

Implementation exists in exactly one place: `odb.c`
(`fill_alternate_refs_command`). A full-tree grep of the v2.51.0 tarball for
`odb_for_each_alternate_ref` / `for_each_alternate_ref(` yields **three call
sites only** (plus definitions/declarations in `odb.c`/`odb.h`):

| Consumer path | Entry point (v2.51.0) | Effect |
|---|---|---|
| `receive-pack` ref advertisement (push server side) | `builtin/receive-pack.c:362` inside `write_head_info()` (344), callback `show_one_alternate_ref()` (333-342) | advertises alternate tips as `.have` lines |
| `fetch-pack` negotiation (fetch client side) | `fetch-pack.c:119` `for_each_cached_alternate()`; invoked at `:358` (v0 `find_common`), `:804` (`mark_complete_local_refs`), `:1708` (v2 negotiation) | loads alternate tips into the negotiator's "have" set |
| Revision walk given `--alternate-refs` | `revision.c:1894` `add_alternate_refs_to_pending()`, entered only from `revision.c:2856-2857` on the literal option | adds alternate tips as pending revisions (`rev-list`, `log`, any shared revision parser) |

Not a consumer: **`upload-pack`** — zero references in v2.20.0, v2.45.0,
v2.50.0, v2.51.0 and master. So "fetch advertisement" does *not* consume it;
"push advertisement" (receive-pack) does; fetch *negotiation* (client
fetch-pack) does.

Mechanics (`odb.c` v2.51.0):

- `odb.c:483-487` — if `core.alternateRefsCommand` is set, `cmd->use_shell = 1`
  and the alternate repo path is appended as the argument (documented: "The
  first argument is the absolute path of the alternate."). This is arbitrary
  repo-controlled shell execution, gated only by reaching the consumer.
- `odb.c:488-499` — else `git for-each-ref --git-dir=<alt> --format=%(objectname)`;
  `core.alternateRefsPrefixes` is read **only in this else branch** (`:495-498`),
  so it has no effect when the command is set (matches git-config(1)).
- `odb.c:550-562` — second gate: the alternate path must end in `/objects` and a
  sibling `refs/` directory must exist, else the command is never spawned.
- `odb.c:569-576` — `odb_for_each_alternate_ref()` iterates the object DB's
  alternates; with no alternates, neither key is consulted.

Master still has the same three callers (`builtin/receive-pack.c:346`,
`fetch-pack.c:119`, `revision.c:1891`; implementation `odb.c:121/133`).

## Confirmation for the named commands

| Command | Census site (cbf688ab) | Consumes? | Basis |
|---|---|---|---|
| `rev-parse` | `tools/souji-census.sh:1104` (`--is-inside-work-tree`) | **no** | `builtin/rev-parse.c` contains zero `alternate_ref`/`alternateRefs`; not one of the three call sites |
| `worktree list` | `:852`, `:1076` | **no** | `builtin/worktree.c` zero references |
| `for-each-ref` | `:858` (`refs/remotes` names) | **no** | `builtin/for-each-ref.c` zero; it is the *fallback target* (`odb.c:492`), not a consumer |
| `rev-list` | `:862`, `:866` | **no as invoked** | consumer is option-gated: `revision.c:2856-2857` only on `--alternate-refs`; census passes only `--count --branches` / `--not --remotes`, and the script contains no `--alternate-refs` (grep: none) |
| `status` | `:947-953` | **no** | `cmd_status` lives in `builtin/commit.c:1532`; `wt-status.c` zero references |
| `config` | `:589`, `:592`, `:635`, `:876`, `:910` | **no** | `builtin/config.c` zero; it reads/prints values, never evaluates this one |
| `ls-files` | `:922-923` | **no** | `builtin/ls-files.c` zero |
| `check-attr` | `:924-925` | **no** | `builtin/check-attr.c` zero |

Selftest-only plumbing (`git add`, `write-tree`, `symbolic-ref`, `update-ref`;
`:1402-1516`) is covered by the same whole-tree caller proof: none route to the
three consumers.

## Relation to the census claims

- Header rationale `tools/souji-census.sh:108-109`: "core.alternateRefsCommand
  (consumed only when advertising alternate refs, which no census command
  does)".
- Inline rationale `tools/souji-census.sh:640-643`: same claim with
  "(fetch/push)".
- Fixture repeats it: `tests/fixtures/r15-census-config.py:1203-1205`.

The **conclusion** is correct for the current command set: no census command is
receive-pack, no census command is a fetch, and the two `rev-list` calls omit
`--alternate-refs`. Accepted values are therefore inert today.

The **stated reason is wrong**, and has been for years:

1. `upload-pack` (fetch advertisement) does not consume it; `receive-pack`
   (push advertisement) does.
2. `fetch-pack` negotiation consumes it since at least v2.20.0
   (`<https://github.com/git/git/blob/v2.20.0/fetch-pack.c>` has the call;
   use `grep -c 'for_each_alternate_ref'` against that tag).
3. Any revision walk given `--alternate-refs` consumes it; the option exists in
   v2.23.0 (`revision.c` has the string; absent in v2.22.0) and is documented:
   "The set of included objects may be modified by core.alternateRefsCommand,
   etc." So "only when advertising" is false independent of the census.

## Findings

**F1 (calibration, low severity, documentation).** The three rationale sites
above should name the real consumers instead of "advertising alternate refs
(fetch/push)". Precise replacement text:

> consumed only when git enumerates alternate refs — receive-pack ref
> advertisement, fetch/fetch-pack negotiation, or a revision walk given
> `--alternate-refs`; no census command is any of these (`rev-list` here uses
> `--count --branches [--not --remotes]`, never `--alternate-refs`).

Why it matters: `core.alternateRefsCommand` is shell-executed with the scanned
repo's config (`odb.c:483-487`). A future edit that adds `git fetch` (plausible
for unpushed/behind accuracy) or switches `rev-list` to `--alternate-refs`
would turn this "accepted, inert" key into code execution during a read-only
census. The guard boundary-checks alternates (`tools/souji-census.sh:456-482`,
`:505`) but never neutralizes them, so nothing else blocks that path.

**F2 (operability, tripwire gap, low/medium).** The selftest source audit
`tools/souji-census.sh:1729` bans non-comment `git ... fetch|push|commit|branch|
checkout|reset|rebase|prune`, but not the option `--alternate-refs` — the one
non-fetch consumer a read-only command could reach. Cheap durable check:
require zero non-comment lines matching `--alternate-refs` (and optionally
`upload-pack|receive-pack`). Current script: zero matches, so the check would
pass now and fail on regression.

**F3 (test power, low).** The fixture's `SENT_AR` sentinel is non-discriminating
for this key. `tests/fixtures/r15-census-config.py:514-517` points
`core.alternateRefsCommand` at the sentinel, and `:1202-1214` asserts it never
fires — but the fixture never writes `objects/info/alternates` (grep over the
fixture finds no alternates path; only the `FL_ALTREFS` name at `:216`).
Because `odb_for_each_alternate_ref` iterates alternates (`odb.c:575`) and
requires a sibling `refs/` dir (`odb.c:556-559`), the command could not run even
if the census did call a consumer. The sentinel proves acceptance and clean
rows, not non-consumption. To make it discriminating, give `r-altrefs-cmd` an
`objects/info/alternates` pointing at a sibling fixture repo that has `refs/`
(untested suggestion; the guard resolves such targets at `:456-482`).

**F4 (completeness, informational).** `core.alternateRefsPrefixes` is absent from
the guard's accepted-value doc block; it is accepted by fall-through in
`scan_config_file` (`tools/souji-census.sh:604-646` handles only named keys). It
is inert on the same three consumers and is a documented no-op when the command
is set (`odb.c:495-498`), so no behavior change is needed; naming it beside
`alternateRefsCommand` would make the accepted set complete.

## Verdict

`core.alternateRefsCommand`/`core.alternateRefsPrefixes` are **inert for the
exact census command set at cbf688ab** (structural proof: only three upstream
callers, none invoked). C1's alternateRefs sub-claim holds. The script/fixture
*wording* overstates why (F1), the source-audit tripwire misses the only
option-level consumer (F2), and the fixture's inert-sentinel evidence is vacuous
without alternates (F3). No code change is required for correctness today;
F1-F3 are cheap hardening for the next edit.

Confidence: **high** for git v2.51.0 and master (full-tree caller grep plus
source reading); **high** for the negative list (whole-tree caller proof);
**medium** for older releases (spot-checked v2.20.0, v2.45.0, v2.50.0; fetch-pack
consumer present since ≤v2.20.0, `--alternate-refs` since v2.23.0).

Remaining unknowns: installed host git version was not probed (man page
`/usr/share/man/man1/git.1.gz` was not text-readable through the tool, and the
probe rule bars `git --version`); distribution patches could move call sites;
upstream may add consumers later.

## Sources (accessed 2026-10-20)

- <https://git-scm.com/docs/git-config> (2.56.0, last updated 2026-09-28):
  "When advertising tips of available history from an alternate, use the shell
  to execute the specified command instead of git-for-each-ref(1)." (20 words)
  "When listing references from an alternate, list only references that begin
  with the given prefix." (16 words)
  "If core.alternateRefsCommand is set, setting core.alternateRefsPrefixes has
  no effect." (12 words)
- <https://git-scm.com/docs/git-rev-list>:
  "Pretend as if all objects mentioned as ref tips of alternate repositories
  were listed on the command line." (19 words)
  "The set of included objects may be modified by core.alternateRefsCommand,
  etc." (11 words)
- <https://github.com/git/git/blob/v2.51.0/odb.c#L483> — command read,
  `use_shell = 1`, alternate path appended (`:483-487`); prefixes only in the
  fallback (`:495-498`); `refs/` gate (`:556-559`).
- <https://github.com/git/git/blob/v2.51.0/builtin/receive-pack.c#L362> —
  `odb_for_each_alternate_ref(... show_one_alternate_ref ...)` in
  `write_head_info`.
- <https://github.com/git/git/blob/v2.51.0/fetch-pack.c#L119> — negotiation
  cache; uses at `:358`, `:804`, `:1708`.
- <https://github.com/git/git/blob/v2.51.0/revision.c#L2856> — the only entry to
  `add_alternate_refs_to_pending` (v2.51.0 `:1894`), on `--alternate-refs`.
- <https://github.com/git/git/blob/master/odb.c#L121>,
  <https://github.com/git/git/blob/master/builtin/receive-pack.c#L346>,
  <https://github.com/git/git/blob/master/fetch-pack.c#L119>,
  <https://github.com/git/git/blob/master/revision.c#L2945> — master, same
  shape.
- Upstream tag tarball v2.51.0 (codeload, `git/git` refs/tags/v2.51.0): full-tree
  grep for `odb_for_each_alternate_ref|for_each_alternate_ref(` returned only
  `builtin/receive-pack.c:362`, `fetch-pack.c:119`, `odb.c` (definition),
  `odb.h` (declaration), `revision.c:1894`.

## Commands

Shell commands run, verbatim, in order:

```bash
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD; git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file -p cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | grep -n "alternate\|fsmonitor\|promisor\|partialClone\|hooksPath"
git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file -p cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | wc -l; git -C /home/vgpnk/Projects/shokunin/souji-shokunin ls-tree -r --name-only cbf688ab2ab28e38103e5a9417ca525b5f2ed423 | grep -i "census"
git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file -p cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh | sed -n '75,160p' | cat -n | sed 's/^/   /'
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh > /var/tmp/ScoutAltRefsConsumers-census.sh && awk 'NR>=600 && NR<=700 {printf "%d: %s\n", NR, $0}' /var/tmp/ScoutAltRefsConsumers-census.sh
grep -n "git " /var/tmp/ScoutAltRefsConsumers-census.sh | grep -v "^[0-9]*:#" | grep -E "git (-C|--|rev|for-each|status|config|worktree|ls-files|check-attr|rev-list|log|cat-file)"
awk 'NR>=900 && NR<=1000 {printf "%d: %s\n", NR, $0}' /var/tmp/ScoutAltRefsConsumers-census.sh
curl -sS https://raw.githubusercontent.com/git/git/master/Documentation/config/core.adoc -o /var/tmp/ScoutAltRefsConsumers-core.adoc; grep -n -A12 "alternateRefs" /var/tmp/ScoutAltRefsConsumers-core.adoc
cd /var/tmp && for f in refs.c builtin/receive-pack.c upload-pack.c revision.c builtin/for-each-ref.c builtin/rev-list.c builtin/fetch-pack.c; do out=ScoutAltRefsConsumers-$(echo "$f" | tr '/' '_'); curl -sS "https://raw.githubusercontent.com/git/git/master/$f" -o "$out"; done; grep -n "for_each_alternate_ref\|alternate_refs_prefix\|alternate_refs_command\|ALTERNATE_REFS" ScoutAltRefsConsumers-*.c
curl -sS https://raw.githubusercontent.com/git/git/master/Documentation/git-rev-list.adoc -o /var/tmp/ScoutAltRefsConsumers-rev-list.adoc; grep -n -B2 -A6 "alternate-refs" /var/tmp/ScoutAltRefsConsumers-rev-list.adoc
cd /var/tmp && grep -in "alternate" ScoutAltRefsConsumers-upload-pack.c | head -40; echo ---; grep -in "alternate" ScoutAltRefsConsumers-rev-list.adoc | head -20; echo ---; curl -sS https://raw.githubusercontent.com/git/git/master/odb.c -o ScoutAltRefsConsumers-odb.c; grep -n "alternate_ref\|alternateRefs\|alternate_refs" ScoutAltRefsConsumers-odb.c | head -40
cd /var/tmp && grep -in "alternate" ScoutAltRefsConsumers-refs.c | head -40; echo ---REVISION---; grep -n -B6 -A18 "odb_for_each_alternate_ref" ScoutAltRefsConsumers-revision.c
cd /var/tmp && grep -n "alternate-refs\|alternate_refs" ScoutAltRefsConsumers-revision.c | head; echo ---; for t in v2.50.0 v2.45.0; do for f in upload-pack.c builtin/receive-pack.c; do curl -sS "https://raw.githubusercontent.com/git/git/$t/$f" -o "ScoutAltRefsConsumers-$t-$(echo $f|tr / _)"; done; done; grep -n "odb_for_each_alternate_ref\|for_each_alternate_ref" ScoutAltRefsConsumers-v2.50.0-* ScoutAltRefsConsumers-v2.45.0-*
awk 'NR>=840 && NR<=880 {printf "%d: %s\n", NR, $0}' /var/tmp/ScoutAltRefsConsumers-census.sh; echo ---; awk 'NR>=104 && NR<=112 {printf "%d: %s\n", NR, $0}' /var/tmp/ScoutAltRefsConsumers-census.sh
cd /var/tmp && awk 'NR>=105 && NR<=215 {printf "%d: %s\n", NR, $0}' ScoutAltRefsConsumers-odb.c
cd /var/tmp && curl -sSL https://codeload.github.com/git/git/tar.gz/refs/tags/v2.51.0 -o ScoutAltRefsConsumers-git.tar.gz && mkdir -p ScoutAltRefsConsumers-src && tar -xzf ScoutAltRefsConsumers-git.tar.gz -C ScoutAltRefsConsumers-src --strip-components=1 && grep -rn "odb_for_each_alternate_ref\|for_each_alternate_ref(" ScoutAltRefsConsumers-src --include='*.c' --include='*.h'
cd /var/tmp && curl -sS https://git-scm.com/docs/git-config -o ScoutAltRefsConsumers-gitconfig.html && curl -sS https://git-scm.com/docs/git-rev-list -o ScoutAltRefsConsumers-gitrevlist.html && for f in ScoutAltRefsConsumers-gitconfig.html ScoutAltRefsConsumers-gitrevlist.html; do echo "== $f"; grep -o -E "(When advertising tips of available history from an alternate[^<]*|When listing references from an alternate[^<]*|core\.alternateRefsCommand|core\.alternateRefsPrefixes|--alternate-refs|Pretend as if all objects mentioned as ref tips of alternate[^<]*)" "$f" | sort -u; done
cd /var/tmp && for v in 2.25.0 2.26.0; do curl -sS "https://raw.githubusercontent.com/git/git/master/Documentation/RelNotes/$v.txt" -o "ScoutAltRefsConsumers-RelNotes-$v.txt"; echo "== $v"; grep -n -i "alternate" "ScoutAltRefsConsumers-RelNotes-$v.txt" | head -8; done
cd /var/tmp && awk 'NR>=85 && NR<=140 {printf "%d: %s\n", NR, $0}' ScoutAltRefsConsumers-src/fetch-pack.c; echo "=== master fetch-pack ==="; curl -sS https://raw.githubusercontent.com/git/git/master/fetch-pack.c -o ScoutAltRefsConsumers-fetch-pack-master.c; grep -n -B8 -A6 "odb_for_each_alternate_ref" ScoutAltRefsConsumers-fetch-pack-master.c
cd /var/tmp && python3 - <<'PY'
import re,html
data=open('ScoutAltRefsConsumers-gitrevlist.html',encoding='utf-8',errors='replace').read()
i=data.find('--alternate-refs')
# print a window of text around the option, stripped of tags
seg=data[max(0,i-200):i+1200]
txt=re.sub(r'<[^>]+>',' ',seg)
txt=html.unescape(re.sub(r'\s+',' ',txt))
print(txt[:1200])
PY
cd /var/tmp && for v in 2.20.0 2.21.0 2.22.0 2.23.0 2.24.0 2.25.0 2.26.0 2.27.0 2.28.0 2.29.0 2.30.0; do curl -sS "https://raw.githubusercontent.com/git/git/master/Documentation/RelNotes/$v.txt" -o "ScoutAltRefsConsumers-RN-$v.txt"; m=$(grep -n -i "alternate-refs\|alternateRefs" "ScoutAltRefsConsumers-RN-$v.txt" | head -4); [ -n "$m" ] && { echo "== $v"; echo "$m"; }; done; true
cd /var/tmp && for t in v2.20.0 v2.30.0 v2.39.0 v2.45.0; do curl -sS "https://raw.githubusercontent.com/git/git/$t/fetch-pack.c" -o "ScoutAltRefsConsumers-$t-fetch-pack.c"; echo "== $t fetch-pack: $(grep -c 'odb_for_each_alternate_ref\|for_each_alternate_ref(' "ScoutAltRefsConsumers-$t-fetch-pack.c")"; curl -sS "https://raw.githubusercontent.com/git/git/$t/upload-pack.c" -o "ScoutAltRefsConsumers-$t-upload-pack.c"; echo "   upload-pack: $(grep -c 'alternate_ref' "ScoutAltRefsConsumers-$t-upload-pack.c")"; done
cd /var/tmp && for t in v2.20.0 v2.25.0 v2.26.0 v2.30.0; do for f in Documentation/rev-list-options.txt Documentation/rev-list-options.adoc; do curl -sfS "https://raw.githubusercontent.com/git/git/$t/$f" -o "ScoutAltRefsConsumers-$t-rlo"; done; echo "== $t: $(grep -c 'alternate-refs' "ScoutAltRefsConsumers-$t-rlo" 2>/dev/null || echo 0)"; done
cd /var/tmp && grep -n -B4 -A10 "for_each_cached_alternate" ScoutAltRefsConsumers-src/fetch-pack.c | head -80
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git cat-file -p cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r15-census-config.py | grep -n "alternateRefs\|alternate"
cd /var/tmp && grep -nE "git [^;|)]*(fetch|push|clone|upload-pack|receive-pack|rev-list|for-each-ref|worktree|status|ls-files|check-attr|rev-parse|config)" ScoutAltRefsConsumers-census.sh | grep -v "^\s*#" | sed -n '1,80p'
cd /var/tmp && grep -n "add_alternate_refs_to_pending\|\"--alternate-refs\"" ScoutAltRefsConsumers-src/revision.c; echo ---; for t in v2.21.0 v2.22.0 v2.23.0 v2.24.0; do curl -sfS "https://raw.githubusercontent.com/git/git/$t/Documentation/rev-list-options.txt" -o "ScoutAltRefsConsumers-$t-rlo" && echo "== $t: $(grep -c 'alternate-refs' ScoutAltRefsConsumers-$t-rlo)"; done
cd /var/tmp/ScoutAltRefsConsumers-src && awk 'NR>=470 && NR<=585 {printf "%d: %s\n", NR, $0}' odb.c
cd /var/tmp/ScoutAltRefsConsumers-src && awk 'NR>=330 && NR<=375 {printf "%d: %s\n", NR, $0}' builtin/receive-pack.c; echo "=== revision ==="; awk 'NR>=1880 && NR<=1900 {printf "%d: %s\n", NR, $0}' revision.c
cd /var/tmp && curl -sS https://raw.githubusercontent.com/git/git/master/Documentation/RelNotes/2.23.0.txt -o ScoutAltRefsConsumers-RN-2.23.0.txt; grep -n -i -B2 -A2 "alternate" ScoutAltRefsConsumers-RN-2.23.0.txt | head -20
cd /var/tmp && for t in v2.22.0 v2.23.0; do curl -sS "https://raw.githubusercontent.com/git/git/$t/revision.c" -o "ScoutAltRefsConsumers-$t-revision.c"; echo "== $t: $(grep -c 'alternate-refs' "ScoutAltRefsConsumers-$t-revision.c")"; done; echo "== census fetch/push tokens:"; grep -nE "\b(fetch|push|clone|upload-pack|receive-pack)\b" ScoutAltRefsConsumers-census.sh | grep -v "^[0-9]*: *#" ; echo "== census --alternate-refs:"; grep -n "alternate-refs" ScoutAltRefsConsumers-census.sh || echo none
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git cat-file -p cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r15-census-config.py | awk 'NR>=140 && NR<=150 {printf "%d: %s\n", NR, $0} NR>=1195 && NR<=1215 {printf "%d: %s\n", NR, $0}'
ls -d /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1 2>/dev/null || echo missing
cd /var/tmp && grep -rn "alternateRefs" ScoutAltRefsConsumers-src --include='*.c' --include='*.h' --include='*.txt' --include='*.adoc' | grep -v t/ | head -20
awk 'NR>=520 && NR<=600 {printf "%d: %s\n", NR, $0}' /var/tmp/ScoutAltRefsConsumers-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git cat-file -p cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r15-census-config.py | awk 'NR>=500 && NR<=530 {printf "%d: %s\n", NR, $0}'; git cat-file -p cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r15-census-config.py | grep -n "altrefs-sentinel\|altrefs.sh\|SENTINEL" | head -20
awk 'NR>=1715 && NR<=1750 {printf "%d: %s\n", NR, $0}' /var/tmp/ScoutAltRefsConsumers-census.sh
grep -n "rev-list\|for-each-ref\|worktree list" /var/tmp/ScoutAltRefsConsumers-census.sh | sed -n '1,40p'; echo ===; awk 'NR>=108 && NR<=110 {printf "%d: %s\n", NR, $0}' /var/tmp/ScoutAltRefsConsumers-census.sh
cd /var/tmp/ScoutAltRefsConsumers-src && for f in builtin/rev-parse.c builtin/worktree.c builtin/for-each-ref.c builtin/status.c wt-status.c builtin/config.c builtin/ls-files.c builtin/check-attr.c builtin/rev-list.c upload-pack.c; do printf '%-28s alternate_ref=%s alternateRefs=%s\n' "$f" "$(grep -c 'alternate_ref' $f)" "$(grep -c 'alternateRefs' $f)"; done
cd /var/tmp/ScoutAltRefsConsumers-src && grep -n "alternate" builtin/rev-parse.c builtin/worktree.c builtin/status.c wt-status.c builtin/config.c builtin/ls-files.c builtin/check-attr.c builtin/rev-list.c upload-pack.c | head -20; echo "exit=$?"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git cat-file -p cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tests/fixtures/r15-census-config.py | grep -n "alternates\|FL_ALTREFS\|UNSAFE / \"r-altrefs"
cd /var/tmp/ScoutAltRefsConsumers-src && printf '%-24s %s\n' "builtin/commit.c" "$(grep -c 'alternate_ref\|alternateRefs' builtin/commit.c)"; grep -n "cmd_status\|include.*status" builtin/commit.c | head -5
cd /var/tmp/ScoutAltRefsConsumers-src && grep -n -A12 "void strvec_pushv" strvec.c; echo ===; grep -n -A18 "int repo_config_get_value(" config.c
cd /var/tmp/ScoutAltRefsConsumers-src && grep -n -B3 -A22 "int git_config_get_value(" config.c | head -40
awk 'NR>=486 && NR<=518 {printf "%d: %s\n", NR, $0}' /var/tmp/ScoutAltRefsConsumers-census.sh
awk 'NR>=456 && NR<=484 {printf "%d: %s\n", NR, $0}' /var/tmp/ScoutAltRefsConsumers-census.sh
rm -rf /var/tmp/ScoutAltRefsConsumers-* /var/tmp/ScoutAltRefsConsumers-src && ls -d /var/tmp/ScoutAltRefsConsumers* 2>/dev/null || echo cleaned
```

Tool reads (not shell commands): `/usr/share/doc/git` (absent),
`https://git-scm.com/docs/git-config`, `/usr/share/man/man1/git.1.gz`,
`/usr/share/man/man1/git.1.gz:1-25` (size-only render; version not extractable).
