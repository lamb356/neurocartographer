import json
from pathlib import Path

from neurocartographer.execution import execute_notebook


def _notebook(cells):
    return {"cells": cells, "metadata": {}, "nbformat": 4, "nbformat_minor": 5}


def _code(source):
    return {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": source}


def test_execute_notebook_runs_safe_generated_code_cells(tmp_path: Path):
    path = tmp_path / "safe.ipynb"
    path.write_text(json.dumps(_notebook([_code("print('hello neuro')")])) , encoding="utf-8")

    report = execute_notebook(path, tmp_path / "execution_report.json")

    assert report.status == "passed"
    assert report.executed_cell_count == 1
    assert "hello neuro" in report.stdout


def test_execute_notebook_blocks_unsafe_imports(tmp_path: Path):
    path = tmp_path / "unsafe.ipynb"
    path.write_text(json.dumps(_notebook([_code("import subprocess")])) , encoding="utf-8")

    report = execute_notebook(path, tmp_path / "execution_report.json")

    assert report.status == "blocked"
    assert "subprocess" in report.reason
