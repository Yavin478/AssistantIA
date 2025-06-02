''' Auteur : Yavin 4u78 (avec chatGPT)
Fichier pour la reconnaissance vocale.
'''

from OllamaAPI import *

# Classe permettant la reconnaissance vocale et la transcription en texte.
class AudioRecorder:
    def __init__(self, update_ui_callback):
        self.is_recording = False
        self.audio = []
        self.thread = None
        self.update_ui_callback = update_ui_callback  # pour mettre à jour la GUI après transcription

    def audio_callback(self, indata, frames, time, status):
        if status:
            print("⚠️ Audio stream status:", status)
        self.audio.append(indata.copy())

    # Méthode permettant de lancer l'enregistrement audio.
    def start_recording(self):
        self.is_recording = True
        self.audio = []

        def _record():
            with sd.InputStream(samplerate=16000, channels=1, callback=self.audio_callback):
                while self.is_recording:
                    sd.sleep(100)

        self.thread = threading.Thread(target=_record)
        self.thread.start()

    # Méthode permettant de stopper la transcription audio.
    def stop_and_transcribe(self):
        self.is_recording = False
        self.thread.join()
        audio_data = np.concatenate(self.audio, axis=0)
        audio_int16 = np.int16(audio_data * 32767)
        text = self.transcribe_audio(audio_int16, 16000)

        # Met à jour l'UI (champ texte, envoi du message, etc.)
        if self.update_ui_callback:
            self.update_ui_callback(text)

    # Méthode permettant de transcrire l'audio enregistré en texte.
    def transcribe_audio(self, audio, samplerate):
        # Générer un chemin temporaire unique
        temp_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.wav")

        # Enregistrer le fichier audio
        wav.write(temp_path, samplerate, audio)

        # Charger le modèle
        model = WhisperModel("base", device="auto", compute_type="int8")

        # Transcrire l’audio
        segments, _ = model.transcribe(temp_path)

        # Nettoyer le fichier
        os.remove(temp_path)

        return "".join([s.text for s in segments]).strip()

# Classe permettant de retranscrire le texte obtenu en audio.
class AudioSynthesizer:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", Settings.synthetic_rate)
        self.engine.setProperty("volume", Settings.synthetic_volume)

    # Méthode pour le text-to-speech.
    def speak(self, text: str):
        if not text.strip():
            return
        self.engine.say(text)
        self.engine.runAndWait()
