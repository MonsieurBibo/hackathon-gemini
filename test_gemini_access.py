import os
from google import genai
from dotenv import load_dotenv

# Charge le fichier .env
load_dotenv()

api_key = os.environ.get("GOOGLE_API_KEY")

if not api_key:
    print("❌ Erreur : GOOGLE_API_KEY non trouvée.")
else:
    client = genai.Client(api_key=api_key, http_options={'api_version': 'v1alpha'})
    print("✅ Client configuré.")

    try:
        print("\n--- Liste des modèles disponibles ---")
        # Tentative de lister les modèles avec le nouveau SDK
        # Note: Dans le nouveau SDK genai, la méthode peut varier selon la version
        for model in client.models.list():
            print(f"- {model.name} (v {model.version})")
        
        # Test de génération simple pour confirmer que la clé est active
        response = client.models.generate_content(
            model='gemini-2.0-flash', 
            contents="Dis 'Hello Gemini 3' en 3 langues."
        )
        print("\n--- Test de génération (Gemini 2.0 Flash) ---")
        print(response.text)
        print("\n✅ Accès et clé validés.")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de l'accès à l'API : {e}")
