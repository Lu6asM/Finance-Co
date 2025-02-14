# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from market_analyzer import MarketAnalyzer
from utils import add_news_ticker, render_footer

def configure_page():
    st.set_page_config(
        page_title="Komorebi Investments",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Style CSS harmonisé pour toute l'application
    st.markdown("""
        <style>
        /* Style des cartes */
        .custom-card {
            background-color: #ffffff;
            padding: 1.5rem;
            border-radius: 0.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
            transition: transform 0.2s ease;
        }
        .custom-card:hover {
            transform: translateY(-2px);
        }
        
        /* Style des boutons Streamlit */
        .stButton button {
            width: 100%;
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            padding: 1rem 2rem;
            transition: all 0.2s ease;
        }
        .stButton button:hover {
            background-color: #e9ecef;
            transform: translateY(-2px);
        }
        
        /* Style des métriques */
        .metric-container {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
        }
        
        /* Style du ticker */
        .ticker-container {
            background-color: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(5px);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        /* Style des onglets */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 1rem 2rem;
        }
        </style>
    """, unsafe_allow_html=True)

def create_navigation_buttons():
    """Crée les boutons de navigation harmonisés avec descriptions précises"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
            <div class="custom-card">
                <h3>🌍 Vue Globale du Marché</h3>
                <p>Analyse complète de 55 valeurs internationales sélectionnées.</p>
                <ul>
                    <li>Cartographie interactive par secteur et capitalisation</li>
                    <li>Filtres dynamiques par pays et secteur d'activité</li>
                    <li>Analyse des PER et rendements par secteur</li>
                    <li>Score composite valorisation/rendement (0-100)</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Accéder à la vue globale", key="btn_vue_globale", use_container_width=True):
            st.switch_page("pages/1_🌍_Vue_Globale.py")
    
    with col2:
        st.markdown("""
            <div class="custom-card">
                <h3>📈 Suivi de Portefeuille</h3>
                <p>Gestion et simulation d'un portefeuille d'1M€.</p>
                <ul>
                    <li>Suivi en temps réel avec conversion multidevises</li>
                    <li>Répartition sectorielle et géographique interactive</li>
                    <li>Simulation de performance depuis une date donnée</li>
                    <li>Calcul de métriques de risque (beta, drawdown)</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Accéder au portefeuille", key="btn_portefeuille", use_container_width=True):
            st.switch_page("pages/2_📊_Suivi_Portefeuille.py")
    
    with col3:
        st.markdown("""
            <div class="custom-card">
                <h3>🏢 Analyse des Entreprises</h3>
                <p>Profils détaillés de chaque entreprise sélectionnée.</p>
                <ul>
                    <li>Business model et positionnement détaillé</li>
                    <li>Actualités en temps réel filtrées par pertinence</li>
                    <li>Graphiques de cours avec multiples timeframes</li>
                    <li>Métriques financières clés et valorisation</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)
        if st.button("Accéder aux entreprises", key="btn_entreprises", use_container_width=True):
            st.switch_page("pages/3_🏢_Analyse_Entreprises.py")

@st.cache_data(ttl=300)
def load_selected_stocks():
    try:
        return pd.read_csv('https://raw.githubusercontent.com/thidescac25/Finance-Co/refs/heads/main/data/stocks_data.csv')
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {str(e)}")
        return None

def create_market_summary(market_data):
    """Crée un aperçu du marché avec distributions des capitalisations par secteur"""
    fig = go.Figure()
    
    fig.add_trace(
        go.Box(
            x=market_data['Secteur'],
            y=market_data['Capitalisation_boursiere']/1e9,
            name='Distribution des capitalisations',
            boxpoints='outliers',
            marker_color='rgb(107,174,214)',
            line_width=1
        )
    )
    
    fig.update_layout(
        title={
            'text': "Distribution des capitalisations par secteur",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title="Secteur",
        yaxis_title="Capitalisation (Mrd€)",
        height=400,
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(
            family="Arial, sans-serif",
            size=12
        )
    )
    
    return fig

def main():
    configure_page()
    from utils import initialize_ticker_data
    initialize_ticker_data()
    
    # Bandeau d'actualités avec variations en temps réel
    add_news_ticker()
    
    # Titre principal
    st.title("📊 Komorebi Investments Dashboard")
    
    # Boutons de navigation
    create_navigation_buttons()
    
    # Séparateur
    st.markdown("---")
    
    analyzer = MarketAnalyzer()
    selected_stocks = load_selected_stocks()
    
    if analyzer.market_data is not None and selected_stocks is not None:
        tab0, tab1, tab2 = st.tabs([
            "🏠 Accueil",
            "🔍 Points marquants",
            "📊 Analyses détaillées"
        ])
        
        with tab0:
            st.markdown("""
                <div class="custom-card">
                    <h2>👋 Bienvenue dans Komorebi Investments</h2>
                    <p>Solution complète d'analyse et de suivi pour une sélection de 55 valeurs internationales avec un portefeuille virtuel d'1M€.</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 📱 Structure de l'Application")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                    <div class="custom-card">
                        <h3>🎯 Pages Principales</h3>
                        <h4>1. Vue Globale du Marché (🌍)</h4>
                        <ul>
                            <li>Cartographie interactive colorée par score composite</li>
                            <li>Filtres dynamiques par pays, secteur et capitalisation</li>
                            <li>Analyse comparative des PER et rendements</li>
                            <li>Classement détaillé des valeurs suivies</li>
                        </ul>
                        <h4>2. Suivi de Portefeuille (📊)</h4>
                        <ul>
                            <li>Gestion d'un portefeuille virtuel d'1M€</li>
                            <li>Conversion automatique en multi-devises</li>
                            <li>Métriques de risque détaillées (beta, volatilité)</li>
                            <li>Simulation de performance historique</li>
                        </ul>
                        <h4>3. Analyse des Entreprises (🏢)</h4>
                        <ul>
                            <li>Description détaillée des business models</li>
                            <li>Flux d'actualités filtré par pertinence</li>
                            <li>Analyses techniques sur plusieurs périodes</li>
                            <li>Métriques financières et valorisation</li>
                        </ul>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                    <div class="custom-card">
                        <h3>📊 Fonctionnalités Clés</h3>
                        <h4>📈 Analyse Marché</h4>
                        <ul>
                            <li>Score composite valorisation/rendement</li>
                            <li>Visualisation Treemap interactive</li>
                            <li>Analyse sectorielle comparative</li>
                            <li>Filtres multi-critères</li>
                        </ul>
                        <h4>🔍 Sélection des Valeurs</h4>
                        <ul>
                            <li>55 entreprises internationales</li>
                            <li>7 zones géographiques majeures</li>
                            <li>Multi-devises (EUR, USD, GBP, JPY, etc.)</li>
                            <li>Diversification sectorielle</li>
                        </ul>
                        <h4>📊 Analyses Approfondies</h4>
                        <ul>
                            <li>Business models détaillés</li>
                            <li>Actualités en temps réel</li>
                            <li>Graphiques techniques personnalisables</li>
                            <li>Métriques de valorisation</li>
                        </ul>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("""
                <div class="custom-card">
                    <h3>💡 Fonctionnalités & Utilisation</h3>
                    <ul>
                        <li><strong>Bandeau d'actualités :</strong> Variations en temps réel des 55 valeurs suivies avec mise à jour toutes les 5 minutes</li>
                        <li><strong>Navigation intuitive :</strong> Structure en trois sections principales avec navigation fluide entre les pages</li>
                        <li><strong>Filtres avancés :</strong> Personnalisation des analyses par secteur, pays, et capitalisation</li>
                        <li><strong>Interactivité :</strong> Graphiques dynamiques avec zoom, hover et sélection de périodes</li>
                        <li><strong>Multi-devises :</strong> Conversion automatique des valeurs en euros pour le portefeuille</li>
                        <li><strong>Actualités filtrées :</strong> Agrégation et filtrage intelligent des news des dernières 48h</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)
        
        with tab1:
            highlights = analyzer.get_market_highlights()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🔥 Top 5 Performances")
                st.dataframe(
                    highlights['best_performers'].style.format({
                        'Variation_52_semaines': '{:+.1f}%'
                    })
                )
                
                st.subheader("💰 Top 5 Dividendes")
                st.dataframe(
                    highlights['highest_dividends'].style.format({
                        'Rendement_du_dividende': '{:.2f}%'
                    })
                )
            
            with col2:
                st.subheader("❄️ Moins bonnes Performances")
                st.dataframe(
                    highlights['worst_performers'].style.format({
                        'Variation_52_semaines': '{:+.1f}%'
                    })
                )
                
                st.subheader("📊 Répartition sectorielle")
                st.dataframe(
                    highlights['sector_allocation'].to_frame('Poids').style.format({
                        'Poids': '{:.1f}%'
                    })
                )
        
        with tab2:
            analysis_type = st.selectbox(
                "Type d'analyse",
                ["Capitalisations", "Performance", "Valorisation"]
            )
            
            if analysis_type == "Capitalisations":
                st.info("ℹ️ Les capitalisations sont affichées en milliards d'euros pour plus de lisibilité")
                
                # Filtres pour les capitalisations
                cap_filter = st.slider(
                    "Filtrer par capitalisation (Mrd€)",
                    min_value=0.0,
                    max_value=100.0,
                    value=(0.0, 100.0),
                    step=5.0
                )
                
                filtered_data = analyzer.market_data[
                    (analyzer.market_data['Capitalisation_boursiere'] >= cap_filter[0] * 1e9) &
                    (analyzer.market_data['Capitalisation_boursiere'] <= cap_filter[1] * 1e9)
                ]
                
                # Distribution des capitalisations par secteur avec échelle log
                fig_box = go.Figure()
                for sector in sorted(filtered_data['Secteur'].unique()):
                    sector_data = filtered_data[filtered_data['Secteur'] == sector]
                    fig_box.add_trace(go.Box(
                        y=sector_data['Capitalisation_boursiere'] / 1e9,
                        name=sector,
                        boxpoints='outliers'
                    ))
                
                fig_box.update_layout(
                    title="Distribution des capitalisations par secteur",
                    yaxis_title="Capitalisation (Mrd€)",
                    height=500,
                    showlegend=False,
                    yaxis_type="log"
                )
                st.plotly_chart(fig_box, use_container_width=True)
                
                # Treemap avec échelle de couleur logarithmique
                fig_treemap = px.treemap(
                    filtered_data,
                    path=['Secteur', 'Industrie', 'Nom_complet'],
                    values='Capitalisation_boursiere',
                    color='Capitalisation_boursiere',
                    color_continuous_scale='Viridis',
                    color_continuous_midpoint=np.median(filtered_data['Capitalisation_boursiere']),
                    title='Répartition détaillée des capitalisations'
                )
                fig_treemap.update_layout(height=600)
                st.plotly_chart(fig_treemap, use_container_width=True)
                
            elif analysis_type == "Performance":
                st.info("ℹ️ Les performances extrêmes (>200% ou <-80%) sont exclues pour une meilleure lisibilité")
                
                # Filtrage des performances extrêmes
                perf_data = analyzer.market_data[
                    (analyzer.market_data['Variation_52_semaines'] > -0.8) &
                    (analyzer.market_data['Variation_52_semaines'] < 2.0)
                ]
                
                # Box plot des performances par secteur
                fig_perf_box = px.box(
                    perf_data,
                    x='Secteur',
                    y='Variation_52_semaines',
                    title='Distribution des performances par secteur',
                    points='outliers'
                )
                fig_perf_box.update_layout(
                    height=400,
                    yaxis_title="Variation sur 52 semaines (%)",
                    yaxis_tickformat='.0%'
                )
                st.plotly_chart(fig_perf_box, use_container_width=True)
                
                # Histogramme des performances
                fig_hist = px.histogram(
                    perf_data,
                    x='Variation_52_semaines',
                    nbins=50,
                    title='Distribution des performances',
                    color_discrete_sequence=['lightblue'],
                    marginal='box'
                )
                fig_hist.update_layout(
                    height=400,
                    xaxis_title="Variation sur 52 semaines (%)",
                    xaxis_tickformat='.0%'
                )
                st.plotly_chart(fig_hist, use_container_width=True)
                
                # Top/Flop performances
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("🔝 Top 10 Performances")
                    top_10 = perf_data.nlargest(10, 'Variation_52_semaines')[
                        ['Nom_complet', 'Variation_52_semaines', 'Secteur']
                    ]
                    st.dataframe(
                        top_10.style.format({
                            'Variation_52_semaines': '{:.1%}'
                        }).background_gradient(subset=['Variation_52_semaines'], cmap='RdYlGn')
                    )
                
                with col2:
                    st.subheader("👎 Flop 10 Performances")
                    bottom_10 = perf_data.nsmallest(10, 'Variation_52_semaines')[
                        ['Nom_complet', 'Variation_52_semaines', 'Secteur']
                    ]
                    st.dataframe(
                        bottom_10.style.format({
                            'Variation_52_semaines': '{:.1%}'
                        }).background_gradient(subset=['Variation_52_semaines'], cmap='RdYlGn')
                    )
                
            elif analysis_type == "Valorisation":
                st.info("ℹ️ Les PER extrêmes (>100) sont exclus pour une meilleure lisibilité")
                
                # Filtrage des valeurs extrêmes
                filtered_data = analyzer.market_data[
                    (analyzer.market_data['PER_historique'] > 0) &
                    (analyzer.market_data['PER_historique'] < 100)
                ]
                
                # Contrôles pour les filtres
                col1, col2 = st.columns(2)
                with col1:
                    per_range = st.slider(
                        "Filtre PER",
                        0.0,
                        100.0,
                        (0.0, 50.0),
                        step=5.0
                    )
                with col2:
                    div_range = st.slider(
                        "Filtre Rendement (%)",
                        0.0,
                        20.0,
                        (0.0, 10.0),
                        step=0.5
                    )
                
                filtered_data = filtered_data[
                    (filtered_data['PER_historique'] >= per_range[0]) &
                    (filtered_data['PER_historique'] <= per_range[1]) &
                    (filtered_data['Rendement_du_dividende'] >= div_range[0]/100) &
                    (filtered_data['Rendement_du_dividende'] <= div_range[1]/100)
                ]
                
                # Graphique de dispersion amélioré
                fig_scatter = px.scatter(
                    filtered_data,
                    x='PER_historique',
                    y='Rendement_du_dividende',
                    color='Secteur',
                    size='Capitalisation_boursiere',
                    hover_data=['Nom_complet', 'Prix_actuel'],
                    title='PER vs Rendement du dividende',
                    labels={
                        'PER_historique': 'PER',
                        'Rendement_du_dividende': 'Rendement (%)',
                        'Capitalisation_boursiere': 'Capitalisation (€)'
                    }
                )
                fig_scatter.update_traces(
                    marker=dict(sizeref=2.*max(filtered_data['Capitalisation_boursiere'])/
                              (40.**2)),
                    selector=dict(mode='markers')
                )
                fig_scatter.update_layout(
                    height=600,
                    yaxis_tickformat='.1%'
                )
                st.plotly_chart(fig_scatter, use_container_width=True)
                
                # Métriques de valorisation moyennes par secteur
                st.subheader("Métriques moyennes par secteur")
                sector_metrics = filtered_data.groupby('Secteur').agg({
                    'PER_historique': 'mean',
                    'Rendement_du_dividende': 'mean',
                    'Ratio_cours_valeur_comptable': 'mean',
                    'Capitalisation_boursiere': 'mean',
                    'Nombre_d_avis_analystes': 'mean'
                }).round(2)
                
                # Formater le DataFrame pour l'affichage
                sector_metrics_display = sector_metrics.copy()
                sector_metrics_display['Capitalisation_boursiere'] = sector_metrics_display['Capitalisation_boursiere'] / 1e9
                
                st.dataframe(
                    sector_metrics_display.style
                    .format({
                        'PER_historique': '{:.1f}',
                        'Rendement_du_dividende': '{:.1%}',
                        'Ratio_cours_valeur_comptable': '{:.1f}',
                        'Capitalisation_boursiere': '{:.1f} Mrd€',
                        'Nombre_d_avis_analystes': '{:.0f}'
                    })
                    .background_gradient(cmap='YlOrRd', subset=['PER_historique'])
                    .background_gradient(cmap='YlOrRd', subset=['Rendement_du_dividende'])
                    .background_gradient(cmap='YlOrRd', subset=['Capitalisation_boursiere'])
                )
                
                # Ajouter un graphique radar pour comparer les secteurs
                st.subheader("Comparaison multifactorielle par secteur")
                
                # Normaliser les données pour le graphique radar
                radar_metrics = sector_metrics.copy()
                for column in radar_metrics.columns:
                    if column != 'Nombre_d_avis_analystes':
                        max_val = radar_metrics[column].max()
                        min_val = radar_metrics[column].min()
                        radar_metrics[column] = (radar_metrics[column] - min_val) / (max_val - min_val)
                
                fig_radar = go.Figure()
                
                for sector in radar_metrics.index:
                    fig_radar.add_trace(go.Scatterpolar(
                        r=radar_metrics.loc[sector, ['PER_historique', 'Rendement_du_dividende', 'Ratio_cours_valeur_comptable']],
                        theta=['PER', 'Rendement', 'Price/Book'],
                        name=sector,
                        fill='toself'
                    ))
                
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 1]
                        )),
                    showlegend=True,
                    height=500,
                    title="Analyse multifactorielle par secteur"
                )
                
                st.plotly_chart(fig_radar, use_container_width=True)
        
        # Footer
        render_footer()

if __name__ == "__main__":
    main()