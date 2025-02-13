import streamlit as st
from datetime import datetime, timedelta
from portfolio_analyzer import PortfolioAnalyzer, add_technical_analysis
from portfolio_manager import PortfolioManager
from utils import add_news_ticker

def main():
    add_news_ticker()
    st.title("📊 Suivi du Portefeuille")
    
    tracker = PortfolioManager()
    portfolio = tracker.portfolio_data
    
    if portfolio.empty:
        st.error("Impossible de charger les données du portefeuille")
        return
    
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
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Vue d'ensemble", "💼 Positions", "📊 Performance", "📈 Graphiques"])
    
    with tab1:
        # Vue d'ensemble du portefeuille
        st.plotly_chart(tracker.create_portfolio_overview(), use_container_width=True)

    with tab2:
        # Détail des positions
        st.dataframe(
            portfolio[[
                'Ticker', 'Nom complet', 'Secteur', 'Prix actuel', 
                'valeur_position', 'weight', 'Bêta', 'Rendement du dividende'
            ]].style.format({
                'Prix actuel': '{:.2f}€',
                'valeur_position': '{:,.2f}€',
                'weight': '{:.2%}',
                'Bêta': '{:.2f}',
                'Rendement du dividende': '{:.2f}%'
            }).background_gradient(subset=['weight', 'valeur_position'], cmap='YlOrRd'),
            use_container_width=True,
            height=400
        )

    with tab3:
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

    with tab4:
        # Date selector for historical view
        date_invested = st.date_input(
            "Date d'investissement",
            value=datetime.now() - timedelta(days=365),
            max_value=datetime.now()
        )
        tracker.get_current_values(date_invested)

if __name__ == "__main__":
    main()