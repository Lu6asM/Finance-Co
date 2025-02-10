from src.config.database import init_db, test_db_connection, get_db
import logging
from sqlalchemy import text

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def clean_database():
    """Nettoie la base de données"""
    try:
        with get_db() as db:
            # Ne supprime que la table stock_data
            db.execute(text("DROP TABLE IF EXISTS stock_data CASCADE"))
            db.commit()
            logger.info("Table stock_data supprimée avec succès")
    except Exception as e:
        logger.error(f"Erreur lors du nettoyage de la base: {str(e)}")

def verify_tables():
    """Vérifie que la table a été créée correctement"""
    try:
        with get_db() as db:
            expected_tables = {'stock_data'}
            
            result = db.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            
            existing_tables = {row[0] for row in result}
            
            missing_tables = expected_tables - existing_tables
            if missing_tables:
                logger.warning(f"Tables manquantes: {missing_tables}")
                return False
                
            logger.info("Table stock_data créée avec succès")
            return True
            
    except Exception as e:
        logger.error(f"Erreur lors de la vérification des tables: {str(e)}")
        return False

def main():
    """Script principal d'initialisation de la base de données"""
    logger.info("Début de l'initialisation de la base de données...")
    
    if not test_db_connection():
        logger.error("Impossible de se connecter à la base de données")
        return
    
    try:
        clean_database()
        init_db()
        
        if verify_tables():
            logger.info("Initialisation de la base de données terminée avec succès")
        else:
            logger.error("La table n'a pas été créée correctement")
        
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation: {str(e)}")

if __name__ == "__main__":
    main()