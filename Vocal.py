''' Auteur : Yavin 4u78 (avec chatGPT)
Fichier ayant les classes pour les fonctionnalités d'intéraction vocale avec l'assistant.
'''

from OllamaAPI import *

# Classe de base commune pour l'utilisation des fonctionnalités vocales du modele Whisper
class BaseAudioProcessor:
    def __init__(self, model_size="base", device="auto", compute_type="int8"):
        self.samplerate = 16000
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)

    def transcribe_audio(self, audio, samplerate=None):
        if samplerate is None:
            samplerate = self.samplerate

        temp_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.wav")
        wav.write(temp_path, samplerate, audio)
        segments, _ = self.model.transcribe(temp_path)
        os.remove(temp_path)
        return "".join([s.text for s in segments]).strip()


# Classe pour l'enregistrement manuel avec arrêt sur silence
class AudioRecorder(BaseAudioProcessor):
    def __init__(self, update_ui_callback):
        super().__init__()
        self.is_recording = False
        self.audio = []
        self.thread = None
        self.update_ui_callback = update_ui_callback

        # Configuration du silence
        self.q = queue.Queue()
        self.silence_threshold = Settings.silence_threshold
        self.silence_duration = Settings.silence_duration

    def audio_callback(self, indata, frames, time, status):
        if status:
            print("Status du micro :", status)
        self.q.put(indata.copy())

    def start_recording(self):
        self.is_recording = True
        self.audio = []

        def _record():
            silence_start = None
            with sd.InputStream(samplerate=self.samplerate, channels=1, callback=self.audio_callback):
                while self.is_recording:
                    try:
                        data = self.q.get(timeout=0.5)
                        self.audio.append(data)

                        # Calcul RMS
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

        self.thread = threading.Thread(target=_record)
        self.thread.start()

    def stop_and_transcribe(self):
        if not self.is_recording:
            return

        self.is_recording = False

        # Ne pas join le thread si on est déjà dedans
        if self.thread and threading.current_thread() != self.thread:
            self.thread.join()

        if not self.audio:
            print("Aucune donnée audio enregistrée.")
            return

        audio_data = np.concatenate(self.audio, axis=0)
        audio_int16 = np.int16(audio_data * 32767)
        text = self.transcribe_audio(audio_int16)

        if self.update_ui_callback:
            self.update_ui_callback(text)



# Classe pour l'écoute en mode "mains libres"
class HandsFreeListener(BaseAudioProcessor):
    def __init__(self, on_command_detected):
        super().__init__()
        self.active = False
        self.thread = None
        self.on_command_detected = on_command_detected
        self.buffer_duration = 3
        self.is_listening = False

    def start(self):
        if not self.active:
            self.active = True
            self.thread = threading.Thread(target=self.listen_loop, daemon=True)
            self.thread.start()

    def stop(self):
        self.active = False

    def capture_audio(self, duration):
        return sd.rec(int(duration * self.samplerate), samplerate=self.samplerate, channels=1, dtype='int16')

    def listen_loop(self):
        if Settings.debug : print("Écoute mains libres démarrée.")
        while self.active:
            audio = self.capture_audio(self.buffer_duration)
            sd.wait()
            text = self.transcribe_audio(audio)
            if not text:
                continue

            if Settings.debug : print(f"Texte interprété : {text}")

            if Settings.handfree_keywordstart.lower() in text.lower():
                self.on_command_detected("start_recording")
                if Settings.debug : print("start_recording")


# Classe pour la synthèse vocale
class AudioSynthesizer:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", Settings.synthetic_rate)
        self.engine.setProperty("volume", Settings.synthetic_volume)

    # Méthode pour le text-to-speech
    def speak(self, text: str):
        if not text.strip():
            return
        self.engine.say(text)
        self.engine.runAndWait()