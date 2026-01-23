import subprocess
import sys
import os


def run(script_path: str):
    """
    Run a script using the same Python interpreter with PYTHONPATH set.
    """
    env = os.environ.copy()
    env['PYTHONPATH'] = 'src'
    
    cmd = [sys.executable, script_path]
    print(f"\n▶ {' '.join(cmd)}")
    
    result = subprocess.run(
        cmd,
        env=env,
        check=True,
        capture_output=False
    )


if __name__ == "__main__":
    run("scripts/run_ingest.py")
    run("scripts/run_scan.py")
