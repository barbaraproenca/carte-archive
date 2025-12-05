#!/usr/bin/env python3
"""
Script d'integration des inventaires scrapes dans les donnees de la visualisation.
Met a jour le JSON de la visualisation avec le nombre d'inventaires en ligne par categorie.

Auteur: Barbara Proenca
"""

import json
from pathlib import Path

# Chemins
PROJECT_ROOT = Path(__file__).parent.parent
INVENTAIRES_PATH = PROJECT_ROOT / "data" / "inventaires_ad13.json"
ARCHIVES_JSON_PATH = PROJECT_ROOT / "docs" / "data" / "archives.json"


def load_inventaires():
    """Charge les inventaires scrapes."""
    with open(INVENTAIRES_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_archives():
    """Charge les donnees de la visualisation."""
    with open(ARCHIVES_JSON_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


def compute_stats_by_category(inventaires_data):
    """Calcule les statistiques par categorie."""
    stats = {}
    
    for fonds in inventaires_data['fonds']:
        cat = fonds.get('categorie', 'AUTRE')
        if cat not in stats:
            stats[cat] = {
                'nb_inventaires': 0,
                'nb_notices': 0,
                'fonds': []
            }
        stats[cat]['nb_inventaires'] += 1
        stats[cat]['nb_notices'] += fonds.get('nb_notices', 0)
        stats[cat]['fonds'].append({
            'cote': fonds.get('cote', ''),
            'titre': fonds.get('titre', ''),
            'dates': fonds.get('dates', ''),
            'nb_notices': fonds.get('nb_notices', 0),
            'url': fonds.get('url', '')
        })
    
    return stats


def update_archives_with_inventaires(archives_data, inv_stats):
    """Met a jour les donnees archives avec les stats des inventaires."""
    
    # Mapping entre noms de categories
    category_mapping = {
        'ARCHIVES ANCIENNES': 'ARCHIVES ANCIENNES',
        'ARCHIVES REVOLUTIONNAIRES': 'ARCHIVES REVOLUTIONNAIRES',
        'ARCHIVES MODERNES ET CONTEMPORAINES': 'ARCHIVES MODERNES ET CONTEMPORAINES',
        'ARCHIVES HOSPITALIERES': 'ARCHIVES HOSPITALIERES',
        'ARCHIVES COMMUNALES ET INTERCOMMUNALES DEPOSEES': 'ARCHIVES COMMUNALES ET INTERCOMMUNALES DEPOSEES',
        'ARCHIVES PRIVEES': 'ARCHIVES PRIVEES',
        'FONDS ICONOGRAPHIQUES ET AUDIOVISUELS': 'FONDS ICONOGRAPHIQUES ET AUDIOVISUELS',
        'BIBLIOTHEQUE': 'BIBLIOTHEQUE',
        'ETAT CIVIL': 'ETAT CIVIL',
        'ARCHIVES NOTARIALES': 'ARCHIVES NOTARIALES'
    }
    
    # Mettre a jour chaque fonction avec les stats d'inventaires
    for func in archives_data['fonctions']:
        func_name = func.get('fonction', '')
        
        if func_name in inv_stats:
            stats = inv_stats[func_name]
            func['nb_inventaires_en_ligne'] = stats['nb_inventaires']
            func['nb_notices_en_ligne'] = stats['nb_notices']
            # Ajouter les 5 fonds principaux (par nombre de notices)
            top_fonds = sorted(stats['fonds'], key=lambda x: x['nb_notices'], reverse=True)[:5]
            func['inventaires_principaux'] = top_fonds
        else:
            func['nb_inventaires_en_ligne'] = 0
            func['nb_notices_en_ligne'] = 0
            func['inventaires_principaux'] = []
    
    # Ajouter les metadonnees globales
    total_inventaires = sum(s['nb_inventaires'] for s in inv_stats.values())
    total_notices = sum(s['nb_notices'] for s in inv_stats.values())
    
    archives_data['metadata'] = {
        'inventaires_en_ligne': {
            'total_inventaires': total_inventaires,
            'total_notices': total_notices,
            'date_extraction': archives_data.get('metadata', {}).get('date_extraction', ''),
            'source': 'https://www.archives13.fr/archive/recherche/fonds/n:93'
        }
    }
    
    return archives_data


def save_archives(archives_data):
    """Sauvegarde les donnees mises a jour."""
    with open(ARCHIVES_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(archives_data, f, ensure_ascii=False, indent=2)


def main():
    print("Integration des inventaires dans la visualisation")
    print("=" * 50)
    
    # Verifier que les inventaires existent
    if not INVENTAIRES_PATH.exists():
        print(f"Erreur: Fichier {INVENTAIRES_PATH} non trouve.")
        print("Executez d'abord: python scripts/scrape_ad13_inventaires.py")
        return
    
    # Charger les donnees
    print("Chargement des inventaires...")
    inventaires = load_inventaires()
    print(f"  {len(inventaires['fonds'])} inventaires charges")
    
    print("Chargement des donnees de visualisation...")
    archives = load_archives()
    print(f"  {len(archives['fonctions'])} fonctions")
    
    # Calculer les stats
    print("Calcul des statistiques par categorie...")
    inv_stats = compute_stats_by_category(inventaires)
    for cat, stats in sorted(inv_stats.items()):
        print(f"  {cat}: {stats['nb_inventaires']} inventaires, {stats['nb_notices']} notices")
    
    # Mettre a jour
    print("Mise a jour des donnees...")
    updated_archives = update_archives_with_inventaires(archives, inv_stats)
    
    # Sauvegarder
    print("Sauvegarde...")
    save_archives(updated_archives)
    
    print(f"\nFichier mis a jour: {ARCHIVES_JSON_PATH}")
    print("Integration terminee!")


if __name__ == "__main__":
    main()

