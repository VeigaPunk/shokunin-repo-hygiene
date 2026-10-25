# shokoknowledge

The shokunin fleet's knowledge vault — two complimentary tiers per specialist.

## The two tiers

- **`source/`** (symlink → git repo) — the *raw/auditable* tier: corpus,
  LOG.md round arc, SCORECARD axis evidence, verifier reports, commit
  history. Canonical, append-only, evidence-first. Shokunins store
  non-refined learnings and auditable traces here via git.
- **`<lane>-*.md`** (real vault notes) — the *refined* tier: human-legible
  distilled knowledge — quickref, lessons, resources, frontier. The
  reference sheet a shokunin (or operator) consults before digging into
  the auditable trail.

## Layout

| Folder | Domain | Refined notes | Source repo |
|---|---|---|---|
| `kasegi [security-research]` | Bounty & security research | quickref · lessons · resources · frontier | `~/Projects/shokunin/kasegi-shokunin` |
| `kengaku [llm-research]` | LLM/model research & evaluation | quickref · lessons · resources · frontier | `~/Projects/shokunin/kengaku-shokunin` |
| `kake [web-publishing]` | Web properties & publishing | quickref · lessons · resources · frontier | `~/Projects/shokunin/kake-shokunin` |
| `kumitate [orchestration]` | Orchestration & tooling (OMP, UFO) | quickref · lessons · resources · frontier | `~/Projects/shokunin/kumitate-shokunin` |
| `kotoba [prompt-craft]` | Prompt & skill craft | quickref · lessons · resources · frontier | `~/Projects/shokunin/kotoba-shokunin` |
| `kagi [secrets-ops]` | Secrets & vault ops | quickref · lessons · resources · frontier | `~/Projects/shokunin/kagi-shokunin` |
| `kama [endpoint-health]` | Local model serving & endpoint health | quickref · lessons · resources · frontier | `~/Projects/shokunin/kama-shokunin` |
| `kaidoku [reverse-engineering]` | REA shipped-artifact RE (Devin-side) | quickref · lessons · resources · frontier | [shokunin-reverse-engineering](https://github.com/VeigaPunk/shokunin-reverse-engineering) — `~/Projects/shokunin/kaidoku-shokunin` |
| `audio [game-audio]` | Game SFX/soundtrack, headless-verified | quickref · lessons · resources · frontier | [shokunin-game-audio](https://github.com/VeigaPunk/shokunin-game-audio) — `~/Projects/shokunin/audio-shokunin` |
| `game-dev-2d [godot-2d]` | 2D fixtures on Godot 4.7.2 headless | quickref · lessons · resources · frontier | [shokunin-godot-2d](https://github.com/VeigaPunk/shokunin-godot-2d) — `~/Projects/shokunin/game-dev-2d-shokunin` |
| `game-dev-3d [3d-engines]` | 3D across Godot/three.js/Unity/Unreal | quickref · lessons · resources · frontier | [shokunin-3d-engines](https://github.com/VeigaPunk/shokunin-3d-engines) — `~/Projects/shokunin/game-dev-3d-shokunin` |
| `lore [world-bible]` | Fictional-world records + consistency | quickref · lessons · resources · frontier | [shokunin-world-bible](https://github.com/VeigaPunk/shokunin-world-bible) — `~/Projects/shokunin/lore-shokunin` |
| `revenger [reverse-engineering]` | REA evidence-ledger discipline (origin lane) | quickref · lessons · resources · frontier | [shokunin-binary-forensics](https://github.com/VeigaPunk/shokunin-binary-forensics) — `~/Projects/shokunin/revenger-shokunin` |
| `protocol` | Canonical specialist-learning protocol | — | `~/Projects/kimi-shokunin/skills/shokunin/protocol` |
| `sources/skills` | Curation inputs (rea, godspeed, swarm, tower, ufo, shokunin) | — | `~/.agents/skills/*` |
| `atlas` | Fleet-level index: [[Corpus-Map]], [[Verdict-Log]], [[Frontier-Queue]], [[Curation-Sources]] | — | this vault |

## Conventions

- Note names carry the lane prefix (`audio-quickref`) so `[[wikilinks]]`
  resolve unambiguously across folders.
- The `[domain]` suffix tags the folder — name stays the identity.
- Refined notes cite source paths (`source/corpus/knowledge/...`,
  `source/LOG.md`) instead of duplicating evidence. Distilled claims keep
  the obs/inference/unknown labels of their source entries.
- Cross-lane findings (e.g. `evidence_id` path-sensitivity, wakaru OOM
  fix) get mirrored into the *affected* lanes' refined notes, not copied
  corpus-to-corpus.
- Folder names use `[`/`]` — fine on disk and for display; always link by
  basename (`[[lore-frontier]]`), never by folder path.

## Tool inventory

- **`notesmd-cli`** — file ops on real vault files (refined notes +
  atlas): `list`, `print`, `create`, `move`, `search`, `daily`.
  Caveat: `search-content` does NOT traverse `source/` symlinks.
- **`obsidian-cli-inspector`** (`oci`) — sqlite index over ALL notes
  including both tiers: `search notes`, `search backlinks`, `search tags`,
  `graph neighbors`, `analyze bloat`, `diagnose orphans`, `tui`.
  Config: `~/.config/obsidian-cli-inspector/config.toml`.
  **Re-run `index index` after corpus changes** (~2s); after moving or
  renaming folders, `init init --force` first — incremental indexing does
  not purge stale paths. Quote hyphenated terms: `search notes '"wide-reach"'`
  (bare hyphens are parsed as FTS operators).
Fleet remotes: roster repo [VeigaPunk/shokunin](https://github.com/VeigaPunk/shokunin)
(MANIFEST.json canonical; protocol vendored from kimi-shokunin). The `.shokunin/<lane>` paths inside `~/Projects/prymeagnt/*` worktrees are
symlinks → `~/Projects/shokunin/<id>-shokunin/` (canonical); lane verify
commands using `.shokunin/<lane>/...` keep resolving.

- **`rg -L <pattern> ~/Documents/shokoknowledge/`** — grep-grade path,
  follows all `source/` symlinks into lane corpora.
- Obsidian app: open `~/Documents/shokoknowledge` — graph spans all six
  shokunin folders + atlas.
