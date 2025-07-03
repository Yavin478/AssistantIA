''' Auteur : Yavin 4u78 (avec l'aide de chatGPT et Le Chat)
Fichier contenant la classe principale permettant l'affichage de l'interface graphique pour les intéractions avec l'utilisateur.
'''

from OllamaAPI import *

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

        # Initialisation de l'objet permettant de charger les documents personnels pour le RAG
        self.document_loader = DocumentLoader(Settings.folder_path)

        # Initialisationde l'objet permettant de construire l'index vectoriel pour le RAG
        self.index_builder = IndexBuilder(Settings.index_path, self.document_loader, Settings.embed_model_name)

        # Case à cocher pour activer/désactiver le RAG
        self.rag_enabled = False  # Booléen indiquant l'activation ou non du RAG
        self.rag_checkbox = QCheckBox("RAG")
        self.rag_checkbox.setChecked(False)
        self.rag_checkbox.stateChanged.connect(self.toggle_rag)
        main_layout.addWidget(self.rag_checkbox)

        # Footer de l'UI
        button_layout = QHBoxLayout()

        # Bouton pour le micro
        self.mic_button = QPushButton()
        self.mic_button.setIcon(qta.icon("fa5s.microphone"))
        self.mic_button.setFixedSize(40, 40)
        self.mic_button.clicked.connect(self.toggle_recording)

        # Bouton pour l'envoi du message
        self.ask_button = QPushButton("Envoyer")
        self.ask_button.clicked.connect(self.send_prompt)

        # Bouton pour importer des documents
        self.import_button = QPushButton("Importer des documents")
        self.import_button.clicked.connect(self.import_documents)

        button_layout.addWidget(self.mic_button)
        button_layout.addStretch()
        button_layout.addWidget(self.import_button)
        button_layout.addWidget(self.ask_button)
        main_layout.addLayout(button_layout)


    # Méthode permettant d'envoyer le dernier prompt utilisateur envoyé dans l'UI à l'API Ollama,
    # d'afficher la réponse obtenue sur l'UI puis de la faire réciter par synthèse vocale si l'option est activée
    def send_prompt(self):
        self.ask_button.setEnabled(False) # Désactivation temporaire du bouton pour envoyer les requêtes textuelles pendant l'envoi d'un prompt à l'API Ollama
        self.mic_button.setEnabled(False)  # Désactivation temporaire du bouton du micro pendant l'envoi d'un prompt à l'API Ollama
        self.handsfree_checkbox.setEnabled(False) # Désactivation de la case pour le mode "mains libres" pendant l'envoi d'un prompt à l'API Ollama
        self.rag_checkbox.setEnabled(False)  # Désactivation de la case pour activer ou non le RAG pendant l'envoi d'un prompt à l'API Ollama
        self.import_button.setEnabled(False)  # Désactivation du bouton pour importer des fichiers pendant l'envoi d'un prompt à l'API Ollama
        self.tts.stop()  # Arrêt de la synthèse vocale en cours avant d'envoyer une nouvelle requête

        prompt = self.prompt_input.toPlainText().strip()  # Récupération de la requête textuelle écrite dans l'UI
        if not prompt:
            return

        self.append_message("🧑 Utilisateur", prompt)
        self.prompt_input.clear()

        if self.rag_enabled:
            if Settings.debug: print("Réponse avec RAG souhaitée")
            query_engine = self.index_builder.get_query_engine()  # Initialise le moteur de requête basé sur la base vectorielle
            if Settings.debug: print("Query engine initialisé")

            # Récupération du contexte documentaire et enrichissement du prompt initial
            context = query_engine.query(prompt)  #  Effectue la recherche sémantique dans la base vectorielle en fonction du prompt de l'utilisateur
            prompt = f"Précise les sources dans tes réponses:\n{str(context)}"  # Nouveau prompt enrichit par RAG

        # Stocker la requête dans l'historique de la conversation et dans le fichier de sauvegarde
        self.conversation_history.append({"role": "user", "content": prompt})
        self.save_to_file(str({"role": "user", "content": prompt}))

        # Envoi de la requête et réponse de l'API Ollama
        if Settings.debug: print("Envoi de la requête utilisateur à l'API Ollama")
        try:
            self.api_worker = OllamaAPIWorker(self.conversation_history)
            self.api_worker.api_response.connect(self.handle_api_response)
            self.api_worker.api_error.connect(self.handle_api_error)
            self.api_worker.start()

        except Exception as e:
            self.append_message("Erreur", str(e))
            print(f"Exception levée lors de l'initialisation de OllamaAPIWorker : \n{e}")
            self.save_to_file(f"Erreur + {str(e)}")
            QMessageBox.critical(self, "Erreur", "Erreur lors de l'initialisation du thread API.")

            self.ask_button.setEnabled(True)  # Réactivation du bouton d'envoi des requêtes textuelles dans le cas ou l'appel API a échoué
            self.mic_button.setEnabled(True)  # Réactivation du bouton du micro dans le cas ou l'appel API a échoué
            self.handsfree_checkbox.setEnabled(True)  # Réactivation de la case du mode "mains libres" dans le cas ou l'appel API a échoué
            self.rag_checkbox.setEnabled(True)  # Réactivation de la case pour activer ou non le RAG dans le cas ou l'appel API a échoué
            self.import_button.setEnabled(True)  # Réactivation du bouton pour importer des fichiers dans le cas ou l'appel API a échoué

    # Méthode permettant de traiter la réponse de l'API obtenue pour l'afficher dans l'UI et la dicter si l'option à été selectionné
    def handle_api_response(self, response):
        self.ask_button.setEnabled(True)  # Réactivation du bouton d'envoi des requêtes textuelles dans le cas où l'appel API est un succès
        self.mic_button.setEnabled(True)  # Réactivation du bouton du micro dans le cas où l'appel API est un succès
        self.rag_checkbox.setEnabled(True)  # Réactivation de la case pour activer ou non le RAG dans le cas où l'appel API est un succès
        self.import_button.setEnabled(True)  # Réactivation du bouton pour importer des fichiers dans le cas où l'appel API est un succès

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

            # Connexion du signal de fin global 'finished_speaking' aux différentes actions programmées
            # Ce signal est trigger lorsque la synthèse est terminée, le programme le détecte et exécute les actions ci-dessous
            self.tts.finished_speaking.connect(lambda: print("Synthèse vocale terminée") if Settings.debug else None)  # Affichage du log de fin de la synthèse en mode debug
            self.tts.finished_speaking.connect(lambda: (self.handsfree_listener.start(), print(
                "Mode mains libres réactivée après la synthèse vocale")) if handsfree_was_active and Settings.debug else None)  # Affichage du log pour la réactivation de mode 'mains libres' en mode debug
            self.tts.finished_speaking.connect(lambda: self.handsfree_checkbox.setEnabled(True))  # Réactivation de la case à cocher du mode 'mains libres'
            self.tts.speak(response)  # Synthèse vocale

        self.handsfree_checkbox.setEnabled(True)  # Réactivation de la case du mode "mains libres" dans le cas ou l'appel API est un succès

    # Méthode permettant de traiter une erreur survenue lors d'un appel API
    def handle_api_error(self, error_message):
        self.ask_button.setEnabled(True)
        self.mic_button.setEnabled(True)
        self.handsfree_checkbox.setEnabled(True)
        self.rag_checkbox.setEnabled(True)
        self.import_button.setEnabled(True)

        QMessageBox.critical(self, "Erreur API",f"Une erreur est survenue lors de l'appel à l'API Ollama")
        self.append_message("Erreur", error_message)
        self.save_to_file(f"Erreur API: {error_message}")

    # Méthode permettant d'ajouter une intéraction sur l'interface graphique
    def append_message(self, sender, message):
        try :
            message = message.strip()

            # Blocs de code ```...``` (multilignes)
            message = re.sub(
                r"```(.*?)```",
                r"<pre style='background-color:#f4f4f4; border:1px solid #ccc; padding:6px; font-family:monospace;'>\1</pre>",
                message,
                flags=re.DOTALL
            )

            # Code en ligne `...`
            message = re.sub(
                r"`([^`\n]+)`",
                r"<code style='background-color:#e8e8e8; font-family:monospace;'>\1</code>",
                message
            )

            message = message.replace("\n", "<br>")  # Convertit les sauts de ligne
            message = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", message)  # Convertit les mots en **gras**
            message = re.sub(r"\*(.*?)\*", r"<i>\1</i>", message)  # Convertit les mots en *italique*

            formatted = f"<b>{sender} :</b><br>{message}<br><hr>"
            self.history_display.append(formatted)
            if Settings.debug: print("Affichage d'un message dans l'UI")

        except Exception as e:
            print(f"Exception levée au niveau de l'affichage d'un message dans l'UI : \n{e}")

    # Méthode permettant de sauvegarder une interaction d'une conversation dans un fichier texte externe
    def save_to_file(self, message):
        with open(self.history_file, "a", encoding="utf-8") as f:
            f.write(message + "\n")

    # Méthode pour mettre à jour dynamiquement le modèle utilisé
    def update_model(self, model_name):
        Settings.model = model_name

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

    # Méthode pour activer/désactiver la synthèse vocale
    def toggle_voice(self, state):
        self.tts.stop()  # Arrêt de la synthèse vocale en cours si il y en a une
        self.voice_enabled = state == 2  # 2 signifie "Checked" dans Qt

    # Méthode pour activer/désactiver le mode main libre : lancement de la boucle d'écoute en continue
    def toggle_handsfree_mode(self):
        try:
            if self.handsfree_checkbox.isChecked():
                self.tts.stop()  # Arrêt de la synthèse vocale en cours pour éviter tout conflit avec le mode "mains libres"
                self.handsfree_listener.start()
                self.mic_button.setEnabled(False)  # Désactivation automatique du bouton du micro en entrant en mode "mains libres"
                if Settings.debug : print("Mode mains libres activé")
            else:
                self.handsfree_listener.stop()
                self.mic_button.setEnabled(True)  # Réactivation automatique du bouton du micro en sortant du mode "mains libres"
                if Settings.debug : print("Mode mains libres désactivé")
        except Exception as e:
            print(f"Exception levée lors de l'usage du mode mains libre: \n{e}")

    # Méthode permettant de commenecr un enregistrement audio suite au repérage du mot-clé lors d'une écoute en continu du mode 'mains libres'
    def handle_handsfree_command(self, command_type):
        if command_type == "start_recording":  # Vérifie qu'un enregistrement à bien été déclenché depuis le mode 'mains libres' grâce au str passé en paramètre

            if not hasattr(self.recorder, 'worker') or not self.recorder.worker or not self.recorder.worker.isRunning():
                if Settings.debug: print("Début de l'enregistrement en mode mains libres")
                self.tts.speak("J'écoute")
                time.sleep(1)  # Delay pour laisser le temps à la synthèse de se terminer avant l'enregistrement
                self.recorder.start_recording()  # Appel de la méthode pour lancer un enregistrement avec 'Audiorecorder'
                self.mic_button.setIcon(qta.icon("fa5s.stop"))

    # Méthode pour activer/désactiver le RAG
    def toggle_rag(self, state):
        self.rag_enabled = state == 2  # 2 signifie "Checked" dans Qt

    # Méthode pour importer des documents depuis l'interface
    def import_documents(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Sélectionner des fichiers", "","Documents (*.pdf *.doc *.docx *.txt)")

        if not files:
            return  # L'utilisateur a annulé

        for file_path in files:
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in Settings.allowed_extensions:
                QMessageBox.warning(self, "Type non supporté",f"Le fichier {os.path.basename(file_path)} n'est pas un format accepté.")
                continue

            try:
                dest_folder = Settings.folder_path  # Chemin du dossier "docs/"
                os.makedirs(dest_folder, exist_ok=True)
                shutil.copy(file_path, dest_folder)
            except Exception as e:
                QMessageBox.critical(self, "Erreur", f"Impossible de copier {file_path}.\n{str(e)}")

        # Reconstruction de l'index après l'import
        self.index_builder.load_or_build_index()
        if Settings.debug : print("Index reconstruit après import")

        QMessageBox.information(self, "Import terminé", "Les documents ont été importés avec succès !")

