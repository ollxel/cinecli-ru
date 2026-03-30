# cinecli/api.py

from rutracker_api import RutrackerApi
from rutracker_api.exceptions import AuthorizationException
import rutracker_api.page_provider as _pp
import sys

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
        
        # Parse cookie string and add to session.cookies
        for cookie_part in cookie_str.split('; '):
            if '=' in cookie_part:
                key, val = cookie_part.split('=', 1)
                self.session.cookies.set(key.strip(), val.strip())
    return _cookie_login

_client: RutrackerApi | None = None


def get_client(username: str, password: str, cookie: str | None = None) -> RutrackerApi:
    """Return an authenticated RutrackerApi instance (singleton per process)."""
    global _client
    
    # Don't cache if using cookie - always create fresh client because cookies may expire
    if cookie:
        # Patch the PageProvider login method first
        _pp.PageProvider.login = _make_cookie_login(cookie)
        
        client = RutrackerApi()
        client.page_provider.session.headers.update({"User-Agent": _USER_AGENT})
        
        # Now call login with the patched method
        client.page_provider.login(None, None)
        return client
    
    # For username/password, use cached client
    if _client is None:
        _client = RutrackerApi()
        _client.page_provider.session.headers.update({"User-Agent": _USER_AGENT})
        try:
            _client.login(username, password)
        except AuthorizationException as exc:
            raise RuntimeError(
                "❌ Rustracker login failed with username/password.\n"
                "Rutracker может требовать cookie аутентификацию.\n"
                "Попробуй обновить кукис в конфиге."
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
    
    # Попытка получить через API (если доступен)
    try:
        result = client.topic(topic_id)
        if result and isinstance(result, list) and len(result) > 0:
            return result[0]
    except Exception:
        pass  # API недоступен, это нормально
    
    # Fallback: скребим страницу напрямую, минимальная информация
    from bs4 import BeautifulSoup
    pp = client.page_provider
    
    url = f"https://rutracker.org/forum/viewtopic.php?t={topic_id}"
    try:
        resp = pp.session.get(
            url,
            headers={"Cookie": pp.cookie} if pp.cookie else {},
        )
        soup = BeautifulSoup(resp.content, "html.parser")
        
        # Extract title from page
        title_elem = soup.find("h1")
        title = title_elem.text.strip() if title_elem else f"Torrent #{topic_id}"
        
        # Create minimal Torrent object
        from rutracker_api.torrent import Torrent
        torrent = Torrent(
            state="downloaded",
            category="Unknown",
            title=title,
            topic_id=topic_id,
            author="Unknown",
            size=0,
            seeds=0,
            leeches=0,
            downloads=0,
            registered=0,
        )
        torrent.url = url
        return torrent
    except Exception as e:
        raise RuntimeError(f"Ошибка при загрузке торрента #{topic_id}: {str(e)}")


def resolve_hash(torrent, username: str, password: str, cookie: str | None = None) -> str:
    """
    Get infohash for a torrent fetched without get_hash.
    Scrapes the topic page for data-hash — works when api.rutracker.org is down.
    """
    if torrent.hash:
        return torrent.hash

    from bs4 import BeautifulSoup
    import re
    
    client = get_client(username, password, cookie)
    pp = client.page_provider

    resp = pp.session.get(
        torrent.url,
        headers={"Cookie": pp.cookie} if pp.cookie else {},
    )

    soup = BeautifulSoup(resp.content, "html.parser")

    # Check if we got a login page
    if soup.find(id="login-form-full") or soup.find(id="login-form-quick"):
        raise RuntimeError(
            "❌ Потеря аутентификации при получении хеша (вновь появилась страница логина).\n"
            "Кукиs могут быть истекшими. Обновите их в конфиге."
        )

    # rutracker embeds hash in data-hash attribute on the download button
    el = soup.find(attrs={"data-hash": True})
    if el:
        torrent.hash = el["data-hash"]
        return torrent.hash

    # fallback: scrape magnet link - try different patterns
    a = soup.find("a", href=lambda h: h and h.startswith("magnet:"))
    if a:
        m = re.search(r"urn:btih:([a-fA-F0-9]{40})", a["href"])
        if m:
            torrent.hash = m.group(1)
            return torrent.hash

    # More aggressive search for magnet links in all links
    for a_tag in soup.find_all("a", href=True):
        href = a_tag.get("href", "")
        if "magnet:" in href:
            m = re.search(r"urn:btih:([a-fA-F0-9]{40})", href)
            if m:
                torrent.hash = m.group(1)
                return torrent.hash

    raise RuntimeError(
        f"❌ Не удалось получить хеш для торрента #{torrent.topic_id}.\n"
        "Это может означать что:\n"
        "  1. Кукиs истекли или потеряны - обновите в конфиге\n"
        "  2. Торрент требует авторизованного доступа\n"
        "  3. Используйте 'cinecli get {topic_id}' и выберите 'magnet' вместо 'stream'"
    )