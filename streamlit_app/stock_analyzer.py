import streamlit as st
import pandas as pd
import yfinance as yf
import feedparser
from datetime import datetime, timedelta
from urllib.parse import quote_plus
import time

class StockAnalyzer:
    def __init__(self):
        self.tickers_dict = {
            "ASML Holding": "ASML.AS", "AT&T": "T", "Adobe": "ADBE", "Aercap Holdings": "AER",
            "Air Products & Chemicals": "APD", "Alphabet": "GOOGL", "Amazon.com": "AMZN",
            "Bank of America": "BAC", "BioMérieux": "BIM.PA", "Bureau Veritas": "BVI.PA",
            "CAE": "CAE", "Canadian Pacific Kansas City": "CP", "Carrier Global": "CARR",
            "Christian Dior": "CDI.PA", "Compagnie Financière Richemont": "CFR.SW",
            "Corning": "GLW", "Covivio": "COV.PA", "Danone": "BN.PA", "Deere & Company": "DE",
            "Deutsche Telekom": "DTE.DE", "Elis": "ELIS.PA", "Emerson Electric": "EMR",
            "Engie": "ENGI.PA", "EssilorLuxottica": "EL.PA", "Euronext": "ENX.PA",
            "Gaztransport et Technigaz": "GTT.PA", "Groupe Bruxelles Lambert": "GBLB.BR",
            "Hitachi": "6501.T", "Hyundai Mobis": "012330.KS", "Iberdrola": "IBE.MC",
            "Intercontinental Hotels Group": "IHG.L", "International Business Machines": "IBM",
            "Komatsu": "6301.T", "Macquarie Group": "MQG.AX", "Nippon Sanso Holdings": "4091.T",
            "Publicis Groupe": "PUB.PA", "Qualcomm": "QCOM", "Roche Holding": "ROG.SW",
            "Rolls-Royce Holdings": "RR.L", "Saint-Gobain": "SGO.PA", "Siemens": "SIE.DE",
            "Stef": "STF.PA", "Straumann Holding": "STMN.SW", "Sumitomo": "8053.T",
            "Technip Energies": "TE.PA", "Tenable Holdings": "TENB", "Thales": "HO.PA",
            "Toray Industries": "3402.T", "Toyota Tsusho": "8015.T", "UBS Group": "UBSG.SW",
            "Unibail-Rodamco-Westfield": "URW.PA", "Veolia Environnement": "VIE.PA",
            "Vinci": "DG.PA", "Walmart": "WMT", "Zurich Insurance Group": "ZURN.SW"
        }
        try:
            # Charger le CSV contenant les business models
            self.stocks_data = pd.read_csv('https://raw.githubusercontent.com/thidescac25/Finance-Co/refs/heads/main/data/selected_stocks.csv')
            # Convertir les noms de colonnes en string pour éviter les problèmes de type
            self.stocks_data.columns = self.stocks_data.columns.astype(str)
        except Exception as e:
            st.error(f"Erreur lors du chargement du CSV: {e}")
            self.stocks_data = pd.DataFrame()

    @st.cache_data(ttl=300)
    def get_stock_data(_self, ticker):
        try:
            # D'abord, trouver la correspondance dans le dictionnaire
            company_name = next((name for name, t in _self.tickers_dict.items() if t == ticker), None)
            
            # Récupérer les données du CSV
            stock_info = {}
            if not _self.stocks_data.empty:
                # Chercher par ticker exact
                csv_data = _self.stocks_data[_self.stocks_data['Ticker'] == ticker]
                if csv_data.empty and company_name:
                    # Si pas trouvé, chercher par nom de l'entreprise
                    csv_data = _self.stocks_data[_self.stocks_data['Nom_complet'].str.contains(company_name, case=False, na=False)]
                
                if not csv_data.empty:
                    row = csv_data.iloc[0]
                    stock_info = {
                        "Nom": row.get('Nom_complet', company_name or ticker),
                        "Business_models": row.get('Business_models', ''),
                        "Industrie": row.get('Industrie', 'N/A'),
                        "Pays": row.get('Pays', 'N/A')
                    }
            
            # Compléter avec les données yfinance
            stock = yf.Ticker(ticker)
            info = stock.info if hasattr(stock, 'info') else {}
            hist = stock.history(period="2d")
            variation = 0
            if len(hist) >= 2:
                variation = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
            
            # Mettre à jour stock_info avec les données yfinance
            if not stock_info:
                stock_info = {
                    "Nom": info.get("longName", ticker),
                    "Business_models": "",
                    "Industrie": info.get("industry", "N/A"),
                    "Pays": info.get("country", "N/A")
                }
            
            stock_info.update({
                "Prix actuel": info.get("currentPrice", hist['Close'].iloc[-1] if not hist.empty else "N/A"),
                "Variation": round(variation, 2),
                "PER historique": info.get("trailingPE", "N/A"),
                "BPA historique": info.get("trailingEps", "N/A"),
                "Rendement dividende": round(info.get("dividendYield", 0) * 100, 2) if info.get("dividendYield") else "N/A",
                "Plus haut 52 sem.": info.get("fiftyTwoWeekHigh", "N/A"),
                "Plus bas 52 sem.": info.get("fiftyTwoWeekLow", "N/A"),
                "Cap. Boursière (Mds)": round(info.get("marketCap", 0) / 1e9, 2) if info.get("marketCap") else "N/A",
                "Analystes": info.get("numberOfAnalystOpinions", "N/A")
            })
            
            return stock_info
            
        except Exception as e:
            st.error(f"Erreur lors de la récupération des données pour {ticker}: {str(e)}")
            return {
                "Nom": ticker,
                "Prix actuel": "N/A",
                "Variation": 0,
                "PER historique": "N/A",
                "BPA historique": "N/A",
                "Rendement dividende": "N/A",
                "Plus haut 52 sem.": "N/A",
                "Plus bas 52 sem.": "N/A",
                "Cap. Boursière (Mds)": "N/A",
                "Analystes": "N/A",
                "Pays": "N/A",
                "Industrie": "N/A",
                "Business_models": ""
            }

    def get_ticker_prices(self):
        ticker_data = []
        for company, ticker in self.tickers_dict.items():
            try:
                stock = yf.Ticker(ticker)
                hist = stock.history(period="2d")
                if len(hist) >= 2:
                    current_price = hist['Close'].iloc[-1]
                    prev_price = hist['Close'].iloc[-2]
                    variation = ((current_price - prev_price) / prev_price) * 100
                    arrow = "▲" if variation >= 0 else "▼"
                    color = "#00c853" if variation >= 0 else "#ff1744"
                    ticker_data.append(f"{company}: {current_price:.2f}$ <span style='color: {color};'>({arrow} {variation:.2f}%)</span>")
            except:
                continue
        return ticker_data

    def get_company_news(self, company_name, ticker):
        company_encoded = quote_plus(f"{company_name} stock")
        ticker_encoded = quote_plus(ticker)
        rss_feeds = [
            f"https://news.google.com/rss/search?q={ticker}+stock+market&hl=en",
            f"https://www.msn.com/fr-fr/finance/rss?query={ticker}",
            f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US",
            f"https://seekingalpha.com/api/sa/combined/{ticker}.xml",
            f"https://feeds.finviz.com/rss/news.ashx?v=1&s={ticker}",
            f"https://feeds.marketwatch.com/marketwatch/realtimeheadlines?s={ticker}",
            f"https://www.benzinga.com/feeds/stock?symbols={ticker}",
            f"https://www.fool.com/feed/quoters/{ticker}",
            f"https://www.investopedia.com/feedbuilder/feed/tickers/{ticker}",
            f"https://www.barrons.com/market-data/{ticker}/feed",
            f"https://www.bloomberg.com/feeds/securities/{ticker}",
            f"https://www.reuters.com/markets/companies/{ticker}/feed"
        ]

        news_list = []
        cutoff_time = datetime.utcnow() - timedelta(hours=48)

        for feed_url in rss_feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:5]:
                    # Filtrage strict des actualités pour ne garder que celles concernant spécifiquement la valeur
                    if (company_name.lower() in entry.title.lower() or 
                        ticker.lower() in entry.title.lower() or 
                        ticker.split('.')[0].lower() in entry.title.lower()):
                        try:
                            entry_time = datetime(*entry.published_parsed[:6])
                            if entry_time >= cutoff_time:
                                news_list.append({
                                    'title': entry.title,
                                    'link': entry.link,
                                    'date': entry_time.strftime("%d/%m/%Y %H:%M"),
                                    'source': entry.source.title if hasattr(entry, 'source') else 'Source financière'
                                })
                        except (AttributeError, TypeError):
                            continue
            except Exception:
                continue

        return sorted(news_list, key=lambda x: x['date'], reverse=True)