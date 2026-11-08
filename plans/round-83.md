# Round 83 — amendments to the frozen claims (Amendment 59, pre-file falsification)

Written before the round report was filed. The frozen wording lives in `census/round-83/preregistration.txt`
(commit `fbf0ae5e4ac54eec16b9ef5f2439de2a44dfb7b0`, F) and is not edited here: each amendment records what the
round's own adversarial artifacts falsified in that wording, and the narrower sentence the round now puts its
name to. The numbers are re-derived on committed bytes by non-author seats and by the L1; records under
`census/round-83/records/` and the wave's reports under `.ufo/waves/round-83/w1/`.

Wave evidence root: `.ufo/waves/round-83/w1/`.

## A0 — C2 instrument correction, before any candidate score (not an amendment to a claim)

- **Artifact:** `census/round-83/c2-tree-walk-counter.py` (the `deep` stub) and the refreshed control receipt
  `census/round-83/controls/c2-K-a-r82-tool.txt`.
- **What was wrong:** the first frozen `deep` stub wrote its hang mark BEFORE spawning the N children; the counter
  waits for the mark and signals 0.3 s later, so under the monitor launch (job control, 24 background forks) the
  signal could arrive while the stub was still spawning and the row measured the stub's fork speed, not the tool's
  walk. Measured on the L1's reference implementation: `d24-monitor-group` left 16 survivors with the mark first.
- **Correction (commit `51b50c94d0d9a5baf3e6564d1b5dbc48b970053c`, after F and before any candidate was scored):**
  the stub spawns the children first and writes the mark last; the hang point is then a tree that already exists.
  Predicates, rows, target and commands are unchanged, and the control stays red for the same reason
  (`SUMMARY rows=20 mismatches=4 errors=0 orphans=4`, EXIT=1).
- **Disclosure:** the instrument's digest therefore post-dates F. No seat had been spawned when the correction
  landed (the wave was deferred by the host gate), so no score exists on the old bytes.

## A1 — C1: the six-shape list is over-specified; the candidate carries only the three real wave-directory shapes

- **Artifacts:** `.ufo/waves/round-83/w1/S83CriticClaims.md` A1 (a `w[0-9]+/`-only shape list passes all 36 rows,
  receipt `S83CriticClaims/c1-shapelean.txt`), A3 (the `waves|wave|records/wave-*` alternates can never change a
  verdict because the `_capture_ok` fallback runs first and already accepts them; the own tree contains none of
  those names).
- **Frozen wording falsified:** the enumeration "w1/, w2/, w3/ (w[0-9]+/), a2w1/, assimilation/, plus the r82
  capture shapes waves/, wave/ and records/wave-<w>/" presents six shapes as the agreement the population
  certifies; the population certifies `w[0-9]+` only, and three of the six are dead as decisions.
- **Correction landed (census/round-83/c1-pointer-counter.py, after the first score, comment-only + dead-code
  deletion; behaviour re-derived on the final bytes):** `OWNTREE_WAVE` = `w[0-9]+|a2w1|assimilation`; the r82
  capture shapes stay handled by the `_capture_ok` fallback before it.
- **Amended sentence:** *the own-tree branch adds a real wave-directory alternation — `w[0-9]+/`, `a2w1/`,
  `assimilation/` — followed by the token's path below its own first below-round component; the r82 capture branch
  is the `_capture_ok` fallback and keeps TF4/TF5/PF-1. On the 36-row population only `w1/` and `w2/` carry rows;
  `a2w1/` and `assimilation/` are real shapes (S331) with no row, and a `w[0-9]+/`-only list meets the same target
  (critic A1).*

## A2 — C1: the full-suffix clause is exercised one component deep only

- **Artifact:** `.ufo/waves/round-83/w1/S83CriticClaims.md` A2 (`len(got)==2 and got[1]==want[-1]` — a
  basename-only rule — passes all 36 rows; receipt `S83CriticClaims/c1-baseonly.txt`), because every own-tree
  token sits exactly one component below its wave directory.
- **Amended sentence:** *the remaining-path comparison is a full suffix in order, and the population exercises it
  only for a token one component below its wave directory; a deep-token true row and its flattened decoy are routed
  to round 84, which is what makes the suffix clause load-bearing.*

## A3 — C1: the identity disjunct is unreachable and NF-K is not its decoy

- **Artifacts:** `.ufo/waves/round-83/w1/S83CriticClaims.md` A7 (the `tt == tk` disjunct cannot fire from a MOVED
  row; NF-K is refused by the suffix comparison, not by an identity test), S83MutCounter m5 (deleting the disjunct
  changes no row).
- **Correction landed:** the disjunct is deleted from `_owntree_ok`; NF-K is re-labelled "a flattened copy at the
  round-tree root" in the population note.
- **Amended sentence:** *the own-tree branch holds no identity clause; a MOVED row cannot have target == token, so
  the r82 `tt == tk` disjunct was dead code and is removed.*

## A4 — C1: "a genuine move into a real wN/ directory" is a layout, not a recorded move

- **Artifact:** `.ufo/waves/round-83/w1/S83CriticClaims.md` A6: the lane has 65 `w1/` directories, but across the
  r77–r82 ledgers and `corpus/knowledge/obsidian-ledger.tsv` all 14 MOVED targets are `census/round-<N>/waves/…` or
  `…/wave/…`; not one ledger row has moved an artifact into a `.ufo/waves/round-<N>/wN/` directory, and the
  fixture's bytes at `.ufo/waves/round-32/w1/` are not the lane's bytes at that path.
- **Amended sentence:** *before, the rule refused a target laid out in the lane's real `wN/` directories; no
  recorded ledger move used that layout, so the delivered delta is a rule-vs-layout calibration (the layout exists,
  the move does not), and TF6/TF7 are synthetic rows over a real layout.*

## A5 — C2: the control is a load-dependent race; the fixed "mismatches=4" before is withdrawn

- **Artifacts:** `census/round-83/controls/c2-K-a-r82-tool.txt` (`mismatches=4`, load1 ≈ 250),
  `census/round-83/records/c2-before-pgrep.txt` (`mismatches=1`, load1 ≈ 56),
  `.ufo/waves/round-83/w1/S83Reviewer.md` F1 (five executions of the byte-identical control: **0, 2, 2, 2, 4**;
  on an idle host the r82 tool is GREEN: deep rows 1.8/2.0/3.8/4.6 s, `SUMMARY rows=20 mismatches=0`),
  `.ufo/waves/round-83/w1/S83CriticClaims.md` C2 (a `mismatches=2` run),
  `.ufo/waves/round-83/w1/S83ExecEvade.md` (fan24 costs 26 `pgrep` forks, 2.99–3.83 s on a loaded host).
- **Frozen wording falsified:** "K-a reports mismatches=4 on exactly the four deep rows and exits 1" — on an idle
  host the same byte-identical tool meets the target sentence, so the populated settle does not separate the two
  tools, and the claim's fixed-count before is a measurement of host load (F-2's cost scales with the host's
  process count).
- **Amended sentence:** *the r82 tool costs ≈0.16 s per tree node (1.8/2.0 s at 12 descendants, 3.8/4.6 s at 24 on
  an idle host) and crosses the 5 s settle at 24 descendants under load; the control's mismatch count over five
  executions is 0, 2, 2, 2, 4, so the round claims no fixed before-count. The separating measurements are
  structural: the `pgrep` invocation count (106–108 for the r82 tool, 0 for the candidate) and the deep-row
  signal→exit seconds (r82 1.8–4.6 s idle and ≥5 s under load; candidate 0.3–0.4 s). The after target
  `rows=20 mismatches=0 errors=0 orphans=0` stays, and the round does not claim the r82 tool is red on an idle
  host.*
- **Kill-rule consequence:** the frozen kill rule's "a K-a SUMMARY differing from the sentence" cannot be applied to
  a fixed count; the round applies it to the amended before-state (the control's distribution and the structural
  counts), and the closure sees the raw executions in the reviewer's receipts.

## A6 — C2: the starttime re-check and the as-discovered order carry no row

- **Artifacts:** `.ufo/waves/round-83/w1/S83MutTool.md` m1 (starttime re-check dropped: mutant survives all 20
  rows), m7 (a `ps` map passes all 20 rows), m8 (moving the private-file removal survives); S83CriticClaims C2
  (the safety clauses are not measured).
- **Amended sentence:** *the measured delta is the one-pass map and the deep-row settle (12/24 descendants inside
  the frozen 5 s settle, 0 survivors, both launches); the starttime re-check before each signal and the
  as-discovered kill order are code properties with no row that separates them — a pid-reuse row and a
  parent-before-child row are routed to round 84 (`plans/round-83.md` A6, lesson M).*

## A7 — C2: the pgrep count is an external probe with its own variable name

- **Artifacts:** `census/round-83/probes/pgrep-shim/pgrep` (logs to `R83PGREP_LOG`),
  `census/round-83/records/c2-before-pgrep.txt` (108 invocations, `S83Connector` §3.1), and the counter's env filter
  (`c2-tree-walk-counter.py` strips `SOUJI_*`, so the prereg's `$SOUJI_R83_PGREP_LOG` would log nothing).
- **Amended sentence:** *the `pgrep` count is measured by an external PATH shim (`probes/pgrep-shim/pgrep`, log
  variable `R83PGREP_LOG`), not by the counter: 108 invocations for the r82 tool and 0 for the candidate over the
  frozen population; the counter itself neither invokes nor asserts the shim.*

## A8 — C2: the foreground fallback is an undisclosed limit

- **Artifact:** `.ufo/waves/round-83/w1/S83Connector.md` §4: when `cli_tmp_ok` is false (TMPDIR inside, equal to or
  an ancestor of the vault directory) or `mktemp` fails, `cli_claim` runs the CLI in the foreground with no traps
  armed, so `cli_kill_tree` is never reached.
- **Amended (stated limit added):** *the foreground path (`cli_tmp_ok` false, or no private file) keeps the r82
  behaviour: no traps, no tree walk, a caller's signal during that call leaves the CLI group as at base; no frozen
  row exercises it (probe D covers the refusal, not a signal inside it).*

## A9 — C2/C1: four further narrowings the wave measured

- **Arity guard on the /proc parse (reviewer F3, MEDIUM).** The tool runs `set -euo pipefail`; a `/proc/<pid>/stat`
  read whose remainder has fewer than 20 words made `${20}` an unbound-variable fatal inside the trap handler, so
  the tool exited 1 without the `SIG` line and left the subtree alive (observed on the pre-integration draft at
  `v2-int-pid`: `survivors=2`). The landed bytes now guard both loops (`[ "$#" -ge 20 ] || continue`) in the pass
  and before each TERM and KILL; the C2 receipts were regenerated on the guarded bytes
  (`tools/souji-vault-verify.sh` sha256 `b0a5b662…`).
- **Unescaped comm and short stat lines (S83ScoutSources F-6, reviewer F3, disclosed).** The stat path emits comm
  unescaped (`proc_task_name(..., false)`, S332 lines 114-117), so a newline in comm splits the file; the
  first-line `read` then yields fewer than 20 fields and the arity guard skips that pid and its descendants — safe
  (nothing is signalled) but a hostile CLI can keep a descendant out of the map. This is a stated limit, not a row.
- **Late forks are not signalled (reviewer F8, LOW, disclosed).** The map is a snapshot; a child forked after the
  pass is never in it. The corrected `deep` stub fans out before its mark, so no frozen row can see this; it is a
  stated limit, not a claim.
- **The token's own first component is dropped unconditionally (S83ScoutDirs §3.4, MEDIUM).** `_owntree_ok` treats
  the token's first component below its round as its wave directory whether or not it is one, so a token under
  `.ufo/waves/round-<N>/records/…` or `…/decoy/…` also gets an own-tree move case (probe `fx6`: r83 returns MOVED,
  r82 REFUSED). No frozen row carries such a token, so the SUMMARY is unchanged; the prereg's limit ("a token with
  no wave directory has no own-tree move case") is corrected to "is treated as if it had one", and an `NF-L3` row is
  routed to round 84.
- **`records/wave-<anything>` (reviewer F7, LOW).** The r81/r82 `CAPTURE` literal is `records/wave-[^/]+`, so the
  sentence's `records/wave-<w>/` is a label, not a numeric requirement; tightening it to `wave-[0-9]+` would refuse
  the r78 regression row TF2 (`records/wave-a2w1/`). The sentence is amended; the rule is unchanged.
- **Freeze-check form (reviewer F4, MEDIUM).** The r83 preregistration is prose, not the r80–r82 `Round:/Base:/
  Counter:/Population:/Control:/Target:/Kill:` key-line shape, so `tools/souji-freeze-check.py` reports 13
  `FIELD-MISSING` findings and verifies nothing about this round; the numbers are pinned instead by the harness
  `POP_PIN` (`c9a6d58c…`), the counter's ROUTES table and the receipts' instrument digests. Restoring the key lines
  is routed to round 84; the prereg is frozen and is not rewritten.
