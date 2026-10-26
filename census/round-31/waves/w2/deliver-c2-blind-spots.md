# deliver-c2-blind-spots — what the r31 C2 tokenizer rules suppress on real lane content

Seat: SwarmCritic14 (wave 2, round 31). Lane `/home/vgpnk/Projects/shokunin/souji-shokunin`.
Read at rev `2c16d018e40db7c23420a2c3bb546b52957bcc25` (lane tip) and control revs
`9f17a1ef571f3a510a51ac233d7cf50ac0c871fc` (lane base) and
`8024b540b04d677d47cf51a0d1132ec8705ef14a` (C2 landing).

STATUS: the C2 suppressions are quantified. No LG-DANGLING-PTR false negative exists on the
scanned real content of rounds 13-30. Two tokenizer rules are nevertheless wider than the
contract's stated intent and lose true positives on citation shapes that occur in the lane
(reproduced; one occurrence in real content, one shape absent from the counter's SHIFT oracle).

## 1. Gate pair used

| role | bytes | sha256 |
|---|---|---|
| base gate @ lane base | `git show 9f17a1ef571f3a510a51ac233d7cf50ac0c871fc:tools/souji-landing-gate.py` | `ba37e6bf804db1ad16b2ab53878a6626308bebb854af9bc2e7d230de81cd9056` |
| tip gate @ lane tip (also @ C2 landing: blob `7bfcb9b5a42ff942843e138de1de9ee1b0d83c9b`) | `tools/souji-landing-gate.py` | `577f1387ad51fc554f547a2aa4c40754ad73460db359de3178d40b559f09d8b8` |

The preregistration blob at `1d45496ae0e519b6fa0e9fa3b1f7e16130f4b525` hashes to the base
gate digest (`ba37e6bf…`), so "base gate" and "preregistration gate" are the same bytes.

## 2. LG-DANGLING-PTR set diff, rounds 13-30

Command (serial, once per round, identical arguments for both gates):

```
python3 -B <gate> --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev 2c16d018e40db7c23420a2c3bb546b52957bcc25 --round N \
  --fleet-root /home/vgpnk/Projects/shokunin
```

Result at tip rev (pointer findings per round; the pointer pass runs only for round >= 18 —
`tools/souji-landing-gate.py:1249` gates it):

| round | base gate | tip gate |
|---|---|---|
| 13-18, 21, 22, 25-27, 29, 30 | 0 | 0 |
| 19 | 4 | 0 |
| 20 | 6 | 0 |
| 23 | 2 | 2 |
| 24 | 1 | 0 |
| 28 | 2 | 0 |
| **total** | **15** | **2** |

The tip set is a strict subset of the base set: 13 removed, 0 added. The same 15 -> 2 diff
reproduces at the C2 landing commit `8024b540b04d…` and at base rev `9f17a1ef…` (base gate at
base content: 15 = the preregistration's 13 "false" pointers in rounds 19/20/24/28 plus the
2 round-23 pointers that cite genuinely absent paths).

Rule attribution of the 13 removed findings (each verified by reading the cited line):

- 7 letters-only prose (rounds 19, 20, 24, 28) — the A3-disclosed `_prose_pointer` skip;
- 2 `census/round-{18,19}/...seat-audit...json` — the new `"..." in raw` skip (G4);
- 3 en/em-dash line ranges (`tools/souji-seat-audit.py:274–277`,
  `tests/fixtures/r18-proc-census.sh:395–396`,
  `corpus/knowledge/process-residue-observations.md:58–59`) — the trim fix;
- 1 `.../.gitignore:fixture/` — the `:text` trim plus the `.captured` mapping (G6).

The 2 residuals are correct: `corpus/lessons/round-23.md:69` cites `tools/__pycache__/` as a K4
mismatch, and `corpus/lessons/round-23-verifier-spotcheck.md:28` cites
`census/round-3/garbage-census.out` with the words "The source path cannot be reopened: it is
absent". Both paths are absent at every rev tested; the gate's verdict is right.

## 3. Sweep of the suppressed classes

Delivered script: `deliver-c2-blind-spots-sweep.py` (imports the tip gate by path and reuses its
own regexes, so every verdict below is the gate's decision). Command:

```
python3 -B .ufo/waves/round-31/w2/deliver-c2-blind-spots-sweep.py \
  --root /home/vgpnk/Projects/shokunin/souji-shokunin \
  --rev 2c16d018e40db7c23420a2c3bb546b52957bcc25 \
  --gate /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py \
  [--from-round 13 --to-round 17] --json OUT
```

Summary (occurrences / distinct `source:line:token`), rounds 18-30 then 13-17:

| class | rule | 18-30 | 13-17 |
|---|---|---|---|
| S1 prose | `_prose_pointer` skip (`tools/souji-landing-gate.py:1118`) | 7 / 7 | 3 / 3 |
| S2 ellipsis | whole-token skip, `…` (base) or `...` (r31, `:921`) | 6 / 6 | 2 / 2 |
| S3 `:text` | second regex of `_trim_pointer_token` (`:878`) | 1 / 1 | 1 / 1 |
| S4 printf | r31 widening of `TEMPLATE_POINTER_RE` | 0 / 0 | 0 / 0 |

### 3.1 S1 — letters-only tokens: 13 distinct reach the prose test, 7 suppressed, 0 hidden dangling

Six letters-only tokens resolve to real directories (`corpus/knowledge` x6 occurrences). The
seven absent ones were read line by line:

| source:line | token | judgment |
|---|---|---|
| `corpus/lessons/round-15.md:11` | `tests/probes` | prose: "this round prohibits all seat tests/probes" |
| `corpus/lessons/round-15.md:64` | `census/checker` | prose: "not executions of the census/checker" |
| `corpus/lessons/round-17.md:80` | `census/verify/vault/quarantine` | prose: four suites, four counts "(49/49/57/101, 0 failed)" |
| `corpus/lessons/round-19-verifier-spotcheck.md:154` | `tools/tests/census/corpus` | prose: "Preserve tools/tests/census/corpus refusals" — four roots |
| `corpus/lessons/round-20.md:153` | `corpus/helper` | prose noun pair ("wrapper and corpus/helper inputs") |
| `LOG.md:1106` | `corpus/authority` | prose (the example A3 names) |
| `LOG.md:1123` | `tools/kill/killpg` | prose pair (the G8 example) |
| `LOG.md:1436` | `corpus/source/QUALITY` | prose triple: "Existing corpus/source/QUALITY rows" |
| `corpus/lessons/round-24.md:145` | `corpus/census/tools` | prose triple: "the corpus/census/tools line numbers" |
| `corpus/lessons/round-28-verifier-spotcheck.md:36` | `corpus/knowledge/registry` | literal grep pattern inside `grep -c 'corpus/knowledge/registry'` |

Verdict: 10/10 prose, none a path citation. The class is a live hole (A3 says so) but costs
zero false negatives on this content. Rounds 18-30 only: 7/7 prose, 6 real directories resolved.

### 3.2 S2 — ellipsis tokens: 8 distinct, 0 hidden dangling

| source:line | token | judgment |
|---|---|---|
| `corpus/lessons/round-19-verifier-spotcheck.md:49` | `census/round-{18,19}/...seat-audit...json` | placeholder cut (G4); interior dots, no single path |
| `corpus/lessons/round-19.md:138` | `census/round-10/__pycache__/…pyc` | cut; the named file exists (`…/S13-candidate-battery.cpython-314.pyc`) |
| `corpus/lessons/round-22-verifier-spotcheck.md:166` | `census/…/man7-rename.2.txt` | cut; file exists at `census/round-22/attempt2/sources/man7-rename.2.txt` |
| `corpus/lessons/round-22-verifier-spotcheck.md:167` | `census/…/arch-gio.1.txt`, `census/…/gtk-filetrash.txt`, `census/…/man7-statx.2.txt` | cuts; all three exist under `census/round-22/attempt2/sources/` |
| `corpus/lessons/round-17-verifier-spotcheck.md:99` | `.ufo/quarantine/round-17/…/dot-git-empty-stub` | cut of an untracked runtime stub; the line states it is absent |
| `LOG.md:946` | `.ufo/quarantine/round-17/…` | same directory cut |

Only one of the eight is skipped *because of the r31 rule* (the G4 placeholder, which base
flagged twice after brace expansion). Verdict: 0 hidden dangling pointers.

### 3.3 S3 — `:text` trims: 8 distinct, 6 benign, 1 contract case, 1 defect

Six are trailing-colon forms (`corpus/README.md:471-472:`, `tools/souji-verify.sh:`,
`census/round-12/scout-surfaces.md:94:`, `LOG.md:1511`, `:1532`, `:1651`) that the pre-existing
`rstrip(".,;:!?")` already removed at base. One is the G6 case
`census/round-26/waves/assimilation/validate/tests/vault/vadv-49/.gitignore:fixture/` (resolved
through `.gitignore.captured`; the as-cited name is absent and base flagged it). The eighth is
the defect in section 4.

### 3.4 S4 — printf widening: unexercised on this content

Zero `%d`/`%f`-shaped tokens exist in the scanned files of rounds 13-30. The 36 template skips
are all the pre-existing `round-` cut (`census/round-`, `corpus/lessons/round-` at
`corpus/QUALITY.md:150`, two distinct tokens). The r31 widening of `TEMPLATE_POINTER_RE`
therefore changes nothing on the current content.

### 3.5 Whole-token skips are invisible in SUMMARY

`checked_ptrs` counts only paths that `_pointer_paths` yielded. Distinct whole-token skips in
rounds 18-30: 60 (`skip:angle-or-star` 38, `skip:round-placeholder` 19, `skip:ellipsis-single`
5, `skip:ellipsis-triple` 1, `skip:unbalanced-braces` 1; classes overlap). None appears in the
TSV or in any SUMMARY field, so `fp=0 real=2` cannot distinguish "nothing cited" from "every
citation skipped". Across rounds 18-30 the gate yields 2068 distinct existing paths, 7 prose
skips and 2 dangling findings at tip.

Instrument fidelity: the sweep reproduces the gate's own `checked_ptrs` and its dangling count
exactly for all 13 rounds (e.g. round 20: gate 1331, sweep 1331; round 23: gate 2, sweep 2).

## 4. Defect A — a colon-joined pair silently drops the second path

`_trim_pointer_token` (`tools/souji-landing-gate.py:878`) strips `:(?![0-9])[^:\s]*$` under the
docstring's reading that a `:<non-digit>` suffix "names something inside the cited path". For
`A:B` where B is itself a rooted path, B is not inside A, and B is never resolved.

Real occurrence in the lane: `corpus/lessons/round-17.md:7` writes the replay argument
`--specs .ufo/waves/round-16/w1-spec.json:.ufo/waves/round-16/w2-spec.json`. The sweep reports
`dropped_pathlike: true`, `dropped: .ufo/waves/round-16/w2-spec.json`, `dropped_exists: true`.
Both elements exist today, so no wrong verdict has been produced; the token is unverifiable by
construction. Note this line sits in a lesson the pointer pass never reads (round 17 < 18).

Reproduction (scratch clone of the lane at tip, `origin` removed, throwaway identity; commits
`39b9f99644770e897ab1b88e397cbce4304308ed` and `45009205bb7cb64bc72bdb94aed33dff0887cce1`,
appending to the always-scanned `corpus/README.md`):

```
- colon pair: `census/round-17/seat-audit-replay.py --specs .ufo/waves/round-16/w1-spec.json:.ufo/waves/round-16/w2-missing.json`
```

base gate: `LG-DANGLING-PTR  .ufo/waves/round-16/w1-spec.json:.ufo/waves/round-16/w2-missing.json  corpus/README.md:704`
tip gate: no LG-DANGLING-PTR (findings = the same 3 LG-SEAT-UNCARRIED as at the unprobed tip).

Smallest safe correction (stricter-only): skip the trim when the suffix matches
`POINTER_PATH_RE` or starts with a pointer root; resolve `A:B` as cited, so an absent B is
reported exactly as base reported it.

## 5. Defect B — a trailing sentence ellipsis suppresses a complete path

`tools/souji-landing-gate.py:921` skips any token containing `"..."`. G4's class is an *interior*
placeholder (`census/round-18/...seat-audit...json`). A complete citation followed by a sentence
ellipsis has only trailing dots; the base gate handled it correctly, because
`token.rstrip(".,;:!?")` removed them before resolution.

Reproduction (same scratch commit `45009205bb7cb64bc72bdb94aed33dff0887cce1`, appended line):

```
- ellipsis probe: see tools/souji-missing-tool.py... (sentence continues)
- prose probe: the tools/missingprobe split
```

base gate: `LG-DANGLING-PTR tools/souji-missing-tool.py corpus/README.md:706` and
`LG-DANGLING-PTR tools/missingprobe corpus/README.md:707`; tip gate: neither (0 dangling).

Of the three probe tokens the tip gate suppresses, the letters-only one is contract-sanctioned
by G8/A3; the other two are true positives lost by implementation breadth, and neither shape is
in the counter's SHIFT oracle (the v3 probes are listed at `census/round-31/c2-counter-v3.py:186-191`:
interior-dot placeholder, dash and hyphen line specs, `tools/x.py:<word>`, `round-%02d`,
`round-%d`, a `.captured` name and `corpus/<word>/<word>` — no colon-joined pair, no trailing
ellipsis on a complete path), so `shift=ok` cannot catch either.

Smallest safe correction (stricter-only): evaluate the skip on `raw.rstrip(".")` instead of
`raw`. `census/round-18/...seat-audit...json` still holds interior dots and still skips, so G4
is preserved.

## 6. Correction is verdict-neutral on measured content

A patched copy of the tip gate implementing both corrections (scratch, sha256
`792c53ee5949a404e8576e76b1203bc3cccfc4099f11a1222a496ff5ea949e15`):

- probe rev `4500920`: recovers both true positives and still reports no G4 placeholder, no
  prose token (findings = 2 LG-DANGLING-PTR + same carry lines);
- rev `2c16d018e40d` rounds 18-30 and rev `9f17a1ef571f` rounds 18-30: byte-identical finding
  sets to the tip gate (`diff` on the non-SUMMARY lines, all 26 round runs, empty).

So the two rules can be tightened without moving any measured reading of C2, including
`fp=0 real=2`, the REDARM cases G4/G6/G8, and the SHIFT oracle.

## 7. Bottom line

- 13 false LG-DANGLING-PTR removed at tip rev, 0 added; 2 true absent-path citations still
  reported. The diff is stable across tip, C2 landing and base revisions.
- Suppressed on real content: 10 prose tokens (10 prose, 0 citations), 8 ellipsis tokens
  (0 dangling), 8 `:text` trims (1 contract case, 1 pair defect), 0 printf tokens.
- Hidden dangling pointers found on the scanned real content: 0. Latent true-positive losses
  reproduced: 2 (colon pair; trailing ellipsis). Neither is disclosed in A0-A5 and neither is
  covered by the SHIFT oracle.
- No frozen target is relaxed by the correction; no axis is harmed at the measured readings.
  Operability is the axis the two defects would erode if a future lesson cites either shape.
