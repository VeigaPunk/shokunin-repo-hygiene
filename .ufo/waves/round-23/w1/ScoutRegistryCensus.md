# C3 "before" receipt — registry baseline at lane base

## Status

STATUS: PASS — census validate at lane base 1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd exits 0 with
0 E-codes and 30 pre-existing W04 warnings; registry rows=114, max id S114, tier A110/B3/C1,
status mined91/queued15/rejected8, malformed rows=0, duplicate ids=0. All five metrics agree with
the frozen parser (`sources-census.sh census`) and with an independent re-parse of the table.

## Evidence

Lane rev (`git rev-parse HEAD`): `1208bfb4924d9c6d4fdd1cdf8ccdc29b834893cd` — equals the
preregistration lane base. `git status --porcelain -- corpus/SOURCES.md` → 0 lines (registry
untouched by round-23 work, so this baseline is not contaminated).

Registry bytes are the base-rev bytes: `git ls-tree <rev> corpus/SOURCES.md` →
`100644 blob 3ab461a7c61796bb5009d24b78d004f60b79fbbb`; `git cat-file blob 3ab461a7… | sha256sum`
→ `4179f0884120575c1826e7db1e17db8d934129e201982c06dc062790501686c4`, identical to
`sha256sum corpus/SOURCES.md` on the worktree. File is 183 lines / 82871 bytes.

Census tool (fleet-owned, outside the lane's git): `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh`,
size=35466, mtime=2026-10-19 21:22:45 -0300, sha256
`3fb7261569f46423dd80ecc23e0a23789a7926f667c7a3fc559d2439d4a64e30`.

### E1 — the frozen C3 command (verbatim), exit code, full output

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji
```
exit `0`; 31 output lines = 30 `W04` + 1 `ok`; `E01..E12` count = 0.

```
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
```

Line/severity counts (same captured bytes):
```
wc -l < /var/tmp/souji-r23-ScoutRegistryCensus/validate.out          → 31
grep -cE $'\tE[0-9]{2}\t' /var/tmp/souji-r23-ScoutRegistryCensus/validate.out → 0
grep -cE $'\tW[0-9]{2}\t' /var/tmp/souji-r23-ScoutRegistryCensus/validate.out → 30
```

### E2 — row count (the brief's command)

```
grep -cE '^ {0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
```
→ `114`

### E3 — max id

```
grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md | grep -oE 'S[0-9]+' | awk -F'S' '{print $2}' | sort -n | awk 'END{print "S"$0}'
```
→ `S114`

### E4 — tier histogram (header column `tier`)

```
awk -F'|' '/^ {0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|/{gsub(/^[[:space:]]+|[[:space:]]+$/,"",$5); h[$5]++} END{for(k in h) printf "tier.%s %d\n",k,h[k]}' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md | sort
```
→
```
tier.A 110
tier.B 3
tier.C 1
```
(invalid/other bucket: 0)

### E5 — status histogram

```
awk -F'|' '/^ {0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|/{gsub(/^[[:space:]]+|[[:space:]]+$/,"",$9); h[$9]++} END{for(k in h) printf "status.%s %d\n",k,h[k]}' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md | sort
```
→
```
status.mined 91
status.queued 15
status.rejected 8
```
(invalid bucket: 0)

### E6 — malformed rows (cell count != 11)

```
awk -F'|' '/^ {0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|/{ if (NF-2 != 11) {c++; printf "line %d id=%s cells=%d\n", NR, $2, NF-2} } END{printf "malformed=%d\n", c+0}' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
```
→ `malformed=0` (no per-line detail lines emitted; cell-count histogram is `{11: 114}`)

### E7 — supporting: duplicate ids / non-conforming ids

```
grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md | grep -oE 'S[0-9]+' | sort | uniq -d | wc -l
```
→ `0`; non-`S[0-9]{3,}` ids → none. Ids are exactly S001..S114, contiguous, 114 distinct.

### E8 — authoritative cross-check (frozen parser, census mode)

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && /home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --root /home/vgpnk/Projects/shokunin souji | sort
```
exit `0` →
```
FLEET	missing	0
FLEET	rows	114
FLEET	status.invalid	0
FLEET	status.mined	91
FLEET	status.queued	15
FLEET	status.rejected	8
FLEET	tier.A	110
FLEET	tier.B	3
FLEET	tier.C	1
FLEET	tier.invalid	0
souji	rows	114
souji	status.mined	91
souji	status.queued	15
souji	status.rejected	8
souji	tier.A	110
souji	tier.B	3
souji	tier.C	1
```
Every E2/E4/E5 number matches the frozen parser exactly. The grep in E2 sees all 114 rows
because the validate run emitted no `E12` (no row-shaped `S###` line outside `## Registry`), so
the grep and the section-scoped parser enumerate the same set at this revision.

### E9 — one-block re-run (for the L1's round-end receipt)

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD && /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji; echo "census_rc=$?" && grep -cE '^ {0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md && awk -F'|' '/^ {0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|/{gsub(/^[[:space:]]+|[[:space:]]+$/,"",$5); t[$5]++; gsub(/^[[:space:]]+|[[:space:]]+$/,"",$9); s[$9]++; if (NF-2 != 11) m++} END{printf "tier.A=%d tier.B=%d tier.C=%d status.mined=%d status.queued=%d status.rejected=%d malformed=%d\n", t["A"],t["B"],t["C"],s["mined"],s["queued"],s["rejected"],m+0}' corpus/SOURCES.md
```

## Findings

1. **Census is clean-but-warning at base.** `sources-census.sh validate … souji` exits `0` at
   1208bfb with 30 `W04` (duplicate URL across scopes) and zero `E01`–`E12`. Location:
   output block E1. The warnings are pre-existing registry content (S035…S108), not round-23
   damage.
2. **rows = 114, matching the preregistration's "registry holds 114 rows (max S114)".** Location:
   `/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md` `## Registry` (line 20 heading,
   rows to line 183 minus trailing notes). Three independent enumerations (grep, independent
   parser, frozen census parser) agree: 114.
3. **max id = S114; ids are contiguous S001..S114 with 0 duplicates**, so the next free id for the
   assimilation append is **S115** — the preregistration's adopted continuation point. Location:
   same file; E3/E7.
4. **Tier histogram A=110, B=3, C=1, invalid=0** (E4), identical to `census` mode's
   `tier.A/tier.B/tier.C` (E8). Location: registry column `tier`.
5. **Status histogram mined=91, queued=15, rejected=8, invalid=0** (E5), identical to `census`
   mode (E8). Sum 91+15+8 = 114 = row count, so no row escapes the status enum.
6. **Malformed rows = 0**; every one of the 114 rows has exactly 11 cells (NF=13 under the
   contract's leading/trailing-pipe rule). Location: E6. The `E01` count of 0 in E1 corroborates
   this from the frozen parser, not just from my awk.
7. **The baseline is byte-identical to the base rev**, so it is a valid "before" anchor:
   worktree `sha256(corpus/SOURCES.md)` = `4179f088…` = `sha256(git cat-file blob 3ab461a7…)`,
   and `git status --porcelain -- corpus/SOURCES.md` is empty. Location: Evidence header.
8. **The census tool cannot be bound to a lane revision.** `sources-census.sh` lives at
   `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh` (fleet tree), not inside
   souji-shokunin, so a lane receipt can record its sha256 (`3fb7261…`, mtime 2026-10-19) but the
   digest is not resolvable through the lane's `git cat-file <rev>`; the C2 verifier's
   "committed blob at the named revision" rule has no lane-local object to compare against for
   this tool. Location: Evidence header + preregistration C2 kill rule. `[INFERENCE]` for the C2
   consequence: such a receipt needs either a fleet-rev field or a vendored copy, and that choice
   is the L1's, not mine.
9. **Baseline deltas the round must move (C3 target restated against measured base):** rows
   114 → >=117 (+3), malformed stays 0, duplicate ids stay 0, census exit stays 0. Location:
   preregistration C3 targets vs E1/E2/E6/E7.

## Attack log

- **A1 — the "census exit 0" clause of C3's target is vacuous at base.** Measured base exit is
  already `0` (E1: warnings only, `W04` never changes status per the tool's own contract comment
  at `scripts/sources-census.sh:17`). A do-nothing control therefore satisfies that conjunct; the
  only discriminating clause is `rows 114 -> >=117` with `0 malformed` and `0 duplicate ids`. Not
  edited — reported per contract. Suggested framing for the L1's verdict text: exit 0 is
  necessary-not-sufficient, and the row count is the control.
- **A2 — the brief's "3rd `|`-cell bucket A/B/C" names the wrong cell.** Cell 3 is `kind`
  (docs/code/community/spec/book/own-work); A/B/C is cell 4, `tier`. Measured kind histogram, for
  the record: docs 101, code 6, own-work 3, community 2, spec 1, book 1 (sum 114). A round-end
  re-run script that hard-codes cell 3 will bucket kinds and silently report "A=0 B=0 C=0". Use
  `$5` (E4) or the header-name lookup, never a positional cell index taken from prose.
- **A3 — exit code cannot detect a citation-only re-append.** `E03` (duplicate id) is the only
  fatal id check; a row re-appended under a *new* id with an already-used URL+scope produces at
  most `E04`/`W04`, and `W04` leaves exit 0 (`scripts/sources-census.sh:17`, E1 shows 30 such
  warnings exiting 0). So "census exit 0 + rows >= 117 + 0 dup ids" does not by itself prove the
  C3 re-pointing rule was honoured. `[INFERENCE]`: the real evidence for re-pointing is
  `souji-gate-check.py --entries … --expect-slice 0` (entries=2 ok=2 fail=0), and the census
  receipt should be read as a shape check, not a provenance check. Preregistered control
  (append staged S112–S114 as-is → E03) remains valid and is *not* weakened by this.
- **A4 — W04 baseline is 30 and will drift silently.** Any append that shares a URL with an
  existing row adds a W04 line without changing the exit code, so a round-end diff of the
  validate output will show new warnings that look like regressions but are advisory by design.
  The L1 should diff the W04 *set*, not the count, or state that W04 is out of scope.

No installs or upgrades were performed this run; no `pacman` transaction was attempted. Scratch
used `/var/tmp/souji-r23-ScoutRegistryCensus/` (single captured stdout file) and was removed
before finishing. No write occurred outside
`/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-23/w1/ScoutRegistryCensus.md`.
