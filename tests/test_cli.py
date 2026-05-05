import json
import os
import subprocess
import sys
from pathlib import Path


def test_cli_offline_end_to_end(tmp_path: Path):
    output_dir = tmp_path / "demo"
    env = {**os.environ, "PYTHONPATH": str(Path.cwd() / "src")}
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "neurocartographer",
            "Find mouse visual cortex calcium imaging datasets with behavior",
            "--offline",
            "--out",
            str(output_dir),
            "--limit",
            "3",
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        env=env,
    )

    assert completed.returncode == 0, completed.stderr
    assert "DANDI:000728" in completed.stdout
    assert (output_dir / "starter_analysis.ipynb").exists()
    manifest = json.loads((output_dir / "run_manifest.json").read_text())
    assert manifest["artifact_count"] == 5
