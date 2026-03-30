# CineCLI v0.1.5

CLI tool for searching and streaming movies from Rutracker directly in your terminal using mpv and webtorrent.

## Features

- Search torrents on Rutracker directly from the terminal
- Direct streaming to mpv without downloading files to disk
- Magnet link generation with multiple trackers for fast startup
- Interactive mode for convenient browsing and selection
- Flexible configuration with browser cookie support
- Smart torrent selection — automatically prefers 1080p, high seed counts, WebRip/BDRip releases

## Requirements

- Python 3.10+ (tested on 3.14)
- webtorrent — installed globally
- mpv — media player for streaming
- Node.js (required for installing webtorrent)

## Installation

### Step 1: Python package

```bash
pip install cinecli
```

### Step 2: System dependencies

#### macOS

```bash
brew install mpv
npm install -g webtorrent
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt-get install mpv npm
sudo npm install -g webtorrent
```

#### Linux (Fedora/RHEL)

```bash
sudo dnf install mpv npm
sudo npm install -g webtorrent
```

### Step 3: Configuration

Create the file `~/.config/cinecli/config.toml`:

```bash
mkdir -p ~/.config/cinecli
```

#### Option A: Username + Password

```toml
[rutracker]
username = "your_username"
password = "your_password"

[settings]
default_limit = 20
```

#### Option B: Browser cookies (recommended)

A more reliable method is to use cookies from your browser.

1. Open rutracker.org and log in
2. Open DevTools (F12)
3. Go to Application → Cookies → rutracker.org
4. Copy all cookies from the site (needed: `bb_guid`, `bb_session`, `bb_ssl`, `bb_t`, `bb_clearance`)
5. Add them to the config:

```toml
[rutracker]
username = "your_username"
password = "your_password"
cookie = "bb_guid=XXX; bb_session=YYY; bb_ssl=1; bb_t=ZZZ; bb_clearance=WWW"

[settings]
default_limit = 20
```

Tip: You can use a browser extension to export cookies automatically.

## Usage

### Search torrents

```bash
cinecli search matrix
cinecli search "enemy at the gates" --limit 10
cinecli search avatar -n 5
```

### Watch directly (main command)

Searches, automatically selects the best torrent, and starts streaming.

```bash
cinecli watch matrix
cinecli watch dune --limit 10
```

Selection can be manual if auto-selection is disabled in the prompt.

### Torrent details and actions

Open a specific torrent (by topic_id) and choose what to do with it.

```bash
cinecli get 6677988
```

Available actions:

- stream — direct streaming to mpv via webtorrent
- magnet — open the magnet link in a torrent client (qBittorrent, Transmission, etc.)
- page — open the torrent page in a browser
- skip — cancel and exit

### Interactive mode

```bash
cinecli interactive
```

How it works:

1. Enter the movie name
2. See a table of results
3. Choose automatic selection (best by seeds) or select manually
4. Select an action (stream, magnet, or page)

## Command Options

### `search` and `watch`

- `--limit N` or `-n N` — maximum number of results (default: 20)

Examples:

```bash
cinecli search "blade runner" --limit 5
cinecli watch inception -n 15
```

## Streaming Quality

The tool automatically prioritizes torrents suitable for streaming.

Priority:

- 1080p resolution
- WebRip, BDRip formats (~2–4 GB for fast start)
- High seed counts

Avoided:

- Large remux releases (>10 GB, slow buffering)
- UHD or Blu-ray rips that are too large

Tip: For the best experience choose WebRip or BDRip releases around 2–4 GB.

## Troubleshooting

### Authentication error

Problem: "Rutracker login failed" or login page returned.

Solution:

1. Check your username and password
2. Try using browser cookies instead (more reliable)
3. Make sure the site is accessible
4. Refresh cookies — they may expire

### webtorrent not found

```bash
npm install -g webtorrent
webtorrent --version
```

### mpv not found

- macOS: `brew install mpv`
- Ubuntu: `sudo apt-get install mpv`
- Fedora: `sudo dnf install mpv`

### Slow streaming

- Check your internet connection
- Choose torrents with more seeds
- Use `cinecli get <id>` and select a smaller file (WebRip)
- Avoid large remux releases for streaming

### API unavailable

If you see a warning about the API, the Rutracker server may be temporarily unavailable. The tool will automatically fall back to scraping the web interface (which works but may be slower).

## Configuration

### Config file location

- Linux/macOS: `~/.config/cinecli/config.toml`
- Windows: `%APPDATA%\cinecli\config.toml`

### Full configuration example

```toml
[rutracker]
username = "your_username"
password = "your_password"
cookie = ""

[settings]
default_limit = 20
```

## Development

### Build from source

```bash
git clone https://github.com/yourusername/cinecli
cd cinecli
pip install -e .
```

### Project dependencies

- typer — CLI framework
- rich — formatted terminal output (tables, panels)
- rutracker-api — Rutracker API client
- beautifulsoup4 — HTML parsing
- requests — HTTP requests
- lxml — parser for BeautifulSoup

### Development & testing

```bash
pip install -e ".[dev]"
pytest
black .
ruff .
```

## Usage Examples

### Scenario 1: Quickly watch a movie

```bash
$ cinecli watch matrix
Searching: matrix

Auto-select (most seeds)? [Y/n]: y

Selected: The Matrix (1999) 1080p WEB-DL [10 seeds, 2.3 GB]

Streaming: The Matrix (1999) 1080p WEB-DL
```

### Scenario 2: Manual selection

```bash
$ cinecli watch dune

Auto-select (most seeds)? [Y/n]: n
Select number [0-19]: 5
```

### Scenario 3: Get a magnet link for a torrent client

```bash
$ cinecli get 6677988

Action [stream/magnet/page/skip]: magnet

Magnet link opened in torrent client
```

## Legal Notice

This tool is intended only for personal lawful use with content you are legally allowed to access. Please respect copyright laws in your jurisdiction.

---

Version: 0.1.5  
Python: 3.10+  
License: MIT
