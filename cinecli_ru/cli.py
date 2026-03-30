# cinecli/cli.py

import typer
from rich.prompt import Prompt
from rich.console import Console

from cinecli_ru.config import load_config, require_credentials
from cinecli_ru.api import search_torrents, get_torrent
from cinecli_ru.ui import show_torrents, show_torrent_details
from cinecli_ru.magnets import get_magnet, stream, open_magnet, open_torrent_page, select_best_torrent

# ─────────────────────────────────────────────────────────────────────────────
app = typer.Typer(
    help="🎬 CineCLI — Ищи фильмы и смотри прямо в терминале",
)
console = Console()

# ─────────────────────────────────────────────────────────────────────────────
# search
# ─────────────────────────────────────────────────────────────────────────────

@app.command()
def search(
    query: list[str] = typer.Argument(..., help="Поисковый запрос"),
    limit: int = typer.Option(20, "--limit", "-n", help="Макс. результатов"),
):
    """Найти торренты на Rutracker."""
    config = load_config()
    username, password, cookie = require_credentials(config)
    limit = limit or config.get("settings", {}).get("default_limit", 20)

    search_query = " ".join(query)
    console.print(f"[dim]Ищу:[/dim] [bold]{search_query}[/bold] …")

    try:
        torrents = search_torrents(search_query, username, password, limit, cookie)
    except RuntimeError as e:
        console.print(f"[red]❌ {e}[/red]")
        raise typer.Exit(code=1)

    if not torrents:
        console.print("[red]❌ Ничего не найдено.[/red]")
        raise typer.Exit(code=1)

    show_torrents(torrents)
    console.print(
        "\n[dim]Используй [bold]cinecli watch <topic_id>[/bold] "
        "чтобы сразу стримить, или [bold]cinecli get <topic_id>[/bold] "
        "для других опций.[/dim]"
    )


# ─────────────────────────────────────────────────────────────────────────────
# watch  — главная команда: найти → стримить в mpv
# ─────────────────────────────────────────────────────────────────────────────

@app.command()
def watch(
    query: list[str] = typer.Argument(..., help="Название фильма"),
    limit: int = typer.Option(20, "--limit", "-n", help="Макс. результатов"),
):
    """
    Найти фильм и сразу запустить в mpv через webtorrent.

    Пример: cinecli watch матрица
    """
    config = load_config()
    username, password, cookie = require_credentials(config)
    limit = config.get("settings", {}).get("default_limit", limit)

    search_query = " ".join(query)
    console.print(f"[dim]Ищу:[/dim] [bold]{search_query}[/bold] …")

    try:
        torrents = search_torrents(search_query, username, password, limit, cookie)
    except RuntimeError as e:
        console.print(f"[red]❌ {e}[/red]")
        raise typer.Exit(code=1)

    if not torrents:
        console.print("[red]❌ Ничего не найдено.[/red]")
        raise typer.Exit(code=1)

    show_torrents(torrents)

    # ── выбор торрента ────────────────────────────────────────────────────────
    auto = typer.confirm("\n🎯 Авто-выбор (больше всего сидов)?", default=True)

    if auto:
        torrent = select_best_torrent(torrents)
        console.print(
            f"[bold]Выбрано:[/bold] {torrent.title} "
            f"([green]{torrent.seeds or 0} seeds[/green], {torrent.formatted_size() if torrent.size else '?'})"
        )
    else:
        idx = Prompt.ask(
            "Выбери номер",
            choices=[str(i) for i in range(len(torrents))],
        )
        torrent = torrents[int(idx)]
        show_torrent_details(torrent)

    # ── стриминг ─────────────────────────────────────────────────────────────
    try:
        stream(torrent, username, password, cookie)
    except RuntimeError as e:
        console.print(f"[red]{e}[/red]")
        raise typer.Exit(code=1)


# ─────────────────────────────────────────────────────────────────────────────
# get  — детали + выбор действия
# ─────────────────────────────────────────────────────────────────────────────

@app.command()
def get(topic_id: int = typer.Argument(..., help="Rutracker topic ID")):
    """Показать детали торрента и выбрать действие (стрим / магнет / страница)."""
    config = load_config()
    username, password, cookie = require_credentials(config)

    console.print(f"[dim]Загружаю топик {topic_id} …[/dim]")
    try:
        torrent = get_torrent(topic_id, username, password, cookie)
    except RuntimeError as e:
        console.print(f"[red]❌ {e}[/red]")
        raise typer.Exit(code=1)

    show_torrent_details(torrent)

    action = Prompt.ask(
        "Действие",
        choices=["stream", "magnet", "page", "skip"],
        default="stream",
    )

    if action == "stream":
        try:
            stream(torrent, username, password, cookie)
        except RuntimeError as e:
            console.print(f"[red]{e}[/red]")
    elif action == "magnet":
        magnet = get_magnet(torrent, username, password, cookie)
        open_magnet(magnet)
        console.print("[green]🧲 Магнет открыт в торрент-клиенте![/green]")
    elif action == "page":
        open_torrent_page(torrent)
        console.print(f"[green]🌐 Открыто:[/green] {torrent.url}")
    else:
        console.print("[dim]Пропущено.[/dim]")


# ─────────────────────────────────────────────────────────────────────────────
# interactive
# ─────────────────────────────────────────────────────────────────────────────

@app.command()
def interactive():
    """Интерактивный режим: поиск → выбор → стрим."""
    config = load_config()
    username, password, cookie = require_credentials(config)
    limit = config.get("settings", {}).get("default_limit", 20)

    query = Prompt.ask("🔍 Что смотрим?")
    console.print("[dim]Ищу …[/dim]")

    try:
        torrents = search_torrents(query, username, password, limit, cookie)
    except RuntimeError as e:
        console.print(f"[red]❌ {e}[/red]")
        raise typer.Exit(code=1)

    if not torrents:
        console.print("[red]❌ Ничего не найдено.[/red]")
        raise typer.Exit()

    show_torrents(torrents)

    auto = typer.confirm("\n🎯 Авто-выбор (больше всего сидов)?", default=True)

    if auto:
        torrent = select_best_torrent(torrents)
        console.print(
            f"[bold]Выбрано:[/bold] {torrent.title} "
            f"([green]{torrent.seeds or 0} seeds[/green], {torrent.formatted_size() if torrent.size else '?'})"
        )
    else:
        idx = Prompt.ask(
            "Выбери номер",
            choices=[str(i) for i in range(len(torrents))],
        )
        torrent = torrents[int(idx)]

    show_torrent_details(torrent)

    action = Prompt.ask(
        "Действие",
        choices=["stream", "magnet", "page", "skip"],
        default="stream",
    )

    if action == "stream":
        try:
            stream(torrent, username, password, cookie)
        except RuntimeError as e:
            console.print(f"[red]{e}[/red]")
    elif action == "magnet":
        magnet = get_magnet(torrent, username, password, cookie)
        open_magnet(magnet)
        console.print("[green]🧲 Магнет открыт в торрент-клиенте![/green]")
    elif action == "page":
        open_torrent_page(torrent)
        console.print(f"[green]🌐 Открыто:[/green] {torrent.url}")
    else:
        console.print("[dim]Пропущено.[/dim]")