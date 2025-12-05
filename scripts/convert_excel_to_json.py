#!/usr/bin/env python3
"""
Script de conversion des donnees Excel vers JSON pour la visualisation des archives.
Ce script lit le fichier Excel et genere un JSON hierarchique pour la visualisation.

Archives departementales des Bouches-du-Rhone (AD13)
Auteur: Barbara Proenca
"""

import pandas as pd
import json
import sys
from pathlib import Path
from collections import defaultdict


def convert_excel_to_json(excel_path: str, output_path: str) -> None:
    """
    Convertit le fichier Excel des archives en JSON pour la visualisation.
    
    Structure du fichier Excel attendu:
    - Feuille 'Fonction': Categories principales (archives anciennes, modernes, etc.)
    - Feuille 'Thematique': Series archivistiques (Serie A, Serie B, etc.)
    - Feuille 'Inventaire': Liste detaillee des inventaires en ligne
    - Feuille 'Producteur': (optionnel) Producteurs d'archives
    
    Args:
        excel_path: Chemin vers le fichier Excel source
        output_path: Chemin vers le fichier JSON de sortie
    """
    print("=" * 60)
    print("Conversion Excel -> JSON")
    print("=" * 60)
    print(f"\nLecture du fichier Excel: {excel_path}")
    
    xl = pd.ExcelFile(excel_path)
    sheets = xl.sheet_names
    print(f"Feuilles trouvees: {', '.join(sheets)}")
    
    # Charger les feuilles principales
    fonctions = pd.read_excel(xl, sheet_name='Fonction')
    thematiques = pd.read_excel(xl, sheet_name='Thématique')
    
    # Charger les inventaires si disponibles
    inventaires = None
    if 'Inventaire' in sheets:
        inventaires = pd.read_excel(xl, sheet_name='Inventaire')
        print(f"  Inventaires: {len(inventaires)} lignes")
    
    # Charger les producteurs si disponibles
    producteurs = pd.DataFrame()
    if 'Producteur' in sheets:
        producteurs = pd.read_excel(xl, sheet_name='Producteur')
    
    # Nettoyer les valeurs NaN
    fonctions = fonctions.fillna('')
    thematiques = thematiques.fillna('')
    producteurs = producteurs.fillna('')
    if inventaires is not None:
        inventaires = inventaires.fillna('')
    
    print(f"\nDonnees chargees:")
    print(f"  - Fonctions: {len(fonctions)}")
    print(f"  - Thematiques: {len(thematiques)}")
    print(f"  - Producteurs: {len(producteurs)}")
    
    # Si on a des inventaires, les integrer aux thematiques
    if inventaires is not None and len(inventaires) > 0:
        print(f"  - Inventaires: {len(inventaires)}")
        
        # Grouper les inventaires par serie
        inv_by_serie = defaultdict(list)
        for _, inv in inventaires.iterrows():
            serie = inv.get('serie', '')
            inv_by_serie[serie].append({
                "cote": str(inv.get('cote', '')),
                "titre": str(inv.get('titre', '')),
                "dates": str(inv.get('dates', '')),
                "nb_notices": int(inv.get('nb_notices', 0)) if inv.get('nb_notices', '') != '' else 0,
                "url": str(inv.get('url', ''))
            })
        
        # Ajouter les inventaires aux thematiques
        thematiques_with_inv = []
        for _, theme in thematiques.iterrows():
            theme_dict = theme.to_dict()
            theme_name = theme.get('Thématique', '')
            theme_dict['inventaires'] = inv_by_serie.get(theme_name, [])
            thematiques_with_inv.append(theme_dict)
        
        thematiques_data = thematiques_with_inv
    else:
        thematiques_data = thematiques.to_dict(orient='records')
    
    # Calculer les stats globales
    total_inventaires = sum(
        int(f.get('nb_inventaires_en_ligne', 0)) if f.get('nb_inventaires_en_ligne', '') != '' else 0
        for f in fonctions.to_dict(orient='records')
    )
    total_notices = sum(
        int(f.get('nb_notices_en_ligne', 0)) if f.get('nb_notices_en_ligne', '') != '' else 0
        for f in fonctions.to_dict(orient='records')
    )
    
    # Construire la structure de donnees
    data = {
        "metadata": {
            "source": "https://www.archives13.fr",
            "total_inventaires": total_inventaires,
            "total_notices": total_notices
        },
        "fonctions": fonctions.to_dict(orient='records'),
        "thematiques": thematiques_data,
        "producteurs": producteurs.to_dict(orient='records') if len(producteurs) > 0 else []
    }
    
    # Ecrire le fichier JSON
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\nFichier JSON genere: {output_path}")
    print(f"  - Fonctions: {len(data['fonctions'])}")
    print(f"  - Thematiques: {len(data['thematiques'])}")
    print(f"  - Total inventaires: {total_inventaires}")
    print(f"  - Total notices: {total_notices}")


def main():
    # Chemins par defaut
    project_root = Path(__file__).parent.parent
    excel_path = project_root / "data" / "archives.xlsx"
    output_path = project_root / "docs" / "data" / "archives.json"
    
    # Permettre de passer des chemins en arguments
    if len(sys.argv) >= 2:
        excel_path = Path(sys.argv[1])
    if len(sys.argv) >= 3:
        output_path = Path(sys.argv[2])
    
    if not excel_path.exists():
        print(f"Erreur: Fichier Excel introuvable: {excel_path}")
        sys.exit(1)
    
    convert_excel_to_json(str(excel_path), str(output_path))
    print("\nConversion terminee!")


if __name__ == "__main__":
    main()
