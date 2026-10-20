# SiblingOverlap — round 16 (R6 cross-domain evidence line)

**Seat:** connector (leaf). **Axes in play:** adjacency (judged), calibration C2 (attribution
accuracy); C1 operability is not touched by this seat. **Method:** exact-path reads of
`MANIFEST.json` roster/notes, all 21 lane `PROVINCE.md` files (first 60 lines), and the two
gate-bearing `SKILL.md` files (`tameshi`, `kumitate`, first 60 lines), plus exact-file greps on
those same files to resolve line numbers (no recursive search, no lane tree walks, no sibling gate
execution). Citations past line 60 are marked with their file and were resolved by exact-file
grep; every claim below is a quotation or a direct boundary read.

## 1. Surface map — who owns what this round touches

| Surface touched by r16 | Owning sibling | Evidence pointer (verbatim boundary) | Disposition |
|---|---|---|---|
| **Repo hygiene census** (C1 `tools/souji-census.sh`) | **souji** — no sibling claims it | `souji-shokunin/PROVINCE.md:19-22` (work surfaces: fleet root + lanes), `:52-57` (F1/F2 frontier); prior sweep `:69-70` "no sibling claims F1/F3/F4 ground". tameshi lists other lanes' census gates as read-only *primary surfaces* (`tameshi-shokunin/PROVINCE.md:28-33`) but not souji's, and refuses product gates: ":14-17 every lane's gate remains its own … Never edits a sibling's gate code". | Souji-owned; tameshi gets method advice only, by offer. |
| **Landing / round gate** (C2 `tools/souji-landing-gate.py`) | **kumitate** owns the fleet's `round-gate` instrument; **integrator** owns fleet conformance | `kumitate-shokunin/SKILL.md:601` registry row `round-gate` (`kumitate-round-gate-v1`); `:727-731` "audits THIS lane's own round artifacts — a tripwire + integration smoke, not a guarantee", boundary drawn against "the integrator's fleet-conformance step"; `:622-624` checklist. | Souji may audit its own artifacts; must not present as fleet conformance nor as kumitate's gate. |
| **Frozen pins** (C2 detector 2; R4 re-pin) | **tameshi** owns pin classification; each lane owns its own pins | `tameshi-shokunin/PROVINCE.md:51-57` seven legs, `round-gate.mjs` pinned at rev `364f1d5…` / blob sha256 `f890e277…`, leg `js-round-gate`; `SKILL.md:150-157` committed bytes only, "a pin on uncommitted bytes is a false anchor"; `:941-948` `git show <rev>:<path>`, pin mismatch = SETUP refusal; `:1033-1035` `current`/`stale`/`drift`; `:1083-1086` re-pin rule. Second independent encoding: `tsukuroi-shokunin/SKILL.md:706-709` two sweeps = two pins, never merged, both cite committed bytes. | Souji's detector must adopt tameshi's rule and vocabulary; no new pin taxonomy. |
| **Git config semantics** (C1 `hooksPath`/`fsmonitor`/`alternateRefsCommand`/`promisor`/`partialClone` inert) | **unclaimed** fleet-wide | All 21 lane `PROVINCE.md` files were read at first 60 lines and the 13 roster domains (`MANIFEST.json` roster) consulted; none declares git-config semantics. Nearest: `kumitate-shokunin/PROVINCE.md:21` "Isolation substrates for parallel agents (git worktrees, harness isolation backends) — `corpus/SOURCES.md` rows, queued" (frontier, queued, not owned); `kumitate-shokunin/PROVINCE.md:24` adjacent scope "reported, never absorbed". The fleet's existing disposition for genuinely unowned ground is escalation, not absorption: `kengaku-shokunin/PROVINCE.md:24-25` "the model-serving plane … no lane owns it; escalate to the integrator instead of remediating". | Souji's inertness is a **census-scope statement**, not git-config domain knowledge; leave the hook for kumitate's queued frontier. |

Non-overlaps confirmed: mori already bounds souji to artifacts, not fleet health
(`mori-shokunin/PROVINCE.md:69`, citing `souji-shokunin/PROVINCE.md:40-41`); kagi's census is
credential-surface (`tameshi-shokunin/PROVINCE.md:31`; `kagi-shokunin/PROVINCE.md:45-53`
`surface-census.sh` / `scope-gate.sh` / `claim-ledger.sh`), not repo hygiene; revenger/kaidoku own
Evidence-ID ledgers for shipped artifacts, not committed-byte pins
(`revenger-shokunin/PROVINCE.md:1-7`; `kaidoku-shokunin/PROVINCE.md:3-10`).

Pin checkers are **plural and lane-local**, which is why only the classification is tameshi's:
tsukuroi's own sweeps must "cite committed bytes" (`tsukuroi-shokunin/SKILL.md:706-709`), kumitate
pins `pin.*` sha256 in its proxy stanza (`kumitate-shokunin/SKILL.md:781-782`), kotoba ships
`verifiers/check_substrate_pins.py` over skill/AGENTS substrates
(`kotoba-shokunin/PROVINCE.md:14`), kama pins baseURLs rather than bytes
(`kama-shokunin/PROVINCE.md:11`). A souji pin detector is a fifth lane-local instance, not a new
fleet instrument. Likewise the game lanes explicitly refuse harness/evidence auditing
("harness-integrity, gate-evidence, rlm-dispatch") — `game-dev-2d-shokunin/PROVINCE.md:10`,
`game-dev-3d-shokunin/PROVINCE.md:34-35` — so no sibling gate claim collides with souji's.

## 2. The one cross-domain evidence line (R6)

CROSS-DOMAIN: frozen-pin and round-landing-gate validation are split-owned — pin classification and its refusals are tameshi's (a dirty-byte pin is a false anchor; a rev/blob mismatch is SETUP, not a verdict), the fleet's `round-gate` instrument is kumitate's lane-scoped `round-gate.mjs` (explicitly not a fleet-conformance guarantee), and souji's `tools/souji-landing-gate.py` therefore checks only souji's own r15 pins, reads them via `git show <rev>:<path>`, cites tameshi's rule, and claims neither mutation-leg status nor fleet landing conformance — evidence: `tameshi-shokunin/PROVINCE.md:51-57` (kumitate `scripts/round-gate.mjs` at rev `364f1d5…` / blob `f890e277…`, ledger leg `js-round-gate`), `tameshi-shokunin/SKILL.md:150-157,941-948,1033-1035`, `kumitate-shokunin/SKILL.md:727-731`; reported, not absorbed.

## 3. Second-order effects and risks

- **Contract — name proximity.** `souji-landing-gate.py` sits one noun away from kumitate's
  `round-gate.mjs` / `kumitate-round-gate-v1`. A closure reader can read "landing gate green" as
  fleet conformance. Required: one scope sentence in the tool header and in the r16 report —
  "audits souji's own round artifacts only; not `kumitate-round-gate-v1`, not fleet conformance"
  (boundary source `kumitate-shokunin/SKILL.md:727-731`).
- **Runtime — pin resolution.** If the pin detector hashes working-tree bytes, it re-creates the
  r15 defect class it is meant to catch. It must resolve `git show <rev>:<path>` and compare the
  blob sha256, and must report a missing repo/rev/blob or a mismatch as could-not-evaluate/SETUP,
  never as a red/green verdict (tameshi `SKILL.md:941-948`, `:1033-1035`). Red on historical
  `b410186` is a *historical* pin reading, not evidence about current bytes (`:1083-1086`).
- **Verification — do not absorb a ledger leg.** Tameshi's seven-leg ledger lists
  kumitate/kagi/tsukuroi/mado gates, not souji's (`PROVINCE.md:28-33`, `:51-57`). If souji wants
  its gate swept, that is an **opt-in offer** carrying a pinned revision, one-command hermetic
  suite and recorded expected table; the service never edits or re-pins a gate and no opt-in means
  no sweep (`tameshi-shokunin/SKILL.md:806-825`, `:823-825`, `:1258-1262`). Claiming a kill rate
  without that is an overreach.
- **Calibration — per-detector provenance.** C2's three detectors have three owners of provenance:
  parse check (GNU Bash `set -n`, souji SOURCES row), pin check (tameshi rule above), lesson-carry
  check (souji's own R3 contract). Attributing all three to one source would overstate novelty;
  attribute each, and do not claim the pin check as new method.
- **Calibration — the reusable-lesson bar.** The r14 value-blind harm is a census blind spot, and
  tsukuroi already routes that question class to tameshi: ADJ-07 "ask for method advice, not
  transfer of gate ownership", with the minimum packet (failing behavior, command/exit, measured
  census revision, expected invariant) — `tsukuroi-shokunin/PROVINCE.md:52`. Souji keeps the
  repair; a general lesson needs two independent lanes (`tameshi-shokunin/PROVINCE.md:14-16`).
- **Surface — kumitate's named gap, not souji's closure.** kumitate's SKILL carries the named gap
  "no gate yet ships the §Gate standard 'two evidences' frozen-snapshot run with a
  digest-pinned expected-verdict file" (`kumitate-shokunin/SKILL.md:607-608`) — read in lane
  scope, as its own gate set's gap. A gate that is red on a retained historical revision and
  green at round end is that *shape*; report it as an offer to tameshi, never as closing
  kumitate's gap.
- **Surface — git config.** `hooksPath`/`fsmonitor` alter command execution and therefore bear on
  worktree isolation, which kumitate holds as a **queued frontier** row
  (`kumitate-shokunin/PROVINCE.md:21`). C1's "inert" is true only for census counting; the r16
  report must not generalize it into git-config semantics. Report the adjacency, do not write the
  knowledge.
- **Surface — health framing.** C1's single whole-run exit 2 (protected-namespace reach) is a
  census verdict, not host/fleet health. Mori owns process/fleet health and already records the
  boundary (`mori-shokunin/PROVINCE.md:69`); do not route it there and do not read
  `.ufo/state` / watchdog state for it.

## 4. Verdict

Adjacency classified: 3 of the 4 named surfaces have a named owning sibling; **git config
semantics is unclaimed** and its nearest claimant is a queued kumitate frontier row. No contested
code and no sibling edit is needed: tameshi refuses sibling gate code
(`tameshi-shokunin/PROVINCE.md:14-17`), kumitate's gate is lane-scoped
(`kumitate-shokunin/SKILL.md:727-731`), and mori already concedes the artifact/fleet split
(`mori-shokunin/PROVINCE.md:69`). The cross-domain line above is reported for the r16 report and
for tameshi's intake, not absorbed into souji's claims.

STATUS: none

## Commands

```bash
cat /home/vgpnk/Projects/shokunin/MANIFEST.json | head -c 4000
ls /home/vgpnk/Projects/shokunin/
ls -1 /home/vgpnk/Projects/shokunin/*/PROVINCE.md 2>/dev/null; echo ---; ls -1 /home/vgpnk/Projects/shokunin/*/SKILL.md 2>/dev/null
python3 - <<'EOF'
import json
d=json.load(open('/home/vgpnk/Projects/shokunin/MANIFEST.json'))
for r in d['roster']:
    print(r['id'], '|', r['name'], '|', r['domain'])
print('---keys---', [k for k in d.keys()])
EOF
ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1/ 2>&1; echo "rc=$?"
ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1/SiblingOverlap.md; echo "---"; ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/souji-shokunin 2>&1 | head -5; echo "---"; wc -l /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-16/w1/SiblingOverlap.md
```

Tool-level reads/greps (not shell), all on exact named paths: `read` on
`shokunin/MANIFEST.json`; every lane `PROVINCE.md` first 60 lines —
`tameshi`, `tsukuroi`, `chousa`, `kumitate`, `kotodama`, `mori`, `mado`, `revenger`,
`kaidoku`, `kagi`, `kama`, `kengaku`, `lore`, `tabi`, `audio`, `game-dev-2d`,
`game-dev-3d`, `kake`, `kasegi`, `kotoba`, `souji` — plus
`.../tameshi-shokunin/SKILL.md` and `.../kumitate-shokunin/SKILL.md` first 60 lines; `grep` on the
same exact files plus `.../tsukuroi-shokunin/SKILL.md` and `.../kotoba-shokunin/PROVINCE.md` to
resolve cited line numbers. No recursive search, no whole-lane sweep, no sibling gate run, no
census against a real directory. Citations past line 60 come from those exact-file greps.

