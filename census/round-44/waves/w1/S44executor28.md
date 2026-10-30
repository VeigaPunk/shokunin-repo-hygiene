# S44executor28 report

Detailed findings: `.ufo/waves/round-44/w1/S44executor28/report.md`.

C2 frozen counter at `d314fd6e85d62565344fa6c4b102f52f62297884` exited 0 with `SUMMARY tool=present population=ok retention=ok hidden_v2=10/10 clean_stub=REJECTED findings_stub=REJECTED controls_ran=ok selftest=ok tmpdir=ok`; stderr empty. Complete captured stdout/stderr/rc are in the seat output directory. Current v2 negative controls require parseable audit summaries and failures; crashes are not classified as rejection. Caveat: retained r43 hidden memorizer path treats nonzero as rejection without requiring a summary, so its historical control alone could mistake a crash for rejection. No source changes/tool installs; scratch removed.
