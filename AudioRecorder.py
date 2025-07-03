''' Auteur : Yavin 4u78 (avec l'aide de chatGPT et Le Chat)
Fichier contenant les classes nécessaires à l'enregistrement et à la transcription écrite des requêtes vocales envoyées au modèle via l'interface graphique.
'''

from AudioBase import *

# Classe "Worker" pour l'enregistrement et la transcription
# Cette classe permet de créer des threads d'enregistrement vocal indépendants, s'exécutant en parallèle d'autres actions
# Cela permet de ne pas bloquer l'UI ou de faire planter le programme en cas d'actions simultanées
# Cette classe hérite de 'AudioBase' afin de pouvoir utiliser la fonctionalité de transcription audio permise par le modèle Whisper
class AudioRecorderWorker(QThread, AudioBase):
    transcription_ready = pyqtSignal(str)  # Signal indiquant la fin de l'enregistrement pour l'envoi de la transcription obtenue
    stop_recording_signal = pyqtSignal()  # Signal indiquant l'arrêt manuel de l'enregistrement par l'utilisateur

    def __init__(self, samplerate, silence_threshold, silence_duration):
        AudioBase.__init__(self)  # Initialise la partie AudioBase
        QThread.__init__(self)  # Initialise la partie QThread
        self.samplerate = samplerate
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self.is_recording = False  # Etat du thread d'enregistrement
        self.audio = []
        self.q = queue.Queue()

    # Méthode pour exécuter l'enregistrement audio
    def run(self):
        self.is_recording = True
        self.audio = []  # Initialisation de la liste contenant les données auditives qui seront enregistrées
        silence_start = None

        def audio_callback(indata, frames, time, status):
            if status:
                if Settings.debug: print("Status du micro :", status)
            self.q.put(indata.copy())

        with sd.InputStream(samplerate=self.samplerate, channels=1, callback=audio_callback):
            while self.is_recording:  # Vérifie si le thread en cours dois toujours enregistrer
                try:
                    data = self.q.get(timeout=0.5)
                    self.audio.append(data)  # Ajout des données auditives enregistrées

                    volume = np.linalg.norm(data) / np.sqrt(len(data))

                    if volume < self.silence_threshold:
                        if silence_start is None:
                            silence_start = time.time()
                        elif time.time() - silence_start > self.silence_duration:
                            print("Silence prolongé détecté. Arrêt de l'enregistrement")
                            self.stop_and_transcribe()  # Appel de la méthode pour la transcription des données recueillies
                            break
                    else:
                        silence_start = None

                except queue.Empty:
                    continue

    # Méthode permettant de changer l'état du thread en indiquant l'arrêt d'un enregistrement
    # Stop l'enregistrement en cours de la méthode "run" via la sortie de la boucle 'while' dû au changement de valeur du booléan
    def stop_recording(self):
        self.is_recording = False

    # Méthode permettant de transcrire les données audio enregistrée en texte
    def stop_and_transcribe(self):
        self.stop_recording()  # Appel de la méthode de la classe pour arrêter l'enregistrement en cours
        if not self.audio:
            if Settings.debug : print("Aucunes données audio enregistrées")
            return

        if Settings.debug: print("Début de la transcription")
        audio_data = np.concatenate(self.audio, axis=0)
        audio_int16 = np.int16(audio_data * 32767)
        text = self.transcribe_audio(audio_int16)  # Appel de la méthode de la classe 'AudioBase' pour effectuer la transcription
        self.transcription_ready.emit(text)  # Emission du signal indiquant la fin de la transcription avec le texte transcrit
        if Settings.debug: print("Fin de la transcription. L'audio a été transcrit avec succès !")

# Classe princiapale pour démarrer le processus d'enregistrement et de transcription audio
# Initialisée qu'une unique fois, cette classe permet d'orchestrer ces processus en créant ou en stoppant des workers
class AudioRecorder(AudioBase):
    def __init__(self, update_ui_callback):
        super().__init__()
        self.worker = None  # Initialisation d'un objet worker vide pour l'enregistrement et la transcription audio
        self.update_ui_callback = update_ui_callback  # Méthode 'handle_transcription(self, text)' passée comme argument

    # Méthode permettant de lancer un enregistrement et ensuite une transcription audio
    def start_recording(self):
        self.worker = AudioRecorderWorker(self.samplerate, Settings.silence_threshold, Settings.silence_duration)  # Initialisation du worker pour l'enregistrement et la transcription spontanés
        self.worker.transcription_ready.connect(self.update_ui_callback)  # Connection du signal d'envoi de la transcription obtenue par le worker à la méthode permettant de traiter son affichage
                                                                          # Lorsque ce signal est émis cela trigger la méthode en lui passant comme argument le texte transcrit
        self.worker.start()  # Exécution du run du worker créé
        if Settings.debug: print("Début de l'enregistrement audio")

    # Méthode permettant de stopper manuellement l'enregistrement audio en cours d'un worker actif
    def stop_recording(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop_recording_signal.emit()  # Emission du signal indiquant l'arrêt manuel de l'enregistrement par l'utilisateur
            self.worker.quit()
            self.worker.wait()
            if Settings.debug: print("Arrêt manuel de l'enregistrement")
