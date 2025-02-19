import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from utils import add_news_ticker, render_footer
from stock_analyzer import StockAnalyzer

def configure_page():
    st.set_page_config(
        page_title="Komorebi Investments",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Style CSS harmonisé pour toute l'application
    st.markdown("""
        <style>
        
        /* Style des cartes */
        .custom-card {
            background-color: #ffffff;
            padding: 1.5rem;
            border-radius: 0.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
            transition: transform 0.2s ease;
        }
        .custom-card:hover {
            transform: translateY(-2px);
        }
        
        /* Style des boutons Streamlit */
        .stButton button {
            width: 100%;
            background-color: #f8f9fa;
            border: 1px solid #e9ecef;
            padding: 1rem 2rem;
            transition: all 0.2s ease;
        }
        .stButton button:hover {
            background-color: #e9ecef;
            transform: translateY(-2px);
        }
        /* Enlève le surlignage bleu par défaut */
        .stButton button:focus {
            outline: none;
            box-shadow: none;
        }
        
        /* Style des métriques */
        .metric-container {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
        }
        
        /* Style du ticker */
        .ticker-container {
            background-color: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(5px);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        /* Style des onglets */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 1rem 2rem;
        }
        </style>
    """, unsafe_allow_html=True)

def display_business_model(data):
    """Affiche le business model de manière structurée"""
    if 'Business_models' in data and data['Business_models']:
        business_model = data['Business_models']
        
        # Diviser le texte en paragraphes
        paragraphs = [p.strip() for p in business_model.split('.') if p.strip()]
        
        # Sections prédéfinies avec leurs mots-clés
        sections = {
            "activites": set(["activité", "chiffre d'affaires", "revenus", "division", "représente"]),
            "geographie": set(["réalise", "présence", "géographique", "mondial"]),
            "forces": set(["succès", "force", "position", "leader", "avantage"]),
            "risques": set(["risque", "défi", "menace", "concurrence", "faiblesse"])
        }
        
        # Classification du contenu
        sorted_content = {
            "activites": [],
            "geographie": [],
            "forces": [],
            "risques": []
        }
        
        # Trier les paragraphes
        for p in paragraphs:
            p = p.strip()
            p_lower = p.lower()
            classified = False
            
            for section, keywords in sections.items():
                if any(keyword in p_lower for keyword in keywords):
                    sorted_content[section].append(p)
                    classified = True
                    break
            
            if not classified and p:
                sorted_content["activites"].append(p)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Business Model")
            for p in sorted_content["activites"]:
                st.markdown(f"- {p}.")
            
            if sorted_content["geographie"]:
                st.markdown("#### 🌍 Présence géographique")
                for p in sorted_content["geographie"]:
                    st.markdown(f"- {p}.")
        
        with col2:
            if sorted_content["forces"]:
                st.markdown("#### 💪 Forces & Avantages")
                for p in sorted_content["forces"]:
                    st.markdown(f"- {p}.")
            
            if sorted_content["risques"]:
                st.markdown("#### ⚠️ Risques & Défis")
                for p in sorted_content["risques"]:
                    st.markdown(f"- {p}.")

    st.markdown("---")


def main():
    configure_page()
    add_news_ticker()
    st.title("🏢 Analyse des Entreprises")
    
    analyzer = StockAnalyzer()

    selected_company = st.selectbox(
        "Sélectionnez une entreprise",
        options=list(analyzer.tickers_dict.keys()),
        key="company_selector"
    )

    if selected_company:
        ticker = analyzer.tickers_dict[selected_company]
        data = analyzer.get_stock_data(ticker)
        
        st.header(data['Nom'])
        st.subheader(f"{data['Industrie']}")

        if 'Business_models' in data and data['Business_models']:
            display_business_model(data)


        
        # KPIs en petites cartes
        kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

        with kpi1:
            st.info(
                f"""
                **🎯 Valorisation**
                ### {data['PER historique']:.1f}
                PER
                """
            )

        with kpi2:
            st.warning(
                f"""
                **💰 Rendement**
                ### {data['Rendement dividende'] / 100}%
                Dividende
                """
            )

        with kpi3:
            variation = data['Variation']
            color = "success" if variation >= 0 else "error"
            getattr(st, color)(
                f"""
                **📈 Performance**
                ### {variation:+.2f}%
                Variation
                """
            )

        with kpi4:
            st.warning(
                f"""
                **💵 BPA**
                ### ${data['BPA historique']}
                Par action
                """
            )

        with kpi5:
            st.info(
                f"""
                **🏢 Capitalisation**
                ### ${data['Cap. Boursière (Mds)']}B
                Milliards $
                """
            )

        # Onglets dans le nouvel ordre
        tab1, tab2 = st.tabs(["📰 Actualités", "💰 Performance"])
        
        with tab1:
            news = analyzer.get_company_news(selected_company, ticker)
            
            if news:
                for article in news:
                    with st.expander(article['title'], expanded=False):
                        cols = st.columns([1, 1])
                        with cols[0]:
                            st.caption(f"Source: {article['source']}")
                        with cols[1]:
                            st.caption(f"Date: {article['date']}")
                        st.markdown(f"[Lire l'article]({article['link']})")
            else:
                st.info("Aucune actualité récente disponible.")

        with tab2:

            st.subheader("Performance sur 52 semaines")
            perf_col1, perf_col2, perf_col3 = st.columns(3)
            
            with perf_col1:
                prix_moyen = (data['Plus haut 52 sem.'] + data['Plus bas 52 sem.']) / 2  # Calcul moyenne
                st.metric(
                    "Prix Moyen",
                    f"${round(prix_moyen, 2)}",  # Arrondi à 2 décimales
                )
            
            with perf_col2:
                st.metric(
                    "Plus Haut",
                    f"${data['Plus haut 52 sem.']}",
                    round(data['Plus haut 52 sem.'] - data['Plus bas 52 sem.'], 2)
                )

            with perf_col3:
                st.metric(
                    "Plus Bas",
                    f"${data['Plus bas 52 sem.']}",
                    round(data['Plus bas 52 sem.'] - data['Plus haut 52 sem.'], 2)
                )

            periode = st.radio(
                "Période",
                ["1 mois", "6 mois", "1 an"],
                horizontal=True
            )
            
            periods_map = {
                "1 mois": "1mo",
                "6 mois": "6mo",
                "1 an": "1y"
            }
            
            hist = yf.Ticker(ticker).history(period=periods_map[periode])
            
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=hist.index,
                open=hist['Open'],
                high=hist['High'],
                low=hist['Low'],
                close=hist['Close'],
                name=ticker
            ))
            
            fig.update_layout(
                title=f"Evolution du cours - {periode}",
                yaxis_title="Prix ($)",
                xaxis_title="Date",
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)

    render_footer()

if __name__ == "__main__":
    main()