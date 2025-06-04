''' Auteur : Yavin 4u78 (avec chatGPT)
Fichier pour les importations des librairies externes nécessaires au projet.
'''

# Pour les appels API
import requests

# Pour le projet en général
from dataclasses import dataclass
import time

# Pour l'interface graphique
import sys
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QScrollArea,QLabel, QHBoxLayout, QFrame, QPushButton, QHBoxLayout, QComboBox,QCheckBox )

# Pour les intéractions vocales
import os
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