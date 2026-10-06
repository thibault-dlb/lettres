"""Fenêtre Tkinter : dessin libre, aperçu automatique, annuler / continuer."""

import os
import subprocess
import sys
import tkinter as tk

from PIL import Image, ImageTk

from . import stockage
from .traitement import TAILLE, TraceInvalide, rendre_image

TAILLE_AFFICHAGE = 420  # taille à l'écran des deux zones (l'image enregistrée fait 512x512)
EPAISSEUR_ECRAN = 6

# Palette Solarized Dark (pdf-theme-solarized-dark.css)
FOND = "#002b36"
PANNEAU = "#073642"
BORDURE = "#586e75"
TEXTE = "#93a1a1"
TITRE = "#fdf6e3"
ACCENT = "#2aa198"
ACCENT_ACTIF = "#268bd2"
ERREUR = "#dc322f"
OK = "#859900"


def ouvrir_dossier(dossier):
    os.makedirs(dossier, exist_ok=True)
    if sys.platform.startswith("win"):
        os.startfile(dossier)  # noqa: S606
    elif sys.platform == "darwin":
        subprocess.Popen(["open", dossier])
    else:
        subprocess.Popen(["xdg-open", dossier])


class Application:
    def __init__(self, racine, dossier, ouvrir=ouvrir_dossier, telechargements=None):
        self.racine = racine
        self.dossier = dossier
        self._ouvrir = ouvrir
        self._telechargements = telechargements
        self.traits = []
        self.trait_courant = None
        self.image_apercu = None
        self._photo_apercu = None
        self.lettre = None
        self.numero = None

        racine.title("Lettres manuscrites")
        racine.configure(bg=FOND)
        racine.resizable(False, False)

        self.titre = tk.Label(racine, font=("Segoe UI", 18, "bold"), bg=FOND, fg=TITRE)
        self.titre.pack(pady=(12, 0))
        self.progression = tk.Label(racine, font=("Segoe UI", 10), bg=FOND, fg=TEXTE)
        self.progression.pack()

        zones = tk.Frame(racine, bg=FOND)
        zones.pack(padx=16, pady=10)
        tk.Label(zones, text="Dessine ici", bg=FOND, fg=TEXTE).grid(row=0, column=0)
        tk.Label(zones, text="Aperçu (512 × 512)", bg=FOND, fg=TEXTE).grid(row=0, column=1)

        self.zone_dessin = tk.Canvas(
            zones, width=TAILLE_AFFICHAGE, height=TAILLE_AFFICHAGE,
            bg="white", highlightthickness=1, highlightbackground=BORDURE, cursor="pencil",
        )
        self.zone_dessin.grid(row=1, column=0, padx=8)
        self.zone_apercu = tk.Canvas(
            zones, width=TAILLE_AFFICHAGE, height=TAILLE_AFFICHAGE,
            bg="white", highlightthickness=1, highlightbackground=BORDURE,
        )
        self.zone_apercu.grid(row=1, column=1, padx=8)

        self.message = tk.Label(racine, font=("Segoe UI", 10), bg=FOND, fg=TEXTE, wraplength=840)
        self.message.pack()

        style_bouton = dict(
            bg=PANNEAU, fg=TITRE, activebackground=BORDURE, activeforeground=TITRE,
            disabledforeground=BORDURE, relief="flat", bd=0, padx=10, pady=5,
        )
        boutons = tk.Frame(racine, bg=FOND)
        boutons.pack(pady=(4, 14))
        self.bouton_retour = tk.Button(
            boutons, text="Effacer le dernier trait (Ctrl+Z)",
            command=self.annuler_dernier_trait, **style_bouton,
        )
        self.bouton_retour.grid(row=0, column=0, padx=6)
        self.bouton_annuler = tk.Button(
            boutons, text="Annuler (Échap)", command=self.annuler, **style_bouton
        )
        self.bouton_annuler.grid(row=0, column=1, padx=6)
        self.bouton_continuer = tk.Button(
            boutons, text="Continuer (Entrée)", command=self.continuer, state="disabled",
            **{**style_bouton, "bg": ACCENT, "fg": FOND, "activebackground": ACCENT_ACTIF,
               "activeforeground": FOND},
        )
        self.bouton_continuer.grid(row=0, column=2, padx=6)

        self.zone_dessin.bind("<ButtonPress-1>", lambda e: self.commencer_trait(e.x, e.y))
        self.zone_dessin.bind("<B1-Motion>", lambda e: self.ajouter_point(e.x, e.y))
        self.zone_dessin.bind("<ButtonRelease-1>", lambda e: self.finir_trait())
        racine.bind("<Control-z>", lambda e: self.annuler_dernier_trait())
        racine.bind("<Escape>", lambda e: self.annuler())
        racine.bind("<Return>", lambda e: self.continuer())

        self._charger_prochaine_image()

    # ----- parcours -----

    def _charger_prochaine_image(self):
        suivante = stockage.prochaine_image(self.dossier)
        self._reinitialiser()
        if suivante is None:
            self._afficher_fin()
            return
        self.lettre, self.numero = suivante
        self._afficher_en_tete()

    def _afficher_en_tete(self):
        total = len(stockage.LETTRES) * stockage.IMAGES_PAR_LETTRE
        faites = sum(stockage.nombre_images(self.dossier, l) for l in stockage.LETTRES)
        self.titre.config(
            text=f"Lettre « {self.lettre} » (minuscule) "
                 f"— image {self.numero}/{stockage.IMAGES_PAR_LETTRE}"
        )
        self.progression.config(text=f"Total : {faites}/{total} images enregistrées")
        self._dire("Dessine la lettre le plus grand possible, sans te soucier du cadrage.")

    def _afficher_fin(self):
        self.lettre = self.numero = None
        total = len(stockage.LETTRES) * stockage.IMAGES_PAR_LETTRE
        self.titre.config(text="Terminé !")
        self.progression.config(text=f"{total}/{total} images enregistrées")
        self._dire("Déplacement des images dans le dossier Téléchargements...", OK)
        for bouton in (self.bouton_retour, self.bouton_annuler, self.bouton_continuer):
            bouton.config(state="disabled")
        self.racine.unbind("<Return>")
        self.racine.unbind("<Escape>")
        self.zone_dessin.unbind("<ButtonPress-1>")
        self.racine.after(600, self._terminer)

    def _terminer(self):
        """Déplace le dossier dans Téléchargements, l'ouvre, puis ferme l'application."""
        try:
            self.dossier = stockage.deplacer_vers_telechargements(
                self.dossier, self._telechargements
            )
        except OSError as erreur:
            self._dire(
                f"Déplacement impossible ({erreur}). Les images restent dans « {self.dossier} ».",
                ERREUR,
            )
        self._ouvrir(self.dossier)
        self.racine.destroy()

    # ----- dessin -----

    def commencer_trait(self, x, y):
        if self.lettre is None:
            return
        self.trait_courant = [(x, y)]
        self.traits.append(self.trait_courant)
        self._tracer_point(x, y)

    def ajouter_point(self, x, y):
        if self.trait_courant is None:
            return
        precedent = self.trait_courant[-1]
        self.trait_courant.append((x, y))
        self.zone_dessin.create_line(
            *precedent, x, y, width=EPAISSEUR_ECRAN, capstyle="round", fill="black"
        )

    def finir_trait(self):
        if self.trait_courant is None:
            return
        self.trait_courant = None
        self._mettre_a_jour_apercu()

    def _tracer_point(self, x, y):
        r = EPAISSEUR_ECRAN / 2
        self.zone_dessin.create_oval(x - r, y - r, x + r, y + r, fill="black", outline="black")

    def _redessiner(self):
        self.zone_dessin.delete("all")
        for trait in self.traits:
            if len(trait) == 1:
                self._tracer_point(*trait[0])
            for a, b in zip(trait, trait[1:]):
                self.zone_dessin.create_line(
                    *a, *b, width=EPAISSEUR_ECRAN, capstyle="round", fill="black"
                )

    # ----- actions -----

    def annuler_dernier_trait(self):
        if self.lettre is None or not self.traits:
            return
        self.traits.pop()
        self.trait_courant = None
        self._redessiner()
        self._mettre_a_jour_apercu()

    def annuler(self):
        """Efface tout le tracé pour recommencer l'image."""
        if self.lettre is None:
            return
        self._reinitialiser()
        self._dire("Tracé annulé : redessine la lettre.")

    def continuer(self):
        """Enregistre l'image affichée en aperçu puis passe à la suivante."""
        if self.lettre is None or self.image_apercu is None:
            return
        try:
            stockage.enregistrer(self.image_apercu, self.dossier, self.lettre, self.numero)
        except (OSError, FileExistsError) as erreur:
            self._dire(f"Enregistrement impossible : {erreur}", ERREUR)
            return
        self._charger_prochaine_image()

    # ----- aperçu -----

    def _mettre_a_jour_apercu(self):
        try:
            image = rendre_image(self.traits)
        except TraceInvalide as erreur:
            self._vider_apercu()
            self._dire(str(erreur), ERREUR if self.traits else TEXTE)
            return
        self.image_apercu = image
        affichage = image.resize((TAILLE_AFFICHAGE, TAILLE_AFFICHAGE), Image.LANCZOS)
        self._photo_apercu = ImageTk.PhotoImage(affichage)
        self.zone_apercu.delete("all")
        self.zone_apercu.create_image(0, 0, anchor="nw", image=self._photo_apercu)
        self.bouton_continuer.config(state="normal")
        self._dire(
            f"Aperçu prêt ({TAILLE}×{TAILLE}, sans déformation, touche deux bords). "
            "Continuer pour enregistrer ou Annuler pour recommencer.",
            OK,
        )

    def _vider_apercu(self):
        self.image_apercu = None
        self._photo_apercu = None
        self.zone_apercu.delete("all")
        self.bouton_continuer.config(state="disabled")

    def _reinitialiser(self):
        self.traits = []
        self.trait_courant = None
        self.zone_dessin.delete("all")
        self._vider_apercu()

    def _dire(self, texte, couleur=TEXTE):
        self.message.config(text=texte, fg=couleur)


def lancer_application(dossier):
    racine = tk.Tk()
    Application(racine, dossier)
    racine.mainloop()
