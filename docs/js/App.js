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
        onNodeClick: (data) => this.handleNodeClick(data)
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
    document.getElementById('stat-producteurs').textContent = stats.nombreProducteurs;
    document.getElementById('stat-metrage').textContent = `${stats.totalMetrage} ml`;
    document.getElementById('stat-entrees').textContent = stats.totalEntrees;
  }

  /**
   * Configure les ecouteurs d'evenements
   */
  setupEventListeners() {
    document.querySelectorAll('.view-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const view = e.currentTarget.dataset.view;
        this.switchView(view);
      });
    });

    document.getElementById('expand-all')?.addEventListener('click', () => {
      this.treeViz.expandAll();
    });

    document.getElementById('collapse-all')?.addEventListener('click', () => {
      this.treeViz.collapseAll();
    });

    document.getElementById('export-btn')?.addEventListener('click', () => {
      if (this.currentView === 'treemap') {
        this.treemapViz.exportImage('png');
      }
    });

    window.addEventListener('resize', () => {
      if (this.treemapViz) {
        this.treemapViz.resize();
      }
    });

    document.getElementById('close-info')?.addEventListener('click', () => {
      document.getElementById('info-panel').classList.remove('visible');
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

    document.getElementById('tree-controls').classList.toggle('hidden', view !== 'tree');

    if (view === 'treemap' && this.treemapViz) {
      setTimeout(() => this.treemapViz.resize(), 100);
    }
  }

  /**
   * Gere le clic sur un noeud du treemap
   */
  handleNodeClick(data) {
    console.log('Treemap node clicked:', data);
  }

  /**
   * Gere le clic sur un noeud de l'arbre
   */
  handleTreeNodeClick(data) {
    console.log('Tree node clicked:', data);
    
    const infoPanel = document.getElementById('info-panel');
    if (!infoPanel) return;

    const badge = document.getElementById('info-badge');
    if (badge) badge.textContent = data.children ? 'Categorie' : 'Element';
    
    const title = document.getElementById('info-title');
    if (title) title.textContent = data.name;
    
    const desc = document.getElementById('info-description');
    if (desc) desc.textContent = data.description || 'Cliquez pour explorer les sous-elements.';
    
    const statsContainer = document.getElementById('info-stats-container');
    if (statsContainer && data.value) {
      let statsHtml = `
        <div class="stat">
          <span class="stat-value">${data.value.toFixed(2)}</span>
          <span class="stat-label">metres lineaires</span>
        </div>
      `;
      if (data.nombreEntrees) {
        statsHtml += `
          <div class="stat">
            <span class="stat-value">${data.nombreEntrees}</span>
            <span class="stat-label">versements</span>
          </div>
        `;
      }
      statsContainer.innerHTML = statsHtml;
    }
    
    const dates = document.getElementById('info-dates');
    if (dates) dates.textContent = `Dates extremes: ${data.dateExtreme || '-'}`;

    // Afficher le lien vers le site AD13 si disponible
    const link = document.getElementById('info-link');
    if (link) {
      if (data.url) {
        link.href = data.url;
        link.classList.remove('hidden');
      } else {
        link.classList.add('hidden');
      }
    }

    infoPanel.classList.add('visible');
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
