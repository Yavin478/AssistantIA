''' Auteur : Yavin 4u78 (avec l'aide de chatGPT et Le Chat)
Fichier contenant les classes nécessaires au fonctionnement du mode 'mains libres'.
Ce mode permet d'effectué des requêtes à l'oral sans avoir à appuyer sur le bouton du microphone pour lancer un enregistrement.
Il lance une écoute en continu et déclenche un enregistrement lorsque le mot-clé pré-défini est reconnu.
'''

from AudioSynthesizer import *

# Classe "Worker" pour démarrer une écoute en continu en mode 'mains libres'
# Cette classe permet de créer des threads d'écoute en continu indépendants, s'exécutant en parallèle d'autres actions
# Cela permet de ne pas bloquer l'UI ou de faire planter le programme en cas d'actions simultanées
# Cette classe hérite de 'AudioBase' afin de pouvoir utiliser la fonctionalité de transcription audio permise par le modèle Whisper
class AudioHandsFreeListenerWorker(QThread, AudioBase):
    command_detected = pyqtSignal(str)  # Signal indiquant la détection du mot-clé lors de l'écoute en continu du mode 'mains libres'

    def __init__(self, samplerate, buffer_duration, handfree_keywordstart):
        AudioBase.__init__(self)  # Initialise la partie AudioBase
        QThread.__init__(self)  # Initialise la partie QThread
        self.samplerate = samplerate
        self.buffer_duration = buffer_duration
        self.handfree_keywordstart = handfree_keywordstart  # Récupération du mot-clé
        self.active = False  # Etat du thread d'écoute en continu

    def run(self):
        self.active = True

        while self.active:  # Vérifie si le thread d'écoute en cours dois toujours se poursuivre
            audio = self.capture_audio(self.buffer_duration)
            sd.wait()
            text = self.transcribe_audio(audio)  # Appel de la méthode de la classe mère 'AudioBase' pour transcrire en texte le contenu du dernier segment d'écoute
            if not text:
                continue

            else :
                if Settings.debug: print(f"Texte interprété : {text}")

                if self.handfree_keywordstart.lower() in text.lower():  # Vérification de la présence du mot-clé dans le texte transcrit
                    self.command_detected.emit("start_recording")  # Emission du signal indiquant la détection du mot-clé et la validation du lancement d'un enregistrement
                    if Settings.debug: print("Mot-clé détecté !")

    # Méthode permettant de capturer le contenu audio par segment de durée définie
    def capture_audio(self, duration):
        return sd.rec(int(duration * self.samplerate), samplerate=self.samplerate, channels=1, dtype='int16')

    # Méthode permettant de changer l'état du thread en indiquant l'arrêt d'une écoute
    # Stop l'écoute en cours traitée par la méthode "run" via la sortie de la boucle 'while' dû au changement de valeur du booléan
    def stop(self):
        self.active = False

# Classe princiapale pour démarrer l'écoute en continu du mode 'mains libres'
# Initialisée qu'une unique fois, cette classe permet d'orchestrer ces écoutes en créant ou en stoppant des workers
class AudioHandsFreeListener(AudioBase):
    def __init__(self, on_command_detected):
        super().__init__()
        self.worker = None  # Initialisation d'un objet worker vide pour l'écoute en continu
        self.on_command_detected = on_command_detected  # Méthode 'handle_handsfree_command(self, command_type)' passée comme argument

    # Méthode permettant de lancer une écoute en continu
    def start(self):
        if self.worker is None or not self.worker.isRunning():
            self.worker = AudioHandsFreeListenerWorker(self.samplerate, Settings.buffer_duration, Settings.handfree_keywordstart)  # Initialisation du worker pour l'écoute en continu
            self.worker.command_detected.connect(self.on_command_detected)  # Connection du signal de reconnaissance du mot-clé émis par le worker à la méthode permettant de traiter la suite de processus
                                                                            # Lorsque ce signal est émis cela trigger cette méthode en lui passant comme argument le str validant le lancement d'un enregistrement
            self.worker.start()
            if Settings.debug: print("Écoute en continu démarrée")

    # Méthode permettant de sortir du mode 'mains libres' et de stopper l'écoute en continu en cours du worker actif
    def stop(self):
        if self.worker is not None and self.worker.isRunning():
            self.worker.stop()  # Appel de la méthode du worker actif pour stopper l'écoute en cours
            self.worker.quit()
            self.worker.wait()
            if Settings.debug: print("Écoute en continu stopée")

