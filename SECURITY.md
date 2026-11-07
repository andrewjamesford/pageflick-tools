# Security and privacy

The tools connect only to the paired PageFlick API on IPv4 loopback `127.0.0.1`. Connections to other hosts and HTTP redirects are rejected. The MCP adapter runs over stdio, not a public network listener.

The pairing JSON contains a secret that grants access to PageFlick's local API. Pairing creates an owner-only `0600` connection file. The reader rejects symlinks, files owned by another user, and files readable by other users. Keep this secret out of version control, logs, support messages and screenshots. Clear it from the clipboard after pairing. Only use `--replace` when intentionally replacing a saved connection.

The application rotates the local connection when restarted or when its key is rotated. Disable the API in PageFlick to close its listener. Pairing is not synced through iCloud.

CLI output and exports contain reading information. An MCP client can receive the same data, and may forward it to its AI provider according to the client's configuration. Book titles, authors, reading statistics and history may be personal. Export files are created with `0600` permissions and existing files are not overwritten.

Tests must use synthetic data and temporary files. Do not read or copy the user's real connection file, database, EPUBs, exports, notes or credentials for packaging tests.

Before public distribution, establish a private security-reporting channel and document it here. Never report a real token or private reading data in a public issue.
