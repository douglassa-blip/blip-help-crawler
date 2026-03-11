from src.transformers.chunking import chunk_text


def test_chunking_uses_800_chars_default():
    text = "a" * 1700
    chunks = list(chunk_text(text))
    assert len(chunks) == 3
    assert len(chunks[0]) == 800
    assert len(chunks[1]) == 800
    assert len(chunks[2]) == 100
