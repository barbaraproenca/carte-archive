#!/usr/bin/env python3
"""
Script de conversion des donnees Excel vers JSON pour la visualisation des archives.
Archives departementales des Bouches-du-Rhone (AD13)

Auteur: Barbara Proenca
"""

import pandas as pd
import json
import sys
from pathlib import Path


def convert_excel_to_json(excel_path: str, output_path: str) -> None:
    """
    Convertit le fichier Excel des archives en JSON pour la visualisation.
    
    Args:
        excel_path: Chemin vers le fichier Excel source
        output_path: Chemin vers le fichier JSON de sortie
    """
    print(f"Lecture du fichier Excel: {excel_path}")
    
    xl = pd.ExcelFile(excel_path)
    
    # Charger les feuilles
    fonctions = pd.read_excel(xl, sheet_name='Fonction')
    thematiques = pd.read_excel(xl, sheet_name='Thématique')
    producteurs = pd.read_excel(xl, sheet_name='Producteur')
    
    # Nettoyer les valeurs NaN
    fonctions = fonctions.fillna('')
    thematiques = thematiques.fillna('')
    producteurs = producteurs.fillna('')
    
    # Construire la structure de donnees
    data = {
        "fonctions": fonctions.to_dict(orient='records'),
        "thematiques": thematiques.to_dict(orient='records'),
        "producteurs": producteurs.to_dict(orient='records')
    }
    
    # Ecrire le fichier JSON
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"Fichier JSON genere: {output_path}")
    print(f"  - Fonctions: {len(data['fonctions'])}")
    print(f"  - Thematiques: {len(data['thematiques'])}")
    print(f"  - Producteurs: {len(data['producteurs'])}")


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


if __name__ == "__main__":
    main()

