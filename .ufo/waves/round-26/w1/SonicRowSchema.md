# SonicRowSchema — field-count and cell-schema census of the five staged rows

## Status
STATUS: PASS — all five staged rows measured with their own `awk -F'|'` field count and with the frozen K3 validator: `NF=13` on every row and zero literal or escaped `|` in any cell, but 5/5 recheck cells fail E09 as staged; the landed normalized counterparts (S128–S132) validate clean. No row is metered as clean on recheck.

## Evidence

Revision: lane HEAD `ba8b54b85814dd980aa96050fe111c7cbfd4956a` (base `0eca7c8a5d10bcbfdae50d0c390d277deec63bfd` verified ancestor). Read-only source bytes: `/home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md`, sha256 `1510052ee7ca2b6fa3d6e2b89c397011865b07dec0fa1c8e097945cfa6b9f7d6`, 170331 bytes, mtime 2026-10-24 23:33:20 -0300. Header is file line 5, separator line 6; the five staged rows are lines 7 / 8 / 9 / 21 / 29.

Schema authority: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh:3` — "one registry table, 11 columns => NF=13".

### 1. Per-row field count (`awk -F'|' '{print NF}'`, the five lines)

```
line 7  S109 NF=13
line 8  S110 NF=13
line 9  S111 NF=13
line 21 S123 NF=13
line 29 S131 NF=13
```

13 fields = 11 columns + 2 boundary pipes on every row.

### 2. Pipe-escape scan

```
literal pipe chars per row: line 7=12 line 8=12 line 9=12 line 21=12 line 29=12
backslash-pipe occurrences in the 5 rows: 0        (no backslash of any kind occurs in the five rows)
'&#124;' / '｜' occurrences: 0
```

Negative arm (proves the scan discriminates): one escaped pipe injected into S109 → `S109 NF=14` and validator `E01 S109 fields=12`.

### 3. Offending cells — recheck (column 10), all five

Mirror `/var/tmp/souji-r26-SonicRowSchema/corpus/SOURCES.md` = header + separator + these five rows only; command `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin/souji-shokunin --file <mirror> --today 2026-10-25`, exit 1:

```
file	E09	S109 recheck=on-release — host `git --version` is 2.56.0
file	E09	S110 recheck=on-release — re-grep call sites at the next host git tag
file	E09	S111 recheck=on-release — re-read builtin/pull.c at the next host git tag
file	E09	S123 recheck=90d — re-run `bash fixtures/r23-trigger-prune.sh` (expect 7 PASS and exit 0)
file	E09	S131 recheck=90d — re-run the read-only census (expect 5 registrations, 0 prunable)
```

Code histogram on that mirror: `E01=0  E09=5  E11=8`, exit 1. The eight E11 are a minimal-mirror artifact (no `corpus/knowledge/` files present); see Finding 6.

Positive control: stripping only the em-dash tail to bare `on-release` / `90d` leaves `E09=0` (residual lines are E11 only). The prose, not the mirror, causes the flag.

### 4. Landing state at HEAD (same validator, real registry)

`/home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --file corpus/SOURCES.md --root . --today 2026-10-25` → exit 0; findings naming S128–S132: none; code histogram `1 ok`, `34 W04` (pre-existing duplicate-url-across-scopes warnings, non-status).

```
 S128  recheck=[ on-release ]  usedby=[ corpus/knowledge/git-auto-maintenance-trigger-set.md, corpus/knowledge/git-auto-maintenance-trigger-set-r23.md ]  NF=13
 S129  recheck=[ on-release ]  usedby=[ corpus/knowledge/git-auto-maintenance-trigger-set.md, corpus/knowledge/git-auto-maintenance-trigger-set-r23.md ]  NF=13
 S130  recheck=[ on-release ]  usedby=[ corpus/knowledge/git-auto-maintenance-trigger-set.md, corpus/knowledge/git-auto-maintenance-trigger-set-r23.md ]  NF=13
 S131  recheck=[ 90d ]         usedby=[ corpus/knowledge/git-auto-maintenance-trigger-set-r23.md ]  NF=13
 S132  recheck=[ 90d ]         usedby=[ corpus/knowledge/git-auto-maintenance-trigger-set-r23.md ]  NF=13
```

The staged S131 used-by path was re-pointed as the prereg planned: `corpus/knowledge/count-objects-garbage-semantics-r23.md` → exists=no in the lane; the two admitted entry paths → exists=yes.

## Findings

1. **Field count compliant, 5/5.** `/home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md:7,8,9,21,29` each carry `NF=13`; no row needs a column repair. This is the whole of the "expect 13" check and it is clean.
2. **No `|` escape in any cell.** Same five lines: 12 literal pipes each (13−1), zero `\|`, zero backslash at all, zero `&#124;`, zero fullwidth `｜`. Nothing is masked by the field count — a masked pipe would have produced `NF=14` / `E01`, as the injected control shows.
3. **E09 ×5 — every recheck cell carries a prose tail after its cadence.** `SOURCES.append.md:7` recheck = "on-release — host `git --version` is 2.56.0"; `:8` = "on-release — re-grep call sites at the next host git tag"; `:9` = "on-release — re-read builtin/pull.c at the next host git tag"; `:21` = "90d — re-run `bash fixtures/r23-trigger-prune.sh` (expect 7 PASS and exit 0)"; `:29` = "90d — re-run the read-only census (expect 5 registrations, 0 prunable)". Each fails both the `^[0-9]+d$` arm and the symbolic arm because of the em dash, backticks, parentheses and periods. Fix is mechanical and already specified by the prereg: keep the leading cadence token, move the instruction out of the cell.
4. **The five staged rows are not the lane's convention.** `corpus/SOURCES.md` at HEAD, 132 rows: recheck values are `on-release` ×108, `180d` ×8, `90d` ×7, `365d` ×7, `on-correction` ×1, `on-change` ×1 — no row in the registry carries a prose tail. The staged tails are therefore an import artifact of the shokuknow package, not a lane style to preserve.
5. **Landed normalized rows pass.** `corpus/SOURCES.md:128-132` (HEAD) hold bare cadence, `NF=13`, used-by re-pointed onto admitted entries, and the frozen validator reports nothing for those ids at exit 0 — so the staged defects were actually repaired, not laundered.
6. **My `E11=8` is a mirror artifact, not a row defect.** The real count is one (staged S131's `count-objects-garbage-semantics-r23.md`, `[ -e ]` → no), which the full-tree mirror in `w1/MutC2Rows.md` independently established. Reporting the difference so the two reports are not read as contradicting.
7. **Independent re-derivation of `w1/MutC2Rows.md`, same verdicts.** Same five lines, same `NF=13`, same five E09 strings, same used-by set. This seat adds only the negative controls (Findings 2 and 3) and Finding 4's registry-convention census; nothing in the sibling report is contradicted.

## Attack log

**A1 — E09's symbolic arm accepts arbitrary prose, so the recheck schema gate is evadable.**

- Predicate: `/home/vgpnk/Projects/shokunin/scripts/sources-census.sh:582` — `function symbolic(s) { return s ~ /^[A-Za-z][A-Za-z0-9 _-]*$/ }` — and the E09 branch at `:665-666` (`recheck !~ /^[0-9]+d$/ && !symbolic(recheck)`).
- Demonstration: S109's recheck replaced with `on release whenever the host git tag moves and we re-grep the call sites` — letters and spaces only, `NF=13`, validator result `E09_for_S109=0`, prose accepted, exit 1 only from unrelated E11.
- Consequence: the frozen contract's "recheck = ISO date, NNd or symbolic cadence" is enforced only against prose that contains punctuation. A normalized row can satisfy K3's malformed-finding arm while carrying an unmeasurable recheck, and the no-punctuation variant is strictly easier to write than the staged one that was caught.
- Recommendation (stricter-only, and therefore amendment-gated, not applied): replace the shape regex with an enumerated cadence set (`on-release`, `on-correction`, `on-change`, `annual`, `NNd`) so the symbolic arm is an allowlist. No predicate, target or case set is changed by this report; the finding is filed for the L1 to amend before any future after-data if it is accepted.

## Housekeeping

- Scratch `/var/tmp/souji-r26-SonicRowSchema/` removed before yielding; no other directory touched.
- No tooling installed or upgraded (no pacman, uv, npx or cargo invocation this seat).
- No lane mutation: read-only `git rev-parse`, `git log`, `git merge-base` against the lane; the only file written is this report. `/home/vgpnk/Projects/shokuknow` was read only.

## Handoff

Main agent: nothing to re-run for my two classes — the census is closed. If A1 is accepted, it needs an L1 amendment with a red arm before any after-data; if the append is re-opened, re-run `bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` at the tip and confirm `E09` count is 0 and row count is 132.
