# cinecli/config.py

from pathlib import Path
import tomllib
import sys

CONFIG_PATH = Path.home() / ".config" / "cinecli" / "config.toml"

EXAMPLE = """
# ~/.config/cinecli/config.toml

[rutracker]
username = "your_username"
password = "your_password"

[settings]
default_action = "magnet"   # "magnet" | "torrent"
default_limit  = 20
"""


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    with open(CONFIG_PATH, "rb") as f:
        return tomllib.load(f)


def require_credentials(config: dict) -> tuple[str, str, str | None]:
    """Extract rutracker credentials from config or abort with a helpful message."""
    rt = config.get("rutracker", {})
    username = rt.get("username", "")
    password = rt.get("password", "")
    cookie   = rt.get("cookie") or None   # опционально

    if not username or not password:
        from rich.console import Console
        Console().print(
            "[bold red]❌ Rutracker credentials not configured.[/bold red]\n"
            f"Create [cyan]{CONFIG_PATH}[/cyan] with:\n"
            f"[dim]{EXAMPLE}[/dim]"
        )
        sys.exit(1)

    return username, password, cookie