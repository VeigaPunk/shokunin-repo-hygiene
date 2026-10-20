STATUS: DONE — R1 fails statically: the quarantine tool emits `--as souji` for an owning lane, which the helper rejects when its recorded id is `kama`.

Axis: operability (identity routing).

## Finding — wrong owner id in generated recipe

**Verdict: fails.** At the pinned Souji revision `b5763415cc67ecff1e8fe56c58c39a6fb106d7a3`, `tools/souji-quarantine.sh:246-251` formats every jj-colocated repository's recipe with the literal `--as souji`. Its callers at `:549` and `:574` pass the owning repository path, source-relative path, and quarantine-relative path. For `/x/kama-shokunin`, and simple path arguments `src/item.txt` and `.ufo-quarantine/q/src/item.txt`, the exact `printf %q` output is:

```text
jj-lane.sh commit /x/kama-shokunin --as souji -m souji-quarantine:\ stage\ src/item.txt\ into\ quarantine -- src/item.txt .ufo-quarantine/q/src/item.txt
```

The source and quarantine arguments above are illustrative substitutions because the assignment does not specify an actual quarantined file; the repo argument and `--as souji` are fixed by the recipe. `%q` escapes dynamic arguments as shell words.

In `scripts/hyaku/jj-lane.sh:106-111`, `lane_id_jj` reads the repo's configured `user.name` and removes its trailing `-shokunin`. At `:516-518`, `commit` accepts only that lane id or `protocol`, otherwise it calls `err` and exits 1. With the owning repo configured as `user.name=kama-shokunin`, the exact refusal on stderr is:

```text
jj-lane: --as must be the lane id (kama) or protocol: souji
```

This is the refusal after earlier helper preconditions succeed (the repo is initialized, has a lane branch and valid identity/config). The owner id is determined by jj config, not proven by a directory basename alone.

`SKILL.md:125-130` describes the intended owning-lane recipe as `--as <owner-id>` and says the helper refuses other ids except `protocol`; that guidance is consistent with helper behavior, but the tool's generated recipe contradicts it and the wording does not state how to derive `<owner-id>`.

**Smallest correct derivation rule:** derive `<owner-id>` from that owning repo's `jj config get user.name`, stripping the exact trailing `-shokunin` suffix, as `lane_id_jj` does; put that value in `--as`. Do not hard-code `souji` or infer the id from the path. State this derivation alongside `<owner-id>` in the checklist.

## Evidence and commands

- `read skill://godspeed` — returned the skill text requiring named axes and concurrent cheap iteration.
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b5763415cc67ecff1e8fe56c58c39a6fb106d7a3:tools/souji-quarantine.sh | sed -n '236,255p'` — output includes `q_jj_commit_recipe` and its format string: `printf 'jj-lane.sh commit %s --as souji -m %s -- %s %s' ...`.
- `git -C /home/vgpnk/Projects/shokunin/souji-shokunin show b5763415cc67ecff1e8fe56c58c39a6fb106d7a3:SKILL.md | sed -n '125,130p'` — output states the owning-lane `--as <owner-id>` recipe and refusal rule.
- `read /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-quarantine.sh:236-255` — confirmed the pinned recipe text; `grep` on that exact file located recipe callers at `:549` and `:574`.
- `read /home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh:106-111` — returned `lane_id_jj`, which reads `user.name` and strips `-shokunin`.
- `read /home/vgpnk/Projects/shokunin/scripts/hyaku/jj-lane.sh:495-520` — returned the `--as` guard: `[ "$id" = "$lane_id" ] || [ "$id" = protocol ]`, otherwise `err "--as must be the lane id ($lane_id) or protocol: $id"; exit 1`.
- `grep` on that exact helper file located `err()` at `:65`: `echo "jj-lane: $*" >&2`.
- `git -C /home/vgpnk/Projects/shokunin rev-parse --show-toplevel && git -C /home/vgpnk/Projects/shokunin log -1 --format='%H %h %cs %s' -- scripts/hyaku/jj-lane.sh && git -C /home/vgpnk/Projects/shokunin ls-files -s scripts/hyaku/jj-lane.sh` — output:
  ```text
  /home/vgpnk/Projects/shokunin
  14df5b933128bc04495b7b646672956db3d7ac03 14df5b9 2026-10-20 ops(hyaku): jj-lane.sh v2 — fast-forward-only pushes, remote-rewrite stop, rebase without --ignore-immutable keeping the --as committer, branch bound at init, canonical paths as filesets, .ufo/state + large-file + phantom-deletion + sweep + foreign-identity guards, deletions/renames land, realpath lock, single citable 'landed <hash>', push --no-rebase for the driver; state falls back to git detection for every lane; selftest 45/45 (28 cases fail on v1); inline.sh verify: strict state, fast-forward push only, unpushed = not landed
  100755 c3abd3e5d74f776d16ac5cdc66b7132c14f44a7a 0 scripts/hyaku/jj-lane.sh
  ```
- `read xd://lsp` — output: `No such tool: xd://lsp` (mounted-tool inventory contained no LSP device). Therefore literal grep was used only to locate exact call sites and `err()`; it is not semantic proof.

**Residual verification gap:** no live `/x/kama-shokunin` repository or its `user.name` was inspected, and no recipe/helper was executed. The exact `kama` refusal is conditional on `user.name=kama-shokunin`; the mismatch itself is statically established from the hard-coded recipe and helper guard. No tools were installed or updated.