# S65ConnectorOverlap — shokuknow merge package (read-only read)

Source read: `/home/vgpnk/Projects/shokuknow/merge/souji/MERGE-REPORT.md` (read-only; no campaign tool run; nothing adopted; nothing written in the lane).

## Theme that fits round 65: `none` for adoption; one row is topically adjacent

Round 65's claims are the receipt writer's status visibility (C1 V1/V2: `status.showUntrackedFiles` overridden per read), the GIT_INDEX_FILE env refusal (C1 P13), and the C2 live-marker agreement. The one staged theme that touches that surface is the config-scope row:

- `corpus/knowledge/fleet-config-scope-resolved-r26.md` (staged from round 5): "The fleet's configuration has no system scope at all, so there is nothing an operator can override."

Why it is adjacent and not adopted: `status.showUntrackedFiles` is a git config key, so its effective value depends on which config scope an operator sets. The writer's per-read `--untracked-files=all` override makes the writer's verdict independent of that key, but system or global scope is where a concealing value would come from. The row's scope claim is asserted in the merge package and was not re-measured in this seat. Round 65's predicates do not depend on it.

Recommendation to L1: name `fleet-config-scope-resolved-r26` as the adjacency candidate only; do not adopt the package this round.

## Staleness and collision found while reading (informational)

- The report states "lane registry currently holds **108** rows; first staged id is **S109**." The lane's `corpus/SOURCES.md` now holds **219** rows (`grep -c '^| S[0-9]\{3\} |'` = 219; tail S294–S296), so the staged S109–S143 ids collide with rows the lane already holds. Any adoption would need renumbering.
- The report's dangling-citation table cites `S022` as absent from the package. That is a package defect; it was not checked further here.
- The report flags three "rows whose source the lane's registry already holds" (S143, S169, S170 against S001/S002/S042/S057/S063). Those concern git `pull.rebase` and maintenance pruning, not this round's surfaces.

No merge tool was run; no file in `shokuknow` was changed.
