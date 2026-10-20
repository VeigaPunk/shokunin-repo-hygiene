# RerunGateReplayR15 — C2 red replay at `b410186`

Seat: `SoujiR16.RerunGateReplayR15-4` (leaf reviewer). Target: `tools/souji-landing-gate.py` at lane HEAD `a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae`; replay `--rev b410186 --round 15` (the r15 landing commit, `b410186` = "round-15: land operator-stopped config repair candidates; acceptance unrun"). Lane root `/home/vgpnk/Projects/shokunin/souji-shokunin`.

Attack: C2's red is only as good as its false positives. I asked whether exit 1 and exactly these 5 findings are true of the r15 landing, and whether the counts that summarise the check surface (`checked_reg/pins/markers/reports`) are honest.

## Verdict: holds

`exit 1`; `findings=5`; reproduced twice with identical finding identities and identical `SUMMARY` counts (`checked_reg=18 checked_pins=16 checked_markers=1 checked_reports=64`). Each of the 5 is a real r15 landing defect; none is a false positive. I found no missed defect inside the gate's declared check set.

| # | id | path | claim | genuine? | independent anchor |
|---|---|---|---|---|---|
| F1 | LG-FROZEN-MEASURED | `tests/fixtures/r15-preservation-frozen/expected.json` | `files[tests/fixtures/r15-census-config.py]` absent at `measured_commit fc3a8d49b52d` | **holds** | record.json:`measured_commit`; `git cat-file -e fc3a8d4:tests/fixtures/r15-census-config.py` rc 128; closure `round-15-verifier-spotcheck.md:57` |
| F2 | LG-FROZEN-MEASURED | same | `files[tools/souji-census.sh]` pinned `b5187351…` but `fc3a8d4:` hashes `fcff8b05…` | **holds** | my `sha256sum` of the `fc3a8d4` blob = `fcff8b057b3e7dc5…`; closure `:45`, `:56` |
| F3 | LG-FROZEN-PIN | same | `tools/souji-census.sh` pinned `b5187351…` but `b410186:` hashes `dab4122c…` | **holds** | my `sha256sum` of the `b410186` blob = `dab4122c997db9b9…`; closure `:45`, `:56`, `:125` (R4) |
| F4 | LG-PARSE-REG | `tools/souji-census.sh` | `bash -n rc=2` at line 1368 | **holds** | I reproduced `bash -n` rc=2 on the exact `b410186` blob; `fc3a8d4` blob parses rc 0; closure `:7`, `:42`, `:122` (R1) |
| F5 | LG-SEAT-UNCARRIED | `.ufo/waves/round-15/w1/ConfigRepair.md` | `line 7` STATUS INCOMPLETE not carried | **holds on substance** (format caveat below) | closure `:30` (D1), `:105`, `:124` (R3); `round-16.md` retro-carry "r15's lesson and report understated them" |

Run output (verbatim except the per-run temp directory token, normalised here to `<snapdir>`; see finding 2). Quoted inside a fence so it cannot itself register as a failure channel:

```text
LG-FROZEN-MEASURED	tests/fixtures/r15-preservation-frozen/expected.json	files[tests/fixtures/r15-census-config.py] absent at measured_commit fc3a8d49b52d (path tests/fixtures/r15-census-config.py)
LG-FROZEN-MEASURED	tests/fixtures/r15-preservation-frozen/expected.json	files[tools/souji-census.sh] pinned b51873514d1f6d34 but fc3a8d49b52d:tools/souji-census.sh hashes fcff8b057b3e7dc5
LG-FROZEN-PIN	tests/fixtures/r15-preservation-frozen/expected.json	files[tools/souji-census.sh] pinned b51873514d1f6d34 but tools/souji-census.sh hashes dab4122c997db9b9
LG-PARSE-REG	tools/souji-census.sh	bash -n rc=2: <snapdir>/tools/souji-census.sh: line 1368: syntax error near unexpected token `}'
LG-SEAT-UNCARRIED	.ufo/waves/round-15/w1/ConfigRepair.md	line 7: ## STATUS: INCOMPLETE — file has an unresolved syntax error
SUMMARY	findings=5	checked_reg=18	checked_pins=16	checked_markers=1	checked_reports=64
```

## Per-finding evidence

**F1 — the frozen record names a commit that could not contain the measured fixture.** `tests/fixtures/r15-preservation-frozen/record.json` (at `b410186`) has `"declared_consistency_only": true`, `"measured_commit": "fc3a8d49b52de26bef74418da96611aae34b958d"`, `"fixture": {"path": "tests/fixtures/r15-census-config.py", "sha256": "6314d45d…"}`. The fixture does not exist at `fc3a8d4` (`git cat-file -e` rc 128) and does exist at `b410186` (and hashes `6314d45d…`, matching both the record and `expected.json`). So the record's provenance names the pre-integration commit for a file that only appears in the landing: the declaration is internally false, not merely unexecuted. That is exactly the shape `LG-FROZEN-MEASURED` exists to catch. The r15 closure recorded the weaker form — "no committed self-test tally, frozen verdict or measured revision to verify" (`corpus/lessons/round-15-verifier-spotcheck.md:57`); the gate is strictly more informative here, not merely restating the closure. Its per-file message is accurate.

**F2 — the pin cannot be satisfied at the record's own measured commit.** The pinned digest `b51873514d1f6d34…` matches neither `fc3a8d4` (`fcff8b057b3e7dc5…`, my `sha256sum` of the blob) nor `b410186` (`dab4122c997db9b9…`). The closure measured both endpoints and concluded `b5187351…` "matches no committed revision" (`:45`, `:56`). `round-15.md:101` itself concedes "The frozen pins are pre-integration declarations and were not refreshed", so the finding is the mechanical form of an admitted r15 defect, closed by R4 (`:125`).

**F3 — the landing-vs-pin mismatch.** Same root cause as F2, observed at `b410186`: pinned `b5187351…`, actual `dab4122c…`. Genuine; a frozen run against the landed tree would have returned `snapshot_tampered` (could-not-evaluate), not the declared `clean` (closure `:56`).

**F4 — the landing introduced a non-parsing census.** I materialised the exact `b410186:tools/souji-census.sh` blob (`sha256 dab4122c…`) and ran `bash -n` → rc 2, `line 1368: syntax error near unexpected token '}'`. The `fc3a8d4` blob (`fcff8b05…`) parses rc 0. `git log cc21683..b410186 -- tools/souji-census.sh` lists only `b410186`, so the regression is the landing commit's, not an inherited state. The closure independently records the same failure site and root cause (`:7`, and `:42`: `bash -n` line 1368 plus SC1046 at 1324 — `list_repos` missing `fi`), and routed it as R1 (`:122`). Smallest fix, unchanged from R1: close the `if` with `fi` at ~1324 or revert the file to `cc21683`, then re-pin (F2/F3) after the fix.

**F5 — the landing never carried a known, seat-declared failure.** `ConfigRepair.md:7` is the only failure-vocabulary STATUS line among all 64 r15 seat reports (I enumerated every `STATUS`-prefixed line in `.ufo/waves/round-15/**.md` at `b410186`; the next-nearest candidates are `Status: design-only` forms whose first value word is outside the vocabulary). `corpus/lessons/round-15.md` at `b410186` has no `## Seat-reported failures` heading at all; its nearest disclosure is `:95` ("committed as an **unverified candidate**") and the C1 row at `:100`, which never says the file does not parse. The closure routed exactly this: D1 (`:30`) and R3 (`:124`, "must reach the L1 report and lesson verbatim. 'Unverified candidate' must not stand for 'known broken'"). `corpus/lessons/round-16.md` now retro-carries the line with `resolved@cbf688a` and states "r15's lesson and report understated them". Substance: true.

## Findings, by severity

**1. MEDIUM — interpretation risk on F5 (no code change required, wording constraint on the landing artifact).** The specific carry channel `## Seat-reported failures` + `open|resolved@<hex>` is a round-16 convention: it does not exist in `round-13.md`, `round-14.md`, or `round-15.md` at `b410186`; its first occurrence is `round-16.md:39` at lane HEAD. The r15 landing therefore did not violate a format that existed when it landed. The *substance* defect is independently established by the closure (D1/R3) and by round-16's own retro-carry, so F5 is a true positive for the r15 replay, but the replay must not be cited as "r15 was non-conformant with the carry format". The gate's own detail line is scoped correctly (it asserts only that the line is not carried); the risk lives in how C2/L1 phrases the result. Smallest fix: in any landing artifact, label F5 "r15 lesson never carried the failure (substance, per R3)" and keep the format rule labelled as round-16 policy. Optional gate hardening: include the pinned channel name/version in the detail string.

**2. LOW — the gate's finding detail is not byte-reproducible (non-hermetic temp path).** `check_bash` writes the blob under a fresh `tempfile.mkdtemp(prefix="souji-landing-gate-", dir="/var/tmp")` and runs `bash -n <abs snapdir>/<path>` (`tools/souji-landing-gate.py:192-213` and the `snapdir` creation in `evaluate`, ~`:530`). Bash echoes the absolute path, so the first two runs differ only in that token:

```text
run1: /var/tmp/souji-landing-gate-rw57kbe0/tools/souji-census.sh: line 1368: ...
run2: /var/tmp/souji-landing-gate-ttnndpox/tools/souji-census.sh: line 1368: ...
```

The directory is removed in `finally`, so the printed path is dangling after the run. Finding identity and counts are stable — this does not change the verdict — but any consumer that records the finding strings verbatim (landing receipt, diff against a re-run) will see churn. Smallest fix: run `bash -n` with `cwd=snapdir` and the repo-relative `path`, or strip `^<snapdir>/` from `err` before formatting.

**3. LOW — the selftest asserts finding-id membership, not the finding set or any detail.** `run_selftest`'s `check()` (`tools/souji-landing-gate.py:769-776`) passes only when `res["exit"] == expect_exit`, every `expect_ids` id is present (`all(i in ids …)` — a subset test), and no `forbid_ids` id is present; the detail strings are printed but never compared. Consequences: (a) in any case that already expects `exit 1` — 10 of the 18 — a spurious extra finding whose id is not in that case's `forbid_ids` does not fail the selftest; the strict tests against false positives are the five expect-exit-0 worlds (`clean-pass`, `carried-open`, `carried-resolved`, `fenced-and-table-ignored`, and the inline `uncited-nonparsing-not-flagged`, which is the only one that also asserts `not res["findings"]`), none of which is the r13/r14/r15 replays the wave's calibration claim rests on; (b) the temp-path churn in finding 2 is invisible to it; (c) a correct id with a wrong claim text would pass. Case census verified in source: 15 `check()` invocations (four green, ten exit-1, one exit-2) + 3 inline assertions (`passed += 1` at `:824`, `:945`, `:962`) = 18, so the wave's "18/18" count is honest — the gap is assertion strength, not case count. For a gate whose product is the finding text, that is the weaker half of calibration. Smallest fix: give each case an exact `expect_ids` set and assert `set(ids) == expected`; add one assertion that the `LG-PARSE-REG` detail matches `line \d+: syntax error` with no `/var/tmp/` prefix.

**4. NOTE — 5 findings are 4 distinct defects; do not report "5 independent r15 defects".** The `tools/souji-census.sh` pin is reported twice: once as `LG-FROZEN-PIN` against the landing tree and once as `LG-FROZEN-MEASURED` against the record's declared commit. Exit is binary (`1 if findings else 0`), so there is no verdict impact, but the artifact count should be read as: parse (1), census pin wrong (2 findings), declared measured commit invalid / fixture absent (1), seat failure uncarried (1).

## Invariants, callers, error paths checked

- **Rev-pinned identity, no worktree leakage.** The current worktree `tools/souji-census.sh` is `64a60fd0b0ed…` (the r16 C1 file, identical at `HEAD` and `0a70bef`), yet the gate reported `dab4122c…` for `b410186` and `fcff8b05…` for `fc3a8d4`. All blob reads go through `list_tree`/`blob_by_oid`/`blob_at_path` (git plumbing); `resolve_commit` pins the rev before any read (`:160-176`). A dirty worktree cannot move this red — the r16 tree state does not influence the r15 verdict.
- **Snapshot fidelity of the parsed bytes.** The blob written for `bash -n` hashes `dab4122c…`, i.e. the committed `b410186` bytes, so the parse finding is about the landing, not the snapshot.
- **Cleanup.** The per-run snapdir is removed in `finally`; no residue.
- **Determinism.** Two runs, same five identities, same order, same counts; the only difference is the temp token in F4's detail (finding 2 above).
- **Saturation of the summary counts, checked by hand.**
  - `checked_reg=18` = the 18 distinct paths matched by `CITED_PATH_RE` in `b410186:SKILL.md`; I enumerated them and all 18 exist at `b410186`, so `LG-MISSING-REG` is genuinely 0.
  - `checked_pins=16` = 7 (`r13-cert-frozen`) + 2 (`r14-cache-frozen`) + 3 (`r15-preservation-frozen`) file pins, + 1 `record_sha256` (`r15`), + 3 `measured_commit` cross-checks (`r15`). The other two frozen sets carry no `measured_commit`, so 16 is complete for the pinned rule; the two r15 pins that do match (`6314d45d…`, `4749ad07…`) are correctly silent, matching closure `:56`.
  - `checked_markers=1` = the single failure-vocabulary STATUS line I found by independent enumeration of all 64 reports.
  - `checked_reports=64` = the 64 `.md` files under `.ufo/waves/round-15/` at `b410186`.
- **Honest saturation of the red.** The 5 findings cover each mechanically visible r15 landing defect the closure routed as R1 (parse), R3 (disclosure), R4 (pins), plus the record-provenance defect the closure only gestured at (`:57`). R2/R5/R6/R7 are admission or process defects outside the gate's id set by design; the gate does not claim them.

## Residual risk and verification gaps

- **No `--base` in the replay** means the parse surface is citation-scoped: a landing that broke an uncited script would be invisible unless `--base` (→ `LG-PARSE-CHANGED`) is passed. This is a designed boundary, pinned by the selftest's `tools/uncited-bad.sh` case (`:709`). At `b410186` two changed-but-uncited scripts exist — `census/round-15/count-claims.py` and `census/round-15/run-verification.py` — and `python3 -m py_compile` on both `b410186` blobs returns rc 0, so the boundary produced no missed defect here. If C2 wants landing parse coverage independent of citation, the replay should pass `--base cc21683` (or the r15 baseline) and report `LG-PARSE-CHANGED` separately.
- I did not run the gate's `--selftest` or the held-out fixture (neither is in this seat's ALLOWED-EXEC; the contract records 18/18 and 15/15).
- I did not run ShellCheck; the gate checks parse only. The SC1046 root cause (`:42`) is quoted from the closure, not re-measured.
- `corpus/lessons/round-15-verifier-spotcheck.md` does not exist in the `b410186` tree (introduced by `58ace9f`, present at HEAD). Every citation to it is the closure's later re-measurement of `b410186`, not bytes that existed in the landing tree.
- I did not inspect `census/round-16/*.json` beyond key enumeration: those artifacts are the C1 census matrix and do not record a landing-gate replay, so there was no recorded wave-1 r15 replay to diff against.

STATUS: ok

## Commands

```bash
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev b410186 --round 15; echo "EXIT=$?"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git log --oneline -3 b410186 && echo ---- && git show b410186:corpus/lessons/round-15-verifier-spotcheck.md | sed -n '1,120p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show b410186:.ufo/waves/round-15/w1/ConfigRepair.md | sed -n '1,30p' | cat -A | sed -n '1,30p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== r15 tree lessons ==" && git ls-tree -r --name-only b410186 corpus/lessons/ && echo "== HEAD lessons ==" && git ls-tree -r --name-only HEAD corpus/lessons/
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show b410186:tests/fixtures/r15-preservation-frozen/expected.json | python3 -m json.tool | sed -n '1,80p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== fixture at fc3a8d4 ==" && git cat-file -e fc3a8d4:tests/fixtures/r15-census-config.py 2>&1; echo "rc=$?" && echo "== fixture at b410186 ==" && git cat-file -e b410186:tests/fixtures/r15-census-config.py 2>&1; echo "rc=$?" && echo "== sha census at b410186 ==" && git show b410186:tools/souji-census.sh | sha256sum && echo "== sha census at fc3a8d4 ==" && git show fc3a8d4:tools/souji-census.sh | sha256sum && echo "== sha fixture at b410186 ==" && git show b410186:tests/fixtures/r15-census-config.py | sha256sum
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show b410186:corpus/lessons/round-15.md | grep -n "Seat-reported failures" ; echo "---- section ----"; git show b410186:corpus/lessons/round-15.md | sed -n '1,80p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "FAILURE_STATUS_WORDS\|def check_carry\|def failures_section_lines\|def seat_failure_lines\|def check_frozen_pins\|def is_failure_line\|def status_value" tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show b410186:corpus/lessons/round-15.md | grep -n "ConfigRepair\|syntax\|does not parse\|INCOMPLETE\|Seat-reported" ; echo "rc=$?"; echo "== tail =="; git show b410186:corpus/lessons/round-15.md | sed -n '80,200p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '60,100p;240,340p' tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '340,440p' tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '440,520p' tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show b410186:tests/fixtures/r15-preservation-frozen/record.json | sed -n '1,60p'
set -e; D=/var/tmp/souji-r16-RerunGateReplayR15-4; rm -rf "$D"; mkdir -p "$D"; cd /home/vgpnk/Projects/shokunin/souji-shokunin; git show b410186:tools/souji-census.sh > "$D/census-b410186.sh"; echo "sha=$(sha256sum "$D/census-b410186.sh")"; echo "lines=$(wc -l < "$D/census-b410186.sh")"; bash -n "$D/census-b410186.sh"; echo "bashn_rc=$?"; git show fc3a8d4:tools/souji-census.sh > "$D/census-fc3a8d4.sh"; bash -n "$D/census-fc3a8d4.sh"; echo "fc3a8d4_bashn_rc=$?"; echo "== ctx 1360-1372 =="; sed -n '1360,1372p' "$D/census-b410186.sh" | cat -n
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for f in $(git ls-tree -r --name-only b410186 .ufo/waves/round-15/ | grep '\.md$'); do git show "b410186:$f" | grep -n -i '^[#*[:space:]]*STATUS' | sed "s|^|$f:|"; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin && for r in 13 14; do echo "== round-$r heading =="; git show b410186:corpus/lessons/round-$r.md | grep -n "Seat-reported failures" || echo "(none)"; done; echo "== HEAD r15 spotcheck carry =="; git show HEAD:corpus/lessons/round-15-verifier-spotcheck.md | grep -n "Seat-reported failures\|syntax\|ConfigRepair\|INCOMPLETE" || echo "(none)"
D=/var/tmp/souji-r16-RerunGateReplayR15-4; cd /home/vgpnk/Projects/shokunin/souji-shokunin; git show fc3a8d4:tools/souji-census.sh > "$D/census-fc3a8d4.sh"; sha256sum "$D/census-fc3a8d4.sh"; bash -n "$D/census-fc3a8d4.sh"; echo "fc3a8d4_bashn_rc=$?"; echo "== diffstat fc3a8d4..b410186 census =="; git diff --stat fc3a8d4 b410186 -- tools/souji-census.sh; echo "== commits touching census r15 range =="; git log --oneline cc21683..b410186 -- tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== spotcheck pin mentions =="; git show HEAD:corpus/lessons/round-15-verifier-spotcheck.md | grep -n -i "frozen\|pin\|expected.json\|measured\|b5187351\|b518735\|dab4122\|fcff8b" || echo "(none)"; echo "== r16 heading at HEAD =="; git show HEAD:corpus/lessons/round-16.md | grep -n "Seat-reported failures" || echo "(none)"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:corpus/lessons/round-15-verifier-spotcheck.md | sed -n '44,62p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== frozen dirs at b410186 =="; git ls-tree -r --name-only b410186 tests/fixtures/ | grep -E '\-frozen/' ; echo "== gate registry check code =="; grep -n "def check_registry\|def cited_paths\|REGISTRY\|CITED_PATH_RE" tools/souji-landing-gate.py | head -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '525,600p' tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 - <<'EOF'
import json,subprocess,re
def show(p,rev="b410186"):
    return subprocess.run(["git","-C","/home/vgpnk/Projects/shokunin/souji-shokunin","show",f"{rev}:{p}"],capture_output=True,text=True).stdout
for p in ["tests/fixtures/r13-cert-frozen/expected.json","tests/fixtures/r14-cache-frozen/expected.json","tests/fixtures/r15-preservation-frozen/expected.json"]:
    d=json.loads(show(p))
    print(p,"files=",len(d.get("files") or {}),"record=",d.get("record"),"rsha=" ,bool(d.get("record_sha256")))
skill=show("SKILL.md")
cited=sorted(set(re.findall(r"(?:tools|tests/fixtures|census/round-\d+)/[A-Za-z0-9_.-]+\.(?:sh|py)",skill)))
print("cited_count=",len(cited))
for c in cited: print("  ",c)
EOF
python3 /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-landing-gate.py --root /home/vgpnk/Projects/shokunin/souji-shokunin --rev b410186 --round 15 > /var/tmp/souji-r16-RerunGateReplayR15-4/run2.txt 2>&1; echo "EXIT=$?"; cat /var/tmp/souji-r16-RerunGateReplayR15-4/run2.txt
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:corpus/lessons/round-15-verifier-spotcheck.md | sed -n '100,130p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '160,235p' tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "BAD_SH\|check_bash\|LG-PARSE" tools/souji-landing-gate.py | sed -n '1,40p'; echo "== selftest assertions around parse =="; sed -n '660,760p' tools/souji-landing-gate.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== spotcheck introduced by =="; git log --oneline -1 -- corpus/lessons/round-15-verifier-spotcheck.md; echo "== r16 failures section =="; git show HEAD:corpus/lessons/round-16.md | sed -n '35,60p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== ConfigRepair.md lines 1-13 =="; git show b410186:.ufo/waves/round-15/w1/ConfigRepair.md | sed -n '1,13p'; echo "== r15 report count =="; git ls-tree -r --name-only b410186 .ufo/waves/round-15/ | grep -c '\.md$'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== scripts changed fc3a8d4..b410186 =="; git diff --name-only --diff-filter=AM fc3a8d4 b410186 | grep -E '\.(sh|py)$' || echo "(none)"; echo "== cited set membership =="; git diff --name-only --diff-filter=AM fc3a8d4 b410186 | grep -E '\.(sh|py)$' | while read p; do printf '%s ' "$p"; git show b410186:SKILL.md | grep -qF "$p" && echo cited || echo UNCITED; done
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls -d .ufo/waves/round-16/w2 2>&1; git ls-tree -r --name-only HEAD .ufo/waves/round-16/w2/ 2>&1 | head -20; echo "== worktree =="; git status --porcelain -- .ufo/waves/round-16/w2 2>&1
D=/var/tmp/souji-r16-RerunGateReplayR15-4; cd /home/vgpnk/Projects/shokunin/souji-shokunin; for p in census/round-15/count-claims.py census/round-15/run-verification.py; do mkdir -p "$D/$(dirname "$p")"; git show "b410186:$p" > "$D/$p"; python3 -m py_compile "$D/$p"; echo "$p py_compile_rc=$?"; done; echo "== diffs of these two =="; git diff --stat fc3a8d4 b410186 -- census/round-15/count-claims.py census/round-15/run-verification.py
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "count-claims\|run-verification" SKILL.md | head; echo "rc=$?"; git show b410186:SKILL.md | grep -n "count-claims\|run-verification" | head; echo "rc_b410186=$?"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && ls -l census/round-16/c1-matrix-final.json census/round-16/c1-matrix-landing.json 2>&1; python3 -c "
import json,sys
for p in ['census/round-16/c1-matrix-final.json','census/round-16/c1-matrix-landing.json']:
    try:
        d=json.load(open(p))
    except Exception as e:
        print(p,'ERR',e); continue
    print('==',p,'keys=',list(d)[:20])
    s=json.dumps(d)
    print('  mentions b410186:', 'b410186' in s)
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show b410186:corpus/lessons/round-15.md | grep -n "unverified candidate\|C1 operability\|C2 calibration\|frozen pins are pre-integration"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:corpus/lessons/round-15-verifier-spotcheck.md | grep -n "^1\.\|^2\.\|^3\.\|^4\.\|^7\.\|^Status: ok\|^## Routed defects\|^## Trend verdicts" | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && echo "== worktree census (r16) =="; sha256sum tools/souji-census.sh; echo "== blob at HEAD =="; git show HEAD:tools/souji-census.sh | sha256sum; echo "== blob at 0a70bef =="; git show 0a70bef:tools/souji-census.sh | sha256sum; echo "== cleanup =="; rm -rf /var/tmp/souji-r16-RerunGateReplayR15-4; ls -d /var/tmp/souji-r16-RerunGateReplayR15-4 2>&1
```

Tool installs/updates: none.
