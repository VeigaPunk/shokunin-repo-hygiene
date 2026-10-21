STATUS: DONE — Verified the four requested public Git documentation facts and proposed the exact C2 Git argv sequence from the observed helper; no code patch.

# Findings

- Worktree source reviewed: `tools/souji-rev-pin.py:32-38,56-60,69-83,86-147`. The helper itself requires a lowercase 40-hex string at `:32,96-103`, verifies it as a commit at `:104-109`, enumerates only `refs/heads`, `refs/tags`, and `refs/remotes` at `:33,69-83`, checks ancestry against those tips at `:113-126`, and compares only caller-supplied measured paths at `:130-147`.
- `git symbolic-ref --quiet HEAD` is a useful diagnostic for the current `HEAD`: success prints its symbolic target; detached `HEAD` is nonzero. It is not part of the helper's validation path. The helper's full-ID gate rejects `HEAD`, branch names, abbreviations, and symref names before `rev-parse`; `symbolic-ref` alone would not reject an ordinary direct branch ref name.
- `rev-parse --verify` proves resolvability/type as requested, not reachability or worktree equality. Reachability is separately established by `merge-base --is-ancestor` against tips produced only from the three allowed ref prefixes. `refs/jj` is excluded by the enumeration patterns, not by a post-hoc filter over all refs.
- The diff check is scoped to the supplied `measured_paths`, not necessarily every tracked path in the repository. With `git diff --quiet <commit> -- <paths>`, status 0 means no difference; status 1 means differences; another nonzero is a refusal/error. Untracked files are not part of this tracked-path comparison.
- The page's `rev-parse --verify` wording describes a raw 20-byte SHA-1 object ID. The exact 40-lowercase-hex policy is the observed helper's `COMMIT_RE` (`tools/souji-rev-pin.py:32`), not a universal Git object-format guarantee; do not infer SHA-256 repository support from that quote.

## Proposed exact argv sequence

The following mirrors the observed `tools/souji-rev-pin.py` helper; it is a proposal/report, not a patch. Before any Git invocation, reject unless `REV` matches `^[0-9a-f]{40}$`. For each Git process, the common argv prefix is:

```text
["git", "-C", ROOT,
 "-c", "maintenance.auto=false",
 "-c", "core.fsmonitor=false",
 "-c", "core.hooksPath=/dev/null"]
```

Then append these argument vectors in order:

```text
["rev-parse", "--verify", "--quiet", REV + "^{commit}"]
["for-each-ref", "--format=%(objectname) %(*objectname) %(refname)",
 "refs/heads", "refs/tags", "refs/remotes"]
["merge-base", "--is-ancestor", REV, TIP]     # once per valid peeled/direct TIP
["diff", "--quiet", REV, "--", *MEASURED_PATHS]  # tree_check=True
```

Require the `rev-parse` status to be 0 and its trimmed output to equal `REV`. For each `for-each-ref` row, use the peeled object name when present, otherwise the direct object name; retain full 40-hex tips. Require at least one ancestry command to return 0. For the diff, status 1 is a difference/refusal and status 0 is clean; any other nonzero is also refusal. The observed helper additionally sets `GIT_CONFIG_NOSYSTEM=1`, `GIT_OPTIONAL_LOCKS=0`, `GIT_TERMINAL_PROMPT=0`, and `LC_ALL=C` in the child environment (`:45-53,56-60`).

The separate symbolic-ref diagnostic argv, if documenting the current `HEAD` state, is the common prefix followed by `["symbolic-ref", "--quiet", "HEAD"]`; it is deliberately not an extra acceptance step in the helper sequence.

# Evidence

1. **40-hex commit/object identity — 18 words.** Quote: “Verify that exactly one parameter is provided, and that it can be turned into a raw 20-byte SHA-1”. Source: [git-rev-parse](https://git-scm.com/docs/git-rev-parse), accessed 2026-10-21; § OPTIONS, `--verify`. The same section documents the `^{type}` peeling operator used with `^{commit}`.
2. **Symbolic-ref detection — 24 words.** Quote: “Do not issue an error message if the <name> is not a symbolic ref but a detached HEAD; instead exit with non-zero status silently.” Source: [git-symbolic-ref](https://git-scm.com/docs/git-symbolic-ref), accessed 2026-10-21; § OPTIONS, `-q`/`--quiet`. Its NOTES section gives status 1 for a non-symbolic-ref name and 128 for another error.
3. **Durable-ref exclusion — 19 words.** Quote: “If one or more <pattern> parameters are given, only refs are shown that match against at least one pattern”. Source: [git-for-each-ref](https://git-scm.com/docs/git-for-each-ref), accessed 2026-10-21; § OPTIONS, `<pattern>...`. Passing only `refs/heads refs/tags refs/remotes` therefore excludes `refs/jj` by construction.
4. **Tree/worktree difference — 18 words.** Quote: “This form is to view the changes you have in your working tree relative to the named <commit>.” Source: [git-diff](https://git-scm.com/docs/git-diff), accessed 2026-10-21; § DESCRIPTION, `git diff <commit> [--] [<path>...]`. For the proposed quiet form, § OPTIONS `--quiet` says it implies `--exit-code`; § OPTIONS `--exit-code` defines status 1 for differences and 0 for none.

# Commands run

- Opened the four exact public documentation URLs above with `curl -fsS`; extracted relevant text from the saved HTML and counted quote words with Python. No other network URLs were opened.
- Read `.ufo/waves/round-19/preregistration.txt` and the cited ranges of `tools/souji-rev-pin.py`; searched the lane source registry for S079–S081 to establish prior provenance context.
- No Git/Jujutsu command, fixture, census, test, or build was run. No tool was installed.

# Contract compliance

- Wrote only this scoped report; no patch or other lane file was changed.
- No Git/Jujutsu mutation, process signal, `/proc/*/environ` read, secret/credential read, live census, or fixture execution.
- Scratch documentation downloads were confined to `/var/tmp/souji-r19-ScoutDurableRef/` and removed after report composition.