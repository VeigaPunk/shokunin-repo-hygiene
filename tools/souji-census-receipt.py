#!/usr/bin/env python
"""souji-census-receipt.py — capture and verify digest-bound receipts of the
round contract's census run (souji r50).

Why: the round contract requires a sources-census before→after measurement
every round, taken on this host through the r48 adapter
`tools/souji-census-run.sh` (the conf form's raw rc-2 verdict recorded
beside the explicit-lane-directory form's verdict — disclosed, never
masked). Until r50 those census receipts were raw text captures with no
binding: a reader could not check that the bytes in `census/round-<N>/records/`
re-derive the counts the record quotes, nor that the fleet script that
produced them is still the same bytes. This tool upgrades the class: it
captures the adapter run into a receipt whose body is digest-bound, embeds
the adapter's raw output verbatim, and verifies a receipt later by
re-deriving every header value from the embedded raw output and re-hashing
the named scripts.

Receipt grammar (header, then the raw section; the receipt's own digest line
covers every byte strictly above it):
  # souji census receipt v1 - <UTC>
  LANE=<lane>
  FLEET-ROOT=<as given>
  FLEET-SCRIPT-SHA256=<64hex>
  ADAPTER-SHA256=<64hex>
  CONF-RC=<n> DIR-RC=<n> DIR-RESULT=ok|failed DIR-WARN-W04=<n> ADAPTER-EXIT=<n>
  RECEIPT-SHA256=<64hex>
  RAW-SECTION BEGIN
  <the adapter's stdout, verbatim>
  RAW-SECTION END

verify checks (each refusal/mismatch names its class):
  RECEIPT-MALFORMED         a key line missing or ill-shaped; raw section
                            markers missing or duplicated; no provenance
                            line; no CENSUS-RUN final line
  RECEIPT-DIGEST-MISMATCH   the recomputed digest of the bytes above the
                            RECEIPT-SHA256 line differs
  RECEIPT-RC-INCONSISTENT   the embedded CENSUS-RUN line's conf_rc/dir_rc or
                            the adapter exit disagree with the header
  RECEIPT-COUNT-MISMATCH    the W04 line recount over the embedded DIR-FORM
                            section, or the DIR-RESULT ok-line shape,
                            disagrees with the header
  RECEIPT-SCRIPT-DRIFT      --fleet-root given and the fleet script's bytes
                            now hash differently than FLEET-SCRIPT-SHA256
  RECEIPT-ADAPTER-DRIFT     the adapter bytes next to this tool now hash
                            differently than ADAPTER-SHA256 (skipped,
                            reported as adapter=unchecked, when no adapter
                            file is found beside this tool)

Usage:
  python -B tools/souji-census-receipt.py capture --fleet-root DIR
          [--lane souji] --out PATH [--adapter PATH] [--timeout N]
  python -B tools/souji-census-receipt.py verify --receipt PATH [--fleet-root DIR]
  python -B tools/souji-census-receipt.py --selftest
Exit: capture 0 when the receipt was written and the census dir form exited 0;
otherwise the census's exit code (or 2 on environment failure). verify 0 ok;
1 a named mismatch; 2 could-not-evaluate (unreadable receipt). Selftest 0
pass / 1 fail; it writes only under the caller's TMPDIR (refused when unset,
empty, or at/inside the lane root — Q66). Stdlib only; read-only over the
fleet root and the adapter; the only write is the caller-named --out.
"""
import argparse
import datetime
import hashlib
import os
import re
import subprocess
import sys

HEX64 = re.compile(r"^[0-9a-f]{64}$")
RC = re.compile(r"^\d+$")
PROVENANCE = re.compile(r"^# fleet-script sha256=([0-9a-f]{64}) path=(.+)$", re.M)
CENSUS_RUN = re.compile(r"^CENSUS-RUN lane=(\S+) conf_rc=(\d+) dir_rc=(\d+)\s*$", re.M)
KEY_LINE = re.compile(r"^([A-Z][A-Z0-9-]*)=(.*)$")
REQUIRED_KEYS = ("LANE", "FLEET-ROOT", "FLEET-SCRIPT-SHA256", "ADAPTER-SHA256",
                 "CONF-RC", "DIR-RC", "DIR-RESULT", "DIR-WARN-W04", "ADAPTER-EXIT",
                 "RECEIPT-SHA256")
DIGEST_KEYS = ("FLEET-SCRIPT-SHA256", "ADAPTER-SHA256", "RECEIPT-SHA256")
RC_KEYS = ("CONF-RC", "DIR-RC", "ADAPTER-EXIT")


def utcnow():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path):
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def adapter_default():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "souji-census-run.sh")


def parse_adapter_output(text):
    """Parse the adapter's section output; returns dict or None."""
    prov = PROVENANCE.findall(text)
    if len(prov) != 1:
        return None
    runs = CENSUS_RUN.findall(text)
    if len(runs) != 1:
        return None
    for marker in ("CONF-FORM BEGIN", "CONF-FORM END", "DIR-FORM BEGIN", "DIR-FORM END"):
        if text.count(marker + "\n") != 1:
            return None
    dir_block = text.split("DIR-FORM BEGIN\n", 1)[1].split("DIR-FORM END\n", 1)[0]
    w04 = sum(1 for line in dir_block.splitlines() if "\tW04\t" in line)
    ok_lines = [line for line in dir_block.splitlines() if "\tok\t" in line]
    result = "ok" if ok_lines else "failed"
    return {"fleet_script_sha": prov[0][0], "fleet_script_path": prov[0][1],
            "lane": runs[0][0], "conf_rc": runs[0][1], "dir_rc": runs[0][2],
            "w04": str(w04), "result": result}


def capture(args):
    adapter = args.adapter or adapter_default()
    if not os.path.isfile(adapter):
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: adapter missing: %s\n" % adapter)
        return 2
    if not args.out:
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: --out is required\n")
        return 2
    resolved_out = os.path.realpath(args.out)
    root = os.path.realpath(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if resolved_out == root or resolved_out.startswith(root + os.sep) or root.startswith(resolved_out + os.sep):
        sys.stderr.write("ERROR: --out resolves inside the lane root; receipts are staged "
                         "outside the repo (r48 receipt-staging discipline) and copied in "
                         "by the caller before a commit\n")
        return 2
    try:
        run = subprocess.run(["bash", adapter, "--fleet-root", args.fleet_root,
                              "--lane", args.lane], stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, timeout=args.timeout, check=False)
    except subprocess.TimeoutExpired:
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: adapter run exceeded %ds\n" % args.timeout)
        return 2
    output = run.stdout.decode("utf-8", "replace")
    parsed = parse_adapter_output(output)
    if parsed is None:
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: adapter output did not match the "
                         "r48 adapter grammar\n")
        return 2
    fleet_sha = parsed["fleet_script_sha"]
    local_fleet = os.path.join(args.fleet_root, "scripts", "sources-census.sh")
    if os.path.isfile(local_fleet):
        try:
            fleet_sha = sha256_file(local_fleet)
        except OSError:
            pass
    adapter_sha = sha256_file(adapter)
    header = [
        "# souji census receipt v1 - %s" % utcnow(),
        "LANE=%s" % parsed["lane"],
        "FLEET-ROOT=%s" % args.fleet_root,
        "FLEET-SCRIPT-SHA256=%s" % fleet_sha,
        "ADAPTER-SHA256=%s" % adapter_sha,
        "CONF-RC=%s" % parsed["conf_rc"],
        "DIR-RC=%s" % parsed["dir_rc"],
        "DIR-RESULT=%s" % parsed["result"],
        "DIR-WARN-W04=%s" % parsed["w04"],
        "ADAPTER-EXIT=%d" % run.returncode,
    ]
    body = "\n".join(header) + "\n"
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
    text = body + "RECEIPT-SHA256=%s\nRAW-SECTION BEGIN\n%sRAW-SECTION END\n" % (digest, output)
    with open(args.out, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)
    sys.stdout.write("RECEIPT-WRITTEN path=%s lane=%s conf_rc=%s dir_rc=%s w04=%s result=%s\n"
                     % (args.out, parsed["lane"], parsed["conf_rc"], parsed["dir_rc"],
                        parsed["w04"], parsed["result"]))
    try:
        dir_rc = int(parsed["dir_rc"])
    except ValueError:
        return 2
    return 0 if run.returncode == 0 and dir_rc == 0 else (run.returncode or 1)


def verify(args, adapter_override=None):
    path = args.receipt
    adapter = adapter_override or adapter_default()
    if not os.path.isfile(path):
        sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: receipt missing: %s\n" % path)
        return 2
    with open(path, "rb") as handle:
        raw = handle.read()
    marker = raw.find(b"RECEIPT-SHA256=")
    if marker < 0:
        print("VERIFY refused receipt=%s class=RECEIPT-MALFORMED detail=no-digest-line" % path)
        return 1
    line_end = raw.find(b"\n", marker)
    if line_end < 0:
        print("VERIFY refused receipt=%s class=RECEIPT-MALFORMED detail=digest-line-unterminated" % path)
        return 1
    digest_value = raw[marker + len(b"RECEIPT-SHA256="):line_end].decode("utf-8", "replace").strip()
    body = raw[:marker]
    header = body.decode("utf-8", "replace")
    keys = {}
    bad_shape = False
    for line in header.splitlines():
        match = KEY_LINE.match(line)
        if not match:
            continue
        keys[match.group(1)] = match.group(2)
    keys["RECEIPT-SHA256"] = digest_value
    for key in REQUIRED_KEYS:
        if key not in keys:
            print("VERIFY refused receipt=%s class=RECEIPT-MALFORMED detail=missing-key-%s"
                  % (path, key))
            return 1
    for key in DIGEST_KEYS:
        if not HEX64.match(keys[key]):
            bad_shape = True
    for key in RC_KEYS:
        if not RC.match(keys[key]):
            bad_shape = True
    if keys["DIR-RESULT"] not in ("ok", "failed"):
        bad_shape = True
    if bad_shape:
        print("VERIFY refused receipt=%s class=RECEIPT-MALFORMED detail=key-shape" % path)
        return 1
    if hashlib.sha256(body).hexdigest() != keys["RECEIPT-SHA256"]:
        print("VERIFY refused receipt=%s class=RECEIPT-DIGEST-MISMATCH" % path)
        return 1
    raw_text = raw.decode("utf-8", "replace")
    if raw_text.count("RAW-SECTION BEGIN\n") != 1 or raw_text.count("RAW-SECTION END\n") != 1:
        print("VERIFY refused receipt=%s class=RECEIPT-MALFORMED detail=raw-section" % path)
        return 1
    raw_section = raw_text.split("RAW-SECTION BEGIN\n", 1)[1].split("RAW-SECTION END\n", 1)[0]
    parsed = parse_adapter_output(raw_section)
    if parsed is None:
        print("VERIFY refused receipt=%s class=RECEIPT-MALFORMED detail=adapter-output" % path)
        return 1
    if (parsed["conf_rc"] != keys["CONF-RC"] or parsed["dir_rc"] != keys["DIR-RC"]
            or parsed["dir_rc"] != keys["ADAPTER-EXIT"]):
        print("VERIFY refused receipt=%s class=RECEIPT-RC-INCONSISTENT" % path)
        return 1
    if parsed["w04"] != keys["DIR-WARN-W04"] or parsed["result"] != keys["DIR-RESULT"]:
        print("VERIFY refused receipt=%s class=RECEIPT-COUNT-MISMATCH" % path)
        return 1
    checks = "grammar,digest,raw-section,rc,w04,result"
    adapter_state = "unchecked"
    if os.path.isfile(adapter):
        adapter_state = "ok" if sha256_file(adapter) == keys["ADAPTER-SHA256"] else "drift"
        checks += ",adapter-sha"
        if adapter_state == "drift":
            print("VERIFY refused receipt=%s class=RECEIPT-ADAPTER-DRIFT" % path)
            return 1
    if args.fleet_root:
        fleet = os.path.join(args.fleet_root, "scripts", "sources-census.sh")
        if not os.path.isfile(fleet):
            sys.stderr.write("REFUSAL COULD-NOT-EVALUATE: fleet script missing: %s\n" % fleet)
            return 2
        checks += ",fleet-script-sha"
        if sha256_file(fleet) != keys["FLEET-SCRIPT-SHA256"]:
            print("VERIFY refused receipt=%s class=RECEIPT-SCRIPT-DRIFT" % path)
            return 1
    print("VERIFY ok receipt=%s lane=%s conf_rc=%s dir_rc=%s w04=%s result=%s checks=%s adapter=%s"
          % (path, keys["LANE"], keys["CONF-RC"], keys["DIR-RC"], keys["DIR-WARN-W04"],
             keys["DIR-RESULT"], checks, adapter_state))
    return 0


def repo_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def tmpdir_refusal():
    value = os.environ.get("TMPDIR", "")
    if not value.strip():
        return "TMPDIR is unset or empty; refusing to run (Q66 scratch discipline)"
    resolved = os.path.realpath(value)
    root = os.path.realpath(repo_root())
    if resolved == root or resolved.startswith(root + os.sep) or root.startswith(resolved + os.sep):
        return "TMPDIR resolves at or inside the lane root; refusing to run"
    return ""


def selftest():
    refusal = tmpdir_refusal()
    if refusal:
        sys.stderr.write("ERROR: %s\n" % refusal)
        return 2
    import tempfile
    import shutil

    fake_adapter = r"""#!/usr/bin/env bash
printf '%s\n' "# fleet-script sha256=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa path=/fixture/fleet/scripts/sources-census.sh"
printf 'CONF-FORM BEGIN\n'
printf 'souji missing /fixture/fleet/souji-shokunin/corpus/SOURCES.md\n'
printf 'CONF-FORM END\n'
printf 'DIR-FORM BEGIN\n'
printf 'fixture-lane\tW04\tS001 duplicate url example.org/a across scopes\n'
printf 'fixture-lane\tW04\tS002 duplicate url example.org/b across scopes\n'
printf 'fixture-lane\tok\t/fixture/fixture-lane/corpus/SOURCES.md\n'
printf 'DIR-FORM END\n'
printf 'CENSUS-RUN lane=souji conf_rc=2 dir_rc=0\n'
"""
    scratch = tempfile.mkdtemp(prefix="souji-census-receipt-selftest.")
    passed = failed = 0

    def run_self(argv):
        run = subprocess.run([sys.executable, "-B", os.path.abspath(__file__)] + argv,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                             timeout=300, check=False,
                             env=dict(os.environ, TMPDIR=scratch))
        return run.returncode, run.stdout + run.stderr

    try:
        tools_dir = os.path.join(scratch, "tools")
        os.makedirs(tools_dir)
        fixture_adapter = os.path.join(tools_dir, "fixture-adapter.sh")
        with open(fixture_adapter, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(fake_adapter)
        receipt_path = os.path.join(scratch, "receipt.txt")

        # A1: capture over the fixture adapter verifies clean
        rc, out = run_self(["capture", "--fleet-root", "/fixture/fleet", "--lane", "souji",
                            "--out", receipt_path, "--adapter", fixture_adapter])
        ok = rc == 0 and "RECEIPT-WRITTEN" in out and os.path.isfile(receipt_path)
        rc2, out2 = run_self(["verify", "--receipt", receipt_path,
                              "--tools-adapter", fixture_adapter])
        ok = ok and rc2 == 0 and "VERIFY ok" in out2
        passed += 1 if ok else 0
        failed += 0 if ok else 1
        print("SELFTEST-CASE %s capture-verify %s" % ("pass" if ok else "fail", out2.strip()[:120]))

        def read_receipt():
            with open(receipt_path, "r", encoding="utf-8", newline="") as handle:
                return handle.read()

        clean_receipt = read_receipt()

        def write_receipt(text):
            with open(receipt_path, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(text)

        def restore():
            write_receipt(clean_receipt)

        def reseat_digest(text):
            """Recompute RECEIPT-SHA256 after a deliberate header edit (so the
            digest leg passes and the intended class fires)."""
            idx = text.find("RECEIPT-SHA256=")
            digest = hashlib.sha256(text[:idx].encode("utf-8")).hexdigest()
            return text[:idx] + "RECEIPT-SHA256=%s\n" % digest + text[idx:].split("\n", 1)[1]

        # A2: header byte flipped without reseating the digest -> DIGEST-MISMATCH
        restore()
        tampered = clean_receipt.replace("CONF-RC=2", "CONF-RC=0", 1)
        write_receipt(tampered)
        rc, out = run_self(["verify", "--receipt", receipt_path, "--tools-adapter", fixture_adapter])
        ok = rc == 1 and "RECEIPT-DIGEST-MISMATCH" in out
        passed += 1 if ok else 0
        failed += 0 if ok else 1
        print("SELFTEST-CASE %s digest-mismatch" % ("pass" if ok else "fail"))

        # A3: W04 line dropped from the raw section, digest reseated -> COUNT-MISMATCH
        restore()
        tampered = clean_receipt.replace(
            "fixture-lane\tW04\tS002 duplicate url example.org/b across scopes\n", "", 1)
        tampered = reseat_digest(tampered)
        write_receipt(tampered)
        rc, out = run_self(["verify", "--receipt", receipt_path, "--tools-adapter", fixture_adapter])
        ok = rc == 1 and "RECEIPT-COUNT-MISMATCH" in out
        passed += 1 if ok else 0
        failed += 0 if ok else 1
        print("SELFTEST-CASE %s count-mismatch" % ("pass" if ok else "fail"))

        # A4: CENSUS-RUN dir_rc flipped with digest reseated -> RC-INCONSISTENT
        restore()
        tampered = reseat_digest(clean_receipt.replace(
            "CENSUS-RUN lane=souji conf_rc=2 dir_rc=0",
            "CENSUS-RUN lane=souji conf_rc=2 dir_rc=3", 1))
        write_receipt(tampered)
        rc, out = run_self(["verify", "--receipt", receipt_path, "--tools-adapter", fixture_adapter])
        ok = rc == 1 and "RECEIPT-RC-INCONSISTENT" in out
        passed += 1 if ok else 0
        failed += 0 if ok else 1
        print("SELFTEST-CASE %s rc-inconsistent" % ("pass" if ok else "fail"))

        # A5: adapter bytes drift -> ADAPTER-DRIFT (verify against a changed copy)
        drifted_tools = os.path.join(scratch, "drift-tools")
        os.makedirs(drifted_tools)
        drifted_adapter = os.path.join(drifted_tools, "drifted-adapter.sh")
        with open(drifted_adapter, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(fake_adapter + "# drifted\n")
        restore()
        ok = False
        rc, out = run_self(["verify", "--receipt", receipt_path,
                            "--tools-adapter", drifted_adapter])
        ok = rc == 1 and "RECEIPT-ADAPTER-DRIFT" in out
        passed += 1 if ok else 0
        failed += 0 if ok else 1
        print("SELFTEST-CASE %s adapter-drift" % ("pass" if ok else "fail"))

        # A6: raw section damaged (DIR-FORM END removed) -> MALFORMED
        restore()
        tampered = clean_receipt.replace("DIR-FORM END\n", "", 1)
        write_receipt(tampered)
        rc, out = run_self(["verify", "--receipt", receipt_path, "--tools-adapter", fixture_adapter])
        ok = rc == 1 and "RECEIPT-MALFORMED" in out
        passed += 1 if ok else 0
        failed += 0 if ok else 1
        print("SELFTEST-CASE %s malformed-raw-section" % ("pass" if ok else "fail"))
    finally:
        shutil.rmtree(scratch, ignore_errors=True)

    total = passed + failed
    if failed == 0:
        print("SELFTEST cases=%d pass=%d fail=0" % (total, passed))
        return 0
    print("SELFTEST cases=%d pass=%d fail=%d" % (total, passed, failed))
    return 1


def main(argv):
    parser = argparse.ArgumentParser(add_help=True)
    sub = parser.add_subparsers(dest="mode")
    cap = sub.add_parser("capture")
    cap.add_argument("--fleet-root", required=True)
    cap.add_argument("--lane", default="souji")
    cap.add_argument("--out", required=True)
    cap.add_argument("--adapter")
    cap.add_argument("--timeout", type=int, default=900)
    ver = sub.add_parser("verify")
    ver.add_argument("--receipt", required=True)
    ver.add_argument("--fleet-root")
    ver.add_argument("--tools-adapter")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)

    if args.selftest:
        return selftest()
    if args.mode == "capture":
        return capture(args)
    if args.mode == "verify":
        return verify(args, adapter_override=getattr(args, "tools_adapter", None))
    parser.print_usage(sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
