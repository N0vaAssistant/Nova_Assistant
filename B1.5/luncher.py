import subprocess
import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QMessageBox, QSizePolicy
)
from PyQt6.QtGui import QPixmap, QFont, QIcon
from PyQt6.QtCore import Qt, QSize

# Définition des noms de fichiers pour une meilleure maintenabilité
FRENCH_BAT_FILE = "start_fr.bat"
ENGLISH_BAT_FILE = "start_en.bat"
LOGO_PATH = "public/images/nova_logo.png"  # Chemin vers le logo

class NovaLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        """Initialise l'interface utilisateur de la fenêtre."""
        self.setWindowTitle("Nova Launcher")
        self.setWindowIcon(QIcon(LOGO_PATH))  # Utilise le logo comme icône de la fenêtre
        self.setFixedSize(500, 400)  # Taille ajustée pour inclure le texte supplémentaire

        # Layout principal
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        # Logo
        self.logo_label = QLabel(self)
        pixmap = QPixmap(LOGO_PATH)
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(300, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.logo_label.setPixmap(scaled_pixmap)
            self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            self.logo_label.setText("NOVA ASSISTANT")
            self.logo_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
            self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            QMessageBox.warning(self, "Erreur de chargement", f"Impossible de charger le logo : {LOGO_PATH}")

        layout.addWidget(self.logo_label)

        # Texte sous le logo
        self.instruction_label = QLabel(
            "Veuillez sélectionner votre langue pour le démarrage de Nova\nPlease select your language to launch Nova",
            self
        )
        self.instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.instruction_label.setFont(QFont("Arial", 12))
        layout.addWidget(self.instruction_label)

        # Bouton Français
        self.fr_button = QPushButton("Français", self)
        self.fr_button.setFont(QFont("Arial", 16))
        self.fr_button.setFixedSize(200, 60)
        self.fr_button.clicked.connect(lambda: self.launch_nova(FRENCH_BAT_FILE))
        layout.addWidget(self.fr_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # Bouton Anglais
        self.en_button = QPushButton("English", self)
        self.en_button.setFont(QFont("Arial", 16))
        self.en_button.setFixedSize(200, 60)
        self.en_button.clicked.connect(lambda: self.launch_nova(ENGLISH_BAT_FILE))
        layout.addWidget(self.en_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)

        # Style CSS
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f2f5;
                font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
            }
            QLabel#logo_label {
                margin-bottom: 20px;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                transition: background-color 0.3s ease;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004085;
            }
        """)

    def launch_nova(self, filename: str):
        file_path = os.path.join(os.getcwd(), filename)

        if not os.path.exists(file_path):
            QMessageBox.critical(self, "Erreur de fichier",
                                 f"Le fichier '{filename}' est introuvable à l'emplacement :\n{file_path}\n"
                                 "Veuillez vous assurer que les fichiers .bat sont dans le même répertoire que le lanceur.")
            return

        try:
            subprocess.Popen([file_path], shell=True)
            QMessageBox.information(self, "Lancement réussi",
                                    f"Nova a été lancé via '{filename}'. Le lanceur va maintenant se fermer.")
            QApplication.instance().quit()
        except Exception as e:
            QMessageBox.critical(self, "Erreur de lancement",
                                 f"Une erreur inattendue est survenue lors du démarrage de '{filename}' :\n{e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    launcher = NovaLauncher()
    launcher.show()
    sys.exit(app.exec())
