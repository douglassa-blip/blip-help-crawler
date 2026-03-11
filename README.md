# blip-help-export

Pipeline em Python para exportar conteúdos públicos do `https://help.blip.ai` usando API do Zendesk como fonte primária e crawler HTTP/HTML como fallback.

## Funcionalidades

- Descoberta completa de artigos por paginação da API Zendesk.
- Coleta de metadados e conteúdo do artigo.
- Modo `full` e `incremental` por `updated_at`.
- Saídas em `data/raw`, `data/normalized`, `data/markdown` e `data/exports`.
- Export consolidado em `articles.jsonl`, `articles.csv` e `manifest.json`.
- Deduplicação por `id` e, secundariamente, por URL canônica.
- Workflow GitHub Actions com `workflow_dispatch` e inputs para execução manual.

## Estrutura

```text
src/
  clients/
    zendesk.py
    crawler.py
  pipelines/
    export_full.py
    export_incremental.py
  transformers/
    normalize.py
    markdown.py
    chunking.py
  utils/
    logging.py
    retries.py
    files.py
data/
  raw/
  normalized/
  markdown/
  exports/
.github/workflows/export-help-center.yml
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Configure variáveis/Secrets:

- `ZENDESK_SUBDOMAIN`
- `ZENDESK_EMAIL`
- `ZENDESK_API_TOKEN`

## Execução local

### Full

```bash
python -m src.main --mode full --source auto --locale pt-br
```

### Incremental

```bash
python -m src.main --mode incremental --source api --locale pt-br --updated-since 2024-01-01T00:00:00Z
```

## GitHub Actions

Workflow: `.github/workflows/export-help-center.yml`

Inputs disponíveis no `Run workflow`:

- `mode`: `full` ou `incremental`
- `source`: `api`, `crawler` ou `auto`
- `locale`
- `publish_artifacts`: `true/false`
- `updated_since` (usado no incremental)

## Testes

```bash
pytest
```
