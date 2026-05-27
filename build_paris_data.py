"""Run the Paris data builder in scripts/build_paris_data.py."""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).parent / "scripts" / "build_paris_data.py"), run_name="__main__")
