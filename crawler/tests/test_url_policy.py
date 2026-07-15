import unittest

from crawler.app import is_public_http_url


class UrlPolicyTests(unittest.TestCase):
    def test_rejects_non_public_urls(self) -> None:
        self.assertFalse(is_public_http_url("file:///etc/passwd"))
        self.assertFalse(is_public_http_url("http://127.0.0.1:8080"))
        self.assertFalse(is_public_http_url("http://localhost:8080"))


if __name__ == "__main__":
    unittest.main()
