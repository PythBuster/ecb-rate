import tomllib
from pathlib import Path


def load_pyproject() -> dict:
    pyproject_path = Path(__file__).resolve().parent.parent / "pyproject.toml"

    with pyproject_path.open("rb") as file:
        return tomllib.load(file)
