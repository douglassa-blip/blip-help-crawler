from pathlib import Path

from src.pipelines.export_full import run_full_export


def test_full_export_generates_expected_outputs(tmp_path: Path):
    raw_articles = [
        {
            "id": 1,
            "title": "A",
            "locale": "pt-br",
            "body": "<p>A</p>",
            "url": "https://help.blip.ai/a",
        },
        {
            "id": 1,
            "title": "A duplicated",
            "locale": "pt-br",
            "body": "<p>A</p>",
            "url": "https://help.blip.ai/a",
        },
    ]

    manifest = run_full_export(raw_articles, output_root=tmp_path, source_used="api")

    assert manifest["deduped"] == 1
    assert (tmp_path / "exports" / "articles.jsonl").exists()
    assert (tmp_path / "exports" / "articles.csv").exists()
    assert (tmp_path / "exports" / "manifest.json").exists()
