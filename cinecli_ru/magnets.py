# cinecli/magnets.py

import subprocess
import shutil
import webbrowser
from urllib.parse import quote
from rich.console import Console

console = Console()

# Большой список публичных трекеров — больше трекеров = больше пиров = быстрее старт
TRACKERS = [
    "http://bt2.t-ru.org/ann?magnet",
    "http://bt4.t-ru.org/ann?magnet",
    "udp://open.tracker.cl:1337/announce",
    "udp://tracker.opentrackr.org:1337/announce",
    "udp://tracker.openbittorrent.com:6969/announce",
    "udp://open.stealth.si:80/announce",
    "udp://tracker.torrent.eu.org:451/announce",
    "udp://explodie.org:6969/announce",
    "udp://tracker.empire-js.us:1337/announce",
    "udp://uploads.gamecoast.net:6969/announce",
    "udp://tracker1.bt.moack.co.kr:80/announce",
    "udp://tracker.tiny-vps.com:6969/announce",
    "udp://tracker.theoks.net:6969/announce",
    "udp://tracker.dler.org:6969/announce",
    "udp://tracker.altrosky.cc:6969/announce",
    "udp://retracker01-msk-virt.corbina.net:80/announce",
    "udp://opentracker.i2p.rocks:6969/announce",
    "udp://open.demonii.com:1337/announce",
    "udp://movies.zsw.ca:6969/announce",
    "udp://leet-tracker.moe:1337/announce",
    "udp://ipv4.tracker.harry.lu:80/announce",
    "udp://bt.oiyo.tk:6969/announce",
    "https://tracker.tamersunion.org:443/announce",
    "https://tracker.loligirl.cn:443/announce",
    "https://tracker.gbitt.info:443/announce",
]


def build_magnet(hash_: str, name: str) -> str:
    """Build a clean magnet URI with many trackers for fast peer discovery."""
    dn = quote(name, safe="")
    trackers = "".join(f"&tr={quote(t, safe=':/?=&')}" for t in TRACKERS)
    return f"magnet:?xt=urn:btih:{hash_}&dn={dn}{trackers}"


def get_magnet(torrent, username: str, password: str, cookie: str | None = None) -> str:
    """Return a clean magnet link, resolving hash from topic page if needed."""
    if not torrent.hash:
        from cinecli_ru.api import resolve_hash
        resolve_hash(torrent, username, password, cookie)
    return build_magnet(torrent.hash, torrent.title or "")


def _check_deps() -> None:
    """Check if webtorrent and mpv are installed."""
    if not shutil.which("webtorrent"):
        raise RuntimeError(
            "❌ webtorrent не установлен.\n"
            "Установите через: npm install -g webtorrent\n"
            "Или используйте: cinecli get <topic_id> для выбора других опций"
        )
    if not shutil.which("mpv"):
        raise RuntimeError(
            "❌ mpv не установлен.\n"
            "Установите через: brew install mpv\n"
            "Или используйте: cinecli get <topic_id> для выбора других опций"
        )


def stream(torrent, username: str, password: str, cookie: str | None = None) -> None:
    """Stream torrent directly into mpv via webtorrent."""
    _check_deps()

    magnet = get_magnet(torrent, username, password, cookie)
    size_gb = (torrent.size or 0) / 1024 ** 3

    console.print(
        f"\n[bold green]▶ Стриминг:[/bold green] [bold]{torrent.title}[/bold]\n"
        f"[dim]Размер: {torrent.formatted_size() if torrent.size else '?'} · "
        f"Трекеров: {len(TRACKERS)} · Ждём пиров…[/dim]\n"
    )

    if size_gb > 10:
        console.print(
            "[yellow]⚠  Файл больше 10 GB — стриминг может долго буферизоваться.\n"
            "   Рекомендуем выбрать торрент поменьше (BDRip/WEBRip ~2-4 GB).[/yellow]\n"
        )

    try:
        subprocess.run(["webtorrent", magnet, "--mpv"], check=True)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ webtorrent завершился с ошибкой: {e}[/red]")
    except KeyboardInterrupt:
        console.print("\n[dim]Остановлено.[/dim]")


def open_magnet(magnet_url: str) -> None:
    webbrowser.open(magnet_url)


def open_torrent_page(torrent) -> None:
    webbrowser.open(torrent.url)


# Ключевые слова хорошего размера для стриминга (меньше = быстрее старт)
_STREAM_FRIENDLY = ["webrip", "web-dl", "bdrip", "web-dlrip", "hdrip"]
_STREAM_HOSTILE  = ["bdremux", "remux", "blu-ray", "bluray", "uhd"]

def _stream_score(t) -> tuple:
    """Score a torrent for streaming suitability: prefer 1080p, smaller size, more seeds."""
    title_lower = (t.title or "").lower()
    size_gb = (t.size or 0) / 1024 ** 3

    # штраф за огромные ремуксы
    hostile = any(k in title_lower for k in _STREAM_HOSTILE)
    friendly = any(k in title_lower for k in _STREAM_FRIENDLY)

    # предпочитаем 1080p
    is_1080p = "1080" in title_lower

    # меньше размер = быстрее для стриминга (инвертируем)
    size_penalty = size_gb

    seeds = t.seeds or 0

    return (
        int(is_1080p),       # 1080p приоритет
        int(friendly),       # stream-friendly кодек
        int(not hostile),    # не ремукс
        seeds,               # больше сидов
        -size_penalty,       # меньше размер
    )


def select_best_torrent(torrents: list) -> object:
    """Pick best torrent for streaming: 1080p, small size, many seeds."""
    return max(torrents, key=_stream_score)