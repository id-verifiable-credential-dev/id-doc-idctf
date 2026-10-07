import json
import socket
import threading
import unittest
import urllib.error
import urllib.request
from http.server import HTTPServer
from unittest import mock

import chat
from _ask import gemini, service


class HandlerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = HTTPServer(("127.0.0.1", 0), chat.handler)
        cls.port = cls.server.server_address[1]
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        service.LIMITER._hits.clear()

    def post(self, body: bytes, headers=None):
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/api/chat",
            data=body,
            method="POST",
            headers={"Content-Type": "application/json", **(headers or {})},
        )
        try:
            with urllib.request.urlopen(req) as resp:
                return resp.status, json.loads(resp.read())
        except urllib.error.HTTPError as err:
            return err.code, json.loads(err.read())

    def test_post_happy_path_through_stubbed_model(self):
        def fake_ask(system, contents, *, models, call=None):
            return gemini.ModelReply(text=json.dumps({"answer": "hi", "sources": []}), model=models[0], blocked_reason=None)

        with mock.patch.object(service.gemini, "ask_model", fake_ask), \
             mock.patch.object(service.corpus, "load", lambda env: ("corpus", {"/"})):
            status, out = self.post(json.dumps({"question": "hello"}).encode())
        self.assertEqual(status, 200)
        self.assertEqual(out, {"answer": "hi", "sources": []})

    def test_get_is_405(self):
        req = urllib.request.Request(f"http://127.0.0.1:{self.port}/api/chat")
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req)
        self.assertEqual(ctx.exception.code, 405)
        self.assertEqual(json.loads(ctx.exception.read()), {"error": "bad_request"})
        self.assertEqual(ctx.exception.headers["Cache-Control"], "no-store")

    def test_options_is_405_json(self):
        req = urllib.request.Request(f"http://127.0.0.1:{self.port}/api/chat", method="OPTIONS")
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req)
        self.assertEqual(ctx.exception.code, 405)
        self.assertEqual(json.loads(ctx.exception.read()), {"error": "bad_request"})
        self.assertEqual(ctx.exception.headers["Cache-Control"], "no-store")

    def test_head_is_405(self):
        # urllib hides a body on a HEAD response either way, so go through a
        # raw socket to confirm the server itself writes none.
        with socket.create_connection(("127.0.0.1", self.port)) as raw_sock:
            raw_sock.sendall(b"HEAD /api/chat HTTP/1.1\r\nHost: x\r\n\r\n")
            chunks = []
            while True:
                chunk = raw_sock.recv(4096)
                if not chunk:
                    break
                chunks.append(chunk)
        raw = b"".join(chunks)
        self.assertTrue(raw.startswith(b"HTTP/1.0 405"))
        self.assertEqual(raw.split(b"\r\n\r\n", 1)[1], b"")

    def test_oversize_body_is_413(self):
        big = json.dumps({"question": "x" * 70000}).encode()
        req = urllib.request.Request(
            f"http://127.0.0.1:{self.port}/api/chat",
            data=big,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req)
        self.assertEqual(ctx.exception.code, 413)
        self.assertEqual(json.loads(ctx.exception.read()), {"error": "bad_request"})
        self.assertEqual(ctx.exception.headers["Cache-Control"], "no-store")

    def test_negative_content_length_is_400(self):
        status, out = self.post(b'{"question": "x"}', headers={"Content-Length": "-1"})
        self.assertEqual((status, out), (400, {"error": "bad_request"}))

    def test_unhandled_service_error_is_503(self):
        with mock.patch.object(chat.service, "handle", side_effect=RuntimeError("boom")):
            req = urllib.request.Request(
                f"http://127.0.0.1:{self.port}/api/chat",
                data=json.dumps({"question": "q"}).encode(),
                method="POST",
                headers={"Content-Type": "application/json"},
            )
            with self.assertRaises(urllib.error.HTTPError) as ctx:
                urllib.request.urlopen(req)
        self.assertEqual(ctx.exception.code, 503)
        self.assertEqual(json.loads(ctx.exception.read()), {"error": "unavailable"})
        self.assertEqual(ctx.exception.headers["Cache-Control"], "no-store")

    def test_response_is_json_and_not_cached(self):
        with mock.patch.object(service.corpus, "load", lambda env: ("corpus", {"/"})), \
             mock.patch.object(service.gemini, "ask_model",
                               lambda system, contents, *, models, call=None: gemini.ModelReply(text='{"answer":"a","sources":[]}', model="m", blocked_reason=None)):
            req = urllib.request.Request(f"http://127.0.0.1:{self.port}/api/chat",
                                         data=json.dumps({"question": "q"}).encode(), method="POST",
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req) as resp:
                self.assertEqual(resp.headers["Content-Type"], "application/json; charset=utf-8")
                self.assertEqual(resp.headers["Cache-Control"], "no-store")


if __name__ == "__main__":
    unittest.main()
