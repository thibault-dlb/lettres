"""Point d'entrée : python -m lettres_app (utilisé par lancer.py)."""

import os

from .interface import lancer_application
from .stockage import DOSSIER_SORTIE

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    lancer_application(os.path.join(RACINE, DOSSIER_SORTIE))
