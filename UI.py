''' Auteur : Yavin 4u78 (avec chatGPT)
Fichier contenant les classes pour le GUI
'''

from OllamaAPI import *

class AssistantWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Assistant IA local (Ollama)")
        self.setGeometry(100, 100, 500, 400)

        layout = QVBoxLayout()

        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Écris ta question ici...")
        layout.addWidget(self.prompt_input)

        self.ask_button = QPushButton("Envoyer à Mistral")
        self.ask_button.clicked.connect(self.send_prompt)
        layout.addWidget(self.ask_button)

        self.response_label = QLabel("Réponse :")
        self.response_label.setWordWrap(True)
        layout.addWidget(self.response_label)

        self.setLayout(layout)

    def send_prompt(self):
        prompt = self.prompt_input.toPlainText().strip()
        if not prompt:
            self.response_label.setText("Veuillez entrer une question.")
            return

        self.response_label.setText("En attente de la réponse...")
        try:
            response = ask_ollama(prompt)
            self.response_label.setText("Réponse : " + response)
        except Exception as e:
            self.response_label.setText(f"Erreur : {str(e)}")