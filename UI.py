''' Auteur : Yavin 4u78 (avec chatGPT)
Fichier contenant les classes pour le GUI
'''

from OllamaAPI import *

class AssistantWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Assistant IA Local - avec Ollama")
        self.setGeometry(200, 200, 800, 700)

        self.conversation_history = [
            {
                "role": "system",
                "content": Settings.system_prompt
            }
        ]

        # Initialisation du fichier de sauvegarde des conversations
        self.history_file = Settings.history_file

        # Réinitialiser le fichier à chaque lancement (sans rien écrire)
        with open(self.history_file, "w", encoding="utf-8"):
            pass

        # Layout principal de l'interface
        main_layout = QVBoxLayout(self)

        # Affichage du modèle utilisé
        model_label = QLabel(f"Modèle utilisé : {Settings.model}")
        model_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        main_layout.addWidget(model_label)

        # Historique de conversation (affichage)
        self.history_display = QTextEdit()
        self.history_display.setReadOnly(True)
        self.history_display.setStyleSheet("font: 12pt 'Courier';")
        main_layout.addWidget(self.history_display, stretch=5)

        # Zone de saisie
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Écris ta question ici...")
        self.prompt_input.setFixedHeight(80)
        main_layout.addWidget(self.prompt_input, stretch=1)

        # Bouton
        button_layout = QHBoxLayout()
        self.ask_button = QPushButton("Envoyer")
        self.ask_button.clicked.connect(self.send_prompt)
        button_layout.addStretch()
        button_layout.addWidget(self.ask_button)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    # Méthode permettant d'envoyer un prompt à l'API Ollama et d'afficher la réponse obtenue sur l'interface graphique.
    def send_prompt(self):
        prompt = self.prompt_input.toPlainText().strip()
        if not prompt:
            return

        self.append_message("🧑 Utilisateur", prompt)
        self.prompt_input.clear()

        # Stocker dans l'historique
        self.conversation_history.append({"role": "user", "content": prompt})
        self.save_to_file(str({"role": "user", "content": prompt}))

        # Requête et réponse de l'API Ollama
        try:
            response = ask_ollama(self.conversation_history)
            self.append_message("🤖 Assistant IA", response)
            self.conversation_history.append({"role": "assistant", "content": response})
            self.save_to_file(str({"role": "assistant", "content": response}))
        except Exception as e:
            self.append_message("Erreur", str(e))
            self.save_to_file("Erreur", str(e))

    # Méthode permettant d'ajouter une intéraction sur l'interface graphique.
    def append_message(self, sender, message):
        formatted = f"<b>{sender} :</b><br>{message}<br><hr>"
        self.history_display.append(formatted)

    # Méthode permettant de sauvegarder une interaction d'une conversation dans un fichier texte externe.
    def save_to_file(self, message):
        with open(self.history_file, "a", encoding="utf-8") as f:
            f.write(message + "\n")