/**
 * App - Application principale de visualisation des archives
 * Archives departementales des Bouches-du-Rhone (AD13)
 * 
 * Auteur: Barbara Proenca
 */
import { DataLoader } from './DataLoader.js';
import { SunburstViz } from './SunburstViz.js';
import { TreeViz } from './TreeViz.js';

class App {
  constructor() {
    this.dataLoader = new DataLoader();
    this.sunburstViz = null;
    this.treeViz = null;
    this.currentView = 'sunburst';
  }

  /**
   * Initialise l'application
   */
  async init() {
    try {
      this.showLoader(true);

      const data = await this.dataLoader.load();

      this.displayStats();

      // Initialiser le Sunburst
      this.sunburstViz = new SunburstViz('sunburst-container', {
        onNodeClick: (data) => this.handleNodeClick(data)
      });
      this.sunburstViz.render(data);

      // Initialiser l'arbre (lazy)
      this.treeData = this.dataLoader.buildTreeData();

      this.setupEventListeners();

      this.showLoader(false);

      console.log('Application initialisee - Sunburst');
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

    // Controles de l'arbre
    document.getElementById('expand-all')?.addEventListener('click', () => {
      if (this.treeViz) this.treeViz.expandAll();
    });

    document.getElementById('collapse-all')?.addEventListener('click', () => {
      if (this.treeViz) this.treeViz.collapseAll();
    });

    // Redimensionnement
    window.addEventListener('resize', () => {
      if (this.currentView === 'sunburst' && this.sunburstViz) {
        this.sunburstViz.resize();
      }
    });
  }

  /**
   * Bascule entre les vues
   */
  switchView(view) {
    this.currentView = view;

    // Mettre a jour les boutons
    document.querySelectorAll('.view-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.view === view);
    });

    // Afficher/masquer les conteneurs
    document.getElementById('sunburst-view').classList.toggle('hidden', view !== 'sunburst');
    document.getElementById('tree-view').classList.toggle('hidden', view !== 'tree');

    // Initialiser l'arbre si necessaire (lazy loading)
    if (view === 'tree' && !this.treeViz && this.treeData) {
      const treeContainer = document.getElementById('tree-container');
      const treeHeight = treeContainer ? treeContainer.clientHeight || 600 : 600;
      const treeWidth = treeContainer ? treeContainer.clientWidth || 1200 : 1200;
      
      this.treeViz = new TreeViz('tree-container', {
        width: treeWidth,
        height: treeHeight,
        onNodeClick: (data) => this.handleTreeNodeClick(data)
      });
      this.treeViz.render(this.treeData);
    }

    // Redimensionner
    if (view === 'sunburst' && this.sunburstViz) {
      setTimeout(() => this.sunburstViz.resize(), 100);
    }
  }

  /**
   * Gere le clic sur un noeud du sunburst
   */
  handleNodeClick(data) {
    console.log('Sunburst node clicked:', data);
    // Le clic ouvre directement le lien (gere dans SunburstViz)
  }

  /**
   * Gere le clic sur un noeud de l'arbre
   */
  handleTreeNodeClick(data) {
    console.log('Tree node clicked:', data);
    
    // Si c'est un inventaire avec URL, ouvrir dans un nouvel onglet
    if (data.type === 'inventaire' && data.url) {
      window.open(data.url, '_blank');
    } else if (data.url) {
      window.open(data.url, '_blank');
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
    this.showLoader(false);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const app = new App();
  app.init();
});

export default App;
