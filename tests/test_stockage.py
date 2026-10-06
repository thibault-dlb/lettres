import os
import sys
import tempfile
import unittest

from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lettres_app import stockage  # noqa: E402


class TestStockage(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dossier = os.path.join(self._tmp.name, "lettre")
        self.image = Image.new("L", (512, 512), 255)

    def tearDown(self):
        self._tmp.cleanup()

    def test_nommage(self):
        self.assertEqual(stockage.nom_fichier("a", 1), "a_01.png")
        self.assertEqual(stockage.nom_fichier("b", 13), "b_13.png")
        self.assertEqual(stockage.nom_fichier("g", 20), "g_20.png")

    def test_dossier_vide_commence_a_a_01(self):
        self.assertEqual(stockage.prochaine_image(self.dossier), ("a", 1))

    def test_enregistrer_cree_le_dossier_et_le_png(self):
        chemin = stockage.enregistrer(self.image, self.dossier, "a", 1)
        self.assertTrue(os.path.isfile(chemin))
        with Image.open(chemin) as lue:
            self.assertEqual(lue.format, "PNG")
            self.assertEqual(lue.size, (512, 512))

    def test_reprise_apres_fichiers_partiels(self):
        for numero in range(1, 4):
            stockage.enregistrer(self.image, self.dossier, "a", numero)
        self.assertEqual(stockage.prochaine_image(self.dossier), ("a", 4))

    def test_reprise_trouve_le_premier_trou(self):
        for numero in (1, 2, 4):
            stockage.enregistrer(self.image, self.dossier, "a", numero)
        self.assertEqual(stockage.prochaine_image(self.dossier), ("a", 3))

    def test_passage_a_la_lettre_suivante(self):
        for numero in range(1, 21):
            stockage.enregistrer(self.image, self.dossier, "a", numero)
        self.assertEqual(stockage.prochaine_image(self.dossier), ("b", 1))
        self.assertEqual(stockage.nombre_images(self.dossier, "a"), 20)

    def test_tout_termine(self):
        for lettre in stockage.LETTRES:
            for numero in range(1, 21):
                stockage.enregistrer(self.image, self.dossier, lettre, numero)
        self.assertIsNone(stockage.prochaine_image(self.dossier))

    def test_pas_d_ecrasement(self):
        stockage.enregistrer(self.image, self.dossier, "a", 1)
        with self.assertRaises(FileExistsError):
            stockage.enregistrer(self.image, self.dossier, "a", 1)

    def test_ordre_des_lettres(self):
        self.assertEqual(stockage.LETTRES, ["a", "b", "f", "k", "j", "g"])


if __name__ == "__main__":
    unittest.main()
