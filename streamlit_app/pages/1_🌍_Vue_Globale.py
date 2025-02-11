# pages/1_🌍_Vue_Globale.py
import streamlit as st
from market_analyzer import MarketAnalyzer

def main():
    st.set_page_config(page_title="Vue Globale du Marché", layout="wide")
    st.title("🌍 Vue Globale du Marché")
    
    # Initialisation de l'analyseur
    analyzer = MarketAnalyzer()
    
    if analyzer.market_data is not None and not analyzer.market_data.empty:
        # Filtres dans la barre latérale
        st.sidebar.header("Filtres")
        
        # Filtre par secteur
        sectors = sorted(analyzer.market_data['Secteur'].unique())
        selected_sectors = st.sidebar.multiselect(
            "Secteurs",
            options=sectors,
            default=[]
        )
        
        # Filtre par pays
        countries = sorted(analyzer.market_data['Pays'].unique())
        selected_countries = st.sidebar.multiselect(
            "Pays",
            options=countries,
            default=[]
        )
        
        # Filtre par capitalisation
        min_cap = st.sidebar.number_input(
            "Capitalisation minimum (M€)",
            min_value=0,
            value=0
        )
        
        # Application des filtres
        filtered_data = analyzer.market_data.copy()
        
        if selected_sectors:
            filtered_data = filtered_data[filtered_data['Secteur'].isin(selected_sectors)]
        if selected_countries:
            filtered_data = filtered_data[filtered_data['Pays'].isin(selected_countries)]
        if min_cap > 0:
            filtered_data = filtered_data[filtered_data['Capitalisation_boursiere'] >= min_cap * 1_000_000]
        
        # Métriques principales
        metrics = analyzer.calculate_market_metrics()
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Nombre d'entreprises",
                f"{metrics['nb_companies']:,}"
            )
        with col2:
            st.metric(
                "Capitalisation totale",
                f"{metrics['total_market_cap']/1e9:.1f} Mrd€"
            )
        with col3:
            st.metric(
                "PER moyen",
                f"{metrics['avg_per']:.1f}"
            )
        with col4:
            st.metric(
                "Rendement moyen",
                f"{metrics['avg_yield']:.1f}%"
            )
        
        # Visualisations
        fig_treemap, fig_per, fig_returns = analyzer.create_market_overview(filtered_data)
        
        if fig_treemap:
            st.plotly_chart(fig_treemap, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if fig_per:
                st.plotly_chart(fig_per, use_container_width=True)
        with col2:
            if fig_returns:
                st.plotly_chart(fig_returns, use_container_width=True)
        
        # Tableau détaillé
        st.subheader("Détail des entreprises")
        st.dataframe(
            filtered_data[[
                'Ticker', 'Nom_complet', 'Secteur', 'Pays',
                'Prix_actuel', 'Capitalisation_boursiere',
                'PER_historique', 'Rendement_du_dividende',
                'Variation_52_semaines'
            ]].style.format({
                'Prix_actuel': '{:.2f} €',
                'Capitalisation_boursiere': '{:,.0f} €',
                'PER_historique': '{:.2f}',
                'Rendement_du_dividende': '{:.2f}%',
                'Variation_52_semaines': '{:+.2f}%'
            })
        )
    
    else:
        st.error("Aucune donnée n'a pu être chargée. Veuillez vérifier le fichier de données.")

if __name__ == "__main__":
    main()