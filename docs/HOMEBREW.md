# Homebrew distribution plan

## Package the companion, not the App Store app

Keep PageFlick installed and updated through the Mac App Store. Package this Python CLI/MCP companion as a Homebrew **formula**. Homebrew can install its Python dependency and place the `pageflick` command on PATH; users do not need the app source repository.

A **cask** for the graphical app would be a separate distribution decision and would require an upstream-supported downloadable app archive or installer. An App Store listing URL is not that artifact. No direct-download PageFlick app is created by this repository.

## Own tap is the practical starting point

A third-party tap is an ordinary Git repository containing formula files. The proposed name is `andrewjamesford/homebrew-tap`, with `Formula/pageflick-tools.rb`. It can host other tools later too.

A tap is not mandatory for every Homebrew package: software accepted into Homebrew's official repositories can be installed without an upstream tap. But `homebrew/core` requires an acceptable open-source license, stable verifiable source and must not depend on proprietary software or a cask. Because this companion requires the proprietary PageFlick app, our own tap is the practical route, rather than planning around core acceptance.

After a public tap and release are actually ready, the intended command would be:

```sh
brew install andrewjamesford/tap/pageflick-tools
```

This command is **not available yet**. Modern Homebrew also applies trust controls to third-party taps; users should review the package they install.

## Needed before publishing

1. Approve repository visibility and a distribution license for the companion. Keeping the main app private is independent of choosing a license for these small tools.
2. Verify minimum compatible App Store app version and fresh-user pairing instructions.
3. Publish a versioned, immutable archive of the reviewed tools, with tests and documentation. Record its SHA-256.
4. Create the tap and a macOS-only formula with description, homepage, version/archive URL, SHA-256, the chosen license, and a Homebrew Python dependency. The formula should install the helper with the Homebrew interpreter and never write or request a pairing secret during installation.
5. Test installation from that exact archive, `--version`/`--help`, fixture-based CLI/MCP behavior, uninstall/reinstall, and applicable `brew audit`/`brew test` checks.
6. For each release, update the formula's version, URL and checksum, then repeat the checks.

Private taps can be used by authorized users but are not friction-free public distribution. This initial repository creation does not create a tap, publish a release, select a public license, or enable automatic release workflows.

## Official references

- [Create and maintain a tap](https://docs.brew.sh/How-to-Create-and-Maintain-a-Tap)
- [Acceptable formulae](https://docs.brew.sh/Acceptable-Formulae)
- [Formula cookbook](https://docs.brew.sh/Formula-Cookbook)
- [Acceptable casks](https://docs.brew.sh/Acceptable-Casks)
- [Cask cookbook](https://docs.brew.sh/Cask-Cookbook)

Reviewed 2026-11-07. These are Homebrew's policies, not a guarantee of acceptance into an official repository.
