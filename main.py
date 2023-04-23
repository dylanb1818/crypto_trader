from gemini_API import GeminiAPI
from PyQt5.QtWidgets import *

if __name__ == '__main__':
    app = QApplication([])
    a = GeminiAPI()
    app.exec_()