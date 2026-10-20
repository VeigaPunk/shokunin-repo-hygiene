# ReopenS049 — S049 (git(1) GIT_NO_LAZY_FETCH)

Scope: falsify row S049 in `corpus/SOURCES.md:63` (worktree) against the live page
https://git-scm.com/docs/git (re-opened 2026-10-20) and the two files its teaches/used-by
claim names, at lane HEAD `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae`.

## Cells under attack

Row S049, verbatim cells:

- source: `git(1) GIT_NO_LAZY_FETCH — https://git-scm.com/docs/git`
- scope: `on-demand promisor fetch suppression only, not proof that a partial clone yields complete status`
- anchor: `web manual "git last updated in 2.56.0", opened 2026-10-20; § ENVIRONMENT VARIABLES GIT_NO_LAZY_FETCH; installed git(1) 2.56.0`
- teaches: `setting it tells git not to lazily fetch missing objects from the promisor remote on demand; the census exports it on every git call`
- status/recheck/used-by: `mined | 2026-10-20 | on-release | corpus/lessons/round-16.md`

## Observed facts

1. **Page supports the quote and the scope.** The live page (fetched 2026-10-20) carries the
   entry under the rendered `Environment Variables` heading (`<h2 id="_environment_variables">`,
   HTML line 5220). Located quote, 21 words:

   > "Setting this Boolean environment variable to true tells Git not to lazily fetch missing
   > objects from the promisor remote on demand."

   Location: § Environment Variables › `GIT_NO_LAZY_FETCH` (text-stripped page line 7402;
   also the per-command synopsis line 4378). Byte-identical sentence in the installed man page:
   `zcat /usr/share/man/man1/git.1.gz` roff lines 2127–2130. The quote count is ≤25.

2. **The negative half of the scope is supported by documented silence, swept, not guessed.**
   The whole page mentions "promisor" exactly twice: the `--no-lazy-fetch` OPTIONS entry
   (lines 4368–4374: "Do not fetch missing objects from the promisor remote on demand. Useful
   together with `git cat-file -e <object>`") and the env entry above. Neither says that a
   partial clone yields complete status, nor what happens when an object is needed and cannot
   be fetched. `scope` therefore correctly stops at suppression.

3. **Page version stamp and installed version match the anchor.** Page footer string:
   `git last updated in 2.56.0`. Host `git --version` → `git version 2.56.0`; the installed
   `git(1)` roff carries the entry at 2127–2130. The section name is written uppercase in the
   registry (`ENVIRONMENT VARIABLES`) as in existing rows S006/S036; the rendered h2 is title
   case. Same section, registry convention, not a mismatch.

4. **The teaches' implementation clause is true at HEAD.** `tools/souji-census.sh` is
   unmodified vs HEAD (`git diff --name-only HEAD -- tools/` empty) and its sha256 is
   `64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c`, matching the round
   record. `export GIT_NO_LAZY_FETCH=1` is at line 161, top level, before any executed git
   call (first non-comment git invocation is line 618; lines 589–672 are function definitions).
   There is no `env -i` and no later `unset GIT_NO_LAZY_FETCH`; the selftest wrappers use
   `env -u GIT_DIR` (lines 1613, 1615, 1724, 1740, 1755, 1777, 1786, 1798, 1809), which drops
   only `GIT_DIR`, so the export is inherited by every census git call.

5. **The claim is measured, not only read.** `tests/fixtures/r15-census-config.py:974-979`
   (safety case `R15CFG-08`) asserts that every observed spy `git` invocation carries
   `GIT_NO_LAZY_FETCH=1` and that a successful run shows git calls at all;
   `spy_git_env()` at :856-866 reads the per-call `ENV` dump. The fixture also states the
   exact boundary S049's scope names: promisor values are inert "on a COMPLETE repository"
   (:44-48), i.e. missing-object behaviour is deliberately not claimed.

6. **`tools/souji-landing-gate.py` does not use it, and S049 does not claim it does.**
   `git show HEAD:tools/souji-landing-gate.py | grep -c GIT_NO_LAZY_FETCH` → 0. The teaches
   and used-by name only the census and the round-16 lesson, so this is consistent, not a
   broken used-by.

7. **Used-by resolves.** `corpus/lessons/round-16.md:32` carries the same 21-word quote with
   the 2.56.0 stamp, and :35 attributes "C1's … lazy-fetch export" to S049. The Gate heading
   (`### Sources opened this round (URL · access 2026-10-20 · located quote ≤25 words)`)
   supplies the access date the row's `opened` cell names.

8. **Tier/status/recheck follow the registry's own precedents.** Tier A is used for primary
   official documentation throughout (S001–S011, S034–S037); community sources are B
   (`census/round-12/sources-gate.md:92`). S049 is the official git manual → A. `mined` with
   `used-by corpus/lessons/round-16.md` matches the actual citation; `on-release` matches
   every git-doc row (S001–S011, S034–S037, S042). The contract file `SOURCES-CONTRACT-v1.md`
   is not present in this lane (searched to depth 3 under the lane and one level above);
   tier meaning was checked against the r12 gate text instead.

9. **Version-floor cross-check (advisory, outside the row's cells).** The census comments
   assert `git >= 2.45` at `tools/souji-census.sh:115, :156, :684`; the row does not carry
   that floor, and its anchor cites only the 2.56.0 page. Independent check of the git-scm
   archives: `/docs/git/2.44.0` has 0 occurrences of `GIT_NO_LAZY_FETCH`;
   `/docs/git/2.45.0` has 2 (synopsis + entry, entry text identical). So the floor is real
   but is not sourced by S049's cited revision, and the census performs no runtime
   `git --version`/`--version` gate at all (`grep -n '2\.45\|2\.4[0-9]\|--version'` matches
   only the three comments). On a host with git < 2.45 the export would be inert
   `[INFERENCE]` and the census's "Accepted: any `remote.*.promisor` or
   `extensions.partialClone` value" cell (:115-117) would be ungrounded; status failures on
   such a repo would still be caught by `count_dirty()` (:1043-1046 prints `unverifiable`
   when status exits nonzero), so the failure mode is a possible lazy fetch, not a false
   "clean".

## Counterexample attempts that failed

- Quote not verbatim? No — exact 21-word sentence, web and installed roff agree.
- Scope overclaims completeness? No — page silent; the fixture also confines promisor
  cases to complete repositories.
- teaches overclaims "every git call"? No — export at :161 precedes all executed calls,
  and `R15CFG-08` asserts the env on every observed spy call.
- Wrong file claimed? No — census only; gate has zero occurrences and is not named.
- Wrong tier/status/recheck? No — matches primary-doc and git-doc-row precedents.

## Verdict

**holds** — page supports both scope and teaches; anchor, tier, status, recheck and used-by
are correct; the named claim is genuinely implemented and measured at HEAD.

STATUS: ok

Advisory calibration note (not a row failure, smallest fix named): S049's scope could carry
the `git >= 2.45` floor its named use asserts (census :115, :156, :684) — the row's 2.56.0
anchor cannot source that floor. Smallest fix: append `; git >= 2.45` to the S049 `scope`
cell (optionally cite `/docs/git/2.45.0`). Tool-side, a one-line setup refusal when
`git --version` < 2.45 would close the unenforced precondition; not needed on this host
(2.56.0).

## Commands

```
grep -n "S049" /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD; git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain | head -20
sed -n '1,30p' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
curl -sS --max-time 60 https://git-scm.com/docs/git | sed 's/></>\n</g' | grep -n -A12 'GIT_NO_LAZY_FETCH' | sed -e 's/<[^>]*>//g' | tr -s ' \n' ' ' | cut -c1-2000; echo; echo "---exit:$?"
grep -n 'GIT_NO_LAZY_FETCH' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py; echo "grep-exit:$?"; git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse --short HEAD; git --version
curl -sS --max-time 60 https://git-scm.com/docs/git | sed 's/></>\n</g' | sed -n '7370,7430p' | sed -e 's/<[^>]*>//g' | tr -s ' \n' ' '; echo; echo "=== footer/version ==="; curl -sS --max-time 60 https://git-scm.com/docs/git | grep -o -i -E 'git last updated in [0-9.]+|last updated in [0-9.]+' | sort -u
sed -n '100,170p;675,695p' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh
grep -n 'S049\|LAZY_FETCH' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/round-16.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin; grep -n 'env -i\|env -u\|env  *-\|sudo\|unset GIT_NO_LAZY_FETCH\|GIT_NO_LAZY_FETCH' tools/souji-census.sh; echo ---; grep -cn '\bgit\b' tools/souji-census.sh; echo ---; grep -n 'GIT_NO_LAZY_FETCH' /usr/share/man/man1/git.1.gz 2>/dev/null; zcat /usr/share/man/man1/git.1.gz 2>/dev/null | grep -n -A3 'GIT_NO_LAZY_FETCH' | sed 's/\\f[BIRP]//g'
curl -sS --max-time 60 https://raw.githubusercontent.com/git/git/v2.45.0/Documentation/RelNotes/2.45.0.adoc | grep -n -i -B2 -A2 'lazy.fetch\|lazy-fetch'; echo "exit:$?"
cd /home/vgpnk/Projects/shokunin/souji-shokunin; grep -n '^| S036' corpus/SOURCES.md | cut -c1-1200; echo ---; grep -rn 'SOURCES-CONTRACT' --include='*.md' corpus | head -5
cd /home/vgpnk/Projects/shokunin/souji-shokunin; find . -maxdepth 3 -name '*CONTRACT*' -not -path './.git/*' 2>/dev/null; find .. -maxdepth 2 -name 'SOURCES-CONTRACT-v1.md' 2>/dev/null | head
curl -sS --max-time 45 https://raw.githubusercontent.com/git/git/v2.45.0/Documentation/RelNotes/2.45.0.adoc | grep -n -i -E 'fetch|promisor|partial' | head -20
for t in v2.42.0 v2.43.0 v2.44.0 v2.45.0 v2.46.0; do n=$(curl -sS --max-time 45 "https://raw.githubusercontent.com/git/git/$t/Documentation/git.adoc" | grep -c 'GIT_NO_LAZY_FETCH'); echo "$t: $n"; done
curl -sS -o /dev/null -w 'git.adoc44:%{http_code} size:%{size_download}\n' --max-time 45 https://raw.githubusercontent.com/git/git/v2.44.0/Documentation/git.adoc; curl -sS -o /dev/null -w 'relnotes45:%{http_code} size:%{size_download}\n' --max-time 45 https://raw.githubusercontent.com/git/git/v2.45.0/Documentation/RelNotes/2.45.0.adoc
curl -sS --max-time 45 https://git-scm.com/docs/git/2.44.0 | grep -c 'GIT_NO_LAZY_FETCH'; curl -sS --max-time 45 https://git-scm.com/docs/git/2.45.0 | grep -c 'GIT_NO_LAZY_FETCH'; curl -sS --max-time 45 https://git-scm.com/docs/git/2.46.0 | grep -c 'GIT_NO_LAZY_FETCH'
curl -sS --max-time 60 https://git-scm.com/docs/git | sed 's/></>\n</g' | grep -n -A6 'no-lazy-fetch' | sed -e 's/<[^>]*>//g' | tr -s ' \n' ' ' | cut -c1-1200
cd /home/vgpnk/Projects/shokunin/souji-shokunin; grep -rn 'tier' corpus/QUALITY.md | head -20; echo ---; grep -rln 'SOURCES-CONTRACT-v1\|own-work' --include='*.md' . | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin; ls .ufo/contracts 2>/dev/null; find .ufo -maxdepth 3 -iname '*sources*' -o -maxdepth 3 -iname '*contract*' | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin; grep -nE '^[^#]*\bgit\b' tools/souji-census.sh | grep -vE '^\s*[0-9]+:#' | head -30; echo "---total---"; grep -nE '^[^#]*\bgit\b' tools/souji-census.sh | grep -vcE ':[[:space:]]*#'
cd /home/vgpnk/Projects/shokunin/souji-shokunin; grep -n 'status-unverifiable\|status-skipped\|git status\|status_ok\|status_out' tools/souji-census.sh | head -40
curl -sS --max-time 60 https://git-scm.com/docs/git | sed 's/></>\n</g' | grep -n -i -A4 'promisor' | sed -e 's/<[^>]*>//g' | tr -s ' \n' ' ' | cut -c1-3000
cd /home/vgpnk/Projects/shokunin/souji-shokunin; grep -n 'git --version\|GIT_VERSION\|version' tools/souji-census.sh | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin; sed -n '1205,1240p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin; grep -n '2\.45\|2\.4[0-9]\|--version' tools/souji-census.sh; echo "rc=$?"
cd /home/vgpnk/Projects/shokunin/souji-shokunin; sed -n '1000,1040p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin; sed -n '1040,1070p' tools/souji-census.sh
curl -sS --max-time 60 https://git-scm.com/docs/git | grep -n -i -E 'id="(environment-variables|_environment_variables|envvar_GIT_NO_LAZY_FETCH)"|>ENVIRONMENT VARIABLES<' | head -10
curl -sS --max-time 60 https://git-scm.com/docs/git | sed 's/></>\n</g' | sed -n '7395,7412p' | sed -e 's/<[^>]*>//g' | tr -s ' \n' ' '; echo; echo "=== anchor link ==="; curl -sS --max-time 60 https://git-scm.com/docs/git | grep -o 'id="[^"]*GIT_NO_LAZY_FETCH[^"]*"' | head -3
curl -sS --max-time 45 https://git-scm.com/docs/git/2.44.0 | grep -o -i '<title>[^<]*</title>' | head -1; curl -sS --max-time 45 https://git-scm.com/docs/git/2.45.0 | grep -o -i '<title>[^<]*</title>' | head -1; echo "---2.45 context---"; curl -sS --max-time 45 https://git-scm.com/docs/git/2.45.0 | sed 's/></>\n</g' | grep -n -A6 'GIT_NO_LAZY_FETCH' | sed -e 's/<[^>]*>//g' | tr -s ' \n' ' ' | cut -c1-700
cd /home/vgpnk/Projects/shokunin/souji-shokunin; grep -rn -i 'tier A\|tier B\|tier definitions' census/round-12/sources-gate.md corpus/lessons/round-12.md | head -12
cd /home/vgpnk/Projects/shokunin/souji-shokunin; sed -n '150,170p' tools/souji-census.sh | cat -A | cut -c1-120 | head -25
cd /home/vgpnk/Projects/shokunin/souji-shokunin; grep -rn 'LAZY_FETCH\|promisor\|partialClone' tests/fixtures/r15-census-config.py tests/fixtures/*.py census/round-16/*.json 2>/dev/null | head -12; echo rc=$?
cd /home/vgpnk/Projects/shokunin/souji-shokunin; sed -n '40,55p;125,150p;190,240p' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin; grep -n 'GIT_NO_LAZY_FETCH\|EXPECTED_ENV\|env\[' tests/fixtures/r15-census-config.py | head -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin; echo "== HEAD census =="; git show HEAD:tools/souji-census.sh | grep -n 'export GIT_NO_LAZY_FETCH=1'; git show HEAD:tools/souji-census.sh | grep -c 'GIT_NO_LAZY_FETCH'; echo "== HEAD gate =="; git show HEAD:tools/souji-landing-gate.py | grep -c 'GIT_NO_LAZY_FETCH'; echo "== sha =="; sha256sum tools/souji-census.sh tools/souji-landing-gate.py; echo "== diff names =="; git diff --name-only HEAD -- tools/ tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin; sed -n '968,982p' tests/fixtures/r15-census-config.py; echo ---; grep -n 'def spy_git_env' -A12 tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin; printf '%s' 'Setting this Boolean environment variable to true tells Git not to lazily fetch missing objects from the promisor remote on demand.' | wc -w; git status --porcelain | head -10; ls -l .ufo/waves/round-16/w2/ReopenS049.md
```

No tools installed or upgraded; no ALLOWED-EXEC commands were run.
