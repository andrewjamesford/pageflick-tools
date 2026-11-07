# Initial extraction verification

Historical extraction checks on the owner's Apple Silicon Mac on 2026-11-07, before publication. Later release and Homebrew checks are recorded in the release notes and tap documentation.

## Passed

- Both copied source files match their original SHA-256 hashes in `PROVENANCE.md`.
- Nine synthetic CLI/MCP tests passed on each installed Python 3.13, 3.14 and 3.15 interpreter, including real stdio MCP subprocesses and private export-file behavior.
- Python byte compilation, `--help` and `--version` passed.
- Built `pageflick_tools-1.0.0-py3-none-any.whl` using the declared setuptools build backend.
- Installed the wheel with `--no-index --no-deps` into a fresh temporary virtual environment outside the repository.
- The installed command passed `--help`, `--version`, and the existing nine-test suite with the subprocess command pointed at the installed copy. It was a real installed script, not a symlink into the source checkout.
- Inspected the wheel contents: one script plus package metadata; no runtime dependencies, credentials, real connection files, app data or app source.

## Not verified or performed

- Python 3.9–3.12 were not available for this validation. The inherited minimum remains Python 3.9.
- The real installed App Store app was not paired or queried. Minimum released-app compatibility and live app acceptance remain open.
- No Homebrew formula installation/audit, public tap, release tag, public package publication, signing or notarization.
- No changes to the user's actual CLI installation, MCP client configuration or saved pairing.
- No CI workflow was enabled in this initial extraction.

The fixture tests are not a full live-app or public-distribution acceptance result.
