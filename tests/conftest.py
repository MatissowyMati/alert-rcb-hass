"""Lightweight package bootstrap for API unit tests without Home Assistant."""

import sys
from pathlib import Path
from types import ModuleType

if "custom_components.rso" not in sys.modules:
    package = ModuleType("custom_components.rso")
    package.__path__ = [str(Path(__file__).parents[1] / "custom_components" / "rso")]
    sys.modules["custom_components.rso"] = package
