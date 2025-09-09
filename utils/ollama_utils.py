from ollama import chat
from config import MODEL_NAME, EXTRACTION_PROMPT
from utils.excel_exporter import validate_and_clean_data, display_preview
import streamlit as st
import time
import re

def extract_with_ollama(text_chunks):
    """
    Extrait les données d'un PDF chunk par chunk en utilisant le modèle local Ollama.
    Affiche les données extraites de chaque chunk avant de passer au suivant.
    """
    all_extracted_data = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, chunk in enumerate(text_chunks):
        try:
            progress = (i + 1) / len(text_chunks)
            progress_bar.progress(progress)
            status_text.text(f"Traitement chunk {i + 1}/{len(text_chunks)} avec Ollama...")

            full_prompt = EXTRACTION_PROMPT + chunk
            response = chat(model=MODEL_NAME, messages=[{"role": "user", "content": full_prompt}])

            # Extraire le JSON du message
            try:
                response_text = response.message.content
            except AttributeError:
                response_text = str(response)

            # Récupérer uniquement le JSON
            match = re.search(r"\[.*\]", response_text, re.DOTALL)
            if match:
                response_text = match.group(0)
            else:
                response_text = "[]"

            # Valider et nettoyer le JSON
            chunk_data = validate_and_clean_data(response_text)

            if chunk_data:
                all_extracted_data.extend(chunk_data)

                # Afficher un aperçu pour ce chunk
                st.subheader(f"📄 Données extraites du chunk {i + 1}")
                display_preview(chunk_data)
            else:
                st.warning(f"Aucune donnée trouvée pour le chunk {i + 1}")

            time.sleep(0.2)  # pause pour fluidité

        except Exception as e:
            st.error(f"Erreur sur le chunk {i + 1} : {str(e)}")
            continue

    progress_bar.empty()
    status_text.empty()
    return all_extracted_data
