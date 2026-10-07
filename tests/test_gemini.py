import os
import unittest
from unittest import mock

from _ask import gemini, prompt


def ok(text):
    def call(model, system, contents):
        return gemini.ModelReply(text=text, model=model, blocked_reason=None)
    return call


class AskModelTest(unittest.TestCase):
    MODELS = ("primary", "fallback")

    def test_primary_answer_is_returned(self):
        reply = gemini.ask_model("sys", [], models=self.MODELS, call=ok('{"answer":"a","sources":[]}'))
        self.assertEqual(reply.model, "primary")
        self.assertEqual(reply.text, '{"answer":"a","sources":[]}')

    def test_vendor_error_falls_back_once(self):
        calls = []

        def call(model, system, contents):
            calls.append(model)
            if model == "primary":
                raise gemini.VendorError("503")
            return gemini.ModelReply(text="ok", model=model, blocked_reason=None)

        reply = gemini.ask_model("sys", [], models=self.MODELS, call=call)
        self.assertEqual(calls, ["primary", "fallback"])
        self.assertEqual(reply.model, "fallback")

    def test_both_fail_raises_vendor_error(self):
        def call(model, system, contents):
            raise gemini.VendorError("down")

        with self.assertRaises(gemini.VendorError):
            gemini.ask_model("sys", [], models=self.MODELS, call=call)

    def test_own_bug_is_not_retried(self):
        calls = []

        def call(model, system, contents):
            calls.append(model)
            raise KeyError("bug")

        with self.assertRaises(KeyError):
            gemini.ask_model("sys", [], models=self.MODELS, call=call)
        self.assertEqual(calls, ["primary"])

    def test_blocked_reply_is_not_retried(self):
        calls = []

        def call(model, system, contents):
            calls.append(model)
            return gemini.ModelReply(text=None, model=model, blocked_reason="SAFETY")

        reply = gemini.ask_model("sys", [], models=self.MODELS, call=call)
        self.assertEqual(calls, ["primary"])
        self.assertIsNone(reply.text)
        self.assertEqual(reply.blocked_reason, "SAFETY")


class CallGeminiTest(unittest.TestCase):
    def test_missing_key_raises_missing_key(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(gemini.MissingKey):
                gemini.call_gemini("m", "sys", [])

    def test_sdk_error_becomes_vendor_error(self):
        class FakeModels:
            def generate_content(self, **kwargs):
                from google.genai import errors
                raise errors.APIError(503, {"error": {"message": "busy"}})

        class FakeClient:
            def __init__(self, api_key):
                self.models = FakeModels()

        with mock.patch.dict(os.environ, {"GEMINI_API_KEY": "k"}):
            with mock.patch.object(gemini, "_client_factory", FakeClient):
                with self.assertRaises(gemini.VendorError):
                    gemini.call_gemini("m", "sys", [{"role": "user", "text": "q"}])

    def test_empty_text_reports_block_reason(self):
        class Feedback:
            block_reason = "SAFETY"

        class Candidate:
            finish_reason = "SAFETY"

        class Resp:
            text = None
            prompt_feedback = Feedback()
            candidates = [Candidate()]

        class FakeModels:
            def generate_content(self, **kwargs):
                return Resp()

        class FakeClient:
            def __init__(self, api_key):
                self.models = FakeModels()

        with mock.patch.dict(os.environ, {"GEMINI_API_KEY": "k"}):
            with mock.patch.object(gemini, "_client_factory", FakeClient):
                reply = gemini.call_gemini("m", "sys", [{"role": "user", "text": "q"}])
        self.assertIsNone(reply.text)
        self.assertIn("SAFETY", reply.blocked_reason)

    def test_request_carries_safety_json_mode_and_temperature(self):
        seen = {}

        class Resp:
            text = '{"answer":"a","sources":[]}'
            prompt_feedback = None
            candidates = []

        class FakeModels:
            def generate_content(self, **kwargs):
                seen.update(kwargs)
                return Resp()

        class FakeClient:
            def __init__(self, api_key):
                self.models = FakeModels()

        with mock.patch.dict(os.environ, {"GEMINI_API_KEY": "k"}):
            with mock.patch.object(gemini, "_client_factory", FakeClient):
                gemini.call_gemini("m", "sys", [{"role": "user", "text": "q"}])
        config = seen["config"]
        self.assertEqual(seen["model"], "m")
        self.assertEqual(config.temperature, 0.2)
        self.assertEqual(config.response_mime_type, "application/json")
        self.assertEqual(len(config.safety_settings), 4)
        self.assertEqual(config.system_instruction, "sys")
        self.assertEqual(seen["contents"][0].role, "user")
        self.assertEqual(config.response_schema, prompt.RESPONSE_SCHEMA)
        self.assertEqual(config.http_options.timeout, 25000)


if __name__ == "__main__":
    unittest.main()
