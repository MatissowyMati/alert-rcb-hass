"""Lightweight package bootstrap for API unit tests without Home Assistant."""

import sys
from pathlib import Path
from types import ModuleType

if "custom_components.alert_rcb" not in sys.modules:
    package = ModuleType("custom_components.alert_rcb")
    package.__path__ = [
        str(Path(__file__).parents[1] / "custom_components" / "alert_rcb")
    ]
    sys.modules["custom_components.alert_rcb"] = package
