import io
import pandas as pd
import streamlit as st
import plotly.express as px
from engine import analyze, action_plan

st.set_page_config(page_title='Smart DMAIC', page_icon='📊', layout='wide')
st.title('📊 Smart DMAIC')
st.caption('Diagnóstico de processos industriais • MVP 1.0 • Recomendações baseadas em regras')
with st.sidebar:
    st.header('Projeto')
    project = st.text_input('Nome do projeto', 'Diagnóstico do processo')
    sector = st.selectbox('Área', ['Produção','Qualidade','Logística','Manutenção','Almoxarifado','Expedição','Segurança','Outra'])
    st.info('Os dados são processados na sessão da aplicação. Evite enviar informações confidenciais a servidores não autorizados.')

uploaded = st.file_uploader('Importe dados (.csv ou .xlsx)', type=['csv','xlsx'])
if uploaded:
    try:
        if uploaded.name.lower().endswith('.csv'):
            raw = uploaded.getvalue()
            try: df = pd.read_csv(io.BytesIO(raw), sep=None, engine='python')
            except UnicodeDecodeError: df = pd.read_csv(io.BytesIO(raw), sep=None, engine='python', encoding='latin1')
        else:
            excel = pd.ExcelFile(uploaded)
            sheet = st.selectbox('Aba da planilha', excel.sheet_names)
            df = pd.read_excel(excel, sheet_name=sheet)
    except Exception as exc:
        st.error(f'Não foi possível ler o arquivo: {exc}')
        st.stop()
else:
    st.info('Sem arquivo? Use a amostra demonstrativa abaixo para experimentar.')
    sample = pd.DataFrame({'Data': pd.date_range('2026-10-01', periods=24).strftime('%d/%m/%Y'),
        'Área': ['Linha A','Linha B','Linha C']*8,
        'Tipo de ocorrência': ['Atraso','Retrabalho','Falha de máquina','Atraso','Atraso','Retrabalho']*4,
        'Tempo de parada (min)': [12,20,8,25,18,13,9,30,16,11,24,15,22,19,7,14,27,10,21,8,17,26,12,23]})
    st.download_button('Baixar CSV de exemplo', sample.to_csv(index=False).encode('utf-8-sig'), 'exemplo_smart_dmaic.csv', 'text/csv')
    df = sample

if df.empty or not len(df.columns):
    st.error('A tabela está vazia.')
    st.stop()
st.subheader('1. Definir e medir')
st.dataframe(df.head(15), use_container_width=True)
columns = df.columns.tolist()
metric = st.selectbox('Indicador numérico a analisar', columns, index=columns.index('Tempo de parada (min)') if 'Tempo de parada (min)' in columns else 0)
category = st.selectbox('Categoria para Pareto (opcional)', ['(Nenhuma)'] + columns, index=columns.index('Tipo de ocorrência')+1 if 'Tipo de ocorrência' in columns else 0)
date = st.selectbox('Coluna de data (opcional)', ['(Nenhuma)'] + columns, index=columns.index('Data')+1 if 'Data' in columns else 0)
direction = st.radio('Sentido desejado do indicador', ['Menor é melhor','Maior é melhor'], horizontal=True)
use_target = st.checkbox('Definir meta', value=True)
target = st.number_input('Meta por registro', value=15.0) if use_target else None
if st.button('🔎 Analisar processo', type='primary'):
    try:
        result = analyze(df, metric, None if category == '(Nenhuma)' else category,
                         None if date == '(Nenhuma)' else date, target, direction)
    except Exception as exc:
        st.error(f'Falha na análise: {exc}')
        st.stop()
    st.session_state['analysis'] = result
    st.session_state['config'] = (project, sector, metric)

if 'analysis' in st.session_state:
    r = st.session_state['analysis']
    st.subheader('2. Resultados e diagnóstico')
    a,b,c,d = st.columns(4)
    a.metric('Registros válidos', f'{r["count"]}')
    b.metric('Média', f'{r["mean"]:.2f}')
    c.metric('Desvio-padrão', f'{r["std"]:.2f}')
    d.metric('Dentro da meta', f'{r["target_rate"]:.1f}%' if r['target_rate'] is not None else 'Não definida')
    st.write('**Status:**', r['status'])
    if r['pareto'] is not None:
        counts = r['pareto'].rename_axis('Categoria').reset_index(name='Registros')
        st.plotly_chart(px.bar(counts, x='Categoria', y='Registros', title='Frequência por categoria (base para Pareto)'), use_container_width=True)
        st.caption('Frequência não equivale a impacto. Confirme criticidade e exposição antes de agir.')
    if r['trend'] is not None:
        trend = r['trend'].rename_axis('Data').reset_index(name='Média')
        st.plotly_chart(px.line(trend, x='Data', y='Média', markers=True, title='Evolução temporal'), use_container_width=True)
    st.subheader('3. Analisar e melhorar')
    for priority, title, reason, owner in r['recommendations']:
        with st.expander(f'{priority} | {title}', expanded=True):
            st.write(reason)
            st.caption(f'Responsável sugerido: {owner} | Hipótese/ação a validar')
    st.subheader('4. Controlar — plano de ação 5W2H')
    plan = action_plan(r['recommendations'])
    st.dataframe(plan, use_container_width=True, hide_index=True)
    st.download_button('⬇️ Exportar plano de ação (CSV)', plan.to_csv(index=False).encode('utf-8-sig'), 'plano_5w2h.csv', 'text/csv')
    report = f'# Smart DMAIC — {st.session_state["config"][0]}\n\nÁrea: {st.session_state["config"][1]}\n\nIndicador: {st.session_state["config"][2]}\n\nRegistros: {r["count"]}\nMédia: {r["mean"]:.2f}\nDesvio-padrão: {r["std"]:.2f}\nStatus: {r["status"]}\n\n## Recomendações\n' + '\n'.join(f'- [{p}] {t}: {why}' for p,t,why,_ in r['recommendations']) + '\n\n**Nota:** sugestões automáticas exigem validação técnica e acompanhamento de resultados.\n'
    st.download_button('⬇️ Exportar relatório (Markdown)', report, 'relatorio_dmaic.md', 'text/markdown')
    st.caption('MVP: sem login, banco de dados, IA generativa ou exportação PDF. Não substitui validação de engenharia.')
