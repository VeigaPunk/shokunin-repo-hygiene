# Round 26 census-after recipe (claim C2, counter K3)

Recipe only: nothing here counts as after-evidence until the L1 runs it at the landing tip.
Both blocks are read-only. Run from any cwd; every lane path below is absolute.

Preconditions: run at the landing tip in a clean tree. The S128–S132 append is already
committed (commit `0833de9` touches `corpus/SOURCES.md`; HEAD at preparation time
`c5949013f89fe0b8289bdb7050ab64a47e08c911`), and the C1/C3 commits do not touch
`corpus/SOURCES.md`, so the expected values below are stable for this round's tip
[INFERENCE for a later tip that also leaves SOURCES.md unchanged].

## 1. Validate — exact command (prereg C2 K3)

```sh
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji; echo "rc=$?"
```

Expected at tip: `rc=0`, 34 `souji	W04	…` lines, zero `souji	E…` lines, last line
`souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md`, registry row count 132.

Paste-ready excerpt (observed at `c594901`, with the first and last W04 lines shown):

```text
souji	W04	S035 duplicate url git-scm.com/docs/git-repo across scopes
…
souji	W04	S126 duplicate url git-scm.com/docs/git-worktree across scopes
souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
rc=0
```

W04 is a warning by contract (`scripts/sources-census.sh:33`: "W04 same URL across scopes
(warnings do not affect clean lanes)") and does not affect the exit code. The count is
unchanged 34 → 34 because S128–S132 add no URL+scope pair that duplicates an existing row
(S129/S130 are new github.com/git/git tag-v2.56.0 URLs; S131/S132 are own-work rows with no URL).
[INFERENCE on the reason; the count is observed.]

## 2. Manual census — frozen block, `CORPUS.md:131-151`

Run from the lane root: `cd /home/vgpnk/Projects/shokunin/souji-shokunin`. Commands are the
frozen block verbatim; expected values are the after-state. These are the six table-integrity
greps (checks 1–6) plus the block's seventh command, the used-by existence loop (check 7).

### Check 1 — rows

```sh
grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md
```
After: `132`

### Check 2 — malformed rows (must print 0)

```sh
awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ && NF!=13 {n++} END{print n+0}' corpus/SOURCES.md
```
After: `0`

### Check 3 — tier histogram

```sh
awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ {t=$5; gsub(/[[:space:]]/,"",t); n[t]++} END{for(k in n) printf "%s=%d ", k, n[k]; print ""}' corpus/SOURCES.md
```
After: `A=125 B=5 C=2 ` (sums to 132)

### Check 4 — status histogram

```sh
awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ {s=$9; gsub(/[[:space:]]/,"",s); n[s]++} END{for(k in n) printf "%s=%d ", k, n[k]; print ""}' corpus/SOURCES.md
```
After: `mined=108 queued=15 rejected=9 ` (sums to 132)

### Check 5 — duplicate ids (must print nothing)

```sh
awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ {i=$2; gsub(/[[:space:]]/,"",i); print i}' corpus/SOURCES.md | sort | uniq -d
```
After: no output

### Check 6 — enum violations and tier inflation (must print nothing)

```sh
awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ && NF==13 {i=$2;k=$4;t=$5;s=$9; gsub(/[[:space:]]/,"",i); gsub(/[[:space:]]/,"",k); gsub(/[[:space:]]/,"",t); gsub(/[[:space:]]/,"",s); if (t !~ /^[ABC]$/) print "tier", i, t; if (s !~ /^(queued|mined|rejected)$/) print "status", i, s; if (k !~ /^(spec|docs|paper|code|tool|dataset|talk|book|community|own-work)$/) print "kind", i, k; if (t=="A" && k=="community") print "tier-inflation", i}' corpus/SOURCES.md
```
After: no output

### Check 7 — mined used-by paths missing (must print nothing)

```sh
awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ && NF==13 {s=$9; gsub(/[[:space:]]/,"",s); if (s=="mined") {n=split($12, a, /[,;]/); for (j=1;j<=n;j++) {p=a[j]; gsub(/^[[:space:]]+|[[:space:]]+$/,"",p); if (p!="" && p!="—") print p}}}' corpus/SOURCES.md | while read -r p; do [ -e "$p" ] || echo "missing: $p"; done
```
After: no output (27 distinct mined used-by paths, all present)

Column-zero regexes: the maintained parser accepts 0–3 leading spaces (`CORPUS.md:152-154`);
at the tip there are 0 indented row-shaped lines, so the manual and parser counts agree
(`grep -cE '^ {1,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md` → `0`).

Optional corroboration (not part of K3, same numbers):

```sh
/home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --root /home/vgpnk/Projects/shokunin souji
```
Observed: `souji	rows	132`, `tier.A 125`, `tier.B 5`, `tier.C 2`, `status.mined 108`,
`status.queued 15`, `status.rejected 9`, `FLEET.rows 132`, `missing 0`, rc 0.

## 3. Expected-delta table (deliverable for the report)

Base 0eca7c8a5d10bcbfdae50d0c390d277deec63bfd (`corpus/SOURCES.md` blob `f3cffccd…`);
tip `c594901` (blob `35747ad6…`).

| measure | before (0eca7c8) | after (tip) | delta | source |
|---|---|---|---|---|
| registry rows | 127 | 132 | +5 | manual check 1 / C2 K3 |
| tier A | 120 | 125 | +5 | manual check 3 |
| tier B | 5 | 5 | 0 | manual check 3 |
| tier C | 2 | 2 | 0 | manual check 3 |
| status mined | 103 | 108 | +5 | manual check 4 |
| status queued | 15 | 15 | 0 | manual check 4 |
| status rejected | 9 | 9 | 0 | manual check 4 |
| malformed rows | 0 | 0 | 0 | manual check 2 |
| duplicate ids | none | none | 0 | manual check 5 |
| enum / tier-inflation findings | none | none | 0 | manual check 6 |
| mined used-by missing | none | none | 0 | manual check 7 |
| validate exit | 0 | 0 | 0 | section 1 |
| validate W04 warnings | 34 | 34 | 0 | section 1 |
| validate E-codes | 0 | 0 | 0 | section 1 |

Sum checks: 120+5+2 = 127 and 103+15+9 = 127 (before); 125+5+2 = 132 and 108+15+9 = 132 (after).

**Tier arithmetic (correcting the planning hint).** The append block's five rows are all
tier A and all status mined — committed cells at `corpus/SOURCES.md:149-153`:
S128 docs/A, S129 code/A, S130 code/A, S131 own-work/A, S132 own-work/A. Therefore tier A is
**+5, not +3**; no existing row changed tier or status (B, C, queued, rejected are all
unchanged). The hint's "+3" matches neither the draft block
(`.ufo/waves/round-26/w1/sources-append-block.md`) nor the committed registry.

## 4. Paste-ready after block

```text
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji; echo rc=$?
souji	W04	… (34 W04 warning lines, byte-identical to .ufo/waves/round-26/census-before.txt) …
souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
rc=0

# CORPUS.md §Census, from the lane root
rows:            132
malformed:       0
tiers:           A=125 B=5 C=2
statuses:        mined=108 queued=15 rejected=9
duplicate ids:   (none)
enum/tier:       (none)
used-by missing: (none)
```

## 5. Provenance of the values in this recipe

- Base values: `git show 0eca7c8a5d10bcbfdae50d0c390d277deec63bfd:corpus/SOURCES.md` piped
  through the frozen commands of section 2 (this run).
- After values: frozen commands and `validate` run this run at `c594901` against
  `/home/vgpnk/Projects/shokunin`; `validate` output `diff`-empty against
  `.ufo/waves/round-26/census-before.txt`.
- Append commit: `git log -S'S128' -- corpus/SOURCES.md` → `0833de9`.
- Row locations: S128 at `corpus/SOURCES.md:149`, S129:150, S130:151, S131:152, S132:153.
