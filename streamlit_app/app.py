# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from market_analyzer import MarketAnalyzer

# Configuration de la page
st.set_page_config(
    page_title="Finance Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fonction pour charger les données sélectionnées
def load_selected_stocks():
    try:
        return pd.read_csv('https://raw.githubusercontent.com/thidescac25/Finance-Co/refs/heads/main/data/stocks_data.csv')
    except Exception as e:
        st.error(f"Erreur lors du chargement des stocks sélectionnés : {str(e)}")
        return None

# Fonction pour créer un résumé rapide du marché
def create_market_summary(market_data):
    fig = go.Figure()
    
    # Distribution des capitalisations boursières par secteur
    fig.add_trace(
        go.Box(
            x=market_data['Secteur'],
            y=market_data['Capitalisation_boursiere']/1e9,
            name='Distribution des capitalisations'
        )
    )
    
    fig.update_layout(
        title="Aperçu rapide du marché",
        xaxis_title="Secteur",
        yaxis_title="Capitalisation (Mrd€)",
        height=400
    )
    
    return fig

def main():
    st.title("📊 Finance Dashboard")
    
    analyzer = MarketAnalyzer()
    selected_stocks = load_selected_stocks()
    
    if analyzer.market_data is not None and selected_stocks is not None:
        # Ajout de l'onglet Accueil
        tab0, tab1, tab2, tab3 = st.tabs(["🏠 Accueil", "📈 Vue d'ensemble", "🔍 Points marquants", "📊 Analyses détaillées"])
        
        with tab0:
            # Page d'accueil
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.info("""
                ### 🌍 Vue Globale du Marché
                
                **Une vue complète de l'ensemble du marché**
                
                Découvrez :
                - Analyses sectorielles détaillées
                - Cartographie des capitalisations
                - Indicateurs de performance clés
                - Filtres personnalisables
                """)
            
            with col2:
                st.info("""
                ### 📈 Suivi de Portefeuille
                
                **Gérez votre portefeuille d'1M€**
                
                Accédez à :
                - Performances par position
                - Répartition des actifs
                - Métriques de risque
                - Analyses comparatives
                """)
            
            with col3:
                st.info("""
                ### 🏢 Analyse des Entreprises
                
                **Explorez les sociétés en détail**
                
                Étudiez :
                - Profils financiers complets
                - Ratios et métriques clés
                - Analyses qualitatives
                - Comparaisons sectorielles
                """)
            
            # Guide rapide
            st.markdown("---")
            st.markdown("""
            ### 🎯 Pour commencer
            
            1. Naviguez entre les onglets pour explorer différentes vues
            2. Utilisez la **Vue d'ensemble** pour les tendances globales
            3. Consultez les **Points marquants** pour les performances clés
            4. Approfondissez avec les **Analyses détaillées**
            """)
        
        with tab1:
            # Métriques principales dans une seule ligne
            metrics = analyzer.calculate_market_metrics()
            cols = st.columns(4)
            
            with cols[0]:
                st.metric(
                    "Nombre d'entreprises",
                    f"{metrics['nb_companies']:,}",
                    delta=f"+{len(selected_stocks)} sélectionnées"
                )
            
            with cols[1]:
                total_market_cap = metrics['total_market_cap'] / 1e12
                st.metric(
                    "Capitalisation totale",
                    f"{total_market_cap:.2f} T€"
                )
            
            with cols[2]:
                st.metric(
                    "PER moyen",
                    f"{metrics['avg_per']:.1f}",
                    delta=f"{metrics['avg_yield']:.1f}% rendement"
                )
            
            with cols[3]:
                st.metric(
                    "Variation moyenne",
                    f"{metrics['avg_variation']:.1f}%"
                )
            
            # Graphique Sunburst des secteurs
            st.plotly_chart(analyzer.create_sector_sunburst(), use_container_width=True)
        
        with tab2:
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
        
        with tab3:
            # Options d'analyse
            analysis_type = st.selectbox(
                "Type d'analyse",
                ["Capitalisations", "Performance", "Valorisation"]
            )
            
            if analysis_type == "Capitalisations":
                st.plotly_chart(create_market_summary(analyzer.market_data))
            # Ajouter d'autres types d'analyses selon les besoins
        
        # Footer
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.caption("*Dernière mise à jour : {}*".format(
                pd.Timestamp.now().strftime("%d/%m/%Y %H:%M")
            ))
        with col2:
            st.caption("*Données fournies à titre indicatif uniquement*")

if __name__ == "__main__":
    main()