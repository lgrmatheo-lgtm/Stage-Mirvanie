import pandas as pd
import glob
import os
import re


def clean_number(x):
    if pd.isna(x):
        return ""
    return re.sub(r"[^\d.,]", "", str(x))


def extract_first_number(x):
    if pd.isna(x):
        return ""
    m = re.search(r"\d+", str(x))
    return m.group() if m else ""


def parse_type(text):
    if not isinstance(text, str):
        return "Autre"

    t = text.lower()

    mapping = {
        "studio": "Studio",
        "appartement": "Appartement",
        "apartment": "Appartement",
        "villa": "Villa",
        "maison": "Maison",
        "house": "Maison",
        "terrain": "Terrain",
        "land": "Terrain",
        "bureau": "Bureau",
        "office": "Bureau",
        "boutique": "Commerce",
        "shop": "Commerce",
        "hôtel": "Hôtel",
        "hotel": "Hôtel",
        "duplex": "Duplex",
        "immeuble": "Immeuble"
    }

    for k, v in mapping.items():
        if k in t:
            return v

    return "Autre"


def safe_series(df, col1, col2=None):
    """
    Retourne toujours une Series valide (évite les erreurs .apply sur str).
    Version robuste du code 1, combinée avec df.get() du code 2.
    """
    if col1 in df.columns:
        return df[col1]
    if col2 and col2 in df.columns:
        return df[col2]
    return pd.Series([""] * len(df))


def process_csv_files(directory, output_file):

    all_files = glob.glob(os.path.join(directory, "*.csv"))

    print(f"\n📁 Fichiers trouvés : {len(all_files)}\n")

    final_data = []
    total_input_rows = 0
    total_output_rows = 0
    unknown_files = []

    for file in all_files:

        name = os.path.basename(file).lower()

        try:
            # sep=None + engine="python" du code 1 : détecte auto le séparateur
            df = pd.read_csv(file, encoding="utf-8", sep=None, engine="python")

            print(f"📄 {name} | INPUT: {len(df)} lignes")

            total_input_rows += len(df)

            if df.empty:
                print(f"⚠️  Fichier vide ignoré : {name}")
                continue

            out = pd.DataFrame()

    

            out["reference"]   = safe_series(df, "web_scraper_order")
            out["site_url"]    = safe_series(df, "web_scraper_start_url")
            out["titre"]       = safe_series(df, "title", "name")
            out["description"] = safe_series(df, "description")
            out["image_url"]   = safe_series(df, "image")

         

            out["ville"]              = ""
            out["devise"]             = ""
            out["surface_m2"]         = ""
            out["nombre_chambres"]    = ""
            out["nombre_salles_bain"] = ""

         

            type_series    = safe_series(df, "title", "name")
            out["type_bien"] = type_series.apply(parse_type)



            price_series = safe_series(df, "price", "data")
            out["prix"]   = price_series
            out["valeur"] = price_series.apply(clean_number)

        

            out["nom_pays"]  = "Inconnu"
            out["code_pays"] = "UNK"



            if "angocasa" in name:
                out["nom_pays"]  = "Angola"
                out["code_pays"] = "AGO"

            elif "aqarmap" in name:
                out["nom_pays"]  = "Égypte"
                out["code_pays"] = "EGY"

            elif "buyrentkenya" in name:
                out["nom_pays"]  = "Kenya"
                out["code_pays"] = "KEN"

            elif "ci-coinafrique" in name:
                out["nom_pays"]  = "Côte d'Ivoire"
                out["code_pays"] = "CIV"

            elif "congo" in name:
                out["nom_pays"]  = "Congo"
                out["code_pays"] = "COG"

            elif "gambia" in name:
                out["nom_pays"]  = "Gambie"
                out["code_pays"] = "GMB"

            else:
                unknown_files.append(name)

            total_output_rows += len(out)
            final_data.append(out)

        except Exception as e:
            print(f"❌ Erreur fichier {name} : {e}")


    if not final_data:
        print("❌ Aucune donnée à exporter.")
        return

    df_final = pd.concat(final_data, ignore_index=True)

    output_columns = [
        "reference",
        "nom_pays",
        "code_pays",
        "site_url",
        "titre",
        "ville",
        "type_bien",
        "prix",
        "valeur",
        "devise",
        "surface_m2",
        "nombre_chambres",
        "nombre_salles_bain",
        "description",
        "image_url"
    ]

    
    for col in output_columns:
        if col not in df_final.columns:
            df_final[col] = ""

    df_final = df_final[output_columns]

    df_final.to_excel(output_file, index=False)


    print("\n=========================")
    print("📊 STATS FINALES")
    print("=========================")
    print(f"Lignes INPUT  : {total_input_rows}")
    print(f"Lignes OUTPUT : {len(df_final)}")
    print(f"Fichiers inconnus : {len(unknown_files)}")
    if unknown_files:
        print(f"Exemples      : {unknown_files[:10]}")
    print("=========================")
    print(f"✅ Fichier créé : {output_file}")


CHEMIN = r"C:\Users\lagie\Desktop\stage mirvanie\Fichiers_Immo"
OUTPUT = r"C:\Users\lagie\Desktop\stage mirvanie\resultat_final.xlsx"

process_csv_files(CHEMIN, OUTPUT)
