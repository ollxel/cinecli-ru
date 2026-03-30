# cinecli/ui.py

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()


def show_torrents(torrents: list) -> None:
    """Render a table of Rutracker Torrent objects."""
    table = Table(title="🔍 Search Results", show_lines=False)

    table.add_column("#",        style="cyan",   justify="right",  no_wrap=True)
    table.add_column("ID",       style="dim",    justify="right",  no_wrap=True)
    table.add_column("Title",    style="bold",   ratio=4)
    table.add_column("Category", style="magenta",ratio=2)
    table.add_column("Size",     justify="right",no_wrap=True)
    table.add_column("Seeds",    justify="center",no_wrap=True)
    table.add_column("Leeches",  justify="center",no_wrap=True)
    table.add_column("Date",     justify="center",no_wrap=True)

    for idx, t in enumerate(torrents):
        seeds_str   = _colored_num(t.seeds,   "green")
        leeches_str = _colored_num(t.leeches, "red")

        try:
            date_str = t.formatted_registered()
        except Exception:
            date_str = "—"

        table.add_row(
            str(idx),
            str(t.topic_id),
            t.title or "—",
            t.category or "—",
            t.formatted_size() if t.size else "—",
            seeds_str,
            leeches_str,
            date_str,
        )

    console.print(table)


def show_torrent_details(torrent) -> None:
    """Render a detail panel for a single Torrent."""
    try:
        date_str = torrent.formatted_registered()
    except Exception:
        date_str = "—"

    lines = [
        f"[bold]{torrent.title}[/bold]",
        "",
        f"[dim]Topic ID:[/dim]  {torrent.topic_id}",
        f"[dim]Category:[/dim]  {torrent.category or '—'}",
        f"[dim]Author:[/dim]    {torrent.author or '—'}",
        f"[dim]Size:[/dim]      {torrent.formatted_size() if torrent.size else '—'}",
        f"[dim]Seeds:[/dim]     [green]{torrent.seeds or 0}[/green]",
        f"[dim]Leeches:[/dim]   [red]{torrent.leeches or 0}[/red]",
        f"[dim]Downloads:[/dim] {torrent.downloads or '—'}",
        f"[dim]Added:[/dim]     {date_str}",
        f"[dim]URL:[/dim]       [link={torrent.url}]{torrent.url}[/link]",
    ]

    console.print(Panel("\n".join(lines), title="📦 Torrent Details", expand=False))


# ── helpers ──────────────────────────────────────────────────────────────────

def _colored_num(value, color: str) -> str:
    if value is None:
        return "[dim]—[/dim]"
    return f"[{color}]{value}[/{color}]"