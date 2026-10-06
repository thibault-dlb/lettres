"""Transformation d'un tracé libre en image 512x512 conforme aux consignes.

Le tracé est redessiné avec un seul facteur d'échelle (aucune déformation) :
son plus grand côté occupe toute l'image, il touche donc au moins deux bords
opposés ; l'autre dimension est centrée.
"""

from PIL import Image, ImageDraw

TAILLE = 512
EPAISSEUR = 18  # épaisseur du trait dans l'image finale, identique pour toutes les images
SURECHANTILLONNAGE = 4  # rendu agrandi puis réduit pour lisser le trait
TAILLE_MINIMALE = 10  # plus grand côté minimal du tracé, en pixels d'écran
SEUIL_ENCRE = 128  # un pixel plus sombre que ce seuil est de l'encre


class TraceInvalide(ValueError):
    """Le tracé est vide ou trop petit pour être mis à l'échelle."""


def _boite(traits):
    points = [p for trait in traits for p in trait]
    if not points:
        raise TraceInvalide("Aucun tracé : dessine la lettre avant de continuer.")
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return min(xs), min(ys), max(xs), max(ys)


def bords_touches(image):
    """Retourne l'ensemble des bords ('haut', 'bas', 'gauche', 'droite') qui portent de l'encre."""
    largeur, hauteur = image.size
    pixels = image.load()

    def a_de_l_encre(coordonnees):
        return any(pixels[x, y] < SEUIL_ENCRE for x, y in coordonnees)

    bords = {
        "haut": [(x, 0) for x in range(largeur)],
        "bas": [(x, hauteur - 1) for x in range(largeur)],
        "gauche": [(0, y) for y in range(hauteur)],
        "droite": [(largeur - 1, y) for y in range(hauteur)],
    }
    return {nom for nom, coordonnees in bords.items() if a_de_l_encre(coordonnees)}


def rendre_image(traits, taille=TAILLE, epaisseur=EPAISSEUR):
    """Convertit les traits (listes de points (x, y) de l'écran) en image PNG 512x512.

    Lève TraceInvalide si le tracé est vide ou trop petit.
    """
    x_min, y_min, x_max, y_max = _boite(traits)
    largeur = x_max - x_min
    hauteur = y_max - y_min
    plus_grand = max(largeur, hauteur)
    if plus_grand < TAILLE_MINIMALE:
        raise TraceInvalide("Tracé trop petit : dessine la lettre plus grande.")

    echelle = taille / plus_grand
    # Le plus grand côté va de 0 à taille ; l'autre est centré.
    decalage_x = (taille - largeur * echelle) / 2
    decalage_y = (taille - hauteur * echelle) / 2

    facteur = SURECHANTILLONNAGE
    grand = Image.new("L", (taille * facteur, taille * facteur), 255)
    dessin = ImageDraw.Draw(grand)
    rayon = epaisseur * facteur / 2

    def convertir(point):
        x = ((point[0] - x_min) * echelle + decalage_x) * facteur
        y = ((point[1] - y_min) * echelle + decalage_y) * facteur
        return (x, y)

    for trait in traits:
        points = [convertir(p) for p in trait]
        if len(points) > 1:
            dessin.line(points, fill=0, width=int(epaisseur * facteur), joint="curve")
        for x, y in points:  # bouts et jonctions arrondis
            dessin.ellipse((x - rayon, y - rayon, x + rayon, y + rayon), fill=0)

    image = grand.resize((taille, taille), Image.LANCZOS)

    if len(bords_touches(image)) < 2:
        raise TraceInvalide("La lettre ne touche pas deux bords de l'image.")
    return image
