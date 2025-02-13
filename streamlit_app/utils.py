import pandas as pd
import yfinance as yf
import streamlit as st
import numpy as np

def get_exchange_rates():
    """Taux de change par rapport à l'EUR"""
    return {
        'EUR': 1.0,
        'USD': 0.93,
        'KRW': 0.000696,
        'JPY': 0.00622,
        'GBP': 1.17,
        'CHF': 1.07,
        'CNY': 0.129,
        'HKD': 0.119,
        'TWD': 0.0295,
        'SGD': 0.69,
        'BRL': 0.186,
        'CAD': 0.69,
        'AUD': 0.605,
        'INR': 0.0112,
        'ZAR': 0.049,
    }

def normalize_metric(series, reverse=False):
    """Normalise une série de données entre 0 et 100"""
    min_val = series.min()
    max_val = series.max()
    if max_val == min_val:
        return series * 0
    normalized = (series - min_val) / (max_val - min_val) * 100
    return 100 - normalized if reverse else normalized

def prepare_market_data(df):
    """Prépare les données du marché"""
    df = df.copy()
    exchange_rates = get_exchange_rates()
    
    # Conversion des capitalisations
    df['Capitalisation_origine'] = df['Capitalisation_boursiere']
    for index, row in df.iterrows():
        if pd.notna(row['Devise']) and row['Devise'] in exchange_rates:
            if pd.notna(row['Capitalisation_boursiere']):
                if row['Devise'] != 'EUR':
                    df.at[index, 'Capitalisation_boursiere'] = row['Capitalisation_boursiere'] * exchange_rates[row['Devise']]
    
    # Nettoyage des colonnes numériques
    numeric_columns = {
        'Prix_actuel': 0.0,
        'Capitalisation_boursiere': 0.0,
        'Volume': 0.0,
        'PER_historique': 0.0,
        'Rendement_du_dividende': 0.0,
        'Variation_52_semaines': 0.0
    }
    
    for col, default_value in numeric_columns.items():
        df[col] = df[col].astype(str).str.replace(',', '.')
        df[col] = df[col].str.replace(r'[^\d.-]', '', regex=True)
        df[col] = pd.to_numeric(df[col], errors='coerce')
        df[col] = df[col].fillna(default_value)
    
    # Nettoyage des colonnes catégorielles
    categorical_columns = ['Secteur', 'Industrie', 'Pays']
    for col in categorical_columns:
        df[col] = df[col].fillna('Non classifié')
        df[col] = df[col].astype(str).str.strip()
        df[col] = df[col].str.replace(r'[^\w\s]', '', regex=True)
        df[col] = df[col].str.replace(r'\s+', ' ', regex=True)
    
    # Nettoyage de Nom_complet
    df['Nom_complet'] = df['Nom_complet'].fillna(df['Ticker'])
    df['Nom_complet'] = df['Nom_complet'].str.strip()
    
    # Calcul du score composite
    df['PER_norm'] = normalize_metric(df['PER_historique'].clip(0, 100), reverse=True)
    df['Rendement_norm'] = normalize_metric(df['Rendement_du_dividende'].clip(0, 15))
    df['Score'] = (
        df['PER_norm'] * 0.4 +
        df['Rendement_norm'] * 0.6
    )
    
    # Filtrage et tri
    df = df[df['Capitalisation_boursiere'] > 0]
    df = df.sort_values('Capitalisation_boursiere', ascending=False)
    
    return df

def initialize_ticker_data():
    """Initialise les données du ticker une seule fois par session"""
    if 'ticker_data' not in st.session_state:
        from stock_analyzer import StockAnalyzer
        analyzer = StockAnalyzer()
        st.session_state.ticker_data = analyzer.get_ticker_prices()

def add_news_ticker():
    """Ajoute le bandeau de news à la page en utilisant les données en cache"""
    # S'assure que les données sont initialisées
    initialize_ticker_data()
    
    # Styles CSS pour le bandeau
    st.markdown("""
    <style>
        .ticker-container {
            width: 100%;
            overflow: hidden;
            white-space: nowrap;
            background-color: #f8f9fa;
            padding: 15px 0;
            border-top: 1px solid #dee2e6;
            border-bottom: 1px solid #dee2e6;
            margin-bottom: 20px;
        }
        .ticker-item {
            display: inline-block;
            padding: 0 50px;
            animation: ticker 1440s linear infinite;
        }
        @keyframes ticker {
            0% { transform: translateX(100%); }
            100% { transform: translateX(-100%); }
        }
        .ticker-item > span {
            margin: 0 100px;
            padding: 5px 15px;
            border-right: 2px solid #dee2e6;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Affichage du bandeau avec les données en cache
    ticker_html = ' '.join([f"<span>{item}</span>" for item in st.session_state.ticker_data])
    st.markdown(f"""
    <div class="ticker-container">
        <div class="ticker-item">
            {ticker_html}
        </div>
    </div>
    """, unsafe_allow_html=True)