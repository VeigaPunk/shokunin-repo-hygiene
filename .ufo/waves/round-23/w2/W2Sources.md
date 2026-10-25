# W2Sources — C3 registry rows S115–S119: shape/used-by/pipe/cadence/teaches + census warning-set diff

STATUS: **survives** — all five assigned checks pass on the committed tip bytes; the census
warning SET is byte-identical to the base's retained 30 `W04` rows. Two adjacent inconsistencies
surfaced (one cadence divergence between a used-by entry and its rows; one uncommitted evidence
drift at the tip) — routed below, neither falsifies the rows.

Seat: `L1Souji23.W2Sources` (scout / falsify). Round 23, wave 2.
Artifact: `corpus/SOURCES.md` lines 135–139 (rows S115–S119), landed at `4765250` (rows added),
current tip `102690017115cb202f292828c90b72705f69bf09`.
Preregistration: `.ufo/waves/round-23/preregistration.txt` §C3, frozen target
"registry rows 114 -> >=117 with 0 malformed and 0 duplicate ids; census exit 0".

Read-only: all probes were `git show`/`git diff`/`grep`/`python3` reads plus the frozen counters.
Every scratch copy lived under `/var/tmp/souji-r23-w2-Sources/` (removed before yield). No lane
file, index, jj state, or git object written.

NOTE — the working tree is mid-wave dirty (peers in flight). Every check below that names "the
tip" was run against **committed bytes** (`git show 4765250:` = HEAD bytes for these files; the
registry and `repo-size-census-readonly.md` are clean, `count-objects-garbage-readings-r25.md`
and `census/round-23/sources/qiita-gc-auto.raw` carry uncommitted edits — see F-2).

---

## 1. Assigned checks, all on committed bytes

### 1a. 11-column shape — PASS

Registry contract (sources-census.sh:3, "SOURCES-CONTRACT-v1: one registry table, 11 columns =>
NF=13") and the header at `SOURCES.md:19` declare 11 columns. Per-row pipe census:

```
S115 line=135 pipes=12 cells=11 empty_cells=[] kind=docs tier=A status=mined opened=2026-10-25
S116 line=136 pipes=12 cells=11 empty_cells=[] kind=docs tier=A status=mined opened=2026-10-25
S117 line=137 pipes=12 cells=11 empty_cells=[] kind=docs tier=A status=mined opened=2026-10-25
S118 line=138 pipes=12 cells=11 empty_cells=[] kind=community tier=B status=mined opened=2026-10-25
S119 line=139 pipes=12 cells=11 empty_cells=[] kind=community tier=B status=mined opened=2026-10-25
```

12 pipes = leading + 10 separators + trailing for 11 cells; no empty cells. The five rows sit
inside `## Registry` (heading line 17, table header line 19); census E12 clean.

### 1b. No literal or escaped pipe in any cell — PASS

`sed -n '135,139p' corpus/SOURCES.md | tr -cd '|' | awk '{print length}'` → `60` (5×12, so no
extra pipe byte exists anywhere in the five lines). `grep -c '\\|'` → 0; `grep -c '&#124;'` → 0.

### 1c. `used-by` names an existing entry — PASS, and stronger than the validator

```
S115,S116,S117 → corpus/knowledge/repo-size-census-readonly.md   (exists at tip)
S118,S119      → corpus/knowledge/count-objects-garbage-readings-r25.md (exists at tip)
```

The census E11 only checks path existence for `mined` rows (sources-census.sh:555-568;
.ufo/reports/round-12/SOURCES.md:114 admits it "does not prove that a target cites the row ID").
I verified the citation too:

- `repo-size-census-readonly.md:1-3` — `source: S115 — https://git-scm.com/docs/git-count-objects`,
  `S116 — git-fsck`, `S117 — git-prune`, each URL byte-matching the registry cell.
- `count-objects-garbage-readings-r25.md:1-2` — `source: S118`, `source: S119` with matching
  URLs; S118/S119 also cited in body at lines 51–52.

### 1d. `recheck` is a valid cadence — PASS

S115–S117 = `on-release` (symbolic, matches the script's `/^[A-Za-z][A-Za-z0-9 _-]*$/` at line 582);
S118–S119 = `180d` (matches `/^[0-9]+d$/`). The registry's cadence vocabulary across all 119 rows:
`{'on-release': 97, '180d': 8, '365d': 7, '90d': 5, 'on-change': 1, 'on-correction': 1}` — both
values are established. Zero E09 findings.

### 1e. `teaches` ≤ 25 words — PASS

Whitespace tokens = alnum tokens (no punctuation-only tokens):

```
S115 teaches=24 | S116 teaches=22 | S117 teaches=20 | S118 teaches=22 | S119 teaches=20
```

### 1f. Census validate + warning SET diff — PASS (set identical, not merely count)

```
$ ./scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji        # tip
  → 30 W04 rows + ok trailer, rc=0, zero E-findings, zero lines naming S115–S119
$ ./scripts/sources-census.sh validate <scratch lane with git show 4765250^:corpus/SOURCES.md>  # base
  → 30 W04 rows + ok trailer, rc=0, zero E-findings
$ sha256sum of sorted W04 sets: ff0b05788daa6bffebfe00c77efb90b0cf76331ad0f12b3d02dcdfac85527f58  (both)
$ diff base.w04 cur.w04 → IDENTICAL W04 SET
```

Base bytes were extracted read-only (`git show 4765250^:corpus/SOURCES.md`, parent `1208bfb`,
114 registry rows — the previous registry change was `7bc458c`) and validated in a scratch lane
with the full `corpus/{knowledge,lessons}` tree so E11 could resolve. The only output difference
base↔current is the `ok <path>` trailer. The lesson's claim "Registry `114 → 119` rows, 0
malformed, 0 duplicate ids, census exit 0 with the retained 30 W04" reproduces exactly
(`grep -cE '^ {0,3}\|[[:space:]]*S[0-9]{3,}[[:space:]]*\|'` → 114 base / 119 tip; `git diff
4765250^..tip` on SOURCES.md = exactly five added lines, zero changed lines).

### 1g. Frozen C3 counter on committed bytes — PASS

```
$ python3 -B tools/souji-gate-check.py --root <committed-bytes scratch> --round-date 2026-10-25 \
    --entries corpus/knowledge/repo-size-census-readonly.md \
              corpus/knowledge/count-objects-garbage-readings-r25.md \
    --snapshot-dir census/round-23/sources --slice census/round-23/records/empty-slice \
    --slice-verdicts census/round-23/records/empty-verdicts
entries=2 ok=2 slice_verdicts=0 slice_total=0 fail=0   (rc=0)
```

119 ≥ prereg target ≥117. Headline "2 entries, 3 rows" is descriptive, not the counter; the frozen
counter uses ≥117 — satisfied.

## 2. Findings

| id | file:line | what | verdict / required action |
|---|---|---|---|
| F-1 | `corpus/knowledge/repo-size-census-readonly.md:5` vs `corpus/SOURCES.md:135-137` | Entry front-matter `recheck: 90d`, but its three source rows say `on-release`, and the entry's own prose reads "after a host git upgrade" — on-release semantics. Convention is agreement: S110/S111 rows 90d ↔ r23 entry 90d; S112 row 180d ↔ r24 entry 180d; S118/S119 rows 180d ↔ r25 entry 180d. Only this entry diverges. No counter binds entry recheck to row recheck (gate-check has no recheck rule; census E09 checks syntax only). | The five-row checks still pass, but the round must **fix or disclose** the label — the boring fix is `recheck: on-release` on line 5 to match rows and prose. |
| F-2 | tip working tree (`git status --porcelain`, captured this run) | `census/round-23/sources/qiita-gc-auto.raw` modified in flight: committed sha256 `7d2298c1…` (2962 B blob `8b703259`) vs working `3274d936…` (2687 B, mtime 05:50); `corpus/knowledge/count-objects-garbage-readings-r25.md` modified (committed § `設定` locators being relabeled to § `ガベージコレクション`); `tools/__pycache__/` untracked again (R23-M8's "removed before landing" now contradicted). The S118 quote `"The default value is 6700. Setting this to 0 disables it."` survives in **both** byte versions (2× each), and §1g passes on committed bytes, so S118's grounding survives — but the gate's green at yield time is over drifted bytes. | Not a falsification of the rows; **disclose/route** — K4's owner counts `__pycache__` as a mismatch and whoever lands the r25/qiita edits must reconcile the committed snapshot receipt with the drifted bytes. |

## 3. Remaining unknowns

- Whether the entry's `90d` label was deliberate (the lesson's Gate at
  `corpus/lessons/round-23.md:79-83` declares only status/quotes, no cadence rationale).
- Whether the in-flight r25-entry and qiita-raw edits land or revert — the § `設定` vs §
  `ガベージコレクション` locator question is a peer dispute I did not adjudicate.
- S115's teaches ends "no write side effect documented"; the lesson (Gate, line 79) already
  discloses this is documentation-absence, not an empirical read-only proof — consistent wording,
  no action.
