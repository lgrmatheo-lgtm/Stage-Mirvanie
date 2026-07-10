import os
import PyPDF2
import re

def extraire_pdf_brut(dossier_racine):
    for element in os.listdir(dossier_racine):
        chemin_dossier_pays = os.path.join(dossier_racine, element)
        
        if os.path.isdir(chemin_dossier_pays):
            for fichier in os.listdir(chemin_dossier_pays):
                if fichier.lower().endswith(".pdf"):
                    chemin_pdf = os.path.join(chemin_dossier_pays, fichier)
                    
                    nom_de_base = os.path.splitext(fichier)[0][:50]
                    nom_fichier_sortie = os.path.join(chemin_dossier_pays, f"{nom_de_base}_copier_sans_modification.txt")
                    
                    try:
                        with open(chemin_pdf, "rb") as f_pdf:
                            lecteur = PyPDF2.PdfReader(f_pdf)
                            texte_brut = ""
                            
                            for page in lecteur.pages:
                                texte_page = page.extract_text()
                                if texte_page:
                                    texte_brut += texte_page + " "
                            
                            texte_pave = re.sub(r'\s+', ' ', texte_brut).strip()
                            
                            with open(nom_fichier_sortie, "w", encoding="utf-8") as fichier_sortie:
                                fichier_sortie.write(texte_pave)
                                
                    except Exception as e:
                        nom_fichier_erreur = os.path.join(chemin_dossier_pays, f"ERREUR_{nom_de_base}.txt")
                        try:
                            with open(nom_fichier_erreur, "w", encoding="utf-8") as fichier_sortie:
                                fichier_sortie.write(f"[ERREUR LORS DE LA LECTURE DU PDF : {str(e)}]")
                        except:
                            pass

dossier_base = "."
extraire_pdf_brut(dossier_base)
print("C'est Good, chaque PDF a son TXT brut dans le dossier de son pays")