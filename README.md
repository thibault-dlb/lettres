# Lettres

Logiciel pour créer les images de lettres manuscrites du projet de Machine Learning : 20 images PNG de 512 × 512 pixels pour chacune des lettres **a, b, f, k, j, g**, en respectant automatiquement les consignes.

## Lancer

1. Télécharge le dépôt (bouton **Code → Download ZIP**, puis décompresse) ou clone-le.
2. **Windows** : double-clic sur `lancer.bat`.
   **Mac / Linux** : `python3 lancer.py`.

Le script vérifie Python, crée un environnement `.venv` dans le dossier, installe Pillow si besoin, puis ouvre le logiciel. Le premier lancement demande une connexion internet (environ une minute) ; les suivants sont instantanés. Sous Windows, si Python n'est pas installé, `lancer.bat` propose de l'installer.

Seul prérequis : **Python 3.8 ou plus récent** avec Tkinter (inclus dans l'installeur officiel sur python.org ; sous Linux : `sudo apt install python3-tk python3-venv`).

## Utiliser

1. Dessine la lettre demandée à la souris, comme tu veux (la taille n'a pas d'importance, plusieurs traits sont possibles).
2. L'aperçu 512 × 512 apparaît automatiquement à droite : il est agrandi sans déformation, centré, et touche au moins deux bords.
3. **Continuer** (Entrée) enregistre l'image et passe à la suivante ; **Annuler** (Échap) efface tout pour recommencer ; **Ctrl+Z** retire le dernier trait.

Les images sont enregistrées dans le dossier `lettre/` sous les noms `a_01.png` … `g_20.png`. Après un arrêt, relancer le logiciel reprend à la première image manquante ; un fichier existant n'est jamais écrasé.

## Ce que le logiciel garantit

| Consigne | Comment |
| --- | --- |
| 512 × 512 pixels, PNG | Image de sortie fixe, trait noir sur fond blanc |
| Lettre la plus grande possible, touchant au moins deux bords | Le plus grand côté du tracé occupe toute l'image (deux bords opposés), vérifié avant l'enregistrement |
| Pas de déformation | Un seul facteur d'échelle pour la largeur et la hauteur, l'autre dimension est centrée |
| Trait homogène | Épaisseur identique sur toutes les images, quelle que soit la taille dessinée |
| 20 images par lettre | Compteur, parcours automatique et reprise |

## Développement

```
python -m unittest discover tests
```

- `lancer.py` : vérification et installation des dépendances, lancement.
- `lettres_app/traitement.py` : tracé → image 512 × 512.
- `lettres_app/stockage.py` : nommage, dossier de sortie, reprise.
- `lettres_app/interface.py` : fenêtre Tkinter.
