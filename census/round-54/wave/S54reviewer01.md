# S54reviewer01 — souji round 54, C1 v3 counter attack report (reviewer seat)

Seat: S54reviewer01 (role: reviewer, leaf member — no subagent dispatch).
Scope: attack the FROZEN C1 v3 counter `census/round-54/c1-counter.py` over the
frozen fixture grammar; never edit frozen bytes; classify every observed
behavior as CommonMark-consistent, named-limit confirmation, or routed defect
for r55. All paths below are relative to the lane repo
`/home/vgpnk/Projects/shokunin/souji-shokunin`; receipts live at
`.ufo/waves/round-54/w1/S54reviewer01/receipts/`.

## 0. Pins, tooling, method

Frozen-byte verification (sha256sum at seat start):

```
f45d3d8f4eced147b7e2c4127bf5fefe6d080f2f0fd0c637cfd44f8d41fccf7e  census/round-54/c1-counter.py          (= prereg pin)
ae5881f850ba5f5895fc27e6e3185658af372535ae7ccf971476175be118b1ba  census/round-54/fixtures/build-fixtures.py (= prereg pin)
4e73c495b6a7d1db1ef8dc5506ac874a167720a48e7618d2a41ccec55af2a1c7  census/round-54/records/c1-selftest-expected.tsv (= prereg pin)
a7928d05df794f14d5d0213ddb78d042f62819b52f5c49b3c838a1b96da1ed15  census/round-53/c1-counter.py (v2 control arm, recorded)
```

Freeze commit confirmed: `3c394cab round-54: freeze — preregistration (2 claims …)`; lane tip at seat start `bfdbb336` (the r54 C2 capture commit).

Tooling: none installed (system `python3` and `git` sufficient; tooling
authorization unused). Scratch: `/fast/scratch/hyaku/souji-r54/S54reviewer01/`
(deleted before yield; every receipt was copied into the seat dir first — that
copy is the durable record). Attack fixtures were built by importing the
FROZEN builder module (`build_one`) and, for attack states, either:

- **appended**: copy of a builder fixture + one appended commit (pure line
  additions; real base..rev history, `base=af893285b1f1` visible in each
  receipt SUMMARY) — used for F12b-derived pair/scan attacks;
- **isolated**: fresh single-commit repo (rev == base, so `git diff --numstat
  base..rev` is empty and DELETED-LINES cannot fire) — used where the attack
  must rewrite a site line or replace corrections. Disclosure: rev==base is a
  deliberate isolation device; it removes only the DELETED-LINES surface from
  the run, all other checks run normally.

Every run: `python3 -B census/round-54/c1-counter.py --root <fixture> --rev <tip>
--base <base> --record-sha256 <sha>` (+ `--sources-rev-before/after` on
F12b-derived v3 runs; the F12b honest annotation requires them — without them
the counter exits 2 `CANNOT-EVALUATE flagged filing at LOG.md:2 needs
--sources-rev-before/after`, itself a correct refusal). Full command lines,
full stdout and the fixture tree at tip are embedded verbatim in each receipt.
60 counter runs total: 13 carry-over + 31 attack states (v3) + 16 control-arm
(v2) comparisons.

## 1. Fence grammar edges (task 1)

CommonMark 0.31.2 clauses used for judgment (receipts
`01-commonmark-clauses.txt`, `01b-…`, `01c-…`): opening fence = "a code fence,
preceded by up to three spaces of indentation"; "If the info string comes
after a backtick fence, it may not contain any backtick characters"; "The
closing code fence may be preceded by up to three spaces of indentation, and
may be followed only by spaces or tabs"; "The closing code fence must be at
least as long as the opening fence" (+ same character); unclosed fence →
"the code block contains all of the lines after the opening code fence until
the end of the … document"; indented code block = lines "preceded by four or
more spaces"; HTML block type 2: start "line begins with the string `<!--`",
end "line contains the string `-->`".

| # | attack (SCORECARD.md shape) | v3 observed | classification |
|---|---|---|---|
| AF1a | corrections inside `~~~text` … `~~~` | exit 1, `CORRECTION-IN-FENCE` ×2 (receipt `AF1a-tilde-info.txt`) | **v3 hides — correct** (v2 arm exit 0, before-state confirmed) |
| AF1b | `` ````` `` opener, `` ```` `` close, corrections between | exit 1, `CORRECTION-IN-FENCE` ×2 | **v3 hides — correct**; CommonMark: 4 < 5 is not a closing fence, block unclosed → hidden (v2 arm also exit 1: its per-line toggle hides this shape too) |
| AF1c | ``` line inside `<!-- … -->`, corrections AFTER `-->` | exit 0, both corrections filed | **v3 accepts — correct** (comment hides the fence-marked line; corrections after the comment are visible prose; no over-hide) |
| AF1c2 | corrections BETWEEN `<!--`+```` ``` ```` and `-->` | exit 1, `CORRECTION-IN-FENCE` | **v3 hides — correct**; the in-comment ``` is comment content, not a fence opener (in_html branch wins), `-->` closes the comment |
| AF1d | `~~~` at EOF, corrections inside, never closed | exit 1, `CORRECTION-IN-FENCE` ×2 | **v3 hides — correct** (CommonMark: unclosed tilde fence runs to EOF) |
| AF1e | corrections wrapped in ONE-LINE comments `<!-- R52-CORRECTION … -->` | exit 1 but **no FINDING line at all**: `SUMMARY … unfiled=2 … inert=0 … fenced=0` | **grammar hole (refusal by side-effect)** — `CORR_RE` anchors `^R52`, the comment-wrapped line never lexes as a filing, so `CORRECTION-IN-FENCE`/`INERT` cannot fire; refusal comes only from unfiled (v2 arm identical, receipt `AF1e-oneline-comment-wrap.txt`) |
| AF1e2 | same one-line-comment burial on a GREEN site (both sites read 79), corrections claim `stale=79 recomputed=83` | **exit 0** — `unfiled=0 … fenced=0`, no findings | **ROUTED DEFECT R1** — a bogus buried correction is fully swallowed; v2 arm identical |
| AF1e3 | same burial via 2-space INDENT (`  R52-CORRECTION …`, visible prose per CommonMark) on a green site | **exit 0** | **ROUTED DEFECT R1** (same root cause: line-start anchor + hidden-lines audit only covers parsed filings) |
| AF1f1 | `  ~~~` fences (2-space indent) | exit 1, `CORRECTION-IN-FENCE` ×2 | **v3 hides — correct** (CommonMark allows ≤3 spaces) |
| AF1f2 | `    ```text` fences (4-space indent) | exit 1, `CORRECTION-IN-FENCE` ×2 | **ROUTED DEFECT R5** — CommonMark: 4 spaces = indented code block, NOT a fence; the corrections are visible and v3 over-hides (false positive). v2 arm also refuses (lstrip-based toggle), so this is a v2-inherited divergence, now nameable against the spec |
| AF1f3 | `\t~~~` fences (tab indent) | exit 0, corrections filed | **v3 accepts — correct** (CommonMark: tab = 4-col indent → indented code block, not a fence; `lstrip(' ')` not stripping tabs accidentally matches the spec) |
| AF1f4 | corrections placed after a `~~~\t` close | exit 0, filed | **v3 accepts — correct** (receipt `AF1f4-tab-close-tilde.txt`): v3 computes `stripped = ln.rstrip()` (all trailing whitespace), so `~~~\t` closes; CommonMark agrees ("followed only by spaces or tabs … ignored"). Note: this contradicts my pre-run prediction — recorded as observed |
| AF1g | opener line `` ```text``` `` (info string contains backticks), corrections inside | exit 1, `CORRECTION-IN-FENCE` ×2 | **ROUTED DEFECT R5** — CommonMark: "If the info string comes after a backtick fence, it may not contain any backtick characters" → NOT a fence, corrections visible; v3 opens a fence and over-hides |
| AF1h | `<!--` opened INSIDE a `~~~` fence, correction after the fence closes | exit 1, `CORRECTION-IN-FENCE` (correction inside the fence only) | **v3 hides exactly right** — comment markers inside a fence are literal; fence branch takes precedence, `in_html` is not set by fence content |

## 2. Zone edges (task 2)

| # | attack | v3 observed | classification |
|---|---|---|---|
| AF2a | opener `(` at zone offset 31, digits at 32–33 (SCORECARD line 5) | exit 1, `ZONE-TOKEN-STRADDLES-EDGE SCORECARD.md line 5 a count token starts inside the 32-char zone and ends beyond it` + INERT on the naming correction | **v3 refuses — correct** (F10 class generalized to any offset; receipt `AF2a-opener31-digits33.txt`) |
| AF2b | TWO planted straddling-looking tokens (`→ 79` at 30, `→ 81` at 36) | exit 1, ONE `ZONE-TOKEN-STRADDLES-EDGE`; SUMMARY `straddle=1` | **refusal holds; named nuance** — regex non-overlap + a boolean flag mean at most ONE straddle can ever register per line: after the first match ends beyond offset 32, every later token starts ≥32 and is dropped as "wholly outside". The second straddle is unreportable (does not change the verdict; worth r55 wording if multiple-straddle lines matter) |
| AF2c | token wholly beyond the zone (only token on the site line: 33 spaces then `(79`) | **exit 2** `CANNOT-EVALUATE no annotation in zone at SCORECARD.md` | **named limit confirmed, with semantics note**: the beyond-zone token is indeed ignored (not an annotation), but the consequence is exit 2 could-not-evaluate, not a FINDING and not exit 0 — a site whose only annotation sits beyond offset 32 forces exit 2 instead of a named refusal. Disclosed limit ("a token wholly beyond it is still not an annotation") holds; behavior is safe (no acceptance) |
| AF2d | DUAL ANCHOR on one site line: first anchor honest `(79)`, second anchor `dup: <ANCHOR> (999)` beyond the zone | **exit 0** — `mismatches=1 filed=1 unfiled=0`, the (999) is never read | **ROUTED DEFECT R2** — `zone_tokens` uses the FIRST anchor occurrence (`ln.find`); a second, lying annotation on the same line is invisible to both the site check and the filed-correction validation. v2 arm identical (first-occurrence `ln.index`) |

## 3. BOGUS-RECOMPUTED edges (task 3)

| # | attack | v3 observed | classification |
|---|---|---|---|
| AF3a | correction whose recomputed MATCHES the record but stale does not (`stale=999 recomputed=79` on sites reading 78) | exit 1, `INERT-CORRECTION` ×2 (`reads 78, correction claims stale=999 recomputed=79`), `bogus=0` | **INERT path wins — confirmed**: `elif` ordering means a wrong-stale filing is never evaluated for BOGUS. Refusal stands; precedence observation for r55 (the finding id misdescribes the failure mode) |
| AF3b | two corrections on ONE site: honest (78→79) + bogus (78→83) | exit 1, `BOGUS-RECOMPUTED SCORECARD.md:5 recomputed=83 but record count is 79`, `unfiled=0` (honest filing still counts as filed) | **v3 refuses — correct** |
| AF3c | bogus recomputed on the F12b PAIR path: second `R53-CORRECTION LOG.md:2 stale=3->4 recomputed=999->1000` | exit 1, `SOURCES-RECOMPUTE-MISMATCH LOG.md:2 filing recomputed=999->1000 but the census grep recomputes 3->3`, `logrecomp=1` | **pair grammar DOES validate recomputed against the registry counts at the pinned revs — confirmed** |
| AF3d | pair filing whose STALE pair does not match the annotation (`stale=3->5 recomputed=3->3` alongside the honest `3->4` filing) | **exit 0** — `logrecomp=0`, no finding; the bogus-stale filing is silently dropped (`match` filters it out) | **ROUTED DEFECT R3** — the pair grammar has no INERT analog: a pair-form filing with wrong numbers can sit in SCORECARD.md unexamined. v2 arm exit 0 (never reads pairs) |
| AF3e | bogus pair recomputed when the annotation is within registry reach (`3 -> 3 rows` vs registry 3) | **exit 0** — annotation line skipped (`max(a,b) <= registry_rows`), filing never consulted, `recomputed=999->1000` unvalidated | **named limit confirmed** ("annotations whose pair does not exceed the current count are historical notes the instrument does not re-derive"); the filing validation is annotation-triggered, so the limit covers it — r55 wording may want a PAIR-FILING audit independent of the trigger |

## 4. LOG/README scan bypasses (task 4)

All F12b-derived (append-only commits; sources revs = F12b tip; registry = 3 rows).

| # | attack | v3 observed | classification |
|---|---|---|---|
| AF4a | overstatement line with a fake pointer: `- also said corpus/SOURCES.md 999 -> 1000 rows (see LOG.md:1).` | **exit 0** — `PTR_RE` matches `LOG.md:1`, line exempted as a meta-reference | **named limit confirmed** ("exempts lines carrying a path:line pointer"); v2 arm exit 0. A one-token dodge; r55 may re-word, but it is disclosed |
| AF4b | pair WITHOUT the word rows: `- also said corpus/SOURCES.md 999 -> 1000.` | **exit 0** — `PAIR_ANNOT_RE` requires `rows?\b` | **ROUTED DEFECT R4** — the 274->275 class minus the literal unit word dodges `UNFILED-SOURCES-ANNOTATION` entirely |
| AF4c | same overstatement in PROVINCE.md | **exit 0** — only `PAIR_SITES = ['LOG.md', 'corpus/README.md']` are scanned | **named-limit scope confirmed** (the frozen class names those two files); routed r55 wording: "pair annotations in any other lane file are invisible to the instrument" |
| AF4d | pair line INSIDE a fenced block in LOG.md (`` ``` `` … `- example: corpus/SOURCES.md 999 -> 1000 rows` … `` ``` ``) | **exit 1**, `UNFILED-SOURCES-ANNOTATION LOG.md:5 claims 999 -> 1000 rows but the registry holds 3` | **ROUTED DEFECT R6** — the scan does NOT hide-fence: `hidden_lines()` exists but is applied only to SCORECARD filings, not to the PAIR_SITES scan → false positive on a fenced code EXAMPLE (CommonMark: code-block content is not prose) |
| AF4e | line drift: `- drift marker.` inserted after LOG.md line 1, annotation moves 2→3, filing still names `LOG.md:2` | **exit 1**, `UNFILED-SOURCES-ANNOTATION LOG.md:3 claims 3 -> 4 rows … no pair-form filing names it` | **which finding fires: UNFILED-SOURCES-ANNOTATION at the NEW line** — confirmed; the orphaned filing at `LOG.md:2` produces NO finding of its own (silent orphan; exit 1 comes only from the annotation side). Pure line insertion → no DELETED-LINES noise |
| AF4f | same overstatement in corpus/README.md (created) | **exit 1**, `UNFILED-SOURCES-ANNOTATION corpus/README.md:1 …` | **README scan confirmed** (contrast with AF4c) |
| AF4g1 | boundary `3 -> 3 rows` (max == registry rows) | exit 0 | **boundary semantics confirmed**: strict `max(A,B) > registry_rows`; equal-to-current is in-reach |
| AF4g2 | boundary `3 -> 4 rows` (registry 3) | exit 1, `UNFILED-SOURCES-ANNOTATION LOG.md:3 …` | consistent with AF4g1; the overstatement threshold is exactly registry_rows+1 |

## 5. Carry-over (task 5)

Pinned selftest (`00-v3-selftest.txt`, pins verified BEFORE exec):

```
SELFTEST-CASE F1-HONEST-TIP pass rc=0 want_rc=0 finding=- want_finding=-
SELFTEST-CASE F2-MULTI-ANNOT pass rc=1 want_rc=1 finding=MULTIPLE-ANNOTATIONS …
SELFTEST-CASE F5-REWRITE pass rc=1 finding=DELETED-LINES
SELFTEST-CASE F6-RECORD-DRIFT pass rc=1 finding=RECORD-SHA-MISMATCH
SELFTEST-CASE F7-TILDE-FENCE pass rc=1 finding=CORRECTION-IN-FENCE
SELFTEST-CASE F8-BT4-PARITY pass rc=1 finding=CORRECTION-IN-FENCE
SELFTEST-CASE F9-HTML-COMMENT pass rc=1 finding=CORRECTION-IN-FENCE
SELFTEST-CASE F10-STRADDLE pass rc=1 finding=ZONE-TOKEN-STRADDLES-EDGE
SELFTEST-CASE F11-BOGUS-RECOMP pass rc=1 finding=BOGUS-RECOMPUTED
SELFTEST-CASE F12-LOG-UNFILED pass rc=1 finding=UNFILED-SOURCES-ANNOTATION
SELFTEST-CASE F12b-LOG-FILED pass rc=0 finding=-
SELFTEST pass cases=13
```

Direct v3 runs on all 13 rebuilt fixtures (`carry-v3-*.txt`) match the expected
matrix exactly (F1 green; F2–F6 killed with their v2 findings: MULTIPLE,
INERT, IN-FENCE, DELETED-LINES, RECORD-SHA; F7–F12 killed with the new ids;
F12b green). **Carry-over: no regression.**

v2 acceptance control arm (`v2arm-*.txt`): the frozen v2 counter exits 0 on
every NEW attack fixture F7, F8, F9, F10, F11, F12 and F12b — **the claimed
work is not vacuous** (before-state reproduced). It also exits 0 on AF1a and
AF4a/b-class states it never scanned.

## 6. Verdict table

| attack | observed | classification | suggested r55 wording |
|---|---|---|---|
| AF1a tilde+info fence | refused IN-FENCE | v3 hides, CommonMark-consistent | — |
| AF1b 5-open/4-close | refused IN-FENCE | v3 hides, CommonMark-consistent | — |
| AF1c ``` inside comment, corr after | accepted, filed | correct (comment ends at `-->`) | — |
| AF1c2 corr between `<!--`/`-->` | refused IN-FENCE | correct | — |
| AF1d unclosed tilde fence | refused IN-FENCE | correct | — |
| AF1e one-line-comment wrap (stale sites) | exit 1 via unfiled ONLY, fenced=0 | grammar hole (refusal by side-effect) | fold into R1 |
| AF1e2 one-line-comment wrap (green site) | **exit 0 swallow** | **ROUTED R1** | "CORRECTION-IN-FENCE also fires when a line of CORR_FILE that hidden_lines() hides is correction-SHAPED under a prefix-tolerant match (comment wrapper, 1–3 leading spaces); today only CORR_RE-parsed filings are audited, so a buried bogus correction on an agreeing site exits 0" |
| AF1e3 2-space-indented correction (green site) | **exit 0 swallow** | **ROUTED R1** | same root cause; include the indent case in R1 |
| AF1f1 2-space tilde fence | refused IN-FENCE | correct | — |
| AF1f2 4-space fence | refused IN-FENCE | **ROUTED R5** (over-hide vs CommonMark) | "hidden_lines enforces the CommonMark 0.31.2 fence START conditions: at most three spaces of indentation (four spaces is an indented code block) and no backtick in a backtick fence's info string" |
| AF1f3 tab-indented fence | accepted, filed | correct (accidental spec match) | — |
| AF1f4 close with trailing tab | accepted, filed | correct (`rstrip()` strips the tab) | — |
| AF1g backticks in info string | refused IN-FENCE | **ROUTED R5** (over-hide vs CommonMark) | see AF1f2 wording |
| AF1h comment inside fence | refused IN-FENCE (fence content only) | correct | — |
| AF2a opener@31 digits@32–33 | refused STRADDLE | correct | — |
| AF2b two straddling tokens | refused, but only ONE straddle registers | nuance (boolean flag + regex non-overlap; second token dropped as wholly-outside) | "ZONE-TOKEN-STRADDLES-EDGE reports one flag per line; additional straddling tokens past the first are indistinguishable from beyond-zone tokens" |
| AF2c token wholly beyond zone | **exit 2 CANNOT-EVALUATE** | named limit confirmed (ignored, not accepted; consequence = exit 2, not a finding) | disclosed; optionally name the exit-2 consequence in the limit wording |
| AF2d dual anchor, lie beyond first zone | **exit 0, lie invisible** | **ROUTED R2** | "the annotation zone is evaluated after EVERY occurrence of the anchor on a site line; a second annotated anchor (or any second count token beyond the first 32 chars when the line repeats the anchor) must refuse, not alias" |
| AF3a stale wrong, recomputed right | refused INERT (bogus unevaluated) | precedence observation | "BOGUS-RECOMPUTED is evaluated independently of the INERT checks (elif -> separate if) so the finding id names the actual failure" |
| AF3b two corrections, one bogus | refused BOGUS, unfiled=0 | correct | — |
| AF3c bogus pair recomputed | refused SOURCES-RECOMPUTE-MISMATCH | correct — pair path validates recomputed at pinned revs | — |
| AF3d pair filing, wrong stale pair | **exit 0, filing silently dropped** | **ROUTED R3** | "a pair-form R53-CORRECTION filing whose stale pair differs from the annotated pair is refused (PAIR-FILING-INERT), never silently dropped" |
| AF3e bogus pair recomputed, annotation in reach | exit 0 | named limit confirmed (historical note) | optionally audit pair filings independent of the annotation trigger |
| AF4a fake pointer | exit 0 | named limit confirmed (path:line exemption) | disclosed; wording already names the exemption |
| AF4b pair without 'rows' | **exit 0** | **ROUTED R4** | "the UNFILED class matches `corpus/SOURCES.md <A> -> <B>` with or without the unit word (`rows?` made optional in PAIR_ANNOT_RE)" |
| AF4c PROVINCE.md annotation | exit 0 | named-limit scope confirmed (PAIR_SITES only) | "pair-form annotations are scanned in every lane file, or the limit names the two-file scope explicitly" |
| AF4d pair line inside a fence | **exit 1 false positive** | **ROUTED R6** | "the PAIR_SITES scan skips lines hidden by the same hidden_lines() grammar applied to CORR_FILE (fenced examples are not annotations)" |
| AF4e line drift (2527->2528 class) | refused UNFILED at the NEW line; orphan filing silent | correct refusal; orphan nuance | "an orphaned pair filing whose annotation moved produces its own finding (or is folded into UNFILED's detail)" |
| AF4f README scan | refused UNFILED | correct | — |
| AF4g1/g2 boundary | exit 0 / refused | correct (strict > registry_rows) | — |

## 7. Summary for the L1

- 60 counter runs, 31 distinct v3 attack states, 16 v2-arm comparisons, 13/13
  pinned selftest pass, carry-over clean, v2-arm acceptance control intact
  (exit 0 on all of F7–F12b): **the C1 v3 claim as frozen is not vacuous and
  holds on its own fixtures.**
- No attack makes v3 exit 0 on F1/F12b or exit 1 on a real green lane state in
  my probes; the exit-0 acceptance defects below live on new states the frozen
  fixture matrix does not cover.
- **Routed defects for r55 (6 classes, none editable this round — frozen
  bytes):**
  - R1 hidden-correction swallow (AF1e2, AF1e3): correction-shaped lines with
    any prefix (one-line HTML comment, 1–3 leading spaces) never lex as
    filings; `hidden_lines()` is audited only against parsed filings → exit 0
    on agreeing sites. v2 inherits this.
  - R2 dual-anchor aliasing (AF2d): only the first anchor occurrence per site
    line is judged; a second annotated anchor's lie is invisible. v2 inherits.
  - R3 pair-filing stale drop (AF3d): a pair filing whose stale pair ≠ the
    annotated pair is silently ignored (no INERT analog).
  - R4 rows-word dodge (AF4b): `corpus/SOURCES.md N -> M` without "rows"
    escapes UNFILED.
  - R5 fence over-hide vs CommonMark 0.31.2 (AF1f2 4-space indent, AF1g
    backtick-in-info): v3 refuses content CommonMark shows (false
    CORRECTION-IN-FENCE).
  - R6 PAIR_SITES scan does not hide-fence (AF4d): UNFILED fires on fenced
    code examples (false positive).
- Named limits CONFIRMED by attack (behavior matches the disclosed limit):
  AF4a (path:line pointer exemption), AF4c (two-file scan scope), AF3e
  (historical notes not re-derived), AF2c (beyond-zone token ignored → exit 2
  CANNOT-EVALUATE, not acceptance).
- Honest notes: (i) isolated fixtures use rev==base to mute DELETED-LINES
  mutation noise (disclosed per-run in receipts); (ii) my AF1f4 pre-run
  prediction was wrong — v3's `ln.rstrip()` strips trailing tabs and the
  observed behavior is CommonMark-correct; the report records the observation,
  not the prediction; (iii) the attack driver script lived in scratch and was
  deleted with it; each receipt embeds the full command line and the complete
  fixture tree at tip, so every attack is reproducible from its receipt alone.

Receipts: `.ufo/waves/round-54/w1/S54reviewer01/receipts/` —
`00-v3-selftest.txt`, `01*-commonmark-clauses.txt`, `02-driver-log.txt`,
`summary.tsv`, `carry-v3-F*.txt` (13), `v2arm-*.txt` (7), `AF1*-AF4*.txt` (40).
