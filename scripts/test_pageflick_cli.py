"""Owned loopback fixtures for the Mac CLI/MCP adapter. No app library access."""
import http.server
import importlib.machinery
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).with_name("pageflick")
loader = importlib.machinery.SourceFileLoader("pageflick_cli", str(SCRIPT))
spec = importlib.util.spec_from_loader(loader.name, loader)
cli = importlib.util.module_from_spec(spec)
loader.exec_module(cli)
TOKEN = "a" * 64
REPORT = {"schemaVersion": 1, "activeSeconds": 180, "movingSeconds": 60, "wordCountStatus": "unavailable"}
BOOK_ID = "91b3fcc4-784d-49f0-977f-47049d96345a"


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def respond(self, status, value):
        data = json.dumps(value).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def allowed(self):
        if self.headers.get("Authorization") != "Bearer " + TOKEN:
            self.respond(401, {"error": "unauthorized"})
            return False
        return True

    def do_GET(self):
        if not self.allowed():
            return
        if self.path.startswith("/v1/stats?"):
            self.respond(200, REPORT)
        elif self.path == "/v1/export":
            self.respond(200, {"schemaVersion": 1, "reports": [REPORT], "sessions": []})
        elif self.path == "/v1/books":
            self.respond(200, [{"id": BOOK_ID, "title": "Synthetic", "author": "Fixture"}])
        elif self.path == "/redirect":
            self.send_response(302)
            self.send_header("Location", "https://example.com/")
            self.end_headers()
        else:
            self.respond(404, {"error": "unknown_endpoint"})

    def do_POST(self):
        if not self.allowed():
            return
        length = int(self.headers.get("Content-Length", "0"))
        data = json.loads(self.rfile.read(length))
        if self.path == "/v1/open" and data.get("id") == BOOK_ID:
            self.respond(200, {"opened": True})
        else:
            self.respond(409, [{"id": BOOK_ID, "title": "Choose explicitly", "author": "Fixture"}])


class CLITests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.config = {"schemaVersion": 1, "host": "127.0.0.1", "port": cls.server.server_port,
                      "token": TOKEN, "bundleID": "nz.co.andrewford.PageFlick.dev"}

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="PageFlick-CLI-fixture-")
        self.addCleanup(self.directory.cleanup)
        self.connection = Path(self.directory.name) / "connection.json"
        cli.pair(self.connection, json.dumps(self.config))

    def wait_pending(self, server):
        deadline = time.monotonic() + 3
        while server.pending and time.monotonic() < deadline:
            time.sleep(0.01)
        self.assertFalse(server.pending)

    def test_pairing_is_private_exclusive_and_rejects_symlinks(self):
        self.assertEqual(self.connection.stat().st_mode & 0o777, 0o600)
        self.assertEqual(cli.load_connection(self.connection), self.config)
        with self.assertRaises(cli.LocalError):
            cli.pair(self.connection, json.dumps(self.config))
        link = Path(self.directory.name) / "link.json"
        link.symlink_to(self.connection)
        with self.assertRaises(cli.LocalError):
            cli.load_connection(link)

    def test_remote_host_and_world_readable_credentials_are_rejected(self):
        for host in ("localhost", "0.0.0.0", "example.com", "127.0.0.2"):
            with self.assertRaises(cli.LocalError):
                cli.validate_connection(dict(self.config, host=host))
        self.connection.chmod(0o644)
        with self.assertRaises(cli.LocalError):
            cli.load_connection(self.connection)

    def test_query_export_and_book_metadata_match_fixture_api(self):
        client = cli.Client(self.config)
        self.assertEqual(client.tool("reading_stats", {"period": "week"}), REPORT)
        self.assertEqual(client.tool("reading_export", {})["reports"], [REPORT])
        self.assertEqual(client.tool("library_books", {})["books"][0]["id"], BOOK_ID)

    def test_unauthorized_and_redirect_errors_do_not_leak_token_or_follow_remote_host(self):
        client = cli.Client(dict(self.config, token="b" * 64))
        with self.assertRaises(cli.LocalError) as error:
            client.tool("reading_stats", {})
        self.assertNotIn("b" * 64, str(error.exception))
        with self.assertRaisesRegex(cli.LocalError, "redirects"):
            cli.Client(self.config).request("GET", "/redirect")

    def test_open_uses_stable_id_and_ambiguous_continue_is_an_error(self):
        client = cli.Client(self.config)
        with patch.object(client, "activate") as activate:
            self.assertTrue(client.tool("open_book", {"id": BOOK_ID})["opened"])
            activate.assert_called_once()
            with self.assertRaises(cli.LocalError):
                client.tool("continue_reading", {})
        with self.assertRaises(ValueError):
            client.tool("open_book", {"id": "not-a-uuid"})

    def test_mcp_modern_discovery_query_and_version_errors(self):
        output = io.StringIO()
        server = cli.MCPServer(cli.Client(self.config), output)
        self.addCleanup(server.close)
        metadata = {"io.modelcontextprotocol/protocolVersion": cli.MODERN,
                    "io.modelcontextprotocol/clientCapabilities": {}}
        server.handle({"jsonrpc": "2.0", "id": 1, "method": "server/discover", "params": {"_meta": metadata}})
        server.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {
            "_meta": metadata, "name": "reading_stats", "arguments": {"period": "week"}}})
        self.wait_pending(server)
        server.handle({"jsonrpc": "2.0", "id": 3, "method": "tools/list", "params": {
            "_meta": dict(metadata, **{"io.modelcontextprotocol/protocolVersion": "1900-01-01"})}})
        server.handle({"jsonrpc": "2.0", "id": 4, "method": "tools/list", "params": {
            "_meta": {"io.modelcontextprotocol/protocolVersion": cli.MODERN}}})
        replies = {item["id"]: item for item in map(json.loads, output.getvalue().splitlines())}
        self.assertIn(cli.MODERN, replies[1]["result"]["supportedVersions"])
        self.assertEqual(replies[2]["result"]["structuredContent"], REPORT)
        self.assertEqual(replies[2]["result"]["resultType"], "complete")
        self.assertEqual(replies[3]["error"]["code"], -32022)
        self.assertEqual(replies[4]["error"]["code"], -32602)

    def test_mcp_legacy_handshake_and_unknown_tool_errors(self):
        output = io.StringIO()
        server = cli.MCPServer(cli.Client(self.config), output)
        self.addCleanup(server.close)
        server.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-11-25"}})
        server.handle({"jsonrpc": "2.0", "method": "notifications/initialized"})
        server.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        server.handle({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "delete_all_books"}})
        self.wait_pending(server)
        replies = {item["id"]: item for item in map(json.loads, output.getvalue().splitlines())}
        self.assertEqual(replies[1]["result"]["protocolVersion"], "2025-11-25")
        self.assertEqual(len(replies[2]["result"]["tools"]), 5)
        self.assertEqual(replies[3]["error"]["code"], -32602)

    def test_mcp_cancellation_stops_pending_work_and_sends_no_success(self):
        class WaitingClient:
            def tool(self, name, arguments, call):
                call.cancelled.wait(3)
                raise cli.LocalError("Request cancelled.")
        output = io.StringIO()
        server = cli.MCPServer(WaitingClient(), output)
        self.addCleanup(server.close)
        server.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-11-25"}})
        server.handle({"jsonrpc": "2.0", "method": "notifications/initialized"})
        server.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "reading_stats"}})
        server.handle({"jsonrpc": "2.0", "method": "notifications/cancelled", "params": {"requestId": 2}})
        self.wait_pending(server)
        replies = list(map(json.loads, output.getvalue().splitlines()))
        self.assertEqual([item["id"] for item in replies], [1])

    @unittest.skipUnless(sys.platform == "darwin", "Mac-only executable")
    def test_real_stdio_process_and_cli_export_preserve_json_and_private_files(self):
        process = subprocess.Popen([sys.executable, str(SCRIPT), "--connection", str(self.connection), "mcp"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            for request in [
                {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-11-25"}},
                {"jsonrpc": "2.0", "method": "notifications/initialized"},
                {"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "reading_stats", "arguments": {"period": "week"}}}
            ]:
                process.stdin.write(json.dumps(request) + "\n")
                process.stdin.flush()
                if "id" in request:
                    reply = json.loads(process.stdout.readline())
                    self.assertEqual(reply["id"], request["id"])
                    if request["id"] == 2:
                        self.assertEqual(reply["result"]["structuredContent"], REPORT)
            process.stdin.close()
            self.assertEqual(process.wait(timeout=5), 0)
            self.assertEqual(process.stderr.read(), "")
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()
            process.stdout.close()
            process.stderr.close()
        exported = Path(self.directory.name) / "reading.json"
        command = [sys.executable, str(SCRIPT), "--connection", str(self.connection), "export", "--output", str(exported)]
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 0)
        self.assertEqual(exported.stat().st_mode & 0o777, 0o600)
        original = exported.read_bytes()
        self.assertEqual(subprocess.run(command, capture_output=True).returncode, 2)
        self.assertEqual(exported.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
