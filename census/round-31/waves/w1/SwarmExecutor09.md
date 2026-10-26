# SwarmExecutor09 — C3Snapshots (round 31, wave 1)

## Status

STATUS: PASS — the three assigned C3 source pages are pinned byte-exact (HTTP 200, tag-pinned) with basename-keyed
`SHA256SUMS`, a 3-row fetch receipt, and 16 verbatim anchor quotes (4..25 words each) mapped to line numbers; the
frozen L4 shape was simulated green over the delivered files. No lane commit, no jj mutation, scratch removed.

## Evidence

Lane revision (read-only): `git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD` ->
`1b811368461785040e955f41f9c97e62f61fd67c` (base `9f17a1ef571f3a510a51ac233d7cf50ac0c871fc`). I made no commit.

Status probe before download (`curl -s -o /dev/null -w 'http=%{http_code} size=%{size_download}' -m 60`):

```
http=200 size=5657    git/git v2.56.0 Documentation/git-reflog.adoc
http=200 size=7753    git/git v2.56.0 Documentation/config/gc.adoc
http=200 size=12284   jj-vcs/jj v0.45.1 docs/git-compatibility.md
```

Fetch (`curl -fsSL -m 60 -o`) into `/fast/scratch/hyaku/souji-r31/C3Snapshots/src`, then copied byte-identical
(`cmp` all three -> `identical`) into `.ufo/waves/round-31/w1/sources/`:

```
https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/git-reflog.adoc	200	2026-10-26T06:21:38Z	5657	59e7f0f15204a8c9f9b058ee62cb26aa2fa726b35dc85c702b75243424d6bf54
https://raw.githubusercontent.com/git/git/v2.56.0/Documentation/config/gc.adoc	200	2026-10-26T06:21:38Z	7753	0ab75f6f40ebdbda26bd3f3a8982405d764c87f72e7fbfef878f3df82a042f1a
https://raw.githubusercontent.com/jj-vcs/jj/v0.45.1/docs/git-compatibility.md	200	2026-10-26T06:21:38Z	12284	0fb71f992b0ed05d547e597d3f5f1cd33ed9e5d56a4e4e4cb851ba30c766c641
```

`sha256sum -c sources/SHA256SUMS` (inside `.ufo/waves/round-31/w1/sources`): `git-reflog.adoc: OK`,
`gc.adoc: OK`, `git-compatibility.md: OK`.

L4 shape simulated with the counter's own parsing (`SHA256SUMS` keyed by basename, receipt keyed by full snapshot
path, compare sha256 and `http == 200`):

```
receipt keys: ['census/round-31/sources/git-reflog.adoc', 'census/round-31/sources/gc.adoc', 'census/round-31/sources/git-compatibility.md']
each: http 200, sums_ok True, receipt_ok True
```

Anchor verification (`python3 -B`, 16 `<<< >>>` blocks parsed from `deliver-c3-anchor-lines.md`, each quote
whitespace-collapsed and tested as a substring of the snapshot named on its bullet line):

```
blocks= 16 bad= 0   (word counts 5..23; no block contains a pipe or a double quote)
```

Negative claim sweep: `grep -c -i reflog .ufo/waves/round-31/w1/sources/git-compatibility.md` -> `0` (258 lines).

## Findings

1. `docs/git-compatibility.md` **does exist** at tag v0.45.1 (HTTP 200, 12284 B), so the
   `api.github.com/.../git/trees/v0.45.1?recursive=1` fallback was not needed and no substitute page was chosen.
   Location: `.ufo/waves/round-31/w1/sources/git-compatibility.md:1-258`.
2. `git reflog expire` and `--expire-unreachable` anchors live in `git-reflog.adoc`: synopsis at line 19; expire
   semantics at 66-68; the option's "not reachable from the current tip of the branch" at 119-121; `=all` at
   124-127; `--expire=never` reachable-entry caveat at 116-117.
3. The two gc clocks and their defaults are stated in `gc.adoc`: `gc.reflogExpire` "defaults to 90 days" (115-122,
   default on line 118); `gc.reflogExpireUnreachable` "defaults to 30 days" (124-132, default on line 128); why the
   latter is shorter (133-138).
4. What keeps objects present for gc/prune: `git-reflog.adoc:145-148` names reflogs as the protection older
   collectors lacked; `gc.adoc:96-105` gives the `prune --expire 2.weeks.ago` clock; `gc.adoc:85-88` keeps
   unreachable objects in cruft packs by default `true`; `gc.adoc:140-147` keeps "any objects (and their descendants)"
   a `gc.recentObjectsHook` lists. The canonical keep-set sentence ("reflogs ... and anything else in the refs/*
   namespace") is in `git-gc(1)` NOTES, already pinned in-lane at
   `census/round-30/sources/git-gc.adoc:141-145` (sha `e3dbc4081095faf8d2d760eb4a47a1350f89d0c772f55eaada9cfbcdbeafba8c`).
5. jj side: `git-compatibility.md:229` states "Commits created by `jj` have a ref starting with `refs/jj/` to prevent
   GC"; the page supports detached HEAD (44-45), allows mixing `jj`/`git` (111-113), and calls running `git gc` in
   the Git repo untested (52-54). It never mentions reflogs, so the entry's reflog facts must rest on the two git
   pages only.
6. Two byte traps for Gate spans: `git-compatibility.md:114-117` contains literal double quotes (unusable inside a
   double-quoted Gate quote), and `git-compatibility.md:44` carries `* **Detached HEAD: Yes.**` bold markers that are
   part of the bytes; both are recorded in the anchor file rather than silently normalised.

## Deliveries

- `.ufo/waves/round-31/w1/sources/git-reflog.adoc`
- `.ufo/waves/round-31/w1/sources/gc.adoc`
- `.ufo/waves/round-31/w1/sources/git-compatibility.md`
- `.ufo/waves/round-31/w1/sources/SHA256SUMS`
- `.ufo/waves/round-31/w1/deliver-fetch-receipts.tsv` (header `url	http	fetched_at	bytes	sha256	snapshot`)
- `.ufo/waves/round-31/w1/deliver-c3-anchor-lines.md`
- `.ufo/waves/round-31/w1/SwarmExecutor09.md` (this report)

## Risks / blockers

- L1 must land the three snapshots at `census/round-31/sources/<basename>` unchanged (the receipt's `snapshot` field
  and L4's lookup key are those paths) and merge my three rows into
  `census/round-31/records/fetch-receipts.tsv`; any rename (e.g. `gc.adoc` -> `gc-config.adoc`) breaks L4.
- SwarmScribe15-2 signalled it may also cite `lib/src/git_backend.rs` (sha `95147270e5bc2a689e1191256c0f214d8e52ac6d4523756eb6b8ec8113d86c69`)
  and `cli/src/commands/util/gc.rs`. I did not fetch or verify those bytes; if they appear as `snapshot:` in the
  Gate, their `SHA256SUMS` lines and receipt rows must be unioned with mine (L4 requires every named snapshot to
  match both). I told that seat the exact basenames to use for my three files.
- [INFERENCE] `c3-counter.py` was not run: at this HEAD the entry, RUN, fixture and `census/round-31/sources/` are
  not integrated, so no C3 green/red claim is made here. Only the L4 shape was simulated over the delivered files.
- Tooling: no installs or upgrades (curl, sha256sum, python3 -B, cmp only); no pacman transaction.
