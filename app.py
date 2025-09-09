import streamlit as st
import json
from groq import Groq
from datetime import datetime
import time

# Imports locaux
from config import GROQ_API_KEY, MODEL_NAME, EXTRACTION_PROMPT
from utils.pdf_processor import extract_text_from_pdf, chunk_text
from utils.excel_exporter import create_excel_from_data, validate_and_clean_data, display_preview

# Configuration de la page
st.set_page_config(
    page_title="PDF to Excel Extractor",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)


def init_groq_client():
    """Initialise le client Groq avec la clé API."""
    if not GROQ_API_KEY:
        st.error("❌ Clé API Groq manquante. Veuillez configurer GROQ_API_KEY dans votre fichier .env")
        st.stop()

    return Groq(api_key=GROQ_API_KEY)


def extract_with_groq(client, text_chunks):
    """Extrait les informations en utilisant Groq LLama3."""

    all_extracted_data = []

    # Créer une barre de progression pour le traitement Groq
    progress_bar = st.progress(0)
    status_text = st.empty()

    for i, chunk in enumerate(text_chunks):
        try:
            # Mettre à jour la progression
            progress = (i + 1) / len(text_chunks)
            progress_bar.progress(progress)
            status_text.text(f"Traitement avec Groq... Chunk {i + 1}/{len(text_chunks)}")

            # Préparer le prompt complet
            full_prompt = EXTRACTION_PROMPT + chunk

            # Appeler l'API Groq
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )

            # Extraire la réponse
            response_text = response.choices[0].message.content.strip()

            # Valider et nettoyer les données
            chunk_data = validate_and_clean_data(response_text)

            if chunk_data:
                all_extracted_data.extend(chunk_data)

            # Petite pause pour éviter les rate limits
            time.sleep(0.5)

        except Exception as e:
            st.error(f"Erreur lors du traitement du chunk {i + 1} : {str(e)}")
            continue

    # Nettoyer la barre de progression
    progress_bar.empty()
    status_text.empty()

    return all_extracted_data


def main():
    """Fonction principale de l'application."""

    # Titre et description
    st.title("📄➡️📊 PDF to Excel Extractor")
    st.markdown("### Extrayez automatiquement les informations d'entreprise depuis vos PDF")

    # Sidebar pour la configuration
    st.sidebar.title("⚙️ Configuration")

    # Vérification de la clé API
    if GROQ_API_KEY:
        st.sidebar.success("✅ Clé API Groq configurée")
    else:
        st.sidebar.error("❌ Clé API Groq manquante")
        st.sidebar.markdown("Créez un fichier `.env` avec : `GROQ_API_KEY=votre_clé`")

    # Informations sur les champs extraits
    st.sidebar.subheader("📋 Champs extraits")
    fields = ["Company", "Product Group", "Country", "Address", "Phone", "Email", "Website", "Brands"]
    for field in fields:
        st.sidebar.text(f"• {field}")

    # Zone principale
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("📁 Upload du PDF")

        # Upload du fichier PDF
        uploaded_file = st.file_uploader(
            "Sélectionnez votre fichier PDF",
            type=['pdf'],
            help="Uploadez un fichier PDF contenant des informations d'entreprise"
        )

        if uploaded_file is not None:
            # Afficher les informations du fichier
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

        # Bouton de traitement
        if uploaded_file is not None and GROQ_API_KEY:
            if st.button("🚀 Extraire les données", type="primary", use_container_width=True):

                with st.spinner("Traitement en cours..."):

                    # 1. Extraire le texte du PDF
                    st.info("📖 Extraction du texte du PDF...")
                    pdf_text = extract_text_from_pdf(uploaded_file)

                    if pdf_text:
                        st.success("✅ Texte extrait avec succès !")

                        # Afficher un aperçu du texte
                        with st.expander("👀 Aperçu du texte extrait"):
                            st.text_area("Texte (premiers 1000 caractères)",
                                         pdf_text[:1000] + "..." if len(pdf_text) > 1000 else pdf_text,
                                         height=200)

                        # 2. Découper le texte en chunks si nécessaire
                        text_chunks = chunk_text(pdf_text)
                        st.info(f"📄 Texte divisé en {len(text_chunks)} partie(s)")

                        # 3. Traiter avec Groq
                        st.info("🤖 Traitement avec Groq LLama3...")
                        client = init_groq_client()
                        extracted_data = extract_with_groq(client, text_chunks)

                        if extracted_data:
                            st.success(f"✅ {len(extracted_data)} entreprise(s) trouvée(s) !")

                            # 4. Afficher l'aperçu des données
                            display_preview(extracted_data)

                            # 5. Créer le fichier Excel
                            st.info("📊 Création du fichier Excel...")
                            excel_buffer = create_excel_from_data(extracted_data)

                            if excel_buffer:
                                st.success("✅ Fichier Excel créé avec succès !")

                                # Bouton de téléchargement
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
            if not uploaded_file:
                st.warning("📁 Veuillez d'abord uploader un PDF")
            if not GROQ_API_KEY:
                st.error("🔑 Configurez votre clé API Groq")

    # Section d'aide
    st.markdown("---")
    st.subheader("💡 Comment utiliser cette application")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        **1️⃣ Configuration**
        - Créez un fichier `.env`
        - Ajoutez votre clé Groq API
        - Installez les dépendances
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