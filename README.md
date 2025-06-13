## Auteur du projet

Projet développé par Yavin 4u78 avec l'aide de ChatGPT et Le Chat, dans le cadre d'un projet personnel autour de l’intelligence artificielle locale, open source.

---

## 🧠 Assistant IA Local – avec Ollama, PyQt5 et Reconnaissance Vocale

Ce projet propose un assistant personnel basé sur un **modèle de langage open source** fonctionnant **entièrement en local**, sans connexion Internet nécessaire. Il utilise :

- 🧠 Un **LLM open source** via [Ollama](https://ollama.com/)
- 🎙️ Une **interface vocale** (reconnaissance de la parole)
- 💬 Une **interface graphique simple et claire** avec PyQt5
- 🐍 Le tout codé en **Python**, uniquement avec des outils **open source**

---

## 🧰 Fonctionnalités

- Interface graphique intuitive (PyQt5)
- Conversation multilingue avec un LLM téléchargé en local avec Ollama
- Historique des conversations sauvegardé dans un fichier texte
- Possibilité d’interagir par la voix (transcription automatique)
- Mode "mains libres" pour les commandes vocales sans interaction manuelle
- Synthèse vocale pour les réponses de l'assistant

---

## 📦 Dépendances

Voici la liste complète des bibliothèques Python requises :

```bash
pip install pyqt5 qtawesome requests sounddevice scipy faster-whisper pyttsx3 numpy

