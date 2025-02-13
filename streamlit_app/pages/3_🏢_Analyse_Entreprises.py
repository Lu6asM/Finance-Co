import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from utils import add_news_ticker
from stock_analyzer import StockAnalyzer

def main():
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
        st.subheader(f"Secteur: {data['Industrie']}")

        if 'Business_models' in data and data['Business_models']:
            with st.expander("📌 Business Model de l'entreprise", expanded=False):
                st.write(data['Business_models'])

        
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
                ### {data['Rendement dividende']}%
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
        tab1, tab2, tab3 = st.tabs(["📰 Actualités", "📈 Graphiques", "💰 Performance"])
        
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

        with tab3:
            st.subheader("Performance sur 52 semaines")
            perf_col1, perf_col2 = st.columns(2)
            
            with perf_col1:
                st.metric(
                    "Plus Haut",
                    f"${data['Plus haut 52 sem.']}",
                    "↗️ Maximum"
                )
            
            with perf_col2:
                st.metric(
                    "Plus Bas",
                    f"${data['Plus bas 52 sem.']}",
                    "↘️ Minimum",
                    delta_color="inverse"
                )

if __name__ == "__main__":
    main()