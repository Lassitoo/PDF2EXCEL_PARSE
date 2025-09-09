"""
Script pour lister tous les modèles Groq disponibles
"""

from groq import Groq
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()


def list_available_models():
    """Liste tous les modèles Groq disponibles."""

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        print("❌ ERREUR: Clé API Groq manquante!")
        print("Créez un fichier .env avec: GROQ_API_KEY=votre_clé")
        return

    try:
        print("🔍 Connexion à Groq...")
        client = Groq(api_key=api_key)

        print("📡 Récupération de la liste des modèles...")
        models = client.models.list()

        print("\n✅ MODÈLES GROQ DISPONIBLES:")
        print("=" * 50)

        for i, model in enumerate(models.data, 1):
            print(f"{i:2d}. {model.id}")
            if hasattr(model, 'created'):
                print(f"    Créé: {model.created}")
            if hasattr(model, 'owned_by'):
                print(f"    Propriétaire: {model.owned_by}")
            print()

        print(f"📊 Total: {len(models.data)} modèles disponibles")

        # Suggestions basées sur les noms courants
        print("\n💡 SUGGESTIONS POUR VOTRE APPLICATION:")
        print("=" * 50)

        recommended = []
        for model in models.data:
            model_id = model.id.lower()
            if 'llama' in model_id and ('70b' in model_id or '8b' in model_id):
                recommended.append(model.id)
            elif 'mixtral' in model_id:
                recommended.append(model.id)
            elif 'gemma' in model_id:
                recommended.append(model.id)

        if recommended:
            print("🎯 Modèles recommandés pour l'extraction de données:")
            for i, model in enumerate(recommended, 1):
                print(f"  {i}. {model}")

        print(f"\n📋 Pour utiliser un modèle, copiez son nom exact dans config.py")
        print(f"Exemple: MODEL_NAME = \"{models.data[0].id if models.data else 'model_name'}\"")

    except Exception as e:
        print(f"❌ ERREUR: {str(e)}")
        print("Vérifiez votre clé API et votre connexion internet.")


if __name__ == "__main__":
    list_available_models()