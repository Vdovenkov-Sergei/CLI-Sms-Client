"""TOML-based application configuration loader."""

from typing import Any

import toml

from app.exceptions import ConfigError


class Config:
    """Loads and provides access to application configuration from a TOML file.

    Attributes:
        path: Path to the TOML configuration file.
        data: The parsed configuration dictionary.
    """

    def __init__(self, path: str) -> None:
        """Initializes the `Config` instance by loading the specified TOML file."""
        self.path = path
        self.data = self.load()

    def load(self) -> dict[str, Any]:
        """Reads and parses the TOML configuration file.

        Returns:
            A dictionary of configuration key-value pairs.

        Raises:
            ConfigError: If the file does not exist or contains invalid TOML.
        """
        try:
            with open(self.path, "r") as file:
                return toml.load(file)
        except FileNotFoundError:
            raise ConfigError(f"Config file '{self.path}' not found")
        except toml.TomlDecodeError:
            raise ConfigError(f"Error parsing the TOML file '{self.path}'")

    def get(self, key: str) -> Any:
        """Returns the value for the given configuration key.

        Args:
            key: The configuration key to look up.

        Returns:
            The value associated with *key*.

        Raises:
            ConfigError: If *key* is not present in the configuration file.
        """
        if key not in self.data:
            raise ConfigError(f"Missing required config key: '{key}'")
        return self.data[key]
