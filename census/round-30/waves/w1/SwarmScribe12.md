# SwarmScribe12 — r30 w1, C3 keep-ref expiry entry (draft)

## Status

STATUS: PASS — `corpus/knowledge/jj-keep-ref-expiry.md` drafted at
`.ufo/waves/round-30/w1/deliver-entry-jj-keep-ref-expiry.md` (122 lines, sha256
`bc07f511f08b00794eb71b069c2dfe81b51b2f1316f53f1f03fceeeb58eee2ce`); four sources are tag-verified and the
mechanically checkable C3 legs (L3 gate, L4 snapshots, L5 quotes, L6 rows and URL binding, L7 hosts, L8 measured
record) were simulated green against a scratch tree. L1 (three F1 entries), L2 (coverage row) and L9 (sources
census) need the landing commit and are not mine.

## Evidence

Revision: lane HEAD `df6afe817d096e4ad71ba2b9cc21a83f126eb658` (`git -C
/home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD`; `git status --porcelain` shows only another seat's
`?? corpus/lessons/round-30.md`). Base `9420341d9a814cb6089c25fb03a4cc9b23dc0d1b`; preregistration commit
`d4928ec86b667e3d1ed0adb07fb088e500cf1631`; controls `bae103cba91884947a0557940e60c320f5512f75`. Contract read
first: `census/round-30/records/preregistration.txt:9` (C3 clause).

Source verification (four files fetched live this run, compared with the wave-1 capture, which another seat
placed):

```
$ cd /fast/scratch/hyaku/souji-r30/SwarmScribe12
$ curl -fsS -o 'cli-reference@.md.snap' https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/cli/tests/cli-reference@.md.snap
$ curl -fsS -o git_backend.rs    https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/lib/src/git_backend.rs
$ curl -fsS -o operation-log.md  https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/docs/operation-log.md
$ curl -fsS -o git-gc.adoc       https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-gc.adoc
$ sha256sum *
b330694348c2a6fb21b637425c711d48ac9fa41d0b3596b4ca2955f7a9333554  cli-reference@.md.snap
95147270e5bc2a689e1191256c0f214d8e52ac6d4523756eb6b8ec8113d86c69  git_backend.rs
2a48dab85483f8bed666ccc1aebd458d70f4ff57ece1a122aee8889b3209ce18  operation-log.md
e3dbc4081095faf8d2d760eb4a47a1350f89d0c772f55eaada9cfbcdbeafba8c  git-gc.adoc
$ cmp -s <each> /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-30/w1/sources/<same name>  # all identical
```

`jj --version` -> `jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5`; `git --version` -> `git version 2.56.0`.

Gate and counter-leg simulation (scratch tree with the draft at `corpus/knowledge/`, the four snapshots at
`census/round-30/sources/`, a scratch 4-row `corpus/SOURCES.md`, and scratch `SHA256SUMS`/`fetch-receipts.tsv`
derived from those four files — so L4/L6 were exercised, not the lane's real registry):

```
$ python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-26 \
    --entries corpus/knowledge/jj-keep-ref-expiry.md --snapshot-dir census/round-30/sources \
    --slice census/round-30/records/empty-slice --slice-verdicts census/round-30/records/empty-verdicts
entries=1 ok=1 slice_verdicts=0 slice_total=0 fail=0        rc=0
```

Replicated legs (same regexes as `census/round-30/c3-counter.py`): `L4 True snapshots=4 bad=[]`;
`L5 True quotes=14 bad=[]`; `L6 True cited=['S220','S221','S222','S223'] missing=[] url_unbound=[]`;
`L7 True bad=[]`; `L8 True results=8` (`jj-version: jj 0.45.1…` present, 8 `RESULT ` lines, entry contains
`refs/jj/keep`, `util gc` and `census/round-30/records/jj-keep-expiry-run.txt`).

Scratch ran only under `/fast/scratch/hyaku/souji-r30/SwarmScribe12/`; `rm -rf` done, path confirmed absent. No
tool installed or upgraded this item.

## Findings

1. **The wave-1 snapshots are the tag bytes.** All four `cmp` identical to the captures named above; the hashes in
   the entry's `verified-at:` are the fetched-and-compared ones (location: `.ufo/waves/round-30/w1/sources/`).
2. **The CLI reference path is `cli/tests/cli-reference@.md.snap`, with a literal `@`.** At v0.45.1
   `docs/cli-reference.md` is a 674-byte mkdocs include stub naming that file, and the w1 filename is correct rather
   than a missing tag; probes returned 200 for `docs/cli-reference.md` and `cli/tests/cli-reference@.md.snap`, 404
   for the guessed `cli/tests/snapshots/test_generate_md_cli_help__help_md.snap` (location: fetched stub bytes,
   this run).
3. **Keep-ref deletion has two gates, not one.** `recreate_no_gc_refs` deletes a keep ref only when the commit is
   absent from `index.all_heads_for_gc()` (`git_backend.rs:1558-1564`) and the loose-ref file is not newer than
   `keep_newer` (`git_backend.rs:917-961`). The source comment says the mtime test is racy on re-import and that a
   packed ref is not demoted to loose, so a packed keep ref bypasses the age test (entry carries this as
   `[INFERENCE]`).
4. **`jj op abandon` is not the remover.** The CLI doc says abandoned operations, commits and other unreachable
   objects are collected later by `jj util gc` (`cli-reference@.md.snap:2419`); the measured `abandon` step still
   reports `target_keep=yes` (`census/round-30/records/jj-keep-expiry-run.txt`).
5. **`git gc` alone is a no-op on a keep-held commit.** Measured `git-gc-prune-now` still reports
   `target_keep=yes`; the source states git gc removes unreachable objects and keeps everything reachable
   (`git-gc.adoc:18-20, 159-161`), and a keep ref is a ref.
6. **The record's steps 6-8 are a separate repository.** The fixture header says steps 6-8 run as controls on a
   second repo, which is why step 6's count exceeds step 5's; the entry states this so the sequence is not
   misread (`deliver-r30-jj-keep-expiry.sh:15-19`).
7. **The hidden-head arm is undecided by the delivered record.** The probe receipt shows a keep ref naming a
   commit that `jj log` reports `hidden=true` surviving two `jj util gc --expire=now` runs; the fixture target has
   a child, so it never tests that arm. The draft records the gap under "What this does NOT establish"
   (`receipt-SwarmExecutor06-keepref-mechanism.txt`).
8. **Landing traps for the L1, from the frozen counter.** `SHA256SUMS` is keyed by basename but
   `fetch-receipts.tsv` by full snapshot path (`c3-counter.py:100,106`), so both must name the four files exactly;
   `cited` takes only the first S-id on each `source:` line (`:112`), so one id per line; Gate URLs are matched
   against column 2 of each cited row (`:115`), so each of the four URLs must appear verbatim in its row's
   title/URL cell. The draft's snapshot paths are fixed at
   `census/round-30/sources/{cli-reference@.md.snap,git_backend.rs,operation-log.md,git-gc.adoc}`.
9. **L8 does not bind the prose.** L8 checks the record's shape and two literals in the entry, not the `<k>` counts
   in the observed paragraph (`c3-counter.py:123-125`); a wave-2 falsifier has to read
   `census/round-30/records/jj-keep-expiry-run.txt` against the entry's step claims. Reported for an attack seat;
   not filed as an ATTACK here because this item is not an attack seat.

## Deliveries

- `.ufo/waves/round-30/w1/deliver-entry-jj-keep-ref-expiry.md` — the C3 entry draft, land-ready at
  `corpus/knowledge/jj-keep-ref-expiry.md` after the L1 renumbers S220-S223, copies the four
  `census/round-30/sources/` snapshots, registers the four `corpus/SOURCES.md` rows (opened 2026-10-26, exact URLs
  from the `source:` lines) with matching `SHA256SUMS` + `fetch-receipts.tsv`, commits the run record at
  `census/round-30/records/jj-keep-expiry-run.txt` and the fixture at `tests/fixtures/r30-jj-keep-expiry.sh`, and
  updates the F1 coverage row. S-id order by document: S220 CLI reference, S221 `git_backend.rs`, S222
  `operation-log.md`, S223 `git-gc.adoc`.
- `.ufo/waves/round-30/w1/SwarmScribe12.md` — this report.

Untouched: lane product code, census counters, corpus, SOURCES.md, coverage map, jj state, git index; the fleet
root and every sibling lane; `census/round-30/sources/` does not exist yet and was not created by this seat.
