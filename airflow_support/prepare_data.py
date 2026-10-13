"""Generate the demo dataset once; never overwrite existing input on retries."""
from pathlib import Path
import subprocess
import sys

PROJECT_DIR = Path(__file__).resolve().parents[1]


def prepare_data(project_dir=PROJECT_DIR):
    paths = [project_dir / "data" / f"{name}.csv"
             for name in ("customers", "accounts", "transactions")]
    present = [path.is_file() for path in paths]
    if all(present):
        print("Using existing CSV files; not regenerating input.", flush=True)
        return
    if any(present):
        raise RuntimeError("Incomplete CSV dataset: restore all three input files before retrying.")
    subprocess.run([sys.executable, str(project_dir / "generate_data.py")],
                   cwd=project_dir, check=True)
    if not all(path.is_file() for path in paths):
        raise RuntimeError("Generator did not create all three CSV files.")


if __name__ == "__main__":
    prepare_data()
