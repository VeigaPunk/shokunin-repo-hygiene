# Scout — host git version vs git-scm.com docs (round 16, w1)

Scope: recurrence recon only. No edits outside this report; no test run.

## Verdict

**The item's premise is stale: the host runs git 2.56.0, not 2.55.** git-scm.com serves
2.56.0, so the served docs *are* the installed version's docs (no cross-version gap to
reconcile). Every r16 cited behavior I checked is documented identically in the served 2.55
and 2.56 pages, so even the stated 2.55 baseline would have matched. The only 2.56-only
doc surface touching the census is `includeIf "worktree:..."`, and it is inert for
`tools/souji-census.sh` (see below). One portability floor is undocumented by the script:
`GIT_NO_LAZY_FETCH` exists only from git 2.45.

HEAD of the lane equals the declared revision (observed):
`git rev-parse HEAD` -> `cbf688ab2ab28e38103e5a9417ca525b5f2ed423`, so the line numbers
below are the cited commit's lines.

## Observed facts

| Item | Observed value |
|---|---|
| `git --version` | `git version 2.56.0` |
| Binary / package | `/usr/bin/git`, pacman `git 2.56.0-1`, mtime 2026-09-28 |
| `git version --build-options` | `built from commit: a018953688f1b10bddf91bff8747068f5f4746a4` |
| git-scm.com "Latest version" | "git last updated in 2.56.0"; 2.56.0 dated **2026-09-28** (2.55.0 dated 2026-06-29) |
| Local man pages | `git-config(1)` is 2.56.0 and carries the same `core.hooksPath` `/dev/null` paragraph (man lines 2456-2459) and the same `GIT_NO_LAZY_FETCH` entry in `git(1)` (man lines 1390-1392) |

Sources, all accessed **2026-10-20**:
`https://git-scm.com/docs/git`, `https://git-scm.com/docs/git-config/{2.55.0,2.56.0}`,
`https://git-scm.com/docs/gitattributes/{2.55.0,2.56.0}`,
`https://git-scm.com/docs/git/{2.31.0,2.32.0,2.44.0,2.45.0,2.46.0,2.54.0,2.55.0,2.56.0}`,
`https://git-scm.com/docs/git-config/{2.19.0,2.20.0}`,
`https://raw.githubusercontent.com/git/git/master/Documentation/RelNotes/2.56.0.adoc`.

## Per-behavior check (script line -> doc support)

All quotes <=25 words. "identical" = the served 2.55 and 2.56 text for that key matched;
verified by extracting the key paragraphs from both pages.

1. **`core.hooksPath` inert / overridden on every status** — `tools/souji-census.sh:101-102`,
   `:948`. 2.56: "You can also disable all hooks entirely by setting core.hooksPath to
   /dev/null." Identical in 2.55; local 2.56 man page agrees. The script's
   `-c core.hooksPath=/dev/null` is the documented per-command form.
2. **`core.fsmonitor=false`** — `:101-102`, `:947`. 2.56 documents the variable as
   boolean-or-path; `false` is a valid boolean. Identical in 2.55.
3. **`core.excludesFile` / `core.attributesFile`, XDG defaults** — `:91-93`, `:937-938`,
   `:948-949`. 2.56: "Defaults to $XDG_CONFIG_HOME/git/ignore" and "Its default value is
   $XDG_CONFIG_HOME/git/attributes". Identical in 2.55. The script substitutes its own
   computed values via `-c`, so its own boundary check is what governs.
4. **`include.path` / `includeIf.*.path`, `%s(prefix)`, `~user`** — `:88-96`, `:605-618`.
   2.56: "the remainder is interpreted as a path relative to Git's "runtime prefix"" and
   "relative path ... relative to the configuration file in which the include directive was
   found". `%(prefix)` occurs 4x in both 2.55 and 2.56. The script's soft refusal of
   `~user`/`%(prefix)` (`cfg_soft git-config-unsupported`) is therefore conservative, not
   stale, and version-independent.
5. **`extensions.worktreeConfig` + `config.worktree`** — `:89-90`, `:652-681`. 2.56:
   "config.worktree is read from or written to if extensions.worktreeConfig is enabled."
   Identical in 2.55. Floor: the key is absent from the 2.19.0 page, present in 2.20.0.
6. **`remote.*.promisor`, `extensions.partialClone`, `GIT_NO_LAZY_FETCH`** — `:105-107`,
   `:147`, `:643-644`. 2.56: "Setting this Boolean environment variable to true tells Git
   not to lazily fetch missing objects from the promisor remote on demand." The
   `partialClone` extensions heading occurs once in both 2.55 and 2.56. **Floor: the
   `GIT_NO_LAZY_FETCH` entry is absent from the 2.44.0 `git(1)` page and present in 2.45.0**
   (2.46.0 and 2.54.0 also present).
7. **`core.alternateRefsCommand` inert** — `:107-109`. 2.56: "When advertising tips of
   available history from an alternate, use the shell to execute the specified command".
   Identical in 2.55; no census call advertises alternate refs.
8. **`filter.<driver>.clean|smudge|process` status skip** — `:97-100`, `:922-930`.
   2.56: "If the filter command (a string value) is defined via filter.<driver>.process".
   `filter.<driver>.process` occurs 2x in both 2.55 and 2.56; `required` semantics match.
9. **CLI/plumbing used** — `git config --file --no-includes --list -z` (`:589`, `:592`),
   `--type=bool` (`:635`), `git worktree list [--porcelain]` (`:852`, `:1076`),
   `git for-each-ref --format='%(refname)' refs/remotes` (`:858`),
   `git rev-list --count --branches --not --remotes` (`:862`, `:866`),
   `git status --porcelain --ignore-submodules=all -- .` (`:949`). `--no-includes` occurs
   on both 2.55 and 2.56 config pages; none of these flags is 2.56-gated.

## Version gaps that matter

* **On this host: none.** Installed 2.56.0 == served 2.56.0 == local man 2.56.0; every cite
  above is supported.
* **Silent floors (operability risk if the tool is run on another host):**
  * git < **2.45**: `GIT_NO_LAZY_FETCH` is ignored [INFERENCE from its absence in 2.44.0
    docs and presence in 2.45.0]. Then the header claim at `:105-107`/`:643-644` that
    promisor/partial-clone configs "cannot fetch under GIT_NO_LAZY_FETCH=1" is false, and a
    `status`/`rev-list` could lazily fetch (network + credential use).
  * git < **2.32**: `GIT_CONFIG_GLOBAL`/`GIT_CONFIG_SYSTEM` are ignored [INFERENCE: absent
    in 2.31.0 docs, present in 2.32.0]. The "Global/system git config ... cleared" claim at
    `:112` and the exports at `:143` would silently not hold.
  * git < **2.20**: `extensions.worktreeConfig` absent; an older git would not read
    `config.worktree` at all, so the script's pre-guard is stricter than git - no exposure.
  * The script has **no `git --version` gate** (grep for a version assertion in
    `tools/souji-census.sh` returned nothing), so none of these floors is enforced or stated.

## 2.55 -> 2.56 doc surface intersecting the script

* `includeIf "worktree:<dir>"` / `includeIf "worktree/i:..."` are **new in 2.56**:
  the literal `worktree:` occurs **0x** on the served 2.55 config page and **5x** on 2.56;
  RelNotes 2.56: "has been taught to use the location of the worktree in its condition."
  **Inert for the census** for two independent reasons: (a) the repo-local scan matches
  `includeif:path` regardless of condition and guards every target (`:605-618`); (b)
  global/system config is disabled (`:143`), so a global `includeIf "worktree:..."` is
  never read by any census git call.
* 2.56 RelNotes changes that touch the census call surface are non-semantic for its TSV:
  "The enumeration of untracked and ignored files in 'git status' has been optimized by
  avoiding quadratic complexity" (performance only); `excludes_file` and other globals
  were migrated "into the per-repository structure" (internal); the `git status`
  behind-branch advice text changed (stderr, not parsed); new
  `promisor.acceptFromServerURL`/`checkFields`/`remote.<name>.advertisedAs` are fetch-time
  only; `-h` now exits 0 instead of 129 (unused).
* `hook.<event>.enabled` occurs 2x in **both** 2.55 and 2.56; irrelevant anyway because
  `core.hooksPath=/dev/null` disables all hooks entirely per the documented paragraph.

## Remaining unknowns

* I did not execute the census or any git command that applies these configs to a real
  repository (probe rule). Behavior claims above are doc-grounded; the only empirical
  cross-check is that the installed man pages (2.56.0, commit a0189536) match the served
  2.56 text at the two most load-bearing spots (`GIT_NO_LAZY_FETCH`, `hooksPath=/dev/null`).
* I did not locate any lane text asserting "installed 2.55"; the premise's origin is
  outside this item's read scope. The measured value is 2.56.0.

STATUS: no host version/doc gap; item premise "installed 2.55" is false - installed is git 2.56.0 (pacman 2.56.0-1), matching served 2.56.0 docs.

## Commands

All bash calls, verbatim:

```bash
git --version; echo "---"; git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD; echo "---"; git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file -t cbf688ab2ab28e38103e5a9417ca525b5f2ed423; echo "---"; git -C /home/vgpnk/Projects/shokunin/souji-shokunin cat-file -s cbf688ab2ab28e38103e5a9417ca525b5f2ed423:tools/souji-census.sh
```

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -E 'hooksPath|fsmonitor|attributesFile|excludesFile|alternateRefsCommand|partialClone|promisor|worktreeConfig|config\.worktree|include|filter\.|GIT_NO_LAZY_FETCH|GIT_OPTIONAL_LOCKS|ignore-submodules|set -n|nounset' tools/souji-census.sh | head -100
```

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log -1 --format='%H %ci %s' cbf688ab2ab28e38103e5a9417ca525b5f2ed423; echo '---'; git log --oneline -8 -- tools/souji-census.sh
```

```bash
git help --no-man-viewer -a 2>/dev/null | head -3; echo '---'; git version --build-options 2>/dev/null; echo '---'; man git 2>/dev/null | col -b | grep -n -A6 'GIT_NO_LAZY_FETCH' | head -30
```

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'git --version\|version\b' tools/souji-census.sh | grep -v '^#' | head -20; echo '--- git calls ---'; grep -nE '\bgit (-C |config |rev-list|status|worktree|for-each-ref|cat-file|rev-parse)' tools/souji-census.sh | head -40
```

```bash
cd /tmp && curl -sS https://git-scm.com/docs/git-config/2.56.0 -o /tmp/gc256.html && curl -sS https://git-scm.com/docs/git-config/2.55.0 -o /tmp/gc255.html && ls -l /tmp/gc256.html /tmp/gc255.html
```

```bash
cd /tmp && for v in 2.56.0 2.55.0 2.54.0; do printf '%s: ' "$v"; curl -sS "https://git-scm.com/docs/git/$v" | grep -o 'GIT_NO_LAZY_FETCH' | head -1 || echo MISSING; done; echo '--- githooks 2.56 ---'; curl -sS https://git-scm.com/docs/githooks/2.56.0 | sed 's/<[^>]*>//g' | grep -n -A3 -B3 'dev/null' | head -30
```

```bash
man githooks 2>/dev/null | col -b | grep -n -B4 -A6 'dev/null' | head -40; echo '=== config local ==='; man git-config 2>/dev/null | col -b | grep -n -B2 -A4 'dev/null' | head -30
```

```bash
man git-config 2>/dev/null | col -b | grep -n -B3 -A8 'disable all hooks'
```

```bash
cd /tmp && for f in gc255.html gc256.html; do echo "=== $f ==="; python3 - "$f" <<'PY'
import sys,re,html
s=open(sys.argv[1],encoding='utf-8',errors='replace').read()
s=re.sub(r'<[^>]+>','',s); s=html.unescape(s)
for m in re.finditer(r'/dev/null', s):
    i=m.start(); print(repr(s[max(0,i-320):i+220])); print('---')
PY
done
```

```bash
cd /tmp && for v in 2.44.0 2.45.0 2.46.0; do printf '%s: ' "$v"; curl -sS "https://git-scm.com/docs/git/$v" | grep -c 'GIT_NO_LAZY_FETCH'; done; echo '=== partialClone in 2.56 config ==='; python3 - <<'PY'
import re,html
s=open('/tmp/gc256.html',encoding='utf-8',errors='replace').read()
s=re.sub(r'<[^>]+>','',s); s=html.unescape(s)
for m in re.finditer(r'partialclone|partialClone', s, re.I):
    i=m.start(); print(repr(s[max(0,i-260):i+260])); print('----')
PY
```

```bash
cd /tmp && for v in 2.31.0 2.32.0; do printf 'GIT_CONFIG_GLOBAL %s: ' "$v"; curl -sS "https://git-scm.com/docs/git/$v" | grep -c 'GIT_CONFIG_GLOBAL'; done; echo '--- worktreeConfig ---'; for v in 2.19.0 2.20.0; do printf '%s: ' "$v"; curl -sS "https://git-scm.com/docs/git-config/$v" | grep -c 'extensions.worktreeConfig'; done
```

```bash
curl -sS https://raw.githubusercontent.com/git/git/master/Documentation/RelNotes/2.56.0.adoc -o /tmp/rn256.txt; wc -l /tmp/rn256.txt; grep -n -iE 'status|worktree|fsmonitor|hooksPath|attributes|excludes|promisor|partial|include|config\.worktree|rev-list|porcelain' /tmp/rn256.txt | head -60
```

```bash
cd /tmp && curl -sS https://git-scm.com/docs/gitattributes/2.56.0 -o /tmp/ga256.html && python3 - <<'PY'
import re,html
def txt(p):
    s=open(p,encoding='utf-8',errors='replace').read()
    s=re.sub(r'<[^>]+>','',s); s=html.unescape(s)
    return s
def grab(doc, pat, n=520):
    for m in re.finditer(pat, doc, re.I):
        i=m.start(); print(repr(doc[max(0,i-300):i+n])); print('----')
a=txt('/tmp/gc255.html'); b=txt('/tmp/gc256.html')
print('### 2.56 conditional includes / worktree')
grab(b, r'includeIf|conditional include', 600)
PY
```

```bash
cd /tmp && python3 - <<'PY'
import re,html
def txt(p):
    s=open(p,encoding='utf-8',errors='replace').read()
    s=re.sub(r'<[^>]+>','',s); s=html.unescape(s)
    return s
b=txt('/tmp/gc256.html')
for pat in [r'core\.worktree', r'%\(prefix\)']:
    print('#####',pat)
    for m in list(re.finditer(pat,b,re.I))[:4]:
        i=m.start(); print(repr(b[max(0,i-200):i+520])); print('--')
PY
echo '=== gitattributes filter ==='; python3 - <<'PY'
import re,html
s=open('/tmp/ga256.html',encoding='utf-8',errors='replace').read()
s=re.sub(r'<[^>]+>','',s); s=html.unescape(s)
for m in list(re.finditer(r'filter\.<driver>\.process', s))[:2]:
    i=m.start(); print(repr(s[max(0,i-100):i+900])); print('--')
PY
```

```bash
cd /tmp && curl -sS https://git-scm.com/docs/gitattributes/2.56.0 -o /tmp/ga256.html && python3 - <<'PY'
import re,html
s=open('/tmp/ga256.html',encoding='utf-8',errors='replace').read()
s=re.sub(r'<[^>]+>','',s); s=html.unescape(s)
for m in list(re.finditer(r'filter\.<driver>\.process', s))[:2]:
    i=m.start(); print(repr(s[max(0,i-120):i+800])); print('--')
for m in list(re.finditer(r'required', s))[:3]:
    i=m.start(); print('REQ>',repr(s[max(0,i-260):i+320])); print('--')
PY
```

```bash
cd /tmp && python3 - <<'PY'
import re,html
def txt(p):
    s=open(p,encoding='utf-8',errors='replace').read(); s=re.sub(r'<[^>]+>','',s); return html.unescape(s)
a=txt('/tmp/gc255.html'); b=txt('/tmp/gc256.html')
for label,doc in (('2.55',a),('2.56',b)):
    print(label,'includeIf worktree:', doc.count('worktree:'), '| partialClone heading:', doc.count('\npartialClone \n'), '| %(prefix):', doc.count('%(prefix)'))
PY
echo '=== local man extensions.partialClone ==='; man git-config 2>/dev/null | col -b | grep -n -A6 'extensions.partialClone' | head -20
```

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -E 'GIT_OPTIONAL_LOCKS=0|GIT_CONFIG_GLOBAL|GIT_CONFIG_NOSYSTEM|GIT_NO_LAZY_FETCH|GIT_TERMINAL_PROMPT|no-includes|ignore-submodules=all|core\.hooksPath=/dev/null|worktree list --porcelain|for-each-ref|rev-list --count' tools/souji-census.sh
```

```bash
command -v git; type -a git 2>/dev/null | head -5; pacman -Q git 2>/dev/null; echo '---'; ls -l /usr/bin/git 2>/dev/null; ls -l /usr/local/bin/git 2>/dev/null || true
```

```bash
cd /tmp && python3 - <<'PY'
import re,html
def txt(p):
    s=open(p,encoding='utf-8',errors='replace').read(); s=re.sub(r'<[^>]+>','',s); return html.unescape(s)
a=txt('/tmp/gc255.html'); b=txt('/tmp/gc256.html')
for label,doc in (('2.55',a),('2.56',b)):
    print(label, 'hook.<event>.enabled:', doc.count('hook.<event>.enabled'), '| --no-includes:', doc.count('--no-includes'), '| core.hooksPath:', doc.count('core.hooksPath'))
PY
curl -sS https://git-scm.com/docs/gitattributes/2.55.0 -o /tmp/ga255.html && python3 - <<'PY'
import re,html
def txt(p):
    s=open(p,encoding='utf-8',errors='replace').read(); s=re.sub(r'<[^>]+>','',s); return html.unescape(s)
a=txt('/tmp/ga255.html'); b=txt('/tmp/ga256.html')
for label,doc in (('2.55',a),('2.56',b)):
    print(label, 'filter.<driver>.process:', doc.count('filter.<driver>.process'), '| git-filter-client:', doc.count('git-filter-client'))
PY
```

Non-shell tools used: one `eval` Python cell (extracting the cited config-key paragraphs
from `/tmp/gc255.html` and `/tmp/gc256.html`, no shell), and `read` on the URL
`https://git-scm.com/docs/git`, on `tools/souji-census.sh:555-700`, and on
`/tmp/rn256.txt` ranges 1-70 and 325-365. No installs or updates were performed.
