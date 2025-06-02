''' Auteur : Yavin 4u78 (avec chatGPT)
Fichier de configuration des paramètres variables du projet.
'''

from Libraries import *

# Classe contenant les paramètres configurables du projet.
@dataclass
class Settings:
    # Attributs pour l'usage du LLM avec Ollama.

    # Liste des modèles disponibles, téléchargés au préalable avec Ollama.
    available_models = ["mistral:7b", "tinyllama:1.1b-chat-v1-q4_0"]
    # Modèle par défaut.
    model: str = available_models[0]
    # Url de l'API Ollama.
    api_url: str = "http://localhost:11434/api/chat"
    # Prompt système envoyé au LLM.
    system_prompt: str = (
        "Tu es Ignis, un assistant IA francophone utile, honnête et concis. "
        "Tu dois toujours répondre clairement à la question posée en français, sans imaginer de contexte fictif. "
        "Si tu ne sais pas, dis-le franchement."
        "Tu ne dois surtout pas halluciner"
    )

    # Paramètres graphiques.
    window_title: str = "Ignis - Assistant IA local"

    # Paramètres pour la synthèse vocale.
    synthetic_rate: int = 180
    synthetic_volume: float = 1.0

    # Autres attributs.
    debug: bool = False
    history_file: str = "Chat_history.txt"