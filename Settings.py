''' Auteur : Yavin 4u78 (avec chatGPT)
Fichier de configuration des paramètres variables du projet
'''

from Libraries import *

# Classe contenant les paramètres configurables du projet.
@dataclass
class Settings:
    # Attributs pour l'usage du LLM avec Ollama
    model: str = "mistral:7b"
    api_url: str = "http://localhost:11434/api/chat"
    system_prompt: str = (
        "Tu es un assistant IA francophone utile, honnête et concis. "
        "Tu dois toujours répondre clairement à la question posée en français, sans imaginer de contexte fictif. "
        "Si tu ne sais pas, dis-le franchement."
        "Tu ne dois surtout pas halluciner"
    )

    # Autres attributs
    debug: bool = False
    history_file: str = "Chat_history.txt"