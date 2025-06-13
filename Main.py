''' Auteur : Yavin 4u78 (avec l'aide de chatGPT et Le Chat)
Fichier principale du programme.
'''

from UI import *

if __name__=='__main__':
    app = QApplication(sys.argv)
    window = AssistantWindow()
    window.show()
    sys.exit(app.exec_())