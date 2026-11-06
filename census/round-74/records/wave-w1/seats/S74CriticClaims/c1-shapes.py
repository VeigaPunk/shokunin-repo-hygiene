#!/usr/bin/env python3
"""S74CriticClaims C1 shape probe: index-mode/type stat forgeries the frozen 9-row matrix omits,
run against the lane-base gate and the stage-W gate. Read-only wrt the lane; fixtures under scratch."""
import hashlib
import importlib.util
import os
import shutil
import struct
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/souji-shokunin"
S = "/fast/scratch/hyaku/souji-r74/S74CriticClaims"
GC = os.path.join(LANE, "census/round-74/c1-gate-counter.py")
BASE_GATE = os.path.join(S, "gate-base.sh")
CAND_GATE = os.path.join(S, "c1/cand-commit/souji-pre-report-gate.sh")


def load_gc():
    spec = importlib.util.spec_from_file_location("gc", GC)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def forge_mode_stat(gc, repo, rel, force_mode):
    """gc.forge_index_stat, but the entry's mode is forced too (the index stat block's mode field)."""
    st = os.lstat(os.path.join(repo, rel))
    p = os.path.join(repo, ".git", "index")
    data = open(p, "rb").read()
    ver, n = struct.unpack(">II", data[4:12])
    off, out, target, hit = 12, bytearray(data[:12]), rel.encode(), False
    for _ in range(n):
        start = off
        fixed = data[off:off + 62]
        sha, flags = fixed[40:60], fixed[60:62]
        ns = off + 62
        z = data.index(b"\0", ns)
        name = data[ns:z]
        tail_end = z + 1 + ((8 - ((z + 1 - start) % 8)) % 8)
        if name == target:
            hit = True
            fixed = struct.pack(">10I", int(st.st_ctime), st.st_ctime_ns % 1_000_000_000,
                                int(st.st_mtime), st.st_mtime_ns % 1_000_000_000,
                                st.st_dev & 0xFFFFFFFF, st.st_ino & 0xFFFFFFFF, force_mode,
                                st.st_uid, st.st_gid, st.st_size & 0xFFFFFFFF) + sha + flags
            out += fixed + data[ns:tail_end]
        else:
            out += data[start:tail_end]
        off = tail_end
    if not hit:
        raise SystemExit(f"{rel} not in index (v{ver})")
    out += data[off:-20]
    out += hashlib.sha1(bytes(out)).digest()
    with open(p, "wb") as f:
        f.write(bytes(out))
    t = st.st_mtime + 5
    os.utime(p, (t, t))


def main() -> int:
    gc = load_gc()
    work = os.path.join(S, "c1shapes")
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work)
    results = []

    def case(name, prep, expect_status_clean):
        d = os.path.join(work, name)
        clone, report, prereg = gc.build(d, "GH1")
        prep(clone)
        st = gc.git(clone, "status", "--porcelain=v1", "--untracked-files=all").stdout
        st_ok = (st == b"") if expect_status_clean else (st != b"")
        row = [f"SHAPE {name} status_clean={st_ok} status={st!r}"]
        for tag, gate in (("base", BASE_GATE), ("cand", CAND_GATE)):
            rc, clean, text = gc.run_gate(gate, clone, report, prereg)
            det = [l for l in text.splitlines() if l.startswith("detail-clean")]
            row.append(f"{tag}:clean={clean} rc={rc} detail={det[:1]}")
        results.append(" | ".join(row))
        print(results[-1])

    def e1(clone):
        os.chmod(os.path.join(clone, "run.sh"), 0o644)
        forge_mode_stat(gc, clone, "run.sh", 0o100644)

    def e2(clone):
        p = os.path.join(clone, "ln")
        os.unlink(p)
        with open(p, "wb") as f:
            f.write(b"tgt-one")
        forge_mode_stat(gc, clone, "ln", 0o100644)

    def e3(clone):
        gc.git(clone, "config", "core.fileMode", "false")
        os.chmod(os.path.join(clone, "run.sh"), 0o644)

    def e4(clone):
        p = os.path.join(clone, "a.txt")
        keep = os.path.join(work, "a-copy")
        shutil.copyfile(p, keep)
        os.unlink(p)
        os.rename(keep, os.path.join(work, "a-hold"))  # keep the bytes, remove the worktree path
        # forge the index stat from the saved copy's lstat (the worktree path is absent)
        saved = os.path.join(work, "a-hold")
        st = os.lstat(saved)
        pidx = os.path.join(clone, ".git", "index")
        data = open(pidx, "rb").read()
        version, n = struct.unpack(">II", data[4:12])
        off, out, target, hit = 12, bytearray(data[:12]), b"a.txt", False
        for _ in range(n):
            start = off
            fixed = data[off:off + 62]
            sha, flags = fixed[40:60], fixed[60:62]
            ns = off + 62
            z = data.index(b"\0", ns)
            name = data[ns:z]
            tail_end = z + 1 + ((8 - ((z + 1 - start) % 8)) % 8)
            if name == target:
                hit = True
                mode = struct.unpack(">I", fixed[24:28])[0]
                fixed = struct.pack(">10I", int(st.st_ctime), st.st_ctime_ns % 1_000_000_000,
                                    int(st.st_mtime), st.st_mtime_ns % 1_000_000_000,
                                    st.st_dev & 0xFFFFFFFF, st.st_ino & 0xFFFFFFFF, mode,
                                    st.st_uid, st.st_gid, st.st_size & 0xFFFFFFFF) + sha + flags
                out += fixed + data[ns:tail_end]
            else:
                out += data[start:tail_end]
            off = tail_end
        out += data[off:-20]
        out += hashlib.sha1(bytes(out)).digest()
        with open(pidx, "wb") as f:
            f.write(bytes(out))
        os.utime(pidx, (st.st_mtime + 5, st.st_mtime + 5))

    case("E1-exec-bit-flip-index-mode-forged", e1, True)
    case("E2-symlink-to-regular-same-bytes-mode-forged", e2, True)
    case("E3-exec-bit-flip-core.fileMode-false-config", e3, True)
    case("E4-deleted-file-stat-forged", e4, False)
    out = os.path.join(S, "c1shapes.txt")
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(results) + "\n")
    print("WROTE", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
