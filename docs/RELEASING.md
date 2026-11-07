# Release procedure

## Before publishing

1. The companion is MIT licensed. Preserve its license in every release. The formula's license field describes the companion package; it does not grant a separate license for the tap repository. The app itself has separate licensing and must not be copied into either repository.
2. Confirm version consistency in `scripts/pageflick` and `pyproject.toml`.
3. Run the synthetic test suite, byte compilation, clean wheel installation and package-content checks documented in `VERIFICATION.md`.
4. Review every tracked file for secrets, personal data and unintended app/source inclusion. Never package ignored build directories, connection files or the entire parent folder.
5. Commit reviewed source, metadata, license and documentation. Require a clean worktree. A release tag must identify that exact commit; never silently move a published tag.

## Source archive

Run from the repository root after the release commit exists, using the intended version and immutable commit:

```sh
VERSION=1.0.0
COMMIT=$(git rev-parse HEAD)
test -z "$(git status --porcelain)"
test -f LICENSE
mkdir -p dist
git archive --format=tar --prefix="pageflick-tools-$VERSION/" "$COMMIT" \
  | gzip -n > "dist/pageflick-tools-$VERSION.tar.gz"
shasum -a 256 "dist/pageflick-tools-$VERSION.tar.gz"
tar -tzf "dist/pageflick-tools-$VERSION.tar.gz"
```

`git archive` includes tracked files from the selected commit only. `gzip -n` omits variable timestamps and source filenames. Inspect the archive and extract it into a fresh temporary directory, then repeat tests against the extracted files.

## Homebrew formula

The formula installs `scripts/pageflick` directly, rewriting its shebang to the declared Homebrew Python dependency. There are no runtime PyPI dependencies or installation-time pairing actions.

Use the source archive's exact public release URL and SHA-256. Test installation, `brew test`, and the applicable style/audit checks. The formula test should use a synthetic connection and MCP tool discovery, never real pairing credentials or the user's library. After publication, download the artifact anonymously and verify that its SHA-256 still matches the formula.

## GitHub publication

Publish only after the owner has approved the license and public distribution. Verify the repository visibility, tag's commit, release asset and tap commit after each operation. Do not repeat an uncertain write before inspecting its outcome. Do not upload a wheel/source archive with a version that differs from the helper's reported version.

After the release and tap are public and verified, update the setup instructions with the real install command. Verify the remote commit rather than relying only on a successful local commit or push output. A GitHub dependency-graph run is not a substitute for test CI.
