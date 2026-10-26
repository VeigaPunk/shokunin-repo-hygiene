# SwarmConnector31 — sibling-impact scan, souji round 30 w2 (falsification wave)

## Status

STATUS: PASS — scan ran to completion across all 21 sibling lanes' tools/tests, fleet
scripts/ and templates/, plus a filename-copy sweep and a 21-PROVINCE ground check on the
landed F1 entry; zero contested-scope findings; every attacked item verified.

## Evidence

- Tool greps: `grep -rn "souji-landing-gate\|souji-capability-agreement\|souji-wave-evidence-capture" /home/vgpnk/Projects/shokunin/*-shokunin/tools /home/vgpnk/Projects/shokunin/*-shokunin/tests` → only souji-shokunin's own tools/fixtures; same pattern over `/home/vgpnk/Projects/shokunin/scripts` and `/home/vgpnk/Projects/shokunin/templates` → zero matches; rename-resistance sweep `grep -rln "landing-gate\|wave-evidence-capture\|capability-agreement"` over sibling tools/tests → zero; `find` filename sweep fleet-wide → no copy outside souji-shokunin.
- Wave-pointer grep: `grep -rn "\.ufo/waves/round-\|ufo/waves/round-" /home/vgpnk/Projects/shokunin/*-shokunin` → sibling hits are their own report dirs only (e.g. chousa-shokunin `.ufo/waves/round-25/build/build-spec.json:3` verbatim: `"reportDir": ".ufo/waves/round-25/build"`); none touches souji's capture/exemption semantics.
- F1 ground reads this run: souji-shokunin/PROVINCE.md:63,195-211; corpus/knowledge/jj-keep-ref-expiry.md (header + Consequence); kumitate-shokunin/PROVINCE.md:1-60; kumitate-shokunin/corpus/knowledge/jj-workspace-seat-containment.md:102; agent-isolation-substrates.md:57-59; tsukuroi-shokunin/PROVINCE.md (grep, zero jj/housekeeping hits); kotoba-shokunin/PROVINCE.md:72.
- Sibling citations of souji's gate (evidence, not invocations): kasegi-shokunin/.ufo/waves/round-25/wave1/ConnectorSiblings.md:21; kengaku-shokunin/.ufo/waves/round-25/build/ConnSoujiKaidoku.md:20.
- Read-only throughout; no installs; scratch `/fast/scratch/hyaku/souji-r30/SwarmConnector31/` (TMPDIR) removed after the run.

## Findings

1. No sibling lane copies, vendors or invokes `tools/souji-landing-gate.py`,
   `tools/souji-capability-agreement.py` or `tools/souji-wave-evidence-capture.sh`. Zero hits
   across every sibling lane's `tools/` and `tests/`, fleet `scripts/`, fleet `templates/`, and
   a fleet-wide filename sweep. Consequence: the C2 gate change (committed-capture discovery,
   landed `68447afe…`) and the capture tool cannot break any sibling — nothing calls them.
2. Sibling mentions of the gate are adjacent-evidence citations only:
   kasegi `ConnectorSiblings.md:21` verbatim (13 words): "Landing gate runs `bash -n FILE` on
   candidate shell files; never executes repo code"; kengaku `ConnSoujiKaidoku.md:20` cites
   "souji `tools/souji-landing-gate.py:31-34`, `:217-221`" as "ADJACENT, exit-map
   CONTRADICTION". Knowledge reuse, zero runtime dependency.
3. No sibling depends on souji's `.ufo/waves/round-N/` pointer semantics. Sibling
   `.ufo/waves/round-N/` hits are their own ufo-swarm report directories (chousa round-25
   spec/registry/reportDir); the capture-mediated resolution landed in C2 is exercised only by
   souji's own fixtures (`tests/fixtures/r30-landing-gate-discovery.py`, gate selftest).
4. F1 entry ground uncontested. Souji PROVINCE.md:63 verbatim: "F1 git-native housekeeping vs
   receipts — git's own deleters"; the round-30 boundary note (:195-211) keeps F1 frontier and
   refuses lane-runtime jj authority, verbatim (23 words): "jj's own store GC stays out of
   scope — this lane runs neither `jj op abandon` nor `jj util gc` on a lane repository".
5. Kumitate's nearest ground is a different claim class: PROVINCE.md:22 verbatim (10 words):
   "Isolation substrates for parallel agents (git worktrees, harness isolation backends, jj
   workspaces)" — seat containment (staleness, `update-stale` abandoned-file recovery). Its
   jj-workspace-seat-containment.md:102 shares only the command names, verbatim (15 words):
   "only `jj op abandon` + `jj util gc` or a separate clone excludes them from storage" —
   storage exclusion, not `refs/jj/keep/*` expiry thresholds. Adjacent; report, never absorb.
6. Tsukuroi PROVINCE has no jj/housekeeping/keep-ref ground (grep zero) — not contested.
   Kotoba PROVINCE.md:72 verbatim (9 words): "souji owns receipt-gated removal of stale or
   duplicate artifacts" — sibling-side confirmation of souji's scope.

## Attack log

- Attacked w1 SwarmConnector31's "no sibling references the gate/capability tools (zero hits)":
  re-ran over sibling tools/tests + fleet scripts/templates + filename sweep → HOLDS (only
  souji's own files match; sibling wave-report citations found but they are evidence citations,
  not references/dependencies; w1's scanned surfaces never included sibling `.ufo/waves`
  reports, so its claim stands on its stated scope).
- Attacked the landed C2 change for sibling impact (would the discovery change break a sibling
  reading the gate or the gitignored wave dir?) → HOLDS — zero sibling invocations; no sibling
  impact either direction.
- Attacked the landed C3 F1 entry for PROVINCE overlap (kumitate jj ground? tsukuroi?) →
  HOLDS — no contested scope; kumitate's jj-workspace containment is complementary and disjoint
  (seat staleness/files vs ref lifetime/receipt durability).
- Attacked the capture tool (`souji-wave-evidence-capture.sh`) for sibling vendors → HOLDS —
  zero hits.
- Tooling note (DEFECT-NOT-FATAL, already reported at `xd://report_issue` by w1): harness grep
  with absolute-path globs can return "No matches found" where a literal path matches; this
  seat used directory-path greps and shell grep for the sweeps, all results cross-checked.

## Deliveries

- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-30/w2/deliver-sibling-impact.md`
  — scan tables, verbatim quotes, contested-scope verdicts, bounded adjacency proposal.
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-30/w2/SwarmConnector31.md` —
  this report.
