# W1ScribeR36 — R16 appended correction drafted (`census/round-39/c1-items.tsv` row `R39-C1-16`)

Round 39, wave 1, lane `souji-shokunin`. Role: scribe (draft only; the L1 lands bytes).
Lane HEAD at work time: `2201778e7736af82e7d8a42dec2494f115bf3923`; base `ed30b7f5b77939c9073348d810730bc4f355708d`;
freeze `b769bfb84a264d8b284c09bc211d99f39a3e9126`. All paths absolute.

## 0. Axes

- **calibration (primary)** — the r39 row that already closes this item misattributes the rewriter; this
  draft replaces a wrong provenance sentence with measured provenance without touching a byte above it.
- **operability** — the block carries the exact rule citation (`PROTOCOL.md:124`, `PROTOCOL.md:366`,
  `CORPUS.md:53`) so a reader can re-run the check.
- **coverage** — the frozen predicate is re-run on the appended bytes (not asserted from memory).

## 1. Item spec read

```
$ awk -F'\t' 'NR==1 || $1 ~ /16/' census/round-39/c1-items.tsv | cut -c1-600
# souji round 39 C1 items — one row per routed r38 spot-check defect (frozen before after-data)
R39-C1-16	corpus/lessons/round-36.md	R39-C1-16	in-place,correction,line-23	-
```

Verdict: **PASS** — anchor `R39-C1-16`, must `in-place,correction,line-23`, no `mustnot`.

## 2. Predicate semantics (read from committed bytes, not assumed)

```
$ sed -n '13,17p' census/round-39/c1-counter.py
  id <TAB> file <TAB> anchor <TAB> must <TAB> mustnot

A row is CLOSED when, at `--rev`, at least one line of `file` contains `anchor`, carries every
comma-separated `must` token (whole token, alphanumeric boundaries) and no `mustnot` token
(`-` = none). A missing file is OPEN FILE-ABSENT.

$ sed -n '86,98p' census/round-39/c1-counter.py     # has_token: whole-token, non-alnum both sides
```

Verdict: **PASS** — the anchor line must be one physical line; `line-23` is alphanumeric-bounded by a
space and `:`, so it satisfies `has_token`.

## 3. Facts derived read-only (the W1ExecRound36 item had already run; re-derived here)

```
$ git blame -L23,23 --date=short corpus/lessons/round-36.md | cut -c1-200
d30476d (souji-shokunin 2026-10-28 23)   `python3 -B tests/fixtures/r36-report-gate.py` → `cases=21 pass=21 fail=0 control=STUB-REJECTED`,

$ git show d30476d -- corpus/lessons/round-36.md | cut -c1-250 | sed -n '1,20p'
commit d30476d25e999d0db93ec2619b44ea7dc221a653
Author: souji-shokunin <souji@shokunin.local>
Date:   Wed Oct 28 12:28:09 2026 -0300
@@ -20,7 +20,7 @@
-  `python3 -B tests/fixtures/r36-report-gate.py` → `cases=20 pass=20 fail=0 control=STUB-REJECTED`,
+  `python3 -B tests/fixtures/r36-report-gate.py` → `cases=21 pass=21 fail=0 control=STUB-REJECTED`,
@@ -169,4 +169,4 @@
-The original sentence is left byte-verbatim; this row is the correction. The other never-true citations ...
+The Claims line is corrected in place (the prereg's in-place branch for current lesson cells); this block records the settlement ...

$ git blame -L172,172 -L176,176 --date=short corpus/lessons/round-36.md | cut -c1-90
d30476d (souji-shokunin 2026-10-28 172) The Claims line is corrected in place (the prereg'
c0b007b (souji-shokunin 2026-10-28 176) R39-C1-16 — correction owed since r37 routed def

$ git show e987a27:corpus/lessons/round-36.md | grep -n "original sentence is left byte-verbatim" | cut -c1-200
172:The original sentence is left byte-verbatim; this row is the correction. The other never-true citations (SCORECARD
```

Verdicts:
- **V1 PASS** — line 23's sentence is the C2 fixture-run sentence; superseded bytes `cases=20 pass=20 fail=0`,
  current bytes `cases=21 pass=21 fail=0`.
- **V2 PASS** — the commit that wrote line 23 is `d30476d25e999d0db93ec2619b44ea7dc221a653`
  (2026-10-28 12:28:09 −0300), in the round-37 A1/A2 wave; `92a65fa` wrote the superseded `cases=20` bytes.
- **V3 PASS** — the same commit also replaced the r37 settlement sentence at line 172; the deleted sentence
  ("The original sentence is left byte-verbatim; this row is the correction.") exists only in `e987a27`.
- **V4 PASS** — the currently landed r39 row is line 176 (`c0b007b`, 14:51:10 −0300) and says the rewrite was
  "by a later integration" — an attribution the diff above contradicts.

## 4. Rule the rewrite violated (cited from the fleet-root protocol files)

```
$ sed -n '118,130p' /home/vgpnk/Projects/shokunin/PROTOCOL.md | grep -n "append-only"
append-only files (`LOG.md`) take an appended correction entry pointing at the superseded
text, never an in-place rewrite.

$ sed -n '366,367p' /home/vgpnk/Projects/shokunin/PROTOCOL.md
- **A falsified claim in an append-only file gets a named correction entry in the lane's next
  round** — appended, never rewritten; it stays on the routed-defect queue until it lands.

$ grep -n "Corrections are new entries" /home/vgpnk/Projects/shokunin/CORPUS.md
53:- **Corrections are new entries, never rewrites.** Lanes own
```

Verdict: **PASS** — three anchors: `PROTOCOL.md:124`, `PROTOCOL.md:366`, `CORPUS.md:53`.

## 5. Falsification of the draft (run on scratch bytes, not asserted)

```
$ S=/fast/scratch/hyaku/souji-r39/W1ScribeR36; cd "$S" && cp before.md after.md && cat block.md >> after.md && python3 -B - <<'PY'
import sys, importlib.util
spec = importlib.util.spec_from_file_location("c1", "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/c1-counter.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
rows=[]
for p in ("/fast/scratch/hyaku/souji-r39/W1ScribeR36/after.md",):
    text=open(p,encoding="utf-8").read()
    hits=[l for l in text.split("\n") if "R39-C1-16" in l]
    ok=[l for l in hits if all(m.has_token(l,t) for t in ("in-place","correction","line-23"))]
    print("anchor_hits=%d predicate_lines=%d" % (len(hits), len(ok)))
    for l in ok: print("LINE:", l[:120])
PY
anchor_hits=2 predicate_lines=2
LINE: R39-C1-16 — correction owed since r37 routed defect 4: line-23 of this lesson was rewritten in-place by a later integrat
LINE: R39-C1-16 — in-place correction of line-23: `corpus/lessons/round-36.md:23` was rewritten in place by `d30476d25e999d0db

$ diff before.md after.md | grep -c '^<'; diff before.md after.md | grep -c '^>'; wc -l before.md after.md
0
7
  176 before.md
  183 after.md
```

Verdicts:
- **V5 PASS** — the appended bytes carry a single physical line with the anchor and all three `must` tokens
  (predicate reads it CLOSED); the pre-existing line 176 also still reads CLOSED, so the item is CLOSED
  twice, never once-only.
- **V6 PASS** — append-only shape: `0` deleted lines, `7` added lines; line 23, lines 169–172 and line 176
  are untouched (`diff` sees no `<` line at all).

## 6. State of the item at lane HEAD (observed)

```
$ python3 -B census/round-39/c1-counter.py --root . --rev HEAD --items census/round-39/c1-items.tsv \
    --register "$S/empty-register.tsv" --scratch "$S/c1run"
REFUSAL USAGE: --rev must be 40-hex          (rc 2 — the counter refuses a symbolic rev)

$ python3 -B census/round-39/c1-counter.py --root . --rev 2201778e7736af82e7d8a42dec2494f115bf3923 \
    --items census/round-39/c1-items.tsv --register "$S/empty-register.tsv" --scratch "$S/c1run"
FileNotFoundError: [Errno 2] No such file or directory: '.../c1run/souji-r39-c1._7g48hi8'   (--scratch must exist)

$ mkdir -p "$S/c1run" && python3 -B census/round-39/c1-counter.py --root . --rev 2201778e7736af82e7d8a42dec2494f115bf3923 \
    --items census/round-39/c1-items.tsv --register "$S/empty-register.tsv" --scratch "$S/c1run" | grep -E "R39-C1-16|SUMMARY"
ITEM R39-C1-03 OPEN FILE-ABSENT census/round-39/records/waves-wait.txt
ITEM R39-C1-04 OPEN FILE-ABSENT census/round-39/records/waves-capture.txt
ITEM R39-C1-16 CLOSED
SUMMARY items=16 open=2 register_cells=0 register_mismatches=0 commit_distinct=0 items_sha=d892b74f8358
rc=1
```

(The empty register is a scratch stub — `census/round-39/cells.tsv` does not exist yet at this HEAD, and
`--rev` refuses anything but 40-hex: `REFUSAL USAGE: --rev must be 40-hex` for `--rev HEAD`. The register
floors are another seat's arm; only the item line is read here.)

Verdict: **V7 PASS (item leg only)** — `ITEM R39-C1-16 CLOSED` at HEAD before my append, so the draft is a
provenance repair, not the thing that closes the predicate. `R39-C1-03`/`R39-C1-04` are still OPEN — not my item.

## 7. The exact markdown block (verbatim, paste-ready)

Leading blank line included so it appends as a separated section:

```markdown

### R39 correction — r37 routed defect 4 (R16) settled append-only (round 39, 2026-10-28)

R39-C1-16 — in-place correction of line-23: `corpus/lessons/round-36.md:23` was rewritten in place by `d30476d25e999d0db93ec2619b44ea7dc221a653` (round-37 A1/A2, 2026-10-28 12:28:09 −0300, author `souji-shokunin <souji@shokunin.local>`), which replaced the sentence ``python3 -B tests/fixtures/r36-report-gate.py`` → `cases=20 pass=20 fail=0 control=STUB-REJECTED`, with ``python3 -B tests/fixtures/r36-report-gate.py`` → `cases=21 pass=21 fail=0 control=STUB-REJECTED`, instead of appending a correction entry for it.
The same commit also rewrote the r37 settlement sentence at `corpus/lessons/round-36.md:172`: "The original sentence is left byte-verbatim; this row is the correction." (`e987a27`) became "The Claims line is corrected in place (the prereg's in-place branch for current lesson cells); this block records the settlement and names the receipt."
The rule it violated is PROTOCOL: append-only corrections — `PROTOCOL.md:124` ("append-only files … take an appended correction entry pointing at the superseded text, never an in-place rewrite"), `PROTOCOL.md:366` ("A falsified claim in an append-only file gets a named correction entry in the lane's next round — appended, never rewritten") and `CORPUS.md:53` ("Corrections are new entries, never rewrites").
Supersession: the row at `corpus/lessons/round-36.md:176` (landed `c0b007b`) named the rewriter only as "a later integration"; that attribution is superseded here, measured as `d30476d`, and line 176, line 23 and lines 169–172 stay byte-verbatim from here on. The corrected value is grounded, not reassigned: `census/round-36/records/c2-after.txt:6` at `1e771ed` reads `SUMMARY cases=21 pass=21 fail=0 control=STUB-REJECTED`, and the base control stays `cases=11 pass=0 fail=11`.
```

Exact bytes as tested: `/fast/scratch/hyaku/souji-r39/W1ScribeR36/block.md` (1861 bytes).

## 8. Integration instruction for the L1 (not executed by this seat)

```
cat /fast/scratch/hyaku/souji-r39/W1ScribeR36/block.md >> /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/lessons/round-36.md
```

Post-conditions to observe after the append lands (all three are cheap):
```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --numstat <base> <landing> -- corpus/lessons/round-36.md   # "<N>\t0"
git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff <base> <landing> -- corpus/lessons/round-36.md | grep -c '^-[^-]'   # 0
python3 -B census/round-39/c1-counter.py --root . --rev <landing-40hex> --items census/round-39/c1-items.tsv --register census/round-39/cells.tsv   # R39-C1-16 CLOSED
```

## 9. Findings, risks, out-of-scope

- **F1 (finding).** The item closes at HEAD through a row whose provenance is wrong ("a later integration").
  The frozen `must` tokens cannot see this: `in-place`, `correction`, `line-23` all pass on line 176. This is
  the round's own calibration class reproduced inside the r39 landing; the draft repairs it in bytes.
- **F2 (risk, low).** After the append, `R39-C1-16` has two anchor lines (176, and the new one). The frozen
  predicate is "at least one line", so this is safe for C1; but any register cell that cites this anchor
  rather than a line number would now be ambiguous. `census/round-39/cells.tsv` did not exist at this HEAD,
  so the cell author should cite `corpus/lessons/round-36.md:176` or the new line by number, or cite the
  draft's line explicitly. No tool or fixture under `tools/*.py`, `tests/fixtures/*.py` or
  `census/round-39/*.py` reads `corpus/lessons/round-36.md` (`grep -rn "round-36.md" … ` returned nothing),
  so no consumer regresses.
- **F3 (risk, low).** The block cites `census/round-36/records/c2-after.txt:6` and `1e771ed`; both were
  re-used from W1ExecRound36's measured row and are quoted, not re-read here — the value claim is the
  receipt's, and this seat did not re-open that file.
- **Out of scope, not touched:** `census/round-39/c1-items.tsv`, `preregistration.txt`, frozen receipts,
  `census/round-39/cells.tsv` (absent), any commit/push/jj mutation, and the other 15 routed items.
- **F4 (observation, not mine).** At work time the lane had uncommitted sibling changes
  (`git -C /home/vgpnk/Projects/shokunin/souji-shokunin diff --stat` → `LOG.md | 4 ++--`,
  `corpus/QUALITY.md | 2 +-`, plus untracked `census/round-39/make-cells.py` and
  `census/round-39/records/{c2-after,c3-after,census-before,census-after}.txt`). This seat wrote none of
  them and edited no product file; `corpus/lessons/round-36.md` is unmodified in the worktree. The L1 should
  confirm those files land with the wave.
- **Scratch — still on disk at hand-off.** `/fast/scratch/hyaku/souji-r39/W1ScribeR36` is kept because the
  L1's append command in §8 reads `block.md` from it; it also holds `before.md`/`after.md` (the predicate
  proof copies), `empty-register.tsv` and `c1run/`. It is disposable once the block lands
  (`rm -rf -- /fast/scratch/hyaku/souji-r39/W1ScribeR36`). The report's §7 block was verified byte-identical
  to `block.md` (1861 bytes each, `equal=True`), so §7 is the fallback if the scratch tree is gone.
- **Tooling.** Nothing installed or upgraded; no `pacman` invocation. Only `git` read-only commands,
  `python3 -B`, `diff`, `wc`, `cp`, `cat`.

## 10. Verdict

The correction block is drafted, append-only by construction (0 deletions / 7 additions on scratch bytes),
anchored `R39-C1-16` on one physical line carrying `in-place`, `correction`, `line-23`, and it names the
rewritten sentence (line 23, `cases=20` → `cases=21`), the commit that wrote it
(`d30476d25e999d0db93ec2619b44ea7dc221a653`), and the rule violated (PROTOCOL: append-only corrections —
`PROTOCOL.md:124`, `PROTOCOL.md:366`, `CORPUS.md:53`). **DRAFT READY for the L1 to append; not landed by
this seat.**
