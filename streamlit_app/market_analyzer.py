import streamlit as st
import pandas as pd
import plotly.express as px
from utils import prepare_market_data

class MarketAnalyzer:
    def __init__(self):
        self.market_data = None
        self.load_and_clean_data()
        
    def load_and_clean_data(self):
        """Charge et nettoie les données du marché"""
        try:
            # Chargement des données
            df = pd.read_csv('stocks_data.csv')
            
            # Nettoyage des données
            df = prepare_market_data(df)

            self.market_data = df
            
        except Exception as e:
            st.error(f"Erreur lors du chargement des données : {str(e)}")
            self.market_data = pd.DataFrame()
    
    def create_market_overview(self, filtered_data=None):
        """Crée les visualisations du marché"""
        df = filtered_data if filtered_data is not None else self.market_data
        
        if df is None or df.empty:
            return None, None, None

        # Treemap
        fig_treemap = px.treemap(
            df,
            path=['Secteur', 'Industrie', 'Nom_complet'],
            values='Capitalisation_boursiere',
            color='Score',
            color_continuous_scale='RdYlBu',
            hover_data=['Ticker', 'Prix_actuel', 'PER_historique', 'Rendement_du_dividende'],
            title='Répartition des capitalisations boursières'
        )

        fig_treemap.update_layout(
            height=700,
            title={
                'text': 'Répartition des capitalisations boursières par score',
                'x': 0.5,
                'xanchor': 'center'
            }
        )

        fig_treemap.update_traces(
            hovertemplate="""
            <b>%{label}</b><br>
            Capitalisation: %{value:,.0f} €<br>
            Ticker: %{customdata[0]}<br>
            Prix: %{customdata[1]:.2f} €<br>
            PER: %{customdata[2]:.2f}<br>
            Rendement: %{customdata[3]:.2f}%<br>
            Score: %{color:.1f}/100
            <extra></extra>
            """
        )

        # Distribution des PER
        fig_per = px.box(
            df,
            x='Secteur',
            y='PER_historique',
            title='Distribution des PER par secteur'
        )
        fig_per.update_layout(height=400)

        # Distribution des rendements
        fig_returns = px.histogram(
            df,
            x='Variation_52_semaines',
            nbins=50,
            title='Distribution des rendements sur 52 semaines'
        )
        fig_returns.update_layout(height=400)

        return fig_treemap, fig_per, fig_returns
    
    def calculate_market_metrics(self, filtered_data=None):
        """Calcule les métriques du marché"""
        df = filtered_data if filtered_data is not None else self.market_data
        
        if df is None or df.empty:
            return {}
        
        return {
            'nb_companies': len(df),
            'total_market_cap': df['Capitalisation_boursiere'].sum(),
            'avg_per': df['PER_historique'].mean(),
            'avg_yield': df['Rendement_du_dividende'].mean(),
            'avg_variation': df['Variation_52_semaines'].mean()
        }
    
    def get_market_highlights(self):
        """Récupère les points marquants du marché"""
        df = self.market_data
        
        # Plus fortes hausses/baisses sur 52 semaines
        best_performers = df.nlargest(5, 'Variation_52_semaines')[
            ['Ticker', 'Nom_complet', 'Variation_52_semaines']
        ]
        worst_performers = df.nsmallest(5, 'Variation_52_semaines')[
            ['Ticker', 'Nom_complet', 'Variation_52_semaines']
        ]
        
        # Plus gros dividendes
        highest_dividends = df.nlargest(5, 'Rendement_du_dividende')[
            ['Ticker', 'Nom_complet', 'Rendement_du_dividende']
        ]
        
        # Répartition par secteur
        sector_allocation = df.groupby('Secteur')['Capitalisation_boursiere'].sum()
        sector_allocation = (sector_allocation / sector_allocation.sum() * 100).round(2)
        
        return {
            'best_performers': best_performers,
            'worst_performers': worst_performers,
            'highest_dividends': highest_dividends,
            'sector_allocation': sector_allocation
        }

    def create_sector_sunburst(self):
        """Crée un graphique sunburst des secteurs et industries"""
        df = self.market_data
        
        fig = px.sunburst(
            df,
            path=['Secteur', 'Industrie'],
            values='Capitalisation_boursiere',
            color='Score',
            color_continuous_scale='RdYlBu',
        )
        
        fig.update_layout(height=500)
        return fig