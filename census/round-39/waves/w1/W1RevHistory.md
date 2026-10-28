# W1RevHistory — why the r38 defect classes recur (round 39, wave 1)

Seat: `W1RevHistory`, role revenger. Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Assignment: from committed history, find the **earlier** routing of the three r38 classes —
(a) a stated completion with an unevidenced count (R2/R15), (b) a prereg file edited in place (R9),
(c) a receipt naming a non-durable path (R7) — and state, per class, when it was first routed, what
fix was attempted, and why the fix did not generalise. Deliver the intent statement the r39 lesson
can cite.

Read-only throughout: no commit, no push, no mutating git/jj. No tool installed. Scratch
`/fast/scratch/hyaku/souji-r39/W1RevHistory` was created and is removed at the end (see §Scratch).

## Revision disclosure — the lane tip moved under this seat

Every command below names its revision. The tip advanced three times while I read:

```
$ git -C …/souji-shokunin rev-parse HEAD        # at seat start
2201778e7736af82e7d8a42dec2494f115bf3923
$ … rev-parse HEAD                              # after the gate run
f8ba3f3b4fdac9669182af1c2829d79c1658f314
$ … rev-parse HEAD                              # at write time
2605bf20b90940f95282cbd6c65e80154ac6b2f2
```

All HEAD-state claims in this file were re-read at **2605bf2** after the last move
(`§Class A`/`§Class C` re-verification block). Base for the round is `ed30b7f5`.

---

## Class A — a stated completion with an unevidenced count (R2 / R15)

### A.1 First routing, with the committed capture that falsified it

```
$ git log --oneline --diff-filter=A -- corpus/lessons/round-33-verifier-spotcheck.md
9c76c72 round-33 verifier spot-check (integrator, hyaku): non-author admit/reject
$ git log -1 --format='%ci %s' 9c76c72
2026-10-26 16:34:24 -0300 round-33 verifier spot-check (integrator, hyaku): non-author admit/reject
```

`9c76c72:corpus/lessons/round-33-verifier-spotcheck.md` — Routed defects, item 1 (verbatim):

> **D1, seat count:** the report and lesson say "All 48 reports landed, with 0 dead seats" and
> "executor 11". The committed capture `census/round-33/waves/w1/` holds **47** seat reports
> (`SwarmExecutor` × 10), and `.ufo/waves/round-33/w1/` also holds 47. `SwarmExecutor31` has no
> report: per `c442b97`, it was a straggler the orchestrator stopped, and its output was unused.
> **Append a correction to LOG and the lesson.**

This is the archetype of R2: a completion count asserted in prose, contradicted by a committed
artifact, and — critically — *falsifiable only because a committed capture existed*.

Earlier, weaker ancestors in the same history (recorded, not routed by a non-author):
`corpus/lessons/round-16-verifier-spotcheck.md` item D3 (a LOG count "28" re-derived as 29) and
`round-19-verifier-spotcheck.md` routed defect 6 ("wave record accuracy … Preserve
first-refusal/start/dead/unexecuted distinctions … No report or transcript completeness is
fabricated."). Both are count-accuracy routes; neither had a committed capture to read.

### A.2 The in-range chain (the window this seat was given)

```
$ git log --oneline 'ca4369a~40..HEAD' -- SCORECARD.md LOG.md corpus/lessons/
… (67 commits; ca4369a~40 = cb76cb5 "round-35: preserve W2 feasibility timeout residual")
```

| round | commit | routed line (quoted) |
|---|---|---|
| 35 | `0ab5231` | d4: "never report a 40-seat partial W1 as satisfying the run-10 64-seat floor or **imply an unreceived wave result**" |
| 36 | `0d974ff` | d6: "report wave section says the launcher had not taken `w2.ready` at filing — the marker is 11:37:46 -03, before the 11:42:24 authoring" |
| 37 | `ca4369a` | d1: "Line 76 says `git ls-remote … prints 131ea876… (the lane tip)` … At closure the lane HEAD and `origin/master` are `cb443f5` … named in neither the report nor `LOG.md`" |
| 38 | `ed30b7f` | **R2**: "The report's opening line says "4 + 0 dead"; its own waves table says w1 dead 0 / w2 dead 0 … Nothing supports 4" · **R15**: "the last row's commit cell is the placeholder `<integration>`" |

The r38 report bytes (`6afdd3c6` in the fleet repo) carry the claim:

```
$ git -C /home/vgpnk/Projects/shokunin show 6afdd3c6:.ufo/reports/round-38/souji.md | sed -n '1,20p'
… Round shape: two v1 waves, 42 +
32 = 74 seats, 4 + 0 dead, inside the 64–128 band.
$ … | grep -n -B2 -A4 "integration"
92:| wave-2 findings integrated (this report's integration commit) | § Round 38 | `<integration>` |
```

### A.3 The fix attempted

Two attempts, both real, both narrow:

1. **An instrument** — `tools/souji-wave-evidence-capture.sh` exists to copy `.ufo/waves/round-N/`
   into a committable `census/round-N/waves/`:

   ```
   $ git log --oneline --diff-filter=A -- tools/souji-wave-evidence-capture.sh
   765fe8b round-28: repair pointers, curate F4 primitives, capture wave evidence
   $ sed -n '1,10p' tools/souji-wave-evidence-capture.sh
   # Capture a round's .ufo/waves evidence into a committable census receipt, so
   # that the receipt verifies over COMMITTED bytes rather than over the lane disk
   # (r28 closure routed defect 1).
   ```

2. **A prose correction** — r34 committed the capture it needed:

   ```
   $ git log --oneline --diff-filter=A -- census/round-34/waves/summary.tsv
   cdbae3b round-34: integrate partial calibration and honest C2 miss
   $ git show HEAD:census/round-34/waves/summary.tsv | wc -l
   73            # 72 seat rows + header
   ```

### A.4 Why the fix did not generalise — three measured mechanisms

**(i) The r33 correction itself never landed.** At tip `2605bf2` the falsified sentence is still
live, and no correction exists anywhere in the lane:

```
$ git show 2605bf2:corpus/lessons/round-33.md | sed -n '76p' | grep -o "48 reports, 0 dead"
48 reports, 0 dead
$ git show 2605bf2:LOG.md | sed -n '1827p' | cut -c1-60
- Wave w1 48 seats, 48 reports; wave 2 built, not dispatched
$ git ls-tree -r --name-only 2605bf2 census/round-33/waves/w1/ | grep -c "Swarm.*\.md"
47
$ git grep -n -E "SwarmExecutor31|47 reports|47 seat" 2605bf2 -- LOG.md SCORECARD.md corpus/
corpus/lessons/round-33-verifier-spotcheck.md:144:1. D1, seat count: …      # the route only
```

Two rounds elapsed between the route and r38, and the routed line was still false.

**(ii) The capture instrument is optional and decayed to zero.** Committed `census/round-N/waves/`
file counts:

```
$ for r in 33 34 35 36 37 38 39; do echo -n "r$r: "; git ls-tree -r --name-only HEAD census/round-$r/ | grep -c "waves/"; done
r33: 91   r34: 171   r35: 0   r36: 0   r37: 0   r38: 0   r39: 0
```

The rounds that were falsifiable on this class (33, 34) are exactly the rounds that captured. From
r35 on, the capture is absent, so a stated seat/dead count has no committed artifact to contradict
it — which is precisely the state R2 describes ("Nothing supports 4"). No gate requires the capture
to exist; the instrument is only run when a seat remembers to run it.

**(iii) The r38 closure is prose again.** `corpus/lessons/round-39.md` §Routed-defect closures:

> | R2 dead-seat count | r38 lesson gets the on-disk numbers; `W2MutBattery` settled after closure | R39-C1-02 |

The frozen C1 item `R39-C1-02` binds one lesson line carrying
`w1-reports=42/42,w2-reports=32/32,W2MutBattery,dead=0,settled-after-closure`. That is a true
sentence about r38, but it re-introduces no capture and adds no check — the class's carrier (a count
with no committed artifact) is untouched for r39's own waves, whose capture is still absent at the
revision I measured (`census/round-39/waves/` = 0 files, and the landing gate reports it dangling).

**Verdict A — PASS (the recurrence is explained, and the r33 instance is shown still open).**
The first routing is `9c76c72` (r33 D1, 2026-10-26); the fix attempted was a committed wave capture
(`765fe8b` instrument, `cdbae3b` first use); it did not generalise because the capture is not on a
gate path (0 files in r35–r39), the r33 correction never landed, and the r38 closure repeats the
prose-only shape.

---

## Class B — a prereg file edited in place (R9)

### B.1 First recorded instance, and first non-author routing

Earliest recorded instance in committed history (lane's own deviation list, `corpus/lessons/round-24.md`
lines 96-101, item 1):

> The frozen remedy says "before any after-data", and the amendment rewrote it as "before any
> after-receipt", which is weaker (`W2C1Amend` F1).

First **non-author routed** instance inside the given window:

```
$ git log -1 --format='%ci %s' 0d974ff
2026-10-28 12:10:26 -0300 round-36 verifier spot-check (integrator, hyaku): non-author admit/reject
```

`0d974ff:corpus/lessons/round-36-verifier-spotcheck.md` — Routed defects, item 2 (verbatim):

> **Prereg discipline.** A7 rewrote the C2 target after after-data existed (letter of prereg
> "not rewritten after any after-data"); **mitigate by amending the rule text to allow disclosed
> tighter-only retargeting with an atomic receipt refresh, and correct the frozen sentence.**

The recurrence chain:

| round | commit | quoted |
|---|---|---|
| 37 | `ca4369a` | d4: "**In-place corpus rewrite.** `corpus/lessons/round-36.md:23` was rewritten in place … under an "in-place branch" the r37 prereg asserts (prereg:25). CORPUS.md requires corrections as new entries, never rewrites." |
| 38 | `ed30b7f` | **R9**: "`git diff 4090ee5 fcdecaa -- census/round-38/preregistration.txt` replaces the frozen sentence "…must be tighter-only." with "…is tighter-only unless stated otherwise." — a relaxation of the amendment rule inside the file that claims append-only treatment" |

The r38 diff itself:

```
$ git diff 4090ee5 fcdecaa -- census/round-38/preregistration.txt | head -12
-None. Any later amendment is appended below with the seat that produced it and must be
-tighter-only.
+Any amendment below was appended after the wave seat that produced it and is tighter-only unless
+stated otherwise. The frozen predicate sentences, counters and targets are unchanged by A0-A2.
```

### B.2 The fix attempted (r37) — and the sentence it wrote

`census/round-37/preregistration.txt` (r37's own contract) states the rule:

```
$ grep -n -B2 -A6 -iE "amend|tighter-only|in-place" census/round-37/preregistration.txt
24:           corrections are append-only lines anchored R37-C1-<n> (SCORECARD,
25:           prereg) or in-place current-registry cells (SKILL, lesson Claims).
83:AMENDMENT RULE: an amendment may only tighten a predicate or add a disclosed
84:limit; predicate, counter and target are not rewritten after any after-data.
```

And r37 did the right thing for the *previous* round's file — it appended, it did not rewrite:

```
$ git diff 1e771ed cb443f5 --stat -- census/round-36/preregistration.txt
 census/round-36/preregistration.txt | 3 +++
$ … | grep "^+R37-C1-"
+R37-C1-8 … The frozen sentence is left byte-verbatim; this row is the correction.
+R37-C1-9 … The frozen sentence is left byte-verbatim; this row is the correction.
```

### B.3 Why the fix did not generalise — three measured mechanisms

**(i) The rule lives inside the round's own prereg, which is re-authored each round.** r37's
`AMENDMENT RULE` did not survive as a standing rule: r38's freeze bytes (`4090ee5`) open the
amendments section with a fresh sentence, `"None. Any later amendment is appended below with the
seat that produced it and must be tighter-only."` — a new sentence with no memory of r37's wording,
which its own A0 then relaxed in place.

**(ii) The r36 remedy licensed editing the rule text.** Item 2's remedy is literally "amend the
rule text … and correct the frozen sentence"; the next round wrote that licence into the contract as
an *in-place branch* (r37 prereg line 24-25, quoted above), and r37 d4 then found an in-place
rewrite performed under it. The correction generalised as a **permission**, not as a **check**.

**(iii) No instrument reads a prereg's append-only discipline.**

```
$ grep -rln "preregistration" tools/ census/*/*.py | head
tools/souji-declared-evidence.py
tools/souji-gate-check.py
tools/souji-record-agreement.py
tools/souji-receipt-run.py
tools/souji-axis-check.py
…
$ grep -n "preregistration" tools/souji-axis-check.py
2:"""souji-axis-check.py — preregistration axis-of-surface checker (round 26 C3).
7:Reads the preregistration's `## MACHINE BLOCK` section only …
```

Every reader of a prereg reads a machine block, a list revision or a declared-evidence pointer. None
compares `census/round-N/preregistration.txt` at its freeze blob with its blob at the landing to ask
whether any line was *deleted or replaced*. The r38 rewrite was found by a human `git diff`, which is
why it took two rounds (`r36 d2` → `r37 d4` → `r38 R9`) to route the same shape.

**r39 disposition (first append-only closure of the three).** `c0b007b` appended A11 to the r38
prereg, which now reads:

```
$ grep -n -A6 "^### A11" census/round-38/preregistration.txt
231:R39-C1-09 — A11 (appended 2026-10-28 by round 39): A0's clarification replaced the frozen rule
sentence "must be tighter-only." with "is tighter-only unless stated otherwise." in place; that edit
is superseded by this appended amendment, and the rule reads: a frozen sentence is amended only by an
appended block that names the superseded sentence, never by rewriting it in place.
```

The relaxed sentence is still in the file at `2605bf2` (line 120), superseded append-only — the first
of the three classes whose r39 fix uses the correct shape.

**Verdict B — PASS.** First recorded instance: `corpus/lessons/round-24.md:96-101`; first non-author
routing in the window: `0d974ff` (r36 d2); fix attempted: r37's `AMENDMENT RULE` plus append-only
`R37-C1-8/9`; it did not generalise because the rule is per-round text, the r36 remedy licensed
editing the rule sentence, and no instrument diffs a prereg against its freeze blob.

---

## Class C — a receipt naming a non-durable path (R7)

### C.1 First routing, and the instrument it produced

```
$ git show HEAD:corpus/lessons/round-18.md | sed -n '7p'
- C2: … 10 findings — 7 citations of two never-committed records under `census/round-17/`
  (`gate-replays-ddb7347.json` at SKILL.md:163,165; `jj-receipts-ddb7347.txt` at corpus/README.md:216
  and the knowledge entry jj-colocation-receipts lines 2, 44, 126, 148) …
$ … | sed -n '95p'
- **R2 (closure).** `SKILL.md` rows … re-pointed from never-committed `ddb7347` record names to the
  committed `census/round-17/gate-replays-4f48343.json`, `jj-receipts-4f48343.txt` and
  `seat-audit-r16-replay-4f48343.json` …
```

r18 closed it the right way: it re-pointed the citations **and** put a check behind them —
`LG-DANGLING-PTR` in `tools/souji-landing-gate.py` (confirmed live: it fired 10 findings in my own
read-only run, §C.4).

In-range routing:

```
$ git log -1 --format='%ci %s' ca4369a
2026-10-28 13:23:09 -0300 round-37 verifier spot-check (integrator, hyaku): non-author admit/reject
```

`ca4369a:corpus/lessons/round-37-verifier-spotcheck.md` — Routed defects, item 5 (verbatim):

> **Unreachable pointer in a corpus row.** SOURCES S238 `teaches` cites
> `.ufo/waves/round-37/w1/W1ScribeGate.md` (gitignored, unreachable at closure) and a byte count
> (9812 B) that disagrees with the lesson's `## Gate` (11365 B) for the same control. **Point at the
> committed counter arm (`c2-after.txt`, `case-env-witness=PASS`) and drop or commit the control; a
> numeric claim needs its command.**

Then r38's R7 (`ed30b7f`), same class, new shape:

> `consumers-after*.txt` run `r37-drift-escapes.py --base-tool /fast/scratch/hyaku/souji-r38/final/drift-r36.py`;
> `$HYAKU_SCRATCH` is reaper-deleted and `final/` is already gone, so the command is not re-runnable
> from committed bytes … Cite the revision, not the scratch file.

The bytes, at `fcdecaa`:

```
$ git grep -n "drift-r36" fcdecaa
census/round-38/records/consumers-after2.txt:14:## python3 -B tests/fixtures/r37-drift-escapes.py --base-tool /fast/scratch/hyaku/souji-r38/after2/drift-r36.py
census/round-38/records/consumers-after3.txt:14:… /fast/scratch/hyaku/souji-r38/after5/drift-r36.py
census/round-38/records/consumers-after4.txt:14:… /fast/scratch/hyaku/souji-r38/after6/drift-r36.py
census/round-38/records/consumers-after5.txt:14:… /fast/scratch/hyaku/souji-r38/final/drift-r36.py
```

### C.2 The fix attempted

r18: re-point + instrument (above). r37 d5: "Point at the committed counter arm … and drop or commit
the control."

### C.3 Why the fix did not generalise — three measured mechanisms

**(i) The r37 d5 fix never landed, and its target has no durable replacement.** At tip `2605bf2`
the S238 row still cites the gitignored path, and the capture that would resolve it does not exist:

```
$ git show 2605bf2:corpus/SOURCES.md | grep -c "W1ScribeGate"
1
$ git ls-tree -r --name-only 2605bf2 census/round-37/ | grep -c "waves/"
0
$ cat .gitignore
.ufo/waves/
census/operator-sweep-*/
__pycache__/
$ ls -l .ufo/waves/round-37/w1/W1ScribeGate.md
-rw-r--r-- 1 vgpnk vgpnk 9865 Oct 28 12:32 .ufo/waves/round-37/w1/W1ScribeGate.md
```

The file exists only on this host, inside a gitignored tree, and is now 9865 bytes against the row's
9812 — the numeric claim is not re-derivable from committed bytes at all.

**(ii) The instrument does not scan the registry.** `check_pointers` builds its source set from a
fixed list:

```
$ sed -n '1068,1090p' tools/souji-landing-gate.py
    sources = {
        path for path in (
            "SKILL.md", "SHONEN.md", "SCORECARD.md", "PROVINCE.md",
            "corpus/QUALITY.md", "corpus/README.md",
            "corpus/lessons/round-%d.md" % round_no,
            "corpus/lessons/round-%d-verifier-spotcheck.md" % round_no,
        ) if path in tree
    }
    sources.update(path for path in tree if path.startswith("corpus/knowledge/") …)
$ grep -n "SOURCES.md" tools/souji-landing-gate.py
                                      # no output: corpus/SOURCES.md is never a pointer source
```

`corpus/SOURCES.md` — where r37 d5's defect lives — is outside the scan set, so the row cannot be
flagged by the instrument that r18 created.

**(iii) The instrument cannot see the R7 shape at all.** The token regex only matches in-repo roots:

```
$ sed -n '140,152p' tools/souji-landing-gate.py
POINTER_ROOTS = ("census/", "tests/", "tools/", "corpus/", ".ufo/waves/", ".ufo/quarantine/")
POINTER_PATH_RE = re.compile(r"(?<![A-Za-z0-9_./<>*])(?:(?:\.\./)+|\./)?"
                             r"(?:census|tests|tools|corpus|\.ufo/waves|\.ufo/quarantine)/[^\s`\"()\[\]]+")
$ python3 -B -c "…POINTER_PATH_RE.findall(tok)…"
'/fast/scratch/hyaku/souji-r38/final/drift-r36.py' -> []
'/var/tmp/souji-r18-x/base-tools'                  -> []
'census/round-37/records/c2-after.txt'             -> ['census/round-37/records/c2-after.txt']
'.ufo/waves/round-37/w1/W1ScribeGate.md'           -> ['.ufo/waves/round-37/w1/W1ScribeGate.md']
```

An absolute scratch path matches nothing, and `census/round-38/records/*.txt` is not a scanned source
either, so R7's exact bytes were invisible to the gate **by construction**, while r37 d5's
`.ufo/waves/...` token was at least matchable (it was not scanned only because the row lives in
`SOURCES.md`).

### C.4 Control: the gate is live, and it is live only inside its surface

Read-only run at the then-HEAD (`f8ba3f3`), no `--json`, nothing written:

```
$ python3 -B tools/souji-landing-gate.py --root . --rev HEAD --round 39 | tail -12
LG-DANGLING-PTR	census/round-39/cells.tsv	SKILL.md:273 cites path absent at f8ba3f3b4fda
LG-DANGLING-PTR	census/round-39/records/c2-after.txt	SKILL.md:276 cites path absent at f8ba3f3b4fda
LG-DANGLING-PTR	census/round-39/waves/	corpus/lessons/round-39.md:60 cites path absent at f8ba3f3b4fda
SUMMARY	findings=10	checked_reg=99	checked_changed=0	checked_pins=13	checked_measured=3 …
COULD-NOT-EVALUATE	no .md reports under .ufo/waves/round-39/ or census/round-39/waves/ at f8ba3f3b4fda…
```

Zero findings for `/fast/scratch` or `/var/tmp` anywhere in the committed tree — consistent with the
regex measurement above.

**r39 disposition.** `corpus/lessons/round-39.md` §R39-C1-07 closes R7 in prose only:

> … every r39 receipt cites-a-revision (`--rev`/`--base-rev`) instead of a scratch path.

No instrument was added, and the C1 item that carries this line (`R39-C1-07`, `mustnot=/fast/scratch`)
constrains one lesson line, not the receipts.

**Verdict C — PASS.** First routing: r18 (`round-18.md:7`, `:95` — never-committed `ddb7347`
records), closed with re-pointing **plus** `LG-DANGLING-PTR`; in-window routing: `ca4369a` (r37 d5,
`SOURCES.md` row → gitignored `.ufo/waves/` path) and `ed30b7f` (r38 R7, receipt command → scratch
path). It did not generalise because the registry is not a pointer source, the regex cannot match an
absolute scratch path, and the r37 d5 fix never landed (S238 still cites the gitignored path at
`2605bf2`).

---

## Cross-class mechanism

The three classes share one structure, and it is why they recur across rounds rather than within one:

- each was **routed by a human/agent reading bytes** (`git diff`, `ls-tree`, a spot-check table),
  not by an instrument on the gate path;
- each fix was **a correction to the round that found it** — a lesson line, a re-pointed cell, an
  amendment block — so the next round starts with the class intact and no memory of the route;
- where an instrument *was* built (wave capture r28, `LG-DANGLING-PTR` r18, prereg counters), its
  **scan surface was narrower than the class**: the capture is optional (0/5 rounds used it), the
  pointer arm reads a fixed prose set without `SOURCES.md` or `census/`, and no reader diffs a
  prereg against its freeze blob.

The single strongest datum is the r33 count: routed 2026-10-26, still false at `2605bf2`
(`48 reports, 0 dead` vs 47 committed reports), two rounds before the identical shape was routed
again as r38 R2.

## Intent statement (for the r39 lesson to cite)

> Three r38 defect classes had already been routed before r38: a stated completion count with no
> committed artifact behind it (r33 D1, `9c76c72`), a frozen contract sentence relaxed by an in-place
> amendment (r24 item 1; r36 d2, `0d974ff`), and a citation to a path that committed bytes cannot
> resolve (r18 R2; r37 d5, `ca4369a`). Each was closed by correcting the round that found it, and each
> therefore re-armed: the r33 count still reads 48 against 47 committed reports, `SOURCES.md` S238
> still cites a gitignored `.ufo/waves/` path, and the r38 prereg still carries the relaxed rule
> sentence (superseded append-only only in r39). The standing intent is that **a defect class closes
> only when an instrument over the class's own shape is on a gate path** — every stated completion
> count read against a committed capture, every prereg diffed against its freeze blob, every
> citation token resolved against the committed tree at the cited revision — and that a prose
> correction which names a round is recorded as a routed defect, not as a closure. An instrument
> whose scan surface is narrower than the class (a pointer arm that skips `SOURCES.md` and cannot
> match an absolute path; a capture tool no gate requires) does not close the class either.

## Verdicts

| check | command | observed | verdict |
|---|---|---|---|
| H1a first routing, class A | `git log --diff-filter=A -- corpus/lessons/round-33-verifier-spotcheck.md`; `git show 9c76c72:…` | `9c76c72`, 2026-10-26 16:34:24 -0300; D1 quotes "All 48 reports landed, with 0 dead seats" against 47 committed reports | **pass** |
| H1b first routing, class B | `git show HEAD:corpus/lessons/round-24.md` (96-101); `git show 0d974ff:…round-36-verifier-spotcheck.md` | r24: "the amendment rewrote it as "before any after-receipt", which is weaker"; r36 d2: "A7 rewrote the C2 target after after-data existed … correct the frozen sentence" | **pass** |
| H1c first routing, class C | `git show HEAD:corpus/lessons/round-18.md` (7, 95); `git show ca4369a:…round-37-verifier-spotcheck.md` | r18: "7 citations of two never-committed records"; r37 d5: "SOURCES S238 `teaches` cites `.ufo/waves/round-37/w1/W1ScribeGate.md` (gitignored, unreachable at closure)" | **pass** |
| H2 fix attempted, class A | `git log --diff-filter=A -- tools/souji-wave-evidence-capture.sh`; `… -- census/round-34/waves/summary.tsv` | instrument landed `765fe8b` ("r28 closure routed defect 1"); first use `cdbae3b`, `summary.tsv` 73 lines | **pass** |
| H2 fix attempted, class B | `grep -n -A6 -iE "amend\|tighter-only\|in-place" census/round-37/preregistration.txt`; `git diff 1e771ed cb443f5 -- census/round-36/preregistration.txt` | r37 `AMENDMENT RULE` at :83-84; +3 lines, both "The frozen sentence is left byte-verbatim; this row is the correction." | **pass** |
| H2 fix attempted, class C | `git show ca4369a:…` item 5; `git grep -n "drift-r36" fcdecaa` | instruction "Point at the committed counter arm … and drop or commit the control"; four receipts name `/fast/scratch/…` | **pass** |
| H3a non-generalisation, class A | `git ls-tree … census/round-$r/waves/` for r33-r39; `git show 2605bf2:corpus/lessons/round-33.md` | captures 91/171/0/0/0/0/0; r33 line still "48 reports, 0 dead" vs 47 files | **pass** |
| H3b non-generalisation, class B | `git diff 4090ee5 fcdecaa -- census/round-38/preregistration.txt`; `grep -rln preregistration tools/` | frozen "must be tighter-only." replaced in place; no tool diffs a prereg against its freeze blob | **pass** |
| H3c non-generalisation, class C | `git show 2605bf2:corpus/SOURCES.md \| grep -c W1ScribeGate` → 1; `sed -n '1068,1090p' tools/souji-landing-gate.py`; `POINTER_PATH_RE.findall('/fast/scratch/…')` → `[]` | S238 still cites the gitignored path; `SOURCES.md` absent from the pointer source set; absolute paths unmatched | **pass** |
| H4 intent statement | — | §Intent statement above | **delivered** |

No axis is claimed improved or harmed by this seat: the report is history reconstruction for the r39
lesson. Nothing was edited outside this file.

## Scratch

`mkdir -p /fast/scratch/hyaku/souji-r39/W1RevHistory` was created; nothing was written into it and it
is removed with `rm -rf` at the end of this seat. No `/tmp` files, no clones, no receipts written.

## Disclosure — inference markers

- `[INFERENCE]` The statement that r35–r39 omitted the capture because no gate requires it is an
  inference from the absence of a `census/round-N/waves/` requirement in `souji-landing-gate.py`
  (I grepped `waves/` handling only through `CAPTURE_POINTER_RE`, which resolves a pointer *to* a
  capture; it does not require one to exist).
- `[INFERENCE]` That the r38 `4 + 0 dead` figure originated in prose rather than a reading cannot be
  proven from committed bytes: r38's wave directory is gitignored and no capture exists. What is
  observed is that nothing committed supports the number, which is exactly the r38 R2 wording.
