"""Motor determinístico de diagnóstico Smart DMAIC v1."""
import pandas as pd
import numpy as np


def analyze(df, metric, category=None, date=None, target=None, direction='Menor é melhor'):
    data = df.copy()
    data[metric] = pd.to_numeric(data[metric], errors='coerce')
    valid = data.dropna(subset=[metric]).copy()
    if valid.empty:
        raise ValueError('Não há valores numéricos válidos na coluna selecionada.')
    values = valid[metric]
    avg = float(values.mean())
    median = float(values.median())
    std = float(values.std()) if len(values) > 1 else 0.0
    result = {'count': len(values), 'missing': int(data[metric].isna().sum()),
              'mean': avg, 'median': median, 'std': std,
              'min': float(values.min()), 'max': float(values.max()),
              'recommendations': [], 'pareto': None, 'trend': None,
              'target_rate': None, 'status': 'Sem meta definida'}
    recommendations = result['recommendations']
    if target is not None:
        target = float(target)
        bad = values > target if direction == 'Menor é melhor' else values < target
        result['target_rate'] = float((~bad).mean() * 100)
        result['status'] = 'Meta média atendida' if ((avg <= target) if direction == 'Menor é melhor' else (avg >= target)) else 'Meta média não atendida'
        if bad.any():
            recommendations.append(('Alta', 'Reduzir desvios em relação à meta', f'{int(bad.sum())} de {len(values)} registros fora da meta. Segmentar por turno, equipamento ou tipo de ocorrência e validar as causas no local.', 'Produção / Qualidade'))
    if std > 0 and abs(avg) > 1e-9 and std / abs(avg) > 0.25:
        recommendations.append(('Média', 'Investigar variação do processo', 'A dispersão relativa dos registros é elevada (CV acima de 25%). Estratificar por turno, máquina e lote; confirmar se a métrica admite esse indicador.', 'Engenharia de Processos'))
    if category and category in valid.columns:
        counts = valid[category].fillna('Não informado').astype(str).value_counts()
        result['pareto'] = counts
        if len(counts):
            top = counts.index[0]
            share = counts.iloc[0] / counts.sum() * 100
            if share >= 35:
                recommendations.append(('Alta', f'Priorizar categoria: {top}', f'Esta categoria representa {share:.1f}% dos registros. Verificar sua gravidade e seu impacto antes de priorizar ações corretivas.', 'Líder da Área'))
    if date and date in valid.columns:
        valid['_date'] = pd.to_datetime(valid[date], errors='coerce', dayfirst=True)
        valid = valid.dropna(subset=['_date']).sort_values('_date')
        if not valid.empty:
            trend = valid.groupby('_date')[metric].mean().sort_index()
            result['trend'] = trend
            if len(trend) >= 4:
                first, last = trend.iloc[0], trend.iloc[-1]
                worsened = (last > first) if direction == 'Menor é melhor' else (last < first)
                if worsened:
                    recommendations.append(('Média', 'Investigar evolução temporal desfavorável', 'O último período apresenta média pior que o primeiro. Verificar sazonalidade, composição da amostra e mudanças operacionais.', 'Engenharia de Processos'))
    if result['missing']:
        recommendations.append(('Média', 'Melhorar qualidade dos dados', f'{result["missing"]} registros sem valor numérico válido. Revisar coleta, preenchimento e padronização.', 'Responsável pelos Dados'))
    if not recommendations:
        recommendations.append(('Baixa', 'Manter monitoramento e padronização', 'Nenhum gatilho configurado foi acionado. Validar a adequação dos indicadores e manter acompanhamento periódico.', 'Líder da Área'))
    return result


def action_plan(recommendations):
    rows = []
    for priority, what, why, who in recommendations:
        rows.append({'Prioridade': priority, 'O quê': what, 'Por quê': why,
                     'Onde': 'Processo analisado', 'Quem (sugerido)': who,
                     'Quando': 'A definir', 'Como': 'Validar hipótese, testar ação e medir resultado',
                     'Quanto': 'A estimar', 'Status': 'Proposta — não validada'})
    return pd.DataFrame(rows)
