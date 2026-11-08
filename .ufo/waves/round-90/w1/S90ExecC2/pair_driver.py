"""S90ExecC2 hand-driven check: the K4 FLAGFAIL detail's escape cell for the byte/character pair.

Loads the tool under test from argv[1] and prints the exact cell `_escape_text` produces for:
  - a stderr carrying the RAW BYTE 0x85 (arrives as U+DC85 through surrogateescape)
  - a stderr carrying the CHARACTER U+0085 encoded as UTF-8 (b"\\xc2\\x85")
Plus the public-path cell `_one_line_bytes` for the same two stderrs.
"""
import importlib.util
import sys

path = sys.argv[1]
spec = importlib.util.spec_from_file_location("tool_under_test", path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

RAW_BYTE_0x85 = b"fatal: nel \x85 marker\n"          # invalid UTF-8: lone byte 0x85
CHAR_U0085_UTF8 = b"fatal: nel \xc2\x85 marker\n"    # U+0085 encoded UTF-8


def cell(raw):
    return mod._escape_text(mod._decode_record(raw))


b = cell(RAW_BYTE_0x85)
c = cell(CHAR_U0085_UTF8)
print(f"tool_loaded={path}")
print(f"has_escape_text={hasattr(mod, '_escape_text')} has_decode_record={hasattr(mod, '_decode_record')}")
print(f"raw0x85_cell={b!r}")
print(f"u0085char_cell={c!r}")
print(f"cells_distinct={b != c}")
print(f"raw0x85_cell_bytes={b.encode('ascii', 'backslashreplace')!r}")
print(f"u0085char_cell_bytes={c.encode('ascii', 'backslashreplace')!r}")
print(f"one_line_bytes_raw0x85={mod._one_line_bytes(RAW_BYTE_0x85)!r}")
print(f"one_line_bytes_u0085char={mod._one_line_bytes(CHAR_U0085_UTF8)!r}")
print(f"direct_escape_text_char={mod._escape_text('fatal: nel \u0085 marker')!r}")
print(f"direct_escape_text_surrogate={mod._escape_text('fatal: nel \udc85 marker')!r}")
