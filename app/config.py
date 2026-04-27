from typing import Any

import toml

from app.exceptions import ConfigError


class Config:
    def __init__(self, config_file: str = "config.toml"):
        self.config_file = config_file
        self.config_data = self.load_config()

    def load_config(self) -> dict[str, Any]:
        try:
            with open(self.config_file, "r") as file:
                return toml.load(file)
        except FileNotFoundError:
            raise ConfigError(f"Config file '{self.config_file}' not found.")
        except toml.TomlDecodeError:
            raise ConfigError(f"Error parsing the TOML file '{self.config_file}'.")

    def get(self, key: str) -> Any:
        if key not in self.config_data:
            raise ConfigError(f"Missing required config key: '{key}'")
        return self.config_data[key]
