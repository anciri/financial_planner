"""Utility functions to load planner configuration from YAML files."""

from pathlib import Path
from typing import Any, Dict

import yaml


def load_yaml(path: Path) -> Dict[str, Any]:
    """Return the parsed YAML file as a dictionary."""
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_config(global_path: Path, productos_path: Path) -> Dict[str, Any]:
    """Load global and product configuration."""
    global_cfg = load_yaml(global_path)
    product_cfg = load_yaml(productos_path)
    return {"global": global_cfg, "productos": product_cfg}
