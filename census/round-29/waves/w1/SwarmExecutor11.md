# SwarmExecutor11 — quarantine slice + gate dry run (C3SliceGate)

## Status
STATUS: PASS — the §6 item-10 awk derives an 8-row slice whose id set is identical to `census/round-24/records/quarantine-slice`; `deliver-slice-verdicts.tsv` carries 8 gate-vocabulary rows (7 `carried r24`, S118 re-grounded on the PDF opened this run); the gate dry run is green at the committed root with an existing source id (`fail=0`), green on a mirrored registry carrying S216–S219 (`fail=0`), and the as-specified command fails only on `check5-dangling-source` for the two not-yet-landed ids.

## Evidence

Lane revision: `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD` → `b8cb4b31ce80e2e3314b88e85d40ea9873180804` (prereg); lane base `691dd29211c53d0ef94fa072394cb9c8a69fe92e`.

**1. Slice derivation** (awk copied from round prompt §6 item 10, output redirected to the L1-assigned `w1` path; the register was read, never written):

```
A=/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-29/w1/assimilation   # mkdir -p, created empty by the wave
R=/home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md
awk -F'|' -v l='souji' '$2 ~ ("`" l "`") && $3 ~ /round[0-9]+/ && $4 ~ /S[0-9]+/ \
  {print $4, $5}' "$R" > "$A/quarantine-slice"
```

Output (8 lines, `wc -l` → `8`):

```
 S114   `payload-absent`
 S123   `payload-absent`
 S124   `payload-absent`
 S126   `payload-absent`
 S131   `payload-absent`
 S133   `payload-absent`
 S138   `payload-absent`
 S118`   the cited source could not be fetched, so no quote was checked
```

Id-set comparison against r24 (campaign ids): `grep -oE 'S[0-9]{3}'` on both files, sorted, `diff` → empty; `ID-SET-IDENTICAL 8 ids`.

**2. S118 re-grounding** (bytes opened this run):

```
curl -sS -L -o broder97resemblance.pdf -w 'http=%{http_code} bytes=%{size_download} ctype=%{content_type}\n' \
  https://www.cs.princeton.edu/courses/archive/spring13/cos598C/broder97resemblance.pdf
  -> http=200 bytes=254930 ctype=application/pdf
sha256sum broder97resemblance.pdf
  -> da1227992d4a308f9f6f9f99893fd7b00c26e6cf757b1372f426074c101ef56b
pdftotext -layout broder97resemblance.pdf broder.txt      # pdftotext version 26.08.0
grep -n 'resemblance r(A, B)' broder.txt                 # -> 10: and 32:
```

Required sentence, PDF page 1 Abstract, `broder.txt` lines 9–11, verbatim quote (16 words):
"resemblance r(A, B) and their containment c(A, B) that seem to capture well"
Location: https://www.cs.princeton.edu/courses/archive/spring13/cos598C/broder97resemblance.pdf p.1 Abstract (sentence start "Given two documents A and B we define two mathematical notions: their"), PDF sha256 `da1227992d4a308f9f6f9f99893fd7b00c26e6cf757b1372f426074c101ef56b`.

**3. Gate dry runs** — two stub entries authored in scratch (front matter `source: S216` / `source: S217`, `## Gate` with an https URL, `opened: 2026-10-25`, quoted span ≤25 words with a `DESCRIPTION` locator, `snapshot:` inside `/var/tmp/souji-r29-C3SliceGate/snapshots/`, one `- ADMIT:` and one `- REJECT:` each with `reason:`), snapshots being excerpts of the locally rendered `statx(2)` / `cmp(1)` man pages. Commands as specified:

```
python3 -B tools/souji-gate-check.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --round-date 2026-10-25 \
  --entries <e1-identity.md> <e2-byte-equality.md> --snapshot-dir /var/tmp/souji-r29-C3SliceGate/snapshots \
  --slice .ufo/waves/round-29/w1/assimilation/quarantine-slice \
  --slice-verdicts .ufo/waves/round-29/w1/deliver-slice-verdicts.tsv
FAIL .../e1-identity.md check5-dangling-source: S216
FAIL .../e2-byte-equality.md check5-dangling-source: S217
entries=2 ok=0 slice_verdicts=8 slice_total=8 fail=2          rc=1
```

Green control, same templates with `source: S215` (an id the committed registry holds), same root/slice/verdicts:

```
entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0          rc=0
```

Green control on a mirrored registry (`/var/tmp/souji-r29-C3SliceGate/mirror/corpus/SOURCES.md` = committed copy plus four stub rows S216–S219), entries still citing S216/S217:

```
entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0          rc=0
```

Negative controls (four deliberately broken entries + a verdict file with the 8 good rows plus four malformed rows), mirror root:

```
FAIL .../c1-wrong-date.md check2-opened-date: found ['2026-10-24'] want 2026-10-25
FAIL .../c2-long-quote.md check3-quote-50-words-gate-line-6
FAIL .../c2-long-quote.md check3-no-located-quote-with-snapshot
FAIL .../c3-quote-absent.md check4-quote-absent-from-snapshot-line-6
FAIL .../c3-quote-absent.md check3-no-located-quote-with-snapshot
FAIL .../c4-no-reject.md check6-no-reject
FAIL slice verdict-bad-class-line-11:bogus-class
FAIL slice verdict-short-row-line-12
FAIL slice verdict-no-evidence-line-13
FAIL slice verdict-duplicate:S131
entries=4 ok=0 slice_verdicts=8 slice_total=8 fail=10         rc=1
```

Delivered verdict bytes: 8 data rows, 3 tab fields each (`awk -F'\t'` → `fields=3` for every row, classes `accepted`, ids S114 S123 S124 S126 S131 S133 S138 S118); the five leading `#` lines are skipped by `check_slice`.

## Findings

1. **Slice = 8 rows, same id set as r24.** `.ufo/waves/round-29/w1/assimilation/quarantine-slice` vs `census/round-24/records/quarantine-slice`: `diff` empty. The register's header and `## By lane` totals were not used (§6 says they are stale); only data rows matched the awk predicate.
2. **The register's S118 row is malformed, not `payload-absent`.** `/home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md:361` (the last data row) has its cells shifted one column left: its id cell is `S118` followed by a stray backtick, its third cell holds the prose `the cited source could not be fetched, so no quote was checked`, and its cited-source cell is `https://doi.org/10.1109/SEQUEN.1997.666900` with no quote cell at all. Every other slice row is `payload-absent`. The gate tool extracts ids only (`SLICE_ID_RE`), so the shift does not affect `slice_total`.
3. **S118 verdict: `accepted`, unchanged pass class, new grounding.** The pass class is the r24+ collapsed one (`corpus/lessons/round-25.md:42-44`: detail `present`/`present-via-mirror`/`present-quote-needs-fix` map to gate `accepted`, and the r24 vocabulary collapses r22's `present` and `accepted` into one `accepted`), so re-opening the PDF strengthens the evidence without a re-grade. The required sentence exists at p.1 Abstract in the fetched PDF; r24's report that `doi.org` itself answers 202 with 0 bytes was **not re-probed this run** — that part is carried, not re-measured.
4. **The as-specified failure is registry state, not the entry template.** The two `check5-dangling-source` lines are S216/S217, which `corpus/SOURCES.md` at `b8cb4b3` does not hold (139 registry rows, last id S215); C3 lands them. The `source: S215` control proves the rest of the template passes against the committed registry (`fail=0`), and the mirrored registry proves it passes once S216–S219 exist.
5. **Failure-case → sub-check map** (each exercised above):

| failure case | sub-check(s) hit |
|---|---|
| opened date ≠ round date | `check2-opened-date` (a missing https URL would add `check2-no-url`) |
| quote longer than 25 words | `check3-quote-N-words-gate-line-N` plus `check3-no-located-quote-with-snapshot` when it was the only quote |
| quote with no locator token | `check3-no-locator-gate-line-N` |
| quote absent from the named snapshot | `check4-quote-absent-from-snapshot-line-N` (+ `check3-no-located-quote-with-snapshot`) |
| snapshot outside `--snapshot-dir`, unnamed, or missing | `check4-snapshot-outside-dir-line-N`, `check4-no-snapshot-named-line-N`, `check4-snapshot-missing-line-N` |
| front-matter source id absent from `corpus/SOURCES.md` | `check5-dangling-source: S216` (as-specified run) |
| no `source:` line | `check5-no-source-citation` |
| ADMIT or REJECT row missing / no `reason:` | `check6-no-admit`, `check6-no-reject`, `check6-row-without-reason` |
| verdict class outside the four-word set | `verdict-bad-class-line-N:CLASS` |
| verdict row with fewer than 3 fields | `verdict-short-row-line-N` |
| verdict row with empty evidence | `verdict-no-evidence-line-N` |
| same id twice | `verdict-duplicate:ID` |
| verdict file covering fewer than `slice_total` ids | not a `fail` entry: `tools/souji-gate-check.py:174-177` counts a missing row in neither V nor F, so only the `V==T` condition turns rc 1 with `fail=0` (code reading, not executed this run) |

6. **Path deviation, for the L1 only.** §6 item 10's awk writes to `.ufo/waves/round-29/assimilation`; this seat was assigned `.ufo/waves/round-29/w1/assimilation`. The slice content is byte-identical to what the prompt's path would receive from the same register bytes; copy it if the canonical location is wanted.
7. **Write scope held.** No writes outside `souji-shokunin/.ufo/waves/round-29/w1/`; the register, `census/round-24/records/slice-verdicts.tsv`, the lane's index, jj state and all fleet paths were read-only. No tool was installed (existing `pdftotext` 26.08.0 / poppler; no pacman transaction). Scratch `/var/tmp/souji-r29-C3SliceGate/` removed after the runs.
8. `git status --short` at close shows only the pre-existing ` M .ufo/waves/round-26/w1/ScribeGateDraft.md` (already modified before this seat started). The seat's three files are under `.ufo/waves/`, which `.gitignore:1` ignores (`git check-ignore -v` → `.gitignore:1:.ufo/waves/` for all three), so the tracked tree is unchanged. The `check5-dangling-source` failure in the as-specified run is therefore a property of the committed registry, not of local files.

## Deliveries
- `.ufo/waves/round-29/w1/assimilation/quarantine-slice` — 8-row slice from the §6 item-10 awk.
- `.ufo/waves/round-29/w1/deliver-slice-verdicts.tsv` — 8 gate-vocabulary verdict rows (7 `carried r24`, new S118 grounding).
- `.ufo/waves/round-29/w1/SwarmExecutor11.md` — this report.
