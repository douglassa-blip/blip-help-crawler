# blip-help-export

Exportador da base de conhecimento `https://help.blip.ai` com descoberta via sitemap e geração de dataset para IA/RAG.

## Pipeline

`sitemap.xml -> URLs -> filtro /articles/ -> download -> limpeza HTML -> normalização -> markdown -> dataset -> chunking`

Sitemap utilizado: `https://help.blip.ai/hc/sitemap.xml`

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Execução local

### Full

```bash
python src/pipelines/export_full.py --locale pt-br --output-root data
```

### Incremental

```bash
python src/pipelines/export_incremental.py --locale pt-br --output-root data
```

## Estrutura de saída

```text
data/
  raw/
    {article_id}.html
  normalized/
    {article_id}.json
  markdown/
    {article_id}.md
  exports/
    articles.jsonl
    articles.csv
    chunks.jsonl
    manifest.json
  state.json
```

## Incremental

No modo incremental, o timestamp da última execução é salvo em `data/state.json`.
Somente artigos com `updated_at > last_run` permanecem no dataset incremental.

## GitHub Actions

Workflow: `.github/workflows/export-help-center.yml`

Trigger manual (`workflow_dispatch`) com inputs:
- `mode` (`full` ou `incremental`)
- `locale` (ex.: `pt-br`)
- `publish_artifacts` (`true/false`)

Artifacts publicados:
- `data/exports/articles.jsonl`
- `data/exports/articles.csv`
- `data/exports/chunks.jsonl`
- `data/markdown/`
- `data/exports/manifest.json`
