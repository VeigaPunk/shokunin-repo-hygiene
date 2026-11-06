source: S306 (gitattributes(5), https://git-scm.com/docs/gitattributes, `filter` clean command, sha256 0a1e8015…6aee, accessed 2026-11-06); S307 (git(1) OPTIONS `--attr-source`, equivalent to GIT_ATTR_SOURCE, accessed 2026-11-06); S308 (git-config(1) `core.fileMode`, accessed 2026-11-06); S310 (git-config(1) `attr.tree`, queued: no row measures it); host probe census/round-71/probes/attr-filemode-probe-base.txt (git 2.56.0); controls census/round-71/controls/c1-*.txt; counter census/round-71/c1-counter.py frozen at aa91d1cad89200ec733edd3475461010a372923d
verified-at: a1db6c8514771c0a0321c29741831606d09cc2a5 (writer candidate; 2026-11-06, git 2.56.0 on this host)
recheck: `python3 -B census/round-71/c1-counter.py --root . --matrix census/round-71/c1-matrix.tsv --base-rev 8b9345b1f2c4bb908ae418588d4cbde6a34a5bd0 --rev <tip> --tool tools/souji-receipt-write.py --work <scratch>` must print `SUMMARY matrix=70 base_forgeries=7 base_honest=19 new_forgeries=0 new_honest=19 class_mismatches=0 new_echo=0 errors=0 regress=PASS` and `EXIT=0` (census/round-71/records/c1-after.txt); on every git release, re-run the probe and re-fetch S306-S308 against their sha256

# A clean `git status` is not a clean tree when a clean filter or core.fileMode=false is configured

A receipt or cleanup tool that decides "the tree is clean" from `git status --porcelain` trusts git's
own comparison of the worktree with the index. Two repository-level settings change that comparison
without changing any file the tool looks at:

- A `filter` attribute with a configured clean command. gitattributes(5): "the clean command is used
  to convert the contents of worktree file upon checkin" (S306). git compares the *cleaned* bytes, so
  an edit the clean command maps back to the committed bytes is not reported. The attribute can come
  from a committed `.gitattributes`, from `$GIT_DIR/info/attributes`, or from a tree the caller names
  with `GIT_ATTR_SOURCE` / `--attr-source` (S307: attributes are read "instead of the worktree").
- `core.fileMode=false`. git-config(1): the variable "Tells Git if the executable bit of files in the
  working tree is to be honored" (S308). In repository-local config it hides an executable-bit flip.

Observed on git 2.56.0 against the round-start writer (`census/round-71/probes/attr-filemode-probe-base.txt`):

| route | before round 71 | rule now |
|---|---|---|
| GIT_ATTR_SOURCE tree with `filter=t` + local `filter.t.clean`, size-preserving forged bytes (P2) or in-run edit (P10) | receipt written | GIT_ATTR_SOURCE scrubbed from the writer's git calls; the edit is then seen (`lane worktree is dirty` / RECEIPT-STATE-CHANGED-DURING-RUN) |
| committed `.gitattributes` or `info/attributes` `filter=t` + local clean driver (P3, P4; FC3 row) | receipt written | refuse RECEIPT-FILTER-DRIVER-SET before the status read and again after the wrapped command |
| local `core.fileMode=false`, pre-run (P6) or in-run (P7) chmod | receipt written | every writer git call pins `-c core.fileMode=true` |
| filter attribute with no configured driver (P5); driver configured but no tracked path carries it (P11); `core.fileMode=false` on an unchanged tree (P8) | receipt written | still written (a blanket presence refusal over-refuses these: control F1, `new_honest=16` of 19) |

The size of the edit matters: git's stat check sees a size change before any clean filter runs, so a
size-changing edit is reported even under a filter (first probe run, recorded in
`census/round-71/preregistration.txt`), and a CRLF rewrite under a `text` attribute (P1) is visible.
The forgery needs a size-preserving edit, which is cheap (`v2` for `v1`).

General lesson for this domain: before trusting a clean status as evidence that a tree may be cleaned,
quarantined or receipted, resolve every tracked path's `filter` attribute under the tool's own
pinned environment and refuse when a clean/process driver is configured, and pin `core.fileMode`.

## What this does not cover

- `attr.tree` in repository config (S310, queued) and `core.attributesFile`: the writer's
  `check-attr` read honors both, but no matrix row measures either.
- `filter.<driver>.process` long-running drivers: refused by the same check, but unmeasured.
- Smudge-only drivers (they act on checkout, not on the status comparison).
- git releases other than 2.56.0.
