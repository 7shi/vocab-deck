import os
from dataclasses import dataclass
from pathlib import Path


APP_NAME = "vocab-deck"


@dataclass
class RuntimeConfig:
    data_dir: Path
    settings_path: Path
    memo_db_path: Path


def _default_config_home() -> Path:
    env = os.environ.get("XDG_CONFIG_HOME")
    return Path(env).expanduser() if env else Path.home() / ".config"


def default_config() -> RuntimeConfig:
    config_home = _default_config_home() / APP_NAME
    return RuntimeConfig(
        data_dir=Path.cwd(),
        settings_path=config_home / "settings.toml",
        memo_db_path=config_home / "memo.db",
    )


_runtime_config = default_config()


def get_config() -> RuntimeConfig:
    return _runtime_config


def set_config(
    *,
    data_dir: Path | None = None,
    settings_path: Path | None = None,
    memo_db_path: Path | None = None,
) -> RuntimeConfig:
    global _runtime_config
    current = _runtime_config
    _runtime_config = RuntimeConfig(
        data_dir=(data_dir or current.data_dir).resolve(),
        settings_path=(settings_path or current.settings_path).expanduser().resolve(),
        memo_db_path=(memo_db_path or current.memo_db_path).expanduser().resolve(),
    )
    return _runtime_config
