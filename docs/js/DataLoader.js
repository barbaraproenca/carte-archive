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
        nombreEntrees: func["Nombre d'entrée"] || 0,
        url: func.url || '',
        urlRecherche: func.url_recherche || 'https://www.archives13.fr/archive/recherche/fonds/n:93',
        nbInventairesEnLigne: func.nb_inventaires_en_ligne || 0,
        nbNoticesEnLigne: func.nb_notices_en_ligne || 0,
        inventairesPrincipaux: func.inventaires_principaux || []
      });
      colors.push(functionColors[func.fonction] || '#888888');
    }

    // Niveau 2: Thematiques (series)
    for (const theme of this.rawData.thematiques) {
      const funcName = theme.Fonction || theme.fonction;
      const themeName = theme.Thématique || theme.Thematique;
      const themeId = `${funcName}/${themeName}`;
      const inventaires = theme.inventaires || [];
      
      ids.push(themeId);
      labels.push(themeName);
      parents.push(funcName);
      values.push(theme['Métrage réel'] || theme.nb_notices || 0);
      customdata.push({
        type: 'thematique',
        fonction: funcName,
        description: theme.Description || `${inventaires.length} inventaires en ligne`,
        metrage: theme['Métrage réel'] || 0,
        nombreEntrees: theme["Nombre d'entrée"] || inventaires.length,
        nbInventaires: theme.nb_inventaires || inventaires.length,
        nbNotices: theme.nb_notices || 0,
        url: functionUrls[funcName] || '',
        urlRecherche: functionSearchUrls[funcName] || 'https://www.archives13.fr/archive/recherche/fonds/n:93',
        inventaires: inventaires
      });
      const parentColor = functionColors[funcName] || '#888888';
      colors.push(this.adjustColor(parentColor, 0.12));
      
      // Niveau 3: Inventaires individuels
      for (const inv of inventaires) {
        const invId = `${themeId}/${inv.cote}`;
        ids.push(invId);
        labels.push(inv.cote);
        parents.push(themeId);
        values.push(inv.nb_notices || 1);
        customdata.push({
          type: 'inventaire',
          cote: inv.cote,
          titre: inv.titre,
          dates: inv.dates,
          nbNotices: inv.nb_notices || 0,
          url: inv.url || '',
          urlRecherche: inv.url || ''
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
