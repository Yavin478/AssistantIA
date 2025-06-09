from AudioBase import *

class AudioRecorderWorker(QThread, AudioBase):
    transcription_ready = pyqtSignal(str)  # Signal de fin de l'enregistrement pour l'envoi de la transcription
    stop_recording_signal = pyqtSignal()  # Signal pour l'arrêt manuel de l'enregistrement

    def __init__(self, samplerate, silence_threshold, silence_duration):
        AudioBase.__init__(self)  # Initialise la partie AudioBase
        QThread.__init__(self)  # Initialise la partie QThread
        self.samplerate = samplerate
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self.is_recording = False
        self.audio = []
        self.q = queue.Queue()

    def run(self):
        if Settings.debug: print("Début du run d'enregistrement")
        self.is_recording = True
        self.audio = []
        silence_start = None

        def audio_callback(indata, frames, time, status):
            if status:
                print("Status du micro :", status)
            self.q.put(indata.copy())

        with sd.InputStream(samplerate=self.samplerate, channels=1, callback=audio_callback):
            while self.is_recording:
                try:
                    data = self.q.get(timeout=0.5)
                    self.audio.append(data)

                    volume = np.linalg.norm(data) / np.sqrt(len(data))

                    if volume < self.silence_threshold:
                        if silence_start is None:
                            silence_start = time.time()
                        elif time.time() - silence_start > self.silence_duration:
                            print("Silence prolongé détecté. Arrêt de l'enregistrement.")
                            self.stop_and_transcribe()
                            break
                    else:
                        silence_start = None

                except queue.Empty:
                    continue

    # Méthode permettant de changer l'état du thread en indiquant l'arrêt manuel d'un enregistrement
    # Stop l'enregistrement en cours de la méthode "run" via la sortie de la boucle 'while'
    def stop_recording(self):
        self.is_recording = False

    def stop_and_transcribe(self):
        self.stop_recording()
        if not self.audio:
            if Settings.debug : print("Aucune donnée audio enregistrée.")
            return

        audio_data = np.concatenate(self.audio, axis=0)
        audio_int16 = np.int16(audio_data * 32767)
        text = self.transcribe_audio(audio_int16)
        self.transcription_ready.emit(text)


class AudioRecorder(AudioBase):
    def __init__(self, update_ui_callback):
        super().__init__()
        self.update_ui_callback = update_ui_callback
        self.worker = None

    def start_recording(self):
        self.worker = AudioRecorderWorker(self.samplerate, Settings.silence_threshold, Settings.silence_duration)
        self.worker.transcription_ready.connect(self.update_ui_callback)
        self.worker.start()
        if Settings.debug: print("Début de l'enregistrement vocal")

    def stop_recording(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop_recording_signal.emit()
            self.worker.quit()
            self.worker.wait()
            if Settings.debug: print("Arrêt manuel de l'enregistrement")

    def stop_and_transcribe(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop_and_transcribe()
            self.worker.quit()
            self.worker.wait()
