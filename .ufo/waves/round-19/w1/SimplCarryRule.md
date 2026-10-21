STATUS: DONE — three helpers are the minimal split; only `status_paragraph`+`carry_entries` may merge into one join primitive; `carries` and the pre-round-18 branch must stay.

# Findings

## Axes (calibration)

1. **False-pass closure** — unmarked cuts at a source physical-line end must emit `LG-SEAT-UNCARRIED` (the seven round-16 quotes; fixture `wrap-unmarked`).
2. **False-fail closure** — complete paragraphs, ellipsis at a source line end, and lesson bullets that wrap must exit 0 (`wrap-complete`, `wrap-marked`, `wrap-bullet-wrapped`).
3. **Replay stability** — pinned replays before round 18 must keep the old first-line substring match (`WRAP_STRICT_FROM_ROUND = 18`, `tools/souji-landing-gate.py:122`, `:496–518`).

## Can the three helpers collapse?

| Helper | Role | Needed for 4 fixtures + 7 historical? |
|--------|------|--------------------------------------|
| `_continues_paragraph` | Shared wrap boundary | Yes — both sides |
| `status_paragraph` | Report-side block | Yes — without it strict mode sees only the marker physical line and reopens false-pass (base gate behavior at `3ab2c81`) |
| `carry_entries` | Lesson-side join + `norm_line` | Yes for `wrap-bullet-wrapped` only among the four cases; inert on all seven historical bullets (one physical line each per `.ufo/waves/round-18/w1/ScoutCarryWrap.md:94`) |
| `carries` | Paragraph vs entry predicate | Yes — encodes (a) full normalized paragraph and (b) prefix at source line end + ellipsis; mid-line ellipsis rejected via `ELLIPSIS_RE.match(entry, m.end())` (`:446–464`) |

**Verdict:** Do not collapse to a single helper. `carries` should remain a pure `(block, entry) → bool` function so `census/round-19/probe-carry-invariants.py` can load the gate module and stress the predicate without git worlds.

**Allowed collapse (cosmetic only):** merge `status_paragraph` and `carry_entries` into one internal `_join_wrapped(lines, *, start_idx=None)` — same `_continues_paragraph` rules, either one block from `start_idx` or a list of normalized lesson entries. Saves one def name and ~8 lines; zero semantic change.

**Do not merge `carries` into `check_carry`:** the match loop plus `re.finditer(re.escape(prefix), entry)` is the non-obvious guard against vacuous mid-line ellipsis; isolating it preserves testability.

## Minimal-code sketch

Keep `_continues_paragraph`, one join primitive, `carries`, and the existing `check_carry` branch (`:467–539`):

```python
def _join_wrapped(lines, start_idx=None):
    if start_idx is not None:
        block = [lines[start_idx]]
        j = start_idx + 1
        while j < len(lines) and _continues_paragraph(lines[j]):
            block.append(lines[j])
            j += 1
        return block
    entries, cur = [], None
    for line in lines:
        if cur is not None and _continues_paragraph(line):
            cur.append(line)
        else:
            if cur is not None:
                entries.append(norm_line(" ".join(cur)))
            cur = [line]
    if cur is not None:
        entries.append(norm_line(" ".join(cur)))
    return entries

def carries(block, entry):
    full = norm_line(" ".join(block))
    if full in entry:
        return True
    for k in range(1, len(block)):
        prefix = norm_line(" ".join(block[:k]))
        if not prefix:
            continue
        for m in re.finditer(re.escape(prefix), entry):
            if ELLIPSIS_RE.match(entry, m.end()):
                return True
    return False

# check_carry (strict): entries = _join_wrapped(carry_lines); block = _join_wrapped(report_lines, lineno-1)
# check_carry (legacy): unchanged first-line needle in nl loop for round_no < 18
```

Nothing slimmer removes a branch without reopening a failure direction.

## YAGNI deletion list (reject these shrinks)

| Candidate deletion | Why reject |
|--------------------|------------|
| Drop `carry_entries` / lesson join | Reopens false-fail: `wrap-bullet-wrapped` fails with per-line match (observed: base arm exit 1 on that case in `tests/fixtures/r19-carry-wrap.py` run 2026-10-21). |
| Drop `status_paragraph` / report join | Reopens false-pass: strict mode degenerates to first-line `needle in nl`; seven historical quotes and `wrap-unmarked` silent-pass again. |
| Drop `carries`; inline only `full in entry` | Reopens false-pass on unmarked first-line cuts; drops marked-cut and boundary semantics. |
| Restrict `carries` to `k == 1` only | Not required by four fixtures or seven historical quotes (all first-line unmarked cuts), but **would** false-fail a valid ellipsis after the second source physical line; `probe-carry-invariants.py` exercises all boundary `k` (562 cases, 0 violations). |
| Accept ellipsis after any shorter prefix without source line-end alignment | Vacuous carry (`STATUS: PARTIAL …` carries everything); ruled out in ScoutCarryWrap `:92–93`. |
| Remove `round_no >= WRAP_STRICT_FROM_ROUND` else branch | Breaks replay contract: `r16-landing` at `6ff91f5` would gain seven findings vs pinned `gate-replays-expected.json` (`ScoutCarryWrap.md:102–112`). |
| Remove `LG-SEAT-UNCARRIED` continuation hint (`:521–525`) | Not exercised by the four external fixture cases; keep — calibration signal for authors, zero match cost. |
| Remove `CARRY_TOKEN_RE` gate on entries | Unrelated to wrap rule but still required for open/resolved carry semantics on all rounds. |
| Fold `_continues_paragraph` into callers | Duplicates stop conditions (fence, table, heading, list, thematic break, new STATUS); one shared predicate is already minimal. |

## Code that is required but outside the four fixtures

- **`for k in range(1, len(block))` with `re.finditer`:** fixtures use `k=1` or full paragraph only; loop generalizes the authored rule and is validated by the probe, not by the seven silent historical cuts.
- **Legacy branch (`:513–518`):** no fixture case runs wrap below round 18; required so pinned replays and `--round 16` selftest worlds stay byte-stable.

## Preserved contract

Paragraph-aware carry when `round_no >= 18`: normalized whole marker paragraph in a joined lesson entry, or normalized prefix ending at a **source** physical-line boundary immediately followed by `…`/`...`; lesson bullets may wrap; mid-line ellipsis never carries; rounds below 18 keep first-line substring matching.

# Evidence

- Read integrated gate carry block: `tools/souji-landing-gate.py:407–464`, `467–539`, selftest wrap cases `:2092–2171`.
- Read base gate at `3ab2c81479f5004c8bc91946eea482caec45408f`: no `status_paragraph`/`carry_entries`/`carries`; `check_carry` uses `needle in nl` only (`git show 3ab2c81:tools/souji-landing-gate.py` lines 393–430).
- Read fixture contract: `tests/fixtures/r19-carry-wrap.py:6–14`, `:75–100`.
- Read seven-quote table: `.ufo/waves/round-18/w1/ScoutCarryWrap.md:20–31` (all first physical-line unmarked cuts).
- Executed 2026-10-21 from lane root:
  - `python3 tests/fixtures/r19-carry-wrap.py` → `SUMMARY total=4 failed=0 base_discriminating=2` (matches `census/round-19/c1-carry.txt:9–18`).
  - `python3 census/round-19/probe-carry-invariants.py` → `violations=0` (400 paragraphs, 562 boundary cuts, 842 midline cuts).

No tool installs.

# Commands run

```bash
git -C /home/vgpnk/Projects/shokunin/souji-shokunin show 3ab2c81:tools/souji-landing-gate.py  # read-only, carry section
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 tests/fixtures/r19-carry-wrap.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 census/round-19/probe-carry-invariants.py
mkdir -p /var/tmp/souji-r19-SimplCarryRule  # scratch dir created; removed after runs (fixture uses its own /var/tmp prefix)
```

# Contract compliance

- Leaf seat: no subagents, no lane edits outside this report.
- Did not run live census, git/jj mutations, or fleet tools.
- Scratch under `/var/tmp/souji-r19-SimplCarryRule/`; fixture cleans its own `souji-r19-carry-wrap.*` trees.
- Report only; no changes to `tools/`, `tests/`, `census/`, or corpus.
