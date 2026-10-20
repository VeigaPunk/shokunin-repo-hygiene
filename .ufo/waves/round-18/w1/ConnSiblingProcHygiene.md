STATUS: DONE — no sibling SKILL description claims /var/tmp or scratch hygiene; mori and tsukuroi already own the host/process observation C3 must report, not absorb.

# ConnSiblingProcHygiene — C3/C1 sibling overlap (round 18, wave 1)

Seat: `SoujiR18.ConnSiblingProcHygiene-5` (connector, leaf). No subagents. No tool installed or updated (pacman paused; nothing required). No census, proc-census, or signal was run. Sibling claims below are SKILL.md frontmatter `description` values only. Body lines that fell inside the read window are marked spill and are not claims.

Axes named: coverage (judged), operability (C1 watchdog must stay possible), calibration (description vs spill vs stale roster).

## Verdict

Holds: the real overlaps are mori (fleet and host observability: liveness, kill/OOM, resource runway) and tsukuroi (host operability and system repair). Kama is a near-miss (endpoint health, not residue). Kagi is credential hygiene, already refused. No description in the 21 on-disk lanes claims process-residue hygiene, `/var/tmp`, `/tmp`, `/dev/shm`, or scratch cleanup.

Fails if integrated as written: `ScribeProvinceProc.md` §2b refuses every signal, which cancels C1's repo-timeout SIGTERM/SIGKILL, and §2c names only mori. `PROVINCE.md:46-47` ("never on processes") and `:48-49` ("never touches the OS") already contradict an unbounded proc census.

Partial: three roster lanes have no `SKILL.md`, so they have no description to classify. That absence is not a vacant surface.

Smallest fix: land the adjacency block in §Proposed move. Do not edit any sibling. Do not land §2b of `ScribeProvinceProc.md` as an absolute ban.

## Roster contradiction (coverage)

`MANIFEST.json` `"roster"` (`:5-110`) lists 13 lanes and stops at kaidoku. Its `repo` fields for the last six do not exist as directories: `shokunin-game-audio` (`:67`), `shokunin-godot-2d` (`:75`), `shokunin-3d-engines` (`:83`), `shokunin-world-bible` (`:91`), `shokunin-binary-forensics` (`:99`), `shokunin-reverse-engineering` (`:107`). On-disk dirs match the `name` field (`audio-shokunin`, and so on).

The same file's souji mint note (`MANIFEST.json:3780`) says a scan of 21 lane provinces found no lane owns removal, and names tsukuroi (refuses removals), mori/kama/mado (detect-and-report), and kagi (credential hygiene only). That sentence is about artifact removal, not process residue. `shokunin.conf:19-83` lists those 21 child lanes plus `protocol|aggregator` on the fleet root. A roster-array-only pass would miss mori and tsukuroi, the two description-level overlaps.

On-disk `*-shokunin` dirs match that 21. `tameshi-shokukin/` is a one-entry typo dir (`.ufo` only), not a lane.

## Description classification

Hit = the description claims process, host, `/var/tmp`, or scratch hygiene. Near = a neighboring word that must stay reported. None = no such claim.

| lane | SKILL description | class |
|---|---|---|
| mori | `mori-shokunin/SKILL.md:2` — fleet and host observability; detect and report fleet liveness, wave settlement, kill/OOM, resource runway. Anti-trigger: not kumitate dispatch, not tsukuroi OS package/systemd/driver state, not kama endpoint health | HIT host + process-death observation |
| tsukuroi | `tsukuroi-shokunin/SKILL.md:2` — host operability and system repair | HIT host |
| kama | `kama-shokunin/SKILL.md:2` — local model serving and endpoint health; baseURL drift; model-id reconciliation | NEAR (health of endpoints, not residue) |
| kagi | `kagi-shokunin/SKILL.md:2` — credential hygiene evidence | NEAR (hygiene of secrets; already souji's anti-trigger) |
| kumitate | `kumitate-shokunin/SKILL.md:2` — OMP dispatch, ufo-fsd scripts, `crates/ufo-core-runtime` | NONE (dispatch, not hygiene; existing lock adjacency stands) |
| kaidoku | `kaidoku-shokunin/SKILL.md:2` — REA "on this Linux host" | NONE (host as workplace) |
| game-dev-3d | `game-dev-3d-shokunin/SKILL.md:2` — headless fixtures, engine census, "what a 3D engine did on this host" | NONE (fixture claims, not residue) |
| souji | `souji-shokunin/SKILL.md:2` — workspace hygiene; trigger `scratch bloat`; anti-trigger credential hygiene; contested artifacts reported, never absorbed | own scratch-artifact claim, not process residue |
| kasegi, kengaku, kake, kotoba, lore, chousa, kotodama, mado, tabi, tameshi | descriptions at each `SKILL.md:2` (kotoba `:2-15`, lore `:2-11`) | NONE |
| audio, game-dev-2d, revenger | directory read: no `SKILL.md` | no description; do not invent one |

No description contains `/var/tmp`, `/tmp`, `/dev/shm`, "process residue", or "scratch" except souji's own `scratch bloat`.

## Spills (inside the read window, not description claims)

- `mori-shokunin/SKILL.md:9` detection and report only, never remediates. `:19` resource runway uses `df -P` on the fleet root and `/tmp`. That is disk runway, not a process list. C3 must not emit runway or OOM verdicts.
- `kaidoku-shokunin/SKILL.md:39-40` ephemeral `/tmp/rea-ghidra-*` sessions are shared; never clean another session's dir.
- `tameshi-shokunin/SKILL.md:25-28` scratch namespace `/tmp/<lane>-r<round>-<n>-*/` from the first write.
- `tabi-shokunin/SKILL.md:16-17` "session hygiene" is the browser-capture runbook, not host scratch.
- `kumitate-shokunin/SKILL.md:21` fixture `self-iter` mentions `local/fixture-primary` processes and "NEVER native host execution".

These do not add a sibling claim. They are why a vanished `/tmp/<lane>-*` row is reported to that lane instead of deleted. game-dev-2d's descendant-timeout work is in `MANIFEST.json` round notes (`:1615`, `:1654`, `:1693`), not in a skill description.

## What C1/C3 would absorb if the wording stays absolute

- C3 (`souji-proc-census.sh`, own-uid, deleted cwd or argv path gone under `/var/tmp`, `/tmp`, `/dev/shm`, never signals) is a new list. It is not fleet liveness (mori), not host repair (tsukuroi), not endpoint identity (kama), not credential hygiene (kagi).
- `PROVINCE.md:46-47` says souji never acts on processes. A list contradicts "never on processes" unless the sentence is narrowed to "never signals a process it did not fork" and "never classifies liveness".
- `PROVINCE.md:48-49` says souji never touches the OS. A `/proc` read is not tsukuroi's repair and is not a deletion of `/tmp`. Leaving the sentence absolute makes C3 illegal; deleting it lets souji repair the host.
- `ScribeProvinceProc.md` §2a (list-only, residue is not a removal receipt) agrees with the mint note that no lane owns removal. §2b ("Signalling any process … never a souji action") contradicts C1: the census watchdog must SIGTERM the group `emit_census` forked, then SIGKILL 2 s later. §2c lets mori cite the list but does not forbid souji from stating OOM, runway, or daemon-death findings, and it never mentions tsukuroi.
- C1's "no lane fixture leaves a blocked process" is souji's census-fixture contract (`start_new_session` + `killpg` on that group). Read as a fleet law, it absorbs game-dev-3d headless fixtures, tameshi's fixture craft, and game-dev-2d's process-lifetime notes.
- `ScribeSkillRules.md` proc-census selftest kills sleepers in the group the fixture started. That matches "signal only what you forked". It does not match §2b.

## Proposed move (one)

Paste this in place of `PROVINCE.md:46-49`, and use it to narrow `ScribeProvinceProc.md` §2b–2c. Do not add a second process owner. Do not edit sibling skills.

```
- mori-shokunin detects and reports fleet liveness, wave settlement, kill/OOM
  events, and resource runway. souji's residue census lists own-uid rows only
  (deleted cwd, or argv naming a path under /var/tmp, /tmp, or /dev/shm that
  is gone). It does not classify liveness, OOM, runway, or daemon death.
  Rows of that kind are reported to mori. Complementary.
- tsukuroi-shokunin owns host operability and system repair and does not
  remove packages. souji removes receipt-gated files and does not repair the
  OS, systemd, or the driver. The /proc list is not host repair and is not
  a deletion of /var/tmp, /tmp, or /dev/shm. Host-operability questions in a
  row are reported to tsukuroi.
- kama-shokunin owns endpoint health. A residue row is not an endpoint
  verdict. A row whose redacted command names a model server is reported
  to kama.
- kagi-shokunin owns credential hygiene. The census redacts command text,
  cites paths and modes only, and never reads /proc/<pid>/environ.
- The residue census never signals. The only signal souji issues is the
  census repo-timeout watchdog, and only against the process group that
  census forked for that one repository (SIGTERM, then SIGKILL 2 s later).
  It does not signal a residue row, another lane's fixture, or any process
  it did not fork. "No blocked census child" is that contract. It is not a
  fleet fixture-hygiene law.
- Scratch bloat souji governs is workspace artifacts under a receipt
  (.scratch/, stale outputs). No sibling description claims /var/tmp or
  scratch cleanup, and that vacancy is not permission to delete host
  scratch or another lane's /tmp/<lane>-* tree. A vanished path is reported
  to the lane named by its prefix. Residue rows are not removal receipts.
```

Keep `ScribeProvinceProc.md` §2a (list-only work-surface bullet, land it in the same commit as the tool so `LG-DANGLING-PTR` does not fire). Replace §2b with the signal split in the block above.

## Affected axes

- Coverage: the governed residue class is the list (two predicates: deleted cwd, vanished scratch argv). Liveness, OOM, runway, endpoint identity, host repair, and other lanes' fixtures stay outside it. Counting "before → after" stays 0 → that list, not 0 → the host.
- Operability: C1's watchdog still has a process group to signal. An absolute signal ban would make the hang fix unlawful in `PROVINCE.md`.
- Calibration: untouched. Description lines above were read; spills are labeled; three missing skills are not filled in from `MANIFEST` domains.

No axis loses a surface it already had. Mori keeps kill/OOM and runway. Tsukuroi keeps repair. Souji gains a list and keeps a self-forked watchdog.

## Risks

- Landing §2b verbatim and the C1 watchdog in one province file leaves two contradictory refuses.
- Treating "no description mentions `/var/tmp`" as sole ownership, then deleting those paths, is host repair (tsukuroi) and can remove kaidoku or tameshi scratch (spill lines, not claims).
- Citing `census/round-17/gate-replays-ddb7347.json` or a not-yet-landed `tools/souji-proc-census.sh` from `PROVINCE.md` trips `LG-DANGLING-PTR` at round ≥ 18. The block above names no path that is absent, except the tool name already queued by the scribe; land both together.
- `shokunin.conf` is driver config. It was used to check the 21-lane set against the mint note. It is not a skill description.

## Verification (not run here)

After L1 pastes the block: `PROVINCE.md` contains the mori report sentence, the tsukuroi non-repair sentence, and the watchdog-only signal sentence; it does not contain "never on processes" or "Signalling any process". Re-read the twelve description lines cited above if a sibling skill changes. Do not run `souji-census.sh` or `souji-proc-census.sh` against the fleet. The orphan-counter comparison in the C3 claim is unmeasured in this seat.

## Commands

Reads only (no shell pipeline). Outputs are the line citations above.

- `MANIFEST.json` `:1-110` (roster) and `:3773-3781` (mint note).
- `shokunin.conf` `:19-83`.
- `souji-shokunin/SKILL.md` `:1-3`; `PROVINCE.md` `:1-121`.
- Each lane `SKILL.md` frontmatter: kasegi, kengaku, kake, kumitate, kotoba, kagi, kama, game-dev-3d, lore, kaidoku, mori, tsukuroi, tabi, mado, tameshi, kotodama, chousa (all under `/home/vgpnk/Projects/shokunin/<lane>/SKILL.md`).
- Directory reads, no `SKILL.md`: `audio-shokunin/`, `game-dev-2d-shokunin/`, `revenger-shokunin/`.
- Round cache: `.ufo/waves/round-18/w1/ScribeProvinceProc.md`, `ScribeRowsProc.md`, `ScribeSkillRules.md`; prior boundary `.ufo/waves/round-14/w1/SiblingOverlap.md` `:53-56` (souji then "never touches … host processes").
- Fleet root directory read: the 21 `*-shokunin` dirs. `~/.agents/skills/godspeed/SKILL.md` `:1-17` (posture only).
