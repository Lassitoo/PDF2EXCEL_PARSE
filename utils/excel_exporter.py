import pandas as pd
import streamlit as st
from io import BytesIO
from typing import List, Dict
import json


def create_excel_from_data(extracted_data: List[Dict]) -> BytesIO:
    """
    Crée un fichier Excel à partir des données extraites.

    Args:
        extracted_data: Liste de dictionnaires contenant les données extraites

    Returns:
        BytesIO: Fichier Excel en mémoire
    """
    try:
        # Créer un DataFrame à partir des données
        df = pd.DataFrame(extracted_data)

        # Créer un buffer en mémoire
        excel_buffer = BytesIO()

        # Créer le fichier Excel
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Extracted_Data', index=False)

            # Ajuster la largeur des colonnes
            worksheet = writer.sheets['Extracted_Data']
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter

                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass

                adjusted_width = min(max_length + 2, 50)  # Maximum 50 caractères
                worksheet.column_dimensions[column_letter].width = adjusted_width

        excel_buffer.seek(0)
        return excel_buffer

    except Exception as e:
        st.error(f"Erreur lors de la création du fichier Excel : {str(e)}")
        return None


def validate_and_clean_data(raw_data: str) -> List[Dict]:
    """
    Valide et nettoie les données JSON reçues de Groq.

    Args:
        raw_data: Données JSON brutes de Groq

    Returns:
        List[Dict]: Données nettoyées et validées
    """
    try:
        # Essayer de parser le JSON
        if raw_data.startswith('```json'):
            raw_data = raw_data.replace('```json', '').replace('```', '').strip()

        # Parser le JSON
        parsed_data = json.loads(raw_data)

        # Si c'est un seul objet, le convertir en liste
        if isinstance(parsed_data, dict):
            parsed_data = [parsed_data]

        # Valider et nettoyer chaque entrée
        cleaned_data = []
        required_fields = ["Company", "Product Group", "Country", "Address", "Phone", "Email", "Website", "Brands"]

        for entry in parsed_data:
            cleaned_entry = {}
            for field in required_fields:
                value = entry.get(field, "N/A")
                # Nettoyer la valeur
                if value is None or value == "" or str(value).lower() in ["null", "none", ""]:
                    cleaned_entry[field] = "N/A"
                else:
                    cleaned_entry[field] = str(value).strip()

            cleaned_data.append(cleaned_entry)

        return cleaned_data

    except json.JSONDecodeError as e:
        st.error(f"Erreur de parsing JSON : {str(e)}")
        st.error(f"Données reçues : {raw_data[:500]}...")
        return []
    except Exception as e:
        st.error(f"Erreur lors du nettoyage des données : {str(e)}")
        return []


def display_preview(data: List[Dict]):
    """
    Affiche un aperçu des données extraites dans Streamlit.

    Args:
        data: Données à afficher
    """
    if not data:
        st.warning("Aucune donnée à afficher.")
        return

    st.subheader("📊 Aperçu des données extraites")

    # Créer un DataFrame pour l'affichage
    df = pd.DataFrame(data)

    # Afficher les statistiques
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Nombre d'entreprises", len(data))
    with col2:
        completed_fields = sum(1 for entry in data for value in entry.values() if value != "N/A")
        total_fields = len(data) * len(data[0]) if data else 0
        completion_rate = (completed_fields / total_fields * 100) if total_fields > 0 else 0
        st.metric("Taux de complétion", f"{completion_rate:.1f}%")
    with col3:
        unique_countries = len(set(entry.get("Country", "N/A") for entry in data if entry.get("Country") != "N/A"))
        st.metric("Pays uniques", unique_countries)

    # Afficher le tableau
    st.dataframe(df, use_container_width=True)