# R41scout02 — C2 sibling-overlap recon (souji round 41, wave 1)

Seat: R41scout02 (scout, leaf — no subagent dispatch). Lane: /home/vgpnk/Projects/shokunin/souji-shokunin, freeze commit e2a74312af4233963e44e4dbb38838ece07b8bd2.
Read-only recon of /home/vgpnk/Projects/shokunin; the only file this seat wrote is this report. All paths below are relative to the fleet root /home/vgpnk/Projects/shokunin unless absolute.

## Verdict

**No existing tool in the fleet duplicates `tools/souji-freeze-check.py`'s contract.** C2's tool (spec: `souji-shokunin/census/round-41/c2-counter.py:59-206`) must: take `--root DIR --prereg RELPATH --rev 40HEX`; read the preregistration **from the committed tree at `--rev`**; parse the r41 prereg grammar (`# prereg`, `Round:`, `## C<n> — …` sections with `Base:/Counter:/Population:/Control:/Target:/Kill:` fields, counter/population carrying `sha256=<64hex>`); emit `FINDING <claim> <CLASS>` lines with the closed vocabulary `NO-CLAIMS, FIELD-MISSING, FIELD-EMPTY, BASE-UNRESOLVED, BASE-NOT-ANCESTOR, COUNTER-MISSING, COUNTER-DIGEST, POPULATION-MISSING, POPULATION-DIGEST, POPULATION-EMPTY, CONTROL-MISSING, CONTROL-NOT-RED, FROZEN-EDITED, DISPATCH-BEFORE-FREEZE`; end with `SUMMARY claims=N findings=N`; exit 0/1 findings/2 `COULD-NOT-EVALUATE` (c2-counter.py:166-173, 199-206). No sibling tool combines (a) prereg-grammar parsing, (b) rev-addressed instrument-digest verification, (c) a must-be-red control, and (d) dispatch-must-postdate-freeze. Four siblings each hold one of these primitives (details §3); none holds the contract. `tools/souji-freeze-check.py` is absent at both base 7eebc183 and freeze e2a7431 (§2.7) — nothing in-lane to collide with.

## 1. Sweep commands and counts

Harness `grep` tool (case-insensitive, recursive, gitignore disabled, hidden paths searched — proven by the control probes). `path` is `;`-joined. "Files" = distinct matching files reported by the tool (it caps at 20 shown matches/file; file totals are exact as reported).

| # | Pattern (case-insens.) | Path scope | Files |
|---|---|---|---|
| G1 | `preregistration` | `tools` (fleet) + `*/tools` (9 lanes: chousa, kaidoku, kama, kotodama, mado, mori, souji, tameshi, tsukuroi) | **55** |
| G2 | `sha256=` | same as G1 | **95** |
| G3 | `preregistration` | `scripts` (fleet) + `templates` (fleet) | **0** |
| G4 | `sha256=` | `scripts` + `templates` (fleet) | **0** |
| G5 | `preregistration` | `.ufo/gates` (fleet, hidden dotdir given explicitly) | **0** |
| G6 | `sha256=` | `.ufo/gates` (fleet) | **0** |
| G7 | `preregistration` | `*/scripts` + `*/templates` (lanes: kake, kumitate, tabi, kotodama) | **0** |
| G8 | `sha256=` | `*/scripts` + `*/templates` | **12** (kumitate 3, tabi 9) |
| G9 | `preregistration` | `*/.ufo/gates` (lane gates dirs) | **0** |
| G10 | `sha256=` | `*/.ufo/gates` | **1** (kaidoku) |
| X1 | `fr(eez|oz)` (freeze-word sweep, extra) | fleet `scripts`+`templates`+`.ufo/gates` | **10** (scripts 4, templates 4, gates 2) |
| X2 | `preregistration` / `sha256=` (extra, out-of-mandate dir) | `kotoba-shokunin/verifiers` | **0** / **3** |

Controls (prove searched paths were actually indexed):
- Control A (G3/G4 negatives): pattern `watchdog` over fleet `scripts`+`templates` → 9 files (shokunin-watchdog.sh, hyaku/{closure-prompt.md,fleet-commit.sh,hyaku.env,inline-dispatcher.py,inline.sh,jj-lane.sh,lane-addendum.md}, templates/round-prompt.md). Same tool, same scope: the negative is a true negative.
- Control B (hidden-dir searchability): pattern `fr(eez|oz)` over fleet `.ufo/gates` → 2 files hit (`root-ledgers.py`, `root-ledgers/expected.json`) — the dotdir is searched when named explicitly.
- Excluded per mandate: `.git`/`.jj` (never matched — scoped paths exclude them), and every scratch tree (`/fast/scratch/hyaku/*`, fleet `.scratch/`, `.ufo-scratch/`, lane `scratch/`/`.scratch/` dirs — none lie under the swept scope paths). Fleet-root dirs outside the mandate were not swept except the X2 extra.

G1's 55 files by lane: kama 42, souji 8, tameshi 3, kaidoku 1 (fixture corpus), tsukuroi 1. G2's 95 by lane: souji 53, tsukuroi 7, tameshi 6, mori 7, mado 4, kaidoku 11, kama 3, kotodama 2, chousa 2. Fleet `tools/` (round-49 control fixtures: manifest.json + binary blobs only): 0 hits in G1/G2.

## 2. Deep dives — every hit that could plausibly duplicate C2's tool

### 2.1 In-lane preregistration readers (souji-shokunin/tools)
- `souji-shokunin/tools/souji-axis-check.py` (:1-30, 55-83) — the only in-lane tool that **parses a preregistration file**. Reads a PATH (not a rev); parses only a `## MACHINE BLOCK … END` section of `CLAIM <id>` blocks with `axis:/surface-class:/enumerate:`; checks axis-ownership rules R1-R4; stdout `claims=C flags=F`. **No duplicate**: disjoint grammar (MACHINE BLOCK vs `## C<n>` fields), no git blob reads, no sha256 pins, no control/dispatch checks. souji-freeze-check's grammar is a different section shape; both can coexist.
- `souji-shokunin/tools/souji-pre-report-gate.sh` (:6-46) — post-round gate; check #5 "The preregistration is mandatory" tests only `[[ -s $prereg ]]` on a **working-tree file**. No grammar, no rev, no digests. No duplicate.
- `souji-shokunin/tools/souji-gate-check.py` (:1-24), `souji-declared-evidence.py` (:20), `souji-receipt-run.py` (:52), `souji-record-agreement.py` (:7,40), `souji-capability-agreement.py` (:5,106), `souji-capability-cells.py` (:4,150) — G1 hits are docstring references "Frozen contract: .ufo/waves/round-NN/preregistration.txt" (the counters' own contracts). They read SCORECARD/lessons/receipts, not prereg files. No duplicate.
- `souji-shokunin/tools/souji-landing-gate.py` (:1-43) — landing consistency gate; already re-derives "frozen pins matching no committed bytes" (its defect class 2, r15) and "pinned digest" classes against `git ls-tree`/`cat-file` bytes at `--rev`. **Partial mechanism overlap** (pin→committed-bytes at a rev) but its pins come from fixture `expected.json`/report pointers, not a preregistration; no prereg grammar, no control/dispatch legs. No duplicate.
- `souji-shokunin/tools/souji-rev-pin.py` (:1-12) — durable rev resolution helper ("a resolution helper, not a verdict"). Complementary primitive; no prereg logic. No duplicate.
- souji `cand-*`/`impl-*`/`souji-*-verify*` family (53 of the 95 G2 files, e.g. `cand-a1-vault.sh:370`, `souji-vault-verify.sh:384`, `impl-06.sh:481-484`) — quarantine/obsidian-ledger `source-sha256=`/`vault-sha256=` bookkeeping receipts. Incidental digest emission; no duplication.

### 2.2 Rev-addressed preregistration readers (other lanes)
- `kama-shokunin/tools/round56-prereg-check.py` (:1-46) — reads `.ufo/waves/round-56/preregistration.json` **at `--tip` via `git show tip:path`** (same primitive as C2's "reads a preregistration at a revision"), then compares the JSON `battery.roster` to the battery file's AST `ROSTER`. Kama-specific JSON grammar, fixed path, single round; no digest pins, no `Base`-ancestor, no control-red, no dispatch check. Not a duplicate; prior art for rev-addressed prereg reads.
- `kama-shokunin/tools/round58-c1-counter.py` (:10,32), `round59-c1-counter.py` (:20), `round59-battery-outcome-check.py` (:13), `round58-battery-exec-check.py` (:43) — read the r56 preregistration.json among committed FILES at tip for their own batteries. Single-round counters.
- kama `round35…round54-*-audit.py` (~35 further G1 files) — each docstring pins "PREDICATE (same sentence in the preregistration)" and re-derives that round's committed-byte facts; none parses preregistrations generically. No duplication.
- `kaidoku-shokunin/tools/round-49/control-fixtures/pos/corpus/SOURCES.md` (:74,213) — fixture corpus prose citing the PNAS preregistration paper. Not a checker.

### 2.3 Frozen-counter/instrument digest verifiers (G2's relevant subset)
- `tabi-shokunin/scripts/check-measurement-binding.mjs` (:1-73) — **mechanically the closest sibling**. Binds each claim's counter blob `sha256` at `measuredRevision` and at tip (`counter_digest_mismatch`, `counter_changed_since_measurement`), requires `measured_revision_not_ancestor` refusal, closed finding vocabulary, exit 0/1/2. But it is manifest-driven (`corpus/evidence/round-<N>/measurement-binding.json`, tabi schema v1): the pins live in a JSON manifest the counter does not derive from any preregistration; no prereg grammar; no `DISPATCH-BEFORE-FREEZE`; no must-be-red control. Overlaps C2's COUNTER-DIGEST/BASE-NOT-ANCESTOR *mechanism*, not its contract. Not a duplicate.
- `tabi-shokunin/scripts/count-c1-round40-binding.mjs` (:1-25) — one-shot r40: hashes driver/wrapper/counter blobs at `REV` against `claims.frozenDigests` pins. Single-round, single-claim. No duplicate.
- `tabi-shokunin/scripts/check-round-contract.mjs` (:1199-1203), `check-user-round-contract.mjs` (:919-921), `check-freshness.mjs` (:110-114, PIN_MATCH sha256 pins), `check-gate-mutants.mjs` (:417) — instrument/contract witnesses with `code_sha256`/`codeRevision` binding; tabi-round-specific. No duplicate.
- fleet `.ufo/gates/root-ledgers.py` (:29-35, 294-346) — caught only by the X1 freeze-word sweep (G5/G6 negative is real but this file IS a frozen-digest checker): replays pinned revisions from `.ufo/gates/root-ledgers/expected.json`, compares blob sha256 of fleet-root `SCORECARD.md`/`LOG.md` at pinned revs (`frozen %s: %s:%s sha256 %s != pinned %s`). Same "bytes at pinned rev must equal pinned digest" primitive; pins live in expected.json (not a prereg), object is fleet ledgers. No duplicate — but it is the in-fleet precedent for digest-pinning a freeze artifact.
- `kama-shokunin/tools/citation-provenance.py` (:9-32) — verifies `cite(<rev>, <path>, sha256=<hex>)` tokens against `git cat-file` blob digests. Same blob-digest-at-rev primitive on a citation registry. No duplicate.
- `kama-shokunin/tools/gate-registry-check.py` (:1-73, 281-322) — instrument-registry gate: every tracked counter must be registered in SKILL.md tables with non-empty exit maps; its selftest fixtures pin `.ufo/waves/round-98/preregistration.json` paths. Registry-coverage gate, not a prereg validator. No duplicate.
- `kama-shokunin/tools/round40-operability-audit.py` (:7-10) — checks committed `spec.json` sha256 == pin (frozen artifact digest, single artifact). No duplicate.
- `chousa-shokunin/tools/research-gate.sh` (:229-233, 4301-4314 `GATE_PIN … gate_sha256=…`, `--drift` byte-compare) — pins and drift-checks its **own** tool's normalised output; plus `CLAIM_SOURCE_REVISION_MISMATCH` (pinned sha256 vs source bytes). Different object entirely. No duplicate.
- `mori-shokunin/tools/mori-round14-regressions.py` (:2245-2271, `frozen census sha256=… expected=…` SnapshotTampered), `mori-round15-regressions.py` (:721-724, `PINNED_FROZEN_SHA256`) — verify their own frozen census snapshot bytes. No duplicate.
- `mado-shokunin/tools/mado-evidence-audit.py` (:129-130 `snapshot_tampered`, :262-264 `expected_sha256`/`tool_sha256`), `mado-verify.sh` (:2255-2281 recorded pins) — evidence-snapshot and recorded-pin checks inside mado's own harness. No duplicate.
- `kaidoku-shokunin/tools/timestamps/run-gate-hashed.py` (:263-269), `round-33/measure_driver.py` (:604-692 classifier/spec sha refusal), `round-42/fetch-carrier.py` (:667-671) — receipt/tool/spec digest recording and refusal inside kaidoku's harness. No duplicate.
- `kaidoku-shokunin/.ufo/gates/custody-pair/custody-pair.py:830` (G10's single lane-gates hit) — prints `RECEIPT: … sha256=%s` of its own output. Incidental.
- Remaining G2 files (souji quarantine/ledger family, kumitate `counter-rerun.mjs` summary_sha256 / `report-receipt-diff.mjs`, kotodama `exercise-handoff-e2e.py` packet_sha256, tsukuroi `tsukuroi-census.sh` identity line, `check-boot-chain.py` json sha fields, tameshi witness TAMPER checks, kumitate/tabi omp-binary probes, kama `error-verdict-census.py`, chousa `assimilate-rows.py` FIXTURES_SHA256, mori/mado hostguard receipts) — digest **printing/selftest** surfaces, none validates a preregistration or a counter pin. Incidental; full per-file line refs in the G2 sweep output (greps G1/G2 with skip 0/20/40/60/80, §1).

### 2.4 Freeze-before-data
- `kotodama-shokunin/tools/harness/claims-freshness.py` (:1-53) — "Pre-dispatch claims-freshness gate … refuses a stale dispatch": re-derives each claim's `before` premise from `baseline_commit` via `git ls-tree`/`cat-file` (never the worktree). The fleet's strongest existing "freeze before data" gate — but its input is a `claims.json` contract (axis/before/before_checks), not the preregistration; it checks premise freshness, not prereg grammar, digests, controls, or dispatch-file ordering. No duplicate.
- `scripts/hyaku/lane-addendum.md:399-406` (G3-scope negative, X1 hit) — the **prose rule C2 operationalizes**: "Before freezing, build the cheapest control that skips the claimed work, score it with the frozen counter … if it meets the target, the counter or target is wrong — fix it before data" and ":512-517" frozen-and-resumed-rounds rules. Prose in the round-prompt addendum, never executable. This is what `souji-freeze-check.py` replaces with a runnable command; keeping the prose intact is required (frozen fleet scripts — never edited).
- `DISPATCH-BEFORE-FREEZE` (c2-counter.py:117-119 `dispatch_before`: `.ufo/waves/round-41/w1-dispatch.json` committed before the freeze commit must be flagged) — **no existing tool checks dispatch/wave artifacts against freeze ordering**. souji-pre-report-gate.sh is post-report only; kotodama's gate is premise-level. This leg is genuinely new.
- `templates/round-prompt.md` + `templates/agents/*` X1 hits — prose only ("frozen manual census commands", "contract freeze", "never frozen up front"). No checkers.

### 2.5 Out-of-mandate extra (X2, kotoba verifiers/)
- `kotoba-shokunin/verifiers/check_sibling_reread.py` (:29-48) — pins `BASE_CHECKER_SHA256` (sha256 of the base checker at BASE_REV, refused on drift, exit 2) and `FREEZE_SHA256` (**sha256 of the L1's freeze file** `receipts/sibling-heads-freeze.tsv`, "the L1's freeze written before any wave-1 seat ran"). Conceptually the closest existing "freeze file digest + checker digest" verifier in the fleet. Still kotoba-specific, no prereg grammar/controls/dispatch ordering. No duplicate; cite as prior art.
- `kotoba-shokunin/verifiers/check_substrate_pins.py` (:409-462 omp/cursor binary sha256+mtime pins), `fault_injection_corpus.sh:444` instrument_sha256 — substrate pin gates. Not duplicates. (Note: `verifiers/` was outside the mandated `*/tools` surface; swept anyway for coverage.)

## 3. Negative claims, each with its sweep

1. **No preregistration checker exists in fleet `scripts/` or `templates/`.** Sweep G3 (0 files), control A (9 files for `watchdog` in the same scope), X1 (8 prose/driver files for freeze wording, none a checker). Command: grep pattern=`preregistration`|`sha256=` path=`scripts;templates` case=false → "No matches found".
2. **No preregistration checker exists in fleet `.ufo/gates`.** Sweep G5 (0), G6 (0), X1 (2 files: `root-ledgers.py` + `expected.json`; `root-ledgers.py` is a ledger-digest replay, §2.3 — found only via the freeze-word sweep, reported as a hit despite the literal-pattern negative).
3. **No preregistration checker exists in lane-level `*/scripts`, `*/templates`, `*/.ufo/gates`** (G7 0 files; G9 0 files). G8's 12 and G10's 1 sha256= files are classified in §2.3 (binding witnesses kumitate/tabi; kaidoku receipt print).
4. **`tools/souji-freeze-check.py` does not exist yet anywhere in the fleet.** G1/G2 never matched such a path; in the lane, `git -C souji-shokunin ls-tree --name-only <rev> -- tools/` at **both** base 7eebc183f2685d1ea9b004b4de22c09a8a4035a7 and freeze e2a74312af4233963e44e4dbb38838ece07b8bd2 returns the identical 141-entry list (cand-*, impl-*, qrun-11.sh, souji-*.py/.sh, souji-worktree-drift.py) with **no souji-freeze-check.py** — consistent with C2's kill condition "tool absent" and the c2-counter control stubs (STUB_CLEAN/STUB_FINDINGS, c2-counter.py:65-66). Read-only `ls-tree` only; no git state was mutated.
5. **Fleet `tools/` (round-49) contains only control fixtures** (manifest.json + after.json/binaries, glob inventory) — 0 hits in G1/G2.

## 4. Commands run (as invoked)

Built-in grep tool (per harness policy) with parameters (pattern, path, case-insensitive, gitignore=false, skip): G1 `preregistration` @ `tools;*/tools` skip 0/20/40 → 55 files; G2 `sha256=` @ `tools;*/tools` skip 0/20/40/60/80 → 95 files; G3/G4 @ `scripts;templates` → 0/0; G5/G6 @ `.ufo/gates` → 0/0; G7/G8 @ `*/scripts;*/templates` → 0/12; G9/G10 @ `*/.ufo/gates` → 0/1; X1 `fr(eez|oz)` @ `scripts;templates;.ufo/gates` → 10; control A `watchdog` @ `scripts;templates` → 9; X2 @ `kotoba-shokunin/verifiers` → 0/3. Reads: `census/round-41/preregistration.txt` (full), `census/round-41/c2-counter.py:1-240`, headers/ranges of the 13 sibling files cited above. Bash: `mkdir -p /fast/scratch/hyaku/souji-r41/R41scout02` (unused, removed before yield) and the two read-only `git ls-tree` calls in §3.4. No tool was installed or upgraded (tooling authorization unused). No mutating git/jj command was run; nothing outside this report file and the seat scratch dir was written.

## 5. Bottom line for the C1..C3 builders

- C2's `souji-freeze-check.py` is **greenfield**: nothing to reconcile, no sibling to retire. Reusable prior art if wanted: kotoba's freeze-file sha256 pin (`check_sibling_reread.py:41-48`), tabi's counter-digest-at-revision classes (`check-measurement-binding.mjs:46-72`), kotodama's pre-dispatch refusal posture (`claims-freshness.py:1-9`), fleet `root-ledgers.py` replay pattern — none of which the frozen c2-counter requires or references.
- The prose rule C2 replaces lives at `scripts/hyaku/lane-addendum.md:399-406` (frozen fleet script — cite, never edit).
- Only in-lane prereg parser is `souji-axis-check.py` (different grammar); the lane already has rev-addressed blob readers (`souji-landing-gate.py`, `souji-rev-pin.py`) whose mechanics match what the counter's fixtures demand (COULD-NOT-EVALUATE on unresolved rev/absent prereg, c2-counter.py:199-206).
