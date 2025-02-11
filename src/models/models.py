from sqlalchemy import Column, Integer, String, Float, DateTime, Index, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class StockData(Base):
    """Table des données boursières"""
    __tablename__ = 'stock_data'
    
    id = Column(Integer, primary_key=True)
    
    # 1. Informations générales
    Ticker = Column(String, nullable=False)
    Pays = Column(String)
    Industrie = Column(String)
    Secteur = Column(String)
    Bourse = Column(String)
    Nom_complet = Column(String)
    Devise = Column(String)
    Devise_financiere = Column(String)

    # 2. Informations sur le prix de l'action
    Cloture_precedente = Column(Float)
    Prix_d_ouverture = Column(Float)
    Plus_bas_du_jour = Column(Float)
    Plus_haut_du_jour = Column(Float)
    Cloture_precedente_marche_regulier = Column(Float)
    Prix_actuel = Column(Float)
    Plus_bas_sur_52_semaines = Column(Float)
    Plus_haut_sur_52_semaines = Column(Float)
    Moyenne_sur_50_jours = Column(Float)
    Moyenne_sur_200_jours = Column(Float)

    # 3. Indicateurs de volume et de capitalisation
    Volume = Column(Float)
    Volume_moyen = Column(Float)
    Volume_moyen_10_jours = Column(Float)
    Capitalisation_boursiere = Column(Float)
    Actions_en_circulation = Column(Float)
    Pourcentage_detenu_institutions = Column(Float)

    # 4. Ratios et valorisation
    Ratio_cours_ventes_TTM = Column(Float)
    Valeur_d_entreprise = Column(Float)
    Marges_beneficiaires = Column(Float)
    Ratio_cours_valeur_comptable = Column(Float)
    Valeur_entreprise_chiffre_d_affaires = Column(Float)
    Valeur_entreprise_EBITDA = Column(Float)

    # 5. Dividendes et rémunération des actionnaires
    Taux_de_dividende = Column(Float)
    Rendement_du_dividende = Column(Float)
    Ratio_de_distribution = Column(Float)
    Rendement_moyen_5_ans = Column(Float)
    Valeur_dernier_dividende = Column(Float)

    # 6. Croissance et performances financières
    Croissance_trimestrielle_benefices = Column(Float)
    Benefice_net_actions_ordinaires = Column(Float)
    BPA_historique = Column(Float)
    BPA_previsionnel = Column(Float)
    Croissance_benefices = Column(Float)
    Croissance_chiffre_d_affaires = Column(Float)
    Marges_brutes = Column(Float)
    Marges_EBITDA = Column(Float)
    Marges_operationnelles = Column(Float)
    Rendement_actifs = Column(Float)
    Rendement_capitaux_propres = Column(Float)

    # 7. Situation financière et liquidité
    Tresorerie_totale = Column(Float)
    Tresorerie_par_action = Column(Float)
    Dette_totale = Column(Float)
    Ratio_dette_capitaux_propres = Column(Float)
    Valeur_comptable = Column(Float)
    Ratio_liquidite_immediate = Column(Float)
    Ratio_liquidite_courante = Column(Float)
    Benefice_brut = Column(Float)
    Flux_de_tresorerie_dispo = Column(Float)
    Flux_de_tresorerie_exploitation = Column(Float)

    # 8. Objectifs et recommandations des analystes
    Objectif_prix_eleve = Column(Float)
    Objectif_prix_bas = Column(Float)
    Prix_cible_moyen = Column(Float)
    Prix_cible_median = Column(Float)
    Moyenne_des_recommandations = Column(Float)
    Recommandation_cle = Column(String)
    Nombre_d_avis_analystes = Column(Integer)

    # 9. Historique et fractionnement des actions
    Dernier_split = Column(String)
    Date_dernier_split = Column(DateTime)
    Variation_52_semaines = Column(Float)

    # 10. Indicateurs de risque et volatilité
    Beta = Column(Float)
    PER_historique = Column(Float)
    PER_previsionnel = Column(Float)
    Ratio_PEG_historique = Column(Float)

    # Relation avec PriorityStocks (optionnel si besoin)
    priority_stock = relationship("PriorityStocks", back_populates="stock_data", uselist=False)

class PriorityStocks(Base):
    """Table pour le suivi temps réel des 55 tickers prioritaires"""
    __tablename__ = 'priority_stocks'

    id = Column(Integer, primary_key=True)
    Ticker = Column(String, nullable=False)
    Nom_complet = Column(String)
    Prix_actuel = Column(Float)
    Volume = Column(Float)
    Variation_jour = Column(Float)  # Pour le % de variation
    Date_collecte = Column(DateTime, default=lambda: datetime.utcnow())

    # Clé étrangère pour relier aux données principales
    stock_data_id = Column(Integer, ForeignKey('stock_data.id'), nullable=True)
    
    # Relation avec StockData
    stock_data = relationship("StockData", back_populates="priority_stock")

    __table_args__ = (
        Index('idx_priority_ticker_date', 'Ticker', 'Date_collecte'),
    )

    def __repr__(self):
        return f"<PriorityStocks(Ticker='{self.Ticker}', Prix_actuel={self.Prix_actuel}, Date_collecte='{self.Date_collecte}')>"