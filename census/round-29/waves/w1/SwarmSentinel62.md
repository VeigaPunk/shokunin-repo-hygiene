# SwarmSentinel62 — credential and private-URL sentinel (souji r29, w1)

## Status
STATUS: PASS — no credential, token, secret-reference, session, private or internal host, credentialed or userinfo URL, or foreign-home path in any assigned surface; every seat delivery stays inside the permitted write set except one self-disclosed probe deviation (files removed). Residuals are public third-party addresses and one plain-HTTP locator, reported masked below; no claim, counter or axis is affected.

## Evidence

Read-only; lane base `691dd29211c53d0ef94fa072394cb9c8a69fe92e`, preregistration commit `b8cb4b31ce80e2e3314b88e85d40ea9873180804`. Frozen contract read first: `census/round-29/records/preregistration.txt` (C1/C2/C3, counters, kill rules, targets, controls).

Surfaces scanned (absolute):
- `/home/vgpnk/Projects/shokuknow/merge/souji/knowledge/corpus/knowledge/duplicate-*.md`, `near-duplicate-*.md` (9 files) and `/home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md` (140 lines, rows S109–S242).
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-29/w1/` — 95 files / 46 seat reports at `2026-10-26T01:02:19Z`; 99 files / 50 reports at the final re-scan `01:03:28Z`, the three reports that landed meanwhile reviewed clean and in-bounds.
- `/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-29/` (7 files) and `/home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-registry-agreement.py` (123 lines).

Pre-write pattern sweep of the wave root, binary-safe, `grep -raicE`, every class zero:

| class probed | hits |
|---|---|
| 1Password secret-reference scheme (letters `op` then `:` slash slash) | 0 |
| GitHub token prefixes (`ghp`/`gho`/`ghs`/`ghu` plus underscore) | 0 |
| GitHub fine-grained PAT, GitLab `glpat`, Slack `xox`, AWS `AKIA`+16, Google `AIza`+20 | 0 |
| PEM private-key armour opener | 0 |
| request authorization header, response cookie header, password-equals form, user-colon-pass-at form | 0 |
| any `@` inside the authority of an http or https URL | 0 |
| ssh or git URL carrying a user part | 0 |
| loopback, unspecified, 10/8, 192.168/16, 172.16/12 authorities | 0 |
| `Users` and `root` home prefixes | 0 |
| internal / dot-local pseudo-TLD | 1 — only the prose path `~/.local/bin` at `SwarmExecutor08.md:43`, not a host |
| base64 blob with padding, 40+ chars | 0 |
| session-id, cookie, OAuth, `hvs`, npm, pypi token shapes | 0 |

Host inventory over all wave text (46 reports plus deliveries), scheme stripped: `man7.org` 45, `www.cs.princeton.edu` 22, `doi.org` 17, `ieeexplore.ieee.org` 11, `api.crossref.org` 4, then one each `qiita.com`, `github.com`, `git-scm.com`, `docs.gtk.org`, `roussev.net` — all public, none with a user part or a port.

Census surface: zero URL matches at all; the only home-prefix occurrences are the lane root (`records/census-start.txt:36`, `records/preregistration.txt:9`, `controls.sh:4`), all `/home/vgpnk/Projects/shokunin/souji-shokunin`; zero address matches; zero secret-reference matches.

Tool surface: `tools/souji-registry-agreement.py` has no URL, no credential, no address; git invoked as an argv list (`:20`), `--rev` constrained to full 40-hex (`:113`), reads only `cat-file`/`ls-tree`, writes nothing.

Instrument read-through (delivered; will land as `tools/` and `tests/fixtures/`): `deliver-souji-wave-evidence-capture.sh` runs git via argv lists (`:189`, `:205`, `:579`), never a shell string, never `eval`, has no network and no environment or key-directory reads, and validates `lane` absolute with no `..` segments (`:125-131`), `round` digits-only (`:123-125`), `--rev` 40-hex (`:133-137`) before its single destructive call `shutil.rmtree(dst)` (`:431`), where `dst` is derived as `lane` plus `census/round-<N>/waves` (`:632-633`) and refused when nested with `src` (`:412-420`) or when a symlink (`:423`). `deliver-r29-registry-agreement-fixture.py` calls `tempfile.mkdtemp(..., dir=BASE)` and removes only its own `workdir` (`:257-287`). `deliver-sources-diff.py:55` and `deliver-results-summary.py` use argv lists and only `json.load` / `ast.literal_eval`. `deliver-r29-wave-evidence-capture-fixture.sh:53-54` uses `mktemp -d` under `/var/tmp/souji-r29-*` with a quoted `trap` cleanup.

Delivery-path audit: every `## Deliveries` block of all 46 reports parsed and each absolute path classified against `.ufo/waves/round-29/w1/` and `/var/tmp/souji-r29-*`. Only exceptions: SwarmExecutor08 (finding 5) and SwarmScribe25's read-only reference to the merge package (a read, not a write).

## Findings

1. **CLEAN, all six surfaces.** No credential material of any class in the staged F3 inputs, the staged `SOURCES.append.md`, the wave directory, the preregistration, `census/round-29/`, or the C1 counter tool. Verdict is clean, not a partial list.

2. **Third-party addresses, public bibliographic (masked).** The Broder 1997 author address `b****r at pa.dec.com` sits in the copied paper text at `…/w1/sources/broder97resemblance.txt:5` and is repeated in prose at `…/w1/SwarmScout35.md:21`. Mailing-list addresses for man-pages (`m***-p***s at man7.org`) and diffutils (`b**-d******s at gnu.org`) are embedded in the fetched snapshots `sources/statx.2.html`, `sources/link.2.html`, `sources/cmp.1.html`. Class: third-party address inside public fetched bytes. Impact: none — no credential, published contact addresses belonging to the source itself. Smallest remediation: none; redacting would break the pinned sha256 and the Gate's verbatim-quote rule.

3. **Lane-identity contact in a query parameter (permitted, flagged).** `s****-lane at shokunin.org` at `/home/vgpnk/Projects/shokuknow/merge/souji/SOURCES.append.md:115` (staged row S217, Unpaywall) and at `…/knowledge/corpus/knowledge/near-duplicate-threshold-source-r34.md:3`. Class: lane-identity address used as an API parameter. Permitted by my brief. Note, not a defect: the string is absent from the lane's committed tree at `691dd29` (a `git grep` for it printed nothing), so it enters the lane only through the merge package; and that staged row is a rejected near-duplicate, not one of the four admitted rows. Impact: low — a role address disclosed to a third-party API, no credential.

4. **Placeholder addresses in fixtures.** `l*****t at example.invalid` at `…/w1/deliver-landing-checklist.md:199`, `r29 at s******.invalid` at `…/w1/SwarmExecutor03.md:27`, and `f*****e at localhost` at `…/w1/deliver-r29-wave-evidence-capture-fixture.sh:95` — throwaway git identities inside scratch repos; the reserved `.invalid` TLD is non-routable. Class: placeholder, not a leak. No action.

5. **Probe deviation outside the scratch bound, self-disclosed and cleaned.** `…/w1/SwarmExecutor08.md` Deliveries records three paths written outside the permitted `/var/tmp/souji-r29-<ItemId>/`: two capture files in `/tmp` and `/var/tmp/probe-uu.txt`. Class: write-bound breach, including the `/tmp` prohibition. The owner states all three were removed. Impact: none observable now. Smallest remediation: none retroactive; if that seat's commands are re-run, its probe files must sit inside its own scratch root.

6. **Plain-HTTP source locator — transport hygiene, not credential.** `roussev.net` is cited over cleartext `http` among the staged locators (`SOURCES.append.md`; also `…/knowledge/corpus/knowledge/near-duplicate-literature-identity-r33.md`, the Broder mirror). Impact: an on-path attacker could serve different bytes; already mitigated because the admitted row uses the `https` princeton.edu PDF and every Gate quote is checked against a sha256-pinned snapshot this round. No action on credential grounds.

7. **Package numbering versus lane numbering: the collision is real and already handled — do not append the staged rows.** In the staged package S216–S219 name *different documents* (`SOURCES.append.md:114-117`: Breitinger et al.; the Unpaywall record; git `gc.txt` v2.45.0; git `git-worktree.txt` v2.45.0), and the four F3 sources exist nowhere as staged rows. The lane tip at base has 139 rows ending at S215, so S216–S219 are free *in the lane*. Both scribe deliveries resolve this consistently: `deliver-sources-append-block.md:15-18` assigns lane S216=statx(2), S217=Broder, S218=link(2), S219=cmp(1); `:25-32` records the staged campaign ids S117/S118/S122/S136 and states that both id sets are already used in the package for other documents; `deliver-sources-rows.md:126-127` gives the collision table. Verdict: no defect. The L1 must append from `deliver-sources-append-block.md` and never by copying the staged `SOURCES.append.md` rows.

8. **Post-write re-scan note.** The only deltas after my own write are this report and four later seat reports (SwarmReviewer43, SwarmSimplifier67, SwarmCritic50, SwarmCritic52 — clean, deliveries in-bounds); the wave went 95 to 100 files. My first draft spelled the swept token shapes literally, which would have left secret-reference-scheme, token-prefix and header-name strings in the wave for the next pattern scanner; this version spells each class descriptively instead, so a re-scan sees zero. Confirmed after the final write at `01:03:53Z`: all fifteen probed classes zero, address set unchanged, host set unchanged.

## Deliveries
- `/home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-29/w1/SwarmSentinel62.md` — this report only. No scratch created (reads plus this write); no tool installed or upgraded; no `git` or `jj` mutation; no signal; no fleet-wide broadcast.
