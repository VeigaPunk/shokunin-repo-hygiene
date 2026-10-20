# ReopenS046 — S046 (git-check-attr(1)) re-opened and attacked

Target: `corpus/SOURCES.md` row S046 (worktree, line 60).
Evidence base: live page https://git-scm.com/docs/git-check-attr fetched 2026-10-20 (reader proxy; served manual body, "Latest version" banner, and change list), host `git version 2.56.0` installed `git-check-attr(1)`, and the two named consumers at HEAD.

HEAD moved during the audit (lane was `a6ec7810` with SOURCES.md uncommitted at first read; L1 committed and HEAD became `163158a706352f1c0ee3521c4da2e5289970db57`, with `a6ec7810` an ancestor). The S046 row bytes are identical in both: `git show HEAD:corpus/SOURCES.md | grep -n S046` returns the same row as the worktree line 60, and `corpus/SOURCES.md` is clean at `163158a`. All line citations below resolve at both revisions.

## What the page actually says (observed)

- Version banner: `git-check-attr last updated in 2.52.0`; change list first entry `2.53.0 → 2.56.0 no changes`. Row's provenance string matches both literally.
- § OPTIONS `-z`: "The output format is modified to be machine-parsable. If `--stdin` is also given, input paths are separated with a NUL character instead of a linefeed character."
- § OPTIONS `--stdin` alone: "Read pathnames from the standard input, one per line, instead of from the command line."
- § OUTPUT: "The output is of the form: <path> COLON SP <attribute> COLON SP <info> LF unless `-z` is in effect, in which case NUL is used as delimiter: <path> NUL <attribute> NUL <info> NUL", then `<info>` = `unspecified` | `unset` | `set` | `<value>`.

Located quote (≤25 words, § OUTPUT, 19 words — the same quote the lesson Gate carries):

> "unless -z is in effect, in which case NUL is used as delimiter: <path> NUL <attribute> NUL <info> NUL"

## Cell-by-cell attack

| cell | attack result |
|---|---|
| scope "`-z`/`--stdin` record framing for attribute lookup, not driver execution" | **holds.** Framing is exactly the section pair the page documents. "not driver execution" is a negative boundary, not a page claim; nothing in the row credits the page with it (and the page never discusses drivers). |
| anchor "web manual … § OUTPUT, § OPTIONS -z" | **holds.** Both headings exist with that exact id; the two version strings are verbatim. Rechecking the installed manual adds the section pair unchanged (see below). |
| teaches | **holds, phrase by phrase.** Output form is verbatim from § OUTPUT; "--stdin paths are NUL-separated" is verbatim from § OPTIONS -z (conditioned on `-z`, as the row's "with -z" scopes it). "the census parses stride-3 records" is observable: `tools/souji-census.sh:1008` runs `check-attr -z --stdin filter`, `:1011` fails closed unless `% 3 == 0`, `:1012` reads the `<info>` field at `i = 2; i += 3`. Train of reasoning carries from documented framing to shipped code with no unstated hop. |
| kind / tier `docs` / `A` | **holds.** Primary vendor reference manual; every primary vendor/upstream reference in the registry is A (S001–S013, S033, S035, S036, S042), and the contract's tier definitions are not repeated here. B is reserved for a community blog, a vendor write-up and a book (S014, S017, S029); a primary git manual is not that class. |
| status `mined` | **holds.** Used-by is a lesson that names the claim (below); same convention as S038/S040. |
| opened `2026-10-20` | **holds.** Page served today; row/lesson record the L1 re-derivation, and `census/round-16/seat-audit-w1.json` independently records the voided seat (`SrcGitCheckAttr`: 26 calls, 1 minor `V-RECURSIVE` at line 69), which is what "seat draft is void under the probe rule" asserts. |
| recheck `on-release` | **holds.** Content is version-pinned and frozen since 2.52.0 with a served "no changes 2.53.0 → 2.56.0" list; a new git release is the only drift trigger. (365d would also be defensible, but on-release is the house rule for git docs and is not wrong here.) |
| used-by `corpus/lessons/round-16.md` | **holds.** Lesson line 29 is the Gate record with the exact quote; line 35 states "C1's bound-filter skip, check-attr parsing, XDG default and lazy-fetch export rest on S045, S046, S047, S049". That is the claim the census code implements. |

## Is it truly used by the claim it names?

- `tools/souji-census.sh:1002-1016` (HEAD) is the only consumer: `check-attr -z --stdin filter` fed by `ls-files -z`, stride-3 modulo check, `<info>` compared against `filter.<name>.clean|smudge|process` config keys. Load-bearing: without the documented NUL record framing, `mapfile -d ''` would yield 1 field and every repo with any configured filter driver would be misread (fail-closed to `unverifiable`), i.e. the framing is what makes the changed-arm fixture rows behave.
- `tools/souji-landing-gate.py` has **zero** `check-attr` references (`git show HEAD:… | grep -c check-attr` → 0). The row correctly does not name the gate.
- No other file is claimed; no second registry row shares this URL (the two `git-check-attr` hits in SOURCES.md are the S046 row at line 60 and the Paths narrative at line 84, which independently states "L1 re-opened git-check-attr (the seat that first opened it breached the round's probe rule)" and lists the "check-attr records" claim).

## Version drift check (strengthens the row, no defect)

Host `git --version` is 2.56.0, and `man -P cat 1 git-check-attr` § OUTPUT is byte-for-byte the web text quoted above (including the `-z` NUL form). So the "latest" web manual is not ahead of or behind the host for this page; the page's own 2.52.0/2.56.0 statement is borne out by the installed copy.

## Failed attacks (page survives)

- `--stdin`-alone framing: page says one-per-line; the row attaches NUL separation to "with -z", matching the page's condition. Not a false statement.
- Multiple requested attributes (stride would still be 3 per answer) and `<info>` being `set`/`unset`/`unspecified`/`<value>`: the census reads `i = 2 mod 3` only, so any of the four forms lands in the right slot; page's description is sufficient.
- Pathological paths: page's `-z` fields are raw bytes with NUL as delimiter, and git paths cannot contain NUL, so field count cannot exceed 3 per answer.
- Provenance inflation: the anchor's "re-derived; seat draft void" is meta, is corroborated by the seat audit, and has precedent in S042's anchor. Not a defect.

## Minor calibration notes (none changes the verdict; each has a smallest fix)

1. **Quote covers the OUTPUT half only.** The teaches cell's second clause ("--stdin paths are NUL-separated") rests on § OPTIONS `-z`, which the anchor names but the ≤25-word Gate quote does not include. Truth is unaffected (the anchor is the locator). Smallest fix, if L1 wants the quote to carry both halves: replace with the 21-word `-z` sentence — "The output format is modified to be machine-parsable. If --stdin is also given, input paths are separated with a NUL character".
2. **Scope's "`-z`/`--stdin`" slash-pair.** Read as a pair it is right; read as independent flags it would imply `--stdin` alone is NUL-framed, which the page denies ("one per line"). Smallest fix: `-z` with `--stdin` record framing.
3. **No version and no installed-man citation in the anchor.** Neighbouring git rows pin a version (S001 "git 2.55.0 …") and cite the installed roff. Here the version lives only in the "last updated / no changes" strings. Smallest fix: prepend `git 2.52.0–2.56.0` to scope and append `; installed man page git 2.56.0` to the anchor (verified identical today).

## Adjacent note for C1 (not an S046 defect)

`tools/souji-census.sh:982` asserts "Neither ls-files nor check-attr runs a driver." That negative is not grounded by any registry row: S046 explicitly scopes driver execution out and S045 covers only the check-in conversion path. The claim is true but unwitnessed; C1 should either ground it (e.g. a `git-check-attr`/`ls-files` source or manual statement) or strike the comment. It does not weaken S046, which is honest about what it does not cover.

## Verdict

**holds.** The page supports the scope and teaches cells as written, the quote is faithful and located at § OUTPUT, tier `A` / status `mined` / recheck `on-release` match both the registry's own conventions and this source's version behaviour, and the row is genuinely load-bearing for the claim it names in `corpus/lessons/round-16.md` (`tools/souji-census.sh:1008-1016` at HEAD). Three cosmetic refinements are offered above; none is a factual failure.

## Commands

```
grep -n "S046" /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
git -C /home/vgpnk/Projects/shokunin/souji-shokunin rev-parse HEAD; git -C /home/vgpnk/Projects/shokunin/souji-shokunin status --porcelain | head -30
sed -n '1,20p;50,70p' /home/vgpnk/Projects/shokunin/souji-shokunin/corpus/SOURCES.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "check-attr\|stride\|read -d ''\|-z" tools/souji-census.sh | head -40; echo ---; grep -n "check-attr" tools/souji-landing-gate.py | head
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:corpus/SOURCES.md | grep -n "S046"; echo "---lesson---"; grep -n "S046\|check-attr" corpus/lessons/round-16.md | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '975,1045p' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -rn "SOURCES-CONTRACT-v1" corpus/SOURCES.md corpus/QUALITY.md | head; ls corpus/*contract* 2>/dev/null
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '20,60p' corpus/lessons/round-16.md; echo "=== git version ==="; git --version; echo "=== installed man ==="; zcat /usr/share/man/man1/git-check-attr.1.gz 2>/dev/null | col -b | sed -n '/^OUTPUT/,/^EXAMPLES/p' | head -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "tier\|Tier\|mined\|queued\|rejected\|recheck\|on-release\|on-change\|quote" corpus/QUALITY.md | head -50
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '1,14p' corpus/QUALITY.md; echo "=== man ==="; man -P cat 1 git-check-attr 2>/dev/null | sed -n '/^OUTPUT/,/^EXAMPLES/p' | head -20
cd /home/vgpnk/Projects/shokunin/souji-shokunin && awk 'NR>=1000 && NR<=1020 {printf "%d\t%s\n", NR, $0}' tools/souji-census.sh
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "Tier\|tier\|status vocabulary\|mined\|queued\|recheck" corpus/SOURCES.md | sed -n '1,40p'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && wc -l corpus/SOURCES.md; sed -n '1,1p' corpus/SOURCES.md | cut -c1-200; grep -c "^| S0" corpus/SOURCES.md
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sha256sum tools/souji-census.sh; echo "--- HEAD lines ---"; git show HEAD:tools/souji-census.sh | awk 'NR>=1007 && NR<=1017 {printf "%d\t%s\n", NR, $0}'; echo "--- gate hits ---"; git show HEAD:tools/souji-landing-gate.py | grep -c "check-attr"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:corpus/lessons/round-16.md 2>&1 | head -2; echo "rc=$?"; git log --oneline -3 -- corpus/lessons/round-16.md; git check-ignore -v corpus/lessons/round-16.md || true
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git rev-parse HEAD; git merge-base --is-ancestor a6ec7810e9b5cca2d8ca997f5cdcf2ead84b93ae HEAD && echo "a6ec781 is ancestor"; echo "--- HEAD SOURCES S046 ---"; git show HEAD:corpus/SOURCES.md | grep -n "S046" | cut -c1-400; echo "--- status now ---"; git status --porcelain | head -12
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -o "SrcGitCheckAttr[^,}]*" census/round-16/seat-audit-w1.json | head -20; echo "---"; grep -c "SrcGitCheckAttr" census/round-16/seat-audit-w1.json
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:corpus/lessons/round-16.md | awk 'NR==29' | wc -w; git show HEAD:corpus/lessons/round-16.md | awk 'NR==29'
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
d=json.load(open('census/round-16/seat-audit-w1.json'))
def walk(o,p=''):
    if isinstance(o,dict):
        for k,v in o.items(): walk(v,p+'/'+k)
    elif isinstance(o,list):
        for i,v in enumerate(o): walk(v,p+f'[{i}]')
    else:
        if 'CheckAttr' in str(o): print(p,'=',str(o)[:300])
walk(d)
" 2>&1 | head -30
cd /home/vgpnk/Projects/shokunin/souji-shokunin && python3 -c "
import json
d=json.load(open('census/round-16/seat-audit-w1.json'))
print(type(d), list(d)[:8] if isinstance(d,dict) else len(d))
def find(o):
    if isinstance(o,dict):
        for k,v in o.items():
            if k=='SrcGitCheckAttr' or ('CheckAttr' in k): print(json.dumps({k:v},indent=1)[:1200])
            find(v)
    elif isinstance(o,list):
        for v in o: find(v)
find(d)
"
cd /home/vgpnk/Projects/shokunin/souji-shokunin && git show HEAD:tools/souji-census.sh | awk 'NR>=980 && NR<=983 {printf "%d\t%s\n", NR, $0}'; printf '%s' 'unless -z is in effect, in which case NUL is used as delimiter: <path> NUL <attribute> NUL <info> NUL' | wc -w; printf '%s' 'The output format is modified to be machine-parsable. If --stdin is also given, input paths are separated with a NUL character' | wc -w
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -c "git-check-attr" corpus/SOURCES.md; grep -n "| B |" corpus/SOURCES.md | cut -c1-120
cd /home/vgpnk/Projects/shokunin/souji-shokunin && grep -n "git-check-attr" corpus/SOURCES.md | cut -c1-160
cd /home/vgpnk/Projects/shokunin/souji-shokunin && sed -n '84p' corpus/SOURCES.md | fold -w 160 | head -12
cd /home/vgpnk/Projects/shokunin/souji-shokunin && diff <(sed -n '60p' corpus/SOURCES.md) <(git show HEAD:corpus/SOURCES.md | sed -n '60p') && echo IDENTICAL; cmp -s <(sed -n '60p' corpus/SOURCES.md) <(git show HEAD:corpus/SOURCES.md | sed -n '60p') && echo BYTE-IDENTICAL
cd /home/vgpnk/Projects/shokunin/souji-shokunin && man -P cat 1 git-check-attr 2>/dev/null | sed -n '/^OPTIONS/,/^OUTPUT/p' | sed -n '1,24p'
```

Web read (not a shell command): https://git-scm.com/docs/git-check-attr fetched via the reader on 2026-10-20.

No tool installed or upgraded; no ALLOWED-EXEC command run; nothing written outside this report.

STATUS: ok
