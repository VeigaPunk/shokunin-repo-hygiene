# R41w2mutationtester03 — mutation test of the C3 fixture's tool side (round 41, wave 2)

Seat: R41w2mutationtester03 (role mutation-tester, leaf, no subagents). Judged on: coverage.
Lane: /home/vgpnk/Projects/shokunin/souji-shokunin. Tip: 1d41c13574db80fdd9a4bde490b712da7ce2a85f.

## Verdict

**C3 (coverage) — NOT VERIFIED at behaviour level; verified only at label level.**

- The committed fixture `tests/fixtures/r41-refusal-sites.py` (a1144120…) passes on the frozen tool (21/21) and kills
  the 19 class-label mutants the C3 counter applies (its receipt `census/round-41/records/c3-after.txt` says 19/19). That
  label-level claim holds. The counter's `mutate()` (c3-counter.py lines 102-105) only replaces the class string at each
  `REFUSAL <CLASS>:` site, so the 19/19 receipt cannot speak to refusal *conditions*.
- Of 56 single-defect mutants of `tools/souji-worktree-drift.py` (no label swaps), 10 are equivalent by construction
  (section 3), 1 is unresolved (G6, not constructed), and 45 are non-equivalent. The committed fixture kills 28 of the 45
  non-equivalent mutants and misses 17 (E2, E4, F2, D3, B1, J5, J9, G2, G3, G4, G5, H1, H2, H3, I1, M1, N1). Those 17 changed
  behaviour that no committed probe observes; I confirmed each is observable with an uncommitted probe (section 4).
- No axis is harmed by the fixture itself (it changes no tool bytes). The gap is coverage: an admission of C3 as
  "refusal-site coverage" overstates what the battery pins. Section 5 lists the probes the L1 owner should consider. I did not
  write them into tests/ (out of scope for this seat).

## 1. Pins and inputs (verified)

| item | value | how |
|---|---|---|
| frozen tool sha256 (disk and `1d41c13:tools/souji-worktree-drift.py`) | b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6 | `sha256sum`; `git show 1d41c13…:tools/… \| sha256sum` |
| committed fixture sha256 (disk, `a1144120:…`, `1d41c13:…`) | f32022e28fe2293af44d7fee1cb73f9a39221fbcc534022b78d77a8c96551978 | same |
| repository toplevel | /home/vgpnk/Projects/shokunin/souji-shokunin | `git rev-parse --show-toplevel` |
| uid | 1000 (non-root; the fixture refuses root) | `id -u` |

No tool was installed or upgraded (python3 stdlib and git only). No git mutation was run in the lane (`git status --short`
after the run printed nothing; `git init` was run only inside scratch fixtures).

## 2. Method

- Mutants are generated in memory from the frozen bytes by exact `str.replace` of one occurrence; the harness aborts if an
  `old` string does not occur exactly once. Each mutant file's sha256 is in `receipts/summary.json` (`records.<ID>.mutant_sha256`).
- Each mutant is run through (a) the **unmodified committed fixture** (21 probes, `fixture-committed-r41-refusal-sites.py`
  copied byte-for-byte), and (b) **18 supplementary probes x01–x18** plus **x19 timing** (uncommitted, scratch-only, used only
  to classify fixture survivors; never proposed as a candidate here).
- Baseline: fixture 21/21 PASS on the frozen tool; all 18 supplementary probes PASS on the frozen tool; x19 BASE elapsed 40.1 s, PASS.
- Harness: `harness.py` (in this seat). Receipts: `receipts/` (per-mutant `<ID>.txt`, `summary.json`, `run1.tsv`, `timing.txt`).

## 3. Results (56 mutants)

Legend: "fixture" = committed fixture FAIL probes (`probe-*=FAIL`); "supp" = uncommitted probe that fails on the mutant.
Verdict column: K = killed by committed fixture; G = fixture gap, killed by uncommitted probe; E = equivalent (reason in 3a); U = unresolved.

| ID | group | mutation (frozen line text → change) | fixture | supp | verdict |
|---|---|---|---|---|---|
| A1 | errno | parse_record ENOENT test → EACCES | P01,P02a | – | K |
| A2 | errno | ELOOP folded into MALFORMED branch | P02b | – | K |
| A3 | errno | ENOENT branch inverted | P01,P02a,P02b | – | K |
| A4 | errno | open_nofollow: ENXIO dropped | P10a | – | K |
| A5 | errno | open_nofollow: EISDIR dropped | P10b | – | K |
| A6 | errno | open_nofollow: not-regular translation disabled | P10a,P10b | – | K |
| A7 | errno | open_nofollow: EACCES folded in | P18 | – | K |
| B1 | O_NONBLOCK | parse_record open without O_NONBLOCK | – | x06 (timeout: blocks on FIFO) | G |
| B2 | O_NONBLOCK | open_nofollow leaf open without O_NONBLOCK | P10a (30 s timeout) | – | K |
| B3 | O_NONBLOCK | parse_record set_blocking(True) removed | – | – | E |
| B4 | O_NONBLOCK | open_nofollow set_blocking(True) removed | – | – | E |
| C1 | S_ISREG | parse_record fstat gate removed | P03 | x06 (rc2 RECORD-EMPTY) | K |
| C2 | S_ISREG | open_nofollow post-open gate removed | P11 | – | K |
| D1 | nlink | multi-link threshold 1 → 2 | P17 | – | K |
| D2 | nlink | multi-link test removed | P17 | – | K |
| D3 | nlink | multi-link test over-refuses (`>= 1`) | – | x10,x11,x17,x18 | G |
| E1 | commonpath | record-row containment removed | P13 | – | K |
| E2 | commonpath | record-row containment → commonprefix | – | x01 | G |
| E3 | commonpath | gitdir containment removed | P14 | – | K |
| E4 | commonpath | gitdir containment → commonprefix | – | x02 | G |
| E5 | commonpath | JSON guard loops over [root] only | – | – | E |
| E6 | commonpath | JSON-INSIDE-MEASURED-TREE test removed | P16 | x03 | K |
| E7 | commonpath | gitdir not appended to measured | – | – | E |
| E8 | commonpath | root not seeded into measured | P16 | x03 | K |
| E9 | commonpath | repo path not appended to measured | – | – | E |
| F1 | alias | path-equality alias test removed | – | – | E |
| F2 | alias | inode-equality alias test removed | – | x04 (JSON-HARDLINKED instead of JSON-IS-RECORD) | G |
| F3 | alias | JSON-IS-RECORD refusal removed | P15,P16,P17,P18 | x04 | K |
| G1 | timeout | timeout lower bound `< 0` | P19 | – | K |
| G2 | timeout | timeout lower bound `<= 1` | – | x07,x08 | G |
| G3 | timeout | argparse --timeout default 20 → 1 | – | x19 timing (40.1 s BASE vs 2.0 s mutant) | G |
| G4 | timeout | measure list-timeout handler re-raises | – | x08 | G |
| G5 | timeout | measure list-rc check removed | – | x09 (detail becomes `prune-rc=128`) | G |
| G6 | timeout | measure prune-rc check removed | – | – | U |
| H1 | argparse | --root not required | – | x15b | G |
| H2 | argparse | --record not required | – | x15a | G |
| H3 | argparse | --skip-unrecorded store_false | – | x14 | G |
| H4 | argparse | --json default `""` | – | – | E |
| I1 | discover | symlinked-child skip removed | – | x14 (UNRECORDED lnk) | G |
| J1 | record | duplicate-name refusal removed | P04 | – | K |
| J2 | record | TOTAL repos check removed | P07 | x05 | K |
| J3 | record | TOTAL regs check removed | P08 | – | K |
| J4 | record | TOTAL prunable check removed | P09 | – | K |
| J5 | record | only last TOTAL row kept (r40 M40-4 regression) | – | x05 | G |
| J6 | record | `#` comment skip removed | P06 | – | K |
| J7 | record | RECORD-EMPTY refusal removed | P06 | – | K |
| J8 | record | schema refusal → continue | P05 | – | K |
| J9 | record | ROW regex regs single digit | – | x16 | G |
| K1 | usage | --root isdir USAGE check removed | P12 | – | K |
| L1 | nofollow | O_NOFOLLOW removed from ancestor walk | – | – | E |
| L2 | nofollow | O_NOFOLLOW removed from leaf open | – | – | E |
| M1 | write | ftruncate before JSON write removed | – | x11 | G |
| N1 | exit | drift exit 1 → 0 | – | x07,x08,x09,x12,x13,x14,x16 | G |
| P1 | exit | refusal exit 2 → 1 (sanity mutant) | all 20 refusal probes | x01–x06 | K |
| T1 | drift | ABSENT branch removed | P10a,P10b,P11,P17,P18 | x07,x13 | K |
| X1 | env | CHILD_ENV GIT_CONFIG_GLOBAL removed | – | – | E |

Counts: 56 mutants = 28 K (incl. sanity P1) + 17 G + 10 E + 1 U. Non-equivalent: 46; fixture kill rate 28/46 = 61%.

### 3a. Equivalent mutants (no observable change), with reasons

- **B3, B4**: O_NONBLOCK affects only FIFO/device open and read. The `set_blocking(True)` calls run only after the S_ISREG gate
  (lines 139–141, 274–277), so the descriptor is a regular file, where O_NONBLOCK has no effect on Linux.
- **E5**: every path added to `measured` already passed the containment test (row loop lines 296–301; gitdir lines 313–318),
  so each lies under root_real. Looping over `[root_real]` refuses exactly the same JSON targets.
- **E7, E9**: same argument. `measured.append(gitdir)` and `measured.append(resolved)` run only after the containment checks,
  so their entries are already subsumed by the `root_real` base.
- **F1**: path equality implies inode equality when the record exists. `parse_record` opened it earlier, so `os.stat` succeeds
  on both sides and the inode test returns True. F2 is the non-equivalent alias case (G).
- **H4**: `default=""` is falsy like `None` in `if args.json:`.
- **L1, L2**: `json_target` is `os.path.realpath`'d (line 326) before `open_nofollow`, so no component is a symlink at the walk.
  O_NOFOLLOW only defends a symlink swap between realpath and open (a TOCTOU race) and cannot be triggered deterministically
  by this fixture. Probes x17 (symlinked ancestor) and x18 (symlinked leaf) pass on the frozen tool and resolve to the target,
  as the realpath design implies. Doc-claim note: the docstring's "(including a symlinked path component, refused by the
  O_NOFOLLOW walk)" can fire only under a race.
- **X1**: the whitelisted child environment (`git_env`) never passes HOME or XDG_CONFIG_HOME, so git has no global-config
  path to read even without GIT_CONFIG_GLOBAL. GIT_CONFIG_NOSYSTEM and GIT_CONFIG_SYSTEM still neutralise system config.
  Reasoned, not measured against an injected HOME: this is equivalent only while the whitelist excludes HOME.

### 3b. Unresolved

- **G6** (`if dry.returncode != 0` removed): I could not construct a repository where `git worktree list --porcelain` succeeds
  and `git worktree prune --dry-run -v` exits nonzero. Three constructions gave rc 0 for both calls (section 6). Without that
  check, error lines on stderr would be counted as prunable. Survivor, constructibility unproven.

## 4. Fixture gaps: behaviour changed, no committed probe observes it

Each row is a non-equivalent mutant that the committed fixture passes. Evidence is in `receipts/<ID>.txt`.

| ID | what the committed fixture does not pin | supplementary killer | observed on mutant |
|---|---|---|---|
| E2 | containment is by string prefix: `../root2` resolves to a sibling sharing the root's string prefix, and is accepted | x01 | rc=1, record not refused (expected RECORD-OUTSIDE-ROOT, rc 2) |
| E4 | same for gitdir (`s/.git` → sibling `rootX/gd2`) | x02 | rc=0, not refused |
| D3 | no positive control: a clean run that should write JSON is never probed (`>= 1` over-refuses every write) | x10, x11, x17, x18 | rc=2 (refused; stderr not captured in receipt) |
| M1 | no successful JSON write probed, so truncation before write is unpinned | x11 (pre-filled 5000-byte target) | rc=0, target is not valid JSON |
| N1 | drift exit code never probed (all probes expect 2) | x12 and six others | rc=0 where 1 expected |
| F2 | JSON that is a hardlink (other path) of the record is not probed | x04 | JSON-HARDLINKED, not JSON-IS-RECORD |
| J5 | two TOTAL rows, first disagreeing and last agreeing, is not probed (r40 M40-4 regression) | x05 | rc=1 accepted, expected RECORD-MALFORMED |
| J9 | two-digit regs is never probed | x16 | rc=2 (expected rc 1 with `record=10 live=1`; stderr not captured) |
| B1 | FIFO as record path is never probed (r37 A2.4 / r38 A4 hang class) | x06 | timeout (open blocks) |
| I1 | discovery never runs: every fixture command passes `--skip-unrecorded` (fixture line 75) | x14 | UNRECORDED lnk (symlinked child measured) |
| H3 | same: --skip-unrecorded inversion is invisible to the fixture | x14 | no UNRECORDED u2 row |
| G2 | `--timeout 1` boundary never probed (P19 uses 0) | x07, x08 | rc=2 USAGE on a valid value |
| G4 | list-timeout branch never executed (no probe times out in measure) | x08 (FIFO HEAD) | rc=1, empty stdout (expected DRIFT UNREACHABLE list-timeout row) |
| G5 | list-rc branch never executed | x09 (empty .git dir) | `UNREACHABLE:prune-rc=128` instead of `list-rc=128` |
| G3 | default --timeout never probed | x19 (timing) | elapsed 2.0 s vs 40.1 s baseline |
| H1 | --root missing never probed | x15b | argparse default ran instead of rc 2 |
| H2 | --record missing never probed | x15a | rc=1 instead of rc 2 |

Note on P16: its record names `a` (absent), so repo `r` is never in `measured`. P16 is refused only by the `--root` base (E8
kills P16 and E9 does not). The per-repo JSON path is never exercised by the committed fixture.

Note on B2 and G-series hangs: B2 is pinned only by a 30 s subprocess timeout (fixture reports `probe-P10a=FAIL timeout`).

## 5. Recommendations for the L1 owner (not written here)

Promote, for the C3 battery, probes that kill the 17 gaps above, keeping the fixture's shape:
1. a positive control (clean run writes valid JSON; drift returns 1) — kills D3, M1, N1;
2. sibling-name prefix for row and gitdir — kills E2, E4 (a real containment escape under the mutant);
3. JSON hardlink of the record — kills F2;
4. two TOTAL rows, first disagreeing — kills J5;
5. FIFO record — kills B1 (must run under the 30 s subprocess timeout);
6. one discovery case without `--skip-unrecorded` (unrecorded repo plus symlinked child) — kills I1, H3;
7. `--timeout 1` accepted, a FIFO-HEAD repo for list-timeout, an empty `.git` for list-rc — kills G2, G4, G5 (cheap, ~2 s each);
8. argparse missing --root and --record — kills H1, H2;
9. two-digit regs — kills J9.
G3 needs a 40 s probe; decide whether that cost is acceptable. G6 needs a construction first.

Each promoted probe must be reviewed through the usual L1 path. Supplementary probes here are in scratch only.

## 6. Commands actually run and observed output

```
$ id -u                                  -> 1000
$ git rev-parse --show-toplevel          -> /home/vgpnk/Projects/shokunin/souji-shokunin
$ git show 1d41c13574db…:tools/souji-worktree-drift.py | sha256sum
                                         -> b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6  -
$ git show a1144120611b…:tests/fixtures/r41-refusal-sites.py | sha256sum
                                         -> f32022e28fe2293af44d7fee1cb73f9a39221fbcc534022b78d77a8c96551978  -
$ env -i PATH=$PATH TMPDIR=$S/tmp/BASE LC_ALL=C python3 -B $S/fixture.py --tool $S/mut/BASE.py --work $S/work/BASE; echo EXIT=$?
probe-P01=PASS rc=2 … probe-P19=PASS rc=2
SUMMARY probes=21 pass=21 fail=0
EXIT=0
$ python3 -B .../w2/R41w2mutationtester03/harness.py > results/run1.tsv   (wall 46.8 s, exit 0; table in receipts/run1.tsv)
$ python3 -B .../w2/R41w2mutationtester03/timing.py                         (wall 42.2 s)
X19-default-timeout tag=BASE sha=b2a6… elapsed=40.1s rc=1 stdout=DRIFT | UNREACHABLE | t | UNREACHABLE:list-timeout  -> PASS
X19-default-timeout tag=G3   sha=53b8… elapsed=2.0s  rc=1 stdout=DRIFT | UNREACHABLE | t | UNREACHABLE:list-timeout  -> FAIL-or-short
```

G6 construction attempts (in scratch, git init in fixture only), all rc 0:

```
$ git -C g worktree list --porcelain          ; echo "list rc=$?"   -> list rc=0 (worktrees as a regular file)
$ git -C g worktree prune --dry-run -v        ; echo "prune rc=$?"  -> prune rc=0
(second: worktrees/wt1 with gitdir -> /nonexistent)                 -> list rc=0 / "prunable gitdir file points to non-existent location"; prune rc=0
(third: worktrees/wt1 unreadable, chmod 000)                        -> list rc=0 / "Removing worktrees/wt1: gitdir file does not exist"; prune rc=0
```

Sample mutant runs (committed fixture, from `receipts/<ID>.txt`):
`A1: probe-P01=FAIL rc=2`, `B2: probe-P10a=FAIL timeout`, `E3: probe-P14=FAIL rc=0`, `T1: probe-P10a=FAIL rc=1`.

Supplementary probe on the frozen tool (BASE): `SUPP p_x01=PASS rc=2 stderr=['REFUSAL RECORD-OUTSIDE-ROOT: ../root2 resolves outside …/root']`.
Supplementary probe on E2 (mutant): `SUPP p_x01=FAIL rc=1 stderr=`.

Lane status after the run: `git -C …/souji-shokunin status --short` printed nothing. The tool sha was still
b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6.

## 7. Limits and honesty notes

- I did not read the wave-1 reports (`.ufo/waves/round-41/w1/*.md`). Conclusions rest on the committed bytes and my own runs.
- I did not re-run the committed C3 counter. I rely on its receipt and on my reading of its `mutate()`.
- Supplementary probes x01–x19 and the harness are my construction. They are evidence for classification only, not candidates. Running them relies on git init in scratch and a 40 s x19 probe.
- The `user` CPU time in the `time` output (≈6–12 min for ≈45 s wall) is unexplained by this seat. It does not affect any verdict.
- Scratch `/fast/scratch/hyaku/souji-r41/R41w2mutationtester03` was deleted after copying receipts to `receipts/`.

## 8. Receipts (seat directory)

- `harness.py` — mutant generator, fixture runner, supplementary probes x01–x18 (`p_x*`).
- `timing.py` — x19 default-timeout probe (BASE vs G3).
- `receipts/summary.json` — mutant specs (old/new), sha256 of each mutant, per-tag fixture and supplementary results.
- `receipts/run1.tsv` — the 56-row table.
- `receipts/<ID>.txt` — per-mutant fixture output and supplementary details (56 files including BASE).
- `receipts/timing.txt` — x19 output.
- `receipts/fixture-committed-r41-refusal-sites.py` — byte copy of the committed fixture (sha f32022e2…).
