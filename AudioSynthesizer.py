''' Auteur : Yavin 4u78 (avec l'aide de chatGPT et Le Chat)
Fichier contenant les classes nécessaires à la synthèse vocale pour les réponses auditives du modèle.
'''

from AudioRecorder import *

# Classe "Worker" pour la synthèse vocale
# Cette classe permet de créer des threads afin de réaliser des synthèses vocales s'exécutant en parallèle d'autres actions
# Cela permet de ne pas bloquer l'UI ou de faire planter le programme en cas d'actions simultanées
class AudioSynthesizerWorker(QThread):
    speech_finished = pyqtSignal()  # Signal indiquant que la synthèse vocale enclenchée par le worker est terminée

    def __init__(self, text):
        super().__init__()
        self.text = text
        self.engine = None
        self.is_running = True  # Etat du thread de synthèse

    # Méthode pour exécuter la synthèse vocale
    def run(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", Settings.synthetic_rate)
        self.engine.setProperty("volume", Settings.synthetic_volume)
        self.engine.say(self.text)
        self.engine.runAndWait()
        if self.is_running:
            self.finished.emit()  # Emission du signal de fin de la synthèse

    # Méthode pour stopper la synthèse vocale en cours
    def stop(self):
        self.is_running = False
        if self.engine is not None:
            self.engine.stop()
        self.quit()
        self.wait(2000)  # Attendre jusqu'à 2 secondes pour que le thread s'arrête

# Classe princiapale pour la synthèse vocale
# Initialisée qu'une unique fois, cette classe permet d'orchestrer les synthèses vocales en créant ou en stoppant des workers
class AudioSynthesizer(QObject):
    finished_speaking = pyqtSignal()  # Signal global indiquant que toute synthèse vocale est terminée

    def __init__(self):
        super().__init__()
        self.worker = None  # Initialisation d'un objet worker vide pour la synthèse vocale

    # Méthode pour initialiser et lancer un worker de synthèse vocale
    def speak(self, text: str):
        if not text.strip():
            return

        self.stop()  # Arrêt de toute synthèse vocale en cours pour pouvoir initialiser un nouvel objet worker
        self.worker = AudioSynthesizerWorker(text)  # Initialisation du worker pour la synthèse vocale spontanée
        self.worker.finished.connect(self.finished_speaking)  # Connection du signal global de fin de cette classe au signal de fin du worker créé
        self.worker.start()  # Exécution du run du worker créé

    # Méthode pour stopper un worker de synthèse vocale
    def stop(self):
        if self.worker is not None and self.worker.isRunning():
            self.worker.stop()  # Appel de la méthode du worker pour stopper sa run active
            self.worker = None  # Remise à zero de l'objet worker


