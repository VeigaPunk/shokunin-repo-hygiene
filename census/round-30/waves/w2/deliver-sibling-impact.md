# Souji round 30 w2 — sibling-impact scan (seat SwarmConnector31)

Scan date: 2026-10-26, wave 2 (falsification wave). Read-only. Scope: do sibling lanes
copy/vendor/invoke souji's `tools/souji-landing-gate.py`, `tools/souji-capability-agreement.py`
or the capture tool `tools/souji-wave-evidence-capture.sh`, or depend on `.ufo/waves/round-N/`
pointer semantics; and does the new F1 entry `corpus/knowledge/jj-keep-ref-expiry.md` (landed
C3, commit `76c94eb41fc38093d7143a016006b6275e102d5d`) overlap any sibling's PROVINCE ground.

## 1. Tool copy/vendor/invoke scan — zero hits

Greps (all read-only; lane path prefix elided here, all absolute in seat commands):

- `grep -rn "souji-landing-gate\|souji-capability-agreement\|souji-wave-evidence-capture"
  /home/vgpnk/Projects/shokunin/*-shokunin/tools /home/vgpnk/Projects/shokunin/*-shokunin/tests`
  → hits only inside `/home/vgpnk/Projects/shokunin/souji-shokunin/` (the tools themselves and
  souji's own fixtures `tests/fixtures/r16-landing-gate.py`, `r18-landing-pointers.py`,
  `r19-carry-wrap.py`, `r28-wave-evidence-capture.sh`, `r30-landing-gate-discovery.py`).
- Same pattern over `/home/vgpnk/Projects/shokunin/scripts` → no matches.
- Same pattern over `/home/vgpnk/Projects/shokunin/templates` → no matches.
- Filename sweep: `find /home/vgpnk/Projects/shokunin -maxdepth 4 -name "*souji-landing-gate*" -o
  -name "*souji-capability*" -o -name "*souji-wave-evidence*"` → no file outside souji-shokunin.
- Rename-resistance sweep: `grep -rln "landing-gate\|wave-evidence-capture\|capability-agreement"
  *-shokunin/tools *-shokunin/tests` (souji excluded) → zero hits.

Verdict: no sibling lane copies, vendors or invokes any of the three tools. The only non-souji
occurrences fleet-wide are citations in committed wave reports, all adjacent-evidence pattern
comparisons, never invocations:

- `kasegi-shokunin/.ufo/waves/round-25/wave1/ConnectorSiblings.md:21` — verbatim (13 words):
  "Landing gate runs `bash -n FILE` on candidate shell files; never executes repo code".
- `kengaku-shokunin/.ufo/waves/round-25/build/ConnSoujiKaidoku.md:20` — cites
  "souji `tools/souji-landing-gate.py:31-34`, `:217-221`" as "ADJACENT, exit-map CONTRADICTION".
- Fleet-level souji round reports (`.ufo/reports/round-16..28/souji.md`) document souji's own
  gate usage; kumitate's rounds cite souji's lessons/census as reusable patterns
  (e.g. `kumitate-shokunin/.ufo/waves/round-41/falsify/ConnSiblingOverlap.md:18` — souji
  round-19 dead-seats JSON as a fourth absent-seat class, "Knowledge only; no tool").

Consequence for the landed items: C2's gate change (committed-capture discovery) and the capture
tool cannot break any sibling — no sibling calls them. The C2 behavioral change is souji-internal.

## 2. `.ufo/waves/round-N/` pointer-semantics dependency — none

- The pointer-resolution semantics landed in C2 (gate resolves `.ufo/waves/round-N/` pointers
  through the committed `census/round-N/waves/` capture) are exercised only by souji's own
  fixtures (`tests/fixtures/r30-landing-gate-discovery.py` and the selftest inside
  `tools/souji-landing-gate.py`).
- Sibling references to `.ufo/waves/round-N/` are their own report directories in standard
  ufo-swarm layout, e.g. `chousa-shokunin/.ufo/waves/round-25/build/build-spec.json:3` —
  verbatim: `"reportDir": ".ufo/waves/round-25/build"`. None references souji's capture paths or
  exemption semantics.

Verdict: no sibling depends on souji's `.ufo/waves/round-N/` pointer semantics.

## 3. F1 entry (`jj-keep-ref-expiry.md`) vs sibling PROVINCE ground — uncontested

Souji's own ground (opened this run):

- `souji-shokunin/PROVINCE.md:63` — verbatim: "F1 git-native housekeeping vs receipts — git's
  own deleters".
- `souji-shokunin/PROVINCE.md:195-211` (round-30 boundary note) — verbatim (12 words): "F1 now
  holds a measured entry — `corpus/knowledge/jj-keep-ref-expiry.md` — beside the four". The note
  keeps F1 frontier (`frontier, entries held`), adds nothing to Core, and refuses lane-runtime jj
  authority — verbatim (23 words): "jj's own store GC stays out of scope — this lane runs neither
  `jj op abandon` nor `jj util gc` on a lane repository".
- The entry itself carries `ground: F1 — git-native housekeeping vs receipts (keep-ref expiry)`
  and the receipt-durability consequence: "A keep-only commit is not a durable receipt root."

Sibling PROVINCE scan (21 `*-shokunin/PROVINCE.md` greped for `jj|jujutsu|keep-ref|git-native|
housekeeping|garbage collect|prune|receipt`):

- kumitate-shokunin claims an "Isolation substrates for parallel agents (git worktrees, harness
  isolation backends, jj workspaces)" frontier (`PROVINCE.md:22`, verbatim quote above), advanced
  by `corpus/knowledge/jj-workspace-seat-containment.md` — seat containment: staleness rules,
  `update-stale` abandoned-file recovery, mechanism M7. Different claim class from keep-ref
  expiry. The one adjacency is `jj-workspace-seat-containment.md:102` — verbatim (15 words):
  "only `jj op abandon` + `jj util gc` or a separate clone excludes them from storage" — the
  storage-exclusion side of the same commands, not `refs/jj/keep/*` removal thresholds. Adjacent,
  reported, not absorbed; no contested scope.
- `kumitate-shokunin/corpus/knowledge/agent-isolation-substrates.md:57-59` counts "one keep-ref"
  in a snapshot census (creation-side observation), not ref-lifetime measurement.
- tsukuroi-shokunin PROVINCE: no jj/housekeeping/keep-ref ground (pacman/AUR update-safety).
  Not contested.
- kotoba-shokunin `PROVINCE.md:72` independently confirms souji's receipt-gated-removal
  ownership — verbatim (9 words): "souji owns receipt-gated removal of stale or duplicate
  artifacts".

Verdict: the r30 F1 entry sits inside souji's declared F1 frontier; no sibling PROVINCE contests
keep-ref-expiry ground. Kumitate's jj-workspace seat containment and the fleet jj helper
(`scripts/hyaku/jj-lane.sh`, covered in w1: never runs `jj util gc`/`jj op abandon`) are
complementary, disjoint surfaces.

## One bounded proposal (connector output)

Record this scan's verdict as a standing adjacency row: souji holds keep-ref-expiry mechanism
ground; kumitate holds jj-workspace seat-containment ground; either lane citing the other's
entry must route, not restate. No code, gate or counter change is proposed.

## Method / hygiene

- Read-only greps/reads/finds only; no lane or sibling file modified, no git/jj mutation.
- Installs: none (grep quirk already reported by w1 at `xd://report_issue`; directory-path greps
  worked this run).
- Scratch `/fast/scratch/hyaku/souji-r30/SwarmConnector31/` held TMPDIR only; removed after the
  run.
