# S54connector01 — souji round 54, seat report (connector role)

Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`
Round: 54, wave w1. Seat dir: `.ufo/waves/round-54/w1/S54connector01/`
Scratch (created, used, removed before yield): `/fast/scratch/hyaku/souji-r54/S54connector01/`
Tools installed: none. No `pacman`, no `uv tool`, no `npx`, no release binary — every command used a tool already on the host (`git`, `python3`, `grep`, `bash`, `diff`, `sed`, `awk`, `file`).

**Mandate:** sibling-overlap scan on the round's three declared surfaces, plus the fleet-root shared-state check, plus the L0 dependency table. **No subagent dispatched** (leaf member).

---

## 0. Verdict summary

| Surface | Verdict | Evidence |
|---|---|---|
| **(1) annotation-agreement counters** (correction-filing grammar, zone/straddle checks) | **NO-OVERLAP** | 0 sibling hits on `annotation-agreement` in any sibling `census/`+`corpus/`+`tools/`; the 3 r54 finding ids appear in **zero** files outside souji |
| **(2) fleet-root census capture verification** (receipt grammar, `#`-shape rules, CR naming) | **NO-OVERLAP** | `souji-fleet-root-census` is referenced in **zero** files outside souji; no sibling instrument reads the capture bytes |
| **(3) fixture-builder hardening** (pinned dates, git env flags) | **NO-OVERLAP** | sibling builders exist (kaidoku, kasegi, tameshi, tsukuroi, mori, chousa, kama) but each writes **its own** lane's fixtures; none shares souji's fixture paths, revs, or pins |
| **Fleet-root shared state** (does drift invalidate ENTRIES=49?) | **NO — ENTRIES=49 still holds** | re-take of the **pinned** tool at the *current* fleet root reproduces all 49 rows byte-for-byte; only the `# FLEET_HEAD` line differs |
| **L0 dependency** | **ZERO of 18 souji L0 questions is depended on** | table in §4; the two routed-around rulings (261 credential-name, 262 ignored-derivation) confirmed independent **by measurement**, not assertion |

**One bounded proposal (the connector's one move):** §5 — the C1 v3 counter's `PTR_RE` pointer exemption is **broader than the disclosure states** and swallows *any* `<token>:<digits>`, so an overstating SOURCES-pair annotation that merely carries a **timestamp** evades `UNFILED-SOURCES-ANNOTATION` entirely. A one-line narrowing keeps the honest real-lane case green and every committed fixture verdict unchanged, and it composes with the wave's already-routed `F12c-LOG-POINTER-EXEMPT` fixture.

---

## 1. Per-lane hit counts (evidence for the NO-OVERLAP verdicts)

Command (verbatim, `census/`+`corpus/`+`tools/` only, case-insensitive, `grep -rilE`):

```
for L in <20 sibling lanes>; do D=$L-shokunin; dirs=<census corpus tools that exist>;
  grep -rilE 'annotation-agreement|CORRECTION-IN-FENCE|RECEIPT_VERSION|CAPTURE-CRLF|fleet-root census|correction filing' $dirs; done
```

Verbatim output (receipt: `receipts/01-sibling-hit-counts.txt`):

```
audio          hits=0
chousa         hits=0
game-dev-2d    hits=0
game-dev-3d    hits=0
kagi           hits=0
kaidoku        hits=1 tools/round-40/score-receipt.sh
kake           hits=0
kama           hits=1 corpus/lessons/round-40-verifier-spotcheck.md
kasegi         hits=0
kengaku        hits=0
kotoba         hits=0
kotodama       hits=0
kumitate       hits=0
lore           hits=0
mado           hits=0
mori           hits=1 corpus/lessons/round-75.md
revenger       hits=0
tabi           hits=0
tameshi        hits=0
tsukuroi       hits=0
```

**Total across 20 sibling lanes: 3 hits, 3 files.** For contrast, the same grep over souji's own `census/ corpus/ tools/` returns **36 files** (the whole r52/r53/r54 counter family, the builder, the preregistrations, the matrices, the capture, the receipt, the knowledge entries, the lessons).

Two negative controls that make the NO-OVERLAP verdicts load-bearing rather than a grep artefact:

```
$ grep -ril 'souji-fleet-root-census' <all lanes except souji>
(empty)

$ grep -rlE 'ZONE-TOKEN-STRADDLES-EDGE|BOGUS-RECOMPUTED|UNFILED-SOURCES-ANNOTATION|
             RECEIPT-UNKNOWN-KEY|COMMENT-AMBIGUOUS-NAME|TOOL-SHA-ARG-MISMATCH' <all lanes except souji>
(empty)
```

So no sibling lane owns, reads, or reproduces **any** r54 finding id, and no sibling instrument touches the fleet-root capture tool.

---

## 2. Per-hit overlap verdicts (each hit opened enough to classify)

Receipt: `receipts/07-per-hit-overlap-verdicts.txt`.

**HIT 1 — `kaidoku-shokunin/tools/round-40/score-receipt.sh` → DIFFERENT SURFACE.**
`receipt_version` here is a **JSON object key** in a score-receipt wrapper that captures one counter run's stdout/stderr and re-emits it with `exit_code`, `counter_sha256`, `stdout_json`… It reads no fleet-root capture bytes, no SOURCES rows, no annotation grammar. The r54 C2 surface is a **`# KEY=VALUE` machine-readable receipt header** with a frozen five-key grammar (`RECEIPT_VERSION, TOOL_SHA256, FLEET_HEAD, CAPTURE_SHA256, ENTRIES`) bound to a capture's sha256. Different artifact, different grammar, different bytes. **No overlap.**

**HIT 2 — `kama-shokunin/corpus/lessons/round-40-verifier-spotcheck.md` → DIFFERENT SURFACE.**
Prose in a lesson about the **fleet-owned** `scripts/sources-census.sh` (the corpus/SOURCES.md **registry** census) run against a parked worktree. The r54 C2 surface is the **lane-owned** `tools/souji-fleet-root-census.py` (a **top-level-entry hygiene** capture of the fleet root). Same words, different instrument, different bytes: the kama line names no capture file, no receipt, no `#`-row shape. **No overlap.** (This is a *vocabulary* collision, not an ownership collision — recorded because §5's move turns on the same two scripts reading the same registry differently.)

**HIT 3 — `mori-shokunin/corpus/lessons/round-75.md` → DIFFERENT SURFACE.**
Prose about the fleet script's 120 s foreground budget at round start ("the fleet-root census validator exceeded the 120 s foreground shell budget"). No instrument, no byte overlap. **No overlap.**

Sibling references to souji's *bytes* are prose only (3 files: `kumitate/…/agent-isolation-substrates.md`, `mori/…/drift-classification-r20.json`, `mori/…/round-12.md`) — none is an instrument that reads souji's committed census bytes.

---

## 3. Fleet-root shared state: does drift invalidate ENTRIES=49?

**No.** The capture records `FLEET_HEAD=3b0d5329147d3b05d3aec5e908c75405ae3bc05a`; the fleet root has since advanced (other rounds land commits continuously — the fleet HEAD moved *twice during this seat's own scan*). Receipt: `receipts/08-entries-49-revalidation.txt`.

```
$ python3 -B souji-shokunin/tools/souji-fleet-root-census.py \
      --fleet-root /home/vgpnk/Projects/shokunin --out <scratch>
CENSUS ENTRIES=49 tracked=22 ignored=22 untracked-stray=5 symlink=0

$ diff <(grep -v '^# FLEET_HEAD' <fresh>) \
       <(grep -v '^# FLEET_HEAD' souji-shokunin/census/round-54/records/fleet-root-census.tsv)
IDENTICAL: all 49 rows, all class/COUNT/disposition columns, and every other header are byte-for-byte equal

$ diff <fresh> <committed>
4c4
< # FLEET_HEAD=36d6efc95c3138e13b6bf0b301d618ad170ed1e5
---
> # FLEET_HEAD=3b0d5329147d3b05d3aec5e908c75405ae3bc05a
```

Since the capture's `FLEET_HEAD`, the fleet has touched exactly two top-level paths (`MANIFEST.json`, `.ufo`) — **both already rows of the 49-entry capture** — and `.gitignore` is unchanged (empty `git diff --stat`). The only new top-level name on disk is `.git`, which the tool excludes by design (`entry.name == '.git'`, `tools/souji-fleet-root-census.py:140`).

Counter verdict on the committed capture at the measured rev (unchanged):

```
SUMMARY entries=49 rows=49 unclassified=0 class_mismatch=0 counts=ok tool_sha=ok
        removal_proposed=0 receipt=ok sorted=ok tool_pin=ok rev=bfdbb336329e
RC=0
```

**Second-order note for the L1 (not a defect):** the capture is a *snapshot*, and its `FLEET_HEAD` names the rev it was taken at, so a later fleet commit will keep the capture valid (proved above) but will never make it "current". The C2 counter only **format-checks** `FLEET_HEAD` (40-hex) and requires receipt-⇄capture agreement on it — it deliberately does not resolve it against the live fleet head (already disclosed as a named limit: *"FLEET_HEAD remains format-checked, not resolved"*). No action; recorded so the L1 knows the drift is expected and benign.

---

## 4. L0 dependency table

Full table with per-line evidence: `receipts/05-l0-souji-lines.txt`. Summary:

| line | round | topic | depends on an answer? |
|---|---|---|---|
| 59 | r16 | census contractions scope | **NO** |
| 66 | r17 | jj keep refs | **NO** |
| 67 | r17 | `census/operator-sweep-20261019/` disposition | **NO** |
| 70 | r18 | reaping 58 fixture orphans | **NO** |
| 71 | r18 | re-derive `NAMESPACE_SHA256` (different tool) | **NO** |
| 79 | r20 | F5 reason-field exposure | **NO** |
| 202 | r40 | `merge/souji` staged id collisions | **NO** — r54 opened its **own** row **S277**; `S277` appears in **no** file under `census/round-46/assimilation/` (staged max is S242) |
| 205 | r40 | correction to the r40 collision note | **NO** |
| 206 | r41 | inline dispatcher log | **NO** |
| 215 | r44 | `--json` leaf-symlink semantics | **NO** — r54's symlink surface is the capture's `kind=symlink` **row class** (FA8/FH2), not a `--json` output path refusal |
| 223 | r46 | `merge/souji` staged package | **NO** — assimilation held; no merge/souji row landed |
| 235 | r46 | L2 floor on the Windows host | **NO** — this round ran on this Linux host |
| 245 | r48 | census conf-form on the Windows layout | **NO** — on this Linux host the conf form resolves souji → `CONF-RC=0` (`census/round-54/records/census-before-receipt.txt`) |
| 252 | r50 | consolidated conf-form proposal | **NO** — same |
| **261** | r52 | **credential-name rule (refuse vs redact)** | **NO — measured**: the tool's own `CRED_NAME` regex, applied to all 49 capture names, matches **none**; the refusal path is never exercised, so the capture is valid under **either** ruling |
| **262** | r52 | **`ignored`-column derivation** | **NO — measured**: `c1-counter.py` contains **0** occurrences of `ignored`/`check-ignore`; `c2-counter.py` contains **0** `check-ignore` calls. Neither counter re-derives `ignored` from git; the counter checks the capture's **own** columns |
| 263 | r52 | stray entries report-only | **NO — measured**: all 5 `untracked-stray` rows carry `disposition=report-only`; `removal_proposed=0` passes |
| 264 | r52 | host note (no ruling requested) | **NO** |

**Zero of 18 souji L0 questions is depended on by the frozen r54 work.** The two the round named as routed-around are confirmed independent by measurement, not by assertion.

**Quantified caveat on 262 (for the L1 and the r55 planner):** the *next* capture's numbers depend on the ruling. On this host the two derivations disagree on **4** top-level names — `.jj`, `.ruff_cache`, `.ufo`, `kumitate-shokinin` — of which **3** are untracked and therefore class-relevant: if the `ls-files` variant is chosen, those 3 rows move `untracked-stray → ignored` and the capture's COUNT block becomes `tracked=22 ignored=25 untracked-stray=2` instead of `tracked=22 ignored=22 untracked-stray=5`. The **committed** r54 capture remains verifiable as-is (the counter checks its own columns); a **future** capture taken under the other derivation carries different numbers. No r54 claim depends on which is chosen.

---

## 5. The one move (connector proposal): narrow the C1 pointer exemption to a *path-like* token

### The gap

`census/round-54/c1-counter.py:80`:

```python
PTR_RE = re.compile(r'[A-Za-z0-9_.\-]+:\d')
```

The preregistration discloses the exemption narrowly (`:159-160`): *"the SOURCES scan is line-based and **exempts lines carrying a path:line pointer** (meta-references quoting an annotation are not annotations)"*. But the regex matches **any** run of `[A-Za-z0-9_.-]` followed by `:` and a digit — it is **not** path-scoped. So a line that is *not* a meta-reference at all is silently exempt from the `UNFILED-SOURCES-ANNOTATION` class the round claims to instrument.

### Measured: the overstatement evades on a timestamp

Receipt: `receipts/03-c1-ptr-exemption-probe.txt`. On the **unmodified F12-LOG-UNFILED** fixture the class fires; append **one parenthetical** and it does not:

```
F12-LOG-UNFILED (unmodified):
  FINDING UNFILED-SOURCES-ANNOTATION LOG.md:2 claims 274 -> 275 rows but the registry holds 3; ...
  SUMMARY ... logunfiled=1 ...            RC=1

SAME fixture, the ONLY change = " (S275:1)" appended to the LOG line:
  SUMMARY ... logunfiled=0 ...            RC=0
```

Three further shapes, each an overstatement that the frozen counter accepts (exit 0, `logunfiled=0`) — all built on the unmodified builder, only the LOG line rewritten:

| variant | LOG line | frozen v3 | `PTR_RE` matched |
|---|---|---|---|
| `T-TS` | `- 2026-11-03T20:31:08Z the r52 note said corpus/SOURCES.md 274 -> 275 rows.` | **rc=0, logunfiled=0** | `2026-11-03T20:3` |
| `T-UTC` | `- r52 note (2026-11-03 20:31) said corpus/SOURCES.md 274 -> 275 rows.` | **rc=0, logunfiled=0** | `20:3` |
| `T-CLOCK` | `- at 14:05 the r52 note said corpus/SOURCES.md 274 -> 275 rows.` | **rc=0, logunfiled=0** | `14:0` |

This matters because **timestamps are the ordinary shape of a dated LOG entry**: `grep -cE '20[0-9]{2}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}' souji-shokunin/LOG.md` → **0** today, but `corpus/README.md` already carries **8** bare `YYYY-MM-DD` stamps and the lane's own receipts stamp `2026-11-03T20:31:08Z` (the format of `census/round-54/records/census-before-receipt.txt`). A future dated frontier line that also names a row count is exactly the misread class the round instrumented — and it is exempt.

### The move: one regex, no fixture churn

Change the exemption to require a **path-like** token (a `.` or `/` before the `:`):

```python
PTR_RE = re.compile(r'[A-Za-z0-9_.\-/]*[A-Za-z0-9_.\-][./][A-Za-z0-9_.\-/]*:\d')
```

**Measured on a scratch copy (the lane's frozen bytes were not touched):**

- the real lane at the measured commit stays green — `SUMMARY … logunfiled=0 logrecomp=0 …` **RC=0** (the honest meta-reference `LOG.md:2578` carries `LOG.md:2527`, a path-like pointer, so it stays exempt);
- all **13** committed C1 fixtures keep their exact exit code and their exact named finding — receipt `receipts/04-c1-narrowed-ptr-matrix.txt`:

```
F1-HONEST-TIP   0/0   -              F7-TILDE-FENCE   1/1  CORRECTION-IN-FENCE
F2-MULTI-ANNOT  1/1   MULTIPLE-ANNOTATIONS           F8-BT4-PARITY  1/1  CORRECTION-IN-FENCE
F3-INERT        1/1   INERT-CORRECTION               F9-HTML-COMMENT 1/1  CORRECTION-IN-FENCE
F4-FENCE        1/1   CORRECTION-IN-FENCE            F10-STRADDLE    1/1  ZONE-TOKEN-STRADDLES-EDGE
F5-REWRITE      1/1   DELETED-LINES                  F11-BOGUS-RECOMP 1/1 BOGUS-RECOMPUTED
F6-RECORD-DRIFT 1/1   RECORD-SHA-MISMATCH            F12-LOG-UNFILED 1/1  UNFILED-SOURCES-ANNOTATION
F12b-LOG-FILED  0/0   -              (v3-frozen-exit / v3-narrowed-exit)
```

- the `S275:1` variant flips from exit 0 to **exit 1 with `UNFILED-SOURCES-ANNOTATION`** — the class finally bites;
- F12 and F12b keep their verdicts (1 and 0), so the claim's kill rule is untouched.

### Why this is the *connector's* move, not a new attack

The wave has already routed the pointer exemption twice — reviewer01's `AF4a` ("fake pointer … named limit confirmed") and mutation01's `M7` (survivor, "no fixture carries a pointer") — and the r55 plan names the fixture `F12c-LOG-POINTER-EXEMPT` (*"a LOG pair line with a `path:line` pointer, no filing, must stay green"*). The r55 fixture as worded **pins the broad behaviour as intended**: a `path:line` pointer stays exempt either way, so `F12c` would pass with the broad regex *and* with the narrowed one, and the r55 counter would carry the over-broad exemption forward unexamined. This proposal makes `F12c` load-bearing: it stays green **only** under the narrowed regex, and a second arm (a `path:line`-shaped pointer that must stay green vs. a timestamp-shaped one that must not) discriminates the two.

**Affected axis:** calibration (C1). **Unaffected:** coverage (C2) — the C2 counter never reads `PTR_RE`; and the C1 *claim* is unaffected, since the real lane is green under both.

### Risks (stated, not smoothed)

1. **This is a counter change, and the counters are byte-frozen.** It is a *r55* proposal, not an r54 edit. It must land as a named limit + the r55 fixture, never as an r54 byte change.
2. **A narrower exemption could turn a currently-silent exemption into a refusal on some line not in the live tree today.** I measured the live tree: `broad-only exemptions in live tree: 0` — every pair-annotation line in `LOG.md`/`corpus/README.md` that is exempt today is exempt by a **path-like** token, so the narrowing is a **no-op on the live lane today** (verified: RC=0, `logunfiled=0`). But a *future* meta-reference that used only an `S275:1`-style pointer would flip from silent to refused; that is the intended direction (the class is a refusal class), but it is a behavioural change and the r55 prereg must disclose it.
3. **My narrowed copy is scratch-only and uncommitted.** It is evidence that the move is *compatible*; it is not a proposed byte diff of the frozen counter, and I did not edit the lane's counter.

### Verification the L1 can run

```bash
# (a) the live tree has no broad-only exemption today
python3 - <<'PY'
import re
B=re.compile(r'[A-Za-z0-9_.\-]+:\d'); S=re.compile(r'[A-Za-z0-9_.\-/]*[A-Za-z0-9_.\-][./][A-Za-z0-9_.\-/]*:\d')
for p in ('LOG.md','corpus/README.md'):
    for i,l in enumerate(open(p,encoding='utf-8').read().splitlines(),1):
        if 'corpus/SOURCES.md' in l and B.search(l) and not S.search(l): print(p,i,l[:120])
PY
# (b) the narrowed copy keeps the real lane green (receipts/04 shows the 13-fixture matrix)
```

---

## 6. Cross-lane second-order effect (recorded; no cross-lane action taken)

The connector role asks for second-order effects across runtime / contract / substrate / verification surfaces. One real asymmetry, measured, on the **fleet-owned** script — **not** a souji defect and **not** a cross-lane edit:

`scripts/sources-census.sh` has **two** trims with **different** CR behaviour:
- the bash `trim_cell` (`:531`) uses `[[:space:]]` → **CR-aware**;
- the gawk `trim` (`:581`) uses `gsub(/^[ \t]+|[ \t]+$/,"",s)` → **CR-blind**.

Receipt: `receipts/06-cr-grammar-asymmetry.txt`. A 3-row registry, LF vs CRLF:

```
LF   fleet census rows : 3      LF   fleet validate : file  W03 S001 mined but unused
CRLF fleet census rows : 0      CRLF fleet validate : file  E12 S001 row outside Registry section
```

while the LOG's own stated oracle and the C1 counter's `registry_count` are both **CR-tolerant** (`grep -cE` → 3/3; `REG_ROW_RE` → 3/3). And this is **not hypothetical**: `kotoba-shokunin/corpus/SOURCES.md` is committed **CRLF** (436 CR lines in the blob) — the fleet census reports `file rows 0` and emits `E12 … row outside Registry section` for it, while the LOG-style oracle counts **180** rows. This is the *same* defect kagi already filed as L0 `kagi | round-30` (`scripts/sources-census.sh:581 trim() strips space/tab, not CR`) — still open, still unpatched, and now measurable on a second lane.

**Souji's own registry is LF** (`CR lines: 0`), so the r54 C1 pair-scan and the C2 capture are **unaffected**. This is recorded as context for the L1 and as the concrete instance that makes the r55 wording "a path:line pointer" precise. I did not touch the fleet script (read-only, fleet-owned, out of this lane's scope) and did not file a duplicate L0 — the existing kagi L0 already names it.

---

## 7. Scope, discipline, and honesty notes

- **No lane file was edited.** `git -C souji-shokunin status --short` at the end shows only the L1's own in-flight uncommitted files (`census/round-54/records/*`, `census/round-54/sources/`, `corpus/lessons/round-54.md`, …); the seat's own outputs are confined to `.ufo/waves/round-54/w1/S54connector01/`. The lane tip advanced under me (the L1 landed `0fada8b3 round-54: content …` mid-scan); all lane reads were `git log/show/status/diff` with `GIT_OPTIONAL_LOCKS=0`.
- **No mutating git or jj anywhere.** The two commits I made were inside scratch clones I created (`git clone` of the lane into scratch), with a fixture identity and `core.hooksPath=/dev/null`; each was asserted to be a fixture before committing.
- **Scratch deleted** before yield (`rm -rf /fast/scratch/hyaku/souji-r54/S54connector01/`); receipts were copied into the seat dir first.
- **Nothing was claimed as passing that was not run.** Every number in this report comes from a command whose verbatim output is in `receipts/`. The matrix in §5 is a re-run of the frozen builder + both counter arms in scratch, not a quotation of the committed TSV (though the re-run's 13 rows match the committed `c1-matrix-v3.tsv` on columns 1–6 exactly, and the fixture manifest reproduces the committed `fixture-manifest.tsv` 23/23 — both checked).
- **Contradiction I am flagging rather than smoothing:** the r54 lesson records the pointer exemption as *"behaviour matching the disclosure"* (r54 lesson, reviewer01 `AF4a` line). My measurement says the behaviour is **broader** than the disclosure: the disclosure says *path:line pointer*, the regex accepts any `<token>:<digits>`, and a **timestamp** evades the class. That is a wording-vs-behaviour mismatch in the frozen instrument's own disclosure, not a regression of this round's claims.
- **Unrun:** I did not re-run the standing landing-suite counter (`census/round-46/c1-counter.py`) or the round-end census gate; those are the L1's. I did re-run the r52 and r53 c2 counters against the r54 capture (both exit 0) and the r54 c1/c2 counters at the measured rev (both exit 0), and the pinned selftests (13/13 and 10/10 pass).

### Receipt index (all under `.ufo/waves/round-54/w1/S54connector01/receipts/`)

| file | content |
|---|---|
| `01-sibling-hit-counts.txt` | per-lane hit counts (§1) |
| `02-fleet-root-state.txt` | fleet log/diff since the capture's FLEET_HEAD; fresh re-take; capture sha vs receipt |
| `03-c1-ptr-exemption-probe.txt` | PTR_RE exemption bypass: F12 vs F12+`(S275:1)` (§5) |
| `04-c1-narrowed-ptr-matrix.txt` | the narrowed copy's verdicts across all 13 committed C1 fixtures (§5) |
| `05-l0-souji-lines.txt` | the L0 dependency table with per-line evidence (§4) |
| `06-cr-grammar-asymmetry.txt` | the two-trim CR asymmetry; kotoba's live CRLF instance; the L0-262 derivation diff (§6, §4) |
| `07-per-hit-overlap-verdicts.txt` | each of the 3 hits opened and classified (§2) |
| `08-entries-49-revalidation.txt` | ENTRIES=49 re-validation against the current fleet head (§3) |
