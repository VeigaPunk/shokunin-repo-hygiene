# RevGate — evidence appendix (C2 gate-check review, round 22 attempt 2)

Reviewer seat: `L1Souji22.RevGate`. Report: `../../RevGate.md`.
This file is the fixture transcript log for that report. Everything below was executed; nothing is
inferred unless a line says `[INFERENCE]`.

## A. Identity of the object under review

```
$ cd /home/vgpnk/Projects/shokunin/souji-shokunin
$ git rev-parse HEAD
2a130b47db43eb4b3d80b2e7a5112d6b4b021899
$ git log --oneline -6 -- tools/souji-gate-check.py
a211e4d round-22: declared-evidence audit tool, assimilation entries and gate checker
$ git status --porcelain tools/souji-gate-check.py        # (empty: working tree == HEAD)
$ git rev-parse HEAD:tools/souji-gate-check.py
4309d76930a18891dd1d3446364c4c1dfecc275f
$ sha256sum tools/souji-gate-check.py
d85c269624f4ade5c4ce5a1328c33e7a8f5169c9c14ec71f7f62f74612486b00  tools/souji-gate-check.py
```

Lane base revision per the frozen preregistration: `4edb25d`. The candidate is committed at
`a211e4d`; the lane tip at review time is `2a130b47`. The candidate file is unmodified in the
working tree. `git status --porcelain census/round-22` is empty, so every snapshot, the slice and
the verdicts TSV are reviewed as committed bytes.

## B. Fixture inventory

Root: `.ufo/waves/round-22/attempt2/w1/evidence/gatefix/` (176K, created by this review only;
nothing outside the evidence directory was written). `sha256` manifest, verbatim:

```
c2bdb513aaeff3fda81ab5bdd648cadeecba3c20a963dd5b4f79a15eef31fd3b  ./census/slice
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855  ./census/slice-empty
7b0473eaf29399f40f8ffbe699ab2e603230293b3bba3e379591cc68142d8213  ./census/sources/link-out.txt
53133b0bb1adc63ba4b258d3c4a77e24dfc3cb81a4238eb176da5964830c6ebe  ./census/sources/section-line.txt
b82d4a2612109a65a0d35497dbfcdb13b0611b55e980b8156cb09c95198e959d  ./census/sources/w25.txt
ba96538192930672c7db9518e730cbf51543b6f4426bd657e7d8222a8d223f47  ./census/sources/w26.txt
c38e55a6d1c5f6eb1df1dcbead9aa68fe5a0a33a5c3f0fed5d97a68bc6a96ce3  ./census/sources/x2.txt
a94f79583c9061fd1f75e92612c2888f843f3394b59ff1195f588dc116efaeaa  ./census/sources/x.txt
4f623ac60961d0b70d558bfa286f1e66c20c85ffc50bfbd87c8d8503eb44a670  ./census/verdicts-badclass.tsv
0e6184b31262d4f7908386906302668c165f7b6327458968fb3e34e4185d40be  ./census/verdicts-comment.tsv
859799eac3d1a0092667d9ffd31998dd97ed2752b5703d65faab49eac362d47d  ./census/verdicts-dupe.tsv
efd0a99562975888aedef7fb48395afe89e748541c4ccf58c38e4ebcff435e5e  ./census/verdicts-extra.tsv
64f63ba6383861040fce96ec7c48478c148bcdc90616ecbff07e876ea822eec5  ./census/verdicts-good.tsv
1310d4b3296e53d37cbd84f06aa03d0bcc3453757f3f88cc666b5a8f6179edd0  ./census/verdicts-idinside.tsv
23c52a14dc26f920f0f23fa8e3031fe0a96e717ec46435d3afb296ba046df892  ./census/verdicts-noev.tsv
ef1f666fe231b911e5cefcb12f3d9e9d5d50c49de34dd38629ca045372ae2ac9  ./census/verdicts-partial.tsv
68502e4c2962b9897bda5e8f34301df18dc9af9738c2004dce592853a35bb70b  ./census/verdicts-shortrow.tsv
53629773e5c3fd577ef195f92b787bf9fd9772fdb03db18f40b6375d49385542  ./corpus/SOURCES.md
7b0473eaf29399f40f8ffbe699ab2e603230293b3bba3e379591cc68142d8213  ./elsewhere/y.txt
dc5470af8672c6f31cabe48fb9249c8e6f4edc20a1d3b76fd30ee73ad7dfb35c  ./entries/admit-noreason.md
bb9228c0435317b88f0a2bf80b0a1eade80e1fe9910fda97118f19402015bfb4  ./entries/baddate.md
49fb1f8410330feb9a6d7a90ef0ad2ee4e190968ba6652832e116701445c6cde  ./entries/citedindent.md
96b2822805444be25e340c5f24b69d99a893cdf329c4ac2bcdb01f474a4acfc4  ./entries/citedlist.md
4091e5896c26267c0854da1fba0b0c0f2d63c5430420ea6911b6158c21c5f268  ./entries/dangling.md
9b5eff7861ec3dce817d1c90cdfa0637eac17be5fe51d14b7d96c835b87559ea  ./entries/gatefirst.md
ac8f127b58eca5e09e8980f5ce9e189fd47dcbacd8c233d38f9b7552dc06aa3d  ./entries/good.md
d67b631e7efc2d631e651080a2d008d73172a3fa0c2a4b07f3c1789a910a3f8c  ./entries/locfromfile.md
e15bc50cf2fbb289ecbbe6455f5843c5572e0815205d02005d3d587e874be19e  ./entries/longquote.md
64fe7fb45acd4d513d693959a2c712a4792db92d8c42c16d2b7ccf8193d840a8  ./entries/noadmit.md
56e512f3e8b69ea50b0ff8e61b1c550c22bba97499c4cd7c78a04ae14a7c1610  ./entries/nocite.md
3f6fcdb81b702a9722f46f358b6580abfde9d2503f4c974677ae2e765455a3bd  ./entries/nogate.md
3e08bfe1ccb20651fe8f7feeaf24defb8177eedf48cac2fb515adefb6d3e2851  ./entries/nolocator.md
3dfa5d30a1fbef04afe78da37fb3c887f86225aaf3ba5f65f3bb657b6ab43232  ./entries/noreject.md
3803271697486d41080a452776b60a59c48c163f0c18f9b8325e16e996dbce04  ./entries/nosnap.md
e7073a272be398ba6d21fe98d38aee35879366c1392cc3b72a5f987451d2e13d  ./entries/nourl.md
0431578bee647db82fe8bf7e08e59d6b95263e189c169c7ea42e055764a1a91f  ./entries/perturb.md
e86d8169c48c15f486f774fcfdde9d0076722d132db78ee82698b76e8cc2fa74  ./entries/quote25.md
cb7e29c8458da3d522eec632945b8983101af680d2431eeab0af4787cdbe0f1b  ./entries/quote26.md
c84e6d940da15579ccd43550dd03b9a064a94eb12869c33e08bd518a00233458  ./entries/quoteabsent.md
b13c79951a05a1b6e3b6ee2b72df3d88b13941ab9abd708be21ced17b82793bc  ./entries/reject-emdash.md
0abae1687a2ee41fcd0cf086ccea3c4a3550f36fb8da5dbcac9eb3887382ca08  ./entries/reject-noreason.md
85b02f7da196c885f0b7ee2c64bb97bb89739fadf49d6b38df1b18e08f204d21  ./entries/snapmissing.md
3e2fd6a1b8a160772b60c46752f3914e13a75cf8875e4de3e8162dbee1fc44b8  ./entries/snapoutside.md
f13fb769c418d7e4575ddfebaedae2c8199e47afbd08477ded8fd7ee4efa7e48  ./entries/staged-copy.md
45fb986fdf77e498fab8a68f8f82e753b61ef03a89703d556eb41ddaff4c7448  ./entries/symlinkesc.md
```

Fixture snapshot `census/sources/x.txt` carries the good quote split across a newline, so a match
proves whitespace-collapse rather than a byte-equal search:

```
$ cat -A census/sources/x.txt
Option --no-copy: do not copy, just move.$
RENAME_NOREPLACE do not$
overwrite newpath. Tail sentence here.$
```

`./entries/staged-copy.md` is a byte-exact copy of the staged package entry:

```
$ sha256sum /home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/quarantine-staging-no-copy-r23.md
f13fb769c418d7e4575ddfebaedae2c8199e47afbd08477ded8fd7ee4efa7e48
$ grep -c '## Gate' .../gatefix/entries/staged-copy.md
0
```

## C. Entry-check transcripts

Invocation shape for every case (only `--entries` varies):

```
python3 -B tools/souji-gate-check.py --root <fixture root> --round-date 2026-10-25 \
  --entries entries/<case>.md --snapshot-dir census/sources \
  --slice census/slice --slice-verdicts census/verdicts-good.tsv
```

### C0. The lane's own selftest and the frozen counter (real lane, not fixture)

```
$ python3 -B tools/souji-gate-check.py --selftest
PASS fixture good -> ok [entries=1 ok=1 slice_verdicts=2 slice_total=2 fail=0]
PASS fixture no-date -> fail [entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=1]
PASS fixture long-quote -> fail [entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=2]
PASS fixture quote-absent -> fail [entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=2]
PASS fixture dangling-source -> fail [entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=1]
PASS fixture no-reject -> fail [entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=1]
PASS fixture no-gate -> fail [entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=1]
PASS fixture partial-verdicts -> fail [entries=1 ok=1 slice_verdicts=1 slice_total=2 fail=1]
PASS control always-green -> FALSE-GREEN-REJECTED [FALSE-GREEN-REJECTED]
selftest=9/9
rc=0

$ python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 \
    --entries corpus/knowledge/quarantine-staging-no-copy-r23.md \
              corpus/knowledge/quarantine-origin-record-fields-r24.md \
    --snapshot-dir census/round-22/attempt2/sources \
    --slice census/round-22/attempt2/quarantine-slice \
    --slice-verdicts census/round-22/attempt2/slice-verdicts.tsv
entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0
rc=0
stdout bytes: 52   stdout lines: 1
counts line: [entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0]
MATCHES frozen spelling exactly: entries=<n> ok=<k> slice_verdicts=<v> slice_total=<t> fail=<f>
```

### C1 — check 1 (entry exists, contains `## Gate`)

```
### CASE entry:nogate
FAIL entries/nogate.md check1-no-gate: entries/nogate.md
entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=1
rc=1

### CASE entry:staged-copy   (byte-exact staged package entry, sha f13fb769…)
FAIL entries/staged-copy.md check1-no-gate: entries/staged-copy.md
entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=1
rc=1

### CASE entry:missing-file
FAIL entries/nosuch-entry.md entry-missing: entries/nosuch-entry.md
entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=1
rc=1

### CASE entry:gatefirst      (file starts with "## Gate" at byte 0 — reported as a deviating case)
FAIL entries/gatefirst.md check1-no-gate: entries/gatefirst.md
entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=1
rc=1
```

### C2 — check 2 (https URL + `opened:` == round date)

```
### CASE entry:nourl
FAIL entries/nourl.md check2-no-url
entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=1
rc=1

### CASE entry:baddate
FAIL entries/baddate.md check2-opened-date: found ['2026-10-24'] want 2026-10-25
entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=1
rc=1
```

### C3 — check 3 (located quote, <=25 words)

```
### CASE entry:longquote
FAIL entries/longquote.md check3-quote-26-words-gate-line-6
FAIL entries/longquote.md check3-no-located-quote-with-snapshot
entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=2
rc=1

### CASE entry:nolocator
FAIL entries/nolocator.md check3-no-locator-gate-line-6
FAIL entries/nolocator.md check3-no-located-quote-with-snapshot
entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=2
rc=1

### CASE entry:quote25      (exactly 25 words; snapshot carries them across a newline)
entries=1 ok=1 slice_verdicts=2 slice_total=2 fail=0
rc=0

### CASE entry:quote26      (exactly 26 words)
FAIL entries/quote26.md check3-quote-26-words-gate-line-6
FAIL entries/quote26.md check3-no-located-quote-with-snapshot
entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=2
rc=1

### CASE entry:locfromfile  (no locator token in the line; only the snapshot FILENAME says "section-line")
ADMIT line: - ADMIT: "RENAME_NOREPLACE do not overwrite newpath" — snapshot: census/sources/section-line.txt
entries=1 ok=1 slice_verdicts=2 slice_total=2 fail=0
rc=0
```

### C4 — check 4 (verbatim, whitespace-collapsed, inside `--snapshot-dir`)

```
### CASE entry:good        (positive: quote spans a newline in the snapshot)
entries=1 ok=1 slice_verdicts=2 slice_total=2 fail=0
rc=0

### CASE entry:nosnap      (located quote, no snapshot named on the line)
FAIL entries/nosnap.md check4-no-snapshot-named-line-6
FAIL entries/nosnap.md check3-no-located-quote-with-snapshot
entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=2
rc=1

### CASE entry:quoteabsent
FAIL entries/quoteabsent.md check4-quote-absent-from-snapshot-line-6
FAIL entries/quoteabsent.md check3-no-located-quote-with-snapshot
entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=2
rc=1

### CASE entry:perturb       (one character changed: "newpaths")
FAIL entries/perturb.md check4-quote-absent-from-snapshot-line-6
FAIL entries/perturb.md check3-no-located-quote-with-snapshot
entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=2
rc=1

### CASE entry:snapoutside   (snapshot: elsewhere/y.txt — file exists, outside --snapshot-dir)
FAIL entries/snapoutside.md check4-snapshot-outside-dir-line-6
FAIL entries/snapoutside.md check3-no-located-quote-with-snapshot
entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=2
rc=1

### CASE entry:snapmissing   (snapshot: census/sources/absent.txt)
FAIL entries/snapmissing.md check4-snapshot-missing-line-6
FAIL entries/snapmissing.md check3-no-located-quote-with-snapshot
entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=2
rc=1

### CASE entry:symlinkesc    (census/sources/link-out.txt -> ../elsewhere/y.txt, i.e. outside the dir)
$ ls -l census/sources/link-out.txt
lrwxrwxrwx 1 vgpnk vgpnk 109 … census/sources/link-out.txt -> …/gatefix/elsewhere/y.txt
entries=1 ok=1 slice_verdicts=2 slice_total=2 fail=0
rc=0
```

### C5 — check 5 (`source: S<digits>` resolves in `corpus/SOURCES.md`)

```
### CASE entry:dangling        (column-0 dangling id)
FAIL entries/dangling.md check5-dangling-source: S999
entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=1
rc=1

### CASE entry:nocite          (no source citation at all)
FAIL entries/nocite.md check5-no-source-citation
entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=1
rc=1

### CASE entry:citedlist       (one resolvable column-0 citation PLUS "- source: S999" as a bullet)
body tail: - source: S999 — dangling id written as a bullet, not at column 0
entries=1 ok=1 slice_verdicts=2 slice_total=2 fail=0
rc=0

### CASE entry:citedindent     (one resolvable column-0 citation PLUS "  source: S999" indented 2 spaces)
body tail:   source: S999 — nested dangling citation, indented two spaces
entries=1 ok=1 slice_verdicts=2 slice_total=2 fail=0
rc=0
```

### C6 — check 6 (>=1 ADMIT and >=1 REJECT, reason each)

```
### CASE entry:noadmit
FAIL entries/noadmit.md check3-no-located-quote-with-snapshot
FAIL entries/noadmit.md check6-no-admit
entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=2
rc=1

### CASE entry:noreject
FAIL entries/noreject.md check6-no-reject
entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=1
rc=1

### CASE entry:reject-noreason   ("- REJECT: staged row with no justification of any kind")
FAIL entries/reject-noreason.md check6-reject-without-reason
entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=1
rc=1

### CASE entry:reject-emdash     ("- REJECT: staged row — " — em dash, no reason text)
entries=1 ok=1 slice_verdicts=2 slice_total=2 fail=0
rc=0

### CASE entry:admit-noreason   (ADMIT carries locator+snapshot but NO reason; REJECT carries reason:)
ADMIT line: - ADMIT: "RENAME_NOREPLACE do not overwrite newpath" § DESCRIPTION snapshot: census/sources/x.txt
entries=1 ok=1 slice_verdicts=2 slice_total=2 fail=0
rc=0
```

## D. Slice transcripts

Slice fixture `census/slice` (2 ids, matching the frozen shape ` S<id>   \`payload-absent\` `):

```
$ cat -A census/slice
 S114   `payload-absent` $
 S123   `payload-absent` $
```

Entry held fixed at `entries/good.md`; only `--slice-verdicts` / `--slice` vary.

```
### S1 verdicts-good      (both rows, frozen classes, evidence present)
entries=1 ok=1 slice_verdicts=2 slice_total=2 fail=0
rc=0

### S2 verdicts-partial   (S123 row absent)  <-- a missing row must not become verified
FAIL slice verdict-missing:S123
entries=1 ok=1 slice_verdicts=1 slice_total=2 fail=1
rc=1

### S3 verdicts-extra     (S114 row + a well-formed row for S999, an id not in the slice)
FAIL slice verdict-missing:S123
entries=1 ok=1 slice_verdicts=1 slice_total=2 fail=1
rc=1

### S4 verdicts-badclass  (S123 class "verified", not one of the four frozen classes)
FAIL slice verdict-bad-class-line-2:verified
FAIL slice verdict-missing:S123
entries=1 ok=1 slice_verdicts=1 slice_total=2 fail=2
rc=1

### S5 verdicts-noev      (S114 row with an empty evidence field)
FAIL slice verdict-no-evidence-line-1
FAIL slice verdict-missing:S114
entries=1 ok=1 slice_verdicts=1 slice_total=2 fail=2
rc=1

### S6 verdicts-dupe      (two rows for S114, none for S123)
FAIL slice verdict-duplicate:S114
FAIL slice verdict-missing:S123
entries=1 ok=1 slice_verdicts=1 slice_total=2 fail=2
rc=1

### S7 verdicts-shortrow  (line "S123" with no tab fields)
FAIL slice verdict-short-row-line-2
FAIL slice verdict-missing:S123
entries=1 ok=1 slice_verdicts=1 slice_total=2 fail=2
rc=1

### S8 verdicts-idinside  (only "S114  accepted  see S123 for the other row")
FAIL slice verdict-missing:S123
entries=1 ok=1 slice_verdicts=1 slice_total=2 fail=1
rc=1

### S9 verdicts-comment   (a "# … S123 …" comment line above two real rows)
entries=1 ok=1 slice_verdicts=2 slice_total=2 fail=0
rc=0

### S10 empty slice file   (--slice census/slice-empty, 0 bytes)
entries=1 ok=1 slice_verdicts=0 slice_total=0 fail=0
rc=0

### S11 missing slice file (--slice census/nosuch-slice)
FAIL slice slice-missing
entries=1 ok=1 slice_verdicts=0 slice_total=0 fail=1
rc=1

### S12 missing verdicts file (--slice-verdicts census/nosuch.tsv)
FAIL slice verdict-missing:S114
FAIL slice verdict-missing:S123
entries=1 ok=1 slice_verdicts=0 slice_total=2 fail=2
rc=1

### S13 no --slice / --slice-verdicts flags at all (defaults point at the real lane's paths,
        which do not exist under this fixture root)
FAIL slice slice-missing
entries=1 ok=1 slice_verdicts=0 slice_total=0 fail=1
rc=1
```

## E. Real-lane slice bytes (input side, unmodified)

```
$ cat -A census/round-22/attempt2/quarantine-slice
 S114   `payload-absent` $
 S123   `payload-absent` $
 S124   `payload-absent` $
 S126   `payload-absent` $
 S131   `payload-absent` $
 S133   `payload-absent` $
 S138   `payload-absent` $
 S118`   the cited source could not be fetched, so no quote was checked $
$ wc -l census/round-22/attempt2/quarantine-slice
8 census/round-22/attempt2/quarantine-slice
```

The `S118` row is the register row at line 361 of `corpus/REGISTER`-side data, whose id cell is
`` S118` `` — the frozen extractor propagates that malformation into the derived slice (documented
independently in `.ufo/waves/round-22/attempt2/w1/Slice118.md`, finding H1). Counting it is
therefore faithful to the frozen producer, not a gate defect.

## F. Prior fixture bug in this review (kept for honesty)

The first `entries/good.md` written here omitted the inline `snapshot:` token on the ADMIT line and
correctly failed:

```
### CASE entry:good (first version, sha not retained)
FAIL entries/good.md check4-no-snapshot-named-line-6
FAIL entries/good.md check3-no-located-quote-with-snapshot
entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=2
rc=1
```

The fixture was corrected (final sha `ac8f127b…`) and passes. This confirms check 4 resolves the
snapshot per quote line rather than per Gate — required, because the two real entries name four
different snapshots across their ADMIT lines.

## G. Concurrent change to the real entries (observed mid-review)

Both entries were clean when §C0's real-lane measurement was taken; a sibling seat then edited them
in the working tree. Executed:

```
$ git --no-pager diff --stat -- corpus/knowledge/
 corpus/knowledge/quarantine-origin-record-fields-r24.md | 12 ++++++------
 corpus/knowledge/quarantine-staging-no-copy-r23.md      |  6 +++---
 2 files changed, 9 insertions(+), 9 deletions(-)

$ git --no-pager diff -- corpus/knowledge/quarantine-origin-record-fields-r24.md
-- ADMIT: "List files in the trash with their original locations." — § COMMANDS trash --list — snapshot: census/round-22/attempt2/sources/arch-gio.1.txt
++ ADMIT: "List files in the trash with their original locations." — § COMMANDS trash --list — reason: grounds this entry's claim directly at the quoted locator — snapshot: census/round-22/attempt2/sources/arch-gio.1.txt
   (the same clause is appended to all 6 ADMIT lines of r24 and all 3 of r23)

$ python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 \
    --entries corpus/knowledge/quarantine-staging-no-copy-r23.md \
              corpus/knowledge/quarantine-origin-record-fields-r24.md \
    --snapshot-dir census/round-22/attempt2/sources \
    --slice census/round-22/attempt2/quarantine-slice \
    --slice-verdicts census/round-22/attempt2/slice-verdicts.tsv
entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0
rc=0
```

Both measurements (pre-edit and post-edit) produce the identical counts line. The appended clause
is the same for all 9 ADMIT lines, so it satisfies a mechanical `reason:` test without
distinguishing any claim — recorded in the report as F2.

