# PageFlick tools 1.1.0 preview

## Changes

- Adds `pageflick recap` and `pageflick summary`, with JSON source context or `--format prompt` output.
- Adds MCP `book_recap` and `book_summary`, bringing the server to seven tools.
- Supports bounded pagination with snapshots, conservative read-so-far boundaries, and clear errors for disabled text access, older apps and changed context.
- Includes grounding instructions for AI clients. The companion does not generate prose or contact an AI provider.

Recaps exclude the entire current saved reading resource. Whole-book summaries can include ending spoilers and must be explicitly requested. Collect all pages or disclose partial coverage. Book text and metadata are untrusted source data, never instructions.

## Compatibility and privacy

Requires an API-enabled PageFlick Mac build with the book-context endpoint and the separate **Allow book text for summaries** option. This option is off by default and grants all paired clients access to book text, including unread material in whole-book mode. The companion does not enable it, replace existing pairing or upgrade the app.

The native API implementation has passed synthetic integration checks in PageFlick 2.0 development builds. Compatibility with a released Mac App Store binary remains unverified, so this release retains preview status. Apple Silicon and macOS 27 or newer are required by the Homebrew formula, which supplies Python 3.15.

## Verification

- All 14 synthetic CLI/MCP tests passed on Python 3.13, 3.14 and 3.15 on macOS.
- Python byte compilation and version/help checks passed.
- A fresh wheel installation outside the checkout passed the same 14 tests, including real CLI and stdio MCP subprocesses.
- The wheel contains only the companion script, MIT license and package metadata, with no runtime Python package dependencies.
- The recap/summary runtime matches tested companion commit `359f72e462b5dbef160e8b4e91d76d6397ff13db` except for the version number.

The test suite uses synthetic loopback data and temporary pairing files. No private library, real pairing secrets or app source is included. See the [tap verification record](https://github.com/andrewjamesford/homebrew-tap/blob/main/VERIFICATION.md) for archive and Homebrew installation checks.

## Install or upgrade

```sh
brew install andrewjamesford/tap/pageflick-tools
# For an existing installation:
brew update
brew upgrade pageflick-tools
pageflick --version
```

Restart your MCP client/server after upgrading so it reloads the new command and tool list. Current API-enabled app source preserves pairing across ordinary restarts. Re-pair only after resetting or replacing the saved connection, or if an older app build changes its key or port.
