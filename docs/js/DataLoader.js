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

    // Palette de couleurs professionnelle pour les archives
    const colorPalette = [
      '#3B82F6', // Bleu - Archives anciennes
      '#8B5CF6', // Violet - Archives revolutionnaires  
      '#06B6D4', // Cyan - Archives modernes
      '#10B981', // Emeraude - Archives hospitalieres
      '#F59E0B', // Ambre - Archives communales
      '#EF4444', // Rouge - Archives privees
      '#EC4899', // Rose - Fonds iconographiques
      '#6366F1', // Indigo - Bibliotheque
      '#14B8A6', // Teal - Etat civil
      '#F97316', // Orange - Archives notariales
      '#84CC16', // Lime
      '#A855F7', // Fuchsia
    ];

    // Construire le mapping des couleurs et URLs dynamiquement
    const functionColors = {};
    const functionUrls = {};
    const functionSearchUrls = {};
    if (this.rawData.fonctions) {
      this.rawData.fonctions.forEach((func, index) => {
        functionColors[func.fonction] = colorPalette[index % colorPalette.length];
        functionUrls[func.fonction] = func.url || '';
        functionSearchUrls[func.fonction] = func.url_recherche || 'https://www.archives13.fr/archive/recherche/fonds/n:93';
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
      description: 'Fonds des Archives departementales des Bouches-du-Rhone',
      hoverText: 'Cliquez sur une categorie pour explorer',
      statsText: '982 inventaires en ligne',
      url: 'https://www.archives13.fr'
    });
    colors.push('#6366F1');

    // Niveau 1: Fonctions (categories)
    for (const func of this.rawData.fonctions) {
      const funcId = func.fonction;
      const nbInv = func.nb_inventaires_en_ligne || 0;
      const nbNot = func.nb_notices_en_ligne || 0;
      const desc = func.Description || '';
      const shortDesc = desc.length > 120 ? desc.substring(0, 120) + '...' : desc;
      
      ids.push(funcId);
      labels.push(func.fonction);
      parents.push(rootId);
      values.push(nbNot || 1);
      customdata.push({
        type: 'fonction',
        description: desc,
        hoverText: shortDesc || 'Categorie d\'archives',
        statsText: `${nbInv} inventaires | ${nbNot.toLocaleString()} notices`,
        url: func.url || '',
        urlRecherche: func.url_recherche || 'https://www.archives13.fr/archive/recherche/fonds/n:93',
        nbInventairesEnLigne: nbInv,
        nbNoticesEnLigne: nbNot
      });
      colors.push(functionColors[func.fonction] || '#888888');
    }

    // Niveau 2: Thematiques (series)
    for (const theme of this.rawData.thematiques) {
      const funcName = theme.Fonction || theme.fonction;
      const themeName = theme.Thématique || theme.Thematique;
      const themeId = `${funcName}/${themeName}`;
      const inventaires = theme.inventaires || [];
      const nbInv = inventaires.length;
      const nbNot = theme.nb_notices || 0;
      const desc = theme.Description || `${nbInv} inventaires en ligne`;
      
      ids.push(themeId);
      labels.push(themeName);
      parents.push(funcName);
      values.push(nbNot || 1);
      customdata.push({
        type: 'thematique',
        fonction: funcName,
        description: desc,
        hoverText: desc,
        statsText: `${nbInv} inventaires | ${nbNot.toLocaleString()} notices`,
        nbInventaires: nbInv,
        nbNotices: nbNot,
        url: functionUrls[funcName] || '',
        urlRecherche: functionSearchUrls[funcName] || ''
      });
      const parentColor = functionColors[funcName] || '#888888';
      colors.push(this.adjustColor(parentColor, 0.12));
      
      // Niveau 3: Inventaires individuels
      for (const inv of inventaires) {
        const invId = `${themeId}/${inv.cote}`;
        const titre = inv.titre || '';
        const dates = inv.dates || '';
        const nbNotices = inv.nb_notices || 0;
        
        ids.push(invId);
        labels.push(inv.cote);
        parents.push(themeId);
        values.push(nbNotices || 1);
        customdata.push({
          type: 'inventaire',
          cote: inv.cote,
          titre: titre,
          dates: dates,
          hoverText: `<b>${titre}</b><br>Dates: ${dates}`,
          statsText: `${nbNotices.toLocaleString()} notices`,
          nbNotices: nbNotices,
          url: inv.url || ''
        });
        colors.push(this.adjustColor(parentColor, 0.25));
      }
    }

    return { ids, labels, parents, values, customdata, colors, functionColors };
  }

  /**
   * Construit les donnees pour l'arbre D3.js (structure nested)
   */
  buildTreeData() {
    // Construire le mapping des URLs par fonction
    const functionUrls = {};
    for (const func of this.rawData.fonctions) {
      functionUrls[func.fonction] = func.url || '';
    }

    const root = {
      name: this.rootName,
      url: 'https://www.archives13.fr/n/presentation-des-fonds/n:94',
      children: []
    };

    // Grouper les thematiques par fonction
    const themesByFunction = {};
    for (const theme of this.rawData.thematiques) {
      const funcName = theme.Fonction || theme.fonction;
      const themeName = theme.Thématique || theme.Thematique;
      const inventaires = theme.inventaires || [];
      
      if (!themesByFunction[funcName]) {
        themesByFunction[funcName] = [];
      }
      
      // Creer les enfants (inventaires) pour cette thematique
      const invChildren = inventaires.map(inv => ({
        name: inv.cote,
        titre: inv.titre,
        dates: inv.dates,
        value: inv.nb_notices || 1,
        nbNotices: inv.nb_notices || 0,
        url: inv.url || '',
        type: 'inventaire'
      }));
      
      themesByFunction[funcName].push({
        name: themeName,
        value: theme['Métrage réel'] || theme.nb_notices || 0,
        description: theme.Description || `${inventaires.length} inventaires`,
        nbInventaires: inventaires.length,
        nbNotices: theme.nb_notices || 0,
        url: functionUrls[funcName] || '',
        urlRecherche: 'https://www.archives13.fr/archive/recherche/fonds/n:93',
        children: invChildren
      });
    }

    // Construire l'arbre
    for (const func of this.rawData.fonctions) {
      const funcNode = {
        name: func.fonction,
        value: func['Métrage réel'] || 0,
        description: func.Description || '',
        nbInventaires: func.nb_inventaires_en_ligne || 0,
        nbNotices: func.nb_notices_en_ligne || 0,
        url: func.url || '',
        urlRecherche: func.url_recherche || 'https://www.archives13.fr/archive/recherche/fonds/n:93',
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

    const totalInventaires = this.rawData.fonctions.reduce(
      (sum, f) => sum + (f.nb_inventaires_en_ligne || 0), 0
    );
    const totalNotices = this.rawData.fonctions.reduce(
      (sum, f) => sum + (f.nb_notices_en_ligne || 0), 0
    );

    return {
      nombreFonctions: this.rawData.fonctions.length,
      nombreThematiques: this.rawData.thematiques.length,
      nombreProducteurs: this.rawData.producteurs?.length || 0,
      totalInventaires,
      totalNotices
    };
  }
}
