''' Auteur : Yavin 4u78 (avec chatGPT)
Fichier contenant la classe pour le GUI.
'''

from Vocal import *

# Classe pour l'affichage de l'interface graphique avec les boutons associés aux diverses fonctionnalités.
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

        # Initialisation du fichier de sauvegarde des conversations.
        self.history_file = Settings.history_file

        # Réinitialiser le fichier à chaque lancement (sans rien écrire).
        with open(self.history_file, "w", encoding="utf-8"):
            pass

        # Layout principal de l'interface.
        main_layout = QVBoxLayout(self)

        # Sélection et affichage du modèle utilisé via une liste déroulante.
        model_layout = QHBoxLayout()
        model_label = QLabel("Modèle utilisé :")
        self.model_selector = QComboBox()
        self.model_selector.addItems(Settings.available_models)
        self.model_selector.setCurrentText(Settings.model)
        self.model_selector.currentTextChanged.connect(self.update_model)

        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_selector)
        main_layout.addLayout(model_layout)

        # Zone d'affichage de l'historique de conversation.
        self.history_display = QTextEdit()
        self.history_display.setReadOnly(True)
        self.history_display.setStyleSheet("font: 12pt 'Courier';")
        main_layout.addWidget(self.history_display, stretch=5)

        # Zone de saisie de la requête.
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Écris ta question ici...")
        self.prompt_input.setFixedHeight(80)
        main_layout.addWidget(self.prompt_input, stretch=1)

        # Intéraction vocale.
        self.recorder = AudioRecorder(self.handle_transcription)

        # Boutons (micro + envoyer).
        button_layout = QHBoxLayout()
        self.mic_button = QPushButton()
        self.mic_button.setIcon(qta.icon("fa5s.microphone"))
        self.mic_button.setFixedSize(40, 40)
        self.mic_button.clicked.connect(self.toggle_recording)

        self.ask_button = QPushButton("Envoyer")
        self.ask_button.clicked.connect(self.send_prompt)

        button_layout.addWidget(self.mic_button)
        button_layout.addStretch()
        button_layout.addWidget(self.ask_button)
        main_layout.addLayout(button_layout)


    # Méthode permettant d'envoyer un prompt à l'API Ollama et d'afficher la réponse obtenue sur l'interface graphique.
    def send_prompt(self):
        prompt = self.prompt_input.toPlainText().strip()
        if not prompt:
            return

        self.append_message("🧑 Utilisateur", prompt)
        self.prompt_input.clear()

        # Stocker dans l'historique.
        self.conversation_history.append({"role": "user", "content": prompt})
        self.save_to_file(str({"role": "user", "content": prompt}))

        # Requête et réponse de l'API Ollama.
        try:
            response = OllamaAPI.ask_ollama(self.conversation_history)
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

    # Méthodes pour recueillir l'audio et le transcrire.
    def toggle_recording(self):
        if not self.recorder.is_recording:
            self.recorder.start_recording()
            self.mic_button.setIcon(qta.icon("fa5s.stop"))
        else:
            self.recorder.stop_and_transcribe()
            self.mic_button.setIcon(qta.icon("fa5s.microphone"))

    def handle_transcription(self, text):
        # Affiche la transcription dans le champ de saisie.
        self.prompt_input.setText(text)
        # Envoie le message automatiquement.
        self.send_prompt()

    # Méthode pour mettre à jour dynamiquement le modèle utilisé.
    def update_model(self, model_name):
        Settings.model = model_name

