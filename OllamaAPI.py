''' Auteur : Yavin 4u78 (avec chatGPT)
Fichier contenant les fonctions d'appel pour l'API d'ollama.
Il faut d'abord run Ollama dans le terminal Windows : ollama run mistral
'''

from Libraries import *

def ask_ollama(prompt, model="mistral:7b"):
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }

    response = requests.post(url, json=payload)
    response.raise_for_status()  # Affiche une erreur si la requête échoue
    return response.json()["message"]["content"]