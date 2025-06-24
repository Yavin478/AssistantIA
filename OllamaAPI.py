''' Auteur : Yavin 4u78 (avec l'aide de chatGPT et Le Chat)
Fichier contenant la classe pour effectuer des appels à l'API d'Ollama.
'''

from IndexBuilder import *

# Classe "Worker" pour les intéractions avec l'API d'Ollama afin d'exécuter les LLM téléchargés sans bloquer l'UI
class OllamaAPIWorker(QThread):
    api_response = pyqtSignal(str)  # Signal indiquant la réponse obtenue de l'API
    api_error = pyqtSignal(str)  # Signal indiquant qu'une erreur est survenue lors de l'appel API

    def __init__(self, conversation_history):
        super().__init__()
        self.url = Settings.api_url
        self.conversation_history = conversation_history  # Historique de conversation à transmettre à l'API

    # Méthode pour exécuter l'appel API
    def run(self):
        try:
            response_content = self.ask_ollama(self.conversation_history)
            if Settings.debug: print("Réponse de l'API obtenue avec succès !")
            self.api_response.emit(response_content)

        except Exception as e:
            self.api_error.emit(str(e))
            print(f"Exception levée lors d'un appel à l'API Ollama: \n{e}")

    # Méthode pour envoyer la requête de l'utilisateur au LLM selectionné via l'API Ollama
    def ask_ollama(self, prompt):
        payload = {
            "model": Settings.model,
            "messages": prompt,
            "stream": False
        }
        response = requests.post(self.url, json=payload)
        response.raise_for_status()  # Affiche une erreur si la requête échoue
        return response.json()["message"]["content"]