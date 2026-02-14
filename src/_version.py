import tomllib
from pathlib import Path

_pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"

if _pyproject.is_file():
    VERSION = tomllib.loads(_pyproject.read_text())["project"]["version"]
else:
    VERSION = "dev"
