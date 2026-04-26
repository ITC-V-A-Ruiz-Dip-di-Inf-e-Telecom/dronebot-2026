import logging
import logging.config
import logging.handlers
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # pip install tomli for Python < 3.11


def setup(toml_path: Path | None = None) -> None:
    if toml_path is None:
        toml_path = Path(__file__).parents[2] / "logging.toml"

    with open(toml_path, "rb") as f:
        cfg = tomllib.load(f)

    for handler in cfg.get("handlers", {}).values():
        if "filename" in handler:
            p = Path(handler["filename"])
            if not p.is_absolute():
                p = toml_path.parent / p
            p.parent.mkdir(parents=True, exist_ok=True)
            handler["filename"] = str(p)

    logging.config.dictConfig(cfg)
