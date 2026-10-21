# Round 20 source reopen — S092 (`git-for-each-ref`)

**Scope:** read-only source reopen of the `git-for-each-ref` pattern claim. This is author-side source advice, not independent closure or an execution result.

**Observed source identity:** repository `HEAD` was `12516f7dcdd5b165e5ee208d44a38d63b5bd5812` (the preregistered baseline). At inspection, working-tree SHA-256 values were `tools/souji-rev-pin.py` = `d49efa4e0ee4e9c275e2866dd7b6a20b201a4ac12d2225ca9a0772cfae6578c9`, `corpus/SOURCES.md` = `199c06c9a57e692d010bda0578ae9f8a47bbe6fe2ef34bdbc802996e3b95a500`, and `corpus/lessons/round-20.md` = `239ebaa3c284294f7972b22f72d2a8df1309785dca7bf1d98a0ffda8153dc72e`. The resolver source read is snapshot `souji-rev-pin.py#5DAE`; these hashes identify observed working bytes, not a claim that they are committed or unchanged afterward.

## Observed facts

- The official page, <https://git-scm.com/docs/git-for-each-ref>, identifies 2.54.0 as its last-updated version and lists 2.55.0–2.56.0 as unchanged. Under **OPTIONS `<pattern>...`**, it says: “only refs are shown that match against at least one pattern,” using `fnmatch(3)` or literal matching. This describes selection/filtering; this passage does not designate durable namespaces or discuss `refs/jj`.
- `corpus/SOURCES.md:112` records S092 as a source-only narrowing and says the durable-root selection and `refs/jj` exclusion are lane policy. `corpus/lessons/round-20.md:32` quotes the documented filtering clause and explicitly supersedes S080’s broader teaching. The S092 wording and source quote agree with the reopened page.
- The older `corpus/SOURCES.md:100` S080 row says that selecting `refs/heads refs/tags refs/remotes` “therefore excludes `refs/jj` by construction.” That is an implementation consequence of the chosen patterns, not a documented guarantee that those namespaces are durable.
- The currently observed `tools/souji-rev-pin.py:17-18` still cites S080 for explicit namespace selection and exclusion by construction. The policy itself is visible locally at `:34-35` (`DURABLE_NAMESPACES`) and `:76-82` (those constants are passed to `for-each-ref`). The command is constructed as an argv list at `:63-67`, with no shell; current patterns are literal namespace prefixes, so shell glob expansion is not involved.

## Finding and confidence

**High confidence:** S092’s narrow filtering claim is supported by the official source; it must not be used as authority for the local durable-root policy. The implementation’s selected roots are an explicit lane policy. The code’s S080 source note is stale relative to S092 and leaves the old attribution visible, although the current code separately states the policy in its docstring/constants. This is an attribution/documentation gap, not evidence of a runtime defect or a reason to relax the full-ID/durable-ref rule.

**STATUS: OPEN** — update the source note in `tools/souji-rev-pin.py:17-18` to cite S092 and say that Git documents pattern filtering while the helper’s durable-root set is local policy. This should be checked against the exact current bytes above; I did not wait for later L1 edits.

## One concrete counterexample/oracle

Add one synthetic-repository negative case: with a commit reachable only through `refs/jj/grace`, assert that `git for-each-ref refs/jj` lists the ref under the documented pattern filter while the resolver refuses to treat that commit as durable; then retain the positive control with the same commit reachable from a configured durable namespace. This directly distinguishes “pattern matches” from “namespace has durable authority.” It is a proposed oracle only; no repository or target code was executed here.

## Limits

No build, test, helper invocation, or target execution was performed. The advertised tool routes exposed no LSP device, so source search was only a locator and direct reads are the cited evidence; no grep result is treated as semantic proof. No tools were installed or updated.