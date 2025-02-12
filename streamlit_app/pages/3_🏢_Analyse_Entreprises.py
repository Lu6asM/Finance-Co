import streamlit as st
import pandas as pd
from stock_analyzer import StockAnalyzer

# Configuration de la page en mode large
st.set_page_config(layout="wide")

# Styles CSS personnalisés
st.markdown("""
<style>
    .metric-box {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 5px;
        padding: 10px;
        margin: 5px;
        text-align: center;
    }
    .metric-value {
        font-size: 24px;
        font-weight: bold;
    }
    .metric-label {
        font-size: 14px;
        color: #666;
    }
    .trend-up {
        color: #00c853;
    }
    .trend-down {
        color: #ff1744;
    }
    .ticker-container {
        width: 100%;
        overflow: hidden;
        white-space: nowrap;
        background-color: #f8f9fa;
        padding: 15px 0;
        border-top: 1px solid #dee2e6;
        border-bottom: 1px solid #dee2e6;
    }
    .ticker-item {
        display: inline-block;
        padding: 0 50px;  /* Espacement horizontal */
        animation: ticker 1440s linear infinite;  /* Ralentissement x4 : 360s -> 1440s */
    }
    @keyframes ticker {
        0% { transform: translateX(100%); }
        100% { transform: translateX(-100%); }
    }
    /* Style pour séparer visuellement les éléments du ticker */
    .ticker-item > span {
        margin: 0 100px;  /* Grand espacement entre les valeurs */
        padding: 5px 15px;  /* Padding autour de chaque valeur */
        border-right: 2px solid #dee2e6;  /* Séparateur visuel */
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown("<h1 style='text-align: center; color: #1E88E5;'>Stocks News</h1>", unsafe_allow_html=True)
    
    analyzer = StockAnalyzer()
    
    # Préchargement des données du bandeau
    @st.cache_data(ttl=60)  # Cache d'1 minute pour les données du bandeau
    def load_ticker_data():
        return analyzer.get_ticker_prices()
    
    # Chargement immédiat des données du bandeau
    ticker_data = load_ticker_data()
    ticker_html = ' '.join([f"<span>{item}</span>" for item in ticker_data])
    st.markdown(f"""
    <div class="ticker-container">
        <div class="ticker-item">
            {ticker_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

    selected_company = st.selectbox(
        "Sélectionnez une entreprise",
        options=list(analyzer.tickers_dict.keys()),
        key="company_selector"
    )

    if selected_company:
        ticker = analyzer.tickers_dict[selected_company]
        data = analyzer.get_stock_data(ticker)
        
        st.markdown(f"<h2 style='color: #2c3e50; text-align: center;'>{data['Nom']}</h2>", unsafe_allow_html=True)

        # Information sur le pays et l'industrie
        st.markdown(f"""
        <div style='text-align: center; margin-bottom: 10px;'>
            <span style='color: #666;'>🏭 {data['Industrie']}</span>
        </div>
        """, unsafe_allow_html=True)

        # Prix actuel avec variation
        variation_color = "#00c853" if data['Variation'] >= 0 else "#ff1744"
        variation_arrow = "▲" if data['Variation'] >= 0 else "▼"
        st.markdown(f"""
        <div style='text-align: center; margin-bottom: 20px;'>
            <div class='metric-box' style='display: inline-block;'>
                <div class='metric-value'>
                    {data['Prix actuel']} $ 
                    <span style='color: {variation_color};'>
                        ({data['Variation']:+.2f}% {variation_arrow})
                    </span>
                </div>
                <div class='metric-label'>Prix Actuel</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

                # Métriques principales en 3 colonnes
        cols = st.columns(3)
        with cols[0]:
            st.markdown("""
            <div class='metric-box'>
                <div class='metric-value'>{}</div>
                <div class='metric-label'>PER Historique</div>
            </div>
            <div class='metric-box'>
                <div class='metric-value'>{}</div>
                <div class='metric-label'>BPA Historique</div>
            </div>
            """.format(data["PER historique"], data["BPA historique"]), unsafe_allow_html=True)
            
        with cols[1]:
            st.markdown("""
            <div class='metric-box'>
                <div class='metric-value'>{}%</div>
                <div class='metric-label'>Rendement Dividende</div>
            </div>
            <div class='metric-box'>
                <div class='metric-value'>{}</div>
                <div class='metric-label'>Capitalisation Boursière (Mds $)</div>
            </div>
            """.format(data["Rendement dividende"], data["Cap. Boursière (Mds)"]), unsafe_allow_html=True)
            
        with cols[2]:
            st.markdown("""
            <div class='metric-box'>
                <div class='metric-value'>{}</div>
                <div class='metric-label'>Analystes</div>
            </div>
            <div class='metric-box'>
                <div class='metric-value'>{}</div>
                <div class='metric-label'>Pays</div>
            </div>
            """.format(data["Analystes"], data["Pays"]), unsafe_allow_html=True)

        # Performance sur 52 semaines
        st.markdown("### 📊 Performance sur 52 Semaines")
        cols_52w = st.columns(2)
        with cols_52w[0]:
            st.markdown("""
            <div class='metric-box'>
                <div class='metric-value trend-up'>{} $</div>
                <div class='metric-label'>Plus Haut 52 Sem.</div>
            </div>
            """.format(data["Plus haut 52 sem."]), unsafe_allow_html=True)
            
        with cols_52w[1]:
            st.markdown("""
            <div class='metric-box'>
                <div class='metric-value trend-down'>{} $</div>
                <div class='metric-label'>Plus Bas 52 Sem.</div>
            </div>
            """.format(data["Plus bas 52 sem."]), unsafe_allow_html=True)

        # Actualités
        st.markdown("## 📰 Dernières actualités")
        news = analyzer.get_company_news(selected_company, ticker)

        if news:
            for article in news:
                st.markdown(f"""
                <div style='background-color: #f8f9fa; border-radius: 5px; padding: 10px; margin: 5px 0;'>
                    <div style='display: flex; justify-content: space-between;'>
                        <span style='color: #666;'>{article['source']}</span>
                        <span style='color: #666;'>{article['date']}</span>
                    </div>
                    <a href="{article['link']}" target="_blank" style='text-decoration: none; color: #1E88E5;'>
                        {article['title']}
                    </a>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.write("Aucune actualité récente disponible.")

if __name__ == "__main__":
    main()