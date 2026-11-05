# S297 registry row — paste-ready text for `corpus/SOURCES.md`

**Status: NOT appended.** The L1 owns the registry (`corpus/SOURCES.md`) and every commit. This file is
delivered text only; no lane file was edited by seat `S65ScribeEntry`.

Source of the row fields: the scout seat `S65ScoutSources`
(`.ufo/waves/round-65/w1/S65ScoutSources/row-draft.md`, `s297-located-quote.txt`, `probe-log.txt`,
`used-by-checks.txt`). This seat re-ran the scout's slice assertions against the scout's DELIVERED bytes and
all PASSED (text 299266/299360/299390/299437/299496; man 330781/330827/330890; section anchor at raw HTML
byte offset 761837). The scout's HTML capture digest matches this seat's own independent fetch exactly
(`37aa8407b12e377a38f523d5012835d0515cc82f2249c942b9e5cff656019226`, HTTP 200, 830605 bytes, third-client
confirmed in the scout's seat), so the capture is byte-stable across clients.

## The row (paste verbatim)

```
| S297 | git-config(1) § status.showUntrackedFiles — https://git-scm.com/docs/git-config | docs | A | the writer's untracked-visibility refusal (receipt hygiene, C1 V1/V2 rows) | § status.showUntrackedFiles, accessed 2026-11-05; HTTP 200; 830605 bytes; sha256 37aa8407…9226; capture census/round-65/sources/s297-git-config.html; tag-stripped text census/round-65/sources/s297-git-config.txt; located quote census/round-65/sources/s297-located-quote.txt | `So, this variable controls how the commands display the untracked files.` (11 words) — the page's own words, located at byte offset 299266 of the tag-stripped text capture with `assert text[299266:299338] == quote_bytes` PASSED; the three documented values are `no` (show no untracked files), `normal` (show untracked files and directories) and `all` (show also individual files in untracked directories), and the default is `normal`; the page does not say that a tool must override the variable, and it says nothing about the precedence of `-c` or of `GIT_CONFIG_COUNT` | queued | 2026-11-05 | 180d | corpus/knowledge/untracked-visibility-concealment.md |
```

## Cell-by-cell

| column | value |
|---|---|
| id | `S297` — the next free id (the registry tail stands at 219 rows; the highest present is S296; S293 is a hole) |
| source | `git-config(1) § status.showUntrackedFiles` — `https://git-scm.com/docs/git-config` |
| kind | `docs` |
| tier | `A` |
| scope | `the writer's untracked-visibility refusal (receipt hygiene, C1 V1/V2 rows)` |
| anchor | `§ status.showUntrackedFiles, accessed 2026-11-05; HTTP 200; 830605 bytes; sha256 37aa8407…9226; capture census/round-65/sources/s297-git-config.html; tag-stripped text census/round-65/sources/s297-git-config.txt; located quote census/round-65/sources/s297-located-quote.txt` |
| teaches | the 11-word located quote + the three documented values + the default + two named limits (the page does not assign a duty; the page does not document precedence) |
| status | `queued` — may be flipped to `mined` in the same landing that creates the knowledge entry |
| opened | `2026-11-05` |
| recheck | `180d` |
| used-by | `corpus/knowledge/untracked-visibility-concealment.md` |

## Shape validation (run by this seat on the row text, on a scratch copy of the registry — never on the lane)

| check | result |
|---|---|
| `awk -F'|'` NF on the new row | 13 (11 content cells) — PASSED |
| `|` inside any cell | none — PASSED |
| kind enum (`docs` ∈ spec/docs/paper/code/tool/dataset/talk/book/community/own-work) | PASSED |
| tier enum (`A` ∈ A/B/C) | PASSED |
| status enum (`queued` ∈ queued/mined/rejected) | PASSED |
| recheck cell (`180d`) — an existing registry value | PASSED |
| tier histogram before → after | A=209 B=7 C=3 (219 rows) → A=210 B=7 C=3 (220 rows) — PASSED |
| quote word count | 11 ≤ 25 — PASSED |
| quote is the page's own words | PASSED (slice assertion against the delivered capture) |

## Integration facts the L1 must handle

1. **The row and the knowledge entry must land TOGETHER.** `corpus/knowledge/untracked-visibility-concealment.md`
   is absent at the tip (`16da2445088ccca15aa32c66841d878ee57a8706`); until it lands AND cites `S297`, the
   registry-agreement check (`tools/souji-registry-agreement.py`, K1) reports `K1 used-by-missing` /
   `K1 used-by-no-cite` for this row. The drafted entry is at
   `.ufo/waves/round-65/w1/S65ScribeEntry/knowledge-untracked-visibility-concealment.md`; its `source:` line
   opens with `S297`, so the cite requirement is satisfied by the entry as drafted.
1b. **S291's `used-by` must gain the new entry path, or K1 fires the other way.** The drafted entry's
   `source:` line cites BOTH `S297` and `S291` (S291 is cited because the entry names the index-flag route
   — `skip-worktree`/`assume-unchanged` — as the separate concealment mechanism it is). K1's
   `cited-not-in-used-by` direction then requires `corpus/knowledge/untracked-visibility-concealment.md` to
   appear in S291's `used-by` cell too, which today reads only
   `corpus/knowledge/skip-worktree-concealment.md`. `used-by` may be changed IN PLACE (contract rule 2), and
   the change must be logged old→new in the round lesson:
   `S291 used-by: corpus/knowledge/skip-worktree-concealment.md` →
   `corpus/knowledge/skip-worktree-concealment.md, corpus/knowledge/untracked-visibility-concealment.md`.
   If the L1 prefers not to touch S291's row, the alternative is to drop the `S291` id from the entry's
   `source:` line — but then the entry's index-flag bullet would cite a row it does not declare, which is
   worse. Recommendation: update S291's `used-by` and log the old→new pair.
2. **The captures are not in `census/` yet.** The L1 copies these from
   `.ufo/waves/round-65/w1/S65ScoutSources/` into `census/round-65/sources/` under the names the anchor cell
   names: `s297-git-config.html` (sha256 `37aa8407…9226`), `s297-git-config.txt` (sha256 `a692dbcb…7c3f`),
   `s297-located-quote.txt`. Optional third carrier: `s297-git-config.man.txt` (sha256 `2fec59ce…f8f8`), the
   rendered man page from `git 2.56.0-1`. The tag-strip recipe `s297-tagstrip.py` MUST travel with the text
   capture: the offsets are only meaningful against the exact bytes plus that recipe.
3. **A duplicate-url warning (W04) is expected, not a finding.** `https://git-scm.com/docs/git-config` is
   already carried by S042 (generic config-value effects), S057 (the `-u/--untracked-files` override) and S238
   (`GIT_CONFIG_COUNT`). S297's scope — which values exist and what each displays — is distinct from all
   three, exactly as for S291/S295/S296 and S251/S239/S244.
4. **S057 is the closest neighbour.** Its scope cell reads "not which value the census should use"; S297 is
   the complement that says which values exist and what each displays.
5. **Status.** The row is filed `queued` because the mining knowledge entry does not exist yet. The L1 may
   flip it to `mined` in the same landing that creates the entry (contract rule 2 permits a `status` change in
   place, and the change must be logged old→new in the round lesson).
6. **The registry's provenance preamble needs a round-65 line.** The existing preamble records each round's
   source openings (e.g. "Round-64 provenance: new frontier rows S295 and S296 …"). A round-65 line naming
   S297, its URL, access date and ≤25-word located quote belongs there, and the lesson's `## Gate` carries
   the same record.

## What the page supports, and what it does not

- **Supported (the row's teaches):** the variable exists and controls how the commands display the untracked
  files; its three documented values are `no` (show no untracked files), `normal` (show untracked files and
  directories) and `all` (show also individual files in untracked directories); the default is `normal`; it
  can be overridden by the `-u|--untracked-files` option of `git-status`/`git-commit`.
- **Not supported, and named in the teaches cell:** that a tool must override or scrub the variable (the
  refusal is this lane's design decision); the precedence between a command-line `-c`, a `GIT_CONFIG_COUNT`
  pair and the repository-local config (a probe fact on git 2.56.0, not a documented guarantee); the
  porcelain output shape; anything about receipt writers, content hashing or symlink handling.
- **The row does not license the general rule.** "An operator-injected config cannot hide untracked entries
  from a receipt writer's dirty check" is FALSE on the measured arms (the `core.excludesFile`,
  `.git/info/exclude` and `.gitignore` routes all make the landed writer accept) and is unsupported by the
  page, which documents one variable's values. This is the round's rejection candidate; see the lesson's
  `## Gate` and the drafted knowledge entry's `## Gate`.

## Reproducing the located quote

```sh
cd census/round-65/sources
python3 - <<'EOF'
t = open('s297-git-config.txt','rb').read()
q = b"So, this variable controls how the commands display the untracked files."
assert t[299266:299338] == q   # PASSED
EOF
```
