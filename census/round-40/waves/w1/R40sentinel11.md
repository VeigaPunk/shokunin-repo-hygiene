# R40sentinel11 — C2 operability attack, distinct item 11

- Seat: R40sentinel11 (sentinel, wave round-40/w1, item 11). Lane member (leaf; no subagent dispatch).
- Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`
- Axis attacked: **operability (C2)**.
- Frozen contract read first: `census/round-40/preregistration.txt:8` (C2 paragraph, lines 7–8 of the file).
- Read-only on lane bytes. No production file written, no frozen claim edited, no tool installed (pacman untouched, per the operator directive's paused state).

## Named edge (explicit, and distinct from the other w1 C2 edges)

**`ORACLE-FORGERY-BY-CONTROLLED-PROBE-NAME` + `ENTRY-START-RULE-UNFROZEN`.**

The distinct failure mode I attack is *not* the depth of the continuation join (R40scout17's `TOTAL-ON-SECOND-CONTINUATION`), *not* continuation-ownership/attachment across a class boundary (R40executor62), and *not* the negative-control `EISDIR` attribution (R40executor38). It is the **measurement input of the C2 leg itself**:

> The frozen C2 predicate requires the r40 L4 analyzer to "verify **all observed class/trigger pairs in the frozen list**" and to kill "if **any observed class mapping disagrees with runtime behavior**". The set of *observed* class/trigger pairs is produced by classifying the tool's stderr with a fixed-priority substring scan (`census/round-39/c2-counter.py:117-124`). That scan reads text the tool copies **verbatim from the record path and the record row name** — strings the counter itself chooses. Consequently the observed-pair list, and hence the C2 verdict, is **content-controlled by the counter's own probe filenames**, and the class-to-entry binding rule (how a class entry is *started*) is left unfrozen by the predicate.

Two concrete, executed falsifiers follow, plus one coverage gap.

## Evidence pointers (committed, exact)

| What | Where |
|---|---|
| Frozen C2 predicate + kill condition | `census/round-40/preregistration.txt:8` |
| Committed r39 control extractor (first class line only) | `census/round-39/c2-counter.py:133-144` (`docstring_classes`) |
| Committed class oracle (fixed-priority substring scan over stdout+stderr) | `census/round-39/c2-counter.py:117-124` (`classify`), tokens `RECORD-MISSING, RECORD-MALFORMED, RECORD-EMPTY, RECORD-OUTSIDE-ROOT` |
| Committed r39 L4 leg (the probe set + the mapping check) | `census/round-39/c2-counter.py:186-201` |
| The probed record path is named by the counter | `census/round-39/c2-counter.py:188` (`os.path.join(base_scratch, "absent.tsv")`), `:190` (`probe` = `record-probe.tsv`) |
| Runtime raise sites (ENOENT ⇒ `RECORD-MALFORMED`, other OSError ⇒ `RECORD-MISSING`) | `tools/souji-worktree-drift.py:130-136` (`parse_record`) |
| Runtime copies the record **path** verbatim into stderr | `tools/souji-worktree-drift.py:135` (`"RECORD-MALFORMED: %s is not a regular file" % path`) |
| Runtime copies the record **row name** verbatim into stderr | `tools/souji-worktree-drift.py:293` (`"RECORD-OUTSIDE-ROOT: %s resolves outside %s" % row["name"]`) |
| Committed docstring class block (the refusal-class table) | `tools/souji-worktree-drift.py:43-60` |
| Prose line mentioning a class token by containment, not by prefix | `tools/souji-worktree-drift.py:14` (`outside it is refused (RECORD-OUTSIDE-ROOT), and ...`) |
| Prior-round disclosure that `classify` is a first-match substring scan | `.ufo/waves/round-39/w1/W1CritDisclosure.md:402-409` (D15) |
| Prior-round disclosure that a missing file reports `RECORD-MALFORMED` and an EACCES file reports `RECORD-MISSING` | `.ufo/waves/round-39/w1/W1CritDisclosure.md:407-409` (D15, last sentence) |
| Maintainer precedent for editing only the class line to carry the trigger | commits `601195a` ("drift docstring puts each trigger on its class line (single-line rule)") and `790d16b` ("drop unreachable EISDIR from the RECORD-MISSING line") |

Byte pins used throughout (read via `git show`, never the worktree):

```
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD
be4cb61e84ebcbf05814d3dfe6ba00b6f730f10e
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse 0242085909fb6a4ee041c5443d76316ac6d59d4b:tools/souji-worktree-drift.py
5a2b32941bc5c3da628ee92f75be1c33192ca311
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse 0242085909fb6a4ee041c5443d76316ac6d59d4b:census/round-39/c2-counter.py
953810db16fa0f7f308311b0aa65a49ad1d80223
git -C /home/vgpnk/Projects/shokunin/souji-shokunin merge-base --is-ancestor 0242085909fb6a4ee041c5443d76316ac6d59d4b HEAD
ANCESTOR=yes
git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain -- tools tests census/round-39
(empty)
```

`0242085` is the base revision named in `census/round-40/preregistration.txt:2` ("Base branch revision: 0242085909fb6a4ee041c5443d76316ac6d59d4b (round-39 verified tip)").

## Commands actually run

All probes live in `/fast/scratch/hyaku/souji-r40/R40sentinel11/` and were run with an explicit `TMPDIR`; every tool byte under test was obtained by `git -C <lane> show <rev>:<path>` into scratch, never read from the worktree.

```
cd /fast/scratch/hyaku/souji-r40/R40sentinel11
TMPDIR=/fast/scratch/hyaku/souji-r40/R40sentinel11 python3 -B c2_probe.py      # runtime class map, join variants
TMPDIR=/fast/scratch/hyaku/souji-r40/R40sentinel11 python3 -B c2_probe2.py     # errno space of parse_record
TMPDIR=/fast/scratch/hyaku/souji-r40/R40sentinel11 python3 -B c2_probe3.py     # oracle forgery, path + row channels
TMPDIR=/fast/scratch/hyaku/souji-r40/R40sentinel11 python3 -B c2_probe4.py     # entry-start rule vs join separator
TMPDIR=/fast/scratch/hyaku/souji-r40/R40sentinel11 python3 -B c2_probe5.py     # frozen-pair matrix + oracle + trigger coverage
TMPDIR=/fast/scratch/hyaku/souji-r40/R40sentinel11 python3 -B c2_probe6.py     # falsifier A (entry-start) + B (forgery)
TMPDIR=/fast/scratch/hyaku/souji-r40/R40sentinel11 python3 -B c2_probe7.py     # decisive: verdict vs probe file name
TMPDIR=/fast/scratch/hyaku/souji-r40/R40sentinel11 python3 -B c2_probe8.py     # same, using the committed module's own functions
TMPDIR=/fast/scratch/hyaku/souji-r40/R40sentinel11 python3 -B c2_probe9.py     # final consolidated matrix
```

`c2_probe8.py` and `c2_probe9.py` import `census/round-39/c2-counter.py` **as committed at `0242085`** (`importlib.util.spec_from_file_location` over a `git show` extraction) and call its own `classify`, `docstring_classes` and `run_drift`. The falsifier is therefore not an artefact of my transcription of those functions.

The committed r39 counter was also executed read-only against the lane (it only reads the lane and writes into `--scratch`):

```
cd /home/vgpnk/Projects/shokunin/souji-shokunin && TMPDIR=/fast/scratch/hyaku/souji-r40/R40sentinel11 \
python3 -B census/round-39/c2-counter.py --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev 0242085909fb6a4ee041c5443d76316ac6d59d4b --base-rev 0242085909fb6a4ee041c5443d76316ac6d59d4b \
  --scratch /fast/scratch/hyaku/souji-r40/R40sentinel11
```
Output (rev == base-rev, so L1/L2/L4/L5 are expected to FAIL: the leg is a *difference* leg):
```
LEG L1 FAIL new rc=2 class=True old rc=2 class=True
LEG L2 FAIL new rc=2 class=True old rc=2 class=True
LEG L3 PASS new rc=2 old rc=2
LEG L4 FAIL missing=RECORD-MALFORMED locked=RECORD-MISSING new_maps=True old_maps=True
LEG L5 FAIL new=(8, 8, 0, 0) old=(8, 8, 0, 0)
LEG L6 PASS r38-drift-record=10/10(base 10/10) r36-worktree-drift=12/12(base 12/12) r38-drift-envelope=12/12(base 12/12) r37-citation=16/16(base 16/16) r38-citation-commit=14/14(base 14/14)
SUMMARY legs=6 pass=2 fail=4 harm=0 tool_sha=59f1e57d7af0/e48ed08e6728 fixture_sha=e555d8281484
```
This is the same committed run recorded at `census/round-39/records/c2-after.txt` (`tool_sha=…/e48ed08e6728`, matching the `5a2b329…` blob I pin above).

## Finding 1 — the class oracle is content-controlled; a wrong docstring PASSES when only the probe file name changes

### Mechanism

`census/round-39/c2-counter.py:117-124`:

```python
def classify(proc):
    out = (proc.stdout + proc.stderr).replace("\n", " ")
    for cls in ("RECORD-MISSING", "RECORD-MALFORMED", "RECORD-EMPTY", "RECORD-OUTSIDE-ROOT"):
        if cls in out:
            return cls
    return "NO-CLASS"
```

It returns the **first token in a fixed priority list that occurs anywhere** in the text — not the class the tool raised, and not the *earliest* occurrence in the text. The tool writes the record path and the record row name into that same text verbatim (`tools/souji-worktree-drift.py:135` and `:293`), and the counter chooses both probe record names (`census/round-39/c2-counter.py:188,190`).

### Executed falsifier

`c2_probe9.py` output — the tool bytes are held **fixed** in each column pair; the only variable is the probe file name:

```
TOOL_BYTES             PROBE_NAME       RUNTIME(ENOENT)        OBSERVED(ENOENT)       RUNTIME(EACCES)        r39_L4     r40_joined
committed(correct)     absent           RECORD-MALFORMED       RECORD-MALFORMED       RECORD-MISSING         PASS       PASS
committed(correct)     RECORD-MISSING   RECORD-MALFORMED       RECORD-MISSING       RECORD-MISSING         PASS       PASS
broken-mapping         absent           RECORD-MALFORMED       RECORD-MALFORMED       RECORD-MISSING         FAIL       FAIL
broken-mapping         RECORD-MISSING   RECORD-MALFORMED       RECORD-MISSING       RECORD-MISSING         PASS       PASS
```

* `broken-mapping` = the committed docstring with the absent-path trigger removed from the `RECORD-MALFORMED` entry:
  `RECORD-MALFORMED  a non-regular record path, a line that does not match the schema, a duplicated name, or a TOTAL row that disagrees`.
  Runtime truth is unchanged: an absent record path raises `RECORD-MALFORMED` (`tools/souji-worktree-drift.py:133-135`), and that entry no longer names the trigger.
* `probe=RECORD-MISSING` means the counter names its probe record `RECORD-MISSING.tsv`. The tool's stderr becomes
  `REFUSAL RECORD-MALFORMED: …/RECORD-MISSING.tsv is not a regular file` — the **runtime class is still `RECORD-MALFORMED`**, but `classify` returns `RECORD-MISSING`, because `RECORD-MISSING` has higher priority in the scan list and now occurs in the copied path.
* Consequence: the L4 mapping check is then evaluated against the **wrong class entry**, and it passes for the wrong reason — the word "missing" is present *inside the class token itself* (`RECORD-MISSING`), a tautology the r39 wave already noted (`.ufo/waves/round-39/w1/W1RevC2Doc.md`, cited by R40executor38). The result: **the L4 leg reports PASS on bytes whose mapping is demonstrably wrong at runtime**, and the same leg reports FAIL when the probe is named honestly.

The same forgery works on the **record-content** channel, i.e. without any counter-side naming at all — the record row name is copied into stderr by the tool itself. From `c2_probe4.py`:

```
CASE                                   rc   RUNTIME_CLASS          ORACLE_CLASS           MATCH
path=RECORD-MISSING.tsv (absent)       2    RECORD-MALFORMED       RECORD-MISSING         MISMATCH
rowname=../RECORD-MISSING              2    RECORD-OUTSIDE-ROOT    RECORD-MISSING         MISMATCH
rowname=../RECORD-MALFORMED            2    RECORD-OUTSIDE-ROOT    RECORD-MALFORMED       MISMATCH
rowname=../RECORD-EMPTY                2    RECORD-OUTSIDE-ROOT    RECORD-EMPTY           MISMATCH
control rowname=../plain               2    RECORD-OUTSIDE-ROOT    RECORD-OUTSIDE-ROOT    ok
ORACLE_MISMATCHES 4/9
```

Here the tool raises `RECORD-OUTSIDE-ROOT` (a row resolving outside `--root`) while the oracle reports `RECORD-MISSING` / `RECORD-MALFORMED` / `RECORD-EMPTY` — all three classes the tool never raised. A record file is ordinary caller-supplied input; a record row named `../RECORD-MISSING` is legal under the row regex `ROW = re.compile(r"^REPO\t(?P<name>[^\t]+)\t…")` (`tools/souji-worktree-drift.py:87`).

`c2_probe8.py` reproduces the same result using the committed module's own `classify`/`docstring_classes`/`run_drift`, so this is a property of the committed instrument, not of my transcription:

```
probe=absent             runtime_class=REFUSAL RECORD-MALFORMED r39.classify()=RECORD-MALFORMED   MISMATCH
probe=RECORD-MISSING     runtime_class=REFUSAL RECORD-MALFORMED r39.classify()=RECORD-MISSING     MISMATCH
```

(the "MISMATCH" label on the first row is my harness comparing the full `REFUSAL …` prefix against the bare class token; the substantive comparison — `classify()` returns `RECORD-MALFORMED` when the path is honest and `RECORD-MISSING` when it is forged, while the runtime class is `RECORD-MALFORMED` in both — is correct and is the table shown above.)

### Why this is distinct from the already-disclosed D15 weakness

`.ufo/waves/round-39/w1/W1CritDisclosure.md:402-409` (D15) discloses that `classify` is "first-match over a substring set" and that "L4 proves the docstring *wording* maps to the observed class". It does **not** disclose that the observed class is **attacker/counter-controlled**: that the scan reads verbatim caller-controlled text, that the priority order lets a forged token in the copied path or row name override the real class, and that this converts the L4 leg from "the mapping agrees with runtime" into "the mapping agrees with whichever class the oracle was steered to". D15's correction is a reporting instruction; this is a measurement defect with an executed FAIL→PASS flip.

## Finding 2 — the class-entry *start* rule is unfrozen, and flips the C2 verdict on identical committed bytes

The predicate says the r40 analyzer "joins wrapped continuation lines into one class entry" but does not say how an entry **starts**. Two defensible rules diverge on the committed bytes.

`c2_probe4.py` / `c2_probe6.py`:

```
### D1 entry-start rule divergence (identical committed bytes)
  mode=prefix       sep=SPACE    entry_names_--root=True  len=81
  mode=prefix       sep=EMPTY    entry_names_--root=True  len=80
  mode=prefix       sep=NEWLINE  entry_names_--root=True  len=81
  mode=containment  sep=SPACE    entry_names_--root=False len=493
  mode=containment  sep=EMPTY    entry_names_--root=False len=487
  mode=containment  sep=NEWLINE  entry_names_--root=False len=493
```

and the frozen-pair check over the same bytes:

```
### FALSIFIER A — entry-start rule flips the C2 verdict on identical bytes
  entry_start=prefix       [('RECORD-MISSING','EACCES',True), ('RECORD-MALFORMED','missing',True), ('RECORD-OUTSIDE-ROOT','--root',True)]
  entry_start=prefix       FROZEN_PAIR_CHECK=PASS
  entry_start=containment  [('RECORD-MISSING','EACCES',True), ('RECORD-MALFORMED','missing',True), ('RECORD-OUTSIDE-ROOT','--root',False)]
  entry_start=containment  FROZEN_PAIR_CHECK=FAIL
  -> identical committed bytes, opposite C2 verdicts.
```

Cause: `tools/souji-worktree-drift.py:14` is prose that mentions `RECORD-OUTSIDE-ROOT` **by containment, not by line prefix**:

```
outside it is refused (RECORD-OUTSIDE-ROOT), and `--json` is refused when its
```

A containment-keyed join opens the `RECORD-OUTSIDE-ROOT` entry there and swallows the following prose paragraph (493 chars), producing this entry:

```
outside it is refused (RECORD-OUTSIDE-ROOT), and `--json` is refused when its resolved path is inside the root or any measured repository, or when it is a multi-link (hardlinked) file. It never prunes and never consults the network. The child git process gets a whitelisted environment (no inherited GIT_* variable; config discovery neutralised with GIT_CONFIG_NOSYSTEM=1 and GIT_CONFIG_GLOBAL/SYSTEM=/dev/null), so a path-valued trace variable or an env-injected config cannot make git write.
```

— which does **not** name the class's trigger `--root`. The prefix-keyed rule opens the entry at `tools/souji-worktree-drift.py:49` and does. The r39 control (`census/round-39/c2-counter.py:133-144`) uses `stripped.startswith(cls)`, i.e. the prefix rule, so a containment-keyed r40 analyzer would be *disagreeing with its own stated control* on the frozen base bytes.

A third free parameter — the **join separator** — decides whether a wrap-straddling trigger phrase survives at all (`c2_probe.py`, `c2_probe4.py`):

```
XBOUNDARY entry_firstline='RECORD-OUTSIDE-ROOT    a record row, or the gitdir it resolves to, escapes'
XBOUNDARY phrase='escapes --root' space_contains=True empty_contains=False newline_contains=False
```

`RECORD-OUTSIDE-ROOT`'s entry straddles the wrap (`tools/souji-worktree-drift.py:49-50`: `escapes` / `--root`), so the two-word phrase `escapes --root` is present under a space join and absent under an empty or newline join. The single token `--root` survives all three separators, so a single-token trigger check cannot discriminate the three joins — the frozen predicate's "synthetic wrapped-trigger probe" must be built against a phrase that actually straddles the wrap to have that power.

## Finding 3 — the "frozen list" of observed class/trigger pairs is not enumerated and is not derivable from the committed bytes

`census/round-40/preregistration.txt:8` says "verifies all observed class/trigger pairs **in the frozen list**", but the preregistration enumerates no pair (R40scout53 and R40scout17 make the same observation). Two committed facts make this gap material rather than cosmetic:

**(a) The reachable trigger space is larger than the committed docstring names.** From `c2_probe2.py`, running the committed tool:

```
OBSERVED ENOENT_absent_record        rc=2 r39_classify=RECORD-MALFORMED   stderr=REFUSAL RECORD-MALFORMED: …/absent.tsv is not a regular file
OBSERVED EACCES_locked_record        rc=2 r39_classify=RECORD-MISSING     stderr=REFUSAL RECORD-MISSING: [Errno 13] Permission denied: …
OBSERVED ENOTDIR_component_is_file   rc=2 r39_classify=RECORD-MISSING     stderr=REFUSAL RECORD-MISSING: [Errno 20] Not a directory: …
OBSERVED ELOOP_symlink_loop          rc=2 r39_classify=RECORD-MISSING     stderr=REFUSAL RECORD-MISSING: [Errno 40] Too many levels of symbolic links: …
OBSERVED ENAMETOOLONG_overlong_component rc=2 r39_classify=RECORD-MISSING  stderr=REFUSAL RECORD-MISSING: [Errno 36] File name too long: …
OBSERVED EISDIR_record_is_directory  rc=2 r39_classify=RECORD-MALFORMED   stderr=REFUSAL RECORD-MALFORMED: …/eisdir is not a regular file
OBSERVED RECORD-OUTSIDE-ROOT_row_escapes rc=2 r39_classify=RECORD-OUTSIDE-ROOT stderr=REFUSAL RECORD-OUTSIDE-ROOT: ../escape resolves outside …
```

`tools/souji-worktree-drift.py:130-136` raises `RECORD-MISSING` for **every** `OSError` from `os.open` other than `ENOENT`. The committed entry names only two of them:

```
committed RECORD-MISSING entry: 'RECORD-MISSING         EACCES or ELOOP opening the record path: the path exists but cannot be opened or read'
ENTRY_NAMED_TRIGGERS EACCES,ELOOP
```

`ENOTDIR` and `ENAMETOOLONG` are reachable and both map to `RECORD-MISSING`, yet neither is named. The r39 wave had already removed `EISDIR` from this line for exactly this reason (commit `790d16b`, "drop unreachable EISDIR from the RECORD-MISSING line") — the same class of defect survives for two other errnos. Extending the frozen pair list to include `RECORD-MISSING/ENOTDIR` makes the *committed* bytes fail the C2 check:

```
frozen_pairs=RECORD-MALFORMED/missing+RECORD-MISSING/EACCES                    fails=0
frozen_pairs=RECORD-MALFORMED/missing+RECORD-MISSING/EACCES+RECORD-MISSING/ENOTDIR fails=1 [('RECORD-MISSING','ENOTDIR','TRIGGER-NOT-NAMED')]
```

**(b) The r39 probe set covers 1 of the 4 reachable `RECORD-MISSING` triggers.** From `c2_probe2.py`:

```
R39_L4_PROBE_SET EACCES_locked_record,ENOENT_absent_record
RUNTIME_RECORD_MISSING_TRIGGERS EACCES_locked_record,ELOOP_symlink_loop,ENAMETOOLONG_overlong_component,ENOTDIR_component_is_file
R39_PROBE_COVERAGE 1/4
UNCOVERED_BY_R39_L4 ELOOP_symlink_loop,ENAMETOOLONG_overlong_component,ENOTDIR_component_is_file
```

So the "observed" set is a function of the counter's probe list, and the r39 probe list covers only a quarter of the reachable `RECORD-MISSING` triggers. Since the r40 predicate inherits "the frozen list", the r40 counter inherits the authority to choose which triggers are observed — and with it, the authority to make the C2 leg pass or fail.

## Verdict

**C2 operability: the frozen predicate is not falsifiable as written against a candidate, and the measurement instrument it names admits an executed FAIL→PASS flip. No claim is refuted; the frozen claim is under-specified in a way that lets a candidate be certified without the behaviour the claim names.**

Concretely:

1. **Concrete falsifier (Finding 1).** The C2 verdict is a function of a counter-chosen probe file name, not of the tool bytes. Executed: a docstring whose `RECORD-MALFORMED` entry does not name the absent-path trigger **FAILS** the L4-shaped check with an honest probe name and **PASSES** it with a probe named `RECORD-MISSING.tsv`, on byte-identical tool code, using the committed counter's own `classify`/`docstring_classes`/`run_drift`. The same steering is available from the *record content* channel (a row named `../RECORD-MISSING`), which requires no counter-side naming at all. An r40 counter that inherits the r39 `classify` oracle inherits this steering.
2. **Concrete falsifier (Finding 2).** The class-entry *start* rule is unfrozen; prefix and containment rules give opposite C2 verdicts on the identical committed bytes, because `tools/souji-worktree-drift.py:14` mentions `RECORD-OUTSIDE-ROOT` by containment only. The join separator is a second unfrozen parameter (the `escapes --root` phrase survives only a space join).
3. **Coverage gap (Finding 3).** The frozen pair list is not enumerated in the preregistration; the reachable `RECORD-MISSING` trigger space is `{EACCES, ELOOP, ENOTDIR, ENAMETOOLONG}` while the committed entry names `{EACCES, ELOOP}` and the r39 probe set observes 1 of 4. Adding `RECORD-MISSING/ENOTDIR` to the frozen list makes the *committed* bytes fail.

**Smallest remediation (for the r40 implementer, not a frozen-claim change):** freeze three things the predicate currently leaves free, and require the counter to observe classes from a **fixed, enumerated** source rather than from a priority scan of free text:

- *(i)* Derive the observed class from the **first** `REFUSAL <CLASS>:` token in stderr (positionally, not by priority scan), so copied paths and row names cannot be mistaken for the class. If a priority scan is kept, match the token only at a class-token boundary and exclude any occurrence that is part of a longer filesystem path.
- *(ii)* Freeze the class-entry start rule as **line-prefix** (`stripped.startswith(class_token)`), matching the r39 control at `census/round-39/c2-counter.py:139-143`, and freeze the join separator as a single space.
- *(iii)* Enumerate the frozen class/trigger pair list in the preregistration (or in a committed pair table beside the r40 counter) rather than leaving it to the counter, and make it cover the reachable trigger space observed above (`RECORD-MISSING`/`ENOTDIR` and `RECORD-MISSING`/`ENAMETOOLONG` are currently un-named in the committed docstring and are reachable). Then the r40 leg can kill a candidate that mis-maps a trigger, and the synthetic wrapped-trigger probe can be built to straddle the wrap so it discriminates a one-line join from a deep join *and* a space join from an empty/newline join.

**Limits of this report.** No r40 candidate bytes exist in the tree (`census/round-40/` contains only `preregistration.txt`; `git status --porcelain` shows only `?? census/round-40/`), so I did not and could not execute the candidate counter. Every FAIL/PASS above is a measurement of the **committed r39 instrument** (`census/round-39/c2-counter.py` at `0242085`) applied to committed r39 tool bytes (`5a2b329…`), with the r40 side modelled as a join-based analyzer over the same bytes. The findings are properties of the *measurement contract the predicate inherits*, not allegations about an unseen candidate. I did not run the r40 C3/C1 legs, did not modify any lane file, and did not commit or push anything. The EACCES trigger requires a non-root uid (the r39 wave's D17 records that receipts are reproducible only by uid 1000); this seat ran as uid 1000, and the EACCES probe therefore genuinely produced `RECORD-MISSING`.

Report path relative to the lane root: `.ufo/waves/round-40/w1/R40sentinel11.md`
