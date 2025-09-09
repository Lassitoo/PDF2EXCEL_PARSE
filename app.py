import streamlit as st
from datetime import datetime
from io import BytesIO

# Imports locaux
from config import MODEL_NAME, EXTRACTION_PROMPT, EXCEL_COLUMNS
from utils.pdf_processor import extract_text_from_pdf, chunk_text
from utils.excel_exporter import create_excel_from_data, validate_and_clean_data, display_preview
from utils.ollama_utils import extract_with_ollama

# Configuration de la page
st.set_page_config(
    page_title="PDF to Excel Extractor",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    """Fonction principale de l'application."""
    st.title("📄➡️📊 PDF to Excel Extractor")
    st.markdown("### Extrayez automatiquement les informations d'entreprise depuis vos PDF")

    # Sidebar pour la configuration
    st.sidebar.title("⚙️ Configuration")
    st.sidebar.subheader("📋 Champs extraits")
    for field in EXCEL_COLUMNS:
        st.sidebar.text(f"• {field}")

    # Zone principale
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📁 Upload du PDF")

        uploaded_file = st.file_uploader(
            "Sélectionnez votre fichier PDF",
            type=['pdf'],
            help="Uploadez un fichier PDF contenant des informations d'entreprise"
        )

        if uploaded_file:
            file_details = {
                "Nom du fichier": uploaded_file.name,
                "Taille": f"{uploaded_file.size / 1024:.2f} KB",
                "Type": uploaded_file.type
            }
            st.info("ℹ️ Fichier uploadé avec succès !")
            with st.expander("Détails du fichier"):
                for key, value in file_details.items():
                    st.text(f"{key}: {value}")

    with col2:
        st.subheader("🎯 Actions")

        if uploaded_file:
            if st.button("🚀 Extraire les données", type="primary", use_container_width=True):
                with st.spinner("Traitement en cours..."):

                    # 1. Extraire le texte du PDF
                    st.info("📖 Extraction du texte du PDF...")
                    pdf_text = extract_text_from_pdf(uploaded_file)

                    if pdf_text:
                        st.success("✅ Texte extrait avec succès !")

                        # Aperçu texte
                        with st.expander("👀 Aperçu du texte extrait"):
                            st.text_area(
                                "Texte (premiers 1000 caractères)",
                                pdf_text[:1000] + "..." if len(pdf_text) > 1000 else pdf_text,
                                height=200
                            )

                        # 2. Découper le texte en chunks
                        text_chunks = chunk_text(pdf_text)
                        st.info(f"📄 Texte divisé en {len(text_chunks)} partie(s)")

                        # 3. Traiter avec Ollama local
                        st.info("🤖 Traitement avec Ollama local...")
                        extracted_data = extract_with_ollama(text_chunks)

                        if extracted_data:
                            st.success(f"✅ {len(extracted_data)} entreprise(s) trouvée(s) !")

                            # 4. Aperçu des données
                            display_preview(extracted_data)

                            # 5. Créer le fichier Excel
                            st.info("📊 Création du fichier Excel...")
                            excel_buffer = create_excel_from_data(extracted_data)

                            if excel_buffer:
                                st.success("✅ Fichier Excel créé avec succès !")

                                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                                filename = f"extracted_data_{timestamp}.xlsx"

                                st.download_button(
                                    label="💾 Télécharger le fichier Excel",
                                    data=excel_buffer.getvalue(),
                                    file_name=filename,
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    use_container_width=True
                                )
                        else:
                            st.warning("⚠️ Aucune donnée n'a pu être extraite.")
                    else:
                        st.error("❌ Impossible d'extraire le texte du PDF.")
        else:
            st.warning("📁 Veuillez d'abord uploader un PDF")

    # Section d'aide
    st.markdown("---")
    st.subheader("💡 Comment utiliser cette application")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        **1️⃣ Configuration**
        - Assurez-vous que votre modèle Ollama est installé et local
        - Installez les dépendances Python nécessaires
        """)

    with col2:
        st.markdown("""
        **2️⃣ Upload & Extraction**
        - Uploadez votre PDF
        - Cliquez sur "Extraire"
        - Attendez le traitement
        """)

    with col3:
        st.markdown("""
        **3️⃣ Téléchargement**
        - Vérifiez l'aperçu
        - Téléchargez le Excel
        - Utilisez vos données !
        """)

if __name__ == "__main__":
    main()
