# AlternateRefs — souji round 15, w1 (reviewer seat)

Axes: operability (C1), calibration (C2). Scope: `core.alternateRefsCommand` in `tools/souji-census.sh`.
Method: source inspection only. No tests, builds, probes, or census runs. Nothing edited outside this report.
Source present: yes. Upstream git source was read by read-only `curl` of raw files on GitHub (`odb.c`, `run-command.c`, `revision.c`, `fetch-pack.c`, `builtin/receive-pack.c`). Local git observed as `2.55.0` at `/usr/bin/git` via `git --version` only.
Tooling: nothing installed or upgraded.

## Findings

### F1 — HIGH (operability): value-blind refusal on key presence
- `tools/souji-census.sh:500` lists keys with `git config --file "$cfg" --no-includes --name-only --list`. Only names are captured, never values.
- `tools/souji-census.sh:503-506` lowercases the list and refuses on `*core.alternaterefscommand*`. Any presence refuses, including an empty value, `exit 0`, or a harmless wrapper.
- Documented as refusal in `tools/souji-census.sh:85-88` (header), `SKILL.md:216-220`, and `corpus/lessons/round-14.md:92-95`. Those same surfaces describe the refusal as an operability boundary. The round-14 reject is the harm this round must repair.

### F2 — census never reads or executes the value (refusal is unnecessary for census)
Census git invocations (all `git` calls in the tool, excluding fixture setup):
- config: `:500`, `:511` (`--file`, `--no-includes`, read-only)
- status: `:710-712` (`-c core.fsmonitor=false -c core.hooksPath=/dev/null -c core.excludesFile=/dev/null -c core.attributesFile=/dev/null status --porcelain`)
- worktree list: `:688`, `:836`
- for-each-ref refs/remotes: `:694`
- rev-list: `:698` (`--count --branches`), `:702` (`--count --branches --not --remotes`)
- rev-parse `--is-inside-work-tree`: `:859`
- fixture-only writes: `:1157-1171`, `:1203-1231`, `:1253-1271`

None passes `--alternate-refs`, and none runs fetch, push, fetch-pack, upload-pack, or receive-pack.

Upstream git (master, fetched 2026-10-20):
- `odb.c:115-131` `fill_alternate_refs_command()` reads `core.alternateRefsCommand`. If set, it runs the value through the shell with the alternate path as argument. Otherwise it runs `for-each-ref`.
- `odb.c` `read_alternate_refs()` is the only consumer of that command. It is reached through `odb_for_each_alternate_ref`.
- Callers seen in the fetched files: `fetch-pack.c:119`, `builtin/receive-pack.c:346`, `revision.c:1891` (via `--alternate-refs` at `revision.c:2945-2946`).
- The census invokes none of these. Upstream `builtin/rev-list.c`, `log.c`, `shortlog.c`, `fetch.c`, `for-each-ref.c`, `worktree.c`, `upload-pack.c`, `connected.c`, and `transport.c` contain no such call in the fetched files. This is not an exhaustive tree enumeration.

Conclusion: in the census's command set, the value of `core.alternateRefsCommand` is never executed. A blanket refusal buys no safety in the current tool. Dropping it is consistent with the task's "reject unnecessary blanket refusal".

### F3 — empty and benign values are inert in any consumer that does run (INFERENCE, source-read only)
- `odb.c:121-124`: an empty value is still "set", so `argv = ["", <alt path>]` with `use_shell=1`.
- `run-command.c:288-309` `prepare_shell_cmd()`: `strcspn("", …) == strlen("")`, so no shell wrapper is added. `execvp("")` fails. The child is never run.
- `odb.c` `read_alternate_refs()`: `if (start_command(&cmd)) return;` ends the walk. Expected result: a `cannot run` error on stderr and zero alternate tips. Exact message and exit code not observed (no probe run).
- `exit 0` and wrapper values: run only in a consumer, emit zero or valid tips, and execute nothing unexpected.
- Edge (INFERENCE): a whitespace-only value routes through `sh -c '<v> "$@"'`, which would execute the alternate path itself as a program. Reachable only in a consumer, which the census never runs. No census impact.

### F4 — calibration: refusal has no paired evidence
- No fixture, self-test, or doc example covers `core.alternateRefsCommand` in either direction. Searched: `tools/`, `tests/`, `SKILL.md`, `corpus/`. Self-test region checked: `tools/souji-census.sh:1399-1468`.
- The refusal is therefore an unpaired assertion: no red control (refusal fires on a case that must refuse) and no benign control (refusal must not fire on a benign value). Under the C2 admission rule it is not calibration evidence in either direction.

### F5 — MEDIUM: the source audit does not cover the consumers that would make removing F1 unsafe
- `tools/souji-census.sh:1484` forbids `fetch|push|commit|branch|checkout|reset|rebase|prune` in non-comment lines.
- It does not forbid `--alternate-refs`, `fetch-pack`, `receive-pack`, or `upload-pack`. Those are the only paths that execute `core.alternateRefsCommand`.
- Dropping the refusal is sound only while this audit holds. Extend the audit (see A3).

### F6 — LOW (calibration, same class as the `*include.*` substring over-refusal in `round-14/w1/BoundaryReviewRoot.md:158`)
- `:505` matches substrings against the full lowercased key line, so unrelated subsection names can trip the refusal.
- Not specific to alternateRefsCommand. Note it for the ConfigRepair/AdmissionRules seats.

## Recommended acceptance (design; not executed)

A1. Remove `*core.alternaterefscommand*` from the pattern at `tools/souji-census.sh:505`. Change no other key.
A2. Update the header at `tools/souji-census.sh:85-88` and the wording at `SKILL.md:216-220` to drop `core.alternateRefsCommand` from the refused set. Do not edit the round-14 record.
A3. Extend the audit at `tools/souji-census.sh:1484` to also fail on `--alternate-refs`, `fetch-pack`, `receive-pack`, and `upload-pack`. This is the control that makes A1 sound.
A4. Paired fixture, synthetic `mktemp` root only:
  - Repo `A` (alternate) and repo `R` with `objects/info/alternates` → `A`, and local `core.alternateRefsCommand = touch <SENTINEL>`.
  - Red control: the fixture runs `git -C R rev-list --alternate-refs HEAD`. The sentinel must appear. This proves the value is live where consumers run.
  - Green control: `census --root <fleet>` containing `R` exits 0, emits the `R` row, and the sentinel is absent afterward.
  - Additional green rows: `R2` with empty `core.alternateRefsCommand =`; `R3` with `core.alternateRefsCommand = exit 0`. Each emits its row with exit 0.
  - Mixed fleet: a sibling repo with no alternates config is unaffected in the same run.
A5. AdmissionChecker must reject this key's preservation evidence if the red control or the sentinel-absent green control is missing (green-only is not admitted).
A6. Keep every other refusal in the list unchanged. Any change to the other keys is out of scope for this seat.

## Residual risk
- Census safety for this key depends on the census never invoking an alternate-ref consumer. A4's green sentinel check and A3's audit are the only guards. Future census edits that add `--alternate-refs` or a fetch-family call would re-open execution of a hostile repo's configured command. A3 must hold.
- Upstream surface (git 2.55 observed locally; master fetched) could move consumers. Re-check on git upgrades.

## Unrun checks (for L1 final acceptance)
- The A4 red/green/mixed fixture run and the extended audit (A3). Not executed by this seat.
- Exact stderr text and exit code for an empty `core.alternateRefsCommand` (F3). Not observed.
- Full upstream caller enumeration via `git grep` on a checkout. Not performed; the file list above is partial.

## Boundary disclosure (no-query rule)
- Violation by this seat, before the SoujiR15 boundary reminder: (1) `glob` of `/home/vgpnk/Projects/shokunin/souji-shokunin/**` (limit 200). Its output listed file names under `census/operator-sweep-20261019/` (for example `stage-hold-delete.sh`, `.hold.json`, `results/kotodama-chunk-*.tsv`). Names only; no operator-sweep file was opened, read, copied, or edited. (2) `grep` over the whole lane root for `alternateRefsCommand|alternateRefs|alternate_refs`, and a second case-insensitive grep for `alternaterefs|alternateRefs|alternate_refs|core\.alt` over the whole lane root. Hits returned only from `.ufo/waves/round-14`, `.ufo/waves/round-15`, `tools/`, `corpus/lessons/`, and `SKILL.md`; the operator-sweep directory was not excluded by either pattern, but no hit from it was shown. (3) `grep` for `value-blind|rejected-harmed|harmed|git-config-unsupported|name-only` over the whole lane root; its output included `census/round-1` and `census/round-13` seat files. (4) `grep` for `AlternateRefs|alternateRefs` under `.ufo/waves/round-15` (scoped, not a violation). No further whole-root or census-recursive calls were made after the reminder.
- Limitation: the grep and glob results may contain operator-sweep content I did not inspect; the findings above rely only on `tools/souji-census.sh`, `.ufo/waves/round-15/*`, `.ufo/waves/round-14/w1/*`, `SKILL.md`, and `corpus/lessons/round-14.md`, which are explicit paths. The F1–F6 citations stand on those files. Upstream git source was fetched with `curl` from GitHub, not from the lane.
