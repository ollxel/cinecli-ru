# CineCLI

A command-line tool for searching and streaming movies directly from Rutracker to your terminal using mpv and webtorrent.

## Features

- Search for torrents on Rutracker from the command line
- Stream movies directly to mpv without downloading
- Get quick access to magnet links
- Interactive mode for browsing and selection
- Configuration-based settings
- Support for browser cookies for authentication

## Requirements

- Python 3.10 or higher
- mpv media player
- webtorrent CLI tool
- Node.js (for webtorrent installation)

## Installation

### 1. Install Python Dependencies

```bash
pip install cinecli-ru
```

### 2. Install System Dependencies

#### macOS

```bash
brew install mpv
npm install -g webtorrent-cli
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt-get install mpv
sudo apt-get install npm
sudo npm install -g webtorrent-cli
```

#### Linux (Fedora/RHEL)

```bash
sudo dnf install mpv
sudo dnf install npm
sudo npm install -g webtorrent-cli
```

### 3. Configure Credentials

Create a configuration file at `~/.config/cinecli-ru/config.toml`:

```bash
mkdir -p ~/.config/cinecli-ru
```

Then edit `~/.config/cinecli-ru/config.toml`:

```toml
[rutracker]
username = "your_username"
password = "your_password"

[settings]
default_action = "magnet"   # "magnet" | "torrent"
default_limit  = 20
```

#### Authentication via Browser Cookie (Recommended)

For better reliability, you can use your browser's authentication cookie instead of storing your password:

1. Open rutracker.org in your browser and log in
2. Open Developer Tools (F12)
3. Go to Application → Cookies → rutracker.org
4. Find the `bb_session` cookie and copy its value (starts with "0-")
5. Add it to your config:

```toml
[rutracker]
username = "your_username"
password = "your_password"
cookie = "bb_session=0-XXXXXXXXXXXXX"

[settings]
default_action = "magnet"
default_limit  = 20
```

The tool will prefer the cookie over username/password if provided.

## Usage

### Search for a Movie

```bash
cinecli-ru search matrix
cinecli-ru search "the dark knight" --limit 10
```

### Watch a Movie Directly

Automatically selects the best torrent and streams to mpv:

```bash
cinecli-ru watch matrix
cinecli-ru watch inception --limit 10
```

### Get Torrent Details and Choose Action

Fetch a specific torrent by ID and choose your action:

```bash
cinecli-ru get 12345
```

Actions available:
- `stream` - Stream directly to mpv via webtorrent
- `magnet` - Open magnet link in your torrent client
- `page` - Open torrent page in web browser
- `skip` - Skip and exit

### Interactive Mode

Launch an interactive session:

```bash
cinecli-ru interactive
```

This mode will:
1. Prompt you to enter a search query
2. Display search results
3. Offer to auto-select the best torrent (by seeds and size)
4. Let you choose between stream, magnet, page, or skip

## Options

### Search and Watch Commands

- `--limit N` or `-n N` - Maximum number of search results (default: 20)

Example:
```bash
cinecli-ru search "fight club" --limit 5
cinecli-ru watch "shawshank redemption" -n 15
```

## Streaming Quality

The tool automatically selects torrents optimized for streaming:

- Prefers 1080p resolution
- Prioritizes WebRip and BD-Rip formats (smaller files, faster start)
- Avoids large remux files
- Selects torrents with the most seeds

Note: Very large files (>10GB) may take longer to buffer. For best streaming experience, select WEBRip or BDRip quality (2-4 GB).

## Troubleshooting

### Authentication Failed

If you get "Rutracker login failed":

1. Verify your username and password are correct
2. Try using a browser cookie instead (see Configuration section)
3. Check that Rutracker is accessible
4. Set the cookie from browser following the steps above

### webtorrent Not Found

Install webtorrent globally:

```bash
npm install -g webtorrent-cli
```

Verify installation:

```bash
webtorrent --version
```

### mpv Not Found

Install mpv for your system:

- macOS: `brew install mpv`
- Ubuntu: `sudo apt-get install mpv`
- Fedora: `sudo dnf install mpv`

### Streaming is Slow

- Check your internet connection
- Try a torrent with more seeds
- Use `cinecli-ru get <id>` and select a smaller file (WebRip/BDRip)
- Avoid large remux files for streaming

### API Error

If you see "API unavailable" warnings, the Rutracker API is temporarily down. The tool will automatically fall back to scraping the web interface.

## Configuration File Details

### Default Values

```toml
[rutracker]
username = ""           # Required
password = ""           # Required
cookie = ""            # Optional, preferred over password

[settings]
default_action = "magnet"   # Action when --action not specified
default_limit = 20          # Default search result limit
```

### Configuration Location

- Linux/macOS: `~/.config/cinecli-ru/config.toml`
- Windows: `%APPDATA%\cinecli-ru\config.toml`

## Development

### Building from Source

```bash
git clone https://github.com/ollxel/cinecli-ru
cd cinecli-ru
pip install -e .
```

### Dependencies

- `typer` - CLI framework
- `rich` - Beautiful terminal output
- `rutracker-api` - Rutracker API client
- `webbrowser` - Open web links
- `beautifulsoup4` - Web scraping


## Support

For issues, feature requests, or contributions, please visit the project repository.

---

**Note:** This tool is intended for personal, legal use only. Respect copyright laws in your jurisdiction.
