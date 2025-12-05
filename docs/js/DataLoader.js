/**
 * DataLoader - Charge et transforme les donnees d'archives pour la visualisation
 * Archives departementales des Bouches-du-Rhone (AD13)
 * 
 * Auteur: Barbara Proenca
 */
export class DataLoader {
  constructor(dataUrl = 'data/archives.json') {
    this.dataUrl = dataUrl;
    this.rawData = null;
    this.hierarchyData = null;
    this.rootName = 'Archives departementales 13';
  }

  /**
   * Charge les donnees JSON
   */
  async load() {
    try {
      const response = await fetch(this.dataUrl);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      this.rawData = await response.json();
      this.hierarchyData = this.buildHierarchy();
      return this.hierarchyData;
    } catch (error) {
      console.error('Erreur lors du chargement des donnees:', error);
      throw error;
    }
  }

  /**
   * Construit la structure hierarchique pour Plotly Treemap
   * Format: { ids, labels, parents, values, customdata }
   */
  buildHierarchy() {
    const ids = [];
    const labels = [];
    const parents = [];
    const values = [];
    const customdata = [];
    const colors = [];

    // Palette de couleurs pour les fonctions
    const colorPalette = [
      '#4A90D9', '#50C8C6', '#6B8E8E', '#7CB342', '#A4A424',
      '#FF9800', '#5C4A72', '#FF4081', '#9C7BB8', '#E53935',
      '#00ACC1', '#8D6E63', '#5E35B1', '#43A047', '#FB8C00'
    ];

    // Construire le mapping des couleurs dynamiquement
    const functionColors = {};
    if (this.rawData.fonctions) {
      this.rawData.fonctions.forEach((func, index) => {
        functionColors[func.fonction] = colorPalette[index % colorPalette.length];
      });
    }

    // Racine
    const rootId = this.rootName;
    ids.push(rootId);
    labels.push(rootId);
    parents.push('');
    values.push(0);
    customdata.push({
      type: 'root',
      description: 'Fonds des Archives departementales des Bouches-du-Rhone'
    });
    colors.push('#6366F1');

    // Niveau 1: Fonctions
    for (const func of this.rawData.fonctions) {
      const funcId = func.fonction;
      ids.push(funcId);
      labels.push(func.fonction);
      parents.push(rootId);
      values.push(func['Métrage réel'] || 0);
      customdata.push({
        type: 'fonction',
        description: func.Description || '',
        dateExtreme: func.date_extreme_fonction || '',
        metrage: func['Métrage réel'] || 0,
        nombreEntrees: func["Nombre d'entrée"] || 0
      });
      colors.push(functionColors[func.fonction] || '#888888');
    }

    // Niveau 2: Thematiques
    for (const theme of this.rawData.thematiques) {
      const funcName = theme.Fonction || theme.fonction;
      const themeName = theme.Thématique || theme.Thematique;
      const themeId = `${funcName}/${themeName}`;
      ids.push(themeId);
      labels.push(themeName);
      parents.push(funcName);
      values.push(theme['Métrage réel'] || 0);
      customdata.push({
        type: 'thematique',
        fonction: funcName,
        dateExtreme: theme.date_extreme_thematique || '',
        metrage: theme['Métrage réel'] || 0,
        nombreEntrees: theme["Nombre d'entrée"] || 0,
        nombreProducteurs: theme['Nombre de producteurs'] || 0
      });
      const parentColor = functionColors[funcName] || '#888888';
      colors.push(this.adjustColor(parentColor, 0.15));
    }

    return { ids, labels, parents, values, customdata, colors, functionColors };
  }

  /**
   * Construit les donnees pour l'arbre D3.js (structure nested)
   */
  buildTreeData() {
    const root = {
      name: this.rootName,
      children: []
    };

    // Grouper les thematiques par fonction
    const themesByFunction = {};
    for (const theme of this.rawData.thematiques) {
      const funcName = theme.Fonction || theme.fonction;
      const themeName = theme.Thématique || theme.Thematique;
      if (!themesByFunction[funcName]) {
        themesByFunction[funcName] = [];
      }
      themesByFunction[funcName].push({
        name: themeName,
        value: theme['Métrage réel'] || 0,
        dateExtreme: theme.date_extreme_thematique || '',
        nombreEntrees: theme["Nombre d'entrée"] || 0
      });
    }

    // Construire l'arbre
    for (const func of this.rawData.fonctions) {
      const funcNode = {
        name: func.fonction,
        value: func['Métrage réel'] || 0,
        description: func.Description || '',
        dateExtreme: func.date_extreme_fonction || '',
        children: themesByFunction[func.fonction] || []
      };
      root.children.push(funcNode);
    }

    return root;
  }

  /**
   * Ajuste la luminosite d'une couleur hex
   */
  adjustColor(hex, percent) {
    const num = parseInt(hex.replace('#', ''), 16);
    const amt = Math.round(2.55 * percent * 100);
    const R = Math.min(255, Math.max(0, (num >> 16) + amt));
    const G = Math.min(255, Math.max(0, ((num >> 8) & 0x00FF) + amt));
    const B = Math.min(255, Math.max(0, (num & 0x0000FF) + amt));
    return `#${(0x1000000 + R * 0x10000 + G * 0x100 + B).toString(16).slice(1)}`;
  }

  /**
   * Retourne les statistiques globales
   */
  getStats() {
    if (!this.rawData) return null;

    const totalMetrage = this.rawData.fonctions.reduce(
      (sum, f) => sum + (f['Métrage réel'] || 0), 0
    );
    const totalEntrees = this.rawData.fonctions.reduce(
      (sum, f) => sum + (f["Nombre d'entrée"] || 0), 0
    );

    return {
      nombreFonctions: this.rawData.fonctions.length,
      nombreThematiques: this.rawData.thematiques.length,
      nombreProducteurs: this.rawData.producteurs.length,
      totalMetrage: totalMetrage.toFixed(2),
      totalEntrees
    };
  }
}
