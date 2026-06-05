# Stage-Mirvanie

## Description

Ce projet a pour objectif de collecter, extraire et transformer automatiquement des documents juridiques et fiscaux provenant de sites institutionnels africains.

Le pipeline est composé de trois scripts Python :

### 1. Collecte des documents PDF

`extraction_pdf.py`

* Parcourt une liste de sites gouvernementaux africains.
* Recherche les documents disponibles (principalement les PDF).
* Télécharge les fichiers trouvés dans un dossier dédié à chaque pays.
* Évite de retraiter les pays déjà téléchargés.

### 2. Extraction brute du texte

`extraction_textes_brut.py`

* Parcourt l'ensemble des PDF téléchargés.
* Extrait le texte brut contenu dans chaque document.
* Génère un fichier `.txt` associé à chaque PDF.
* Conserve le contenu sans modification majeure afin de préserver les données d'origine.

### 3. Nettoyage et amélioration des textes

`script_extraction_textes_propres.py`

* Extrait le texte des PDF à l'aide de PyMuPDF.
* Utilise l'OCR (Tesseract) lorsque le document ne contient pas de texte exploitable.
* Nettoie et restructure le contenu afin d'obtenir un texte plus lisible.
* Génère un fichier texte propre prêt à être exploité pour l'analyse ou le traitement automatique.

## Technologies utilisées

* Python
* Requests
* BeautifulSoup
* PyPDF2
* PyMuPDF (fitz)
* Tesseract OCR
* pdf2image

## Structure du projet

```text
Documents_Legaux/
├── extraction_pdf.py
├── extraction_textes_brut.py
├── script_extraction_textes_propres.py
├── README.md
└── Dossiers pays/
    ├── Maroc/
    ├── Sénégal/
    ├── Kenya/
    └── ...
```

## Objectif

Faciliter la constitution d'une base documentaire de textes juridiques et fiscaux africains en automatisant la collecte des documents, l'extraction du texte et le prétraitement des contenus.
