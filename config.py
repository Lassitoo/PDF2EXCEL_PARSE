import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Nom du modèle local Ollama
MODEL_NAME = "llama3.1:8b-instruct-q4_K_M"

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

# Prompt système amélioré
EXTRACTION_PROMPT = """
You are an expert in extracting company information from documents. 
The provided PDF text contains information in both **English** and **Turkish**.
⚠️ IMPORTANT: Only extract information written in **English**. Ignore Turkish text.

Your task is to extract ALL companies mentioned in the text and return them in a **strict JSON format**. 
Do not add any explanation or text outside of the JSON. 
The JSON must be valid and parsable.

Fields to extract:
1. Company : The company name
2. Product Group : The product group or business sector
3. Country : The country where the company is located
4. Address : The full company address
5. Phone : The phone number
6. Email : The email address
7. Website : The company website
8. Brands : The brands associated with the company

Rules:
- If a field is missing, use "N/A"
- Return the result as a JSON **array** of objects, even if there is only one company
- Escape special characters properly (no invalid backslashes)
- Do not include any commentary, explanations, or markdown formatting
- Always include ALL companies found in the text

Example output:
[
  {
    "Company": "ABC Pharma Ltd",
    "Product Group": "Pharmaceuticals",
    "Country": "United Kingdom",
    "Address": "123 Oxford Street, London, UK",
    "Phone": "+44 20 1234 5678",
    "Email": "info@abcpharma.com",
    "Website": "www.abcpharma.com",
    "Brands": "BrandA, BrandB"
  },
  {
    "Company": "XYZ Medical",
    "Product Group": "Medical Devices",
    "Country": "Germany",
    "Address": "Hauptstrasse 45, Berlin, Germany",
    "Phone": "+49 30 9876 5432",
    "Email": "contact@xyzmedical.de",
    "Website": "www.xyzmedical.de",
    "Brands": "N/A"
  }
]

Now extract all companies in the following text:
"""
