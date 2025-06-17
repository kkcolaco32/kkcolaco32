import unittest
from agents.chatgpt_intent import chatgpt_interpret_intent

class TestChatGPTIntent(unittest.TestCase):

    def test_simple_url(self):
        state = {"input_url": "jiomart"}
        result = chatgpt_interpret_intent(state)
        self.assertIn("https://", result["input_url"])
        self.assertIn(result["scan_type"], ["full_crawl", "homepage_only"])

    def test_test_mode(self):
        state = {"input_url": "test"}
        result = chatgpt_interpret_intent(state)
        self.assertEqual(result["input_url"], "test")

if __name__ == '__main__':
    unittest.main()