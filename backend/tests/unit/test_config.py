"""
CASML — Configuration Loading Tests
"""

from __future__ import annotations

import os
from pathlib import Path

import yaml
import pytest


CONFIGS_DIR = Path(__file__).parent.parent.parent.parent / "configs"


class TestConfigurationLoading:
    """Test that all YAML configuration files load correctly."""

    @pytest.mark.parametrize(
        "config_file",
        ["risk.yaml", "policies.yaml", "tools.yaml", "models.yaml", "experiments.yaml", "attacks.yaml"],
    )
    def test_config_file_loads(self, config_file: str) -> None:
        """Each YAML config file should parse without errors."""
        path = CONFIGS_DIR / config_file
        if not path.exists():
            pytest.skip(f"Config file not found: {path}")

        with open(path) as f:
            data = yaml.safe_load(f)

        assert data is not None
        assert isinstance(data, dict)

    def test_risk_config_has_weights(self) -> None:
        """Risk config should define component weights."""
        path = CONFIGS_DIR / "risk.yaml"
        if not path.exists():
            pytest.skip("risk.yaml not found")

        with open(path) as f:
            data = yaml.safe_load(f)

        assert "component_weights" in data
        weights = data["component_weights"]
        assert "provenance" in weights
        assert "injection" in weights
        assert "alignment" in weights

    def test_policies_config_has_default_action(self) -> None:
        """Policies config should define a default action."""
        path = CONFIGS_DIR / "policies.yaml"
        if not path.exists():
            pytest.skip("policies.yaml not found")

        with open(path) as f:
            data = yaml.safe_load(f)

        assert "default_action" in data

    def test_tools_config_has_tools(self) -> None:
        """Tools config should define at least one tool."""
        path = CONFIGS_DIR / "tools.yaml"
        if not path.exists():
            pytest.skip("tools.yaml not found")

        with open(path) as f:
            data = yaml.safe_load(f)

        assert "tools" in data
        assert len(data["tools"]) >= 1
