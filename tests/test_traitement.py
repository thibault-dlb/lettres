import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lettres_app.traitement import (  # noqa: E402
    EPAISSEUR,
    TAILLE,
    TraceInvalide,
    bords_touches,
    rendre_image,
)

# Tracés de test en coordonnées d'écran (origine en haut à gauche)
LETTRE_HAUTE = [[(100, 50), (100, 350)], [(100, 200), (160, 200)]]  # 60 x 300
LETTRE_LARGE = [[(40, 100), (440, 100)], [(240, 100), (240, 160)]]  # 400 x 60
LETTRE_CARREE = [[(50, 50), (250, 50), (250, 250), (50, 250), (50, 50)]]
UN_TRAIT = [[(10, 10), (60, 80), (120, 20), (180, 90)]]
POINT_UNIQUE = [[(10, 10), (10, 10)]]
TRES_PETIT = [[(10, 10), (14, 14)]]


def etendue_encre(image):
    """Boîte englobante (gauche, haut, droite, bas) des pixels sombres."""
    sombre = image.point(lambda v: 255 if v < 128 else 0)
    return sombre.getbbox()


class TestRendu(unittest.TestCase):
    def test_taille_et_mode(self):
        for traits in (LETTRE_HAUTE, LETTRE_LARGE, LETTRE_CARREE, UN_TRAIT):
            image = rendre_image(traits)
            self.assertEqual(image.size, (TAILLE, TAILLE))
            self.assertEqual(image.mode, "L")

    def test_touche_deux_bords_opposes_au_minimum(self):
        for traits in (LETTRE_HAUTE, LETTRE_LARGE, LETTRE_CARREE, UN_TRAIT):
            bords = bords_touches(rendre_image(traits))
            self.assertGreaterEqual(len(bords), 2)
            self.assertTrue(
                {"haut", "bas"} <= bords or {"gauche", "droite"} <= bords,
                f"bords touchés : {bords}",
            )

    def test_lettre_haute_touche_haut_et_bas_et_reste_centree(self):
        image = rendre_image(LETTRE_HAUTE)
        gauche, haut, droite, bas = etendue_encre(image)
        self.assertEqual((haut, bas), (0, TAILLE))
        # largeur finale = 60 * (512 / 300) + trait, centrée
        marge_gauche = gauche
        marge_droite = TAILLE - droite
        self.assertLessEqual(abs(marge_gauche - marge_droite), 2)

    def test_carre_touche_quatre_bords(self):
        self.assertEqual(
            bords_touches(rendre_image(LETTRE_CARREE)),
            {"haut", "bas", "gauche", "droite"},
        )

    def test_aucune_deformation(self):
        # L'étendue de l'encre sur le petit côté suit exactement l'échelle du grand côté.
        image = rendre_image(LETTRE_LARGE)
        gauche, haut, droite, bas = etendue_encre(image)
        echelle = (TAILLE - EPAISSEUR) / 400
        attendu_hauteur = 60 * echelle + EPAISSEUR
        self.assertAlmostEqual(bas - haut, attendu_hauteur, delta=2)
        self.assertEqual((gauche, droite), (0, TAILLE))

    def test_epaisseur_constante_quelle_que_soit_la_taille_du_trace(self):
        petit = [[(0, 0), (0, 40)]]
        grand = [[(0, 0), (0, 400)]]
        largeurs = []
        for traits in (petit, grand):
            gauche, _, droite, _ = etendue_encre(rendre_image(traits))
            largeurs.append(droite - gauche)
        self.assertLessEqual(abs(largeurs[0] - largeurs[1]), 1)
        self.assertAlmostEqual(largeurs[0], EPAISSEUR, delta=2)

    def test_trait_non_coupe_aux_bords(self):
        # Les extrémités arrondies du trait doivent être entières : la colonne/ligne de bord
        # ne contient qu'un petit morceau d'encre, pas toute l'épaisseur aplatie.
        image = rendre_image([[(0, 0), (0, 300)]])
        gauche, haut, droite, bas = etendue_encre(image)
        self.assertEqual((haut, bas), (0, TAILLE))
        # Un trait vertical centré : largeur d'encre = épaisseur, avec marges égales.
        self.assertAlmostEqual(droite - gauche, EPAISSEUR, delta=2)
        self.assertLessEqual(abs(gauche - (TAILLE - droite)), 2)
        # Bout arrondi complet : la ligne du bord n'a que les pixels du sommet de l'arrondi.
        encre_sur_bord = sum(1 for x in range(TAILLE) if image.getpixel((x, 0)) < 128)
        self.assertLess(encre_sur_bord, EPAISSEUR)
        # ... mais l'arrondi complet est présent juste en dessous.
        encre_ligne_9 = sum(1 for x in range(TAILLE) if image.getpixel((x, EPAISSEUR // 2)) < 128)
        self.assertGreaterEqual(encre_ligne_9, EPAISSEUR - 2)

    def test_fond_blanc_et_trait_noir(self):
        image = rendre_image(LETTRE_HAUTE)
        self.assertEqual(image.getpixel((TAILLE - 1, 0)), 255)
        self.assertEqual(image.getpixel((TAILLE // 2, TAILLE // 2)), 0)

    def test_trace_vide(self):
        with self.assertRaises(TraceInvalide):
            rendre_image([])
        with self.assertRaises(TraceInvalide):
            rendre_image([[]])

    def test_trace_trop_petit(self):
        for traits in (POINT_UNIQUE, TRES_PETIT):
            with self.assertRaises(TraceInvalide):
                rendre_image(traits)


if __name__ == "__main__":
    unittest.main()
