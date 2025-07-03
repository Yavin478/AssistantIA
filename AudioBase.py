''' Auteur : Yavin 4u78 (avec l'aide de chatGPT et Le Chat)
Fichier contenant la classe de base pour l'initialisation et l'utilisation du modèle Whisper pour toutes les intéractions vocales du programme.
'''

from Settings import *

# Classe de base commune pour l'utilisation des fonctionnalités vocales du modele Whisper
class AudioBase:
    def __init__(self, model_size="base", device="auto", compute_type="int8"):
        self.samplerate = Settings.samplerate
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)  # Initialisation du modèle Whisper

    # Méthode pour récupérer la transcription obtenue avec le modèle Whisper
    def transcribe_audio(self, audio, samplerate=None):
        if samplerate is None:
            samplerate = self.samplerate

        temp_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}.wav")
        wav.write(temp_path, samplerate, audio)
        segments, _ = self.model.transcribe(temp_path)
        os.remove(temp_path)
        return "".join([s.text for s in segments]).strip()
