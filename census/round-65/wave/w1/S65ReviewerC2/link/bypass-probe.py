#!/usr/bin/env python3
"""S65ReviewerC2 F1 probe: bypass shapes against live_markers() of the COMMITTED c2-counter bytes."""
import importlib.util
spec = importlib.util.spec_from_file_location("c2", "/home/vgpnk/Projects/shokunin/souji-shokunin/census/round-65/c2-counter.py")
c2 = importlib.util.module_from_spec(spec); spec.loader.exec_module(c2)
flag = c2.MARKERS["flag"].decode()

# (a) docstring: needle + literal refuse( on ONE docstring line → LIVE (false green)
live_docstring = ('def disabled(p):\n'
    '    """Was refuse("' + flag + ': " + p) up to rXX; retired after the in-run re-reads landed.\n'
    '    """\n'
    '    pass\n')
# (a2) docstring SPLIT: refuse( and needle on DIFFERENT docstring lines → DEAD
split_docstring = ('def disabled(p):\n'
    '    """Legacy notes: emitted via refuse(\n'
    '    with message ' + flag + ' (retired).\n'
    '    """\n'
    '    pass\n')
# (b) f-string assigned to a dead name, never used; return only on ANOTHER line → DEAD
split_fstring = ('DEADF = f"refuse( {RECEIPT_INDEX_FLAG_CONCEALED} )"\n'
    'def f(x):\n'
    '    return x\n')
# (b2) plain literal UNUSED but its own line carries both return and refuse(<needle>) → LIVE
same_line_literal = 'DEADF = "return refuse(' + flag + ')"\n'
# (c) annotation carrying needle wrapped in refuse(...) text on the signature line, body returns 0
live_annotation = "def g(cmds: list['refuse(" + flag + ")']) -> int:\n    return 0\n"
# (c2) annotation carrying BARE needle (no refuse( beside it), return on next line → DEAD
split_annotation = "def g(cmds: list['" + flag + "']) -> int:\n    return 0\n"
# (c3) annotation one-liner: needle + return on same physical line → LIVE
same_line_annotation = "def g(cmds: list['" + flag + "']) -> int: return 0\n"
# (control) genuine live refusal line
control = "def h(p) -> str: return refuse('" + flag + "')\n"

for name, blob in [("docstring-needle-and-refuse-one-line", live_docstring),
                   ("docstring-split-lines", split_docstring),
                   ("fstring-dead-name-return-elsewhere", split_fstring),
                   ("literal-unused-return-same-line", same_line_literal),
                   ("annotation-refuse-wrapped-signature-line", live_annotation),
                   ("annotation-bare-needle-return-next-line", split_annotation),
                   ("annotation-one-liner-same-line", same_line_annotation),
                   ("control-genuine-refuse-call", control)]:
    m = c2.live_markers(blob.encode())
    print(f"BYPASS-PROBE {name}: flag-live={m['flag']}")
