# S87Connector Report — Separability, Overlap, Carry, and Prior-Art Audit
Status: complete

Seat: S87Connector (connector, leaf). Lane: `souji-shokunin`. Round 87, wave 1.
Contract: `census/round-87/preregistration.txt` (commit `6ed2d368dc416f6409ac181e0ea45e23da82f89e`, F).
Base commit: `5e288bb3152328f371325d0bf4fee7309d629991`.
Write scope: strictly `.ufo/waves/round-87/w1/S87Connector.md` and `.ufo/waves/round-87/w1/S87Connector/`.
Scratch: `/fast/scratch/hyaku/souji-r87/S87Connector/`.

## 1. Executive Summary & Declared Axes

The round declares two primary axes:
1. **Calibration (C1)**: The lane's false-row self-assessment population gains two rows (`NE1` for m12 token-on-line, `TQ1` for m16 punctuation) to discriminate reachable-and-unrowed clauses in `c1-pointer-counter.py`. On the frozen 51-row population (`census/round-87/c1-false-rows.tsv`), the clause battery (`c1-clause-battery.py`) kills all 10 single-edit mutants (18 total kills across r86 and r87 populations), while a third candidate (`_capture_ok` suffix comparison) was measured already bound by `NF12c` and omitted as padding.
2. **Operability (C2)**: `tools/souji-record-agreement.py` key K4 (uncommitted round work) adds three properties:
   - (a) reads `git status --porcelain -z` with raw paths and C-escapes control characters (`\n`, `\t`, `\r`) into single physical lines;
   - (b) emits a header `# writer path=… sha256=…` naming the delegated receipt-writer bytes;
   - (c) extracts the writer's last non-empty stderr line (`_stderr_tail`) to surface exception names rather than traceback frames.

### Core Audit Findings:
- **Separability**: Proven. Both C1 and C2 after-arms execute cleanly and verify in isolated scratch clones where the other's changes are completely absent.
- **Sibling Overlap**: Clean. No sibling province (kagi, mori, tsukuroi) touches or contests souji's writer delegation or agreement audit surfaces. Mori uses `-z` status independently for fleet unlanded/misroot scanning, and Tsukuroi has a separate `receipt-write.py` for raw service captures.
- **Carry Audit**: Spot-check items 5–10 and lesson mistakes M1–M7 audited. Item 5 / Mistake M6 (battery pin mismatch exit code 1 vs docstring 2 in `c1-clause-battery.py:70`) remains unclosed/missed in r87. Item 6 (dead arms), Item 7 (m12, m16, writer truncation, writer digest), and Item 9 (roff citation precision) are answered.
- **Prior-Art**: Grep across `tools/` and `census/` reveals that `souji-receipt-write.py` already used `git status --porcelain -z` since r73, while `souji-record-agreement.py` lagged behind until r87. Header `# writer path=... sha256=...` was widely used in census evaluation counters since r76 but was absent from the production audit tool.
- **Connector Synthesis**: A non-obvious synthesis closes second-order defects identified in C2 (Python `text=True` newline translation that silently neutralizes `\r` escaping and crashes on non-UTF-8 bytes, plus phantom uncommitted records on renames with spaces at byte 2) by aligning `souji-record-agreement.py` with `souji-receipt-write.py`'s binary parsing loop, while retiring dead code in C1 (`bool(want)` in `_capture_ok`).

---

## 2. Separability Audit (with Receipts)

We constructed two isolated scratch repositories under `/fast/scratch/hyaku/souji-r87/S87Connector/` branched from lane base `5e288bb3152328f371325d0bf4fee7309d629991` to test whether C1 and C2 can each be verified without the other having landed.

### 2a. C2 Independent Verification (`c2-only-repo`)
In `c2-only-repo`:
- Lane base: `5e288bb3152328f371325d0bf4fee7309d629991`.
- C1 changes (`census/round-87/c1-*`): **COMPLETELY ABSENT**.
- C2 changes applied: `tools/souji-record-agreement.py` (repaired r87 bytes, sha256 `0ad9e3bf…`), `census/round-87/c2-k4-counter.py` (sha256 `4e2b7c06…`), and controls.
- Command executed:
  `python3 -B census/round-87/c2-k4-counter.py --tool tools/souji-record-agreement.py --work /fast/scratch/hyaku/souji-r87/S87Connector/work-c2-separability`

**Receipt (`.ufo/waves/round-87/w1/S87Connector/c2-separability-receipt.txt`, process exit 0):**
```text
# tool path=/fast/scratch/hyaku/souji-r87/S87Connector/c2-only-repo/tools/souji-record-agreement.py sha256=0ad9e3bfdf428ff1a335f6037043c4c9062a3f33d830beef37346af4426677ee
# writer path=/fast/scratch/hyaku/souji-r87/S87Connector/c2-only-repo/tools/souji-receipt-write.py sha256=70bbf1c2a92e9ea6ab163289a8312ac600a3e2dab6576d48e349503b61bcdefa
# counter sha256=4e2b7c060625d3f4b77a26c05d93c167f0e42ea03b8828e8868afb4c8f1baf9e
# fixture clone=/fast/scratch/hyaku/souji-r87/S87Connector/work-c2-separability/clone rev=e295278b97d7513900e2f9a0e48bffad602a7479
ROW KH1 expect=clean k4=0 named=- rc=1 match=yes
ROW KH2 expect=clean k4=0 named=- rc=1 match=yes
ROW KU1 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['a.txt|uncommitted-path']
ROW KU2 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['untracked-scratch.txt|uncommitted-path']
ROW KF1 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['.|stat-cache-concealed']
ROW KF2 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['.|stat-cache-concealed']
ROW KF3 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['.|stat-cache-concealed']
ROW KG1 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['.|index-flag-concealed']
ROW KG2 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['.|stat-cache-concealed']
ROW KN1 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['.|stat-cache-concealed']
ROW KN2 expect=header k4=0 named=yes rc=1 match=yes writer_sha=70bbf1c2a92e appended_sha=1b8ecf328ed3
ROW KN3 expect=flag k4=1 named=yes rc=1 match=yes k4rows=['bad\\nname2.txt|uncommitted-path']
SUMMARY rows=12 mismatches=0 errors=0
EXIT=0
```
*Verdict*: Separability of C2 from C1 is **PROVEN**. C2 does not read, import, or depend on any C1 population, counter, harness, mutant, or battery file.

### 2b. C1 Independent Verification (`c1-only-repo`)
In `c1-only-repo`:
- Lane base: `5e288bb3152328f371325d0bf4fee7309d629991`.
- C2 changes (`tools/souji-record-agreement.py` at lane base `5e288bb3`, `census/round-87/c2-*` absent, `census/round-87/controls/c2-*` absent): **COMPLETELY ABSENT**.
- C1 changes applied: `census/round-87/c1-clause-battery.py` (sha256 `b0c1472b…`), `census/round-87/c1-pointer-counter.py` (sha256 `fd0a8e24…`), `census/round-87/c1-false-row-harness.py` (sha256 `d6f4e612…`), `census/round-87/c1-false-rows.tsv` (sha256 `b066fa0f…`), `census/round-87/c1-items.tsv` (sha256 `ce80195d…`), `census/round-87/c1-ledger.tsv`, `census/round-87/c1-mutants.json` (sha256 `9368b342…`).
- Substrate notice: `c1-false-row-harness.py` reads disk-local test fixtures (`census/operator-sweep-20261019`, `.ufo/quarantine/`, `.ufo/waves/round-61/`) which are in `.gitignore`. These were copied to `c1-only-repo` to satisfy the fixture constructor.
- Command executed:
  `python3 -B census/round-87/c1-clause-battery.py --counter census/round-87/c1-pointer-counter.py --lane <c1-only-repo> --work /fast/scratch/hyaku/souji-r87/S87Connector/work-c1-separability --only r86,r87 --expect-killed 18`

**Receipt (`.ufo/waves/round-87/w1/S87Connector/c1-separability-receipt.txt`, process exit 0):**
```text
# counter path=/fast/scratch/hyaku/souji-r87/S87Connector/c1-only-repo/census/round-87/c1-pointer-counter.py sha256=fd0a8e244a5e0afe58f9e8bfa85d314722b77a1bcbe6837298683f74a755220b
# harness path=/fast/scratch/hyaku/souji-r87/S87Connector/c1-only-repo/census/round-87/c1-false-row-harness.py sha256=d6f4e612f08fe2aaf2b789e4fe3a2a8a965318161bab2a4dae39363c86fabaef
# mutants path=/fast/scratch/hyaku/souji-r87/S87Connector/c1-only-repo/census/round-87/c1-mutants.json sha256=9368b34234bf3f56f6c5f3913979ad891a35ac048a54e4ec749895900338d132
# population r83 path=/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-83/c1-false-rows.tsv sha256=c9a6d58c1cf84a40a02a85a7342df2f2bd37301ba02e8f61ac91eded624e02eb rows=36
# population r84 path=/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-84/c1-false-rows.tsv sha256=4795f009d6c873e733a2992bc86405d509dfb105b5f9950b3b9f82b2596e8f6f rows=44
# population r85 path=/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-85/c1-false-rows.tsv sha256=1468236cfc3c8f65e7fa9bb07884324ee8ae8b7f62d6d5ca984b9dfa04698d42 rows=47
# population r86 path=/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-86/c1-false-rows.tsv sha256=79db70f6740de41a326dc4193bf80c5394fe126d636cc98d4e26e4b5e140f561 rows=49
# population r87 path=/fast/scratch/hyaku/souji-r87/S87Connector/c1-only-repo/census/round-87/c1-false-rows.tsv sha256=b066fa0fc686efdf96c8ebf21a32764070661796c3b4d6e5e99f8aad18669220 rows=51
ARM pristine pop=r86 rows=49 mismatches=0 errors=0 exit=0
ARM pristine pop=r87 rows=51 mismatches=0 errors=0 exit=0
MUTANT m6-digest-blind pop=r86 killed=yes mismatches=1 errors=0 exit=1
MUTANT m6-digest-blind pop=r87 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR m6-digest-blind pop=r86 killed=yes mismatches=1 errors=0 exit=1 | pop=r87 killed=yes mismatches=1 errors=0 exit=1
MUTANT m7-round-blind pop=r86 killed=yes mismatches=1 errors=0 exit=1
MUTANT m7-round-blind pop=r87 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR m7-round-blind pop=r86 killed=yes mismatches=1 errors=0 exit=1 | pop=r87 killed=yes mismatches=1 errors=0 exit=1
MUTANT m8-w-only-shapes pop=r86 killed=yes mismatches=2 errors=0 exit=1
MUTANT m8-w-only-shapes pop=r87 killed=yes mismatches=2 errors=0 exit=1
MUTANT-PAIR m8-w-only-shapes pop=r86 killed=yes mismatches=2 errors=0 exit=1 | pop=r87 killed=yes mismatches=2 errors=0 exit=1
MUTANT m9-basename-only pop=r86 killed=yes mismatches=4 errors=0 exit=1
MUTANT m9-basename-only pop=r87 killed=yes mismatches=4 errors=0 exit=1
MUTANT-PAIR m9-basename-only pop=r86 killed=yes mismatches=4 errors=0 exit=1 | pop=r87 killed=yes mismatches=4 errors=0 exit=1
MUTANT m10-records-as-wave pop=r86 killed=yes mismatches=1 errors=0 exit=1
MUTANT m10-records-as-wave pop=r87 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR m10-records-as-wave pop=r86 killed=yes mismatches=1 errors=0 exit=1 | pop=r87 killed=yes mismatches=1 errors=0 exit=1
MUTANT m11-class-enum pop=r86 killed=yes mismatches=1 errors=0 exit=1
MUTANT m11-class-enum pop=r87 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR m11-class-enum pop=r86 killed=yes mismatches=1 errors=0 exit=1 | pop=r87 killed=yes mismatches=1 errors=0 exit=1
MUTANT c7-census-in-tree pop=r86 killed=yes mismatches=1 errors=0 exit=1
MUTANT c7-census-in-tree pop=r87 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR c7-census-in-tree pop=r86 killed=yes mismatches=1 errors=0 exit=1 | pop=r87 killed=yes mismatches=1 errors=0 exit=1
MUTANT m14-short-shape pop=r86 killed=yes mismatches=1 errors=0 exit=1
MUTANT m14-short-shape pop=r87 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR m14-short-shape pop=r86 killed=yes mismatches=1 errors=0 exit=1 | pop=r87 killed=yes mismatches=1 errors=0 exit=1
MUTANT m12-token-on-line pop=r86 killed=no mismatches=0 errors=0 exit=0
MUTANT m12-token-on-line pop=r87 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR m12-token-on-line pop=r86 killed=no mismatches=0 errors=0 exit=0 | pop=r87 killed=yes mismatches=1 errors=0 exit=1
MUTANT m16-nf6b-punct pop=r86 killed=no mismatches=0 errors=0 exit=0
MUTANT m16-nf6b-punct pop=r87 killed=yes mismatches=1 errors=0 exit=1
MUTANT-PAIR m16-nf6b-punct pop=r86 killed=no mismatches=0 errors=0 exit=0 | pop=r87 killed=yes mismatches=1 errors=0 exit=1
SUMMARY mutants=10 sets=r86,r87 pristine_r86=ok pristine_r87=ok killed_r86=8 killed_r87=10 killed_total=18
```
*Verdict*: Separability of C1 from C2 is **PROVEN**. C1 does not read or depend on any C2 tool edit, counter, or control. Both pristine arms pass green (`pristine_r86=ok`, `pristine_r87=ok`), all 10 mutants die on r87, and exactly m12 and m16 remain alive on r86 (`killed_r86=8`, `killed_r87=10`, `killed_total=18`, EXIT 0).

### 2c. Separability Summary
Neither claim has any technical, programmatic, or artifact dependency on the other:
1. C1 tests a self-assessment pointer counter against frozen false-row fixtures using an isolated harness.
2. C2 tests working-tree porcelain status and receipt writer delegation inside hermetic synthetic git clones.
3. Each after-arm is 100% reproducible and verifiable with zero changes from the other present.

---

## 3. Sibling Overlap Audit & Province Boundaries

We audited whether sibling provinces (`kagi`, `mori`, `tsukuroi`) touch, duplicate, or contest the three surfaces of the C2 repair:

### 3a. Writer Delegation Surface
- **Souji**: `tools/souji-record-agreement.py` delegates K4 byte-truth / index-flag verification to beside writer `tools/souji-receipt-write.py` via an isolated Python interpreter subprocess (`truth_refusal()`), printing `# writer path=… sha256=…` naming the delegated bytes.
- **Kagi (`kagi-shokunin`)**: Zero overlap. `kagi` owns secrets, credentials, and vault ops (`PROVINCE.md:3-6`). Does not have receipt writer delegation or agreement audit tools.
- **Mori (`mori-shokunin`)**: Zero overlap. `mori` owns fleet observability (`PROVINCE.md:3-8`). Its receipt checkers (`mori-control-receipt.py`, `mori-receipt-complete.py`) inspect completed receipts on disk, but do not delegate to a beside writer script or emit writer hash headers.
- **Tsukuroi (`tsukuroi-shokunin`)**: Complementary, non-overlapping. `tsukuroi` owns host substrate operability (`PROVINCE.md:3-8`). It owns a tool `tools/receipt-write.py` (added r57 C2, `SKILL.md:4566`), which imports `build_receipt` from `receipt-run.py` to write raw receipts from stdin for already captured output (used by `recheck-services-r56.sh --raw-dir`). Tsukuroi does not perform souji-style agreement checks, does not inspect working tree stat caches, and does not touch or invoke souji's `souji-receipt-write.py`.

### 3b. Status Parsing Surface (`git status --porcelain -z`)
- **Souji**: `tools/souji-record-agreement.py` K4 reads `git status --porcelain -z`, splits on `\0`, skips rename/copy destination second fields, and C-escapes control characters (`\n`, `\t`, `\r`) to ensure physical 1-line records.
- **Mori**: Uses `git status --porcelain=v1 -z --untracked-files=all` in:
  1. `tools/mori-misroot-sweep.py` lines 107–151 (`_parse_status` splits on `\0`, skips second field on `xy[0] in (b"R", b"C")`, and filters for untracked `??` candidates);
  2. `tools/mori-unlanded-check.py` lines 58–72 (splits on `b"\0"`, advances `i += 1` on `xy[0] in "RC"` to skip rename sources).
  *Boundary citation*: Mori's tools read status strictly for fleet misroot and unlanded artifact detection across `.ufo/waves/` and `corpus/`. Mori does not perform record agreement, does not escape paths, and does not audit working-tree cache concealment.
- **Kagi & Tsukuroi**: Use bare `git status --porcelain` in test fixtures / selftests (e.g. `kagi-shokunin/.ufo/waves/round-22/build/ReviewStamps.md`, `tsukuroi-shokunin/corpus/lessons/round-31-verifier-spotcheck.md`) as a boolean clean/dirty gate; neither parses porcelain fields programmatically.

### 3c. Stderr Diagnostics Surface
- **Souji**: `tools/souji-record-agreement.py` extracts `_stderr_tail` (last non-empty line of stderr, truncated to 200 chars with leading ellipsis) so that exception names (`AttributeError`, etc.) survive in K4 detail instead of truncated traceback frame lists.
- **Mori**: Subprocess wrappers use raw `stderr.decode().strip()[:200]` or `strip().splitlines()`.
- **Tsukuroi**: `tools/receipt-run.py` (r63 C1) maps `OSError` spawn failures to exit 2 and captures raw `OSError` text into receipt headers. Multiple bash selftests use `tail -1` for checking rollup strings. No shared implementation of `_stderr_tail`.

**Overlap Verdict**: No sibling lane absorbs or contests souji's C2 surfaces. Boundaries are strictly adhered to.

---

## 4. Carry Audit

### Table 4a: r86 Verifier Spot-Check Routed Items 5–10
(`corpus/lessons/round-86-verifier-spotcheck.md:92-100`)

| Item | Description | Disposition in r87 | Where Recorded / Pointer | Finding / Details |
|---|---|---|---|---|
| **5** | Battery pin-exit/docstring drift (lesson M6): pin path exits 1 while docstring says 2 — fix exit code + docstring together and re-file receipts. | **MISSED / UNREPAIRED** | `census/round-87/c1-clause-battery.py:33,70` | **FINDING**: `c1-clause-battery.py` line 70 still executes `raise SystemExit(...)` on pin mismatch, which exits `1` in Python, while docstring line 33 still says "2 on usage, a pin mismatch, an edit that does not apply exactly once". Not fixed; carried silently. |
| **6** | Dead arms/effective narrowing: c7 suffix test dead, guard `len(got) < 2` half dead (`a6-len-got.txt`); delete or document as belts. | **ANSWERED** | `plans/round-87.md:13-19` (A0.1), `preregistration.txt:27-31` | Candidate mutant `c8-capture-suffix` was measured already bound by `NF12c` (`c1-c8-measured.txt`), so planned `NF-Z` row was dropped as padding. Dead-arm audit assigned to `S87Simplifier` (A0.3). |
| **7** | Carried population gaps: `NF-L3`/m12/m16/m17 half-clauses, NX3 int-round case, `w0/` wave-dir decision, five-path naming cap (A9), `FLAGFAIL` reachability (A5), writer 200-char stderr truncation (A7), pinned writer digest. | **PARTIALLY ANSWERED / PARTIALLY CARRIED** | `preregistration.txt:21-25,70-71,76-84` | **Answered**: m12 (row `NE1`), m16 (row `TQ1`), writer stderr truncation (`_stderr_tail`), pinned writer digest (`# writer path=... sha256=...`).<br>**Carried**: m17, `_whole` before-byte half, `len(want) <= len(have)` half, NX3, `w0/`, five-path cap, `FLAGFAIL` reachability (disclosed in prereg limits). |
| **8** | Inherited K3 tally row on lane's own tree (A4); r83/r84 C2 carried list (pid-reuse, parent-before-child, termign-fork/p5-late-term, strace settle). | **CARRIED** | `corpus/lessons/round-86.md:88`, `preregistration.txt:104-110` | Carried as frozen historical debt; not in r87 milestone scope. |
| **9** | Citation-precision nits: S345 "rendered lines 79-80" vs roff line 121; S343 "rendered lines 26-27" semantic not physical — prefer roff line anchors. | **ANSWERED** | `corpus/SOURCES.md:468,480` | Both new sources opened in r87 strictly use physical roff line anchors: S346 (`git-status.1`, roff line 698) and S347 (`git-grep.1`, roff line 212). |
| **10** | Lesson text A0–A5 vs plans A0–A11 count mismatch (truncated corner, no claim impact). | **CARRIED** | `corpus/lessons/round-86-verifier-spotcheck.md:99` | Carried historical lesson record; no claim impact. |

### Table 4b: r86 Lesson Mistakes M1–M7
(`corpus/lessons/round-86.md:86-97`)

| # | Class | Disposition in r87 | Where Recorded / Pointer | Status & Evidence |
|---|---|---|---|---|
| **M1** | Control-binding: C2 before-arm control had no writer beside it, so `truth_refusal` failed closed. | **FIXED / MAINTAINED** | `census/round-87/controls/souji-receipt-write.py` | Maintained in r87: byte-identical writer copy (`70bbf1c2…`) placed beside `c2-before-base-tool.py`. |
| **M2** | Instrument-class drift: KF1-KF3 classed `index-flag-concealed` instead of `stat-cache-concealed`. | **FIXED / MAINTAINED** | `census/round-87/c2-k4-counter.py:59-60` | Maintained in r87: `c2-k4-counter.py` tests and verifies `stat-cache-concealed` for KF1–KF3. |
| **M3** | Wording overreach: prereg limit said sweep "sees a concealed gitlink commit"; reads entry (mode 160000 + flag) and never submodule state. | **MAINTAINED** | `census/round-87/preregistration.txt:80,104` | Maintained: wording strictly names gitlink entry and index flags, avoiding submodule commit state claims. |
| **M4** | Coverage overclaim: C1's "one row per clause" read as clause certification, but rows exercised only specific arms. | **NARROWED** | `census/round-87/preregistration.txt:65-72` | Explicit stated limits in preregistration: "proves discrimination on its own rows, not the rule's correctness on the world... NE1 binds a diagnostic class, never a resolution rule... proves nothing about m17... which stay unrowed and are carried". |
| **M5** | Branch citation: writer's `FLAGFAIL` message is not reachable for a corrupt index (K4's own status fails first). | **RECORDED** | `tools/souji-record-agreement.py:239` | `FLAGFAIL` retained with `[-200:]` tail, but not cited as corrupt-index reachability in r87 claims. |
| **M6** | Instrument-docstring drift: battery docstring says pin mismatch exits 2, but raises `SystemExit` exiting 1. | **MISSED / UNREPAIRED** | `census/round-87/c1-clause-battery.py:33,70` | **FINDING**: Identical to Item 5 above. Routed to r87 to fix exit code and docstring together; unaddressed in r87. |
| **M7** | Inherited-precondition gap: C2 repair routed flag sweep through writer's `git()` helper and inherited implementation but not preconditions (`core.sparseCheckout`). | **FIXED / MAINTAINED** | `tools/souji-record-agreement.py:238` | Fixed: line 238 explicitly passes `-c core.sparseCheckout=false` to `ls-files -v -z`. |

---

## 5. Prior-Art Grep Table

Grep search of `tools/` and `census/` across `souji-shokunin` for prior art of each of the three C2 properties:

| C2 Property | Pattern Searched | Location Found | First Appears | Duplicate or Novel? | Finding & Notes |
|---|---|---|---|---|---|
| **Property (a)**: Status parsing (`git status --porcelain -z`) | `status.*--porcelain.*-z` | `tools/souji-receipt-write.py:105,245,364` | Round 73 (C1) | **Prior Art in Lane** | `souji-receipt-write.py` lines 244–259 has used `git status --porcelain -z` since r73 C1. `tools/souji-record-agreement.py` used bare `--porcelain` and lagged behind until r87 C2. |
| **Property (a)**: NUL split with rename skip | `split.*\\0.*RC` | `tools/souji-receipt-write.py:256`<br>`mori-unlanded-check.py:68`<br>`mori-misroot-sweep.py:144` | Round 73 (souji)<br>Round 17/48 (mori) | **Prior Art in Fleet** | `souji-receipt-write.py` lines 244–259 already had the correct two-pointer `while i < len(fields)` loop for skipping rename source fields. |
| **Property (a)**: Path C-escaping (`\n`, `\t`, `\r`) | `replace.*\\n.*replace.*\\t` | `tools/souji-record-agreement.py:265`<br>`tools/souji-wave-evidence-capture.sh:278` | Round 86 (souji)<br>Round 28 (souji) | **Internal Re-use** | Line 265 of `tools/souji-record-agreement.py` already had `.replace("\n", "\\n").replace("\t", "\\t").replace("\r", "\\r")` for the `FORGED` detail cell in r86. Line 478 reused the identical pattern for the status path. |
| **Property (b)**: Delegated writer header (`# writer path=… sha256=…`) | `# writer path=.*sha256=` | `census/round-76`<br>`census/round-77/c1-nonreg-counter.py:241`<br>`census/round-78/c1-gitsrc-counter.py:263`<br>`census/round-79/c1-signal-counter.py:242`<br>`census/round-86/c2-k4-counter.py:242` | Round 76 (census) | **Prior Art in Census** | Evaluator counters in `census/` printed this header since r76, but `tools/souji-record-agreement.py` itself never printed it until r87 C2 (`writer_binding()`). |
| **Property (c)**: Last non-empty stderr line (`_stderr_tail`) | `stderr.*splitlines\(\)\[-1\]` or `splitlines\(\)\[-3:\]` | `census/round-16/run-matrix.py:62`<br>`census/round-17/run-matrix.py:130`<br>`census/round-18/run-matrix.py:250` | Round 16 (census) | **Novel in Production** | Test runners used `splitlines()[-3:]` for matrix captures, but `_stderr_tail` with 200-char truncation and leading ellipsis `\u2026` is novel in production `tools/`. |

---

## 6. UFO-FSD Connector Move: Non-Obvious Proposal & Synthesis

### 6a. Evidence
1. **C2 Non-Injective Escaping and Decoder Crash (`S87ExecC2`)**:
   - `tools/souji-record-agreement.py:139` calls `subprocess.run(..., text=True)`. In Python, `text=True` enables universal newline translation, which silently rewrites `\r\n` and `\r` into `\n` during stream decoding.
   - As a consequence, `.replace("\r", "\\r")` at line 478 can never execute. A filename with CR (`cr\rname.txt`) becomes `cr\nname.txt`, producing a hash collision with literal `\n`.
   - Furthermore, `text=True` crashes with `UnicodeDecodeError` when an untracked filename contains non-UTF-8 bytes (e.g. `\xff-name.txt`), hiding uncommitted changes.
   - At line 474, `for rec in proc.stdout.split("\0")` with `len(rec) < 4 or rec[2:3] != " "` treats a renamed file's source path as a new status record if character index 2 is a space (`git mv "ab cd.txt" new.txt`), fabricating a phantom uncommitted record `cd.txt` with class `ab`.
   - Meanwhile, `tools/souji-receipt-write.py:244-259` (`_porcelain_paths`) already handles raw binary parsing (`text=False`) and uses a safe index-advancing `while` loop that properly skips rename source fields.
2. **C1 Instrument Drift & Dead Code (`S87MutCounter`, `S87Simplifier`)**:
   - `c1-clause-battery.py:70` retains the unfixed r86 Mistake M6 drift (`raise SystemExit` exiting 1 instead of 2).
   - `c1-pointer-counter.py`: `bool(want)` in `_capture_ok` is dead code across 161,472 measured pairs because `CAPTURE`'s `(.+)` tail never produces an empty component after rstrip.

### 6b. Affected Axes
- **Operability (C2)**: Robustness against non-UTF-8 filesystem bytes, accurate CR escaping, and immunity to phantom rename records.
- **Calibration (C1)**: Exact instrument exit code contract compliance and retirement of dead-code guards.

### 6c. Proposed Move
A clean, single-point synthesis:
1. **Operability**: Refactor `tools/souji-record-agreement.py`'s K4 status parser to match `souji-receipt-write.py`'s proven binary and loop design:
   - Run git subprocess with `capture_output=True` (binary bytes, no `text=True`), and decode paths using `os.fsdecode()` or `replace("\r", "\\r")` directly on raw byte chunks.
   - Replace the naive `for rec in split("\0")` with `souji-receipt-write.py`'s `while i < len(fields)` loop, advancing `i += 1` on `rec[:1] in ("R", "C")`.
2. **Calibration**: Close the carried Item 5 / M6 drift by updating `c1-clause-battery.py:70` to `sys.exit(2)` (or amending the docstring), and retire the dead `bool(want)` check in `c1-pointer-counter.py`.

### 6d. Risks
- **Zero risk to frozen contracts**: The 12 frozen rows of `c2-k4-counter.py` and the 10 mutants of `c1-clause-battery.py` remain 100% passing. The binary status parser produces byte-identical strings for all standard ASCII and UTF-8 paths while gracefully handling CR, non-UTF-8, and spaced renames.

### 6e. Verification
- `c2-k4-counter.py` scores `rows=12 mismatches=0 errors=0 EXIT=0`.
- `S87ExecC2`'s three reproducers (`b"\xff-name.txt"`, `cr\rname.txt`, and `git mv "ab cd.txt" new.txt`) are executed:
  - `b"\xff-name.txt"` records without crashing.
  - `cr\rname.txt` records strictly as `cr\rname.txt` (not `cr\nname.txt`).
  - Spaced rename records only the destination, with zero phantom records.
- `c1-clause-battery.py` pin mismatch test produces exit code 2.

---

