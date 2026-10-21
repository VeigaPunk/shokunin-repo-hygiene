STATUS: DONE — Static adversarial review of the wave-one scope contract and scope-sensitive items.

# Findings

## HIGH — Local reads are not bounded; sibling and fleet reads are explicitly requested

**Exploit path:** A seat can read sibling-repository source or policy files while remaining read-only. The wave-one contract prohibits writes to the fleet repo and sibling lanes, but does not prohibit reads there. `ConnRevPinSiblings` requests a read-only scan of sibling repositories; `ConnSiblingOverlap` requests a scan across the sibling-repository wildcard. Wave two repeats the sibling scan in `ConnRevSiblings` and explicitly runs `git status --porcelain` at the fleet root in `RevMisroot`.

**Evidence:** `.ufo/waves/round-19/w1-spec.json:5` (Contract); `w1-spec.json:269,605`; `.ufo/waves/round-19/w2-spec.json:5,261,461`.

**Impact:** Yes: under the current wording a seat may read beyond the Souji lane, including broad sibling source/configuration. The wave-one items limit some actions to read-only and forbid copying/contacting, but that does not bound which files are read. Wave two's read-only-git clause likewise does not limit repository root or path.

**Smallest wave-two tightening:** Add an explicit local-read boundary: only lane-root files and the seat's named scratch directory may be read/searched/listed/hashed; public documentation is limited to the exact URL named in the item. No fleet-root or sibling-repo reads, and no item overrides this. Replace `ConnRevSiblings` with an L1-provided minimal snapshot; replace `RevMisroot` with an L1-provided status receipt, or name one tightly scoped read-only exception and its exact path/command.

## HIGH — Some wave-one executor prompts name forbidden installation paths before naming the allowed report artifact

**Exploit path:** An executor can interpret the leading imperative as permission to create the target file in the lane, then also deliver the renamed artifact beside its report. For example, `ExecRevHelper` says to create `tools/souji-rev-pin.py`, `ExecCarryFixture` says to write under `tests/fixtures/`, and `ExecD2Pin` says to write under `census/round-19/`. Those destinations are expressly excluded by the shared contract; later text in each prompt instead describes delivery beside the report.

**Evidence:** `.ufo/waves/round-19/w1-spec.json:53,205,397`; shared exclusions and artifact-only rule at `w1-spec.json:5`.

**Impact:** The contract's higher-level prohibition means a compliant seat must not modify those paths, but the conflicting imperatives make unauthorized lane edits a foreseeable misread. This is a wording conflict, not evidence that such edits occurred.

**Smallest wave-two tightening:** Wave two already says reports only and no patches unless an item asks (none do). Add: “Do not create or modify any implementation/fixture path named in an item. If an item requests a proposed artifact, create it only in your named `/var/tmp` scratch and deliver only the exact artifact file allowed by the contract.” For any future patch wave, put the delivery filename first and state that the target path is for the proposal's subject, not a write destination.

## MEDIUM — Operator-sweep prohibition conflicts with a requested path-state check, and wave two's prohibition is narrower

**Exploit path:** `ScoutInherited` asks for the operator-sweep path state. A seat could satisfy that by running lane-root `git status` or another traversal that inspects the path, despite the wave-one parenthetical prohibition on opening/touching it. Wave two only says not to open the operator-sweep directory; `RevMisroot` runs `git status` from the fleet root, which may enumerate or inspect that operator-owned subtree while collecting status.

**Evidence:** `.ufo/waves/round-19/w1-spec.json:5,549`; `.ufo/waves/round-19/w2-spec.json:5,461`.

**Impact:** The wave-one wording is directly contradictory if “path state” includes metadata or traversal. The wave-two “do not open” wording does not clearly forbid stat/list/glob or a parent-root command that traverses it. No operator-sweep content was opened in this review.

**Smallest wave-two tightening:** Say “Do not open, list, stat, hash, glob, traverse, or cause any parent/fleet-root command to inspect `census/operator-sweep-20261019/`; do not report its contents or path state. L1 may provide a sanitized status fact if needed.” Remove the wave-one path-state request rather than asking seats to discover it.

## MEDIUM — `/var/tmp` does not itself establish fixture isolation

**Exploit path:** Wave two prohibits live census, but its exception permits a fleet-reading fixture if an item names an “isolated `/var/tmp` run”; `ALLOWED-EXEC` similarly accepts a private copy or isolated fixture without defining isolation. A copied script can still read live absolute paths or host `/proc`; the scratch location alone does not contain those accesses.

**Evidence:** `.ufo/waves/round-19/w2-spec.json:5` (execution exception), with `ALLOWED-EXEC` examples at `w2-spec.json:13,29,37`; the current `RevCacheDemo` command is named at `w2-spec.json:237`. Static source review of `census/round-14/cache-demonstration.py:4-10,47-48` describes that particular demo as synthetic and says it reads/writes no production data; I found no item asking to run a live census.

**Impact:** The live-census prohibition is explicit, and the current cache-demo does not appear to be a live census. The exception is nevertheless broad enough to be misread as permission to wrap live host/fleet reads in a temporary directory.

**Smallest wave-two tightening:** State that a temporary path is not isolation: any permitted execution must use only synthetic fixture inputs and private code copies, with no live process enumeration, `/proc` reads, fleet/sibling path access, or live census. Keep the exception item-specific and list its exact command and data sources.

## NO FINDING — Inherited-process signals and `/proc/*/environ`

The wave-one contract says never to signal a process and never to read `/proc/*/environ` or secret/credential content; wave two repeats the signal and environ bans. I found no item that authorizes a signal or asks to read process environments. `ExecD5Recheck` asks for a private-copy code change involving a pre-SIGKILL identity recheck and compile-only validation, not execution of the signal path (`w1-spec.json:405`). Wave-two D5 review is read/review work. The text therefore does not authorize signaling an inherited process. Keep the absolute no-signal rule; clarify that writing or compiling code containing a signal call is not authority to execute it.

## LOW — Output-path containment does not specify symlink handling

The wave-one contract scopes the report/artifact by lane-relative name and says it is resolved under the lane root; wave two names an absolute report path and bars other lane writes. Neither explicitly says to reject a symlinked destination or parent. No symlink escape was observed at this report path; this is a text-level residual, not a confirmed path issue.

**Smallest tightening:** Require the resolved destination to remain beneath the canonical lane root and reject symlinked path components. Do not follow an existing output symlink.

# Evidence

- `.ufo/waves/round-19/w1-spec.json:5` — embedded wave-one goal/contract, including report-only delivery, protected paths, process/environment/census rules, and executor-copy limits.
- `.ufo/waves/round-19/w1-spec.json:53,205,397,405,549,605` — conflicting target-path wording, D5 patch scope, operator path-state request, and sibling scans.
- `.ufo/waves/round-19/w2-spec.json:5,13,29,37,237,261,461` — wave-two execution/scope clauses and relevant items.
- `census/round-14/cache-demonstration.py:4-10,47-48` — static source description of synthetic demo inputs and no production data.
- `.ufo/waves/round-19/preregistration.txt:72-77` — wave plan context.

# Commands run

No shell commands or test/fixture commands were run. I used static reads/searches of the cited specs, preregistration, closure lesson, and cache-demonstration source only. No live census, git/jj command, network request, or process signal was made.

# Contract compliance

Wrote only this assigned report. No subagents, git/jj mutations, tool installs, operator-sweep access, `/proc` access, external repository reads, or scratch files. No public-document quote or network source was used.