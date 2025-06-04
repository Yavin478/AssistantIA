''' Auteur : Yavin 4u78 (avec chatGPT)
Fichier contenant la classe principale permettant l'affichage du GUI.
'''

from Vocal import *

# Classe pour l'affichage de l'interface graphique avec les boutons associés aux diverses fonctionnalités
class AssistantWindow(QWidget):
    transcription_ready = pyqtSignal(str) # Signal

    def __init__(self):
        super().__init__()
        self.setWindowTitle(Settings.window_title)
        self.setGeometry(200, 200, 800, 700)

        # Création de l'historique de conversation entre l'utilisateur et l'assistant
        self.conversation_history = [
            {
                "role": "system",
                "content": Settings.system_prompt
            }
        ]

        # Initialisation du fichier de sauvegarde des conversations
        self.history_file = Settings.history_file

        # Réinitialise le fichier à chaque lancement (sans rien écrire)
        with open(self.history_file, "w", encoding="utf-8"):
            pass

        # Layout principal de l'interface
        main_layout = QVBoxLayout(self)

        # Sélection et affichage du modèle utilisé via une liste déroulante
        model_layout = QHBoxLayout()
        model_label = QLabel("Modèle utilisé :")
        self.model_selector = QComboBox()
        self.model_selector.addItems(Settings.available_models)
        self.model_selector.setCurrentText(Settings.model)
        self.model_selector.currentTextChanged.connect(self.update_model)

        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_selector)
        main_layout.addLayout(model_layout)

        # Zone d'affichage de l'historique de conversation
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
        self.transcription_ready.connect(self.handle_transcription)
        self.recorder = AudioRecorder(update_ui_callback=self.emit_transcription)
        self.tts = AudioSynthesizer()

        # Case à cocher pour la réponse vocale de l'assistant
        self.voice_enabled = False  # Désactivé par défaut
        self.voice_checkbox = QCheckBox("Activer la réponse vocale")
        self.voice_checkbox.setChecked(False)
        self.voice_checkbox.stateChanged.connect(self.toggle_voice)
        main_layout.addWidget(self.voice_checkbox)

        # Mode mains libres.
        self.handsfree_listener = HandsFreeListener(on_command_detected=self.handle_handsfree_command)

        # Case à cocher pour activer le mode mains libres
        self.handsfree_checkbox = QCheckBox("Mode mains libres")
        self.handsfree_checkbox.stateChanged.connect(self.toggle_handsfree_mode)
        main_layout.addWidget(self.handsfree_checkbox)

        # Boutons pour le micro et l'envoi du message
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



    # Méthode permettant d'envoyer le dernier prompt utilisateur envoyé dans l'UI à l'API Ollama,
    # d'afficher la réponse obtenue sur l'UI puis de la réciter par synthèse vocale si l'option est activée
    def send_prompt(self):
        prompt = self.prompt_input.toPlainText().strip()
        if not prompt:
            return

        self.append_message("🧑 Utilisateur", prompt)
        self.prompt_input.clear()

        # Stocker la requête dans l'historique de la conversation et dans le fichier de sauvegarde
        self.conversation_history.append({"role": "user", "content": prompt})
        self.save_to_file(str({"role": "user", "content": prompt}))

        # Envoi de la requête et réponse de l'API Ollama
        if Settings.debug: print("Envoi de la requête utilisateur transcrite à l'API Ollama")
        try:
            response = OllamaAPI.ask_ollama(self.conversation_history)
            self.append_message("🤖 Assistant IA", response)
            self.conversation_history.append({"role": "assistant", "content": response})
            self.save_to_file(str({"role": "assistant", "content": response}))

            # Si la synthèse vocale est activée
            if self.voice_enabled :
                # Si le mode mains libres est actif
                handsfree_was_active = self.handsfree_checkbox.isChecked()
                if handsfree_was_active:
                    self.handsfree_listener.stop()
                    if Settings.debug: print("Mains libres temporairement désactivé pendant la synthèse vocale")

                self.tts.speak(response)
                if Settings.debug : print("Réponse vocale énoncée")

                # Réactivation du mode mains libres après la synthèse si il était activé avant
                if handsfree_was_active:
                    self.handsfree_listener.start()
                    if Settings.debug: print("Mains libres réactivé après la synthèse vocale")

        except Exception as e:
            self.append_message("Erreur", str(e))
            self.save_to_file("Erreur", str(e))

    # Méthode permettant d'ajouter une intéraction sur l'interface graphique
    def append_message(self, sender, message):
        formatted = f"<b>{sender} :</b><br>{message}<br><hr>"
        self.history_display.append(formatted)

    # Méthode permettant de sauvegarder une interaction d'une conversation dans un fichier texte externe
    def save_to_file(self, message):
        with open(self.history_file, "a", encoding="utf-8") as f:
            f.write(message + "\n")

    # Méthode pour enclencher ou non l'enregistrement vocal
    def toggle_recording(self):
        if not self.recorder.is_recording:
            if Settings.debug: print("Début de l'enregistrement audio")
            self.recorder.start_recording()
            self.mic_button.setIcon(qta.icon("fa5s.stop"))
        else:
            self.recorder.stop_and_transcribe()
            self.mic_button.setIcon(qta.icon("fa5s.microphone"))

    # Méthode permettant d'écrire dans l'UI la requête transcrite de l'utilisateur
    def handle_transcription(self, text):
        # Réinitialise le bouton micro
        if Settings.debug: print("Transcription reçue : changement de l'état de l'icone du micro dans le UI")
        self.mic_button.setIcon(qta.icon("fa5s.microphone"))
        # Affiche la transcription dans le champ de saisie utilisateur de l'UI
        if Settings.debug: print("Ecriture de la transcription dans l'UI")
        self.prompt_input.setText(text)
        # Appel de la méthode permettant d'envoyer la requête transcrite à l'API
        self.send_prompt()

    # Méthode pour mettre à jour dynamiquement le modèle utilisé
    def update_model(self, model_name):
        Settings.model = model_name

    # Méthode pour indiquer que la réponse vocale est activée.
    def toggle_voice(self, state):
        self.voice_enabled = state == 2  # 2 signifie "Checked" dans Qt

    # Méthode pour activer ou désactiver le mode main libre : lancement de la boucle d'écoute en continue
    def toggle_handsfree_mode(self):
        if self.handsfree_checkbox.isChecked():
            self.handsfree_listener.start()
            if Settings.debug : print("Mode mains libres activé")
        else:
            self.handsfree_listener.stop()
            if Settings.debug : print("Mode mains libres désactivé")

    # Méthode pour commencer ou arreter l'enregistrement audio en mode mains libres
    def handle_handsfree_command(self, command_type):
        if command_type == "start_recording":
            if not self.recorder.is_recording:
                if Settings.debug : print("Début de l'enregistrement en mode mains libres")
                self.tts.speak("J'écoute")
                self.recorder.start_recording()
                self.mic_button.setIcon(qta.icon("fa5s.stop"))

    # Méthode pour émettre le signal
    def emit_transcription(self, text):
        self.transcription_ready.emit(text)
