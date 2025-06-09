
from AudioSynthesizer import *

class AudioHandsFreeListenerWorker(QThread, AudioBase):
    command_detected = pyqtSignal(str)  # Signal indiquant le début d'un enregistrement en mode "mains libres" suite à la détection du mot-clé

    def __init__(self, samplerate, buffer_duration, handfree_keywordstart):
        AudioBase.__init__(self)  # Initialise la partie AudioBase
        QThread.__init__(self)  # Initialise la partie QThread
        self.samplerate = samplerate
        self.buffer_duration = buffer_duration
        self.handfree_keywordstart = handfree_keywordstart
        self.active = False

    def run(self):
        self.active = True
        if Settings.debug: print("Écoute mains libres démarrée")
        while self.active:
            audio = self.capture_audio(self.buffer_duration)
            sd.wait()
            text = self.transcribe_audio(audio)
            if not text:
                continue

            if Settings.debug: print(f"Texte interprété : {text}")

            if self.handfree_keywordstart.lower() in text.lower():
                self.command_detected.emit("start_recording")
                if Settings.debug: print("start_recording")

    def capture_audio(self, duration):
        return sd.rec(int(duration * self.samplerate), samplerate=self.samplerate, channels=1, dtype='int16')

    def stop(self):
        self.active = False


class AudioHandsFreeListener(AudioBase):
    def __init__(self, on_command_detected):
        super().__init__()
        self.worker = None
        self.on_command_detected = on_command_detected

    def start(self):
        if self.worker is None or not self.worker.isRunning():
            self.worker = AudioHandsFreeListenerWorker(self.samplerate, Settings.buffer_duration, Settings.handfree_keywordstart)
            self.worker.command_detected.connect(self.on_command_detected)
            self.worker.start()

    def stop(self):
        if self.worker is not None and self.worker.isRunning():
            self.worker.stop()
            self.worker.quit()
            self.worker.wait()

