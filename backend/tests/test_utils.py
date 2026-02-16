from utils import count_tokens


class TestCountTokens:
    def test_empty_string(self):
        assert count_tokens("") == 0

    def test_simple_text(self):
        tokens = count_tokens("Hello world")
        assert tokens > 0
        assert tokens < 10

    def test_longer_text(self):
        text = "This is a longer piece of text that should have more tokens than the simple example above."
        tokens = count_tokens(text)
        assert tokens > 10
