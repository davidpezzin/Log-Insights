# Log Insights

Ferramenta de linha de comando para transformar logs JSON Lines em métricas úteis: volume por rota, taxa de erro e latência p95. Não usa bibliotecas externas e é apropriada para rodar em pipelines simples.

## Executar

```powershell
python log_insights.py data/sample.jsonl
python -m unittest discover -s tests -v
```

Cada linha do arquivo deve conter `path`, `status` e `duration_ms`. Linhas inválidas são contadas no relatório, mas não interrompem toda a análise.
