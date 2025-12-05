# Visualisation des fonds d'archives - AD13

Outil de visualisation interactive des fonds des Archives departementales des Bouches-du-Rhone.

Deux modes de visualisation sont disponibles :
- **Treemap** : representation proportionnelle des volumes d'archives par fonction et thematique
- **Arbre** : representation hierarchique des fonds avec navigation par niveaux

## Demonstration

La visualisation est accessible sur GitHub Pages : [Voir la demo](https://[votre-username].github.io/vizu-archive/)

## Structure du projet

```
vizu-archive/
├── docs/                    # Site web (GitHub Pages)
│   ├── index.html
│   ├── js/
│   │   ├── App.js
│   │   ├── DataLoader.js
│   │   ├── TreemapViz.js
│   │   └── TreeViz.js
│   └── data/
│       └── archives.json
├── data/
│   └── archives.xlsx        # Donnees source
├── scripts/
│   └── convert_excel_to_json.py
├── .github/
│   └── workflows/
│       └── update-data.yml
└── README.md
```

## Mise a jour des donnees

### Automatique (via GitHub Actions)

1. Modifier le fichier `data/archives.xlsx`
2. Commit et push sur le depot
3. Le workflow genere automatiquement le fichier JSON

### Manuelle

```bash
pip install pandas openpyxl
python scripts/convert_excel_to_json.py data/archives.xlsx docs/data/archives.json
```

## Format des donnees

Le fichier Excel doit contenir trois feuilles :

### Feuille "Fonction"

| Colonne | Description |
|---------|-------------|
| fonction | Nom de la fonction |
| Description | Description detaillee |
| date_extreme_min | Date la plus ancienne |
| date_extreme_max | Date la plus recente |
| date_extreme_fonction | Plage de dates formatee |
| Metrage reel | Volume en metres lineaires |
| Nombre d'entree | Nombre de versements |

### Feuille "Thematique"

| Colonne | Description |
|---------|-------------|
| Thematique | Nom de la thematique |
| fonction | Fonction parente |
| date_extreme_min | Date la plus ancienne |
| date_extreme_max | Date la plus recente |
| date_extreme_thematique | Plage de dates formatee |
| Metrage reel | Volume en metres lineaires |
| Nombre d'entree | Nombre de versements |
| Nombre de producteurs | Nombre de producteurs |

### Feuille "Producteur"

| Colonne | Description |
|---------|-------------|
| Numero Ligeo | Identifiant |
| Nom | Nom du producteur |
| date_extreme_min | Date la plus ancienne |
| date_extreme_max | Date la plus recente |
| date_extreme_producteur | Plage de dates formatee |
| Metrage reel | Volume en metres lineaires |
| Nombre d'entree | Nombre de versements |

## Deploiement sur GitHub Pages

1. Dans les parametres du depot, section "Pages"
2. Source : "Deploy from a branch"
3. Branche : main, dossier /docs
4. Enregistrer

## Technologies

- Plotly.js 2.27 (treemap)
- D3.js v7 (arbre)
- Vanilla JavaScript (ES6 modules)
- GitHub Actions (automatisation)

## Auteur

Barbara Proenca  
Archiviste aux Archives departementales des Bouches-du-Rhone

## Licence

Ce projet est sous licence MIT.

