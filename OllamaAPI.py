''' Auteur : Yavin 4u78 (avec chatGPT)
Fichier contenant les fonctions d'appel pour l'API d'ollama.
Il faut d'abord run Ollama dans le terminal Windows : ollama run mistral.
'''

from Settings import *

# Classe pour les intéractions avec l'API d'Ollama pour exécuter les LLM.
class OllamaAPI():
    def ask_ollama(prompt):
        url = Settings.api_url
        payload = {
            "model": Settings.model,
            "messages": prompt,
            "stream": False
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Affiche une erreur si la requête échoue
        return response.json()["message"]["content"]