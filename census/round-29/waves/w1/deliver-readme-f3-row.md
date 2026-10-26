# Deliver — README coverage-map F3 row (round 29 C3)

Paste target: `corpus/README.md`, line 41 (the `### Coverage map` table, F3 row). Replace
that one line; no other README line changes.

## Exact replacement line

```markdown
| F3 duplicate verdicts | frontier, entries held | `knowledge/dupe-finders-detect-then-act.md`, `knowledge/duplicate-verdict-identity.md`, `knowledge/duplicate-verdict-byte-equality.md` |
```

## What it replaces (base `691dd29211c53d0ef94fa072394cb9c8a69fe92e`)

```markdown
| F3 duplicate verdicts | frontier, entry held | `knowledge/dupe-finders-detect-then-act.md` |
```

## Why

`tools/souji-coverage-agreement.py` maps every knowledge entry whose front matter carries
`ground: F<k>` to a coverage-map row whose ground cell begins `F<k>` and whose entries cell
names it as a backticked `knowledge/<name>` path. Both admitted entries carry `ground: F3`, so
without the two added paths they would be reported `MISSING-FROM-MAP`.

## Measured effect (scratch clone, rev `53264d05f4163c876eb9c4ddf297ddba1a9723c3`)

```
$ python3 -B tools/souji-coverage-agreement.py --root . --rev 53264d05f4163c876eb9c4ddf297ddba1a9723c3
grounded=15 mapped=15 dangling=0 mismatches=0
rc=0
```

The ground cell keeps its `F3` prefix; the status cell moves from `entry held` to
`entries held`. The `## Frontier` bullet at `corpus/README.md:48` is left unchanged by this
delivery (it describes the open operator decision, which this round does not take).
