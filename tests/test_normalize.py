from src.transformers.normalize import clean_html, normalize_article


def test_clean_html_removes_navigation_and_scripts():
    html = "<main><nav>menu</nav><h1>Titulo</h1><script>x</script><p>texto</p></main>"
    cleaned = clean_html(html)
    assert "menu" not in cleaned
    assert "<script" not in cleaned


def test_normalize_article_maps_required_fields():
    raw = {
        "article_id": "360012345678",
        "title": "Como configurar",
        "url": "https://help.blip.ai/hc/pt-br/articles/360012345678",
        "locale": "pt-br",
        "category": "Desk",
        "section": "Config",
        "updated_at": "2024-01-01T00:00:00Z",
        "html": "<article><h1>Como configurar</h1><p>Texto</p></article>",
    }
    article = normalize_article(raw)
    assert article.article_id == "360012345678"
    assert article.locale == "pt-br"
    assert "Texto" in article.content
