
## Gate correction (r35 routed defect 2)

The r35 lesson's Gate recorded S231/S232 as mined without URL, access date or located quote. Both
were re-opened this round; the located facts are:

- **S231** (own-work) — `census/round-35/records/prune-census.tsv`, accessed 2026-10-28, sha256
  `8b37041ac1a954263c6f4e665a8105d37ac342c802fb11f596aadb69ec257177`; quote (the record's own
  totals line): `TOTAL	repos=26	regs=27	prunable=0`. Its 26 REPO rows include four non-git
  paths (`ok`, `research`, `scripts`, `templates`) and its `prunable` column is 0 for every row
  because it counted `prune --dry-run` stdout — both defects are reproduced mechanically by
  `tools/souji-worktree-drift.py` (`census/round-36/records/c3-after.txt`).
- **S232** — https://git-scm.com/docs/git-worktree, re-fetched 2026-10-28 (HTTP 200, 98 918
  bytes, sha256 `cf843ea6e3edda3fdda65877063f6c9b8a8e91b54041bc39d0bc89246a6bc72d`, snapshot
  `census/round-36/sources/git-worktree.html`); located quote: “prunable, if the worktree can be
  pruned via git worktree prune.” (§ OPTIONS, the `git worktree list` annotation paragraph).

## Registry corrections (rule 2, used-by only)

Three rejected rows carried a `used-by` citing path, which contradicts `status=rejected` (a citing
path is the definition of mined). Reported by wave seat SwarmScout04 with row lines, history and the
exact corrected cells; wave seat SwarmReviewer03 read S097's round-20 audit as already dispositioned
— the two datasets agree, only the exemption claim differs, and the contract names no exemption.
Changed in place, old → new:

| row | old `used-by` | new `used-by` |
|---|---|---|
| S090 | `corpus/lessons/round-20.md` | `—` |
| S097 | `corpus/lessons/round-20.md` | `—` |
| S127 | `corpus/knowledge/git-repo-structure-common-dir.md` | `—` |

`status`, `tier`, `teaches` and the Gate rows are unchanged. Census after the correction:
`sources-census.sh validate --root /home/vgpnk/Projects/shokunin souji` exit 0.
