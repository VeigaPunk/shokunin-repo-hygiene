STATUS: DONE — the whitelist is exact only after it trusts unvalidated spec fields; protected-tree writes can be falsely cleared.

# Findings

1. **High — `OWN ONLY` can exempt protected paths, contrary to the brief.** `run()` extracts `owned_paths()` from the item prompt and includes every result in `allowed` (`tools/souji-seat-audit.py:114-118,303-324,272-278`). There is no `tools/`, `tests/`, `census/`, or `corpus/` deny check before this allow-list. The existing selftest explicitly expects a write to `lane/tools/x.py` to be clean when supplied as an owned path (`tools/souji-seat-audit.py:347`). This contradicts both the ExecAuditShapes brief (`.ufo/waves/round-19/w1-spec.json:128-133`) and Q38 (`corpus/QUALITY.md:92`). A protected-path write must remain major even when the prompt lists that path as owned.

2. **High — `name` and `reportDir` can redirect the exact allow-list into `tools/` or `corpus/`.** `run()` interpolates `spec["reportDir"]` and `item["name"]` directly into `report` and later derives sibling suffix paths from it (`tools/souji-seat-audit.py:303-324,272-278`). `target_verdict()` only calls `os.path.normpath()` and then compares the normalized target to normalized allow-list entries (`tools/souji-seat-audit.py:121-127,191-220`). It does not validate either metadata value or reject `..`. For example, with lane `/L` and the normal report directory `.ufo/waves/round-19/w1`, an item name `../../../../tools/escape` yields a normalized report at `/L/tools/escape.md` and an allowed sibling `/L/tools/escape.patch`; a corresponding name targeting `corpus/knowledge/escape` does the same. A `reportDir` of `tools` or `corpus` directly moves the report and suffix allow-list there. Thus exact equality does not help when the values used to construct the approved path are themselves attacker-controlled. `name` also selects the transcript path at line 313, so traversal can reroute the identity lookup as well.

3. **High — the allow-list is lexical and cannot enforce the no-symlink requirement.** `_norm()` is `normpath`, and `_under()` is a string-prefix-with-component-boundary check (`tools/souji-seat-audit.py:121-127`); neither observes filesystem identity. An allowed report directory, parent, final `.patch`/`.py` target, or scratch path may be a symlink into a protected tree and will still compare as the authorized lexical path. The current audit cannot distinguish this from a regular file path. Q38 explicitly excludes symlink escape (`corpus/QUALITY.md:92`), but neither the implementation nor the external fixture checks one.

4. **Medium — the external fixture does not falsify the path-boundary attacks.** It exercises only a normal `Seat` name and fixed reportDir, with patch, scratch, tools, signal, and relative-target cases (`tests/fixtures/r19-seat-audit-shapes.py:71-94`). The built-in selftest adds a neighbour-stem and `tools/` case, but does not test protected paths supplied through `OWN ONLY`, hostile metadata, traversal, symlinks, or case variants (`tools/souji-seat-audit.py:431-440`). The present base-discrimination condition therefore proves patch/signal behavior, not the asserted exact-path boundary.

**Tightest acceptable predicate:** first validate the identity inputs; `name` must be one safe ASCII component (no slash, backslash, `.`/`..`, or path punctuation), and `reportDir` must be the canonical relative wave-report shape `.ufo/waves/round-<digits>/w<digits>` with no absolute path, parent component, or symlinked ancestor. Derive the report and only the contract-approved same-directory sibling names from those validated values. Compare canonical path identity exactly, reject any target containing `..`, and fail closed if an existing component is a symlink or resolves outside the lane. Check protected roots (`tools/`, `tests/`, `census/`, `corpus/`) before any ownership exception; under the current ExecAuditShapes/Q38 wording, an `OWN ONLY` entry is not authority to waive that deny rule. The scratch allowance likewise needs a validated seat name, exact `/var/tmp/souji-r<round>-<Name>/` component boundary, and no traversal or symlink escape. Exact equality already avoids ordinary prefix confusion; it does not cure metadata traversal or symlink aliases.

**Fixture cases required:**

- Positive controls for the exact own report and exact own sibling artifacts; positive own-scratch path, plus a similar-prefix/other-seat scratch denial. The original ExecAuditShapes brief permits `.md`, `.patch`, and `.py` (`w1-spec.json:133`); the later Q38 row also lists `.json`, `.tsv`, and `.txt` (`corpus/QUALITY.md:92`). Resolve that contract drift and cover every permitted suffix, with at least one unsupported suffix denied.
- Deny each protected root (`tools/`, `tests/`, `census/`, `corpus/`) under valid name/reportDir, including `tools/` and `corpus/` paths explicitly present in `OWN ONLY`.
- Reject malformed names, including slash-containing names and `..` names which make the generated `.md` or `.patch` land in `tools/` and `corpus/`; reject reportDir set directly to each protected directory and reportDir values containing parent/absolute-escape components.
- Reject a written target containing `..` even when lexical normalization lands back on an otherwise approved sibling; include a traversal that lands in each protected tree.
- In an isolated synthetic lane, check both a symlinked report-directory ancestor pointing into `tools/` or `corpus/` and a final own-suffix symlink pointing there; include a symlink escape under scratch if scratch remains authorized.
- Deny case-only changes to the seat name, suffix, and report directory on the canonical Linux runtime; if case-insensitive filesystems are supported, test an actual case-folding alias there rather than assuming string comparison models filesystem identity.
- Deny neighbour and near-prefix targets (`Other.patch`, `SeatExtra.patch`, `Seat.patch.bak`, and a descendant under `Seat.patch/`), plus an unrelated lane file renamed with `.patch`. Keep exact sibling positive controls and the existing base-arm discriminator controls.

**Reachability summary:** with a valid, fixed single-component seat identity and reportDir, `.patch` does not authorize an arbitrary lane path; exact equality limits it to that sibling. With unvalidated `name`/`reportDir`, `..`, an owned protected path, or a filesystem symlink, it can be laundered into a protected target. Case folding alone is not an observed bypass on the current Linux runtime: `normpath` remains case-sensitive here, and exact equality denies a case-only string change. Ordinary prefix extensions are also denied by exact equality; the existing neighbour test covers only one such variant.

# Evidence

- Worktree diff against `3ab2c81` adds the delivery suffix set and extends the auditor allow-list; no metadata or filesystem validation is added (`git diff 3ab2c81 -- tools/souji-seat-audit.py tests/fixtures/r19-seat-audit-shapes.py corpus/QUALITY.md`).
- Auditor allow-list and path normalization: `tools/souji-seat-audit.py:114-127,191-242,272-324`.
- Protected-path false negative in the selftest: `tools/souji-seat-audit.py:347`.
- Current external fixture's fixed five cases and spec: `tests/fixtures/r19-seat-audit-shapes.py:71-94`.
- Changed suffix list and boundary selftests: `tools/souji-seat-audit.py:105-107,431-440`.
- Authorization texts: `.ufo/waves/round-19/w1-spec.json:128-133`; `corpus/QUALITY.md:92`.

# Commands run

- Read-only `git diff --no-ext-diff --unified=8 3ab2c81 -- tools/souji-seat-audit.py tests/fixtures/r19-seat-audit-shapes.py corpus/QUALITY.md`.
- Static reads of the auditor, fixture, wave specs, and Q38 criterion; literal location searches for the task brief and Q38 row.
- No tests, fixture, selftest, build, or runtime checks were executed; no output is claimed.

# Contract compliance

- No subagents, git/jj mutations, live census, signal calls, lane edits outside this report, or tool installs.
- No scratch files created. PACMAN remained untouched.
- LSP was unavailable: `read xd://lsp` returned `No such tool`, and the mounted-device inventory contained no LSP device. Accordingly, semantic references/definition/diagnostics were not available; the code review uses the cited source and fixture bytes. Literal grep was used only to locate the task and criterion lines after that unavailability.
- One canonical changed path was reviewed: `main()` → `run()` → `audit_seat()` in `tools/souji-seat-audit.py`. Same-identity routing is not safe because `item.name` is reused for transcript lookup and report construction without validation. No saturation claim applies to this path review and none was measured.
