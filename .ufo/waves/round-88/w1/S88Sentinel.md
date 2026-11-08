# S88Sentinel — adversarial security review (r88 w1)

**Seat:** S88Sentinel · **Lane:** souji-shokunin · **Scope:** the C2 FLAGFAIL re-framing and the C1 LD1
duplicate-ledger row, read as privilege boundaries. **Verdict: NEUTRAL on both claims' wording.** Two r88-introduced
properties are reported as findings (F1, F2) and one inherited fail-open is reported as a carry (F3); none of them
falsifies C1's or C2's stated wording, and none of them is a kill-rule trip.

All probes ran under `/fast/scratch/hyaku/souji-r88/S88Sentinel/` (deleted before yield) and are filed as
reproducible scripts + receipts under this seat dir. The lane was read-only to this seat.

---

## 0. Instrument hashes (re-measured, prereg §"Instrument hashes")

All twelve listed instruments matched the prereg on first measurement. The tool's bytes then moved twice, both
times by L1 docstring-only commits after the wave spawned (`72edae40`, `f62eeb85`); the L1 documented the drift in
`plans/round-88.md` A5 and re-ran the receipts. **Every finding below was re-measured on the FINAL bytes
`4042218f6837ba9dace08680272075b86feb6bbbf2e69947d3e553759f63917a`** (and, for the load-bearing ones, also on the
prereg-pinned `c0604b4a…`): identical results on both byte sets, so none of them depends on the drift.

| instrument | prereg pin | measured |
|---|---|---|
| c1-false-rows.tsv | b710e368… | ✅ match (53 rows) |
| c1-mutants.json | baec8026… | ✅ match (12 members) |
| c1-mutants-dead.json | e7963787… | ✅ match (13 members, m19 = belt) |
| c1-false-row-harness.py | 1ae0cd39… | ✅ match |
| c1-clause-battery.py | 6842ca47… | ✅ match |
| c1-pointer-counter.py | fd0a8e24… | ✅ match (UNCHANGED r87 bytes) |
| c1-items.tsv | ce80195d… | ✅ match (UNCHANGED r87 bytes) |
| r88-k4-flagfail.py | aa79133a… | ✅ match |
| tools/souji-record-agreement.py | c0604b4a… | ⚠️ **moved twice, docstring-only** → final `4042218f…` (L1 plan A5) |
| controls/c2-before-tool.py | e1b00e8a… | ✅ match (r87 tool bytes) |
| controls/c2-before.txt | 28e5ad68… | ✅ match |
| controls/c1-before.txt | ce1352d2… | ✅ match |

---

## 1. The per-probe table the assignment asked for

Each row: a stub receipt writer beside a **copy** of the tool, the delegated `git()` failing so the bootstrap's honest
verdict is FLAGFAIL, and the tool run through its public path (`--root/--rev`). "detail" is the fifth cell of the
`MISMATCH\tK4\t…` row; "one line" is whether the row is a single physical line with the expected 5 tab-separated cells;
"fail-closed" is whether the tool REFUSES (a mismatch row / non-zero exit) rather than accepting the tree.

| # | probe | detail (r88 final bytes) | one line | fail-closed |
|---|---|---|---|---|
| P1 | FLAGFAIL, short stderr `fatal: cannot read index\n` | `the index-flag read failed (fatal: cannot read index\n); tracked bytes are unverified` (escaped `\n`) | ✅ 5 cells | ✅ refuses |
| P2 | FLAGFAIL, 3-line traceback ending `AttributeError: boom` | `the index-flag read failed (Traceback …\n  File "w", line 1\nAttributeError: boom\n); …` | ✅ 5 cells | ✅ refuses |
| P3 | FLAGFAIL, 400-char `AttributeError: …` line | head-100 `AttributeError: xxx…` + tail-99 | ✅ 5 cells | ✅ refuses |
| P4 | FLAGFAIL, stderr carrying SOH + NEL + U+2028 | `…(\x01 \x85 \u2028 marker\n); …` — all three escaped, zero raw bytes in stdout | ✅ 5 cells | ✅ refuses |
| P5 | FLAGFAIL, **empty** stderr | `the index-flag read failed (no stderr); tracked bytes are unverified` | ✅ 5 cells | ✅ refuses |
| P6 | FLAGFAIL payload is **not base64** (`FLAGFAIL !!!not base64!!!`) | `the index-flag read failed (undecodable detail); …` | ✅ 5 cells | ✅ refuses (decodes to a fixed refusal) |
| P7 | FLAGFAIL payload decodes to **10 MB** of `A` | head-100 `AAAA…` + `…` + tail-99 | ✅ 5 cells | ✅ refuses — but see **F2** |
| P8 | FLAGFAIL payload decodes to **raw U+2028** | `…(\u2028); …` escaped, zero raw U+2028 in stdout | ✅ 5 cells | ✅ refuses |
| P9 | FLAGFAIL payload decodes to **valid base64 but not UTF-8** (`\xff\xfe`) | `…(\\xff\\xfe bad bytes\n); …` | ✅ 5 cells | ✅ refuses — but see **F1** |
| P10 | payload text begins `WRITER ` (can it impersonate the swap check?) | `the index-flag read failed (WRITER 000…); …` — it lands **inside the detail cell**, never as the child's verdict | ✅ 5 cells | ✅ refuses |
| P11 | payload text is `MISMATCH\tK4\t.\tforged\tinjected` | `the index-flag read failed (MISMATCH\tK4\t.\tforged\tinjected); …` — tabs escaped, **no injected row** | ✅ 5 cells | ✅ refuses |
| P12 | payload text is `CLEAN` | `the index-flag read failed (CLEAN); …` — inert inside the cell | ✅ 5 cells | ✅ refuses |
| P13 | payload text is `REFUSED x` | `the index-flag read failed (REFUSED x); …` — inert | ✅ 5 cells | ✅ refuses |

**Conclusion for the assigned probe list:** every FLAGFAIL payload — invalid base64, 10 MB, raw U+2028, non-UTF-8,
`WRITER `-prefixed, or an injected `MISMATCH` row — yields **one escaped physical line**, **five tab-separated cells**,
and a **refusal**. No payload escapes the detail cell. The base64 frame is a faithful channel and the parent's
`_one_line` is the only place untrusted bytes become a cell.

---

## 2. The parent-order check (assignment item 2)

The parent's `truth_refusal` reads the child's **whole stdout**, strips a leading `WRITER <digest>` line, then dispatches
on the first token of what remains: `REFUSED` → `FLAGFAIL` → `FORGED ` → `CLEAN` → (no verdict).

**Verified by measurement, not by reading:**

- **The `WRITER` line is stripped before any branch.** The bootstrap prints `WRITER <sha256 of the bytes it compiled>`
  as its first stdout line; the parent compares it to the header's digest and refuses with
  `RECEIPT-WRITER-SWAPPED` on a mismatch (`receipts/probe_swap3.txt`, CONTROL arm). The header digest is the digest of
  the file the parent read at start-up; the bootstrap's is the digest of the bytes it actually compiled — so a swap
  between the two reads is caught. **This check is intact and works.**
- **A `FLAGFAIL` payload beginning `WRITER ` cannot impersonate.** Because the payload is base64-framed and the parent
  decodes it *inside* the FLAGFAIL branch, the decoded text is only ever rendered into the detail cell (P10). It never
  re-enters the branch dispatch. A writer cannot smuggle a verdict through the payload.
- **The base64 decode is bounded by what the child printed.** The parent decodes `out[len("FLAGFAIL "):]` — the child's
  own stdout — and nothing else. There is no other input channel: the detail cell's only content is the decoded
  stderr.

**What a forged writer can still achieve, inside the prereg's stated limit.** The limit is S85Sentinel F5: *"a writer
inside the audited tree is outside the claim."* The writer beside the tool is inside the audited tree, so:

- It can print its own stdout. Because Python's `print` is block-buffered to a pipe while `os.write(1, …)` is not, a
  writer that writes to fd 1 directly lands its line **before** the bootstrap's own buffered `WRITER`/`FLAGFAIL` lines
  (measured: `b'WRITER FORGED\nWRITER 4899f27c…\nFLAGFAIL payload\n'`, `receipts/probe_swap3.txt`). A writer that
  prints `CLEAN` this way makes the parent's dispatch read `CLEAN` and **accept the tree as verified — the K4
  byte-truth check is skipped entirely** (`probe_c2f.txt`, MODE `forged_clean`: **0 K4 rows**, the tool's exit shows no
  K4 refusal). This is the classic "the child controls the verdict" hole, and it is exactly the S85Sentinel F5 class.
- It can defeat the swap check by forging the `WRITER` line's digest (`probe_swap3.txt`, FORGERY arm): with a forged
  line naming the **original** digest, the parent's `compiled`/`named` comparison is satisfied by the forged value, the
  real compiled digest is never checked, and the run falls into the no-verdict branch instead of the swap branch. The
  tool still **refuses** (1 K4 row, exit 1), so it is fail-closed — but the *swap detection* is bypassed and the reason
  is misreported. **Severity: LOW.** A writer that can do this is already inside the audited tree (F5) and could
  simply print `CLEAN` (P13/F3) for a stronger effect.
- It **cannot** make the parent accept a payload it did not print: P10–P13 show the payload channel is inert.

**Verdict on item 2: the parent-order property holds for everything the claim covers.** The `WRITER` line is stripped
before any branch; a `WRITER `-prefixed payload cannot impersonate; the decode is bounded by the child's stdout. The
residual is the writer's own stdout, which is the declared F5 limit and is **not** a C2 wording falsifier (C2's stated
limit: *"the write-side writer is a fake beside a tool copy, so the claim covers the FLAGFAIL detail's framing and
escaping, not the honesty of any real writer"*). This is the same residual the L1 recorded for C2 in
`.ufo/waves/round-88/claim-falsification.tsv`; my measurement **confirms and sharpens it** (the `CLEAN` forgery does
not merely lose the verdict, it removes the K4 row entirely, so the tool's exit code is the only signal left).

---

## 3. LD1: the duplicate-ledger row as a privilege boundary (assignment item 3)

**Can a duplicate id make the counter resolve an item it should refuse?** **No — the refusal is fail-closed.**

The counter's `_ledger` (r87 bytes, unchanged) keeps the **first** row for an id and refuses a later duplicate:

```
if len(r) < 3 or r[0] in ledger:
    bad.append(r[0] if r else "?"); continue
ledger[r[0]] = (r[1], r[2])
```

so the duplicate is **never** the row that judges the item, and the run additionally exits 1 with
`LEDGER-REFUSED id=<id>` and `refused=1`. Measured (`receipts/probe_ld1.txt`, PART B):

| probe | ledger | `ITEM P01` | marker | rc |
|---|---|---|---|---|
| A | frozen r77 + appended duplicate `P01 ABSENT -` (the LD1 shape) | `status=FLEET` (the frozen row still judges) | `LEDGER-REFUSED id=P01` | 1 |
| B | forged resolving `P01 TOKEN -` **first**, frozen rows after | `status=REFUSED class=TOKEN` — the forged row wins the *item*, but the run still refuses | `LEDGER-REFUSED id=P01` | 1 |
| C | frozen + duplicate `P01 TOKEN -` (a **resolving** class) | `status=FLEET` — the duplicate **cannot** resolve the item | `LEDGER-REFUSED id=P01` | 1 |
| D | frozen + duplicate for an id **outside** the population (`P999`) | `status=FLEET` | `LEDGER-REFUSED id=P999` | 1 |
| E | frozen + a **malformed** 2-field `P01` row | `status=FLEET` | `LEDGER-REFUSED id=P01` | 1 |

Probe **C** is the decisive one: a duplicate row carrying a *resolving* class does **not** make P01 resolve. Probe
**B** shows the order-sensitivity honestly: a duplicate placed *first* does win the item's class (first-row-wins), but
the run still refuses and exits 1 — the marker and the exit code are independent of which row won.

**The mutant discrimination works both ways** (`receipts/probe_ld1.txt` + the harness runs):

- pristine counter, r88 53-row population → `ROW LD1 … got=LEDGER-REFUSED rc=1 match=yes`, `SUMMARY rows=53
  mismatches=0 errors=0` (EXIT 0);
- the **m17** mutant (the duplicate-id refusal dropped) → `got=- rc=1 match=no` → the row goes **red** → killed;
- the m17 mutant on the **r87 51-row population** → `SUMMARY rows=51 mismatches=0` → **survives**, exactly as the
  claim's do-nothing control states.

So the LD1 row binds the `_ledger` duplicate-id refusal, and the binding is on the **marker**, not on the exit code
(the m17 mutant also exits 1 — the L1 recorded this as plan A7; my measurement agrees).

**Can the harness write outside its `--work`?** **No.** The harness's `where=ledger` branch writes exactly one file,
`os.path.join(work, f"ledger-{rid}.tsv")`, under `--work`; the counter is then run with `--root lane --rev BASE` and
`cwd=lane`, but the counter is read-only (`git show` / `rev-parse` / `ls-files`, all plumbing). Measured: a full
53-row harness run left **every tracked lane file byte-identical** (`git ls-files` digest `1d06e096…` before and
after). The harness's *other* writes (the `forge-*.tsv` files and the fixture clone) are also under `--work`. Note the
harness's fixture builder does `git clone --shared --no-checkout <lane> <work>/fixture` — the clone is under `--work`,
and `--shared` alternates reference the lane's object store read-only.

**One latent weakness in the harness's marker test (LOW, carried, not a falsifier).** The harness scores LD1 with
`marker = f"LEDGER-REFUSED id={item}"` and `l.startswith(marker)`. `startswith` is a **prefix** test, so a refusal for
`P011` also matches the marker for `P01`. Measured (`/fast/scratch/.../mark2`): with a ledger carrying an extra
`P011` row, the **m17 mutant** (which refuses no duplicate at all) still scores `got=LEDGER-REFUSED` — the marker
check is satisfied by the *wrong* id. In the frozen r88 configuration the r77 ledger holds no `P011`-style id, so this
cannot bite today (probe: `LEDGER-REFUSED id=P011` only appears if such an id is in the ledger). It is a robustness gap
in the row's discriminator, not a falsification of the claim, and it is the same class the L1 already named in plan A8
F7 ("the `LEDGER-REFUSED` marker is shared by three legs"). Smallest fix: match the id exactly
(`l.split()[2] == f"id={item}"`).

**LD1 verdict: fail-closed.** A duplicate id cannot make the counter resolve an item it should refuse (probe C), the
harness writes nothing outside `--work`, and the pristine/mutant pair discriminates the clause in both directions.

---

## 4. Findings

### F1 (MEDIUM, r88-introduced) — the FLAGFAIL detail is no longer injective: two different stderr payloads render as the SAME cell

**Exploit path.** The r88 parent does `raw.decode('utf-8', 'backslashreplace')` and then `_escape_text`. The
`backslashreplace` decode already turns an undecodable byte into the four literal characters `\xff`; `_escape_text`
then doubles that backslash. A stderr carrying the **raw byte** `0xFF` and a stderr carrying the four literal
characters `\xff` therefore produce byte-identical details.

**Evidence** (`receipts/probe_c2g-final-bytes.txt`):

```
r88 (final 4042218f…):   byte-FF vs literal-\xff   SAME DETAIL: True
                          byte-80 vs literal-\x80   SAME DETAIL: True
                          byte-FF-line vs literal-line  SAME DETAIL: True
r87 (control e1b00e8a…): byte-FF vs literal-\xff   SAME DETAIL: False   (r87: U+FFFD vs \xff — distinct)
                          byte-FF vs byte-FE       SAME DETAIL: True    (r87 collided the OTHER way)
```

The r87 control also collides (two invalid bytes both became `�`), but on a *different* pair and with a
distinguishable literal. **r88 traded one collision for another.** Note the prereg's stated limit for C2 says
*"`_escape_text` doubles backslashes, so the detail is an injective spelling, not the raw bytes"* — that sentence is
about `_escape_text` alone (which is injective on **text**), and it stays true of `_escape_text`; the collision is
introduced by the `backslashreplace` **decode** step that precedes it, which is the r88 change. The claim's wording
does not assert injectivity of the *composed* pipeline, so **this does not falsify C2's stated wording** — but the
sentence is one a reader could reasonably read as covering the composed path, and the honest scope note is worth
filing.

**Impact.** Two materially different delegated failures (a byte-corrupt stderr vs. a stderr that literally says
`\xff`) are indistinguishable in the record. For an audit instrument whose detail is the only evidence of *why* a
delegation failed, that is a real loss of fidelity — not a safety hole (the cell is still one line, still escaped,
still a refusal).

**Smallest remediation.** Decode with `errors="surrogateescape"` (or keep the raw bytes and escape them directly, as
`_escape_record` does for paths), so an undecodable byte and its literal spelling stay distinct. The `_escape_record`
path already has this property for path names; the FLAGFAIL detail does not.

### F2 (LOW–MEDIUM, r88-introduced) — the 200-character excerpt is spent on escapes, so the exception's TYPE NAME can be pushed out of the head

**Exploit path.** r88 escapes **first** and then keeps head-100 / `…` / tail-99 of the **escaped** text. Each control
byte costs **four** characters (`\x01`), so 25 leading control bytes consume the entire 100-character head. The
exception type name — which the prereg says the head exists to carry — then survives in neither the head nor the tail.

**Evidence** (`receipts/probe_c2g-final-bytes.txt`, P2 block):

```
r88:  10-SOH + "AttributeError: " + 200x   names_AttributeError=True
      25-SOH + "AttributeError: " + 200x   names_AttributeError=False   <-- the type name is GONE
      30-SOH + "AttributeError: " + 200x   names_AttributeError=False
      40-SOH + "AttributeError: " + 200x   names_AttributeError=False
r87:  every case                                  names_AttributeError=False  (tail-only cut)
```

**Impact.** The r88 repair fixed the *raw-200* truncation (it now keeps both ends), but for a stderr whose leading
bytes are control bytes the head is consumed by escapes and the detail names neither the type nor the message. The
prereg's C2 wording says the detail *"keeps the FIRST characters (where an exception names its type) and the LAST
ones, so a 400-character `AttributeError: …` line still names `AttributeError`"* — the **400-character `AttributeError:`
case does hold** (P3/KFF3 pass, and the fixture's KFF3 case is exactly that shape and passes). The failing shape is a
stderr with ≥25 leading control bytes *before* the type name, which the fixture does not exercise. So this is a
**wording-scope gap, not a falsifier**: the sentence promises the head carries the type name, and there is a measurable
class of stderr where it does not.

**Smallest remediation.** Bound the **raw** payload first (keep the first and last N raw bytes), then escape that
window — so the head-100 is spent on content, not on escape sequences. This also fixes F1's window, since the raw
bytes are preserved.

### F3 (LOW, inherited — NOT an r88 regression) — the parent's verdict dispatch reads the child's whole stdout, so a writer beside the tool can forge `CLEAN` and remove the K4 refusal entirely

**Evidence** (`receipts/probe_c2f-final-bytes.txt`): MODE `forged_clean` → **0 K4 rows** — the tool accepted the tree as
verified although the delegated `ls-files` read had failed. The r87 control behaves identically, so **r88 neither
introduced nor worsened it**; the r88 change did not make it reachable in any new way.

**Scope.** This is the S85Sentinel F5 class the prereg declares out of claim: *"a writer inside the audited tree is
outside the claim"*, and the real `tools/souji-receipt-write.py` is stdout-silent (verified: no `print`/`sys.stdout`
write in its `_truth_refusal`/`_flag_refusal`), so the shipped lane does not exercise it. **Carry to r89**, not a C2
falsifier.

### F4 (LOW, inherited, unchanged by r88) — the sibling branches still embed raw stderr in the cell

`_stderr_tail` (not `_one_line`) renders the detail in the **status-failed** and **no-verdict** branches, so a TAB or a
control byte in the delegated stderr still splits the `MISMATCH` row. Measured (`receipts/probe_sibling-final-bytes.txt`):
a stderr carrying TAB+SOH yields a **6-cell** row and one raw SOH byte in stdout — **identically on the r88 and r87
bytes**. The prereg's stated limit already covers this (*"`_stderr_tail`'s use in the other branches (status-failed,
no-verdict) is unchanged"*), so it is **explicitly out of C2's claim**. Carry to r89.

---

## 5. What I did NOT find (negative results, so the L1 can rely on them)

- **No way to inject a record row through the FLAGFAIL payload.** A payload decoding to
  `MISMATCH\tK4\t.\tforged\tinjected` renders with escaped tabs inside one cell and adds **no** row (P11).
- **No way to make the parent read a payload's text as a verdict.** `WRITER `, `CLEAN`, `REFUSED x` and
  `MISMATCH\t…` payloads are all inert inside the cell (P10–P13); the branch dispatch has already happened by then.
- **No raw SOH / NEL / U+2028 reaches stdout through the FLAGFAIL branch** on the r88 bytes (P4, P8; zero raw bytes
  counted in stdout). The C1 control block beyond NEL is emitted raw (U+0080, U+0081, U+0084, U+0086, U+008D, U+0090,
  U+009B, U+009F each appear raw — `receipts/probe_c2e.txt`); the L1 already narrowed this in plan A3 and the tool's
  docstring records it, so it is a **known, disclosed** property, not a new finding.
- **No boundary escape in the LD1 row.** The duplicate-id refusal is fail-closed in every ordering and every class
  tested (§3), and the harness writes nothing outside `--work`.
- **The C2 fixture reproduces on the final bytes**: `SUMMARY cases=7 tool_pass=7 before_pass=3`, EXIT 0 (re-run here on
  `4042218f…`).
- **The C1 after arm reproduces on the final bytes**: `SUMMARY rows=53 mismatches=0 accepted=0 refused_true=0 errors=0`,
  and the pristine `ROW LD1 … match=yes` (re-run here).

---

## 6. Reproducers

All scripts are in this seat dir and run standalone (stdlib only, no network, `--work` under
`/fast/scratch/hyaku/souji-r88/S88Sentinel/…`):

| script | what it shows | receipt |
|---|---|---|
| `probe_c2.py` | FLAGFAIL detail framing: short / traceback / 10 MB / U+2028 / non-UTF-8 / TAB / clean / forged-WRITER / invalid base64 | `receipts/probe_c2.txt` |
| `probe_c2b.py` | the parent's branch dispatch under a writer that prints `WRITER`/`CLEAN`/`FORGED`/`REFUSED`, and payloads that try to impersonate each token | `receipts/probe_c2b.txt` |
| `probe_c2c.py` | the r88-vs-r87 detail comparison incl. the 10 MB / 10 MB-of-SOH memory cost | `receipts/probe_c2c.txt` |
| `probe_c2d.py` | the escape-order head loss and the r87 control's tail-only cut | `receipts/probe_c2d.txt` |
| `probe_c2e.py` | the escape set, character by character (C0/C1/NEL/LS/PS/DEL/boundaries), and the five LD1 ledger orderings | `receipts/probe_c2e.txt` |
| `probe_c2f.py` | the parent's dispatch order: `honest` / `clean_after` / `noise_after` / `writer_after` / `forged_clean` (the F3 fail-open) | `receipts/probe_c2f-final-bytes.txt` |
| `probe_c2g.py` | **F1** (injectivity) and **F2** (head budget) on the r88 and r87 byte sets | `receipts/probe_c2g-final-bytes.txt` |
| `probe_head.py` | the KFF3 shape vs the control-byte-prefixed shape, r88 vs r87 | `receipts/probe_head.txt` |
| `probe_ld1.py` | the LD1 ledger orderings A–F and the malformed-row case | `receipts/probe_ld1.txt` |
| `probe_sibling.py` | **F4**: the no-verdict branch's 6-cell row and raw SOH, r88 vs r87 | `receipts/probe_sibling-final-bytes.txt` |
| `probe_swap.py`, `probe_swap2.py`, `probe_swap3.py` | the `WRITER` digest binding under an atomic swap: the CONTROL fires `RECEIPT-WRITER-SWAPPED`; the FORGERY arm shows the forged digest defeating the *comparison* (the run still refuses) | `receipts/probe_swap3.txt` |

---

## 7. Recommendation to the L1

**C1:** no wording change needed from this seat. LD1 is fail-closed and discriminates m17 in both directions.
Optional hardening (LOW, r89): make the harness's marker test an exact id match rather than `startswith`, so a
`P011`-style id cannot satisfy `P01`'s marker.

**C2:** no wording change needed from this seat — the claim's stated wording is not falsified by anything this seat
measured. Two optional narrowing sentences, both LOW-to-MEDIUM and both **new** relative to plan A2/A3:

- *A9 (candidate) — the FLAGFAIL detail is injective on the decoded **text**, not on the raw bytes: an undecodable
  byte and the literal spelling of it render identically (F1), and the 200-character excerpt is measured on the
  **escaped** text, so a stderr with ≥25 leading control bytes loses the exception's type name from both ends (F2).*

Carry to r89: **F3** (a writer beside the tool can forge `CLEAN` and remove the K4 refusal; inherited, F5-limited) and
**F4** (the status-failed / no-verdict branches still embed raw stderr; explicitly outside the claim).

**Scratch:** my seat's scratch root `/fast/scratch/hyaku/souji-r88/S88Sentinel/` was deleted in full before this
yield (nothing of mine left behind). **Disclosure:** one file remains at the *shared* scratch parent
`/fast/scratch/hyaku/souji-r88/reca.json` (697 bytes, mtime 08:34) — it is the `--json` output of a
`souji-record-agreement.py` run; **none of this seat's 13 scripts writes it or passes `--json`** (verified by grep), so
it belongs to another seat; I left it in place rather than delete another seat's work.

**Tool installs:** none. No pacman (paused host-wide), no uv/npx/binary fetch, no sysctl, no sudo, no service restart,
no host mutation. The lane was read-only to this seat apart from this seat's own directory and this report file.
