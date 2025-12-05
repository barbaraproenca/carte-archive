#!/usr/bin/env python3
"""
Script de construction de la visualisation complete avec les inventaires.
Integre les 982 inventaires comme elements cliquables dans la visualisation.

Auteur: Barbara Proenca
"""

import json
from pathlib import Path
from collections import defaultdict

# Chemins
PROJECT_ROOT = Path(__file__).parent.parent
INVENTAIRES_PATH = PROJECT_ROOT / "data" / "inventaires_ad13.json"
OUTPUT_PATH = PROJECT_ROOT / "docs" / "data" / "archives.json"

# URL de base
AD13_BASE_URL = "https://www.archives13.fr"
AD13_SEARCH_URL = "https://www.archives13.fr/archive/recherche/fonds/n:93"

# Mapping des categories vers les fonctions
CATEGORY_INFO = {
    "ARCHIVES ANCIENNES": {
        "description": "Les archives anciennes sont les archives des institutions d'Ancien Regime supprimees par la Revolution francaise. Elles couvrent une periode de pres de 1000 ans et forment les series A a H du cadre de classement.",
        "url": f"{AD13_BASE_URL}/n/archives-anciennes/n:101",
        "series": ["A", "B", "C", "D", "E", "F", "G", "H"]
    },
    "ARCHIVES REVOLUTIONNAIRES": {
        "description": "Les archives revolutionnaires concernent la periode de 1789 a 1800, epoque de profonds bouleversements politiques et administratifs.",
        "url": f"{AD13_BASE_URL}/n/archives-revolutionnaires/n:102",
        "series": ["L", "Q"]
    },
    "ARCHIVES MODERNES ET CONTEMPORAINES": {
        "description": "Les archives modernes et contemporaines sont les fonds produits par les administrations publiques du departement de 1800 a nos jours.",
        "url": f"{AD13_BASE_URL}/n/archives-modernes-et-contemporaines/n:103",
        "series": ["K", "M", "N", "O", "P", "R", "S", "T", "U", "V", "W", "Z", "ETP"]
    },
    "ARCHIVES HOSPITALIERES": {
        "description": "Les archives hospitalieres regroupent les fonds des etablissements hospitaliers du departement.",
        "url": f"{AD13_BASE_URL}/n/archives-hospitalieres/n:104",
        "series": ["HDEP"]
    },
    "ARCHIVES COMMUNALES ET INTERCOMMUNALES DEPOSEES": {
        "description": "Les archives communales et intercommunales deposees proviennent des communes du departement.",
        "url": f"{AD13_BASE_URL}/n/archives-communales-et-intercommunales-deposees/n:105",
        "series": ["EDEP"]
    },
    "ARCHIVES PRIVEES": {
        "description": "Les archives privees rassemblent les fonds d'origine privee entres par don, legs, depot ou achat.",
        "url": f"{AD13_BASE_URL}/n/archives-privees/n:106",
        "series": ["J"]
    },
    "FONDS ICONOGRAPHIQUES ET AUDIOVISUELS": {
        "description": "Les fonds iconographiques et audiovisuels comprennent les photographies, cartes postales, affiches, plans, films et enregistrements sonores.",
        "url": f"{AD13_BASE_URL}/n/fonds-iconographiques-et-audiovisuels/n:107",
        "series": ["FI", "PH", "AV"]
    },
    "BIBLIOTHEQUE": {
        "description": "La bibliotheque des Archives departementales conserve des ouvrages de reference et des periodiques.",
        "url": f"{AD13_BASE_URL}/n/bibliotheque/n:108",
        "series": ["BIB"]
    },
    "ETAT CIVIL": {
        "description": "L'etat civil comprend les registres paroissiaux et d'etat civil des communes du departement.",
        "url": f"{AD13_BASE_URL}/n/etat-civil/n:109",
        "series": []
    },
    "ARCHIVES NOTARIALES": {
        "description": "Les archives notariales regroupent les minutes et repertoires des notaires du departement.",
        "url": f"{AD13_BASE_URL}/n/archives-notariales/n:110",
        "series": []
    }
}


def load_inventaires():
    """Charge les inventaires scrapes."""
    if not INVENTAIRES_PATH.exists():
        print(f"Erreur: {INVENTAIRES_PATH} non trouve")
        print("Executez d'abord: python scripts/scrape_ad13_inventaires.py")
        return None
    
    with open(INVENTAIRES_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def extract_serie(cote):
    """Extrait la serie d'une cote."""
    import re
    cote = cote.upper().strip()
    
    # Pattern pour extraire la serie
    # Exemples: "14 B" -> "B", "2404 W" -> "W", "26 J" -> "J", "6 U 2" -> "U"
    match = re.search(r'(\d+\s+)?([A-Z]+)(\s+\d+)?', cote)
    if match:
        return match.group(2)
    return "AUTRE"


def group_inventaires_by_serie(inventaires_data):
    """Groupe les inventaires par serie."""
    by_serie = defaultdict(list)
    
    for inv in inventaires_data['fonds']:
        serie = extract_serie(inv.get('cote', ''))
        by_serie[serie].append(inv)
    
    return dict(by_serie)


def build_visualization_data(inventaires_data):
    """Construit les donnees de visualisation avec les inventaires."""
    
    # Grouper par categorie et serie
    by_category = defaultdict(lambda: defaultdict(list))
    
    for inv in inventaires_data['fonds']:
        cat = inv.get('categorie', 'ARCHIVES MODERNES ET CONTEMPORAINES')
        serie = extract_serie(inv.get('cote', ''))
        by_category[cat][serie].append(inv)
    
    # Construire les fonctions
    fonctions = []
    thematiques = []
    
    for cat_name, cat_info in CATEGORY_INFO.items():
        series_data = by_category.get(cat_name, {})
        
        # Calculer les totaux pour cette fonction
        total_notices = sum(
            inv.get('nb_notices', 0) 
            for series in series_data.values() 
            for inv in series
        )
        total_inventaires = sum(len(series) for series in series_data.values())
        
        # Creer la fonction
        fonction = {
            "fonction": cat_name,
            "Description": cat_info["description"],
            "url": cat_info["url"],
            "url_recherche": AD13_SEARCH_URL,
            "nb_inventaires_en_ligne": total_inventaires,
            "nb_notices_en_ligne": total_notices,
            "Métrage réel": total_notices / 10,  # Estimation
            "Nombre d'entrée": total_inventaires
        }
        fonctions.append(fonction)
        
        # Creer les thematiques (series) avec les inventaires
        for serie, invs in sorted(series_data.items()):
            if not invs:
                continue
            
            serie_notices = sum(inv.get('nb_notices', 0) for inv in invs)
            
            # Nom de la serie
            serie_name = f"Serie {serie}" if len(serie) <= 2 else serie
            
            thematique = {
                "Thématique": serie_name,
                "Fonction": cat_name,
                "Description": f"Serie {serie} - {len(invs)} inventaires en ligne",
                "nb_inventaires": len(invs),
                "nb_notices": serie_notices,
                "Métrage réel": serie_notices / 10,
                "Nombre d'entrée": len(invs),
                "inventaires": [
                    {
                        "cote": inv.get('cote', ''),
                        "titre": inv.get('titre', ''),
                        "dates": inv.get('dates', ''),
                        "nb_notices": inv.get('nb_notices', 0),
                        "url": inv.get('url', '')
                    }
                    for inv in sorted(invs, key=lambda x: x.get('nb_notices', 0), reverse=True)
                ]
            }
            thematiques.append(thematique)
    
    # Ajouter les fonctions sans inventaires en ligne
    for cat_name, cat_info in CATEGORY_INFO.items():
        if cat_name not in by_category or not by_category[cat_name]:
            # Fonction sans inventaires scrapes
            if not any(f['fonction'] == cat_name for f in fonctions):
                fonctions.append({
                    "fonction": cat_name,
                    "Description": cat_info["description"],
                    "url": cat_info["url"],
                    "url_recherche": AD13_SEARCH_URL,
                    "nb_inventaires_en_ligne": 0,
                    "nb_notices_en_ligne": 0,
                    "Métrage réel": 100,
                    "Nombre d'entrée": 0
                })
    
    # Construire le JSON final
    result = {
        "metadata": {
            "source": "https://www.archives13.fr",
            "total_inventaires": len(inventaires_data['fonds']),
            "total_notices": sum(inv.get('nb_notices', 0) for inv in inventaires_data['fonds'])
        },
        "fonctions": fonctions,
        "thematiques": thematiques,
        "producteurs": []  # On peut ajouter plus tard
    }
    
    return result


def main():
    print("=" * 60)
    print("Construction de la visualisation complete")
    print("=" * 60)
    
    # Charger les inventaires
    print("\nChargement des inventaires...")
    inventaires = load_inventaires()
    if not inventaires:
        return
    
    print(f"  {len(inventaires['fonds'])} inventaires charges")
    
    # Construire les donnees
    print("\nConstruction des donnees de visualisation...")
    viz_data = build_visualization_data(inventaires)
    
    print(f"  {len(viz_data['fonctions'])} fonctions")
    print(f"  {len(viz_data['thematiques'])} series/thematiques")
    
    # Stats par fonction
    print("\nRepartition:")
    for func in sorted(viz_data['fonctions'], key=lambda x: x['nb_notices_en_ligne'], reverse=True):
        if func['nb_inventaires_en_ligne'] > 0:
            print(f"  {func['fonction'][:40]:40} : {func['nb_inventaires_en_ligne']:4} inv, {func['nb_notices_en_ligne']:6} notices")
    
    # Sauvegarder
    print(f"\nSauvegarde dans {OUTPUT_PATH}...")
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(viz_data, f, ensure_ascii=False, indent=2)
    
    print("\nTermine!")


if __name__ == "__main__":
    main()

