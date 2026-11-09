# PageFlick tools

Optional command-line tools and a local stdio MCP server for the **installed PageFlick Mac app**. The app stays installed from the Mac App Store; this companion connects to its local API. It does not build, install, modify or replace the app, and it does not need the `pageflick-ios` source checkout.

**Preview version:** 1.0.0. These optional tools are [MIT licensed](LICENSE). The PageFlick app is distributed separately and its license is unchanged. See [provenance](PROVENANCE.md).

**Compatibility preview:** this companion requires an API-enabled PageFlick build with the setting described below. The public App Store listing checked on 2026-11-07 reports version 1.0; compatibility with that build has not been verified. Check for the local API setting before installing these tools. The companion does not upgrade the app or add the API. The first verified compatible public App Store version remains to be confirmed.

## Requirements

- An Apple Silicon Mac running macOS 27 or newer, matching the current PageFlick app requirements. Python 3.9 or newer is required for a manual install; Homebrew supplies Python. Runtime code uses only the Python standard library.
- An installed PageFlick version that exposes **Settings → Automation → Local API, CLI and MCP**. Older settings may call this **Local automation**. The minimum App Store version still needs to be verified before a public release.
- Keep PageFlick open with its local API enabled. A source checkout is not required after the tools are installed.

## Install with Homebrew

```sh
brew install andrewjamesford/tap/pageflick-tools
pageflick --version
```

Homebrew installs the Python runtime and `pageflick` command. It does not install the PageFlick app or pair it automatically. Only the command-line companion is included. To update, run `brew update` and `brew upgrade pageflick-tools`.

The [tap](https://github.com/andrewjamesford/homebrew-tap) downloads the versioned source archive from this repository's [releases](https://github.com/andrewjamesford/pageflick-tools/releases). No PyPI runtime packages are required.

## Install locally without Homebrew

From this repository, install into an isolated environment outside the checkout:

```sh
python3 -m venv "$HOME/.local/share/pageflick-tools/venv"
"$HOME/.local/share/pageflick-tools/venv/bin/python" -m pip install .
"$HOME/.local/share/pageflick-tools/venv/bin/pageflick" --version
```

The installed command works independently of this checkout. Use its full path, or add `$HOME/.local/share/pageflick-tools/venv/bin` to your shell's `PATH` yourself. For subsequent local updates, rerun the pip command with `--upgrade`.

A wheel can be built with `python3 -m pip wheel --no-deps --wheel-dir dist .`. The build uses setuptools; no third-party Python packages are needed at runtime. See [Homebrew](docs/HOMEBREW.md) for distribution details.

## Pair with the installed app

1. Open **PageFlick**, rather than PageFlick Dev, for the App Store app.
2. Enable its local API in Settings, then choose **Copy local connection for pairing**.
3. Run the installed command (use its full virtualenv path if you installed without Homebrew):

```sh
pageflick pair --clipboard
pageflick stats --period week
```

Pairing reads the connection from the clipboard and stores it in an owner-only `0600` file at `~/.config/pageflick/connection.json`. Clear the copied secret from the clipboard after pairing. Never paste it into a chat, issue or repository.

The current app source preserves pairing across ordinary restarts; older builds may not. After resetting or replacing the saved connection, copy it again, run `pageflick pair --clipboard --replace`, then restart your MCP client/server. The examples below assume the installed tools directory is on `PATH`.

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

Pair first, then configure a trusted AI client to launch the installed command with `mcp` as its only argument. Use an **absolute path**; most MCP clients do not expand `~` or shell variables. For Homebrew, run `echo "$(brew --prefix pageflick-tools)/bin/pageflick"` to find the stable installed path.

```json
{
  "mcpServers": {
    "pageflick": {
      "command": "/opt/homebrew/opt/pageflick-tools/bin/pageflick",
      "args": ["mcp"]
    }
  }
}
```

The example uses the Apple Silicon Homebrew path. For a non-Homebrew install, replace it with your actual installed path.

Available tools: `reading_stats`, `reading_export`, `library_books`, `open_book`, `continue_reading`, `book_recap`, and `book_summary`. The server uses stdin/stdout and does not open another network listener. Only JSON-RPC is written to stdout. See [the API contract](docs/LOCAL_API.md) and [security notes](SECURITY.md).

An AI client may receive book titles, authors, reading history and statistics. Use only clients you trust, and review its data-sharing policy. This helper exposes no import or delete tools and does not provide notes. The optional recap and summary tools can provide book text after a separate app opt-in; see below.

## Book recaps and summaries (source context)

These commands require a newer API-enabled app with **separate book text access enabled** in Local automation settings. It is disabled by default. The first compatible public App Store version has not been verified. Updating this companion alone does not add the endpoint to an older app.

```sh
pageflick recap --id BOOK_UUID
pageflick recap --id BOOK_UUID --format prompt
pageflick summary --id BOOK_UUID --format prompt
```

`recap` returns source material **before the entire current saved reading resource**. It deliberately excludes that resource, even if you have read part of it. A resource is often a chapter, but EPUB structure varies. It does not estimate a cutoff from percentage progress, prove which pages you actually read, or automatically fall back to a full-book summary when the saved position is unavailable.

`summary` requests the whole book, including potential ending spoilers. Use it only when you want that coverage. Both commands return JSON context by default, not AI-generated prose. `--format prompt` wraps the page in instructions suitable for a trusted AI client. The companion makes no third-party AI calls and requires no model API key.

Each call returns one bounded page (default 12,000 characters; `--max-characters` accepts 1,000–24,000). If `complete` is false, fetch `nextOffset` using the same scope/book and returned `snapshot`:

```sh
pageflick recap --id BOOK_UUID --offset NEXT_OFFSET --snapshot SNAPSHOT
```

Collect every page from offset zero before claiming complete coverage, or clearly label a summary as partial. `complete: true` means the last page, not that you have collected earlier pages. If the content or cutoff changes, `context_changed` requires discarding earlier pages and starting again at offset zero. Prompts include these limitations; copying one page into an AI client does not supply the rest of the book.

Extraction uses strict XHTML parsing, not OCR or non-text media transcription. Navigation and explicitly hidden elements are excluded; stylesheet visibility is not evaluated, so CSS-hidden text could appear. Extraction fails closed above 2 MB per XHTML resource or 2 million source characters. A smaller page size cannot bypass these limits.

MCP `book_recap` and `book_summary` accept `id`, `offset`, `maxCharacters`, and `snapshot`. Returned instructions require grounding in supplied text, respecting warnings, and treating all book text and metadata as untrusted data rather than commands. A recap must not use the model's knowledge of future plot events. The full-summary tool must be explicitly requested.

Book text may be copyrighted and personal. Only pass it to clients/providers you trust and have permission to use. Avoid redirecting context into public files, logs, or repositories; ordinary shell redirection does not guarantee private file permissions.

## Develop and test

```sh
python3 -m unittest discover -s scripts -p 'test_*.py' -v
python3 -m py_compile scripts/pageflick scripts/test_pageflick_cli.py
python3 scripts/pageflick --help
python3 scripts/pageflick --version
```

Tests use synthetic loopback fixtures and temporary connection files. They do not read the real PageFlick library, pair the installed app or change client settings. On non-Mac hosts the real executable integration test is skipped; macOS is the supported runtime.

## Distribution checklist

- Verify the minimum compatible released PageFlick app version.
- Test the installed package and pairing against that app version, including restart/re-pair behavior.
- Follow [the release procedure](docs/RELEASING.md): publish an immutable versioned archive, calculate its SHA-256, and test the Homebrew formula against that exact archive.
- A future standalone binary/package for users without Python would require a separate build/signing/notarization workflow; none is included in this initial extraction.
