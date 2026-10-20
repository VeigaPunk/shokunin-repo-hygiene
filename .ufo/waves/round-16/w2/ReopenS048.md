# ReopenS048 — SC1046 row falsification

Item: re-open https://www.shellcheck.net/wiki/SC1046 (accessed 2026-10-20) and attack row S048 at
`corpus/SOURCES.md:62` (worktree). Lane HEAD `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae`;
`corpus/SOURCES.md` is modified in the worktree, `corpus/lessons/round-16.md` untracked.

**Verdict: fails (narrow, cell-level).** The page supports the diagnostic name and rationale, and the
row's disposition is right (`rejected`, `365d`, `used-by —`). Two prose cells overstate or mis-cite
what the page grounds, and the anchor leaves a pinnable wiki page unpinned. Three local cell edits fix
it; no lane claim changes.

## Observed (page)

- Served page: HTTP 200, 2809 bytes (`curl -sL -o /dev/null -w`). Raw wiki markdown
  `SC1046.md`: HTTP 200, 611 bytes, wiki HEAD `1c2e3bc72975962298af29b2615cc9a532681e4b`
  (`git ls-remote https://github.com/koalaman/shellcheck.wiki.git HEAD`). Same text; only GFM
  rendering differs.
- Page sections: title "Couldn't find `fi` for this `if`."; Problematic code; Correct code;
  Rationale; Exceptions: None.
- The page contains **no** occurrence of "parse", "error" or "severity". Over the 2809 served bytes,
  `grep -ioE 'parse|severity|SC1047|warning|error'` yields only `SC1047` ×2 and `warning` ×1.
- ≤25-word located quote (16 words), SC1046.md:22 / served page § Rationale:
  "ShellCheck has found an `if` statement that does not appear to have a matching terminating `fi`."
- The SC1046/SC1047 pairing in the row's flip is supported: SC1046.md:24 / served page § Rationale
  says "A companion warning SC1047 is emitted at the point where ShellCheck expected the `fi`."
- The page says nothing about souji, r15, or any repository — the "not evidence about any lane
  revision" clause is true.

## Cell-by-cell

- `scope` — **partial.** "name and rationale of the unterminated-if" is supported (title + Rationale
  sentence above). "**parse error**" is not on the page: the error severity/phase comes from
  shellcheck output (`SC1046 (error)`, shellcheck 0.11.0), not this document. The negative boundary
  ("not evidence about any lane revision") is supported.
- `teaches` — **partial.** "tool-message documentation only" is accurate; "not by this page" is
  accurate. But "the r15 parse failure is established by `bash -n` and shellcheck output on committed
  bytes **(S043)**" attaches one source pointer to a two-tool conjunction. S043 is the GNU Bash
  manual's `-n` text (`corpus/SOURCES.md:57`) and grounds `bash -n` only — it cannot ground
  "shellcheck output". The shellcheck half is own-work measurement, not a registry row.
- `tier A` — **holds by precedent, unverifiable against contract.** Same wiki, same kind as S027
  (`SC2115 | docs | A`), which is the registry's only other ShellCheck-wiki row. `docs` is right:
  the page is the project's own diagnostic documentation. See lane-level caveat below.
- `status rejected` — **holds.** The row was opened to ground the r15 parse failure and does not;
  the failure is tool-output evidence. This is the same rejected-with-flip pattern as S044.
- `recheck 365d` — **holds.** Unversioned wiki page; S027 (same wiki) uses 365d. `on-release` would
  be wrong: the page documents no release cadence.
- `opened 2026-10-20` — **holds.** My access is the same date; Gate line
  `corpus/lessons/round-16.md:31` records the same access and a verbatim title quote.

## Is it used by the claim it names? No — and that is correct

- `used-by —` **holds.** At HEAD, neither named file references the source or its codes:
  `git show HEAD:tools/souji-census.sh | grep -nE 'SC1046|SC1047|shellcheck'` → exit 1;
  `git show HEAD:tools/souji-landing-gate.py | grep …` → exit 1; same result on the worktree copies.
- The landing gate's parse path is `bash -n` only (`tools/souji-landing-gate.py:193-209`,
  `"bash -n rc=%d"` at :207), consistent with C2's S043/S050 sourcing.
- `census/round-16/run-matrix.py:112-113` runs `shellcheck -S warning` and records **rc plus a
  finding count**, not codes (`shellcheck_warning`). The archived r15-baseline arm is
  `bash_n {rc 2}`, `shellcheck_warning {findings 4, rc 1}`, sha256 `dab4122c…` — so the teaches
  claim's "shellcheck output on committed bytes" is real, but only codes-reproduced here, not
  archived.
- Reproduced on committed r15 bytes (not a census run; `bash -n`/`shellcheck` on `git show` stdin):
  `bash -n` rc 2, `line 1368: syntax error near unexpected token '}'`; shellcheck 0.11.0 rc 1 with
  SC1009/SC1046 (line 1324), SC1073, SC1047/SC1072 (line 1368). The SC1046/SC1047 pairing in the
  flip is therefore already observable in the lane's own r15 bytes. No lesson or knowledge entry
  cites the codes (grep of the five `corpus/knowledge/*.md` files named in the registry + round-15/
  round-16 lessons: 0 hits; round-16's only hit is the Gate record at :31).

## Defects and smallest fix

- **D1 — scope says "parse error" that the page never states.** Page has 0 occurrences of
  parse/error/severity. Fix: `name and rationale of the missing-`fi` diagnostic` (severity belongs
  to tool output, not this row).
- **D2 — the `(S043)` pointer overreaches to shellcheck output.** S043 = GNU Bash Set Builtin `-n`;
  it grounds `bash -n`, not shellcheck. Fix: "established by `bash -n` (S043) and by own-work
  shellcheck output on committed bytes (`census/round-16/c1-matrix-final.json` r15-baseline), not by
  this page."
- **D3 — anchor drops a revision that exists.** S027 pins the same wiki at `SC2115.md at wiki HEAD
  d9486e5`; SC1046.md is pinnable at wiki HEAD `1c2e3bc`. Fix: append `; SC1046.md at wiki HEAD
  1c2e3bc (611 bytes)` to the served-page note. The "no version or last-updated line" half is
  factually true (no date/version string in the 2809 served bytes).

## Lane-level caveat (not charged to S048's disposition)

`corpus/SOURCES.md:3` says tier definitions live in `SOURCES-CONTRACT-v1`, but no such file exists in
the lane at HEAD or in the worktree (`git ls-tree -r --name-only HEAD -- corpus` lists only
`QUALITY.md`, `README.md`, `SOURCES.md`, `knowledge/`, `lessons/`; five candidate paths tested absent).
`corpus/QUALITY.md:5` instead points at `corpus/SOURCES.md`, which defines no tiers. Tier A above is
therefore checked against the registry's own S027 precedent, not a written definition. This is a
pre-existing contract-pointer defect for L1, not evidence about S048.

## Remaining unknowns

- Whether kaika (outside this lane) holds `SOURCES-CONTRACT-v1`; sibling-lane reads were not
  authorized for this item, so the written tier rule was not opened.
- Whether the wiki page's rendered form ever carries a footer date; none appears in the fetched
  2809-byte document, but HTTP caching/CDN variation was not swept.

Confidence: high on page content (served + raw wiki HEAD), high on tool greps at HEAD and worktree,
high on the r15 reproduction; medium on tier (precedent only, contract file absent).

STATUS: PARTIAL — S048 fails narrow cell support (scope "parse error"; `(S043)` stretched over
shellcheck output; anchor unpinned) while `rejected` / `365d` / `used-by —` hold.

## Commands

```
grep -nE 'SOURCES-CONTRACT|S048|SC1046' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/QUALITY.md /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/round-16.md | head -60
curl -sL --max-time 30 https://www.shellcheck.net/wiki/SC1046 | grep -inE 'last.?updated|version|generated|20[0-9]{2}-[0-9]{2}-[0-9]{2}' | head -20; echo "curl_exit=${PIPESTATUS[0]}"
grep -rn -- 'SOURCES-CONTRACT-v1' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/QUALITY.md | head
grep -nE 'SC1046|SC1047|shellcheck|ShellCheck' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py; echo "exit=$?"
grep -nEi 'admission|tier|reject' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/QUALITY.md | head -40
ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/ | grep -iE 'contract|quality'; echo ---; curl -sL --max-time 30 https://www.shellcheck.net/wiki/SC1046 | wc -c; curl -sL --max-time 30 https://www.shellcheck.net/wiki/SC1046 | grep -ioE 'parse|severity|SC1047|warning|error' | sort | uniq -c
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && git status --porcelain corpus/SOURCES.md corpus/lessons/round-16.md && git show HEAD:tools/souji-census.sh | grep -nE 'SC1046|SC1047|shellcheck' ; echo "census_head_exit=$?" ; git show HEAD:tools/souji-landing-gate.py | grep -nE 'SC1046|SC1047|shellcheck' ; echo "gate_head_exit=$?"
git ls-remote https://github.com/koalaman/shellcheck.wiki.git HEAD; echo "exit=$?"
curl -sL --max-time 30 https://raw.githubusercontent.com/wiki/koalaman/shellcheck/SC1046.md | head -40; echo "---bytes:"; curl -sL --max-time 30 https://raw.githubusercontent.com/wiki/koalaman/shellcheck/SC1046.md | wc -c
grep -nE 'Tier|tier' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md | head -20; echo ---; test -f /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES-CONTRACT.md && echo EXISTS || echo ABSENT
for f in /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/knowledge/git-auto-maintenance-prunes-worktrees.md /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/knowledge/git-grace-periods-and-expire-to.md /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/knowledge/dupe-finders-detect-then-act.md /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/knowledge/trash-spec-restorable-quarantine.md /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/knowledge/git-repo-structure-readonly.md /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/round-16.md /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/round-15.md; do printf '%s: ' "$(basename "$f")"; grep -cE 'SC1046|SC1047' "$f"; done
grep -nE 'S048|SC1046' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/round-15.md | head
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git ls-tree -r --name-only HEAD -- corpus | grep -iE 'contract|sources' ; echo "exit=$?"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && command -v shellcheck && git cat-file -e b410186^{commit} && echo rev_ok && git show b410186:tools/souji-census.sh | bash -n; echo "bash_n_r15=$?"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show b410186:tools/souji-census.sh | shellcheck -s bash - 2>&1 | head -20; echo "shellcheck_r15_exit=${PIPESTATUS[1]}"
grep -oE 'SC10[0-9]{2}|shellcheck[^,"]*' /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-16/c1-matrix-final.json | sort | uniq -c | head
grep -nE 'Tier|tier|primary|secondary' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/QUALITY.md | head -20; echo ---; grep -n '^#' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
for f in /home/vgpnk/Projects/shokunin/SOURCES-CONTRACT.md /home/vgpnk/Projects/shokunin/corpus/SOURCES-CONTRACT.md /home/vgpnk/Projects/shokunin/souji-shokunin/SOURCES-CONTRACT.md /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES-CONTRACT-v1.md /home/vgpnk/Projects/shokunin/SOURCES-CONTRACT-v1.md; do printf '%s ' "$f"; test -f "$f" && echo EXISTS || echo absent; done; shellcheck --version | head -2
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git ls-tree --name-only HEAD; echo ---; git ls-tree --name-only HEAD:corpus
grep -nE 'shellcheck|bash -n|SC10' /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-16/run-matrix.py | head -20; echo ---; grep -nE 'bash -n|compile\(|parse' /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py | head -20
grep -nE 'Tier|tier' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/README.md | head; echo "exit=$?"
python3 -c "
import json
d=json.load(open('/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-16/c1-matrix-final.json'))
for k,v in d['arms'].items():
    print(k, {kk:v[kk] for kk in v if 'shell' in kk or 'bash' in kk or kk in ('rev','sha256')})
"
grep -nE 'SC1046|SC1047' /home/vgpnk/Projects/shokunin/souji-shokunin/tests/fixtures/r16-landing-gate.py /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-16/run-matrix.py; echo "exit=$?"; printf '%s' 'ShellCheck has found an `if` statement that does not appear to have a matching terminating `fi`.' | wc -w
curl -sL --max-time 30 -o /dev/null -w 'http=%{http_code} bytes=%{size_download} url=%{url_effective}\n' https://www.shellcheck.net/wiki/SC1046; curl -sL --max-time 30 -o /dev/null -w 'raw_http=%{http_code} raw_bytes=%{size_download}\n' https://raw.githubusercontent.com/wiki/koalaman/shellcheck/SC1046.md
curl -sL --max-time 30 https://raw.githubusercontent.com/wiki/koalaman/shellcheck/SC1046.md | grep -nE "ShellCheck has found|companion warning"; echo ---; curl -sL --max-time 30 https://www.shellcheck.net/wiki/SC1046 | grep -nE "ShellCheck has found|companion warning"
```

Also used (not shell): `read` on `corpus/SOURCES.md`, `corpus/QUALITY.md:1-12`,
`corpus/lessons/round-16.md:20-40`, `census/round-16/c1-matrix-final.json?q=keys` and
`?q=.arms|keys`. No tool installs or upgrades were performed.
