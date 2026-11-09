# Local API compatibility

The helper connects to PageFlick's installed Mac app. It does not read the app database directly. A compatible app must expose the local automation API and the user must explicitly enable it and pair the copied connection.

## Connection schema

Connection schema version `1` includes `host`, `port`, secret `token`, and `bundleID`. Only `127.0.0.1`, valid TCP ports and the PageFlick/PageFlick Dev bundle identifiers are accepted. Do not commit a real connection example.

Every HTTP request uses the current bearer token. The app returns JSON. Redirects are rejected. Current app source preserves the paired connection across ordinary restarts; resetting or removing it requires re-pairing. Older builds may change the port and key on restart. This does not establish the behavior of any installed or released build.

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

## Book context endpoint

`POST /v1/book-context` requires authentication, an unlocked/onboarded app, and a separate default-disabled book text access setting. Request:

```json
{"id":"BOOK_UUID","scope":"read_so_far","offset":0,"maxCharacters":12000}
```

- `scope`: `read_so_far` or `whole_book`; the companion maps recap and summary to fixed scopes.
- `offset`: integer from zero through 2,000,000, default zero.
- `maxCharacters`: integer from 1,000 through 24,000, default 12,000.
- `snapshot`: opaque first-page identifier, required for offsets greater than zero. Never derive offsets from byte counts; use the returned `nextOffset`.

Response fields: `schemaVersion: 1`, `kind: "book_summary_context"`, `book: {id,title,author}`, `scope`, `snapshot`, `boundary`, `text`, `offset`, optional `nextOffset`, `complete`, and `warnings` (strings). `boundary` contains `policy` (`before_current_resource` or `whole_book`), `currentResourceExcluded`, and optional `lastReadAt` (ISO-8601) and `progress`. The helper adds `instructions` to guide downstream summarization.

Read-so-far excludes the entire current spine resource. Progress is descriptive only, never used to guess a word cutoff. Material before a saved position is not proof of actual reading. The response must not expose unread resource titles or locators. Whole-book context may include ending spoilers and must be explicitly requested. Missing or unresolved positions must fail rather than silently widen scope.

Pages are bounded. Continue with `nextOffset` and the same snapshot until `complete` is true. The last page alone is not whole coverage. A changed content/cutoff snapshot yields HTTP 409 `context_changed`; discard collected pages and restart at zero. Partial extraction warnings and incomplete pagination must be disclosed in any summary.

Expected errors include HTTP 403 `book_text_access_disabled` or `unlock_and_finish_onboarding`, HTTP 404 `book_not_found`, and HTTP 409 `reading_position_unavailable`, `reading_position_unresolved`, `no_completed_sections`, `content_unavailable`, `unsupported_content`, `book_not_downloaded`, `context_changed`, or `context_too_large`. Malformed requests return HTTP 400 `invalid_context_request`. An unknown endpoint on an older app requires a compatible app update, not merely a companion update. No generated prose, model API calls, book imports or reading-position mutations are performed by these tools.

Extraction uses strict XHTML parsing without OCR or non-text media transcription. Navigation and explicitly hidden elements are excluded, but stylesheet visibility is not evaluated and CSS-hidden text could appear. Limits are 2 MB per XHTML resource and 2 million source characters; exceeding either fails closed with `context_too_large`. Smaller `maxCharacters` pages do not bypass the extraction limits.

## MCP

The extracted adapter supports discovery/meta envelopes for protocol `2026-07-28` and initialize negotiation for `2025-11-25` and `2025-06-18`. Requests and responses are bounded, pending work is limited and cancellation closes the associated HTTP connection. Protocol support is inherited from the existing implementation; public-release QA should test the intended client versions.

## Compatibility status

This is a preview for API-enabled PageFlick builds. The public App Store listing checked on 2026-11-07 reports app version 1.0, released 2026-10-19; compatibility with that build has not been verified. The local API entered the inspected source on 2026-11-04, but source commit dates alone do not establish the content of a distributed app. Check for the local API setting. The first verified compatible public App Store version and live app acceptance remain to be recorded. Synthetic tests verify the helper, not a particular App Store release.
