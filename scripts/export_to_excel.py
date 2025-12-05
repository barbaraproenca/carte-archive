#!/usr/bin/env python3
"""
Script d'export des donnees vers Excel pour la visualisation des archives.
Ce script cree un fichier Excel complet avec toutes les donnees,
facilitant les modifications par un non-developpeur.

Archives departementales des Bouches-du-Rhone (AD13)
Auteur: Barbara Proenca
"""

import pandas as pd
import json
from pathlib import Path
from collections import defaultdict
import re


# Configuration
PROJECT_ROOT = Path(__file__).parent.parent
INVENTAIRES_JSON = PROJECT_ROOT / "data" / "inventaires_ad13.json"
OUTPUT_EXCEL = PROJECT_ROOT / "data" / "archives.xlsx"

# Base URLs
AD13_BASE_URL = "https://www.archives13.fr"
AD13_SEARCH_URL = "https://www.archives13.fr/archive/recherche/fonds/n:93"

# Mapping des categories avec leurs descriptions et URLs
CATEGORIES = {
    "ARCHIVES ANCIENNES": {
        "description": "Les archives anciennes sont les archives des institutions d'Ancien Regime supprimees par la Revolution francaise. Elles couvrent une periode de pres de 1000 ans et forment les series A a H du cadre de classement.",
        "url": f"{AD13_BASE_URL}/n/archives-anciennes/n:101",
        "ordre": 1
    },
    "ARCHIVES REVOLUTIONNAIRES": {
        "description": "Les archives revolutionnaires concernent la periode de 1789 a 1800, epoque de profonds bouleversements politiques et administratifs. Elles forment les series L et Q.",
        "url": f"{AD13_BASE_URL}/n/archives-revolutionnaires/n:102",
        "ordre": 2
    },
    "ARCHIVES MODERNES ET CONTEMPORAINES": {
        "description": "Les archives modernes et contemporaines sont les fonds produits par les administrations publiques du departement de 1800 a nos jours. Elles forment les series K a Z et W.",
        "url": f"{AD13_BASE_URL}/n/archives-modernes-et-contemporaines/n:103",
        "ordre": 3
    },
    "ARCHIVES HOSPITALIERES": {
        "description": "Les archives hospitalieres regroupent les fonds des etablissements hospitaliers du departement.",
        "url": f"{AD13_BASE_URL}/n/archives-hospitalieres/n:104",
        "ordre": 4
    },
    "ARCHIVES COMMUNALES ET INTERCOMMUNALES DEPOSEES": {
        "description": "Les archives communales et intercommunales deposees proviennent des communes du departement ayant choisi de deposer leurs archives anciennes.",
        "url": f"{AD13_BASE_URL}/n/archives-communales-et-intercommunales-deposees/n:105",
        "ordre": 5
    },
    "ARCHIVES PRIVEES": {
        "description": "Les archives privees rassemblent les fonds d'origine privee entres par don, legs, depot ou achat : archives de familles, d'entreprises, d'associations.",
        "url": f"{AD13_BASE_URL}/n/archives-privees/n:106",
        "ordre": 6
    },
    "FONDS ICONOGRAPHIQUES ET AUDIOVISUELS": {
        "description": "Les fonds iconographiques et audiovisuels comprennent les photographies, cartes postales, affiches, plans, films et enregistrements sonores.",
        "url": f"{AD13_BASE_URL}/n/fonds-iconographiques-et-audiovisuels/n:107",
        "ordre": 7
    },
    "BIBLIOTHEQUE": {
        "description": "La bibliotheque des Archives departementales conserve des ouvrages de reference, periodiques et journaux locaux.",
        "url": f"{AD13_BASE_URL}/n/bibliotheque/n:108",
        "ordre": 8
    },
    "ETAT CIVIL": {
        "description": "L'etat civil comprend les registres paroissiaux et d'etat civil des communes du departement, consultables en ligne.",
        "url": f"{AD13_BASE_URL}/n/etat-civil/n:109",
        "ordre": 9
    },
    "ARCHIVES NOTARIALES": {
        "description": "Les archives notariales regroupent les minutes et repertoires des notaires du departement des origines a nos jours.",
        "url": f"{AD13_BASE_URL}/n/archives-notariales/n:110",
        "ordre": 10
    }
}


def extract_serie(cote):
    """Extrait la serie d'une cote."""
    cote = cote.upper().strip()
    
    # Patterns specifiques
    if 'TRIBUNAL' in cote:
        return 'TRIBUNAL'
    if 'ETP' in cote:
        return 'ETP'
    if 'HDEP' in cote:
        return 'HDEP'
    if 'EDEP' in cote:
        return 'EDEP'
    
    # Pattern general: numero + lettre(s)
    match = re.match(r'^\d*\s*([A-Z]+)', cote)
    if match:
        return match.group(1)
    
    return "AUTRE"


def load_inventaires():
    """Charge les inventaires depuis le JSON."""
    if not INVENTAIRES_JSON.exists():
        print(f"Fichier {INVENTAIRES_JSON} non trouve")
        return []
    
    with open(INVENTAIRES_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return data.get('fonds', [])


def build_excel_data(inventaires):
    """Construit les donnees pour les feuilles Excel."""
    
    # Grouper les inventaires par categorie et serie
    by_category = defaultdict(lambda: defaultdict(list))
    
    for inv in inventaires:
        cat = inv.get('categorie', 'ARCHIVES MODERNES ET CONTEMPORAINES')
        serie = extract_serie(inv.get('cote', ''))
        by_category[cat][serie].append(inv)
    
    # Construire les donnees des categories (fonctions)
    categories_data = []
    for cat_name, cat_info in CATEGORIES.items():
        series_data = by_category.get(cat_name, {})
        
        total_inventaires = sum(len(s) for s in series_data.values())
        total_notices = sum(
            inv.get('nb_notices', 0) 
            for series in series_data.values() 
            for inv in series
        )
        
        categories_data.append({
            "fonction": cat_name,
            "Description": cat_info["description"],
            "url": cat_info["url"],
            "url_recherche": AD13_SEARCH_URL,
            "nb_inventaires_en_ligne": total_inventaires,
            "nb_notices_en_ligne": total_notices,
            "ordre": cat_info["ordre"]
        })
    
    # Trier par ordre
    categories_data.sort(key=lambda x: x['ordre'])
    
    # Construire les donnees des series (thematiques)
    series_data = []
    for cat_name in CATEGORIES.keys():
        for serie, invs in sorted(by_category[cat_name].items()):
            if not invs:
                continue
            
            total_notices = sum(inv.get('nb_notices', 0) for inv in invs)
            
            # Extraire les dates extremes
            dates_min = []
            dates_max = []
            for inv in invs:
                dates = inv.get('dates', '')
                if '-' in dates:
                    parts = dates.split('-')
                    if len(parts) >= 2:
                        try:
                            d_min = int(re.search(r'\d{4}', parts[0]).group())
                            d_max = int(re.search(r'\d{4}', parts[-1]).group())
                            dates_min.append(d_min)
                            dates_max.append(d_max)
                        except:
                            pass
            
            date_extreme = ""
            if dates_min and dates_max:
                date_extreme = f"{min(dates_min)} - {max(dates_max)}"
            
            series_data.append({
                "Thématique": f"Serie {serie}" if len(serie) <= 3 else serie,
                "Fonction": cat_name,
                "Description": f"Serie {serie} - {len(invs)} inventaires en ligne",
                "nb_inventaires": len(invs),
                "nb_notices": total_notices,
                "date_extreme_thematique": date_extreme,
                "url": CATEGORIES[cat_name]["url"]
            })
    
    # Construire les donnees des inventaires
    inventaires_data = []
    for inv in inventaires:
        serie = extract_serie(inv.get('cote', ''))
        serie_name = f"Serie {serie}" if len(serie) <= 3 else serie
        
        inventaires_data.append({
            "cote": inv.get('cote', ''),
            "titre": inv.get('titre', ''),
            "dates": inv.get('dates', ''),
            "nb_notices": inv.get('nb_notices', 0),
            "url": inv.get('url', ''),
            "categorie": inv.get('categorie', ''),
            "serie": serie_name
        })
    
    return categories_data, series_data, inventaires_data


def main():
    print("=" * 60)
    print("Export des donnees vers Excel")
    print("=" * 60)
    
    # Charger les inventaires
    print("\nChargement des inventaires...")
    inventaires = load_inventaires()
    print(f"  {len(inventaires)} inventaires charges")
    
    # Construire les donnees
    print("\nConstruction des donnees...")
    categories, series, inventaires_list = build_excel_data(inventaires)
    
    print(f"  {len(categories)} categories")
    print(f"  {len(series)} series")
    print(f"  {len(inventaires_list)} inventaires")
    
    # Creer les DataFrames
    df_categories = pd.DataFrame(categories)
    df_series = pd.DataFrame(series)
    df_inventaires = pd.DataFrame(inventaires_list)
    
    # Ecrire le fichier Excel
    print(f"\nEcriture du fichier Excel: {OUTPUT_EXCEL}")
    with pd.ExcelWriter(OUTPUT_EXCEL, engine='openpyxl') as writer:
        df_categories.to_excel(writer, sheet_name='Fonction', index=False)
        df_series.to_excel(writer, sheet_name='Thématique', index=False)
        df_inventaires.to_excel(writer, sheet_name='Inventaire', index=False)
        
        # Feuille vide pour les producteurs (pour compatibilite)
        pd.DataFrame(columns=['Producteur', 'Description']).to_excel(
            writer, sheet_name='Producteur', index=False
        )
    
    print("\nExport termine!")
    print("\nContenu du fichier Excel:")
    print("  - Feuille 'Fonction': Categories principales des fonds")
    print("  - Feuille 'Thematique': Series archivistiques")
    print("  - Feuille 'Inventaire': Liste des 982 inventaires en ligne")
    print("  - Feuille 'Producteur': (vide, pour ajouts futurs)")


if __name__ == "__main__":
    main()

