# LabSourcesCensus — souji round 26, w1 (runnable census probe)

Seat: leaf lab. Read-only for the lane; every write is this report plus scratch under
`/var/tmp/souji-r26-LabSourcesCensus/` (removed at the end). No tools installed or upgraded.
No `git add/commit/push/stash/checkout/reset`, no `jj` mutation, no signal. Certification OFF.

## Status

STATUS: PARTIAL — every requested census arm and the fleet validator return zero at the
frozen rev `89e0fcee`, with the controls proving each arm can fire; but five registry rows
violate the `status`/`used-by` contract (`/home/vgpnk/Projects/shokunin/CORPUS.md:103,107`)
and no arm in the specified set can see them. The assignment's `CORPUS.md` lane path does not
exist at any revision.

## Evidence

Revisions. Probe target `89e0fceeefcf28db313c94120be6d25e03c60094`; `corpus/SOURCES.md` there
is sha256 `8252728f8fde08004b67492c1b9098d688c904149188248bb66cb7f2853d5859`, 200 lines,
127 registry rows. Lane base `0eca7c8a5d10bcbfdae50d0c390d277deec63bfd` has the **byte-identical**
`corpus/SOURCES.md` (same sha256), and `git rev-parse 0eca7c8:corpus/knowledge` =
`89e0fcee:corpus/knowledge` = `06c05daa7cef7d876ce2dc83527c12a0ffc0d8f9`, so anything found
below is the round's starting state, not introduced by it. Lane HEAD at probe time was
`0833de9` (C1 + C3 landed) with an uncommitted C2 working-tree append (132 rows).

Method. `CORPUS.md` lives at the fleet root, not the lane: the frozen census block is
`/home/vgpnk/Projects/shokunin/CORPUS.md:131-149`, headed
"### Census — run from the lane root (tested 2026-10-19 on a synthetic table)" (CORPUS.md:131,
quoted from bytes opened this run). To run the seven commands **verbatim** (they name
`corpus/SOURCES.md` and resolve `used-by` relative to cwd via `[ -e ]`) without writing in the
lane, I built `/var/tmp/souji-r26-LabSourcesCensus/lane/` containing
`corpus/SOURCES.md` = `git show 89e0fcee:corpus/SOURCES.md`, with `corpus/knowledge`,
`corpus/lessons` and `tools` symlinked read-only into the lane. Commands below are copied
character-for-character from CORPUS.md:134-149; only cwd differs from a lane root.

```
$ cd /var/tmp/souji-r26-LabSourcesCensus/lane && bash /var/tmp/souji-r26-LabSourcesCensus/probe.sh
# rows (spacing-tolerant)
grep -cE '^\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|' corpus/SOURCES.md
127
# malformed rows — 11 columns means NF=13; must print 0
awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ && NF!=13 {n++} END{print n+0}' corpus/SOURCES.md
0
# tier histogram
awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ {t=$5; gsub(/[[:space:]]/,"",t); n[t]++} END{for(k in n) printf "%s=%d ", k, n[k]; print ""}' corpus/SOURCES.md
A=120 B=5 C=2 
# status histogram
awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ {s=$9; gsub(/[[:space:]]/,"",s); n[s]++} END{for(k in n) printf "%s=%d ", k, n[k]; print ""}' corpus/SOURCES.md
mined=103 queued=15 rejected=9 
# duplicate ids — must print nothing
awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ {i=$2; gsub(/[[:space:]]/,"",i); print i}' corpus/SOURCES.md | sort | uniq -d
(no output)
# enum violations and tier inflation — must print nothing
awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ && NF==13 {i=$2;k=$4;t=$5;s=$9; gsub(/[[:space:]]/,"",i); gsub(/[[:space:]]/,"",k); gsub(/[[:space:]]/,"",t); gsub(/[[:space:]]/,"",s); if (t !~ /^[ABC]$/) print "tier", i, t; if (s !~ /^(queued|mined|rejected)$/) print "status", i, s; if (k !~ /^(spec|docs|paper|code|tool|dataset|talk|book|community|own-work)$/) print "kind", i, k; if (t=="A" && k=="community") print "tier-inflation", i}' corpus/SOURCES.md
(no output)
# mined rows whose used-by paths do not exist — must print nothing
awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ && NF==13 {s=$9; gsub(/[[:space:]]/,"",s); if (s=="mined") {n=split($12, a, /[,;]/); for (j=1;j<=n;j++) {p=a[j]; gsub(/^[[:space:]]+|[[:space:]]+$/,"",p); if (p!="" && p!="—") print p}}}' corpus/SOURCES.md | while read -r p; do [ -e "$p" ] || echo "missing: $p"; done
(no output)
rc=0
```

Validator, exactly as requested (live lane working tree):

```
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji
exit=0
# tail (34 W04 lines precede it; no E/W-other line in the whole output)
souji	W04	S124 duplicate url git-scm.com/docs/gitrepository-layout across scopes
souji	W04	S125 duplicate url git-scm.com/docs/git across scopes
souji	W04	S126 duplicate url git-scm.com/docs/git-worktree across scopes
souji	ok	/home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
```

Same validator against the at-rev mirror (`--file`, 127-row bytes): **exit 0**, same 34 W04
lines (S035…S126), final line `file	ok	/var/tmp/souji-r26-LabSourcesCensus/lane/corpus/SOURCES.md`.

Cross-check against the maintained parser (agreement with the frozen commands):

```
$ sources-census.sh census --file <at-rev>/corpus/SOURCES.md
file	rows	127        FLEET	tier.A	120   FLEET	tier.B	5   FLEET	tier.C	2
file	tier.A	120        FLEET	tier.invalid	0
file	tier.B	5          FLEET	status.queued	15   FLEET	status.mined	103
file	tier.C	2          FLEET	status.rejected	9    FLEET	status.invalid	0
file	status.mined	103  FLEET	missing	0
file	status.queued	15
file	status.rejected	9
exit=0
```

Structural checks at the rev: ids are contiguous `S001`–`S127` (127 ids, `diff` against
`seq -f 'S%03g' 1 127` clean); all 127 rows have NF=13; exactly one `## Registry` heading
(file:18) and no row-shaped line outside it (validator E12 silent); zero indented
(0–3 space) rows, so the frozen column-zero examples and the maintained parser cannot diverge
here. Frozen literal reproduction at the freeze commit: C1 `markers=2`, headings
`17 175 231 `; C2 K1 grounded-F1 = 0 at both `0eca7c8` and `89e0fcee`; C2 K3 base row count
at `0eca7c8` = 127; knowledge entries carrying a `ground:` line at the rev = 7, matching the
frozen `grounded=7` K4 base.

Falsifiability controls (scratch copies; a "prints nothing" arm is worthless unless it fires):

```
$ bash /var/tmp/souji-r26-LabSourcesCensus/controls.sh
=== CONTROL C2-malformed: drop one cell from S010 (expect 1)
1
=== CONTROL enum: tier B->D on S014 (expect tier violation + D in histogram)
A=120 B=4 C=2 D=1
tier S014 D
=== CONTROL dup: duplicate the S020 row (expect S020 printed once)
S020
=== CONTROL used-by-missing: point mined S001 used-by at corpus/knowledge/NOPE.md
missing: corpus/knowledge/NOPE.md
=== CONTROL validator E11 on the SAME mutated file (expect E11 + exit 1)
file	E11	S001 missing used-by corpus/knowledge/NOPE.md
validator_exit=1
=== CONTROL directory-shaped used-by: mined S001 used-by = corpus/knowledge (a directory)
(no output)                        # frozen arm passes a directory
file	ok	…/ctl/corpus/SOURCES.md
validator_exit=0                   # maintained validator passes it too
```

Rev-faithful confirmation that the `used-by` result is not an artefact of the symlinked
mirror: all 21 distinct `used-by` paths of mined rows also resolve in the rev tree
(`git cat-file -e 89e0fcee:<p>` for each: no `MISSING-AT-REV`).

## Findings

1. **Five registry rows break the `status`/`used-by` contract, and the specified census
   cannot see it.** Contract (`/home/vgpnk/Projects/shokunin/CORPUS.md:103`): "`status` —
   `queued` (opened, worth mining) · `mined` (cited by ≥1 path in `used-by`) ·"; and
   (CORPUS.md:107): "`used-by` — repo-relative paths of the knowledge entries or lessons
   citing the row, comma-separated, or `—`." Against every `^source:` citation line of the
   15 `corpus/knowledge/*.md` entries at `89e0fcee` (54 id↔entry pairs, 52 distinct ids), five
   rows do not list an entry that cites them:
   - `corpus/SOURCES.md:43` `S022` — `status=mined`, `used-by=corpus/knowledge/trash-spec-restorable-quarantine.md`;
     also cited by `corpus/knowledge/quarantine-origin-record-fields-r24.md:4`
     (`source: S022 — https://specifications.freedesktop.org/trash/latest/ …`), which is a
     `ground: F4` entry named in `corpus/README.md:42`.
   - `corpus/SOURCES.md:96` `S075` and `:97` `S076` — `status=mined`,
     `used-by=corpus/lessons/round-18.md`; also cited by
     `corpus/knowledge/process-residue-observations.md:1` and `:103`, the admitted F5 entry
     named in `corpus/README.md:274` ("`knowledge/process-residue-observations.md` (S082–S085;
     S075/S076 rechecked)").
   - `corpus/SOURCES.md:45` `S024` and `:46` `S025` — `status=queued`, `used-by=—`, yet cited
     by `corpus/knowledge/quarantine-same-filesystem-rename.md:1`
     (`source: S025 … ; S024 …`), an F4 entry held per `corpus/README.md:42`. Either the rows
     are stale (they are cited, so the contract's `mined` applies) or the entry is held while
     resting on rows the registry calls unmined; both readings are a registry defect.
   Pre-existing: `corpus/SOURCES.md`, the `corpus/knowledge` tree and `corpus/README.md` are
   byte-identical at base `0eca7c8` and freeze `89e0fcee`, so this is the starting state.
   Invisible to: all seven frozen arms (CMD7 is forward-only, `[ -e ]` on paths), validator
   `E11` (existence only) and `W03` (mined with `used-by=—`; here `used-by` is non-`—` for
   S022/S075/S076). Consequence for this round: C2 K3's "mined used-by paths missing 0" is a
   path-existence arm only and MUST NOT be read as used-by integrity.

2. **The assignment's census spec path does not exist in the lane.**
   `/home/vgpnk/Projects/shokunin/souji-shokunin/CORPUS.md` is absent in the working tree, in
   `89e0fcee`'s tree, and in all history (`git log --all -- CORPUS.md` is empty). The frozen
   commands are at `/home/vgpnk/Projects/shokunin/CORPUS.md:131-149`. Lane prose that cites
   "CORPUS.md rules" (`corpus/QUALITY.md:7`, `corpus/lessons/round-22.md:301,319`) refers to
   the fleet-root file, so the path in the assignment was wrong, not the lane.

3. **The `mined used-by` arm accepts a directory, so it does not check that `used-by` names a
   knowledge entry.** `[ -e corpus/knowledge ]` is true for a directory. Demonstrated above:
   a mined row whose `used-by` is the bare directory `corpus/knowledge` passes both the frozen
   arm and `sources-census.sh validate` (exit 0). Same class: `[ -e ]` also accepts a symlink
   or an empty file. No current row exploits it (all `used-by` values are `.md` paths files).

4. **The frozen v1 census has no Registry scoping; the maintained parser does.** Every arm
   matches `| S###` rows anywhere in the file, while `sources-census.sh` adds `E12` for
   row-shaped lines outside `## Registry`. No divergence at this rev (one Registry table, zero
   rows outside it, zero indented rows), so the numbers agree exactly; the frozen arm would
   count a row pasted into `## Search log` that `E12` rejects.

5. **State drift, not an attack.** The live working tree already holds the C2 append
   (132 rows, mined 108, tier A 125; +5 rows over the freeze rev). The live validator is
   exit 0 with the same 34 W04 warnings, so the in-flight state is not dirtier than the
   freeze state under the specified arms. Recorded because the requested validator command
   reads the working tree, not `89e0fcee`.

## Attack log

- ATTACK A1 (calibration, HIGH, fires on real data): the `used-by` contract is one-directional
  in the counter set. Five rows (`S022`, `S024`, `S025`, `S075`, `S076`) omit a citing entry or
  carry a status contradicting the contract; all seven frozen arms and the fleet validator
  return clean. Fix direction (stricter-only, for a future prereg, not proposed for this
  round's predicates): add a reverse arm — every id on an entry's `^source:` lines must appear
  in that row's `used-by`, and every cited row must be `mined` — plus a `[ -f ]` rather than
  `[ -e ]` test. Not a kill for C2: C2's K3 predicate is unchanged and its own `used-by` rule
  applies to the two new entries, which this seat did not evaluate.
- ATTACK A2 (calibration, MEDIUM): directory/symlink/empty-file shaped `used-by` passes both
  the frozen arm and `E11` (A1's third sentence, exercised).
- ATTACK A3 (premise, LOW): the assignment places `CORPUS.md` in the lane; it is at the fleet
  root. Any seat scoring "the frozen census from the lane's CORPUS.md" would have to invent
  commands. The lane's own drift is not implicated.
- ATTACK A4 (latent, LOW): frozen arms are registry-unscoped while the maintained parser is
  not (`E12`); no divergence on current bytes.
- Not an attack: zero-row/asymmetry controls all fired, id contiguity and NF=13 hold, validator
  exit 0 at both the freeze rev and the live tree, and every frozen base literal reproduces.

Scratch `/var/tmp/souji-r26-LabSourcesCensus/` removed after the run.
