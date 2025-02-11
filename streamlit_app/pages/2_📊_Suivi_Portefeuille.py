# pages/2_📊_Suivi_Portefeuille.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import numpy as np

class PortfolioTracker:
    def __init__(self):
        self.INITIAL_INVESTMENT = 1_000_000
        self.load_data()
        
    def load_data(self):
        """Charge les données du marché et du portefeuille"""
        try:
            # Chargement des données du marché
            self.market_data = pd.read_csv('stocks_data.csv')
            
            # Chargement de la sélection de titres (à adapter selon votre fichier)
            self.selected_stocks = pd.read_csv('selected_stocks.csv')
            
            # Nettoyage des données
            self._clean_data()
            
        except Exception as e:
            st.error(f"Erreur lors du chargement des données : {str(e)}")
            self.market_data = pd.DataFrame()
            self.selected_stocks = pd.DataFrame()
    
    def _clean_data(self):
        """Nettoie les données chargées"""
        numeric_cols = ['Prix_actuel', 'Variation_52_semaines', 'Volume', 
                       'Capitalisation_boursiere', 'PER_historique']
        
        for col in numeric_cols:
            self.market_data[col] = pd.to_numeric(self.market_data[col], errors='coerce')
            
        # Calcul des poids du portefeuille
        total_stocks = len(self.selected_stocks)
        self.selected_stocks['weight'] = 1 / total_stocks
        
    def calculate_portfolio_metrics(self):
        """Calcule les métriques principales du portefeuille"""
        portfolio = self.selected_stocks.merge(
            self.market_data,
            on='Ticker',
            how='left'
        )
        
        # Calcul des métriques de base
        portfolio['valeur_position'] = portfolio['weight'] * self.INITIAL_INVESTMENT
        portfolio['nombre_actions'] = portfolio['valeur_position'] / portfolio['Prix_actuel']
        portfolio['valeur_actuelle'] = portfolio['nombre_actions'] * portfolio['Prix_actuel']
        
        # Calcul des métriques de risque
        portfolio['contribution_risque'] = (
            portfolio['Beta'] * portfolio['weight']
        )
        
        return portfolio
    
    def create_portfolio_overview(self, portfolio):
        """Crée la vue d'ensemble du portefeuille"""
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
        sector_data = portfolio.groupby('Secteur')['valeur_actuelle'].sum()
        fig.add_trace(
            go.Pie(
                labels=sector_data.index,
                values=sector_data.values,
                name="Secteurs"
            ),
            row=1, col=1
        )
        
        # Répartition géographique
        geo_data = portfolio.groupby('Pays')['valeur_actuelle'].sum()
        fig.add_trace(
            go.Pie(
                labels=geo_data.index,
                values=geo_data.values,
                name="Pays"
            ),
            row=1, col=2
        )
        
        # Top 10 positions
        top10 = portfolio.nlargest(10, 'valeur_actuelle')
        fig.add_trace(
            go.Bar(
                x=top10['Nom_complet'],
                y=top10['valeur_actuelle'],
                name="Top 10"
            ),
            row=2, col=1
        )
        
        # Distribution des rendements
        fig.add_trace(
            go.Histogram(
                x=portfolio['Variation_52_semaines'],
                name="Rendements"
            ),
            row=2, col=2
        )
        
        fig.update_layout(height=800, showlegend=True)
        return fig

def main():
    st.set_page_config(page_title="Suivi du Portefeuille", layout="wide")
    st.title("📊 Suivi du Portefeuille")
    
    # Initialisation du tracker
    tracker = PortfolioTracker()
    
    # Calcul des métriques du portefeuille
    portfolio = tracker.calculate_portfolio_metrics()
    
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
        rendement_moyen = portfolio['Rendement_du_dividende'].mean()
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
    
    # Vue d'ensemble du portefeuille
    st.subheader("Vue d'ensemble")
    fig_overview = tracker.create_portfolio_overview(portfolio)
    st.plotly_chart(fig_overview, use_container_width=True)
    
    # Analyse détaillée des positions
    st.subheader("Détail des positions")
    
    detailed_view = portfolio[[
        'Ticker', 'Nom_complet', 'Secteur', 'Pays',
        'Prix_actuel', 'Variation_52_semaines',
        'valeur_actuelle', 'weight', 'Beta',
        'Rendement_du_dividende'
    ]].copy()
    
    st.dataframe(
        detailed_view.style.format({
            'Prix_actuel': '{:.2f} €',
            'Variation_52_semaines': '{:+.2f}%',
            'valeur_actuelle': '{:,.2f} €',
            'weight': '{:.2%}',
            'Beta': '{:.2f}',
            'Rendement_du_dividende': '{:.2f}%'
        })
    )
    
    # Analyses supplémentaires
    st.subheader("Analyses de risque")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribution des betas
        fig_beta = px.box(
            portfolio,
            y='Beta',
            title="Distribution des Betas"
        )
        st.plotly_chart(fig_beta)
    
    with col2:
        # Relation rendement/risque
        fig_risk = px.scatter(
            portfolio,
            x='Beta',
            y='Variation_52_semaines',
            text='Ticker',
            title="Rendement vs Risque"
        )
        st.plotly_chart(fig_risk)

if __name__ == "__main__":
    main()