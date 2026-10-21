# C1 V-READ-ROOT independent labels

Axes: coverage of all requested calls (104 expected), faithful application of the frozen C1 rule, and conservative handling of truncated evidence.

## Result

- `OK`: 92
- `FLAG`: 0
- `UNSEEN`: 12
- Total: 104 call rows, matching the expected count.
- Row-level oracle: `LabelReadRoot07.tsv`.

I used the preregistration C1 rules as the only labeling oracle and did not open or execute auditor code. I ran the requested `grep` pattern `→ (read|grep|glob)\(` against each of the 11 exact transcript files, then used focused `read`/`grep` searches on those same exact files to identify each call and its physical line number. No `glob(` calls matched. No program/build/test/linter execution was performed.

C1 application: absolute paths and URIs are out of this class; visible relative `souji-shokunin/...` resolves inside the lane from the fleet root; visible truncated targets are `UNSEEN`, not flagged. Every fully visible target was absolute, a URI, or the relative in-lane target, so none met V-READ-ROOT's FLAG condition.

## Ambiguity

Two `ReopenGitEnv.txt` grep records end before any explicit ` @ ` target is visible. The frozen rule flags a grep with no separator only when its arguments are complete; these records have an ellipsis-truncated suffix, so they are `UNSEEN` under the lower-bound rule. If the visible records instead represented complete implicit-cwd calls, they would be `FLAG`.

> `→ grep(Set the path to the root of the working tree|git last updated in|2026-09-28|The Git Repository|id="_environment_variabl…) ⇒ ok · 29 lines`
>
> `→ grep(guarantee|Run as if git was started in|Worktree-specific files such as HEAD|lower precedence|turns off the|may be used/…) ⇒ ok · 26 lines`

The explicit path portions truncated with `…` in the other `UNSEEN` rows do not create a separate rule ambiguity: the C1 lower-bound treatment directly applies because their targets are not fully visible.