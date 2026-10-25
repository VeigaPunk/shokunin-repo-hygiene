STATUS: PARTIAL

# ResGateCheck — residual attack on the landed C2 counter (round 22, attempt 2)

Read-only. Wrote only this report and `residual/evidence/*` (four text files + the fixture
harness). No git/jj write, no service signal, no install, no pacman transaction, no read of
`/proc`, `.tower`, operator-sweep content, or a private TSV. Fixtures were built under
`/var/tmp/regc-gatecheck/base`, never in the lane. Registry reads
`/home/vgpnk/Projects/shokuknow/.ufo/waves/corpus-expansion-1/absent-defect-register.md`
(read-only, campaign tree) only through the frozen awk command.

No LSP device is mounted in this session (the tool inventory exposes none), so definition and
caller checks were done by reading `tools/souji-gate-check.py` and by executing it — not by
semantic navigation. Every claim below is either executed output quoted verbatim or a direct
read of the cited line; nothing rests on a grep match alone, and I mark the one inference I
draw from source text (`[INFERENCE]`, F7).

## 0. Pinned inputs, and the tip moving under the measurement

The lane tip advanced three times while I measured (four tips observed). The tool and both
entries are byte-identical across all four; the moving files are `corpus/SOURCES.md` (S111
locator/teaches row at `7bc458c`) and `census/round-22/attempt2/slice-verdicts.tsv` (S118
evidence text at `8680755`, class unchanged):

| rev | note |
|---|---|
| `4a6ee90a8f88` | tip at first measurement |
| `c1664fcde8b1` | tip at re-verification; C2 inputs identical |
| `7bc458c1e1dc` | `SOURCES.md` S111 row corrected by another seat's residual source audit |
| `868075547dcd` | last observed; `slice-verdicts.tsv` S118 evidence text expanded, class still `unverifiable`; counter re-run green |

Invariant blobs (identical at all four revs, `evidence/counter.txt`):

```
tools/souji-gate-check.py                               f26aa72855e38ee866689d3874e2b2ef8d63212a
corpus/knowledge/quarantine-staging-no-copy-r23.md      a878a6d9eb1758f7351522a69666352adfd4f663
corpus/knowledge/quarantine-origin-record-fields-r24.md 38c6e161a8e376a34cf8709161cb407fc2b5748c
census/round-22/attempt2/quarantine-slice               19fa47d72382c157845fd0638bd032570de07484
```

`slice-verdicts.tsv` was `f6131eac…` through `7bc458c` and `36bf7ed9…` at `8680755`; both
versions carry eight rows, classes `accepted×5, present×2, unverifiable×1`, all inside the
frozen enum. `corpus/SOURCES.md` was `7aa977f0…` at `c1664fcd` and `3ab461a7…` from `7bc458c`.

`git hash-object tools/souji-gate-check.py` = the committed blob at every tip, so the tool I
attacked is the landed tool, not a worktree variant.

## 1. Executed: selftest, then the real run

```
$ python3 -B tools/souji-gate-check.py --selftest
PASS fixture good -> ok [entries=1 ok=1 slice_verdicts=2 slice_total=2 fail=0]
PASS fixture no-date -> fail [entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=1]
PASS fixture long-quote -> fail [entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=2]
PASS fixture quote-absent -> fail [entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=2]
PASS fixture dangling-source -> fail [entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=1]
PASS fixture no-reject -> fail [entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=1]
PASS fixture no-gate -> fail [entries=1 ok=0 slice_verdicts=2 slice_total=2 fail=1]
PASS fixture partial-verdicts -> fail on V!=T with fail=0 [entries=1 ok=1 slice_verdicts=1 slice_total=2 fail=0]
PASS control always-green -> FALSE-GREEN-REJECTED [FALSE-GREEN-REJECTED]
selftest=9/9            SELFTEST_RC=0
```

```
$ python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 \
    --entries corpus/knowledge/quarantine-staging-no-copy-r23.md \
              corpus/knowledge/quarantine-origin-record-fields-r24.md \
    --snapshot-dir census/round-22/attempt2/sources \
    --slice census/round-22/attempt2/quarantine-slice \
    --slice-verdicts census/round-22/attempt2/slice-verdicts.tsv
entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0
REAL_RC=0
```

The frozen seven fixtures are all present and all discriminate; the control line prints
`FALSE-GREEN-REJECTED`, though its strength is qualified in F8 (it asserts rather than runs a
control tool). This matches the frozen kill rule.

Independent confirmation that the two entries' green is not vacuous (executed, `evidence/content.txt`):

- all nine Gate spans appear in the corresponding committed `.raw` page (tags stripped,
  entities unescaped, whitespace collapsed) — the `.txt` snapshots are not fabricated
  relative to their raws, and the raws are committed;
- every locator heading the landed Gates name exists in the snapshot they name
  (`Description` gtk-filetrash.txt:395, `COMMANDS` arch-gio.1.txt:97, `§ 6 Contents of a
  trash directory` freedesktop-trash.txt:54, `DESCRIPTION` man7-statx.2.txt:68 and
  man7-rename.2.txt:85, flags list under DESCRIPTION at man7-rename.2.txt:155);
- the S109 data row's digest matches: `sha256sum census/round-22/attempt2/sources/vendor-noreplace-probe.out`
  = `1634d206ef534f683b5d469a9f0333c80a4aaba58215bb63683111c024be8bb5`, the value quoted in
  the S109 row and in r23 line 1;
- all 13 files under `--snapshot-dir` are tracked at every tip (`git ls-files` = 13, `ls` = 13).

## 2. The six prescribed mutations

Fixture root `/var/tmp/regc-gatecheck/base`, rebuilt per run, one entry per invocation so the
counts line attributes to one mutation. Harness: `evidence/attack-harness.py`; raw output:
`evidence/attacks.txt`. Baseline in the same root: `entries=1 ok=1 slice_verdicts=8
slice_total=8 fail=0`, `RC 0`.

| # | mutation | verdict | observed line |
|---|---|---|---|
| 1 | indented `   - source: S999 — not in the registry` | **killed** | `FAIL entries/a1-indented-source.md check5-dangling-source: S999` / `entries=1 ok=0 … fail=1`, RC 1 |
| 2 | `- REJECT: staged entry alpha — quote cited against the wrong artifact, no reason field` | **killed** | `FAIL entries/a2-reject-no-reason.md check6-row-without-reason` / `entries=1 ok=0 … fail=1`, RC 1 |
| 3 | symlink under the snapshot dir → outside (both `../outside.txt` and an absolute target; the target holds the *same bytes*, so only the guard can fail it) | **killed** | `FAIL … check4-snapshot-outside-dir-line-7` + `check3-no-located-quote-with-snapshot` / `entries=1 ok=0 … fail=2`, RC 1 |
| 4 | locator token only from the snapshot filename (`snapshot: census/sources/section-3.txt`, nothing else locates) | **killed** | `FAIL … check3-no-locator-gate-line-7` / `entries=1 ok=0 … fail=2`, RC 1 |
| 5 | byte-exact staged package copy, no Gate (`sha256` equality asserted in-harness: `5ef47f38d868a7fe` both sides) | **killed** | `FAIL entries/a5-staged-copy.md check1-no-gate: entries/a5-staged-copy.md` / `entries=1 ok=0 … fail=1`, RC 1 |
| 6 | one verdict row deleted (S118) | **killed on V!=T, `fail=0`** | `entries=1 ok=1 slice_verdicts=7 slice_total=8 fail=0`, RC 1 |

All six behave exactly as the frozen kill rule requires. Mutation 6 is the exact shape the
prereg freezes: `fail` stays 0, the row is counted in neither V nor F, and the exit code
comes from `v == t` alone (`tools/souji-gate-check.py:174-177,196`).

## 3. Additional probes (each cheap, each isolating one clause)

| probe | mutation | verdict | observed line |
|---|---|---|---|
| A2b | `reason:` present with an empty payload: `- ADMIT: "…" — § DESCRIPTION flags — reason: — snapshot: …` | **survives** | `entries=1 ok=1 slice_verdicts=8 slice_total=8 fail=0`, RC 0 |
| A4b | locator word supplied by a *second* mention of the snapshot filename: ``… — see `census/sources/section-3.txt` — reason: … — snapshot: census/sources/section-3.txt`` | **survives** | `entries=1 ok=1 … fail=0`, RC 0 |
| A4c | locator word only inside the quoted span: quote `The section below states the rule.`, no other locator | **survives** | `entries=1 ok=1 … fail=0`, RC 0 |
| A6b | two ids on one slice line (` S114 S123 `), verdict for S114 only | **survives** | `entries=1 ok=1 slice_verdicts=2 slice_total=2 fail=0`, RC 0 |
| A7 | the whole run in a root with no VCS at all (`.git` absent), snapshot present only on disk | **survives** (baseline green) | `entries=1 ok=1 … fail=0`, RC 0 |
| A6c | verdict class `bogus` | **killed** | `FAIL slice verdict-bad-class-line-1:bogus`, RC 1 |
| A6d | duplicate verdict row for S114 | **killed** | `FAIL slice verdict-duplicate:S114`, RC 1 |
| A6e | verdicts file absent | fails for the right reason | `slice_verdicts=0 slice_total=8 fail=0`, RC 1 |
| A6f | all eight rows present with evidence pointer `x` | **survives** | `entries=1 ok=1 slice_verdicts=8 slice_total=8 fail=0`, RC 0 |

## 4. Findings

### F1 (medium) — predicate 6 is not enforced for the reason *string*: an empty `reason:` passes

`tools/souji-gate-check.py:46` `ROW_REASON_RE = re.compile(r"reason:\s*\S", re.I)` accepts any
non-space character after `reason:`, and the row separator is an em-dash. So
`— reason: — snapshot: …` satisfies it. The frozen predicate reads "≥1 ADMIT and ≥1 REJECT
with a reason string each" (preregistration C2, item 6); an empty payload is not a reason
string, yet the entry is counted `ok=1` and the tool exits 0 (probe A2b).
No live exposure: every ADMIT/REJECT row in the landed entries carries a real reason
(`r23:74-77`, `r24:71-77`). Fix is one character-class: require a word character that is not
the separator, e.g. `reason:\s*[^\s—]`.

### F2 (medium) — predicate 3 accepts a locator token that does not locate

`LOCATOR_RE` (`:42`) is searched over the whole Gate line after only the `snapshot:` token is
scrubbed (`:87`). Two ways to satisfy it without locating anything:

- the token sits inside the quoted span (A4c: quote `The section below states the rule.`);
- the token sits in a second mention of the filename (A4b: the backticked path reintroduces
  `section` after `SNAPSHOT_RE.sub` removed the `snapshot:` copy).

Both entries return `ok=1`. The frozen wording is "≥1 located quote … with a locator token";
a `section` that is part of the quoted text or of a filename locates nothing. Under the
narrower literal reading ("a token on the line") the implementation matches the text and the
defect is predicate strength, not the code — I record that ambiguity rather than resolve it,
because it changes what the counter may claim, not what the bytes say.
No live exposure: all landed Gate rows carry a real `§ <heading>` reference that exists in
the named snapshot (§1 above).

### F3 (low) — "committed snapshot file" is unenforced

Predicate 4 says "the committed snapshot file the Gate names". The tool contains no VCS read
at all (the only `subprocess` use is the selftest's `rm -rf`, `:286`), so a snapshot that
exists only on disk under `--snapshot-dir` passes: baseline probe A7 runs green in a root with
no `.git` and no commit history. No live exposure — all 13 snapshot files are tracked at every
tip — but the clause cannot fail on its own, which the frozen per-check discipline asks of
each check.

### F4 (low) — the slice reader takes only the first id per line

`SLICE_ID_RE.search(line)` (`:149`) keeps one id per line, so ` S114 S123 …` contributes only
S114 and a missing S123 verdict cannot lower V (`slice_verdicts=2 slice_total=2`, RC 0, probe
A6b). No live exposure: the landed slice is one id per line and reproduces byte-exactly from
the read-only campaign register through the frozen awk:

```
$ awk -F'|' -v l='souji' '$2 ~ ("`" l "`") && $3 ~ /round[0-9]+/ && $4 ~ /S[0-9]+/ \
    {print $4, $5}' "$REGISTER" | diff - census/round-22/attempt2/quarantine-slice
SLICE-REPRODUCED-EXACT     # 8 register rows == 8 slice lines
```

The predicate itself is "for every id line", so one-id-per-line is defensible; the gap only
matters if the derivation ever emits two ids on one line.

### F5 (low) — the verdicts are a presence check, not an adjudication check

`check_slice` accepts any non-empty third column (`:167-173`): all eight rows with pointer `x`
pass (A6f). Round-1's `evidence/CritC2Counter/INDEX.md:23` already recorded the `x`-pointer
fixture and the 8×`refused` variant; I confirm the behaviour is unchanged at the tip rather
than reporting it as new. The counter therefore attests "each slice row has a class and a
pointer", not "each verdict is true" — the truth of the eight rows rests on the per-row
Slice\* seat evidence, not on this counter.

### F6 (info — found and already fixed at the current tip) — registry locator for S111

At `4a6ee90`/`c1664fcd`, `corpus/SOURCES.md:131` field 7 read `§ OPTIONS --no-copy and
--exchange; snapshot …`. `man7-mv.1.txt` has no OPTIONS heading (`NAME|SYNOPSIS|DESCRIPTION|
AUTHOR|…`, DESCRIPTION at line 60; `--exchange` at 75 and `--no-copy` at 90-91 sit under
DESCRIPTION). This was the registry-side leftover of round-1's F2, which had been fixed in the
entry (`r23:76` already said "§ DESCRIPTION, option --no-copy") but not in the row. Commit
`7bc458c` (another seat's residual source audit) replaced it with `§ DESCRIPTION, options
--no-copy and --exchange (the page has no OPTIONS heading)` while I was measuring; verified at
the current tip (`evidence/context.txt`). Not open.

### F7 (info) — the Gate's `url:` is not bound to the snapshot

Check 2 requires *an* https URL with the round date (`:75-79`); nothing ties that URL to the
snapshot or to the quoted span. The baseline fixture proves it (`url: https://example.invalid/doc`
with `snapshot: census/sources/x.txt` → `ok=1`). The frozen predicate 2 does not require the
binding either, so this is a gap between "re-grounded in-round with this lane's own Gate block"
and the predicate as frozen, not a code defect. The landed selection does satisfy the stronger
reading, to the extent it can be checked offline: every one of the nine spans is present in the
committed `.raw` whose `<title>` names the entry's document — `rename(2) - Linux manual page`,
`mv(1) - Linux manual page`, `gio(1) — Arch manual pages`, `Gio.File.trash`,
`Trash Specification`, `statx(2) - Linux manual page` (`evidence/content.txt`). `[INFERENCE]` —
no `.raw` carries a canonical-URL link, so "these are the bytes served at that URL" rests on the
title match, not on a network re-fetch; I did not fetch anything.

### F8 (low, diagnostics honesty) — the "control always-green" line asserts, it does not execute a control

`tools/souji-gate-check.py:280-284`:

```python
green = "entries=1 ok=1 slice_verdicts=2 slice_total=2 fail=0"
control_survives = green.startswith("entries=1 ok=1") and score("no-gate")[1].startswith("entries=1 ok=1")
checks.append(("control always-green -> FALSE-GREEN-REJECTED", not control_survives, ...))
```

`green.startswith("entries=1 ok=1")` is a tautology on a hard-coded string, so the whole
disjunction reduces to "the SUT is not green on fixture 6". No control implementation is fed
the fixture set, unlike C1's frozen kill rule ("a control tool that prints
`assertions=0 skipped=0 mismatches=0` without reading any byte must FAIL the same selftest").
Consequence: the printed label `PASS control always-green -> FALSE-GREEN-REJECTED` claims more
than it demonstrates. C2's own frozen kill rule is satisfied by fixture 6 alone, so this is a
label/strength defect, not a false green claim about C2. A three-line stub that prints the
green line unconditionally and is scored against the same fixtures would make the line honest.

### F9 (info) — dead constant and two unexercised checks

`REASON_RE` (`:45`) is defined and never read after the hardening commit replaced it with
`ROW_REASON_RE`; dead weight. The selftest covers `check6-no-reject` but has no fixture for
`check6-no-admit` or `check2-no-url`. Neither is a frozen-fixture omission (the frozen list is
fixtures 1-7), and both paths are reachable, but "each check must be able to fail on its own"
is only demonstrated for the seven frozen cases.

## 5. Round-1 reconciliation (checked against the landed bytes, not restated)

| round-1 item | status at last-observed tip `8680755` | evidence |
|---|---|---|
| `CritC2Coverage.md` E5 / finding F1 — r24 introduced `LG-DANGLING-PTR` for `corpus/knowledge/quarantine-origin-record-fields-r23.md` | **fixed** | `souji-landing-gate.py --root . --rev <tip> --round 22` → `SUMMARY findings=4`; the r24 pointer is gone, and the four remaining findings are the pre-existing README:217 (×2), jj entry:148, round-22 spot-check:32 (`evidence/context.txt`) |
| `CritC2Coverage.md` E6 / finding F2 — committed r23 Gate cited `§ OPTIONS` | **fixed in the entry** (`r23:76` now `§ DESCRIPTION, option --no-copy`) ; the same wrong locator survived in the S111 registry row until `7bc458c` — see F6 |
| `CritC2Coverage.md` E8 — campaign ids S114/S123/… collide with new lane ids S109-S114; the map lives only in `corpus/lessons/round-22.md` M16 | **still open by design** | `slice-verdicts.tsv` keys are campaign ids; `SOURCES.md:129-134` holds lane ids for different documents. The counter resolves entry `source:` ids against the lane registry only (`:118-128`), so the collision is invisible to it and cannot produce a wrong V. Residual, disclosed in the lesson. |
| `CritC2Coverage.md` F3 / `CritC2Counter` — verdict pointer truth unchecked | **still open** — see F5 |
| frozen target: registry conformance | **met** | `./scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin --today 2026-10-25 souji` → 30 `W04` warnings, `souji ok …/corpus/SOURCES.md`, `VALIDATE_RC=0` at `c1664fcd`, `7bc458c` and `8680755` |

## 6. Residual risk / verification gaps

1. The counter certifies the *landed* entries and slice; it cannot certify that a future
   mutation of the same shape is caught, because three of its clauses (reason string, locator
   provenance, committed snapshot) are weaker than the frozen text — F1/F2/F3.
2. Verdict class semantics (`present|accepted|unverifiable|refused`) are not defined in the
   preregistration; the counter only enforces enum membership, so the eight verdicts' *meaning*
   is unverified here. F4's slice rows were adjudicated by round-1 Slice\* seats — I did not
   re-adjudicate them, and a residual seat should not.
3. I did not re-fetch any URL; the span provenance check is against the committed `.raw` bytes.
   A fabricated `.raw` plus a matching `.txt` would pass every check I ran — the tool has no
   digest binding between snapshot and URL (`evidence/content.txt` is an audit, not a guarantee).
4. The tip moved three times under me; all conclusions are pinned to the blobs in §0 and were
   re-executed at `8680755`. A later tip that changes `tools/souji-gate-check.py`,
   the two entries, the slice, or the verdicts invalidates the measurements, not the method.

## 7. Tooling

Nothing installed or updated: no pacman transaction, no `uv tool install`, no binary fetch.
Only pre-existing `python3` (stdlib), `git` (read-only: `rev-parse`, `ls-files`, `log`, `diff`,
`show`, `hash-object`), `awk`, `sha256sum`, `grep`, `diff` were used.

Evidence: `residual/evidence/counter.txt` (§0-§1), `attacks.txt` + `attack-harness.py` (§2-§3),
`context.txt` (§4 F6, §5), `content.txt` (§1 provenance and locator audit).
