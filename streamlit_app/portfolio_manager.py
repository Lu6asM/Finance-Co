# portfolio_manager.py

# Imports standard
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import yfinance as yf

# Import local
from portfolio_analyzer import PortfolioAnalyzer, add_technical_analysis

class PortfolioManager:
    def __init__(self):
        self.INITIAL_INVESTMENT = 1_000_000  # 1M€
        self.load_data()
        
    def load_data(self):
        """Charge et initialise les données du portefeuille"""
        try:
            self.portfolio_data = pd.read_csv('https://raw.githubusercontent.com/thidescac25/Finance-Co/refs/heads/main/data/selected_stocks.csv')
            
            # Calcul des métriques de base
            total_stocks = len(self.portfolio_data)
            self.portfolio_data['weight'] = 1 / total_stocks
            self.portfolio_data['target_investment'] = self.INITIAL_INVESTMENT * self.portfolio_data['weight']
            
            # Exchange rates
            exchange_rates = {
                'EUR': 1.0,
                'USD': 0.93,
                'GBP': 1.17,
                'CHF': 1.07,
                'JPY': 0.00622,
                'AUD': 0.605,
                'KRW': 0.000696
            }
            
            # Déterminer la devise de chaque action
            def get_currency(ticker):
                if '.PA' in ticker or '.AS' in ticker or '.DE' in ticker or '.BR' in ticker or '.MC' in ticker:
                    return 'EUR'
                elif '.L' in ticker:
                    return 'GBP'
                elif '.SW' in ticker:
                    return 'CHF'
                elif '.T' in ticker:
                    return 'JPY'
                elif '.AX' in ticker:
                    return 'AUD'
                elif '.KS' in ticker:
                    return 'KRW'
                return 'USD'
            
            self.portfolio_data['currency'] = self.portfolio_data['Ticker'].apply(get_currency)
            self.portfolio_data['exchange_rate'] = self.portfolio_data['currency'].map(exchange_rates)
            
            # Calcul du nombre d'actions
            self.portfolio_data['shares'] = (self.portfolio_data['target_investment'] / 
                                           (self.portfolio_data['Prix actuel'] * 
                                            self.portfolio_data['exchange_rate'])).round(2)
            
            # Calcul de la valeur initiale réelle
            self.portfolio_data['valeur_position'] = (self.portfolio_data['Prix actuel'] * 
                                                    self.portfolio_data['shares'] * 
                                                    self.portfolio_data['exchange_rate'])
            
        except Exception as e:
            st.error(f"Erreur lors du chargement des données : {str(e)}")
            self.portfolio_data = pd.DataFrame()

    def get_current_values(self, start_date=None):
        """Récupère les valeurs actuelles et historiques du portefeuille"""
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        
        # Dictionnaire pour stocker toutes les séries de données
        all_series = {}
        positions_data = []
        
        st.write("### Mise à jour des valeurs...")
        progress_bar = st.progress(0)
        
        for idx, stock in self.portfolio_data.iterrows():
            progress_bar.progress(idx/len(self.portfolio_data))
            
            ticker = stock['Ticker']
            initial_price = stock['Prix actuel']
            shares = stock['shares']
            exchange_rate = stock['exchange_rate']
            initial_value = shares * initial_price * exchange_rate
            
            try:
                hist_data = yf.Ticker(ticker).history(start=start_date)
                if not hist_data.empty:
                    # On récupère le premier prix disponible
                    first_price = hist_data['Close'].iloc[0]
                    # On ajuste le nombre d'actions pour avoir la bonne valeur initiale
                    adjusted_shares = (stock['valeur_position'] / (first_price * exchange_rate))
                    
                    # On calcule toute la série avec ce nombre d'actions ajusté
                    stock_values = hist_data['Close'] * adjusted_shares * exchange_rate
                    all_series[ticker] = stock_values
                    
                    # Pour les métriques finales
                    current_price = hist_data['Close'].iloc[-1]
                    current_value = adjusted_shares * current_price * exchange_rate
                    variation = ((current_value/stock['valeur_position'])-1)*100
                else:
                    current_price = initial_price
                    current_value = initial_value
                    variation = 0
                
                positions_data.append({
                    'ticker': ticker,
                    'variation': variation,
                    'current_value': current_value
                })
                
            except Exception as e:
                st.error(f"Erreur pour {ticker}: {str(e)}")
                positions_data.append({
                    'ticker': ticker,
                    'variation': 0,
                    'current_value': initial_value
                })

        progress_bar.empty()

        # Combiner toutes les séries
        if all_series:
            # Créer un DataFrame avec toutes les séries
            historical_values = pd.DataFrame(all_series)
            
            # Remplir les valeurs manquantes en commençant par la fin
            historical_values = historical_values.fillna(method='bfill')
            # Puis remplir le reste avec la méthode forward
            historical_values = historical_values.fillna(method='ffill')
            
            # Calculer la somme totale
            historical_values['Total'] = historical_values.sum(axis=1)
            # Garder uniquement la colonne Total
            historical_values = historical_values[['Total']]
            
            # Calcul des performances
            total_current_value = historical_values['Total'].iloc[-1]
            total_initial_value = historical_values['Total'].iloc[0]
            total_variation = ((total_current_value/total_initial_value)-1)*100
            
            # Création du graphique
            fig = make_subplots(rows=2, cols=1, 
                               subplot_titles=('Valeur du Portefeuille', 'Performance Cumulée (%)'),
                               vertical_spacing=0.12)

            fig.add_trace(
                go.Scatter(
                    x=historical_values.index,
                    y=historical_values['Total'],
                    mode='lines',
                    name='Valeur du Portefeuille',
                    line=dict(color='#1f77b4')
                ),
                row=1, col=1
            )

            performance = (historical_values['Total'] / historical_values['Total'].iloc[0] - 1) * 100
            fig.add_trace(
                go.Scatter(
                    x=historical_values.index,
                    y=performance,
                    mode='lines',
                    name='Performance Cumulée',
                    line=dict(color='#2ca02c')
                ),
                row=2, col=1
            )

            fig.update_layout(
                height=800,
                showlegend=True,
                title_text="Evolution du Portefeuille"
            )

            st.plotly_chart(fig, use_container_width=True)
            
            st.write(f"""
            ### Résumé ###
            - Valeur initiale totale: {total_initial_value:,.2f}€
            - Valeur actuelle totale: {total_current_value:,.2f}€
            - Performance globale: {total_variation:+.2f}%
            """)

            # Top/Flop 5
            positions_df = pd.DataFrame(positions_data)
            top5 = positions_df.nlargest(5, 'variation')
            flop5 = positions_df.nsmallest(5, 'variation')
            
            col1, col2 = st.columns(2)
            with col1:
                st.write("### Top 5 Performances ###")
                for _, pos in top5.iterrows():
                    st.write(f"{pos['ticker']}: {pos['variation']:+.2f}%")
            
            with col2:
                st.write("### Flop 5 Performances ###")
                for _, pos in flop5.iterrows():
                    st.write(f"{pos['ticker']}: {pos['variation']:+.2f}%")

            # Métriques supplémentaires
            volatility = historical_values['Total'].pct_change().std() * np.sqrt(252) * 100
            max_drawdown = ((historical_values['Total'] - historical_values['Total'].cummax()) / 
                           historical_values['Total'].cummax()).min() * 100

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Performance", f"{total_variation:+.2f}%")
            with col2:
                st.metric("Volatilité annualisée", f"{volatility:.2f}%")
            with col3:
                st.metric("Drawdown Maximum", f"{max_drawdown:.2f}%")

    def create_portfolio_overview(self):
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
            secteur_data = self.portfolio_data.groupby('Secteur')['valeur_position'].sum()
            fig.add_trace(
                go.Pie(
                    labels=secteur_data.index,
                    values=secteur_data.values,
                    name="Secteurs"
                ),
                row=1, col=1
            )
            
            # Répartition géographique
            pays_data = self.portfolio_data.groupby('Pays')['valeur_position'].sum()
            fig.add_trace(
                go.Pie(
                    labels=pays_data.index,
                    values=pays_data.values,
                    name="Pays"
                ),
                row=1, col=2
            )
            
            # Top 10 positions
            top10 = self.portfolio_data.nlargest(10, 'valeur_position')
            fig.add_trace(
                go.Bar(
                    x=top10['Nom complet'],
                    y=top10['valeur_position'],
                    name="Top 10"
                ),
                row=2, col=1
            )
            
            # Distribution des rendements
            if 'Variation 52 semaines' in self.portfolio_data.columns:
                fig.add_trace(
                    go.Histogram(
                        x=self.portfolio_data['Variation 52 semaines'],
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