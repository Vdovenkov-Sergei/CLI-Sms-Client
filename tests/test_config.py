"""Tests for Config — TOML loading and key access."""

from pathlib import Path
from unittest.mock import patch

import pytest

from app.config import Config
from app.exceptions import ConfigError


class TestConfig:
    """Tests for `Config` class."""

    def test_load_valid_config(self, tmp_path: Path) -> None:
        """Parses a valid TOML file and populates config data correctly."""
        config_content = """
        api_url = "http://localhost/send_sms"
        username = "username"
        password = "password"
        """
        config_file = tmp_path / "config.toml"
        config_file.write_text(config_content)

        config = Config(str(config_file))
        assert config.data == {
            "api_url": "http://localhost/send_sms",
            "username": "username",
            "password": "password",
        }

    def test_missing_config_file(self) -> None:
        """Raises `ConfigError` when the config file does not exist."""
        with pytest.raises(ConfigError, match="Config file 'missing.toml' not found"):
            Config("missing.toml")

    def test_invalid_toml(self, tmp_path: Path) -> None:
        """Raises `ConfigError` when the file contains invalid TOML syntax."""
        config_file = tmp_path / "bad_config.toml"
        config_file.write_text("invalid toml content")

        with pytest.raises(ConfigError, match="Error parsing the TOML file"):
            Config(str(config_file))

    def test_get_existing_key(self, tmp_path: Path) -> None:
        """Returns the correct value for a key that exists in the config."""
        test_config = {"test_key": "test_value"}
        config_file = tmp_path / "test.toml"
        with patch.object(Config, "load", return_value=test_config):
            config = Config(str(config_file))
            assert config.get("test_key") == "test_value"

    def test_get_missing_key(self, tmp_path: Path) -> None:
        """Raises `ConfigError` when the requested key is absent from the config."""
        test_config: dict[str, str] = {}
        config_file = tmp_path / "test.toml"
        with patch.object(Config, "load", return_value=test_config):
            config = Config(str(config_file))
            with pytest.raises(ConfigError, match="Missing required config key: 'missing'"):
                config.get("missing")
