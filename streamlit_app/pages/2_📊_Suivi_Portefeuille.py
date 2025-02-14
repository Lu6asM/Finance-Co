import streamlit as st
from datetime import datetime, timedelta
from portfolio_analyzer import PortfolioAnalyzer, add_technical_analysis
from portfolio_manager import PortfolioManager
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
    st.title("📊 Suivi du Portefeuille")
    
    tracker = PortfolioManager()
    portfolio = tracker.portfolio_data
    
    if portfolio.empty:
        st.error("Impossible de charger les données du portefeuille")
        return
    
    # Date de valorisation
    st.caption("Valorisation au 10/02/2024")
    
    # KPIs principaux
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

    with kpi1:
        valeur_totale = portfolio['valeur_position'].sum()
        variation = ((valeur_totale / tracker.INITIAL_INVESTMENT) - 1) * 100
        color = "success" if variation >= 0 else "error"
        getattr(st, color)(
            f"""
            **💰 Valeur Totale**
            ### {valeur_totale:,.0f}€
            {variation:+.2f}%
            """
        )

    with kpi2:
        beta_portfolio = portfolio['Bêta'].mean()
        getattr(st, "info")(
            f"""
            **📊 Beta**
            ### {beta_portfolio:.2f}
            Risque marché
            """
        )

    with kpi3:
        rendement_moyen = portfolio['Rendement du dividende'].mean()
        getattr(st, "warning")(
            f"""
            **💸 Rendement**
            ### {rendement_moyen:.2f}%
            Dividende moyen
            """
        )

    with kpi4:
        nb_positions = len(portfolio)
        getattr(st, "success")(
            f"""
            **🎯 Positions**
            ### {nb_positions}
            Entreprises
            """
        )

    with kpi5:
        pct_invested = (valeur_totale / tracker.INITIAL_INVESTMENT) * 100
        getattr(st, "info")(
            f"""
            **📈 Investissement**
            ### {pct_invested:.1f}%
            Capital utilisé
            """
        )

    # Onglets
    tab1, tab2, tab3 = st.tabs(["📈 Vue d'ensemble", "📊 Performance", "💫 Simulation"])
    
    with tab1:
        # Vue d'ensemble du portefeuille
        st.plotly_chart(tracker.create_portfolio_overview(), use_container_width=True)
        
        # Tableau détaillé des positions
        st.subheader("Détail des positions")
        st.dataframe(
            portfolio[[
                'Ticker', 'Nom complet', 'Secteur', 'Prix actuel', 
                'valeur_position', 'weight', 'Bêta', 'Rendement du dividende',
                'shares'
            ]].style.format({
                'Prix actuel': '{:.2f}€',
                'valeur_position': '{:,.2f}€',
                'weight': '{:.2%}',
                'Bêta': '{:.2f}',
                'Rendement du dividende': '{:.2f}%',
                'shares': '{:,.0f}'
            }).background_gradient(subset=['weight', 'valeur_position'], cmap='YlOrRd'),
            use_container_width=True,
            height=400
        )

    with tab2:
        # Positions avec statistiques
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🔝 Meilleures performances")
            best_perf = portfolio.nlargest(5, 'Variation 52 semaines')[
                ['Nom complet', 'Variation 52 semaines']
            ]
            for _, row in best_perf.iterrows():
                st.success(f"{row['Nom complet']}: +{row['Variation 52 semaines']:.1f}%")
        
        with col2:
            st.subheader("👎 Moins bonnes performances")
            worst_perf = portfolio.nsmallest(5, 'Variation 52 semaines')[
                ['Nom complet', 'Variation 52 semaines']
            ]
            for _, row in worst_perf.iterrows():
                st.error(f"{row['Nom complet']}: {row['Variation 52 semaines']:.1f}%")

    with tab3:
        # Date selector for historical view
        col1, col2 = st.columns([2, 1])
        with col1:
            date_invested = st.date_input(
                "Date d'investissement",
                value=datetime.now() - timedelta(days=365),
                max_value=datetime.now()
            )
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)  # Espacement
            if st.button("🔄 Actualiser la simulation", type="primary"):
                st.rerun()
        
        # Graphique de simulation
        tracker.get_current_values(date_invested)
        
        # KPIs de performance dans des colonnes égales avec du style
        st.markdown("""
        <style>
        .performance-metric {
            padding: 1rem;
            border-radius: 0.5rem;
            background: #f8f9fa;
            margin: 0.5rem 0;
            text-align: center;
        }
        .performance-metric h3 {
            margin: 0;
            color: #1f77b4;
        }
        .performance-metric p {
            margin: 0.5rem 0 0 0;
            font-size: 0.9rem;
            color: #666;
        }
        </style>
        """, unsafe_allow_html=True)

    render_footer()

if __name__ == "__main__":
    main()