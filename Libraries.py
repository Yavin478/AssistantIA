''' Auteur : Yavin 4u78 (avec l'aide de chatGPT et Le Chat)
Fichier pour les importations des librairies externes nécessaires au projet.
'''

# Pour les appels API
import requests

# Pour le projet en général
from dataclasses import dataclass
import time
import os
import hashlib
import json
import re

# Pour l'interface graphique
import sys
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QScrollArea,QLabel, QHBoxLayout, QFrame, QPushButton, QHBoxLayout, QComboBox,QCheckBox )

# Pour les intéractions vocales
import threading
import sounddevice as sd
import uuid
import numpy as np
import tempfile
import scipy.io.wavfile as wav
from faster_whisper import WhisperModel
import qtawesome as qta
import pyttsx3
import queue

# Pour le RAG
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, StorageContext, load_index_from_storage
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings as LlamaIndexSettings
from llama_index.core.llms import MockLLM