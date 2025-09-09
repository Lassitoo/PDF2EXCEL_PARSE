import PyPDF2
import streamlit as st
from typing import Optional


def extract_text_from_pdf(pdf_file) -> Optional[str]:
    """
    Extrait le texte d'un fichier PDF uploadé via Streamlit.

    Args:
        pdf_file: Fichier PDF uploadé via st.file_uploader

    Returns:
        str: Texte extrait du PDF ou None si erreur
    """
    try:
        # Lire le fichier PDF
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        # Extraire le texte de toutes les pages
        text = ""
        total_pages = len(pdf_reader.pages)

        # Créer une barre de progression pour l'extraction
        progress_bar = st.progress(0)
        status_text = st.empty()

        for page_num, page in enumerate(pdf_reader.pages):
            # Mettre à jour la progression
            progress = (page_num + 1) / total_pages
            progress_bar.progress(progress)
            status_text.text(f"Extraction de la page {page_num + 1}/{total_pages}")

            # Extraire le texte de la page
            page_text = page.extract_text()
            text += page_text + "\n"

        # Nettoyer la barre de progression
        progress_bar.empty()
        status_text.empty()

        if not text.strip():
            st.error("Aucun texte n'a pu être extrait du PDF.")
            return None

        return text.strip()

    except Exception as e:
        st.error(f"Erreur lors de l'extraction du PDF : {str(e)}")
        return None


def chunk_text(text: str, max_chunk_size: int = 8000) -> list:
    """
    Divise le texte en chunks plus petits pour éviter les limites de l'API.

    Args:
        text: Texte à diviser
        max_chunk_size: Taille maximum de chaque chunk

    Returns:
        list: Liste des chunks de texte
    """
    if len(text) <= max_chunk_size:
        return [text]

    chunks = []
    words = text.split()
    current_chunk = []
    current_size = 0

    for word in words:
        word_size = len(word) + 1  # +1 pour l'espace

        if current_size + word_size > max_chunk_size and current_chunk:
            # Ajouter le chunk actuel à la liste
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_size = word_size
        else:
            current_chunk.append(word)
            current_size += word_size

    # Ajouter le dernier chunk s'il n'est pas vide
    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks