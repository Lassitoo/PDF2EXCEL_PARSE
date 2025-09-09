import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configuration Groq
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_NAME = "llama-3.3-70b-versatile"  # ou "llama3-8b-8192" pour une version plus rapide

# Configuration des colonnes Excel
EXCEL_COLUMNS = [
    "Company",
    "Product Group",
    "Country",
    "Address",
    "Phone",
    "Email",
    "Website",
    "Brands"
]

# Prompt système pour Groq
EXTRACTION_PROMPT = """
Vous êtes un expert en extraction d'informations d'entreprise. Analysez le texte PDF fourni et extrayez UNIQUEMENT les informations suivantes :

1. Company : Le nom de l'entreprise/société
2. Product Group : Le groupe de produits ou secteur d'activité
3. Country : Le pays où se trouve l'entreprise
4. Address : L'adresse complète de l'entreprise
5. Phone : Le numéro de téléphone
6. Email : L'adresse email
7. Website : Le site web de l'entreprise
8. Brands : Les marques associées à l'entreprise

INSTRUCTIONS IMPORTANTES :
- Si une information n'est pas trouvée, répondez "N/A"
- Répondez UNIQUEMENT au format JSON suivant :
{
  "Company": "nom_entreprise",
  "Product Group": "groupe_produit",
  "Country": "pays",
  "Address": "adresse_complete",
  "Phone": "numero_telephone",
  "Email": "email",
  "Website": "site_web",
  "Brands": "marques_separees_par_virgules"
}

- Ne fournissez AUCUNE explication supplémentaire
- Le JSON doit être valide et parsable
- Si plusieurs entreprises sont trouvées, créez un array JSON avec plusieurs objets

Texte à analyser :
"""