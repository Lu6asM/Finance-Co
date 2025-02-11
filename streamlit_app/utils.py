import pandas as pd
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