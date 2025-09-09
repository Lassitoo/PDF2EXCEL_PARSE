import PyPDF2
import streamlit as st
from typing import Optional


def extract_text_from_pdf(pdf_file) -> Optional[str]:
    """
    Extrait le texte d'un fichier PDF uploadé via Streamlit.
    """
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        total_pages = len(pdf_reader.pages)

        progress_bar = st.progress(0)
        status_text = st.empty()

        for page_num, page in enumerate(pdf_reader.pages):
            progress = (page_num + 1) / total_pages
            progress_bar.progress(progress)
            status_text.text(f"Extraction de la page {page_num + 1}/{total_pages}")
            page_text = page.extract_text()
            text += page_text + "\n"

        progress_bar.empty()
        status_text.empty()

        if not text.strip():
            st.error("Aucun texte n'a pu être extrait du PDF.")
            return None

        return text.strip()

    except Exception as e:
        st.error(f"Erreur lors de l'extraction du PDF : {str(e)}")
        return None


def chunk_text(text: str, max_chunk_size: int = 4000) -> list:
    """
    Divise le texte en chunks plus petits pour éviter les pertes d'information.
    """
    if len(text) <= max_chunk_size:
        return [text]

    chunks = []
    words = text.split()
    current_chunk = []
    current_size = 0

    for word in words:
        word_size = len(word) + 1
        if current_size + word_size > max_chunk_size and current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_size = word_size
        else:
            current_chunk.append(word)
            current_size += word_size

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks
