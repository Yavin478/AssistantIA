''' Auteur : Yavin 4u78 (avec chatGPT)
Fichier contenant les fonctions d'appel pour l'API d'Ollama.
Il faut d'abord run Ollama dans le terminal Windows : ollama run mistral.
'''

from Settings import *

# Classe pour les intéractions avec l'API d'Ollama pour exécuter les LLM.
class OllamaAPIWorker(QThread):
    api_response = pyqtSignal(str)  # Signal indiquant la réponse obtenue de l'API

    def __init__(self, conversation_history):
        super().__init__()
        self.conversation_history = conversation_history

    def run(self):
        try:
            response_content = self.ask_ollama(self.conversation_history)
            self.api_response.emit(response_content)
            if Settings.debug : print("Signal de réponse de l'API envoyé ")
        except Exception as e:
            self.api_response.emit(f"Erreur: {str(e)}")

    # Méthode pour envoyer la requête de l'utilisateur au LLM selectionné via l'API Ollama
    def ask_ollama(self, prompt):
        url = Settings.api_url
        payload = {
            "model": Settings.model,
            "messages": prompt,
            "stream": False
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()  # Affiche une erreur si la requête échoue
        return response.json()["message"]["content"]