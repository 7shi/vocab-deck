import tomllib

from .config import get_config


def load_settings() -> dict:
    settings_path = get_config().settings_path
    if settings_path.exists():
        with open(settings_path, "rb") as f:
            return tomllib.load(f)
    return {}


def save_settings(settings: dict) -> None:
    settings_path = get_config().settings_path
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for section, table in settings.items():
        lines.append(f"[{section}]")
        for k, v in table.items():
            k_q = k.replace("\\", "\\\\").replace('"', '\\"')
            v_q = v.replace("\\", "\\\\").replace('"', '\\"')
            lines.append(f'"{k_q}" = "{v_q}"')
        lines.append("")
    settings_path.write_text("\n".join(lines), encoding="utf-8")
