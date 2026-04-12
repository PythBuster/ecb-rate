from pathlib import Path

import pytest

import ecb_rate.utils as utils_module


def test_load_pyproject_returns_parsed_toml(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    project_root = tmp_path
    package_dir = project_root / "ecb_rate"
    package_dir.mkdir()

    pyproject_path = project_root / "pyproject.toml"
    pyproject_path.write_text(
        '[project]\n'
        'name = "ecb-rate"\n'
        'version = "0.4.1"\n'
        'description = "CLI for ECB JSON exchange rates"\n',
        encoding="utf-8",
    )

    fake_module_file = package_dir / "utils.py"
    monkeypatch.setattr(utils_module, "__file__", str(fake_module_file))

    result = utils_module.load_pyproject()

    assert result["project"]["name"] == "ecb-rate"
    assert result["project"]["version"] == "0.4.1"
    assert result["project"]["description"] == "CLI for ECB JSON exchange rates"


def test_load_pyproject_opens_pyproject_from_project_root(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    project_root = tmp_path
    package_dir = project_root / "ecb_rate"
    package_dir.mkdir()

    pyproject_path = project_root / "pyproject.toml"
    pyproject_path.write_text('[project]\nname = "ecb-rate"\n', encoding="utf-8")

    fake_module_file = package_dir / "utils.py"
    monkeypatch.setattr(utils_module, "__file__", str(fake_module_file))

    opened: dict[str, object] = {}
    original_open = Path.open

    def wrapped_open(self: Path, *args, **kwargs):
        opened["path"] = self
        opened["mode"] = args[0] if args else kwargs.get("mode")
        return original_open(self, *args, **kwargs)

    monkeypatch.setattr(Path, "open", wrapped_open)
    monkeypatch.setattr(utils_module.tomllib, "load", lambda _file: {"project": {}})

    result = utils_module.load_pyproject()

    assert result == {"project": {}}
    assert opened["path"] == pyproject_path
    assert opened["mode"] == "rb"