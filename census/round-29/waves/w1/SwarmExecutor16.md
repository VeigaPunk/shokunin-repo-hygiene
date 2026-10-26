# SwarmExecutor16 — C3 landing rehearsal (scratch clone)

## Status

STATUS: PASS — the C3 set lands clean in a scratch clone on top of the prereg commit: grounded F3 2, SOURCES rows 143, coverage `grounded=15 mapped=15 dangling=0 mismatches=0` (rc 0), gate `entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0` (rc 0) once the sibling slice inputs sit at the prereg paths, `sources-census.sh validate` rc 0 in both `--file` and lane-dir modes, and the C1 counter adds **zero** K1 rows (its 6 are the base set, unchanged). The prereg's `k1=0` line belongs to C1's own landing and is not reachable from a C3-only commit; that is the single deviation from the item's expected list, and it is proved to be C1's, not mine.

Scratch root: `/var/tmp/souji-r29-C3RehearseAdmit.C5mrSs` (clone at `.../c`, removed before yield).
Clone lineage: `691dd29` (base) → `b8cb4b3` (prereg, clone HEAD) → `53264d0` (C3 landing rehearsal) → `68b6575` (rehearsal inputs: sibling slice files).

## Evidence

All commands run with `-C`/`cd` on the scratch clone; lane base `691dd29211c53d0ef94fa072394cb9c8a69fe92e`, prereg `b8cb4b31ce80e2e3314b88e85d40ea9873180804`.

```
$ git clone -q --no-local /home/vgpnk/Projects/shokunin/souji-shokunin /var/tmp/souji-r29-C3RehearseAdmit.C5mrSs/c
$ git -C .../c rev-parse --show-toplevel
/var/tmp/souji-r29-C3RehearseAdmit.C5mrSs/c            # required before any commit
$ git -C .../c log --format='%H %P %s' -2
68b657543a318b9e0ef2fb724e6bf8b83f1b1b58 53264d05f4163c876eb9c4ddf297ddba1a9723c3 round-29 C3 rehearsal inputs: sibling quarantine-slice and slice-verdicts at the prereg paths
53264d05f4163c876eb9c4ddf297ddba1a9723c3 b8cb4b31ce80e2e3314b88e85d40ea9873180804 round-29 C3 rehearsal: admit duplicate-verdict identity and byte-equality entries, rows S216-S219 (canonical append block, pinned snapshots)
```

Landing commit `53264d0`, nine paths: `corpus/knowledge/duplicate-verdict-identity.md` (5797 B), `corpus/knowledge/duplicate-verdict-byte-equality.md` (4891 B), `corpus/SOURCES.md` (+4 rows), `corpus/README.md` (1 line), and the five snapshot files under `census/round-29/sources/`.

Counters at tip `68b6575`:

```
$ git grep -lE '^ground: F3' 68b6575... -- corpus/knowledge/ | wc -l
2
$ git show 68b6575...:corpus/SOURCES.md | grep -cE '^[[:space:]]{0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'
143
$ python3 -B tools/souji-coverage-agreement.py --root . --rev 68b6575...
grounded=15 mapped=15 dangling=0 mismatches=0
rc=0
$ python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 \
    --entries corpus/knowledge/duplicate-verdict-identity.md corpus/knowledge/duplicate-verdict-byte-equality.md \
    --snapshot-dir census/round-29/sources \
    --slice census/round-29/records/quarantine-slice --slice-verdicts census/round-29/records/slice-verdicts.tsv
entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0
rc=0
$ bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --today 2026-10-25 --file .../c/corpus/SOURCES.md
file	ok	/var/tmp/souji-r29-C3RehearseAdmit.C5mrSs/c/corpus/SOURCES.md     # rc 0
$ bash .../sources-census.sh validate --today 2026-10-25 .../c
c	ok	/var/tmp/souji-r29-C3RehearseAdmit.C5mrSs/c/corpus/SOURCES.md     # rc 0
$ python3 -B tools/souji-registry-agreement.py --root . --rev 68b6575... --list-rev b8cb4b3...
K1 used-by-no-cite S215 corpus/knowledge/git-auto-maintenance-trigger-set.md
K1 cited-not-in-used-by S075 corpus/knowledge/process-residue-observations.md
K1 cited-not-in-used-by S076 corpus/knowledge/process-residue-observations.md
K1 cited-not-in-used-by S022 corpus/knowledge/quarantine-origin-record-fields-r24.md
K1 cited-not-in-used-by S024 corpus/knowledge/quarantine-same-filesystem-rename.md
K1 cited-not-in-used-by S025 corpus/knowledge/quarantine-same-filesystem-rename.md
SUMMARY k1=6 k2=4 mismatches=10 rev=68b6575...
rc=1
$ diff <(souji-registry-agreement.py --rev 691dd29... --list-rev b8cb4b3... | grep '^K1' | sort) \
       <(souji-registry-agreement.py --rev 68b6575... --list-rev b8cb4b3... | grep '^K1' | sort)
K1-identical-base-vs-tip
```

The only `E`-class finding in either validate mode is none; the sole new warning is `W04 S216 duplicate url man7.org/linux/man-pages/man2/statx.2.html across scopes` (shared with S114 under a different scope), which does not change exit status.

Quotes were verified independently against the pinned snapshot bytes (whitespace-collapsed containment, word counts):

```
PRESENT 5 words statx.2.html  stx_ino; /* Inode number */
PRESENT 7 words statx.2.html  stx_nlink; /* Number of hard links */
PRESENT 14 words link.2.html  This new name may be used exactly as the old one for any operation
PRESENT 15 words cmp.1.html   Exit status is 0 if inputs are the same, 1 if different, 2 if trouble.
PRESENT 23 words broder97resemblance.txt  resemblance r(A, B) and their containment c(A, B) that seem to capture well the informal notions of "roughly the same" and "roughly contained."
```

Snapshots used are the pinned bytes delivered by C3MirrorValidate under `.ufo/waves/round-29/w1/sources/`, verified against its `SHA256SUMS` and copied into the clone at `census/round-29/sources/` (`statx.2.html 2a47fe31…`, `link.2.html 9cb197a7…`, `cmp.1.html 5c68e8d8…`, `broder97resemblance.pdf da122799…`, `broder97resemblance.txt 3ba1e117…`). I did not deliver snapshot bytes (they already exist in `w1/sources/` and are not mine to place).

DOI probe run this seat: `curl … -L https://doi.org/10.1109/SEQUEN.1997.666900` → `status=202 bytes=0 url=https://ieeexplore.ieee.org/document/666900/`.

## Findings

1. **The delivered S217 anchor misattributes the PDF host** — `deliver-sources-append-block.md:15` (row S217) says `author-hosted PDF, 9 pages`. It is not author-hosted: the authors were at DEC SRC, and the only reachable copy this seat could find is a Princeton course-archive mirror (`gatekeeper.dec.com` does not resolve; `hpl.hp.com` tech-report paths time out; the DOI returns 202 with 0 bytes). My rehearsal lands the canonical block with that one phrase replaced by `PDF mirror hosted by a Princeton course archive, 9 pages`; no counter reads the phrase, so the zeros above are identical either way. The L1 should take the corrected cell. Page count 9 is confirmed by `pdfinfo`.
2. **Broder snapshot decode is not reproducible from the committed file alone** — `w1/sources/broder97resemblance.txt` is 21669 B (`3ba1e117…`); my own `pdftotext -layout` decode of the same PDF is 24939 B with a different digest. The quotes hold in the pinned decode, so the landing is safe, but the entry records the decode's sha256 rather than a decode command that a later seat can rerun. Location: `corpus/knowledge/duplicate-verdict-identity.md` `snapshot:` line of S217.
3. **The prereg slice paths do not exist at base** — `census/round-29/records/quarantine-slice` and `census/round-29/records/slice-verdicts.tsv` are absent (`ls` shows only `axis-check-before.txt`, `census-start.txt`, `controls.tsv`, `frozen-digests.txt`, `preregistration.txt`). With the base state the gate prints `FAIL slice slice-missing` / `entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=1` (rc 1) — the entries themselves pass. `fail=0` is reached only when `w1/assimilation/quarantine-slice` and `w1/deliver-slice-verdicts.tsv` are landed at those two exact paths; my rehearsal copies them there and gets 8/8.
4. **C1 `k1=0` is not reachable from a C3-only commit** — the six K1 rows are exactly the base set and none names S216-S219, so the C3 landing is K1-neutral; the target belongs to C1's repair of those six rows. Location: counter output above, diff `K1-identical-base-vs-tip`.
5. **No round-29 provenance paragraph accompanies the appended rows** — every earlier round's appended rows carry a `Round-NN source opening:` paragraph in the prose above `## Registry` (e.g. the Round-25 paragraph at `corpus/SOURCES.md:17`). The canonical append block adds only table rows; no counter reads the prose, so this is a consistency gap for the L1 to decide, not a defect in the measurement.

## Deliveries

- `.ufo/waves/round-29/w1/deliver-duplicate-verdict-identity.md` (sha256 `38635a6dddbf18561af9495906c1c5b9d75a15d9e7a13b3ab9899e7d53530ee8`) — lands verbatim at `corpus/knowledge/duplicate-verdict-identity.md`.
- `.ufo/waves/round-29/w1/deliver-duplicate-verdict-byte-equality.md` (sha256 `4cd1fc45bae36b89902a0b097dc671a367769cd2a96d18f677743144300bd1a8`) — lands verbatim at `corpus/knowledge/duplicate-verdict-byte-equality.md`.
- `.ufo/waves/round-29/w1/deliver-readme-f3-row.md` — the exact `corpus/README.md:41` replacement line and its measured coverage effect.
- Rows S216-S219 are not re-delivered: the rehearsal uses `deliver-sources-append-block.md` verbatim except finding 1's phrase.
