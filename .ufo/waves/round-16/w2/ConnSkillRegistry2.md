# ConnSkillRegistry2 — final registry rows and correction sweep (r16 w2, falsify)

## Binding and drift (read this first)

The assignment names `SKILL.md:138/167/226-231`. Those coordinates were measured at lane
`a6ec781`. **Between my first read and my verification pass L1 advanced the lane to
`163158a` and landed the r16 lesson, S043–S050, SCORECARD and SKILL edits.** At `163158a`
(checked in this seat):

- `SKILL.md` sha256 `fc3006d125446558b741da5c80b0d4a1aabb238a629f2d880133fa4476bb5a5e`,
  23035 bytes, mtime 2026-10-20 12:02:52 -0300.
- The three named sites now resolve to: census row **139** (not 138), census bullet
  **171–174** (not 167), retire-paragraph **232–240** (not 226–231).
- L1 already replaced the stale prose: the preamble now says "Round-15 correction (r16)"
  (18–24), the census row already carries `error`/`status-unverifiable` (139), and the
  r14/r15 paragraph already says R16 restored and measured the census (232–240).

So this report is **not** a transcription of the assignment's line numbers; it is a
falsification pass over the landed rows, with exact replacements against `163158a`. Any
integrator replaying the assignment's coordinates verbatim will edit the wrong lines.

## Axes (godspeed)

- **A1 calibration (judged).** A registry row must state what each exit code proves *and
  what it excludes*. A row that reads as a certification where the tool only samples is a
  calibration defect even if every sentence in it is literally true.
- **A2 operability.** An operator reading one census row must be able to tell a measured
  row from a placeholder without opening the tool.
- **A3 evidence integrity.** "Pinned-value path" must name machine-checkable bytes or say
  explicitly that the only pin is prose.
- **A4 non-claimant.** No row may add admission or deletion authority.

## The one bounded move

**Put the coverage boundary in the verdict map of every row** — one clause, after the
code→class mapping, saying what a 0 (or a clean row) does *not* establish. Do not move
the caveat into a trailing paragraph: the registry is the lookup table operators and
later seats actually read.

Why this and not a rewrite: five of the six rows are already substantially correct; the
false-clean risk is localized to the code→class cell. The move adds no new capability,
no new authority, and no new prose surface — it converts existing tool-header limits into
the one place a reader cannot miss. It improves A1 and A3; A2 stays neutral (the map is
still the lookup); A4 is untouched.

The uncomfortable part, stated plainly: **`souji-seat-audit` is currently registered as
`gate`, but its exit 0 does not establish coverage.** Missing transcripts are counted on
the `SUMMARY` line and do not change the exit code (`tools/souji-seat-audit.py:232-233`).
I propose `probe` for that row with the enforcement finding retained. If L1 reads that as
weakening enforcement, keep `gate` and move the same caveat into the verdict cell; the
contradiction is real either way and must not be smoothed into a scalar verdict.

## Item verdicts

| item (attacks) | verdict | counterexample | smallest fix |
|---|---|---|---|
| `souji-census` exit codes (139) — false measured rows | **partial** | `SKILL.md:139` says `error`/`status-unverifiable` rows are "placeholders, not measurements". Only **`error` from a guard failure** is all-placeholder (`tools/souji-census.sh:1176-1180`: `repo 0 0 0 0 <empty> error`, no git run). A `status-unverifiable` row still measures `worktrees`, `unpushed`, `scratch_bytes`, `mtime_iso`; only `dirty` is unknown (`tools/souji-census.sh:1224-1229`; header 103-104). A malformed count adds an `error` flag to an otherwise measured row (`tools/souji-census.sh:1212-1214`). | replace the row (R1 below) |
| `r15-census-config` r16 revisions (149) — arm semantics and precondition | **partial** | `SKILL.md:149` says "selected tool supplies pre-harm, harmed or changed arm". Arm identity is now a digest label only; the oracle is identical for every tool and is explicitly never digest-keyed (`tests/fixtures/r15-census-config.py:1487-1499`). The fixture also refuses to run as root (`:1464-1465`, exit 2) and hard-requires an `strace` probe (`:730-754`). Neither condition appears in the row. | replace the row (R2) |
| `souji-preservation-evidence` repaired, 47/47 (150) — declared-only verdict | **holds** | Re-measured: `expected.json` pins match live bytes exactly — census `64a60fd0…`, config fixture `27474396…`, r14 fixture `e6a984b1…`; `record_sha256` `173db777…` equals the actual record digest. The row already says 47/47 at r16 vs 24/47 as landed, and "never runs recorded commands". | keep; only the pinned-path phrase "pins every snapshot input" is loose (it pins the measured inputs, not `regenerate.py`/`README.md`). Optional wording. |
| `souji-landing-gate` (152) — channel and pin scope | **partial** | `SKILL.md:152` gives no indication that `LG-SEAT-UNCARRIED` reads **contract `STATUS:` lines only**. The tool measured and dropped free-text phrase markers after 42 false hits at the r16 landing (`tools/souji-landing-gate.py:62-77`). A 0-findings verdict therefore does not mean "no prose-known failure". The row also calls the replays a pinned-value path without saying they are lesson prose with no JSON pin, and omits git-failure from exit 2. | replace the row (R4) |
| `r16-landing-gate` (153) — vacuity and coverage | **holds** | The fixture prints 14 `case(...)` results plus one `vacuity-stub` result = 15 (`tests/fixtures/r16-landing-gate.py:229-485,500-518`), matching the recorded 15/15. Exit map 0/1/2 is correct (`:526-527`, `:200-213`). | say "15 results (14 cases + vacuity stub)" so 15/15 cannot be read as 15 files. |
| `souji-seat-audit` (154) — audit coverage | **fails as written** | `SKILL.md:154` maps "0 → no major violation". `run()` records unexported seats in `missing_transcripts` and skips them (`tools/souji-seat-audit.py:118-125`); `main()` prints `missing=N` but returns `1 if major else 0` (`:232-233`). A wave with 63 of 65 transcripts can exit 0. The tool's own header calls the audit "a lower bound ... never a proof of absence" (truncated args). | replace the row (R6); do **not** claim coverage in the verdict cell |

Adjacent row 151 (`r15-preservation-evidence`) is not in the assignment; it holds as
landed — the fixture has exactly 8 checks (selftest, external-clean, external-green-only,
external-weakened-red, external-no-ns, external-changed-is-baseline, frozen-lane,
frozen-tampered) at `tests/fixtures/r15-preservation-evidence.py:192-306`.

## Draft final registry rows (replace at `163158a`)

Header row is unchanged. R1 replaces line 139; R2 line 149; R3 line 150; R4 line 152;
R5 line 153; R6 line 154. Line 151 stays.

```markdown
| souji-census | probe | `bash tools/souji-census.sh --root DIR [--compare PREV.tsv]` | 0 census emitted, or header-only diff; a degraded repository still exits 0: a guard-failed `error` row has all numerics as placeholders and ran no git command, a malformed count is replaced by 0 and flagged `error` on an otherwise measured row, and a `status-unverifiable` row keeps every measured column except `dirty`; 1 selftest or setup failure (merged — the exit code does not separate them); 2 usage, malformed baseline, or whole-run protected-path refusal `path-protected` (including a config-named path overlapping the store); 3 differential drift detected | `TMPDIR=/var/tmp bash tools/souji-census.sh --selftest` (r16: 38/38) | none for live output; the caller's comparison file is unpinned; r16 behavior measured by `r15-census-config` and `r14-census-boundary` below | read-only census; stdout only; selftest isolated under `/var/tmp` | souji |
| r15-census-config | gate | `python3 tests/fixtures/r15-census-config.py --tool PATH [--case ID] [--list] [--json]` | 0 every `EXPECTED_IDS` case PASS and the id set is exact; 1 failed case or id-set mismatch; 2 could-not-evaluate usage, prerequisite (`strace` probe), or refusal to run as root | default full invocation over an isolated synthetic HOME and mode-000 STORE under `/var/tmp`; `--tool` may be any arm — the digest only labels r14-harm/pre-harm, the oracle is behavioral and never digest-keyed | literal `EXPECTED_IDS` (20), `CASE_CLASSES`, `HARM_CASES` (15; descriptive for the independent checker) and per-case exits/findings/rows; r16 arm results `census/round-16/c1-matrix-final.json` | isolated `/var/tmp/r15-census-config.*`; never a real store or live fleet; refuses to run as root | souji |
| souji-preservation-evidence | gate | `python3 tools/souji-preservation-evidence.py --root DIR --record FILE` or `--frozen DIR` | 0 clean declared consistency (declared bytes re-measure, case universes exact, benign controls red only on the harm arm, namespace controls 12/12); 1 failed honest evidence (missing/unexpected case, non-discriminating arm, failure without a concrete reason); 2 could-not-evaluate malformed/duplicate-key/schema/tampered/unavailable input | `python3 tools/souji-preservation-evidence.py --selftest` (r16: 47/47; landed r15: 24/47); `python3 tests/fixtures/r15-preservation-evidence.py` (8/8 at r16) | checker literal case universe and baseline digests; `tests/fixtures/r15-preservation-frozen/expected.json` pins the measured inputs and record digest; `regenerate.py --rev <rev>` rebuilds the record from real runs | records read-only; self-invocations isolated `/var/tmp`; never executes a recorded command; verdict is declared-record consistency, not proof of execution | souji |
| souji-landing-gate | gate | `python3 tools/souji-landing-gate.py --root LANE --rev REV --round N [--base REV] [--json OUT]` | 0 no findings — covers only the checks below, never prose-only failure statements; 1 findings (LG-PARSE-REG, LG-MISSING-REG, LG-PARSE-CHANGED, LG-FROZEN-PIN, LG-FROZEN-MEASURED, LG-SEAT-UNCARRIED, LG-OPEN-ADMITTED); 2 could-not-evaluate usage, unknown rev, no SKILL.md, missing `.ufo/waves/round-N/` at REV, or git failure | `python3 tools/souji-landing-gate.py --selftest` (18/18 at r16); `python3 tests/fixtures/r16-landing-gate.py` (15/15 at r16) | literal finding ids, STATUS failure vocabulary and frozen-path rule in the tool; reads every committed `tests/fixtures/*-frozen/expected.json`; replay results are lesson prose (`corpus/lessons/round-16.md`), not a JSON pin | reads committed blobs (`git ls-tree`, `git cat-file`) into a private `/var/tmp` snapshot removed in `finally`; runs only `bash -n` and Python `compile()`; never executes repository code; `--json` refuses overwrite; LG-SEAT-UNCARRIED reads contract `STATUS:` lines outside fences, tables and blockquotes only — free-text phrase markers were measured and dropped (42 false hits at the r16 landing) | souji |
| r16-landing-gate | gate | `python3 tests/fixtures/r16-landing-gate.py [--tool PATH]` | 0 all 15 results pass (14 cases plus a vacuity stub that must fail); 1 any failed case; 2 missing prerequisite (tool, git, or lane worktree) | same default invocation; `--tool` selects the gate binary | historical r15 replay pins (`b410186`, round 15) and held-out synthetic cases in the fixture; the gate's finding ids | creates private `/var/tmp` git repositories removed in `finally`; invokes only the selected gate; never runs `tools/souji-census.sh` or touches operator surfaces | souji |
| souji-seat-audit | probe | `python3 tools/souji-seat-audit.py --spec W.json --transcripts DIR --lane LANE [--json OUT]` | 0 no major violation among audited seats — `SUMMARY missing=N` names unexported transcripts and rendered arguments truncate, and neither changes the exit code; a lower bound, not proof of compliance; 1 at least one major violation; 2 usage/unreadable | `python3 tools/souji-seat-audit.py --selftest` (20 classifier cases including wave-summary) | literal violation classes in the tool; per-item `OWN ONLY` paths and `ALLOWED-EXEC:` from the wave spec; a wave run's counts are data, not a pinned baseline | reads exported transcripts read-only; writes only `--json OUT` (refuses overwrite) and stdout | souji |
```

R6 note for the integrator: changing `kind` from `gate` to `probe` is the contested cell.
The exit code still voids evidence on a major; the change only refuses to call a
possibly-incomplete audit a certification. If L1 keeps `gate`, the verdict cell above
still applies unchanged.

## Correction sweep

### C1 — census row (current line 139)

Replace line 139 with R1 above. The smallest semantic delta:

- `error` and `status-unverifiable` are no longer one class: guard failure substitutes
  every numeric; status skip substitutes only `dirty`.
- Add the measured selftest count (38/38) so a reader can distinguish "merged code-1
  debt" from "selftest failing".
- Exit 3 is drift **detected**, not a tool failure.

### C2 — census bullet (current lines 171–174)

Current:

```
- Repeatable fleet census: `tools/souji-census.sh --root $SHOKUNIN_ROOT`
  (r6; per-repo worktrees/unpushed/dirty/scratch/mtime/flags). r15's
  `b410186` copy did not parse; r16 restored and measured it (config
  semantics below and in the tool header).
```

Replace with:

```
- Repeatable fleet census: `tools/souji-census.sh --root $SHOKUNIN_ROOT`
  (r6 fleet data; r16 tool: per-repo worktrees/unpushed/dirty/scratch/
  mtime/flags). r15's `b410186` copy did not parse; r16 restored and
  measured it. Read a guard-failed `error` row as unmeasured and a
  `status-unverifiable` row as "dirty unknown"; neither is clean (registry
  row and tool header).
```

Why: the parenthetical currently mixes an r6 data vintage with a tool-semantics
statement; and the one operational rule a reader needs (how to read a degraded row) is
missing from the fleet-surfaces section.

### C3 — retire paragraph (current lines 232–240)

Current text is already the r16 replacement. Its two imprecisions: "unevaluable config
degrades" has exceptions (a config-named path overlapping the store refuses the whole
run; a soft finding does not stop the scan), and "Measured" names only the green/named
fixtures, not the three harm arms that make the measurement discriminating. Replace with:

```
R14's blanket local-configuration refusal was rejected as harmed by the
outside closure. R15 landed a candidate that did not parse. R16 restored a
parsing census whose config guard is value/effect-aware: a config-named path
overlapping the store still refuses the whole run (`path-protected`); any
other unevaluable config degrades one repository to an `error` row (no git
run); a bound filter driver skips status for that repository
(`status-unverifiable`); hooks, fsmonitor and lazy fetch are neutralized on
every git call (`GIT_CONFIG_COUNT`, `GIT_NO_LAZY_FETCH`). Precedence is the
tool header's, not this summary. Measured at `0a70bef` (census bytes
unchanged at the `7a79dc2` landing rerun): changed arm 20/20 config and
12/12 r14-namespace cases, selftest 38/38, `bash -n` and ShellCheck clean;
r14-harm (`cc21683`) fails all 15 `HARM_CASES` ids plus `R15CFG-19`;
pre-harm (`a31642d`) fails exactly cases 02, 03, 08, 11, 14, 17, 18, 19
(the r16 degrade and preserve oracles plus refusals and safety); r15 baseline
(`b410186`) does not parse (`census/round-16/c1-matrix-final.json`,
`c1-matrix-landing.json`). Residual contractions versus pre-harm:
`corpus/lessons/round-16.md`.
```

The added harm-arm sentence is not decoration: without it, "measured" reads as a
one-sided green claim, which is the exact r15 failure class this round exists to falsify.

### C4 — consistency fix outside the named sweep (flag, do not bundle)

`SKILL.md:18-24` (preamble) says: "read `error` and `status-unverifiable` rows as 'not
measured', never as clean." Same overgeneralization as C1: a `status-unverifiable` row
*is* measured except for `dirty`. Smallest fix: "read `error` rows as unmeasured and
`status-unverifiable` rows as 'dirty unknown'; neither is clean." This line is outside
the assignment's named sites; L1 decides whether to include it. Leaving the preamble
contradicting the registry row is worse than either fix alone.

## Falsification findings (cross-file, beyond the rows)

**F1 — r16 fixture docstring contradicts its own cases (fails).**
`tests/fixtures/r16-landing-gate.py:21-24` advertises `LG-SEAT-UNCARRIED` as STATUS lines
"plus parse/do-not-ship/snapshot_tampered phrase markers outside ``` fences and table
rows". The implemented contract has no phrase markers: `tools/souji-landing-gate.py:62-77`
records that both drafts were measured and dropped, and case 9
(`tests/fixtures/r16-landing-gate.py:384-415`) deliberately asserts that
"The file in tree doesn't parse." (SeatC) and "note: do not ship this" (SeatD) produce
**no** finding. A reader trusting the fixture docstring would expect the opposite of the
held-out test. Smallest fix: replace the phrase-marker clause with "STATUS: lines whose
first word is in the pinned failure vocabulary, outside fences, table rows and
blockquotes; prose-only statements are not findings (phrase markers were measured and
dropped: 42 false hits at the r16 landing)". This is a doc defect, not a behavior defect;
it does not change R5's 15/15.

**F2 — census config fixture docstring is self-superseding (known open, restated).**
`tests/fixtures/r15-census-config.py:10-14` says the "Round-16 revisions ... supersede the
bullets below where they conflict", and the bullets do conflict (e.g. the old
`remote.*.promisor` refusal rule). The lesson already carries this as an open seat report
(`corpus/lessons/round-16.md`, `RevengeInertKeys.md:245`). Registry R2 does not rely on
the docstring; it cites the pinned tables. No action needed for this wave, but do not
"fix" the bullets by deleting the r16 paragraph.

**F3 — `R15CFG-19` is stricter than the r14 namespace fixture (holds, disclose).**
`c1-matrix-final.json` shows r14-harm fails 16/20 config cases: all 15 `HARM_CASES` ids
plus `R15CFG-19`, because the r14 tool prints the synthetic store path while refusing
(`detail: "store: contract: synthetic store path in output"`). The changed arm passes with
`path-protected:credential-store`. So "keeps r14's namespace refusals" is true at the exit
level but not byte-for-byte: r16 tightens disclosure. C3 states this; any row or lesson
line that says the namespace behavior is unchanged would be false.

**F4 — landing gate replay pin is prose, not machine-checked (holds, must be labelled).**
`SKILL.md:152`'s pinned-value cell pointed at "replays in `corpus/lessons/round-16.md`".
Those replay numbers (b410186 → 5 findings; a31642d/cc21683 → 0) are not a JSON artifact;
R4 says so explicitly. This matters because the landing gate's own LG-FROZEN checks
cannot verify its own prose.

**F5 — `souji-seat-audit` missing-transcript hole is a tool gap, not only a row gap
(partial).** For this wave the gap is observable: wave 1's audit recorded
`missing_transcripts: []` and 65 seats (`census/round-16/seat-audit-w1.json`), so the
recorded evidence is complete; but the exit contract allows a future run with missing
transcripts to report major=0 and exit 0. R6 is the smallest registry fix. A behavior
fix (exit 2, or a hard requirement that `missing=0` for a 0 verdict) would need its own
fixture case; do not bundle it into a prose wave.

## Risks

- **Table drift.** Verdict cells get longer; if a later tool edit changes an exit code,
  the row becomes the stale authority. Mitigation: every clause above names a code path
  or tool-header sentence, and the landing gate's `LG-PARSE-REG`/`LG-MISSING-REG` checks
  the cited paths — but it does not check prose truth. Re-run the six self-tests in an
  ALLOWED-EXEC context after any tool change.
- **Kind change for seat-audit.** Could be read as weakening the probe-rule enforcement.
  The exit code still voids evidence on a major; only the coverage claim is withdrawn.
  State the contradiction rather than resolving it silently.
- **R6 does not fix the hole.** A 0 from seat-audit remains unsafe for certification
  until missing transcripts are made fatal. That is a separate, bounded tool change.

## Verification performed (and not performed)

Performed here: exact bytes (`sha256sum`), current line numbers (`nl -ba`), frozen-pin
re-measure against live bytes, matrix arm summaries, `HARM_CASES` coverage, fixture case
counts, exit-code code paths, and the docstring/case contradiction. All counts cited as
"recorded" come from `census/round-16/c1-matrix-final.json`, `c1-matrix-landing.json`,
`LOG.md:836-882`, `SCORECARD.md:14,46-48` and `corpus/lessons/round-16.md:19-25`.

**Not performed (probe rule; this item carries no `ALLOWED-EXEC`):** no selftest, fixture,
matrix runner, census or gate invocation. The 38/38, 18/18, 15/15, 47/47 and 8/8 numbers
are L1's recorded runs at the named commits, not re-executed by this seat. An unrun check
has not passed here.

Recommended L1 checks after integration: `bash -n` on no files (no shell edits), the
landing gate at the r16 landing (`--round 16`) to confirm every cited path still resolves
and the edited rows parse, and one replay (`--rev b410186 --round 15`) to confirm the
gate still exits 1 with 5 findings. Do not accept a registry row from this report as
evidence that a tool ran.

STATUS: ok

## Commands

```bash
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && ls tools/ | grep -E 'souji-(census|preservation|landing-gate|seat-audit)' ; ls tests/fixtures/ | grep -E 'r1[56]-(census-config|landing-gate|preservation)'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls; echo ---; find . -maxdepth 3 -name SKILL.md -not -path './.git/*' 2>/dev/null
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls .ufo/waves/round-16/w2/ 2>/dev/null; echo ---; ls corpus/ | head -50
cd /home/vgpnk/Projects/shokunin/souji-shokunin && nl -ba SKILL.md | sed -n '130,180p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && nl -ba SKILL.md | sed -n '210,231p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1,90p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1,90p' tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1,70p' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1,60p' tools/souji-seat-audit.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1,60p' tools/souji-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '90,210p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1,70p' tests/fixtures/r16-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls census/round-16/ && echo --- && python3 -c "
import json
for f in ['census/round-16/c1-matrix-final.json','census/round-16/c1-matrix-landing.json','census/round-16/seat-audit-w1.json']:
    d=json.load(open(f)); print(f, json.dumps(d)[:1200]); print()
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git status --porcelain | head -20; echo ---; grep -n 'S04[3-9]\|S050' corpus/SOURCES.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls corpus/lessons/ && echo --- && grep -n 'Seat-reported failures' corpus/lessons/round-1*.md 2>/dev/null | head
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
d=json.load(open('census/round-16/c1-matrix-final.json'))
def walk(o,p=''):
    if isinstance(o,dict):
        for k,v in o.items():
            if isinstance(v,(dict,list)): walk(v,p+'/'+k)
            else: print(p+'/'+k,'=',v)
    elif isinstance(o,list) and len(o)<8: print(p,'=',o)
walk(d)
" 2>&1 | head -80
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "LG-SEAT-UNCARRIED\|phrase\|marker" tests/fixtures/r16-landing-gate.py | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -rn "landing-gate\|landing gate" LOG.md SCORECARD.md MINT.md corpus/lessons/round-16.md 2>/dev/null | head -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
d=json.load(open('census/round-16/seat-audit-w1.json'))
print({k:v for k,v in d.items() if k!='seats'})
print('seats',len(d['seats']),'calls',sum(s['calls'] for s in d['seats'].values()))
maj=[(n,v) for n,s in d['seats'].items() for v in s['violations'] if v['severity']=='major']
minr=sum(1 for s in d['seats'].values() for v in s['violations'] if v['severity']=='minor')
print('major',len(maj),'minor',minr); print(maj[:3])
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "HARM_CASES\|EXPECTED_IDS\|bash -n\|def main\|--tool\|exit(" tests/fixtures/r15-census-config.py | head -70
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '836,900p' LOG.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls -la tests/fixtures/r15-preservation-frozen/ && python3 -c "
import json;d=json.load(open('tests/fixtures/r15-preservation-frozen/expected.json'));print(json.dumps(d)[:900])"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
d=json.load(open('census/round-16/c1-matrix-final.json'))
print('arms:',list(d['arms']))
for k,v in d['arms'].items():
  print(k, {kk:(vv if not isinstance(vv,dict) else {x:vv[x] for x in vv if x in ('total','failed','valid','rc','checks')}) for kk,vv in v.items()})
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '120,200p' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1433,1520p' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "selftest\|SELFTEST\|EXPECTED\|def main" tools/souji-seat-audit.py | head -30 && sed -n '140,230p' tools/souji-seat-audit.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '100,135p' SKILL.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
d=json.load(open('census/round-16/c1-matrix-final.json'))
harm=set('R15CFG-01 R15CFG-03 R15CFG-04 R15CFG-06 R15CFG-07 R15CFG-08 R15CFG-09 R15CFG-10 R15CFG-12 R15CFG-13 R15CFG-14 R15CFG-15 R15CFG-16 R15CFG-18 R15CFG-20'.split())
for arm in ('r14-harm','pre-harm'):
  c=d['arms'][arm]['r15-config']['cases']
  fails={k for k,v in c.items() if v['verdict']!='PASS'}
  print(arm,'failed',len(fails),'harm_missing',sorted(harm-fails),'extra',sorted(fails-harm))
l=json.load(open('census/round-16/c1-matrix-landing.json'))
print('landing arms:',{k:{kk:(vv if not isinstance(vv,dict) else (vv.get('total'),vv.get('failed'),vv.get('checks'))) for kk,vv in v.items() if kk in ('rev','sha256','bash_n','selftest','r14-namespace','r15-config')} for k,v in l['arms'].items()})
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "seat-audit\|seat audit\|census\b" SCORECARD.md | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1520,1575p' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "def case\|cases = \|case(" tests/fixtures/r16-landing-gate.py | tail -30; echo ---; grep -n "return 0\|return 1\|return 2\|exit_code\|sys.exit" tests/fixtures/r16-landing-gate.py | tail -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "R15CFG-19\|def case_19\|def .*19" tests/fixtures/r15-census-config.py | head; echo ---; python3 -c "
import json
d=json.load(open('census/round-16/c1-matrix-final.json'))
print(json.dumps(d['arms']['r14-harm']['r15-config']['cases']['R15CFG-19'],indent=1))
print(json.dumps(d['arms']['changed']['r15-config']['cases']['R15CFG-19'],indent=1))
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -c 'case("' tests/fixtures/r16-landing-gate.py; grep -n 'case("' tests/fixtures/r16-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "probe\b\|kind\b\|gate\b" AGENTS.md PROVINCE.md | head -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1361,1410p' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '200,230p' tests/fixtures/r16-landing-gate.py; echo ---; sed -n '470,530p' tests/fixtures/r16-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1,60p' corpus/lessons/round-16.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "return 0\|return 1\|return 2\|mkdtemp\|--json\|def run" tools/souji-landing-gate.py | tail -25
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD; git status --porcelain SKILL.md; sha256sum SKILL.md; git log -1 --format='%H %ci %s' -- SKILL.md; stat -c '%y %s' SKILL.md; date -u
cd /home/vgpnk/Projects/shokunin/souji-shokunin && nl -ba SKILL.md | sed -n '126,175p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && nl -ba SKILL.md | sed -n '210,232p'; echo ---; git log --oneline -5
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1,40p' tests/fixtures/r15-preservation-frozen/regenerate.py; echo ---; grep -n "def main\|argparse\|--rev\|add_argument" tests/fixtures/r15-preservation-frozen/regenerate.py | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -c 'case(\|CASES\[' tests/fixtures/r15-preservation-evidence.py; grep -n "EXPECTED\|CASES\|def main\|return 0\|return 1\|return 2" tests/fixtures/r15-preservation-evidence.py | head -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && nl -ba SKILL.md | sed -n '231,250p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "status-unverifiable\|status_skipped\|config-unsupported\|error" tools/souji-census.sh | head -40
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1140,1240p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "def die\|def cleanup\|raise SystemExit\|geteuid" tests/fixtures/r15-census-config.py | head -10; echo ---; grep -n "EXPECTED\|checks\|passed\|def main" tests/fixtures/r15-preservation-evidence.py | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum tools/souji-census.sh tests/fixtures/r15-census-config.py tests/fixtures/r14-census-boundary.py tests/fixtures/r15-preservation-frozen/record.json; python3 -c "
import json;d=json.load(open('tests/fixtures/r15-preservation-frozen/expected.json'));print(d['files']);print('record_sha',d['record_sha256'])
import hashlib;print('actual',hashlib.sha256(open('tests/fixtures/r15-preservation-frozen/record.json','rb').read()).hexdigest())"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n '\-frozen\|expected.json' tools/souji-landing-gate.py | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '192,260p' tests/fixtures/r15-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '260,310p' tests/fixtures/r15-preservation-evidence.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "def probe_strace\|strace" tests/fixtures/r15-census-config.py | head -12; sed -n '260,300p' tests/fixtures/r15-census-config.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && nl -ba SKILL.md | sed -n '1,50p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '90,140p' tools/souji-seat-audit.py; echo ---; sed -n '230,270p' tools/souji-seat-audit.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '356,432p' tests/fixtures/r16-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && nl -ba SKILL.md | sed -n '112,133p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && nl -ba tests/fixtures/r16-landing-gate.py | sed -n '17,27p'; echo ---; nl -ba tools/souji-landing-gate.py | sed -n '44,64p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && nl -ba tools/souji-census.sh | sed -n '94,110p'; echo ---; nl -ba tools/souji-census.sh | sed -n '1214,1234p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && nl -ba tools/souji-seat-audit.py | sed -n '224,238p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "EXPECTED_JSON_RE" tools/souji-landing-gate.py; sed -n '360,400p' tools/souji-landing-gate.py
```
