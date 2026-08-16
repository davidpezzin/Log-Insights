# Log-Insights
Ferramenta de linha de comando para transformar logs JSON Lines em métricas úteis: volume por rota, taxa de erro e latência p95. Não usa bibliotecas externas e é apropriada para rodar em pipelines simples.

## Uso

```bash
python3 /home/runner/work/Log-Insights/Log-Insights/log_insights.py /caminho/para/logs.jsonl
cat /caminho/para/logs.jsonl | python3 /home/runner/work/Log-Insights/Log-Insights/log_insights.py -
```
