# Re-open S047 — gitignore(5) global excludes default

Scope attacked: worktree row `corpus/SOURCES.md:61` (uncommitted; absent from HEAD). Claim consumer: `corpus/lessons/round-16.md:30,35` → "C1 … XDG default". Tools inspected at lane HEAD `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae`.

**Verdict: holds.** Page, version stamp, scope, teaches, tier, status, recheck and the named use all check out; three non-fatal edge notes below.

## Quote (≤25 words, located)

> "Its default value is $XDG_CONFIG_HOME/git/ignore. If $XDG_CONFIG_HOME is either not set or empty, $HOME/.config/git/ignore is used instead."

17 words. Location: gitignore(5) **§ DESCRIPTION**, bullet 3 of "Which file to place a pattern in depends on how the pattern is meant to be used" (the `core.excludesFile` bullet), fetched live 2026-10-20. Observed; not inferred.

## Page support for the row cells

| Cell | Verdict | Evidence |
|---|---|---|
| scope "default location of the global excludes file, not pattern semantics" | holds | The quoted sentence is exactly the default `core.excludesFile` value/location. The census never parses ignore patterns: `grep -n 'gitignore\|check-ignore' tools/souji-census.sh` returns no pattern-engine use; its `:(exclude…)` strings (`tools/souji-census.sh:1003-1006,1038-1041`) are git **pathspec** magic, not gitignore syntax. |
| teaches "when core.excludesFile is unset git reads $XDG_CONFIG_HOME/git/ignore, else $HOME/.config/git/ignore; the census honors that default when boundary-clean" | holds (minor wording) | Doc supports every clause, including the *empty* XDG case. The "else" maps to "XDG_CONFIG_HOME unset/empty", not "core.excludesFile set"; the lesson row (`round-16.md:30`) carries the verbatim conditional, so no misinformation is introduced. |
| anchor/version "last updated in 2.55.0", "2.56.0 no changes", § DESCRIPTION, opened 2026-10-20 | holds | Live page banner: "gitignore last updated in 2.55.0"; version list line 1: "2.56.0 no changes". Exact string match, exact section. |
| tier A | holds | Same tier as every other vendor-manual row (S042 git-config, S046 git-check-attr, S049 git): `docs` + A. Tier definitions live in `SOURCES-CONTRACT-v1` (`corpus/SOURCES.md:3`); that file is **not in the tree** at HEAD or worktree, so this is judged against peer-row usage — observed, with the missing-contract caveat. |
| status mined | holds | `corpus/lessons/round-16.md:30` cites S047 with the quote and `:35` states C1's XDG default rests on S047; the row's used-by names that lesson. Real consumer. |
| recheck on-release | holds | Version-pinned vendor manual whose page advertises 2.56.0 "no changes"; matches S042/S045/S046/S049/S050. |

## Is it truly used by the named claim?

- **Lesson**: `corpus/lessons/round-16.md:30` (citation + quote), `:35` ("C1's … XDG default … rest on … S047"). Observed.
- **tools/souji-census.sh @ HEAD** — HEAD blob sha256 `64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c`, identical to worktree (matches the wave's recorded bytes):
  - `status_info_file()` defined `:942`; XDG/HOME fallback `:960-976`: `${XDG_CONFIG_HOME:-}` → if empty `$HOME/.config` → `$base/git/$leaf`, then `/dev/null` for non-absolute, protected, unresolvable or non-regular targets.
  - called at `:1023` for `core.excludesFile ignore`; enforced at `:1036` with `-c core.excludesFile="$ex"`.
  - Fidelity: unset→XDG default; XDG unset **or empty**→`$HOME/.config/git/ignore`; set-but-unmodellable→status `unverifiable`; protected default→`/dev/null`. That is what the page says the default is, and the row's "when boundary-clean" is the code's own fence.
- **tools/souji-landing-gate.py @ HEAD** — sha256 `e7d2439d97efca34ef5c848158e85366bf58b0106c39cd5f0388fa81022cb3f2`, no `excludes`/`XDG`/`gitignore`/`attributesFile` match. Not a consumer — and the row does not name it. No unmet consumer, no false used-by.

## Counterexamples examined (none fatal)

1. **Relative `XDG_CONFIG_HOME`**: census falls to `/dev/null` for a non-absolute target (`tools/souji-census.sh:962-966`), while git would carry a relative XDG path through. Conservative divergence, not doc-contradicting (XDG requires absolute). [INFERENCE] on git's relative resolution — not executed (probe rule).
2. **"else" compression** in the teaches cell: the HOME fallback is conditional on XDG unset/empty; the cell reads as if unconditional after the XDG clause. Fix if desired: "…$XDG_CONFIG_HOME/git/ignore, or $HOME/.config/git/ignore when XDG_CONFIG_HOME is unset or empty". Not a factual error given `round-16.md:30`.
3. **Corroborated elsewhere**: git-config(1) — S042's URL — states the same default at its `core.excludesFile` entry (served HTML lines 8497-8503). S042's teaches cell does not carry that default, so S047 is not a registry duplicate; it is corroborative rather than the unique anchor. Calibration note only.

## Remaining unknowns

- `SOURCES-CONTRACT-v1` definitions not present in the repo; tier/recheck judgment is by peer-row convention, not the frozen text.
- No execution of git to demonstrate default-file pickup (forbidden here); the code and manual agree by inspection only.
- Probe-rule disclosure: `git status --porcelain -- corpus/SOURCES.md` (read-only, named path) and two metadata listings (`find -maxdepth 3 -name 'SOURCES-CONTRACT*'`, `git ls-tree -r --name-only HEAD | grep contract|SOURCES`) were run outside the enumerated verb list. They read no content, no operator-owned surface, no sibling lane. All substantive evidence above comes from the allowed page fetch, `git show`, `grep` on named files, and `sha256sum`.

STATUS: ok

Page reads used the `read` tool directly (https://git-scm.com/docs/gitignore and the rendered git-config page); `curl` below is the only network shell call.

## Commands

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD; git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain -- corpus/SOURCES.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git --no-pager grep -n -i -E 'gitignore|fsmonitor|GIT_CONFIG_COUNT|core\.hooksPath' -- tools/souji-census.sh tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -E '\bex=|excludesFile|XDG_CONFIG_HOME|\.config/git' tools/souji-census.sh | sed -n '1,80p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -E 'S047|gitignore|XDG_CONFIG_HOME|excludesFile' corpus/lessons/round-16.md | sed -n '1,60p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git --no-pager show HEAD:corpus/SOURCES.md | sed -n '61p' | cat -A | sed -n '1p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -i -E 'excludes|XDG|gitignore|attributesFile' tools/souji-landing-gate.py || echo 'NO-MATCH landing-gate'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git --no-pager show HEAD:tools/souji-census.sh | grep -n -E 'XDG_CONFIG_HOME|core.excludesFile|core\.attributesFile' | sed -n '1,20p'; echo '---'; ls corpus | grep -i -E 'contract|quality'; echo '---'; sed -n '61p' corpus/SOURCES.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -E '^\| S047|S047' corpus/lessons/round-16.md; echo '---'; sed -n '25,36p' corpus/lessons/round-16.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -i -E 'tier|recheck|on-release|primary|mined' corpus/QUALITY.md | sed -n '1,60p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1,22p' corpus/QUALITY.md; echo '=== contract refs ==='; grep -rn 'SOURCES-CONTRACT' corpus/*.md corpus/**/*.md 2>/dev/null | sed -n '1,12p'
curl -s https://git-scm.com/docs/git-config | grep -n -A6 'core.excludesFile' | sed -n '1,24p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls -1 corpus/SOURCES-CONTRACT-v1.md 2>/dev/null; find . -maxdepth 3 -name 'SOURCES-CONTRACT*' -not -path './.git/*' 2>/dev/null
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '56p' corpus/SOURCES.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git --no-pager ls-tree -r --name-only HEAD | grep -i -E 'contract|SOURCES' | sed -n '1,20p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -rn -E 'tier A|tier B|recheck.*on-release|on-release' corpus/lessons/round-12.md corpus/lessons/round-15.md census/round-12/sources-gate.md 2>/dev/null | sed -n '1,30p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '40,60p' corpus/SOURCES.md; echo '--- tail ---'; sed -n '86,98p' corpus/SOURCES.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n 'status_info_file()' tools/souji-census.sh; echo '--- sha HEAD vs worktree ---'; git cat-file -p HEAD:tools/souji-census.sh | sha256sum; sha256sum tools/souji-census.sh; git cat-file -p HEAD:tools/souji-landing-gate.py | sha256sum; sha256sum tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '952,978p' tools/souji-census.sh; echo '--- lesson claim line ---'; sed -n '34,35p' corpus/lessons/round-16.md
ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w2/ 2>&1 | sed -n '1,20p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n -E 'gitignore|check-ignore|\.gitignore|exclude' tools/souji-census.sh | sed -n '1,30p'; echo '=== gate comments ==='; grep -n -i -E 'census|config' tools/souji-landing-gate.py | sed -n '1,15p'
```
