# Round 14 W1 — SourceLedger (SoujiR14.SourceLedger)

Scope: re-derive committed `corpus/SOURCES.md` rows and histograms from baseline `a31642d` by `git show` + text parse (no census tool execution); read the round-13 S034 correction; propose registry mutations as old → new. No edits to shared bookkeeping, no commits, no builds/tests/linters, operator sweep not opened.

## Baseline identity (exercised)

- `git rev-parse --verify a31642d^{commit}` → `a31642d14006830ec62edf40b0354c3699728c4a`, commit 2026-10-20T03:01:44-03:00, subject "round-13 verifier spot-check (integrator, hyaku): non-author admit/reject".
- HEAD short ref is `a31642d`; `git diff --stat a31642d HEAD -- corpus/SOURCES.md` is empty, so working tree SOURCES.md equals baseline. Last SOURCES.md-touching commit: `23014d4`.
- `corpus/SOURCES.md` at baseline: 77 lines, sha256 `a405cdd4e7d12aa18868a7db1c1b1cc3e2debc3513043d9a018d9005466e34ab`.

## Re-derived committed inventory (exercised: Python over `git show a31642d:corpus/SOURCES.md`)

Parser: lines matching `^\|\s*S\d{3,}\s*\|`; cells = `line.split("|")[1:-1]`, stripped; 13 split fields expected (11 cells). Existence of `mined` used-by paths checked with `git cat-file -e a31642d:<path>`.

| Measure | Result at a31642d |
|---|---|
| source rows | 37 (S001..S037, contiguous, no duplicates) |
| malformed rows (split != 13 fields) | 0 |
| tier A / B / C | 33 / 3 / 1 |
| status mined / queued / rejected | 20 / 15 / 2 |
| tier × status | A-mined 18, A-queued 14, A-rejected 1 (S032), B-mined 2, B-queued 1, C-rejected 1 (S030) |
| kind | docs 29, code 3, community 2, spec 1, book 1, own-work 1 |
| opened | 2026-10-19: 33; 2026-10-20: 4 (S034–S037) |
| recheck | on-release 28, 365d 6, 180d 2, 90d 1 |
| enum violations (tier/status/kind/tier-inflation) | none |
| mined rows with missing used-by path at baseline | none |

Agreement: these match the round-13 closure and lesson counts exactly (37 rows; A=33/B=3/C=1; mined=20/queued=15/rejected=2). Round-13 "before" (a31642d's ancestor 31984f4): 33 rows, A=29/B=3/C=1, mined=16/queued=15/rejected=2 — not re-derived here beyond citing.

Stale-doc note (not a registry defect): `corpus/README.md` r12 bullet still reads "33 rows — 2026-10-19" and is dated, so it stays true for its date. `SOURCES.md` line 3 ("Every row below was opened on 2026-10-19") is superseded in the same file by the round-13 provenance paragraph; no change proposed.

## S034 correction — verification

Vendor source opened this round: `/usr/share/info/coreutils.info.gz` (decompressed in-process, 23,832 lines) and `/usr/share/man/man1/timeout.1.gz`. Installed package: `pacman -Q coreutils` → `coreutils 9.11-2` (matches S034 cell). Web fetch of gnu.org was NOT re-attempted here.

| S034 cell claim | Observed at vendor source | Verdict |
|---|---|---|
| node "timeout invocation" § 23.6 | heading `23.6 'timeout': Run a command with a time limit` at info line 15286 | confirmed |
| `--kill-after` KILL quote "lines 15316-15317" | 15316 blank, 15317–15318 option header; KILL sentence `Ensure the monitored COMMAND is killed by also sending a 'KILL' signal.` at **15319–15320** | **wrong locator** (quote correct, lines off by +3) |
| "Exit status lines … 15349" | 15363 `Exit status:`; **124** at **15365**; 15349 is the `-v` line "Diagnose to standard error, any signal sent upon timeout." | **wrong locator** (exit 124 is 15365; 15349 is not an exit-status line) |
| timeout(1) roff 20-22, 51-52 | roff 19–23 `-k/--kill-after` + "also send a KILL signal…"; roff 50–52 `124 if COMMAND times out, and --preserve-status is not specified` | confirmed |
| "exits 124 on timeout without preserve-status" | info 15365; man 51–52 | confirmed |
| "kill-after sends a secondary KILL" | info 15319–15320; man 20–22 | confirmed |
| "interruption can leave operation residue and does not authorize deletion" | **not in the vendor text** (checked both info and man); originates from round-13 lesson integration reasoning | **overclaim in the teaches cell — not vendor-grounded** |

Lesson pointer: `corpus/lessons/round-13.md:42` says "lines 15316-15317 opened instead" — same wrong locator. Spotcheck (`corpus/lessons/round-13-verifier-spotcheck.md` item 1) already routed this; my check confirms it with the exact lines above.

## Proposed registry mutations (old → new). Nothing applied.

Historical rows are immutable (SOURCES.md header rule). Correction is a new append-only row that names the row it supersedes, following the S035/S036 precedent.

1. **S034** — no in-place change. Old cells stay as written (anchor "lines 15316-15317,15349"; teaches incl. residue sentence). Superseded for locator and scope by S038.

2. **Add S038** (absent → mined):

```
| S038 | GNU coreutils info, node timeout invocation, installed coreutils 9.11-2 (/usr/share/info/coreutils.info.gz) — correction of S034 locator | docs | A | timeout exit 124 and --kill-after KILL on coreutils 9.11-2; supersedes S034 line citations only | /usr/share/info/coreutils.info.gz § 23.6 heading line 15286; -k/--kill-after header 15317-15318 and KILL sentence 15319-15320; -v verbose line 15349; Exit status heading 15363 and code 124 at 15365; timeout(1) roff /usr/share/man/man1/timeout.1.gz lines 20-22, 51-52 | corrects S034 locator only: KILL sentence at 15319-15320, exit 124 at 15365, not 15316-15317 or 15349 (15349 is -v); exits 124 without preserve-status; kill-after sends a secondary KILL; residue and no-deletion claims are not in this vendor text and are not taught here | mined | 2026-10-20 | on-release | corpus/lessons/round-13.md |
```

   - No gnu.org URL in the source cell, so the census should emit no duplicate-URL W04 for S038 (round-13 duplicate W04s were advisory only; exit stayed 0).
   - Residue claim deliberately excluded from S038 teaches; if the operator wants it, it needs its own sourced row, not this one.
   - used-by `corpus/lessons/round-13.md` exists at baseline, so the mined-used-by check passes.

3. **Lesson erratum** (proposed text, applied by L1/scribe only):
   - `corpus/lessons/round-13.md:42`: old "Exit status 15316-15317" → new "KILL sentence lines 15319-15320; exit 124 line 15365 (supersedes locator in S034 via S038)". Do not rewrite the quote itself, which is accurate.

4. **Histograms** before → after landing S038:

| Measure | a31642d (observed) | after S038 (proposed) |
|---|---|---|
| rows | 37 | 38 |
| A / B / C | 33 / 3 / 1 | 34 / 3 / 1 |
| mined / queued / rejected | 20 / 15 / 2 | 21 / 15 / 2 |
| kind docs | 29 | 30 |
| opened 2026-10-20 | 4 | 5 |

## Findings

- F1 (calibration, S034 locator): wrong locator in S034 anchor and in round-13 lesson line 42. Quote text is accurate. Fix by S038 correction row + lesson erratum; S034 cells stay immutable.
- F2 (calibration, S034 teaches overclaim): residue / no-deletion sentence in S034 teaches is not in the cited vendor docs. S038 teaches omit it. Lesson's residue reasoning remains an inference, not a source claim.
- F3 (none): row counts, tier/status/kind histograms, opened dates, enum and used-by checks all agree with round-13's recorded counts. No malformed rows, no duplicate IDs.

## Code inspection vs exercised evidence

- Exercised here: `git rev-parse`, `git log`, `git diff --stat` (empty), `git show a31642d:corpus/SOURCES.md` and `…round-13-verifier…md` text, Python text parse of the baseline SOURCES.md, `git cat-file -e` for mined used-by paths, gzip read of coreutils info and timeout(1) man page (with line-numbered output), `pacman -Q coreutils`.
- Not exercised: the fleet census script, any gate or selftest, any build or test, a live gnu.org fetch, the other seats' lessons beyond the S034 pointer.
- Code/doc inspection only: QUALITY.md criteria Q1–Q19 (read, not evaluated against tool output).

## Tool installs / updates

None. No new tool was required; existing `git`, Python 3 stdlib, `pacman` were used.

## Out of scope / not touched

- `census/operator-sweep-20261019/` and `census/operator-sweep-20261018/`: not opened, copied, hashed, queried or modified.
- `~/.omp/agent/`: only `RULES.md` read. No omp CLI launched.
- No commits, no edits to `corpus/SOURCES.md`, `corpus/lessons/*`, `LOG.md`, `SCORECARD.md`, or tools.

## Final L1 commands (for the main agent, after the registry/lesson edits land; not run by this seat)

```sh
# 1. Canonical census, unchanged command used by round-13 closure
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji
#    expect exit 0, final line ok for corpus/SOURCES.md; advisory W04 only if S038 duplicates a URL

# 2. Append-only check: exactly one inserted line, zero deletions vs baseline
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --numstat a31642d -- corpus/SOURCES.md
#    expect: "1	0	corpus/SOURCES.md"

# 3. Row count after landing
grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
#    expect 38

# 4. Re-derivation parse (same as this seat, run on the landed revision)
#    python3: git show <rev>:corpus/SOURCES.md → regex rows → tier col [3], status col [7] → Counter; expect A=34 B=3 C=1, mined=21 queued=15 rejected=2

# 5. Vendor locator check for the S034/S038 correction
#    python3: gzip.open('/usr/share/info/coreutils.info.gz') lines 15319-15320 contain "killed by also sending a 'KILL' signal"; line 15365 contains "124 if COMMAND times out"

# 6. Lesson erratum commit: stage named paths only, with the maintenance guard
git -C /home/vgpnk/Projects/shokunin/souji-shokunin -c maintenance.auto=false commit -m "<msg>" -- corpus/SOURCES.md corpus/lessons/round-13.md
```

Note on step 2: a clean append-only landing of S038 is exactly one inserted line in `SOURCES.md`; any deletion or changed existing row means a historical cell was rewritten and must be reverted.
