# W2Census — C3 registry numbers re-derived at the lane tip (wave 2, falsify)

Seat: L1Souji23.W2Census. Scope: C3's registry half only — row count, max id, tier histogram,
status histogram, malformed rows, duplicate ids, `sources-census.sh validate` exit code and its
full output. The gate-check arm (`tools/souji-gate-check.py`) and the two entries are other seats'
slices and are **not** re-run here.

Lane tip: jj `@` = `lyykwskx`, HEAD commit `1026900` (git). Registry bytes at the tip:
`git rev-parse HEAD:corpus/SOURCES.md` = `c82f11138bffaba30386fec161ad5b4f658a8ef9`, and the same
blob at `4765250`, `c0eeaa7`, `1026900` — the registry did not move between the round's three
landings. `git hash-object corpus/SOURCES.md` = `c82f1113…`, the same as `HEAD:corpus/SOURCES.md`,
so the working-tree registry is the tip blob (`sha256 027379dc…e0c9`).

Two tracking facts that change how findings are graded: `.ufo/waves/round-23/report-draft.md` is
**untracked** (`git status --porcelain` → `??`, absent from `git ls-files`, not gitignored), so the
round report is still a working draft and the numbers in it are not committed bytes; the committed
claims are the `114 → 119` deltas in `SCORECARD.md:23`, `corpus/README.md:458`,
`corpus/lessons/round-23.md:85-86` and `LOG.md:1599`. Sibling wave-2 seats were editing 13 other
tracked files while I ran (`git status --porcelain` → 13 ` M` entries incl. `SCORECARD.md`,
`corpus/README.md`, `corpus/lessons/round-23.md`, `.ufo/waves/round-23/preregistration.txt`); none of
them touch `corpus/SOURCES.md`, which stayed at blob `c82f1113…`, and a re-run after those edits
still gave rows 119 / `E`=0 / `W04`=30 / rc 0. Concurrent lane edits are not mine and not modified
here.

## Verdict

**survives** for the frozen C3 after-value: at the tip the registry holds **119 rows, max id S119,
0 malformed, 0 duplicate ids, 0 rows outside `## Registry`, and `validate` exits 0** with 30
pre-existing `W04` warnings and no `E` finding. Prereg target `>=117` is met; the SCORECARD/README/
lesson/LOG claim `114 → 119` holds.

**falsified** for one number the draft report publishes in the same sentence: the tier histogram
after-value `A113/B3/C2` (`report-draft.md:133`) is wrong — measured **A113/B5/C1**. That draft is
untracked, so no committed artifact carries the wrong number yet. See F1.

## Re-derivation (commands and outputs)

### 1. Row count, max id, contiguity — independent parse, not the census tool

```
$ awk '/^## Registry/{r=1;next} /^## /&&r{r=0} r&&/^\| S[0-9]/{print}' corpus/SOURCES.md | wc -l
119
$ awk -F'|' '{gsub(/ /,"",$2); print $2}' /tmp/rows.txt | sort -V | tail -1
S119
$ comm -13 <sorted ids> <seq S001..S119>      # missing ids
(empty)
$ comm -13 <base 1208bfb ids> <tip ids>       # new ids
S115 S116 S117 S118 S119
```

Report's own counting command, re-run:
```
$ grep -cE '^ {0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md
119
```
Row-shaped lines anywhere in the file (`grep -cE '^\s*\| S[0-9]{3,} '`) = **119**, equal to the
registry-section count, so no row-shaped line sits outside `## Registry` (consistent with the
tool's own `E12` check firing 0 times; see §4).

### 2. Tier histogram (column 5) and status histogram (column 9)

```
$ awk -F'|' '{gsub(/^ +| +$/,"",$5); print $5}' /tmp/rows.txt | sort | uniq -c
    113 A
      5 B
      1 C
$ awk -F'|' '{gsub(/^ +| +$/,"",$9); print $9}' /tmp/rows.txt | sort | uniq -c
     96 mined
     15 queued
      8 rejected
```
Tier B rows: `S014 S017 S029 S118 S119`; tier C row: `S030` (`corpus/SOURCES.md:50`).
113+5+1 = 119 and 96+15+8 = 119.

### 3. Malformed rows and duplicate ids — independent parse

```
$ awk -F'|' '{print NF}' /tmp/rows.txt | sort | uniq -c
    119 13                    # every row has the contract's 11 cells (NF=13 with edge pipes)
$ awk -F'|' '{gsub(/ /,"",$2); print $2}' /tmp/rows.txt | sort | uniq -d
(empty)                       # no duplicate id
```

### 4. `sources-census.sh validate` — exit code and full output at the tip

```
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate \
    --root /home/vgpnk/Projects/shokunin souji ; echo "EXIT=$?"
souji	W04	S035 duplicate url git-scm.com/docs/git-repo across scopes
souji	W04	S036 duplicate url git-scm.com/docs/git across scopes
souji	W04	S038 duplicate url www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html across scopes
souji	W04	S049 duplicate url git-scm.com/docs/git across scopes
souji	W04	S057 duplicate url git-scm.com/docs/git-config across scopes
souji	W04	S058 duplicate url git-scm.com/docs/git-worktree across scopes
souji	W04	S059 duplicate url git-scm.com/docs/gitattributes across scopes
souji	W04	S063 duplicate url git-scm.com/docs/git-gc across scopes
souji	W04	S065 duplicate url www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html across scopes
souji	W04	S072 duplicate url www.gnu.org/software/bash/manual/html_node/The-Set-Builtin.html across scopes
souji	W04	S073 duplicate url man7.org/linux/man-pages/man2/kill.2.html across scopes
souji	W04	S075 duplicate url man7.org/linux/man-pages/man5/proc_pid_stat.5.html across scopes
souji	W04	S076 duplicate url man7.org/linux/man-pages/man5/proc_pid_exe.5.html across scopes
souji	W04	S077 duplicate url man7.org/linux/man-pages/man2/open.2.html across scopes
souji	W04	S086 duplicate url man7.org/linux/man-pages/man5/proc_pid_fd.5.html across scopes
souji	W04	S087 duplicate url man7.org/linux/man-pages/man5/proc_pid_wchan.5.html across scopes
souji	W04	S088 duplicate url man7.org/linux/man-pages/man5/proc_pid_status.5.html across scopes
souji	W04	S089 duplicate url git-scm.com/docs/git across scopes
souji	W04	S090 duplicate url git-scm.com/docs/git-filter-branch across scopes
souji	W04	S091 duplicate url git-scm.com/docs/git-rev-parse across scopes
souji	W04	S092 duplicate url git-scm.com/docs/git-for-each-ref across scopes
souji	W04	S093 duplicate url git-scm.com/docs/git-diff across scopes
souji	W04	S094 duplicate url www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html across scopes
souji	W04	S095 duplicate url man7.org/linux/man-pages/man5/proc_pid_fd.5.html across scopes
souji	W04	S096 duplicate url man7.org/linux/man-pages/man5/proc_pid_fd.5.html across scopes
souji	W04	S097 duplicate url git-scm.com/docs/git-filter-branch across scopes
souji	W04	S098 duplicate url www.gnu.org/software/coreutils/manual/html_node/timeout-invocation.html across scopes
souji	W04	S099 duplicate url git-scm.com/docs/git-rev-parse across scopes
souji	W04	S106 duplicate url docs.python.org/3/library/json.html across scopes
souji	W04	S108 duplicate url docs.python.org/3/builtins/exceptions.html across scopes
souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
EXIT=0
```
E-codes = 0; `W04` = 30; other warnings = 0; the `ok` line names the correct lane file. Per the
tool header (`scripts/sources-census.sh:17`) `W`-codes do not change status, so exit 0 here means
"no E finding", which is exactly what the claim asserts.

`census` mode agrees with the independent parse line for line:
```
souji	rows	119
souji	tier.A	113	tier.B	5	tier.C	1
souji	status.mined	96	status.queued	15	status.rejected	8
FLEET	tier.invalid	0	status.invalid	0	missing	0
```

### 5. Before-value at the base revision `1208bfb` (the SCORECARD's "before" cell)

Base bytes pulled with `git show 1208bfb:corpus/SOURCES.md` into a `/var/tmp` corpus mirror, then
the same tool against the mirror:

```
rows 114 | A 110 / B 3 / C 1 | mined 91 / queued 15 / rejected 8
malformed 0 | duplicate ids 0 | validate EXIT=0 | W04=30 | E-codes=0
```
So "registry 114 rows" (SCORECARD.md:23 cell 3) is right, and the before/after pair
`114 → 119` is a real 5-row delta.

### 6. Delta decomposition

+5 rows, exactly `S115`–`S119` (`corpus/SOURCES.md:135-139`): S115 A mined (git-count-objects),
S116 A mined (git-fsck), S117 A mined (git-prune), S118 B mined (Qiita JA), S119 B mined (CSDN ZH).
That is +3 A, +2 B, +5 mined — which reproduces the measured `A110/B3/C1 → A113/B5/C1` and
`mined91 → mined96` exactly, with `queued 15` and `rejected 8` unchanged.

Staged-vs-lane id space checked read-only against the package: the staged rows for the same three
documents are `S112/S113/S114` in `/home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md:10-12`
(git-count-objects, git-fsck, git-prune) and `S138/S139` (Qiita, CSDN). The lane's own `S112-S114`
are gio/GLib/statx (`corpus/SOURCES.md:132-134`), i.e. different documents — so the prereg's
collision premise is true and the by-document re-pointing to `S115-S119` is the correct resolution.
No lane row id collides.

## Discriminating power (does exit 0 / "0 malformed" mean anything?)

Byte-identical copy of the tip registry in a `/var/tmp` lane mirror, three injected defects, same
tool, same lane-shaped root:

| fixture | result | exit |
|---|---|---|
| unmodified copy | `ok`, 30 `W04`, no `E` | **0** |
| `S118` row cloned over `S119` (id collision) | `E03 S118 duplicate id`, `E04 … duplicate url … within scope` | **1** |
| `| S999 |` row appended after the registry | `E12 S999 row outside Registry section` | **1** |
| `S119` row with the `opened` cell removed (NF=12) | `E01 S119 fields=10` | **1** |

So the three counters the claim leans on (rows, malformed, duplicate ids) do fire, and exit 0 is
not an always-zero emitter. The report already discloses the weaker fact — exit 0 alone is vacuous
at base (`report-draft.md:126-128`, "the census `validate` exit 0 is vacuous at base … and only the
row/malformed/duplicate counters discriminate"). That disclosure is accurate and I confirm it.

## Findings

### F1 — `report-draft.md:133`: tier histogram after-value is wrong (severity: medium; action: **fix before the report lands**)

The line lives only in the **untracked** draft (see "tracking facts" above — no committed bytes
carry it; the committed artifacts state only the `114 → 119` row delta, which is correct):

```
tier histogram A110/B3/C1 → A113/B3/C2, status mined91/queued15/rejected8 → mined96/queued15/rejected8,
```

Measured after-value: **A113/B5/C1** (census output `tier.B 5`, `tier.C 1`; tier B = S014, S017,
S029, S118, S119; tier C = S030). Three independent defects in that one token:

1. `B3` is the *base* value, not the tip value — B went 3 → 5 (S118 and S119 are the two new
   `community` tier-B rows).
2. `C2` is not a state the registry ever held: C is 1 at both revisions (S030), and no round-23 row
   is tier C.
3. The published triple sums to 118, one short of the 119 rows the same sentence claims — and it
   contradicts the sentence three lines later (`report-draft.md:137-138`: "Rows added by tier: **5**
   — tier A … S115/S116/S117; tier B … S118/S119"), which implies +3 A / +2 B.

Fix: replace `A113/B3/C2` with `A113/B5/C1` (or delete the histogram from the report; SCORECARD's
C3 row does not carry it, so only the report is affected — `grep -rn 'A113/B3/C2'` over
`/home/vgpnk/Projects/shokunin` hits this one line only).

### F2 — `report-draft.md:119-120` calls the C3 control a "receipt"; no such receipt exists (severity: medium; action: **fix or disclose**)

```
118: Controls. … C3's control is the
119: staged rows appended as-is, which the census refuses with `E03 duplicate id` (the collision step's
120: own receipt).
```

The prereg's C3 control clause says "That receipt is committed before append". What is committed is
a **scout report**, not a receipt: `.ufo/waves/round-23/w1/ScoutIdCollision.md:142-200` (committed
at `4765250`) pastes the control arm's `rc=1` and the three `E03 duplicate id` lines. There is no
`receipt=v1` artifact for it — `grep -rl '^receipt=v1' census/` returns exactly five files
(`agreement-after`, `declared-evidence-after`, `gate-check-at-first-landing`,
`gate-check-at-lane-base`, `gate-check-c3`), and none of them runs `sources-census.sh`.

The control's *substance* reproduces (my §"Discriminating power" fixture fires the same `E03`), so
the claim's control is real; the artifact-type word is not. Fix: name the scout report and its
commit, or land the control through `tools/souji-receipt-run.py` so the sentence becomes true.

### F3 — C3's census arm is unbound: no revision, no tool digest (severity: low-medium; action: **disclose**)

`SCORECARD.md:23` cell 6 ("measured commit") reads `snapshots census/round-23/sources/* with
sha256; entries corpus/knowledge/…` — it names **no revision** and **no digest for the census tool**,
unlike C1/C2 which name tool digests and receipt revisions. The counter itself is fleet-owned and
unpinned: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh`, `sha256
3fb7261569f46423dd80ecc23e0a23789a7926f667c7a3fc559d2439d4a64e30`, not tracked in the lane
(`git ls-files scripts/sources-census.sh` → 0 paths), and it reads the working tree rather than a
revision. The draft's named limits disclose the exit-0 vacuity but not this pinning gap
(`grep -n 'fleet-owned\|no lane blob\|outside the lane\|unpinned'` over `corpus/lessons/round-23.md`,
`corpus/README.md`, `report-draft.md` → no hit).

Today the gap is harmless for the number: working tree == tip blob `c82f1113`, so the tree reading
and the revision reading are the same bytes. It still belongs in the report's named limits, because
a later host upgrade of the fleet script could change the reading with nothing in the lane to
compare against.

### F4 — adjacent, out of this slice: `report-draft.md:149` decision count (route to the entries seat)

```
149: Assimilation: one theme (F2 read side), two admitted entries, four Gate decisions — two ADMIT and
150: three REJECT with flips, …
```
"four" contradicts its own "two ADMIT and three REJECT" (five), and `corpus/lessons/round-23.md:90-110`
lists five `### Assimilation decisions` bullets (2 ADMIT, 3 REJECT), while the two entries' Gates
carry 11 ADMIT + 4 REJECT bullets (`repo-size-census-readonly.md` 7/2, `count-objects-garbage-readings-r25.md`
4/2). Not a registry number; the entry/gate seat owns the verdict. Reported here only because it sits
in the same paragraph family as the numbers I re-derived.

### F5 — checked and accepted, not a defect

- `count-objects-garbage-readings-r25.md:37` and `:65` cite **staged** `S134`, an id that does not
  exist in this lane's registry. Both citations label it as the staged package's own-work row and
  the Gate REJECTs it, so it is not a lane id claim and the registry stays collision-free; the
  report records the correction at `report-draft.md:152-153` ("the actual adopted ids are S115–S119
  and the own-work row is refused"). Accept.
- `gate-check-c3.tsv` (`rev=476525026cdb…`, `rc=0`, `entries=2 ok=2 slice_verdicts=0 slice_total=0
  fail=0`) is consistent with the report's "gate `entries=2 ok=2 fail=0`" and with the disclosed
  inert slice arm (`report-draft.md:126`). Not re-run here (other seat's slice); the receipt's own
  numbers are internally consistent.

## Residual risk and verification gaps

- `validate` exit 0 is non-discriminating by itself (0 at base too, disclosed). The C3 after-state
  rests on the row/malformed/duplicate counters, which I proved do fire (§Discriminating power);
  the `>=117` target is met by the count alone, so a hypothetical regression that added rows while
  breaking one would still show in `E01`/`E03`.
- The census tool is unpinned and uncommitted in the lane (F3); my run used its bytes as of
  `sha256 3fb7261…`. A future re-run is only comparable if that digest is recorded.
- The base exit-0 / 30-`W04` before-value was measured on a `/var/tmp` corpus mirror carrying the
  base `SOURCES.md` (needed because `--file` mode resolves `used-by` paths against the fleet root and
  floods `E11`). [INFERENCE] The real base tree would report the same, corroborated by the committed
  scout record `.ufo/waves/round-23/w1/ScoutRegistryCensus.md:164` ("Census is clean-but-warning at
  base … exits `0`").
- No LSP server answers Markdown/TSV here, so the counting was done with the text parse the claim
  itself specifies — for a byte-count claim that parse *is* the measurement, not a proxy. Every
  number above was produced by a command quoted in this report; nothing is source-read-only except
  where marked `[INFERENCE]`.

## Housekeeping

Read-only throughout: no lane write except this report, no git/jj mutation, no signal, no install
(pacman untouched). Scratch lived at `/var/tmp/souji-r23-w2-W2Census/` (base/dup-id/outside-row/
NF fixtures, lane corpus mirror, captured validate output) and was removed before this report was
finalised.
