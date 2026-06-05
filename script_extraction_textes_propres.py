import os
import fitz
import re
from pdf2image import convert_from_path
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r"C:\Users\lagie\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

def nettoyer_texte(texte_brut):
    texte = re.sub(r'([.:;])\s*\n', r'\1\n\n', texte_brut)
    texte = re.sub(r'(?<!\n)\n(?!\n)', ' ', texte)
    texte = re.sub(r'(Art\.|Article\s+[0-9]+)', r'\n\n\1', texte)
    texte = re.sub(r' +', ' ', texte)
    return texte.strip()

def extraire_pdf_individuels(dossier_racine):
    avec_ocr = 0
    sans_ocr = 0
    echecs = 0
    
    for root, dirs, fichiers in os.walk(dossier_racine):
        for fichier in fichiers:
            if fichier.lower().endswith(".pdf"):
                chemin_pdf = os.path.join(root, fichier)
                nom_de_base = os.path.splitext(fichier)[0][:50]
                nom_fichier_sortie = os.path.join(root, f"{nom_de_base}avec_modification_propre.txt")
                
                try:
                    texte_pdf_complet = ""
                    with fitz.open(chemin_pdf) as doc:
                        for page in doc:
                            texte_page = page.get_text()
                            if texte_page:
                                texte_pdf_complet += texte_page + "\n"
                    
                    lettres = re.findall(r'[a-zA-ZÀ-ÿ]', texte_pdf_complet)
                    
                    if len(lettres) < 30:
                        images = convert_from_path(chemin_pdf, poppler_path=r"C:\poppler\Library\bin")
                        texte_pdf_complet = ""
                        for image in images:
                            texte_pdf_complet += pytesseract.image_to_string(image, lang="fra") + "\n"
                        print(f"[REUSSITE] {fichier} (Traité avec OCR)")
                        avec_ocr += 1
                    else:
                        print(f"[REUSSITE] {fichier} (Traité sans OCR)")
                        sans_ocr += 1
                    
                    texte_propre = nettoyer_texte(texte_pdf_complet)
                    
                    with open(nom_fichier_sortie, "w", encoding="utf-8") as fichier_sortie:
                        fichier_sortie.write(texte_propre)
                        
                except Exception as e:
                    print(f"[BUG / BLOQUE] {fichier} -> Raison : {str(e)}")
                    echecs += 1
                    nom_fichier_erreur = os.path.join(root, f"ERREUR_{nom_de_base}.txt")
                    try:
                        with open(nom_fichier_erreur, "w", encoding="utf-8") as fichier_sortie:
                            fichier_sortie.write(f"[ERREUR LORS DE LA LECTURE DU PDF : {str(e)}]")
                    except:
                        pass

    total = avec_ocr + sans_ocr + echecs
    print("\n--- STATISTIQUES DE TRAITEMENT ---")
    if total > 0:
        pct_avec = (avec_ocr / total) * 100
        pct_sans = (sans_ocr / total) * 100
        pct_echec = (echecs / total) * 100
        print(f"Total de fichiers trouvés : {total}")
        print(f"Pourcentage REUSSITE avec OCR  : {pct_avec:.1f}% ({avec_ocr} fichiers)")
        print(f"Pourcentage REUSSITE sans OCR  : {pct_sans:.1f}% ({sans_ocr} fichiers)")
        print(f"Pourcentage BUG / BLOQUE        : {pct_echec:.1f}% ({echecs} fichiers)")
    else:
        print("Aucun fichier PDF n'a été trouvé.")

dossier_base = "."
extraire_pdf_individuels(dossier_base)
print("\nBalayage terminé.")