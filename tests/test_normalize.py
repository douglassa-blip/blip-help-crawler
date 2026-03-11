from src.transformers.normalize import normalize_article


def test_normalize_article_maps_fields():
    raw = {
        "id": 123,
        "title": "Hello",
        "locale": "pt-br",
        "section_id": 10,
        "category_id": 20,
        "author_id": 30,
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-01-02T10:00:00Z",
        "body": "<p>body</p>",
        "url": "https://help.blip.ai/hc/pt-br/articles/123",
        "draft": False,
    }

    article = normalize_article(raw)

    assert article.article_id == "123"
    assert article.locale == "pt-br"
    assert article.body_html == "<p>body</p>"
    assert str(article.source_url).startswith("https://help.blip.ai")
