# Homebrew distribution

## Install the companion

```sh
brew install andrewjamesford/tap/pageflick-tools
pageflick --version
```

The [tap repository](https://github.com/andrewjamesford/homebrew-tap) contains `Formula/pageflick-tools.rb`. It downloads a versioned source archive from the [tools releases](https://github.com/andrewjamesford/pageflick-tools/releases), verifies SHA-256, and installs the standalone script using Homebrew Python 3.15. There are no runtime PyPI dependencies.

**Preview:** an API-enabled PageFlick Mac build is required. Recaps and summaries need the newer book-context endpoint and separate **Allow book text for summaries** opt-in. Compatibility with a released Mac App Store build remains unverified; check for both settings before using those commands.

The command installs the CLI/MCP companion only. Keep PageFlick installed through the Mac App Store and follow the README's pairing steps. Your app must expose the local API setting; the tools do not add that feature to older app builds.

## Update and remove

```sh
brew update
brew upgrade pageflick-tools
brew uninstall pageflick-tools
```

Uninstalling the formula does not uninstall PageFlick, alter its library or delete your private pairing file. To revoke API access, disable the local API or rotate its key in PageFlick. Review and remove any obsolete saved connection file yourself if you no longer need it.

## Why a separate tap?

Official `homebrew/core` inclusion is not required for a third-party tap. Core requires an acceptable open-source license, stable verifiable source and must not depend on proprietary software or a cask. This companion is MIT licensed, but it requires the separately distributed PageFlick app, so a maintained upstream tap is the practical route.

A cask for the graphical app would require a supported direct-download app archive or installer. An App Store listing URL is not that artifact. The tap does not distribute the app or alter its license.

## Maintenance

Follow [the release procedure](RELEASING.md). For each release, update the formula URL and SHA-256, verify installation from the exact archive, and run `brew test`, style and applicable audit checks. Formula installation must never request or write pairing credentials. Formula tests use synthetic data only.

Homebrew applies trust controls to third-party taps. Review the package you install; whole-tap trust is not needed merely to install this formula.

## Official references

- [Create and maintain a tap](https://docs.brew.sh/How-to-Create-and-Maintain-a-Tap)
- [Acceptable formulae](https://docs.brew.sh/Acceptable-Formulae)
- [Formula cookbook](https://docs.brew.sh/Formula-Cookbook)
- [Acceptable casks](https://docs.brew.sh/Acceptable-Casks)
- [Cask cookbook](https://docs.brew.sh/Cask-Cookbook)

Reviewed 2026-11-07. These are Homebrew's policies, not a guarantee of acceptance into an official repository.
