from AudioRecorder import *

class AudioSynthesizerWorker(QThread):
    speech_finished = pyqtSignal()

    def __init__(self, text):
        super().__init__()
        self.text = text
        self.engine = None
        self.is_running = True

    def run(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", Settings.synthetic_rate)
        self.engine.setProperty("volume", Settings.synthetic_volume)
        self.engine.say(self.text)
        self.engine.runAndWait()
        if self.is_running:
            self.finished.emit()

    def stop(self):
        self.is_running = False
        if self.engine is not None:
            self.engine.stop()
        self.quit()
        self.wait(2000)  # Attendre jusqu'à 2 secondes pour que le thread s'arrête

class AudioSynthesizer(QObject):
    finished_speaking = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.worker = None

    def speak(self, text: str):
        if not text.strip():
            return

        self.stop()  # Arrêter toute synthèse vocale en cours
        self.worker = AudioSynthesizerWorker(text)
        self.worker.finished.connect(self.finished_speaking)
        self.worker.start()

    def stop(self):
        if self.worker is not None and self.worker.isRunning():
            self.worker.stop()
            self.worker = None


