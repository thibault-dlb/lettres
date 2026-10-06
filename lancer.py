"""Script de lancement unique : vérifie et installe tout, puis ouvre le logiciel.

    python lancer.py              # vérifie les dépendances puis ouvre la fenêtre
    python lancer.py --verifier   # vérifie / installe seulement, sans ouvrir la fenêtre

Tout est installé dans le dossier .venv de ce projet : rien n'est modifié ailleurs.
"""

import os
import subprocess
import sys

for flux in (sys.stdout, sys.stderr):  # évite un plantage sur les consoles aux accents limités
    if hasattr(flux, "reconfigure"):
        flux.reconfigure(errors="replace")

RACINE = os.path.dirname(os.path.abspath(__file__))
DOSSIER_VENV = os.path.join(RACINE, ".venv")
PYTHON_VENV = os.path.join(
    DOSSIER_VENV, "Scripts" if os.name == "nt" else "bin", "python.exe" if os.name == "nt" else "python"
)
EXIGENCES = os.path.join(RACINE, "requirements.txt")
VERSION_MINIMALE = (3, 8)


def erreur(message):
    print(f"\nErreur : {message}", file=sys.stderr)
    sys.exit(1)


def verifier_python():
    if sys.version_info < VERSION_MINIMALE:
        erreur(
            f"Python {VERSION_MINIMALE[0]}.{VERSION_MINIMALE[1]} ou plus récent est nécessaire "
            f"(version actuelle : {sys.version.split()[0]}). Installe-le sur https://www.python.org/downloads/"
        )
    try:
        import tkinter  # noqa: F401
    except ImportError:
        if sys.platform.startswith("linux"):
            conseil = "Installe-le avec : sudo apt install python3-tk"
        elif sys.platform == "darwin":
            conseil = "Réinstalle Python depuis https://www.python.org/downloads/ (la version officielle inclut Tkinter)."
        else:
            conseil = "Réinstalle Python depuis https://www.python.org/downloads/ en laissant « tcl/tk and IDLE » coché."
        erreur(f"Tkinter (l'interface graphique de Python) est introuvable. {conseil}")


def creer_venv():
    if os.path.exists(PYTHON_VENV):
        return
    print("Première utilisation : création de l'environnement (.venv)...")
    resultat = subprocess.run([sys.executable, "-m", "venv", DOSSIER_VENV])
    if resultat.returncode != 0 or not os.path.exists(PYTHON_VENV):
        conseil = " Sous Linux : sudo apt install python3-venv" if sys.platform.startswith("linux") else ""
        erreur("impossible de créer l'environnement virtuel." + conseil)


def dependances_ok():
    test = "import PIL.Image, PIL.ImageTk, PIL.ImageDraw"
    return subprocess.run([PYTHON_VENV, "-c", test], capture_output=True).returncode == 0


def installer_dependances():
    if dependances_ok():
        return
    print("Installation des dépendances (Pillow), cela peut prendre une minute...")
    resultat = subprocess.run(
        [PYTHON_VENV, "-m", "pip", "install", "--disable-pip-version-check", "-r", EXIGENCES]
    )
    if resultat.returncode != 0 or not dependances_ok():
        erreur("l'installation des dépendances a échoué. Vérifie ta connexion internet puis relance.")


def main():
    os.chdir(RACINE)
    verifier_python()
    creer_venv()
    installer_dependances()
    if "--verifier" in sys.argv:
        print("Tout est prêt : lance « python lancer.py » pour ouvrir le logiciel.")
        return 0
    return subprocess.call([PYTHON_VENV, "-m", "lettres_app"], cwd=RACINE)


if __name__ == "__main__":
    sys.exit(main())
