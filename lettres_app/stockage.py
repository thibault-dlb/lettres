"""Nommage des fichiers, dossier de sortie et reprise du parcours."""

import os
import shutil

LETTRES = ["a", "b", "f", "h", "j", "g"]
IMAGES_PAR_LETTRE = 20
DOSSIER_SORTIE = "lettre"


def nom_fichier(lettre, numero):
    """Ex. nom_fichier('a', 1) -> 'a_01.png'."""
    return f"{lettre}_{numero:02d}.png"


def chemin_image(dossier, lettre, numero):
    return os.path.join(dossier, nom_fichier(lettre, numero))


def prochaine_image(dossier, lettres=LETTRES, par_lettre=IMAGES_PAR_LETTRE):
    """Première image manquante (lettre, numéro), ou None si tout est fait."""
    for lettre in lettres:
        for numero in range(1, par_lettre + 1):
            if not os.path.exists(chemin_image(dossier, lettre, numero)):
                return lettre, numero
    return None


def nombre_images(dossier, lettre, par_lettre=IMAGES_PAR_LETTRE):
    """Nombre d'images déjà enregistrées pour une lettre."""
    return sum(
        os.path.exists(chemin_image(dossier, lettre, n))
        for n in range(1, par_lettre + 1)
    )


def enregistrer(image, dossier, lettre, numero):
    """Enregistre l'image en PNG sans jamais écraser un fichier existant."""
    os.makedirs(dossier, exist_ok=True)
    chemin = chemin_image(dossier, lettre, numero)
    if os.path.exists(chemin):
        raise FileExistsError(f"{nom_fichier(lettre, numero)} existe déjà.")
    image.save(chemin, format="PNG")
    return chemin


def dossier_telechargements():
    return os.path.join(os.path.expanduser("~"), "Downloads")


def deplacer_vers_telechargements(dossier, telechargements=None):
    """Déplace le dossier dans Téléchargements et retourne son nouveau chemin.

    Si un dossier du même nom existe déjà, un suffixe est ajouté : lettre_2, lettre_3...
    """
    cible_parent = telechargements or dossier_telechargements()
    os.makedirs(cible_parent, exist_ok=True)
    nom = os.path.basename(os.path.normpath(dossier))
    cible = os.path.join(cible_parent, nom)
    compteur = 2
    while os.path.exists(cible):
        cible = os.path.join(cible_parent, f"{nom}_{compteur}")
        compteur += 1
    shutil.move(dossier, cible)
    return cible
