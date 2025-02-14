# pages/1_🌍_Vue_Globale.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
        /* Enlève le surlignage bleu par défaut */
        .stButton button:focus {
            outline: none;
            box-shadow: none;
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



def main():
    configure_page()
    add_news_ticker()
    st.title("🌍 Vue Globale du Marché")
    
    # Initialisation de l'analyseur
    analyzer = MarketAnalyzer()
    
    if analyzer.market_data is not None and not analyzer.market_data.empty:
        # Filtres dans la barre latérale
        with st.sidebar:
            st.header("Filtres")
            
            # Filtre par secteur
            sectors = sorted(analyzer.market_data['Secteur'].unique())
            selected_sectors = st.multiselect(
                "Secteurs",
                options=sectors,
                default=[]
            )
            
            # Filtre par pays
            countries = sorted(analyzer.market_data['Pays'].unique())
            selected_countries = st.multiselect(
                "Pays",
                options=countries,
                default=[]
            )
            
            # Filtre par capitalisation avec un slider
            max_cap = float(analyzer.market_data['Capitalisation_boursiere'].max())
            min_cap = float(analyzer.market_data['Capitalisation_boursiere'].min())
            cap_range = st.slider(
                "Capitalisation (M€)",
                min_value=int(min_cap/1e6),
                max_value=int(max_cap/1e6),
                value=(int(min_cap/1e6), int(max_cap/1e6))
            )
        
        # Application des filtres
        filtered_data = analyzer.market_data.copy()
        
        if selected_sectors:
            filtered_data = filtered_data[filtered_data['Secteur'].isin(selected_sectors)]
        if selected_countries:
            filtered_data = filtered_data[filtered_data['Pays'].isin(selected_countries)]
        if cap_range:
            filtered_data = filtered_data[
                (filtered_data['Capitalisation_boursiere'] >= cap_range[0] * 1e6) &
                (filtered_data['Capitalisation_boursiere'] <= cap_range[1] * 1e6)
            ]
        
        # Métriques principales en cards modernes
        metrics = analyzer.calculate_market_metrics(filtered_data)
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.info(
                f"""
                **🏢 Entreprises**
                ### {metrics['nb_companies']:,}
                sociétés analysées
                """
            )
        
        with col2:
            st.success(
                f"""
                **💰 Capitalisation**
                ### {metrics['total_market_cap']/1e9:.1f} Mrd€
                valeur totale
                """
            )
        
        with col3:
            st.warning(
                f"""
                **📊 PER Moyen**
                ### {metrics['avg_per']:.1f}
                valorisation
                """
            )
        
        with col4:
            color = "success" if metrics['avg_yield'] > 0 else "error"
            getattr(st, color)(
                f"""
                **💸 Rendement**
                ### {metrics['avg_yield']:.1f}%
                dividende moyen
                """
            )
        
        # Création des onglets pour une meilleure organisation
        tab1, tab2, tab3 = st.tabs(["📊 Vue d'ensemble", "📈 Analyses", "🔍 Détails"])
        
        with tab1:

            with st.expander("ℹ️ Comment interpréter le score ?"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("""
                    Le score affiché dans la cartographie est un indicateur composite (0-100) qui combine :
                    - **40%** : PER (Price Earnings Ratio)
                        - Un PER plus bas donne un meilleur score
                        - Reflète la valorisation de l'entreprise
                    - **60%** : Rendement du dividende
                        - Un rendement plus élevé donne un meilleur score
                        - Reflète la rémunération des actionnaires
                    
                    🎯 **Interprétation des couleurs :**
                    - 🔵 Bleu foncé : Score élevé (entreprise potentiellement intéressante)
                    - ⚪ Blanc : Score moyen
                    - 🔴 Rouge : Score faible
                    """)
                
                with col2:
                    st.plotly_chart(analyzer.create_sector_sunburst(), use_container_width=True)

            # Treemap amélioré
            fig_treemap = px.treemap(
                filtered_data,
                path=['Secteur', 'Industrie', 'Nom_complet'],
                values='Capitalisation_boursiere',
                color='Score',
                color_continuous_scale='RdYlBu',
                hover_data=['Ticker', 'Prix_actuel', 'PER_historique', 'Rendement_du_dividende'],
                title='Cartographie du Marché par Capitalisation'
            )
            
            fig_treemap.update_layout(height=600)
            st.plotly_chart(fig_treemap, use_container_width=True)
        
        with tab2:
            # Création d'un subplot avec 2 graphiques côte à côte
            fig = make_subplots(
                rows=1, cols=2,
                subplot_titles=('Distribution des PER par Secteur', 'Distribution des Rendements'),
                specs=[[{'type': 'box'}, {'type': 'violin'}]]
            )
            
            # Box plot des PER
            fig.add_trace(
                go.Box(
                    x=filtered_data['Secteur'],
                    y=filtered_data['PER_historique'],
                    name='PER',
                    showlegend=False
                ),
                row=1, col=1
            )
            
            # Violin plot des rendements
            fig.add_trace(
                go.Violin(
                    x=filtered_data['Secteur'],
                    y=filtered_data['Rendement_du_dividende'],
                    name='Rendement',
                    box_visible=True,
                    meanline_visible=True,
                    showlegend=False
                ),
                row=1, col=2
            )
            
            fig.update_layout(
                height=500,
                showlegend=False,
                title_text="Analyse des Distributions"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            # Tableau détaillé avec formatage amélioré
            st.subheader("Liste des Entreprises")
            
            display_cols = [
                'Ticker', 'Nom_complet', 'Secteur', 'Pays',
                'Prix_actuel', 'Capitalisation_boursiere',
                'PER_historique', 'Rendement_du_dividende',
                'Variation_52_semaines'
            ]
            
            st.dataframe(
                filtered_data[display_cols].style.format({
                    'Prix_actuel': '{:.2f} €',
                    'Capitalisation_boursiere': '{:,.0f} €',
                    'PER_historique': '{:.2f}',
                    'Rendement_du_dividende': '{:.2f}%',
                    'Variation_52_semaines': '{:+.2f}%'
                }).background_gradient(
                    subset=['Capitalisation_boursiere', 'Rendement_du_dividende'],
                    cmap='YlOrRd'
                ),
                height=400
            )
    
    else:
        st.error("Aucune donnée n'a pu être chargée. Veuillez vérifier le fichier de données.")

    render_footer()

if __name__ == "__main__":
    main()