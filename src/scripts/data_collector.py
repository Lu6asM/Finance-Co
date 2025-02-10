import yfinance as yf
import pandas as pd
import time
from datetime import datetime
import logging
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from src.config.database import get_db
from src.models.models import StockData
from src.config.constants import (
    API_TIMEOUT,
    MAX_RETRIES,
    RETRY_DELAY,
    EXCEL_FILE,
    LOG_FILE
)

# Configuration du logging simple
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def get_numeric(info: dict, key: str) -> float:
    """Récupère une valeur numérique, retourne None si non disponible"""
    value = info.get(key)
    if value in (None, "N/A", "", "nan"):
        return None
    try:
        float_value = float(value)
        if float_value in (float('inf'), float('-inf')):
            return None
        if pd.isna(float_value):
            return None
        return float_value
    except (ValueError, TypeError):
        return None

def get_text(info: dict, key: str) -> str:
    """Récupère une valeur textuelle"""
    value = info.get(key)
    if value in (None, "N/A", "", "nan", "None", "NULL"):
        return None
    try:
        text_value = str(value).strip()
        return text_value if text_value else None
    except:
        return None

def get_split_date(timestamp) -> datetime:
    """Convertit un timestamp Unix en datetime"""
    if not timestamp or timestamp == "N/A":
        return None
    try:
        return datetime.fromtimestamp(int(timestamp))
    except (ValueError, TypeError):
        return None

def collect_stock_data(ticker):
    """Collecte les données pour un ticker"""
    try:
        stock = yf.Ticker(ticker)
        try:
            info = stock.info
        except Exception as e:
            return None

        if not info:
            return None

        stock_data = {
            # 1. Informations générales
            "Nom_complet": get_text(info, "longName"),
            "Ticker": ticker,
            "Pays": get_text(info, "country"),
            "Industrie": get_text(info, "industry"),
            "Secteur": get_text(info, "sector"),
            "Bourse": get_text(info, "exchange"),
            "Devise": get_text(info, "currency"),
            "Devise_financiere": get_text(info, "financialCurrency"),

            # 2. Informations sur le prix de l'action
            "Cloture_precedente": get_numeric(info, "previousClose"),
            "Prix_d_ouverture": get_numeric(info, "open"),
            "Plus_bas_du_jour": get_numeric(info, "dayLow"),
            "Plus_haut_du_jour": get_numeric(info, "dayHigh"),
            "Cloture_precedente_marche_regulier": get_numeric(info, "regularMarketPreviousClose"),
            "Prix_actuel": get_numeric(info, "currentPrice"),
            "Plus_bas_sur_52_semaines": get_numeric(info, "fiftyTwoWeekLow"),
            "Plus_haut_sur_52_semaines": get_numeric(info, "fiftyTwoWeekHigh"),
            "Moyenne_sur_50_jours": get_numeric(info, "fiftyDayAverage"),
            "Moyenne_sur_200_jours": get_numeric(info, "twoHundredDayAverage"),

            # 3. Indicateurs de volume et de capitalisation
            "Volume": get_numeric(info, "volume"),
            "Volume_moyen": get_numeric(info, "averageVolume"),
            "Volume_moyen_10_jours": get_numeric(info, "averageDailyVolume10Day"),
            "Capitalisation_boursiere": get_numeric(info, "marketCap"),
            "Actions_en_circulation": get_numeric(info, "sharesOutstanding"),
            "Pourcentage_detenu_institutions": get_numeric(info, "heldPercentInstitutions"),

            # 4. Ratios et valorisation
            "Ratio_cours_ventes_TTM": get_numeric(info, "priceToSalesTrailing12Months"),
            "Valeur_d_entreprise": get_numeric(info, "enterpriseValue"),
            "Marges_beneficiaires": get_numeric(info, "profitMargins"),
            "Ratio_cours_valeur_comptable": get_numeric(info, "priceToBook"),
            "Valeur_entreprise_chiffre_d_affaires": get_numeric(info, "enterpriseToRevenue"),
            "Valeur_entreprise_EBITDA": get_numeric(info, "enterpriseToEbitda"),

            # 5. Dividendes et rémunération des actionnaires
            "Taux_de_dividende": get_numeric(info, "dividendRate"),
            "Rendement_du_dividende": get_numeric(info, "dividendYield"),
            "Ratio_de_distribution": get_numeric(info, "payoutRatio"),
            "Rendement_moyen_5_ans": get_numeric(info, "fiveYearAvgDividendYield"),
            "Valeur_dernier_dividende": get_numeric(info, "lastDividendValue"),

            # 6. Croissance et performances financières
            "Croissance_trimestrielle_benefices": get_numeric(info, "earningsQuarterlyGrowth"),
            "Benefice_net_actions_ordinaires": get_numeric(info, "netIncomeToCommon"),
            "BPA_historique": get_numeric(info, "trailingEps"),
            "BPA_previsionnel": get_numeric(info, "forwardEps"),
            "Croissance_benefices": get_numeric(info, "earningsGrowth"),
            "Croissance_chiffre_d_affaires": get_numeric(info, "revenueGrowth"),
            "Marges_brutes": get_numeric(info, "grossMargins"),
            "Marges_EBITDA": get_numeric(info, "ebitdaMargins"),
            "Marges_operationnelles": get_numeric(info, "operatingMargins"),
            "Rendement_actifs": get_numeric(info, "returnOnAssets"),
            "Rendement_capitaux_propres": get_numeric(info, "returnOnEquity"),

            # 7. Situation financière et liquidité
            "Tresorerie_totale": get_numeric(info, "totalCash"),
            "Tresorerie_par_action": get_numeric(info, "totalCashPerShare"),
            "Dette_totale": get_numeric(info, "totalDebt"),
            "Ratio_dette_capitaux_propres": get_numeric(info, "debtToEquity"),
            "Valeur_comptable": get_numeric(info, "bookValue"),
            "Ratio_liquidite_immediate": get_numeric(info, "quickRatio"),
            "Ratio_liquidite_courante": get_numeric(info, "currentRatio"),
            "Benefice_brut": get_numeric(info, "grossProfits"),
            "Flux_de_tresorerie_dispo": get_numeric(info, "freeCashflow"),
            "Flux_de_tresorerie_exploitation": get_numeric(info, "operatingCashflow"),

            # 8. Objectifs et recommandations des analystes
            "Objectif_prix_eleve": get_numeric(info, "targetHighPrice"),
            "Objectif_prix_bas": get_numeric(info, "targetLowPrice"),
            "Prix_cible_moyen": get_numeric(info, "targetMeanPrice"),
            "Prix_cible_median": get_numeric(info, "targetMedianPrice"),
            "Moyenne_des_recommandations": get_numeric(info, "recommendationMean"),
            "Recommandation_cle": get_text(info, "recommendationKey"),
            "Nombre_d_avis_analystes": get_numeric(info, "numberOfAnalystOpinions"),

            # 9. Historique et fractionnement des actions
            "Dernier_split": get_text(info, "lastSplitFactor"),
            "Date_dernier_split": get_split_date(info.get("lastSplitDate")),
            "Variation_52_semaines": get_numeric(info, "52WeekChange"),

            # 10. Indicateurs de risque et volatilité
            "Beta": get_numeric(info, "beta"),
            "PER_historique": get_numeric(info, "trailingPE"),
            "PER_previsionnel": get_numeric(info, "forwardPE"),
            "Ratio_PEG_historique": get_numeric(info, "trailingPegRatio"),

            # Date de collecte
            "Date_de_collecte": datetime.now()
        }

        return stock_data

    except Exception:
        return None

def save_to_database(data):
    """Sauvegarde les données dans PostgreSQL"""
    try:
        with get_db() as db:
            try:
                stock_entry = StockData(**data)
                db.add(stock_entry)
                db.commit()
                logger.info(f"✓ {data['Ticker']} : OK")
                return True
            except SQLAlchemyError:
                db.rollback()
                logger.error(f"✗ {data['Ticker']} : Échec")
                return False
    except Exception:
        return False

def main():
    try:
        # Lecture du fichier de tickers
        try:
            df_tickers = pd.read_excel(EXCEL_FILE)
            if df_tickers.empty:
                logger.error("Fichier de tickers vide")
                return
            logger.info(f"Démarrage : {len(df_tickers)} tickers à traiter\n")
        except Exception as e:
            logger.error(f"Erreur lecture fichier tickers: {str(e)}")
            return

        success_count = 0
        error_count = 0

        # Traitement de chaque ticker
        for index, row in df_tickers.iterrows():
            try:
                ticker = str(row['stock_ticker']).strip()
                if not ticker:
                    continue

                # Tentatives avec retry
                retries = 0
                while retries < MAX_RETRIES:
                    stock_data = collect_stock_data(ticker)
                    if stock_data:
                        if save_to_database(stock_data):
                            success_count += 1
                            break
                    retries += 1
                    if retries < MAX_RETRIES:
                        time.sleep(RETRY_DELAY)

                if retries == MAX_RETRIES:
                    error_count += 1

                time.sleep(RETRY_DELAY)  # Pause entre chaque ticker

            except Exception:
                error_count += 1
                continue

        # Rapport final
        logger.info(f"\n=== Rapport Final ===")
        logger.info(f"Total traité : {success_count + error_count}")
        logger.info(f"Succès : {success_count}")
        logger.info(f"Erreurs : {error_count}")

    except KeyboardInterrupt:
        logger.info("\nCollecte interrompue par l'utilisateur")
        logger.info(f"Succès : {success_count}, Erreurs : {error_count}")
    except Exception as e:
        logger.error(f"Erreur générale: {str(e)}")

if __name__ == "__main__":
    main()