# cinecli/api.py

from rutracker_api import RutrackerApi
from rutracker_api.exceptions import AuthorizationException
import rutracker_api.page_provider as _pp

_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

# ── Cookie-inject patch ───────────────────────────────────────────────────────
# Если в конфиге есть готовая кука из браузера — обходим логин полностью.
# Кука берётся из браузера: DevTools → Application → Cookies → rutracker.org → bb_data

def _make_cookie_login(cookie_str: str):
    """Return a login() replacement that injects a ready-made browser cookie."""
    def _cookie_login(self, username, password):
        self.session.headers.update({"User-Agent": _USER_AGENT})
        self.cookie = cookie_str
        self.authorized = True
    return _cookie_login

_client: RutrackerApi | None = None


def get_client(username: str, password: str, cookie: str | None = None) -> RutrackerApi:
    """Return an authenticated RutrackerApi instance (singleton per process)."""
    global _client
    if _client is None:
        if cookie:
            # Bypass login — use browser cookie directly
            _pp.PageProvider.login = _make_cookie_login(cookie)

        _client = RutrackerApi()
        _client.page_provider.session.headers.update({"User-Agent": _USER_AGENT})

        if cookie:
            _client.page_provider.cookie = cookie
            _client.page_provider.authorized = True
        else:
            try:
                _client.login(username, password)
            except AuthorizationException as exc:
                raise RuntimeError(
                    "❌ Rutracker login failed.\n"
                    "Попробуй добавить cookie из браузера в конфиг:\n"
                    "  1. Открой rutracker.org в браузере и залогинься\n"
                    "  2. DevTools → Application → Cookies → rutracker.org\n"
                    "  3. Скопируй значение куки bb_data\n"
                    "  4. Добавь в ~/.config/cinecli-ru/config.toml:\n"
                    '     cookie = "bb_data=ЗНАЧЕНИЕ"'
                ) from exc
    return _client


def search_torrents(
    query: str,
    username: str,
    password: str,
    limit: int = 20,
    cookie: str | None = None,
) -> list:
    """Search Rutracker and return up to *limit* Torrent objects."""
    client = get_client(username, password, cookie)
    # get_hash=False — пропускаем запрос к api.rutracker.org (часто недоступен).
    # Хеш подтягивается позже при открытии конкретного топика.
    result = client.search(query, get_hash=False)
    torrents = result.get("result", [])
    return torrents[:limit]


def get_torrent(topic_id: int, username: str, password: str, cookie: str | None = None):
    """Fetch a single Torrent object by its topic_id."""
    client = get_client(username, password, cookie)
    return client.get_torrent(topic_id)


def resolve_hash(torrent, username: str, password: str, cookie: str | None = None) -> str:
    """
    Get infohash for a torrent fetched without get_hash.
    Scrapes the topic page for data-hash — works when api.rutracker.org is down.
    """
    if torrent.hash:
        return torrent.hash

    from bs4 import BeautifulSoup
    client = get_client(username, password, cookie)
    pp = client.page_provider

    resp = pp.session.get(
        torrent.url,
        headers={"Cookie": pp.cookie},
    )
    soup = BeautifulSoup(resp.content, "html.parser")

    # rutracker embeds hash in data-hash attribute on the download button
    el = soup.find(attrs={"data-hash": True})
    if el:
        torrent.hash = el["data-hash"]
        return torrent.hash

    # fallback: scrape magnet link
    import re
    a = soup.find("a", href=lambda h: h and h.startswith("magnet:"))
    if a:
        m = re.search(r"urn:btih:([a-fA-F0-9]{40})", a["href"])
        if m:
            torrent.hash = m.group(1)
            return torrent.hash

    raise RuntimeError(f"\u274c Could not resolve hash for topic {torrent.topic_id}")