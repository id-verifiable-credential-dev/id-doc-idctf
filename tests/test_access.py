import unittest

from _ask import access


class LimiterTest(unittest.TestCase):
    def test_allows_up_to_limit_then_blocks(self):
        lim = access.Limiter(limit=3, window=600)
        self.assertTrue(lim.allow("a", now=0))
        self.assertTrue(lim.allow("a", now=1))
        self.assertTrue(lim.allow("a", now=2))
        self.assertFalse(lim.allow("a", now=3))

    def test_keys_are_independent(self):
        lim = access.Limiter(limit=1, window=600)
        self.assertTrue(lim.allow("a", now=0))
        self.assertTrue(lim.allow("b", now=0))
        self.assertFalse(lim.allow("a", now=0))

    def test_window_slides(self):
        lim = access.Limiter(limit=1, window=10)
        self.assertTrue(lim.allow("a", now=0))
        self.assertFalse(lim.allow("a", now=9))
        self.assertTrue(lim.allow("a", now=10.5))

    def test_blocked_attempts_do_not_extend_window(self):
        lim = access.Limiter(limit=1, window=10)
        self.assertTrue(lim.allow("a", now=0))
        for t in range(1, 10):
            self.assertFalse(lim.allow("a", now=t))
        self.assertTrue(lim.allow("a", now=10.5))


class OriginTest(unittest.TestCase):
    def test_production_requires_matching_host(self):
        self.assertTrue(access.origin_allowed("https://idctf.example", "idctf.example", "production"))
        self.assertFalse(access.origin_allowed("https://evil.example", "idctf.example", "production"))

    def test_production_rejects_missing_origin(self):
        self.assertFalse(access.origin_allowed(None, "idctf.example", "production"))
        self.assertFalse(access.origin_allowed("", "idctf.example", "production"))

    def test_preview_behaves_like_production(self):
        self.assertFalse(access.origin_allowed("https://evil.example", "x.vercel.app", "preview"))
        self.assertTrue(access.origin_allowed("https://x.vercel.app", "x.vercel.app", "preview"))

    def test_scheme_must_be_https_in_production(self):
        self.assertFalse(access.origin_allowed("http://idctf.example", "idctf.example", "production"))

    def test_host_comparison_is_case_insensitive(self):
        self.assertTrue(access.origin_allowed("https://IDCTF.example", "idctf.example", "production"))

    def test_null_origin_is_rejected(self):
        self.assertFalse(access.origin_allowed("null", "idctf.example", "production"))

    def test_lookalike_subdomain_is_rejected(self):
        self.assertFalse(access.origin_allowed("https://idctf.example.evil.com", "idctf.example", "production"))

    def test_development_allows_localhost_and_missing(self):
        for vercel_env in (None, "development"):
            with self.subTest(vercel_env=vercel_env):
                self.assertTrue(access.origin_allowed("http://localhost:8000", "localhost:3000", vercel_env))
                self.assertTrue(access.origin_allowed("http://127.0.0.1:8000", "localhost:3000", vercel_env))
                self.assertTrue(access.origin_allowed(None, "localhost:3000", vercel_env))

    def test_development_still_rejects_foreign_origin(self):
        for vercel_env in (None, "development"):
            with self.subTest(vercel_env=vercel_env):
                self.assertFalse(access.origin_allowed("https://evil.example", "localhost:3000", vercel_env))


class ClientKeyTest(unittest.TestCase):
    def test_prefers_x_real_ip(self):
        self.assertEqual(access.client_key({"x-real-ip": "1.2.3.4", "x-forwarded-for": "9.9.9.9"}), "1.2.3.4")

    def test_falls_back_to_first_forwarded(self):
        self.assertEqual(access.client_key({"x-forwarded-for": "5.6.7.8, 10.0.0.1"}), "5.6.7.8")

    def test_unknown_when_absent(self):
        self.assertEqual(access.client_key({}), "unknown")

    def test_header_names_are_case_insensitive(self):
        self.assertEqual(access.client_key({"X-Real-IP": "1.2.3.4"}), "1.2.3.4")

    def test_non_ip_real_ip_is_unknown(self):
        self.assertEqual(access.client_key({"x-real-ip": "evil"}), "unknown")

    def test_non_ip_forwarded_does_not_fall_through_to_next_entry(self):
        self.assertEqual(access.client_key({"x-forwarded-for": "evil, 1.2.3.4"}), "unknown")

    def test_ipv6_address_is_accepted(self):
        self.assertEqual(access.client_key({"x-real-ip": "2001:db8::1"}), "2001:db8::1")

    def test_ipv6_zone_id_is_stripped(self):
        self.assertEqual(access.client_key({"x-real-ip": "2001:db8::1%eth0"}), "2001:db8::1")

    def test_ipv6_address_is_canonicalized(self):
        self.assertEqual(access.client_key({"x-real-ip": "2001:DB8:0::1"}), "2001:db8::1")


if __name__ == "__main__":
    unittest.main()
