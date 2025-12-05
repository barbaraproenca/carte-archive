# Visualisation des fonds d'archives - AD13

Outil de visualisation interactive des fonds des Archives departementales des Bouches-du-Rhone (AD13).

Cette application permet d'explorer les 982 inventaires en ligne disponibles sur le portail archives13.fr, organises en categories, series et fonds individuels.

## Auteur

Barbara Proenca, archiviste aux Archives departementales des Bouches-du-Rhone

## Fonctionnalites

- Treemap interactif : vue hierarchique des fonds par volume de notices
- Arbre collapsible : navigation dans la structure des fonds
- Panneau d'information : details de chaque element selectionne
- Liens directs vers archives13.fr : acces aux inventaires en ligne
- 982 inventaires, 215 075 notices, 10 categories, 16 series

## Structure du projet

```
vizu-archive/
├── data/
│   ├── archives.xlsx          # Donnees source (modifiable)
│   └── inventaires_ad13.json  # Donnees scrappees du portail
├── docs/                      # Site web (GitHub Pages)
│   ├── index.html
│   ├── js/
│   │   ├── App.js
│   │   ├── DataLoader.js
│   │   ├── TreemapViz.js
│   │   └── TreeViz.js
│   └── data/
│       └── archives.json      # Donnees JSON pour la visualisation
├── scripts/
│   ├── convert_excel_to_json.py  # Conversion Excel -> JSON
│   ├── export_to_excel.py        # Export des donnees vers Excel
│   └── scrape_ad13_inventaires.py # Scraping du portail AD13
└── .github/
    └── workflows/
        └── update-data.yml    # Mise a jour automatique
```

## Modifier les donnees

Le fichier `data/archives.xlsx` contient les donnees de la visualisation. Il peut etre modifie par toute personne ayant acces a Excel ou LibreOffice.

### Structure du fichier Excel

Le fichier contient 4 feuilles :

1. **Fonction** : Categories principales des fonds
   - `fonction` : Nom de la categorie
   - `Description` : Description detaillee
   - `url` : Lien vers la page archives13.fr
   - `nb_inventaires_en_ligne` : Nombre d'inventaires
   - `nb_notices_en_ligne` : Nombre total de notices

2. **Thematique** : Series archivistiques
   - `Thematique` : Nom de la serie (ex: "Serie W")
   - `Fonction` : Categorie parente
   - `Description` : Description
   - `nb_inventaires` : Nombre d'inventaires dans la serie
   - `nb_notices` : Nombre de notices

3. **Inventaire** : Liste des 982 inventaires
   - `cote` : Cote de l'inventaire (ex: "14 B")
   - `titre` : Titre de l'inventaire
   - `dates` : Dates extremes
   - `nb_notices` : Nombre de notices
   - `url` : Lien direct vers l'inventaire
   - `categorie` : Categorie
   - `serie` : Serie

4. **Producteur** : Producteurs d'archives (optionnel)

### Mettre a jour la visualisation

Apres modification du fichier Excel :

```bash
# Regenerer le JSON
python scripts/convert_excel_to_json.py

# Tester localement
cd docs && python -m http.server 8080
```

Ou simplement : commiter les modifications sur GitHub. Le workflow automatique regenerera le JSON.

## Installation locale

### Prerequis

- Python 3.8+
- Navigateur web moderne

### Dependances Python

```bash
pip install -r requirements.txt
```

### Lancer le serveur local

```bash
cd docs
python -m http.server 8080
```

Ouvrir http://localhost:8080 dans le navigateur.

## Deploiement GitHub Pages

1. Activer GitHub Pages dans les parametres du repository
2. Source : branche `main`, dossier `/docs`
3. Le site sera accessible sur `https://[username].github.io/[repo-name]/`

## Technologies

- Plotly.js : Treemap interactif
- D3.js : Arbre collapsible
- Python : Scripts de conversion et scraping
- GitHub Actions : Automatisation

## Scripts disponibles

### Conversion Excel vers JSON

```bash
python scripts/convert_excel_to_json.py
```

Lit le fichier `data/archives.xlsx` et genere `docs/data/archives.json`.

### Export des donnees vers Excel

```bash
python scripts/export_to_excel.py
```

Genere un fichier Excel complet a partir des donnees scrappees.

### Scraping du portail AD13

```bash
python scripts/scrape_ad13_inventaires.py
```

Extrait les inventaires disponibles sur archives13.fr.

## Source des donnees

Les donnees sont extraites du portail des Archives departementales des Bouches-du-Rhone : https://www.archives13.fr

## Licence

Ce projet est un outil interne des Archives departementales des Bouches-du-Rhone.
