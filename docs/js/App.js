/**
 * App - Application principale de visualisation des archives
 * Archives departementales des Bouches-du-Rhone (AD13)
 * 
 * Auteur: Barbara Proenca
 */
import { DataLoader } from './DataLoader.js';
import { TreemapViz } from './TreemapViz.js';
import { TreeViz } from './TreeViz.js';

class App {
  constructor() {
    this.dataLoader = new DataLoader();
    this.treemapViz = null;
    this.treeViz = null;
    this.currentView = 'treemap';
    this.currentInventaires = [];
    this.filteredInventaires = [];
  }

  /**
   * Initialise l'application
   */
  async init() {
    try {
      this.showLoader(true);

      const data = await this.dataLoader.load();

      this.displayStats();

      const treemapContainer = document.getElementById('treemap-container');
      const containerHeight = treemapContainer ? treemapContainer.clientHeight || 600 : 600;

      this.treemapViz = new TreemapViz('treemap-container', {
        height: containerHeight,
        onNodeClick: (point) => this.handleTreemapClick(point)
      });
      this.treemapViz.render(data);

      const treeData = this.dataLoader.buildTreeData();
      const treeContainer = document.getElementById('tree-container');
      const treeHeight = treeContainer ? treeContainer.clientHeight || 600 : 600;
      const treeWidth = treeContainer ? treeContainer.clientWidth || 1200 : 1200;
      
      this.treeViz = new TreeViz('tree-container', {
        width: treeWidth,
        height: treeHeight,
        onNodeClick: (data) => this.handleTreeNodeClick(data)
      });
      this.treeViz.render(treeData);

      this.setupEventListeners();

      this.showLoader(false);

      console.log('Application initialisee');
    } catch (error) {
      console.error('Erreur lors de l\'initialisation:', error);
      this.showError(error.message);
    }
  }

  /**
   * Affiche les statistiques globales
   */
  displayStats() {
    const stats = this.dataLoader.getStats();
    if (!stats) return;

    document.getElementById('stat-fonctions').textContent = stats.nombreFonctions;
    document.getElementById('stat-thematiques').textContent = stats.nombreThematiques;
    document.getElementById('stat-metrage').textContent = stats.totalInventaires;
    document.getElementById('stat-entrees').textContent = stats.totalNotices.toLocaleString();
  }

  /**
   * Configure les ecouteurs d'evenements
   */
  setupEventListeners() {
    // Boutons de vue
    document.querySelectorAll('.view-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const view = e.currentTarget.dataset.view;
        this.switchView(view);
      });
    });

    // Controles arbre
    document.getElementById('expand-all')?.addEventListener('click', () => {
      this.treeViz?.expandAll();
    });

    document.getElementById('collapse-all')?.addEventListener('click', () => {
      this.treeViz?.collapseAll();
    });

    // Recherche instantanee
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        this.filterInventaires(e.target.value);
      });
    }

    // Resize
    window.addEventListener('resize', () => {
      if (this.treemapViz) {
        this.treemapViz.resize();
      }
    });
  }

  /**
   * Bascule entre les vues
   */
  switchView(view) {
    this.currentView = view;

    document.querySelectorAll('.view-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.view === view);
    });

    document.getElementById('treemap-view').classList.toggle('hidden', view !== 'treemap');
    document.getElementById('tree-view').classList.toggle('hidden', view !== 'tree');

    if (view === 'treemap' && this.treemapViz) {
      setTimeout(() => this.treemapViz.resize(), 100);
    }
  }

  /**
   * Gere le clic sur le treemap
   */
  handleTreemapClick(point) {
    const customdata = point.customdata || {};
    console.log('Treemap click:', point.label, customdata.type);

    // Si c'est une thematique (serie), afficher les inventaires
    if (customdata.type === 'thematique' && customdata.inventaires) {
      this.showInventairesList(point.label, customdata);
    }
    // Si c'est un inventaire, ouvrir le lien
    else if (customdata.type === 'inventaire' && customdata.url) {
      window.open(customdata.url, '_blank');
    }
    // Si c'est une fonction, afficher info
    else if (customdata.type === 'fonction') {
      this.showFonctionInfo(point.label, customdata);
    }
  }

  /**
   * Affiche la liste des inventaires pour une serie
   */
  showInventairesList(serieName, customdata) {
    const inventaires = customdata.inventaires || [];
    this.currentInventaires = inventaires;
    this.filteredInventaires = inventaires;

    // Mettre a jour le header
    document.getElementById('panel-serie-name').textContent = serieName;
    document.getElementById('panel-count').textContent = inventaires.length;
    document.getElementById('panel-subtitle').textContent = 
      `${customdata.nbNotices?.toLocaleString() || 0} notices au total`;

    // Vider la recherche
    const searchInput = document.getElementById('search-input');
    if (searchInput) searchInput.value = '';

    // Afficher les inventaires
    this.renderInventairesList(inventaires);

    // Afficher le panel sur mobile
    document.getElementById('inventaires-panel')?.classList.add('visible');
  }

  /**
   * Affiche les informations d'une fonction/categorie
   */
  showFonctionInfo(name, customdata) {
    document.getElementById('panel-serie-name').textContent = name;
    document.getElementById('panel-count').textContent = customdata.nbInventairesEnLigne || 0;
    document.getElementById('panel-subtitle').textContent = 
      `${customdata.nbNoticesEnLigne?.toLocaleString() || 0} notices - Cliquez sur une serie`;

    const listContainer = document.getElementById('inventaires-list');
    listContainer.innerHTML = `
      <div class="placeholder-message">
        <div class="icon">📁</div>
        <p><strong>${name}</strong></p>
        <p style="margin-top: 0.5rem; font-size: 0.7rem;">${customdata.description || ''}</p>
        <p style="margin-top: 1rem;">Cliquez sur une <strong>serie</strong> pour voir ses inventaires.</p>
      </div>
    `;

    this.currentInventaires = [];
    this.filteredInventaires = [];
  }

  /**
   * Filtre les inventaires selon la recherche
   */
  filterInventaires(query) {
    const q = query.toLowerCase().trim();
    
    if (!q) {
      this.filteredInventaires = this.currentInventaires;
    } else {
      this.filteredInventaires = this.currentInventaires.filter(inv => {
        const cote = (inv.cote || '').toLowerCase();
        const titre = (inv.titre || '').toLowerCase();
        const dates = (inv.dates || '').toLowerCase();
        return cote.includes(q) || titre.includes(q) || dates.includes(q);
      });
    }

    // Mettre a jour le compteur
    document.getElementById('panel-count').textContent = this.filteredInventaires.length;

    this.renderInventairesList(this.filteredInventaires);
  }

  /**
   * Affiche la liste des inventaires
   */
  renderInventairesList(inventaires) {
    const listContainer = document.getElementById('inventaires-list');
    
    if (inventaires.length === 0) {
      listContainer.innerHTML = `
        <div class="no-results">
          Aucun inventaire trouve.
        </div>
      `;
      return;
    }

    const html = inventaires.map(inv => `
      <a href="${inv.url || '#'}" target="_blank" class="inventaire-item" 
         title="${inv.titre || inv.cote}">
        <div class="cote">${inv.cote}</div>
        <div class="titre">${inv.titre || 'Sans titre'}</div>
        <div class="meta">
          <span class="dates">${inv.dates || '-'}</span>
          <span class="notices">${(inv.nb_notices || 0).toLocaleString()} notices</span>
          <span class="link-icon">→</span>
        </div>
      </a>
    `).join('');

    listContainer.innerHTML = html;
  }

  /**
   * Gere le clic sur un noeud de l'arbre
   */
  handleTreeNodeClick(data) {
    console.log('Tree node clicked:', data);
    
    // Si inventaire, ouvrir le lien
    if (data.type === 'inventaire' && data.url) {
      window.open(data.url, '_blank');
      return;
    }

    // Si serie avec inventaires
    if (data.children && data.children.length > 0 && data.children[0].type === 'inventaire') {
      const inventaires = data.children.map(child => ({
        cote: child.name,
        titre: child.titre,
        dates: child.dates,
        nb_notices: child.nbNotices || child.value,
        url: child.url
      }));
      
      this.showInventairesList(data.name, {
        inventaires: inventaires,
        nbNotices: data.nbNotices
      });
    }
  }

  /**
   * Affiche/masque le loader
   */
  showLoader(show) {
    const loader = document.getElementById('loader');
    if (loader) {
      loader.classList.toggle('hidden', !show);
    }
  }

  /**
   * Affiche une erreur
   */
  showError(message) {
    const errorEl = document.getElementById('error-message');
    if (errorEl) {
      errorEl.textContent = message;
      errorEl.classList.remove('hidden');
    }
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const app = new App();
  app.init();
});

export default App;
