#!/usr/bin/env python3
"""souji r93 C2 fixture (the r92 fixture plus KFF19, an exact-window reference sweep, and KFF20, an ill-formed lead
across the HEAD cut). r92 C2 fixture (the r91 fixture plus five cases and an AST-based KFF13). r90 C2 fixture: the K4 delegation's index-flag failure detail is ONE escaped line that keeps both ends of
the writer's stderr AND spells a raw byte distinctly from the character that decodes to it, measured through the
tool's public path.

r90 change: the r89 tool renders both the raw byte 0x85 and the UTF-8 encoding of U+0085 (NEL) as `\\x85`, so two
materially different delegated failures share one cell. The r90 tool spells U+0085 as `\\u0085`; KFF9 and KFF10
measure the pair and main() additionally requires the two details to differ.

r91 change: four clauses the r90 fixture's wording claimed but did not enforce now have cases. KFF9/KFF10 reject the
DOUBLED-backslash spellings; KFF11 cuts a 201-byte stderr inside U+0085's two-octet encoding and requires neither
spelling (the r90 tool printed the orphan continuation as the raw byte's spelling); KFF12 requires the cell to keep
the text after `marker` and carry no raw line separator (one physical line); KFF13 scans the tool source for the dead
`_one_line` helper. The r90 fixture is the control: the r90 tool passes it 12/12, and the three r91 variants each
pass it 12/12.

r92 change (r91 A2, spot-check routed items 1/2/4): the r91 `_cut_tail` trusted the lead byte's structural length
(C0-DF/2, E0-EF/3, F0-F7/4) and moved the tail cut past bytes that were not a well-formed sequence, landing it inside a
LATER valid sequence. KFF14/KFF15 are the R91ExecC2Tool repro pair (payload A carries a valid U+0085 after an
ill-formed F0 80 lead, payload B the raw byte 0x85 in the same place): A must spell U+0085 as the character and B as
the byte, and the two cells must differ. KFF16 puts an overlong E0 80 80 (ill-formed per Unicode Table 3-7, S355: E0 needs A0..BF
next) across the tail cut, followed by a valid U+0085: a cut that checks only that the declared bytes are
continuations (the r91 A2 routed repair without range checks) still swallows both 0x80 bytes. KFF17 puts a valid U+20AC across the HEAD cut (no escape may appear).
KFF18 imports the tool under test and sweeps 29,700 deterministic payloads (15 well-formed and ill-formed byte tokens,
pairwise, at offsets 84-117 around both cuts, lengths 205/210/214): the excerpt's head must be a prefix and its tail a
suffix of the tool's own full rendering `_escape_text(_decode_record(raw))`. KFF13 is now an `ast` check (no function
definition named `_one_line`, no call whose callee is named `_one_line`); a fixture self-check proves it detects a
spaced `def _one_line (x)` and ignores a docstring that merely mentions `_one_line(` before any case is scored
(rc 2 if not).

r93 change (r92 A1, spot-check routed item 1): KFF18 checks only that the head is SOME prefix and the tail SOME
suffix of the full rendering, so three one-edit forgeries of the filed tool passed the r92 fixture 20/20 (R92MutC2:
C surrogatepass decode, D `len(...) >= 1`, E head cut moved forward). KFF19 pins the cut POSITION: an independent
reference cut written from the WHATWG Encoding Standard's UTF-8 decoder (S356, §8.1.1: per-lead bytes needed and
lower/upper boundaries 0xA0/0x9F/0x90/0x8F, never Python's codec) finds the one well-formed sequence a cut would
split, and the excerpt must EQUAL the cell built from the reference cuts on a boundary-class sweep (every Table 3-7
boundary encoding and its ill-formed neighbours, pairwise, at every byte offset across both cuts). KFF20 is the
mirror of KFF16 on the HEAD cut (R92Connector §3): an overlong E0 80 80 straddles the head cut, so a cut that trusts
the lead's length elides E0 80 instead of keeping both escapes.

Each case runs a copy of the tool under test beside a fake receipt writer in a hermetic scratch repository. The fake
writer's `git()` fails the delegated `ls-files -v -z` read with a chosen stderr, so the bootstrap's FLAGFAIL branch
fires with no lane byte involved. The tool is run as a subprocess and its `MISMATCH\tK4\t...` records are read back
exactly as a line-oriented consumer would.

Cases:
  KFF1 short     a single-line message: the detail names it.
  KFF2 trace     a three-line traceback ending `AttributeError: boom`: the detail is ONE physical line that names the
                 exception (the r87 tool printed it raw, so the row split and the K4 line lost the name).
  KFF3 long      a 400-character line starting `AttributeError: `: the head (the type name) and the tail survive the
                 200-character bound (the r87 tool kept the tail only).
  KFF4 controls  a line carrying SOH, NEL and U+2028: the detail escapes all three and stays one physical line
                 (the r87 tool embedded them raw; `str.splitlines()` tears NEL and U+2028).
  KFF5 empty     empty stderr: `no stderr`, never an empty parenthesis.
  KFC1 clean     the delegated ls-files read succeeds: no K4 row (a blanket refusal is not a gain).
  KFC2 refused   the writer refuses with a second, forged MISMATCH line: one escaped REFUSED detail, no injected row.
  KFF6 badbyte   stderr carrying an invalid UTF-8 byte: one escaped line, surrounding text kept (S88Sentinel F1).
  KFF7 literal   stderr carrying the literal escape spelling: the detail differs from KFF6 (injectivity).
  KFF8 headctl   25 leading SOH bytes then `AttributeError: boom`: the type name stays in the head (S88Sentinel F2).
  KFF9 nelchar   stderr carrying the UTF-8 encoding of U+0085: the cell spells it with the u0085 escape, never with
                 the x85 escape or the doubled-backslash spelling (r90/r91).
  KFF10 nelbyte  stderr carrying the raw byte 0x85: the cell spells it with the x85 escape, never with the u0085
                 escape or its doubled spelling; the pair differs.
  KFF11 nelcut   a 201-byte stderr whose U+0085 straddles the tail cut: neither spelling appears (r91).
  KFF12 oneline  the nelchar cell keeps the text after `marker` and holds no raw line separator (r91).
  KFF13 decl     the tool source parses and holds no `_one_line` definition and no call to `_one_line` (r92: ast).
  KFF14 invcutA  210-byte payload A (F0 80 61 C2 85 at the tail cut): one u0085 spelling, no x85 spelling (r92).
  KFF15 invcutB  210-byte payload B (F0 80 61 62 85): one x85 spelling, no u0085 spelling; cell differs from A (r92).
  KFF16 overlong 210-byte payload with E0 80 80 C2 85 at the tail cut: one u0085 and two x80 spellings, no x85.
  KFF17 headcut  a U+20AC straddling the head cut: no backslash-x escape appears in the cell (r92).
  KFF18 sweep    in-process: 29,700 payloads, every excerpt head a prefix / tail a suffix of the full rendering (r92).
  KFF19 exact    in-process: the excerpt equals the reference-cut cell on the boundary-class sweep (r93).
  KFF20 headill  211-byte payload with E0 80 80 across the head cut: exactly one xe0 and one x80 spelling (r93).

The same table runs on `--before` (the r91 tool bytes since r92): every case the before tool fails is the do-nothing control.
Exit 0 iff every case passes on `--tool` and the before tool passes strictly fewer; 1 otherwise; 2 on usage or a
fixture failure. Writes only under --work (never /tmp), removes what it builds, and reads the lane read-only.

Stdlib only. Python 3.14, git 2.56.0; the fixture repo is synthetic and hermetic.
"""
import argparse
import ast
import hashlib
import importlib.util
import os
import shutil
import subprocess
import sys

sys.dont_write_bytecode = True

FAKE_WRITER = '''# r90 fake receipt writer for the K4 delegation fixture (one rule: no file, no network)
import os


class P:
    def __init__(self, returncode, stdout=b"", stderr=b""):
        self.returncode, self.stdout, self.stderr = returncode, stdout, stderr


def git(*args, **kwargs):
    mode = os.environ.get("R90_STDERR_MODE", "short")
    if mode == "clean":
        return P(0, b"H a.txt\\0")
    err = {
        "short": b"fatal: cannot read index\\n",
        "trace": b"Traceback (most recent call last):\\n  File \\"w\\", line 1\\nAttributeError: boom\\n",
        "long": b"AttributeError: " + b"x" * 380 + b"\\n",
        "controls": b"fatal: \\x01 \\x85 \\xe2\\x80\\xa8 marker\\n",
        "empty": b"",
        "badbyte": b"bad \\xff tail\\n",
        "literal": b"literal \\\\xff tail\\n",
        "headctl": b"\\x01" * 25 + b"AttributeError: boom" + b"y" * 240 + b"\\n",
        "nelchar": b"fatal: nel \\xc2\\x85 marker tailtkn\\n",
        "nelcut": b"fatal: nel " + b"x" * 90 + b"\\xc2\\x85" + b"s" * 98,
        "nelbyte": b"fatal: nel \\x85 marker\\n",
        "invcutA": b"fatal: inv " + b"a" * 99 + b"\\xf0\\x80a\\xc2\\x85" + b"b" * 95,
        "invcutB": b"fatal: inv " + b"a" * 99 + b"\\xf0\\x80ab\\x85" + b"b" * 95,
        "overlong": b"fatal: ovl " + b"a" * 99 + b"\\xe0\\x80\\x80\\xc2\\x85" + b"b" * 95,
        "headcut": b"fatal: hcut " + b"h" * 87 + b"\\xe2\\x82\\xac" + b"t" * 110,
        "headill": b"fatal: hil " + b"h" * 87 + b"\\xe0\\x80\\x80" + b"t" * 110,
    }[mode]
    return P(1, b"", err)


def _truth_refusal(root):
    if os.environ.get("R90_REFUSED") == "1":
        raise SystemExit("r89 refused: bad\\nMISMATCH\\tK4\\t.\\tforged\\tinjected")
    return ""


def _flag_refusal(*args):
    return None
'''

ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update({"GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull, "LC_ALL": "C",
            "GIT_AUTHOR_NAME": "r90 fixture", "GIT_AUTHOR_EMAIL": "fixture@r90.invalid",
            "GIT_COMMITTER_NAME": "r90 fixture", "GIT_COMMITTER_EMAIL": "fixture@r90.invalid",
            "GIT_AUTHOR_DATE": "2026-11-08T00:00:00Z", "GIT_COMMITTER_DATE": "2026-11-08T00:00:00Z"})


class FixtureError(Exception):
    pass


def git(repo, *args):
    if not repo or not os.path.isabs(repo):
        raise FixtureError(f"refusing git -C with {repo!r}")
    p = subprocess.run(["git", "-C", repo, "-c", "core.hooksPath=/dev/null", *args],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENV)
    if p.returncode != 0:
        raise FixtureError(f"git {' '.join(args)} rc={p.returncode}: {p.stderr.decode()[:200]}")
    return p.stdout.decode().strip()


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def make_kit(root, tool):
    """A tool copy beside a fake writer, and a hermetic repo with one commit."""
    tools = os.path.join(root, "tools")
    os.makedirs(tools)
    copy = os.path.join(tools, "souji-record-agreement.py")
    shutil.copyfile(tool, copy)
    with open(os.path.join(tools, "souji-receipt-write.py"), "w", encoding="utf-8") as f:
        f.write(FAKE_WRITER)
    repo = os.path.join(root, "repo")
    os.makedirs(repo)
    git(repo, "init", "-q")
    with open(os.path.join(repo, "a.txt"), "w", encoding="utf-8") as f:
        f.write("seed\n")
    git(repo, "add", "--", "a.txt")
    git(repo, "commit", "-q", "--no-verify", "-m", "r90 fixture seed")
    return copy, repo, git(repo, "rev-parse", "HEAD")


def run_case(kit, mode, refused=False):
    toolcopy, repo, rev = kit
    env = dict(ENV)
    env["R90_STDERR_MODE"] = mode
    env["R90_REFUSED"] = "1" if refused else "0"
    p = subprocess.run([sys.executable, "-B", toolcopy, "--root", repo, "--rev", rev],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
    out = p.stdout.decode("utf-8", "backslashreplace")
    rows = []
    for line in out.split("\n"):
        if not line.startswith("MISMATCH\tK4\t"):
            continue
        cells = line.split("\t", 4)
        rows.append(cells[4] if len(cells) == 5 else "<short-row>")
    return out, rows


def case_short(out, rows):
    return len(rows) == 1 and "fatal: cannot read index" in rows[0]


def case_trace(out, rows):
    return (len(rows) == 1 and "AttributeError: boom" in rows[0] and "\\n" in rows[0]
            and "\n  File " not in out)


def case_long(out, rows):
    return (len(rows) == 1 and "AttributeError" in rows[0] and "\u2026" in rows[0]
            and len(rows[0]) <= 260)


def case_controls(out, rows):
    return (len(rows) == 1 and "\\x01" in rows[0] and "\\x85" in rows[0] and "\\u2028" in rows[0]
            and "\x01" not in out and "\x85" not in out and "\u2028" not in out)


def case_empty(out, rows):
    return len(rows) == 1 and "no stderr" in rows[0]


def case_clean(out, rows):
    return len(rows) == 0


def case_badbyte(out, rows):
    # KFF6 (S88Sentinel F1): the raw byte 0xFF renders as ONE backslash spelling (exactly one backslash before "xff").
    bs = chr(92)
    return len(rows) == 1 and "bad " in rows[0] and rows[0].count(bs + "xff") == 1 and rows[0].count(bs * 2 + "xff") == 0 and "tail" in rows[0]



def case_literal(out, rows):
    # KFF7 (S88Sentinel F1): the literal characters render with a DOUBLED backslash (the backslash doubled, none bare).
    bs = chr(92)
    return len(rows) == 1 and "literal " in rows[0] and rows[0].count(bs * 2 + "xff") == 1 and rows[0].count(bs + "xff") == 1


def case_headctl(out, rows):
    # KFF8 (S88Sentinel F2): 25 leading control bytes must not consume the head; the type name stays visible.
    return len(rows) == 1 and "AttributeError" in rows[0] and "boom" in rows[0]


def case_nelchar(out, rows):
    # KFF9 (r90; r91 doubled-spelling conjunct): the character U+0085, encoded UTF-8, is spelled with the u0085
    # escape; the raw-byte spelling is the OTHER member of the pair and must not appear, and neither must the
    # DOUBLE-backslash spelling (a variant that emits two backslashes used to pass on the single count).
    bs = chr(92)
    return (len(rows) == 1 and "fatal: nel" in rows[0] and "marker" in rows[0]
            and rows[0].count(bs + "u0085") == 1 and rows[0].count(bs + "x85") == 0
            and rows[0].count(bs * 2 + "u0085") == 0)


def case_nelbyte(out, rows):
    # KFF10 (r90; r91 doubled-spelling conjunct): the raw byte 0x85 (invalid UTF-8) takes the x85 escape; the
    # character spelling and the double-backslash spelling must not appear.
    bs = chr(92)
    return (len(rows) == 1 and "fatal: nel" in rows[0] and "marker" in rows[0]
            and rows[0].count(bs + "x85") == 1 and rows[0].count(bs + "u0085") == 0
            and rows[0].count(bs * 2 + "x85") == 0)


def case_nelcut(out, rows):
    # KFF11 (r91): a 201-byte stderr whose U+0085 straddles the raw tail cut. Whole sequences only: neither the
    # character spelling nor the raw-byte spelling may appear (the r90 tool printed the orphan 0x85 as the byte one).
    bs = chr(92)
    return (len(rows) == 1 and "fatal: nel" in rows[0]
            and rows[0].count(bs + "x85") == 0 and rows[0].count(bs + "u0085") == 0)


def case_oneline(out, rows):
    # KFF12 (r91): ONE physical line -- the cell keeps the text after `marker` (tailtkn) and contains no raw line
    # separator. A variant that injects a newline mid-detail loses the tail (and passed the r90 fixture).
    return (len(rows) == 1 and "marker" in rows[0] and "tailtkn" in rows[0]
            and not any(sep in rows[0] for sep in ("\n", "\r", "\u2028", "\u2029", "\u0085")))


def _one_line_refs(src):
    """KFF13 (r92): (definitions, calls) of a callable named `_one_line` in the parsed source. Whitespace before the
    paren cannot hide either, and a docstring or comment that names the token is not code (R91ReviewerC2)."""
    defs = calls = 0
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "_one_line":
            defs += 1
        elif isinstance(node, ast.Call):
            fn = node.func
            name = fn.id if isinstance(fn, ast.Name) else (fn.attr if isinstance(fn, ast.Attribute) else None)
            calls += name == "_one_line"
    return defs, calls


def kff13_selfcheck():
    """Both directions the r91 literal scan got wrong, proved before any case is scored."""
    spaced = 'def _one_line (text):\n    return text\n\n\nx = _one_line ("v")\n'
    mention = 'def f():\n    """the deleted _one_line(text) helper is gone"""\n    return 1\n'
    return _one_line_refs(spaced) == (1, 1) and _one_line_refs(mention) == (0, 0)


def case_source(tool):
    # KFF13 (r92): the dead escape-first helper stays deleted: no definition and no call in the parsed tool source.
    with open(tool, encoding="utf-8") as f:
        src = f.read()
    return _one_line_refs(src) == (0, 0)


def case_invcut_a(out, rows):
    # KFF14 (r92): the valid U+0085 after the ill-formed F0 80 lead keeps its character spelling.
    bs = chr(92)
    return (len(rows) == 1 and "fatal: inv" in rows[0]
            and rows[0].count(bs + "u0085") == 1 and rows[0].count(bs + "x85") == 0)


def case_invcut_b(out, rows):
    # KFF15 (r92): the raw byte 0x85 in the same place keeps its byte spelling.
    bs = chr(92)
    return (len(rows) == 1 and "fatal: inv" in rows[0]
            and rows[0].count(bs + "x85") == 1 and rows[0].count(bs + "u0085") == 0)


def case_overlong(out, rows):
    # KFF16 (r92): E0 80 80 is ill-formed (Table 3-7: E0 needs A0..BF next), so the cut must not swallow it as a
    # three-octet sequence: both 0x80 bytes keep their spelling and the valid U+0085 after them keeps its own.
    bs = chr(92)
    return (len(rows) == 1 and "fatal: ovl" in rows[0] and rows[0].count(bs + "u0085") == 1
            and rows[0].count(bs + "x80") == 2 and rows[0].count(bs + "x85") == 0)


def case_headcut(out, rows):
    # KFF17 (r92): a well-formed U+20AC across the head cut is elided whole; no byte escape appears.
    bs = chr(92)
    return len(rows) == 1 and "fatal: hcut" in rows[0] and rows[0].count(bs + "x") == 0


SWEEP_TOKENS = (b"a", b"\xc2\x85", b"\xe2\x82\xac", b"\xf0\x9d\x84\x9e", b"\x85", b"\xf0\x80", b"\xe0",
                b"\xc0\xaf", b"\xe0\x80\x80", b"\xed\xa0\x80", b"\xf4\x90\x80\x80", b"\xf5\x80", b"\xc1\xbf",
                b"\xe2\x82", b"\xff")


def sweep_payloads():
    for off in range(96, 118):
        for a in SWEEP_TOKENS:
            for b in SWEEP_TOKENS:
                for total in (205, 210, 214):
                    tail = b"x" * off + a + b
                    yield tail + b"y" * max(0, total - len(tail))
                    yield b"x" * (off - 12) + a + b + b"z" * (total - (off - 12) - len(a) - len(b))


def case_sweep(tool):
    # KFF18 (r92): the excerpt never respells a byte by where the window falls.
    spec = importlib.util.spec_from_file_location("tool_under_test_%d" % abs(hash(tool)), tool)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    n = bad = 0
    for raw in sweep_payloads():
        n += 1
        full = mod._escape_text(mod._decode_record(raw))
        cell = mod._one_line_bytes(raw)
        if len(raw) <= 200:
            bad += cell != full
            continue
        head, sep, tail = cell.partition("\u2026")
        bad += not (sep and full.startswith(head) and full.endswith(tail))
    print(f"# KFF18 tool={tool} payloads={n} unfaithful={bad}")
    return n == 29700 and bad == 0


# KFF19 (r93): the reference cut. Written from the WHATWG Encoding Standard's UTF-8 decoder (S356, §8.1.1), not from
# Python's codec: bytes needed and the first continuation's lower/upper boundary per lead byte; every later
# continuation is 0x80..0xBF. A lead outside 0xC2..0xF4 (and every bare continuation) begins no sequence.
def _ref_len(raw, s):
    b = raw[s]
    if b <= 0x7F:
        return 1
    if 0xC2 <= b <= 0xDF:
        need, lo, hi = 1, 0x80, 0xBF
    elif 0xE0 <= b <= 0xEF:
        need, lo, hi = 2, (0xA0 if b == 0xE0 else 0x80), (0x9F if b == 0xED else 0xBF)
    elif 0xF0 <= b <= 0xF4:
        need, lo, hi = 3, (0x90 if b == 0xF0 else 0x80), (0x8F if b == 0xF4 else 0xBF)
    else:
        return None
    for k in range(1, need + 1):
        if s + k >= len(raw) or not lo <= raw[s + k] <= hi:
            return None
        lo, hi = 0x80, 0xBF
    return need + 1


def _ref_straddle(raw, cut):
    """(start, end) of the one well-formed sequence with start < cut < end, or None. A well-formed sequence starts on
    a byte that is never a continuation, so at most one can straddle a cut."""
    for s in range(cut - 1, max(cut - 4, -1), -1):
        n = _ref_len(raw, s)
        if n is not None and s + n > cut:
            return s, s + n
    return None


def ref_cuts(raw, limit=200):
    head = limit // 2
    keep = limit - head - 1
    hs = _ref_straddle(raw, head)
    h = hs[0] if hs else head
    ts = _ref_straddle(raw, len(raw) - keep)
    t = ts[1] if ts else len(raw) - keep
    return h, max(t, h)


EXACT_TOKENS = (
    # well-formed: every Table 3-7 row at its low and high second byte, plus 1-byte ASCII
    b"a", b"\x7f", b"\xc2\x80", b"\xdf\xbf", b"\xe0\xa0\x80", b"\xe0\xbf\xbf", b"\xe1\x80\x80", b"\xec\xbf\xbf",
    b"\xed\x80\x80", b"\xed\x9f\xbf", b"\xee\x80\x80", b"\xef\xbf\xbf", b"\xf0\x90\x80\x80", b"\xf0\xbf\xbf\xbf",
    b"\xf1\x80\x80\x80", b"\xf3\xbf\xbf\xbf", b"\xf4\x80\x80\x80", b"\xf4\x8f\xbf\xbf",
    # ill-formed neighbours: C0/C1 leads, E0 overlong, ED surrogate, F0 overlong, F4 beyond U+10FFFF, F5.., bare
    # continuations, truncated sequences
    b"\xc0\x80", b"\xc1\xbf", b"\xe0\x80\x80", b"\xe0\x9f\xbf", b"\xed\xa0\x80", b"\xed\xbf\xbf",
    b"\xf0\x80\x80\x80", b"\xf0\x8f\xbf\xbf", b"\xf4\x90\x80\x80", b"\xf5\x80\x80\x80", b"\xff", b"\x80", b"\xbf",
    b"\xe2\x82", b"\xf0\x9d\x84",
)
EXACT_LEN = 230
EXACT_N = 14586  # 33 tokens, pairwise, at every offset that puts a cut inside or at the edge of the pair, both cuts


def exact_payloads():
    head, tail = 100, EXACT_LEN - 99
    for cut in (head, tail):
        for a in EXACT_TOKENS:
            for b in EXACT_TOKENS:
                pair = a + b
                for s in range(cut - len(pair), cut + 1):
                    yield b"a" * s + pair + b"a" * (EXACT_LEN - s - len(pair))


def case_exact(tool):
    # KFF19 (r93): the excerpt is exactly the cell the reference cuts give, so a cut that moves too far, not far
    # enough or across bytes that are not one well-formed sequence goes red even when it stays prefix/suffix-faithful.
    spec = importlib.util.spec_from_file_location("tool_exact_%d" % abs(hash(tool)), tool)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    n = bad = 0
    for raw in exact_payloads():
        n += 1
        h, t = ref_cuts(raw)
        want = mod._escape_text(mod._decode_record(raw[:h]) + "\u2026" + mod._decode_record(raw[t:]))
        bad += mod._one_line_bytes(raw) != want
    print(f"# KFF19 tool={tool} payloads={n} inexact={bad}")
    return n == EXACT_N and bad == 0


def case_headill(out, rows):
    # KFF20 (r93): E0 80 80 is ill-formed (Table 3-7; S356 lower boundary 0xA0), so the head cut between the two
    # 0x80 bytes stays: E0 and the first 0x80 keep their escapes, the second 0x80 is elided.
    bs = chr(92)
    return (len(rows) == 1 and "fatal: hil" in rows[0] and rows[0].count(bs + "xe0") == 1
            and rows[0].count(bs + "x80") == 1)


def case_refused(out, rows):
    return len(rows) == 1 and "the receipt writer refused the tree" in rows[0] and "injected" not in out


CASES = (
    ("KFF1", "short", False, case_short),
    ("KFF2", "trace", False, case_trace),
    ("KFF3", "long", False, case_long),
    ("KFF4", "controls", False, case_controls),
    ("KFF5", "empty", False, case_empty),
    ("KFC1", "clean", False, case_clean),
    ("KFC2", "short", True, case_refused),
    ("KFF6", "badbyte", False, case_badbyte),
    ("KFF7", "literal", False, case_literal),
    ("KFF8", "headctl", False, case_headctl),
    ("KFF9", "nelchar", False, case_nelchar),
    ("KFF10", "nelbyte", False, case_nelbyte),
    ("KFF11", "nelcut", False, case_nelcut),
    ("KFF12", "nelchar", False, case_oneline),
    ("KFF13", "decl", False, None),
    ("KFF14", "invcutA", False, case_invcut_a),
    ("KFF15", "invcutB", False, case_invcut_b),
    ("KFF16", "overlong", False, case_overlong),
    ("KFF17", "headcut", False, case_headcut),
    ("KFF18", "sweep", False, None),
    ("KFF19", "exact", False, None),
    ("KFF20", "headill", False, case_headill),
)


def score(kit, tool):
    result = {}
    for cid, mode, refused, check in CASES:
        try:
            if mode == "decl":
                result[cid] = bool(case_source(tool))
                continue
            if mode == "sweep":
                result[cid] = bool(case_sweep(tool))
                continue
            if mode == "exact":
                result[cid] = bool(case_exact(tool))
                continue
            out, rows = run_case(kit, mode, refused)
            result[cid] = bool(check(out, rows))
        except (OSError, subprocess.SubprocessError, KeyError, SyntaxError, ValueError, AttributeError) as exc:
            print(f"# case {cid} fixture error: {type(exc).__name__}: {exc}")
            result[cid] = False
    return result


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tool", required=True, help="tools/souji-record-agreement.py under test")
    ap.add_argument("--before", required=True, help="the r87 tool bytes (do-nothing control)")
    ap.add_argument("--work", required=True, help="empty scratch dir (never under /tmp)")
    ns = ap.parse_args(argv)
    work = os.path.abspath(ns.work)
    if os.path.realpath(work).startswith(("/tmp/", "/var/tmp/", "/dev/shm/")):
        print("R93-FIXTURE-FATAL: --work under /tmp, /var/tmp or /dev/shm", file=sys.stderr)
        return 2
    if os.path.exists(work) and os.listdir(work):
        print(f"R93-FIXTURE-FATAL: --work {work} is not empty", file=sys.stderr)
        return 2
    if not kff13_selfcheck():
        print("R93-FIXTURE-FATAL: the KFF13 ast check does not detect a spaced definition/call or flags a docstring",
              file=sys.stderr)
        return 2
    print("# KFF13 selfcheck spaced=detected docstring=clean")
    os.makedirs(work, exist_ok=True)
    tool, before = os.path.abspath(ns.tool), os.path.abspath(ns.before)
    print(f"# tool path={tool} sha256={sha(tool)}")
    print(f"# before path={before} sha256={sha(before)}")
    print(f"# fixture sha256={sha(os.path.abspath(__file__))}")
    try:
        after_kit = make_kit(os.path.join(work, "after"), tool)
        before_kit = make_kit(os.path.join(work, "before"), before)
    except (FixtureError, OSError, subprocess.SubprocessError) as exc:
        print(f"R93-FIXTURE-FATAL: fixture: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2
    after, old = score(after_kit, tool), score(before_kit, before)
    # Pair checks run on BOTH arms (r90): a pair-bound case's verdict is the case check AND the pair check, so the
    # do-nothing control is scored by the same rule as the tool under test.
    for kit, arm in ((after_kit, after), (before_kit, old)):
        # KFF6/KFF7 injectivity pair: the bad-byte detail and the literal detail must differ on this tool.
        _o6, _r6 = run_case(kit, "badbyte", False)
        _o7, _r7 = run_case(kit, "literal", False)
        _pair_ok = _r6 != _r7 and len(_r6) == 1 and len(_r7) == 1
        arm.update(KFF6=bool(arm["KFF6"] and _pair_ok), KFF7=bool(arm["KFF7"] and _pair_ok))
        # KFF9/KFF10 pair (r90): the character detail and the raw-byte detail must be DIFFERENT cells.
        _o9, _r9 = run_case(kit, "nelchar", False)
        _o10, _r10 = run_case(kit, "nelbyte", False)
        _nel_ok = _r9 != _r10 and len(_r9) == 1 and len(_r10) == 1
        arm.update(KFF9=bool(arm["KFF9"] and _nel_ok), KFF10=bool(arm["KFF10"] and _nel_ok))
        # KFF14/KFF15 pair (r92): payload A (a character) and payload B (a byte) must be DIFFERENT cells.
        _o14, _r14 = run_case(kit, "invcutA", False)
        _o15, _r15 = run_case(kit, "invcutB", False)
        _inv_ok = _r14 != _r15 and len(_r14) == 1 and len(_r15) == 1
        arm.update(KFF14=bool(arm["KFF14"] and _inv_ok), KFF15=bool(arm["KFF15"] and _inv_ok))
    for cid, _mode, _refused, _check in CASES:
        print(f"CASE {cid} tool={'pass' if after[cid] else 'fail'} before={'pass' if old[cid] else 'fail'}")
    a, b = sum(after.values()), sum(old.values())
    print(f"SUMMARY cases={len(CASES)} tool_pass={a} before_pass={b}")
    if a != len(CASES):
        print("R93-FIXTURE-FAIL: the tool under test does not pass every case", file=sys.stderr)
        return 1
    if b >= a:
        print("R93-FIXTURE-FAIL: the do-nothing control passes as many cases (no measured delta)",
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
