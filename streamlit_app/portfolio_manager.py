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
        self.INVESTMENT_DATE = datetime(2024, 1, 1)  # Date fixe de l'investissement initial
        self.load_data()
        
    def load_data(self):
        """Charge et initialise les données du portefeuille"""
        try:
            self.portfolio_data = pd.read_csv('https://raw.githubusercontent.com/thidescac25/Finance-Co/refs/heads/main/data/selected_stocks.csv')
            
            if 'Rendement du dividende' in self.portfolio_data.columns:
                self.portfolio_data['Rendement du dividende'] = self.portfolio_data['Rendement du dividende'] * 100

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

    def get_current_portfolio_value(self):
        """Calcule la valeur actuelle du portefeuille en utilisant yfinance"""
        try:
            # Pour chaque position
            current_values = []
            progress_bar = st.progress(0)
            
            for idx, row in self.portfolio_data.iterrows():
                progress_bar.progress(idx/len(self.portfolio_data))
                ticker = row['Ticker']
                shares = row['shares']
                exchange_rate = row['exchange_rate']
                
                try:
                    # Récupérer le dernier prix via yfinance
                    stock = yf.Ticker(ticker)
                    hist = stock.history(period="1d")
                    if not hist.empty:
                        current_price = hist['Close'].iloc[-1]
                        current_value = current_price * shares * exchange_rate
                    else:
                        current_value = row['valeur_position']  # Fallback sur la valeur du CSV
                except Exception as e:
                    st.warning(f"Erreur pour {ticker}: {str(e)}")
                    current_value = row['valeur_position']  # Fallback sur la valeur du CSV
                
                current_values.append(current_value)
            
            progress_bar.empty()
            
            # Mettre à jour les valeurs dans le DataFrame
            self.portfolio_data['valeur_position_actuelle'] = current_values
            
            # Calculer la valeur totale actuelle
            total_value = sum(current_values)
            initial_value = self.portfolio_data['valeur_position'].sum()
            variation = ((total_value/initial_value)-1)*100
            
            return total_value, variation
            
        except Exception as e:
            st.error(f"Erreur lors du calcul de la valeur du portefeuille : {str(e)}")
            return self.portfolio_data['valeur_position'].sum(), 0.0

    def get_current_values(self, start_date=None):
        """Récupère les valeurs actuelles et historiques du portefeuille"""
        if start_date is None:
            start_date = self.INVESTMENT_DATE.strftime('%Y-%m-%d')
        
        # Style CSS pour tous les éléments
        st.markdown("""
        <style>
        .performance-metric {
            padding: 1.5rem;
            border-radius: 0.5rem;
            background: #f8f9fa;
            margin: 0.5rem 0;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s ease;
        }
        .performance-metric:hover {
            transform: translateY(-2px);
        }
        .performance-metric h3 {
            margin: 0;
            color: #1f77b4;
            font-size: 1.8rem;
            font-weight: 600;
        }
        .performance-metric p {
            margin: 0.5rem 0 0 0;
            font-size: 1rem;
            color: #666;
        }
        .metric-positive {
            color: #2ca02c !important;
        }
        .metric-negative {
            color: #d62728 !important;
        }
        .performance-list {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 0.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .performance-list h3 {
            color: #1f77b4;
            margin-bottom: 1rem;
        }
        .performance-item {
            padding: 0.5rem;
            margin: 0.25rem 0;
            border-radius: 0.25rem;
            transition: background-color 0.2s ease;
        }
        .performance-item:hover {
            background-color: #e9ecef;
        }
        .summary-card {
            background: #ffffff;
            padding: 1.5rem;
            border-radius: 0.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin: 1rem 0;
        }
        .progress-update {
            padding: 1rem;
            background: #e9ecef;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Dictionnaire pour stocker toutes les séries de données
        all_series = {}
        positions_data = []
        
        st.markdown("""
        <div class="progress-update">
            <h3>📊 Mise à jour des valeurs...</h3>
        </div>
        """, unsafe_allow_html=True)
        progress_bar = st.progress(0)
        
        # [Code de récupération des données inchangé...]
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
                    first_price = hist_data['Close'].iloc[0]
                    adjusted_shares = (stock['valeur_position'] / (first_price * exchange_rate))
                    stock_values = hist_data['Close'] * adjusted_shares * exchange_rate
                    all_series[ticker] = stock_values
                    
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
            historical_values = pd.DataFrame(all_series)
            historical_values = historical_values.fillna(method='bfill').fillna(method='ffill')
            historical_values['Total'] = historical_values.sum(axis=1)
            historical_values = historical_values[['Total']]
            
            # Calculs de performance
            total_current_value = historical_values['Total'].iloc[-1]
            total_initial_value = historical_values['Total'].iloc[0]
            total_variation = ((total_current_value/total_initial_value)-1)*100
            
            # Graphique amélioré
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Valeur du Portefeuille (€)', 'Performance Cumulée (%)'),
                vertical_spacing=0.12
            )

            # Premier graphique - Valeur du portefeuille
            fig.add_trace(
                go.Scatter(
                    x=historical_values.index,
                    y=historical_values['Total'],
                    mode='lines',
                    name='Valeur du Portefeuille',
                    line=dict(color='#1f77b4', width=2)
                ),
                row=1, col=1
            )

            # Deuxième graphique - Performance cumulée
            performance = (historical_values['Total'] / historical_values['Total'].iloc[0] - 1) * 100
            fig.add_trace(
                go.Scatter(
                    x=historical_values.index,
                    y=performance,
                    mode='lines',
                    name='Performance Cumulée',
                    line=dict(color='#2ca02c', width=2)
                ),
                row=2, col=1
            )

            fig.update_layout(
                height=800,
                showlegend=True,
                title_text="Evolution du Portefeuille",
                paper_bgcolor='white',
                plot_bgcolor='white',
                font=dict(size=12),
                hovermode='x unified'
            )

            # Ajouter des grilles
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')

            st.plotly_chart(fig, use_container_width=True)
            
            # Résumé avec style
            st.markdown(f"""
            <div class="summary-card">
                <h3>📊 Résumé</h3>
                <p><strong>Date d'investissement:</strong> {self.INVESTMENT_DATE.strftime('%d/%m/%Y')}</p>
                <p><strong>Valeur initiale:</strong> {total_initial_value:,.2f}€</p>
                <p><strong>Valeur actuelle:</strong> {total_current_value:,.2f}€ <em>(au {datetime.now().strftime('%d/%m/%Y %H:%M')})</em></p>
                <p><strong>Performance globale:</strong> <span class="{'metric-positive' if total_variation >= 0 else 'metric-negative'}">{total_variation:+.2f}%</span></p>
            </div>
            """, unsafe_allow_html=True)

            # Top/Flop 5 avec style
            positions_df = pd.DataFrame(positions_data)
            top5 = positions_df.nlargest(5, 'variation')
            flop5 = positions_df.nsmallest(5, 'variation')
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                <div class="performance-list">
                    <h3>🔝 Top 5 Performances</h3>
                """, unsafe_allow_html=True)
                for _, pos in top5.iterrows():
                    st.markdown(f"""
                    <div class="performance-item">
                        <span style="font-weight: bold;">{pos['ticker']}</span>: 
                        <span class="metric-positive">{pos['variation']:+.2f}%</span>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown("""
                <div class="performance-list">
                    <h3>👎 Flop 5 Performances</h3>
                """, unsafe_allow_html=True)
                for _, pos in flop5.iterrows():
                    st.markdown(f"""
                    <div class="performance-item">
                        <span style="font-weight: bold;">{pos['ticker']}</span>: 
                        <span class="metric-negative">{pos['variation']:+.2f}%</span>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            # Métriques supplémentaires avec style
            volatility = historical_values['Total'].pct_change().std() * np.sqrt(252) * 100
            max_drawdown = ((historical_values['Total'] - historical_values['Total'].cummax()) / 
                        historical_values['Total'].cummax()).min() * 100

            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="performance-metric">
                    <h3 class="{'metric-positive' if total_variation >= 0 else 'metric-negative'}">{total_variation:+.2f}%</h3>
                    <p>Performance globale</p>
                </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                <div class="performance-metric">
                    <h3>{volatility:.2f}%</h3>
                    <p>Volatilité annualisée</p>
                </div>
                """, unsafe_allow_html=True)

            with col3:
                st.markdown(f"""
                <div class="performance-metric">
                    <h3>{abs(max_drawdown):.2f}%</h3>
                    <p>Drawdown Maximum</p>
                </div>
                """, unsafe_allow_html=True)

    def create_portfolio_overview(self):
        """Crée une vue d'ensemble du portefeuille"""
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=(
                'Répartition sectorielle',
                'Répartition géographique'
            ),
            specs=[[{'type': 'pie'}, {'type': 'pie'}]]
        )
        
        # Répartition sectorielle
        secteur_data = self.portfolio_data.groupby('Secteur')['valeur_position'].sum()
        fig.add_trace(
            go.Pie(
                labels=secteur_data.index,
                values=secteur_data.values,
                name="Secteurs",
                hole=0.3,
                legendgroup="secteurs",
                showlegend=True
            ),
            row=1, col=1
        )
        
        # Répartition géographique
        pays_data = self.portfolio_data.groupby('Pays')['valeur_position'].sum()
        fig.add_trace(
            go.Pie(
                labels=pays_data.index,
                values=pays_data.values,
                name="Pays",
                hole=0.3,
                legendgroup="pays",
                showlegend=True
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title_text="Vue d'ensemble du portefeuille",
            height=400,  # Réduit la hauteur du graphique
            width=1100,  # Augmente la largeur pour bien utiliser l'espace
            showlegend=True,
            legend=dict(
                orientation="h",  # Légende en horizontal
                yanchor="bottom",
                y=-0.2,  # Décalage sous le graphe
                xanchor="center",
                x=0.5,
                
            )
        )
        
        return fig