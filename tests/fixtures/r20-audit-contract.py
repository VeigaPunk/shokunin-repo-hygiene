#!/usr/bin/env python3
"""Independent round-20 oracle for exact auditor write grants and receipts.

Only synthetic specs, transcripts and manifests are created under a fresh
/var/tmp directory. The fixture imports the selected auditor and exercises its
run() API directly; it never invokes a transcript command or writes a target.

With --base-tool, the base auditor must reproduce the preregistered broad
allowances for five unrequested suffixes and named ungranted scratch shapes.
These are baseline failures, not expected final behavior.

Example:
  python3 tests/fixtures/r20-audit-contract.py \\
    --tool tools/souji-seat-audit.py \\
    --base-tool /path/to/baseline/tools/souji-seat-audit.py
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

SCHEMA = "ufo-swarm-wave-v1"
REPORT_DIR = ".ufo/waves/round-20/w2"
DELIVERY_SUFFIXES = (".patch", ".py", ".json", ".tsv", ".txt")
WRITE_SCOPE = ("V-WRITE-SCOPE", "major")
NO_VIOLATIONS: tuple[tuple[str, str], ...] = ()

REQUIRED_CASE_IDS = frozenset({
    "report-own",
    "unrequested-patch", "unrequested-py", "unrequested-json",
    "unrequested-tsv", "unrequested-txt",
    "deliver-exact-patch", "deliver-alternative-py", "deliver-alternative-json",
    "deliver-alternative-tsv", "deliver-alternative-txt",
    "incidental-delivery-mention",
    "deliver-denial-trailing-text", "deliver-example-fenced",
    "cross-seat-stem", "own-only-exact", "own-only-sibling", "traversal",
    "scratch-r20w2-exact", "scratch-foreign-slot", "scratch-no-fallback",
    "scratch-r19w2-literal", "scratch-wave-name-only",
    "scratch-r18-clone-executor", "scratch-r18-clone-reviewer",
    "receipt-exact-digests", "receipt-spec-digest-change",
    "receipt-transcript-digest-change", "receipt-manifest-digest-change",
    "receipt-auditor-digest-change", "drift-auditor", "drift-spec",
    "drift-transcript", "drift-manifest",
    "drift-auditor-after-import",
    "receipt-spec-transcript-alias",
    "scratch-truncated-inside-unparsed",
})
BASE_BROAD_CASE_IDS = frozenset({
    "unrequested-patch", "unrequested-py", "unrequested-json",
    "unrequested-tsv", "unrequested-txt",
    "deliver-alternative-py", "deliver-alternative-json",
    "deliver-alternative-tsv", "deliver-alternative-txt",
    "deliver-denial-trailing-text", "deliver-example-fenced",
})



def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_auditor(path: Path, label: str):
    spec = importlib.util.spec_from_file_location("souji_r20_audit_" + label, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load auditor module: " + str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not callable(getattr(module, "run", None)):
        raise RuntimeError("auditor has no callable run(spec_path, tdir, lane): " + str(path))
    return module


def make_world(root: Path, case_id: str, *, prompt: str = "",
               target: str | None = None, neighbor: bool = False,
               receipt_transcript: bool = False, role: str = "executor",
               wave: str = "souji-r20w2-audit-contract"):
    world = root / case_id
    lane = world / "lane"
    tdir = world / "transcripts"
    lane.mkdir(parents=True)
    tdir.mkdir()

    names = ["Seat"] + (["Neighbor"] if neighbor else [])
    items = [{"name": name, "role": role, "prompt": prompt if name == "Seat" else ""}
             for name in names]
    spec = {
        "schema": SCHEMA,
        "wave": wave,
        "context": "Synthetic oracle fixture; no implicit scratch grant.",
        "reportDir": REPORT_DIR,
        "items": items,
    }
    spec_path = world / "spec.json"
    spec_path.write_bytes((json.dumps(spec, sort_keys=True, separators=(",", ":")) + "\n").encode())
    manifest = tdir / "MANIFEST.sha256"
    manifest.write_bytes(b"synthetic fixture manifest; no target inputs\n")
    transcript_path = tdir / "Seat.txt"
    if receipt_transcript:
        text = "→ read(/var/tmp/souji-r20-synthetic-input) ⇒ ok\n"
    elif target is not None:
        text = "→ write(" + target + ") ⇒ ok\n"
    else:
        text = ""
    transcript_path.write_bytes(text.encode("utf-8"))
    if neighbor:
        (tdir / "Neighbor.txt").write_bytes(b"")
    return {
        "world": world,
        "lane": lane,
        "tdir": tdir,
        "spec_path": spec_path,
        "manifest": manifest,
        "transcript": transcript_path,
        "names": set(names),
    }


def violations(result: dict, seat: str = "Seat") -> tuple[tuple[str, str], ...]:
    rows = result.get("seats", {}).get(seat, {}).get("violations", [])
    return tuple(sorted((row.get("class", ""), row.get("severity", "")) for row in rows))


def build_cases(root: Path):
    cases = []

    def add(case_id: str, target: str, expected=NO_VIOLATIONS, *, prompt: str = "",
            neighbor: bool = False, role: str = "executor",
            wave: str = "souji-r20w2-audit-contract"):
        world = make_world(root, case_id, prompt=prompt, target=target, neighbor=neighbor,
                           role=role, wave=wave)
        cases.append((case_id, world, tuple(expected)))

    # The report is authorized without a sibling-artifact grant.
    def report_for(case_id: str, seat: str = "Seat") -> str:
        lane = root / case_id / "lane"
        return str(lane / REPORT_DIR / (seat + ".md"))

    report = report_for("report-own")
    add("report-own", report)

    for suffix in DELIVERY_SUFFIXES:
        case_id = "unrequested-" + suffix[1:]
        stem = report_for(case_id)[:-3]
        add(case_id, stem + suffix, (WRITE_SCOPE,))

    requested_patch = report_for("deliver-exact-patch")[:-3] + ".patch"
    add("deliver-exact-patch", requested_patch,
        prompt="DELIVER: " + requested_patch + "\n")
    for suffix in (".py", ".json", ".tsv", ".txt"):
        case_id = "deliver-alternative-" + suffix[1:]
        stem = report_for(case_id)[:-3]
        requested = report_for(case_id)[:-3] + ".patch"
        add(case_id, stem + suffix, (WRITE_SCOPE,),
            prompt="DELIVER: " + requested + "\n")

    denied_path = report_for("deliver-denial-trailing-text")[:-3] + ".patch"
    add("deliver-denial-trailing-text", denied_path, (WRITE_SCOPE,),
        prompt="DELIVER: " + denied_path + " is not authorized\n")

    fenced_path = report_for("deliver-example-fenced")[:-3] + ".patch"
    add("deliver-example-fenced", fenced_path, (WRITE_SCOPE,),
        prompt="Example only; not a grant:\n```\nDELIVER: " + fenced_path + "\n```\n")

    incidental = report_for("incidental-delivery-mention")[:-3] + ".patch"
    add("incidental-delivery-mention", incidental, (WRITE_SCOPE,),
        prompt="Possible output path: " + incidental + "; this mention grants nothing.\n")

    neighbor_patch = report_for("cross-seat-stem", "Neighbor")[:-3] + ".patch"
    add("cross-seat-stem", neighbor_patch, (WRITE_SCOPE,), neighbor=True)

    owned = str(root / "own-only-exact" / "lane" / "tests" / "fixtures" / "assigned.py")
    add("own-only-exact", owned, prompt="OWN ONLY " + owned + "\n")
    add("own-only-sibling", owned + ".sibling", (WRITE_SCOPE,),
        prompt="OWN ONLY " + owned + "\n")

    traversal_lane = root / "traversal" / "lane"
    traversal = str(traversal_lane / REPORT_DIR / "Seat.md" /
                    "../../../../../tools/escape.py")
    add("traversal", traversal, (WRITE_SCOPE,))

    scratch_root = "/var/tmp/souji-r20w2-Seat"
    add("scratch-r20w2-exact", scratch_root + "/probe.txt",
        prompt="SCRATCH: " + scratch_root + "\n")
    add("scratch-truncated-inside-unparsed", scratch_root + "/sub/…",
        (("V-WRITE-UNPARSED", "major"),),
        prompt="SCRATCH: " + scratch_root + "\n")
    add("scratch-foreign-slot", "/var/tmp/souji-r20w1-Seat/probe.txt",
        (WRITE_SCOPE,), prompt="SCRATCH: " + scratch_root + "\n")
    add("scratch-no-fallback", scratch_root + "/probe.txt", (WRITE_SCOPE,))
    historical_root = "/var/tmp/souji-r19w2-Seat"
    add("scratch-r19w2-literal", historical_root + "/probe.txt",
        prompt="- Scratch only under /var/tmp/souji-r19w2-<YourName>/;\n")
    add("scratch-wave-name-only", historical_root + "/probe.txt", (WRITE_SCOPE,),
        wave="souji-r19w2")

    clone_prompt = (
        "CLONES: an item that executes lane code works in its own clone: "
        "`git clone --quiet --no-local https://example.invalid/source "
        "/var/tmp/souji-r18w2-Seat/lane`\n")
    add("scratch-r18-clone-executor", "/var/tmp/souji-r18w2-Seat/probe.txt",
        prompt=clone_prompt, role="executor")
    add("scratch-r18-clone-reviewer", "/var/tmp/souji-r18w2-Seat/probe.txt",
        (WRITE_SCOPE,), prompt=clone_prompt, role="reviewer")

    return cases


def record(case_id: str, ok: bool, detail: str, stats: dict, *, primary: bool = True):
    stats["total"] += 1
    if ok:
        stats["passed"] += 1
        status = "PASS"
    else:
        stats["failed"] += 1
        status = "FAIL"
    if primary:
        stats["primary_ids"].append(case_id)
    print("CASE\t%s\t%s\t%s" % (status, case_id, detail))


def run_case(module, case_id: str, world: dict):
    result = module.run(world["spec_path"], world["tdir"], str(world["lane"]))
    names_ok = set(result.get("seats", {})) == world["names"]
    transcripts_ok = not result.get("missing_transcripts")
    return result, names_ok and transcripts_ok


def receipt_world(root: Path):
    world = make_world(root, "receipt-world", receipt_transcript=True)
    return world


def expected_receipt(module_path: Path, world: dict) -> dict[str, str]:
    paths = (module_path, world["spec_path"], world["transcript"], world["manifest"])
    return {str(path.resolve()): digest(path.read_bytes()) for path in paths}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tool", default="tools/souji-seat-audit.py",
                        help="auditor module path (default: installed tools/souji-seat-audit.py)")
    parser.add_argument("--base-tool", help="optional baseline auditor module path")
    args = parser.parse_args(argv)

    fixture_path = Path(__file__).resolve()
    lane_root = fixture_path.parents[2]

    def selected_path(raw: str) -> Path:
        value = Path(raw)
        candidate = value if value.is_absolute() else lane_root / value
        if candidate.is_symlink():
            raise ValueError("auditor path must not be a symlink: " + str(candidate))
        candidate = candidate.resolve()
        if not candidate.is_file():
            raise ValueError("auditor is not a regular file: " + str(candidate))
        return candidate

    try:
        tool_path = selected_path(args.tool)
        auditor = load_auditor(tool_path, "selected")
        base_path = selected_path(args.base_tool) if args.base_tool else None
        base_auditor = load_auditor(base_path, "base") if base_path else None
    except (OSError, RuntimeError, ValueError) as exc:
        print("r20-audit-contract: prerequisite: %s" % exc, file=sys.stderr)
        return 2

    top = Path(tempfile.mkdtemp(prefix="souji-r20-audit-contract.", dir="/var/tmp"))
    stats = {"total": 0, "passed": 0, "failed": 0, "base_discriminating": 0,
             "primary_ids": []}
    worlds = {}
    try:
        cases = build_cases(top)
        for case_id, world, expected in cases:
            worlds[case_id] = world
            try:
                result, complete = run_case(auditor, case_id, world)
                actual = violations(result)
                ok = complete and actual == expected
                detail = "violations=%s expected=%s" % (list(actual), list(expected))
                record(case_id, ok, detail, stats)
            except (OSError, ValueError, KeyError, TypeError) as exc:
                record(case_id, False, "error=%s" % type(exc).__name__, stats)

        baseline_observed = set()
        if base_auditor is not None:
            for case_id in sorted(BASE_BROAD_CASE_IDS):
                world = worlds[case_id]
                try:
                    result, complete = run_case(base_auditor, case_id, world)
                    actual = violations(result)
                    # The named base defects are missing refusals: each
                    # unauthorized write is incorrectly accepted by baseline.
                    ok = complete and actual == NO_VIOLATIONS
                    if ok:
                        baseline_observed.add(case_id)
                        stats["base_discriminating"] += 1
                    record("base-overauth-" + case_id, ok,
                           "baseline_violations=%s expected_baseline=[]" % (list(actual),),
                           stats, primary=False)
                except (OSError, ValueError, KeyError, TypeError) as exc:
                    record("base-overauth-" + case_id, False,
                           "error=%s" % type(exc).__name__, stats, primary=False)
            baseline_inventory_ok = baseline_observed == BASE_BROAD_CASE_IDS
            record("base-broad-authorization-inventory", baseline_inventory_ok,
                   "observed=%s expected=%s" % (sorted(baseline_observed),
                                                  sorted(BASE_BROAD_CASE_IDS)),
                   stats, primary=False)

        rw = receipt_world(top)
        tool_key = str(tool_path.resolve())
        spec_key = str(rw["spec_path"].resolve())
        transcript_key = str(rw["transcript"].resolve())
        manifest_key = str(rw["manifest"].resolve())
        try:
            receipt, complete = run_case(auditor, "receipt-exact-digests", rw)
            expected = expected_receipt(tool_path, rw)
            actual = receipt.get("input_sha256", {})
            receipt_ok = (complete and not receipt.get("missing_transcripts")
                          and receipt.get("inputs_unchanged_during_run") is True
                          and actual == expected
                          and set(actual) == {tool_key, spec_key, transcript_key, manifest_key})
            record("receipt-exact-digests", receipt_ok,
                   "input_keys=%s exact=%s unchanged=%s" %
                   (sorted(actual), actual == expected,
                    receipt.get("inputs_unchanged_during_run")), stats)
            original_receipt = dict(actual)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            record("receipt-exact-digests", False, "error=%s" % type(exc).__name__, stats)
            original_receipt = {}

        try:
            original = rw["spec_path"].read_bytes()
            spec_data = json.loads(original.decode("utf-8"))
            spec_data["synthetic_oracle_revision"] = 2
            rw["spec_path"].write_bytes((json.dumps(spec_data, sort_keys=True,
                                                      separators=(",", ":")) + "\n").encode())
            changed = auditor.run(rw["spec_path"], rw["tdir"], str(rw["lane"]))
            changed_digest = changed.get("input_sha256", {}).get(spec_key)
            record("receipt-spec-digest-change",
                   bool(changed_digest and changed_digest != original_receipt.get(spec_key)),
                   "changed=%s" % (changed_digest != original_receipt.get(spec_key)), stats)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            record("receipt-spec-digest-change", False, "error=%s" % type(exc).__name__, stats)

        try:
            rw["transcript"].write_bytes(rw["transcript"].read_bytes() + b"\n")
            changed = auditor.run(rw["spec_path"], rw["tdir"], str(rw["lane"]))
            changed_digest = changed.get("input_sha256", {}).get(transcript_key)
            record("receipt-transcript-digest-change",
                   bool(changed_digest and changed_digest != original_receipt.get(transcript_key)),
                   "changed=%s" % (changed_digest != original_receipt.get(transcript_key)), stats)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            record("receipt-transcript-digest-change", False,
                   "error=%s" % type(exc).__name__, stats)

        try:
            rw["manifest"].write_bytes(rw["manifest"].read_bytes() + b"synthetic revision 2\n")
            changed = auditor.run(rw["spec_path"], rw["tdir"], str(rw["lane"]))
            changed_digest = changed.get("input_sha256", {}).get(manifest_key)
            record("receipt-manifest-digest-change",
                   bool(changed_digest and changed_digest != original_receipt.get(manifest_key)),
                   "changed=%s" % (changed_digest != original_receipt.get(manifest_key)), stats)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            record("receipt-manifest-digest-change", False,
                   "error=%s" % type(exc).__name__, stats)

        try:
            marker = b"\n# synthetic auditor receipt variant\n"
            variant_path = rw["world"] / "auditor-variant.py"
            variant_bytes = tool_path.read_bytes() + marker
            variant_path.write_bytes(variant_bytes)
            variant_auditor = load_auditor(variant_path, "receipt_variant")
            changed = variant_auditor.run(rw["spec_path"], rw["tdir"], str(rw["lane"]))
            variant_key = str(variant_path.resolve())
            changed_receipt = changed.get("input_sha256", {})
            changed_digest = changed_receipt.get(variant_key)
            expected_keys = (set(original_receipt) - {tool_key}) | {variant_key}
            record("receipt-auditor-digest-change",
                   changed_digest == digest(variant_bytes)
                   and changed_digest != original_receipt.get(tool_key)
                   and set(changed_receipt) == expected_keys,
                   "changed=%s reimported=%s" %
                   (changed_digest != original_receipt.get(tool_key),
                    variant_key in changed_receipt), stats)
        except (OSError, RuntimeError, ValueError, KeyError, TypeError) as exc:
            record("receipt-auditor-digest-change", False,
                   "error=%s" % type(exc).__name__, stats)
        original_read_bytes = Path.read_bytes
        drift_targets = {
            "drift-auditor": tool_path.resolve(),
            "drift-spec": rw["spec_path"].resolve(),
            "drift-transcript": rw["transcript"].resolve(),
            "drift-manifest": rw["manifest"].resolve(),
        }
        for case_id, target_path in drift_targets.items():
            reads = {"count": 0}

            def drift_read(path, selected=target_path, counter=reads):
                data = original_read_bytes(path)
                if path.resolve() == selected:
                    counter["count"] += 1
                    if counter["count"] == 2:
                        return data + b"\n# controlled mid-read drift\n"
                return data

            caught = None
            try:
                with patch.object(Path, "read_bytes", drift_read):
                    auditor.run(rw["spec_path"], rw["tdir"], str(rw["lane"]))
            except ValueError as exc:
                caught = str(exc)
            drift_ok = (reads["count"] == 2 and caught is not None
                        and "audit input changed during read" in caught)
            record(case_id, drift_ok,
                   "reads=%d detected=%s" % (reads["count"], drift_ok), stats)

        try:
            stale_path = rw["world"] / "auditor-stale-copy.py"
            pristine_source = tool_path.read_bytes()
            stale_path.write_bytes(pristine_source)
            stale_auditor = load_auditor(stale_path, "stale_copy")
            stale_path.write_bytes(pristine_source + b"\n# harmless post-import change\n")
            refusal = None
            try:
                stale_auditor.run(rw["spec_path"], rw["tdir"], str(rw["lane"]))
            except ValueError as exc:
                refusal = str(exc)
            stale_refused = refusal == "auditor source changed since module import"
            record("drift-auditor-after-import", stale_refused,
                   "refused=%s" % stale_refused, stats)
        except (OSError, RuntimeError, KeyError, TypeError) as exc:
            record("drift-auditor-after-import", False,
                   "error=%s" % type(exc).__name__, stats)

        try:
            alias_world = make_world(top, "receipt-spec-transcript-alias",
                                     receipt_transcript=True)
            alias_path = alias_world["transcript"].resolve()
            transcript_path = (alias_world["tdir"] / "Seat.txt").resolve()
            spec_json = alias_world["spec_path"].read_bytes()
            transcript_bytes = alias_path.read_bytes()
            alias_reads = {"count": 0}
            original_alias_read = Path.read_bytes

            def alias_read(path):
                if path.resolve() == alias_path:
                    alias_reads["count"] += 1
                    if alias_reads["count"] == 1:
                        return spec_json
                    return transcript_bytes
                return original_alias_read(path)

            alias_refusal = None
            try:
                with patch.object(Path, "read_bytes", alias_read):
                    auditor.run(alias_path, alias_world["tdir"], str(alias_world["lane"]))
            except ValueError as exc:
                alias_refusal = str(exc)
            alias_ok = (alias_path == transcript_path and alias_reads["count"] == 2
                        and alias_refusal is not None
                        and "audit input changed during repeated read" in alias_refusal)
            record("receipt-spec-transcript-alias", alias_ok,
                   "same_path=%s reads=%d refused=%s" %
                   (alias_path == transcript_path, alias_reads["count"], alias_ok), stats)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            record("receipt-spec-transcript-alias", False,
                   "error=%s" % type(exc).__name__, stats)
        observed = stats["primary_ids"]
        try:
            assert (len(observed) == len(set(observed))
                    and set(observed) == REQUIRED_CASE_IDS)
            inventory_ok = True
        except AssertionError:
            inventory_ok = False
        record("oracle-exact-case-inventory", inventory_ok,
               "missing=%s extra=%s" %
               (sorted(REQUIRED_CASE_IDS - set(observed)),
                sorted(set(observed) - REQUIRED_CASE_IDS)), stats, primary=False)
        print("SUMMARY\ttotal=%d\tpass=%d\tfail=%d\tbase_discriminating=%d" %
              (stats["total"], stats["passed"], stats["failed"],
               stats["base_discriminating"]))
        return 0 if stats["failed"] == 0 else 1
    finally:
        shutil.rmtree(top, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
