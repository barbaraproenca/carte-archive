#!/usr/bin/env python3
"""
Script d'extraction des inventaires depuis le moteur de recherche des AD13.
Extrait les informations des fonds disponibles en ligne.

Auteur: Barbara Proenca
Source: https://www.archives13.fr/archive/recherche/fonds/n:93
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import re
from pathlib import Path
from datetime import datetime
import urllib3

# Desactiver les avertissements SSL (le site AD13 a parfois des problemes de certificat)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
BASE_URL = "https://www.archives13.fr"
SEARCH_URL = f"{BASE_URL}/archive/resultats/fonds/fonds/n:93"
ITEMS_PER_PAGE = 100  # Maximum autorise par le site
OUTPUT_DIR = Path(__file__).parent.parent / "data"
DELAY_BETWEEN_REQUESTS = 1  # Secondes entre chaque requete (respect du serveur)

# Headers pour simuler un navigateur
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'fr-FR,fr;q=0.9,en;q=0.8',
}


def get_page(page_num: int) -> str:
    """Recupere le contenu HTML d'une page de resultats."""
    url = f"{SEARCH_URL}/page:{page_num}/pagination:{ITEMS_PER_PAGE}?Rech_mode=and&type=fonds"
    print(f"  Telechargement page {page_num}...")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=30, verify=False)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"  Erreur lors du telechargement de la page {page_num}: {e}")
        return None


def parse_fonds_list(html: str) -> list:
    """Parse la liste des fonds depuis le HTML."""
    soup = BeautifulSoup(html, 'html.parser')
    fonds_list = []
    
    # Chercher le conteneur des resultats
    results_container = soup.find('div', class_='arc_resultats_fonds')
    if not results_container:
        # Essayer une autre structure
        results_container = soup.find('div', {'id': 'arc_resultats'})
    
    if not results_container:
        # Parser le texte directement
        text_content = soup.get_text()
        
        # Pattern pour extraire les fonds: "COTE - Titre (dates) NB_NOTICES"
        # Exemple: "14 B - Tribunal de commerce de La Ciotat. (1790-1858) 39"
        pattern = r'([A-Z0-9\s]+(?:\s[A-Z]+)?)\s*-\s*([^(]+)\s*\(([^)]+)\)\s*(\d+)'
        
        matches = re.findall(pattern, text_content)
        for match in matches:
            cote = match[0].strip()
            titre = match[1].strip()
            dates = match[2].strip()
            nb_notices = int(match[3])
            
            if cote and titre:
                fonds_list.append({
                    'cote': cote,
                    'titre': titre,
                    'dates': dates,
                    'nb_notices': nb_notices
                })
    
    return fonds_list


def parse_fonds_from_text(text: str) -> list:
    """Parse les fonds depuis le texte brut de la page."""
    fonds_list = []
    
    # Pattern plus flexible pour capturer les fonds
    # Format: "COTE - Titre. (dates) nombre"
    lines = text.split('\n')
    
    current_fonds = None
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Chercher le pattern "Detail des fonds" qui precede chaque lien
        if 'Détail des fonds' in line or 'Detail des fonds' in line:
            continue
        
        # Pattern pour les cotes communes: série + numero (ex: "14 B", "3 ETP", "26 J", "2404 W", "6 U 2")
        cote_pattern = r'^(\d+\s*[A-Z]+(?:\s*\d+)?)\s*-\s*(.+?)(?:\.\s*)?(?:\(([^)]+)\))?\s*(\d+)?$'
        match = re.match(cote_pattern, line)
        
        if match:
            cote = match.group(1).strip()
            titre = match.group(2).strip()
            dates = match.group(3).strip() if match.group(3) else ''
            nb_notices = int(match.group(4)) if match.group(4) else 0
            
            # Nettoyer le titre (enlever le point final)
            titre = titre.rstrip('.')
            
            fonds_list.append({
                'cote': cote,
                'titre': titre,
                'dates': dates,
                'nb_notices': nb_notices
            })
    
    return fonds_list


def extract_fonds_from_soup(soup: BeautifulSoup) -> list:
    """Extrait les fonds depuis le BeautifulSoup en utilisant la table de resultats."""
    fonds_list = []
    
    # Chercher la table des resultats
    table = soup.find('table', {'id': 'resultats'})
    if not table:
        return fonds_list
    
    # Parcourir les lignes de la table (ignorer l'entete)
    rows = table.find_all('tr', class_=re.compile(r'(impair|pair)'))
    
    for row in rows:
        cells = row.find_all('td')
        if len(cells) < 3:
            continue
        
        # Premiere cellule: Cote - Titre (dates)
        info_text = cells[0].get_text(strip=True)
        
        # Deuxieme cellule: Nombre de notices
        nb_notices_text = cells[1].get_text(strip=True)
        nb_notices = int(nb_notices_text) if nb_notices_text.isdigit() else 0
        
        # Troisieme cellule: Lien
        link = cells[2].find('a', href=re.compile(r'/archive/fonds/FRAD013'))
        fonds_url = ''
        fonds_id = ''
        if link:
            href = link.get('href', '')
            fonds_url = f"{BASE_URL}{href}"
            fonds_id_match = re.search(r'FRAD013_(\d+)', href)
            if fonds_id_match:
                fonds_id = fonds_id_match.group(1)
        
        # Parser le texte info: "COTE - Titre. (dates)" ou "COTE - Titre (dates)"
        # Exemples:
        # "14 B - Tribunal de commerce de La Ciotat. (1790-1858)"
        # "65 J - René Egger (architecte). 1948-1990"
        
        # Pattern plus flexible
        pattern = r'^(.+?)\s*-\s*(.+?)(?:\.\s*)?\(([^)]+)\)$'
        match = re.match(pattern, info_text)
        
        if match:
            cote = match.group(1).strip()
            titre = match.group(2).strip().rstrip('.')
            dates = match.group(3).strip()
        else:
            # Pattern alternatif sans parentheses pour les dates
            pattern2 = r'^(.+?)\s*-\s*(.+?)(?:\.\s*)?(\d{4}\s*-\s*\d{4}|\d{4})$'
            match2 = re.match(pattern2, info_text)
            
            if match2:
                cote = match2.group(1).strip()
                titre = match2.group(2).strip().rstrip('.')
                dates = match2.group(3).strip()
            else:
                # Fallback: tout mettre dans le titre
                parts = info_text.split(' - ', 1)
                cote = parts[0].strip() if parts else ''
                titre = parts[1].strip() if len(parts) > 1 else info_text
                dates = ''
        
        if cote:
            fonds_list.append({
                'cote': cote,
                'titre': titre,
                'dates': dates,
                'nb_notices': nb_notices,
                'fonds_id': fonds_id,
                'url': fonds_url
            })
    
    return fonds_list


def categorize_fonds(fonds: dict) -> str:
    """Determine la categorie d'un fonds basee sur sa cote."""
    cote = fonds.get('cote', '').upper().strip()
    
    # Extraire la serie (lettre(s) apres le numero eventuel)
    # Exemples: "14 B" -> "B", "26 J" -> "J", "2404 W" -> "W", "6 U 2" -> "U"
    serie_match = re.search(r'(\d+\s+)?([A-Z]+)(\s+\d+)?', cote)
    serie = serie_match.group(2) if serie_match else ''
    
    # Archives privees (J) - a verifier en premier car courant
    if serie == 'J':
        return "ARCHIVES PRIVEES"
    
    # Series anciennes (A, B, C, D, E, F, G, H sans suffixe DEP)
    if serie in ['A', 'B', 'C', 'D', 'F', 'G', 'H'] and 'DEP' not in cote:
        return "ARCHIVES ANCIENNES"
    
    # Fonds E : peut etre ancien ou etat civil
    if serie == 'E' and 'DEP' not in cote and 'ETP' not in cote:
        # Si les dates sont avant 1792, c'est des archives anciennes
        dates = fonds.get('dates', '')
        if dates:
            year_match = re.search(r'(\d{4})', dates)
            if year_match and int(year_match.group(1)) < 1792:
                return "ARCHIVES ANCIENNES"
        return "ETAT CIVIL"
    
    # Series revolutionnaires (L, Q)
    if serie in ['L', 'Q']:
        return "ARCHIVES REVOLUTIONNAIRES"
    
    # Archives hospitalieres (H DEP, H DEPOT, HDEP)
    if 'H DEP' in cote or 'HDEP' in cote:
        return "ARCHIVES HOSPITALIERES"
    
    # Archives communales (E DEP, EDEP)
    if 'E DEP' in cote or 'EDEP' in cote:
        return "ARCHIVES COMMUNALES ET INTERCOMMUNALES DEPOSEES"
    
    # Fonds iconographiques (FI, Fi, PH, AV)
    if serie in ['FI', 'PH', 'AV'] or 'FI' in cote:
        return "FONDS ICONOGRAPHIQUES ET AUDIOVISUELS"
    
    # Etablissements publics (ETP) -> Archives modernes
    if 'ETP' in cote:
        return "ARCHIVES MODERNES ET CONTEMPORAINES"
    
    # Series modernes et contemporaines (K, M, N, O, P, R, S, T, U, V, W, Z)
    if serie in ['K', 'M', 'N', 'O', 'P', 'R', 'S', 'T', 'U', 'V', 'W', 'Z']:
        return "ARCHIVES MODERNES ET CONTEMPORAINES"
    
    # Versements contemporains (series numeriques pures comme 1000 W, 2000 W, etc.)
    if re.match(r'^\d+\s*W', cote):
        return "ARCHIVES MODERNES ET CONTEMPORAINES"
    
    # Bibliotheque (BIB, BIBL)
    if 'BIB' in cote:
        return "BIBLIOTHEQUE"
    
    # Par defaut
    return "ARCHIVES MODERNES ET CONTEMPORAINES"


def scrape_all_fonds() -> list:
    """Scrape tous les fonds depuis le moteur de recherche."""
    all_fonds = []
    page = 1
    max_pages = 50  # Securite
    
    print("Demarrage de l'extraction des inventaires AD13...")
    print(f"URL de base: {SEARCH_URL}")
    print()
    
    while page <= max_pages:
        html = get_page(page)
        if not html:
            break
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extraire les fonds de cette page
        fonds = extract_fonds_from_soup(soup)
        
        if not fonds:
            # Essayer avec le parsing de texte
            text = soup.get_text()
            fonds = parse_fonds_from_text(text)
        
        if not fonds:
            print(f"  Aucun fonds trouve sur la page {page}, arret.")
            break
        
        print(f"  Page {page}: {len(fonds)} fonds extraits")
        all_fonds.extend(fonds)
        
        # Verifier s'il y a une page suivante
        next_link = soup.find('a', string='>')
        if not next_link:
            print("  Derniere page atteinte.")
            break
        
        page += 1
        time.sleep(DELAY_BETWEEN_REQUESTS)
    
    return all_fonds


def save_results(fonds_list: list):
    """Sauvegarde les resultats en JSON et resume."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Ajouter la categorie a chaque fonds
    for fonds in fonds_list:
        fonds['categorie'] = categorize_fonds(fonds)
    
    # Sauvegarder en JSON
    json_path = OUTPUT_DIR / "inventaires_ad13.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'metadata': {
                'source': 'https://www.archives13.fr/archive/recherche/fonds/n:93',
                'date_extraction': datetime.now().isoformat(),
                'total_fonds': len(fonds_list)
            },
            'fonds': fonds_list
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\nResultats sauvegardes dans: {json_path}")
    
    # Statistiques par categorie
    stats = {}
    for fonds in fonds_list:
        cat = fonds['categorie']
        if cat not in stats:
            stats[cat] = {'count': 0, 'notices': 0}
        stats[cat]['count'] += 1
        stats[cat]['notices'] += fonds.get('nb_notices', 0)
    
    print("\nStatistiques par categorie:")
    print("-" * 60)
    for cat, data in sorted(stats.items()):
        print(f"  {cat}: {data['count']} fonds, {data['notices']} notices")
    
    return json_path


def main():
    """Point d'entree principal."""
    print("=" * 60)
    print("Extraction des inventaires AD13")
    print("=" * 60)
    print()
    
    # Scraper les fonds
    fonds_list = scrape_all_fonds()
    
    if not fonds_list:
        print("Aucun fonds extrait. Verifiez la connexion et la structure du site.")
        return
    
    print(f"\nTotal: {len(fonds_list)} fonds extraits")
    
    # Sauvegarder
    save_results(fonds_list)
    
    print("\nExtraction terminee!")


if __name__ == "__main__":
    main()

