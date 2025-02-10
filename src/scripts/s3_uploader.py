import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.config.database import get_db
from dotenv import load_dotenv
import boto3
import pandas as pd
from datetime import datetime

load_dotenv()  # Chargement des variables d'environnement

def upload_to_s3():
    try:
        # Utiliser get_db au lieu de créer une nouvelle connexion
        with get_db() as db:
            # Récupération des données
            query = "SELECT * FROM stock_data"
            df = pd.read_sql(query, db.bind)
            
            # Nom du fichier avec date
            today = datetime.now().strftime('%Y-%m-%d')
            filename = f'stock_data_{today}.csv'
            
            # Sauvegarde temporaire
            temp_path = os.path.join('data', 'temp', filename)
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            df.to_csv(temp_path, index=False)
            
            # Upload vers S3
            s3 = boto3.client('s3',
                           aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                           aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'))
            
            s3.upload_file(
                temp_path, 
                os.getenv('AWS_BUCKET_NAME'),
                f'stocks/{filename}'
            )
            
            # Nettoyage
            os.remove(temp_path)
            print(f"✓ Données uploadées avec succès : {filename}")
            
    except Exception as e:
        print(f"✗ Erreur lors de l'upload : {str(e)}")

if __name__ == "__main__":
    upload_to_s3()