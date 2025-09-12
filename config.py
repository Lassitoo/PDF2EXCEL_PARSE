import os
from dotenv import load_dotenv

# Charger les variables d'environnement (utile si d'autres variables sont ajoutées plus tard)
load_dotenv()

# Nom du modèle Ollama local
MODEL_NAME = "llama3.1:8b-instruct-q4_K_M"

# Colonnes Excel attendues
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

# Prompt optimisé (plus rapide, clair et strict)
EXTRACTION_PROMPT = """
Extract structured company information from the text below. 
Each company appears twice: once in Turkish and once in English.

Rules:
- Prefer English values.
- If English is missing, use the Turkish version instead of "N/A".
- Fields to extract: 
  Company, Product Group, Country, Address, Phone, Email, Website, Brands.
- Clean prefixes (Tel, Fax, Mob, Web, E-mail, Marks).
- Normalize:
  * Phone → international format if possible
  * Website → add https:// if missing
  * Email → lowercase
  * Country → English spelling if available
- Do not duplicate companies across chunks.
- If info truly does not exist in any language, use "N/A".
- Output must be ONLY a valid JSON array of objects. No explanations or text outside JSON.

Example output:
[
  {
    "Company": "1WIN GROUP LLC",
    "Product Group": "Sports Nutrition",
    "Country": "Russia",
    "Address": "350028, Krasnodar, Zhloby St., 141",
    "Phone": "+7 930 913-29-79",
    "Email": "info@1win-group.com",
    "Website": "https://www.one-win.ru",
    "Brands": "1WIN, SOLAB, DO ECO, MOVI, LIFEON"
  }
]

Now extract the companies:
"""
