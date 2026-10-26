# Sibling-overlap scan — round-32 landed items (attempt 2, wave a2w1)

Seat SwarmConnector28. Read-only scan; nothing outside `souji-shokunin/.ufo/waves/round-32/a2w1/` written.

## Scope scanned

Landed this round, taken as the overlap subjects:

1. C3 entry `corpus/knowledge/jj-abandoned-object-mtime-clock.md` — git cruft packs, the `.mtimes` per-object clock, `gc.pruneExpire`, `gc.cruftPacks` (landed a92e1aa; fixture `tests/fixtures/r32-jj-mtime-clock.sh`; record `census/round-32/records/jj-mtime-clock-run.txt`).
2. Registry row S223 — gitformat-pack(5) at tag v2.56.0 (`corpus/SOURCES.md`:168).
3. C2 scratch-discipline repairs — 26 souji tools/fixtures honouring `TMPDIR`, r20 fixtures re-executing themselves inside a bwrap private `/var/tmp` backed by `TMPDIR` (landed 98e5203).

Lane tip at scan: master = 4e56c48 (orchestrator salvage commit; the three claim landings 98e5203, a92e1aa, 9e8982b are its ancestors).

## Method

Swept every sibling lane under the fleet root (all `*-shokunin` dirs; `ok` and `research` hold none of the scoped files), files:

- `*/PROVINCE.md` — 20 files
- `*/SKILL.md` — 18 files
- `*/corpus/README.md` — 20 files
- `*/corpus/SOURCES.md` — 20 files
- `*/corpus/knowledge/*.md` — 882 files

960 files total, `souji-shokunin/` excluded. Keywords per the seat spec: `cruft`, `mtimes`, `pruneExpire`, `cruftPacks`, `gitformat-pack`, `bwrap`, `private /var/tmp`. Case-sensitive and case-insensitive passes returned identical hit sets. Supplementary probes (outside the fixed keyword set, to rule the subjects' neighbourhoods): literal `/var/tmp`, `git gc`, `unreachable`.

Tool note: the mounted `grep` device silently returns "No matches found" for any path whose middle component is a star (e.g. `/home/vgpnk/Projects/shokunin/*/SKILL.md`); reproduced three times against known-hit bytes and reported to `xd://report_issue`. The sweeps below were therefore executed with plain `grep(1)` over the identical file set (commands in each section).

## Keyword results (sibling lanes only)

| keyword | matching lines | verdict |
|---|---|---|
| `cruft` | 0 | no sibling usage anywhere in scope |
| `gitformat-pack` | 0 | no sibling SOURCES row or text reference |
| `pruneExpire` | 0 | no sibling usage |
| `cruftPacks` | 0 | no sibling usage |
| `private /var/tmp` | 0 | the exact C2 landed pattern is unique to souji |
| `mtimes` | 90 lines / 52 files | all filesystem-timestamp evidence class — not overlap |
| `bwrap` | 81 lines / 22 files | all sandbox-confinement class — shared mechanism, disjoint purpose — not overlap |

Negative claims carry their sweep: `grep -i -c "$kw" */PROVINCE.md */SKILL.md */corpus/README.md */corpus/SOURCES.md */corpus/knowledge/*.md | grep -v '^souji-shokunin/'` summed per keyword over the 960 files, run 2026-10-26 from `/home/vgpnk/Projects/shokunin`.

## Finding 1 — C3 entry's git-pruning vocabulary is fleet-unique in scope

`cruft`, `cruftPacks`, `pruneExpire`, `gitformat-pack` each have **zero** sibling hits across all 960 scoped files. No sibling lane's PROVINCE, SKILL, corpus README, SOURCES registry or knowledge entry covers git cruft packs, the `.mtimes` sidecar, or the `gc.pruneExpire`/`gc.cruftPacks` levers. The entry's subject (an abandoned commit's object fate under `git gc` once keep refs and reflog entries are gone) is uncontested.

Nearest git-adjacent sibling text is a different class entirely: `kumitate-shokunin/corpus/knowledge/agent-isolation-substrates.md:241` uses `git gc --prune=now` only to *manufacture* an unreachable state for a workspace-containment demo ("history after a source history rewrite plus `git gc --prune=now` (`log` exit 128)"), not to study the object clock. Verdict: not overlap; no contested scope.

## Finding 2 — sibling `mtimes` hits are forensic file-timestamp evidence, not the git object clock

90 matching lines in 52 files (enumeration below). Every hit uses file/directory mtimes as *filesystem evidence* — config-cache mtimes (tsukuroi pacman planes), socket/pointer mtimes (tabi webbridge), checkout mtimes (mado, kaidoku), package birth-vs-mtime discipline (tsukuroi `SKILL.md:95-96`: "pacman preserves upstream mtimes"). None references git object mtimes, pack sidecars, or pruning.

Closest methodological neighbours:

- `mori-shokunin/corpus/knowledge/lane-silence-r2.md:128` — "Siblings commit into these trees and a checkout's mtimes move" — a git-checkout attribution caution, opposite concern (commits *moving* worktree mtimes, not mtimes deciding object fate).
- `mori-shokunin/corpus/knowledge/silence-cutover-r3.md:138` — backdating mtimes in a fixture, again evidence hygiene.

Verdict: not overlap; no contested scope. The C3 entry's own language keeps the domains apart (per-object clock inside a cruft pack vs filesystem timestamps of working files).

## Finding 3 — S223 (gitformat-pack) has no sibling registry counterpart

No sibling `corpus/SOURCES.md` row names gitformat-pack(5); the only `.mtimes` registry cells in the fleet are souji's own (S004, S122's `count_cruft` aside, and now S223 — souji-excluded here). Sibling bubblewrap rows (`kumitate-shokunin/corpus/SOURCES.md:82-84,108` S069/S070/S095; `tameshi-shokunin/corpus/SOURCES.md:102,142` S093/S267) are a different upstream document. Verdict: not overlap; S223's id is souji-internal (a placeholder the L1 renumbers by document).

## Finding 4 — sibling `bwrap` usage is confinement of untrusted execution; the C2 repair is scratch redirection

81 matching lines in 22 files (enumeration below). All sibling uses sandbox *execution*: kengaku's probe battery runs cases under `bwrap` (`kengaku-shokunin/SKILL.md:608` — "needs `/usr/bin/bwrap` and is the only registry row with a runtime cost outside its own temp dir"), tameshi's defect probes run mutants "in the bwrap envelope in `defect-probes.py:4-14`, with `env -i`, a private /tmp, and isolated PID and network namespaces" (`tameshi-shokunin/corpus/knowledge/guard-kill-closure.md:129`), kumitate's cap-run hermetic suite needs "unprivileged bwrap" (`kumitate-shokunin/SKILL.md:728`) and its substrates entry scopes bwrap to "run untrusted or generated code" (`kumitate-shokunin/corpus/knowledge/agent-isolation-substrates.md:164`). kengaku even maintains a cross-lane bwrap-usage map (`kengaku-shokunin/PROVINCE.md:318-332`) covering tameshi, kumitate, mado, kake, mori, kotodama, kaidoku — it predates r32 and names no souji row.

The C2 landed pattern differs in purpose and shape: souji's r20 fixtures re-exec themselves with `bwrap --dev-bind / / --bind <tmpdir> /var/tmp` so that *literal `/var/tmp` scratch writes land under the caller's TMPDIR* — bind-target redirection, not namespace confinement (no unshare, no ro-bind, no clearenv; the docstring says "Without bwrap the fixture runs as before"). Sibling private dirs are private `/tmp` (tmpfs), never a bind over `/var/tmp`: zero hits for `private /var/tmp` or any `/var/tmp` bind target; the only sibling `/var/tmp` mentions use it as a plain scratch *location* in older rounds (`kaidoku-shokunin/corpus/knowledge/2026-10-19-arc3-r1-evm-real-solc.md:7` recheck: "mkdir -p /var/tmp/cr2-recheck && TMPDIR=/var/tmp/cr2-recheck npx …"; `kotodama-shokunin/SKILL.md:458` "external temporary directory (for example `/var/tmp`)"). Verdict: shared tool, disjoint purpose and target — not overlap; no contested scope.

Observation (bookkeeping, not contested scope): if kengaku's PROVINCE map at :318-332 intends to be the fleet's bwrap-usage inventory, souji's r20 private-`/var/tmp` pattern is a new shape for kengaku to record in its own lane; nothing for souji to change.

## Per-hit enumeration (lane, file:lines)

`mtimes` (90 lines):

- kagi-shokunin/corpus/knowledge/transcript-hygiene.md:148
- kaidoku-shokunin/corpus/knowledge/2026-10-13-r2-doctor-reverify-r2.md:72
- kaidoku-shokunin/corpus/knowledge/2026-10-13-r3-jq-provenance.md:22
- kaidoku-shokunin/corpus/knowledge/2026-10-19-arc3-r12-go-evidence-id-domain.md:53,57
- kake-shokunin/SKILL.md:314
- kake-shokunin/corpus/knowledge/keeper-timer-inert.md:67
- kasegi-shokunin/corpus/knowledge/operator-queue.md:36
- kasegi-shokunin/corpus/knowledge/submitted-registry.md:60
- kengaku-shokunin/corpus/knowledge/probe-battery-r19.md:296
- kotoba-shokunin/corpus/knowledge/dispatch-prompt-audit-round7.md:55
- kotoba-shokunin/corpus/knowledge/substrate-pin-guard-round23.md:38
- kumitate-shokunin/corpus/knowledge/kimi-binary-secrets.md:337,338
- mado-shokunin/corpus/README.md:17
- mado-shokunin/corpus/knowledge/config-drift-r12.md:57,71
- mado-shokunin/corpus/knowledge/config-health-report-r3.md:988
- mado-shokunin/corpus/knowledge/omarchy-drift-watch.md:48,113,153,265
- mado-shokunin/corpus/knowledge/province-accuracy-selfaudit.md:31,87,243
- mado-shokunin/corpus/knowledge/remaining-planes-census.md:95,135,136
- mado-shokunin/corpus/knowledge/theme-route-r18.md:138
- mado-shokunin/corpus/knowledge/theme-wallpaper-plane.md:200
- mado-shokunin/corpus/knowledge/walker-deep.md:594
- mado-shokunin/corpus/knowledge/walker-deep-r9.md:65,288
- mado-shokunin/corpus/knowledge/walker-live-surface.md:170
- mado-shokunin/corpus/knowledge/waybar-walker-semantics.md:448
- mori-shokunin/corpus/knowledge/lane-silence-r2.md:128,147
- mori-shokunin/corpus/knowledge/silence-cutover-r3.md:138
- tabi-shokunin/SKILL.md:669
- tabi-shokunin/corpus/README.md:423,461
- tabi-shokunin/corpus/knowledge/async-step-evidence.md:121
- tabi-shokunin/corpus/knowledge/browser-surface-census.md:61,85,174,175,224,266
- tabi-shokunin/corpus/knowledge/closeout-r11.md:214
- tabi-shokunin/corpus/knowledge/hygiene-sweep-r4.md:140,153,251
- tabi-shokunin/corpus/knowledge/webbridge-daemon-disposition.md:213
- tabi-shokunin/corpus/knowledge/webbridge-plugin-anatomy.md:235,275,281,291
- tabi-shokunin/corpus/knowledge/webbridge-revival-assessment.md:117
- tameshi-shokunin/corpus/knowledge/gates-survey-kagi.md:440
- tameshi-shokunin/corpus/knowledge/gates-survey-kumitate.md:33,346,351
- tsukuroi-shokunin/SKILL.md:50,95,96,219,3452
- tsukuroi-shokunin/corpus/README.md:7
- tsukuroi-shokunin/corpus/SOURCES.md:105
- tsukuroi-shokunin/corpus/knowledge/aur-risk-plane-ver-s6.md:58
- tsukuroi-shokunin/corpus/knowledge/boot-chain-r17.md:27
- tsukuroi-shokunin/corpus/knowledge/calibration-synthesis.md:93,98
- tsukuroi-shokunin/corpus/knowledge/census-closeout-receipt-r10.md:126
- tsukuroi-shokunin/corpus/knowledge/degraded-triage-r4.md:346
- tsukuroi-shokunin/corpus/knowledge/driver-firmware-plane.md:183,307
- tsukuroi-shokunin/corpus/knowledge/foreign-provenance-r6.md:97,100,256,257
- tsukuroi-shokunin/corpus/knowledge/package-state-plane.md:77,79,81,139,235,236
- tsukuroi-shokunin/corpus/knowledge/pacnew-plane.md:78
- tsukuroi-shokunin/corpus/knowledge/timer-drift-plane.md:182
- tsukuroi-shokunin/corpus/knowledge/update-safety-note.md:317

`bwrap` (81 lines):

- kaidoku-shokunin/SKILL.md:606
- kaidoku-shokunin/corpus/README.md:114
- kaidoku-shokunin/corpus/knowledge/2026-10-13-r2-version-diff-compare.md:18,22,37,52,115
- kaidoku-shokunin/corpus/knowledge/2026-10-13-r4-10-real-version-pair.md:12
- kengaku-shokunin/PROVINCE.md:318,319,320,321,324,325,327,328,329,330,331,332
- kengaku-shokunin/SKILL.md:577,582,587,608,820,872
- kumitate-shokunin/SKILL.md:618,728
- kumitate-shokunin/corpus/README.md:93
- kumitate-shokunin/corpus/SOURCES.md:82,83,84,108
- kumitate-shokunin/corpus/knowledge/agent-isolation-substrates.md:1,18,110,112,114,119,121,125,126,130,131,164,179,180,188,203,204,247,248,250,298
- kumitate-shokunin/corpus/knowledge/counter-amendment-discipline.md:1,9,81
- kumitate-shokunin/corpus/knowledge/jj-workspace-seat-containment.md:101,103
- kumitate-shokunin/corpus/knowledge/mount-order-and-bind-scope.md:1,7,9,13,15
- tameshi-shokunin/SKILL.md:1785,1929
- tameshi-shokunin/corpus/SOURCES.md:102,142,406
- tameshi-shokunin/corpus/knowledge/guard-kill-closure.md:129
- tameshi-shokunin/corpus/knowledge/hermetic-env-differential.md:26,51,89
- tameshi-shokunin/corpus/knowledge/mutation-case-kumitate-round-gate.md:145
- tameshi-shokunin/corpus/knowledge/mutation-case-kumitate-sources-check.md:205
- tameshi-shokunin/corpus/knowledge/regression-tally-completeness.md:1,2,68,72,74
- tsukuroi-shokunin/corpus/knowledge/degraded-triage-r4.md:463

## Contested scope

None. Nothing this round landed steps on a sibling lane's declared scope in any of the 960 scoped files; the only follow-up is kengaku's own choice whether to add souji's r20 private-`/var/tmp` shape to its cross-lane bwrap map (`kengaku-shokunin/PROVINCE.md:318-332`).
