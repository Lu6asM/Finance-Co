import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import numpy as np
from plotly.subplots import make_subplots

class PortfolioAnalyzer:
    """Analyseur pour le portefeuille spécifique"""
    
    def __init__(self, portfolio_data):
        """
        portfolio_data: DataFrame contenant les données du portefeuille
        """
        self.stocks = portfolio_data
        self.metrics = {}
        self._calculate_portfolio_metrics()
    
    def _calculate_portfolio_metrics(self):
        """Calcule les métriques pour chaque action du portefeuille"""
        for _, row in self.stocks.iterrows():
            ticker = row['Ticker']
            self.metrics[ticker] = {
                'prix': row['Prix actuel'],
                'variation': row['Variation 52 semaines'],
                'beta': row['Bêta'],
                'volume': row['Volume'],
                'per': row['PER historique'],
                'rendement': row['Rendement du dividende'],
                'capitalisation': row['Capitalisation boursière'],
                'secteur': row['Secteur'],
                'pays': row['Pays']
            }
    
    def get_stock_metrics(self, ticker):
        """Obtient les métriques pour une action"""
        if ticker not in self.metrics:
            return None
            
        metrics = self.metrics[ticker]
        stock_data = self.stocks[self.stocks['Ticker'] == ticker].iloc[0]
        
        return {
            'prix': metrics['prix'],
            'variation': metrics['variation'],
            'beta': metrics['beta'],
            'volume': metrics['volume'],
            'per': metrics['per'],
            'rendement': metrics['rendement'],
            'capitalisation': metrics['capitalisation'],
            'secteur': metrics['secteur'],
            'pays': metrics['pays'],
            'momentum': self._evaluate_momentum(metrics['variation']),
            'valorisation': self._evaluate_valuation(metrics['per']),
            'risque': self._evaluate_risk(metrics['beta'])
        }
    
    def _evaluate_momentum(self, variation):
        """Évalue le momentum basé sur la variation"""
        if pd.isna(variation):
            return "Non disponible"
        if variation > 20:
            return "Fort"
        elif variation < -20:
            return "Faible"
        return "Neutre"
    
    def _evaluate_valuation(self, per):
        """Évalue la valorisation basée sur le PER"""
        if pd.isna(per):
            return "Non disponible"
        if per < 15:
            return "Attractive"
        elif per > 30:
            return "Élevée"
        return "Moyenne"
    
    def _evaluate_risk(self, beta):
        """Évalue le niveau de risque basé sur le beta"""
        if pd.isna(beta):
            return "Non disponible"
        if beta < 0.8:
            return "Faible"
        elif beta > 1.2:
            return "Élevé"
        return "Moyen"

    def create_stock_analysis(self, ticker):
        """Crée un dashboard d'analyse pour une action"""
        if ticker not in self.metrics:
            return None
            
        metrics = self.metrics[ticker]
        secteur = metrics['secteur']
        
        # Création du layout avec subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Comparaison sectorielle',
                'Analyse de valorisation',
                'Historique de performance',
                'Métriques clés'
            ),
            specs=[[{'type': 'bar'}, {'type': 'indicator'}],
                  [{'type': 'scatter'}, {'type': 'domain'}]]
        )
        
        # Comparaison sectorielle
        secteur_data = self.stocks[self.stocks['Secteur'] == secteur]
        fig.add_trace(
            go.Bar(
                x=['PER', 'Beta', 'Rendement'],
                y=[metrics['per'], metrics['beta'], metrics['rendement']],
                name='Action',
                marker_color='blue'
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Bar(
                x=['PER', 'Beta', 'Rendement'],
                y=[secteur_data['PER historique'].mean(),
                   secteur_data['Bêta'].mean(),
                   secteur_data['Rendement du dividende'].mean()],
                name='Secteur',
                marker_color='lightgray'
            ),
            row=1, col=1
        )
        
        # Indicateur de valorisation
        fig.add_trace(
            go.Indicator(
                mode="gauge+number",
                value=metrics['per'],
                title={'text': "PER"},
                gauge={'axis': {'range': [0, 50]},
                       'steps': [
                           {'range': [0, 15], 'color': "lightgreen"},
                           {'range': [15, 30], 'color': "lightyellow"},
                           {'range': [30, 50], 'color': "lightcoral"}
                       ]},
            ),
            row=1, col=2
        )
        
        # Métriques clés dans un pie chart
        fig.add_trace(
            go.Pie(
                labels=['Rendement', 'Beta', 'Variation'],
                values=[metrics['rendement'], metrics['beta'], metrics['variation']],
                hole=.3
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=800,
            showlegend=True,
            title_text=f"Analyse détaillée - {ticker}"
        )
        
        return fig

def add_technical_analysis(stock_analyzer, ticker):
    """Ajoute l'analyse technique à Streamlit"""
    metrics = stock_analyzer.get_stock_metrics(ticker)
    
    if metrics:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "Prix actuel",
                f"{metrics['prix']:.2f} €",
                f"{metrics['variation']:.1f}% (52s)"
            )
        
        with col2:
            st.metric(
                "Valorisation",
                metrics['valorisation'],
                f"PER: {metrics['per']:.1f}"
            )
        
        with col3:
            st.metric(
                "Risque",
                metrics['risque'],
                f"Beta: {metrics['beta']:.2f}"
            )
        
        # Graphique d'analyse
        fig = stock_analyzer.create_stock_analysis(ticker)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        
        # Informations supplémentaires
        with st.expander("Informations détaillées"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Informations générales**")
                st.write(f"Secteur: {metrics['secteur']}")
                st.write(f"Pays: {metrics['pays']}")
                st.write(f"Capitalisation: {metrics['capitalisation']:,.0f} €")
            
            with col2:
                st.write("**Métriques de marché**")
                st.write(f"Volume: {metrics['volume']:,.0f}")
                st.write(f"Momentum: {metrics['momentum']}")
                st.write(f"Rendement: {metrics['rendement']:.2f}%")