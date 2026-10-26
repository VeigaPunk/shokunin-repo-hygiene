# SwarmSentinel61 — credential-shape scan of the r26/r27/r28 wave source trees

Lane base `691dd29211c53d0ef94fa072394cb9c8a69fe92e`; cleanse tip at scan time `b8cb4b31ce80e2e3314b88e85d40ea9873180804` (preregistration commit, `HEAD`). Read-only seat: no git mutation, no lane writes except this file. Scratch: none created — every pass was an in-process byte read plus `python3 -B` for the counting scripts, so no `__pycache__` appeared in the lane (verified: `find <lane> -name '*.pyc' -newermt '2026-10-25 21:50'` → empty).

## Status

STATUS: PASS — 1,578 regular files (+17 symlinks: 16 resolving to lane fixture files, 1 dangling) in `.ufo/waves/round-26`, `round-27`, `round-28` were read and swept for 15 credential-shape patterns; every hit resolved to a fabricated test fixture, a leak-canary, or a scan-pattern name, with structural proof of fabrication. The 374 regular files + 3 symlinks **not in the git index** — i.e. exactly the material the v2 re-capture would newly commit — contain **zero** credential-shape hits of any class. No live material found; nothing routes to kagi.

## Evidence

Revision: `git -C <lane> rev-parse HEAD` → `b8cb4b31ce80e2e3314b88e85d40ea9873180804`; `git cat-file -t 691dd29211c53d0ef94fa072394cb9c8a69fe92e` → `commit`.

Scan surface and coverage:

```
$ find .ufo/waves/round-26 .ufo/waves/round-27 .ufo/waves/round-28 -type f -print0 | tr -cd '\0' | wc -c
1578          # 1381 (r26) + 123 (r27) + 74 (r28)
$ find .ufo/waves/round-26 .ufo/waves/round-27 .ufo/waves/round-28 -type l -print0 | tr -cd '\0' | wc -c
17            # 16 resolve to lane files, 1 dangling (q/led-dangling.tsv -> missing.tsv)
```

Count note, and the first instance of Finding 8: the same sweep written as `find … -type f | wc -l` prints **1580**, two too many, because two fixture filenames contain a literal newline (`.ufo/waves/round-26/assimilation/validate/tests/vault/vadv54-run/r/nl/first\nsecond.md` and `…/r/scratch/.scratch/old\nname.log`). NUL-safe counting is mandatory on this tree. The 16 resolvable symlinks were read through the link; three of their targets sit outside the scanned dirs (`tests/vault/vadv54-run/{p/p2.md,p/p3.md,elsewhere/led-outside.tsv}`) and were scanned directly: 29/28/383 bytes, 0 credential hits.

Binary/opaque files (NUL in first 8 KiB) were scanned separately as bytes — 5 total:

```
round-26/assimilation/validate/tests/vault/s02-fixture/db/vault.db            90112 bytes  matches 0
round-26/assimilation/validate/tests/fixtures/__pycache__/r26-axis-check.cpython-314.pyc   9615  0
round-26/assimilation/validate/tools/__pycache__/souji-axis-check.cpython-314.pyc          8951  0
round-26/assimilation/validate/tools/__pycache__/souji-gate-check.cpython-314.pyc         23773  0
round-26/assimilation/validate/tools/__pycache__/souji-landing-gate.cpython-314.pyc       93940  0
```

Per-class inventory over all three trees (word-anchored regexes, one `python3 -B` pass reading every file's bytes; each occurrence resolved by hand below):

| class | occurrences | files |
| --- | --- | --- |
| private-key block (`-----BEGIN … PRIVATE KEY-----`) | 0 | 0 |
| `-----BEGIN` armor of any kind | 0 | 0 |
| `op://` refs | 0 | 0 |
| JWT (`eyJ…` / `eyJ…`) | 0 | 0 |
| `Cookie:`/`Set-Cookie:` | 0 | 0 |
| `sessionid`/`JSESSIONID`/`PHPSESSID` | 0 | 0 |
| `X-Api-Key`/`X-Auth-Token` headers | 0 | 0 |
| `sk-…` (16+) | 1 | r21-reason-canary.sh |
| `github_pat_…` | 1 | round-17-verifier-spotcheck.md (pattern name) |
| `ghp_…` | 8 | 4 files |
| `xox?-` | 6 | 3 files |
| `AKIA…` | 7 | 3 files |
| `password=` | 8 | 5 files |
| `Authorization:` (header-shaped) | 0 real — 10 raw hits, all the English word "authorization:" in prose or a fixture canary |
| `://user:pass@` | 3 | 2 fixture files (`example.test`, `host`) |

New-exposure check — the set that is not in the index (this is what the v2 capture would add; r27/r28 wave trees are entirely untracked today):

```
round-26 regular=1381 symlink=17  not-in-index: regular=177 symlink=3
round-27 regular= 123 symlink= 0  not-in-index: regular=123 symlink=0
round-28 regular=  74 symlink= 0  not-in-index: regular= 74 symlink=0
→ 377 path entries (374 regular files + 3 symlinks); credential-shape hits over that set = 0 (all 15 patterns)
```

Negative sweeps that carry their command:

```
$ grep -rIlE -- 'op://'    round-26 round-27 round-28 | wc -l   → 0
$ grep -rIl  -- '-----BEGIN' round-26 round-27 round-28 | wc -l → 0
$ grep -rIlE -- '(x-api-key|api-key|X-Auth-Token)\s*:' …        → 0
```

Highest-entropy leftovers (base64-ish ≥32 chars, not hex, no `/` or `.`) were decoded: the only large blob is `round-26/assimilation/validate/tests/results/final-61.json` (20,948 chars → 15,708-byte embedded copy of `tools/souji-verify.sh`, `#!/usr/bin/env bash`), decoded and re-scanned: **0** credential hits, **0** nested base64 blobs. The other two candidates are the literal base64 alphabet in `souji-seat-audit.py` and sha256 prefixes in `round-28/w1/SwarmSimplifier63.md`.

Environment-artifact sweep: no `HOME=`/`USER=`/`PWD=`/`XDG_*=` env dumps in any `.out`/`.err`/`.log`/`.tmp`/`.old` file under the three trees (0 files matched).

## Findings

1. **`tests/fixtures/case-F10/creds.pem` + `app.env` are synthetic placeholders, and are already committed in three places.** Locations: `.ufo/waves/round-26/assimilation/validate/tests/fixtures/case-F10/{creds.pem,app.env}`, `census/round-26/waves/assimilation/validate/tests/fixtures/case-F10/…`, `tests/fixtures/case-F10/…` (identical blobs `8d4b368…`/`0e70cf3…` at `HEAD`). Proof of fabrication, from bytes opened this run: `creds.pem:1` = `# souji F10 fixture — synthetic placeholder, not a key, never read`; the payload line is a 27-char `SOUJ…` canary that **equals** `expected.json.leak_canaries["creds.pem"]` (boolean-compared, not printed); `app.env` is the same construction and equals `leak_canaries["app.env"]`; `README.md:23-24` states the two files are "synthetic, non-functional placeholders (no real credential material)". **Verdict: safe-to-commit.**
2. **Calibration defect (declared vs bytes): the fixture's mode claim is false once committed.** `README.md:24` says the payloads ship "with mode `600` only so a harness can copy the tree". On disk they are `600`, but `git ls-tree -r HEAD --full-tree` records `100644` for all three copies — git cannot store `600`, so every checkout materialises them world-readable. Location above. This does not gate the commit (the content is a placeholder), but the README sentence is a true/false claim about committed bytes, which is exactly C1's surface class; it is **not** one of the four frozen statements, so the counter is unaffected — recorded here rather than as an amendment. Smallest fix: reword to "mode 600 in the source tree; git stores 100644".
3. **Every token-shaped string in the wave trees is a canary with a fabricated structure.** Locations and structural proof (masked to the first four characters, no values printed): `tools/souji-proc-census.sh:543,547,551,558` — `AKIA***` whose 16-char suffix is all digits (`is_digits=True`), plus `ghp_***`/`sk-f***`/`xoxb***` whose bodies carry the literal marker `fake`/`test`, and the assertions at `:554-559` that require these to be *absent* from the redacted output; `tests/fixtures/r18-proc-census.sh:105-108` — `R18_***` canary, `AKIA***` with a single repeated digit (`distinct=4`), `xoxb***` carrying the markers `fake` and `not-a-token`; `tests/fixtures/r21-reason-canary.sh:61-68` — `ghp_***`/`sk-S***`/`xoxb***` bodies all contain the literal `SOUJ` (11 occurrences in the file) plus `fake`, and the `AKIA***` value is a 16-char hex sequence (`is_hex=True`, 10 digits + 6 upper). Zero high-entropy random tokens; **verdict: safe-to-commit.**
4. **Prose-only matches, no values.** `corpus/lessons/round-17-verifier-spotcheck.md:52` (table of scan patterns), `corpus/knowledge/process-residue-observations.md:185`, `corpus/lessons/round-21.md:210`, `corpus/lessons/round-24.md:85,86,164,324` (redaction post-mortems that name `--token=`/`password=` shapes), `tools/souji-receipt-run.py:82-86` (the redaction regexes themselves), `w1/c1-new-scorecard-head.md:248`, `tools/impl-06.sh:427`, `tools/qrun-11.sh:515` (the word "authorization:" in prose — the case-insensitive header regex false-positives on it). All **safe-to-commit**.
5. **`round-27/w1/RevInheritedSafe.md:9` is a pattern list, not material, and it is one of the 123 r27 files the re-capture would newly commit.** The line lists the classes a prior reviewer grepped (`PRIVATE KEY`, `password=`, …). No value follows any of them. **Verdict: safe-to-commit.**
6. **Build residue: 4 `.pyc` files that the capture swallows and git cannot carry.** Locations: `.ufo/waves/round-26/assimilation/validate/{tools/__pycache__/souji-axis-check,souji-gate-check,souji-landing-gate}.cpython-314.pyc` and `…/tests/fixtures/__pycache__/r26-axis-check.cpython-314.pyc` (136,279 bytes total; byte-scanned, **0** credential strings). The capture tool copies the tree with `cp -a -- "$src/." "$dst/"` (`tools/souji-wave-evidence-capture.sh:100`) and hashes every resulting regular file (`:157`), so bytecode lands in the receipt and in `manifest.sha256` — `census/round-26/waves/manifest.sha256:62,1117,1118,1119`. But `__pycache__/` (root `.gitignore:3`) makes those receipt paths uncommittable, while the `.ufo/waves` copies are tracked only because an earlier round force-added them. **Verdict: needs-removal (by the L1, not by me); smallest remediation: the capture tool skips `__pycache__/`/`*.pyc` before hashing** — this is hygiene, not secrecy.
7. **Host-config disclosure already in history (and in the census snapshot).** `.ufo/waves/round-26/w1/LabGitVersion.md:46-53,63-76,82` reproduces `git config --list --show-origin` verbatim, so it carries the operator home path (`/home/<user>/.config/git/config`), the configured credential-helper binary names (`manager-core`, `git-credential-libsecret`) and `user.email` at the placeholder domain `example.invalid` / `shokunin.local`. No token, no userinfo URL, no helper *output*. Same file is already tracked and present at `census/round-26/waves/w1/LabGitVersion.md`. **Verdict: safe-to-commit** (path/helper-name disclosure only, no secret), noting that credential-helper *names* are pointers to stores and must never be followed by the capture tool.
8. **Newline-in-filename fixtures are present and are not credential material — but they are a scanner trap.** `.ufo/waves/round-26/assimilation/validate/tests/vault/vadv54-run/r/nl/first\nsecond.md` and `…/r/scratch/.scratch/old\nname.log` contain `vadv54 newline payload` / `vadv54 newline scratch payload` (23/31 bytes). `census/round-26/waves/manifest.sha256:1064-1065` records them in GNU escaped form (leading `\`, `\n` in the name), so the manifest is faithful. Two consequences: (a) any scanner that pipes `grep -rc` through a suffix filter produces **phantom path lines** — a filename ending a count line at `:0` splits into `…/first` (survives `grep -v ':0$'`) plus `second.md:0`; my first pass hit exactly this and I discarded the two phantoms after `grep -rIlEZ | tr '\0' '\n'` and a per-file re-check returned 0 matches; (b) consumers must decode `\n` before `stat`, otherwise the record path is unresolvable. **Verdict: safe-to-commit; see constraint (a) for any future credential sweep over these trees.**
9. **F3/F10-style duplication complicates any future redaction.** Each F10 blob exists in three committed locations (finding 1). If a later round ever needs to redact a fixture, all three copies plus the manifest records must change together — the current layout gives the capture tool no uniqueness check on content.
10. **Every one of the 152 r26 records absent from the committed tree is absent for one reason: an ignore rule shipping inside the receipt.** Measured over `census/round-26/waves/manifest.sha256` (1,382 records): the set of records whose receipt path is git-ignored equals exactly the set of records absent from `HEAD:census/round-26/waves` — 152 = 152, no remainder. Breakdown by the rule that fires: 140 `tests/vault/vadv-49/.gitignore` (`fixture/`, `shims/`), 6 `tests/vault/case-V6/.gitignore` (`src/`, `vault/`, `ledger*.tsv`), 4 root `.gitignore:3` (`__pycache__/`), 2 `case-F7|F8/repo-tree/.scratch/.gitignore` (`*`). Command shape: `git -C <lane> check-ignore --no-index -z --stdin` over the record paths vs `git ls-tree -r --name-only -z HEAD census/round-26/waves`. Consequence for the C2 remedy (evidence only — the counter is not mine): `git add -f` would clear `failed` but would commit nested `.gitignore` fixtures *and* 4 bytecode files (finding 6), so exclusion of ignored names is the correct instrument fix; because that changes the record set, the C2 counter's `records` baseline moves with it and the preregistration requires any such change to be stricter-only and logged by the L1.

Path-class verdicts (as requested):

| path class | verdict |
| --- | --- |
| `tests/fixtures/**` (incl. `case-F10/{creds.pem,app.env}`) | safe-to-commit — synthetic, declared canaries |
| `tests/vault/**` (incl. newline-named payloads, `s02-fixture/db/vault.db`) | safe-to-commit — fixture payloads only; `vault.db` is a synthetic demo vault (`note-a…e`, tags `alpha`/`demo`) |
| `tools/**` self-test canaries (`souji-proc-census.sh`, `r18-`/`r21-` fixtures) | safe-to-commit — structural fakes; add a path whitelist to any future scanner so they are not re-flagged |
| `corpus/**` prose and lesson tables | safe-to-commit — pattern names only |
| `__pycache__/**` | needs-removal before capture — 4 `.pyc`, 0 credential strings; already tracked under `.ufo/waves` (force-added in an earlier round) while the receipt copies are uncommittable |
| `w1/LabGitVersion.md` | safe-to-commit, disclosed: host path + credential-helper names |
| route-to-kagi | **none** |

## Deliveries

- `.ufo/waves/round-29/w1/SwarmSentinel61.md` (this report)

No tools installed or upgraded this run (nothing was needed; pacman untouched). No git index, jj or sibling-lane state touched; no file outside this report was written.
