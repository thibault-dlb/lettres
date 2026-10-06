import os
import sys
import tempfile
import tkinter as tk
import unittest

from PIL import Image

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from lettres_app import stockage  # noqa: E402
from lettres_app.interface import Application  # noqa: E402


def dessiner(app, points):
    app.commencer_trait(*points[0])
    for point in points[1:]:
        app.ajouter_point(*point)
    app.finir_trait()


class TestInterface(unittest.TestCase):
    def setUp(self):
        try:
            self.racine = tk.Tk()
        except tk.TclError as erreur:  # pas d'écran disponible
            self.skipTest(f"Tkinter indisponible : {erreur}")
        self.racine.withdraw()
        self._tmp = tempfile.TemporaryDirectory()
        self.dossier = os.path.join(self._tmp.name, "lettre")
        self.app = Application(self.racine, self.dossier)

    def tearDown(self):
        self.racine.destroy()
        self._tmp.cleanup()

    def test_demarre_sur_a_01_sans_apercu(self):
        self.assertEqual((self.app.lettre, self.app.numero), ("a", 1))
        self.assertIsNone(self.app.image_apercu)
        self.assertEqual(str(self.app.bouton_continuer["state"]), "disabled")

    def test_apercu_automatique_apres_un_trait(self):
        dessiner(self.app, [(100, 50), (100, 300), (160, 300)])
        self.assertEqual(self.app.image_apercu.size, (512, 512))
        self.assertEqual(str(self.app.bouton_continuer["state"]), "normal")

    def test_continuer_enregistre_puis_passe_a_l_image_suivante(self):
        dessiner(self.app, [(100, 50), (100, 300)])
        self.app.continuer()
        self.assertTrue(os.path.isfile(os.path.join(self.dossier, "a_01.png")))
        self.assertEqual((self.app.lettre, self.app.numero), ("a", 2))
        self.assertIsNone(self.app.image_apercu)

    def test_annuler_n_ecrit_rien(self):
        dessiner(self.app, [(100, 50), (100, 300)])
        self.app.annuler()
        self.assertFalse(os.path.exists(self.dossier))
        self.assertEqual((self.app.lettre, self.app.numero), ("a", 1))
        self.assertEqual(self.app.traits, [])
        self.assertIsNone(self.app.image_apercu)

    def test_continuer_sans_trace_n_ecrit_rien(self):
        self.app.continuer()
        self.assertFalse(os.path.exists(self.dossier))

    def test_trace_trop_petit_donne_un_message_sans_apercu(self):
        dessiner(self.app, [(10, 10), (12, 12)])
        self.assertIsNone(self.app.image_apercu)
        self.assertIn("petit", self.app.message["text"])

    def test_annuler_dernier_trait(self):
        dessiner(self.app, [(100, 50), (100, 300)])
        dessiner(self.app, [(100, 175), (160, 175)])
        self.app.annuler_dernier_trait()
        self.assertEqual(len(self.app.traits), 1)
        self.assertIsNotNone(self.app.image_apercu)
        self.app.annuler_dernier_trait()
        self.assertIsNone(self.app.image_apercu)

    def test_reprise_au_lancement(self):
        image = Image.new("L", (512, 512), 255)
        for numero in range(1, 21):
            stockage.enregistrer(image, self.dossier, "a", numero)
        stockage.enregistrer(image, self.dossier, "b", 1)
        app = Application(self.racine, self.dossier)
        self.assertEqual((app.lettre, app.numero), ("b", 2))

    def test_ecran_final(self):
        image = Image.new("L", (512, 512), 255)
        for lettre in stockage.LETTRES:
            for numero in range(1, 21):
                stockage.enregistrer(image, self.dossier, lettre, numero)
        app = Application(self.racine, self.dossier)
        self.assertIsNone(app.lettre)
        self.assertIn("Terminé", app.titre["text"])


if __name__ == "__main__":
    unittest.main()
