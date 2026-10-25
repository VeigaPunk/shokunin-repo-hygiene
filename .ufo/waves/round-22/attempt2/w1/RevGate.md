# RevGate — C2 gate-check review (round 22, attempt 2)

**STATUS: PASS** — this review is complete and every line below was executed.
**VERDICT: ACCEPT-WITH-FIXES** — 3 required fixes (F1–F3), 4 optional hardening fixes (F4–F7).
STATUS describes the review; VERDICT describes the candidate.

Object: `tools/souji-gate-check.py`, working tree == HEAD blob `4309d769…`, sha256
`d85c2696…`, committed at `a211e4d` in a lane at tip `2a130b47` (frozen base `4edb25d`).
Fixture transcripts and the sha manifest: `evidence/RevGate.md`; fixture tree
`evidence/gatefix/` (176K, created only under the evidence directory).

No tools were installed or updated for this review (no `uv`/`npx`/pacman/channel use).

## 1. Executed: the frozen counter on the real lane

```
$ python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 \
    --entries corpus/knowledge/quarantine-staging-no-copy-r23.md \
              corpus/knowledge/quarantine-origin-record-fields-r24.md \
    --snapshot-dir census/round-22/attempt2/sources \
    --slice census/round-22/attempt2/quarantine-slice \
    --slice-verdicts census/round-22/attempt2/slice-verdicts.tsv
entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0
rc=0
stdout bytes: 52   stdout lines: 1
MATCHES frozen spelling exactly: entries=<n> ok=<k> slice_verdicts=<v> slice_total=<t> fail=<f>
```

The counts line is byte-identical to the frozen template (preregistration line 78) on success and
is the only line on stdout. `git status --porcelain census/round-22` is empty, so the snapshots,
slice and verdicts read by check 4 and the slice check are the committed bytes, not scratch.

**Concurrent change during this review.** While I was reviewing, another seat modified both
entries in the working tree (they were clean when §1 was first run). Diff, executed:

```
$ git --no-pager diff --stat -- corpus/knowledge/
 corpus/knowledge/quarantine-origin-record-fields-r24.md | 12 ++++++------
 corpus/knowledge/quarantine-staging-no-copy-r23.md      |  6 +++---
 2 files changed, 9 insertions(+), 9 deletions(-)
# every "+" line appends the same clause to an ADMIT line:
+… — § COMMANDS trash --list — reason: grounds this entry's claim directly at the quoted locator — snapshot: …
```

The counter re-run against the modified working tree is identical:

```
$ python3 -B tools/souji-gate-check.py --root . --round-date 2026-10-25 --entries … --slice …
entries=2 ok=2 slice_verdicts=8 slice_total=8 fail=0
rc=0
```

So the C2 receipt is stable across that edit, but the entries are now **modified relative to
`HEAD`**: whoever lands them must re-take the After receipt at the commit that contains them, and
the report must quote the counts line from that commit. See F2 for what the appended clause does
and does not establish.

Built-in selftest, executed: `selftest=9/9`, `rc=0`, including
`PASS control always-green -> FALSE-GREEN-REJECTED`.

## 2. Executed: one must-fail input per check, and the slice counter

Every row below is a fixture I wrote and a run I observed (transcripts in `evidence/RevGate.md`
§C–§D).

| # | Required must-fail input | Fixture | Observed | Correct? |
|---|---|---|---|---|
| 1 | entry without `## Gate` | `nogate.md` | `check1-no-gate` → `ok=0 rc=1` | yes |
| 1 | **byte-exact staged package entry** (sha `f13fb769…`, 0 `## Gate` occurrences) | `staged-copy.md` | `check1-no-gate` → `ok=0 rc=1` | yes |
| 2 | Gate with no https URL | `nourl.md` | `check2-no-url` → `rc=1` | yes |
| 2 | wrong `opened:` | `baddate.md` | `check2-opened-date: found ['2026-10-24'] want 2026-10-25` | yes |
| 3 | 26-word quote | `quote26.md` | `check3-quote-26-words` → `rc=1` | yes |
| 3 | quote on a line with no locator | `nolocator.md` | `check3-no-locator-gate-line-6` → `rc=1` | yes |
| 3 | 25 words, snapshot broken by a newline | `quote25.md` | `ok=1 rc=0` (boundary correct, collapse correct) | yes |
| 4 | quote absent from named snapshot | `quoteabsent.md` | `check4-quote-absent-from-snapshot-line-6` | yes |
| 4 | one-character perturbation (`newpaths`) | `perturb.md` | `check4-quote-absent…` | yes |
| 4 | snapshot outside `--snapshot-dir` (lexical) | `snapoutside.md` | `check4-snapshot-outside-dir-line-6` | yes |
| 4 | snapshot file missing | `snapmissing.md` | `check4-snapshot-missing-line-6` | yes |
| 4 | located quote with no `snapshot:` on the line | `nosnap.md` | `check4-no-snapshot-named-line-6` | yes |
| 4 | whitespace-collapsed positive (quote spans `\n` in snapshot) | `good.md` | `ok=1 rc=0` | yes |
| 5 | column-0 dangling `source: S999` | `dangling.md` | `check5-dangling-source: S999` → `rc=1` | yes |
| 5 | no citation at all | `nocite.md` | `check5-no-source-citation` → `rc=1` | yes |
| 5 | dangling id as `- source: S999` bullet | `citedlist.md` | **`ok=1 rc=0`** | **NO — F1** |
| 5 | dangling id as `  source: S999` (2-space indent) | `citedindent.md` | **`ok=1 rc=0`** | **NO — F1** |
| 6 | no ADMIT | `noadmit.md` | `check6-no-admit` → `rc=1` | yes |
| 6 | no REJECT | `noreject.md` | `check6-no-reject` → `rc=1` | yes |
| 6 | REJECT with no reason token at all | `reject-noreason.md` | `check6-reject-without-reason` → `rc=1` | yes |
| 6 | REJECT with an em dash and no reason text | `reject-emdash.md` | **`ok=1 rc=0`** | **NO — F2** |
| 6 | ADMIT with no reason (REJECT does carry one) | `admit-noreason.md` | **`ok=1 rc=0`** | **NO — F2** |

Slice counter — "a missing row cannot be counted as verified" holds in every probe:

```
S2  one row missing          -> slice_verdicts=1 slice_total=2 fail=1 rc=1   (V did not rise to T)
S3  + a well-formed row for an id NOT in the slice -> V=1 T=2 rc=1          (phantom row not counted)
S7  missing id present as a 2-field short row      -> V=1 T=2 rc=1          (short row not verified)
S8  missing id named only inside another row's evidence text -> V=1 T=2 rc=1
S4/S5/S6  bad class / empty evidence / duplicate  -> fail, V excludes the row
S11/S12   slice file absent / verdicts file absent -> fail, rc=1
S10 empty slice file (0 bytes) -> entries=1 ok=1 slice_verdicts=0 slice_total=0 fail=0 rc=0
```

The real slice has 8 id lines, the verdicts TSV has the same 8 ids in the four frozen classes,
`V=8 T=8`. The malformed 8th line ` S118\`   the cited source could not be fetched…` is what the
frozen extractor emits for register row 361 (independently documented in
`.ufo/waves/round-22/attempt2/w1/Slice118.md` H1), so counting `S118` is faithful, not a gate bug.

## 3. Findings

### F1 (required, MEDIUM) — check 5 does not enumerate every `source: S<digits>` citation
`tools/souji-gate-check.py:39` anchors at column 0: `^source:\s*(S\d{3,})`. Frozen check 5 is
"every `source: S<digits>` id cited in the entry's frontmatter resolves to a row in
`corpus/SOURCES.md`". Executed: `citedlist.md` (`- source: S999`) and `citedindent.md`
(`  source: S999`) both return `entries=1 ok=1 … fail=0 rc=0` while `S999` has no registry row —
a false green that only requires one well-formed column-0 citation elsewhere in the file.
Fix: `re.compile(r"^\s*(?:[-*]\s*)?source:\s*(S\d{3,})", re.M)`.
Impact on current lane data: none — both real entries cite at column 0 and all cited ids
(`S109 S110 S111 S112 S113 S114 S022`) resolve; I re-ran the real counter above.

### F2 (required, MEDIUM) — check 6's "reason string each" is not enforced for ADMIT and is satisfied by punctuation for REJECT
Two independent false greens, both executed:
- `tools/souji-gate-check.py:126-133` checks a reason only on REJECT lines; an ADMIT line with a
  locator and a snapshot but no reason (`admit-noreason.md`) passes. Frozen: ">=1 ADMIT and >=1
  REJECT with a reason string each."
- `REASON_RE` (`:44`) includes a bare `—`, so `- REJECT: staged row — ` (no reason text) passes.
Decision needed, because the current corpus depends on the lax reading: **at the reviewed commit
neither entry's ADMIT line carries a prose reason** — e.g. r23 `- ADMIT: "RENAME_NOREPLACE …" — §
DESCRIPTION flags — snapshot: …` has locator + snapshot only. So either the frozen clause binds
both rows (in which case the commit-time `ok=2` is itself a false green and the entries need
reasons) or it binds the REJECT. The strict reading is also the cheaper one to make true: append a
reason to every ADMIT line in both entries, and tighten `REASON_RE` to require `reason:`/`because:`
with a non-empty tail (or text after the dash).

**Data-side state at review close, and its limit.** A concurrent seat has now appended the *same*
clause to all 9 ADMIT lines (`reason: grounds this entry's claim directly at the quoted locator` —
see §1). That satisfies any mechanical reason check, including the tightened one, but the string is
a tautology: it is true of every located quote and distinguishes none of the 9 claims. So a
mechanical "reason string" test — mine or the current one — cannot establish that each ADMIT states
*why that quote licenses that claim*. Options, to be decided explicitly rather than by the tool:
per-claim reasons (names the claim the quote grounds), or a recorded decision that the frozen
clause binds only the REJECT row. What must not happen is citing `fail=0` as proof of a per-claim
justification, because the tool cannot test that.

### F3 (required, MEDIUM) — the counts line miscounts missing verdict rows into `F`
Frozen (preregistration lines 99–100): "a missing row is a failure and is counted in **neither V
nor F** — it simply cannot raise V to T." Executed: one missing row → `fail=1`; missing verdicts
file → `fail=2`; i.e. `:173`'s `verdict-missing` string is appended to `fails` and summed into
`total_f`. Exit codes are right (V≠T already forces 1), but `fail=<F>` no longer means what the
preregistration froze it to mean. Fix: collect `verdict-missing` diagnostics separately from
`total_f`. With the fix, S2 would read `slice_verdicts=1 slice_total=2 fail=0` and still exit 1.

### F4 (optional, LOW) — check 1 rejects a conforming entry whose `## Gate` is the first line
`gate_section` (`:54`) searches `"\n## Gate"`, so a file starting at byte 0 with `## Gate` is
"no gate" (`gatefirst.md` → `check1-no-gate`). Frozen check 1 only requires that the file
*contains* a `## Gate` heading. Fails closed (no false green) and the real entries have
frontmatter, so this is correctness polish: use `re.search(r"^## Gate", text, re.M)`.

### F5 (optional, LOW) — check 4's "lives under `--snapshot-dir`" is a lexical prefix test
`:99` compares normalized strings, so a symlink inside the snapshot dir that resolves outside it
passes: `census/sources/link-out.txt -> ../elsewhere/y.txt` yields `ok=1 rc=0` (`symlinkesc.md`).
Fix: compare `os.path.realpath`. No symlinks exist in the lane's snapshot dir (all 13 entries are
regular files, per `ls -la census/round-22/attempt2/sources/`), so no current data is affected.

### F6 (optional, LOW) — check 3's locator can be satisfied by the snapshot's filename
`LOCATOR_RE` (`:41`) matches anywhere in the line, including the `snapshot:` path. Executed:
`- ADMIT: "…" — snapshot: census/sources/section-line.txt` has no locator at all and returns
`ok=1 rc=0` because the filename contains "section". Fix: run `LOCATOR_RE` on the line with the
`snapshot:` token removed.

### F7 (optional, LOW) — two selftest fixtures deviate from the frozen kill rule
- Fixture (6) must be "a byte-exact copy of the staged package entry (no Gate)"; the selftest
  uses a 3-line paraphrase (`:242`), not those bytes. I verified the real behaviour with a
  byte-exact copy (`sha256 f13fb769…`, identical to
  `…/shokuknow/merge/souji/knowledge/corpus/knowledge/quarantine-staging-no-copy-r23.md`) → fails.
  To make the fixture bite if the staged entry ever changes, store the copy under the lane and
  have the selftest assert its sha.
- Fixture (2) is "quote of 26 words"; the selftest uses 30 (`:238`), so the 25/26 boundary is
  covered only by my fixtures (25 → ok, 26 → fail).
- `_gate(admit=False)` is dead (no fixture uses it), so "no ADMIT" is untested by the tool itself.

## 4. Residual risk and verification gaps

- **Empty slice file ⇒ exit 0.** `--slice census/slice-empty` prints
  `slice_verdicts=0 slice_total=0 fail=0` and exits 0. This is *faithful* to the frozen exit rule
  ("exit 0 iff … V == T …"), so it is a gap in the frozen counter, not a candidate deviation, and
  I am not redefining the predicate. Mitigation that stays inside the freeze: the round report
  must quote the counts line literally — the frozen After string pins `slice_verdicts=8
  slice_total=8`, which a truncated slice cannot produce.
- **Check 4 reads working-tree bytes.** The frozen wording says "committed snapshot"; the frozen
  counter command has no `--rev`, so commitment is not enforceable by the tool. Verified
  mitigation for this run: `git status --porcelain census/round-22` is empty and all 13 snapshots
  plus the slice and verdicts are in `git ls-files`, i.e. committed at `2a130b47`.
- **Failure-path stdout.** The frozen line "prints exactly one line" holds on success
  (52 bytes, 1 line). On failure the `FAIL …` diagnostics precede the counts line on stdout; if a
  consumer requires stdout to be exactly one line in all cases, route diagnostics to stderr.
- Not checked here (other seats' scope, no redefinition attempted): whether the 8 slice verdicts
  are *correct* classes/evidence for their rows (that is the Slice*.md seats' product and the
  register work), C1's calibration counter, and the frozen C2 After target's registry conformance
  `scripts/sources-census.sh validate --root … souji` — not run, because a validator's write
  behaviour is unverified and my lane bounds forbid writing elsewhere in the lane; the gate review
  itself asserts nothing about it.
- Review is read-only: only `evidence/RevGate.md`, `evidence/gatefix/**` and this report were
  written under round-22; no git/jj write, no lane-index/state/watchdog/MANIFEST edit, no
  mutation of the candidate, no cleanup run, no process signalled, no network access.
