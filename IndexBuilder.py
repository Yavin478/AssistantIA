''' Auteur : Yavin 4u78 (avec l'aide de chatGPT et Le Chat)
Fichier permettant d'indexer les fichiers personnels pour le RAG.
'''

from DocumentLoader import *

class IndexBuilder:
    def __init__(self):
        self.index_path = "storage"
        self.document_loader = DocumentLoader(Settings.folder_path)

        LlamaIndexSettings.embed_model = HuggingFaceEmbedding(model_name=Settings.embed_model_name)  # Définit le modèle d'embedding pour la vectorisation et la récupération

    def build_index(self):
        documents = self.document_loader.load_documents()
        if Settings.debug: print("Chargement des documents effectué")
        index = VectorStoreIndex.from_documents(documents)
        if Settings.debug: print("Vector store créé")
        index.storage_context.persist(persist_dir=self.index_path)
        if Settings.debug: print("Vector store enregistré")
        return index

    def load_or_build_index(self):
        if os.path.exists(self.index_path):
            if Settings.debug : print("Chargement de l'index")
            storage_context = StorageContext.from_defaults(persist_dir=self.index_path)
            if Settings.debug: print("Enregistrement du contexte")
            return load_index_from_storage(storage_context)
        else:
            return self.build_index()

    def get_query_engine(self):
        index_loaded = self.load_or_build_index()
        if Settings.debug: print("Création de l'index effectuée avec succès")
        return index_loaded.as_query_engine(llm=MockLLM())