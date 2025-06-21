''' Auteur : Yavin 4u78 (avec l'aide de chatGPT et Le Chat)
Fichier permettant de charger les documents personnels pour le RAG.
'''

from AudioHandsFreeListener import *

class DocumentLoader:
    def __init__(self, folder_path):
        self.folder_path = folder_path  # Initialisation du chemin du répertoire contenant les fichiers personnels

    # Méthode pour charger les fichiers locaux présents dans le repo prévu pour le RAG
    def load_documents(self):
        documents = SimpleDirectoryReader(self.folder_path).load_data()
        return documents