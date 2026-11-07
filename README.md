# PageFlick tools

Optional command-line tools and a local stdio MCP server for the **installed PageFlick Mac app**. The app stays installed from the Mac App Store; this companion connects to its local API. It does not build, install, modify or replace the app, and it does not need the `pageflick-ios` source checkout.

**Status:** initial private extraction. No public release, PyPI package or Homebrew tap has been published. The inherited helper version is `1.0.0`; that is not a newly published release. See [provenance and licensing](PROVENANCE.md) before distribution.

## Requirements

- macOS and Python 3.9 or newer. Runtime code uses only the Python standard library.
- An installed PageFlick version that exposes **Settings → Automation → Local API, CLI and MCP**. Older settings may call this **Local automation**. The minimum App Store version still needs to be verified before a public release.
- Keep PageFlick open with its local API enabled. A source checkout is not required after the tools are installed.

## Install locally

From this repository, install into an isolated environment outside the checkout:

```sh
python3 -m venv "$HOME/.local/share/pageflick-tools/venv"
"$HOME/.local/share/pageflick-tools/venv/bin/python" -m pip install .
"$HOME/.local/share/pageflick-tools/venv/bin/pageflick" --version
```

The installed command works independently of this checkout. Use its full path, or add `$HOME/.local/share/pageflick-tools/venv/bin` to your shell's `PATH` yourself. For subsequent local updates, rerun the pip command with `--upgrade`.

A wheel or source distribution can be built with `python3 -m pip wheel --no-deps --wheel-dir dist .`. The build uses setuptools; no third-party Python packages are needed at runtime. Homebrew distribution is planned, not available yet: see [Homebrew](docs/HOMEBREW.md).

## Pair with the installed app

1. Open **PageFlick**, rather than PageFlick Dev, for the App Store app.
2. Enable its local API in Settings, then choose **Copy local connection for pairing**.
3. Run the installed command:

```sh
"$HOME/.local/share/pageflick-tools/venv/bin/pageflick" pair --clipboard
"$HOME/.local/share/pageflick-tools/venv/bin/pageflick" stats --period week
```

Pairing reads the connection from the clipboard and stores it in an owner-only `0600` file at `~/.config/pageflick/connection.json`. Clear the copied secret from the clipboard after pairing. Never paste it into a chat, issue or repository.

Restarting PageFlick or rotating its key changes the connection. Copy it again, run `pageflick pair --clipboard --replace`, then restart your MCP client/server. The examples below assume the installed tools directory is on `PATH`.

```sh
pageflick stats --period today
pageflick stats --period week
pageflick stats --period year
pageflick books
pageflick open --id BOOK_UUID
pageflick continue
pageflick export --output reading-data.json
```

Use a UUID from `books` for `open`. `continue` reports choices rather than guessing when recent books are ambiguous. Export creates a private JSON file and refuses to overwrite an existing file. Use `--connection PATH` **before** the subcommand, or `PAGEFLICK_CONNECTION_FILE`, for a separate private connection file.

## Connect an MCP client

Pair first, then configure a trusted AI client to launch the installed command with `mcp` as its only argument. Use an **absolute path**; most MCP clients do not expand `~` or shell variables.

```json
{
  "mcpServers": {
    "pageflick": {
      "command": "/Users/YOUR_USER/.local/share/pageflick-tools/venv/bin/pageflick",
      "args": ["mcp"]
    }
  }
}
```

Available tools: `reading_stats`, `reading_export`, `library_books`, `open_book`, and `continue_reading`. The server uses stdin/stdout and does not open another network listener. Only JSON-RPC is written to stdout. See [the API contract](docs/LOCAL_API.md) and [security notes](SECURITY.md).

An AI client may receive book titles, authors, reading history and statistics. Use only clients you trust, and review its data-sharing policy. This helper exposes no import or delete tools and does not provide book text or notes.

## Develop and test

```sh
python3 -m unittest discover -s scripts -p 'test_*.py' -v
python3 -m py_compile scripts/pageflick scripts/test_pageflick_cli.py
python3 scripts/pageflick --help
python3 scripts/pageflick --version
```

Tests use synthetic loopback fixtures and temporary connection files. They do not read the real PageFlick library, pair the installed app or change client settings. On non-Mac hosts the real executable integration test is skipped; macOS is the supported runtime.

## Distribution checklist

- Choose and approve a license before publishing source or packages.
- Verify the minimum compatible released PageFlick app version.
- Test the installed package and pairing against that app version, including restart/re-pair behavior.
- Publish an immutable versioned archive, calculate its SHA-256, and test the Homebrew formula against that exact archive.
- A future standalone binary/package for users without Python would require a separate build/signing/notarization workflow; none is included in this initial extraction.
