# S82ScoutSources — round 82 source-decision falsification (read-only on the lane)

Verdicts: **S330 REJECT (right outcome, one wrong sub-claim)** · **pre-freeze/committed DISAGREE (C1 half)** · **carried line anchors DISAGREE**.

## Q1 — S330 candidate (procps-ng pgrep(1)) — REJECT, but the Gate's rationale has one false sub-claim

**Source opened (host roff):** `/usr/share/man/man1/pgrep.1.gz`, owner `procps-ng 4.0.7-1` (verified: `pacman -Qo` → "is owned by procps-ng 4.0.7-1"; `pacman -Q procps-ng` → `procps-ng 4.0.7-1`; roff line 13: `.TH PGREP 1 2025-12-29 procps-ng`).

**The `-P` text, with location (roff line numbers of the decompressed man):**
```
166: \fB\-P\fR, \fB\-\-parent\fR \fIppid\fP,.\|.\|.
167: Only match processes whose parent process ID is listed.
```
(`zcat /usr/share/man/man1/pgrep.1.gz | sed -n '166,167p'` — OPTIONS section, `.SH OPTIONS` at roff line 56.)

**Q1a — Is the man page's ORDER claim ("parents before children, deeper first") grounded? NO.**
The man page states only the *matching predicate* ("Only match processes whose parent process ID is listed", roff:167). It says **nothing** about output order, tree order, or kill order. `pgrep` man has no "order"/"sort" statement at all (grep over the rendered man for `order|sort|ppid|stat` returns only roff:166 `-P`, roff:188 `-r`, roff:314 `/proc/pid/stat` for the `-f` note). So the ORDER is **not** man-grounded; it is the tool's own choice.
The tool's actual order is **parents-first, breadth-first-ish by stack** — `tools/souji-vault-verify.sh:227-241`: `tree+=("$child")` then `stack+=("$k")`, popped with `stack[${#stack[@]}-1]` (LIFO) ⇒ `tree[]` is **root first, then deepest-last**, and the kill loops (`:239` TERM, `:241` KILL) fire **parents before children**, i.e. *not* "deeper first". Reproduced live (`/fast/scratch/hyaku/souji-r82/S82ScoutSources/order_probe.sh`, `tree3.sh`): `tree[1]=ROOT(bash) tree[2]=child(sleep)` ⇒ parents precede children. So if any r82 text claims the man page grounds a kill order, that is unsupported; the *no-text* claim is currently absent, so no live falsehood — but the sentence "the man page grounds the ORDER" is not available to cite.

**Q1b — Is the recursion self-evident from `-P`? YES for one level, NO for depth.**
`-P` matches *only* processes whose **parent process ID** is listed ⇒ one level per call. Reproduced (`tree3.sh`): `pgrep -P ROOT` returned only the direct child; the grandchild was **not** in `pgrep -P ROOT`'s output ⇒ the tool's explicit recursion (`cli_kill_tree`, `souji-vault-verify.sh:227-241`) is required, not optional. The man page grounds the one-level predicate, and the recursion is a correct consequence — but the *order* is not grounded.

**Q1c — Is the Gate's rejection rationale right? Outcome YES; one sub-claim FALSE.**
`corpus/lessons/round-82.md:23` (raw line) rejects S330 because S075 already governs process identity and "the C2 counter's `nonce_pids` census (S075's own ground) is the executable evidence".
**FALSE sub-claim:** `nonce_pids` (`census/round-82/c2-vault-signal-counter.py:164-179`) reads `/proc/<pid>/environ` and `/proc/<pid>/stat` **field 3 (state)** — `f.read().rsplit(b")", 1)[1].split()[0]` (`:174`) — and S075 covers proc_pid_stat **fields 5, 6, 22** (`corpus/SOURCES.md:110`: "pgrp/session IDs and starttime tick units … § DESCRIPTION fields 5, 6, 22"). Field 3 (state) and `/proc/<pid>/environ` are **not** in S075's scope, and `corpus/SOURCES.md` has **no** row for `/proc/<pid>/environ` (grep `proc_pid_environ` → no hit; the proc_pid_* rows are S082–S085 = cwd/fd/wchan/status). So the census is **not** "S075's own ground"; it runs on S075-uncovered ground. The rejection still stands on the *stated* grounds (docs/A scope is one man page's `-P` prose; the tool proves the mechanism by running; CORPUS rule 4 — `CORPUS.md:123` "Expansion is knowledge, not rows" — bars a second row for a covered ground). **Severity LOW**: the reasoning survives, but the parenthetical source attribution is wrong and would mislead a future row's `teaches`.

**Admit/reject per row: S330 = REJECT** (consistent with CORPUS rule 4; S075 + S085 + the executable rows already carry the ground). **Fix if kept:** reword "S075's own ground" → the census reads `/proc/<pid>/environ` + stat field 3, which S075 (fields 5/6/22) and S085 (status field) do not cover; a `/proc/<pid>/environ` row is the uncovered ground if ever needed.

**Also checked (both HOLD):** the Gate's "Flip" names `pgrep --oldest`/`-a` — both exist (roff:156 `-o, --oldest`; roff:70 `-a, --list-full`; `pgrep --oldest` and `pgrep -a` both exit 0 on this host). The S325/S326 sourcing for the process-group mechanics is intact (`corpus/SOURCES.md:284-285`).

## Q2 — pre-freeze-vs-committed claim: **DISAGREE on the C1 half**

Lesson `corpus/lessons/round-82.md:24` (raw): "the C1 draft measured in `census/round-82/records/prefreeze/` (sha256 `cbfdc07c…`, **the committed counter minus the prereg/docstring delta only**) and the C2 draft (`d1a43e08…`, byte-equal to the committed successor counter)".

Re-hashed committed bytes (`sha256sum`):
| file | committed sha256 | verdict |
|---|---|---|
| `census/round-82/c1-pointer-counter.py` (HEAD) | `cbfdc07c0d5de31f83555747e45f7335bf5584635c7f4665431048880db1875a` | **= the claimed "C1 draft" digest** |
| `census/round-82/c1-pointer-counter.py` @W1 `f5bc4197` | `cbfdc07c…` (identical) | |
| `census/round-82/c2-vault-signal-counter.py` (HEAD) | `d1a43e0890ab19a129755a408334ebdee70903a63735a2e1f33ea8901281d0df` | = claimed `d1a43e08…` → **HOLD (byte-equal)** |

**Finding (MEDIUM):** the C1 draft digest `cbfdc07c…` **is** the committed counter's digest — the committed file is byte-identical to the "draft", so it cannot also be "the committed counter minus the prereg/docstring delta". The prereg's own frozen binding already names `cbfdc07c…`? No — the prereg binds only the **harness** `a45a9022…` (`census/round-82/preregistration.txt`, "Counter: census/round-82/c1-false-row-harness.py sha256=a45a9022…"), and the prefreeze receipt `census/round-82/records/prefreeze/c1-candidate-draft.txt:1` says "C1 draft (cbfdc07c…, **later committed as census/round-82/c1-pointer-counter.py W1**)". So the prefreeze receipt itself records the draft as *becoming* the committed file; the lesson's "minus the prereg/docstring delta" clause contradicts it and the digests. The C2 half is fine (`d1a43e08…` byte-equal, and the same digest is bound at `:3` of the K-a receipt).

## Q3 — carried status-trusting anchors: **DISAGREE (the anchors no longer match the claim)**

Prereg `census/round-82/preregistration.txt:117` names "the status-trusting lane tools (`tools/souji-verify.sh:550,594`, `tools/souji-census.sh`, writer)" — carried from `corpus/lessons/round-76.md:114` and `.ufo/waves/round-76/w1/S76Connector.md:22` ("tools/souji-verify.sh:550,594; souji-vault-verify.sh:550,594 | status --porcelain").

Re-derived at HEAD:
- `tools/souji-verify.sh:550` = `is_secret_shaped "$p" && return 1`; `:594` = `}` — **not** `status --porcelain`. The file is byte-identical to the r76 base (`git show ee59aa4d…:tools/souji-verify.sh | sha256sum` = `e6cb3f93…` = HEAD's), so these anchors were **already wrong for souji-verify.sh at r76**; the real `status --porcelain` sites in that file are **:377, :421, :713, :883**. The r76 seat's own row merged the two tools' anchors onto one line.
- `tools/souji-vault-verify.sh:550,594` at r76 base were `status --porcelain` sites; at HEAD they are `local target=$1 repo=$2 intro ref` / `local target=$1 repo=$2 rel="" base n out status` (the W2 commit shifted them to :638/:682/:996/:1173).
- `tools/souji-census.sh` — the prereg names it without line numbers; census.sh is unchanged since r76 (`git diff --stat ee59aa4d… HEAD -- tools/souji-census.sh` = empty), and its status sites are still :41 (doc line) and :1249 (the `status --porcelain` call) ⇒ **the census.sh part HOLDs**.
- The "writer" (`tools/souji-receipt-write.py` / `souji-record-agreement.py`): no `status --porcelain` call in the receipt writer; `tools/souji-record-agreement.py:23` only *mentions* it in prose ⇒ the writer half of the carried list does not name a status-trusting site either.
**Severity LOW** (carried, not a claim — the prereg says so explicitly), but the anchors are stale and one file's pair was mis-transcribed at r76; a wave attacking "souji-verify.sh:550,594" would hit `is_secret_shaped` and a closing brace, not a status call.

## Additional source-level finding (LOW): the r82 knowledge entry's frontmatter was not updated
`corpus/knowledge/gate-signal-handling.md:4` still reads `round: 79, 80, 81` although the r82 section was added at `9881676a`; `source:` (`:3`) is unchanged, and the r82 section's new `pgrep -P` mechanism therefore cites **no row** — consistent with rejecting S330, but it leaves the r82 section uncited and the `round:` field stale (the r81 section's precedent: the file's frontmatter is the entry's own index).

## Commands run (lane root; scratch `/fast/scratch/hyaku/souji-r82/S82ScoutSources`)
- `zcat /usr/share/man/man1/pgrep.1.gz | sed -n '166,167p'` (and 56, 70, 156, 300-362); `pacman -Qo /usr/share/man/man1/pgrep.1.gz`; `pgrep --help`; `pgrep --oldest -f true`; `pgrep -a -f true`
- `sha256sum census/round-82/c1-pointer-counter.py census/round-82/c2-vault-signal-counter.py census/round-82/c1-false-row-harness.py census/round-82/c1-false-rows.tsv census/round-82/c2-population.tsv`; `git show f5bc4197…:census/round-82/c1-pointer-counter.py | sha256sum`; `git show 1cb7c7d1…:census/round-82/c2-vault-signal-counter.py | sha256sum`
- `python3 -B census/round-82/c1-false-row-harness.py --counter census/round-82/c1-pointer-counter.py --lane /home/vgpnk/Projects/shokunin/souji-shokunin --fleet-root /home/vgpnk/Projects/shokunin --work /fast/scratch/hyaku/souji-r82/S82ScoutSources/c1` ⇒ **`SUMMARY rows=32 mismatches=0 accepted=0 refused_true=0 errors=0`, `EXIT=0`** (77.5 s) — the C1 claim's number **reproduces** (NF-F/NF-G/NF-H/NF-I refused, PF-1/TF4/TF5 true).
- `awk 'NR==550||NR==594{…}' tools/souji-verify.sh tools/souji-vault-verify.sh tools/souji-census.sh`; `git show ee59aa4d…:tools/souji-{verify,vault-verify,census}.sh | sed -n '550p;594p'`; `grep -n "status --porcelain" tools/souji-{verify,vault-verify,census}.sh`
- `bash /fast/scratch/hyaku/souji-r82/S82ScoutSources/{order_probe.sh,tree3.sh}` (3-level process tree, no kills; scratch-only, all processes reaped)
- `git show 9881676a -- corpus/knowledge/gate-signal-handling.md`; `grep -n "^| S075\|^| S325\|^| S326" corpus/SOURCES.md`; `grep -n "expansion is knowledge" /home/vgpnk/Projects/shokunin/CORPUS.md`

## Files written
- `.ufo/waves/round-82/w1/S82ScoutSources.md` (this report)
- scratch (removed at exit): `/fast/scratch/hyaku/souji-r82/S82ScoutSources/{order_probe.sh,tree3.sh,c1/,holder.sh}` — no lane tracked file touched; no git mutation run.

Tooling: none installed (no `pacman`/`uv`/`cargo`/`npm` call this seat). No host sysctl, no `sudo`, no signal sent to a process this seat did not start.
