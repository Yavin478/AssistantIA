''' Auteur : Yavin 4u78 (avec chatGPT)
Fichier contenant la classe principale permettant l'affichage de l'interface graphique pour les intéractions avec l'utilisateur.
'''
import time

from AudioHandsFreeListener import *

# Classe pour l'affichage de l'interface graphique avec les boutons associés aux diverses fonctionnalités implémentées du projet
class AssistantWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(Settings.window_title)
        self.setGeometry(200, 200, 800, 700)

        # Création de l'historique de conversation entre l'utilisateur et l'assistant en commençant par le prompt système de l'assistant
        self.conversation_history = [
            {
                "role": "system",
                "content": Settings.system_prompt
            }
        ]
        # Initialisation du fichier de sauvegarde des conversations
        self.history_file = Settings.history_file

        # Réinitialise le fichier à chaque lancement du programme, sans rien écrire dedans
        with open(self.history_file, "w", encoding="utf-8"):
            pass

        # Layout principal de l'interface
        main_layout = QVBoxLayout(self)

        # Sélection et affichage du LLM utilisé via une liste déroulante
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

        # Zone de saisie de la requête textuelle à envoyer au modèle
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Écris ta question ici...")
        self.prompt_input.setFixedHeight(80)
        main_layout.addWidget(self.prompt_input, stretch=1)

        # Initialisation de la transcription audio
        self.recorder = AudioRecorder(self.handle_transcription)

        # Initialisation de la synthèse vocale
        self.tts = AudioSynthesizer()

        # Case à cocher pour activer/désactiver la réponse vocale de l'assistant
        self.voice_enabled = False  # Désactivé par défaut
        self.voice_checkbox = QCheckBox("Activer la réponse vocale")
        self.voice_checkbox.setChecked(False)
        self.voice_checkbox.stateChanged.connect(self.toggle_voice)
        main_layout.addWidget(self.voice_checkbox)

        # Initialisation du mode "mains libres"
        self.handsfree_listener = AudioHandsFreeListener(on_command_detected=self.handle_handsfree_command)

        # Case à cocher pour activer/désactiver le mode mains libres
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
    # d'afficher la réponse obtenue sur l'UI puis de la faire réciter par synthèse vocale si l'option est activée
    def send_prompt(self):
        self.ask_button.setEnabled(False) # Désactivation temporaire du bouton pour envoyer les requêtes textuelles pendant l'envoi d'un prompt à l'API Ollama
        self.mic_button.setEnabled(False)  # Désactivation temporaire du bouton du micro pendant l'envoi d'un prompt à l'API Ollama
        self.handsfree_checkbox.setEnabled(False) # Désactivation de la case pour le mode "mains libres" pendant l'envoi d'un prompt à l'API Ollama
        self.tts.stop()  # Arrêt de la synthèse vocale en cours avant d'envoyer une nouvelle requête

        prompt = self.prompt_input.toPlainText().strip()  # Récupération de la requête textuelle écrite dans l'UI
        if not prompt:
            return

        self.append_message("🧑 Utilisateur", prompt)
        self.prompt_input.clear()

        # Stocker la requête dans l'historique de la conversation et dans le fichier de sauvegarde
        self.conversation_history.append({"role": "user", "content": prompt})
        self.save_to_file(str({"role": "user", "content": prompt}))

        # Envoi de la requête et réponse de l'API Ollama
        if Settings.debug: print("Envoi de la requête utilisateur à l'API Ollama")
        try:
            self.api_worker = OllamaAPIWorker(self.conversation_history)
            self.api_worker.api_response.connect(self.handle_api_response)
            self.api_worker.start()

        except Exception as e:
            self.append_message("Erreur", str(e))
            self.save_to_file("Erreur", str(e))
            self.ask_button.setEnabled(True)  # Réactivation du bouton d'envoi des requêtes textuelles dans le cas ou l'appel API a échoué
            self.mic_button.setEnabled(True)  # Réactivation du bouton du micro dans le cas ou l'appel API a échoué
            self.handsfree_checkbox.setEnabled(True)  # Réactivation de la case du mode "mains libres" dans le cas ou l'appel API a échoué

    # Méthode permettant de traiter la réponse de l'API obtenue pour l'afficher dans l'UI et la dicter si l'option à été selectionné
    def handle_api_response(self, response):
        if Settings.debug: print("Réponse de l'API obtenue avec succès !")
        self.ask_button.setEnabled(True)  # Réactivation du bouton d'envoi des requêtes textuelles dans le cas ou l'appel API est un succès
        self.mic_button.setEnabled(True)  # Réactivation du bouton du micro dans le cas ou l'appel API est un succès

        self.append_message("🤖 Assistant IA", response)
        self.conversation_history.append({"role": "assistant", "content": response})
        self.save_to_file(str({"role": "assistant", "content": response}))

        # Si la synthèse vocale est activée
        if self.voice_enabled:

            # Si le mode mains libres est actif
            handsfree_was_active = self.handsfree_checkbox.isChecked()
            if handsfree_was_active:
                self.handsfree_listener.stop()
                if Settings.debug: print("Mains libres temporairement désactivé pendant la synthèse vocale")

            # Connexion du signal finished_speaking pour réactiver le mode "mains libres" et afficher des logs à la fin de la synthèse vocale
            self.tts.finished_speaking.connect(lambda: print("Synthèse vocale terminée") if Settings.debug else None)
            self.tts.finished_speaking.connect(lambda: (self.handsfree_listener.start(), print(
                "Mode mains libres réactivée après la synthèse vocale")) if handsfree_was_active else None)
            self.tts.finished_speaking.connect(lambda: self.handsfree_checkbox.setEnabled(True))
            self.tts.speak(response)

        self.handsfree_checkbox.setEnabled(True)  # Réactivation de la case du mode "mains libres" dans le cas ou l'appel API est un succès

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
        self.tts.stop()  # Arrêt de la synthèse vocale en cours avant d'envoyer une nouvelle requête

        if not hasattr(self.recorder, 'worker') or not self.recorder.worker or not self.recorder.worker.isRunning():
            self.mic_button.setIcon(qta.icon("fa5s.stop"))
            self.recorder.start_recording()
        else:
            self.recorder.stop_recording()
            self.mic_button.setIcon(qta.icon("fa5s.microphone"))

    # Méthode permettant d'écrire dans l'UI la requête transcrite de l'utilisateur
    def handle_transcription(self, text):
        self.mic_button.setIcon(qta.icon("fa5s.microphone"))
        self.prompt_input.setText(text)
        self.send_prompt()

    # Méthode pour mettre à jour dynamiquement le modèle utilisé
    def update_model(self, model_name):
        Settings.model = model_name

    # Méthode pour indiquer que la réponse vocale est activée.
    def toggle_voice(self, state):
        self.tts.stop()  # Arrêt de la synthèse vocale en cours si il y en a une
        self.voice_enabled = state == 2  # 2 signifie "Checked" dans Qt

    # Méthode pour activer ou désactiver le mode main libre : lancement de la boucle d'écoute en continue
    def toggle_handsfree_mode(self):
        if self.handsfree_checkbox.isChecked():
            self.tts.stop()  # Arrêt de la synthèse vocale en cours pour éviter tout conflit avec le mode "mains libres"
            self.handsfree_listener.start()
            self.mic_button.setEnabled(False)  # Désactivation automatique du bouton du micro en entrant en mode "mains libres"
            if Settings.debug : print("Mode mains libres activé")
        else:
            self.handsfree_listener.stop()
            self.mic_button.setEnabled(True)  # Réactivation automatique du bouton du micro en sortant du mode "mains libres"
            if Settings.debug : print("Mode mains libres désactivé")

    # Méthode pour commencer l'enregistrement audio en mode "mains libres" suite au repérage du mot-clé
    def handle_handsfree_command(self, command_type):
        if command_type == "start_recording":
            if not hasattr(self.recorder, 'worker') or not self.recorder.worker or not self.recorder.worker.isRunning():
                if Settings.debug: print("Début de l'enregistrement en mode mains libres")
                self.tts.speak("J'écoute")
                time.sleep(1)
                self.recorder.start_recording()
                self.mic_button.setIcon(qta.icon("fa5s.stop"))

