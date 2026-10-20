# DraftSkillCensusFinal — SKILL.md draft: "Census config semantics (r16)"

Scope: draft the subsection from the census header at HEAD, including what `error` and `status-unverifiable` rows mean. Attacks: calibration of the header's stated semantics against the emitting code. Writes only this report.

Anchor: lane HEAD a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae; `tools/souji-census.sh` sha256 64a60fd0b0ed410125e9e06c02bcf6ddb7f398708de89d54bc30eaff7fe8d07c (matches the r16 pin).

## Draft subsection (≤20 lines)

### Census config semantics (r16)

Per repository, `tools/souji-census.sh` takes one of four outcomes:

- **Refused** (whole run, exit 2, stderr `path-protected`): a config-named path (include target, core.excludesFile, core.attributesFile, core.worktree) overlaps a protected root. No census is emitted.
- **`error` row** (that repository only, exit 0, no git command runs in it, stderr `config-unsupported: <reason>`): `~user`/`%(prefix)` paths; unresolvable or ambiguous config paths; include cycle or depth over 10; non-regular or hardlinked include or config.worktree target; NUL bytes or unparsable config; invalid extensions.worktreeConfig boolean. Numeric columns are 0 placeholders and mtime_iso is empty. The row is not a measurement and never carries `clean`.
- **`status-unverifiable`** (that repository only, `git status` skipped): a filter.<name>.clean|smudge|process driver bound by an attributes source to a tracked path, an effective excludes/attributes value that cannot be modelled or is non-regular (stderr `status-skipped`), or an invalid promisor boolean that makes git status fail. Worktree, unpushed and scratch figures are still measured. The `dirty` column prints 0 but means *unknown*.
- **Accepted, not degraded**: any core.hooksPath or core.fsmonitor (neutralized via GIT_CONFIG_COUNT); remote.*.promisor and extensions.partialClone (GIT_NO_LAZY_FETCH=1); core.alternateRefsCommand; unbound filter drivers; missing include targets; boundary-clean excludes/attributes files.

Reading a row: `clean` requires unpushed=0, dirty=0, a remote-tracking ref, and no `error`, `status-unverifiable`, `not-a-repo`, `no-remote`, `unpushed` or `dirty` flag. Any `error` or `status-unverifiable` flag means the row is unverified, not clean: resolve the named cause before trusting its numbers. Only a protected-path refusal stops the whole run.

## Findings (code vs header)

F1 — `dirty=0` placeholder is ambiguous in the TSV. `tools/souji-census.sh:1224-1226`: on `dirty=unverifiable` the code sets `dirty=0` and adds `status-unverifiable`. The header (line 104) says "dirty unknown", but the TSV column reads `0`, identical to a measured zero. Verdict: holds for `clean` gating (line 1236 withholds `clean`); partial for TSV readability. Smallest fix: document in the header (line 35-39) that `dirty=0` plus `status-unverifiable` means unknown, or emit a non-numeric token; the SKILL draft above carries the rule meanwhile.

F2 — `error` has undocumented emitters. The header (lines 97-99) attributes `error` only to config degradation. The code also emits `error` for: `git rev-parse --is-inside-work-tree` failure (`:1194-1196`, a plain row with 0 placeholders); non-numeric worktree/unpushed/scratch counts (`:1212-1214`, adds `error` and zeroes the field, row still gets other flags). Verdict: fails as documentation (behaviour is safe: `error` still blocks `clean`). Smallest fix: extend header line 97 to "or a work tree git cannot read, or a non-numeric count". The draft above says "config" only where the header does; SKILL.md should carry the widened definition once the header is fixed.

F3 — `.git` symlink vs header text. Header lines 83-84 say "a .git symlink is not followed as a row", but `:1183-1185` emits a row tagged `not-a-repo` for a `.git` symlink, and `:1187-1191` does the same for a missing `.git`. Verdict: partial (not followed, but a row IS emitted). `not-a-repo` appears in the vocabulary (line 52) with no description. Smallest fix: header line 83-84 → "a .git symlink or missing .git emits a `not-a-repo` row and is not followed"; add a one-line definition of `not-a-repo` next to `error`.

F4 — `dirty` on `error` rows. `:1180`/`:1195` print `0 0 0 0` plus empty mtime, so an `error` row also reads `dirty=0`. Same ambiguity as F1; the SKILL draft's "Reading a row" paragraph covers it (`error` ⇒ not clean, numbers not measured).

## Verification performed

- Read header lines 1-153 of `tools/souji-census.sh` (exact file).
- Grepped the exact file for `status-unverifiable|error`; read `:1169-1235` to confirm emitter lines.
- Hash and HEAD confirmed as above. No census run, no edits to lane files, no git mutation.
- No tool installs or upgrades in this assignment.

## Out of scope

- The `#` header `--compare` and selftest semantics are not drafted here.
- SKILL.md target file was not located by me; the subsection is delivered as text for L1 to place.

STATUS: ok — draft delivered; F1–F3 are advisory calibration findings against the header, not failures of the tool.

## Commands

git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD && sha256sum /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-census.sh
