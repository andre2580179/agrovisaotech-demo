"""
AgrovisãoTech - Versão Simplificada para Deploy
Sistema de Monitoramento Agrícola em arquivo único
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import io
import base64

# Configuração da página
st.set_page_config(
    page_title="AgrovisãoTech - Monitoramento Agrícola",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #2E7D32 0%, #4CAF50 50%, #66BB6A 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .main-header h1 {
        color: white;
        text-align: center;
        margin: 0;
        font-size: 2.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #2E7D32;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .alert-card {
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #ffc107;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .success-card {
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid #28a745;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .status-excellent { color: #2E7D32; font-weight: bold; font-size: 1.1em; }
    .status-good { color: #66BB6A; font-weight: bold; font-size: 1.1em; }
    .status-regular { color: #FF9800; font-weight: bold; font-size: 1.1em; }
    .status-critical { color: #F44336; font-weight: bold; font-size: 1.1em; }
</style>
""", unsafe_allow_html=True)

# Função para gerar dados de exemplo
@st.cache_data
def generate_sample_data():
    """Gera dados de exemplo para demonstração"""
    
    fazendas = [
        {
            "id": "fazenda_001",
            "nome": "Fazenda São João",
            "area": 520.5,
            "cultura": "Soja",
            "coordenadas": [-15.7801, -47.9292],
            "ndvi_medio": 0.78,
            "status": "Excelente",
            "ultima_analise": "2024-01-15",
            "proprietario": "João Silva",
            "variedade": "Soja BRS 360"
        },
        {
            "id": "fazenda_002", 
            "nome": "Sítio Esperança",
            "area": 280.3,
            "cultura": "Milho",
            "coordenadas": [-15.7901, -47.9392],
            "ndvi_medio": 0.65,
            "status": "Muito Boa",
            "ultima_analise": "2024-01-14",
            "proprietario": "Maria Santos",
            "variedade": "Milho AG 7098"
        },
        {
            "id": "fazenda_003",
            "nome": "Fazenda Vista Verde",
            "area": 750.0,
            "cultura": "Soja",
            "coordenadas": [-15.7701, -47.9192],
            "ndvi_medio": 0.42,
            "status": "Regular",
            "ultima_analise": "2024-01-13",
            "proprietario": "Carlos Oliveira",
            "variedade": "Soja TMG 7262"
        },
        {
            "id": "fazenda_004",
            "nome": "Agro Futuro",
            "area": 1200.0,
            "cultura": "Milho",
            "coordenadas": [-15.7601, -47.9092],
            "ndvi_medio": 0.25,
            "status": "Crítica",
            "ultima_analise": "2024-01-12",
            "proprietario": "José Ferreira",
            "variedade": "Milho DKB 390"
        }
    ]
    
    # Dados históricos de NDVI
    dates = pd.date_range(start='2024-01-01', end='2024-01-15', freq='D')
    ndvi_data = []
    
    for fazenda in fazendas:
        base_ndvi = fazenda["ndvi_medio"]
        for i, date in enumerate(dates):
            seasonal_effect = 0.1 * np.sin(2 * np.pi * i / len(dates))
            random_variation = np.random.normal(0, 0.03)
            ndvi_value = max(0, min(1, base_ndvi + seasonal_effect + random_variation))
            
            ndvi_data.append({
                "fazenda": fazenda["nome"],
                "data": date,
                "ndvi": ndvi_value,
                "area": fazenda["area"],
                "cultura": fazenda["cultura"],
                "temperatura": np.random.uniform(20, 35),
                "umidade": np.random.uniform(40, 80),
                "precipitacao": np.random.exponential(2) if np.random.random() > 0.7 else 0
            })
    
    return fazendas, pd.DataFrame(ndvi_data)

# Função para criar imagem NDVI simulada
def create_ndvi_sample():
    """Cria amostra visual de NDVI"""
    
    # Gerar dados simulados
    red_band = np.random.randint(40, 100, (50, 50), dtype=np.uint8)
    nir_band = np.random.randint(150, 220, (50, 50), dtype=np.uint8)
    
    # Adicionar área com problema
    red_band[20:35, 20:35] = np.random.randint(100, 140, (15, 15))
    nir_band[20:35, 20:35] = np.random.randint(80, 120, (15, 15))
    
    # Calcular NDVI
    ndvi = (nir_band.astype(float) - red_band.astype(float)) / (nir_band.astype(float) + red_band.astype(float))
    ndvi = np.clip(ndvi, -1, 1)
    
    # Criar visualização
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # Banda Vermelha
    im1 = axes[0].imshow(red_band, cmap='Reds', vmin=0, vmax=255)
    axes[0].set_title('Banda Vermelha (Red)', fontweight='bold')
    axes[0].axis('off')
    plt.colorbar(im1, ax=axes[0], fraction=0.046)
    
    # Banda NIR
    im2 = axes[1].imshow(nir_band, cmap='Greens', vmin=0, vmax=255)
    axes[1].set_title('Banda Infravermelho (NIR)', fontweight='bold')
    axes[1].axis('off')
    plt.colorbar(im2, ax=axes[1], fraction=0.046)
    
    # NDVI
    im3 = axes[2].imshow(ndvi, cmap='RdYlGn', vmin=-1, vmax=1)
    axes[2].set_title('NDVI Calculado', fontweight='bold')
    axes[2].axis('off')
    plt.colorbar(im3, ax=axes[2], fraction=0.046)
    
    plt.suptitle('AgrovisãoTech - Análise Multiespectral', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    # Converter para exibição no Streamlit
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
    img_buffer.seek(0)
    plt.close()
    
    return img_buffer, ndvi

def show_dashboard(fazendas, ndvi_df):
    """Exibe dashboard principal"""
    st.header("📊 Dashboard Executivo - AgrovisãoTech")
    
    # Métricas principais
    col1, col2, col3, col4, col5 = st.columns(5)
    
    total_fazendas = len(fazendas)
    total_area = sum(f["area"] for f in fazendas)
    ndvi_medio_geral = np.mean([f["ndvi_medio"] for f in fazendas])
    fazendas_criticas = len([f for f in fazendas if f["status"] in ["Regular", "Crítica"]])
    producao_estimada = total_area * 3.2
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #2E7D32; margin: 0;">🏭 Propriedades</h3>
            <h2 style="margin: 5px 0;">{total_fazendas}</h2>
            <p style="color: #666; margin: 0;">Fazendas monitoradas</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #2E7D32; margin: 0;">📏 Área Total</h3>
            <h2 style="margin: 5px 0;">{total_area:.0f} ha</h2>
            <p style="color: #666; margin: 0;">Hectares monitorados</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #2E7D32; margin: 0;">🌿 NDVI Médio</h3>
            <h2 style="margin: 5px 0;">{ndvi_medio_geral:.2f}</h2>
            <p style="color: #666; margin: 0;">Índice de saúde</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        alert_color = "#F44336" if fazendas_criticas > 0 else "#2E7D32"
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: {alert_color}; margin: 0;">⚠️ Alertas</h3>
            <h2 style="margin: 5px 0; color: {alert_color};">{fazendas_criticas}</h2>
            <p style="color: #666; margin: 0;">Áreas com atenção</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #2E7D32; margin: 0;">📈 Produção Est.</h3>
            <h2 style="margin: 5px 0;">{producao_estimada:.0f} t</h2>
            <p style="color: #666; margin: 0;">Toneladas estimadas</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        # Status das fazendas
        status_counts = {}
        for fazenda in fazendas:
            status = fazenda["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        fig_pie = px.pie(
            values=list(status_counts.values()),
            names=list(status_counts.keys()),
            title="📊 Distribuição de Status das Propriedades",
            color_discrete_map={
                "Excelente": "#2E7D32",
                "Muito Boa": "#66BB6A",
                "Regular": "#FF9800",
                "Crítica": "#F44336"
            }
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # NDVI por fazenda
        fazenda_names = [f["nome"] for f in fazendas]
        ndvi_values = [f["ndvi_medio"] for f in fazendas]
        colors = []
        for ndvi in ndvi_values:
            if ndvi >= 0.7: colors.append("#2E7D32")
            elif ndvi >= 0.5: colors.append("#66BB6A")
            elif ndvi >= 0.3: colors.append("#FF9800")
            else: colors.append("#F44336")
        
        fig_bar = go.Figure(data=[
            go.Bar(x=fazenda_names, y=ndvi_values, marker_color=colors)
        ])
        fig_bar.update_layout(
            title="🌿 NDVI Médio por Propriedade",
            xaxis_title="Propriedades",
            yaxis_title="NDVI",
            yaxis=dict(range=[0, 1])
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Evolução temporal
    st.subheader("📈 Evolução Temporal do NDVI")
    fig_timeline = px.line(
        ndvi_df, 
        x='data', 
        y='ndvi',
        color='fazenda',
        title="Monitoramento Contínuo - Últimos 15 dias"
    )
    st.plotly_chart(fig_timeline, use_container_width=True)

def show_ndvi_analysis():
    """Exibe análise visual do NDVI"""
    st.header("🔬 Análise Visual NDVI")
    st.markdown("### Comparativo: Imagens Multiespectrais ↔️ Interpretação")
    
    # Gerar imagem NDVI
    img_buffer, ndvi = create_ndvi_sample()
    
    # Exibir imagem
    st.image(img_buffer, use_column_width=True)
    
    # Interpretação
    col1, col2 = st.columns(2)
    
    with col1:
        ndvi_mean = np.mean(ndvi)
        ndvi_std = np.std(ndvi)
        
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; border: 1px solid #dee2e6;">
            <h4 style="color: #2E7D32;">📊 Análise Técnica</h4>
            <p><strong>NDVI Médio:</strong> {ndvi_mean:.3f}</p>
            <p><strong>Desvio Padrão:</strong> {ndvi_std:.3f}</p>
            <p><strong>Mínimo:</strong> {np.min(ndvi):.3f}</p>
            <p><strong>Máximo:</strong> {np.max(ndvi):.3f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if ndvi_mean >= 0.7:
            status = "Excelente"
            color = "#2E7D32"
            recommendations = ["✅ Manter práticas atuais", "📊 Monitorar continuamente"]
        elif ndvi_mean >= 0.5:
            status = "Boa"
            color = "#66BB6A"
            recommendations = ["💧 Manter irrigação", "🌱 Monitorar crescimento"]
        elif ndvi_mean >= 0.3:
            status = "Regular"
            color = "#FF9800"
            recommendations = ["💧 Verificar irrigação", "🧪 Analisar solo"]
        else:
            status = "Crítica"
            color = "#F44336"
            recommendations = ["🚨 Intervenção imediata", "🔬 Análise completa"]
        
        st.markdown(f"""
        <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; border: 1px solid #dee2e6;">
            <h4 style="color: #2E7D32;">💡 Interpretação</h4>
            <p><strong>Status:</strong> <span style="color: {color};">{status}</span></p>
            <p><strong>Recomendações:</strong></p>
        </div>
        """, unsafe_allow_html=True)
        
        for rec in recommendations:
            st.write(f"- {rec}")

def show_alerts(fazendas):
    """Exibe sistema de alertas"""
    st.header("🚨 Central de Alertas")
    
    # Categorizar alertas
    alertas_criticos = []
    alertas_atencao = []
    alertas_info = []
    
    for fazenda in fazendas:
        if fazenda["status"] == "Crítica":
            alertas_criticos.append(fazenda)
        elif fazenda["status"] == "Regular":
            alertas_atencao.append(fazenda)
        else:
            alertas_info.append(fazenda)
    
    # Alertas críticos
    if alertas_criticos:
        st.markdown("### 🚨 Alertas Críticos")
        for fazenda in alertas_criticos:
            st.markdown(f"""
            <div class="alert-card" style="border-left-color: #F44336;">
                <h4 style="color: #F44336; margin: 0;">⚠️ {fazenda['nome']}</h4>
                <p><strong>Problema:</strong> NDVI crítico ({fazenda['ndvi_medio']:.2f})</p>
                <p><strong>Ação:</strong> Intervenção imediata necessária</p>
                <p><strong>Proprietário:</strong> {fazenda['proprietario']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Alertas de atenção
    if alertas_atencao:
        st.markdown("### ⚠️ Alertas de Atenção")
        for fazenda in alertas_atencao:
            st.markdown(f"""
            <div class="alert-card">
                <h4 style="color: #FF9800; margin: 0;">⚡ {fazenda['nome']}</h4>
                <p><strong>Problema:</strong> NDVI abaixo do ideal ({fazenda['ndvi_medio']:.2f})</p>
                <p><strong>Ação:</strong> Monitoramento intensivo</p>
                <p><strong>Proprietário:</strong> {fazenda['proprietario']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Status normal
    if alertas_info:
        st.markdown("### ✅ Status Normal")
        for fazenda in alertas_info:
            st.markdown(f"""
            <div class="success-card">
                <h4 style="color: #2E7D32; margin: 0;">✅ {fazenda['nome']}</h4>
                <p><strong>Status:</strong> Condições adequadas</p>
                <p><strong>NDVI:</strong> {fazenda['ndvi_medio']:.2f}</p>
                <p><strong>Proprietário:</strong> {fazenda['proprietario']}</p>
            </div>
            """, unsafe_allow_html=True)

def show_drone_specs():
    """Exibe especificações dos drones"""
    st.header("🛰️ Especificações dos Drones")
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%); padding: 2rem; border-radius: 15px; margin: 2rem 0;">
        <h3>🚁 Drones Multiespectrais AgrovisãoTech</h3>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 2rem; margin: 2rem 0;">
            <div>
                <h4>📷 Sensores</h4>
                <ul>
                    <li><strong>Câmera RGB:</strong> 20MP</li>
                    <li><strong>Sensor Multiespectral:</strong> 5 bandas</li>
                    <li><strong>Banda Vermelha:</strong> 668nm ±10nm</li>
                    <li><strong>Banda NIR:</strong> 840nm ±20nm</li>
                    <li><strong>Resolução:</strong> 5cm/pixel</li>
                </ul>
            </div>
            
            <div>
                <h4>✈️ Especificações de Voo</h4>
                <ul>
                    <li><strong>Altitude Operacional:</strong> 120m AGL</li>
                    <li><strong>Velocidade:</strong> 8 m/s</li>
                    <li><strong>Autonomia:</strong> 30 minutos</li>
                    <li><strong>Cobertura:</strong> 200 ha/voo</li>
                    <li><strong>Precisão GPS:</strong> ±2cm</li>
                </ul>
            </div>
            
            <div>
                <h4>📊 Processamento</h4>
                <ul>
                    <li><strong>Software:</strong> IA Customizada</li>
                    <li><strong>Tempo:</strong> 2-4 horas</li>
                    <li><strong>Índices:</strong> NDVI, NDRE, GNDVI</li>
                    <li><strong>Formato:</strong> GeoTIFF, Shapefile</li>
                    <li><strong>Precisão NDVI:</strong> ±0.05</li>
                </ul>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Função principal do aplicativo"""
    
    # Header com logo
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <h1 style="color: #2E7D32; font-size: 3rem; margin: 0;">
            🌱 AgrovisãoTech
        </h1>
        <h3 style="color: #666; margin: 0;">
            Inteligência Artificial para o Agronegócio
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="main-header">
        <h1>Sistema de Monitoramento Agrícola</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Gerar dados
    fazendas, ndvi_df = generate_sample_data()
    
    # Sidebar
    st.sidebar.title("🎛️ Painel de Controle AgrovisãoTech")
    st.sidebar.markdown("---")
    
    menu_options = [
        "🏠 Dashboard Executivo",
        "🔬 Análise NDVI Visual",
        "🚨 Central de Alertas",
        "🛰️ Especificações Drones"
    ]
    
    selected_menu = st.sidebar.selectbox("Navegação:", menu_options)
    
    # Filtros
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔍 Filtros")
    
    fazenda_selecionada = st.sidebar.selectbox(
        "Propriedade:",
        ["Todas"] + [f["nome"] for f in fazendas]
    )
    
    cultura_selecionada = st.sidebar.selectbox(
        "Cultura:", 
        ["Todas", "Soja", "Milho"]
    )
    
    # Informações do sistema
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### 📊 Sistema AgrovisãoTech
    - **4 propriedades** monitoradas
    - **2.750 hectares** totais
    - **IA proprietária** para NDVI
    - **Alertas automáticos**
    - **Interface profissional**
    
    ### 🎯 Meta Comercial
    - 30-50 clientes iniciais
    - 9.000 hectares mapeados
    - Cases de sucesso validados
    """)
    
    # Renderizar conteúdo baseado na seleção
    if selected_menu == "🏠 Dashboard Executivo":
        show_dashboard(fazendas, ndvi_df)
    elif selected_menu == "🔬 Análise NDVI Visual":
        show_ndvi_analysis()
    elif selected_menu == "🚨 Central de Alertas":
        show_alerts(fazendas)
    elif selected_menu == "🛰️ Especificações Drones":
        show_drone_specs()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p><strong>AgrovisãoTech</strong> - Sistema de Monitoramento Agrícola</p>
        <p>🤖 Desenvolvido com Memex AI | 🌱 Inteligência Artificial para o Agronegócio</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()