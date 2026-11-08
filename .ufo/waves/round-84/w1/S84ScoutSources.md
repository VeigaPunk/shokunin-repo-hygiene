# S84ScoutSources — souji round 84 source opening for the C1/C2 knowledge sections

Seat: `S84ScoutSources`. Lane: `souji` (`/home/vgpnk/Projects/shokunin/souji-shokunin`). Date: 2026-11-08.
Deliverables in my seat dir `.ufo/waves/round-84/w1/S84ScoutSources/`:
`sources-draft.tsv` (registry-schema draft) and `sources-receipt.txt` (per-fetch receipts).
`corpus/SOURCES.md` was **not** modified by me — the L1 (`SoujiR84`) integrates.

## Findings

### 1. Registry id sequence and collision check

At 2026-11-08 03:41 the registry holds **259 distinct ids**, no duplicate id, max **S336**.
The specified collision check (`grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}'`) and the census script's own
row regex (`awk -F'|'` over `^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|`) agree on 259.
**Next free ids: S337, S338, S339, S340** (then S341-S345). Census before the draft:
`rows 259 | tier.A 248 | tier.B 8 | tier.C 3 | queued 14 | mined 217 | rejected 28`, 0 E-codes, 0 missing.

`S334`, `S335`, `S336` were filed **concurrently by another seat** between 03:20 and 03:41 (S334 `signal(7)`
as installed, S335 the r84 clause-kill receipts, S336 a rejected arXiv id). My first read of the registry
showed max S333; the L1 must re-run the collision check at integration time, because ids are moving under me.

### 2. Four rows proposed (2 for C2, 1 for C2 as a rejection, 1 for C1)

| id | source | verdict | why |
|---|---|---|---|
| S337 | `setsid(2)` — https://man7.org/linux/man-pages/man2/setsid.2.html (HTTP 200, 11555 B, sha256 `52cbc190…370f`, man-pages 6.19 2026-06-05) | **ADMIT** | the syscall contract the r84 latefork stub depends on: the caller becomes leader of a **new session and a new process group** and is the only process in it, so a group- or session-directed signal at the tool's group cannot reach the escaped child. Quote (17 w): "The calling process also becomes the process group leader of a new process group in the session". Distinct scope from S328, which covers the util-linux `setsid(1)` *utility's* fork-vs-exec behaviour. |
| S338 | `proc_pid_stat(5)` — https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html (HTTP 200, 20647 B, sha256 `0f04d789…700f`, man-pages 6.19 2026-02-08) | **ADMIT** | documents the field list the C2 map is keyed on: fields "in order, with their proper scanf(3) format specifiers", field (4) `ppid` = "The PID of the parent of this process", and which fields are ptrace-gated (a gated field reads 0 — a trap for a walk that reads 0 as a real ppid). Distinct scope from S075 (field 6/22 attribution) and S332 (kernel emission). |
| S339 | GNU `timeout(1)` 9.12 — https://man.archlinux.org/man/timeout.1.en (HTTP 200, 11852 B, sha256 `1f10e224…1f91e`) | **REJECT** | the shipped page mentions **no process group and no session at all** — measured `grep -ci group` → 0 and `grep -ci session` → 0 on the rendered page and on the installed `timeout.1.gz`. It cannot ground the group semantics; that scope stays S326 (implementation). Flip: a coreutils revision whose `timeout(1)` states the new process group. Kept as a row so the next round does not re-fetch it. |
| S340 | Papadakis et al., *Mutation Testing Advances: An Analysis and Survey* — author preprint https://mutationtesting.uni.lu/survey.pdf (HTTP 200, 1129278 B, sha256 `63b7bfca…f023`; Advances in Computers 112 (2019), DOI 10.1016/bs.adcom.2018.03.015) | **ADMIT** (tier B) | the convention C1's battery reuses: a test that distinguishes a mutant's behaviour from the original's *kills* it, and the mutation score is the ratio of mutants so killed. C1's `killed_r84=5` / `killed_r83=0` (S335) are counts in exactly that convention, so **a population that kills no mutant certifies no clause**. Quote (20 w, PDF p. 8): "We can define as 'mutation score' or mutation coverage the ratio of mutants that are killed by our test cases." |

Every quote was verified to be a **contiguous substring of the whitespace-normalized fetched bytes**, and its word
count computed from the same string (all ≤ 25 words; the receipt carries the counts and the locators).

### 3. Two candidates opened and deliberately **not** filed as rows

- **`census/round-83/records/wave-dirs.txt`** (sha256 `996507e8…9620`, 514 B; byte-identical to
  `git show 1014143d:…`) — the assignment's own-work C1 alternative. **Already covered twice**: S331 (the shape
  vocabulary `w1/ 65, w2/ 19, assimilation/ 4, records/ 3, residual/ 2, w3/ 1, a2w1/ 1`) and S333 (its corrected
  provenance). The r84 population's TF9/TF10 use `a2w1/` and `assimilation/`, both inside S331's teaches cell.
  A third row for the same file under the same scope would violate the registry's duplicate-URL/scope rule.
  No id spent.
- **`signal(7)`** (https://man7.org/linux/man-pages/man7/signal.7.html, HTTP 200, 56519 B, sha256
  `6ab11c52…38db`) — S334 was filed this round with exactly this scope, from the installed capture whose sha256
  `177f2734…e3b4b` **equals this host's** `/usr/share/man/man7/signal.7.gz`. My fetch therefore *corroborates*
  S334's quote ("The signals SIGKILL and SIGSTOP cannot be caught, blocked, or ignored.") rather than opening new
  ground. No id spent.

### 4. Consequences for the two claims' knowledge sections

- **C2 (operability 8)** — the claim rests on three documented facts. SIGSTOP's delivery semantics: **S334**
  (already filed). The escape mechanism that makes a late-forked setsid'd child unreachable by a group kill:
  **S337** (new). The field semantics of the walk's map key: **S338** (new), with **S075**/**S332** unchanged
  behind it. The claim's *stated limits* are not weakened by any row I opened: the timeout(1) rejection (S339)
  means the group semantics rest on the implementation (S326), not on a manual, and neither S337 nor S338 says
  anything about `/proc` atomicity or pid reuse.
- **C1 (calibration 7)** — the instrument is S335 (the lane's own receipts). **S340** supplies the external
  vocabulary that makes `killed_r84=5` / `killed_r83=0` readable: the kill count *is* the mutation score, so the
  r83 36-row population certifying zero clauses and the r84 44-row population certifying five is a statement in
  the method's own terms, not a local convention. S340 also discharges the flip condition S336 recorded
  ("a paper source is only reopened when a retrievable abstract states the mutation-testing proposition the entry
  needs"): the two arXiv ids in circulation are wrong — 1906.06117 is a pseudo-code generation paper and
  1607.05512 is "Assessing and Comparing Mutation-based Fault Localization Techniques" — and the retrievable
  source is the authors' own preprint.

### 5. Known gaps and cautions for the L1

1. **Ids moved under me.** S334-S336 appeared mid-seat. Re-run the collision check before integrating; if another
   seat has taken S337+, renumber — the four rows are independent and order-free.
2. **S340 vs S336.** S340 is a *new* URL and document, so it is a new row rather than a supersede of S336. If the
   L1 prefers the correction form, the only change is the teaches cell opening "supersedes S336 —".
3. **W04 expected on S338.** It shares `proc_pid_stat(5)` with S075/S068 under a distinct scope — a warning in the
   lane's own census, not a finding (the r40 precedent for S251 says so explicitly).
4. **gnu.org was unreachable** from this host (curl exit 28, HTTP 000, 40 s cap) for the canonical coreutils
   manual URL — the same failure S043 and S065 already record. I used a mirror that answers plus the installed
   man page, and the two are the same text. If the L1 wants the canonical URL in the anchor, note that the page
   itself never answered here.
5. **The man7.org revision stamps differ per page** (`setsid(2)` is man-pages 6.19 dated 2026-06-05; `signal(7)`
   and `proc_pid_stat(5)` are 6.19 dated 2026-02-08), so each row's anchor names its own stamp.

## Reproducer

```sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin
# collision check + next free id
grep -oE '^ {0,3}\|[[:space:]]*S[0-9]{3,}' corpus/SOURCES.md | sort -u | wc -l          # 259
awk -F'|' '/^\|[[:space:]]*S[0-9][0-9][0-9]+[[:space:]]*\|/ {i=$2; gsub(/[[:space:]]/,"",i); print i}' \
    corpus/SOURCES.md | sort | uniq -d                                                  # (empty: no dup id)
for n in $(seq 337 345); do grep -qE "^ {0,3}\|[[:space:]]*S${n}([^0-9]|$)" corpus/SOURCES.md \
    || echo "FREE S${n}"; done
# registry census (read-only; the script lives at the fleet root)
bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh \
    --file souji-shokunin/corpus/SOURCES.md --today 2026-11-08
# my drafts
cat .ufo/waves/round-84/w1/S84ScoutSources/sources-draft.tsv
cat .ufo/waves/round-84/w1/S84ScoutSources/sources-receipt.txt
```

## Bounds observed

Writes limited to `.ufo/waves/round-84/w1/S84ScoutSources/` and `.ufo/waves/round-84/w1/S84ScoutSources.md`.
No write to `corpus/SOURCES.md`, `MANIFEST.json`, `.ufo/state/*`, `.scratch/*`, `.ufo/watchdog.log`, any
sibling-lane file, `/home/vgpnk/Projects/shokunin/souji-know`, or any campaign tool. No git/jj mutation
anywhere (git used read-only inside the lane). Scratch under `/fast/scratch/hyaku/souji-r84/S84ScoutSources/`,
removed on exit after the receipts were copied into the wave directory; nothing written under `/tmp`. No tool
was installed or upgraded (pacman transactions are paused host-wide, and no tool this seat needed was missing).
