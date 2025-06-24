''' Auteur : Yavin 4u78 (avec l'aide de chatGPT et Le Chat)
Fichier permettant d'indexer les fichiers personnels pour le RAG.
'''

from DocumentLoader import *

class IndexBuilder:
    def __init__(self, index_path, document_loader, embed_model_name ):
        self.index_path = index_path
        self.hash_path = os.path.join(self.index_path, "docs_hash.json")
        self.document_loader = document_loader
        self.embed_model_name = embed_model_name

        try :
            LlamaIndexSettings.embed_model = HuggingFaceEmbedding(model_name=Settings.embed_model_name)  # Définit le modèle d'embedding pour la vectorisation et la récupération
            if Settings.debug : print(f"Modèle d'embedding défini : {Settings.embed_model_name}")
        except Exception as e :
            print(f"Exception levée lors de la configuration du modèle d'embedding : \n{e}")


    def compute_docs_hash(self):
        file_info = []
        for root, _, files in os.walk(Settings.folder_path):
            for file in sorted(files):
                filepath = os.path.join(root, file)
                stat = os.stat(filepath)
                file_info.append({
                    "name": file,
                    "size": stat.st_size,
                    "mtime": stat.st_mtime
                })
        if Settings.debug: print("Calcul du hash des documents courant effectué")
        return hashlib.sha256(json.dumps(file_info).encode()).hexdigest()

    def load_previous_hash(self):
        if os.path.exists(self.hash_path):
            with open(self.hash_path, "r") as f:
                if Settings.debug: print("Chargement du hash des documents")
                return json.load(f).get("hash")
        return None

    def save_current_hash(self, hash_value):
        os.makedirs(self.index_path, exist_ok=True)
        with open(self.hash_path, "w") as f:
            json.dump({"hash": hash_value}, f)
        if Settings.debug: print("Sauvegarde du hash des documents")

    def build_index(self):
        try:
            documents = self.document_loader.load_documents()
            if Settings.debug: print("Chargement des documents effectué")
            index = VectorStoreIndex.from_documents(documents)
            if Settings.debug: print("Vector store créé")
            index.storage_context.persist(persist_dir=self.index_path)
            if Settings.debug: print("Vector store enregistré")
            return index
        except Exception as e:
            print(f"Exception levée au niveau de la construction de l'index : \n{e}")
            return None

    def load_or_build_index(self):
        try :
            current_hash = self.compute_docs_hash()
            previous_hash = self.load_previous_hash()

            if current_hash != previous_hash:
                if Settings.debug: print("Changement détecté dans les documents : reconstruction de l’index.")
                index = self.build_index()
                self.save_current_hash(current_hash)
                return index
            else:
                if Settings.debug: print("Aucun changement détecté : chargement de l’index existant.")
                storage_context = StorageContext.from_defaults(persist_dir=self.index_path)
                if Settings.debug: print("Enregistrement du contexte")
                return load_index_from_storage(storage_context)

        except Exception as e:
            print(f"Exception levée lors du chargement ou de la construction de l'index : \n{e}")
            return None

    def get_query_engine(self):
        try :
            index = self.load_or_build_index()
            if Settings.debug: print("Création ou chargement de l'index effectué avec succès")
            return index.as_query_engine(llm=MockLLM(),
                response_mode="compact",  # ou "tree_summarize" pour résumer plusieurs docs
                similarity_top_k=5,  # nombre de documents les plus similaires
                include_source=True   # ⬅️ Ceci permet d’inclure les métadonnées des sources dans la réponse)
                )
        except Exception as e:
            print(f"Exception levée lors de la création du moteur de requêtes : \n{e}")
            return None
