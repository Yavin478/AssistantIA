''' Auteur : Yavin 4u78 (avec chatGPT)
Fichier pour les importations des librairies externes nécessaires au projet.
'''

# Pour les appels API.
import requests

# Pour le projet en général.
from dataclasses import dataclass

# Pour l'interface graphique.
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QScrollArea,QLabel, QHBoxLayout, QFrame)

# Pour l'intéraction vocale.
import os
import threading
import sounddevice as sd
import uuid
import numpy as np
import tempfile
import scipy.io.wavfile as wav
from faster_whisper import WhisperModel
import qtawesome as qta
from PyQt5.QtWidgets import QPushButton, QHBoxLayout