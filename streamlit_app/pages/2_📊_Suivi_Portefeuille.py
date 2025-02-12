import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from portfolio_analysis import PortfolioAnalyzer, add_technical_analysis

class PortfolioTracker:
    def __init__(self):
        self.INITIAL_INVESTMENT = 1_000_000
        self.load_data()
        
    def load_data(self):
        """Charge les données du portefeuille"""
        try:
            self.selected_stocks = pd.read_csv('https://raw.githubusercontent.com/thidescac25/Finance-Co/refs/heads/main/data/selected_stocks.csv')
            
            # Calcul des métriques de base
            total_stocks = len(self.selected_stocks)
            self.selected_stocks['weight'] = 1 / total_stocks
            self.selected_stocks['valeur_position'] = self.INITIAL_INVESTMENT / total_stocks
            self.selected_stocks['valeur_actuelle'] = self.selected_stocks['valeur_position']
            
            # Utiliser la colonne Bêta
            self.selected_stocks['contribution_risque'] = self.selected_stocks['Bêta'] * self.selected_stocks['weight']
            
        except Exception as e:
            st.error(f"Erreur lors du chargement des données : {str(e)}")
            self.selected_stocks = pd.DataFrame()

    def calculate_portfolio_metrics(self):
        """Retourne le portefeuille avec les métriques calculées"""
        if hasattr(self, 'selected_stocks'):
            return self.selected_stocks
        return pd.DataFrame()
    
    def create_portfolio_overview(self, portfolio):
        """Crée une vue d'ensemble du portefeuille"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Répartition sectorielle',
                'Répartition géographique',
                'Top 10 positions',
                'Distribution des rendements'
            ),
            specs=[[{'type': 'pie'}, {'type': 'pie'}],
                  [{'type': 'bar'}, {'type': 'histogram'}]]
        )
        
        # Répartition sectorielle
        secteur_data = portfolio.groupby('Secteur')['valeur_position'].sum()
        fig.add_trace(
            go.Pie(
                labels=secteur_data.index,
                values=secteur_data.values,
                name="Secteurs"
            ),
            row=1, col=1
        )
        
        # Répartition géographique
        pays_data = portfolio.groupby('Pays')['valeur_position'].sum()
        fig.add_trace(
            go.Pie(
                labels=pays_data.index,
                values=pays_data.values,
                name="Pays"
            ),
            row=1, col=2
        )
        
        # Top 10 positions
        top10 = portfolio.nlargest(10, 'valeur_position')
        fig.add_trace(
            go.Bar(
                x=top10['Nom complet'],
                y=top10['valeur_position'],
                name="Top 10"
            ),
            row=2, col=1
        )
        
        # Distribution des rendements
        if 'Variation 52 semaines' in portfolio.columns:
            fig.add_trace(
                go.Histogram(
                    x=portfolio['Variation 52 semaines'],
                    name="Rendements"
                ),
                row=2, col=2
            )
        
        fig.update_layout(
            height=800, 
            showlegend=True,
            title_text="Vue d'ensemble du portefeuille"
        )
        return fig

def main():
    st.set_page_config(page_title="Suivi du Portefeuille", layout="wide")
    st.title("📊 Suivi du Portefeuille")
    
    tracker = PortfolioTracker()
    portfolio = tracker.calculate_portfolio_metrics()
    
    if portfolio.empty:
        st.error("Impossible de charger les données du portefeuille")
        return
    
    tab1, tab2 = st.tabs(["📈 Vue d'ensemble", "🔍 Analyse Technique"])
    
    with tab1:
        # Métriques principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            valeur_totale = portfolio['valeur_actuelle'].sum()
            variation = ((valeur_totale / tracker.INITIAL_INVESTMENT) - 1) * 100
            st.metric(
                "Valeur totale",
                f"{valeur_totale:,.2f} €",
                f"{variation:+.2f}%"
            )
        
        with col2:
            beta_portfolio = portfolio['contribution_risque'].sum()
            st.metric(
                "Beta du portefeuille",
                f"{beta_portfolio:.2f}"
            )
        
        with col3:
            rendement_moyen = portfolio['Rendement du dividende'].mean()
            st.metric(
                "Rendement moyen",
                f"{rendement_moyen:.2f}%"
            )
        
        with col4:
            nb_positions = len(portfolio)
            st.metric(
                "Nombre de positions",
                nb_positions
            )
        
        # Vue d'ensemble
        st.subheader("Vue d'ensemble")
        fig_overview = tracker.create_portfolio_overview(portfolio)
        st.plotly_chart(fig_overview, use_container_width=True)
        
        # Détail des positions
        st.subheader("Détail des positions")
        cols_to_display = [
            'Ticker', 'Nom complet', 'Secteur', 'Pays',
            'Prix actuel', 'Variation 52 semaines',
            'valeur_actuelle', 'weight', 'Bêta',
            'Rendement du dividende'
        ]
        
        st.dataframe(
            portfolio[cols_to_display].style.format({
                'Prix actuel': '{:.2f} €',
                'Variation 52 semaines': '{:+.2f}%',
                'valeur_actuelle': '{:,.2f} €',
                'weight': '{:.2%}',
                'Bêta': '{:.2f}',
                'Rendement du dividende': '{:.2f}%'
            })
        )

    with tab2:
        st.subheader("Analyse Technique des Positions")
        selected_ticker = st.selectbox(
            "Sélectionner une position",
            options=portfolio['Ticker'].tolist(),
            format_func=lambda x: f"{x} - {portfolio[portfolio['Ticker'] == x]['Nom complet'].iloc[0]}"
        )
        
        portfolio_analyzer = PortfolioAnalyzer(portfolio)
        add_technical_analysis(portfolio_analyzer, selected_ticker)

if __name__ == "__main__":
    main()