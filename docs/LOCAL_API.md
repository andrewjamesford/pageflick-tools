# Local API compatibility

The helper connects to PageFlick's installed Mac app. It does not read the app database directly. A compatible app must expose the local automation API and the user must explicitly enable it and pair the copied connection.

## Connection schema

Connection schema version `1` includes `host`, ephemeral `port`, secret `token`, and `bundleID`. Only `127.0.0.1`, valid TCP ports and the PageFlick/PageFlick Dev bundle identifiers are accepted. Do not commit a real connection example.

Every HTTP request uses the current bearer token. The app returns JSON. Redirects are rejected. Restarting the app requires re-pairing because the port and key can change.

## Endpoints

- `GET /v1/stats?period=today|week|year`: reading report.
- `GET /v1/export`: versioned reading export.
- `GET /v1/books`: stable book ID, title and author choices.
- `POST /v1/open` with a book UUID: open at its saved position; success waits for reader readiness.
- `POST /v1/continue`: open the uniquely most recent book; ambiguous choices return an error with candidates.

Expected failures include unauthorized (`401`), locked/onboarding (`403`), missing book (`404`), ambiguous/unavailable/failed open (`409`), and unavailable service (`503`). A cancelled request abandons the waiter; it does not undo navigation already shown in the app.

## Data

Reports and exports use schema version `1`, ISO-8601 dates, seconds for durations, and half-open calendar periods. Listening is separate from active reading. Moving time reflects the app's reading setting, not measured exercise. Word and pace estimates are based on observed visible text at page turns; unavailable measurements remain explicit rather than invented.

Exports contain library metadata and reading history. They exclude EPUB files, book text, covers, camera frames, annotation text and locator contents. Opening a book alone does not start a recorded reading session; successful page turns do.

## MCP

The extracted adapter supports discovery/meta envelopes for protocol `2026-07-28` and initialize negotiation for `2025-11-25` and `2025-06-18`. Requests and responses are bounded, pending work is limited and cancellation closes the associated HTTP connection. Protocol support is inherited from the existing implementation; public-release QA should test the intended client versions.

## Compatibility status

This is a preview for API-enabled PageFlick builds. The public App Store listing checked on 2026-11-07 reports app version 1.0, released 2026-10-19; compatibility with that build has not been verified. The local API entered the inspected source on 2026-11-04, but source commit dates alone do not establish the content of a distributed app. Check for the local API setting. The first verified compatible public App Store version and live app acceptance remain to be recorded. Synthetic tests verify the helper, not a particular App Store release.
