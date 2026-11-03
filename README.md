# Smart DMAIC — MVP 1.0

Aplicação web para análise inicial de processos industriais, baseada em regras transparentes de DMAIC.

## Instalação

Requer Python 3.10 ou superior.

```bash
pip install -r requirements.txt
streamlit run app.py
```

O terminal mostrará o endereço local (geralmente http://localhost:8501).

## Como usar

1. Abra o endereço local no navegador.
2. Carregue um CSV ou XLSX (ou use os dados de exemplo).
3. Escolha a coluna numérica do indicador, uma categoria opcional e uma coluna de data opcional.
4. Defina se menor ou maior é melhor e uma meta opcional.
5. Clique em **Analisar processo**.
6. Revise recomendações, gráficos e exporte o plano 5W2H.

## Limitações

- As sugestões são heurísticas, não conclusões causais nem IA generativa.
- Frequências por categoria não são automaticamente taxas de defeito ou impactos.
- O alvo é aplicado a cada registro, e o status da meta considera a média.
- O gráfico temporal usa médias por data e não é uma carta de controle estatístico.
- Não há autenticação, armazenamento persistente, integração com ERP nem PDF.
- Faça revisão humana e proteja dados corporativos antes de implantar.
