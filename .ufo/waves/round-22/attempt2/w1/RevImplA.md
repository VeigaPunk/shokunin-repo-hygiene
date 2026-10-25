# RevImplA — C1 declared-evidence tool review (round 22, attempt 2, w1)

STATUS: PARTIAL

Verdict: **ACCEPT-WITH-FIXES** — F1–F4 must land before the tool's `mismatches=0` is cited as
complete over the enumerated set; F5–F6 must land before the claim's wording is generalised.
Raw transcripts and fixture sources: `.ufo/waves/round-22/attempt2/w1/evidence/RevImplA.md`.

## Target

The assigned path `.ufo/waves/round-22/attempt2/w1/evidence/impl-a/souji-declared-evidence.py`
does not exist (`ls` -> "No such file or directory"; that evidence dir holds only `snap-*.raw`).
The candidate reviewed is the committed artifact the frozen counter command names:

```
$ git log --oneline --follow -- tools/souji-declared-evidence.py
a211e4d round-22: declared-evidence audit tool, assimilation entries and gate checker
$ git rev-parse a211e4d:tools/souji-declared-evidence.py ; git rev-parse HEAD:...
f388642ca182cae9dbe82f07a53f5fd7cc8f274c          (both; a211e4d is an ancestor of HEAD)
$ git diff --stat HEAD -- tools/souji-declared-evidence.py     # empty
$ sha256sum tools/souji-declared-evidence.py
58ddbfef46e08f40c72bc1c4fd7819dacee692f2809cb310de48aced013ae2b2
```

HEAD `2a130b47db43eb4b3d80b2e7a5112d6b4b021899`; base `4edb25dfe262515d0da63224bbba71e02e36cba5`.

## 1. Frozen counter line and exit codes — conformant (executed)

```
--rev 4edb25dfe262515d0da63224bbba71e02e36cba5  -> assertions=56 resolved=53 skipped=33 mismatches=3   RC=1
--rev 2a130b47db43eb4b3d80b2e7a5112d6b4b021899  -> assertions=56 resolved=56 skipped=36 mismatches=0   RC=0
--rev 4edb25d (abbrev)                          -> identical to the full sha, RC=1
```

Byte-exact spelling at `tools/souji-declared-evidence.py:185`
(`"assertions=%d resolved=%d skipped=%d mismatches=%d\n"`), exactly one stdout line in `counts`
format, `return 0 if mism == 0 else 1` (line 186). An unresolvable `--rev` exits 1 with a stderr
diagnostic and no counts line — contract-consistent (M undefined), though it is a `SystemExit`
rather than the frozen line, so a harness must not parse stdout alone.

## 2. Selftest — 8/8, rc=0 (executed)

All five frozen fixtures fire, plus a correct-digest positive control, the always-zero control
(`FALSE-GREEN-REJECTED`), and a skipped-accounting fixture. Transcript in the evidence file.

## 3. Compile / lint (executed)

`python3 -m py_compile` rc=0; `pyflakes` 4.0.3 rc=0 (clean); `ruff` 0.17.2 → 31 diagnostics on
this file, all style/robustness (UP031 x19, C408 x5, PLW1510 x3, UP022 x2, FURB167 x1, SIM115 x1);
no E9/F63/F7/F82. shellcheck N/A (`file` → "Python script ... executable"). Two worth fixing:
`SIM115` (line 245 `open(...).read()` leaks an fd) and `B007` (line 274 dead loop variable).

## 4. Read-only — conformant (source read)

Every write site enumerated: the caller's output stream (184-185, 290-291) and `_write` /
`os.makedirs` / `git init` / `rm -rf` confined to `base = tempfile.mkdtemp(..., dir="/var/tmp")`
(242; writes 201-230; cleanup 287). Git invocations in the measurement path are read-only
plumbing only — `rev-parse --show-toplevel`, `cat-file -e <rev>^{commit}`, `ls-tree -r --name-only`,
`show <rev>:<path>` — under `-c maintenance.auto=false` (line 55), which also suppresses
auto-maintenance writes. No write path exists outside the mktemp.

## 5. Q4 `/tmp` — conformant

No `/tmp` reference: the only two matches are `/var/tmp` (comment line 17; `mkdtemp` dir line 242).
There is no explicit refusal branch, because no `/tmp` path is ever constructed; the only residual
is that `mkdtemp(dir="/var/tmp")` raises if `/var/tmp` is absent rather than falling back.

## 6. Class conformance against the frozen enum

| Clause | Result | Receipt |
|---|---|---|
| A: path present at `--rev`, worktree never consulted | pass | P2: path untracked in worktree only -> `mismatches=1` |
| A: glob expanded over tracked files at `--rev` | **fail (F6)** | `corpus/*.md` resolves though only `corpus/knowledge/x.md` exists; shell glob matches nothing |
| A: `:<line>` suffix | pass | P9: `tools/x.md:1` resolved, `tools/nope.md:9` mismatch |
| A: token charset | **fail (F4)** | absent `docs/a+b.md`, `docs/a@b.md`, `docs/a b.md` -> `assertions=0 skipped=1 mismatches=0` |
| A: no form outside the enum | **fail (F5)** | `rev:path` resolved against a non-`--rev` revision |
| B: table cell + revision context, `cat-file -e <tok>^{commit}` | pass | live rows at HEAD: 5 B assertions, all resolved; dangling token -> mismatch |
| B: "inside a table cell" | **fail (F7)** | prose line with `measured commit deadbeef…` becomes a B assertion |
| C: 64-hex in the same cell as exactly one backticked path | pass | C6 (two paths) and C7 (no path) both skipped |
| C: sha256 over `git show` bytes, not the worktree | pass | committed digest + dirty worktree -> resolved; declared worktree digest -> `mismatch:digest sha256 is cc2e4bb5…` |
| C: "a 64-hex token" (case) | **fail (F3)** | uppercase 64-hex -> `skipped=1 mismatches=0` |
| `skipped` enumerates every candidate token | **fail (F2)** | `measured at deadbeef.` -> `assertions=0 resolved=0 skipped=0 mismatches=0` |

## Findings

### F1 — HIGH — declaration silently read from the worktree when absent at `--rev` (false green)
`read_declaration` (lines 72-80) tries `git show <rev>:<file>`, and on any miss falls through to
`open(os.path.join(root, relfile))` with no diagnostic. A measurement labelled with `--rev` can
therefore be computed from uncommitted bytes and still print the frozen line with `mismatches=0`.

Fixture (exact): repo `c1 = {docs/a.md}`, `c2 = {docs/b.md, SCORECARD.md}`; then overwrite the
worktree `SCORECARD.md` to assert `docs/a.md`; run `--rev c1 --file SCORECARD.md`.
Observed: `rc=0 assertions=1 resolved=1 skipped=0 mismatches=0`. `SCORECARD.md` is not tracked at
`c1`, so no committed declaration exists to audit — the audit must fail, not pass.
Fix: if the declaration file is not tracked at `--rev`, exit non-zero with a diagnostic; keep an
explicit `--file-is-worktree` escape hatch only for the selftest.

### F2 — HIGH — a hex token followed by `.`/`-`/`_` vanishes from both N and S
`HEX_B_RE` (line 37) carries `(?![A-Za-z0-9_.-])`, so `deadbeef.` does not match; and because it
was not a backticked span, nothing increments `skipped`. The token is in neither `assertions` nor
`skipped`, which breaks the frozen clause "N+S enumerates every candidate token the scanner saw",
and a dangling revision reports `mismatches=0`.

Fixture (exact): table cell `| measured at deadbeef. | x |` →
`rc=0 assertions=0 resolved=0 skipped=0 mismatches=0`. Same for `-` and `_`; `,` `;` `)` `:` and a
backtick correctly yield `mismatches=1`.
Fix: treat only a trailing sentence-period as punctuation (strip `[.,;:)]+` before matching), and
count every unmatched hex-shaped token as `skipped` so the identity N+S holds.

### F3 — HIGH — uppercase 64-hex digests are skipped, not checked
`HEX64_RE`/`HEX_B_RE` are `[0-9a-f]` only (lines 37-38). The frozen class C says "a 64-hex token";
a digest written in uppercase is silently excluded, so a wrong digest yields a green line.

Fixture (exact): `| sha256 ` + 64 × `A` + ` on ` + "`tools/f.txt`" + ` | measured commit 092748a |` →
`rc=0 assertions=2 resolved=2 skipped=1 mismatches=0`. A wrong lowercase digest in the same shape
correctly yields `mismatches=1` (selftest fixture 4).
Fix: match `[0-9a-fA-F]` and compare case-insensitively (or lower-case the token before comparing).

### F4 — MEDIUM-HIGH — class A charset drops legitimate repo-relative paths
`PATH_RE`/`GLOB_RE` (lines 34-35) allow only `[A-Za-z0-9_./*-]`. A backticked repo-relative path
ending `.md` that contains `+`, `@`, or a space is not class A at all, so an absent path is silent.

Fixtures (exact): `| ` + "`docs/a+b.md`" + ` | see |` → `rc=0 assertions=0 skipped=1 mismatches=0`;
same for `docs/a@b.md` and `docs/a b.md`. Git permits all three characters.
Fix: define class A by "no scheme/absolute prefix, ends with the frozen extension set", or extend
the class to `[^`\s]` minus a leading `/`, and let `git ls-tree` decide presence.

### F5 — MEDIUM — `rev:path` extension resolves against a revision other than `--rev` (false green)
Lines 100-105 introduce a form the frozen enum does not contain ("the enum, nothing else counts")
and resolve it at the *named* revision, so a path absent at `--rev` reports resolved.

Fixture (exact): `c1` holds `docs/old.md`; `c2` deletes it and its `SCORECARD.md` contains
`` `7425453:docs/old.md` ``; run `--rev c2` → `rc=0 assertions=1 resolved=1 skipped=1 mismatches=0`.
Fix: remove the `rev:path` branch, or require the named revision to equal `--rev` and still check
presence at `--rev`.

### F6 — MEDIUM — glob expansion uses `fnmatch`, where `*` crosses `/`
Line 150: `fnmatch.fnmatch(f, glob)` matches `corpus/knowledge/x.md` against `corpus/*.md`, which
shell/tree-glob semantics do not. This over-resolves a glob that names files at a level where none
exist. Live risk: `SCORECARD.md` carries `census/round-14/verification*.json`,
`census/round-17/jj-receipts-*.txt`, and `refs/jj/*` — all resolve today, so the vector is latent
but will fire on the next edit that moves a globbed file one level deeper.
Fixture (exact): tracked `corpus/knowledge/x.md` only, declaration `` `corpus/*.md` `` →
`rc=0 resolved=1`; `bash -c 'ls corpus/*.md'` → rc=2.
Fix: match segment-wise (`*` and `?` never cross `/`; `**` may), or translate to a regex
anchored per segment.

### F7 — LOW — class B applies outside table cells
`cells_of` (line 88) returns `[line]` when a line has fewer than two pipes, so any prose line is
treated as one cell and a bare hex token there becomes class B once the word `at`/`commit`/…
appears. The frozen class requires "inside a table cell"; this over-counts and can raise M on text
the enum excludes.
Fixture (exact): `We measured commit deadbeefdeadbeefdeadbeefdeadbeefdeadbeef earlier.` →
`rc=1 assertions=1 resolved=0 skipped=0 mismatches=1`.
Fix: run the B/C pass only on lines that are table rows (`line.count("|") >= 2`), and `skipped += 1`
for hex tokens elsewhere.

### F8 — MEDIUM (test gap) — several frozen properties have no fixture
A conforming regression still scores 8/8 in these cases:
1. **Committed-read branch is never exercised.** Every selftest fixture passes an absolute path
   (`os.path.join(base, ...)`), which always takes the worktree branch; a worktree-only
   `read_declaration` passes all 8. Proof of the duality: same revision, `--file SCORECARD.md` →
   `resolved` (committed), `--file /abs/.../SCORECARD.md` → `mismatch` (worktree).
2. **No negative fixture for C's "exactly one path" rule.** A pairing bug that took the first of
   two paths yields the same counts line as the correct skip in the existing fixtures.
3. **No fixture for the unmatched-token path** that F2 hits (`skipped` must grow).
4. No fixture for a glob, a `:line` suffix, or a `rev:path` token, so F4/F5/F6 are unguarded.

### F9 — NIT — missing declaration file raises a traceback
`--file DOES-NOT-EXIST.md` → uncaught `FileNotFoundError` traceback, rc=1. Prefer a `SystemExit`
diagnostic consistent with the unresolvable-rev path.

### F10 — NIT — selftest hygiene
`subprocess.run(["rm", "-rf", base])` (line 287, S607) instead of `shutil.rmtree`; unused loop
variable (line 274); fd left open at line 245.

## C1 truth-preservation spot-check (executed, outside the tool)

All three base mismatches still do not exist at HEAD (`git cat-file -e HEAD:<p>` fails for
`AXES.md`, `reason-after.txt`, `.ufo/scopes/souji-mint-20261018/obsidian-cli-probe.md`), so the
repair is a token-role repair, not file creation. Each repaired cell is truthful on inspection:

- `AXES.md` → `Axes (fleet \`/home/vgpnk/Projects/shokunin/AXES.md\`)`; the fleet file exists
  (5160 B) and the token is no longer repo-relative, so it leaves class A.
- `reason-after.txt` → `census/round-21/reason-after.txt`, present at HEAD (committed receipt).
- `obsidian-cli-probe.md` → de-backticked, and the prose now states "that file is absent (checked
  2026-10-25, ls -> "No such file or directory") … no longer [evidence]" (SCORECARD.md:83-85).
  This is stronger than the contract's third option.

Base `mismatches=3` → HEAD `mismatches=0` reproduces, and the new tokens added at HEAD
(`census/round-22/attempt2/declared-evidence-before.tsv`, `corpus/lessons/round-22-verifier-spotcheck.md`)
all resolve.

## Residual risk and verification gaps

- For the *measured document* the gaps are latent, not live: `SCORECARD.md` at HEAD contains no
  64-hex digest, no `rev:path` token, no `+`/`@`/space path, and no punctuation-terminated hex in a
  revision cell. The 56/56/36/0 line is therefore complete over the tokens present.
- They are not latent for the claim's *wording*: C1 says "the number of such assertions that do not
  resolve … is zero over the enumerated set". With F2/F3/F4 the instrument cannot see part of that
  set, so the zero is evidence only for the tokens the scanner recognises. Either fix the scanner or
  scope the claim to the scanner's coverage.
- Not verified here: behaviour on a shallow/partial clone where `git show` fails for a present path
  (F1's fallback would then silently substitute worktree bytes); and `fnmatch` behaviour on a
  bracketed glob (skipped, since `GLOB_RE` excludes `[`).
- The selftest was not mutated; no negative-mutation seat was run against it in this review.

## Tooling record

`~/.local/share/uv/tools/` was deleted on the host mid-review (dangling `/home/vgpnk/.local/bin/ruff`
and `pyflakes` symlinks); `uv tool install` reported success and the tree was removed again. Final
channel: `uv venv /var/tmp/revimpla/venv` + `uv pip install ruff pyflakes` → ruff 0.17.2,
pyflakes 4.0.3 on Python 3.14.8. No pacman transaction (host-wide pause), no other installs, no
write to the lane repo or any sibling.
