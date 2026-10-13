"""Re-run all three reproduction scripts in one command."""
import os
import subprocess
import sys

here = os.path.dirname(os.path.abspath(__file__))
scripts = [
    os.path.join(here, "exp1_rdf_oo.py"),
    os.path.join(here, "exp2_scaling.py"),
    os.path.join(here, "exp3_barrier.py"),
]

py = sys.executable  # whatever invoked this
for s in scripts:
    print(f"\n=== running {os.path.basename(s)} ===", flush=True)
    r = subprocess.run([py, s], check=False)
    if r.returncode != 0:
        print(f"FAIL: {s}", file=sys.stderr)
        sys.exit(r.returncode)
print("\nall done.")
