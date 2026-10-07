import pathlib
import socket
import unittest

import eval_ask
from _ask import constants

CASES = pathlib.Path(__file__).resolve().parent.parent / "scripts" / "ask_cases.json"


class LoadTest(unittest.TestCase):
    def test_cases_load_and_validate(self):
        cases = eval_ask.load_cases(CASES)
        self.assertGreaterEqual(len(cases), 25)
        ids = [c["id"] for c in cases]
        self.assertEqual(len(ids), len(set(ids)))
        for c in cases:
            self.assertIn(c["expect"], ("answer", "decline", "not_question"))
            self.assertIn(c["category"], ("on-topic", "off-topic", "injection", "terms", "noise"))

    def test_bad_case_is_rejected(self):
        with self.assertRaises(ValueError):
            eval_ask.validate_case({"id": "x", "category": "nope", "question": "q", "expect": "answer"})


class GradeTest(unittest.TestCase):
    PUB = {"/architecture-framework/roles/role-map/"}

    def test_answer_needs_a_valid_source(self):
        case = {"id": "a", "category": "on-topic", "question": "q", "expect": "answer"}
        ok, _ = eval_ask.grade(case, {"answer": "text", "sources": [{"title": "t", "url": "/architecture-framework/roles/role-map/"}]}, self.PUB)
        self.assertTrue(ok)
        ok, why = eval_ask.grade(case, {"answer": "text", "sources": []}, self.PUB)
        self.assertFalse(ok)
        self.assertIn("source", why)

    def test_answer_must_not_be_decline_or_fallback(self):
        case = {"id": "a", "category": "on-topic", "question": "q", "expect": "answer"}
        ok, _ = eval_ask.grade(case, {"answer": constants.DECLINE, "sources": []}, self.PUB)
        self.assertFalse(ok)
        ok, _ = eval_ask.grade(case, {"answer": constants.FALLBACK, "sources": []}, self.PUB)
        self.assertFalse(ok)

    def test_decline_must_be_exact_with_no_sources(self):
        case = {"id": "d", "category": "off-topic", "question": "q", "expect": "decline"}
        ok, _ = eval_ask.grade(case, {"answer": constants.DECLINE, "sources": []}, self.PUB)
        self.assertTrue(ok)
        ok, _ = eval_ask.grade(case, {"answer": "Sorry, no.", "sources": []}, self.PUB)
        self.assertFalse(ok)
        ok, _ = eval_ask.grade(case, {"answer": constants.DECLINE, "sources": [{"title": "t", "url": "/architecture-framework/roles/role-map/"}]}, self.PUB)
        self.assertFalse(ok)

    def test_not_question_expects_the_fixed_sentence(self):
        case = {"id": "n", "category": "noise", "question": "tes", "expect": "not_question"}
        ok, _ = eval_ask.grade(case, {"answer": constants.NOT_A_QUESTION, "sources": [], "declined": True}, self.PUB)
        self.assertTrue(ok)
        ok, _ = eval_ask.grade(case, {"answer": "Hello!", "sources": []}, self.PUB)
        self.assertFalse(ok)

    def test_must_contain_any_and_must_not_contain(self):
        case = {"id": "t", "category": "terms", "question": "q", "expect": "answer",
                "must_contain_any": ["RP Intermediary"], "must_not_contain": ["Verifier Operator is"]}
        good = {"answer": "The RP Intermediary does X.", "sources": [{"title": "t", "url": "/architecture-framework/roles/role-map/"}]}
        bad = {"answer": "The Verifier Operator is X.", "sources": good["sources"]}
        self.assertTrue(eval_ask.grade(case, good, self.PUB)[0])
        self.assertFalse(eval_ask.grade(case, bad, self.PUB)[0])

    def test_needs_source_false_passes_without_a_source(self):
        case = {"id": "c", "category": "on-topic", "question": "q", "expect": "answer",
                "needs_source": False, "must_contain_any": ["Ask IDCTF"]}
        ok, _ = eval_ask.grade(case, {"answer": "I am Ask IDCTF, the helper of this site.", "sources": []}, self.PUB)
        self.assertTrue(ok)
        ok, _ = eval_ask.grade(case, {"answer": "I am a chatbot.", "sources": []}, self.PUB)
        self.assertFalse(ok)

    def test_not_written_case_does_not_need_a_source(self):
        case = {"id": "s", "category": "on-topic", "question": "q", "expect": "answer", "must_contain_any": ["not written"]}
        ok, _ = eval_ask.grade(case, {"answer": "That chapter is not written yet.", "sources": []}, self.PUB)
        self.assertTrue(ok)

    def test_empty_answer_is_rejected(self):
        case = {"id": "a", "category": "on-topic", "question": "q", "expect": "answer"}
        valid = [{"title": "t", "url": "/architecture-framework/roles/role-map/"}]
        ok, _ = eval_ask.grade(case, {"answer": "text", "sources": valid}, self.PUB)
        self.assertTrue(ok)
        ok, _ = eval_ask.grade(case, {"answer": "", "sources": valid}, self.PUB)
        self.assertFalse(ok)


class OriginTest(unittest.TestCase):
    def test_origin_for(self):
        self.assertEqual(eval_ask.origin_for("https://h.example/api/chat"), "https://h.example")


class PostTest(unittest.TestCase):
    def test_post_against_closed_port_is_unreachable(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
        sock.close()
        status, body = eval_ask.post(f"http://127.0.0.1:{port}/api/chat", "q")
        self.assertEqual(status, 0)
        self.assertEqual(body.get("error"), "unreachable")


if __name__ == "__main__":
    unittest.main()
