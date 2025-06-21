''' Auteur : Yavin 4u78 (avec l'aide de chatGPT et Le Chat)
Fichier principale du programme.
'''

from UI import *

if __name__=='__main__':
    app = QApplication(sys.argv)
    window = AssistantWindow()
    window.show()
    sys.exit(app.exec_())

    # try:
    #     prompt_user = "Quelles sont les commandes pour installer chromium ? "
    #     print(ask_ollama_with_rag(prompt_user))
    #     print("Ok")
    # except Exception as e:
    #     print(e)