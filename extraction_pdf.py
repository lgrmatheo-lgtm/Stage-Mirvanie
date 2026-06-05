import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import urllib3
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

urls_gouvernementaux = {
    "Maroc": "https://adala.justice.gov.ma/fr/Home/Lois",
    "Senegal": "https://www.finances.gouv.sn/lois-et-reglements/",
    "Kenya": "https://www.kra.go.ke/en/downloads",
    "Afrique_du_Sud": "https://www.treasury.gov.za/legislation/",
    "Egypte": "https://eta.gov.eg/",
    "Nigeria": "https://nass.gov.ng/documents/acts",
    "Ethiopie": "https://investethiopia.gov.et/investment-laws/",
    "RDC": "https://dgi.gouv.cd/",
    "Tanzanie": "https://www.tra.go.tz/index.php/laws",
    "Soudan": "https://cbos.gov.sd/en/laws-and-regulations",
    "Ouganda": "https://www.ura.go.ug/",
    "Algerie": "https://www.invest.caci.dz/index.php?page=investissements-etrangers",
    "Angola": "https://angolex.com/",
    "Ghana": "https://gra.gov.gh/",
    "Mozambique": "https://www.bancomoc.mz/pt/sobre-nos/legislacao/",
    "Cote_d_Ivoire": "https://www.cepici.ci/telechargements/",
    "Madagascar": "http://www.assemblee-nationale.mg/textes-de-lois/",
    "Cameroun": "https://www.investincameroon.net/fr/documentation",
    "Niger": "https://investinniger.ne/ressources-documentaires/",
    "Mali": "https://dgi.gouv.ml/",
    "Burkina_Faso": "https://www.investburkina.com/documents-utiles/",
    "Malawi": "https://www.mitc.mw/downloads/",
    "Zambie": "https://www.zra.org.zm/",
    "Tchad": "https://www.finances.gouv.td/",
    "Somalie": "https://somalilandlaw.com/",
    "Zimbabwe": "https://www.zimra.co.zw/",
    "Guinee": "https://apip.gov.gn/documentations/",
    "Benin": "https://finances.bj/documentation/",
    "Rwanda": "https://rdb.rw/laws-and-regulations/",
    "Burundi": "https://www.obr.bi/",
    "Tunisie": "http://www.finances.gov.tn/",
    "Togo": "https://investirautogo.tg/telechargements/",
    "Libye": "https://tax.gov.ly/",
    "Soudan_du_Sud": "https://boss.gov.ss/publications/",
    "Centrafrique": "https://finances.gouv.cf/loi-de-finances/",
    "Liberia": "https://investliberia.gov.lr/publications/",
    "Sierra_Leone": "https://sliepa.gov.sl/resources/",
    "Congo_Brazzaville": "https://www.apic-congo.com/documentation/",
    "Mauritanie": "https://apim.gov.mr/fr/cadre-juridique/",
    "Erythree": "https://eritrean-embassy.se/documents/",
    "Namibie": "https://nipdb.com/resources/",
    "Gambie": "https://www.giepa.gm/downloads",
    "Botswana": "https://www.burs.org.bw/",
    "Gabon": "https://dgi.ga/",
    "Lesotho": "https://www.rsl.org.ls/",
    "Guinee_Bissau": "https://guineebissaugov.com/documentos/",
    "Guinee_equatoriale": "https://www.beac.int/reglementation/",
    "Eswatini": "https://investeswatini.org.sz/resources/",
    "Maurice": "https://www.mra.mu/",
    "Djibouti": "https://djiboutinvest.com/cadre-legal/",
    "Comores": "https://finances.gouv.km/",
    "Cap_Vert": "https://www.mf.gov.cv/",
    "Sao_Tome_et_Principe": "https://apci.st/publicacoes/",
    "Seychelles": "https://www.cbs.sc/Publications/Legislations.html"
}
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}

def dossier_deja_rempli(chemin_dossier):
    """Retourne True si le dossier existe et contient au moins un fichier."""
    if not os.path.exists(chemin_dossier):
        return False
    fichiers = os.listdir(chemin_dossier)
    return len(fichiers) > 0

def collecter_documents_afrique():
    dossier_racine = "collecte_lois_fiscales"
    if not os.path.exists(dossier_racine):
        os.makedirs(dossier_racine)
        print(f"[INIT] Dossier racine créé : {dossier_racine}")
    else:
        print(f"[INIT] Dossier racine existant : {dossier_racine}")

    session = requests.Session()
    session.headers.update(headers)

    total_pays = len(urls_gouvernementaux)
    pays_sans_resultats = []
    pays_skipped = []
    total_pdf_telecharges = 0

    print(f"\n[DEBUT] Traitement de {total_pays} pays\n" + "="*60)

    for index, (pays, url) in enumerate(urls_gouvernementaux.items(), start=1):
        print(f"\n[{index}/{total_pays}] >>> PAYS : {pays}")

        dossier_pays = os.path.join(dossier_racine, pays)

        # --- SKIP si le dossier existe et n'est pas vide ---
        if dossier_deja_rempli(dossier_pays):
            nb_fichiers = len(os.listdir(dossier_pays))
            print(f"  [SKIP] Dossier déjà rempli ({nb_fichiers} fichier(s)) — pays ignoré")
            pays_skipped.append(pays)
            continue

        print(f"  URL : {url}")
        debut_pays = time.time()

        if not os.path.exists(dossier_pays):
            os.makedirs(dossier_pays)
            print(f"  [DOSSIER] Créé : {dossier_pays}")

        liens_a_visiter = [url]
        liens_visites = set()
        liens_pdf_trouves = set()
        domaine_base = urlparse(url).netloc
        succes_telechargement = False

        # --- Étape 1 : page principale ---
        print(f"  [ETAPE 1] Chargement de la page principale...")
        try:
            reponse_principale = session.get(url, timeout=20, verify=False)
            print(f"  [ETAPE 1] Statut HTTP : {reponse_principale.status_code}")
            soup_principale = BeautifulSoup(reponse_principale.text, 'html.parser')
            liens_trouves_page = 0

            for balise_a in soup_principale.find_all('a', href=True):
                href = balise_a['href']
                lien_complet = urljoin(url, href)

                if any(mot in href.lower() for mot in ['.pdf', 'download', 'fichier', 'file', 'document', 'telecharger']):
                    liens_pdf_trouves.add(lien_complet)
                    liens_trouves_page += 1
                elif urlparse(lien_complet).netloc == domaine_base and lien_complet not in liens_visites:
                    liens_a_visiter.append(lien_complet)

            print(f"  [ETAPE 1] {liens_trouves_page} liens PDF/doc trouvés, {len(liens_a_visiter)-1} sous-pages à explorer")

        except Exception as e:
            print(f"  [ETAPE 1] ECHEC page principale : {e}")

        # --- Étape 2 : sous-pages si rien trouvé ---
        if not liens_pdf_trouves:
            sous_pages = liens_a_visiter[1:25]
            print(f"  [ETAPE 2] Aucun PDF direct — exploration de {len(sous_pages)} sous-pages...")

            for i, sous_lien in enumerate(sous_pages, start=1):
                if sous_lien in liens_visites:
                    continue
                liens_visites.add(sous_lien)
                print(f"    [SOUS-PAGE {i}/{len(sous_pages)}] {sous_lien}")
                try:
                    rep_sous = session.get(sous_lien, timeout=15, verify=False)
                    soup_sous = BeautifulSoup(rep_sous.text, 'html.parser')
                    avant = len(liens_pdf_trouves)
                    for balise_a in soup_sous.find_all('a', href=True):
                        href = balise_a['href']
                        lien_complet = urljoin(sous_lien, href)
                        if any(mot in href.lower() for mot in ['.pdf', 'download', 'fichier', 'file', 'document', 'telecharger']):
                            liens_pdf_trouves.add(lien_complet)
                    nouveaux = len(liens_pdf_trouves) - avant
                    if nouveaux > 0:
                        print(f"    [SOUS-PAGE {i}] +{nouveaux} liens PDF trouvés (total : {len(liens_pdf_trouves)})")
                except Exception as e:
                    print(f"    [SOUS-PAGE {i}] ECHEC : {e}")
        else:
            print(f"  [ETAPE 2] Ignorée (PDF déjà trouvés à l'étape 1)")

        print(f"  [BILAN LIENS] {len(liens_pdf_trouves)} liens PDF/doc au total")

        # --- Étape 3 : téléchargements ---
        if liens_pdf_trouves:
            print(f"  [ETAPE 3] Téléchargement de {len(liens_pdf_trouves)} fichiers...")
            pdf_ok = 0
            pdf_ko = 0

            for j, lien in enumerate(liens_pdf_trouves, start=1):
                nom_fichier = lien.split('/')[-1].split('?')[0]
                if not nom_fichier.lower().endswith('.pdf'):
                    nom_fichier += '.pdf'
                nom_fichier = "".join(c for c in nom_fichier if c.isalnum() or c in "._- ")
                if not nom_fichier.strip() or nom_fichier == ".pdf":
                    print(f"    [FICHIER {j}] Nom invalide, ignoré : {lien}")
                    continue

                chemin_final = os.path.join(dossier_pays, nom_fichier)
                print(f"    [FICHIER {j}/{len(liens_pdf_trouves)}] {nom_fichier} ...")

                try:
                    flux_pdf = session.get(lien, stream=True, timeout=20, verify=False)
                    type_contenu = flux_pdf.headers.get('Content-Type', '')
                    print(f"      Content-Type : {type_contenu}")
                    if 'application/pdf' in type_contenu or lien.lower().endswith('.pdf'):
                        with open(chemin_final, 'wb') as fichier:
                            for morceau in flux_pdf.iter_content(chunk_size=16384):
                                fichier.write(morceau)
                        taille = os.path.getsize(chemin_final)
                        print(f"      [OK] Sauvegardé ({taille} octets) -> {chemin_final}")
                        succes_telechargement = True
                        pdf_ok += 1
                        total_pdf_telecharges += 1
                    else:
                        print(f"      [IGNORE] Pas un PDF (Content-Type : {type_contenu})")
                        pdf_ko += 1
                except Exception as e:
                    print(f"      [ECHEC] {e}")
                    pdf_ko += 1

            print(f"  [ETAPE 3] Résultat : {pdf_ok} OK / {pdf_ko} échoués/ignorés")
        else:
            print(f"  [ETAPE 3] Aucun lien PDF à télécharger")

        duree = round(time.time() - debut_pays, 1)
        if not succes_telechargement:
            pays_sans_resultats.append(pays)
            print(f"  [RESULTAT] AUCUN PDF téléchargé pour {pays} (durée : {duree}s)")
        else:
            print(f"  [RESULTAT] Succès pour {pays} (durée : {duree}s)")

    # --- Résumé final ---
    print("\n" + "="*60)
    print(f"[FIN] Traitement terminé. Total PDF téléchargés cette session : {total_pdf_telecharges}")

    if pays_skipped:
        print(f"\n[SKIPPÉS] {len(pays_skipped)} pays ignorés (dossier déjà rempli) :")
        for p in pays_skipped:
            print(f"  - {p}")

    if pays_sans_resultats:
        print(f"\nAUCUN PDF TÉLÉCHARGÉ POUR CES {len(pays_sans_resultats)} PAYS :")
        for p in pays_sans_resultats:
            print(f"  - {p}")
    else:
        print("SUCCÈS : Des PDF ont été récupérés pour tous les pays traités !")
    print("="*60 + "\n")

if __name__ == "__main__":
    collecter_documents_afrique()